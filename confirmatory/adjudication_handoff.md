# Confirmatory adjudication handoff

Status: **HUMAN ACTION REQUIRED**

The third independent adjudicator must label the private file:

`confirmatory_private/human_annotation/confirmatory_adjudication_blinded.csv`

Frozen handoff SHA-256:

`bd482d5d83466d68c886231acd5a8ed7175a8d9e05ec886e42e18caf694f6424`

The file contains 209 items in a reproducibly randomized order. Use `protocol/final_annotation_manual.md`. Complete `adjudicator_initial_label`, integer `adjudicator_confidence` from 1 through 5, and optional `adjudicator_notes` without changing any other field, header, anonymous item ID, or row.

The adjudicator must be a third person distinct from Annotators A and B. They must not receive the private adjudication key, either annotator's judgments, model identity, scorer outputs, sampling strata, inclusion probabilities, weights, or generation provenance.

After the independent adjudicator file is returned, preserve it byte-for-byte and validate it before applying the frozen resolution rule. Do not overwrite the original A/B labels.
