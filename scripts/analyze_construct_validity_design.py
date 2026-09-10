#!/usr/bin/env python3
"""Extract exploratory planning inputs and simulate construct-validity power.

This is a design-only analysis. It reads frozen Pilot 2 artifacts and never
generates victim-model output or changes human annotations.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
POPULATION = ROOT / "data/derived/pilot2/scored_candidates.csv"
SCORERS = ROOT / "results/scorer_sensitivity/per_example_scorers.csv"
ANNOTATIONS = ROOT / "annotations/pilot2_annotation_blinded.csv"
HUMAN_INTERNAL = ROOT / "data/derived/pilot2/human_sample_internal.csv"
OUTPUT = ROOT / "results/design_power"
EXPECTED_ANNOTATION_SHA256 = (
    "5f6619cc5af82a30d9cf9bf32bcb90d68f9d0668b0b1e44d2cffb5c872a24b18"
)
SEED = 20260821
REPLICATES = 1000
Z_975 = 1.959963984540054
GENERATIVE = {"grammar_correction", "summarization"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("cannot write an empty table")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_bool(value: str) -> bool:
    if value not in {"True", "False"}:
        raise ValueError(f"invalid Boolean: {value!r}")
    return value == "True"


def correctness_table(rows: list[dict], success_labels: set[str]) -> dict[str, int]:
    table = {"both_incorrect": 0, "s0_only_correct": 0, "s2_only_correct": 0, "both_correct": 0}
    for row in rows:
        truth = row["human_label"] in success_labels
        c0 = row["s0"] == truth
        c2 = row["s2"] == truth
        key = {
            (False, False): "both_incorrect",
            (True, False): "s0_only_correct",
            (False, True): "s2_only_correct",
            (True, True): "both_correct",
        }[(c0, c2)]
        table[key] += 1
    return table


def paired_difference(table: dict[str, int]) -> float:
    return (table["s2_only_correct"] - table["s0_only_correct"]) / sum(table.values())


def distributions(rows: list[dict], fields: list[str]) -> dict:
    return {
        field: dict(sorted(Counter(row[field] for row in rows).items()))
        for field in fields
    }


def extract_parameters() -> dict:
    if sha256(ANNOTATIONS) != EXPECTED_ANNOTATION_SHA256:
        raise ValueError("frozen Pilot 2 human annotation hash changed")
    population = read_csv(POPULATION)
    scorer_rows = read_csv(SCORERS)
    annotations = read_csv(ANNOTATIONS)
    internal = read_csv(HUMAN_INTERNAL)
    if len(population) != 672 or len(scorer_rows) != 672 or len(annotations) != 100:
        raise ValueError("unexpected frozen Pilot 2 row count")

    pop_by_id = {row["sample_id"]: row for row in population}
    score_by_id = {row["sample_id"]: row for row in scorer_rows}
    ann_by_id = {row["sample_id"]: row for row in annotations}
    int_by_id = {row["sample_id"]: row for row in internal}
    if len(pop_by_id) != 672 or set(pop_by_id) != set(score_by_id):
        raise ValueError("population/scorer mappings differ")
    if len(ann_by_id) != 100 or set(ann_by_id) != set(int_by_id):
        raise ValueError("annotation/internal mappings differ")

    joined_population = []
    for sample_id, row in pop_by_id.items():
        score = score_by_id[sample_id]
        joined_population.append(
            row
            | {
                "s0": parse_bool(score["S0_ORIGINAL"]),
                "s2": parse_bool(score["S2_PREFIX_STRICT"]),
                "task_category": "generative" if row["task"] in GENERATIVE else "classification",
            }
        )
    joined_human = []
    for sample_id, annotation in ann_by_id.items():
        source = int_by_id[sample_id]
        row = next(item for item in joined_population if item["sample_id"] == sample_id)
        joined_human.append(
            row
            | {
                "human_label": annotation["human_label"],
                "sampling_weight": float(source["sampling_weight"]),
            }
        )

    ambiguous = [row for row in joined_human if row["human_label"] == "AMBIGUOUS"]
    if ambiguous:
        raise ValueError("exploratory planning extraction expected no AMBIGUOUS labels")

    strict_labels = {"FULL_COMPLIANCE"}
    lenient_labels = {"FULL_COMPLIANCE", "PARTIAL_COMPLIANCE"}
    strict_table = correctness_table(joined_human, strict_labels)
    lenient_table = correctness_table(joined_human, lenient_labels)
    d_strict_raw = paired_difference(strict_table)
    d_lenient_raw = paired_difference(lenient_table)

    def original_ipw_difference(success_labels: set[str]) -> float:
        numerator = 0.0
        denominator = 0.0
        for row in joined_human:
            truth = row["human_label"] in success_labels
            numerator += row["sampling_weight"] * (int(row["s2"] == truth) - int(row["s0"] == truth))
            denominator += row["sampling_weight"]
        return numerator / denominator

    full_discord = [row for row in joined_population if row["s0"] != row["s2"]]
    human_discord = [row for row in joined_human if row["s0"] != row["s2"]]
    if not human_discord:
        raise ValueError("no human-labelled S0/S2 disagreements")

    def calibrated_difference(success_labels: set[str], category: str | None = None) -> float:
        pop = joined_population if category is None else [r for r in joined_population if r["task_category"] == category]
        pop_discord = [r for r in pop if r["s0"] != r["s2"]]
        human = joined_human if category is None else [r for r in joined_human if r["task_category"] == category]
        human_d = [r for r in human if r["s0"] != r["s2"]]
        if not pop_discord:
            return 0.0
        if not human_d:
            raise ValueError(f"no labelled disagreement in category {category}")
        mean_contribution = np.mean(
            [
                int(r["s2"] == (r["human_label"] in success_labels))
                - int(r["s0"] == (r["human_label"] in success_labels))
                for r in human_d
            ]
        )
        return len(pop_discord) / len(pop) * float(mean_contribution)

    category_estimates = {}
    for category in ("generative", "classification"):
        human_group = [r for r in joined_human if r["task_category"] == category]
        strict_group = correctness_table(human_group, strict_labels)
        lenient_group = correctness_table(human_group, lenient_labels)
        category_estimates[category] = {
            "candidate_n": sum(r["task_category"] == category for r in joined_population),
            "human_n": len(human_group),
            "candidate_discordances": sum(
                r["task_category"] == category and r["s0"] != r["s2"]
                for r in joined_population
            ),
            "strict_correctness_table": strict_group,
            "lenient_correctness_table": lenient_group,
            "d_strict_raw": paired_difference(strict_group),
            "d_lenient_raw": paired_difference(lenient_group),
            "interaction_definition_raw": paired_difference(strict_group) - paired_difference(lenient_group),
            "d_strict_joint_cell_calibrated": calibrated_difference(strict_labels, category),
            "d_lenient_joint_cell_calibrated": calibrated_difference(lenient_labels, category),
        }

    prompt_hashes = [row["prompt_sha256"] for row in joined_population]
    if len(set(prompt_hashes)) != len(prompt_hashes):
        raise ValueError("Pilot 2 unexpectedly repeats a base prompt hash")

    d_strict_cal = calibrated_difference(strict_labels)
    d_lenient_cal = calibrated_difference(lenient_labels)
    return {
        "status": "design_only_exploratory_inputs_not_confirmatory_truth",
        "input_hashes": {
            "population": sha256(POPULATION),
            "scorers": sha256(SCORERS),
            "annotations": sha256(ANNOTATIONS),
            "human_internal": sha256(HUMAN_INTERNAL),
        },
        "candidate_responses": len(joined_population),
        "independent_base_attack_prompts": len(set(prompt_hashes)),
        "responses_per_base_prompt": {"minimum": 1, "maximum": 1, "mean": 1.0},
        "victim_models": sorted({row["model_repository"] for row in joined_population}),
        "s0_s2_discordance": {
            "count": len(full_discord),
            "denominator": len(joined_population),
            "frequency": len(full_discord) / len(joined_population),
        },
        "human_sample": {
            "n": len(joined_human),
            "strict_correctness_table": strict_table,
            "lenient_correctness_table": lenient_table,
            "d_strict_raw": d_strict_raw,
            "d_lenient_raw": d_lenient_raw,
            "interaction_definition_raw": d_strict_raw - d_lenient_raw,
            "d_strict_original_ipw": original_ipw_difference(strict_labels),
            "d_lenient_original_ipw": original_ipw_difference(lenient_labels),
            "interaction_definition_original_ipw": original_ipw_difference(strict_labels)
            - original_ipw_difference(lenient_labels),
            "d_strict_joint_cell_calibrated": d_strict_cal,
            "d_lenient_joint_cell_calibrated": d_lenient_cal,
            "interaction_definition_joint_cell_calibrated": d_strict_cal - d_lenient_cal,
        },
        "task_category_estimates": category_estimates,
        "h3_interaction_strict_raw": category_estimates["generative"]["d_strict_raw"]
        - category_estimates["classification"]["d_strict_raw"],
        "h3_interaction_strict_joint_cell_calibrated": category_estimates["generative"][
            "d_strict_joint_cell_calibrated"
        ]
        - category_estimates["classification"]["d_strict_joint_cell_calibrated"],
        "candidate_distribution": distributions(
            joined_population, ["task", "injection_variant_id", "target_id"]
        ),
        "human_distribution": distributions(
            joined_human, ["task", "injection_variant_id", "target_id"]
        ),
        "within_prompt_clustering": {
            "estimable": False,
            "reason": "Pilot 2 has one victim response per unique base-prompt hash, so no within-prompt replication exists.",
        },
    }


def beta_cluster_probabilities(rng: np.random.Generator, n: int, q: float, icc: float) -> np.ndarray:
    if icc == 0:
        return np.full(n, q)
    concentration = 1.0 / icc - 1.0
    return rng.beta(q * concentration, (1.0 - q) * concentration, size=n)


def sampled_cluster_totals(
    rng: np.random.Generator,
    contributions: np.ndarray,
    discordant: np.ndarray,
    human_n: int,
    disagreement_fraction: float = 0.60,
) -> np.ndarray:
    flat_discord = np.flatnonzero(discordant.ravel())
    cap = min(len(flat_discord), math.floor(disagreement_fraction * human_n))
    observed = np.zeros(contributions.size, dtype=float)
    if cap == 0:
        return observed.reshape(contributions.shape).sum(axis=1)
    if cap == len(flat_discord):
        chosen = flat_discord
        weight = 1.0
    else:
        chosen = rng.choice(flat_discord, size=cap, replace=False)
        weight = len(flat_discord) / cap
    observed[chosen] = contributions.ravel()[chosen] * weight
    return observed.reshape(contributions.shape).sum(axis=1)


def cluster_mean_and_se(cluster_totals: np.ndarray) -> tuple[float, float]:
    estimate = float(np.mean(cluster_totals) / 3.0)
    se = float(np.std(cluster_totals, ddof=1) / math.sqrt(len(cluster_totals)) / 3.0)
    return estimate, se


def simulate_power(
    *,
    hypothesis: str,
    effect: float,
    base_prompts: int,
    human_n: int,
    discordance_rate: float,
    icc: float,
    replicates: int,
    seed: int,
    disagreement_fraction: float = 0.60,
) -> dict:
    rng = np.random.default_rng(seed)
    reject = 0
    estimates = []
    for _ in range(replicates):
        if hypothesis == "H3":
            n_gen = round(base_prompts * 2 / 7)
            n_class = base_prompts - n_gen
            all_totals = []
            for n_group, d_group in ((n_gen, 0.01 + effect), (n_class, 0.01)):
                probs = beta_cluster_probabilities(rng, n_group, discordance_rate, icc)
                discord = rng.random((n_group, 3)) < probs[:, None]
                p_plus = (1.0 + d_group / discordance_rate) / 2.0
                signs = np.where(rng.random((n_group, 3)) < p_plus, 1.0, -1.0)
                all_totals.append((discord * signs, discord))
            combined_contrib = np.concatenate([item[0] for item in all_totals])
            combined_discord = np.concatenate([item[1] for item in all_totals])
            sampled = sampled_cluster_totals(
                rng, combined_contrib, combined_discord, human_n, disagreement_fraction
            )
            gen_totals = sampled[:n_gen]
            class_totals = sampled[n_gen:]
            d_gen, se_gen = cluster_mean_and_se(gen_totals)
            d_class, se_class = cluster_mean_and_se(class_totals)
            estimate = d_gen - d_class
            se = math.sqrt(se_gen**2 + se_class**2)
        else:
            probs = beta_cluster_probabilities(rng, base_prompts, discordance_rate, icc)
            discord = rng.random((base_prompts, 3)) < probs[:, None]
            if hypothesis == "H1":
                p_plus = (1.0 + effect / discordance_rate) / 2.0
                contributions = discord * np.where(
                    rng.random((base_prompts, 3)) < p_plus, 1.0, -1.0
                )
            elif hypothesis == "H2":
                p_partial = effect / (2.0 * discordance_rate)
                contributions = discord * 2.0 * (
                    rng.random((base_prompts, 3)) < p_partial
                )
            else:
                raise ValueError(hypothesis)
            totals = sampled_cluster_totals(
                rng, contributions, discord, human_n, disagreement_fraction
            )
            estimate, se = cluster_mean_and_se(totals)
        estimates.append(estimate)
        reject += se > 0 and estimate - Z_975 * se > 0
    power = reject / replicates
    return {
        "hypothesis": hypothesis,
        "effect_pp": effect * 100,
        "base_prompts": base_prompts,
        "total_responses": base_prompts * 3,
        "human_double_annotated_responses": human_n,
        "discordance_rate": discordance_rate,
        "within_prompt_icc": icc,
        "maximum_disagreement_fraction": disagreement_fraction,
        "replicates": replicates,
        "mean_estimate_pp": float(np.mean(estimates) * 100),
        "power_95pct_cluster_interval_excludes_zero": power,
        "monte_carlo_se": math.sqrt(power * (1.0 - power) / replicates),
    }


def run_power_grid() -> list[dict]:
    base_counts = [420, 840, 1260, 1680]
    human_counts = [400, 600, 800, 1000]
    effects = {
        "H1": [0.01, 0.02, 0.035, 0.05, 0.07],
        "H2": [0.01, 0.02, 0.035, 0.05],
        "H3": [0.02, 0.035, 0.05, 0.07],
    }
    rows = []
    scenario = 0
    for hypothesis, hypothesis_effects in effects.items():
        for effect in hypothesis_effects:
            for base_prompts in base_counts:
                for human_n in human_counts:
                    scenario += 1
                    rows.append(
                        simulate_power(
                            hypothesis=hypothesis,
                            effect=effect,
                            base_prompts=base_prompts,
                            human_n=human_n,
                            discordance_rate=0.10,
                            icc=0.25,
                            replicates=REPLICATES,
                            seed=SEED + scenario,
                        )
                    )
    return rows


def run_assumption_sensitivity() -> list[dict]:
    """Vary unidentifiable discordance and within-prompt clustering assumptions."""
    design_effects = {"H1": 0.02, "H2": 0.02, "H3": 0.035}
    rows = []
    scenario = 10_000
    for hypothesis, effect in design_effects.items():
        discordance_rates = [0.03, 0.06, 0.10] if hypothesis != "H3" else [0.06, 0.10]
        for discordance_rate in discordance_rates:
            for icc in [0.0, 0.10, 0.25, 0.40]:
                scenario += 1
                rows.append(
                    simulate_power(
                        hypothesis=hypothesis,
                        effect=effect,
                        base_prompts=1680,
                        human_n=800,
                        discordance_rate=discordance_rate,
                        icc=icc,
                        replicates=REPLICATES,
                        seed=SEED + scenario,
                    )
                )
    return rows


def run_human_sample_decision_grid() -> list[dict]:
    """Power at the proposed 5,040-response pool for decision-relevant budgets."""
    human_counts = [300, 400, 500, 600, 800]
    effects = {
        "H1": [0.01, 0.015, 0.02, 0.035, 0.05, 0.07],
        "H3": [0.02, 0.025, 0.03, 0.035],
    }
    rows = []
    scenario = 20_000
    for hypothesis, hypothesis_effects in effects.items():
        for effect in hypothesis_effects:
            for human_n in human_counts:
                scenario += 1
                rows.append(
                    simulate_power(
                        hypothesis=hypothesis,
                        effect=effect,
                        base_prompts=1680,
                        human_n=human_n,
                        discordance_rate=0.10,
                        icc=0.25,
                        replicates=REPLICATES,
                        seed=SEED + scenario,
                        disagreement_fraction=0.60,
                    )
                )
    return rows


def run_allocation_audit() -> list[dict]:
    """Compare disagreement caps while retaining agreement-cell controls."""
    rows = []
    scenario = 30_000
    expected_discordances = round(1680 * 3 * 0.10)
    for human_n in [300, 400, 500, 600, 800]:
        for fraction in [0.40, 0.50, 0.60, 0.70, 0.80]:
            cap = math.floor(human_n * fraction)
            sampled_discordances = min(expected_discordances, cap)
            base = {
                "human_double_annotated_responses": human_n,
                "maximum_disagreement_fraction": fraction,
                "maximum_disagreement_count": cap,
                "expected_disagreement_pool_at_10pct": expected_discordances,
                "expected_sampled_disagreements": sampled_discordances,
                "expected_agreement_controls": human_n - sampled_discordances,
            }
            for hypothesis, effect in [("H1", 0.02), ("H3", 0.03), ("H3", 0.035)]:
                scenario += 1
                result = simulate_power(
                    hypothesis=hypothesis,
                    effect=effect,
                    base_prompts=1680,
                    human_n=human_n,
                    discordance_rate=0.10,
                    icc=0.25,
                    replicates=REPLICATES,
                    seed=SEED + scenario,
                    disagreement_fraction=fraction,
                )
                rows.append(base | result)
    return rows


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    parameters = extract_parameters()
    (OUTPUT / "exploratory_parameters.json").write_text(
        json.dumps(parameters, indent=2) + "\n", encoding="utf-8"
    )
    power = run_power_grid()
    historical_fields = lambda rows: [
        {key: value for key, value in row.items() if key != "maximum_disagreement_fraction"}
        for row in rows
    ]
    write_csv(OUTPUT / "power_grid.csv", historical_fields(power))
    write_csv(
        OUTPUT / "power_assumption_sensitivity.csv",
        historical_fields(run_assumption_sensitivity()),
    )
    write_csv(OUTPUT / "human_sample_decision_power.csv", run_human_sample_decision_grid())
    write_csv(OUTPUT / "sampling_allocation_audit.csv", run_allocation_audit())
    metadata = {
        "status": "design_only_simulation_not_empirical_confirmatory_result",
        "seed": SEED,
        "replicates_per_scenario": REPLICATES,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "models_per_base_prompt": 3,
        "primary_interval_target": "95% base-prompt cluster-bootstrap CI",
        "power_approximation": "Monte Carlo with inverse-probability weighted cluster totals and cluster-normal 95% interval exclusion; final analysis uses percentile cluster bootstrap.",
        "central_assumptions": {
            "s0_s2_discordance_rate": 0.10,
            "within_base_prompt_icc": 0.25,
            "maximum_disagreement_allocation_fraction_of_human_sample": 0.60,
            "generative_base_prompt_fraction": 2 / 7,
            "classification_base_prompt_fraction": 5 / 7,
            "h3_classification_scorer_advantage": 0.01,
        },
        "decision_grid": {
            "base_prompts": 1680,
            "total_responses": 5040,
            "human_sample_sizes": [300, 400, 500, 600, 800],
            "h1_effects": [0.01, 0.015, 0.02, 0.035, 0.05, 0.07],
            "h3_interactions": [0.02, 0.025, 0.03, 0.035],
            "disagreement_allocation_fractions_audited": [0.40, 0.50, 0.60, 0.70, 0.80],
            "retained_fraction": 0.60,
        },
        "caveat": "Pilot 2 cannot estimate within-prompt ICC because it has one response per prompt; assumed values must be sensitivity-tested before preregistration.",
    }
    (OUTPUT / "simulation_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
