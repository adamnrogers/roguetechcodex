# GitHub Actions Release Setup

Trunk-based deployment: all work merges to `main`; a version tag on `main` triggers a release.

---

## What CI can and cannot build

| Artifact | CI can build? | Reason |
|---|---|---|
| Frontend (JS/CSS) | ✅ | Pure code — no mod files needed |
| `roguetech.db` | ❌ | Built from mod files at `RT_ROOT`, not in repo |
| `portraits/` | ❌ | Converted from mod DDS files at `RT_ROOT`, not in repo |
| `RogueTech-Codex.exe` | ⚠️ Partially | Windows runner can run PyInstaller, but the exe bundles `roguetech.db` and portraits which CI doesn't have |

**Practical conclusion:** use CI to create the release and generate notes; upload the built artifact manually.

---

## 1. Repository Prerequisites

### Enable GitHub Actions
**Settings → Actions → General → Allow all actions**.

### Protect `main` (optional but recommended)
**Settings → Branches → Add rule → `main`**:
- Require pull request before merging
- Require status checks to pass

---

## 2. Tagging Convention

Use [Semantic Versioning](https://semver.org/): `v<MAJOR>.<MINOR>.<PATCH>`

```bash
git tag v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

Tag must be on `main`. To delete a tag before a release is created:

```bash
git tag -d v1.2.0
git push origin :refs/tags/v1.2.0
```

---

## 3. Workflow File — CI creates the release, you upload artifacts

Create `.github/workflows/release.yml`:

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

The release is created as a **draft**. After you upload your artifacts (see below), publish it manually via the GitHub UI.

---

## 4. Uploading artifacts to the release

After building locally (see `docs/building-locally.md`), upload with the `gh` CLI:

```bash
gh release upload v1.0.0 RogueTech-Codex-v1.0.0.zip
```

Then publish the draft:

```bash
gh release edit v1.0.0 --draft=false
```

Or publish via the GitHub UI: go to **Releases**, open the draft, click **Publish release**.

---

## 5. What `--generate-notes` does

GitHub auto-generates release notes from PR titles and commit messages since the previous tag. The result can be edited before publishing. For clean notes, use conventional commit messages (`feat:`, `fix:`, `chore:` etc.).

---

## 6. Pre-releases

Tags containing a hyphen (e.g. `v1.0.0-beta`, `v1.0.0-rc1`) are automatically marked as pre-releases by the workflow above.

---

## 7. Version in the UI

The navbar version label is read at build time from `frontend/src/package.json` via a Vite `define` constant (`__APP_VERSION__`). Bump the `version` field before tagging — the built app shows it automatically.

---

## 8. Typical Release Flow

```bash
# 1. Ensure main is up to date
git checkout main && git pull

# 2. Bump version in frontend/src/package.json (e.g. "1.0.0")
git add frontend/src/package.json
git commit -m "chore: bump version to v1.0.0"
git push

# 3. Build artifacts locally (see docs/building-locally.md)
#    - make dev-pipeline && make copy-db   (WSL)
#    - make portraits                      (WSL)
#    - cd frontend/src && npm run build    (WSL)
#    - pyinstaller standalone/roguetech.spec  (PowerShell)
#    - Compress-Archive dist\RogueTech-Codex RogueTech-Codex-v1.0.0.zip  (PowerShell)

# 4. Tag and push — triggers the workflow which creates a draft release
git tag v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 5. Upload artifact to the draft release
gh release upload v1.0.0 RogueTech-Codex-v1.0.0.zip

# 6. Publish
gh release edit v1.0.0 --draft=false
```

---

## 9. Advanced: CI builds the exe (optional)

If you want CI to build the exe, it needs `roguetech.db`. One way: maintain a `data-latest` release tag containing only the DB, updated whenever the mod changes.

**Upload the DB to a data release (run locally after each mod update):**

```bash
# First time
gh release create data-latest --title "Data (DB)" roguetech.db

# Subsequent updates
gh release upload data-latest roguetech.db --clobber
```

**Workflow job on `windows-latest` that downloads the DB and builds the exe:**

```yaml
  build-exe:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - name: Download DB from data release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: gh release download data-latest --pattern roguetech.db

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Build frontend
        working-directory: frontend/src
        run: |
          npm ci
          npm run build

      - name: Build exe
        run: |
          pip install pyinstaller
          pip install -r api/requirements.txt
          pyinstaller standalone/roguetech.spec

      - name: Package
        run: |
          Compress-Archive -Path dist\RogueTech-Codex `
            -DestinationPath "RogueTech-Codex-${{ github.ref_name }}.zip"

      - name: Upload to release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh release upload ${{ github.ref_name }} `
            "RogueTech-Codex-${{ github.ref_name }}.zip"
```

Note: this workflow still requires `roguetech.db` and the `portraits/` directory to be available (downloaded from the data release). Portraits are bundled into the exe by PyInstaller — no separate upload needed.
