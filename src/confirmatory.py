"""Deterministic helpers for the externally preregistered confirmatory study."""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Iterable


PREREGISTERED_COMMIT = "853eb6aa7c61e03896cdca3eb991fcf8debdc9cc"
PREREGISTRATION_TAG = "confirmatory-preregistered-v1"
UNTRUSTED_DELIMITER = "[UNTRUSTED EXTERNAL CONTENT]"
PRIVATE_ROOT = Path("confirmatory_private")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_text(value: str) -> str:
    """Frozen normalization used for deduplication/freshness hashes only."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", value).strip())


def length_framed_sha256(parts: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for part in parts:
        encoded = normalized_text(part).encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def input_content_sha256(value: str) -> str:
    return hashlib.sha256(normalized_text(value).encode("utf-8")).hexdigest()


def derived_seed(master: int, purpose: str, task: str) -> int:
    material = f"{master}:{purpose}:{task}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def stable_prompt_id(
    *, source_revision: str, task: str, source_row_id: str, template_id: str, target_id: str
) -> str:
    digest = length_framed_sha256(
        [
            "confirmatory-v1",
            source_revision,
            task,
            source_row_id,
            template_id,
            target_id,
        ]
    )
    return "C1-" + digest[:20].upper()


def canonical_json_line(record: dict) -> bytes:
    return (
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def generation_key(prompt_id: str, model_revision: str) -> str:
    return f"{prompt_id}::{model_revision}"


def response_filename(prompt_id: str, model_revision: str) -> str:
    digest = hashlib.sha256(generation_key(prompt_id, model_revision).encode("utf-8")).hexdigest()
    return f"{prompt_id}--{digest[:16]}.json"


def assert_unique_generation_keys(prompt_ids: Iterable[str], model_revisions: Iterable[str]) -> int:
    keys = [generation_key(prompt_id, revision) for prompt_id in prompt_ids for revision in model_revisions]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate generation keys")
    return len(keys)


def terminal_record_exists(output_dir: Path, prompt_id: str, model_revision: str) -> bool:
    return (output_dir / response_filename(prompt_id, model_revision)).exists()


def persist_terminal_record_once(output_dir: Path, record: dict) -> Path:
    """Atomically persist one terminal success/failure record without overwrite."""
    output_dir.mkdir(parents=True, exist_ok=True)
    required = {"confirmatory_prompt_id", "model_revision", "generation_status"}
    missing = required - record.keys()
    if missing:
        raise ValueError(f"terminal record missing fields: {sorted(missing)}")
    final = output_dir / response_filename(
        str(record["confirmatory_prompt_id"]), str(record["model_revision"])
    )
    payload = canonical_json_line(record)
    try:
        descriptor = os.open(final, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise FileExistsError(f"refusing to overwrite terminal record: {final}") from error
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    return final


def load_private_manifest(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.endswith("\n"):
                raise ValueError(f"manifest line {line_number} lacks LF terminator")
            records.append(json.loads(line))
    return records
