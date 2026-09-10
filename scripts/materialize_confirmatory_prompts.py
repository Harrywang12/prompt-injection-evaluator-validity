#!/usr/bin/env python3
"""Materialize the frozen confirmatory prompt sample without model generation.

Text-bearing output is written only beneath the Git-ignored private root. The
public JSON contains aggregate counts and cryptographic hashes, never source
text, reference answers, injection text, or selected source-row identifiers.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from src.confirmatory import (
    PRIVATE_ROOT,
    UNTRUSTED_DELIMITER,
    canonical_json_line,
    derived_seed,
    input_content_sha256,
    length_framed_sha256,
    sha256_file,
    stable_prompt_id,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "protocol/final_generation_config.yaml"
MODELS = ROOT / "protocol/final_model_revisions.yaml"
PILOT1 = ROOT / "data/derived/pilot_inputs.csv"
PILOT2 = ROOT / "data/derived/pilot2/candidate_inputs.csv"
EXPECTED_CONFIG_SHA256 = "3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284"
EXPECTED_DATASET_REVISION = "3d8510441c06a3d9dfb32eb0d7f80151730bcc4f"
EXPECTED_BILLSUM_SHA256 = "2733cb656a2a6fbff0fc012ca50bbf159615ff6451c0adb229884bbd474780b3"
EXPECTED_TASK_COUNTS = {
    "duplicate_sentence_detection": 256,
    "grammar_correction": 240,
    "hate_detection": 256,
    "natural_language_inference": 176,
    "sentiment_analysis": 256,
    "spam_detection": 256,
    "summarization": 240,
}
EXPECTED_ELIGIBLE = {
    "duplicate_sentence_detection": 307,
    "grammar_correction": 646,
    "hate_detection": 24679,
    "natural_language_inference": 178,
    "sentiment_analysis": 770,
    "spam_detection": 5058,
    "summarization": 3268,
}
MODEL_CONTEXT = {
    "qwen2_5_1_5b_instruct": 32768,
    "phi3_5_mini_instruct": 131072,
    "smollm2_1_7b_instruct": 8192,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--billsum-parquet",
        type=Path,
        default=PRIVATE_ROOT / "source_cache/billsum/data/test-00000-of-00001.parquet",
    )
    parser.add_argument("--tokenizer-root", type=Path, default=PRIVATE_ROOT / "tokenizers")
    parser.add_argument(
        "--private-manifest",
        type=Path,
        default=PRIVATE_ROOT / "prompts/confirmatory_prompt_manifest.jsonl",
    )
    parser.add_argument(
        "--public-audit",
        type=Path,
        default=ROOT / "confirmatory/prompt_manifest_audit.json",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def exploratory_exclusions() -> tuple[set[tuple[str, int]], set[str]]:
    source_ids: set[tuple[str, int]] = set()
    content_hashes: set[str] = set()
    for path in (PILOT1, PILOT2):
        for row in read_csv(path):
            source_ids.add((row["task"], int(row["source_row_id"])))
            content_hashes.add(input_content_sha256(row["legitimate_input"]))
    return source_ids, content_hashes


def literal_allowed_outputs() -> dict[str, set[str]]:
    # BaseLoader preserves unquoted YAML literals `yes` and `no` as strings.
    raw = yaml.load(CONFIG.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    return {
        task["id"]: set(task.get("allowed_outputs", []))
        for task in raw["source"]["tasks"]
    }


def load_tokenizers(root: Path, model_config: dict):
    try:
        import transformers
        from transformers import AutoTokenizer
    except ImportError as error:
        raise RuntimeError("Transformers 5.15.0 is required for materialization") from error
    if transformers.__version__ != "5.15.0":
        raise RuntimeError(f"expected Transformers 5.15.0, found {transformers.__version__}")
    directory = {
        "qwen2_5_1_5b_instruct": "qwen",
        "phi3_5_mini_instruct": "phi",
        "smollm2_1_7b_instruct": "smol",
    }
    tokenizers = {}
    for model in model_config["models"]:
        if model["tokenizer_revision"] != model["revision"]:
            raise ValueError("tokenizer revision differs from model revision")
        tokenizers[model["model_id"]] = AutoTokenizer.from_pretrained(
            root / directory[model["model_id"]], local_files_only=True
        )
    return tokenizers


def attack_variants(config: dict) -> list[tuple[str, str, str, str]]:
    return [
        (template["id"], target["id"], template["text"].format(target=target["text"]), target["text"])
        for template in config["injection_templates"]
        for target in config["targets"]
    ]


def context_filter(
    rows: list[dict], tokenizers: dict, variants: list[tuple[str, str, str, str]],
    *, billsum: bool, max_new_tokens: int, chunk_size: int = 256,
) -> tuple[list[dict], int]:
    ok = [True] * len(rows)
    for start in range(0, len(rows), chunk_size):
        chunk = rows[start : start + chunk_size]
        for _, _, injection, _ in variants:
            conversations = [
                [
                    {"role": "system", "content": row["legitimate_instruction"]},
                    {
                        "role": "user",
                        "content": f'{row["legitimate_input"]}\n\n{UNTRUSTED_DELIMITER}\n{injection}',
                    },
                ]
                for row in chunk
            ]
            for model_id, tokenizer in tokenizers.items():
                encoded = tokenizer.apply_chat_template(
                    conversations, tokenize=True, add_generation_prompt=True
                )
                input_ids = encoded["input_ids"] if hasattr(encoded, "keys") else encoded
                threshold = 8000 if billsum else MODEL_CONTEXT[model_id] - max_new_tokens
                for offset, ids in enumerate(input_ids):
                    if len(ids) > threshold:
                        ok[start + offset] = False
    accepted = [row for row, keep in zip(rows, ok, strict=True) if keep]
    return accepted, ok.count(False)


def wrapper_population(
    task: dict, config: dict, source_ids: set[tuple[str, int]], content_hashes: set[str],
    allowed: set[str], tokenizers: dict, variants: list[tuple[str, str, str, str]],
) -> tuple[list[dict], dict[str, int]]:
    source_path = ROOT / task["source_path"]
    if sha256_file(source_path) != task["source_sha256"]:
        raise ValueError(f"source hash mismatch: {task['id']}")
    rows = read_csv(source_path)
    if len(rows) != task["source_rows"]:
        raise ValueError(f"source row count mismatch: {task['id']}")
    reasons = Counter()
    seen: set[str] = set()
    candidates = []
    for row_id, row in enumerate(rows):
        if any(not row.get(field, "").strip() for field in config["source"]["required_columns"]):
            reasons["missing_required"] += 1
            continue
        if allowed and row["output"] not in allowed:
            reasons["invalid_closed_label"] += 1
            continue
        dedup = length_framed_sha256(
            [task["id"], row["instruction"], row["input"], row["output"]]
        )
        if dedup in seen:
            reasons["duplicate"] += 1
            continue
        seen.add(dedup)
        if (task["id"], row_id) in source_ids:
            reasons["exploratory_source_id_overlap"] += 1
            continue
        if input_content_sha256(row["input"]) in content_hashes:
            reasons["exploratory_content_overlap"] += 1
            continue
        candidates.append(
            {
                "source_row_id": str(row_id),
                "source_dataset": row["dataset"],
                "source_revision": config["source"]["revision"],
                "legitimate_instruction": row["instruction"],
                "legitimate_input": row["input"],
                "legitimate_expected_output": row["output"],
                "source_title": None,
            }
        )
    eligible, context_rejections = context_filter(
        candidates,
        tokenizers,
        variants,
        billsum=False,
        max_new_tokens=config["generation"]["max_new_tokens"],
    )
    reasons["context_length"] += context_rejections
    reasons["eligible"] = len(eligible)
    return eligible, dict(reasons)


def billsum_population(
    task: dict, parquet_path: Path, content_hashes: set[str], tokenizers: dict,
    variants: list[tuple[str, str, str, str]], config: dict,
) -> tuple[list[dict], dict[str, int]]:
    try:
        import pyarrow.parquet as pq
    except ImportError as error:
        raise RuntimeError("pyarrow 20.0.0 is required") from error
    if task["revision"] != EXPECTED_DATASET_REVISION:
        raise ValueError("BillSum revision differs from frozen revision")
    if task["split"] != "test" or "ca_test" not in task["excluded_splits"]:
        raise ValueError("BillSum split rule differs from frozen design")
    if sha256_file(parquet_path) != EXPECTED_BILLSUM_SHA256:
        raise ValueError("BillSum parquet hash mismatch")
    source_rows = pq.read_table(parquet_path, columns=["text", "summary", "title"]).to_pylist()
    if len(source_rows) != task["source_rows"]:
        raise ValueError("BillSum source row count mismatch")
    reasons = Counter()
    seen: set[str] = set()
    candidates = []
    instruction = task["field_mapping"]["legitimate_instruction"]
    for row_id, row in enumerate(source_rows):
        if any(not isinstance(row.get(field), str) or not row[field].strip() for field in task["required_fields"]):
            reasons["missing_required"] += 1
            continue
        dedup = length_framed_sha256(
            ["summarization", instruction, row["text"], row["summary"]]
        )
        if dedup in seen:
            reasons["duplicate"] += 1
            continue
        seen.add(dedup)
        if input_content_sha256(row["text"]) in content_hashes:
            reasons["exploratory_content_overlap"] += 1
            continue
        candidates.append(
            {
                "source_row_id": str(row_id),
                "source_dataset": "FiscalNote/billsum",
                "source_revision": task["revision"],
                "legitimate_instruction": instruction,
                "legitimate_input": row["text"],
                "legitimate_expected_output": row["summary"],
                "source_title": row["title"],
            }
        )
    eligible, context_rejections = context_filter(
        candidates,
        tokenizers,
        variants,
        billsum=True,
        max_new_tokens=config["generation"]["max_new_tokens"],
    )
    reasons["context_length"] += context_rejections
    reasons["eligible"] = len(eligible)
    return eligible, dict(reasons)


def select_task_rows(task: dict, rows: list[dict], config: dict) -> list[dict]:
    task_id = task["id"]
    source_seed = derived_seed(
        config["random_seeds"]["source_sampling_master"], "source_sampling", task_id
    )
    cell_seed = derived_seed(
        config["random_seeds"]["cell_allocation_master"], "cell_allocation", task_id
    )
    if task_id == "summarization":
        if source_seed != task["source_sampling_seed"] or cell_seed != task["cell_allocation_seed"]:
            raise ValueError("BillSum derived seed mismatch")
    ordered = sorted(rows, key=lambda row: int(row["source_row_id"]))
    random.Random(source_seed).shuffle(ordered)
    selected = ordered[: task["selected_base_prompts"]]
    cells = [
        (template, target)
        for template in config["injection_templates"]
        for target in config["targets"]
        for _ in range(task["repetitions_per_target_template_cell"])
    ]
    random.Random(cell_seed).shuffle(cells)
    if len(cells) != len(selected):
        raise ValueError(f"cell allocation length mismatch: {task_id}")
    output = []
    for source, (template, target) in zip(selected, cells, strict=True):
        injection = template["text"].format(target=target["text"])
        prompt_id = stable_prompt_id(
            source_revision=source["source_revision"],
            task=task_id,
            source_row_id=source["source_row_id"],
            template_id=template["id"],
            target_id=target["id"],
        )
        output.append(
            {
                "confirmatory_prompt_id": prompt_id,
                "task": task_id,
                "task_category": task["category"],
                "source_dataset": source["source_dataset"],
                "source_revision": source["source_revision"],
                "source_row_id": source["source_row_id"],
                "source_title": source["source_title"],
                "template_id": template["id"],
                "target_id": target["id"],
                "legitimate_instruction": source["legitimate_instruction"],
                "legitimate_input": source["legitimate_input"],
                "legitimate_expected_output": source["legitimate_expected_output"],
                "untrusted_content_delimiter": UNTRUSTED_DELIMITER,
                "injection_text": injection,
                "target_text": target["text"],
                "target_behavior": target["behavior"],
                "user_message": f'{source["legitimate_input"]}\n\n{UNTRUSTED_DELIMITER}\n{injection}',
                "source_sampling_seed": source_seed,
                "cell_allocation_seed": cell_seed,
            }
        )
    return output


def main() -> None:
    args = parse_args()
    config_hash = sha256_file(CONFIG)
    if config_hash != EXPECTED_CONFIG_SHA256:
        raise ValueError(f"frozen generation config hash mismatch: {config_hash}")
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    model_config = yaml.safe_load(MODELS.read_text(encoding="utf-8"))
    if len(model_config["models"]) != 3:
        raise ValueError("expected three pinned models")
    tokenizers = load_tokenizers(args.tokenizer_root, model_config)
    variants = attack_variants(config)
    if len(variants) != 8:
        raise ValueError("expected eight template-target variants")
    source_ids, content_hashes = exploratory_exclusions()
    allowed = literal_allowed_outputs()

    all_prompts = []
    population_audit = {}
    for task in config["source"]["tasks"]:
        if task["id"] == "summarization":
            eligible, reasons = billsum_population(
                task, args.billsum_parquet, content_hashes, tokenizers, variants, config
            )
        else:
            eligible, reasons = wrapper_population(
                task, config, source_ids, content_hashes, allowed[task["id"]], tokenizers, variants
            )
        if len(eligible) != EXPECTED_ELIGIBLE[task["id"]]:
            raise ValueError(
                f"eligible count mismatch for {task['id']}: {len(eligible)} != {EXPECTED_ELIGIBLE[task['id']]}"
            )
        selected = select_task_rows(task, eligible, config)
        if len(selected) != EXPECTED_TASK_COUNTS[task["id"]]:
            raise ValueError(f"selected count mismatch: {task['id']}")
        all_prompts.extend(selected)
        population_audit[task["id"]] = {
            "source_population": task["source_rows"],
            "exclusions": {key: value for key, value in sorted(reasons.items()) if key != "eligible"},
            "eligible": len(eligible),
            "selected": len(selected),
        }

    if len(all_prompts) != 1680 or len({row["confirmatory_prompt_id"] for row in all_prompts}) != 1680:
        raise ValueError("prompt count or ID uniqueness failure")
    args.private_manifest.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.private_manifest.with_suffix(args.private_manifest.suffix + ".tmp")
    with temporary.open("wb") as handle:
        for row in all_prompts:
            handle.write(canonical_json_line(row))
        handle.flush()
    temporary.replace(args.private_manifest)
    manifest_hash = sha256_file(args.private_manifest)

    task_counts = Counter(row["task"] for row in all_prompts)
    category_counts = Counter(row["task_category"] for row in all_prompts)
    template_counts = Counter(row["template_id"] for row in all_prompts)
    target_counts = Counter(row["target_id"] for row in all_prompts)
    cell_counts: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )
    for row in all_prompts:
        cell_counts[row["task"]][row["template_id"]][row["target_id"]] += 1
    prompt_id_set_hash = hashlib.sha256(
        "\n".join(sorted(row["confirmatory_prompt_id"] for row in all_prompts)).encode("ascii")
    ).hexdigest()
    audit = {
        "schema_version": "confirmatory-prompt-manifest-audit-v1",
        "public_safe": True,
        "contains_source_text": False,
        "contains_selected_source_row_ids": False,
        "preregistered_commit": "853eb6aa7c61e03896cdca3eb991fcf8debdc9cc",
        "prompt_manifest_sha256": manifest_hash,
        "prompt_id_set_sha256": prompt_id_set_hash,
        "generation_config_sha256": config_hash,
        "total_prompts": len(all_prompts),
        "expected_generation_keys": 5040,
        "counts_by_task": dict(sorted(task_counts.items())),
        "counts_by_task_category": dict(sorted(category_counts.items())),
        "counts_by_template": dict(sorted(template_counts.items())),
        "counts_by_target": dict(sorted(target_counts.items())),
        "task_template_target_counts": {
            task: {
                template: dict(sorted(targets.items()))
                for template, targets in sorted(templates.items())
            }
            for task, templates in sorted(cell_counts.items())
        },
        "source_revisions": {
            task["id"]: task.get("revision", config["source"]["revision"])
            for task in config["source"]["tasks"]
        },
        "source_population_audit": population_audit,
        "sampling_seeds": {
            "source_sampling_master": config["random_seeds"]["source_sampling_master"],
            "cell_allocation_master": config["random_seeds"]["cell_allocation_master"],
            "billsum_source_sampling": config["source"]["tasks"][-1]["source_sampling_seed"],
            "billsum_cell_allocation": config["source"]["tasks"][-1]["cell_allocation_seed"],
            "derived_by_task": {
                task["id"]: {
                    "source_sampling": derived_seed(
                        config["random_seeds"]["source_sampling_master"],
                        "source_sampling",
                        task["id"],
                    ),
                    "cell_allocation": derived_seed(
                        config["random_seeds"]["cell_allocation_master"],
                        "cell_allocation",
                        task["id"],
                    ),
                }
                for task in config["source"]["tasks"]
            },
        },
        "prohibited_exploratory_overlap": 0,
        "bill_sum": {
            "repository": "FiscalNote/billsum",
            "revision": EXPECTED_DATASET_REVISION,
            "split": "test",
            "excluded_splits": ["train", "ca_test"],
            "eligible": 3268,
            "selected": 240,
            "common_input_token_threshold_inclusive": 8000,
        },
        "gigaword_active": False,
        "id_assignment": "C1- plus first 20 uppercase hex characters of the frozen length-framed SHA-256 procedure",
        "permutation_implementation": "Python random.Random(seed).shuffle over source-row-ID-sorted eligible rows; CPython Mersenne Twister",
    }
    args.public_audit.parent.mkdir(parents=True, exist_ok=True)
    args.public_audit.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(args.private_manifest), "audit": str(args.public_audit), "sha256": manifest_hash, "prompts": len(all_prompts)}, indent=2))


if __name__ == "__main__":
    main()
