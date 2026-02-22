# Silver-target Iteration Loop (Kaggle GPU only)

This loop is designed to run **all training/inference on Kaggle compute (GPU enabled)**.
Local machine is CPU-only for orchestration/logging.

## Loop steps

1. Build + push one experiment kernel to Kaggle
2. Wait for Kaggle run completion
3. Submit output (`/kaggle/working/submission.csv`) on Kaggle
4. Pull submission history and update best score
5. Record hypothesis + result in `logs/runs.jsonl`
6. Iterate

## Run one experiment (GPU on Kaggle)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_experiment.ps1 -KaggleUsername "<username>" -Slug "rna3d-exp-001" -Strategy "mean_median_blend" -BlendAlpha 0.7
```

## Suggested starter sweep

- exp-001: mean
- exp-002: median
- exp-003: mean_median_blend alpha=0.3
- exp-004: mean_median_blend alpha=0.5
- exp-005: mean_median_blend alpha=0.7
- exp-006: mean_median_blend alpha=0.9

## Pull leaderboard snapshot

```powershell
.\.venv\Scripts\python.exe .\scripts\update_best_score.py
```

## Notes

- This scaffold gives a stable iterative mechanism.
- Reaching silver likely requires stronger feature/modeling kernels; use this loop to benchmark and rank each upgrade quickly.
