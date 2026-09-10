# Construct-Validity Study: Statistical Analysis Plan — Design Draft

## Status

This is a design-stage statistical plan, not a preregistration. It supersedes
the earlier proposal to make GEE the sole primary analysis, without deleting
that design history.

The 2026-08-18 hierarchy resolution additionally retires the former H2
directional/co-primary formulation. H1 is sole primary, RQ2 is estimation-
focused, and H3 is secondary confirmatory.

## Human outcomes

- Strict: `FULL_COMPLIANCE = 1`; every other non-ambiguous category = 0.
- Lenient: `FULL_COMPLIANCE` or `PARTIAL_COMPLIANCE = 1`; every other
  non-ambiguous category = 0.
- Final adjudicated `AMBIGUOUS` cases follow the exclusion-and-bounds rule in
  `construct_validity_sampling_plan.md`.

## Primary estimands

For scorer `s`, human definition `H`, and eligible population `P`, define
`Accuracy(s,H) = E_P[1(s=H)]`.

### H1

`D_STRICT = Accuracy(S2,H_strict) - Accuracy(S0,H_strict)`.

Primary presentation: calibrated design-weighted point estimate, raw paired
correctness table, and 95% base-prompt cluster-bootstrap confidence interval.
H1 is supported only if the interval excludes zero in favor of S2 and the
effect is not driven by a data-integrity or reliability failure. Always report
the magnitude; a positive point estimate alone is insufficient.

### RQ2 — construct-validity estimation

`D_LENIENT = Accuracy(S2,H_lenient) - Accuracy(S0,H_lenient)`.

`INTERACTION_DEFINITION = D_STRICT - D_LENIENT`.

Report both component differences, their paired interaction,
raw human-category counts within the S0/S2 disagreement cell, and a 95%
cluster-bootstrap interval. Since the interaction equals twice the population
prevalence of partial-compliance scorer disagreements, its sign is
nonnegative by construction. Do not test that sign. No practical threshold is
adopted because none has been independently justified; magnitude and
uncertainty are the scientific quantities of interest.

### H3

Under the strict human definition:

- `D_GENERATIVE` is the S2-minus-S0 accuracy difference in grammar correction
  and summarization;
- `D_CLASSIFICATION` is the same difference in the other five task families;
  and
- `INTERACTION_TASK = D_GENERATIVE - D_CLASSIFICATION`.

Primary presentation: category-specific paired tables and calibrated weighted
differences, their interaction, and a 95% cluster-bootstrap interval. The
estimand is a fixed contrast across these seven tasks. Lenient category effects
and the definition × task-category interaction are secondary.

## Weighted estimation

Compute S0 and S2 correctness on the same human-labeled rows. Apply the final
sampling weights to paired correctness contributions, not to separately
sampled scorer datasets. Calibrate weights to the known candidate-pool counts
in joint scorer × model × task strata. Report:

- unweighted human-sample estimates;
- calibrated candidate-pool estimates;
- stratum counts, sampling fractions, and effective sample size; and
- raw numerator/denominator beside every rate.

Agreement rows contribute zero to D estimands but remain essential for each
scorer's accuracy, precision, recall, F1, kappa, false-positive rate, and
false-negative rate.

## Cluster bootstrap

Before analysis, freeze a seed and use at least 9,999 replicates.

1. Resample base attack-prompt IDs with replacement within the seven task
   families, preserving the planned task allocation.
2. Carry all observed model-response records, annotation inclusion indicators,
   calibrated weights, and adjudicated labels associated with each resampled
   prompt.
3. Recompute weighted accuracies and all paired contrasts in every replicate.
4. Use percentile 95% intervals as the primary presentation; add studentized
   or bias-corrected intervals as prespecified sensitivity analyses if their
   computation is stable.
5. Report bootstrap failure/degeneracy counts. Do not silently replace failed
   replicates.

This resampling treats the fresh prompts as sampled units and the seven tasks
as fixed design strata. It does not support generalization to all possible
tasks.

## Robustness analyses

Retain inverse-probability-weighted identity-link GEE analyses as robustness
checks:

- H1: correctness modeled by scorer, strict human outcome;
- RQ2: scorer × human-definition interaction as an estimation robustness check;
- H3: scorer × task-category interaction under strict success;
- robust standard errors clustered by base prompt; and
- prespecified model, task, target, and injection-variant terms.

Report GEE marginal contrasts on the accuracy scale. Use a logit-link GEE only
as a secondary sensitivity model. Failure to converge is reported; it does not
trigger outcome-dependent model changes.

Also report raw paired McNemar tables/tests for H1 and both human definitions,
but do not treat unweighted McNemar results as population inference after
stratified sampling. Cohen's kappa is descriptive only.

## Human reliability and metric reporting

Human-human reliability is evaluated before adjudication. Then, for S0 and S2
under both binary definitions, report raw and weighted TP, TN, FP, FN,
accuracy, precision, recall, F1, kappa, false-positive rate, and false-negative
rate with confidence intervals where estimable. Repeat primary contrasts using
each original annotator separately.

## Multiplicity

H1 is the sole primary confirmatory hypothesis. It is evaluated at unadjusted
two-sided alpha 0.05 using the cluster-bootstrap interval; no multiplicity
correction is required for one primary test. H3 is a secondary confirmatory
hypothesis tested at two-sided alpha 0.05 only if H1 rejects, using fixed-
sequence gatekeeping. If H1 does not reject, H3 receives an estimate and
interval but no confirmatory rejection claim.

RQ2 is estimation-focused without a sign test. Per-model, individual-task,
target, injection-variant, and other subgroup tests are exploratory. Their
effect estimates and intervals are always shown; any p-values use Benjamini-
Hochberg false-discovery-rate control within a named family rather than being
presented as additional confirmatory hypotheses.
