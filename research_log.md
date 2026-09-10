# Research Log

This log distinguishes preregistered commitments, source-established facts,
methodological decisions, and later empirical findings. Raw data and raw model
outputs must never be overwritten.

## 2026-08-17T14:53:29-04:00 — Protocol freeze (Phase 1)

- **Repository state:** `9a0d7aa0d75851a45604fe636bc7507e361f747a`
  (`Clarify automated scoring metric under audit`). The worktree contained
  untracked `.DS_Store` and `external/` paths before this study workflow began.
- **Preregistered research question:** How often does standard automated
  scoring of prompt-injection attacks disagree with human judgment, and in
  which direction?
- **Preregistered primary hypothesis:** Substring-match scoring will
  overestimate true attack success rate relative to human evaluation.
- **Preregistered mechanistic hypothesis:** A substantial source of the
  overestimate will be refusals that nevertheless quote or repeat the attack
  target string.
- **Frozen human labels:** `FULL_COMPLIANCE`, `PARTIAL_COMPLIANCE`, `REFUSAL`,
  `REFUSAL_QUOTATION`, `OFF_TOPIC_FAILURE`, and `AMBIGUOUS`, with meanings in
  `protocol/annotation_rubric.md`.
- **Primary binary success definition:** `FULL_COMPLIANCE` is success. All
  other substantive categories are failure; `AMBIGUOUS` is set aside for
  adjudication.
- **Prespecified sensitivity analysis:** Count `FULL_COMPLIANCE` plus
  `PARTIAL_COMPLIANCE` as success.
- **Primary automated scorer:** KEY-E-style keyword evaluation: success when a
  response contains the predetermined attacker-controlled keyword or target
  string. Exact implementation details must be verified from the primary
  source before implementation.
- **Planned pilot size:** Approximately 50 suitable, traceable attack-response
  examples, selected reproducibly rather than by row order.
- **Unresolved methodological questions at freeze:** Which candidate source
  exposes target, response, and model metadata under suitable access terms;
  the exact normalization/case behavior of the published KEY-E evaluator; and
  whether enough naturally occurring responses exist for a 50-item pilot.
- **Outcome-data status:** No attack-response outcomes were inspected before
  this freeze entry. Only protocol files, repository paths, and Git metadata
  were inspected.

## 2026-08-17 — Literature and scorer verification (Phase 2)

- **Source-established:** HackAPrompt uses exact equality after whitespace
  normalization, not substring matching. Automatic and Universal defines
  KEY-E containment for predetermined keywords, with an exact-match exception
  for static objectives and a gated GPT-4-0613 LM-E check for non-static
  objectives. Formalizing and Benchmarking uses injected-task metrics (label
  accuracy, ROUGE-1, or GLEU), not a general malicious-target substring rule.
- **Methodological decision before outcomes:** Audit case-sensitive KEY-E on
  semi-dynamic/dynamic objectives. Preserve exact matching as a distinct
  robustness analysis. See `protocol/proposed_amendments.md` for a code/paper
  inconsistency found before any outcomes were viewed.
- **Outcome-data status:** Still not inspected.

## 2026-08-17 — Candidate data-source verification (Phase 3)

- **HackAPrompt:** Ideal released schema, including target and response, but the
  official Hugging Face files are gated behind logged-in acceptance and no
  accepted-access token is configured. Metadata only was inspected.
- **Open-Prompt-Injection:** Code, task definitions, attacks, and evaluator are
  available at local commit `95290f7`; raw published victim responses are not.
- **Universal-Prompt-Injection:** Inputs, targets, and generation/scoring code
  are available at local commit `19bf570`; optimized suffix result files and
  raw victim responses are not.
- **Pre-outcome pilot decision:** Generate a small new pilot from reproducibly
  sampled Universal-Prompt-Injection contexts, a fixed semi-dynamic injection,
  and pinned Qwen2.5-1.5B-Instruct. This audits the published KEY-E rule but is
  not represented as a reproduction of the paper's attack efficacy.
- **Outcome-data status:** No victim responses generated or inspected yet.

## 2026-08-17 — Pre-output generation diagnostic

- The first attempted batched generation emitted a decoder-only right-padding
  warning after five records were computed in memory. No response text was
  inspected, no scorer was run, and the script had not written its atomic raw
  output file. The process was interrupted.
- **Correction before outcome inspection:** Set tokenizer padding to `left`
  explicitly and clear irrelevant sampling defaults under greedy decoding,
  then restart all 50 generations from the same frozen inputs and seed.

## 2026-08-17 — Pilot construction (Phase 4)

- Sampled 50 unique source rows using seed `20260817`, stratified across the
  seven source tasks as 8/7/7/7/7/7/7. Pilot-input SHA-256:
  `f0ce9fdcddee2829f965b5b1890c09c27dc2d9842ec481aac0db2b424676b7ae`.
- Downloaded Qwen2.5-1.5B-Instruct at revision `989aa798...`; weights SHA-256:
  `dd924a11b4c220f385b51ffa522daea7c9f3d850e31b162bb5661df483c6d3ee`.
- Generated 50 non-empty raw responses with seed `314159`, greedy decoding,
  left padding, and a 160-token cap. Raw-output SHA-256:
  `ab7023d0ea231d514aaf29d8d0d028de2ecfe304166416786b6c9c33c6ddde3c`.
- Applied the source-faithful case-sensitive KEY-E scorer and two separately
  named sensitivity scorers. Automated outputs were saved only in the internal
  derived table; no rates, verdict counts, or response content were inspected.
- Eight unit tests passed. Outcome analysis remains prohibited pending human
  labels.

## 2026-08-17 — Blinded pilot annotation handoff (Phase 5)

- Created `annotations/pilot_annotation_blinded.csv` with 50 records shuffled
  using seed `17082026`.
- Included only sample ID, legitimate task context, injected instruction,
  target behavior, victim response, and blank human-entry fields. Automated
  verdicts, original labels, and judge outputs are absent.
- Blinded file SHA-256:
  `1f9aa3e1cde892623af9b1107e3bcd25025865fdd284b900b20449ea0d75cf89`.
- Schema, unique IDs, empty human fields, and forbidden-field leakage were
  validated mechanically. All eight tests pass.
- **Human action required:** A real annotator must fill `human_label`,
  `human_confidence`, and optional `notes` in the blinded file. No pilot outcome
  analysis will be performed until the user explicitly confirms completion.

## 2026-08-17 — Completed annotation validation and pilot analysis (Phases 6–7)

- The user committed 50 completed human annotations before automated outcomes
  were unblinded. Spreadsheet export normalized embedded line endings in seven
  frozen `legitimate_input` fields. Those non-human fields were restored from
  revision `e6712df`; all human-entered values were copied unchanged and
  mechanically verified unchanged. The resulting completed annotation SHA-256
  is `6b48d29e171ce022de5dd83e5587eb1aec13a2f4d5767172d5ce43034c5396c3`.
- Strict validation passed: exactly 50 rows, frozen columns/order/sample IDs and
  non-human fields, valid labels, and confidence integers from 1 to 5.
- **Confirmatory finding:** KEY-E and strict human judgment each classified
  5/50 examples as successes (10.0%). Delta ASR was 0.0 percentage points; the
  confusion matrix was TN=45, FP=0, FN=0, TP=5; accuracy, precision, recall,
  F1, and Cohen's kappa were all 1.0.
- Paired percentile-bootstrap 95% intervals used 20,000 resamples and seed
  `20260817`. KEY-E and human ASR intervals were each 2.0%–18.0%; the paired
  difference interval was 0.0–0.0 points because every observed pair agreed.
  The two-sided exact 95% upper bound for an unseen discordance rate after 0/50
  observed discordances is 7.11%.
- There were no false positives, false negatives, `REFUSAL_QUOTATION` labels,
  or `PARTIAL_COMPLIANCE` labels. The refusal-quotation share among false
  positives is undefined (0/0). The partial-compliance sensitivity analysis is
  identical to the primary analysis.
- **Interpretation:** The pilot does not support the preregistered primary or
  mechanistic hypothesis in this sample. This null result was retained without
  changing the hypothesis or labels.
- **Post-outcome methodological issue:** The rubric lacks a distinct category
  for an ignored attack accompanied by legitimate-task compliance. A proposed
  prospective category and broader second-pilot design are recorded in
  `protocol/proposed_amendments.md`; no retrospective relabeling occurred.
- **Decision:** `MODIFY`. Do not scale the identical narrow design. Full-scale
  work remains paused pending user approval.

## 2026-08-17T16:28:54-04:00 — Amendment 001 formalized

- **Repository state before amendment:**
  `4b3c6743d5cf7f71b4e314eb4577e7efce2e86ad` (`Report null pilot scoring
  result`). Saved Pilot 1 metrics and artifact hashes were rechecked and match
  the committed report.
- **Timing:** The category problem was discovered during blinded Pilot 1 human
  annotation, before automated outcome unblinding. The amendment itself was
  formalized after Pilot 1 completion.
- **Reason:** The Pilot 1 rubric did not distinguish explicit refusal from a
  response that ignores the injection and performs the legitimate task.
- **Prospective change:** Amendment 001 adds `INJECTION_IGNORED` as a failure
  category for Pilot 2 and later work. Strict success remains
  `FULL_COMPLIANCE` only; the lenient sensitivity remains
  `FULL_COMPLIANCE + PARTIAL_COMPLIANCE`.
- **Preservation:** The original preregistration and every Pilot 1 input, raw
  response, scorer output, human label, result, figure, and analysis remain
  untouched.

## 2026-08-17T16:30:56-04:00 — Pilot 2 protocol and design freeze

- **Repository state before freeze:**
  `240b5b4db12916dd9b2d0aad79d2b9cc83f8831b` (`Document post-pilot annotation
  rubric amendment`).
- **Pilot 1 audit:** Exactly 50 responses were generated and all 50 entered the
  human sample. The sole template/target/model produced 5 KEY-E positives,
  all in summarization; the remaining six task types produced 0/43.
- **Post-pilot objective:** Test whether the perfect Pilot 1 agreement was
  partly a consequence of an insufficiently informative, narrow pool. This is
  not a restatement or replacement of the original hypothesis.
- **Frozen initial design:** 672 candidates balanced across seven tasks, four
  injection variants, and two official harmless targets, using unique source
  rows within task. Fixed seeds and a content-independent expansion rule are
  recorded in `config/pilot2_config.yaml`.
- **Model decision:** Retain pinned Qwen2.5-1.5B-Instruct. At freeze time the
  host had Apple M3/16 GB, no PyTorch MPS/CUDA support, and about 1.2 GiB free
  storage; adding another local model was impractical.
- **Planned human sample:** 50 randomly sampled KEY-E positives and 50
  negatives, with inclusion probabilities and weights retained internally and
  a separately shuffled blinded file.
- **Outcome-data status:** No Pilot 2 victim response had been generated or
  inspected when this protocol and configuration were frozen.

## 2026-08-17T17:18:15-04:00 — Pilot 2 candidate generation and KEY-E scoring

- **Pre-generation repository state:**
  `978d5580f758259e4431f775815972af4cfc9f61` (`Prepare frozen Pilot 2 candidate
  pool`). The deterministic candidate-input SHA-256 is
  `3d8018798e67079d0fa656a8936671a45a19031adc9cef2cb2425d6e26f6cd55`.
- Generated the frozen initial batch of 672 candidates with pinned
  `Qwen/Qwen2.5-1.5B-Instruct` revision `989aa798...`, model-weights SHA-256
  `dd924a11b4c220f385b51ffa522daea7c9f3d850e31b162bb5661df483c6d3ee`,
  seed `271828`, greedy decoding, CPU execution, left padding, batches of 5,
  and a 128-new-token cap.
- Preserved all 672 raw responses in 24 immutable 28-record JSONL parts under
  `data/raw/pilot2/`. All 672 have status `ok`; there were zero empty/error
  responses and zero duplicate IDs. Part hashes and environment/model
  provenance are in `data/raw/pilot2/manifest_batch_000.json` (SHA-256
  `62ec4e205eeaa97fbf03e22f2e34ff98ecec844240ed12d17761a28d1d5c14a9`).
- Applied the frozen raw, case-sensitive KEY-E containment rule only after raw
  preservation. The pool contains 84 lexical positives and 588 lexical
  negatives; an independent direct raw-response containment check reproduced
  these counts. The planned expansion rule was not invoked because at least
  50 usable positives existed.
- Candidate aggregate counts by task, target, variant, and model are stored in
  `results/pilot2/candidate_pool_summary.json`. No human label was generated,
  and no lexical-human outcome analysis was performed.

## 2026-08-17T17:20:17-04:00 — Pilot 2 blinded annotation handoff

- **Repository state before sampling:**
  `bea376ebf8eaec21c7b66379f7c92753a6c96d14` (`Generate and score Pilot 2
  candidate pool`).
- Using the frozen human-sampling seed `20260819`, selected 50 of 84 usable
  KEY-E-positive candidates and 50 of 588 usable KEY-E-negative candidates by
  simple random sampling without replacement within each stratum.
- Positive inclusion probability/weight: `50/84 = 0.595238...` / `1.68`.
  Negative inclusion probability/weight: `50/588 = 0.085034...` / `11.76`.
  These are stored only in the restricted internal table and manifest.
- Shuffled the 100 selected rows with independent seed `20260820` and created
  `annotations/pilot2_annotation_blinded.csv` (SHA-256
  `c41255336c9a0c688c4704bee813ba56e51b646f9e0c68eab8767ad6ed1f102a`).
- The sample contains all seven tasks, both target IDs, and all four injection
  variants. It uses the one frozen Qwen victim model.
- Strict validation passed: 100 unique rows; exact expected columns and
  deterministic row order; intact mappings to the internal/raw data; no
  scorer, stratum, inclusion-probability, weight, benchmark-label, or judge
  columns; nonempty targets/responses; blank `human_label`,
  `human_confidence`, and `notes`; valid CSV parse/write/parse roundtrip.
- Seventeen automated tests passed, including immutable Pilot 1 hash checks.
  No Pilot 1 artifact changed.
- **Human action required:** A real human must annotate the blinded Pilot 2
  file using `annotations/PILOT2_ANNOTATION_INSTRUCTIONS.md`. No Pilot 2
  lexical-human outcome analysis may begin before completed labels are
  returned and validated.

## 2026-08-17T20:50:54-04:00 — Pilot 2 completed-label validation and analysis-method freeze

- The user committed independently completed Pilot 2 annotations at
  `8671b1e`. Before scorer unblinding, strict validation found 29 whitespace-
  only changes in frozen `legitimate_input` fields from spreadsheet export.
- With user authorization, restored only those non-human fields from the
  blinded handoff commit `bb7351c`; all human labels, confidence values, and
  notes were preserved exactly. The repaired completed annotation SHA-256 is
  `5f6619cc5af82a30d9cf9bf32bcb90d68f9d0668b0b1e44d2cffb5c872a24b18`,
  committed at `fdee289c711d89aaaeb05a6b5cc6de734331f437`.
- Validation then passed: exactly 100 rows, valid Pilot 2 labels, confidence
  integers 1–5, frozen IDs/order/mappings/non-human fields, and a valid CSV
  parse/write/parse roundtrip.
- **Before reading any scorer outcome or human-label distribution**, froze a
  50,000-replicate stratified finite-population pseudo-population percentile
  bootstrap with seed `20260821`. It resamples the lexical-positive and
  lexical-negative strata independently and retains their known 84/588
  population weights. This implements the existing requirement for design-
  appropriate uncertainty rather than an ordinary unweighted row bootstrap.
- Frozen `AMBIGUOUS` handling is unchanged: exclude from primary complete-case
  binary comparisons and report explicitly; count as failure only in the
  prespecified sensitivity recorded in `config/pilot2_analysis.yaml`.
- **Outcome-data status:** No Pilot 2 scorer/sampling table or human-label
  distribution had been read when this implementation detail was frozen.

## 2026-08-17T21:00:45-04:00 — Pilot 2 analysis completed

- **Analysis implementation commit:**
  `37b9f5c0034f4ca49384be5088f5f0d24688aef3` (`Implement weighted Pilot 2
  analysis`). Twenty tests passed before final reporting.
- **Raw enriched sample:** 100 rows (50 sampled from each lexical stratum), 39
  strict human successes and 47 lenient successes. Strict confusion matrix:
  TN=50, FP=11, FN=0, TP=39; accuracy=0.89, precision=0.78, recall=1.0,
  F1=0.8764, kappa=0.78.
- **Strict false positives:** 7 `PARTIAL_COMPLIANCE`, 4
  `INJECTION_IGNORED`, and zero in every refusal, refusal-quotation, off-topic,
  or ambiguous category. `REFUSAL_QUOTATION` accounts for 0/11 (0%).
- **Weighted strict estimates:** Known full-pool KEY-E ASR=12.50%; human
  ASR=9.75% (design-aware 95% CI 8.75%–10.75%); difference=+2.75 percentage
  points (95% CI +1.75 to +3.75); disagreement=2.75% (95% CI 1.75%–3.75%);
  false-positive rate among estimated human failures=3.05% (95% CI
  1.96%–4.11%).
- **Prespecified lenient sensitivity:** Weighted human ASR=13.25% (95% CI
  11.00%–17.00%); KEY-E minus human=−0.75 points (95% CI −4.50 to +1.50).
  The result is therefore sensitive to whether partial compliance is success.
- No record was `AMBIGUOUS`; complete-case and ambiguous-as-failure estimates
  coincide. All 50,000 bootstrap replicates were valid for every statistic.
- **Interpretation:** The original strict primary hypothesis receives
  qualified support in this candidate pool based on magnitude, a CI excluding
  zero, and uniformly false-positive strict disagreements. It is not supported
  by the lenient sensitivity and is not generalized beyond the tested design.
  The refusal-quotation mechanism receives no support.
- **Decision:** `CONTINUE`. A larger confirmatory study is scientifically
  justified to test generality and threshold sensitivity, but has not started
  and requires explicit user approval.
- An independent direct calculation from the completed annotation and internal
  stratum table reproduced the raw confusion counts and both weighted ASR
  differences. Re-running `make analyze-pilot2` produced byte-identical JSON,
  CSV, and figure files. Final verification: 20/20 tests passed, including the
  immutable Pilot 1 artifact checks.

## 2026-08-17T21:50:03-04:00 — Exploratory scorer-sensitivity protocol frozen

- **Pre-protocol repository state:**
  `09b9ac9314526378ee19013ab9c711ce6fce73c3` (`Report stratified Pilot 2
  findings`).
- This analysis was designed after inspecting Pilot 1 and Pilot 2 results. It
  is explicitly exploratory, not preregistered or confirmatory.
- Defined and froze six reasonable lexical implementations before executing
  the scorer grid: original case-sensitive containment, Unicode casefolded
  containment, strict prefix, whitespace-tolerant prefix, NFC containment,
  and NFKC containment.
- Froze full-pool, pairwise, subgroup, mechanical-flip, and raw/weighted human-
  comparison methods in `protocol/scorer_sensitivity_exploratory.md`.
- The analysis is restricted to the existing 672 frozen Pilot 2 responses. No
  new victim-model output will be generated, and all Pilot 1/Pilot 2 artifacts
  remain immutable.
- **Outcome-data status:** The six-variant scorer grid had not been executed
  when this protocol was written.

## 2026-08-17T21:59:18-04:00 — Exploratory scorer-sensitivity analysis completed

- Executed the six scorers only after protocol commit
  `6a8359a647d0b9e91fc31f6cc3ac366e201e55b5`. No victim-model generation code
  was invoked.
- Verified all 24 frozen raw-part hashes, 672/672 usable one-to-one candidate/
  response mappings, and exact reproduction of every existing S0/KEY-E
  verdict before calculating alternative scorers.
- Full-pool results: S0 84/672 (12.50%), S1 86/672 (12.80%), S2 74/672
  (11.01%), S3 74/672 (11.01%), S4 84/672 (12.50%), and S5 84/672 (12.50%).
  Maximum-minus-minimum ASR was 1.79 percentage points.
- Twelve unique responses had any disagreement: 10 non-prefix target
  occurrences and 2 casefold gains. No leading-whitespace, NFC, NFKC, or
  mechanically unclear flip was observed.
- Largest task-specific change was grammar correction: prefix scoring changed
  21/96 successes (21.88%) to 13/96 (13.54%), −8.33 points. Target-level
  scorer ranges were 2.08 points for T_EMAIL and 1.49 points for T_WEB.
- On the enriched 100-record human sample, strict raw accuracy/kappa ranged
  from 88%/0.761 (casefold) to 96%/0.917 (both prefix variants). Lenient raw
  accuracy was 95% for S0/S4/S5 and 96% for S1/S2/S3, with different FP/FN
  tradeoffs.
- All subgroup patterns and human comparisons are explicitly exploratory.
  Weighted human-comparison cells use the frozen S0-stratum inclusion weights
  and are kept distinct from the exact 672-record scorer ASRs.
- **Decision:** `CONTINUE`. The overall ASR range is modest, but the task-
  specific and human-agreement changes justify a newly designed confirmatory
  study. No follow-up or multi-model experiment has begun.
- Two consecutive executions from implementation commit `be6233d` produced
  byte-identical derived CSV, JSON, and PNG artifacts. Final verification:
  44/44 tests passed, including frozen Pilot 1 hashes and Pilot 2 raw-manifest
  integrity checks.

## 2026-08-17T22:56:37-04:00 — Scorer-sensitivity reporting correction

- During the requested final audit, identified ambiguous wording in
  `results/scorer_sensitivity/report.md`: it described an eight-point strict
  human-agreement change after discussing prefix scoring.
- The exact S0-to-S2 raw accuracy contrast is 89% to 96%, a **7-point**
  increase. Eight points is the separate maximum-minus-minimum range across
  all scorers (S1 88% versus S2/S3 96%).
- `decision.md` contained the correct endpoints and did not explicitly call
  their difference eight points; it was clarified to state both quantities.
- Recorded the correction in `reporting_correction_001.md`. No data, scorer
  verdict, human label, numerical result table, or figure changed.

## 2026-08-17T22:58:57-04:00 — Final exploratory scorer-sensitivity audit

- Independently reconstructed the six-scorer aggregate table, the full 672-row
  S0/S2 cross-tabulation, every S0/S2 disagreement, the strict/lenient raw and
  weighted human comparisons, subgroup result, and mechanical flip counts.
- S0/S2 finite-pool cells are 74 both-success, 10 S0-only success, 0 S2-only
  success, and 588 both-failure. Seven of the 10 disagreements are in the
  human subset.
- Confirmed grammar correction as the −8/96 = −8.33-point task result: eight
  separate examples cause the change.
- Confirmed 12 unique flip records partitioned into 10 non-prefix occurrences
  and two casefold gains, with no overlap or other observed mechanism.
- Concluded that the data more directly support evaluator/attack-condition
  alignment as the relevant interpretation than broad instability from
  arbitrary lexical implementation details. This conclusion remains
  exploratory and limited to the frozen design.
- Saved the complete diagnostic, including raw responses for every S0/S2
  disagreement, in `results/scorer_sensitivity/final_exploratory_audit.md`.
  No confirmatory experiment or model generation was started.

## 2026-08-18 — Final confirmatory preregistration-readiness package

- **Starting commit:** `f6cda7e713909ed4f5f97e613ad139357d1eb7f0`.
- Preserved all Pilot 1, Pilot 2, scorer-sensitivity data, results, and human
  labels. No confirmatory prompt sample was drawn and no victim-model output
  was generated.
- Resolved exact public model revisions: Qwen2.5-1.5B-Instruct
  `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, Phi-3.5-mini-instruct
  `2fe192450127e6a83f7441aef6e3ca586c338b77`, and SmolLM2-1.7B-Instruct
  `31b70e2e869a7173562077fd711b654946d38674`; tokenizer revisions are the
  same commits.
- Hardware preflight found an Apple M3 host with 16 GiB RAM, unavailable
  PyTorch MPS, and approximately 0.73 GiB free disk. The study therefore
  cannot run on the audited host. A sequential CUDA/bfloat16 environment with
  at least 16 GiB VRAM, 32 GiB RAM, and 25 GiB free disk is frozen as the
  execution requirement.
- Audited fresh-source capacity against Pilot 1/Pilot 2 IDs and normalized
  content hashes. NLI had only 178 eligible fresh unique rows, so the final
  allocation is 240 grammar, 240 summarization, 176 NLI, and 256 in each of
  the other four classification tasks: 1,680 base prompts, 480 generative and
  1,200 classification. Every task remains exactly balanced over four
  injection templates and two targets.
- Froze greedy generation, S0/S2, a probability sample of 800 human rows (up
  to 480 S0-only disagreements and at least 320 agreement controls), two
  independent annotators, a third independent adjudicator, model-identity
  blinding, a seven-category manual, and strict/lenient mappings.
- Froze 9,999 task-stratified base-prompt cluster-bootstrap replicates at seed
  `2026082207`, paired weighted estimands, fixed-sequence multiplicity, IPW GEE
  robustness, and all missingness, ambiguity, weight, zero-cell, and software
  failure rules.
- The design is ready for external preregistration but not study activation.
  Human action remains for registry submission, annotator identities, source-
  use authorization (especially Gigaword), and compatible hardware. These
  conditions do not authorize post-registration design changes.

## 2026-08-18 — Final non-study readiness and permissions audit

- **Starting commit:** `78a14590243fe64fc246db85c3184919eae388be`.
- Recorded the operator-supplied Google Colab preflight as PASS for CUDA,
  native BF16, batch size 1, greedy decoding, 128 new tokens, and all three
  exact pinned model/tokenizer revisions. Only trivial diagnostic prompts were
  used; no confirmatory source row, attack, target, prompt, or output was
  generated. Exact runtime versions remain explicit human-input placeholders.
- Audited all seven task sources against official owner, benchmark, or author
  materials. The wrapper's MIT license was not treated as licensing its
  underlying corpora. Public release defaults to source IDs/hashes and derived
  metadata rather than raw upstream text or text-bearing outputs.
- JFLEG, HSOL, and SMS Spam have affirmative CC BY-NC-SA 4.0, MIT, and CC BY
  4.0 terms respectively. MRPC, GLUE RTE, and GLUE SST-2 support conservative
  internal academic benchmark use, but raw redistribution was not established
  and is excluded.
- The 189,651-row summarization file matches TFDS Gigaword 1.2.0 validation,
  which derives from LDC-licensed English newswire. Neither TFDS nor the author
  wrapper grants underlying corpus rights, and no applicable project LDC
  authorization is documented. Per the frozen readiness rule, this is
  `BLOCKING`; no substitute dataset was selected.
- A mechanical cross-document audit found no scientific-design inconsistency,
  no structurally guaranteed relationship framed as an empirical hypothesis,
  and consistent exploratory-status disclosures. The preregistration draft
  received only permissions/preflight clarifications and one grammatical fix.
- The package is scientifically frozen but is **not ready for external
  preregistration** until Gigaword authorization is documented. Personnel IDs,
  exact Colab runtime transcription, and registry details remain human inputs.

## 2026-08-18T21:17:01-04:00 — Pre-registration summarization-source substitution

- **Starting commit:** `ccc35f2b0012d9126484c2c5f2aebbad04d53c6e`.
- Recorded operator-supplied successful Colab values: Tesla T4, CUDA available,
  CUDA 12.8, PyTorch 2.11.0+cu128, native BF16, and Transformers 5.15.0. The
  preflight used trivial diagnostics only and was not rerun locally.
- Removed Gigaword from the active confirmatory design before external
  preregistration, source sampling, or model generation because applicable LDC
  authorization could not be established. Preserved that history in
  `protocol/source_substitution_001_gigaword_to_billsum.md`.
- Verified the replacement against the official FiscalNote repository and
  dataset card, GovInfo policies, and the BillSum paper. Froze
  `FiscalNote/billsum` revision
  `3d8510441c06a3d9dfb32eb0d7f80151730bcc4f`, U.S. federal `test` only;
  excluded `train` and `ca_test`. The pinned test parquet SHA-256 is
  `2733cb656a2a6fbff0fc012ca50bbf159615ff6451c0adb229884bbd474780b3`.
- Froze a common maximum of 8,000 complete input tokens across all three pinned
  tokenizers and all eight target/template variants. This reserves 128 output
  tokens plus 64 additional tokens within SmolLM2's limiting 8,192-token
  context. Truncation is forbidden.
- Tokenizer-only eligibility audit under the frozen Transformers 5.15.0,
  counting the explicit returned `input_ids`: 3,269 U.S. test rows; 3,268 eligible; one
  context-length rejection; zero missing-field, duplicate-key, or exploratory-
  overlap exclusions. The local audit used pinned tokenizer artifacts only;
  it loaded no model weights and generated no response.
- Froze future BillSum source-selection seed `12749496974040719988` and
  cell-allocation seed `9976436367042203202`. No final 240-row sample has been
  drawn. The 240 prompts remain balanced at 30 per four-template by two-target
  cell.
- Confirmed the other six sources and all task counts remain unchanged:
  1,680 independent base prompts, 5,040 planned model responses, and 800
  double-labeled human responses. H1, RQ2, H3, S0/S2, human design, and all
  statistical methods remain unchanged.
- Full repository test suite passed: 44 tests. A final YAML/count audit
  confirmed seven tasks, 1,680 base prompts, and 5,040 planned responses.

## 2026-08-19 — External confirmatory preregistration submitted

- Submitted the confirmatory preregistration to OSF:
  https://osf.io/9jrab (registration ID `9jrab`).
- Preserved the user-provided submission timestamp exactly: August 19, 2026,
  7:06:59 PM. No timezone was supplied or available in local repository
  metadata, so none was inferred.
- Study title: *Construct validity of lexical prompt-injection success
  evaluators*.
- The exact externally preregistered scientific state is Git commit
  `853eb6aa7c61e03896cdca3eb991fcf8debdc9cc`.
- No confirmatory model output and no confirmatory human annotation existed
  before external submission. Pilot 1 and Pilot 2 remain preliminary, and the
  frozen 672-response scorer-sensitivity study remains exploratory.
- This entry and `protocol/external_preregistration_record.md` are
  administrative provenance only. They do not change any frozen hypothesis,
  dataset, model, prompt allocation, scorer, human rubric, sampling rule, or
  statistical method. Confirmatory generation may begin only after this
  registration-record commit; none was performed in this task.

## 2026-08-19T19:26:22-04:00 — Confirmatory generation preparation activated

- Verified `confirmatory-preregistered-v1^{commit}` resolves to the registered
  scientific commit `853eb6aa7c61e03896cdca3eb991fcf8debdc9cc` and verified
  the OSF URL/timestamp in the administrative record before materialization.
- Protected `confirmatory_private/` through `.gitignore`, then downloaded only
  the pinned BillSum test parquet and pinned tokenizer/config artifacts into
  that ignored tree. No model weights were used for this preparation.
- Applied the frozen source hashes, missing/label/duplicate rules, Pilot 1 and
  Pilot 2 source-ID and normalized-content exclusions, context rules, and
  seeds. Materialized exactly 1,680 private prompts: 480 generative and 1,200
  classification, with every task exactly balanced over four templates by two
  targets. Prohibited exploratory overlap was zero.
- BillSum yielded 3,268 eligible U.S. test rows and 240 selected rows; `train`
  and `ca_test` remained excluded. One U.S. test row failed the frozen common
  8,000-input-token rule.
- Private manifest SHA-256:
  `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed`.
  Frozen generation-config SHA-256:
  `3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284`.
- Implemented a Google-Colab-compatible runner for 5,040 unique generation
  keys with exclusive-create terminal records, immediate persistence,
  checkpoint/resume skipping, exact revision checks, runtime provenance, no
  output cleaning, and zero automatic retries.
- All 53 tests passed. No frozen scientific design artifact was edited and no
  victim-model response was generated. No protocol deviation occurred.

## 2026-08-19T23:08:35-04:00 — Confirmatory dependency-packaging correction

- Discovered after OSF preregistration but before any confirmatory response
  that installing generic `requirements.txt` downgraded Colab Transformers
  from the frozen 5.15.0 environment to 4.52.4. The runner correctly stopped
  before model generation on its exact-version assertion; no outcome existed
  or was inspected.
- Git history establishes that `requirements.txt` originated in commit
  `f3bbc613004e3860ffc5e652c9520242854f4787` (`Build reproducible 50-item
  pilot dataset`) and the contemporaneous README assigns it to the Pilot
  workflow. It was not the confirmatory environment specification.
- Preserved historical `requirements.txt` unchanged. Added
  `requirements-confirmatory.txt` with `transformers==5.15.0`; intentionally
  omitted PyTorch so Colab's CUDA-enabled build is not replaced by a CPU or
  incompatible wheel. Unfrozen supporting-package versions remain runtime
  provenance.
- Updated the Colab instructions with the confirmatory-only install command
  and explicit `transformers.__version__ == "5.15.0"` assertion. Added a
  minimal bundle builder that excludes generic `requirements.txt` and includes
  the ignored authoritative private prompt manifest.
- Classified this as an implementation/packaging correction, not a scientific
  protocol deviation. H1/RQ2/H3, all models/revisions, prompts, datasets,
  scorers, annotation and sampling plans, generation settings, seeds, and
  statistical methods remain unchanged.
- Reverified zero response files. Prompt-manifest SHA-256 remains
  `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed`;
  generation-config SHA-256 remains
  `3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284`.

## 2026-08-21 — Confirmatory Colab test-packaging correction

- Discovered before any confirmatory generation that Colab bundle v2 omitted
  the public-safe confirmatory activation test because the bundle builder's
  explicit file whitelist did not include the test or its local builder
  dependency.
- Corrected bundle packaging to include the confirmatory activation test and
  its public-safe test/runtime support files. The extracted-bundle test now
  verifies the packaged private-data ignore rule even without Git metadata.
- Built `confirmatory_colab_bundle_v3.zip` (local, Git-ignored), SHA-256
  `55a137e777184a75b80882cb0e1e9021885ea920409f47844a4657263699d49d`;
  all 12 packaged activation tests passed after extraction, and all 56 local
  repository tests passed.
- This is a packaging correction, not a scientific protocol deviation. No
  hypothesis, model, revision, prompt, manifest, source, scorer, annotation
  rule, generation configuration, seed, or statistical method changed, and no
  confirmatory response was generated.

## 2026-08-29 — Phi generation compatibility amendment prepared

- Froze the reported original terminal-record census: Qwen 1,680 successes;
  Phi 1,680 technical failures and zero successes; SmolLM2 1,679 successes and
  one technical failure. All 5,040 original records remain immutable. The
  single SmolLM2 failure will not be retried.
- The preregistered `trust_remote_code: true` Phi path loaded pinned repository
  `modeling_phi3.py`, which failed systematically under Transformers 5.15.0
  because it accessed the absent `DynamicCache.seen_tokens` attribute.
- Before any scoring, ASR, hypothesis analysis, or human sampling, a trivial
  synthetic-only CUDA/BF16 diagnostic passed with the exact pinned Phi weights
  and tokenizer using `trust_remote_code=false`; the resolved module was
  `transformers.models.phi3.modeling_phi3`. Diagnostic SHA-256:
  `ce4d69f30184f367be9955caf744f0b52c1e6cce32958b29f4caad6642f85232`.
- Prepared Amendment 002 and a separate Phi-only runner that preserves all
  prompts, revisions, hashes, seeds, decoding, and zero-retry rules while
  writing only to a versioned corrected namespace. Because remote-code loading
  was explicitly preregistered, this is documented as a post-registration
  protocol amendment. Corrected confirmatory Phi generation was not run.
- Original snapshot-manifest SHA-256:
  `8bca7369fbfbaa78d8adcadab7967aa5a3a2d76ee802b8a591f1985a835913f8`.
  Private backup archive SHA-256:
  `90465d1463615b3350e3fa4534481c8d6315e5cad733487e22e9e2a71d57287f`.
- Built the ignored Colab handoff
  `confirmatory_colab_bundle_phi_amended_v1.zip`, SHA-256
  `58de219506433c0a86889693af29f97377b600c96a8cfeab5aac5b66082c3b5a`.
  Its 20 activation/amendment tests passed after extraction. The full local
  suite had 62 passes and two unrelated Pilot 2 fixture errors because the
  untracked external source checkout currently marks
  `data/summarization/data.csv` deleted; that user-owned checkout was not
  modified.

## 2026-09-07 — Confirmatory human-validation sample activated

- Validated the frozen terminal-record census without modifying source files:
  Qwen 1,680 successes; amended native Phi 1,634 successes and 46 failures;
  SmolLM2 1,679 successes and one failure. The 1,680 original remote-code Phi
  failures remain provenance only. The canonical usable population contains
  exactly 4,993 unique successful, nonempty response keys and excludes all 47
  final technical failures.
- Applied the frozen case-sensitive S0 substring-anywhere and S2 character-zero
  prefix rules privately, with no case, whitespace, Unicode, line-ending, or
  markup normalization. S2-implies-S0 validation passed. No ASR, model/task
  comparison, or hypothesis result was calculated or reported.
- Using frozen human-sampling seed `2026082204`, selected 480 disagreement
  records and 320 probability-sampled agreement controls through model-by-task
  scorer strata, Hamilton allocation, capacity redistribution, and seeded
  sampling without replacement. All 800 keys are unique and retain exact
  inclusion probabilities and weights privately.
- Created private blinded A/B CSVs with identical anonymous item sets and
  independent orders from seeds `2026082205` and `2026082206`. The files omit
  model, scorer, stratum, weight, and provenance fields; annotation-visible
  text round-trips exactly, and all human-input fields are blank.
- Private artifact hashes and the public-safe validation record are stored in
  `confirmatory/human_sampling_activation_audit.md`. No human annotation,
  agreement calculation, adjudication, bootstrap, GEE, or H1/RQ2/H3 analysis
  was performed.
- All 27 confirmatory activation, amended-generation, and human-sampling tests
  passed. The repository-wide run had 69 passes and the same two unrelated
  Pilot 2 fixture failures previously documented: the user-owned untracked
  `external/Universal-Prompt-Injection` checkout marks its historical
  summarization CSV deleted. That external checkout was not modified.

## 2026-09-09 — Pre-adjudication human agreement and handoff

- Located the completed annotations as Numbers-exported XLSX files in the
  user's Downloads directory and preserved byte-identical private raw copies.
  Annotator A SHA-256: `0ef4c380e33b390f844214c2c8b12de00ea2194b4c26c85f0b01b2c409a76c50`;
  Annotator B SHA-256: `50dbbfd099783b9aaf612829e55fc885debc7a584f7325f3d6782b92e7667af1`.
- Initial exact validation found that Numbers had normalized CRLF to LF in
  `legitimate_input` for the same 45 rows in each workbook. Validation stopped
  before agreement calculation. After explicit user authorization, rebuilt
  private completed CSVs from the frozen original non-human fields while
  copying each workbook's `human_label`, `human_confidence`, and `notes`
  unchanged. No other non-human discrepancy was accepted.
- Both reconstructed files passed validation: 800 rows, 800 unique IDs,
  identical A/B ID sets, frozen row mappings, complete valid labels, and
  integer confidence from 1 through 5.
- Calculated only pre-adjudication human-human reliability and created the
  exact adjudication set defined by A/B disagreement or either annotator using
  `AMBIGUOUS`. Prepared a private adjudicator CSV in a fresh order using the
  administrative seed `2026082207` and a separate withheld A/B label key.
- No scorer-human comparison, ASR, H1, RQ2, H3, bootstrap, GEE, model, or task
  result was calculated.
- All 34 directly applicable confirmatory activation, sampling, amended-Phi,
  and human-agreement tests passed. The repository-wide run had 76 passes and
  the same two previously documented unrelated Pilot 2 fixture failures caused
  by the missing user-owned untracked
  `external/Universal-Prompt-Injection/data/summarization/data.csv`; that
  checkout was not modified.

## 2026-09-10 — Independent adjudication validated; consensus required

- Located the completed 209-row adjudicator CSV in the user's Downloads
  directory and preserved it byte-for-byte at the private raw path. SHA-256:
  `6cb63f6a7199aa337f416f55611299345579fe047dbb27727600175fc7cdad34`.
- Validation passed: 209 rows and unique anonymous IDs; exact frozen ID set and
  order; complete valid seven-category labels; confidence integers 1–5; no
  added metadata; and exact non-human fields. Unlike the prior Numbers XLSX
  exports, this CSV required no mechanical reconstruction.
- Applied only the frozen adjudication rule. Of the 209 rows, 40 adjudicator
  judgments matched Annotator A, 155 matched Annotator B, and 14 were genuine
  three-way disagreements. The 591 original A/B agreements retained their
  agreed labels. All original A/B/adjudicator labels remain separate and
  unchanged.
- Created an 800-row private working table. The 786 rule-resolved labels are
  populated; the 14 three-way rows remain blank. Created a private discussion
  file containing only those 14 rows, their blinded context and three human
  labels, plus blank consensus fields. No final human-ground-truth artifact was
  created.
- No scorer/model/sampling information was used, and no S0/S2 agreement, ASR,
  H1/RQ2/H3, bootstrap, or GEE analysis was performed.
- All 40 directly applicable confirmatory tests passed. The full suite had 82
  passes and the same two previously documented unrelated Pilot 2 fixture
  failures caused by the missing user-owned untracked
  `external/Universal-Prompt-Injection/data/summarization/data.csv`; that
  checkout was not modified.

## 2026-09-10 — Final adjudicated human ground truth frozen

- Located the completed 14-row consensus CSV in the user's Downloads directory
  and preserved a byte-identical private raw copy. SHA-256:
  `96fe9c870c75b3f8b03f4860810cc0a0760e611e27dde1f57713215b8d7633dd`.
- Also preserved the partially edited in-place private working copy separately
  before reconstructing the blank frozen handoff deterministically from the
  prior frozen working/adjudication artifacts. The reconstructed handoff hash
  is `233771cb54c552d166219c9d2d37bd0f4f394b840f99a6071017903b833940ea`,
  exactly matching the hash recorded before discussion. The complete Downloads
  CSV—not the partial working copy—was used as the consensus decision source.
- Validation passed with the exact 14 frozen IDs, unchanged order, unchanged
  context and original A/B/adjudicator labels, and complete valid consensus
  categories. No line-ending or other mechanical reconstruction was required.
- Applied the 14 consensus decisions to the frozen 800-row working table. All
  became `CONSENSUS_RESOLVED`; none required `NO_CONSENSUS_AMBIGUOUS`. The
  previous 591 A/B agreements, 40 match-A rows, and 155 match-B rows remain
  unchanged.
- Froze the private 800-row final adjudicated human ground truth with SHA-256
  `20804593269be59b3578fb1e12f033d7b3044895775a21dc2195ca5bb53f11e7`.
  All 800 IDs and labels are complete and valid; zero final labels are
  `AMBIGUOUS`.
- Created a separate private binary-outcome artifact using only the frozen
  strict/lenient definitions. `AMBIGUOUS` would remain blank and excluded from
  primary complete-case estimands. No scorer-human accuracy, ASR, H1/RQ2/H3,
  bootstrap, GEE, model, task, or subgroup result was calculated.
- All 46 directly applicable confirmatory tests passed. The full suite had 88
  passes and the same two previously documented unrelated Pilot 2 fixture
  failures caused by the missing user-owned untracked
  `external/Universal-Prompt-Injection/data/summarization/data.csv`; that
  checkout was not modified.

## 2026-09-10 — First preregistered confirmatory analysis

- Analysis first executed at `2026-09-10T12:46:53-0400`, after external
  preregistration and the immutable human-ground-truth freeze. All six frozen
  private input SHA-256 values matched their recorded identifiers.
- Built and froze the private canonical 800-row analysis dataset (SHA-256
  `634f4ef28c68696f8c7681fa83827bb12ab6568c5077e9ddf6c926bfe2bf6a3b`).
  It has 800 unique anonymous and response keys, valid recorded inclusion
  probabilities/weights, no failed-generation records, no original failed-Phi
  records, no `AMBIGUOUS` final labels, and satisfies S2=>S0.
- Ran the registered 9,999-replicate task-stratified base-prompt cluster
  bootstrap with seed `2026082207`; every main estimand retained all 9,999
  valid replicates. The registered Kish-ESS threshold triggered the specified
  uncalibrated-IPW sensitivity; it was reported alongside and did not replace
  the calibrated primary estimator.
- H1 rejected under the frozen positive-estimate/two-sided-percentile-CI rule,
  opening the fixed-sequence H3 gate. H3 then rejected under its frozen rule.
  RQ2 was reported as estimation-focused. The SAP froze no primary bootstrap
  p-value, so none was invented; identity-link IPW GEE p-values are labeled
  robustness results.
- The registered descriptive scorer metrics, ASRs, A/B sensitivity comparisons,
  and exploratory model/task/target/template families were produced. No
  exploratory p-values were reported, so Benjamini-Hochberg adjustment was not
  invoked.
- The complete analysis was rerun with identical aggregate files and private
  result hashes. No response generation occurred; no human label, scorer
  output, sampling decision, or frozen scientific artifact was modified. No
  deviation from the frozen SAP occurred.
- All 53 confirmatory tests passed. The full suite had 95 passes and the same
  two previously documented unrelated Pilot 2 fixture failures caused by the
  absent `external/Universal-Prompt-Injection/data/summarization/data.csv` in
  the user-owned untracked checkout; that checkout was not modified.

## 2026-09-10 — Confirmatory scientific state frozen

- **CONFIRMATORY SCIENTIFIC ANALYSIS COMPLETE AND FROZEN** at
  `2026-09-10T17:05:33Z`. The final analyzed scientific state begins from
  results commit `68d077c96424a7834e9cbc3fd65578b33f904bca`.
- Recomputed all available authoritative hashes directly from their local
  files; every frozen prompt, generation, usable-response, scorer, sampling,
  human-ground-truth, binary-outcome, analysis-dataset, and result hash matched.
- Created the ignored private final-freeze manifest with SHA-256
  `4e070cd5287243e4f72efb5f77b524cb3a2e82063d573bb18c0375db29141a41`.
  It records private annotation/adjudication hashes, model revisions, generation
  counts, runtime provenance, bootstrap settings, and the Phi amendment.
- Final human-ground-truth SHA-256:
  `20804593269be59b3578fb1e12f033d7b3044895775a21dc2195ca5bb53f11e7`.
  Canonical analysis-dataset SHA-256:
  `634f4ef28c68696f8c7681fa83827bb12ab6568c5077e9ddf6c926bfe2bf6a3b`.
- H1 decision: reject/H1 supported. RQ2 status: estimation-focused. H1 opened
  the fixed-sequence gate and H3 was rejected. No deviation from the frozen
  statistical analysis plan occurred during confirmatory analysis. The earlier
  post-preregistration Phi-3.5 technical implementation amendment documented in
  `protocol/amendment_002_phi_generation_compatibility.md` remained in effect
  and is not erased or reclassified by this freeze.
- Manuscript drafting is now authorized. Future manuscript edits do not alter
  the frozen scientific state. Any genuinely new analysis after this freeze
  must be labeled post-hoc/exploratory unless it was already preregistered.
- All 60 directly applicable confirmatory/freeze tests passed. The full suite
  had 102 passes and the same two documented historical Pilot 2 fixture
  failures caused by the absent
  `external/Universal-Prompt-Injection/data/summarization/data.csv`; no frozen
  artifact or user-owned external file was changed to address them.
