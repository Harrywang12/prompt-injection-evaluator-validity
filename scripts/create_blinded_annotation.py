#!/usr/bin/env python3
"""Create a shuffled annotation file containing no automated verdicts."""

from __future__ import annotations

import csv
import random
from pathlib import Path

import yaml


OUTPUT_FIELDS = [
    "sample_id",
    "legitimate_instruction",
    "legitimate_input",
    "attack_injection_text",
    "target_behavior",
    "victim_model_response",
    "human_label",
    "human_confidence",
    "notes",
]
FORBIDDEN_FRAGMENTS = ("lexical", "judge", "correct", "success", "score", "verdict")


def main() -> None:
    with Path("config/research_config.yaml").open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    with Path(config["paths"]["pilot_inputs"]).open(newline="", encoding="utf-8") as handle:
        inputs = {row["sample_id"]: row for row in csv.DictReader(handle)}
    with Path(config["paths"]["scored_responses"]).open(newline="", encoding="utf-8") as handle:
        scored = list(csv.DictReader(handle))
    random.Random(config["random"]["annotation_shuffle_seed"]).shuffle(scored)
    rows = []
    for row in scored:
        source = inputs[row["sample_id"]]
        rows.append(
            {
                "sample_id": row["sample_id"],
                "legitimate_instruction": source["legitimate_instruction"],
                "legitimate_input": source["legitimate_input"],
                "attack_injection_text": source["attack_injection_text"],
                "target_behavior": source["target_behavior"],
                "victim_model_response": row["victim_response"],
                "human_label": "",
                "human_confidence": "",
                "notes": "",
            }
        )
    assert not any(any(fragment in field.lower() for fragment in FORBIDDEN_FRAGMENTS) for field in OUTPUT_FIELDS)
    output_path = Path(config["paths"]["blinded_annotation"])
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"created blinded annotation set with {len(rows)} records at {output_path}")


if __name__ == "__main__":
    main()

