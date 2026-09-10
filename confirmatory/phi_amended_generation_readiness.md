# Amended Phi-only generation readiness

Status: **PREPARED; CORRECTED PHI GENERATION HAS NOT RUN**

This is the operational handoff for Amendment 002. It generates only `microsoft/Phi-3.5-mini-instruct` at revision `2fe192450127e6a83f7441aef6e3ca586c338b77`, using the native Transformers 5.15.0 Phi3 implementation (`trust_remote_code=false`).

## Required private state

Extract the amended bundle over a private Colab working directory that contains the untouched original state. The bundle supplies the frozen prompt manifest but deliberately excludes original responses and checkpoints. Before running, ensure these private files are present:

- `confirmatory_private/responses/phi3_5_mini_instruct/`: exactly 1,680 original terminal failure records;
- `confirmatory_private/responses/qwen2_5_1_5b_instruct/`: untouched original Qwen records;
- `confirmatory_private/responses/smollm2_1_7b_instruct/`: untouched original SmolLM2 records;
- `confirmatory_private/checkpoints/original_generation_snapshot_manifest.json`: the unchanged snapshot-manifest file whose SHA-256 is `8bca7369fbfbaa78d8adcadab7967aa5a3a2d76ee802b8a591f1985a835913f8`.

If the snapshot file currently has another name, copy it byte-for-byte to the required path; do not reserialize or edit it.

## Environment and tests

Do not install generic `requirements.txt`.

```bash
python3 -m pip install --upgrade -r requirements-confirmatory-test.txt
python3 -c 'import transformers; assert transformers.__version__ == "5.15.0", transformers.__version__'
PYTHONPATH=. python3 -m pytest -q tests/test_confirmatory_activation.py tests/test_confirmatory_phi_amended.py
```

## Corrected Phi-only command

After preserving the private directory outside the ephemeral Colab runtime, run:

```bash
PYTHONPATH=. python3 scripts/run_confirmatory_phi_amended.py
```

The command has no model selector. It writes only to:

- responses: `confirmatory_private/responses_phi_amended_v1/phi3_5_mini_instruct/`
- checkpoints: `confirmatory_private/checkpoints_phi_amended_v1/`

It refuses to load the model unless the manifest/config hashes, all 1,680 prompt keys, all 1,680 original Phi failure keys, snapshot hash, runtime version, frozen model/revisions, generation parameters, and isolated namespaces pass validation. Existing corrected success and failure records are terminal and skipped on resume.
