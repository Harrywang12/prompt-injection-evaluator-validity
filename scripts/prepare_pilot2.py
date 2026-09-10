#!/usr/bin/env python3
"""Create or append a deterministic Pilot 2 candidate-input batch."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import yaml

from src.pilot2 import CANDIDATE_FIELDS, assert_no_duplicate_attack_input_pairs, construct_batch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/pilot2_config.yaml"))
    parser.add_argument("--batch-index", type=int, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    output = Path(config["paths"]["candidate_inputs"])
    new_rows = construct_batch(config, args.batch_index)
    existing: list[dict[str, str]] = []
    if output.exists():
        with output.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if list(reader.fieldnames or []) != CANDIDATE_FIELDS:
                raise ValueError("existing candidate schema differs")
            existing = list(reader)
    existing_batches = {int(row["generation_batch"]) for row in existing}
    if args.batch_index in existing_batches:
        expected = [row for row in existing if int(row["generation_batch"]) == args.batch_index]
        if expected != new_rows:
            raise ValueError("existing candidate batch differs from deterministic reconstruction")
        print(f"candidate batch {args.batch_index} already exists and validates ({len(expected)} rows)")
        return
    if existing_batches != set(range(args.batch_index)):
        raise ValueError("candidate batches must be appended in order")
    combined = existing + new_rows
    if len({row["sample_id"] for row in combined}) != len(combined):
        raise ValueError("duplicate sample IDs across candidate batches")
    assert_no_duplicate_attack_input_pairs(combined)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_FIELDS)
        writer.writeheader()
        writer.writerows(combined)
    temporary.replace(output)
    print(f"appended batch {args.batch_index}: {len(new_rows)} candidates; total {len(combined)}")


if __name__ == "__main__":
    main()
