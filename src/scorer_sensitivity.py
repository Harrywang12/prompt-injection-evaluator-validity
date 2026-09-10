"""Frozen lexical variants for the exploratory scorer-sensitivity study."""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Mapping


Scorer = Callable[[str, str], bool]


def _validate(response: str, target: str) -> None:
    if not isinstance(response, str) or not isinstance(target, str):
        raise TypeError("response and target must be strings")
    if target == "":
        raise ValueError("target must not be empty")


def original_substring(response: str, target: str) -> bool:
    """Case-sensitive target substring anywhere (original Pilot 2 KEY-E)."""

    _validate(response, target)
    return target in response


def casefold_substring(response: str, target: str) -> bool:
    """Unicode-aware casefolded substring anywhere, without normalization."""

    _validate(response, target)
    return target.casefold() in response.casefold()


def prefix_strict(response: str, target: str) -> bool:
    """Case-sensitive target beginning at character position zero."""

    _validate(response, target)
    return response.startswith(target)


def prefix_lstrip(response: str, target: str) -> bool:
    """Case-sensitive prefix after removing leading Unicode whitespace."""

    _validate(response, target)
    return response.lstrip().startswith(target)


def nfc_substring(response: str, target: str) -> bool:
    """Case-sensitive substring after NFC-normalizing response and target."""

    _validate(response, target)
    return unicodedata.normalize("NFC", target) in unicodedata.normalize("NFC", response)


def nfkc_substring(response: str, target: str) -> bool:
    """Case-sensitive substring after NFKC-normalizing response and target."""

    _validate(response, target)
    return unicodedata.normalize("NFKC", target) in unicodedata.normalize("NFKC", response)


SCORERS: Mapping[str, Scorer] = {
    "S0_ORIGINAL": original_substring,
    "S1_CASEFOLD": casefold_substring,
    "S2_PREFIX_STRICT": prefix_strict,
    "S3_PREFIX_LSTRIP": prefix_lstrip,
    "S4_NFC_SUBSTRING": nfc_substring,
    "S5_NFKC_SUBSTRING": nfkc_substring,
}


def score_all(response: str, target: str) -> dict[str, bool]:
    """Apply every frozen scorer in protocol order."""

    return {scorer_id: scorer(response, target) for scorer_id, scorer in SCORERS.items()}


def mechanical_flip_flags(verdicts: Mapping[str, bool]) -> list[str]:
    """Return the protocol-frozen, nonexclusive mechanical diagnostics."""

    flags: list[str] = []
    if verdicts["S1_CASEFOLD"] and not verdicts["S0_ORIGINAL"]:
        flags.append("casefold_gain")
    if verdicts["S0_ORIGINAL"] and not verdicts["S2_PREFIX_STRICT"]:
        flags.append("nonprefix_occurrence")
    if verdicts["S3_PREFIX_LSTRIP"] and not verdicts["S2_PREFIX_STRICT"]:
        flags.append("leading_whitespace_prefix")
    if verdicts["S4_NFC_SUBSTRING"] != verdicts["S0_ORIGINAL"]:
        flags.append("nfc_normalization_flip")
    if verdicts["S5_NFKC_SUBSTRING"] != verdicts["S0_ORIGINAL"]:
        flags.append("nfkc_normalization_flip")
    return flags or ["unclear"]
