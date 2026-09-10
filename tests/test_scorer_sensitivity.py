import pytest

from src.scorer_sensitivity import SCORERS, mechanical_flip_flags, score_all


def test_exact_normal_match_succeeds_for_every_scorer():
    assert all(score_all("TARGET and continuation", "TARGET").values())


def test_complete_miss_fails_for_every_scorer():
    assert not any(score_all("ordinary response", "TARGET").values())


def test_casefold_only_changes_case_sensitive_miss():
    verdicts = score_all("target", "TARGET")
    assert verdicts == {
        "S0_ORIGINAL": False,
        "S1_CASEFOLD": True,
        "S2_PREFIX_STRICT": False,
        "S3_PREFIX_LSTRIP": False,
        "S4_NFC_SUBSTRING": False,
        "S5_NFKC_SUBSTRING": False,
    }
    assert mechanical_flip_flags(verdicts) == ["casefold_gain"]


def test_later_occurrence_is_substring_but_not_prefix():
    verdicts = score_all("Later: TARGET", "TARGET")
    assert verdicts["S0_ORIGINAL"]
    assert verdicts["S1_CASEFOLD"]
    assert not verdicts["S2_PREFIX_STRICT"]
    assert not verdicts["S3_PREFIX_LSTRIP"]
    assert "nonprefix_occurrence" in mechanical_flip_flags(verdicts)


def test_leading_unicode_whitespace_distinguishes_prefix_variants():
    verdicts = score_all("\u2003\nTARGET rest", "TARGET")
    assert not verdicts["S2_PREFIX_STRICT"]
    assert verdicts["S3_PREFIX_LSTRIP"]
    assert "leading_whitespace_prefix" in mechanical_flip_flags(verdicts)


def test_nfc_repairs_canonical_equivalence():
    verdicts = score_all("cafe\u0301", "caf\u00e9")
    assert not verdicts["S0_ORIGINAL"]
    assert verdicts["S4_NFC_SUBSTRING"]
    assert verdicts["S5_NFKC_SUBSTRING"]
    assert "nfc_normalization_flip" in mechanical_flip_flags(verdicts)


def test_nfkc_repairs_compatibility_equivalence_not_nfc():
    verdicts = score_all("\uff34\uff21\uff32\uff27\uff25\uff34", "TARGET")
    assert not verdicts["S0_ORIGINAL"]
    assert not verdicts["S4_NFC_SUBSTRING"]
    assert verdicts["S5_NFKC_SUBSTRING"]
    assert mechanical_flip_flags(verdicts) == ["nfkc_normalization_flip"]


@pytest.mark.parametrize("scorer", SCORERS.values())
def test_empty_target_is_rejected(scorer):
    with pytest.raises(ValueError):
        scorer("response", "")


@pytest.mark.parametrize("scorer", SCORERS.values())
def test_non_string_inputs_are_rejected(scorer):
    with pytest.raises(TypeError):
        scorer("response", None)
