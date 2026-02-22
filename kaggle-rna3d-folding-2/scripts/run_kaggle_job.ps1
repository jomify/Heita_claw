param(
  [Parameter(Mandatory = $true)][string]$KaggleUsername,
  [string]$KernelSlug = "rna3d-folding2-baseline"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Py = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$KaggleConfigDir = Join-Path $ProjectRoot "kaggle_config"

if (!(Test-Path $Py)) { throw "Missing venv python. Run setup_env.ps1 first." }
if (!(Test-Path (Join-Path $KaggleConfigDir "kaggle.json"))) { throw "Missing kaggle_config\kaggle.json" }

$env:KAGGLE_CONFIG_DIR = $KaggleConfigDir

& $Py (Join-Path $ProjectRoot "scripts\prepare_kaggle_kernel.py") --username $KaggleUsername --slug $KernelSlug

Push-Location (Join-Path $ProjectRoot "kaggle_kernel")
try {
  & (Join-Path $ProjectRoot ".venv\Scripts\kaggle.exe") kernels push
  Write-Host "Kernel pushed. Check Kaggle for run status/output and submission.csv in /kaggle/working."
}
finally {
  Pop-Location
}
