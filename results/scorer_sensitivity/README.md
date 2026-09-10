# Scorer-Sensitivity Artifacts

This directory contains the explicitly exploratory post-Pilot-2 lexical
scorer-implementation sensitivity analysis. The frozen protocol is
`protocol/scorer_sensitivity_exploratory.md`.

Reproduce all derived tables and figures with:

```sh
make analyze-scorer-sensitivity
```

The workflow reads only the frozen 672 Pilot 2 responses and never invokes
model generation. See `report.md` for interpretation and `decision.md` for the
`CONTINUE` decision.
