# build-package.ps1 — Windows packaging script for standalone release
# Runs step 4: PyInstaller build only
# Run from repo root in PowerShell:
#   cd '\\wsl$\Ubuntu\home\snafu\projects\RogueTech Codex'
#   .\scripts\build-package.ps1

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot | Split-Path -Parent
Set-Location $RepoRoot

# Verify WSL outputs exist before starting
foreach ($required in @("roguetech.db", "portraits", "frontend\src\dist")) {
    if (-not (Test-Path $required)) {
        Write-Error "Missing required build artifact: $required`nRun build-wsl.sh in WSL first."
        exit 1
    }
}

Write-Host "==> [4/4] Building standalone exe"
pip install --quiet pyinstaller
pip install --quiet -r api\requirements.txt
pyinstaller standalone\roguetech.spec

$distDir = "dist\RogueTech-Codex"
if (-not (Test-Path $distDir)) {
    Write-Error "PyInstaller output not found at $distDir"
    exit 1
}
Write-Host "    dist\RogueTech-Codex\ built"

Write-Host ""
Write-Host "PyInstaller build complete."
Write-Host "Back in WSL, run: bash scripts/package-release.sh -v <version>"
