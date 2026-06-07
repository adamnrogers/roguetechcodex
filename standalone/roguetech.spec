# roguetech.spec — PyInstaller build spec for standalone distribution
# Run from repo root: pyinstaller standalone/roguetech.spec

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# uvicorn ships data files (logging config, etc.) that must be bundled
uvicorn_datas = collect_data_files("uvicorn")

a = Analysis(
    ["standalone/__main__.py"],
    pathex=[".", "api"],          # "." for standalone pkg; "api" for flat imports
    binaries=[],
    datas=[
        ("frontend/src/dist", "dist"),   # pre-built Vue SPA
        ("roguetech.db", "."),           # pre-built SQLite database
        *uvicorn_datas,
    ],
    hiddenimports=[
        # uvicorn — dynamic imports that PyInstaller cannot trace statically
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
    console=True,   # keep console so users can see the startup URL and errors
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
