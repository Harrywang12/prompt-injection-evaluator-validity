# Preregistration readiness audit

Audit date: 2026-08-18 (America/Toronto)

Audit basis: source-substitution audit beginning at repository commit `ccc35f2b0012d9126484c2c5f2aebbad04d53c6e`. No confirmatory source sample was drawn and no victim-model response was generated.

## Classification

| Item | Status | Evidence or required action |
|---|---|---|
| Prior-work disclosure | RESOLVED | Pilot 1/Pilot 2 are preliminary; 672-response scorer study is exploratory; hypothesis timing is explicit. |
| H1/RQ2/H3 hierarchy | RESOLVED | H1 sole primary; RQ2 estimation; H3 gated secondary. |
| Construct and binary definitions | RESOLVED | Frozen in `final_annotation_manual.md`. |
| Synthetic rubric examples | RESOLVED | At least two per category, created before confirmatory outputs. |
| Annotator blinding fields | RESOLVED | Model, scorers, stratum, weights, and peer labels omitted. |
| Model-identity blinding feasibility | RESOLVED | Model metadata is omitted and rows independently randomized; unavoidable self-identification in raw responses is not redacted and is a limitation. |
| Adjudicator independence | RESOLVED | Must be a third person distinct from A and B. |
| Personnel roles and independence | RESOLVED | A and B independently label the same rows; the adjudicator must be a distinct third person; all are blinded as frozen. |
| Personnel identities | HUMAN INPUT REQUIRED | Stable names/IDs are not present. Role placeholders are sufficient in this preregistration draft unless the selected registry requires names, but identities and acceptance are mandatory before annotation. |
| Exact model/tokenizer revisions | RESOLVED | Three immutable Hugging Face Git SHAs recorded. |
| Model licenses and repository access | RESOLVED | Apache-2.0, MIT, Apache-2.0; repositories were publicly accessible and nongated at audit. |
| CUDA hardware preflight | RESOLVED | The operator reports PASS on Google Colab Tesla T4: CUDA 12.8, PyTorch 2.11.0+cu128, native BF16, Transformers 5.15.0, all pinned revisions, batch 1, greedy decoding, and 128 tokens. Only trivial diagnostics were used. |
| Remaining Colab provenance metadata | HUMAN INPUT REQUIRED | Date/tier/VRAM/driver/Python/supporting-package versions and retained log path remain placeholders. They are activation provenance, not blockers to registering the already fixed design. |
| Source paths, hashes, operational splits | RESOLVED | Six wrapper task sources remain frozen; BillSum U.S. `test` is pinned to an exact repository revision and parquet hash; `ca_test` is excluded. |
| Dataset-use audit | RESOLVED | All seven sources, operational splits, owners, access conditions, terms, research-use status, and public-artifact rules are documented in `final_dataset_use_audit.md`. |
| Gigaword removal / BillSum authorization | RESOLVED | Gigaword was removed pre-registration because LDC authorization was unavailable. Official BillSum sources identify U.S. federal `test` as GovInfo-derived CC0-1.0; the California split is excluded. |
| Freshness and deduplication rule | RESOLVED | Source-ID and normalized content-hash exclusions cover Pilot 1/Pilot 2. |
| Tokenizer context eligibility rule | RESOLVED | BillSum requires all 24 complete rendered prompts per row to be at most 8,000 tokens. The pinned test split yields 3,268/3,269 eligible rows; one context rejection. No truncation or threshold change is allowed. |
| Task/category allocation | RESOLVED | 1,680 total; 480 generative and 1,200 classification; eight cells balanced per task. |
| Injection and target allocation | RESOLVED | Four templates by two targets per task, fixed before generation. |
| Generation configuration | RESOLVED | Prompt formatting, decoding, seed, stop, retry, malformed, and failure rules frozen. |
| S0/S2 scorer definitions | RESOLVED | Exact rules and subset relation frozen. |
| Human sampling algorithm | RESOLVED | 800; up to 480 disagreements; at least 320 probability controls; inclusion probabilities retained. |
| Ambiguous and missing-label rules | RESOLVED | Complete A/B labels required; independent adjudication; unresolved ambiguous complete-case exclusion plus bounds. |
| Statistical estimands and inference | RESOLVED | Paired weighted estimands, 9,999-replicate cluster bootstrap, and fixed fallbacks frozen. |
| Multiplicity | RESOLVED | H1 alpha .05; H3 fixed sequence; RQ2 estimation; named exploratory BH families. |
| Cross-document consistency | RESOLVED | Frozen values and mathematical constraints pass `final_preregistration_consistency_audit.md`; no scientific inconsistency found. |
| External registry and owner | HUMAN INPUT REQUIRED | Authorized researcher must select registry and submit; this package does not preregister on the user's behalf. |
| Confirmatory output generation | RESOLVED | None performed. |

## Readiness conclusion

**READY FOR EXTERNAL PREREGISTRATION.** Every scientific and analytical choice is frozen and internally consistent, the Colab hardware preflight is resolved, and all active dataset sources have a documented planned-use determination. Gigaword has been replaced by the pinned U.S. federal BillSum `test` split before registration and before data collection. No item remains `BLOCKING` for external preregistration.

Personnel names/IDs, remaining Colab provenance fields, and registry owner/details remain `HUMAN INPUT REQUIRED`. Role placeholders are methodologically adequate in this draft unless the selected registry requires names, but named personnel and acceptance are mandatory before annotation. No confirmatory work may begin merely because these documents are committed: the external preregistration and all activation checks remain required.
