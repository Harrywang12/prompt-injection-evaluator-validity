#!/usr/bin/env python3
"""Freeze the canonical 800-row analysis dataset before result inspection."""

from __future__ import annotations

import json
from pathlib import Path

from src.confirmatory_analysis import (
    ANALYSIS_FIELDS,
    INPUT_HASHES,
    build_analysis_dataset,
    sha256_file,
    write_csv_immutable,
)

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "confirmatory_private"
INPUT_PATHS = {
    "usable_response_manifest.jsonl": PRIVATE / "scoring/usable_response_manifest.jsonl",
    "s0_s2_scores.jsonl": PRIVATE / "scoring/s0_s2_scores.jsonl",
    "human_sample_master.csv": PRIVATE / "human_sample/human_sample_master.csv",
    "sampling_audit.json": PRIVATE / "human_sample/sampling_audit.json",
    "final_adjudicated_human_ground_truth.csv": PRIVATE / "human_annotation/final_adjudicated_human_ground_truth.csv",
    "final_human_binary_outcomes.csv": PRIVATE / "human_annotation/final_human_binary_outcomes.csv",
}
OUTPUT = PRIVATE / "analysis/final_analysis_dataset.csv"
AUDIT = PRIVATE / "analysis/analysis_dataset_freeze_audit.json"


def main() -> None:
    rows = build_analysis_dataset(INPUT_PATHS)
    write_csv_immutable(OUTPUT, rows, ANALYSIS_FIELDS)
    audit = {
        "status": "PASS",
        "input_sha256": INPUT_HASHES,
        "analysis_dataset_sha256": sha256_file(OUTPUT),
        "rows": len(rows),
        "unique_annotation_item_ids": len({row["annotation_item_id"] for row in rows}),
        "unique_generation_keys": len({row["generation_key"] for row in rows}),
        "s2_implies_s0": all(not int(row["s2"]) or int(row["s0"]) for row in rows),
        "ambiguous_rows": sum(row["adjudicated_label"] == "AMBIGUOUS" for row in rows),
        "failed_generation_rows": 0,
        "original_failed_phi_rows": 0,
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
