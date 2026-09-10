"""Shared deterministic helpers for the post-amendment Pilot 2 workflow."""

from __future__ import annotations

import csv
import hashlib
import random
from collections.abc import Iterable
from pathlib import Path


CANDIDATE_FIELDS = [
    "sample_id",
    "generation_batch",
    "source_dataset",
    "source_repository_url",
    "source_commit",
    "source_row_id",
    "task",
    "legitimate_instruction",
    "legitimate_input",
    "legitimate_expected_output",
    "injection_variant_id",
    "attack_injection_text",
    "target_id",
    "target_text",
    "target_behavior",
    "objective_type",
    "victim_model_id",
    "model_repository",
    "model_revision",
]

BLINDED_FIELDS = [
    "sample_id",
    "legitimate_instruction",
    "legitimate_input",
    "injected_instruction",
    "target_behavior",
    "victim_model_response",
    "human_label",
    "human_confidence",
    "notes",
]

FORBIDDEN_BLINDED_FRAGMENTS = (
    "lexical",
    "judge",
    "success",
    "score",
    "verdict",
    "stratum",
    "inclusion",
    "weight",
    "expected_output",
)


def derived_seed(base_seed: int, *parts: str) -> int:
    material = ":".join([str(base_seed), *parts]).encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def stable_sample_id(
    source_commit: str,
    task: str,
    source_row_id: int,
    variant_id: str,
    target_id: str,
    model_id: str,
) -> str:
    material = ":".join(
        [source_commit, task, str(source_row_id), variant_id, target_id, model_id]
    ).encode()
    return "P2-" + hashlib.sha256(material).hexdigest()[:16].upper()


def read_source_rows(source_root: Path, task: str) -> list[dict[str, str]]:
    with (source_root / task / "data.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def batch_slice(config: dict, batch_index: int) -> tuple[int, int, int]:
    design = config["design"]
    if batch_index < 0 or batch_index > design["maximum_expansion_batches"]:
        raise ValueError("batch index is outside the frozen design")
    cells = len(design["injection_variants"]) * len(design["targets"]) * len(
        config["victim_models"]
    )
    initial = design["initial_repetitions_per_task_variant_target"] * cells
    expansion = design["expansion_repetitions_per_task_variant_target"] * cells
    if batch_index == 0:
        return 0, initial, design["initial_repetitions_per_task_variant_target"]
    start = initial + (batch_index - 1) * expansion
    return start, start + expansion, design["expansion_repetitions_per_task_variant_target"]


def construct_batch(config: dict, batch_index: int) -> list[dict[str, str]]:
    source = config["source"]
    source_root = Path(source["root"])
    start, stop, repetitions = batch_slice(config, batch_index)
    selected: list[dict[str, str]] = []
    for task in source["tasks"]:
        rows = read_source_rows(source_root, task)
        row_ids = list(range(len(rows)))
        random.Random(
            derived_seed(config["random"]["source_sampling_seed"], "rows", task)
        ).shuffle(row_ids)
        if stop > len(row_ids):
            raise ValueError(f"frozen design needs {stop} unique rows from {task}, only {len(rows)} exist")
        chosen_ids = row_ids[start:stop]

        cells = [
            (variant, target, model)
            for variant in config["design"]["injection_variants"]
            for target in config["design"]["targets"]
            for model in config["victim_models"]
            for _ in range(repetitions)
        ]
        random.Random(
            derived_seed(
                config["random"]["source_sampling_seed"], "cells", task, str(batch_index)
            )
        ).shuffle(cells)
        if len(cells) != len(chosen_ids):
            raise AssertionError("balanced cell count does not match selected source rows")

        for row_id, (variant, target, model) in zip(chosen_ids, cells, strict=True):
            row = rows[row_id]
            target_text = target["text"]
            selected.append(
                {
                    "sample_id": stable_sample_id(
                        source["commit"], task, row_id, variant["id"], target["id"], model["id"]
                    ),
                    "generation_batch": str(batch_index),
                    "source_dataset": source["name"],
                    "source_repository_url": source["repository_url"],
                    "source_commit": source["commit"],
                    "source_row_id": str(row_id),
                    "task": task,
                    "legitimate_instruction": row["instruction"],
                    "legitimate_input": row["input"],
                    "legitimate_expected_output": row["output"],
                    "injection_variant_id": variant["id"],
                    "attack_injection_text": variant["template"].format(target=target_text),
                    "target_id": target["id"],
                    "target_text": target_text,
                    "target_behavior": target["behavior_template"].format(target=target_text),
                    "objective_type": target["objective_type"],
                    "victim_model_id": model["id"],
                    "model_repository": model["repository"],
                    "model_revision": model["revision"],
                }
            )
    if len({row["sample_id"] for row in selected}) != len(selected):
        raise AssertionError("Pilot 2 sample IDs are not unique")
    return selected


def assert_no_duplicate_attack_input_pairs(rows: Iterable[dict[str, str]]) -> None:
    pairs = [
        (
            row["task"],
            row["source_row_id"],
            row["injection_variant_id"],
            row["target_id"],
            row["victim_model_id"],
        )
        for row in rows
    ]
    if len(set(pairs)) != len(pairs):
        raise ValueError("duplicate attack/input/model pairs detected")


def validate_blinded_rows(
    rows: list[dict[str, str]], expected_size: int, *, require_blank_human_fields: bool = True
) -> None:
    if len(rows) != expected_size:
        raise ValueError(f"expected {expected_size} blinded rows, found {len(rows)}")
    if len({row["sample_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate blinded sample IDs")
    if any(
        any(fragment in field.lower() for fragment in FORBIDDEN_BLINDED_FRAGMENTS)
        for field in BLINDED_FIELDS
    ):
        raise ValueError("forbidden automated-outcome field in blinded schema")
    for row in rows:
        if not row["sample_id"] or not row["target_behavior"] or not row["victim_model_response"].strip():
            raise ValueError("missing blinded sample ID, target behavior, or response")
        if require_blank_human_fields and (
            row["human_label"] or row["human_confidence"] or row["notes"]
        ):
            raise ValueError("human-entry fields must be blank at handoff")
