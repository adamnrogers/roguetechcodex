from __future__ import annotations

import json

import aiosqlite
from db import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import StarSystemDetail, StarSystemListResponse, StarSystemSummary

router = APIRouter(prefix="/api/v1", tags=["star-systems"])

_SORT_COLUMN_MAP: dict[str, str] = {
    "name": "s.ui_name",
    "difficulty": "s.difficulty",
}


@router.get("/star-systems", response_model=StarSystemListResponse)
async def list_star_systems(
    q: str | None = Query(default=None),
    biomes: list[str] | None = Query(default=None),
    population: list[str] | None = Query(default=None),
    tags: list[str] | None = Query(default=None),
    min_difficulty: int | None = Query(default=None),
    max_difficulty: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=60, ge=1, le=200),
    sort: str = Query(default="name"),
    sort_dir: str = Query(default="asc"),
    db: aiosqlite.Connection = Depends(get_db),
) -> StarSystemListResponse:
    order_col = _SORT_COLUMN_MAP.get(sort, "s.ui_name")
    order_dir = "DESC" if sort_dir.lower() == "desc" else "ASC"

    conditions: list[str] = []
    params: list = []

    if q:
        conditions.append("s.ui_name LIKE ?")
        params.append(f"%{q}%")

    if biomes:
        parts = []
        for b in biomes:
            parts.append("s.biomes_json LIKE ?")
            params.append(f'%"{b}"%')
        conditions.append(f"({' OR '.join(parts)})")

    if population:
        placeholders = ",".join("?" * len(population))
        conditions.append(f"s.population IN ({placeholders})")
        params.extend(population)

    if tags:
        for t in tags:
            conditions.append("s.filter_tags_json LIKE ?")
            params.append(f'%"{t}"%')

    if min_difficulty is not None:
        conditions.append("s.difficulty >= ?")
        params.append(min_difficulty)

    if max_difficulty is not None:
        conditions.append("s.difficulty <= ?")
        params.append(max_difficulty)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    count_sql = f"SELECT COUNT(*) FROM star_system s {where_clause}"
    async with db.execute(count_sql, params) as cur:
        row = await cur.fetchone()
        total: int = row[0] if row else 0

    offset = (page - 1) * page_size
    data_sql = f"""
        SELECT s.id, s.ui_name, s.difficulty, s.population, s.biomes_json
        FROM star_system s
        {where_clause}
        ORDER BY {order_col} {order_dir}
        LIMIT ? OFFSET ?
    """
    async with db.execute(data_sql, params + [page_size, offset]) as cur:
        rows = await cur.fetchall()

    results = [
        StarSystemSummary(
            id=r["id"],
            ui_name=r["ui_name"],
            difficulty=r["difficulty"],
            population=r["population"],
            biomes=json.loads(r["biomes_json"] or "[]"),
        )
        for r in rows
    ]

    return StarSystemListResponse(total=total, page=page, page_size=page_size, results=results)


@router.get("/star-systems/{system_id}", response_model=StarSystemDetail)
async def get_star_system(
    system_id: str,
    db: aiosqlite.Connection = Depends(get_db),
) -> StarSystemDetail:
    async with db.execute("SELECT * FROM star_system WHERE id = ?", (system_id,)) as cur:
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Star system not found")

    try:
        biomes = json.loads(row["biomes_json"] or "[]")
    except (json.JSONDecodeError, TypeError):
        biomes = []

    try:
        tags = json.loads(row["tags_json"] or "[]")
    except (json.JSONDecodeError, TypeError):
        tags = []

    return StarSystemDetail(
        id=row["id"],
        ui_name=row["ui_name"],
        details=row["details"],
        difficulty=row["difficulty"],
        star_type=row["star_type"],
        owner_id=row["owner_id"],
        jump_distance=row["jump_distance"],
        fueling_station=bool(row["fueling_station"]),
        population=row["population"],
        size=row["size"],
        biomes=biomes,
        tags=tags,
        source_mod=row["source_mod"],
    )
