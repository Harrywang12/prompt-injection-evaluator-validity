import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_aggregate_results_match_frozen_values():
    result = json.loads((ROOT / "confirmatory/confirmatory_results.json").read_text())
    point = result["point_estimands"]
    assert point["accuracy_s0_strict"] == 0.8109990739171592
    assert point["accuracy_s2_strict"] == 0.9277625427735582
    assert point["d_strict"] == 0.11676346885639899
    assert point["d_lenient"] == 0.00773839280504518
    assert point["i_definition"] == 0.10902507605135381
    assert point["d_generative"] == 0.282842785355348
    assert point["d_classification"] == 0.05249999999999999
    assert point["i_task"] == 0.23034278535534802


def test_public_freeze_provenance_identifiers():
    freeze = json.loads(
        (ROOT / "confirmatory/final_confirmatory_study_freeze.json").read_text()
    )
    assert freeze["external_preregistration"]["url"] == "https://osf.io/9jrab"
    assert freeze["external_preregistration"]["preregistered_commit"] == "853eb6aa7c61e03896cdca3eb991fcf8debdc9cc"
    assert freeze["analysis"]["results_commit"] == "68d077c96424a7834e9cbc3fd65578b33f904bca"
    assert freeze["sha256"]["final_human_ground_truth"] == "20804593269be59b3578fb1e12f033d7b3044895775a21dc2195ca5bb53f11e7"
    assert freeze["sha256"]["canonical_analysis_dataset"] == "634f4ef28c68696f8c7681fa83827bb12ab6568c5077e9ddf6c926bfe2bf6a3b"


def test_private_data_directories_are_absent():
    for name in ("confirmatory_private", "external", "annotations", "data"):
        assert not (ROOT / name).exists()


def test_historical_private_tags_are_not_recreated():
    # The clean export records their names and SHAs as provenance only.
    import subprocess

    tags = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True).splitlines()
    assert "confirmatory-preregistered-v1" not in tags
    assert "confirmatory-analysis-v1" not in tags
