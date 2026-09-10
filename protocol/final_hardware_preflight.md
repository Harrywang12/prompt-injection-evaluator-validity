# Final hardware preflight

Status: **RESOLVED for the frozen generation configuration**, based on the project operator's completed non-study diagnostic preflight in Google Colab. No local CUDA preflight was rerun.

## Intended execution environment

The confirmatory generation environment is Google Colab with a CUDA GPU. Models will be loaded sequentially, one at a time, at batch size 1 using the exact revisions in `final_model_revisions.yaml` and the immutable generation settings in `final_generation_config.yaml`.

The completed preflight established all of the following:

- CUDA was available.
- The assigned GPU reported native bfloat16 support.
- Frozen batch size 1 executed successfully.
- Greedy decoding with `do_sample=false` executed successfully.
- `max_new_tokens=128` executed successfully.
- Each pinned tokenizer and model loaded at its exact revision.
- All three models completed the same non-study diagnostic procedure.

| Model | Frozen revision | Load | Frozen diagnostic generation |
|---|---|---|---|
| `Qwen/Qwen2.5-1.5B-Instruct` | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | PASS | PASS |
| `microsoft/Phi-3.5-mini-instruct` | `2fe192450127e6a83f7441aef6e3ca586c338b77` | PASS | PASS |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | `31b70e2e869a7173562077fd711b654946d38674` | PASS | PASS |

Only trivial diagnostic prompts were used. The preflight did not use or generate a confirmatory prompt, source row, legitimate task instance, injection template, target string, attack, scorer input, or study output. Diagnostic text and generations are excluded from every study population and analysis.

## Recorded successful runtime values

The operator supplied the following exact values from the completed preflight:

- Preflight date/time and timezone: `[HUMAN INPUT REQUIRED: paste exact value]`
- Colab runtime type/tier: `[HUMAN INPUT REQUIRED: paste exact value]`
- GPU model: `Tesla T4`
- GPU VRAM: `[HUMAN INPUT REQUIRED: paste exact value]`
- NVIDIA driver: `[HUMAN INPUT REQUIRED: paste exact value]`
- CUDA available: `True`
- CUDA version reported by PyTorch: `12.8`
- Python: `[HUMAN INPUT REQUIRED: paste exact value]`
- PyTorch: `2.11.0+cu128`
- Native bfloat16 support: `True`
- Transformers: `5.15.0`
- Accelerate: `[HUMAN INPUT REQUIRED: paste exact value]`
- Hugging Face Hub client: `[HUMAN INPUT REQUIRED: paste exact value]`
- Exact trivial diagnostic prompt(s), or the retained preflight log path: `[HUMAN INPUT REQUIRED: paste value]`

Immediately before confirmatory generation, the operator must save these runtime values, the Colab notebook revision/hash, model/config/tokenizer file hashes, and the output of the same non-study load diagnostic. A different GPU assignment is acceptable only if CUDA and native bfloat16 remain available and the frozen configuration passes; generation parameters may not be tuned by model or after observing study outputs.
