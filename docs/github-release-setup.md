# GitHub Actions Release Setup

Trunk-based deployment: all work merges to `main`; a version tag on `main` triggers a release.

---

## What CI can and cannot build

| Artifact | CI can build? | Notes |
|---|---|---|
| Frontend (JS/CSS) | ✅ | Pure code — no mod files needed |
| `RogueTech-Codex.exe` | ✅ | Windows runner downloads `roguetech.db` from data repo |
| `roguetech.db` | ❌ | Built from mod files at `RT_ROOT`, uploaded manually |
| `portraits/` | ❌ | Converted from mod DDS files at `RT_ROOT`, bundled locally |

---

## Repositories

| Repo | Purpose |
|---|---|
| `adamrogers/RogueTech-Codex` | Main code repo |
| `adamrogers/roguetechcodex-data` | Hosts `roguetech.db` as a release asset for CI |

The data repo exists only to serve the db to CI builds. It has no code. The `roguetech-db` release tag is updated in place on each mod update; the release title shows the build date.

---

## One-time setup

### 1. Create a PAT for cross-repo db access

The build workflow runs in `RogueTech-Codex` but downloads from `roguetechcodex-data`. `GITHUB_TOKEN` cannot cross repos, so a Personal Access Token is required.

1. GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Create a token scoped to `roguetechcodex-data` with **Contents: Read**
3. In `RogueTech-Codex` repo → **Settings → Secrets and variables → Actions**
4. Add secret named `DATA_REPO_TOKEN` with the PAT value

### 2. Update the build workflow to use the PAT

In `.github/workflows/build-standalone.yml`, the db download step uses `GH_TOKEN`. Change it to use the PAT secret:

```yaml
      - name: Download RogueTech DB
        env:
          GH_TOKEN: ${{ secrets.DATA_REPO_TOKEN }}
        shell: pwsh
        run: |
          gh release download roguetech-db --repo adamrogers/roguetechcodex-data \
            --pattern "roguetech.db" --output roguetech.db
```

### 3. Enable GitHub Actions

**Settings → Actions → General → Allow all actions**.

### 4. Protect `main` (optional but recommended)

**Settings → Branches → Add rule → `main`**:
- Require pull request before merging
- Require status checks to pass

---

## Tagging convention

Use [Semantic Versioning](https://semver.org/): `v<MAJOR>.<MINOR>.<PATCH>`

Tags containing a hyphen (e.g. `v1.0.0-beta`) are automatically marked as pre-releases.

```bash
git tag v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

To delete a tag before a release is created:

```bash
git tag -d v1.2.0
git push origin :refs/tags/v1.2.0
```

---

## Release workflow

`.github/workflows/release.yml` fires on version tags and creates a draft release with auto-generated notes. The `build-standalone.yml` workflow builds the exe and uploads it.

### `release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Create draft release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          PRERELEASE_FLAG=""
          if [[ "${{ github.ref_name }}" == *-* ]]; then
            PRERELEASE_FLAG="--prerelease"
          fi

          gh release create ${{ github.ref_name }} \
            --title "RogueTech Codex ${{ github.ref_name }}" \
            --generate-notes \
            --draft \
            $PRERELEASE_FLAG
```

---

## Version in the UI

The navbar version label is read at build time from `frontend/src/package.json` via a Vite `define` constant (`__APP_VERSION__`). Bump the `version` field before tagging.

---

## Typical release flow

```bash
# 1. Ensure main is up to date
git checkout main && git pull

# 2. Bump version in frontend/src/package.json (e.g. "1.2.0")
git add frontend/src/package.json
git commit -m "chore: bump version to v1.2.0"
git push

# 3. Tag — triggers release.yml which creates a draft release
git tag v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# 4. Trigger the exe build
gh workflow run build-standalone.yml -f version=v1.2.0

# 5. Download the built exe artifact from the Actions run, attach to the draft release
gh release upload v1.2.0 RogueTech-Codex-v1.2.0.zip

# 6. Publish
gh release edit v1.2.0 --draft=false
```

---

## Updating the database

Run after each RogueTech mod update. No RTC release required.

```bash
# Rebuild the database
cd /path/to/RogueTech-Codex
make dev-pipeline

# Copy to data repo and publish
cp pipeline/roguetech.db ../roguetechcodex-data/roguetech.db
cd ../roguetechcodex-data
gh release edit roguetech-db --title "RogueTech DB $(date +%Y-%m-%d)"
gh release upload roguetech-db roguetech.db --clobber
```

First time only (creates the `roguetech-db` release):

```bash
cd ../roguetechcodex-data
gh release create roguetech-db roguetech.db \
  --title "RogueTech DB $(date +%Y-%m-%d)" \
  --prerelease \
  --notes "Pipeline-generated database for RogueTech Codex CI builds"
```
