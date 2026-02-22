from __future__ import annotations

import csv
from pathlib import Path


# Kaggle Notebook/Job runtime paths
INPUT_ROOT = Path("/kaggle/input")
WORKING_ROOT = Path("/kaggle/working")


def find_file(name: str) -> Path:
    matches = list(INPUT_ROOT.rglob(name))
    if not matches:
        raise FileNotFoundError(f"Could not find {name} under /kaggle/input")
    return matches[0]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    sample_path = find_file("sample_submission.csv")
    train_labels_path = None
    try:
        train_labels_path = find_file("train_labels.csv")
    except FileNotFoundError:
        pass

    sample_rows = read_csv_rows(sample_path)
    if not sample_rows:
        raise ValueError("sample_submission.csv is empty")

    fieldnames = list(sample_rows[0].keys())
    id_cols = [c for c in fieldnames if c.lower() in {"id", "row_id"}]
    target_cols = [c for c in fieldnames if c not in id_cols]

    means = {c: 0.0 for c in target_cols}
    if train_labels_path is not None:
        labels = read_csv_rows(train_labels_path)
        for col in target_cols:
            vals = []
            for r in labels:
                try:
                    vals.append(float(r[col]))
                except Exception:
                    pass
            if vals:
                means[col] = sum(vals) / len(vals)

    output_path = WORKING_ROOT / "submission.csv"
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sample_rows:
            out = dict(row)
            for col in target_cols:
                out[col] = f"{means[col]:.6f}"
            writer.writerow(out)

    print(f"Wrote: {output_path}")
    print("Done. You can submit /kaggle/working/submission.csv to the competition.")


if __name__ == "__main__":
    main()
