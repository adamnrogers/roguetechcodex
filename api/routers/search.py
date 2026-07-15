from __future__ import annotations

from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, Query

from db import get_db
from models import SearchHit, SearchResponse, SearchPageResponse

router = APIRouter(prefix="/api/v1", tags=["search"])

_UNIT_TYPE_TO_RESULT_TYPE: dict[str, str] = {
    "mech": "mech",
    "vehicle": "vehicle",
    "vtol": "vtol",
    "battle_armor": "battle_armor",
}

_COMPONENT_TYPE_TO_RESULT_TYPE: dict[str, str] = {
    "weapon": "weapon",
    "heatsink": "equipment",
    "jumpjet": "equipment",
    "upgrade": "equipment",
    "ammobox": "equipment",
}


def _component_result_type(component_type: Optional[str]) -> str:
    if component_type is None:
        return "equipment"
    ct = component_type.lower()
    if ct.startswith("quirk"):
        return "quirk"
    return _COMPONENT_TYPE_TO_RESULT_TYPE.get(ct, "equipment")


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(min_length=2),
    db: aiosqlite.Connection = Depends(get_db),
) -> SearchResponse:
    q_starts = f"{q}%"
    q_contains = f"%{q}%"

    chassis_hits: list[SearchHit] = []
    async with db.execute(
        """
        SELECT
            c.prefab_base, c.ui_name, c.unit_type, c.tonnage,
            (
                SELECT v2.variant_name FROM variant v2
                WHERE v2.chassis_id = c.prefab_base AND v2.variant_name LIKE ?
                ORDER BY
                    CASE WHEN LOWER(v2.variant_name) = LOWER(?) THEN 1
                         WHEN v2.variant_name LIKE ? THEN 2
                         ELSE 3 END
                LIMIT 1
            ) AS matched_variant,
            CASE
                WHEN LOWER(c.ui_name) = LOWER(?) THEN 1
                WHEN EXISTS(SELECT 1 FROM variant v3 WHERE v3.chassis_id = c.prefab_base
                            AND LOWER(v3.variant_name) = LOWER(?)) THEN 2
                WHEN c.ui_name LIKE ? THEN 3
                WHEN EXISTS(SELECT 1 FROM variant v4 WHERE v4.chassis_id = c.prefab_base
                            AND v4.variant_name LIKE ?) THEN 4
                WHEN c.ui_name LIKE ? THEN 5
                ELSE 6
            END AS rank
        FROM chassis c
        WHERE c.ui_name LIKE ?
           OR EXISTS(SELECT 1 FROM variant v5 WHERE v5.chassis_id = c.prefab_base
                     AND v5.variant_name LIKE ?)
           OR EXISTS(SELECT 1 FROM variant v6 JOIN loadout l6 ON l6.variant_id = v6.id
                     WHERE v6.chassis_id = c.prefab_base AND l6.nickname_name LIKE ?)
        ORDER BY rank, c.ui_name
        LIMIT 8
        """,
        [q_contains, q, q_starts, q, q, q_starts, q_starts, q_contains, q_contains, q_contains, q_contains],
    ) as cursor:
        async for row in cursor:
            unit_type: str = row["unit_type"] or "mech"
            tonnage = row["tonnage"]
            t = f"{int(tonnage)}t" if tonnage else ""
            ut = unit_type.replace("_", " ").title()
            base_subtitle = f"{t} · {ut}" if t else ut
            matched_variant: Optional[str] = row["matched_variant"]
            subtitle = (
                f"{matched_variant} · {base_subtitle}"
                if matched_variant
                else base_subtitle
            )
            chassis_hits.append(
                SearchHit(
                    id=row["prefab_base"],
                    name=row["ui_name"],
                    subtitle=subtitle,
                    result_type=_UNIT_TYPE_TO_RESULT_TYPE.get(unit_type, "mech"),
                )
            )

    gear_hits: list[SearchHit] = []
    async with db.execute(
        "SELECT id, ui_name, component_type FROM gear "
        "WHERE ui_name LIKE ? OR id LIKE ? ORDER BY ui_name LIMIT 8",
        [q_contains, q_contains],
    ) as cursor:
        async for row in cursor:
            ct: Optional[str] = row["component_type"]
            subtitle = ct.replace("_", " ").title() if ct else "Equipment"
            gear_hits.append(
                SearchHit(
                    id=row["id"],
                    name=row["ui_name"],
                    subtitle=subtitle,
                    result_type=_component_result_type(ct),
                )
            )

    return SearchResponse(q=q, chassis=chassis_hits, gear=gear_hits)


@router.get("/search/chassis", response_model=SearchPageResponse)
async def search_chassis(
    q: str = Query(min_length=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: aiosqlite.Connection = Depends(get_db),
) -> SearchPageResponse:
    q_starts = f"{q}%"
    q_contains = f"%{q}%"
    offset = (page - 1) * page_size

    async with db.execute(
        """
        SELECT COUNT(*)
        FROM chassis c
        JOIN variant v ON v.chassis_id = c.prefab_base
        LEFT JOIN loadout l ON l.variant_id = v.id
        WHERE c.ui_name LIKE ? OR v.variant_name LIKE ? OR l.nickname_name LIKE ?
        """,
        [q_contains, q_contains, q_contains],
    ) as cursor:
        row = await cursor.fetchone()
        total = row[0] if row else 0

    results: list[SearchHit] = []
    async with db.execute(
        """
        SELECT
            c.prefab_base, c.ui_name, c.unit_type, c.tonnage,
            v.id AS variant_id, v.variant_name, v.ui_name AS variant_ui_name,
            CASE
                WHEN LOWER(c.ui_name) = LOWER(?) THEN 1
                WHEN LOWER(v.variant_name) = LOWER(?) THEN 2
                WHEN c.ui_name LIKE ? THEN 3
                WHEN v.variant_name LIKE ? THEN 4
                WHEN c.ui_name LIKE ? THEN 5
                ELSE 6
            END AS rank
        FROM chassis c
        JOIN variant v ON v.chassis_id = c.prefab_base
        LEFT JOIN loadout l ON l.variant_id = v.id
        WHERE c.ui_name LIKE ? OR v.variant_name LIKE ? OR l.nickname_name LIKE ?
        ORDER BY rank, c.ui_name, v.variant_name
        LIMIT ? OFFSET ?
        """,
        [q, q, q_starts, q_starts, q_contains, q_contains, q_contains, q_contains, page_size, offset],
    ) as cursor:
        async for row in cursor:
            unit_type: str = row["unit_type"] or "mech"
            tonnage = row["tonnage"]
            t = f"{int(tonnage)}t" if tonnage else ""
            ut = unit_type.replace("_", " ").title()
            subtitle = f"{t} · {ut}" if t else ut
            variant_ui = row["variant_ui_name"]
            chassis_ui = row["ui_name"]
            display_name = variant_ui if (variant_ui and variant_ui != chassis_ui) else f"{chassis_ui} ({row['variant_name']})"
            results.append(
                SearchHit(
                    id=row["prefab_base"],
                    name=display_name,
                    subtitle=subtitle,
                    result_type=_UNIT_TYPE_TO_RESULT_TYPE.get(unit_type, "mech"),
                    variant_id=row["variant_id"],
                )
            )

    return SearchPageResponse(total=total, page=page, page_size=page_size, results=results)


@router.get("/search/gear", response_model=SearchPageResponse)
async def search_gear(
    q: str = Query(min_length=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: aiosqlite.Connection = Depends(get_db),
) -> SearchPageResponse:
    q_starts = f"{q}%"
    q_contains = f"%{q}%"
    offset = (page - 1) * page_size

    async with db.execute(
        "SELECT COUNT(*) FROM gear WHERE ui_name LIKE ? OR id LIKE ?",
        [q_contains, q_contains],
    ) as cursor:
        row = await cursor.fetchone()
        total = row[0] if row else 0

    results: list[SearchHit] = []
    async with db.execute(
        """
        SELECT id, ui_name, component_type,
            CASE
                WHEN LOWER(ui_name) = LOWER(?) THEN 1
                WHEN ui_name LIKE ? THEN 2
                WHEN ui_name LIKE ? THEN 3
                ELSE 4
            END AS rank
        FROM gear
        WHERE ui_name LIKE ? OR id LIKE ?
        ORDER BY rank, ui_name
        LIMIT ? OFFSET ?
        """,
        [q, q_starts, q_contains, q_contains, q_contains, page_size, offset],
    ) as cursor:
        async for row in cursor:
            ct: Optional[str] = row["component_type"]
            subtitle = ct.replace("_", " ").title() if ct else "Equipment"
            results.append(
                SearchHit(
                    id=row["id"],
                    name=row["ui_name"],
                    subtitle=subtitle,
                    result_type=_component_result_type(ct),
                )
            )

    return SearchPageResponse(total=total, page=page, page_size=page_size, results=results)
