# Public export safety audit

This repository was assembled as a clean export rather than by publishing the authoritative private archive's Git history.

Audit date: 2026-09-10

## Included

- Public protocols and preregistration records.
- Project-owned scorer, sampling, generation, validation, and analysis code.
- Public-safe aggregate results and figures.
- Public audit and freeze records.
- Manuscript source, rendered manuscript, and aggregate-results figure.
- Tests that operate without private fixtures.

## Excluded

- The authoritative archive's `.git` directory and historical private commits.
- `confirmatory_private/`, `external/`, `data/`, and `annotations/`.
- Raw prompts, raw model responses, and terminal generation records.
- Completed row-level annotations, adjudication files, sampling keys, and analysis datasets.
- Per-example scorer tables and flipped-response files.
- Source-dataset dumps, model weights, caches, credentials, and local working files.
- The journal class and logo, whose independent redistribution terms were not established.

## Automated checks

The export was recursively checked for forbidden private paths and filenames, row-level study identifiers, private absolute paths, common credential/token patterns, private-key markers, and data-table schemas associated with raw responses or human labels. Expected schema names occur in reusable code and the annotation manual, but no row-level instances were found. Aggregate tables were inspected separately to confirm their aggregate schemas.

The historical identifiers `confirmatory-preregistered-v1` and `confirmatory-analysis-v1` are documented as provenance but are deliberately not created as tags in this clean repository.
