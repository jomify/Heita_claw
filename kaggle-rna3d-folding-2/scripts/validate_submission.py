from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_schema_and_count(path: Path) -> tuple[list[str], int]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        count = sum(1 for _ in reader)
    return cols, count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", default="artifacts/submission_dryrun.csv")
    parser.add_argument("--sample", default="data/raw/sample_submission.csv")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    submission_path = project_root / args.submission
    sample_path = project_root / args.sample

    sub_cols, sub_rows = read_schema_and_count(submission_path)
    smp_cols, smp_rows = read_schema_and_count(sample_path)

    if sub_cols != smp_cols:
        raise ValueError("Submission columns do not match sample_submission")
    if sub_rows != smp_rows:
        raise ValueError("Submission row count does not match sample_submission")

    print("Submission format check: PASS")
    print(f"Rows: {sub_rows}, Columns: {len(sub_cols)}")


if __name__ == "__main__":
    main()
