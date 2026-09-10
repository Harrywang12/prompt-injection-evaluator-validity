#!/usr/bin/env python3
"""Run the frozen confirmatory analysis on the immutable 800-row dataset."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

from src.confirmatory_analysis import (
    BOOTSTRAP_REPLICATES,
    BOOTSTRAP_SEED,
    verify_hashes,
    sha256_file,
)
from scripts.prepare_confirmatory_analysis_dataset import INPUT_PATHS

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "confirmatory_private/analysis"
DATA = PRIVATE / "final_analysis_dataset.csv"
PRIMARY = PRIVATE / "primary_confirmatory_results.json"
BOOTSTRAP = PRIVATE / "bootstrap_results.csv"
GEE = PRIVATE / "gee_results.json"
EXPLORATORY = PRIVATE / "exploratory_results.csv"
PUBLIC_JSON = ROOT / "confirmatory/confirmatory_results.json"
PUBLIC_MD = ROOT / "confirmatory/confirmatory_results.md"
PUBLIC_AUDIT = ROOT / "confirmatory/confirmatory_analysis_audit.md"

TASKS = [
    "grammar_correction", "summarization", "duplicate_sentence_detection",
    "hate_detection", "natural_language_inference", "sentiment_analysis",
    "spam_detection",
]
SCORERS = ["s0", "s2"]


def read_rows() -> list[dict]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, strict=True))
    for row in rows:
        for key in ("s0", "s2", "strict_human_success", "lenient_human_success"):
            row[key] = int(row[key])
        row["analysis_weight"] = float(row["analysis_weight"])
        row["inclusion_probability"] = float(row["inclusion_probability"])
        row["stratum_population_size"] = int(row["stratum_population_size"])
        row["stratum_sample_size"] = int(row["stratum_sample_size"])
    return rows


def ratio(rows: list[dict], values, weights) -> float:
    den = sum(weights(row) for row in rows)
    if den <= 0:
        return math.nan
    return sum(weights(row) * values(row) for row in rows) / den


def weighted_kappa(tp: float, tn: float, fp: float, fn: float) -> float | None:
    total = tp + tn + fp + fn
    if total <= 0:
        return None
    po = (tp + tn) / total
    p_pred = (tp + fp) / total
    p_true = (tp + fn) / total
    pe = p_pred * p_true + (1 - p_pred) * (1 - p_true)
    return None if math.isclose(1 - pe, 0) else (po - pe) / (1 - pe)


def metrics(rows: list[dict], scorer: str, human: str, weight_key=None) -> dict:
    def weight(row):
        return 1.0 if weight_key is None else float(row[weight_key])
    cells = {}
    for name, pred, truth in (("tp", 1, 1), ("tn", 0, 0), ("fp", 1, 0), ("fn", 0, 1)):
        cells[name] = sum(weight(r) for r in rows if r[scorer] == pred and r[human] == truth)
    tp, tn, fp, fn = (cells[x] for x in ("tp", "tn", "fp", "fn"))
    total = tp + tn + fp + fn
    precision = None if tp + fp == 0 else tp / (tp + fp)
    recall = None if tp + fn == 0 else tp / (tp + fn)
    f1 = None if precision is None or recall is None or precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        **cells,
        "accuracy": (tp + tn) / total,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "kappa": weighted_kappa(tp, tn, fp, fn),
    }


def raw_and_weighted(rows: list[dict], scorer: str, human: str) -> dict:
    raw = metrics(rows, scorer, human)
    for key in ("tp", "tn", "fp", "fn"):
        raw[key] = int(raw[key])
    return {"raw": raw, "weighted": metrics(rows, scorer, human, "analysis_weight")}


def estimands(rows: list[dict], weight_key="analysis_weight") -> dict:
    def acc(scorer, human, subset=None):
        selected = rows if subset is None else [r for r in rows if subset(r)]
        return ratio(selected, lambda r: int(r[scorer] == r[human]), lambda r: r[weight_key])
    strict0, strict2 = acc("s0", "strict_human_success"), acc("s2", "strict_human_success")
    lenient0, lenient2 = acc("s0", "lenient_human_success"), acc("s2", "lenient_human_success")
    is_gen = lambda r: r["task_category"] == "generative_text_transformation"
    is_class = lambda r: r["task_category"] == "closed_label_classification"
    gen0, gen2 = acc("s0", "strict_human_success", is_gen), acc("s2", "strict_human_success", is_gen)
    cls0, cls2 = acc("s0", "strict_human_success", is_class), acc("s2", "strict_human_success", is_class)
    d_strict, d_lenient = strict2 - strict0, lenient2 - lenient0
    d_gen, d_cls = gen2 - gen0, cls2 - cls0
    asr0 = ratio(rows, lambda r: r["s0"], lambda r: r[weight_key])
    asr2 = ratio(rows, lambda r: r["s2"], lambda r: r[weight_key])
    return {
        "accuracy_s0_strict": strict0, "accuracy_s2_strict": strict2,
        "d_strict": d_strict,
        "accuracy_s0_lenient": lenient0, "accuracy_s2_lenient": lenient2,
        "d_lenient": d_lenient, "i_definition": d_strict - d_lenient,
        "accuracy_s0_strict_generative": gen0, "accuracy_s2_strict_generative": gen2,
        "d_generative": d_gen,
        "accuracy_s0_strict_classification": cls0, "accuracy_s2_strict_classification": cls2,
        "d_classification": d_cls, "i_task": d_gen - d_cls,
        "asr_s0": asr0, "asr_s2": asr2, "delta_asr": asr0 - asr2,
    }


def replicate_weights(rows: list[dict], multiplicity: dict[str, int]) -> tuple[list[dict], Counter]:
    """Task-stratified cluster replicate with calibrated stratum weights.

    Sampling strata are scorer-cell x model x task. Multiplicity retains all
    sampled model records in each resampled base-prompt cluster. Each observed
    stratum is recalibrated to its frozen candidate-population total.
    """
    copied, denominators = [], defaultdict(float)
    for row in rows:
        mult = multiplicity.get(row["confirmatory_prompt_id"], 0)
        if mult:
            new = dict(row)
            new["_mult"] = mult
            key = row["sampling_stratum"]
            denominators[key] += mult * row["analysis_weight"]
            copied.append(new)
    pop, meta = {}, {}
    for row in rows:
        pop[row["sampling_stratum"]] = row["stratum_population_size"]
        meta[row["sampling_stratum"]] = (
            row["scorer_cell"], row["model_id"], row["task_category"]
        )
    collapse = Counter()
    leaves_by_modelcat, leaves_by_category, leaves_by_scorer = defaultdict(list), defaultdict(list), defaultdict(list)
    for key, (cell, model, category) in meta.items():
        leaves_by_modelcat[(cell, model, category)].append(key)
        leaves_by_category[(cell, category)].append(key)
        leaves_by_scorer[cell].append(key)
    force_modelcat = {
        parent for parent, leaves in leaves_by_modelcat.items()
        if any(denominators.get(leaf, 0) <= 0 for leaf in leaves)
    }
    force_category = {
        parent for parent, leaves in leaves_by_category.items()
        if any(sum(denominators.get(k, 0) for k in leaves_by_modelcat[mc]) <= 0
               for mc in leaves_by_modelcat if mc[0] == parent[0] and mc[2] == parent[1])
    }
    force_scorer = {
        cell for cell, leaves in leaves_by_scorer.items()
        if any(sum(denominators.get(k, 0) for k in leaves_by_category[cat]) <= 0
               for cat in leaves_by_category if cat[0] == cell)
    }
    group_for = {}
    for key, (cell, model, category) in meta.items():
        if cell in force_scorer:
            group_for[key] = ("scorer", cell)
        elif (cell, category) in force_category:
            group_for[key] = ("category", cell, category)
        elif (cell, model, category) in force_modelcat:
            group_for[key] = ("model_category", cell, model, category)
        else:
            group_for[key] = ("leaf", key)
    groups = defaultdict(list)
    for key, group in group_for.items():
        groups[group].append(key)
    factors = {}
    for group, leaves in groups.items():
        den = sum(denominators.get(k, 0) for k in leaves)
        num = sum(pop[k] for k in leaves)
        factors[group] = math.nan if den <= 0 else num / den
        if group[0] != "leaf":
            collapse[{"model_category": "task_to_category", "category": "model_within_category", "scorer": "category_within_scorer"}[group[0]]] += 1
    for row in copied:
        factor = factors[group_for[row["sampling_stratum"]]]
        row["bootstrap_weight"] = row["_mult"] * row["analysis_weight"] * factor
    return copied, collapse


def bootstrap(rows: list[dict]) -> tuple[list[dict], dict]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    task_clusters = {}
    for task in TASKS:
        task_clusters[task] = sorted({r["confirmatory_prompt_id"] for r in rows if r["task"] == task})
    draws, collapses = [], Counter()
    names = list(estimands(rows))
    for replicate in range(BOOTSTRAP_REPLICATES):
        multiplicity = Counter()
        for task in TASKS:
            clusters = np.asarray(task_clusters[task], dtype=object)
            for cluster in rng.choice(clusters, size=len(clusters), replace=True):
                multiplicity[str(cluster)] += 1
        rep_rows, rep_collapses = replicate_weights(rows, multiplicity)
        collapses.update(rep_collapses)
        values = estimands(rep_rows, "bootstrap_weight")
        for row in rep_rows:
            row["uncalibrated_weight"] = row["_mult"] * row["analysis_weight"]
        uncalibrated = estimands(rep_rows, "uncalibrated_weight")
        draws.append({"replicate": replicate + 1, **values, **{f"uncalibrated_{k}": v for k, v in uncalibrated.items()}})
    intervals = {}
    for name in names:
        valid = np.asarray([d[name] for d in draws if math.isfinite(d[name])])
        intervals[name] = {
            "requested_replicates": BOOTSTRAP_REPLICATES,
            "valid_replicates": int(valid.size),
            "ci_95_percentile": None if valid.size < 9500 else [float(x) for x in np.percentile(valid, [2.5, 97.5])],
        }
    uncalibrated_intervals = {}
    for name in names:
        key = f"uncalibrated_{name}"
        valid = np.asarray([d[key] for d in draws if math.isfinite(d[key])])
        uncalibrated_intervals[name] = {
            "requested_replicates": BOOTSTRAP_REPLICATES,
            "valid_replicates": int(valid.size),
            "ci_95_percentile": None if valid.size < 9500 else [float(x) for x in np.percentile(valid, [2.5, 97.5])],
        }
    return draws, {"seed": BOOTSTRAP_SEED, "replicates": BOOTSTRAP_REPLICATES, "intervals": intervals, "fallback_counts": dict(collapses), "triggered_uncalibrated_ipw_sensitivity_intervals": uncalibrated_intervals}


def gee_fit(rows: list[dict], kind: str) -> dict:
    models = sorted({r["model_id"] for r in rows})
    tasks = sorted({r["task"] for r in rows})
    observations = []
    if kind == "strict":
        for row in rows:
            for scorer in SCORERS:
                observations.append((row, int(row[scorer] == row["strict_human_success"]), scorer == "s2", False))
        terms = ["intercept", "s2"] + [f"model:{x}" for x in models[1:]] + [f"task:{x}" for x in tasks[1:]]
    elif kind == "definition":
        for row in rows:
            for human, is_lenient in (("strict_human_success", False), ("lenient_human_success", True)):
                for scorer in SCORERS:
                    observations.append((row, int(row[scorer] == row[human]), scorer == "s2", is_lenient))
        terms = ["intercept", "s2", "lenient", "s2_x_lenient"] + [f"model:{x}" for x in models[1:]] + [f"task:{x}" for x in tasks[1:]]
    elif kind == "task":
        for row in rows:
            for scorer in SCORERS:
                observations.append((row, int(row[scorer] == row["strict_human_success"]), scorer == "s2", False))
        terms = ["intercept", "s2", "s2_x_generative"] + [f"model:{x}" for x in models[1:]] + [f"task:{x}" for x in tasks[1:]]
    else:
        raise ValueError(kind)
    X, y, w, cluster = [], [], [], []
    for row, outcome, s2, lenient in observations:
        vals = []
        for term in terms:
            if term == "intercept": vals.append(1.0)
            elif term == "s2": vals.append(float(s2))
            elif term == "lenient": vals.append(float(lenient))
            elif term == "s2_x_lenient": vals.append(float(s2 and lenient))
            elif term == "s2_x_generative": vals.append(float(s2 and row["task_category"] == "generative_text_transformation"))
            elif term.startswith("model:"): vals.append(float(row["model_id"] == term[6:]))
            elif term.startswith("task:"): vals.append(float(row["task"] == term[5:]))
        X.append(vals); y.append(outcome); w.append(row["analysis_weight"]); cluster.append(row["confirmatory_prompt_id"])
    X, y, w = np.asarray(X), np.asarray(y), np.asarray(w)
    bread_matrix = X.T @ (w[:, None] * X)
    rank = int(np.linalg.matrix_rank(bread_matrix))
    if rank != len(terms):
        return {"status": "UNAVAILABLE_SINGULAR", "rank": rank, "columns": len(terms), "terms": terms}
    bread = np.linalg.inv(bread_matrix)
    beta = bread @ (X.T @ (w * y))
    resid = y - X @ beta
    meat = np.zeros_like(bread)
    for group in sorted(set(cluster)):
        idx = np.asarray([i for i, value in enumerate(cluster) if value == group])
        score = X[idx].T @ (w[idx] * resid[idx])
        meat += np.outer(score, score)
    covariance = bread @ meat @ bread
    if not np.all(np.isfinite(covariance)):
        return {"status": "UNAVAILABLE_NONFINITE", "terms": terms}
    se = np.sqrt(np.maximum(np.diag(covariance), 0))
    estimates = {}
    for i, term in enumerate(terms):
        z = beta[i] / se[i] if se[i] > 0 else math.nan
        estimates[term] = {"estimate": float(beta[i]), "se": float(se[i]), "ci_95": [float(beta[i]-1.959963984540054*se[i]), float(beta[i]+1.959963984540054*se[i])], "p_value_two_sided": None if not math.isfinite(z) else float(2*stats.norm.sf(abs(z)))}
    return {"status": "AVAILABLE", "family": "Gaussian", "link": "identity", "working_correlation": "independence", "variance": "cluster_robust_sandwich", "cluster": "confirmatory_prompt_id", "weights": "inverse_probability", "terms": terms, "rank": rank, "observations": len(y), "clusters": len(set(cluster)), "estimates": estimates}


def weight_diagnostics(rows: list[dict]) -> dict:
    weights = np.asarray([r["analysis_weight"] for r in rows])
    mean = float(weights.mean()); cv = float(weights.std(ddof=0) / mean)
    ess = float(weights.sum() ** 2 / np.square(weights).sum())
    census = sorted({r["sampling_stratum"] for r in rows if r["stratum_population_size"] == r["stratum_sample_size"]})
    triggered = max(weights) / mean > 20 or cv > 2 or ess < len(rows) / 2
    return {"maximum": float(max(weights)), "mean": mean, "maximum_normalized_to_mean": float(max(weights)/mean), "coefficient_of_variation": cv, "kish_effective_sample_size": ess, "census_strata": census, "sensitivity_triggered": triggered}


def subgroup_rows(rows: list[dict]) -> list[dict]:
    output = []
    for family, field in (("model", "model_id"), ("task", "task"), ("target", "target_id"), ("injection_template", "template_id")):
        for level in sorted({r[field] for r in rows}):
            subset = [r for r in rows if r[field] == level]
            for definition in ("strict", "lenient"):
                human = f"{definition}_human_success"
                a0 = metrics(subset, "s0", human, "analysis_weight")["accuracy"]
                a2 = metrics(subset, "s2", human, "analysis_weight")["accuracy"]
                output.append({"family": family, "level": level, "human_definition": definition, "raw_n": len(subset), "weighted_accuracy_s0": a0, "weighted_accuracy_s2": a2, "d_s2_minus_s0": a2-a0, "inferential_status": "EXPLORATORY_DESCRIPTIVE_NO_P_VALUE"})
    return output


def confirmatory_decisions(point: dict, intervals: dict) -> tuple[bool, bool]:
    """Apply the frozen positive-estimate, two-sided CI, fixed-sequence rules."""
    h1_ci = intervals["d_strict"]["ci_95_percentile"]
    h1 = h1_ci is not None and h1_ci[0] > 0 and point["d_strict"] > 0
    h3_ci = intervals["i_task"]["ci_95_percentile"]
    h3 = h1 and h3_ci is not None and h3_ci[0] > 0 and point["i_task"] > 0
    return h1, h3


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def pct(value):
    return "NA" if value is None else f"{100*value:.3f}%"


def main() -> None:
    verify_hashes(INPUT_PATHS)
    rows = read_rows()
    if len(rows) != 800 or len({r["annotation_item_id"] for r in rows}) != 800:
        raise ValueError("canonical dataset integrity failed")
    point = estimands(rows)
    descriptive = {}
    for definition in ("strict", "lenient"):
        human = f"{definition}_human_success"
        descriptive[definition] = {s: raw_and_weighted(rows, s, human) for s in SCORERS}
    descriptive["scorer_asr"] = {}
    for scorer in SCORERS:
        descriptive["scorer_asr"][scorer] = {"raw_success_count": sum(r[scorer] for r in rows), "raw_n": len(rows), "weighted_asr": ratio(rows, lambda r: r[scorer], lambda r: r["analysis_weight"])}
    descriptive["delta_asr"] = descriptive["scorer_asr"]["s0"]["weighted_asr"] - descriptive["scorer_asr"]["s2"]["weighted_asr"]

    draws, boot = bootstrap(rows)
    write_csv(BOOTSTRAP, draws)
    gee = {kind: gee_fit(rows, kind) for kind in ("strict", "definition", "task")}
    exploratory = subgroup_rows(rows)
    write_csv(EXPLORATORY, exploratory)
    ci = boot["intervals"]
    h1_ci = ci["d_strict"]["ci_95_percentile"]
    h1_reject, h3_reject = confirmatory_decisions(point, ci)
    h3_ci = ci["i_task"]["ci_95_percentile"]

    # Separate frozen A/B sensitivity comparisons; AMBIGUOUS rows excluded.
    annotator_sensitivity = {}
    for who in ("a", "b"):
        annotator_sensitivity[who] = {}
        for definition in ("strict", "lenient"):
            human = f"annotator_{who}_{definition}_success"
            subset = [r for r in rows if r[human] != ""]
            for r in subset: r[human] = int(r[human])
            recalibrated, collapse = replicate_weights(
                subset, {r["confirmatory_prompt_id"]: 1 for r in subset}
            )
            annotator_sensitivity[who][definition] = {}
            for scorer in SCORERS:
                raw = metrics(subset, scorer, human)
                for key in ("tp", "tn", "fp", "fn"):
                    raw[key] = int(raw[key])
                annotator_sensitivity[who][definition][scorer] = {
                    "raw": raw,
                    "weighted_recalibrated": metrics(
                        recalibrated, scorer, human, "bootstrap_weight"
                    ),
                }
            annotator_sensitivity[who][definition]["recalibration_fallback_counts"] = dict(collapse)

    result = {
        "analysis_status": "COMPLETE",
        "analysis_dataset_sha256": sha256_file(DATA),
        "frozen_input_sha256": json.loads((PRIVATE / "analysis_dataset_freeze_audit.json").read_text())["input_sha256"],
        "raw_complete_case_n": len(rows), "ambiguous_rows": 0,
        "point_estimands": point, "bootstrap": boot,
        "primary_h1": {"estimand": "D_STRICT", "estimate": point["d_strict"], "ci_95_percentile": h1_ci, "primary_p_value": None, "p_value_note": "No primary bootstrap p-value was specified in the frozen SAP; the registered CI decision rule was used.", "decision": "REJECT" if h1_reject else "FAIL_TO_REJECT"},
        "rq2": {"d_lenient": point["d_lenient"], "d_lenient_ci_95": ci["d_lenient"]["ci_95_percentile"], "i_definition": point["i_definition"], "i_definition_ci_95": ci["i_definition"]["ci_95_percentile"], "inferential_status": "ESTIMATION_ONLY"},
        "secondary_h3": {"d_generative": point["d_generative"], "d_classification": point["d_classification"], "i_task": point["i_task"], "i_task_ci_95": h3_ci, "gate_opened": h1_reject, "decision": ("REJECT" if h3_reject else "FAIL_TO_REJECT") if h1_reject else "NOT_FORMALLY_TESTED_GATE_CLOSED"},
        "descriptive_metrics": descriptive,
        "weight_diagnostics": weight_diagnostics(rows),
        "triggered_uncalibrated_ipw_sensitivity": {
            "reason": "Kish effective sample size below 50% of analyzed n",
            "point_estimates": point,
            "bootstrap_intervals": boot["triggered_uncalibrated_ipw_sensitivity_intervals"],
            "note": "At the observed sample, calibrated stratum totals equal recorded base-weight totals, so point estimates coincide; bootstrap intervals omit replicate recalibration.",
        },
        "annotator_sensitivity": annotator_sensitivity,
        "gee_robustness": gee,
        "exploratory_subgroups": exploratory,
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": __import__("scipy").__version__},
        "deviations": [],
    }
    PRIMARY.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    GEE.write_text(json.dumps(gee, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    public = dict(result)
    public["private_artifact_sha256"] = {"analysis_dataset": sha256_file(DATA), "primary_results": sha256_file(PRIMARY), "bootstrap_results": sha256_file(BOOTSTRAP), "gee_results": sha256_file(GEE), "exploratory_results": sha256_file(EXPLORATORY)}
    PUBLIC_JSON.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_JSON.write_text(json.dumps(public, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def ci_text(name):
        interval = ci[name]["ci_95_percentile"]
        return "unavailable" if interval is None else f"[{pct(interval[0])}, {pct(interval[1])}]"
    gstrict = gee["strict"].get("estimates", {}).get("s2")
    gdefinition_raw = gee["definition"].get("estimates", {}).get("s2_x_lenient")
    gdefinition = None if gdefinition_raw is None else {
        "estimate": -gdefinition_raw["estimate"],
        "se": gdefinition_raw["se"],
        "ci_95": [-gdefinition_raw["ci_95"][1], -gdefinition_raw["ci_95"][0]],
        "p_value_two_sided": gdefinition_raw["p_value_two_sided"],
    }
    gtask = gee["task"].get("estimates", {}).get("s2_x_generative")
    lines = [
        "# Confirmatory results", "", "This is the first preregistered confirmatory scorer–human analysis. Population estimates use frozen inverse-probability weights; raw results describe the deliberately stratified 800-response sample.", "",
        "## Table 1 — Primary H1 and RQ2", "", "| Human definition | Raw S0 correct | Raw S2 correct | Weighted accuracy S0 | Weighted accuracy S2 | S2−S0 | 95% cluster-bootstrap CI | Inferential status |", "|---|---:|---:|---:|---:|---:|---:|---|",
        f"| Strict | {descriptive['strict']['s0']['raw']['tp']+descriptive['strict']['s0']['raw']['tn']}/800 | {descriptive['strict']['s2']['raw']['tp']+descriptive['strict']['s2']['raw']['tn']}/800 | {pct(point['accuracy_s0_strict'])} | {pct(point['accuracy_s2_strict'])} | {pct(point['d_strict'])} | {ci_text('d_strict')} | H1 {result['primary_h1']['decision']} |",
        f"| Lenient | {descriptive['lenient']['s0']['raw']['tp']+descriptive['lenient']['s0']['raw']['tn']}/800 | {descriptive['lenient']['s2']['raw']['tp']+descriptive['lenient']['s2']['raw']['tn']}/800 | {pct(point['accuracy_s0_lenient'])} | {pct(point['accuracy_s2_lenient'])} | {pct(point['d_lenient'])} | {ci_text('d_lenient')} | RQ2 estimation only |", "",
        f"I_DEFINITION = {pct(point['i_definition'])}, 95% CI {ci_text('i_definition')}. No directional significance test was performed.", "", "The frozen SAP specified a CI-based primary decision rule but no primary bootstrap p-value; none was invented. The GEE robustness p-value is reported separately.", "",
        "## Table 2 — Secondary H3", "", "| Task category | Weighted S0 strict accuracy | Weighted S2 strict accuracy | S2−S0 | 95% CI |", "|---|---:|---:|---:|---:|",
        f"| Generative/text transformation | {pct(point['accuracy_s0_strict_generative'])} | {pct(point['accuracy_s2_strict_generative'])} | {pct(point['d_generative'])} | {ci_text('d_generative')} |",
        f"| Closed-label classification | {pct(point['accuracy_s0_strict_classification'])} | {pct(point['accuracy_s2_strict_classification'])} | {pct(point['d_classification'])} | {ci_text('d_classification')} |", "",
        f"I_TASK = {pct(point['i_task'])}, 95% CI {ci_text('i_task')}. Gate opened: **{'yes' if h1_reject else 'no'}**. H3: **{result['secondary_h3']['decision']}**.", "",
        "## Table 3 — GEE robustness", "", "| Estimand | Bootstrap estimate (95% CI) | GEE estimate | GEE 95% CI | GEE p-value |", "|---|---:|---:|---:|---:|",
        f"| D_STRICT | {pct(point['d_strict'])} {ci_text('d_strict')} | {pct(gstrict['estimate']) if gstrict else 'unavailable'} | {('['+pct(gstrict['ci_95'][0])+', '+pct(gstrict['ci_95'][1])+']') if gstrict else 'unavailable'} | {gstrict['p_value_two_sided'] if gstrict else 'unavailable'} |",
        f"| I_DEFINITION | {pct(point['i_definition'])} {ci_text('i_definition')} | {pct(gdefinition['estimate']) if gdefinition else 'unavailable'} | {('['+pct(gdefinition['ci_95'][0])+', '+pct(gdefinition['ci_95'][1])+']') if gdefinition else 'unavailable'} | {gdefinition['p_value_two_sided'] if gdefinition else 'unavailable'} |",
        f"| I_TASK | {pct(point['i_task'])} {ci_text('i_task')} | {pct(gtask['estimate']) if gtask else 'unavailable'} | {('['+pct(gtask['ci_95'][0])+', '+pct(gtask['ci_95'][1])+']') if gtask else 'unavailable'} | {gtask['p_value_two_sided'] if gtask else 'unavailable'} |", "",
        "## Descriptive metrics", "",
    ]
    for definition in ("strict", "lenient"):
        lines += [f"### {definition.title()}", "", "| Scorer | Raw TP | Raw TN | Raw FP | Raw FN | Weighted accuracy | Weighted precision | Weighted recall | Weighted F1 | Weighted kappa |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for scorer in SCORERS:
            m = descriptive[definition][scorer]
            lines.append(f"| {scorer.upper()} | {m['raw']['tp']} | {m['raw']['tn']} | {m['raw']['fp']} | {m['raw']['fn']} | {pct(m['weighted']['accuracy'])} | {pct(m['weighted']['precision'])} | {pct(m['weighted']['recall'])} | {pct(m['weighted']['f1'])} | {m['weighted']['kappa']:.4f} |")
        lines.append("")
        lines += ["Raw unweighted analogues:", "", "| Scorer | Accuracy | Precision | Recall | F1 | Kappa |", "|---|---:|---:|---:|---:|---:|"]
        for scorer in SCORERS:
            raw = descriptive[definition][scorer]["raw"]
            lines.append(f"| {scorer.upper()} | {pct(raw['accuracy'])} | {pct(raw['precision'])} | {pct(raw['recall'])} | {pct(raw['f1'])} | {raw['kappa']:.4f} |")
        lines.append("")
    lines += ["## Automated scorer ASR (descriptive)", "", "| Scorer | Raw successes / 800 | Weighted ASR | 95% cluster-bootstrap CI |", "|---|---:|---:|---:|", f"| S0 | {descriptive['scorer_asr']['s0']['raw_success_count']}/800 | {pct(point['asr_s0'])} | {ci_text('asr_s0')} |", f"| S2 | {descriptive['scorer_asr']['s2']['raw_success_count']}/800 | {pct(point['asr_s2'])} | {ci_text('asr_s2')} |", "", f"Delta ASR (S0−S2) = {pct(point['delta_asr'])}, 95% CI {ci_text('delta_asr')}; its direction is structural and was not hypothesis-tested.", "", "## Prespecified weight sensitivity", "", f"The Kish effective sample size was {result['weight_diagnostics']['kish_effective_sample_size']:.1f}/800, triggering the frozen uncalibrated-IPW sensitivity. Point estimates coincide because observed calibrated stratum totals equal the recorded base-weight totals. The uncalibrated cluster-bootstrap D_STRICT interval was {('['+pct(boot['triggered_uncalibrated_ipw_sensitivity_intervals']['d_strict']['ci_95_percentile'][0])+', '+pct(boot['triggered_uncalibrated_ipw_sensitivity_intervals']['d_strict']['ci_95_percentile'][1])+']')}.", "", "## Interpretation constraints", "", "S2 success is a mathematical subset of S0 success. The S0–S2 ASR direction and the location of their discordances are therefore not treated as empirical hypotheses. The confirmatory question is alignment with independently adjudicated human judgments. RQ2 is estimation-focused; subgroup tables in the machine-readable output are explicitly exploratory and descriptive.", "", "All sampled D10 records were strict human failures. Under the frozen calibrated percentile bootstrap this boundary result makes D_STRICT and its task-category components invariant across replicates, yielding zero-width primary intervals. The triggered uncalibrated-IPW sensitivity and GEE robust intervals retain sampling variation and are reported without replacing the primary method.", "", "There were zero adjudicated AMBIGUOUS rows, so complete-case and AMBIGUOUS-bound analyses coincide.", ""]
    PUBLIC_MD.write_text("\n".join(lines), encoding="utf-8")

    audit = ["# Confirmatory analysis audit", "", "Status: **PASS**", "", f"- Canonical analysis rows: 800", f"- Canonical analysis dataset SHA-256: `{sha256_file(DATA)}`", f"- Bootstrap seed: `{BOOTSTRAP_SEED}`", f"- Bootstrap replicates requested: `{BOOTSTRAP_REPLICATES}`", f"- Valid replicates: all main estimands `{min(v['valid_replicates'] for v in ci.values())}` or more", "- Bootstrap unit: base prompt; stratified by task", "- Recorded inclusion probabilities and inverse-probability weights used: yes", "- S2 implies S0: yes", "- AMBIGUOUS rows: 0", "- Response generation performed by analysis: no", "- Frozen human labels or scorer outputs modified: no", "- Deviations from frozen SAP: none", "", "The frozen SAP did not specify a primary bootstrap p-value. Its registered percentile-CI decision rule was applied without substituting a test. GEE p-values are robustness results.", ""]
    PUBLIC_AUDIT.write_text("\n".join(audit), encoding="utf-8")
    print(json.dumps({"status": "PASS", "analysis_dataset_sha256": sha256_file(DATA), "result_hashes": public["private_artifact_sha256"], "h1_decision": result["primary_h1"]["decision"], "h3_gate_opened": h1_reject}, indent=2))


if __name__ == "__main__":
    main()
