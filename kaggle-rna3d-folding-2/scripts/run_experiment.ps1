param(
  [Parameter(Mandatory = $true)][string]$KaggleUsername,
  [Parameter(Mandatory = $true)][string]$Slug,
  [ValidateSet('mean','median','mean_median_blend')][string]$Strategy = 'mean_median_blend',
  [double]$BlendAlpha = 0.7
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Py = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$KaggleExe = Join-Path $ProjectRoot '.venv\Scripts\kaggle.exe'
$KaggleConfigDir = Join-Path $ProjectRoot 'kaggle_config'

if (!(Test-Path $Py)) { throw 'Missing venv python. Run setup_env.ps1 first.' }
if (!(Test-Path $KaggleExe)) { throw 'Missing kaggle cli in venv.' }
if (!(Test-Path (Join-Path $KaggleConfigDir 'kaggle.json'))) { throw 'Missing kaggle_config\kaggle.json' }

$env:KAGGLE_CONFIG_DIR = $KaggleConfigDir

& $Py (Join-Path $ProjectRoot 'scripts\build_kaggle_experiment.py') --username $KaggleUsername --slug $Slug --strategy $Strategy --blend-alpha $BlendAlpha

Push-Location (Join-Path $ProjectRoot 'kaggle_kernel')
try {
  & $KaggleExe kernels push
}
finally {
  Pop-Location
}

Write-Host "Pushed experiment: $KaggleUsername/$Slug (strategy=$Strategy, blend_alpha=$BlendAlpha)"
