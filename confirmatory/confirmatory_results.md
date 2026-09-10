# Confirmatory results

This is the first preregistered confirmatory scorer–human analysis. Population estimates use frozen inverse-probability weights; raw results describe the deliberately stratified 800-response sample.

## Table 1 — Primary H1 and RQ2

| Human definition | Raw S0 correct | Raw S2 correct | Weighted accuracy S0 | Weighted accuracy S2 | S2−S0 | 95% cluster-bootstrap CI | Inferential status |
|---|---:|---:|---:|---:|---:|---:|---|
| Strict | 266/800 | 746/800 | 81.100% | 92.776% | 11.676% | [11.676%, 11.676%] | H1 REJECT |
| Lenient | 554/800 | 496/800 | 86.298% | 87.072% | 0.774% | [0.244%, 1.306%] | RQ2 estimation only |

I_DEFINITION = 10.903%, 95% CI [10.371%, 11.432%]. No directional significance test was performed.

The frozen SAP specified a CI-based primary decision rule but no primary bootstrap p-value; none was invented. The GEE robustness p-value is reported separately.

## Table 2 — Secondary H3

| Task category | Weighted S0 strict accuracy | Weighted S2 strict accuracy | S2−S0 | 95% CI |
|---|---:|---:|---:|---:|
| Generative/text transformation | 65.745% | 94.030% | 28.284% | [28.284%, 28.284%] |
| Closed-label classification | 87.041% | 92.291% | 5.250% | [5.250%, 5.250%] |

I_TASK = 23.034%, 95% CI [23.034%, 23.034%]. Gate opened: **yes**. H3: **REJECT**.

## Table 3 — GEE robustness

| Estimand | Bootstrap estimate (95% CI) | GEE estimate | GEE 95% CI | GEE p-value |
|---|---:|---:|---:|---:|
| D_STRICT | 11.676% [11.676%, 11.676%] | 11.676% | [9.862%, 13.491%] | 1.7838384024897215e-36 |
| I_DEFINITION | 10.903% [10.371%, 11.432%] | 10.903% | [9.101%, 12.704%] | 1.9251502536753355e-32 |
| I_TASK | 23.034% [23.034%, 23.034%] | 23.034% | [17.549%, 28.519%] | 1.8571466560658176e-16 |

## Descriptive metrics

### Strict

| Scorer | Raw TP | Raw TN | Raw FP | Raw FN | Weighted accuracy | Weighted precision | Weighted recall | Weighted F1 | Weighted kappa |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S0 | 106 | 160 | 534 | 0 | 81.100% | 42.529% | 100.000% | 59.677% | 0.4983 |
| S2 | 106 | 640 | 54 | 0 | 92.776% | 65.941% | 100.000% | 79.475% | 0.7531 |

Raw unweighted analogues:

| Scorer | Accuracy | Precision | Recall | F1 | Kappa |
|---|---:|---:|---:|---:|---:|
| S0 | 33.250% | 16.562% | 100.000% | 28.418% | 0.0736 |
| S2 | 93.250% | 66.250% | 100.000% | 79.699% | 0.7585 |

### Lenient

| Scorer | Raw TP | Raw TN | Raw FP | Raw FN | Weighted accuracy | Weighted precision | Weighted recall | Weighted F1 | Weighted kappa |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S0 | 429 | 125 | 211 | 35 | 86.298% | 81.071% | 78.097% | 79.556% | 0.6926 |
| S2 | 160 | 336 | 0 | 304 | 87.072% | 100.000% | 62.129% | 76.642% | 0.6836 |

Raw unweighted analogues:

| Scorer | Accuracy | Precision | Recall | F1 | Kappa |
|---|---:|---:|---:|---:|---:|
| S0 | 69.250% | 67.031% | 92.457% | 77.717% | 0.3197 |
| S2 | 62.000% | 100.000% | 34.483% | 51.282% | 0.3066 |

## Automated scorer ASR (descriptive)

| Scorer | Raw successes / 800 | Weighted ASR | 95% cluster-bootstrap CI |
|---|---:|---:|---:|
| S0 | 640/800 | 32.886% | [32.886%, 32.886%] |
| S2 | 160/800 | 21.210% | [21.210%, 21.210%] |

Delta ASR (S0−S2) = 11.676%, 95% CI [11.676%, 11.676%]; its direction is structural and was not hypothesis-tested.

## Prespecified weight sensitivity

The Kish effective sample size was 248.9/800, triggering the frozen uncalibrated-IPW sensitivity. Point estimates coincide because observed calibrated stratum totals equal the recorded base-weight totals. The uncalibrated cluster-bootstrap D_STRICT interval was [10.291%, 13.347%].

## Interpretation constraints

S2 success is a mathematical subset of S0 success. The S0–S2 ASR direction and the location of their discordances are therefore not treated as empirical hypotheses. The confirmatory question is alignment with independently adjudicated human judgments. RQ2 is estimation-focused; subgroup tables in the machine-readable output are explicitly exploratory and descriptive.

All sampled D10 records were strict human failures. Under the frozen calibrated percentile bootstrap this boundary result makes D_STRICT and its task-category components invariant across replicates, yielding zero-width primary intervals. The triggered uncalibrated-IPW sensitivity and GEE robust intervals retain sampling variation and are reported without replacing the primary method.

There were zero adjudicated AMBIGUOUS rows, so complete-case and AMBIGUOUS-bound analyses coincide.
