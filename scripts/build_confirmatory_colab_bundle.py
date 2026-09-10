#!/usr/bin/env python3
"""Build the private amended-Phi Colab bundle without pilot dependencies."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from src.confirmatory import sha256_file


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_MANIFEST = ROOT / "confirmatory_private/prompts/confirmatory_prompt_manifest.jsonl"
AUDIT = ROOT / "confirmatory/prompt_manifest_audit.json"
PUBLIC_FILES = (
    ".gitignore",
    "requirements-confirmatory.txt",
    "requirements-confirmatory-test.txt",
    "pytest.ini",
    "scripts/build_confirmatory_colab_bundle.py",
    "scripts/run_confirmatory_generation.py",
    "scripts/run_confirmatory_phi_amended.py",
    "src/__init__.py",
    "src/confirmatory.py",
    "tests/test_confirmatory_activation.py",
    "tests/test_confirmatory_phi_amended.py",
    "protocol/final_generation_config.yaml",
    "protocol/final_model_revisions.yaml",
    "confirmatory/prompt_manifest_audit.json",
    "confirmatory/generation_readiness.md",
    "confirmatory/dependency_packaging_correction.md",
    "confirmatory/phi_generation_incident_audit.md",
    "confirmatory/phi_amended_generation_readiness.md",
    "protocol/amendment_002_phi_generation_compatibility.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "confirmatory_colab_bundle_phi_amended_v1.zip",
    )
    return parser.parse_args()


def build_bundle(output: Path) -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if sha256_file(PRIVATE_MANIFEST) != audit["prompt_manifest_sha256"]:
        raise ValueError("private prompt manifest hash differs from public audit")
    config = ROOT / "protocol/final_generation_config.yaml"
    if sha256_file(config) != audit["generation_config_sha256"]:
        raise ValueError("generation config hash differs from public audit")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing bundle: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in PUBLIC_FILES:
            path = ROOT / relative
            if not path.is_file():
                raise FileNotFoundError(path)
            archive.write(path, relative)
        archive.write(
            PRIVATE_MANIFEST,
            "confirmatory_private/prompts/confirmatory_prompt_manifest.jsonl",
        )
    with zipfile.ZipFile(output, "r") as archive:
        names = set(archive.namelist())
    if "requirements.txt" in names:
        raise AssertionError("legacy requirements.txt entered confirmatory bundle")
    if "requirements-confirmatory.txt" not in names:
        raise AssertionError("confirmatory requirements missing from bundle")
    if "tests/test_confirmatory_activation.py" not in names:
        raise AssertionError("confirmatory activation tests missing from bundle")
    if "scripts/run_confirmatory_phi_amended.py" not in names:
        raise AssertionError("amended Phi runner missing from bundle")
    if "tests/test_confirmatory_phi_amended.py" not in names:
        raise AssertionError("amended Phi tests missing from bundle")
    print(f"created {output}")
    print(f"bundle_sha256={sha256_file(output)}")
    print(f"prompt_manifest_sha256={audit['prompt_manifest_sha256']}")


if __name__ == "__main__":
    build_bundle(parse_args().output)
