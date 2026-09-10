#!/usr/bin/env python3
"""Restore frozen non-human annotation fields without changing human entries."""

from __future__ import annotations

import argparse
import csv
import io
import subprocess
from pathlib import Path


HUMAN_FIELDS = {"human_label", "human_confidence", "notes"}


def read_rows(raw: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    rows = list(reader)
    return list(reader.fieldnames or []), rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--reference-revision", required=True)
    args = parser.parse_args()

    fields, current = read_rows(args.path.read_bytes())
    reference_raw = subprocess.check_output(
        ["git", "show", f"{args.reference_revision}:{args.path.as_posix()}"]
    )
    reference_fields, reference = read_rows(reference_raw)
    if fields != reference_fields:
        raise ValueError("annotation columns differ from the frozen reference")
    if len(current) != len(reference):
        raise ValueError("annotation row count differs from the frozen reference")
    if [row["sample_id"] for row in current] != [row["sample_id"] for row in reference]:
        raise ValueError("sample IDs or row order differ from the frozen reference")

    human_before = [tuple(row[field] for field in fields if field in HUMAN_FIELDS) for row in current]
    repaired: list[dict[str, str]] = []
    for current_row, reference_row in zip(current, reference, strict=True):
        repaired.append(
            {
                field: current_row[field] if field in HUMAN_FIELDS else reference_row[field]
                for field in fields
            }
        )

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(repaired)
    temporary = args.path.with_suffix(args.path.suffix + ".tmp")
    temporary.write_bytes(buffer.getvalue().encode("utf-8"))
    temporary.replace(args.path)

    _, after = read_rows(args.path.read_bytes())
    human_after = [tuple(row[field] for field in fields if field in HUMAN_FIELDS) for row in after]
    if human_after != human_before:
        raise RuntimeError("human-entered fields changed during structural restoration")
    print(f"restored frozen non-human fields for {len(after)} rows; human fields unchanged")


if __name__ == "__main__":
    main()
