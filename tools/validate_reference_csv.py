#!/usr/bin/env python3
"""Validate Metashape camera reference CSV files without third-party packages."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import Counter
from pathlib import Path


REQUIRED_COLUMNS = (
    "image_name",
    "camera_band",
    "Longitude",
    "Latitude",
    "Elevation",
)
EXPECTED_BANDS = {"RGB", "Green", "Red", "RedEdge", "NIR"}


def validate(path: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    bands: Counter[str] = Counter()
    names: Counter[str] = Counter()
    values: dict[str, list[float]] = {
        "Longitude": [],
        "Latitude": [],
        "Elevation": [],
    }

    try:
        stream = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        print(f"ERROR {path}: {exc}")
        return 1

    with stream:
        reader = csv.DictReader(stream)
        missing = [name for name in REQUIRED_COLUMNS if name not in (reader.fieldnames or [])]
        if missing:
            print(f"ERROR {path}: missing columns: {', '.join(missing)}")
            return 1

        row_count = 0
        for line_number, row in enumerate(reader, start=2):
            row_count += 1
            image_name = (row["image_name"] or "").strip()
            band = (row["camera_band"] or "").strip()
            if not image_name:
                errors.append(f"line {line_number}: empty image_name")
            else:
                names[image_name] += 1
            if not band:
                errors.append(f"line {line_number}: empty camera_band")
            else:
                bands[band] += 1

            for column in ("Longitude", "Latitude", "Elevation"):
                raw = (row[column] or "").strip()
                try:
                    number = float(raw)
                except ValueError:
                    errors.append(f"line {line_number}: invalid {column}={raw!r}")
                    continue
                if not math.isfinite(number):
                    errors.append(f"line {line_number}: non-finite {column}={raw!r}")
                    continue
                values[column].append(number)
                if column == "Longitude" and not -180 <= number <= 180:
                    errors.append(f"line {line_number}: longitude outside [-180, 180]")
                if column == "Latitude" and not -90 <= number <= 90:
                    errors.append(f"line {line_number}: latitude outside [-90, 90]")

    duplicate_names = [name for name, count in names.items() if count > 1]
    if duplicate_names:
        errors.append(f"duplicate image names: {len(duplicate_names)}")

    unknown_bands = sorted(set(bands) - EXPECTED_BANDS)
    missing_bands = sorted(EXPECTED_BANDS - set(bands))
    if unknown_bands:
        warnings.append(f"unexpected bands: {', '.join(unknown_bands)}")
    if missing_bands:
        warnings.append(f"missing expected bands: {', '.join(missing_bands)}")
    if bands and len(set(bands.values())) != 1:
        warnings.append("band counts are not equal")

    print(f"FILE {path}")
    print(f"  rows: {row_count}")
    print("  bands: " + ", ".join(f"{name}={count}" for name, count in sorted(bands.items())))
    for column in ("Longitude", "Latitude", "Elevation"):
        if values[column]:
            print(f"  {column}: {min(values[column]):.12g} .. {max(values[column]):.12g}")
    for warning in warnings:
        print(f"  WARNING: {warning}")
    for error in errors[:20]:
        print(f"  ERROR: {error}")
    if len(errors) > 20:
        print(f"  ERROR: ... and {len(errors) - 20} more")
    print("  result: " + ("FAIL" if errors else "PASS"))
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, nargs="+", help="reference CSV file(s)")
    args = parser.parse_args()
    return max(validate(path) for path in args.csv)


if __name__ == "__main__":
    sys.exit(main())
