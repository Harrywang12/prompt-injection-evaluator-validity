# Confirmatory pre-adjudication human-agreement audit

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

- Exact category agreement: 591 / 800 (73.875%)
- Disagreement: 209
- Seven-category Cohen's kappa: 0.597554
- FULL_COMPLIANCE versus PARTIAL_COMPLIANCE disagreements: 3
- Rows where either annotator used AMBIGUOUS: 9

Rows are Annotator A; columns are Annotator B.

| A \ B | FULL_COMPLIANCE | PARTIAL_COMPLIANCE | INJECTION_IGNORED | REFUSAL | REFUSAL_QUOTATION | OFF_TOPIC_FAILURE | AMBIGUOUS |
|---|---:|---:|---:|---:|---:|---:|---:|
| FULL_COMPLIANCE | 106 | 1 | 0 | 0 | 0 | 0 | 0 |
| PARTIAL_COMPLIANCE | 2 | 330 | 146 | 0 | 0 | 19 | 1 |
| INJECTION_IGNORED | 0 | 11 | 101 | 0 | 0 | 3 | 0 |
| REFUSAL | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| REFUSAL_QUOTATION | 0 | 3 | 2 | 0 | 0 | 0 | 0 |
| OFF_TOPIC_FAILURE | 0 | 12 | 0 | 0 | 0 | 54 | 0 |
| AMBIGUOUS | 2 | 2 | 0 | 0 | 0 | 4 | 0 |

## Adjudication set

- Unique rows: 209
- Due to category disagreement: 209
- Involving AMBIGUOUS: 9
- Overlap: 9
- Administrative row-order seed: `2026082207`

The private adjudicator file contains only the same substantive blinded context shown to A/B plus blank adjudicator fields. It contains no A/B judgments, model identity, scorer verdict, stratum, probability, weight, or generation provenance.

## Private artifact SHA-256

- `annotator_A_completed_raw.xlsx`: `0ef4c380e33b390f844214c2c8b12de00ea2194b4c26c85f0b01b2c409a76c50`
- `annotator_B_completed_raw.xlsx`: `50dbbfd099783b9aaf612829e55fc885debc7a584f7325f3d6782b92e7667af1`
- `annotator_A_completed_validated.csv`: `ddcd736d7cabf72ffcbd8bd8db784d9510f004d78139503954cfb82fe2517099`
- `annotator_B_completed_validated.csv`: `8fe95faa55ec5815f3572e6f3726b6f3d518c6fe0de2beec1b7888614a794d0b`
- `merged_annotations_AB.csv`: `0ccac6338f0223ebda54f254a1ac103fe28d5f620b9ea9b43b49a48cafb6d6ac`
- `pre_adjudication_agreement.json`: `9e1eede8ee52158d5cc2036fa0d04373588eec0d0080cf6326d8374ace1c636f`
- `confirmatory_adjudication_blinded.csv`: `bd482d5d83466d68c886231acd5a8ed7175a8d9e05ec886e42e18caf694f6424`
- `adjudication_key_private.csv`: `1ccb7b82eaf1cc4c2c1f1aa39257f305e008b7ce09f511a677047ec4b132344d`
