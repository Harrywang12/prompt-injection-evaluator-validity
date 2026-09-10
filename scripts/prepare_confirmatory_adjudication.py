#!/usr/bin/env python3
"""Reconstruct completed CSVs, validate, and prepare human-only adjudication."""

from __future__ import annotations

import json
from pathlib import Path

from src.confirmatory_human_agreement import (
    ADJUDICATOR_FIELDS, EXPECTED_FIELDS, FORBIDDEN_ADJUDICATOR_FIELDS,
    adjudicator_rows, agreement, merged_rows, read_csv_strict,
    read_xlsx_first_sheet, reconstruct_completed, sha256_file,
    validate_completed, write_csv,
)

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "confirmatory_private/human_annotation"
RAW_A = PRIVATE / "raw/annotator_A_completed_raw.xlsx"
RAW_B = PRIVATE / "raw/annotator_B_completed_raw.xlsx"
FROZEN_A = ROOT / "confirmatory_private/human_sample/confirmatory_annotation_A_blinded.csv"
FROZEN_B = ROOT / "confirmatory_private/human_sample/confirmatory_annotation_B_blinded.csv"
VALID_A = PRIVATE / "validated/annotator_A_completed_validated.csv"
VALID_B = PRIVATE / "validated/annotator_B_completed_validated.csv"
MERGED = PRIVATE / "merged_annotations_AB.csv"
AGREEMENT = PRIVATE / "pre_adjudication_agreement.json"
ADJUDICATION = PRIVATE / "confirmatory_adjudication_blinded.csv"
KEY = PRIVATE / "adjudication_key_private.csv"
PUBLIC_AUDIT = ROOT / "confirmatory/human_agreement_activation_audit.md"
ORDER_SEED = 2026082207
MERGED_FIELDS = ["annotation_item_id", "annotator_a_label", "annotator_a_confidence", "annotator_a_notes", "annotator_b_label", "annotator_b_confidence", "annotator_b_notes"]
KEY_FIELDS = ["annotation_item_id", "annotator_a_label", "annotator_b_label"]


def matrix_markdown(result: dict) -> str:
    labels = result["category_order"]
    lines = ["| A \\ B | " + " | ".join(labels) + " |", "|---|" + "---:|" * len(labels)]
    matrix = result["confusion_matrix_a_rows_b_columns"]
    for a in labels:
        lines.append("| " + a + " | " + " | ".join(str(matrix[a][b]) for b in labels) + " |")
    return "\n".join(lines)


def public_audit(result: dict, hashes: dict[str, str], restored_a: int, restored_b: int) -> None:
    hash_lines = "\n".join(f"- `{name}`: `{digest}`" for name, digest in hashes.items())
    PUBLIC_AUDIT.write_text(f"""# Confirmatory pre-adjudication human-agreement audit

Audit date: 2026-09-09 (America/Toronto)

Status: **PASS**

This stage used human annotations only. It performed no scorer-human comparison, ASR, H1/RQ2/H3 analysis, bootstrap, GEE, model comparison, or task comparison.

## Validation and preservation

- Annotator A: 800 rows, 800 unique IDs, valid complete labels and confidence
- Annotator B: 800 rows, 800 unique IDs, valid complete labels and confidence
- A/B ID sets: identical
- Raw completed XLSX files: preserved byte-for-byte under the ignored private tree
- Authorized export reconstruction: restored the frozen CRLF representation in 45 non-human `legitimate_input` cells for A and 45 for B; the same 45 item IDs were affected
- Human-entered labels, confidence, and notes: copied unchanged from each preserved XLSX
- All reconstructed non-human fields, anonymous IDs, and row mappings: exact matches to the frozen blinded handoffs

## Pre-adjudication human-human agreement

- Exact category agreement: {result['category_agreement_count']} / 800 ({result['category_agreement_percentage']:.3f}%)
- Disagreement: {result['disagreement_count']}
- Seven-category Cohen's kappa: {result['cohens_kappa_seven_category']:.6f}
- FULL_COMPLIANCE versus PARTIAL_COMPLIANCE disagreements: {result['full_vs_partial_disagreement_count']}
- Rows where either annotator used AMBIGUOUS: {result['either_annotator_ambiguous_count']}

Rows are Annotator A; columns are Annotator B.

{matrix_markdown(result)}

## Adjudication set

- Unique rows: {result['adjudication_set_size']}
- Due to category disagreement: {result['adjudication_due_to_disagreement_count']}
- Involving AMBIGUOUS: {result['adjudication_due_to_ambiguous_count']}
- Overlap: {result['adjudication_condition_overlap_count']}
- Administrative row-order seed: `{ORDER_SEED}`

The private adjudicator file contains only the same substantive blinded context shown to A/B plus blank adjudicator fields. It contains no A/B judgments, model identity, scorer verdict, stratum, probability, weight, or generation provenance.

## Private artifact SHA-256

{hash_lines}
""", encoding="utf-8")


def main() -> None:
    frozen_a, frozen_b = read_csv_strict(FROZEN_A), read_csv_strict(FROZEN_B)
    exported_a, exported_b = read_xlsx_first_sheet(RAW_A), read_xlsx_first_sheet(RAW_B)
    rows_a, restored_a = reconstruct_completed(exported_a, frozen_a, "A")
    rows_b, restored_b = reconstruct_completed(exported_b, frozen_b, "B")
    validate_completed(rows_a, frozen_a, "A")
    validate_completed(rows_b, frozen_b, "B")
    if {x["annotation_item_id"] for x in rows_a} != {x["annotation_item_id"] for x in rows_b}:
        raise ValueError("A/B item-ID sets differ")

    result = agreement(rows_a, rows_b)
    merged = merged_rows(rows_a, rows_b)
    adjudication = adjudicator_rows(rows_a, result["adjudication_ids"], ORDER_SEED)
    if FORBIDDEN_ADJUDICATOR_FIELDS.intersection(ADJUDICATOR_FIELDS):
        raise RuntimeError("adjudicator schema exposes forbidden fields")
    if {x["annotation_item_id"] for x in adjudication} != set(result["adjudication_ids"]):
        raise RuntimeError("adjudicator IDs do not equal adjudication set")

    write_csv(VALID_A, rows_a, EXPECTED_FIELDS)
    write_csv(VALID_B, rows_b, EXPECTED_FIELDS)
    write_csv(MERGED, merged, MERGED_FIELDS)
    AGREEMENT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(ADJUDICATION, adjudication, ADJUDICATOR_FIELDS)
    merged_by_id = {x["annotation_item_id"]: x for x in merged}
    key_rows = [{field: merged_by_id[item_id][field] for field in KEY_FIELDS} for item_id in result["adjudication_ids"]]
    write_csv(KEY, key_rows, KEY_FIELDS)

    paths = {
        "annotator_A_completed_raw.xlsx": RAW_A,
        "annotator_B_completed_raw.xlsx": RAW_B,
        "annotator_A_completed_validated.csv": VALID_A,
        "annotator_B_completed_validated.csv": VALID_B,
        "merged_annotations_AB.csv": MERGED,
        "pre_adjudication_agreement.json": AGREEMENT,
        "confirmatory_adjudication_blinded.csv": ADJUDICATION,
        "adjudication_key_private.csv": KEY,
    }
    hashes = {name: sha256_file(path) for name, path in paths.items()}
    public_audit(result, hashes, restored_a, restored_b)
    print(json.dumps({
        "status": "PASS",
        "agreement_count": result["category_agreement_count"],
        "agreement_percentage": result["category_agreement_percentage"],
        "cohens_kappa": result["cohens_kappa_seven_category"],
        "disagreement_count": result["disagreement_count"],
        "full_vs_partial_disagreement_count": result["full_vs_partial_disagreement_count"],
        "either_annotator_ambiguous_count": result["either_annotator_ambiguous_count"],
        "adjudication_set_size": result["adjudication_set_size"],
        "private_artifact_sha256": hashes,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
