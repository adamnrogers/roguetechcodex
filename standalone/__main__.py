from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

# ── Path resolution ──────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS  # type: ignore[attr-defined]
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(BASE_DIR, "api"))

os.environ.setdefault("DB_PATH", os.path.join(BASE_DIR, "roguetech.db"))

# ── Deferred imports ──────────────────────────────────────────────────────────
import uvicorn  # noqa: E402

from standalone.server import build_app  # noqa: E402

PORT = 8765

if getattr(sys, "frozen", False):
    DIST_DIR = os.path.join(BASE_DIR, "dist")
    PORTRAITS_DIR: Path | None = Path(sys.executable).parent / "portraits"
    if not PORTRAITS_DIR.is_dir():
        print(f"[warn] portraits directory not found: {PORTRAITS_DIR} — portrait images will not be served")
else:
    DIST_DIR = os.path.join(BASE_DIR, "frontend", "src", "dist")
    PORTRAITS_DIR = None  # dev: portraits served from dist/ via catch-all


def _open_browser() -> None:
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{PORT}")


if __name__ == "__main__":
    if not os.path.isfile(os.environ["DB_PATH"]):
        sys.exit(f"Database not found: {os.environ['DB_PATH']}")

    threading.Thread(target=_open_browser, daemon=True).start()
    app = build_app(DIST_DIR, PORTRAITS_DIR)
    print(f"RogueTech Codex  →  http://localhost:{PORT}  (Ctrl+C to quit)")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
