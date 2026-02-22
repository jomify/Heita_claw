from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--output", default="artifacts/submission_dryrun.csv")
    parser.add_argument("--run-log", default="logs/runs.jsonl")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / args.data_dir
    out_path = project_root / args.output

    sample_path = data_dir / "sample_submission.csv"
    if not sample_path.exists():
        raise FileNotFoundError(sample_path)

    sample_rows = read_csv(sample_path)
    fieldnames = list(sample_rows[0].keys()) if sample_rows else []
    id_cols = [c for c in fieldnames if c.lower() in {"id", "row_id"}]
    target_cols = [c for c in fieldnames if c not in id_cols]

    means = {c: 0.0 for c in target_cols}
    label_path = data_dir / "train_labels.csv"
    if label_path.exists():
        labels = read_csv(label_path)
        for col in target_cols:
            vals = []
            for r in labels:
                try:
                    vals.append(float(r[col]))
                except Exception:
                    pass
            if vals:
                means[col] = sum(vals) / len(vals)

    out_rows = []
    for row in sample_rows:
        new_row = dict(row)
        for c in target_cols:
            new_row[c] = f"{means[c]:.6f}"
        out_rows.append(new_row)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    run_log_path = project_root / args.run_log
    run_log_path.parent.mkdir(parents=True, exist_ok=True)
    with run_log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "rows": len(out_rows),
            "output": str(out_path.relative_to(project_root)),
            "score": None,
        }) + "\n")

    print(f"Wrote submission: {out_path}")


if __name__ == "__main__":
    main()
