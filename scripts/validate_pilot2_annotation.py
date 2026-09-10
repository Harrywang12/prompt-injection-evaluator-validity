#!/usr/bin/env python3
"""Strictly validate Pilot 2 blinding and mapping integrity."""

from __future__ import annotations

import csv
import random
from pathlib import Path

import yaml

from src.pilot2 import BLINDED_FIELDS, FORBIDDEN_BLINDED_FRAGMENTS, validate_blinded_rows


def main() -> None:
    config = yaml.safe_load(Path("config/pilot2_config.yaml").read_text(encoding="utf-8"))
    blinded_path = Path(config["paths"]["blinded_annotation"])
    internal_path = Path(config["paths"]["internal_sample"])
    with blinded_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if list(reader.fieldnames or []) != BLINDED_FIELDS:
            raise ValueError("blinded columns differ from expected columns")
        blinded = list(reader)
    validate_blinded_rows(blinded, config["study"]["planned_human_sample_size"])
    with internal_path.open(newline="", encoding="utf-8") as handle:
        internal = {row["sample_id"]: row for row in csv.DictReader(handle)}
    if set(internal) != {row["sample_id"] for row in blinded}:
        raise ValueError("blinded and internal sample IDs differ")
    expected_order = list(internal)
    random.Random(config["random"]["annotation_shuffle_seed"]).shuffle(expected_order)
    if [row["sample_id"] for row in blinded] != expected_order:
        raise ValueError("blinded row order differs from deterministic shuffle")
    for row in blinded:
        source = internal[row["sample_id"]]
        expected = {
            "legitimate_instruction": source["legitimate_instruction"],
            "legitimate_input": source["legitimate_input"],
            "injected_instruction": source["attack_injection_text"],
            "target_behavior": source["target_behavior"],
            "victim_model_response": source["victim_response"],
        }
        for field, value in expected.items():
            if row[field] != value:
                raise ValueError(f"mapping mismatch for {row['sample_id']} field {field}")
    leaked_fields = [
        field for field in BLINDED_FIELDS
        if any(fragment in field.lower() for fragment in FORBIDDEN_BLINDED_FRAGMENTS)
    ]
    if leaked_fields:
        raise ValueError(f"hidden scorer/sampling fields leaked: {leaked_fields}")
    # A strict parse/write/parse roundtrip detects malformed quoting or rows.
    import io
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=BLINDED_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(blinded)
    if list(csv.DictReader(io.StringIO(buffer.getvalue(), newline=""))) != blinded:
        raise ValueError("CSV roundtrip integrity check failed")
    print(f"validated {len(blinded)} blinded Pilot 2 records; no scorer/sampling fields exposed")


if __name__ == "__main__":
    main()
