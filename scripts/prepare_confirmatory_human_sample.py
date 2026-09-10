#!/usr/bin/env python3
"""Build the private scored population and frozen blinded human sample.

The command deliberately emits no ASR, model/task scorer breakdown, or
hypothesis statistic. Raw text and row-level scorer data remain private.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from src.confirmatory import load_private_manifest, sha256_file
from src.confirmatory_human_sample import (
    ANNOTATION_A_ORDER_SEED,
    ANNOTATION_B_ORDER_SEED,
    BLINDED_FIELDS,
    GENERATION_CONFIG_SHA256,
    HUMAN_SAMPLE_SIZE,
    HUMAN_SAMPLING_SEED,
    MODEL_SPECS,
    PROMPT_MANIFEST_SHA256,
    allocate_and_sample,
    blinded_rows,
    build_usable_population,
    join_sample_context,
    score_population,
    validate_blinded_files,
    write_csv,
    write_jsonl,
)


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = ROOT / "confirmatory_private"
SCORING_ROOT = PRIVATE_ROOT / "scoring"
SAMPLE_ROOT = PRIVATE_ROOT / "human_sample"
USABLE_PATH = SCORING_ROOT / "usable_response_manifest.jsonl"
SCORES_PATH = SCORING_ROOT / "s0_s2_scores.jsonl"
MASTER_PATH = SAMPLE_ROOT / "human_sample_master.csv"
AUDIT_PATH = SAMPLE_ROOT / "sampling_audit.json"
ANNOTATION_A_PATH = SAMPLE_ROOT / "confirmatory_annotation_A_blinded.csv"
ANNOTATION_B_PATH = SAMPLE_ROOT / "confirmatory_annotation_B_blinded.csv"
PUBLIC_AUDIT_PATH = ROOT / "confirmatory/human_sampling_activation_audit.md"

MASTER_FIELDS = [
    "annotation_item_id",
    "generation_key",
    "confirmatory_prompt_id",
    "model_id",
    "model_repository",
    "model_revision",
    "tokenizer_revision",
    "task",
    "task_category",
    "template_id",
    "target_id",
    "target_text",
    "legitimate_instruction",
    "legitimate_input",
    "legitimate_reference_answer",
    "injected_instruction",
    "target_behavior",
    "raw_decoded_response",
    "source_record_path",
    "generation_provenance",
    "prompt_manifest_sha256",
    "generation_config_sha256",
    "s0",
    "s2",
    "scorer_cell",
    "sampling_stratum",
    "stratum_population_size",
    "stratum_sample_size",
    "inclusion_probability_numerator",
    "inclusion_probability_denominator",
    "inclusion_probability",
    "analysis_weight",
    "human_sampling_seed",
]


def validate_master(master: list[dict], usable: list[dict]) -> None:
    if len(master) != HUMAN_SAMPLE_SIZE:
        raise RuntimeError("private master does not contain 800 rows")
    usable_keys = {row["generation_key"] for row in usable}
    keys = [row["generation_key"] for row in master]
    if len(keys) != len(set(keys)) or not set(keys).issubset(usable_keys):
        raise RuntimeError("sample keys are duplicated or outside usable population")
    for row in master:
        pi = row["inclusion_probability"]
        weight = row["analysis_weight"]
        if not (0 < pi <= 1) or not math.isclose(weight, 1 / pi, rel_tol=1e-12):
            raise RuntimeError("invalid inclusion probability/analysis weight")
        if row["scorer_cell"] not in {"D10", "A00", "A11"}:
            raise RuntimeError("invalid scorer cell in private master")
        if row["task_category"] not in {
            "generative_text_transformation",
            "closed_label_classification",
        }:
            raise RuntimeError("invalid task category")
        if row["model_id"] not in MODEL_SPECS:
            raise RuntimeError("invalid internal model identity")
        if row["generation_provenance"] == "original" and row[
            "model_id"
        ] == "phi3_5_mini_instruct":
            raise RuntimeError("original failed-Phi record entered human sample")


def write_public_audit(
    *,
    census: dict,
    sampling: dict,
    artifact_hashes: dict[str, str],
) -> None:
    sample_cells = sampling["sample_scorer_cell_counts"]
    disagreement_n = sample_cells.get("D10", 0)
    controls_n = sample_cells.get("A00", 0) + sample_cells.get("A11", 0)
    mode = "census" if sampling["disagreement_census"] else "stratified probability sample"
    model_lines = "\n".join(
        f"- `{model_id}`: {count:,}"
        for model_id, count in sorted(census["usable_model_counts"].items())
    )
    hash_lines = "\n".join(
        f"- `{name}`: `{digest}`" for name, digest in sorted(artifact_hashes.items())
    )
    PUBLIC_AUDIT_PATH.write_text(
        f"""# Confirmatory human-sampling activation audit

Audit date: 2026-09-07 (America/Toronto)

Status: **PASS — blinded double-annotation files prepared; no human labels collected**

This public-safe audit contains no prompt or response text, row-level scorer verdicts, ASR, model/task scorer comparisons, human labels, or hypothesis results.

## Frozen usable generation population

- Planned generation keys: 5,040
- Usable successful nonempty responses: 4,993
- Final technical failures: 47
- Original remote-code Phi failures retained only as provenance and excluded: 1,680

Usable counts by model:

{model_lines}

The usable manifest contains unique `(confirmatory_prompt_id, model_revision)` keys, contains no failed or empty response, and uses the amended native-Phi namespace rather than the original failed-Phi namespace. S2-implies-S0 structural validation passed.

## Frozen human sampling

- Sampling seed: `{HUMAN_SAMPLING_SEED}`
- Annotator A order seed: `{ANNOTATION_A_ORDER_SEED}`
- Annotator B order seed: `{ANNOTATION_B_ORDER_SEED}`
- Target and achieved human sample: 800
- Sampled disagreement records: {disagreement_n}
- Sampled agreement controls: {controls_n}
- Disagreement selection mode: {mode}

The procedure applied the preregistered quota rule, model-by-task strata within each scorer cell, Hamilton largest-remainder allocation with frozen lexical tie-breaking, capacity redistribution, and seeded sampling without replacement. Every sampled row retains `N_h`, `n_h`, exact rational inclusion probability, and inverse-probability weight privately. Agreement controls cover both scorer-agreement cells, all three usable model families, and both frozen task categories.

Annotators A and B receive the same 800 anonymous item IDs in independently randomized orders. Their files omit model/revision, scorer verdicts and cell, stratum, probabilities, weights, generation provenance, source paths, and the other annotator's fields. All label, confidence, and notes cells are blank. CSV round-trip validation confirmed exact preservation of annotation-visible response and task text.

## Private artifact SHA-256 hashes

{hash_lines}

All listed artifacts are ignored by Git because they contain row-level scorer information, upstream source text, or raw model responses. The frozen prompt-manifest SHA-256 remains `{PROMPT_MANIFEST_SHA256}` and the frozen generation-config SHA-256 remains `{GENERATION_CONFIG_SHA256}`.
""",
        encoding="utf-8",
    )


def main() -> None:
    usable, census = build_usable_population(PRIVATE_ROOT)
    scores = score_population(usable)
    sampled, sampling = allocate_and_sample(scores)
    prompts = load_private_manifest(
        PRIVATE_ROOT / "prompts/confirmatory_prompt_manifest.jsonl"
    )
    master = join_sample_context(sampled, usable, prompts)
    validate_master(master, usable)

    write_jsonl(USABLE_PATH, usable)
    write_jsonl(SCORES_PATH, scores)
    write_csv(MASTER_PATH, master, MASTER_FIELDS)
    write_csv(
        ANNOTATION_A_PATH,
        blinded_rows(master, ANNOTATION_A_ORDER_SEED),
        BLINDED_FIELDS,
    )
    write_csv(
        ANNOTATION_B_PATH,
        blinded_rows(master, ANNOTATION_B_ORDER_SEED),
        BLINDED_FIELDS,
    )
    validate_blinded_files(ANNOTATION_A_PATH, ANNOTATION_B_PATH, master)

    artifact_paths = {
        "usable_response_manifest.jsonl": USABLE_PATH,
        "s0_s2_scores.jsonl": SCORES_PATH,
        "human_sample_master.csv": MASTER_PATH,
        "confirmatory_annotation_A_blinded.csv": ANNOTATION_A_PATH,
        "confirmatory_annotation_B_blinded.csv": ANNOTATION_B_PATH,
    }
    artifact_hashes = {name: sha256_file(path) for name, path in artifact_paths.items()}
    private_audit = {
        "status": "PASS",
        "usable_population_count": len(usable),
        **census,
        "s2_implies_s0": all(not row["s2"] or row["s0"] for row in scores),
        "human_sampling_seed": HUMAN_SAMPLING_SEED,
        "annotation_order_seeds": {
            "annotator_a": ANNOTATION_A_ORDER_SEED,
            "annotator_b": ANNOTATION_B_ORDER_SEED,
        },
        "human_sample_size": len(master),
        **sampling,
        "private_artifact_sha256": artifact_hashes,
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(
        json.dumps(private_audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    artifact_hashes["sampling_audit.json"] = sha256_file(AUDIT_PATH)
    write_public_audit(census=census, sampling=sampling, artifact_hashes=artifact_hashes)

    sample_cells = sampling["sample_scorer_cell_counts"]
    safe_summary = {
        "status": "PASS",
        "usable_population": len(usable),
        "usable_model_counts": census["usable_model_counts"],
        "technical_failures": census["technical_failure_total"],
        "s2_subset_validation": "PASS",
        "human_sample_size": len(master),
        "sampled_disagreement": sample_cells.get("D10", 0),
        "sampled_agreement_controls": sample_cells.get("A00", 0)
        + sample_cells.get("A11", 0),
        "private_artifact_sha256": artifact_hashes,
    }
    print(json.dumps(safe_summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
