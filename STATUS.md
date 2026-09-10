# Study Status

## DONE

- Read and froze the preregistered hypothesis, annotation rubric, and analysis
  plan.
- Recorded the initial repository state in `research_log.md`.
- Verified the scoring methods in the three required primary sources.
- Identified KEY-E for semi-dynamic/dynamic objectives as the lexical scorer
  most directly corresponding to the preregistered audit.
- Audited the availability, schema, provenance, and suitability of all three
  priority candidate sources.
- Built and validated a reproducible 50-item pilot with immutable raw outputs.
- Implemented and tested the primary KEY-E scorer and separate sensitivity
  scorers.
- Created and validated the blinded pilot annotation file and instructions.
- Validated and preserved 50 completed human annotations against the frozen
  handoff.
- Completed the preregistered pilot analysis and partial-compliance
  sensitivity analysis.
- Generated machine-readable metrics, a report, figures, and a `MODIFY`
  decision. The full-scale study has not begun.
- Formalized Amendment 001 prospectively for Pilot 2 without changing Pilot 1.
- Froze the Pilot 2 protocol and balanced 672-candidate design before outcome
  generation.
- Preserved 672/672 usable Pilot 2 raw responses and applied the frozen KEY-E
  scorer separately (84 positive, 588 negative, zero failures).
- Created and validated the 100-row blinded Pilot 2 human sample with 50
  randomly sampled records from each lexical stratum.
- Validated and preserved all 100 independently completed Pilot 2 human
  annotations.
- Completed the raw stratified-sample and weighted finite-population Pilot 2
  analyses, figures, Pilot 1 comparison, and sensitivity analysis.
- Selected `CONTINUE`; the strict hypothesis receives qualified support, the
  lenient sensitivity does not, and the refusal-quotation mechanism receives
  no support.
- Froze and completed the explicitly exploratory six-implementation lexical
  scorer-sensitivity analysis on the unchanged 672 Pilot 2 responses.
- Preserved per-example, pairwise, task, target, and raw/weighted human-
  comparison results under `results/scorer_sensitivity/`.
- Selected exploratory scorer-sensitivity decision `CONTINUE`: overall ASR
  changes modestly, but prefix semantics materially affect one task and strict
  human agreement. No follow-up experiment has begun.
- Completed the final construct-validity preregistration package: exact model
  revisions, fresh-prompt allocation, generation/scoring rules, human rubric,
  probability sampling, inferential fallbacks, multiplicity, and readiness
  audit are frozen without generating confirmatory outputs.
- Replaced the blocked Gigaword summarization source before preregistration
  with the pinned U.S. federal BillSum `test` split under documented CC0-1.0
  terms. Froze an 8,000-token all-model/all-variant eligibility rule; 3,268 of
  3,269 rows are eligible. No final source sample or response was generated.
- Recorded the successful Google Colab Tesla T4 preflight with CUDA 12.8,
  PyTorch 2.11.0+cu128, native BF16, and Transformers 5.15.0.
- Submitted the frozen confirmatory design to OSF at https://osf.io/9jrab on
  August 19, 2026, 7:06:59 PM. The preregistered scientific state is commit
  `853eb6aa7c61e03896cdca3eb991fcf8debdc9cc`; no confirmatory model outputs or
  human annotations existed before submission.
- Activated the registered study for generation preparation at
  `2026-08-19T19:26:22-0400`, materialized the frozen 1,680-prompt private
  manifest, verified zero exploratory overlap, and prepared an idempotent
  5,040-key Colab runner. No victim-model response was generated.
- Corrected a post-registration, pre-generation packaging inconsistency:
  generic pilot `requirements.txt` would downgrade Transformers to 4.52.4,
  while the confirmatory environment requires 5.15.0. Added a separate
  confirmatory dependency file and clean-bundle builder without changing the
  scientific design. No victim-model response existed or was generated.
- Froze the original 5,040-record confirmatory generation census after a
  systematic Phi compatibility incident: Qwen 1,680/1,680 successful, Phi
  0/1,680 successful, and SmolLM2 1,679/1,680 successful. Original terminal
  records and their private snapshot/backup are preserved.
- Documented Amendment 002 after a synthetic-only diagnostic established that
  the exact pinned Phi weights and tokenizer generate successfully under
  Transformers 5.15.0 through the native Phi3 implementation. Prepared a
  separate Phi-only, native-code, immutable/resumable runner; it has not been
  used for confirmatory generation.
- Froze the completed confirmatory generation population: 4,993 usable
  successful nonempty responses (Qwen 1,680, amended native Phi 1,634,
  SmolLM2 1,679) and 47 final technical failures. No further generation,
  retry, or replacement is permitted.
- Applied the frozen S0/S2 rules privately and validated the structural
  implication S2=>S0. Drew the preregistered 800-response probability sample
  with seed `2026082204`: 480 disagreement records and 320 agreement controls.
  Prepared independently ordered, blinded Annotator A/B files containing the
  same 800 anonymous items. No ASR, hypothesis analysis, human agreement, or
  human labeling was performed.
- Preserved and validated both completed 800-item human annotation files. With
  explicit authorization, reconstructed the completed CSVs using the frozen
  non-human fields after Numbers normalized CRLF to LF in 45 `legitimate_input`
  cells; all human labels, confidence values, and notes remain unchanged.
- Computed pre-adjudication seven-category human-human agreement and prepared
  the exact blinded 209-item adjudication set. No scorer-human, ASR, H1/RQ2/H3,
  bootstrap, GEE, model, or task analysis was performed.
- All 34 directly applicable tests pass. The full suite has 76 passes and two
  unchanged, unrelated Pilot 2 source-fixture failures in the user-owned
  untracked external checkout.
- Preserved and validated the completed 209-row independent adjudicator CSV.
  No mechanical reconstruction was required. The frozen rule resolved 40 rows
  by matching Annotator A and 155 by matching Annotator B; 14 genuine
  three-way disagreements remain blank pending human consensus discussion.
- All 40 directly applicable confirmatory tests pass. The full suite has 82
  passes and the same two unrelated historical Pilot 2 source-fixture failures
  in the user-owned untracked external checkout.
- Preserved and validated the completed 14-row three-person consensus file;
  no mechanical reconstruction was required. Applied all 14 decisions without
  changing any original A/B/adjudicator label and froze the complete private
  800-row adjudicated human ground truth. No final label is `AMBIGUOUS`.
- All 46 directly applicable confirmatory tests pass. The full suite has 88
  passes and the same two unrelated historical Pilot 2 source-fixture failures
  in the user-owned untracked external checkout.
- First preregistered confirmatory scorer–human analysis executed on
  2026-09-10 after the 800-row ground truth was frozen. All six private input
  hashes matched; the canonical analysis dataset SHA-256 is
  `634f4ef28c68696f8c7681fa83827bb12ab6568c5077e9ddf6c926bfe2bf6a3b`.
- The 9,999-replicate, task-stratified base-prompt cluster bootstrap used seed
  `2026082207`; all main estimands retained 9,999 valid replicates. H1 rejected
  under its registered CI rule, opening the fixed-sequence gate; H3 then also
  rejected. RQ2 remains estimation-focused. No SAP deviation occurred.
- All 53 confirmatory tests pass. The repository-wide suite has 95 passes and
  the same two unrelated historical Pilot 2 fixture failures caused by the
  missing file in the user-owned untracked external checkout.
- **CONFIRMATORY SCIENTIFIC ANALYSIS COMPLETE AND FROZEN.** The scientific
  state was frozen at `2026-09-10T17:05:33Z`; the private final-freeze manifest
  SHA-256 is
  `4e070cd5287243e4f72efb5f77b524cb3a2e82063d573bb18c0375db29141a41`.
  The final human-ground-truth and canonical analysis-dataset hashes remain
  `20804593269be59b3578fb1e12f033d7b3044895775a21dc2195ca5bb53f11e7`
  and `634f4ef28c68696f8c7681fa83827bb12ab6568c5077e9ddf6c926bfe2bf6a3b`.
- H1 and gated H3 were rejected under their registered rules; RQ2 remains
  estimation-focused. No deviation from the frozen statistical analysis plan
  occurred during analysis. The documented post-preregistration Phi technical
  implementation amendment in `protocol/amendment_002_phi_generation_compatibility.md`
  remained in effect.
- All 60 directly applicable confirmatory/freeze tests pass. The full suite has
  102 passes and the same two unrelated historical Pilot 2 fixture failures
  caused by the absent file in the user-owned untracked external checkout.

## IN PROGRESS

- Manuscript drafting is authorized. Frozen confirmatory artifacts must remain
  unchanged; genuinely new analyses must be labeled post-hoc/exploratory unless
  already preregistered.

## BLOCKED

- None in the computational preparation. Progress is paused at the required
  independent-human-annotation boundary.

## HUMAN ACTION REQUIRED

- Supply stable identities for Annotators A/B and an independent adjudicator.
- Add remaining Colab provenance fields (date/tier/VRAM/driver/Python,
  supporting-package versions, and diagnostic-log location) when available.
- No human-labeling action remains.
