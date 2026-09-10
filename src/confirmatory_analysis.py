"""Frozen confirmatory analysis dataset and preregistered estimators."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


INPUT_HASHES = {
    "usable_response_manifest.jsonl": "aa543f839be2d489374318ea46d182527d9bd988b07d13284fcc187f1e419f9f",
    "s0_s2_scores.jsonl": "e98889194ab841957aa60cf0825543916a63324f710a319f4900b513186e64bf",
    "human_sample_master.csv": "548253edba237af76373be7ba5064d876a4a76b0f5367a3c5b0e8131477edd6f",
    "sampling_audit.json": "5476c6824705d93c8da06b1b06dc3f953aef4019e86b1046043699c0d002157f",
    "final_adjudicated_human_ground_truth.csv": "20804593269be59b3578fb1e12f033d7b3044895775a21dc2195ca5bb53f11e7",
    "final_human_binary_outcomes.csv": "10deeafa9f83f21f560649d5c4020e5defe5e51d165739afc4cbc9c3b1f19a9a",
}
PROMPT_MANIFEST_SHA256 = "b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed"
GENERATION_CONFIG_SHA256 = "3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284"
BOOTSTRAP_SEED = 2026082207
BOOTSTRAP_REPLICATES = 9999

ANALYSIS_FIELDS = [
    "annotation_item_id",
    "generation_key",
    "confirmatory_prompt_id",
    "model_id",
    "model_repository",
    "model_revision",
    "task",
    "task_category",
    "template_id",
    "target_id",
    "s0",
    "s2",
    "adjudicated_label",
    "strict_human_success",
    "lenient_human_success",
    "annotator_a_label",
    "annotator_a_strict_success",
    "annotator_a_lenient_success",
    "annotator_b_label",
    "annotator_b_strict_success",
    "annotator_b_lenient_success",
    "scorer_cell",
    "sampling_stratum",
    "stratum_population_size",
    "stratum_sample_size",
    "inclusion_probability_numerator",
    "inclusion_probability_denominator",
    "inclusion_probability",
    "analysis_weight",
    "generation_provenance",
    "prompt_manifest_sha256",
    "generation_config_sha256",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        rows = list(reader)
    if not reader.fieldnames or any(
        None in row or any(value is None for value in row.values()) for row in rows
    ):
        raise ValueError(f"malformed CSV: {path}")
    return rows


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def write_csv_immutable(path: Path, rows: list[dict], fields: list[str]) -> None:
    import io

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=fields, extrasaction="raise", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"immutable analysis dataset differs: {path}")
        return
    with path.open("xb") as handle:
        handle.write(payload)


def verify_hashes(paths: dict[str, Path]) -> None:
    if set(paths) != set(INPUT_HASHES):
        raise ValueError("analysis input path set does not match frozen hash set")
    mismatches = {
        name: (sha256_file(path), INPUT_HASHES[name])
        for name, path in paths.items()
        if sha256_file(path) != INPUT_HASHES[name]
    }
    if mismatches:
        raise ValueError(f"frozen analysis input hash mismatch: {mismatches}")


def build_analysis_dataset(paths: dict[str, Path]) -> list[dict[str, str]]:
    verify_hashes(paths)
    usable = {row["generation_key"]: row for row in read_jsonl(paths["usable_response_manifest.jsonl"])}
    scores = {row["generation_key"]: row for row in read_jsonl(paths["s0_s2_scores.jsonl"])}
    master = read_csv(paths["human_sample_master.csv"])
    final = {row["annotation_item_id"]: row for row in read_csv(paths["final_adjudicated_human_ground_truth.csv"])}
    binary = {row["annotation_item_id"]: row for row in read_csv(paths["final_human_binary_outcomes.csv"])}

    if len(usable) != 4993 or len(scores) != 4993 or len(master) != 800:
        raise ValueError("frozen population/sample row counts failed")
    if len(final) != 800 or len(binary) != 800:
        raise ValueError("frozen human ground-truth row counts failed")
    if len({row["annotation_item_id"] for row in master}) != 800 or len(
        {row["generation_key"] for row in master}
    ) != 800:
        raise ValueError("duplicate anonymous or response key in human master")

    rows = []
    for sample in master:
        item_id = sample["annotation_item_id"]
        key = sample["generation_key"]
        if key not in usable or key not in scores or item_id not in final or item_id not in binary:
            raise ValueError(f"missing one-to-one linkage for {item_id}")
        source, score, human, derived = usable[key], scores[key], final[item_id], binary[item_id]
        for field in ("confirmatory_prompt_id", "model_id", "task", "task_category"):
            if str(sample[field]) != str(score[field]) or str(sample[field]) != str(source[field]):
                raise ValueError(f"linkage mismatch for {item_id}: {field}")
        if sample["s0"] != str(score["s0"]) or sample["s2"] != str(score["s2"]):
            raise ValueError(f"scorer linkage mismatch for {item_id}")
        if human["adjudicated_label"] != derived["adjudicated_label"]:
            raise ValueError(f"human binary linkage mismatch for {item_id}")
        if derived["adjudicated_label"] == "AMBIGUOUS":
            raise ValueError("frozen confirmatory ground truth unexpectedly contains AMBIGUOUS")

        def annotator_binary(label: str, lenient: bool) -> str:
            if label == "AMBIGUOUS":
                return ""
            successes = {"FULL_COMPLIANCE", "PARTIAL_COMPLIANCE"} if lenient else {"FULL_COMPLIANCE"}
            return str(int(label in successes))

        n_h = int(sample["stratum_sample_size"])
        N_h = int(sample["stratum_population_size"])
        pi = float(sample["inclusion_probability"])
        weight = float(sample["analysis_weight"])
        if not (0 < pi <= 1) or n_h <= 0 or N_h <= 0:
            raise ValueError(f"invalid sampling values for {item_id}")
        if not math.isclose(pi, n_h / N_h, rel_tol=1e-12) or not math.isclose(
            weight, 1 / pi, rel_tol=1e-12
        ):
            raise ValueError(f"recorded sampling weight mismatch for {item_id}")
        if int(sample["s2"]) and not int(sample["s0"]):
            raise ValueError("S2 subset invariant failed")
        if source["prompt_manifest_sha256"] != PROMPT_MANIFEST_SHA256 or source[
            "generation_config_sha256"
        ] != GENERATION_CONFIG_SHA256:
            raise ValueError("source provenance hash mismatch")
        if source["model_id"] == "phi3_5_mini_instruct" and source[
            "generation_provenance"
        ] == "original":
            raise ValueError("original failed-Phi record entered analysis")

        rows.append(
            {
                "annotation_item_id": item_id,
                "generation_key": key,
                "confirmatory_prompt_id": sample["confirmatory_prompt_id"],
                "model_id": sample["model_id"],
                "model_repository": sample["model_repository"],
                "model_revision": sample["model_revision"],
                "task": sample["task"],
                "task_category": sample["task_category"],
                "template_id": sample["template_id"],
                "target_id": sample["target_id"],
                "s0": sample["s0"],
                "s2": sample["s2"],
                "adjudicated_label": human["adjudicated_label"],
                "strict_human_success": derived["strict_human_success"],
                "lenient_human_success": derived["lenient_human_success"],
                "annotator_a_label": human["annotator_a_label"],
                "annotator_a_strict_success": annotator_binary(
                    human["annotator_a_label"], False
                ),
                "annotator_a_lenient_success": annotator_binary(
                    human["annotator_a_label"], True
                ),
                "annotator_b_label": human["annotator_b_label"],
                "annotator_b_strict_success": annotator_binary(
                    human["annotator_b_label"], False
                ),
                "annotator_b_lenient_success": annotator_binary(
                    human["annotator_b_label"], True
                ),
                "scorer_cell": sample["scorer_cell"],
                "sampling_stratum": sample["sampling_stratum"],
                "stratum_population_size": sample["stratum_population_size"],
                "stratum_sample_size": sample["stratum_sample_size"],
                "inclusion_probability_numerator": sample[
                    "inclusion_probability_numerator"
                ],
                "inclusion_probability_denominator": sample[
                    "inclusion_probability_denominator"
                ],
                "inclusion_probability": sample["inclusion_probability"],
                "analysis_weight": sample["analysis_weight"],
                "generation_provenance": sample["generation_provenance"],
                "prompt_manifest_sha256": sample["prompt_manifest_sha256"],
                "generation_config_sha256": sample["generation_config_sha256"],
            }
        )
    return rows
