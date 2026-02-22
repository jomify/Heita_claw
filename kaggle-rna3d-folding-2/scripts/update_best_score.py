from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def kaggle_cmd() -> list[str]:
    exe = Path(sys.executable).resolve().parent / "kaggle.exe"
    if exe.exists():
        return [str(exe)]
    return ["kaggle"]

import pandas as pd

COMPETITION = "stanford-rna-3d-folding-2"


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    os.environ["KAGGLE_CONFIG_DIR"] = str(project_root / "kaggle_config")

    out_csv = project_root / "artifacts" / "submissions.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    raw = subprocess.run(
        [*kaggle_cmd(), "competitions", "submissions", "-c", COMPETITION],
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if len(lines) < 2:
        print("No submissions yet.")
        return

    # Kaggle CLI table output is not stable CSV; keep raw snapshot for manual inspection.
    out_csv.write_text(raw, encoding="utf-8")

    best_path = project_root / "logs" / "best_score.json"
    cur = {"best_score": None, "updated_at": None}
    if best_path.exists():
        cur = json.loads(best_path.read_text(encoding="utf-8"))

    # Best-effort extract from any floating number in lines
    import re

    scores = []
    for ln in lines[1:]:
        for m in re.findall(r"\b\d+\.\d+\b", ln):
            scores.append(float(m))
    if scores:
        candidate = min(scores)
        if cur.get("best_score") is None or candidate < cur["best_score"]:
            cur = {"best_score": candidate, "updated_at": datetime.now().isoformat(timespec="seconds")}
            best_path.parent.mkdir(parents=True, exist_ok=True)
            best_path.write_text(json.dumps(cur, indent=2), encoding="utf-8")

    print(json.dumps(cur, ensure_ascii=False))


if __name__ == "__main__":
    main()
