from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--message", default="baseline auto iteration")
    parser.add_argument("--dry-submit", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    py = project_root / ".venv" / "Scripts" / "python.exe"
    if not py.exists():
        raise FileNotFoundError("Please run scripts/setup_env.ps1 first.")

    if not args.skip_download:
        run([str(py), "scripts/download_data.py"], project_root)

    run([str(py), "scripts/baseline_train_infer.py"], project_root)
    run([str(py), "scripts/validate_submission.py"], project_root)

    if args.submit or args.dry_submit:
        cmd = [str(py), "scripts/submit.py", "--file", "artifacts/submission_dryrun.csv", "--message", args.message]
        if args.dry_submit:
            cmd.append("--dry-run")
        run(cmd, project_root)


if __name__ == "__main__":
    main()
