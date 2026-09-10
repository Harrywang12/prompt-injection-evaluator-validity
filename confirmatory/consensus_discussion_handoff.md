# Confirmatory three-way consensus-discussion handoff

Status: **HUMAN ACTION REQUIRED**

Fourteen rows remain unresolved because Annotator A, Annotator B, and the independent adjudicator selected three different categories. No majority or inferred label was assigned.

The three humans must jointly review the private file:

`confirmatory_private/human_annotation/three_way_consensus_discussion.csv`

Frozen discussion-file SHA-256:

`233771cb54c552d166219c9d2d37bd0f4f394b840f99a6071017903b833940ea`

For every row, use `protocol/final_annotation_manual.md` and complete:

- `consensus_label` with a valid frozen category if consensus is reached;
- `consensus_notes` with a concise rationale;
- if consensus cannot be reached, enter `AMBIGUOUS` as `consensus_label`.

Do not change any anonymous ID, substantive context, raw response, or original A/B/adjudicator label. Do not add or consult model identity, scorer outputs, sampling strata, probabilities, weights, or generation provenance.

After all 14 rows are completed, preserve the submitted discussion file byte-for-byte and validate it before freezing the final 800 adjudicated labels.
