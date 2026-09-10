#!/usr/bin/env python3
"""Sample lexical strata and create the blinded Pilot 2 annotation CSV."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path

import yaml

from src.pilot2 import BLINDED_FIELDS, validate_blinded_rows


def parse_bool(value: str) -> bool:
    if value.lower() not in {"true", "false"}:
        raise ValueError(f"invalid Boolean: {value!r}")
    return value.lower() == "true"


def main() -> None:
    config_path = Path("config/pilot2_config.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    with Path(config["paths"]["scored_candidates"]).open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["usable_response"].lower() == "true"]
    strata = {
        "KEY_E_POSITIVE": [row for row in rows if parse_bool(row["lexical_key_e_success"])],
        "KEY_E_NEGATIVE": [row for row in rows if not parse_bool(row["lexical_key_e_success"])],
    }
    requested = {
        "KEY_E_POSITIVE": config["human_sampling"]["positive_count"],
        "KEY_E_NEGATIVE": config["human_sampling"]["negative_count"],
    }
    rng = random.Random(config["random"]["human_sampling_seed"])
    internal = []
    for stratum in ["KEY_E_POSITIVE", "KEY_E_NEGATIVE"]:
        population = sorted(strata[stratum], key=lambda row: row["sample_id"])
        count = requested[stratum]
        if len(population) < count:
            raise ValueError(f"stratum {stratum} has {len(population)} records; needs {count}")
        selected = population if len(population) == count else rng.sample(population, count)
        probability = count / len(population)
        for row in selected:
            internal.append(
                row
                | {
                    "sampling_stratum": stratum,
                    "stratum_candidate_pool_size": str(len(population)),
                    "stratum_sampled_count": str(count),
                    "inclusion_probability": format(probability, ".17g"),
                    "sampling_weight": format(1 / probability, ".17g"),
                    "human_sampling_seed": str(config["random"]["human_sampling_seed"]),
                }
            )
    if len({row["sample_id"] for row in internal}) != len(internal):
        raise ValueError("duplicate IDs in internal human sample")
    internal_path = Path(config["paths"]["internal_sample"])
    internal_path.parent.mkdir(parents=True, exist_ok=True)
    if internal_path.exists():
        with internal_path.open(newline="", encoding="utf-8") as handle:
            existing_internal = list(csv.DictReader(handle))
        if existing_internal != internal:
            raise ValueError("existing internal sample differs from deterministic reconstruction")
        print(f"validated existing internal sample {internal_path}")
    else:
        with internal_path.open("x", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(internal[0]))
            writer.writeheader()
            writer.writerows(internal)

    blinded = [
        {
            "sample_id": row["sample_id"],
            "legitimate_instruction": row["legitimate_instruction"],
            "legitimate_input": row["legitimate_input"],
            "injected_instruction": row["attack_injection_text"],
            "target_behavior": row["target_behavior"],
            "victim_model_response": row["victim_response"],
            "human_label": "",
            "human_confidence": "",
            "notes": "",
        }
        for row in internal
    ]
    random.Random(config["random"]["annotation_shuffle_seed"]).shuffle(blinded)
    validate_blinded_rows(blinded, config["study"]["planned_human_sample_size"])
    blinded_path = Path(config["paths"]["blinded_annotation"])
    blinded_path.parent.mkdir(parents=True, exist_ok=True)
    if blinded_path.exists():
        with blinded_path.open(newline="", encoding="utf-8") as handle:
            existing_blinded = list(csv.DictReader(handle))
        if existing_blinded != blinded:
            raise ValueError("existing blinded file differs from deterministic reconstruction")
        print(f"validated existing blinded annotation {blinded_path}")
    else:
        with blinded_path.open("x", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=BLINDED_FIELDS)
            writer.writeheader()
            writer.writerows(blinded)

    manifest_path = Path("data/derived/pilot2/human_sample_manifest.json")
    manifest = {
        "human_sampling_seed": config["random"]["human_sampling_seed"],
        "annotation_shuffle_seed": config["random"]["annotation_shuffle_seed"],
        "planned_sample_size": len(internal),
        "strata": {
            stratum: {
                "usable_candidate_pool_size": len(strata[stratum]),
                "sampled_count": requested[stratum],
                "inclusion_probability": requested[stratum] / len(strata[stratum]),
                "sampling_weight": len(strata[stratum]) / requested[stratum],
            }
            for stratum in ["KEY_E_POSITIVE", "KEY_E_NEGATIVE"]
        },
        "internal_sample_sha256": hashlib.sha256(internal_path.read_bytes()).hexdigest(),
        "blinded_annotation_sha256": hashlib.sha256(blinded_path.read_bytes()).hexdigest(),
        "candidate_summary_sha256": hashlib.sha256(
            Path(config["paths"]["candidate_summary"]).read_bytes()
        ).hexdigest(),
    }
    rendered = json.dumps(manifest, indent=2) + "\n"
    if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") != rendered:
        raise ValueError("existing human-sample manifest differs")
    if not manifest_path.exists():
        manifest_path.write_text(rendered, encoding="utf-8")
    print(f"created {len(blinded)} blinded Pilot 2 records at {blinded_path}")


if __name__ == "__main__":
    main()
