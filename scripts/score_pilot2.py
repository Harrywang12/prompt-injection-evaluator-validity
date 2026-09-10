#!/usr/bin/env python3
"""Apply source-faithful KEY-E scoring to separately preserved Pilot 2 raw data."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from src.scoring import key_e_contains


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/pilot2_config.yaml"))
    parser.add_argument("--force-derived", action="store_true")
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    with Path(config["paths"]["candidate_inputs"]).open(newline="", encoding="utf-8") as handle:
        candidates = list(csv.DictReader(handle))
    raw_files = sorted(Path(config["paths"]["raw_directory"]).glob("batch_*_part_*.jsonl"))
    raw = []
    for path in raw_files:
        with path.open(encoding="utf-8") as handle:
            raw.extend(json.loads(line) for line in handle if line.strip())
    if len({row["sample_id"] for row in raw}) != len(raw):
        raise ValueError("duplicate raw response IDs")
    raw_by_id = {row["sample_id"]: row for row in raw}
    candidate_ids = {row["sample_id"] for row in candidates}
    if set(raw_by_id) != candidate_ids:
        missing = candidate_ids - set(raw_by_id)
        extra = set(raw_by_id) - candidate_ids
        raise ValueError(f"raw/candidate ID mismatch: missing={len(missing)} extra={len(extra)}")
    rows = []
    for candidate in candidates:
        response = raw_by_id[candidate["sample_id"]]
        usable = response["generation_status"] == "ok" and bool(response["victim_response"].strip())
        lexical = key_e_contains(response["victim_response"], candidate["target_text"]) if usable else None
        rows.append(
            candidate
            | response
            | {
                "usable_response": usable,
                "lexical_key_e_success": lexical if lexical is not None else "",
            }
        )
    output = Path(config["paths"]["scored_candidates"])
    if output.exists() and not args.force_derived:
        raise FileExistsError(f"refusing to overwrite derived scorer table {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)

    usable_rows = [row for row in rows if row["usable_response"]]
    positives = [row for row in usable_rows if row["lexical_key_e_success"]]
    negatives = [row for row in usable_rows if not row["lexical_key_e_success"]]
    dimensions = {}
    for field in ["task", "victim_model_id", "target_id", "injection_variant_id"]:
        grouped = defaultdict(lambda: {"total": 0, "usable": 0, "lexical_positive": 0, "lexical_negative": 0, "generation_failure": 0})
        for row in rows:
            group = grouped[row[field]]
            group["total"] += 1
            if row["usable_response"]:
                group["usable"] += 1
                group["lexical_positive" if row["lexical_key_e_success"] else "lexical_negative"] += 1
            else:
                group["generation_failure"] += 1
        dimensions[field] = dict(sorted(grouped.items()))
    summary = {
        "candidate_count": len(rows),
        "usable_responses": len(usable_rows),
        "lexical_positive": len(positives),
        "lexical_negative": len(negatives),
        "generation_failures": len(rows) - len(usable_rows),
        "duplicate_sample_ids": len(rows) - len({row["sample_id"] for row in rows}),
        "duplicates_removed": 0,
        "generation_batches": dict(sorted(Counter(row["generation_batch"] for row in rows).items())),
        "counts_by": dimensions,
    }
    summary_path = Path(config["paths"]["candidate_summary"])
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
