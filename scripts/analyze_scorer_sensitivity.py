#!/usr/bin/env python3
"""Execute the frozen exploratory scorer grid on Pilot 2's 672 responses."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import unicodedata
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib
import matplotlib.pyplot as plt

from src.metrics import classification_metrics, cohens_kappa, confusion_counts, safe_divide
from src.scorer_sensitivity import SCORERS, mechanical_flip_flags, score_all


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/scorer_sensitivity"
RAW_DIR = ROOT / "data/raw/pilot2"
CANDIDATES = ROOT / "data/derived/pilot2/candidate_inputs.csv"
PILOT2_SCORED = ROOT / "data/derived/pilot2/scored_candidates.csv"
HUMAN_ANNOTATIONS = ROOT / "annotations/pilot2_annotation_blinded.csv"
HUMAN_INTERNAL = ROOT / "data/derived/pilot2/human_sample_internal.csv"
HUMAN_MANIFEST = ROOT / "data/derived/pilot2/human_sample_manifest.json"
EXPECTED_ANNOTATION_SHA256 = "5f6619cc5af82a30d9cf9bf32bcb90d68f9d0668b0b1e44d2cffb5c872a24b18"
VALID_HUMAN_LABELS = {
    "FULL_COMPLIANCE",
    "PARTIAL_COMPLIANCE",
    "INJECTION_IGNORED",
    "REFUSAL",
    "REFUSAL_QUOTATION",
    "OFF_TOPIC_FAILURE",
    "AMBIGUOUS",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def parse_bool(value: str) -> bool:
    if value.lower() not in {"true", "false"}:
        raise ValueError(f"invalid Boolean value: {value!r}")
    return value.lower() == "true"


def load_frozen_population() -> list[dict]:
    _, candidates = read_csv(CANDIDATES)
    if len(candidates) != 672 or len({row["sample_id"] for row in candidates}) != 672:
        raise ValueError("expected 672 unique frozen Pilot 2 candidate inputs")

    raw_parts = sorted(RAW_DIR.glob("batch_*_part_*.jsonl"))
    raw: list[dict] = []
    for path in raw_parts:
        with path.open(encoding="utf-8") as handle:
            raw.extend(json.loads(line) for line in handle if line.strip())
    raw_by_id = {row["sample_id"]: row for row in raw}
    if len(raw) != 672 or len(raw_by_id) != 672:
        raise ValueError("expected 672 unique frozen Pilot 2 raw responses")
    if set(raw_by_id) != {row["sample_id"] for row in candidates}:
        raise ValueError("candidate/raw sample-ID mapping mismatch")
    if any(row["generation_status"] != "ok" or not row["victim_response"].strip() for row in raw):
        raise ValueError("the frozen population contains a nonusable response")

    manifest = json.loads((RAW_DIR / "manifest_batch_000.json").read_text(encoding="utf-8"))
    actual_hashes = {path.name: sha256(path) for path in raw_parts}
    if actual_hashes != manifest["parts"]:
        raise ValueError("frozen raw-part hashes differ from the Pilot 2 manifest")

    _, old_scored = read_csv(PILOT2_SCORED)
    old_by_id = {row["sample_id"]: row for row in old_scored}
    if len(old_by_id) != 672 or set(old_by_id) != set(raw_by_id):
        raise ValueError("existing Pilot 2 scorer table does not cover the frozen population")

    joined: list[dict] = []
    for candidate in candidates:
        sample_id = candidate["sample_id"]
        response = raw_by_id[sample_id]["victim_response"]
        verdicts = score_all(response, candidate["target_text"])
        old = old_by_id[sample_id]
        if old["victim_response"] != response:
            raise ValueError(f"derived/raw response mismatch for {sample_id}")
        if parse_bool(old["lexical_key_e_success"]) != verdicts["S0_ORIGINAL"]:
            raise ValueError(f"S0 does not reproduce frozen Pilot 2 KEY-E for {sample_id}")
        joined.append(
            {
                "sample_id": sample_id,
                "task": candidate["task"],
                "target_id": candidate["target_id"],
                "target_text": candidate["target_text"],
                "victim_response": response,
                "verdicts": verdicts,
            }
        )
    return joined


def binary_cells(truth: list[bool], prediction: list[bool]) -> dict[str, int]:
    return confusion_counts(truth, prediction)


def metrics_from_cells(cells: dict[str, float]) -> dict[str, float | None]:
    tn = cells["true_negative"]
    fp = cells["false_positive"]
    fn = cells["false_negative"]
    tp = cells["true_positive"]
    total = tn + fp + fn + tp
    accuracy = safe_divide(tp + tn, total)
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    f1 = None if precision is None or recall is None else safe_divide(2 * precision * recall, precision + recall)
    truth_positive = safe_divide(tp + fn, total)
    predicted_positive = safe_divide(tp + fp, total)
    if accuracy is None or truth_positive is None or predicted_positive is None:
        kappa = None
    else:
        expected = truth_positive * predicted_positive + (1 - truth_positive) * (1 - predicted_positive)
        kappa = safe_divide(accuracy - expected, 1 - expected)
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "cohens_kappa": kappa,
    }


def full_pool_tables(rows: list[dict]) -> dict:
    scorer_ids = list(SCORERS)
    denominator = len(rows)
    s0 = [row["verdicts"]["S0_ORIGINAL"] for row in rows]
    aggregate: list[dict] = []
    for scorer_id in scorer_ids:
        verdicts = [row["verdicts"][scorer_id] for row in rows]
        successes = sum(verdicts)
        aggregate.append(
            {
                "scorer_id": scorer_id,
                "success_count": successes,
                "denominator": denominator,
                "asr": successes / denominator,
                "absolute_asr_difference_from_s0_pp": abs(successes - sum(s0)) / denominator * 100,
                "verdict_flips_relative_to_s0": sum(a != b for a, b in zip(verdicts, s0, strict=True)),
            }
        )

    pairwise: list[dict] = []
    disagreement_lookup: dict[tuple[str, str], int] = {}
    for scorer_a, scorer_b in combinations(scorer_ids, 2):
        a = [row["verdicts"][scorer_a] for row in rows]
        b = [row["verdicts"][scorer_b] for row in rows]
        cells = binary_cells(a, b)
        disagreement = cells["false_positive"] + cells["false_negative"]
        disagreement_lookup[(scorer_a, scorer_b)] = disagreement
        pairwise.append(
            {
                "scorer_a": scorer_a,
                "scorer_b": scorer_b,
                "both_negative": cells["true_negative"],
                "a_negative_b_positive": cells["false_positive"],
                "a_positive_b_negative": cells["false_negative"],
                "both_positive": cells["true_positive"],
                "disagreement_count": disagreement,
                "agreement_count": denominator - disagreement,
                "raw_agreement": (denominator - disagreement) / denominator,
                "cohens_kappa": cohens_kappa(a, b),
            }
        )
    matrix_rows = []
    for scorer_a in scorer_ids:
        matrix_row = {"scorer_id": scorer_a}
        for scorer_b in scorer_ids:
            if scorer_a == scorer_b:
                value = 0
            elif (scorer_a, scorer_b) in disagreement_lookup:
                value = disagreement_lookup[(scorer_a, scorer_b)]
            else:
                value = disagreement_lookup[(scorer_b, scorer_a)]
            matrix_row[scorer_b] = value
        matrix_rows.append(matrix_row)
    return {"aggregate": aggregate, "pairwise": pairwise, "matrix": matrix_rows}


def subgroup_table(rows: list[dict], field: str) -> list[dict]:
    output: list[dict] = []
    for subgroup in sorted({row[field] for row in rows}):
        group = [row for row in rows if row[field] == subgroup]
        any_disagreement = sum(len(set(row["verdicts"].values())) > 1 for row in group)
        s0_count = sum(row["verdicts"]["S0_ORIGINAL"] for row in group)
        for scorer_id in SCORERS:
            success_count = sum(row["verdicts"][scorer_id] for row in group)
            flips = sum(
                row["verdicts"][scorer_id] != row["verdicts"]["S0_ORIGINAL"]
                for row in group
            )
            output.append(
                {
                    field: subgroup,
                    "scorer_id": scorer_id,
                    "denominator": len(group),
                    "success_count": success_count,
                    "asr": success_count / len(group),
                    "s0_success_count": s0_count,
                    "asr_difference_from_s0_pp": (success_count - s0_count) / len(group) * 100,
                    "verdict_flips_relative_to_s0": flips,
                    "any_scorer_disagreement_count": any_disagreement,
                    "any_scorer_disagreement_rate": any_disagreement / len(group),
                }
            )
    return output


def load_human_sample(population: list[dict]) -> list[dict]:
    if sha256(HUMAN_ANNOTATIONS) != EXPECTED_ANNOTATION_SHA256:
        raise ValueError("completed Pilot 2 annotation hash changed")
    _, annotations = read_csv(HUMAN_ANNOTATIONS)
    _, internal = read_csv(HUMAN_INTERNAL)
    manifest = json.loads(HUMAN_MANIFEST.read_text(encoding="utf-8"))
    if sha256(HUMAN_INTERNAL) != manifest["internal_sample_sha256"]:
        raise ValueError("Pilot 2 internal human-sample table hash changed")
    annotation_by_id = {row["sample_id"]: row for row in annotations}
    internal_by_id = {row["sample_id"]: row for row in internal}
    population_by_id = {row["sample_id"]: row for row in population}
    if len(annotations) != 100 or len(annotation_by_id) != 100:
        raise ValueError("expected 100 unique completed Pilot 2 annotations")
    if set(annotation_by_id) != set(internal_by_id) or not set(annotation_by_id) <= set(population_by_id):
        raise ValueError("human annotation/internal/population IDs do not align")
    output = []
    for sample_id, annotation in annotation_by_id.items():
        if annotation["human_label"] not in VALID_HUMAN_LABELS:
            raise ValueError(f"invalid human label for {sample_id}")
        source = internal_by_id[sample_id]
        row = population_by_id[sample_id]
        if source["victim_response"] != row["victim_response"]:
            raise ValueError(f"human/internal/raw response mismatch for {sample_id}")
        output.append(
            row
            | {
                "human_label": annotation["human_label"],
                "sampling_weight": float(source["sampling_weight"]),
                "sampling_stratum": source["sampling_stratum"],
            }
        )
    return output


def human_comparison(rows: list[dict], full_pool_successes: dict[str, int]) -> list[dict]:
    definitions = {
        "STRICT": {"FULL_COMPLIANCE"},
        "LENIENT": {"FULL_COMPLIANCE", "PARTIAL_COMPLIANCE"},
    }
    output: list[dict] = []
    ambiguous_count = sum(row["human_label"] == "AMBIGUOUS" for row in rows)
    complete = [row for row in rows if row["human_label"] != "AMBIGUOUS"]
    for definition, success_labels in definitions.items():
        truth = [row["human_label"] in success_labels for row in complete]
        for scorer_id in SCORERS:
            prediction = [row["verdicts"][scorer_id] for row in complete]
            raw_cells = confusion_counts(truth, prediction)
            raw_metrics = classification_metrics(truth, prediction) | {
                "cohens_kappa": cohens_kappa(truth, prediction)
            }
            output.append(
                {
                    "analysis_population": "raw_stratified_human_sample",
                    "human_definition": definition,
                    "scorer_id": scorer_id,
                    "sample_records": len(complete),
                    "ambiguous_excluded": ambiguous_count,
                    "estimated_population_denominator": len(complete),
                    "true_negative": raw_cells["true_negative"],
                    "false_positive": raw_cells["false_positive"],
                    "false_negative": raw_cells["false_negative"],
                    "true_positive": raw_cells["true_positive"],
                    "human_success_total": sum(truth),
                    "scorer_success_total": sum(prediction),
                    "human_asr": sum(truth) / len(truth),
                    "scorer_asr": sum(prediction) / len(prediction),
                    "known_full_pool_scorer_success_count": full_pool_successes[scorer_id],
                    "known_full_pool_scorer_asr": full_pool_successes[scorer_id] / 672,
                    **raw_metrics,
                }
            )

            weighted_cells = {
                "true_negative": sum(row["sampling_weight"] for row, y, p in zip(complete, truth, prediction, strict=True) if not y and not p),
                "false_positive": sum(row["sampling_weight"] for row, y, p in zip(complete, truth, prediction, strict=True) if not y and p),
                "false_negative": sum(row["sampling_weight"] for row, y, p in zip(complete, truth, prediction, strict=True) if y and not p),
                "true_positive": sum(row["sampling_weight"] for row, y, p in zip(complete, truth, prediction, strict=True) if y and p),
            }
            weighted_metrics = metrics_from_cells(weighted_cells)
            weighted_total = sum(weighted_cells.values())
            human_success = weighted_cells["true_positive"] + weighted_cells["false_negative"]
            scorer_success = weighted_cells["true_positive"] + weighted_cells["false_positive"]
            output.append(
                {
                    "analysis_population": "weighted_candidate_pool_estimate",
                    "human_definition": definition,
                    "scorer_id": scorer_id,
                    "sample_records": len(complete),
                    "ambiguous_excluded": ambiguous_count,
                    "estimated_population_denominator": weighted_total,
                    **weighted_cells,
                    "human_success_total": human_success,
                    "scorer_success_total": scorer_success,
                    "human_asr": human_success / weighted_total,
                    "scorer_asr": scorer_success / weighted_total,
                    "known_full_pool_scorer_success_count": full_pool_successes[scorer_id],
                    "known_full_pool_scorer_asr": full_pool_successes[scorer_id] / 672,
                    **weighted_metrics,
                }
            )
    return output


def make_figures(aggregate: list[dict], matrix: list[dict], human: list[dict], tasks: list[dict]) -> None:
    figures = OUTPUT / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    scorer_ids = list(SCORERS)

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.bar(scorer_ids, [row["asr"] for row in aggregate], color="#3f7cac")
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Attack success rate")
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.set_title("Exploratory lexical scorer sensitivity on 672 frozen outputs")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(figures / "scorer_asr.png", dpi=220)
    plt.close(fig)

    values = [[row[scorer_id] for scorer_id in scorer_ids] for row in matrix]
    fig, ax = plt.subplots(figsize=(7.0, 5.8))
    image = ax.imshow(values, cmap="Oranges", vmin=0)
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            ax.text(j, i, str(value), ha="center", va="center", color="#222222")
    ax.set_xticks(range(len(scorer_ids)), scorer_ids, rotation=35, ha="right")
    ax.set_yticks(range(len(scorer_ids)), scorer_ids)
    ax.set_title("Pairwise verdict disagreements (count)")
    fig.colorbar(image, ax=ax, label="Disagreeing examples")
    fig.tight_layout()
    fig.savefig(figures / "pairwise_disagreement_matrix.png", dpi=220)
    plt.close(fig)

    raw_human = [row for row in human if row["analysis_population"] == "raw_stratified_human_sample"]
    strict = {row["scorer_id"]: row["accuracy"] for row in raw_human if row["human_definition"] == "STRICT"}
    lenient = {row["scorer_id"]: row["accuracy"] for row in raw_human if row["human_definition"] == "LENIENT"}
    positions = list(range(len(scorer_ids)))
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.bar([x - 0.2 for x in positions], [strict[x] for x in scorer_ids], width=0.4, label="Strict")
    ax.bar([x + 0.2 for x in positions], [lenient[x] for x in scorer_ids], width=0.4, label="Lenient")
    ax.set_xticks(positions, scorer_ids, rotation=25, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Raw agreement with human labels")
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.set_title("Scorer agreement on stratified 100-record human sample")
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.tight_layout()
    fig.savefig(figures / "human_raw_agreement.png", dpi=220)
    plt.close(fig)

    task_names = sorted({row["task"] for row in tasks})
    task_lookup = {(row["task"], row["scorer_id"]): row["asr"] for row in tasks}
    task_values = [[task_lookup[(task, scorer)] for scorer in scorer_ids] for task in task_names]
    fig, ax = plt.subplots(figsize=(9.0, 6.0))
    image = ax.imshow(task_values, cmap="Blues", vmin=0, vmax=max(max(row) for row in task_values))
    ax.set_xticks(range(len(scorer_ids)), scorer_ids, rotation=35, ha="right")
    ax.set_yticks(range(len(task_names)), task_names)
    ax.set_title("Exploratory scorer ASR by legitimate task")
    fig.colorbar(image, ax=ax, label="Attack success rate")
    fig.tight_layout()
    fig.savefig(figures / "task_asr_heatmap.png", dpi=220)
    plt.close(fig)


def main() -> None:
    population = load_frozen_population()
    tables = full_pool_tables(population)
    tasks = subgroup_table(population, "task")
    targets = subgroup_table(population, "target_id")
    full_pool_successes = {
        row["scorer_id"]: row["success_count"] for row in tables["aggregate"]
    }
    humans = human_comparison(load_human_sample(population), full_pool_successes)
    scorer_ids = list(SCORERS)

    per_example = [
        {
            "sample_id": row["sample_id"],
            "task": row["task"],
            "target_id": row["target_id"],
            "target_text": row["target_text"],
            **row["verdicts"],
        }
        for row in population
    ]
    flipped = []
    for row in population:
        if len(set(row["verdicts"].values())) < 2:
            continue
        flipped.append(
            {
                "sample_id": row["sample_id"],
                "task": row["task"],
                "target_id": row["target_id"],
                "target_text": row["target_text"],
                "victim_response": row["victim_response"],
                **row["verdicts"],
                "mechanical_flip_flags": ";".join(mechanical_flip_flags(row["verdicts"])),
            }
        )

    write_csv(OUTPUT / "per_example_scorers.csv", ["sample_id", "task", "target_id", "target_text", *scorer_ids], per_example)
    write_csv(OUTPUT / "aggregate_results.csv", list(tables["aggregate"][0]), tables["aggregate"])
    write_csv(OUTPUT / "pairwise_disagreement.csv", list(tables["pairwise"][0]), tables["pairwise"])
    write_csv(OUTPUT / "pairwise_disagreement_matrix.csv", ["scorer_id", *scorer_ids], tables["matrix"])
    write_csv(OUTPUT / "flipped_examples.csv", ["sample_id", "task", "target_id", "target_text", "victim_response", *scorer_ids, "mechanical_flip_flags"], flipped)
    write_csv(OUTPUT / "task_breakdown.csv", list(tasks[0]), tasks)
    write_csv(OUTPUT / "target_breakdown.csv", list(targets[0]), targets)
    write_csv(OUTPUT / "human_comparison.csv", list(humans[0]), humans)

    metadata = {
        "status": "exploratory_post_pilot1_and_pilot2",
        "protocol_commit": "6a8359a",
        "analysis_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python_version": platform.python_version(),
        "unicode_database_version": unicodedata.unidata_version,
        "matplotlib_version": matplotlib.__version__,
        "candidate_count": len(population),
        "disagreement_example_count": len(flipped),
        "input_sha256": {
            "candidate_inputs": sha256(CANDIDATES),
            "pilot2_scored_candidates": sha256(PILOT2_SCORED),
            "completed_human_annotations": sha256(HUMAN_ANNOTATIONS),
            "human_sample_internal": sha256(HUMAN_INTERNAL),
            "raw_parts": {path.name: sha256(path) for path in sorted(RAW_DIR.glob("batch_*_part_*.jsonl"))},
        },
        "scorer_ids": scorer_ids,
        "mechanical_flip_flag_counts": dict(sorted(Counter(flag for row in flipped for flag in row["mechanical_flip_flags"].split(";")).items())),
    }
    (OUTPUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    make_figures(tables["aggregate"], tables["matrix"], humans, tasks)
    print(json.dumps({"aggregate": tables["aggregate"], "disagreement_examples": len(flipped), "flip_flags": metadata["mechanical_flip_flag_counts"]}, indent=2))


if __name__ == "__main__":
    main()
