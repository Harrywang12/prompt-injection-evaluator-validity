# Final confirmatory scientific-study freeze

Status: **CONFIRMATORY SCIENTIFIC ANALYSIS COMPLETE AND FROZEN**

- Scientific-state freeze timestamp (UTC): `2026-09-10T17:05:33Z`
- External preregistration: https://osf.io/9jrab
- Preregistration submission timestamp as recorded: August 19, 2026, 7:06:59 PM (timezone was not supplied; no UTC conversion is inferred)
- Preregistered scientific commit: `853eb6aa7c61e03896cdca3eb991fcf8debdc9cc`
- Frozen preregistration tag: `confirmatory-preregistered-v1`
- Confirmatory analysis results commit: `68d077c96424a7834e9cbc3fd65578b33f904bca`
- Final usable generation population: 4,993; final technical failures: 47
- Usable responses by model: Qwen 1,680; amended native Phi-3.5 1,634; SmolLM2 1,679
- Human-validation sample: 800, independently labeled by two annotators
- Pre-adjudication exact agreement: 591/800 (73.875%); seven-category Cohen's kappa: 0.597554
- Adjudication: 209 rows; 40 matched Annotator A, 155 matched Annotator B, and all 14 three-way disagreements were resolved by the protocol-defined consensus process
- Final adjudicated labels: 800/800 complete; final `AMBIGUOUS` rows: 0

## Frozen identifiers

| Artifact | SHA-256 |
|---|---|
| Prompt manifest | `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed` |
| Generation configuration | `3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284` |
| Usable-response manifest | `aa543f839be2d489374318ea46d182527d9bd988b07d13284fcc187f1e419f9f` |
| S0/S2 scorer artifact | `e98889194ab841957aa60cf0825543916a63324f710a319f4900b513186e64bf` |
| Master human sample | `548253edba237af76373be7ba5064d876a4a76b0f5367a3c5b0e8131477edd6f` |
| Sampling audit | `5476c6824705d93c8da06b1b06dc3f953aef4019e86b1046043699c0d002157f` |
| Final human ground truth | `20804593269be59b3578fb1e12f033d7b3044895775a21dc2195ca5bb53f11e7` |
| Final binary human outcomes | `10deeafa9f83f21f560649d5c4020e5defe5e51d165739afc4cbc9c3b1f19a9a` |
| Canonical analysis dataset | `634f4ef28c68696f8c7681fa83827bb12ab6568c5077e9ddf6c926bfe2bf6a3b` |
| Primary results | `79d5b0e2675bdc0f454711d1bda7e333a85e64fd9a816f559e998c76758e4545` |
| Bootstrap results | `61560609974ef2d00fe2266dd557e7930aa561f7e6723e5fe3926d253fe3a9c4` |
| GEE results | `911e78a28e15a811298d09a65394789fe4cbb9e50746d38d8508b37aac80ff1c` |
| Exploratory results | `d8d25349149b0371b99bafa2c529b4b6c76f2fbbe5c83d1371263437617536b5` |
| Private final-freeze manifest | `4e070cd5287243e4f72efb5f77b524cb3a2e82063d573bb18c0375db29141a41` |

## Protocol history and interpretation

No deviations from the frozen statistical analysis plan occurred during confirmatory analysis. The previously documented post-preregistration Phi-3.5 technical implementation amendment remained in effect; see `protocol/amendment_002_phi_generation_compatibility.md`. The original remote-code Phi failures remain preserved as provenance. The amendment retained the pinned repository, weights, model/tokenizer revisions, Transformers 5.15.0 environment, prompts, seed, and decoding settings, while changing Phi loading to the native Transformers Phi3 implementation. It was selected before scorer-human or hypothesis analysis.

H1 was rejected in the preregistered direction, RQ2 remains estimation-focused, and H3 was rejected after H1 opened the fixed-sequence gate. The primary calibrated-bootstrap zero-width intervals are retained transparently as consequences of the prespecified calibration and observed boundary condition; they are not interpreted as literal absence of population uncertainty. The registered sensitivity and GEE results remain part of the frozen record.

This freeze does not contain raw prompts, responses, or row-level human labels. Future manuscript edits do not alter the frozen scientific results. Any genuinely new analysis after this timestamp must be identified as post-hoc/exploratory unless it was already preregistered.
