from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True, help="Kaggle username")
    parser.add_argument("--slug", default="rna3d-folding2-baseline")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    template = project_root / "kaggle_kernel" / "kernel-metadata.template.json"
    target = project_root / "kaggle_kernel" / "kernel-metadata.json"

    data = json.loads(template.read_text(encoding="utf-8"))
    data["id"] = f"{args.username}/{args.slug}"
    data["title"] = args.slug

    target.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {target}")


if __name__ == "__main__":
    main()
