from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser

# ── Path resolution ──────────────────────────────────────────────────────────
# In frozen (PyInstaller) mode, _MEIPASS contains all bundled files.
# In development, BASE_DIR is the repo root (parent of standalone/).
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS  # type: ignore[attr-defined]
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# api/ uses flat imports (e.g. `from db import get_db`), so add it to path.
sys.path.insert(0, os.path.join(BASE_DIR, "api"))

# Database path — defaults to roguetech.db alongside the exe / in MEIPASS
os.environ.setdefault("DB_PATH", os.path.join(BASE_DIR, "roguetech.db"))

# ── Deferred imports (need sys.path set first) ────────────────────────────────
import uvicorn  # noqa: E402

from standalone.server import build_app  # noqa: E402

PORT = 8765
DIST_DIR = os.path.join(BASE_DIR, "dist")


def _open_browser() -> None:
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{PORT}")


if __name__ == "__main__":
    if not os.path.isfile(os.environ["DB_PATH"]):
        sys.exit(f"Database not found: {os.environ['DB_PATH']}")

    threading.Thread(target=_open_browser, daemon=True).start()
    app = build_app(DIST_DIR)
    print(f"RogueTech Codex  →  http://localhost:{PORT}  (Ctrl+C to quit)")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
