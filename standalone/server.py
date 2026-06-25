from __future__ import annotations

from pathlib import Path

from fastapi.responses import FileResponse, Response

from main import app  # noqa: E402 - flat import, api/ on sys.path


def build_app(dist_dir: str, portraits_dir: Path | None = None):
    dist = Path(dist_dir).resolve()
    index = dist / "index.html"

    if portraits_dir is not None:
        portraits_dir = portraits_dir.resolve()

        @app.get("/portraits/{filename}")
        async def _portrait(filename: str):
            path = (portraits_dir / filename).resolve()
            if not path.is_relative_to(portraits_dir) or not path.is_file():
                return Response(status_code=404)
            return FileResponse(str(path))

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
