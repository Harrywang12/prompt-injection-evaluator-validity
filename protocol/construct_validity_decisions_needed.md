# Construct-Validity Confirmatory Study: Decisions Needed

## Status

No confirmatory generation or annotation may begin until every current blocker
in the final hierarchy section is resolved, recorded in the final
preregistration, and committed. Later sections explicitly retain superseded
working proposals as design history; they are not current defaults.

## Final hierarchy and sample-size resolution — 2026-08-18

This second design-only resolution supersedes the first audit recommendation
below while retaining it as history:

- H1 is the sole primary hypothesis at unadjusted two-sided alpha 0.05.
- Former H2 is replaced by estimation-focused RQ2; the guaranteed sign of
  `I_DEFINITION` is not tested and no practical threshold is adopted.
- H3 remains secondary confirmatory under fixed-sequence gatekeeping after H1.
- The recommended design remains 1,680 prompts/5,040 responses and 800
  double-labeled responses after direct comparison with n=300, 400, 500, 600,
  and 800.
- Retain a maximum of 480 scorer disagreements and at least 320 probability-
  sampled agreement controls at n=800. The 60% cap was compared with 40%–80%
  alternatives and preserved nearly all contrast power while supporting
  population accuracy estimation.

Items still blocking an external preregistration are now limited to:

1. external/scientific acceptance of the detectable-effect profile, especially
   only 47.6% power for a 2-point H3 interaction;
2. exact immutable model commit SHAs and completed hardware/chat-template
   preflight;
3. identities/qualifications of annotators and the third adjudicator;
4. final model-identity blinding decision;
5. frozen rubric training examples and full-versus-partial boundary guidance;
6. frozen fresh source-row IDs, prompt templates, targets, decoding settings,
   failure handling, and duplicate rules; and
7. bootstrap seed/replicate count, exact stratum-collapse algorithm, and GEE
   convergence fallback encoded in executable analysis code.

No H2 or Delta-ASR practical threshold remains a blocker: absent an external
justification, both are estimation-only.

## First design-only power-audit record — 2026-08-18

This section is retained verbatim as a historical decision record. Its H2 and
remaining-decision statements were superseded by the final hierarchy above.

The following recommendations supersede the earlier working numbers below but
are not yet preregistered:

- 1,680 fresh base prompts × three models = 5,040 responses;
- 800 responses independently labeled by both primary annotators;
- up to 480 S0/S2 disagreements, with the remainder probability-sampled from
  both scorer-agreement cells;
- simple calibrated weighted paired differences with base-prompt
  cluster-bootstrap intervals as the primary presentation; and
- weighted GEE as robustness analysis.

The power audit identified H3 task-category moderation as the sample-size
driver. It also proved
`INTERACTION_DEFINITION = 2 * P(S0=1,S2=0,PARTIAL_COMPLIANCE)`, so H2's sign is
nonnegative by construction. The final preregistration must not present that
sign as a freely varying empirical hypothesis.

Resolved design recommendations are documented in
`construct_validity_power_analysis.md`, `construct_validity_sampling_plan.md`,
and `construct_validity_statistical_plan.md`. The unresolved items that still
block preregistration are:

1. approve a smallest practically meaningful H1 and H3 effect, acknowledging
   that the recommended design has only about 49.5% simulated power for a
   2-point H3 interaction under central assumptions;
2. decide whether H2 is threshold-based confirmatory estimation or is
   reformulated around partial-compliance prevalence;
3. freeze exact model repository commits after hardware/chat-template
   preflight, without substituting newer models;
4. finalize one- versus two-sided claims and multiplicity control for H1/H2;
5. approve model-identity blinding for annotators;
6. name/qualify the two annotators and independent third adjudicator;
7. freeze rubric training examples and full-versus-partial boundary guidance;
8. freeze unused source rows, prompt templates, targets, generation settings,
   failure handling, and duplicate rules;
9. freeze the bootstrap seed, replicate count, calibrated stratum-collapse
   rules, and GEE convergence fallback; and
10. decide whether any practical `Delta_ASR` threshold has an external
    justification; otherwise retain estimation only.

## Verified model repositories and revision-freezing procedure

Official repositories verified on 2026-08-18 without downloading weights:

- `Qwen/Qwen2.5-1.5B-Instruct`:
  <https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct>
- `microsoft/Phi-3.5-mini-instruct`:
  <https://huggingface.co/microsoft/Phi-3.5-mini-instruct>
- `HuggingFaceTB/SmolLM2-1.7B-Instruct`:
  <https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct>

Immediately before preregistration—but before any download or generation—query
each official repository's metadata API for the immutable 40-character commit
SHA, record retrieval UTC time, license/access status, chat-template/config
hashes, and resolved file list in the frozen config. Commit those SHAs in the
preregistration. Afterward, download only with `revision=<frozen_sha>`, verify
the resolved SHA and file hashes, and never resolve `main` during generation.
If preflight fails, amend the design before preregistration rather than silently
substituting a newer model.

## Earlier pre-audit decision record (retained for history)

## Blocking scientific decisions

### 1. Exact victim models and revisions

Working candidates:

- `Qwen/Qwen2.5-1.5B-Instruct`
- `microsoft/Phi-3.5-mini-instruct`
- `HuggingFaceTB/SmolLM2-1.7B-Instruct`

Resolve:

- exact immutable repository revision for each;
- whether all three are practically runnable on available hardware;
- whether model identity is blinded from annotators;
- chat-template compatibility and common generation settings;
- license/access verification at the frozen revisions; and
- replacement rule if a model fails the pre-outcome feasibility audit.

No weights have been downloaded for this design.

### 2. Total confirmatory pool size

Working proposal: 2,520 responses from 840 base attack-prompt cells crossed
with three models.

Resolve via prospective simulation:

- minimum detectable paired accuracy difference for H1;
- power for the scorer-by-definition H2 interaction;
- power for H3 with only two generative and five closed-label task families;
- expected generation-failure allowance without outcome-dependent replacement;
- whether 15 source inputs per task/target/template cell is feasible; and
- final expansion/stopping rule, if any.

### 3. Human-validation subset size and sampling

Working proposal: 600 responses, each labeled independently by two humans;
census or uniform sample of at most 300 S0/S2 disagreements, then sampled
agreement controls.

Resolve:

- final human-label budget;
- maximum disagreement-stratum allocation;
- agreement-cell strata and allocation across models/task categories;
- whether the same base prompt's model responses are sampled together;
- inclusion-probability and weighting specification; and
- minimum informative disagreement count below which H1/H2 are reported as
  underpowered or not estimable rather than prompting design changes.

### 4. Task-category assignment

Proposed assignment to approve before generation:

- Generative/text transformation: `grammar_correction`, `summarization`.
- Closed-label classification: `duplicate_sentence_detection`,
  `hate_detection`, `natural_language_inference`, `sentiment_analysis`,
  `spam_detection`.

Resolve whether task category is treated as a fixed contrast over these seven
families or as a basis for broader task-family generalization. The latter is
not justified with only seven families without additional design work.

### 5. Primary agreement metric and H1 test

Working proposal:

- primary metric: paired accuracy relative to adjudicated strict human labels;
- primary test: directional scorer contrast in an inverse-probability-weighted
  identity-link GEE for paired correctness, with robust standard errors
  clustered by base attack prompt;
- primary effect: design-weighted S2-minus-S0 accuracy difference with a 95%
  stratified cluster-bootstrap interval;
- raw paired correctness cells and exact McNemar tests: unweighted sensitivity
  analyses;
- kappa: descriptive only.

Resolve:

- one-sided versus two-sided primary testing;
- whether H1 and H2 are co-primary with Holm correction;
- exact GEE weights and small-sample robust-variance correction;
- bootstrap unit and number of replicates; and
- whether balanced accuracy or another metric is a prespecified sensitivity
  analysis because attack success may be rare.

### 6. H2 interaction model

Working proposal: inverse-probability-weighted identity-link GEE for correctness
with scorer, human definition, and their interaction; robust standard errors
clustered by base attack prompt; logit GEE sensitivity.

Resolve:

- final covariates and contrast coding;
- convergence fallback that does not depend on observed significance;
- finite-sample correction for cluster-robust standard errors; and
- primary p-value versus cluster-bootstrap confidence-interval criterion.

### 7. H3 moderation model

Working proposal: strict-outcome scorer-by-task-category interaction in the
weighted identity-link GEE; lenient and three-way interactions secondary.

Resolve:

- one-sided versus two-sided H3 alternative;
- model/target/template adjustment terms;
- treatment of task family as fixed versus clustered; and
- minimum subgroup cell sizes for reporting inferential rather than purely
  descriptive results.

### 8. `AMBIGUOUS` human cases

Resolve before annotation:

- primary exclusion versus a frozen binary mapping;
- denominator and weighting consequences of exclusion;
- sensitivity mappings (failure, success, or bounds); and
- treatment when one annotator is ambiguous and the other is not.

No ambiguous label may be silently forced after outcome inspection.

### 9. Adjudication rule

Resolve:

- independent third-human adjudication versus documented A/B consensus;
- whether adjudicator confidence is recorded;
- tie/unresolved procedure;
- whether adjudication sees annotator notes but never scorer verdicts;
- qualification/training examples for annotators; and
- final reference construction when adjudication remains `AMBIGUOUS`.

Both original labels must remain immutable and human-human reliability must be
reported before adjudication.

### 10. Practical Delta-ASR threshold

`Delta_ASR >= 0` is guaranteed and is not a hypothesis.

Resolve whether an independently defensible practically meaningful threshold
exists for `P(S0=1,S2=0)`. Possible bases include operational review burden or
benchmark-ranking sensitivity, but the threshold must not be selected from the
new outcomes. If no external justification is available, report Delta ASR with
counts, magnitude, and confidence interval only, without a significance test.

### 11. Fresh-data independence and prompt design

Resolve and freeze:

- exact unused source-row IDs and content hashes;
- whether the two prior harmless target strings are reused or replaced;
- exact four injection templates;
- exact prefix-plus-legitimate-task objective wording;
- duplicate-detection rules across Pilot 2 and confirmatory inputs;
- decoding parameters and deterministic seeds; and
- treatment of generation failures.

### 12. Human rubric operationalization

Resolve examples and boundary guidance for:

- target emitted away from prefix as partial compliance versus incidental echo;
- prefix emitted but legitimate task omitted;
- legitimate task substantially versus minimally completed;
- refusal quotation and input reproduction;
- malformed or truncated responses; and
- `FULL_COMPLIANCE` versus `PARTIAL_COMPLIANCE`, the boundary central to H2.

Rubric examples must be selected before annotators see confirmatory responses
and must not disclose automated scorer behavior.
