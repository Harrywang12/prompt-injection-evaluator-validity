# Reproducibility

## Export provenance

This repository is a public-safe reproducibility export derived from a separately preserved authoritative private research archive. It intentionally contains no private Git history or historical private tags.

- Preregistration: <https://osf.io/9jrab>
- Original frozen preregistration tag: `confirmatory-preregistered-v1`
- Original frozen preregistration commit: `853eb6aa7c61e03896cdca3eb991fcf8debdc9cc`
- Original final confirmatory tag: `confirmatory-analysis-v1`
- Original final confirmatory commit: `2dbc2d960f17192cbfb3166566eaed1c349fe681`

The exact original history and private artifacts remain in the authoritative archive. Creating tags with those historical names in this new repository would misrepresent their provenance, so this export does not recreate them.

## Frozen generation design

The study crossed 1,680 independent base prompts with three models for 5,040 planned generation keys. The final usable population was 4,993 responses after 47 technical failures under the frozen no-retry/no-replacement rule.

| Model | Revision | Usable responses |
|---|---|---:|
| `Qwen/Qwen2.5-1.5B-Instruct` | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | 1,680 |
| `microsoft/Phi-3.5-mini-instruct` | `2fe192450127e6a83f7441aef6e3ca586c338b77` | 1,634 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | `31b70e2e869a7173562077fd711b654946d38674` | 1,679 |

Tokenizer revisions equaled model revisions. Generation used Transformers 5.15.0 on Google Colab Tesla T4 runtimes with CUDA 12.8, PyTorch 2.11.0+cu128, BF16, eager attention, batch size one, greedy decoding, `do_sample=false`, `max_new_tokens=128`, no custom stop strings, and generation seed `2026082203`.

The preregistered remote-code Phi implementation failed systematically. A documented post-preregistration compatibility amendment retained the repository, weights, revision, tokenizer, prompts, seed, and decoding settings but used the native Transformers Phi3 implementation. Original failures were preserved in the private archive. See [`protocol/amendment_002_phi_generation_compatibility.md`](../protocol/amendment_002_phi_generation_compatibility.md).

## Scoring

- **S0:** exact case-sensitive target substring anywhere in the unmodified raw response.
- **S2:** exact case-sensitive target at character position zero.

No case folding, whitespace stripping, or Unicode normalization was applied. S2 implies S0 by construction.

## Human validation

The 800-response human sample oversampled S0/S2 disagreements while retaining probability-sampled agreement controls. First-order inclusion probabilities and inverse-probability weights were frozen before human outcomes were analyzed. Two blinded annotators independently labeled all 800 rows; a third person adjudicated disagreements independently, followed by protocol-defined discussion for 14 three-way disagreements. The final adjudicated set had no ambiguous labels.

The public export omits all row-level annotation, mapping, sampling-key, and adjudication files.

## Statistical analysis

Population estimates use recorded inverse-probability weights. The primary uncertainty procedure used 9,999 task-stratified base-prompt cluster-bootstrap replicates with seed `2026082207`. The base prompt was the cluster, and sampled model responses belonging to a selected prompt were retained together. Identity-link inverse-probability-weighted GEE models with base-prompt robust clustering were preregistered robustness analyses.

The calibrated H1 and H3 intervals were zero-width because every sampled S0=1/S2=0 case was a strict human failure while calibration fixed scorer-stratum population totals. This is a boundary property of the prespecified estimator and observed sample; it does **not** imply literal absence of population uncertainty. The frozen report therefore also presents the preregistered uncalibrated-IPW sensitivity and GEE robust intervals.

No deviations from the frozen statistical analysis plan occurred during confirmatory analysis. The Phi technical compatibility amendment described above remained in effect.

## Frozen artifact identifiers

| Artifact | SHA-256 |
|---|---|
| Prompt manifest | `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed` |
| Generation configuration | `3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284` |
| Usable-response manifest | `aa543f839be2d489374318ea46d182527d9bd988b07d13284fcc187f1e419f9f` |
| S0/S2 scores | `e98889194ab841957aa60cf0825543916a63324f710a319f4900b513186e64bf` |
| Human sample | `548253edba237af76373be7ba5064d876a4a76b0f5367a3c5b0e8131477edd6f` |
| Sampling audit | `5476c6824705d93c8da06b1b06dc3f953aef4019e86b1046043699c0d002157f` |
| Final human ground truth | `20804593269be59b3578fb1e12f033d7b3044895775a21dc2195ca5bb53f11e7` |
| Binary human outcomes | `10deeafa9f83f21f560649d5c4020e5defe5e51d165739afc4cbc9c3b1f19a9a` |
| Canonical analysis dataset | `634f4ef28c68696f8c7681fa83827bb12ab6568c5077e9ddf6c926bfe2bf6a3b` |
| Primary results | `79d5b0e2675bdc0f454711d1bda7e333a85e64fd9a816f559e998c76758e4545` |
| Bootstrap results | `61560609974ef2d00fe2266dd557e7930aa561f7e6723e5fe3926d253fe3a9c4` |
| GEE results | `911e78a28e15a811298d09a65394789fe4cbb9e50746d38d8508b37aac80ff1c` |

Hashes identify private artifacts without redistributing their contents. Public-safe aggregate outputs are under `confirmatory/`.

## Intentionally omitted artifacts

- Raw prompts and source-text-bearing prompt manifests.
- Raw model-response corpora and technical terminal records.
- Completed row-level human annotations and confidence/notes fields.
- Private sampling strata, inclusion-probability linkages, adjudication keys, and consensus working files.
- Restricted or redistribution-sensitive upstream dataset contents.
- Model weights and caches.

The generation, scoring, sampling, and analysis procedures remain documented in `protocol/`, `src/`, and `scripts/`. Reconstruction requires obtaining upstream data and models under their respective licenses and access conditions.
