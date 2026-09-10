# Confirmatory human-sampling activation audit

Audit date: 2026-09-07 (America/Toronto)

Status: **PASS — blinded double-annotation files prepared; no human labels collected**

This public-safe audit contains no prompt or response text, row-level scorer verdicts, ASR, model/task scorer comparisons, human labels, or hypothesis results.

## Frozen usable generation population

- Planned generation keys: 5,040
- Usable successful nonempty responses: 4,993
- Final technical failures: 47
- Original remote-code Phi failures retained only as provenance and excluded: 1,680

Usable counts by model:

- `phi3_5_mini_instruct`: 1,634
- `qwen2_5_1_5b_instruct`: 1,680
- `smollm2_1_7b_instruct`: 1,679

The usable manifest contains unique `(confirmatory_prompt_id, model_revision)` keys, contains no failed or empty response, and uses the amended native-Phi namespace rather than the original failed-Phi namespace. S2-implies-S0 structural validation passed.

## Frozen human sampling

- Sampling seed: `2026082204`
- Annotator A order seed: `2026082205`
- Annotator B order seed: `2026082206`
- Target and achieved human sample: 800
- Sampled disagreement records: 480
- Sampled agreement controls: 320
- Disagreement selection mode: stratified probability sample

The procedure applied the preregistered quota rule, model-by-task strata within each scorer cell, Hamilton largest-remainder allocation with frozen lexical tie-breaking, capacity redistribution, and seeded sampling without replacement. Every sampled row retains `N_h`, `n_h`, exact rational inclusion probability, and inverse-probability weight privately. Agreement controls cover both scorer-agreement cells, all three usable model families, and both frozen task categories.

Annotators A and B receive the same 800 anonymous item IDs in independently randomized orders. Their files omit model/revision, scorer verdicts and cell, stratum, probabilities, weights, generation provenance, source paths, and the other annotator's fields. All label, confidence, and notes cells are blank. CSV round-trip validation confirmed exact preservation of annotation-visible response and task text.

## Private artifact SHA-256 hashes

- `confirmatory_annotation_A_blinded.csv`: `7feb7d9f212cebd34dee4dd74b28c6cb65e24bd7356fad4066551a31af3828f0`
- `confirmatory_annotation_B_blinded.csv`: `c640edac64e0e2f8d138f9efbb05d827f6b0b7cee02254b2f3c80b4c4114a0b8`
- `human_sample_master.csv`: `548253edba237af76373be7ba5064d876a4a76b0f5367a3c5b0e8131477edd6f`
- `s0_s2_scores.jsonl`: `e98889194ab841957aa60cf0825543916a63324f710a319f4900b513186e64bf`
- `sampling_audit.json`: `5476c6824705d93c8da06b1b06dc3f953aef4019e86b1046043699c0d002157f`
- `usable_response_manifest.jsonl`: `aa543f839be2d489374318ea46d182527d9bd988b07d13284fcc187f1e419f9f`

All listed artifacts are ignored by Git because they contain row-level scorer information, upstream source text, or raw model responses. The frozen prompt-manifest SHA-256 remains `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed` and the frozen generation-config SHA-256 remains `3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284`.
