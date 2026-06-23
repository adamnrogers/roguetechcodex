from __future__ import annotations

import aiosqlite
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from db import get_db
from routers import mechs as mechs_router
from routers import gear as gear_router
from routers import search as search_router
from routers import star_systems as star_systems_router


app = FastAPI(
    title="RogueTech Codex API",
    version="1.0.0",
    default_response_class=ORJSONResponse,
)

# ---------------------------------------------------------------------------
# CORS — wide-open for local home-server wiki use
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(mechs_router.router)
app.include_router(gear_router.router)
app.include_router(search_router.router)
app.include_router(star_systems_router.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
async def health() -> dict:
    async for db in get_db():
        async with db.execute("SELECT COUNT(*) FROM chassis") as cursor:
            row = await cursor.fetchone()
            chassis_count: int = row[0] if row else 0

        async with db.execute("SELECT COUNT(*) FROM variant") as cursor:
            row = await cursor.fetchone()
            variant_count: int = row[0] if row else 0

    return {"status": "ok", "chassis_count": chassis_count, "variant_count": variant_count}
