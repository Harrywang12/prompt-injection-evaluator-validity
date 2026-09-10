"""Small, dependency-free binary metrics for paired scorer evaluation."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from collections.abc import Callable, Sequence


def confusion_counts(truth: Sequence[bool], prediction: Sequence[bool]) -> dict[str, int]:
    if len(truth) != len(prediction) or not truth:
        raise ValueError("truth and prediction must be non-empty and equally sized")
    return {
        "true_negative": sum(not y and not p for y, p in zip(truth, prediction, strict=True)),
        "false_positive": sum(not y and p for y, p in zip(truth, prediction, strict=True)),
        "false_negative": sum(y and not p for y, p in zip(truth, prediction, strict=True)),
        "true_positive": sum(y and p for y, p in zip(truth, prediction, strict=True)),
    }


def safe_divide(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def classification_metrics(truth: Sequence[bool], prediction: Sequence[bool]) -> dict[str, float | None]:
    counts = confusion_counts(truth, prediction)
    tn, fp = counts["true_negative"], counts["false_positive"]
    fn, tp = counts["false_negative"], counts["true_positive"]
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    f1 = None if precision is None or recall is None else safe_divide(2 * precision * recall, precision + recall)
    return {
        "accuracy": (tp + tn) / len(truth),
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def cohens_kappa(truth: Sequence[bool], prediction: Sequence[bool]) -> float | None:
    counts = confusion_counts(truth, prediction)
    n = len(truth)
    observed = (counts["true_positive"] + counts["true_negative"]) / n
    truth_positive = (counts["true_positive"] + counts["false_negative"]) / n
    predicted_positive = (counts["true_positive"] + counts["false_positive"]) / n
    expected = truth_positive * predicted_positive + (1 - truth_positive) * (1 - predicted_positive)
    return safe_divide(observed - expected, 1 - expected)


def exact_mcnemar_p(false_positives: int, false_negatives: int) -> float | None:
    """Two-sided exact McNemar p-value conditional on discordant pairs."""

    if false_positives < 0 or false_negatives < 0:
        raise ValueError("discordant counts cannot be negative")
    discordant = false_positives + false_negatives
    if discordant == 0:
        return None
    lower = min(false_positives, false_negatives)
    tail = sum(math.comb(discordant, k) for k in range(lower + 1)) / (2**discordant)
    return min(1.0, 2 * tail)


def percentile(values: Sequence[float], probability: float) -> float:
    if not values or not 0 <= probability <= 1:
        raise ValueError("values must be non-empty and probability within [0, 1]")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def paired_bootstrap(
    rows: Sequence[object],
    statistics: dict[str, Callable[[list[object]], float]],
    *,
    iterations: int,
    seed: int,
    confidence_level: float = 0.95,
) -> dict[str, dict[str, float]]:
    if not rows or iterations <= 0 or not 0 < confidence_level < 1:
        raise ValueError("invalid bootstrap arguments")
    rng = random.Random(seed)
    distributions = {name: [] for name in statistics}
    n = len(rows)
    for _ in range(iterations):
        replicate = [rows[rng.randrange(n)] for _ in range(n)]
        for name, statistic in statistics.items():
            distributions[name].append(statistic(replicate))
    alpha = (1 - confidence_level) / 2
    return {
        name: {
            "lower": percentile(values, alpha),
            "upper": percentile(values, 1 - alpha),
        }
        for name, values in distributions.items()
    }


def stratified_finite_population_bootstrap(
    rows: Sequence[dict],
    *,
    stratum_field: str,
    population_sizes: dict[str, int],
    statistics: dict[str, Callable[[list[dict]], float | None]],
    iterations: int,
    seed: int,
    confidence_level: float = 0.95,
) -> dict[str, dict[str, float | int]]:
    """Percentile bootstrap for stratified SRSWOR using pseudo-populations.

    Each observed stratum sample is expanded to its known finite population
    size by balanced replication plus a random remainder. A sample of the
    original stratum size is then drawn without replacement. This preserves
    fixed stratum allocation and incorporates the finite-population sampling
    fraction instead of treating the combined sample as iid.
    """

    if not rows or iterations <= 0 or not 0 < confidence_level < 1:
        raise ValueError("invalid bootstrap arguments")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[str(row[stratum_field])].append(row)
    if set(grouped) != set(population_sizes):
        raise ValueError("observed and population strata differ")
    for stratum, sample in grouped.items():
        if not sample or len(sample) > population_sizes[stratum]:
            raise ValueError("invalid stratum sample/population size")

    rng = random.Random(seed)
    distributions: dict[str, list[float]] = {name: [] for name in statistics}
    undefined = {name: 0 for name in statistics}
    for _ in range(iterations):
        replicate: list[dict] = []
        for stratum in sorted(grouped):
            sample = grouped[stratum]
            population_size = population_sizes[stratum]
            quotient, remainder = divmod(population_size, len(sample))
            pseudo_population = sample * quotient
            if remainder:
                pseudo_population += rng.sample(sample, remainder)
            replicate.extend(rng.sample(pseudo_population, len(sample)))
        for name, statistic in statistics.items():
            value = statistic(replicate)
            if value is None or not math.isfinite(value):
                undefined[name] += 1
            else:
                distributions[name].append(value)

    alpha = (1 - confidence_level) / 2
    output: dict[str, dict[str, float | int]] = {}
    for name, values in distributions.items():
        if not values:
            raise ValueError(f"all bootstrap replicates undefined for {name}")
        output[name] = {
            "lower": percentile(values, alpha),
            "upper": percentile(values, 1 - alpha),
            "valid_replicates": len(values),
            "undefined_replicates": undefined[name],
        }
    return output
