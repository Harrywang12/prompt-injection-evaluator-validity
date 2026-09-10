# Pilot 2 Status

Pilot 2 human annotation and the prespecified weighted analysis are complete.
The decision is `CONTINUE`, but the full-scale study has not begun and requires
explicit approval.

## Candidate pool

- Frozen initial candidates: 672
- Usable raw responses: 672
- Generation failures: 0
- Duplicate IDs / duplicates removed: 0 / 0
- KEY-E positives: 84
- KEY-E negatives: 588
- Victim model: `Qwen/Qwen2.5-1.5B-Instruct`, revision `989aa798...`
- Tasks: seven official Universal-Prompt-Injection task datasets
- Injection variants: 4
- Predetermined targets: 2
- Expansion batches used: 0

Aggregate counts by task, model, target, and variant are in
`candidate_pool_summary.json`. Raw response parts and their hashes are under
`data/raw/pilot2/`. The scorer table and internal sampling table are restricted
research artifacts and must not be shown to the annotator.

## Human sample

Using seed `20260819`, simple random sampling without replacement selected 50
of 84 KEY-E positives and 50 of 588 KEY-E negatives. The inclusion
probabilities are 0.595238 and 0.085034, with weights 1.68 and 11.76,
respectively. The selected records were independently shuffled with seed
`20260820`.

The completed human annotation is preserved at:

- `annotations/pilot2_annotation_blinded.csv`
- `annotations/PILOT2_ANNOTATION_INSTRUCTIONS.md`

The annotation file has 100 unique rows, intact raw response mappings, and no
automated verdict or sampling-stratum columns. Results are in
`pilot2_metrics.json`, `pilot2_summary.csv`, `pilot2_report.md`, and
`pilot2_decision.md`.
