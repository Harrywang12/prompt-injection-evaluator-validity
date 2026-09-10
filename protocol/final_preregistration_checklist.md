# Final preregistration checklist

This checklist is evaluated before external submission and again before study activation.

## Design frozen

- [x] Preliminary and exploratory work identified explicitly.
- [x] H1 is the sole primary hypothesis.
- [x] RQ2 is estimation-focused.
- [x] H3 is secondary under fixed-sequence gatekeeping.
- [x] Constructs and seven-category annotation rubric frozen.
- [x] Strict and lenient mappings frozen.
- [x] S0 and S2 implementations frozen; subset relation documented.
- [x] Task categories and base-prompt allocation frozen.
- [x] Injection templates, targets, seeds, and generation settings frozen.
- [x] Human sampling and weighting algorithm frozen.
- [x] Bootstrap, GEE, multiplicity, missingness, ambiguity, and failure rules frozen.
- [x] Exact model and tokenizer revisions recorded.
- [x] Google Colab CUDA/BF16 diagnostic preflight passed for all pinned revisions without study material.
- [x] All seven dataset sources and redistribution conditions audited without treating wrapper licenses as corpus licenses.
- [x] Gigaword replaced before registration/data collection by pinned U.S. federal BillSum `test`; substitution history and rights basis recorded.
- [x] BillSum 8,000-token common eligibility rule, eligible count, split, revision, file hash, and future sampling seed frozen.
- [x] Cross-document consistency and mathematical-constraint audit passed.

## Required before external preregistration

- [x] Every outcome-dependent design choice has a frozen rule or an explicit study-infeasibility stop condition.
- [x] Model revisions, source revision, prompts, generation, scoring, sampling, annotation, estimands, inference, and fallbacks are specified.
- [x] Dataset-use authorization is sufficiently resolved for all active sources; Gigaword is not an active dependency.
- [x] Record supplied successful Colab values: Tesla T4, CUDA 12.8, PyTorch 2.11.0+cu128, BF16 true, Transformers 5.15.0.
- [ ] Add remaining nonessential Colab provenance metadata (date/tier/VRAM/driver/Python/supporting-package versions/log path) when available. **HUMAN INPUT REQUIRED; NOT A PREREGISTRATION BLOCKER**
- [ ] Record the external registry, registration owner, and planned submission timestamp. **HUMAN INPUT REQUIRED**

## Required immediately before study activation

- [ ] External preregistration is public or time-stamped and its identifier is recorded.
- [x] Compatible Google Colab CUDA environment and non-study model/generation preflight recorded.
- [ ] Fill the stable identities of Annotator A, Annotator B, and the independent adjudicator. **HUMAN INPUT REQUIRED**
- [ ] Confirm all three people accept the frozen manual and independence/blinding requirements. **HUMAN INPUT REQUIRED**
- [ ] Source and model file hashes match frozen manifests.
- [ ] No confirmatory source sample or victim response predates registration.
- [ ] Raw-output, derived-output, and annotation paths are separate from Pilot 1/Pilot 2.
- [ ] Secret scan and clean-tree check pass.
- [ ] Test suite passes in the execution environment.
- [ ] Annotator files contain no model/scorer/stratum/weight fields.

The scientific design and active dataset sources are frozen and the package is ready for external preregistration. It has not been submitted. Study activation still requires a time-stamped registration, named personnel, manifest checks, and every activation item above. Failure to reproduce the BillSum eligibility count or fill a frozen task quota makes the design infeasible rather than authorizing a source, threshold, or allocation change.
