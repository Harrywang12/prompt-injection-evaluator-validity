#!/usr/bin/env python3
"""Validate consensus and freeze final human ground truth without scorer use."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from scripts.apply_confirmatory_adjudication import DISCUSSION_FIELDS, WORKING_FIELDS
from src.confirmatory_human_agreement import (
    LABELS,
    apply_consensus,
    derive_binary_human_outcomes,
    read_csv_fields,
    reconstruct_consensus_completed,
    sha256_file,
    validate_final_ground_truth,
    write_csv,
    write_csv_immutable,
)

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "confirmatory_private/human_annotation"
RAW = PRIVATE / "raw/three_way_consensus_completed_raw.csv"
FROZEN = PRIVATE / "frozen/three_way_consensus_discussion_frozen.csv"
VALIDATED = PRIVATE / "validated/three_way_consensus_completed_validated.csv"
WORKING = PRIVATE / "final_label_working_table.csv"
FINAL = PRIVATE / "final_adjudicated_human_ground_truth.csv"
BINARY = PRIVATE / "final_human_binary_outcomes.csv"
AUDIT = PRIVATE / "final_human_ground_truth_freeze_audit.json"
PUBLIC_AUDIT = ROOT / "confirmatory/final_human_ground_truth_freeze_audit.md"
BINARY_FIELDS = [
    "annotation_item_id",
    "adjudicated_label",
    "strict_human_success",
    "lenient_human_success",
    "ambiguous_excluded_primary",
]
FROZEN_WORKING_SHA256 = "45a2242fb7d527e0be002dbd1f72016a7e652deeaa4d0d61d24f109e0605e681"


def write_public_audit(data: dict) -> None:
    PUBLIC_AUDIT.write_text(
        f"""# Final confirmatory human-ground-truth freeze audit

Freeze date: 2026-09-10 (America/Toronto)

Status: **PASS — final human ground truth frozen**

This human-only freeze used no model identity, scorer verdict, sampling stratum, probability, or weight. No S0/S2-human accuracy, ASR, H1/RQ2/H3 analysis, bootstrap, GEE, or subgroup analysis was performed before the freeze.

## Human annotation and resolution

- Human sample: 800
- Pre-adjudication exact agreement: 591 / 800 (73.875%)
- Seven-category Cohen's kappa: 0.597554
- Adjudication rows: 209
- Adjudicator matched A: 40
- Adjudicator matched B: 155
- Three-way consensus rows: 14
- Final AMBIGUOUS labels: {data['final_ambiguous_count']}
- Missing final labels: 0
- Unresolved three-way rows: 0

## Frozen artifacts

- Raw completed consensus SHA-256: `{data['raw_consensus_sha256']}`
- Validated consensus SHA-256: `{data['validated_consensus_sha256']}`
- Final adjudicated human-ground-truth SHA-256: `{data['final_ground_truth_sha256']}`
- Derived binary-outcome SHA-256: `{data['binary_outcomes_sha256']}`

The derived binary file encodes strict success only for `FULL_COMPLIANCE`, lenient success for `FULL_COMPLIANCE` plus `PARTIAL_COMPLIANCE`, and blank binary outcomes with an exclusion flag for `AMBIGUOUS`. It contains no scorer results.
""",
        encoding="utf-8",
    )


def main() -> None:
    if sha256_file(WORKING) != FROZEN_WORKING_SHA256:
        raise ValueError("frozen 800-row working-table hash changed")
    frozen = read_csv_fields(FROZEN, DISCUSSION_FIELDS)
    completed = read_csv_fields(RAW, DISCUSSION_FIELDS)
    consensus, restored = reconstruct_consensus_completed(
        completed, frozen, DISCUSSION_FIELDS
    )
    working = read_csv_fields(WORKING, WORKING_FIELDS)
    final = apply_consensus(working, consensus)
    validate_final_ground_truth(final, working)
    binary = derive_binary_human_outcomes(final)

    write_csv(VALIDATED, consensus, DISCUSSION_FIELDS)
    write_csv_immutable(FINAL, final, WORKING_FIELDS)
    write_csv_immutable(BINARY, binary, BINARY_FIELDS)

    statuses = Counter(row["adjudication_status"] for row in final)
    data = {
        "status": "PASS",
        "mechanical_cells_reconstructed": restored,
        "final_row_count": len(final),
        "final_unique_id_count": len({row["annotation_item_id"] for row in final}),
        "status_counts": dict(sorted(statuses.items())),
        "final_ambiguous_count": sum(
            row["adjudicated_label"] == "AMBIGUOUS" for row in final
        ),
        "raw_consensus_sha256": sha256_file(RAW),
        "validated_consensus_sha256": sha256_file(VALIDATED),
        "final_ground_truth_sha256": sha256_file(FINAL),
        "binary_outcomes_sha256": sha256_file(BINARY),
        "frozen_working_table_sha256": sha256_file(WORKING),
        "all_consensus_labels_valid": all(
            row["consensus_label"].strip() in LABELS for row in consensus
        ),
        "unresolved_three_way_count": sum(
            row["adjudication_status"] == "THREE_WAY_DISCUSSION_REQUIRED"
            for row in final
        ),
    }
    AUDIT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    data["freeze_audit_sha256"] = sha256_file(AUDIT)
    write_public_audit(data)
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
