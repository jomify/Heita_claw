# Kaggle Pipeline: stanford-rna-3d-folding-2

Automated baseline pipeline for downloading data, generating a valid submission, validating format, optional submit, and run logging.

## 1) Environment setup (Windows PowerShell)

```powershell
cd C:\Users\86178\.openclaw\workspace\kaggle-rna3d-folding-2
powershell -ExecutionPolicy Bypass -File .\scripts\setup_env.ps1 -KaggleJsonSource "E:\setup\kaggle.json"
$env:KAGGLE_CONFIG_DIR = (Resolve-Path .\kaggle_config).Path
```

This creates `.venv`, installs dependencies (including `kaggle` CLI locally), and copies `kaggle.json` into `kaggle_config/`.

## 2) Download competition data

```powershell
.\.venv\Scripts\python.exe .\scripts\download_data.py
```

## 3) Build baseline submission (dry run)

```powershell
.\.venv\Scripts\python.exe .\scripts\baseline_train_infer.py
```

Baseline logic:
- Uses `sample_submission` schema
- Fills targets with global means from `train_labels` when available
- Falls back to zeros if labels unavailable

Output:
- `artifacts/submission_dryrun.csv`

## 4) Validate submission format

```powershell
.\.venv\Scripts\python.exe .\scripts\validate_submission.py
```

Checks columns and row count against `data/raw/sample_submission.csv`.

## 5) Optional submit

Dry-run submit command preview:
```powershell
.\.venv\Scripts\python.exe .\scripts\submit.py --file artifacts/submission_dryrun.csv --message "baseline test" --dry-run
```

Real submit:
```powershell
.\.venv\Scripts\python.exe .\scripts\submit.py --file artifacts/submission_dryrun.csv --message "baseline test"
```

## 6) Run one full iteration (cron/task-scheduler friendly)

```powershell
.\.venv\Scripts\python.exe .\scripts\run_iteration.py --dry-submit
```

Options:
- `--skip-download`
- `--submit`
- `--dry-submit`
- `--message "..."`

## Logs & score tracking

- `logs/runs.jsonl`: each generation run metadata
- `logs/submit_history.jsonl`: submit attempts
- `logs/best_score.json`: best score snapshot (maintained by `update_best_score.py`)

Update best score snapshot:

```powershell
.\.venv\Scripts\python.exe .\scripts\update_best_score.py
```
