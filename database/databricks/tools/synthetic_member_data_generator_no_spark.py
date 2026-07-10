#!/usr/bin/env python3
"""
Standalone synthetic member data generator.

This script mirrors the synthetic member schema used by the Databricks
benchmark notebooks, but runs as normal Python without Spark.

Supported output:
- CSV
- JSON Lines

Typical usage:

    python tools/synthetic_member_data_generator.py ^
      --row-count 1000000 ^
      --output-files 8 ^
      --output-dir C:\data\member_output ^
      --format csv

    python tools/synthetic_member_data_generator.py \
      --row-count 1000000 \
      --output-files 8 \
      --output-dir /data/output/member_output \
      --format json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timedelta
from pathlib import Path


CITY_STATE_SEQUENCE = [
    ("Denver", "CO"),
    ("Phoenix", "AZ"),
    ("Nashville", "TN"),
    ("Austin", "TX"),
    ("Seattle", "WA"),
]


def build_row(record_id: int) -> dict[str, object]:
    city, state = CITY_STATE_SEQUENCE[record_id % 5]
    dob = datetime(1980, 1, 1) + timedelta(days=record_id % 12000)

    return {
        "custid": record_id,
        "name": f"Member {record_id:08d}",
        "address": f"{(record_id % 9999) + 1} Test Street",
        "city": city,
        "state": state,
        "zip": f"{record_id % 99999:05d}",
        "phone": f"555{record_id % 10000000:07d}",
        "email": f"member{record_id:08d}@samplecu.org",
        "dob": dob.strftime("%Y-%m-%dT%H:%M:%S"),
        "creditcard": f"45{record_id:014d}",
        "creditcardcode": (record_id % 900) + 100,
        "ssn": f"{record_id % 1000000000:09d}",
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")))
            handle.write("\n")


def chunk_bounds(total_rows: int, output_files: int) -> list[tuple[int, int]]:
    rows_per_file = math.ceil(total_rows / output_files)
    bounds: list[tuple[int, int]] = []

    start = 1
    while start <= total_rows:
        end = min(start + rows_per_file - 1, total_rows)
        bounds.append((start, end))
        start = end + 1

    return bounds


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic member data files for local or shared filesystem testing."
    )
    parser.add_argument("--row-count", type=int, required=True, help="Total number of rows to generate.")
    parser.add_argument(
        "--output-files",
        type=int,
        required=True,
        help="Number of output files to create.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where generated files should be written.",
    )
    parser.add_argument(
        "--format",
        choices=("csv", "json"),
        default="csv",
        help="Output format. 'json' writes JSON Lines.",
    )
    parser.add_argument(
        "--file-prefix",
        default="member_data",
        help="Prefix for output file names.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.row_count <= 0:
        raise ValueError("--row-count must be greater than 0.")
    if args.output_files <= 0:
        raise ValueError("--output-files must be greater than 0.")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    bounds = chunk_bounds(args.row_count, args.output_files)
    extension = "csv" if args.format == "csv" else "jsonl"

    print("Synthetic member data generator")
    print(f"  row_count: {args.row_count}")
    print(f"  output_files_requested: {args.output_files}")
    print(f"  output_files_created: {len(bounds)}")
    print(f"  output_dir: {output_dir}")
    print(f"  format: {args.format}")

    total_written = 0

    for index, (start_id, end_id) in enumerate(bounds, start=1):
        rows = [build_row(record_id) for record_id in range(start_id, end_id + 1)]
        file_path = output_dir / f"{args.file_prefix}_{index:03d}.{extension}"

        if args.format == "csv":
            write_csv(file_path, rows)
        else:
            write_jsonl(file_path, rows)

        total_written += len(rows)
        print(
            f"  wrote {file_path.name}: rows {start_id}-{end_id} "
            f"({len(rows)} records)"
        )

    print(f"Done. Total rows written: {total_written}")


if __name__ == "__main__":
    main()
