from pathlib import Path

from fastapi.responses import FileResponse

# api/ is inserted into sys.path by __main__.py before this import runs
from main import app  # noqa: E402 — flat import, api/ on sys.path


def build_app(dist_dir: str):
    dist = Path(dist_dir).resolve()
    index = dist / "index.html"

    @app.get("/{full_path:path}")
    async def _spa(full_path: str):
        candidate = (dist / full_path).resolve()
        try:
            candidate.relative_to(dist)
        except ValueError:
            return FileResponse(str(index))
        if candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(index))

    return app
