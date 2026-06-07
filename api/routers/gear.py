from __future__ import annotations

import json
from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Query

from db import get_db
from models import GearSummary, GearListResponse, GearDetail, UsedByChassis, AffinityEntry, AffinityLevel

router = APIRouter(prefix="/api/v1", tags=["gear"])

_SORT_COLUMN_MAP: dict[str, str] = {
    "name": "g.ui_name",
    "tonnage": "g.tonnage",
    "cost": "g.cost",
    "damage": "g.damage",
}

_USED_BY_SQL = """
    SELECT DISTINCT c.ui_name, c.prefab_base
    FROM chassis c
    WHERE (
        EXISTS (
            SELECT 1 FROM loadout l
            JOIN variant v ON l.variant_id = v.id
            WHERE v.chassis_id = c.prefab_base
            AND l.inventory_json LIKE ?
        )
        OR EXISTS (
            SELECT 1 FROM variant vf
            WHERE vf.chassis_id = c.prefab_base
            AND vf.fixed_equipment_json LIKE ?
        )
    )
    AND c.unit_type {unit_type_cond}
    ORDER BY c.ui_name
    LIMIT 100
"""


@router.get("/gear", response_model=GearListResponse)
async def list_gear(
    q: Optional[str] = Query(default=None),
    component_type: Optional[str] = Query(default=None),
    include_types: Optional[list[str]] = Query(default=None),
    exclude_types: Optional[list[str]] = Query(default=None),
    include_categories: Optional[list[str]] = Query(default=None),
    exclude_categories: Optional[list[str]] = Query(default=None),
    include_locations: Optional[list[str]] = Query(default=None),
    exclude_locations: Optional[list[str]] = Query(default=None),
    source_mod: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=60, ge=1, le=200),
    sort: str = Query(default="name"),
    sort_dir: str = Query(default="asc"),
    db: aiosqlite.Connection = Depends(get_db),
) -> GearListResponse:
    order_col = _SORT_COLUMN_MAP.get(sort, "g.ui_name")
    order_dir = "DESC" if sort_dir.lower() == "desc" else "ASC"

    conditions: list[str] = []
    params: list = []

    if q:
        conditions.append("g.ui_name LIKE ?")
        params.append(f"%{q}%")

    if component_type:
        ct_lower = component_type.lower()
        if ct_lower == "equipment":
            conditions.append("(g.component_type IS NULL OR g.component_type != 'Weapon')")
        elif ct_lower == "weapon":
            conditions.append("g.component_type = 'Weapon'")
        elif ct_lower == "quirk":
            conditions.append("g.id LIKE 'Quirk_%'")
        else:
            conditions.append("g.component_type = ?")
            params.append(component_type)

    if include_types:
        placeholders = ",".join("?" * len(include_types))
        conditions.append(f"g.component_type IN ({placeholders})")
        params.extend(include_types)

    if exclude_types:
        placeholders = ",".join("?" * len(exclude_types))
        conditions.append(f"(g.component_type NOT IN ({placeholders}) OR g.component_type IS NULL)")
        params.extend(exclude_types)

    if include_categories:
        placeholders = ",".join("?" * len(include_categories))
        conditions.append(f"g.weapon_category IN ({placeholders})")
        params.extend(include_categories)

    if exclude_categories:
        placeholders = ",".join("?" * len(exclude_categories))
        conditions.append(f"(g.weapon_category NOT IN ({placeholders}) OR g.weapon_category IS NULL)")
        params.extend(exclude_categories)

    if include_locations:
        parts: list[str] = []
        for loc in include_locations:
            if loc == "All":
                parts.append("g.allowed_locations = 'All'")
            else:
                parts.append("g.allowed_locations LIKE ?")
                params.append(f"%{loc}%")
        conditions.append(f"({' OR '.join(parts)})")

    if exclude_locations:
        for loc in exclude_locations:
            if loc == "All":
                conditions.append("(g.allowed_locations != 'All' OR g.allowed_locations IS NULL)")
            else:
                conditions.append("(g.allowed_locations NOT LIKE ? OR g.allowed_locations IS NULL)")
                params.append(f"%{loc}%")

    if source_mod:
        conditions.append("g.source_mod = ?")
        params.append(source_mod)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    count_sql = f"SELECT COUNT(*) FROM gear g {where_clause}"
    async with db.execute(count_sql, params) as cur:
        row = await cur.fetchone()
        total: int = row[0] if row else 0

    offset = (page - 1) * page_size
    data_sql = f"""
        SELECT g.id, g.ui_name, g.component_type, g.weapon_category,
               g.tonnage, g.slots, g.cost, g.damage, g.heat_generated,
               g.manufacturer, g.source_mod
        FROM gear g
        {where_clause}
        ORDER BY {order_col} {order_dir}
        LIMIT ? OFFSET ?
    """
    async with db.execute(data_sql, params + [page_size, offset]) as cur:
        rows = await cur.fetchall()

    results = [
        GearSummary(
            id=r["id"],
            ui_name=r["ui_name"],
            component_type=r["component_type"],
            weapon_category=r["weapon_category"],
            tonnage=r["tonnage"],
            slots=r["slots"],
            cost=r["cost"],
            damage=r["damage"],
            heat_generated=r["heat_generated"],
            manufacturer=r["manufacturer"],
            source_mod=r["source_mod"],
        )
        for r in rows
    ]

    return GearListResponse(total=total, page=page, page_size=page_size, results=results)


@router.get("/gear/{gear_id}", response_model=GearDetail)
async def get_gear(
    gear_id: str,
    db: aiosqlite.Connection = Depends(get_db),
) -> GearDetail:
    async with db.execute("SELECT * FROM gear WHERE id = ?", (gear_id,)) as cur:
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Gear not found")

    pattern = f'%"ComponentDefID": "{gear_id}"%'

    async with db.execute(
        _USED_BY_SQL.format(unit_type_cond="= 'mech'"),
        (pattern, pattern),
    ) as cur:
        mech_rows = await cur.fetchall()

    async with db.execute(
        _USED_BY_SQL.format(unit_type_cond="IN ('vehicle', 'vtol')"),
        (pattern, pattern),
    ) as cur:
        vehicle_rows = await cur.fetchall()

    try:
        component_tags = json.loads(row["component_tags"] or "[]")
    except (json.JSONDecodeError, TypeError):
        component_tags = []

    # For quirk items, fetch affinities that reference this quirk ID
    related_affinities: list[AffinityEntry] = []
    if gear_id.startswith("Quirk_"):
        aff_pattern = f'%"{gear_id}"%'
        async with db.execute(
            "SELECT id, levels_json FROM affinity WHERE quirk_names LIKE ?",
            (aff_pattern,),
        ) as cur:
            aff_rows = await cur.fetchall()
        for arow in aff_rows:
            try:
                raw_levels = json.loads(arow["levels_json"] or "[]")
            except (json.JSONDecodeError, TypeError):
                raw_levels = []
            levels = [
                AffinityLevel(
                    missions_required=lv.get("missions_required", 0),
                    level_name=lv.get("level_name", ""),
                    description=lv.get("description", ""),
                )
                for lv in raw_levels
            ]
            if levels:
                related_affinities.append(
                    AffinityEntry(id=arow["id"], affinity_type="Quirk", quirk_name=gear_id, levels=levels)
                )

    return GearDetail(
        id=row["id"],
        ui_name=row["ui_name"],
        details=row["details"],
        component_type=row["component_type"],
        component_subtype=row["component_subtype"],
        weapon_category=row["weapon_category"],
        tonnage=row["tonnage"],
        slots=row["slots"],
        cost=row["cost"],
        rarity=row["rarity"],
        purchasable=bool(row["purchasable"]),
        manufacturer=row["manufacturer"],
        model=row["model"],
        bonus_value_a=row["bonus_value_a"],
        bonus_value_b=row["bonus_value_b"],
        allowed_locations=row["allowed_locations"],
        disallowed_locations=row["disallowed_locations"],
        component_tags=component_tags if isinstance(component_tags, list) else [],
        damage=row["damage"],
        heat_generated=row["heat_generated"],
        min_range=row["min_range"],
        max_range=row["max_range"],
        ammo_category=row["ammo_category"],
        shots_when_fired=row["shots_when_fired"],
        battle_value=row["battle_value"],
        source_mod=row["source_mod"],
        used_by_mechs=[UsedByChassis(prefab_base=r["prefab_base"], ui_name=r["ui_name"]) for r in mech_rows],
        used_by_vehicles=[UsedByChassis(prefab_base=r["prefab_base"], ui_name=r["ui_name"]) for r in vehicle_rows],
        related_affinities=related_affinities,
    )
