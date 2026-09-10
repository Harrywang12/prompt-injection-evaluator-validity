# Public-safe Phi generation incident audit

Date recorded: August 29, 2026

No raw prompt or response text is included in this audit.

## Original terminal-record census

| Model | Success | Generation failure | Total |
|---|---:|---:|---:|
| Qwen/Qwen2.5-1.5B-Instruct | 1,680 | 0 | 1,680 |
| microsoft/Phi-3.5-mini-instruct | 0 | 1,680 | 1,680 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | 1,679 | 1 | 1,680 |
| **Total** | **3,359** | **1,681** | **5,040** |

The 1,680 Phi failures were systematic repository-remote-code compatibility failures. The original records are preserved in ignored private storage and in a private backup; amended Phi outputs will use a separate namespace. The one SmolLM2 failure remains terminal and unretried.

## Preservation hashes

- Prompt manifest: `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed`
- Generation config: `3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284`
- Original-generation snapshot manifest: `8bca7369fbfbaa78d8adcadab7967aa5a3a2d76ee802b8a591f1985a835913f8`
- Private backup archive: `90465d1463615b3350e3fa4534481c8d6315e5cad733487e22e9e2a71d57287f`
- Native-Phi synthetic diagnostic: `ce4d69f30184f367be9955caf744f0b52c1e6cce32958b29f4caad6642f85232`

No scorer or hypothesis outcome had been inspected before the technical amendment was selected.
