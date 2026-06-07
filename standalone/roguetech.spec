# roguetech.spec — PyInstaller build spec for standalone distribution
# Run from anywhere: pyinstaller standalone/roguetech.spec

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# SPECPATH is the directory containing this spec file (i.e. standalone/).
# ROOT is the repo root (one level up).
ROOT = os.path.dirname(SPECPATH)

uvicorn_datas = collect_data_files("uvicorn")

a = Analysis(
    [os.path.join(SPECPATH, "__main__.py")],
    pathex=[ROOT, os.path.join(ROOT, "api")],
    binaries=[],
    datas=[
        (os.path.join(ROOT, "frontend", "src", "dist"), "dist"),
        (os.path.join(ROOT, "roguetech.db"), "."),
        *uvicorn_datas,
    ],
    hiddenimports=[
        # uvicorn — dynamic imports PyInstaller cannot trace statically
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        # fastapi / starlette internals
        "starlette.routing",
        "starlette.staticfiles",
        # async SQLite driver
        "aiosqlite",
        # fast JSON
        "orjson",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "test"],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RogueTech-Codex",
    debug=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="RogueTech-Codex",
)
