# Pilot Decision

## MODIFY

The pilot does not support the preregistered overestimation hypothesis in this
sample. KEY-E and strict human judgment both produced a 10.0% ASR, for a 0.0
percentage-point difference; all 50 paired verdicts agreed. There were no
false positives, no false negatives, and no `REFUSAL_QUOTATION` examples. The
partial-compliance sensitivity analysis was identical because no annotation
used `PARTIAL_COMPLIANCE`.

Scaling this exact single-model, single-target, fixed-template design to a few
thousand examples is not warranted on the pilot evidence. It did not contain
the cases needed to evaluate the preregistered mechanism, and its perfect
agreement may be specific to this narrow construction. At the same time, a
sample of 50 with zero discordances remains compatible with a population
discordance probability as high as 7.11% at the two-sided 95% exact upper
bound, so the pilot is not sufficient grounds to abandon the research
question.

Before any full-scale study, the design should be modified prospectively to:

1. include at least two independently designed sources and more than one
   victim model or target type, without selecting examples based on whether
   they support the hypothesis;
2. separate a representative ASR-discrepancy estimate from an explicitly
   labelled mechanistic stress test that can evaluate refusal quotations;
3. add a prospective `ATTACK_IGNORED_TASK_FOLLOWED` failure category, or an
   equivalent rubric clarification, in a second annotation round while
   preserving every original pilot label; and
4. run a new small blinded validation round before committing resources to the
   full study.

These changes are motivated by coverage and construct-validity limitations,
not by an attempt to force a positive result. They require approval before a
new round because they are post-outcome amendments. The full-scale study has
not begun.
