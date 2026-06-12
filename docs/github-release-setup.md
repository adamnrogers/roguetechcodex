# GitHub Actions Release Setup

Trunk-based deployment: all work merges to `main`; a version tag on `main` triggers a release build.

---

## 1. Repository Prerequisites

### Enable GitHub Actions
In your repository: **Settings → Actions → General → Allow all actions**.

### Create a Personal Access Token (if needed)
The default `GITHUB_TOKEN` provided by Actions is sufficient for creating releases and uploading assets. No PAT required unless you push to other repositories as part of the workflow.

### Protect `main`
**Settings → Branches → Add rule → `main`**:
- Require pull request before merging
- Require status checks to pass

This is optional but recommended for trunk-based flow.

---

## 2. Tagging Convention

Use [Semantic Versioning](https://semver.org/): `v<MAJOR>.<MINOR>.<PATCH>`

```bash
# Create and push a release tag
git tag v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

The tag must be on `main`. Never tag a feature branch.

To delete a tag (before a release is created):
```bash
git tag -d v1.2.0
git push origin :refs/tags/v1.2.0
```

---

## 3. Workflow File

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write   # required to create releases and upload assets

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      # ── Frontend build ──────────────────────────────────────────────────────
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/src/package-lock.json

      - name: Install frontend dependencies
        working-directory: frontend/src
        run: npm ci

      - name: Build frontend
        working-directory: frontend/src
        run: npm run build

      - name: Archive frontend dist
        run: |
          cd frontend/src
          zip -r ../../roguetech-codex-frontend-${{ github.ref_name }}.zip dist/

      # ── Create GitHub Release ───────────────────────────────────────────────
      - name: Create Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh release create ${{ github.ref_name }} \
            --title "RogueTech Codex ${{ github.ref_name }}" \
            --generate-notes \
            roguetech-codex-frontend-${{ github.ref_name }}.zip
```

---

## 4. What `--generate-notes` Does

GitHub auto-generates release notes from PR titles and commit messages since the previous tag. The result can be edited after creation. For clean notes, use descriptive PR titles and conventional commit messages (`feat:`, `fix:`, `chore:` etc.).

---

## 5. Adding More Artifacts

Each additional artifact is appended to the `gh release create` command:

```yaml
gh release create ${{ github.ref_name }} \
  --title "RogueTech Codex ${{ github.ref_name }}" \
  --generate-notes \
  roguetech-codex-frontend-${{ github.ref_name }}.zip \
  roguetech-codex-standalone-${{ github.ref_name }}.exe \
  roguetech.db
```

---

## 6. Standalone Windows Executable (PyInstaller)

The PyInstaller build must run on Windows. Add a second job:

```yaml
  build-standalone:
    runs-on: windows-latest
    needs: []   # run in parallel with the main release job

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r standalone/requirements.txt pyinstaller

      - name: Build executable
        run: pyinstaller standalone/codex.spec

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: standalone-exe
          path: dist/RogueTechCodex.exe
```

Then in the release job, download that artifact before calling `gh release create`:

```yaml
      - name: Download standalone artifact
        uses: actions/download-artifact@v4
        with:
          name: standalone-exe

      - name: Create Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh release create ${{ github.ref_name }} \
            --title "RogueTech Codex ${{ github.ref_name }}" \
            --generate-notes \
            roguetech-codex-frontend-${{ github.ref_name }}.zip \
            RogueTechCodex.exe
```

`needs: [build-standalone]` on the release job ensures the exe is ready before the release is created.

---

## 7. Pre-releases

Add `--prerelease` to mark alpha/beta tags:

```yaml
      - name: Create Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Mark as pre-release if tag contains a hyphen (e.g. v1.0.0-beta)
          PRERELEASE_FLAG=""
          if [[ "${{ github.ref_name }}" == *-* ]]; then
            PRERELEASE_FLAG="--prerelease"
          fi

          gh release create ${{ github.ref_name }} \
            --title "RogueTech Codex ${{ github.ref_name }}" \
            --generate-notes \
            $PRERELEASE_FLAG \
            roguetech-codex-frontend-${{ github.ref_name }}.zip
```

Tags like `v1.0.0-beta`, `v1.0.0-rc1` will be marked pre-release automatically.

---

## 8. Version in the UI

The navbar version label is read at build time from `frontend/src/package.json` via a Vite `define` constant (`__APP_VERSION__`). To update it, bump the `version` field in `package.json` before tagging — no code changes needed in the component itself.

---

## 9. Typical Release Flow

```bash
# 1. Ensure main is up to date and green
git checkout main
git pull

# 2. Bump the version in frontend/src/package.json
#    e.g. "0.1.0-beta" → "1.0.0"
#    The navbar label updates automatically on the next build.

# 3. Commit the version bump
git add frontend/src/package.json
git commit -m "chore: bump version to v1.0.0"
git push

# 4. Tag and push — must match the version in package.json
git tag v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 5. Watch the Actions tab — release appears under Releases when the job completes
```
