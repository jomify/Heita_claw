from __future__ import annotations

import argparse
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

COMPETITION = "stanford-rna-3d-folding-2"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="artifacts/submission_dryrun.csv")
    parser.add_argument("--message", default="baseline auto submit")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    kaggle_config = project_root / "kaggle_config"
    os.environ["KAGGLE_CONFIG_DIR"] = str(kaggle_config)

    file_path = (project_root / args.file).resolve()
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    cmd = [
        *kaggle_cmd(),
        "competitions",
        "submit",
        "-c",
        COMPETITION,
        "-f",
        str(file_path),
        "-m",
        args.message,
    ]

    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "file": str(file_path.relative_to(project_root)),
        "message": args.message,
        "dry_run": bool(args.dry_run),
    }

    try:
        if args.dry_run:
            print("[DRY RUN]", " ".join(cmd))
            record["status"] = "dry_run"
        else:
            subprocess.run(cmd, check=True)
            record["status"] = "submitted"
    except subprocess.CalledProcessError as e:
        record["status"] = "failed"
        record["error"] = str(e)
        raise
    finally:
        submit_log = project_root / "logs" / "submit_history.jsonl"
        submit_log.parent.mkdir(parents=True, exist_ok=True)
        with submit_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
