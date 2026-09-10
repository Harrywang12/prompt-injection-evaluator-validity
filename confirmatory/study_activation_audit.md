# Confirmatory study activation audit

Status: **PASS — prepared for generation; no victim-model response generated**

Activation timestamp: `2026-08-19T19:26:22-0400` (`EDT`)

## Preregistration boundary

- OSF registration: https://osf.io/9jrab
- User-supplied submission timestamp, preserved verbatim: August 19, 2026, 7:06:59 PM
- The OSF timestamp's timezone is not present in local metadata and is not inferred.
- Activation was initiated only after the user confirmed successful external submission. Its recorded local wall-clock time is later than the supplied registration wall-clock time.
- `confirmatory-preregistered-v1^{commit}` resolves to `853eb6aa7c61e03896cdca3eb991fcf8debdc9cc`.
- Administrative registration record: `protocol/external_preregistration_record.md`.
- No confirmatory model output or confirmatory human annotation existed before registration or during this activation-preparation task.

## Frozen prompt sample

The private text-bearing manifest is `confirmatory_private/prompts/confirmatory_prompt_manifest.jsonl`. It is ignored by Git and is not part of the public commit.

- Prompt-manifest SHA-256: `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed`
- Frozen generation-config SHA-256: `3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284`
- Independent base prompts: 1,680
- Expected model-response keys: 5,040
- Prohibited exploratory overlap: 0

| Task | Category | Eligible | Selected | Per template-target cell |
|---|---|---:|---:|---:|
| Grammar correction | Generative/text transformation | 646 | 240 | 30 |
| Summarization (BillSum U.S. `test`) | Generative/text transformation | 3,268 | 240 | 30 |
| Duplicate sentence detection | Closed-label classification | 307 | 256 | 32 |
| Hate detection | Closed-label classification | 24,679 | 256 | 32 |
| Natural language inference | Closed-label classification | 178 | 176 | 22 |
| Sentiment analysis | Closed-label classification | 770 | 256 | 32 |
| Spam detection | Closed-label classification | 5,058 | 256 | 32 |
| **Total selected** |  |  | **1,680** |  |

Category totals are exactly 480 generative/text-transformation and 1,200 closed-label classification. Each task is exactly balanced over four injection templates and two targets. Aggregate template totals are 420 each; aggregate target totals are 840 each.

BillSum is active at `FiscalNote/billsum` revision `3d8510441c06a3d9dfb32eb0d7f80151730bcc4f`, U.S. federal `test` only. The full all-tokenizer/all-variant 8,000-token rule yielded 3,268 eligible rows; one row was excluded for context length. `train` and `ca_test` are excluded. Gigaword is inactive.

## Exclusion and freshness checks

The exact per-task counts by missing field, invalid label, duplicate, exploratory source-ID overlap, exploratory normalized-content overlap, and context length are recorded in `prompt_manifest_audit.json`. Selected source rows were not inspected or altered manually. Freshness uses the frozen Pilot 1/Pilot 2 source-ID and normalized-content-hash exclusions. The selected overlap count is zero.

## Private-data and runner checks

- `.gitignore` excludes the complete `confirmatory_private/` tree before prompts or responses are stored.
- Restricted source text, exact prompts, references, source-row IDs, raw responses, downloaded tokenizers, and checkpoints are absent from the public audit and commit.
- `scripts/run_confirmatory_generation.py` verifies the two frozen hashes and all 5,040 unique keys before loading a model.
- The runner requires CUDA, native BF16, Transformers 5.15.0, greedy decoding, eager attention, batch size 1, 128 new tokens, tokenizer pad/EOS IDs, and the pinned model/tokenizer revisions. It fails rather than falling back.
- One immutable terminal JSON record is created per `(confirmatory_prompt_id, model revision)` with exclusive-create semantics. Existing terminal records are skipped and cannot be overwritten. Technical failures are retained and receive no automatic retry.
- Raw decoded response strings are not stripped, normalized, lowercased, or cleaned. Leading whitespace survives JSON round-trip.
- Runtime GPU/CUDA/Python/PyTorch/Transformers/Accelerate/BF16 information, exact revision checks, hashes, session times, and `pip freeze` are written to the ignored checkpoint area.

## Verification result

All 53 repository tests passed. Tests cover the exact prompt/task/category/cell counts, zero overlap, BillSum and model revisions, generation settings, 5,040 unique keys, resume/overwrite behavior, leading whitespace, Git ignores, and public-audit field safety.

No frozen hypothesis, task, dataset, model, scorer, annotation, sampling, generation, statistical, multiplicity, exclusion, seed, or fallback rule was changed. No protocol deviation occurred.
