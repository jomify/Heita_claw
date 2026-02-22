# Kaggle Pipeline: stanford-rna-3d-folding-2

Default workflow is **Kaggle-side compute (GPU enabled)**.
Local machine workflow is **CPU-only** and intended for prep/format validation.

## 1) Local setup (CPU-only prep tools)

```powershell
cd C:\Users\86178\.openclaw\workspace\kaggle-rna3d-folding-2
powershell -ExecutionPolicy Bypass -File .\scripts\setup_env.ps1 -KaggleJsonSource "E:\setup\kaggle.json"
$env:KAGGLE_CONFIG_DIR = (Resolve-Path .\kaggle_config).Path
```

## 2) Kaggle GPU execution path (default)

This pushes a Kaggle Kernel configured with `enable_gpu: true` and competition source `stanford-rna-3d-folding-2`.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_kaggle_job.ps1 -KaggleUsername "<your_kaggle_username>"
```

Files used:
- `kaggle_kernel/main.py` (baseline train/infer logic on Kaggle runtime)
- `kaggle_kernel/kernel-metadata.template.json` (GPU enabled)
- `kaggle_kernel/kernel-metadata.json` (generated, ignored until created)

After run completes on Kaggle:
- output submission file is `/kaggle/working/submission.csv`
- submit on Kaggle UI or via local `scripts/submit.py` after downloading the file.

## 3) Local CPU-only mode (prep/validation only)

Optional local data pull (no GPU use):
```powershell
.\.venv\Scripts\python.exe .\scripts\download_data.py
```

Build local dry-run submission:
```powershell
.\.venv\Scripts\python.exe .\scripts\baseline_train_infer.py
```

Validate submission format:
```powershell
.\.venv\Scripts\python.exe .\scripts\validate_submission.py
```

## 4) Optional submission from local file

Dry-run:
```powershell
.\.venv\Scripts\python.exe .\scripts\submit.py --file artifacts/submission_dryrun.csv --message "baseline test" --dry-run
```

Real:
```powershell
.\.venv\Scripts\python.exe .\scripts\submit.py --file artifacts/submission_dryrun.csv --message "baseline test"
```

## 5) Cron/task scheduler (local orchestrator, CPU-only)

```powershell
.\.venv\Scripts\python.exe .\scripts\run_iteration.py --skip-download --dry-submit
```

Use this for validation/logging orchestration only. Training/inference should run on Kaggle compute.

## Logs & score tracking

- `logs/runs.jsonl`: generation runs
- `logs/submit_history.jsonl`: submit attempts
- `logs/best_score.json`: best score snapshot

Update best score snapshot:
```powershell
.\.venv\Scripts\python.exe .\scripts\update_best_score.py
```
