#!/usr/bin/env python3
"""Generate Pilot 2 responses into immutable, recoverable raw part files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import random
import traceback
from datetime import datetime, timezone
from pathlib import Path

import torch
import transformers
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer


def choose_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def validate_existing_part(path: Path, expected_ids: list[str]) -> None:
    rows = read_jsonl(path)
    if [row["sample_id"] for row in rows] != expected_ids:
        raise ValueError(f"existing raw part does not match expected IDs: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/pilot2_config.yaml"))
    parser.add_argument("--batch-index", type=int, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    with Path(config["paths"]["candidate_inputs"]).open(newline="", encoding="utf-8") as handle:
        rows = [
            row for row in csv.DictReader(handle)
            if int(row["generation_batch"]) == args.batch_index
        ]
    if not rows:
        raise ValueError("no candidate inputs for requested batch")

    raw_dir = Path(config["paths"]["raw_directory"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    records_per_file = config["generation"]["raw_file_records"]
    parts = [rows[start : start + records_per_file] for start in range(0, len(rows), records_per_file)]
    pending = []
    for part_index, part in enumerate(parts):
        path = raw_dir / f"batch_{args.batch_index:03d}_part_{part_index:03d}.jsonl"
        if path.exists():
            validate_existing_part(path, [row["sample_id"] for row in part])
            print(f"validated existing {path} ({len(part)} records)", flush=True)
        else:
            pending.append((part_index, part, path))
    model_cfg = config["victim_models"][0]
    model_path = Path(model_cfg["local_path"])
    if pending:
        seed = config["random"]["generation_seed"]
        random.seed(seed)
        torch.manual_seed(seed)
        device = choose_device()
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        tokenizer.padding_side = config["generation"]["tokenizer_padding_side"]
        model = AutoModelForCausalLM.from_pretrained(model_path)
        model.generation_config.temperature = None
        model.generation_config.top_p = None
        model.generation_config.top_k = None
        model.to(device)
        model.eval()
    else:
        device = "not_reloaded"
        print("all requested raw parts already exist and validate", flush=True)

    generated_total = sum(
        len(part)
        for part_index, part in enumerate(parts)
        if (raw_dir / f"batch_{args.batch_index:03d}_part_{part_index:03d}.jsonl").exists()
    )
    for part_index, part, output_path in pending:
        output_records: list[dict] = []
        batch_size = config["generation"]["inference_batch_size"]
        for start in range(0, len(part), batch_size):
            mini = part[start : start + batch_size]
            messages = [
                [
                    {"role": "system", "content": row["legitimate_instruction"]},
                    {
                        "role": "user",
                        "content": (
                            row["legitimate_input"]
                            + "\n\n"
                            + config["generation"]["untrusted_content_delimiter"]
                            + "\n"
                            + row["attack_injection_text"]
                        ),
                    },
                ]
                for row in mini
            ]
            prompts = [
                tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
                for message in messages
            ]
            try:
                encoded = tokenizer(prompts, return_tensors="pt", padding=True).to(device)
                with torch.inference_mode():
                    generated = model.generate(
                        **encoded,
                        do_sample=config["generation"]["do_sample"],
                        max_new_tokens=config["generation"]["max_new_tokens"],
                        pad_token_id=tokenizer.pad_token_id,
                        eos_token_id=tokenizer.eos_token_id,
                    )
                for row, input_ids, output_ids, prompt in zip(
                    mini, encoded.input_ids, generated, prompts, strict=True
                ):
                    response = tokenizer.decode(output_ids[len(input_ids) :], skip_special_tokens=True)
                    output_records.append(
                        {
                            "sample_id": row["sample_id"],
                            "generation_status": "ok" if response.strip() else "empty_response",
                            "victim_response": response,
                            "error_type": "",
                            "error_message": "",
                            "model_repository": model_cfg["repository"],
                            "model_revision": model_cfg["revision"],
                            "generation_seed": seed,
                            "do_sample": config["generation"]["do_sample"],
                            "temperature": config["generation"]["temperature"],
                            "max_new_tokens": config["generation"]["max_new_tokens"],
                            "device": device,
                            "python_version": platform.python_version(),
                            "torch_version": torch.__version__,
                            "transformers_version": transformers.__version__,
                            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                        }
                    )
            except Exception as exc:  # Preserve failures instead of discarding them.
                for row, prompt in zip(mini, prompts, strict=True):
                    output_records.append(
                        {
                            "sample_id": row["sample_id"],
                            "generation_status": "error",
                            "victim_response": "",
                            "error_type": type(exc).__name__,
                            "error_message": str(exc),
                            "model_repository": model_cfg["repository"],
                            "model_revision": model_cfg["revision"],
                            "generation_seed": seed,
                            "do_sample": config["generation"]["do_sample"],
                            "temperature": config["generation"]["temperature"],
                            "max_new_tokens": config["generation"]["max_new_tokens"],
                            "device": device,
                            "python_version": platform.python_version(),
                            "torch_version": torch.__version__,
                            "transformers_version": transformers.__version__,
                            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                            "traceback_tail": traceback.format_exc(limit=2),
                        }
                    )
            generated_total += len(mini)
            print(f"generated/recorded {generated_total}/{len(rows)} for batch {args.batch_index}", flush=True)
        if [record["sample_id"] for record in output_records] != [row["sample_id"] for row in part]:
            raise RuntimeError("raw output order/IDs differ from candidate part")
        temporary = output_path.with_suffix(".jsonl.tmp")
        with temporary.open("x", encoding="utf-8") as handle:
            for record in output_records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        temporary.replace(output_path)
        print(f"preserved immutable raw part {output_path}", flush=True)

    batch_files = sorted(raw_dir.glob(f"batch_{args.batch_index:03d}_part_*.jsonl"))
    batch_records = [record for path in batch_files for record in read_jsonl(path)]
    manifest_path = raw_dir / f"manifest_batch_{args.batch_index:03d}.json"
    if manifest_path.exists():
        existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        current_hashes = {path.name: file_sha256(path) for path in batch_files}
        if existing_manifest["parts"] != current_hashes:
            raise ValueError(f"raw manifest hash mismatch: {manifest_path}")
        print(f"validated existing immutable batch manifest {manifest_path}")
        return
    manifest = {
        "generation_batch": args.batch_index,
        "candidate_count": len(rows),
        "record_count": len(batch_records),
        "status_counts": {
            status: sum(record["generation_status"] == status for record in batch_records)
            for status in sorted({record["generation_status"] for record in batch_records})
        },
        "model_repository": model_cfg["repository"],
        "model_revision": model_cfg["revision"],
        "model_weights_sha256": file_sha256(model_path / "model.safetensors"),
        "config_sha256": file_sha256(args.config),
        "parts": {path.name: file_sha256(path) for path in batch_files},
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    overall_path = Path(config["paths"]["generation_manifest"])
    batch_manifests = sorted(raw_dir.glob("manifest_batch_*.json"))
    overall = {
        "config_sha256": file_sha256(args.config),
        "batches": {
            path.stem.removeprefix("manifest_batch_"): json.loads(path.read_text(encoding="utf-8"))
            for path in batch_manifests
        },
    }
    temporary = overall_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")
    temporary.replace(overall_path)
    print(f"wrote immutable batch manifest {manifest_path}")


if __name__ == "__main__":
    main()
