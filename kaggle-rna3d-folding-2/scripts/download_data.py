from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def kaggle_cmd() -> list[str]:
    exe = Path(sys.executable).resolve().parent / "kaggle.exe"
    if exe.exists():
        return [str(exe)]
    return ["kaggle"]

COMPETITION = "stanford-rna-3d-folding-2"


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_raw = project_root / "data" / "raw"
    data_raw.mkdir(parents=True, exist_ok=True)

    kaggle_config = project_root / "kaggle_config"
    os.environ["KAGGLE_CONFIG_DIR"] = str(kaggle_config)

    cmd = [
        *kaggle_cmd(),
        "competitions",
        "download",
        "-c",
        COMPETITION,
        "-p",
        str(data_raw),
        "--force",
    ]
    subprocess.run(cmd, check=True)

    zip_path = data_raw / f"{COMPETITION}.zip"
    if zip_path.exists():
        subprocess.run([
            "python",
            "-m",
            "zipfile",
            "-e",
            str(zip_path),
            str(data_raw),
        ], check=True)

    print(f"Data ready at: {data_raw}")


if __name__ == "__main__":
    main()
