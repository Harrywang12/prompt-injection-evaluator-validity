# Exploratory Scorer-Sensitivity Decision

## CONTINUE

The scorer implementation choices produce a sufficiently meaningful change
to justify designing a fresh confirmatory study, but no such study has begun.

The overall full-pool ASR range is modest—1.79 percentage points—and 660/672
examples receive the same verdict from all six scorers. Nevertheless, prefix
semantics change 10 original verdicts, reduce grammar-correction ASR by 8.33
points, and improve strict raw human agreement from 89% (kappa 0.780) to 96%
(kappa 0.917), a 7-percentage-point increase from S0 to S2. The 8-point raw
range across all variants instead compares S1 (88%) with S2/S3 (96%). Weighted
strict agreement similarly rises from 97.25% to 99.00%. These changes affect
individual verdicts, a subgroup conclusion, and agreement with human judgment,
satisfying the protocol's `CONTINUE` criterion.

The result does not justify claiming that prefix scoring is universally
superior. Under the lenient human definition, casefold and prefix scoring both
reach 96% raw accuracy but make opposite kinds of errors. Unicode normalization
has no effect with the two ASCII targets, and strict versus left-stripped
prefix scoring is identical because no leading-whitespace case occurs.

Any confirmatory follow-up must be newly designed and prospectively freeze the
relationship between target semantics and scorer implementation. It should
test independent targets and datasets, include targets for which Unicode and
case handling are genuinely relevant, and retain both strict and lenient human
definitions. This decision does not authorize new model generation or a new
multi-model experiment.
