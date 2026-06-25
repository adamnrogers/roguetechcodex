# Building Locally

Produces one release artifact:

| Artifact | Contents | Built on |
|---|---|---|
| `RogueTech-Codex-vX.Y.Z.zip` | Standalone exe + DB + frontend + portraits | Windows (PowerShell) |

Portraits are bundled inside the exe package - no separate zip needed.

---

## Prerequisites

- Docker Desktop running (for pipeline)
- Node.js 20+ (in WSL)
- Python 3.12+ (in both WSL and Windows)
- RogueTech mod installed; `RT_ROOT` set in `.env`

---

## Step 1 - Build the database

Run in WSL from the repo root:

```bash
make dev-pipeline   # ingest mod data → roguetech.db in Docker volume
make copy-db        # copy DB from volume to ./roguetech.db
```

`roguetech.db` must exist at the repo root before building the exe.

---

## Step 2 - Build portraits (WSL)

Requires `RT_ROOT` to be set in `.env`.

```bash
make portraits
```

Output: `portraits/` directory at the repo root. PyInstaller bundles this into the exe in step 4.

---

## Step 3 - Build the frontend (WSL)

```bash
cd frontend/src
npm ci
npm run build
cd ../..
```

Output: `frontend/src/dist/` - bundled into the exe in the next step.

---

## Step 4 - Build the standalone exe (PowerShell)

PyInstaller must run on Windows to produce a Windows executable.

Open PowerShell and navigate to the repo root. If the repo is in WSL, access it via:

```powershell
cd \\wsl$\Ubuntu\home\<username>\projects\RogueTech Codex
```

Install dependencies and build:

```powershell
pip install pyinstaller
pip install -r api/requirements.txt
pyinstaller standalone/roguetech.spec
```

Output: `dist\RogueTech-Codex\` - a folder containing the exe and all bundled files (including portraits in `_internal\portraits\`).

---

## Step 5 - Package the exe

In PowerShell, zip the output folder:

```powershell
$version = "v1.0.0"   # match the release tag
Compress-Archive -Path dist\RogueTech-Codex -DestinationPath "RogueTech-Codex-$version.zip"
```

---

## Step 6 - Upload to GitHub Release

One file to upload:

```
RogueTech-Codex-v1.0.0.zip
```

Either upload manually via the GitHub Releases UI, or with the `gh` CLI:

```bash
gh release upload v1.0.0 RogueTech-Codex-v1.0.0.zip
```

See `docs/github-release-setup.md` for the full release workflow.

---

## Version bump reminder

Before tagging, update the version in `frontend/src/package.json`:

```json
"version": "1.0.0"
```

This is what appears in the navbar of the built app.

---

## Quick reference

| Task | Command | Shell |
|---|---|---|
| Rebuild DB | `make dev-pipeline && make copy-db` | WSL |
| Build portraits | `make portraits` | WSL |
| Build frontend | `cd frontend/src && npm run build` | WSL |
| Build exe | `pyinstaller standalone/roguetech.spec` | PowerShell |
