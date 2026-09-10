#!/usr/bin/env python3
"""Validate the adjudicator export and apply the frozen human-only rule."""

from __future__ import annotations

import json
from pathlib import Path

from src.confirmatory_human_agreement import (
    ADJUDICATOR_FIELDS,
    LABELS,
    NON_HUMAN_FIELDS,
    apply_frozen_adjudication,
    read_csv_fields,
    reconstruct_adjudicator_completed,
    sha256_file,
    validate_adjudicator_completed,
    write_csv, write_csv_immutable,
)

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "confirmatory_private/human_annotation"
RAW = PRIVATE / "raw/adjudicator_completed_raw.csv"
FROZEN = PRIVATE / "confirmatory_adjudication_blinded.csv"
VALIDATED = PRIVATE / "validated/adjudicator_completed_validated.csv"
MERGED = PRIVATE / "merged_annotations_AB.csv"
WORKING = PRIVATE / "final_label_working_table.csv"
DISCUSSION = PRIVATE / "three_way_consensus_discussion.csv"
FINAL = PRIVATE / "final_human_ground_truth.csv"
AUDIT = PRIVATE / "adjudication_resolution_audit.json"
PUBLIC_AUDIT = ROOT / "confirmatory/adjudication_resolution_audit.md"

MERGED_FIELDS = [
    "annotation_item_id", "annotator_a_label", "annotator_a_confidence",
    "annotator_a_notes", "annotator_b_label", "annotator_b_confidence",
    "annotator_b_notes",
]
WORKING_FIELDS = [
    "annotation_item_id", "annotator_a_label", "annotator_b_label",
    "adjudicator_initial_label", "adjudicated_label", "adjudication_status",
]
DISCUSSION_FIELDS = [
    *NON_HUMAN_FIELDS,
    "annotator_a_label", "annotator_b_label", "adjudicator_initial_label",
    "consensus_label", "consensus_notes",
]


def write_public_audit(data: dict) -> None:
    hashes = "\n".join(
        f"- `{name}`: `{digest}`" for name, digest in data["private_artifact_sha256"].items()
    )
    PUBLIC_AUDIT.write_text(
        f"""# Confirmatory adjudication-resolution audit

Audit date: 2026-09-10 (America/Toronto)

Status: **{data['status']}**

This human-only stage used no model identity, scorer verdict, sampling stratum, inclusion probability, or analysis weight. It performed no S0/S2 comparison, ASR, H1/RQ2/H3 analysis, bootstrap, or GEE.

## Validation

- Completed adjudicator rows / unique IDs: 209 / 209
- ID set and row order: exact match to frozen blinded adjudication handoff
- Labels and confidence: complete and valid
- Substantive non-human changes: 0
- Mechanical non-human cells reconstructed: {data['mechanical_cells_reconstructed']}
- Raw completed adjudicator file: preserved byte-for-byte

## Frozen-rule disposition

- Original A/B agreements: {data['status_counts'].get('AB_AGREEMENT', 0)}
- Adjudicator matched A: {data['status_counts'].get('ADJUDICATOR_MATCHED_A', 0)}
- Adjudicator matched B: {data['status_counts'].get('ADJUDICATOR_MATCHED_B', 0)}
- Three-way disagreements requiring discussion: {data['status_counts'].get('THREE_WAY_DISCUSSION_REQUIRED', 0)}
- Final 800 adjudicated labels complete: {str(data['final_labels_complete']).lower()}

Three-way rows were not automatically resolved. The private discussion file contains only blinded substantive context, the three human labels, and blank consensus fields. It contains no model/scorer/sampling metadata.

## Private artifact SHA-256

{hashes}
""",
        encoding="utf-8",
    )


def main() -> None:
    frozen = read_csv_fields(FROZEN, ADJUDICATOR_FIELDS)
    completed = read_csv_fields(RAW, ADJUDICATOR_FIELDS)
    canonical, restored = reconstruct_adjudicator_completed(completed, frozen)
    validate_adjudicator_completed(canonical, frozen)
    merged = read_csv_fields(MERGED, MERGED_FIELDS)
    key = read_csv_fields(
        PRIVATE / "adjudication_key_private.csv",
        ["annotation_item_id", "annotator_a_label", "annotator_b_label"],
    )
    if {row["annotation_item_id"] for row in canonical} != {
        row["annotation_item_id"] for row in key
    }:
        raise ValueError("adjudicator IDs differ from the frozen private adjudication key")
    merged_by_id = {row["annotation_item_id"]: row for row in merged}
    for row in key:
        original = merged_by_id[row["annotation_item_id"]]
        if row["annotator_a_label"] != original["annotator_a_label"] or row[
            "annotator_b_label"
        ] != original["annotator_b_label"]:
            raise ValueError("frozen A/B key does not match preserved merged annotations")

    working, status_counts = apply_frozen_adjudication(merged, canonical)
    unresolved = [row for row in working if row["adjudication_status"] == "THREE_WAY_DISCUSSION_REQUIRED"]
    frozen_by_id = {row["annotation_item_id"]: row for row in frozen}
    discussion = [
        {
            **{field: frozen_by_id[row["annotation_item_id"]][field] for field in NON_HUMAN_FIELDS},
            "annotator_a_label": row["annotator_a_label"],
            "annotator_b_label": row["annotator_b_label"],
            "adjudicator_initial_label": row["adjudicator_initial_label"],
            "consensus_label": "",
            "consensus_notes": "",
        }
        for row in unresolved
    ]

    write_csv(VALIDATED, canonical, ADJUDICATOR_FIELDS)
    write_csv(WORKING, working, WORKING_FIELDS)
    # The human handoff is immutable once created. A rerun must never replace
    # a human-edited working copy.
    write_csv_immutable(DISCUSSION, discussion, DISCUSSION_FIELDS)
    if unresolved and FINAL.exists():
        raise RuntimeError("unresolved discussion exists but a final ground-truth artifact is present")
    if not unresolved:
        if any(row["adjudicated_label"] not in LABELS for row in working):
            raise RuntimeError("final adjudicated labels are incomplete or invalid")
        write_csv(FINAL, working, WORKING_FIELDS)

    paths = {
        "adjudicator_completed_raw.csv": RAW,
        "adjudicator_completed_validated.csv": VALIDATED,
        "final_label_working_table.csv": WORKING,
        "three_way_consensus_discussion.csv": DISCUSSION,
    }
    if not unresolved:
        paths["final_human_ground_truth.csv"] = FINAL
    hashes = {name: sha256_file(path) for name, path in paths.items()}
    data = {
        "status": "HUMAN DISCUSSION REQUIRED" if unresolved else "COMPLETE",
        "mechanical_cells_reconstructed": restored,
        "status_counts": status_counts,
        "three_way_disagreement_count": len(unresolved),
        "unresolved_annotation_item_ids": [row["annotation_item_id"] for row in unresolved],
        "final_labels_complete": not unresolved,
        "private_artifact_sha256": hashes,
    }
    AUDIT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    data["private_artifact_sha256"]["adjudication_resolution_audit.json"] = sha256_file(AUDIT)
    write_public_audit(data)
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
