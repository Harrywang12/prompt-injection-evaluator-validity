#!/usr/bin/env python3
"""Checkpointable Google Colab runner for the frozen confirmatory generation.

This file is preparation code. Importing it or running its tests performs no
generation. Actual generation requires an explicit ``--model-id`` or
``--all-models`` invocation in a CUDA/BF16 environment.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import random
import subprocess
import sys
import traceback
from pathlib import Path

import numpy as np
import yaml

from src.confirmatory import (
    PRIVATE_ROOT,
    assert_unique_generation_keys,
    load_private_manifest,
    persist_terminal_record_once,
    sha256_file,
    terminal_record_exists,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "protocol/final_generation_config.yaml"
MODELS_PATH = ROOT / "protocol/final_model_revisions.yaml"
AUDIT_PATH = ROOT / "confirmatory/prompt_manifest_audit.json"
EXPECTED_TRANSFORMERS = "5.15.0"
EXPECTED_CONFIG_SHA256 = "3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--model-id")
    selector.add_argument("--all-models", action="store_true")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PRIVATE_ROOT / "prompts/confirmatory_prompt_manifest.jsonl",
    )
    parser.add_argument("--responses", type=Path, default=PRIVATE_ROOT / "responses")
    parser.add_argument("--checkpoints", type=Path, default=PRIVATE_ROOT / "checkpoints")
    return parser.parse_args()


def load_and_validate_inputs(manifest_path: Path) -> tuple[dict, dict, dict, list[dict]]:
    config_hash = sha256_file(CONFIG_PATH)
    if config_hash != EXPECTED_CONFIG_SHA256:
        raise RuntimeError(f"generation config hash mismatch: {config_hash}")
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    models = yaml.safe_load(MODELS_PATH.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    if sha256_file(manifest_path) != audit["prompt_manifest_sha256"]:
        raise RuntimeError("private prompt manifest hash differs from public audit")
    if config_hash != audit["generation_config_sha256"]:
        raise RuntimeError("generation config hash differs from public audit")
    prompts = load_private_manifest(manifest_path)
    if len(prompts) != 1680 or len({row["confirmatory_prompt_id"] for row in prompts}) != 1680:
        raise RuntimeError("private prompt manifest count/uniqueness failure")
    revisions = [model["revision"] for model in models["models"]]
    if assert_unique_generation_keys(
        [row["confirmatory_prompt_id"] for row in prompts], revisions
    ) != 5040:
        raise RuntimeError("expected exactly 5,040 unique generation keys")
    return config, models, audit, prompts


def runtime_preflight(config: dict) -> tuple[dict, object, object, object]:
    import torch
    import transformers
    from huggingface_hub import HfApi

    if transformers.__version__ != EXPECTED_TRANSFORMERS:
        raise RuntimeError(
            f"Transformers must be {EXPECTED_TRANSFORMERS}; found {transformers.__version__}"
        )
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required; generation will not fall back to CPU or MPS")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("native CUDA bfloat16 support is required")
    if config["generation"]["device"] != "cuda" or config["generation"]["torch_dtype"] != "bfloat16":
        raise RuntimeError("frozen CUDA/bfloat16 settings changed")
    torch.use_deterministic_algorithms(True)
    gpu = torch.cuda.get_device_name(0)
    provenance = {
        "session_start_utc": utc_now(),
        "gpu_model": gpu,
        "cuda_available": True,
        "cuda_version": torch.version.cuda,
        "python_version": platform.python_version(),
        "pytorch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "accelerate_version": None,
        "bfloat16_supported": True,
        "generation_seed": config["random_seeds"]["generation"],
    }
    try:
        import accelerate

        provenance["accelerate_version"] = accelerate.__version__
    except ImportError:
        pass
    return provenance, torch, transformers, HfApi()


def set_frozen_seeds(seed: int, torch) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def verify_remote_revision(api, repository: str, revision: str) -> str:
    resolved = api.model_info(repository, revision=revision).sha
    if resolved != revision:
        raise RuntimeError(f"revision resolution mismatch for {repository}: {resolved}")
    return resolved


def persist_session_provenance(checkpoint_dir: Path, provenance: dict) -> Path:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    session_id = provenance["session_start_utc"].replace(":", "-").replace("+", "_")
    path = checkpoint_dir / f"runtime-{session_id}.json"
    if path.exists():
        raise FileExistsError(f"runtime provenance already exists: {path}")
    path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    freeze = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], check=True, capture_output=True, text=True
    ).stdout
    (checkpoint_dir / f"pip-freeze-{session_id}.txt").write_text(freeze, encoding="utf-8")
    return path


def generation_kwargs(config: dict, tokenizer) -> dict:
    frozen = config["generation"]
    if any(frozen[name] is not None for name in ("temperature", "top_p", "top_k")):
        raise RuntimeError("temperature/top_p/top_k must remain unset")
    if frozen["do_sample"] is not False or frozen["decoding_method"] != "greedy":
        raise RuntimeError("frozen greedy decoding changed")
    if frozen["custom_stop_strings"]:
        raise RuntimeError("custom stop strings are forbidden")
    if tokenizer.pad_token_id is None or tokenizer.eos_token_id is None:
        raise RuntimeError("frozen tokenizer pad/eos IDs must both be defined")
    return {
        "do_sample": False,
        "max_new_tokens": 128,
        "pad_token_id": tokenizer.pad_token_id,
        "eos_token_id": tokenizer.eos_token_id,
    }


def select_models(model_config: dict, args: argparse.Namespace) -> list[dict]:
    models = model_config["models"]
    if args.all_models:
        return models
    matches = [model for model in models if model["model_id"] == args.model_id]
    if len(matches) != 1:
        raise ValueError(f"unknown model ID: {args.model_id}")
    return matches


def run_one_model(
    *, model_spec: dict, prompts: list[dict], config: dict, audit: dict,
    response_root: Path, torch, transformers, api,
) -> dict[str, int]:
    revision = model_spec["revision"]
    repository = model_spec["repository"]
    if model_spec["tokenizer_revision"] != revision:
        raise RuntimeError("tokenizer and model revisions differ")
    model_output = response_root / model_spec["model_id"]
    pending = [
        prompt
        for prompt in prompts
        if not terminal_record_exists(model_output, prompt["confirmatory_prompt_id"], revision)
    ]
    if not pending:
        return {"skipped": len(prompts), "success": 0, "generation_failure": 0}
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        repository,
        revision=revision,
        trust_remote_code=bool(model_spec["trust_remote_code"]),
    )
    model = transformers.AutoModelForCausalLM.from_pretrained(
        repository,
        revision=revision,
        trust_remote_code=bool(model_spec["trust_remote_code"]),
        torch_dtype=torch.bfloat16,
        attn_implementation="eager",
    ).to("cuda")
    model.eval()
    kwargs = generation_kwargs(config, tokenizer)
    counts = {"skipped": len(prompts) - len(pending), "success": 0, "generation_failure": 0}
    seed = config["random_seeds"]["generation"]
    for prompt in prompts:
        prompt_id = prompt["confirmatory_prompt_id"]
        if terminal_record_exists(model_output, prompt_id, revision):
            continue
        started = utc_now()
        status = "success"
        raw_response = None
        failure = None
        try:
            set_frozen_seeds(seed, torch)
            messages = [
                {"role": "system", "content": prompt["legitimate_instruction"]},
                {"role": "user", "content": prompt["user_message"]},
            ]
            encoded = tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt",
                return_dict=True,
            )
            input_length = encoded["input_ids"].shape[-1]
            if prompt["task"] == "summarization" and input_length > 8000:
                raise RuntimeError("BillSum prompt exceeds frozen 8,000-token threshold")
            encoded = {name: tensor.to("cuda") for name, tensor in encoded.items()}
            with torch.inference_mode():
                output = model.generate(**encoded, **kwargs)
            generated = output[0, input_length:]
            raw_response = tokenizer.decode(
                generated,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )
            if raw_response == "":
                raise RuntimeError("empty_decoded_response")
        except Exception as error:  # persisted as a terminal technical failure; no retry
            status = "generation_failure"
            failure = {
                "exception_class": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }
        ended = utc_now()
        record = {
            "confirmatory_prompt_id": prompt_id,
            "model_repository": repository,
            "model_revision": revision,
            "tokenizer_revision": model_spec["tokenizer_revision"],
            "task": prompt["task"],
            "task_category": prompt["task_category"],
            "template_id": prompt["template_id"],
            "target_id": prompt["target_id"],
            "raw_decoded_response": raw_response,
            "generation_seed": seed,
            "decoding_configuration": {
                "do_sample": False,
                "temperature": None,
                "top_p": None,
                "top_k": None,
                "max_new_tokens": 128,
                "torch_dtype": "bfloat16",
                "attention_implementation": "eager",
                "batch_size": 1,
                "pad_token_id": tokenizer.pad_token_id,
                "eos_token_id": tokenizer.eos_token_id,
                "custom_stop_strings": [],
                "skip_special_tokens": True,
                "clean_up_tokenization_spaces": False,
            },
            "generation_start_timestamp_utc": started,
            "generation_end_timestamp_utc": ended,
            "generation_status": status,
            "technical_failure_metadata": failure,
            "prompt_manifest_sha256": audit["prompt_manifest_sha256"],
            "generation_config_sha256": audit["generation_config_sha256"],
        }
        persist_terminal_record_once(model_output, record)
        counts[status] += 1
    del model
    torch.cuda.empty_cache()
    return counts


def main() -> None:
    args = parse_args()
    config, model_config, audit, prompts = load_and_validate_inputs(args.manifest)
    provenance, torch, transformers, api = runtime_preflight(config)
    selected = select_models(model_config, args)
    provenance.update(
        {
            "prompt_manifest_sha256": audit["prompt_manifest_sha256"],
            "generation_config_sha256": audit["generation_config_sha256"],
            "selected_models": [
                {"repository": model["repository"], "revision": model["revision"]}
                for model in selected
            ],
            "model_revision_verification": [
                {
                    "repository": model["repository"],
                    "requested_revision": model["revision"],
                    "resolved_revision": verify_remote_revision(
                        api, model["repository"], model["revision"]
                    ),
                }
                for model in selected
            ],
            "tokenizer_revision_verification": [
                {
                    "repository": model["tokenizer_repository"],
                    "revision": model["tokenizer_revision"],
                    "equals_model_revision": model["tokenizer_revision"] == model["revision"],
                }
                for model in selected
            ],
        }
    )
    provenance_path = persist_session_provenance(args.checkpoints, provenance)
    results = {}
    for model in selected:
        results[model["model_id"]] = run_one_model(
            model_spec=model,
            prompts=prompts,
            config=config,
            audit=audit,
            response_root=args.responses,
            torch=torch,
            transformers=transformers,
            api=api,
        )
    provenance["session_end_utc"] = utc_now()
    provenance["results"] = results
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
