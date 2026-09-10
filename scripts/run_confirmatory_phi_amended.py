#!/usr/bin/env python3
"""Phi-only runner for post-registration compatibility amendment 002.

This runner changes only the Phi implementation-loading path from repository
remote code to the native Transformers 5.15.0 Phi3 implementation. It never
selects Qwen or SmolLM2 and writes only to a new versioned namespace.
"""

from __future__ import annotations

import argparse
import json
import os
import traceback
from pathlib import Path

from scripts.run_confirmatory_generation import (
    generation_kwargs,
    load_and_validate_inputs,
    persist_session_provenance,
    runtime_preflight,
    set_frozen_seeds,
    utc_now,
    verify_remote_revision,
)
from src.confirmatory import (
    PRIVATE_ROOT,
    canonical_json_line,
    generation_key,
    persist_terminal_record_once,
    response_filename,
    sha256_file,
    terminal_record_exists,
)


AMENDMENT_ID = "phi_generation_compatibility_v1"
PHI_MODEL_ID = "phi3_5_mini_instruct"
PHI_REPOSITORY = "microsoft/Phi-3.5-mini-instruct"
PHI_REVISION = "2fe192450127e6a83f7441aef6e3ca586c338b77"
EXPECTED_TRANSFORMERS = "5.15.0"
EXPECTED_PROMPT_MANIFEST_SHA256 = (
    "b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed"
)
EXPECTED_GENERATION_CONFIG_SHA256 = (
    "3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284"
)
EXPECTED_ORIGINAL_SNAPSHOT_MANIFEST_SHA256 = (
    "8bca7369fbfbaa78d8adcadab7967aa5a3a2d76ee802b8a591f1985a835913f8"
)
NATIVE_MODULE_PREFIX = "transformers.models.phi3"
OUTPUT_NAMESPACE_VERSION = "responses_phi_amended_v1"
OUTPUT_ROOT = PRIVATE_ROOT / OUTPUT_NAMESPACE_VERSION
CHECKPOINT_ROOT = PRIVATE_ROOT / "checkpoints_phi_amended_v1"
ORIGINAL_RESPONSES_ROOT = PRIVATE_ROOT / "responses"
ORIGINAL_PHI_ROOT = ORIGINAL_RESPONSES_ROOT / PHI_MODEL_ID
DEFAULT_SNAPSHOT_MANIFEST = (
    PRIVATE_ROOT / "checkpoints/original_generation_snapshot_manifest.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate only amended native-Transformers Phi responses."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PRIVATE_ROOT / "prompts/confirmatory_prompt_manifest.jsonl",
    )
    parser.add_argument(
        "--original-snapshot-manifest",
        type=Path,
        default=DEFAULT_SNAPSHOT_MANIFEST,
    )
    return parser.parse_args()


def phi_generation_keys(prompts: list[dict]) -> set[str]:
    return {
        generation_key(str(prompt["confirmatory_prompt_id"]), PHI_REVISION)
        for prompt in prompts
    }


def assert_frozen_phi_spec(model_config: dict) -> dict:
    matches = [
        model for model in model_config["models"] if model["model_id"] == PHI_MODEL_ID
    ]
    if len(matches) != 1:
        raise RuntimeError("frozen model file must contain exactly one Phi specification")
    model = matches[0]
    required = {
        "repository": PHI_REPOSITORY,
        "revision": PHI_REVISION,
        "tokenizer_repository": PHI_REPOSITORY,
        "tokenizer_revision": PHI_REVISION,
        "trust_remote_code": True,
    }
    observed = {name: model.get(name) for name in required}
    if observed != required:
        raise RuntimeError(f"frozen preregistered Phi specification changed: {observed}")
    return model


def assert_frozen_generation_settings(config: dict) -> None:
    generation = config["generation"]
    expected = {
        "device": "cuda",
        "torch_dtype": "bfloat16",
        "attention_implementation": "eager",
        "inference_batch_size": 1,
        "do_sample": False,
        "decoding_method": "greedy",
        "temperature": None,
        "top_p": None,
        "top_k": None,
        "max_new_tokens": 128,
        "custom_stop_strings": [],
        "skip_special_tokens_when_decoding": True,
        "preserve_leading_whitespace": True,
    }
    observed = {name: generation.get(name) for name in expected}
    if observed != expected:
        raise RuntimeError(f"frozen generation settings changed: {observed}")
    if config["random_seeds"]["generation"] != 2026082203:
        raise RuntimeError("frozen generation seed changed")
    retry = generation["retry_policy"]
    if retry["automatic_per_response_retries"] != 0:
        raise RuntimeError("frozen zero-retry rule changed")


def assert_isolated_namespaces(
    *, output_root: Path = OUTPUT_ROOT, checkpoint_root: Path = CHECKPOINT_ROOT
) -> None:
    output = output_root.resolve()
    checkpoints = checkpoint_root.resolve()
    original = ORIGINAL_RESPONSES_ROOT.resolve()
    forbidden = {
        original,
        ORIGINAL_PHI_ROOT.resolve(),
        (ORIGINAL_RESPONSES_ROOT / "qwen2_5_1_5b_instruct").resolve(),
        (ORIGINAL_RESPONSES_ROOT / "smollm2_1_7b_instruct").resolve(),
    }
    if output in forbidden or original in output.parents:
        raise RuntimeError("amended output namespace overlaps original responses")
    if checkpoints in forbidden or original in checkpoints.parents:
        raise RuntimeError("amended checkpoint namespace overlaps original responses")
    if output == checkpoints or output in checkpoints.parents or checkpoints in output.parents:
        raise RuntimeError("amended response and checkpoint namespaces overlap")


def directory_tree_sha256(root: Path) -> str:
    """Hash relative paths and file bytes without interpreting response content."""
    import hashlib

    if not root.is_dir():
        raise FileNotFoundError(root)
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        file_hash = bytes.fromhex(sha256_file(path))
        digest.update(file_hash)
    return digest.hexdigest()


def assert_original_phi_failures(prompts: list[dict]) -> dict[str, str]:
    expected_ids = {str(prompt["confirmatory_prompt_id"]) for prompt in prompts}
    expected_paths = {
        ORIGINAL_PHI_ROOT / response_filename(prompt_id, PHI_REVISION)
        for prompt_id in expected_ids
    }
    observed_paths = set(ORIGINAL_PHI_ROOT.glob("*.json"))
    if observed_paths != expected_paths:
        raise RuntimeError(
            "original Phi failure-record set does not exactly match 1,680 frozen keys"
        )
    hashes: dict[str, str] = {}
    for path in sorted(observed_paths):
        record = json.loads(path.read_text(encoding="utf-8"))
        prompt_id = str(record.get("confirmatory_prompt_id"))
        if (
            prompt_id not in expected_ids
            or record.get("model_revision") != PHI_REVISION
            or record.get("generation_status") != "generation_failure"
        ):
            raise RuntimeError(f"invalid preserved original Phi failure record: {path}")
        hashes[prompt_id] = sha256_file(path)
    if len(hashes) != len(expected_ids):
        raise RuntimeError("preserved original Phi failure count mismatch")
    return hashes


def pre_generation_checks(
    manifest_path: Path, snapshot_manifest_path: Path
) -> tuple[dict, dict, dict, list[dict], dict, dict[str, str], str]:
    config, model_config, audit, prompts = load_and_validate_inputs(manifest_path)
    if sha256_file(manifest_path) != EXPECTED_PROMPT_MANIFEST_SHA256:
        raise RuntimeError("amended runner prompt-manifest hash mismatch")
    if audit["generation_config_sha256"] != EXPECTED_GENERATION_CONFIG_SHA256:
        raise RuntimeError("amended runner generation-config hash mismatch")
    if len(prompts) != 1680 or len(phi_generation_keys(prompts)) != 1680:
        raise RuntimeError("amended Phi set must contain exactly 1,680 unique keys")
    phi_model = assert_frozen_phi_spec(model_config)
    assert_frozen_generation_settings(config)
    assert_isolated_namespaces()
    if sha256_file(snapshot_manifest_path) != EXPECTED_ORIGINAL_SNAPSHOT_MANIFEST_SHA256:
        raise RuntimeError("original-generation snapshot-manifest hash mismatch")
    original_failure_hashes = assert_original_phi_failures(prompts)
    original_tree_hash = directory_tree_sha256(ORIGINAL_RESPONSES_ROOT)
    return (
        config,
        model_config,
        audit,
        prompts,
        phi_model,
        original_failure_hashes,
        original_tree_hash,
    )


def append_progress(checkpoint_root: Path, record: dict) -> None:
    checkpoint_root.mkdir(parents=True, exist_ok=True)
    progress = checkpoint_root / "terminal-progress.jsonl"
    payload = canonical_json_line(
        {
            "confirmatory_prompt_id": record["confirmatory_prompt_id"],
            "model_revision": record["model_revision"],
            "generation_status": record["generation_status"],
            "terminal_record_persisted_at_utc": utc_now(),
        }
    )
    descriptor = os.open(progress, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, "ab") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def load_native_phi(*, torch, transformers):
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        PHI_REPOSITORY,
        revision=PHI_REVISION,
        trust_remote_code=False,
    )
    model = transformers.AutoModelForCausalLM.from_pretrained(
        PHI_REPOSITORY,
        revision=PHI_REVISION,
        trust_remote_code=False,
        torch_dtype=torch.bfloat16,
        attn_implementation="eager",
    ).to("cuda")
    resolved_model_class = type(model).__name__
    resolved_model_module = type(model).__module__
    if not resolved_model_module.startswith(NATIVE_MODULE_PREFIX):
        raise RuntimeError(
            f"native Phi3 implementation required; resolved {resolved_model_module}"
        )
    model.eval()
    return tokenizer, model, resolved_model_class, resolved_model_module


def run_amended_phi(
    *,
    tokenizer,
    model,
    resolved_model_class: str,
    resolved_model_module: str,
    prompts: list[dict],
    config: dict,
    audit: dict,
    original_failure_hashes: dict[str, str],
    torch,
) -> dict[str, int]:
    kwargs = generation_kwargs(config, tokenizer)
    model_output = OUTPUT_ROOT / PHI_MODEL_ID
    counts = {"success": 0, "generation_failure": 0, "skipped": 0}
    seed = config["random_seeds"]["generation"]
    for prompt in prompts:
        prompt_id = str(prompt["confirmatory_prompt_id"])
        if terminal_record_exists(model_output, prompt_id, PHI_REVISION):
            counts["skipped"] += 1
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
        except Exception as error:  # frozen zero-retry terminal failure
            status = "generation_failure"
            failure = {
                "exception_class": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }
        record = {
            "amendment_id": AMENDMENT_ID,
            "confirmatory_prompt_id": prompt_id,
            "model_repository": PHI_REPOSITORY,
            "model_revision": PHI_REVISION,
            "tokenizer_revision": PHI_REVISION,
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
            "generation_end_timestamp_utc": utc_now(),
            "generation_status": status,
            "technical_failure_metadata": failure,
            "prompt_manifest_sha256": audit["prompt_manifest_sha256"],
            "generation_config_sha256": audit["generation_config_sha256"],
            "original_failed_attempt_preserved": True,
            "original_failed_record_sha256": original_failure_hashes[prompt_id],
            "trust_remote_code": False,
            "resolved_model_class": resolved_model_class,
            "resolved_model_module": resolved_model_module,
            "corrected_output_namespace_version": OUTPUT_NAMESPACE_VERSION,
        }
        persist_terminal_record_once(model_output, record)
        append_progress(CHECKPOINT_ROOT, record)
        counts[status] += 1
    del model
    torch.cuda.empty_cache()
    return counts


def main() -> None:
    args = parse_args()
    (
        config,
        _model_config,
        audit,
        prompts,
        _phi_model,
        original_failure_hashes,
        original_tree_hash_before,
    ) = pre_generation_checks(args.manifest, args.original_snapshot_manifest)
    provenance, torch, transformers, api = runtime_preflight(config)
    if transformers.__version__ != EXPECTED_TRANSFORMERS:
        raise RuntimeError("frozen Transformers version changed")
    resolved_revision = verify_remote_revision(api, PHI_REPOSITORY, PHI_REVISION)
    tokenizer, model, model_class, model_module = load_native_phi(
        torch=torch, transformers=transformers
    )
    provenance.update(
        {
            "amendment_id": AMENDMENT_ID,
            "selected_model": PHI_REPOSITORY,
            "model_revision": PHI_REVISION,
            "tokenizer_revision": PHI_REVISION,
            "resolved_revision": resolved_revision,
            "trust_remote_code": False,
            "resolved_model_class": model_class,
            "resolved_model_module": model_module,
            "prompt_manifest_sha256": audit["prompt_manifest_sha256"],
            "generation_config_sha256": audit["generation_config_sha256"],
            "original_snapshot_manifest_sha256": (
                EXPECTED_ORIGINAL_SNAPSHOT_MANIFEST_SHA256
            ),
            "original_response_tree_sha256_before": original_tree_hash_before,
            "corrected_output_namespace_version": OUTPUT_NAMESPACE_VERSION,
        }
    )
    provenance_path = persist_session_provenance(CHECKPOINT_ROOT, provenance)
    counts = run_amended_phi(
        tokenizer=tokenizer,
        model=model,
        resolved_model_class=model_class,
        resolved_model_module=model_module,
        prompts=prompts,
        config=config,
        audit=audit,
        original_failure_hashes=original_failure_hashes,
        torch=torch,
    )
    original_tree_hash_after = directory_tree_sha256(ORIGINAL_RESPONSES_ROOT)
    if original_tree_hash_after != original_tree_hash_before:
        raise RuntimeError("original response tree changed during amended Phi run")
    provenance["session_end_utc"] = utc_now()
    provenance["original_response_tree_sha256_after"] = original_tree_hash_after
    provenance["results"] = counts
    provenance_path.write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({PHI_MODEL_ID: counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
