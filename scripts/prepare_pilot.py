#!/usr/bin/env python3
"""Sample pilot inputs without reading or modifying any victim outcomes."""

from __future__ import annotations

import argparse
import csv
import hashlib
import random
from pathlib import Path

import yaml


FIELDS = [
    "sample_id",
    "source_dataset",
    "source_commit",
    "source_row_id",
    "task",
    "legitimate_instruction",
    "legitimate_input",
    "legitimate_expected_output",
    "attack_injection_text",
    "objective_type",
    "target_keyword",
    "target_behavior",
]


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def stable_id(source_commit: str, task: str, row_id: int) -> str:
    material = f"{source_commit}:{task}:{row_id}".encode()
    return "P-" + hashlib.sha256(material).hexdigest()[:12].upper()


def sample_rows(config: dict) -> list[dict[str, str]]:
    pilot = config["pilot"]
    rng = random.Random(config["random"]["sampling_seed"])
    selected: list[dict[str, str]] = []
    for task in pilot["tasks"]:
        source_path = Path(pilot["source_root"]) / task / "data.csv"
        with source_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        count = pilot["per_task_counts"][task]
        if count > len(rows):
            raise ValueError(f"requested {count} rows from {task}, only {len(rows)} exist")
        for row_id in sorted(rng.sample(range(len(rows)), count)):
            row = rows[row_id]
            selected.append(
                {
                    "sample_id": stable_id(pilot["source_commit"], task, row_id),
                    "source_dataset": pilot["source_name"],
                    "source_commit": pilot["source_commit"],
                    "source_row_id": str(row_id),
                    "task": task,
                    "legitimate_instruction": row["instruction"],
                    "legitimate_input": row["input"],
                    "legitimate_expected_output": row["output"],
                    "attack_injection_text": pilot["injection_template"],
                    "objective_type": pilot["objective_type"],
                    "target_keyword": pilot["target_keyword"],
                    "target_behavior": pilot["target_behavior"],
                }
            )
    if len(selected) != config["study"]["pilot_size"]:
        raise AssertionError("configured allocation does not equal pilot_size")
    if len({row["sample_id"] for row in selected}) != len(selected):
        raise AssertionError("sample IDs are not unique")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/research_config.yaml"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    output = args.output or Path(config["paths"]["pilot_inputs"])
    if output.exists() and not args.force:
        raise FileExistsError(f"refusing to overwrite {output}; pass --force for derived data")
    rows = sample_rows(config)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} pre-outcome pilot inputs to {output}")


if __name__ == "__main__":
    main()

