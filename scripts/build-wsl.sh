#!/usr/bin/env bash
# build-wsl.sh — WSL build prep for standalone release
# Runs steps 1–3: database, portraits, frontend
# Run from repo root: bash scripts/build-wsl.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

echo "==> [1/3] Building database"
make dev-pipeline
make copy-db

if [[ ! -f roguetech.db ]]; then
    echo "ERROR: roguetech.db not found after copy-db" >&2
    exit 1
fi
echo "    roguetech.db: $(du -h roguetech.db | cut -f1)"

echo "==> [2/3] Building portraits"
make portraits

if [[ ! -d portraits ]]; then
    echo "ERROR: portraits/ directory not found after make portraits" >&2
    exit 1
fi
echo "    portraits/: $(find portraits -type f | wc -l) files"

echo "==> [3/3] Building frontend (standalone: BLACKLISTED items hidden)"
cd frontend/src
npm ci
VITE_HIDE_BLACKLISTED=true npm run build
cd "$REPO_ROOT"

if [[ ! -d frontend/src/dist ]]; then
    echo "ERROR: frontend/src/dist not found after npm build" >&2
    exit 1
fi
echo "    dist/: $(find frontend/src/dist -type f | wc -l) files"

echo ""
echo "WSL build steps complete. Ready for PowerShell packaging."
echo "Run scripts/build-package.ps1 from a PowerShell window at this repo root."
