import pytest

from src.metrics import (
    classification_metrics,
    cohens_kappa,
    confusion_counts,
    exact_mcnemar_p,
    stratified_finite_population_bootstrap,
)


def test_confusion_and_classification_metrics():
    truth = [True, True, False, False]
    prediction = [True, False, True, False]
    assert confusion_counts(truth, prediction) == {
        "true_negative": 1,
        "false_positive": 1,
        "false_negative": 1,
        "true_positive": 1,
    }
    assert classification_metrics(truth, prediction) == {
        "accuracy": 0.5,
        "precision": 0.5,
        "recall": 0.5,
        "f1": 0.5,
    }


def test_kappa_perfect_and_chance_agreement():
    assert cohens_kappa([True, False], [True, False]) == pytest.approx(1.0)
    assert cohens_kappa([True, True, False, False], [True, False, True, False]) == pytest.approx(0.0)


def test_exact_mcnemar_is_symmetric_and_handles_no_disagreement():
    assert exact_mcnemar_p(0, 0) is None
    assert exact_mcnemar_p(1, 5) == pytest.approx(exact_mcnemar_p(5, 1))
    assert exact_mcnemar_p(0, 6) == pytest.approx(0.03125)


def test_stratified_finite_population_bootstrap_respects_constant_strata():
    rows = [
        {"stratum": "positive", "value": 1.0},
        {"stratum": "positive", "value": 1.0},
        {"stratum": "negative", "value": 0.0},
        {"stratum": "negative", "value": 0.0},
    ]
    ci = stratified_finite_population_bootstrap(
        rows,
        stratum_field="stratum",
        population_sizes={"positive": 4, "negative": 6},
        statistics={"weighted_mean": lambda sample: (
            4 * sum(r["value"] for r in sample if r["stratum"] == "positive") / 2
            + 6 * sum(r["value"] for r in sample if r["stratum"] == "negative") / 2
        ) / 10},
        iterations=100,
        seed=7,
    )
    assert ci["weighted_mean"]["lower"] == pytest.approx(0.4)
    assert ci["weighted_mean"]["upper"] == pytest.approx(0.4)
