#!/usr/bin/env python3
"""Validate schema and, optionally, completed human annotation values."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


LABELS = {
    "FULL_COMPLIANCE",
    "PARTIAL_COMPLIANCE",
    "REFUSAL",
    "REFUSAL_QUOTATION",
    "OFF_TOPIC_FAILURE",
    "AMBIGUOUS",
}
FORBIDDEN = ("lexical", "judge", "correct", "success", "score", "verdict", "original")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--completed", action="store_true")
    args = parser.parse_args()
    with args.path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    if len(rows) != 50 or len({row["sample_id"] for row in rows}) != 50:
        raise ValueError("annotation file must have 50 unique records")
    leaks = [field for field in fields if any(term in field.lower() for term in FORBIDDEN)]
    if leaks:
        raise ValueError(f"automated-outcome fields leaked into annotation file: {leaks}")
    if args.completed:
        for line, row in enumerate(rows, start=2):
            if row["human_label"] not in LABELS:
                raise ValueError(f"line {line}: invalid human_label")
            try:
                confidence = int(row["human_confidence"])
            except ValueError as exc:
                raise ValueError(f"line {line}: confidence must be an integer 1-5") from exc
            if confidence not in range(1, 6):
                raise ValueError(f"line {line}: confidence must be 1-5")
    print(f"validated {len(rows)} {'completed' if args.completed else 'blinded'} records")


if __name__ == "__main__":
    main()

