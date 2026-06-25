# build-package.ps1 — Windows packaging script for standalone release
# Runs steps 4–5: PyInstaller build + zip
# Run from repo root in PowerShell:
#   cd "\\wsl$\Ubuntu\home\snafu\projects\RogueTech Codex"
#   .\scripts\build-package.ps1 -Version v0.1.1-beta

param(
    [Parameter(Mandatory = $true)]
    [string]$Version
)

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

Write-Host "==> [4/5] Building standalone exe"
pip install --quiet pyinstaller
pip install --quiet -r api\requirements.txt
pyinstaller standalone\roguetech.spec

$distDir = "dist\RogueTech-Codex"
if (-not (Test-Path $distDir)) {
    Write-Error "PyInstaller output not found at $distDir"
    exit 1
}
Write-Host "    dist\RogueTech-Codex\ built"

Write-Host "==> [5/5] Packaging zip"
$zipName = "RogueTech-Codex-$Version.zip"
if (Test-Path $zipName) {
    Remove-Item $zipName -Force
}
Compress-Archive -Path $distDir -DestinationPath $zipName

$sizeMB = [math]::Round((Get-Item $zipName).Length / 1MB, 1)
Write-Host "    $zipName ($sizeMB MB)"

Write-Host ""
Write-Host "Package ready: $zipName"
Write-Host "Upload to GitHub Release with:"
Write-Host "  gh release upload $Version $zipName"
