# Amendment 002: Phi generation compatibility

## Registration and timing

- External preregistration: https://osf.io/9jrab
- Preregistration submission timestamp: August 19, 2026, 7:06:59 PM
- Preregistered scientific commit: `853eb6aa7c61e03896cdca3eb991fcf8debdc9cc`
- Incident reported and amendment prepared: August 29, 2026 (an exact incident-discovery time was not supplied)
- Timing relative to study: confirmatory generation had begun, but no S0/S2 scoring, ASR calculation, human sampling, or H1/RQ2/H3 analysis had occurred when the compatibility correction was chosen.

This document is a post-preregistration protocol amendment. It does not rewrite the original preregistration.

## Frozen generation census at incident discovery

| Model | Success | Generation failure | Total |
|---|---:|---:|---:|
| Qwen/Qwen2.5-1.5B-Instruct | 1,680 | 0 | 1,680 |
| microsoft/Phi-3.5-mini-instruct | 0 | 1,680 | 1,680 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | 1,679 | 1 | 1,680 |

All 5,040 original terminal records are preserved outside Git. Qwen and SmolLM2 will not be regenerated. The single SmolLM2 technical failure remains terminal and will not be retried under the frozen zero-retry/no-replacement rule.

## Incident and root cause

The original Phi run used the preregistered `trust_remote_code: true` setting for both tokenizer and model loading. The pinned repository configuration maps `AutoModelForCausalLM` to the repository implementation `modeling_phi3.Phi3ForCausalLM`. Under Transformers 5.15.0, every Phi attempt failed with:

```text
AttributeError: 'DynamicCache' object has no attribute 'seen_tokens'
```

The traceback originated in the pinned repository remote `modeling_phi3.py`, in `prepare_inputs_for_generation()` at:

```text
past_length = past_key_values.seen_tokens
```

The remote implementation expected a cache attribute unavailable in the frozen Transformers runtime. This was a systematic implementation compatibility failure, not a prompt-dependent or outcome-dependent failure.

## Synthetic compatibility diagnostic

A non-study diagnostic used only the trivial synthetic prompt `Reply with OK.` No confirmatory prompt, source row, target, injection, or victim response was used.

- NumPy: 2.1.3
- Transformers: 5.15.0
- PyTorch: 2.11.0+cu128
- CUDA: 12.8
- GPU: Tesla T4
- Native BF16: supported
- Model/tokenizer repository: `microsoft/Phi-3.5-mini-instruct`
- Model revision: `2fe192450127e6a83f7441aef6e3ca586c338b77`
- Tokenizer revision: `2fe192450127e6a83f7441aef6e3ca586c338b77`
- Loading: `trust_remote_code=false`
- Resolved class: `Phi3ForCausalLM`
- Resolved module: `transformers.models.phi3.modeling_phi3`
- Synthetic generation: PASS
- Diagnostic SHA-256: `ce4d69f30184f367be9955caf744f0b52c1e6cce32958b29f4caad6642f85232`

## Amended implementation

For Phi only, loading changes from `trust_remote_code=true` to `trust_remote_code=false`. The amended runner must assert that the resolved model module begins with `transformers.models.phi3` before any confirmatory generation. Corrected terminal records are written only under `confirmatory_private/responses_phi_amended_v1/phi3_5_mini_instruct/`, with checkpoints under `confirmatory_private/checkpoints_phi_amended_v1/`.

This change is classified as a **post-preregistration protocol amendment**, because `trust_remote_code: true` was explicitly present in the preregistered model-revision file. The change was selected solely from the complete technical-failure census and synthetic compatibility evidence, before any confirmatory scorer or hypothesis outcome was inspected.

## Unchanged design elements

The following remain unchanged:

- exact Phi weights, repository, model revision, tokenizer, and tokenizer revision;
- all 1,680 prompt IDs and prompt contents;
- prompt-manifest SHA-256 `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed`;
- generation-config SHA-256 `3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284`;
- Transformers 5.15.0, CUDA/BF16, eager attention, batch size 1, greedy decoding, `do_sample=false`, `max_new_tokens=128`, unset temperature/top-p/top-k, tokenizer EOS/pad IDs, chat-template behavior, message construction, decoding behavior, and seed `2026082203`;
- zero automatic retries, no replacement prompts, immutable terminal records, and raw response preservation;
- H1, RQ2, H3, S0/S2, human sampling and annotation, statistical methods, and multiplicity.

## Preservation evidence

- Original-generation snapshot-manifest SHA-256: `8bca7369fbfbaa78d8adcadab7967aa5a3a2d76ee802b8a591f1985a835913f8`
- Private backup archive SHA-256: `90465d1463615b3350e3fa4534481c8d6315e5cad733487e22e9e2a71d57287f`
- Synthetic diagnostic SHA-256: `ce4d69f30184f367be9955caf744f0b52c1e6cce32958b29f4caad6642f85232`

The amended runner requires the original 1,680 Phi failure files and the exact snapshot manifest to remain present, validates the failure-key set before model loading, records hashes of corresponding original failures in corrected records, and refuses to write inside the original response tree.
