#!/usr/bin/env bash
# package-release.sh — Zips the PyInstaller dist and prepares for GitHub release
# Run from repo root after build-package.ps1 has completed:
#   bash scripts/package-release.sh -v v0.1.3-beta

set -euo pipefail

VERSION=""
while getopts "v:" opt; do
    case $opt in
        v) VERSION="$OPTARG" ;;
        *) echo "Usage: bash scripts/package-release.sh -v <version>" >&2; exit 1 ;;
    esac
done

if [[ -z "$VERSION" ]]; then
    echo "ERROR: -v <version> is required" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

DIST_DIR="dist/RogueTech-Codex"
ZIP_NAME="RogueTech-Codex-${VERSION}.zip"

if [[ ! -d "$DIST_DIR" ]]; then
    echo "ERROR: $DIST_DIR not found. Run build-package.ps1 in PowerShell first." >&2
    exit 1
fi

echo "==> Packaging $ZIP_NAME"
rm -f "$ZIP_NAME"
zip -r "$ZIP_NAME" "$DIST_DIR"

SIZE=$(du -h "$ZIP_NAME" | cut -f1)
echo "    $ZIP_NAME ($SIZE)"
echo ""
echo "Package ready: $ZIP_NAME"
echo "Upload to GitHub Release with:"
echo "  gh release upload $VERSION $ZIP_NAME"
