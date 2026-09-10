# Confirmatory adjudication-resolution audit

Audit date: 2026-09-10 (America/Toronto)

Status: **HUMAN DISCUSSION REQUIRED**

This human-only stage used no model identity, scorer verdict, sampling stratum, inclusion probability, or analysis weight. It performed no S0/S2 comparison, ASR, H1/RQ2/H3 analysis, bootstrap, or GEE.

## Validation

- Completed adjudicator rows / unique IDs: 209 / 209
- ID set and row order: exact match to frozen blinded adjudication handoff
- Labels and confidence: complete and valid
- Substantive non-human changes: 0
- Mechanical non-human cells reconstructed: 0
- Raw completed adjudicator file: preserved byte-for-byte

## Frozen-rule disposition

- Original A/B agreements: 591
- Adjudicator matched A: 40
- Adjudicator matched B: 155
- Three-way disagreements requiring discussion: 14
- Final 800 adjudicated labels complete: false

Three-way rows were not automatically resolved. The private discussion file contains only blinded substantive context, the three human labels, and blank consensus fields. It contains no model/scorer/sampling metadata.

## Private artifact SHA-256

- `adjudicator_completed_raw.csv`: `6cb63f6a7199aa337f416f55611299345579fe047dbb27727600175fc7cdad34`
- `adjudicator_completed_validated.csv`: `ad0a3ff0af50e54b680f3e62b1ef2d4be1027327927f7bf09c9a94ada75736b7`
- `final_label_working_table.csv`: `45a2242fb7d527e0be002dbd1f72016a7e652deeaa4d0d61d24f109e0605e681`
- `three_way_consensus_discussion.csv`: `233771cb54c552d166219c9d2d37bd0f4f394b840f99a6071017903b833940ea`
- `adjudication_resolution_audit.json`: `1a1a71a7aeca276a7e7de11a435fc54d1f2785e87104be4b9668bcfe241d397a`
