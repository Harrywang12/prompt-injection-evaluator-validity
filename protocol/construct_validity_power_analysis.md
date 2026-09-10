# Construct-Validity Study: Design-Only Power and Estimand Audit

## Status

This document is a design analysis, not a preregistration. It was prepared
after Pilot 1, Pilot 2, and the 672-response scorer-sensitivity analysis were
examined. It does not contain confirmatory outcomes. No new victim-model output
was generated.

The reproducible extraction and simulation are in
`scripts/analyze_construct_validity_design.py`. Machine-readable outputs are in
`results/design_power/`. Simulation seed: `20260821`; 1,000 Monte Carlo studies
per grid cell.

## Simple estimands

For response `i`, let `C0i(H)` and `C2i(H)` indicate whether S0 and S2 agree
with human binary outcome `H`. Define:

- `D_STRICT = mean[C2i(H_strict) - C0i(H_strict)]`;
- `D_LENIENT = mean[C2i(H_lenient) - C0i(H_lenient)]`;
- `INTERACTION_DEFINITION = D_STRICT - D_LENIENT`;
- `D_GENERATIVE` and `D_CLASSIFICATION` as `D_STRICT` within the two frozen
  task categories; and
- `INTERACTION_TASK = D_GENERATIVE - D_CLASSIFICATION`.

All contrasts are paired. The base attack prompt—not an individual model
response—is the cluster and primary resampling unit.

Because S2 is a subset of S0, only `S0=1,S2=0` responses can contribute a
nonzero paired correctness difference. In the absence of ambiguous labels:

`INTERACTION_DEFINITION = 2 * P(S0=1, S2=0, human=PARTIAL_COMPLIANCE)`.

Thus the H2 interaction is also nonnegative by construction. Whether it is
nonzero, and especially its magnitude, remain empirical; a directional sign
test is not scientifically informative. This identity must be addressed in
the final hypothesis wording before preregistration.

## Is the simple analysis valid?

Yes, if the human subset is a probability sample with recorded inclusion
probabilities. Weighted means of paired correctness differences identify the
candidate-pool estimands. A cluster bootstrap can resample whole base prompts,
carry all three associated model outputs and their annotation indicators, and
recalculate calibrated survey weights and contrasts.

Caveats:

1. Unweighted human-sample differences are not population estimates after
   disagreement oversampling.
2. Response-level sampling weights must be calibrated to known S0/S2 joint-cell
   totals; using only broader S0 strata is valid in expectation but inefficient
   and can yield realized estimates incompatible with a known joint-cell total.
3. With three models per prompt, ordinary row bootstrapping understates
   uncertainty.
4. Very few discordances make all three estimands imprecise, irrespective of
   the number of sampled agreement cases.
5. H3 has only two generative and five classification task families. The
   planned contrast is fixed to these seven families and does not identify a
   population of all possible tasks.
6. Percentile cluster intervals can behave poorly near the structural boundary
   for H2. Raw event counts and a threshold-based interpretation are needed.

## Exploratory planning inputs

These values inform simulation scenarios; they are not assumed true in the
fresh study.

### Dependence and scorer disagreement

| Quantity | Exploratory value |
| --- | ---: |
| Frozen candidate responses | 672 |
| Unique base-prompt hashes | 672 |
| Responses per base prompt | 1 |
| Victim models per prompt | 1 |
| S0/S2 discordances | 10/672 (1.4881%) |
| Empirical within-prompt ICC | Not identifiable |

Pilot 2 used one model response for every unique prompt hash. No defensible
within-prompt clustering coefficient can be extracted. Simulations therefore
vary an assumed ICC rather than presenting a fabricated estimate.

### Paired correctness tables in the raw 100-row human sample

| Human outcome | Both incorrect | S0 only correct | S2 only correct | Both correct | D |
| --- | ---: | ---: | ---: | ---: | ---: |
| Strict | 4 | 0 | 7 | 89 | 7.0 pp |
| Lenient | 1 | 3 | 4 | 92 | 1.0 pp |

The raw H2 interaction was `7.0 - 1.0 = 6.0` points.

### Population-weighting diagnostics

| Estimator | D strict | D lenient | Definition interaction |
| --- | ---: | ---: | ---: |
| Raw stratified sample | 7.000 pp | 1.000 pp | 6.000 pp |
| Original Pilot 2 S0-stratum IPW | 1.750 pp | 0.250 pp | 1.500 pp |
| Joint-cell calibrated to known 10/672 discordances | 1.488 pp | 0.213 pp | 1.276 pp |

The calibrated estimator uses the known full-pool S0/S2 cell count and the
observed human-category mixture among the seven sampled disagreements. It is
preferred for planning but remains highly uncertain.

### Task-category planning estimates

| Category | Pool n | Human n | Pool discordances | Raw D strict | Raw D lenient | Calibrated D strict | Calibrated D lenient |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Generative/text transformation | 192 | 40 | 10 | 17.500 pp | 2.500 pp | 5.208 pp | 0.744 pp |
| Closed-label classification | 480 | 60 | 0 | 0.000 pp | 0.000 pp | 0.000 pp | 0.000 pp |

The raw H3 interaction was 17.5 points; the joint-cell-calibrated interaction
was 5.208 points. All ten population disagreements occurred in the two
generative tasks, so this estimate is particularly unstable and should not be
treated as a confirmatory effect assumption.

### Design dimensions

The 672-response pool was exactly balanced across:

- tasks: 96 for each of seven tasks;
- injection variants: 168 for each of four variants; and
- targets: 336 `T_WEB`, 336 `T_EMAIL`.

The human sample was not balanced on these dimensions: task counts were 11,
19, 20, 5, 7, 17, and 21 in repository task order; variant counts were 21,
23, 16, and 40 for V1–V4; target counts were 40 `T_EMAIL` and 60 `T_WEB`.

## Simulation design

The grid crossed:

- 420, 840, 1,260, and 1,680 independent base prompts;
- three model responses per prompt (1,260–5,040 responses);
- 400, 600, 800, and 1,000 double-annotated responses;
- H1 effects of 1, 2, 3.5, 5, and 7 points;
- H2 interactions of 1, 2, 3.5, and 5 points; and
- H3 interactions of 2, 3.5, 5, and 7 points.

The central stress scenario uses 10% S0/S2 discordance, within-prompt ICC
0.25, the planned 2/7 generative and 5/7 classification proportions, and at
most 60% of human slots allocated to scorer disagreements. Ten percent was
not selected as an expected rate: it permits all requested effect sizes and is
variance-conservative for a fixed paired difference. Assumption sensitivity
uses discordance rates 3%, 6%, and 10% and ICCs 0, 0.10, 0.25, and 0.40.

Power is the fraction of simulated studies whose cluster-based 95% interval
excludes zero in the hypothesized direction. Simulations use calibrated
inverse-probability-weighted cluster totals and cluster-normal intervals as a
computational approximation. The actual study will use a base-prompt cluster
bootstrap; simulation results are approximate to about ±3 percentage points
at worst with 1,000 repetitions.

### Power with 600 human labels

| Hypothesis/effect | 420 prompts | 840 prompts | 1,260 prompts | 1,680 prompts |
| --- | ---: | ---: | ---: | ---: |
| H1, 1 pp | 19.8% | 37.5% | 46.6% | 47.8% |
| H1, 2 pp | 60.3% | 88.8% | 96.0% | 97.1% |
| H1, 3.5 pp | 98.4% | 100.0% | 100.0% | 100.0% |
| H2, 1 pp | 87.5% | 99.8% | 100.0% | 100.0% |
| H2, 2 pp | 99.7% | 100.0% | 100.0% | 100.0% |
| H3, 2 pp | 16.1% | 27.7% | 40.8% | 38.5% |
| H3, 3.5 pp | 39.9% | 67.5% | 82.5% | 85.1% |
| H3, 5 pp | 70.1% | 94.6% | 98.9% | 99.5% |

The nonmonotonic entries occur when a fixed human budget caps the number of
sampled disagreements while the candidate pool grows; they are not evidence
that more candidate responses are harmful.

### Human-budget sensitivity at 1,680 prompts

| Hypothesis/effect | 400 humans | 600 humans | 800 humans | 1,000 humans |
| --- | ---: | ---: | ---: | ---: |
| H1, 1 pp | 36.6% | 47.8% | 52.9% | 65.6% |
| H1, 2 pp | 88.1% | 97.1% | 98.8% | 99.3% |
| H2, 1 pp | 99.9% | 100.0% | 100.0% | 100.0% |
| H3, 2 pp | 26.8% | 38.5% | 49.5% | 54.5% |
| H3, 3.5 pp | 66.3% | 85.1% | 93.4% | 94.2% |
| H3, 5 pp | 93.5% | 99.5% | 99.9% | 99.9% |

At the recommended 5,040-response/800-human design, H3 power for a 3.5-point
interaction remained 91.7%–99.7% across the simulated ICC/rate sensitivity
grid. It remained only 49.5% for a 2-point H3 interaction under the central
scenario. The design cannot honestly promise high power for every small
interaction.

H2's very high apparent power is partly a mathematical-boundary phenomenon:
its interaction is twice the prevalence of partial-compliance S0/S2
disagreements. It must not be used as the sole reason to choose sample size.

## Recommendation

Use **1,680 fresh base attack prompts × three models = 5,040 responses** and
double-annotate **800 responses** (1,600 independent annotation records before
adjudication). This is exactly 240 prompts per task and 30 prompts per
task × target × injection-variant cell.

H3 drives the recommendation. The original 840-prompt/2,520-response design
has only about 67.5% simulated power for a 3.5-point H3 interaction with 600
human responses. The recommended design gives about 93.4% with 800 humans,
while retaining very high power for a 2-point H1 effect. A 2-point H3
interaction remains underpowered and must be reported as such rather than
changing the study after outcomes are known.
