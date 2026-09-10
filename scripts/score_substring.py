#!/usr/bin/env python3
"""Score raw pilot outputs without exposing verdicts to annotators."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from src.scoring import key_e_contains, normalized_contains, whitespace_normalized_exact


def main() -> None:
    with Path("config/research_config.yaml").open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    inputs_path = Path(config["paths"]["pilot_inputs"])
    raw_path = Path(config["paths"]["raw_responses"])
    output_path = Path(config["paths"]["scored_responses"])
    with inputs_path.open(newline="", encoding="utf-8") as handle:
        inputs = {row["sample_id"]: row for row in csv.DictReader(handle)}
    with raw_path.open(encoding="utf-8") as handle:
        responses = [json.loads(line) for line in handle if line.strip()]
    if {row["sample_id"] for row in responses} != set(inputs):
        raise ValueError("raw response IDs do not match pilot input IDs")
    rows = []
    for response_row in responses:
        row = inputs[response_row["sample_id"]] | response_row
        response, target = row["victim_response"], row["target_keyword"]
        row["lexical_key_e_success"] = key_e_contains(response, target)
        row["lexical_normalized_success"] = normalized_contains(response, target)
        row["lexical_exact_success"] = whitespace_normalized_exact(response, target)
        rows.append(row)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"scored {len(rows)} records to restricted derived file {output_path}")


if __name__ == "__main__":
    main()

