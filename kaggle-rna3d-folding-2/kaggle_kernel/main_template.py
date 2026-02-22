from __future__ import annotations

import csv
from pathlib import Path
from statistics import median


# Kaggle Notebook/Job runtime paths
INPUT_ROOT = Path('/kaggle/input')
WORKING_ROOT = Path('/kaggle/working')
STRATEGY = '__STRATEGY__'  # mean | median | mean_median_blend
BLEND_ALPHA = __BLEND_ALPHA__


def find_file(name: str) -> Path:
    matches = list(INPUT_ROOT.rglob(name))
    if not matches:
        raise FileNotFoundError(f'Could not find {name} under /kaggle/input')
    return matches[0]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def pick_value(values: list[float]) -> float:
    if not values:
        return 0.0
    m = sum(values) / len(values)
    md = median(values)
    if STRATEGY == 'mean':
        return m
    if STRATEGY == 'median':
        return md
    return BLEND_ALPHA * m + (1.0 - BLEND_ALPHA) * md


def main() -> None:
    sample_path = find_file('sample_submission.csv')
    train_labels_path = None
    try:
        train_labels_path = find_file('train_labels.csv')
    except FileNotFoundError:
        pass

    sample_rows = read_csv_rows(sample_path)
    if not sample_rows:
        raise ValueError('sample_submission.csv is empty')

    fieldnames = list(sample_rows[0].keys())
    id_cols = [c for c in fieldnames if c.lower() in {'id', 'row_id'}]
    target_cols = [c for c in fieldnames if c not in id_cols]

    stats = {c: 0.0 for c in target_cols}
    if train_labels_path is not None:
        labels = read_csv_rows(train_labels_path)
        for col in target_cols:
            vals = []
            for r in labels:
                try:
                    vals.append(float(r[col]))
                except Exception:
                    pass
            stats[col] = pick_value(vals)

    output_path = WORKING_ROOT / 'submission.csv'
    with output_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sample_rows:
            out = dict(row)
            for col in target_cols:
                out[col] = f'{stats[col]:.6f}'
            writer.writerow(out)

    print(f'STRATEGY={STRATEGY}, BLEND_ALPHA={BLEND_ALPHA}')
    print(f'Wrote: {output_path}')


if __name__ == '__main__':
    main()
