# Reporting Correction 001: Strict Human-Agreement Difference

## Timing

This correction was identified on 2026-08-17 during the requested final audit,
after the exploratory scorer-sensitivity results and decision were committed
at `000c4b6`.

## Original wording

`report.md` stated that implementation choice changed “strict raw human
agreement by eight points” immediately after discussing prefix semantics. That
wording was ambiguous and is incorrect if read as the S0-to-S2 comparison.

`decision.md` reported the correct endpoint values—89% for S0 and 96% for
S2—but did not explicitly state their difference. It did not itself claim that
89% to 96% was eight points.

## Correction

- S0 strict raw accuracy: 89/100 = 89%.
- S2 strict raw accuracy: 96/100 = 96%.
- S0-to-S2 increase: **7 percentage points**.
- Minimum strict raw accuracy across all six scorers: S1 at 88%.
- Maximum strict raw accuracy across all six scorers: S2/S3 at 96%.
- Maximum-minus-minimum range across all variants: **8 percentage points**.

The report and decision now distinguish the 7-point S0/S2 contrast from the
8-point across-scorer range.

## Scope

This is a reporting clarification only. No scorer definition, per-example
verdict, human label, metric table, figure, or underlying result changed.
