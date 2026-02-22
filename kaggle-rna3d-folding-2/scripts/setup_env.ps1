param(
  [string]$PythonExe = "python",
  [string]$KaggleJsonSource = "E:\setup\kaggle.json"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPath = Join-Path $ProjectRoot ".venv"
$KaggleConfigDir = Join-Path $ProjectRoot "kaggle_config"

if (!(Test-Path $VenvPath)) {
  & $PythonExe -m venv $VenvPath
}

$Py = Join-Path $VenvPath "Scripts\python.exe"
& $Py -m pip install --upgrade pip
& $Py -m pip install -r (Join-Path $ProjectRoot "requirements.txt")

if (!(Test-Path $KaggleConfigDir)) {
  New-Item -ItemType Directory -Path $KaggleConfigDir | Out-Null
}

$TargetJson = Join-Path $KaggleConfigDir "kaggle.json"
Copy-Item -Path $KaggleJsonSource -Destination $TargetJson -Force

# Best-effort permission hardening on Windows
icacls $TargetJson /inheritance:r | Out-Null
icacls $TargetJson /grant:r "$env:USERNAME:(R)" | Out-Null

Write-Host "Done."
Write-Host "Activate: .\\.venv\\Scripts\\Activate.ps1"
Write-Host "Set env for current shell: $env:KAGGLE_CONFIG_DIR='$KaggleConfigDir'"
