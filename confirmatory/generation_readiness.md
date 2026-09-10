# Confirmatory generation readiness

Status: **READY TO GENERATE, but generation has not started**

The externally preregistered state is OSF https://osf.io/9jrab and Git tag `confirmatory-preregistered-v1`. The private prompt manifest has 1,680 rows and SHA-256 `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed`. The exact frozen generation config has SHA-256 `3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284`.

## Required private inputs in Colab

Transfer the repository and the ignored file:

`confirmatory_private/prompts/confirmatory_prompt_manifest.jsonl`

Verify its hash before running:

```bash
shasum -a 256 confirmatory_private/prompts/confirmatory_prompt_manifest.jsonl
```

The result must be `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed`. Preserve the entire ignored `confirmatory_private/` directory between Colab sessions, preferably on a mounted persistent drive. Never stage it in Git.

## Frozen runtime checks

The successful preflight used Tesla T4, CUDA 12.8, PyTorch 2.11.0+cu128, Transformers 5.15.0, and native BF16. The runner requires CUDA, BF16, and exactly Transformers 5.15.0. It records harmless runtime differences but stops when a difference would violate a frozen execution requirement.

Install only the confirmatory test/runtime dependency specification. Do **not** install the historical generic `requirements.txt`, which belongs to the pilot/exploratory workflow and pins Transformers 4.52.4. The test specification includes the frozen runtime specification plus `pytest`; the test-tool version is recorded as runtime provenance and is not a scientific design requirement.

```bash
python3 -m pip install --upgrade -r requirements-confirmatory-test.txt
python3 -c 'import transformers; assert transformers.__version__ == "5.15.0", transformers.__version__'
PYTHONPATH=. python3 -m pytest -q tests/test_confirmatory_activation.py
```

`requirements-confirmatory.txt` intentionally does not list PyTorch. Retain Colab's CUDA-enabled PyTorch build; the runner will verify CUDA and native BF16 and record the actual PyTorch/CUDA versions. Never install a replacement CPU wheel to satisfy this project.

Model repositories and revisions are verified through Hugging Face immediately before loading. Authentication may be supplied through normal Hugging Face environment/session mechanisms; tokens must never be written to the repository, manifest, response record, or notebook output.

## Exact runner

From the repository root in Google Colab, run:

```bash
PYTHONPATH=. python3 scripts/run_confirmatory_generation.py --all-models
```

The runner loads one model at a time. If a Colab session ends, rerun the same command after restoring the ignored private directory. Existing terminal records are skipped; they are never overwritten.

Individual models may instead be run in separate sessions with exactly these IDs:

```bash
PYTHONPATH=. python3 scripts/run_confirmatory_generation.py --model-id qwen2_5_1_5b_instruct
PYTHONPATH=. python3 scripts/run_confirmatory_generation.py --model-id phi3_5_mini_instruct
PYTHONPATH=. python3 scripts/run_confirmatory_generation.py --model-id smollm2_1_7b_instruct
```

Do not modify the manifest, config, model IDs/revisions, decoding parameters, output paths, or retry behavior. A technical failure record is terminal under the frozen zero-retry rule and must not be deleted to induce regeneration.

## Expected private outputs

- `confirmatory_private/responses/<model_id>/*.json`: one terminal record per generation key.
- `confirmatory_private/checkpoints/runtime-*.json`: runtime and session provenance.
- `confirmatory_private/checkpoints/pip-freeze-*.txt`: environment inventory.

The complete target is 5,040 terminal generation keys. Scoring and human sampling are separate later phases and must not begin until response completeness/failure validation is performed.
