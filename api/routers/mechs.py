from __future__ import annotations

import json
from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Query

from db import get_db
from models import (
    ChassisSummary,
    ChassisListResponse,
    ChassisDetail,
    VariantDetail,
    VariantLocation,
    Hardpoint,
    LoadoutLocation,
    InventoryItem,
    EquipmentItem,
    StatsResponse,
    AffinityEntry,
    AffinityLevel,
)

router = APIRouter(prefix="/api/v1", tags=["mechs"])

# ---------------------------------------------------------------------------
# Sort whitelist
# ---------------------------------------------------------------------------
_SORT_COLUMN_MAP: dict[str, str] = {
    "name": "c.ui_name",
    "tonnage": "c.tonnage",
}
_SORT_DIR_ALLOWED = {"asc", "desc"}

# ---------------------------------------------------------------------------
# WeaponMountID → hardpoint category letter
# ---------------------------------------------------------------------------
_MOUNT_CATEGORY: dict[str, str] = {
    "Ballistic": "B",
    "Energy": "E",
    "Missile": "M",
    "Special": "S",
    "WingMountedWeapon": "WM",
    "InternalBombBay": "IB",
}
_IGNORED_MOUNTS = {"AntiPersonnel", "BattleArmor", "SpecialHandHeld", ""}


def _compute_hardpoints_summary(locations_json: Optional[str], max_jumpjets: Optional[int]) -> str:
    counts: dict[str, int] = {}
    has_handheld = False
    if locations_json:
        try:
            locs = json.loads(locations_json)
        except (json.JSONDecodeError, TypeError):
            locs = []
        for loc in locs:
            for hp in loc.get("Hardpoints", []):
                mid = hp.get("WeaponMountID", "")
                if mid == "SpecialHandHeld":
                    has_handheld = True
                elif mid in _IGNORED_MOUNTS:
                    continue
                else:
                    cat = _MOUNT_CATEGORY.get(mid, mid)
                    counts[cat] = counts.get(cat, 0) + 1

    parts = []
    for cat in ["B", "E", "M", "S", "WM", "IB"]:
        if counts.get(cat):
            parts.append(f"{counts[cat]}{cat}")
    if has_handheld:
        parts.append("SH")
    jj = max_jumpjets or 0
    if jj:
        parts.append(f"{jj}JJ")
    return " ".join(parts) if parts else "—"


def _compute_health_summary(
    variant_locations: Optional[str],
    loadout_locations: Optional[str],
) -> str:
    max_armor = 0
    total_structure = 0
    if variant_locations:
        try:
            locs = json.loads(variant_locations)
        except (json.JSONDecodeError, TypeError):
            locs = []
        for loc in locs:
            max_armor += int(loc.get("MaxArmor", 0))
            rear = int(loc.get("MaxRearArmor", -1))
            if rear >= 0:
                max_armor += rear
            total_structure += float(loc.get("InternalStructure", 0))

    current_armor = 0
    if loadout_locations:
        try:
            locs = json.loads(loadout_locations)
        except (json.JSONDecodeError, TypeError):
            locs = []
        for loc in locs:
            current_armor += int(loc.get("CurrentArmor", 0))
            current_armor += int(loc.get("CurrentRearArmor", 0))

    s = int(total_structure)
    if max_armor == 0 and s == 0:
        return "—"
    return f"A={current_armor}/{max_armor} S={s}"


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_variant_locations(raw: Optional[str]) -> list[VariantLocation]:
    if not raw:
        return []
    try:
        items = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    result = []
    for item in items:
        hardpoints = [
            Hardpoint(
                weapon_mount_id=hp.get("WeaponMountID", ""),
                omni=bool(hp.get("Omni", False)),
            )
            for hp in item.get("Hardpoints", [])
        ]
        result.append(
            VariantLocation(
                location=item.get("Location", ""),
                hardpoints=hardpoints,
                max_armor=int(item.get("MaxArmor", 0)),
                max_rear_armor=int(item.get("MaxRearArmor", -1)),
                internal_structure=float(item.get("InternalStructure", 0)),
                inventory_slots=int(item.get("InventorySlots", 0)),
            )
        )
    return result


def _parse_loadout_locations(raw: Optional[str]) -> list[LoadoutLocation]:
    if not raw:
        return []
    try:
        items = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    return [
        LoadoutLocation(
            location=item.get("Location", ""),
            current_armor=int(item.get("CurrentArmor", 0)),
            current_rear_armor=int(item.get("CurrentRearArmor", 0)),
            current_internal_structure=float(item.get("CurrentInternalStructure", 0)),
        )
        for item in items
    ]


def _parse_inventory(raw: Optional[str]) -> list[InventoryItem]:
    if not raw:
        return []
    try:
        items = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    return [
        InventoryItem(
            mounted_location=item.get("MountedLocation", ""),
            component_def_id=item.get("ComponentDefID", ""),
            component_def_type=item.get("ComponentDefType", ""),
            hardpoint_slot=int(item.get("HardpointSlot", 0)),
            weapon_category=item.get("weapon_category"),
        )
        for item in items
    ]


def _parse_equipment(raw: Optional[str]) -> list[EquipmentItem]:
    if not raw:
        return []
    try:
        items = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    return [
        EquipmentItem(
            mounted_location=item.get("MountedLocation", ""),
            component_def_id=item.get("ComponentDefID", ""),
            component_def_type=item.get("ComponentDefType", ""),
            hardpoint_slot=int(item.get("HardpointSlot", 0)),
            weapon_category=item.get("weapon_category"),
        )
        for item in items
    ]


def _split_csv(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    return [t.strip() for t in raw.split(",") if t.strip()]


def _parse_json_list(raw: Optional[str]) -> list:
    if not raw:
        return []
    try:
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def _extract_quirk_ids(fixed_equipment_json: Optional[str]) -> list[str]:
    """Return ComponentDefIDs from fixed equipment that start with 'Quirk_'."""
    items = _parse_json_list(fixed_equipment_json)
    return [
        item.get("ComponentDefID", "")
        for item in items
        if isinstance(item, dict) and item.get("ComponentDefID", "").startswith("Quirk_")
    ]


def _parse_affinity_levels(raw: Optional[str]) -> list[AffinityLevel]:
    try:
        items = json.loads(raw or "[]")
    except (json.JSONDecodeError, TypeError):
        return []
    return [
        AffinityLevel(
            missions_required=lv.get("missions_required", 0),
            level_name=lv.get("level_name", ""),
            description=lv.get("description", ""),
        )
        for lv in items
    ]


def _build_affinity_context(
    affinity_rows: list,
    chassis_prefab: str,
) -> tuple[list[AffinityEntry], dict[str, list[AffinityEntry]]]:
    """Return (chassis_level_affinities, quirk_map).

    chassis_level_affinities: Global + Chassis entries pre-matched to this chassis.
      Same across all variants — include for every variant.
    quirk_map: quirk_id → [AffinityEntry] for per-variant Quirk matching.
    """
    chassis_affinities: list[AffinityEntry] = []
    quirk_map: dict[str, list[AffinityEntry]] = {}

    for arow in affinity_rows:
        aff_type = arow["affinity_type"] or ""
        levels = _parse_affinity_levels(arow["levels_json"])
        if not levels:
            continue

        if aff_type == "Global":
            chassis_affinities.append(
                AffinityEntry(id=arow["id"], affinity_type="Global", quirk_name="", levels=levels)
            )

        elif aff_type == "Chassis":
            try:
                chassis_names: list[str] = json.loads(arow["chassis_names"] or "[]")
            except (json.JSONDecodeError, TypeError):
                chassis_names = []
            if chassis_prefab in [c.lower() for c in chassis_names]:
                chassis_affinities.append(
                    AffinityEntry(id=arow["id"], affinity_type="Chassis", quirk_name="", levels=levels)
                )

        elif aff_type == "Quirk":
            try:
                quirk_names: list[str] = json.loads(arow["quirk_names"] or "[]")
            except (json.JSONDecodeError, TypeError):
                quirk_names = []
            for qname in quirk_names:
                entry = AffinityEntry(id=arow["id"], affinity_type="Quirk", quirk_name=qname, levels=levels)
                quirk_map.setdefault(qname, []).append(entry)

    return chassis_affinities, quirk_map


def _build_variant_detail(
    vrow: aiosqlite.Row,
    lrow: Optional[aiosqlite.Row],
    chassis_affinities: Optional[list[AffinityEntry]] = None,
    quirk_map: Optional[dict[str, list[AffinityEntry]]] = None,
) -> VariantDetail:
    loadout_id = lrow["id"] if lrow else None
    era_tags = _split_csv(lrow["era_tags"] if lrow else None)
    faction_tags = _split_csv(lrow["faction_tags"] if lrow else None)
    loadout_locations = _parse_loadout_locations(lrow["locations_json"] if lrow else None)
    inventory = _parse_inventory(lrow["inventory_json"] if lrow else None)
    spawn_tags = _parse_json_list(lrow["required_to_spawn_tags"] if lrow else None)

    hardpoints_summary = _compute_hardpoints_summary(
        vrow["locations_json"], vrow["max_jumpjets"]
    )
    health_summary = _compute_health_summary(
        vrow["locations_json"],
        lrow["locations_json"] if lrow else None,
    )

    # Build per-variant affinity list: global+chassis (pre-matched) + quirk-matched
    affinities: list[AffinityEntry] = list(chassis_affinities or [])
    seen: set[str] = {e.id for e in affinities}
    if quirk_map:
        for qid in _extract_quirk_ids(vrow["fixed_equipment_json"]):
            for entry in quirk_map.get(qid, []):
                if entry.id not in seen:
                    affinities.append(entry)
                    seen.add(entry.id)

    return VariantDetail(
        id=vrow["id"],
        variant_name=vrow["variant_name"],
        details=vrow["details"],
        unit_type=vrow["unit_type"],
        weight_class=vrow["weight_class"],
        tonnage=vrow["tonnage"],
        top_speed=vrow["top_speed"],
        max_jumpjets=vrow["max_jumpjets"],
        drop_cost_modifier=vrow["drop_cost_modifier"],
        chassis_tags=_parse_json_list(vrow["chassis_tags"]),
        locations=_parse_variant_locations(vrow["locations_json"]),
        fixed_equipment=_parse_equipment(vrow["fixed_equipment_json"]),
        chassis_defaults=_parse_json_list(vrow["chassis_defaults_json"]),
        multi_defaults=_parse_json_list(vrow["multi_defaults_json"]),
        lootable_unique_mech=bool(vrow["lootable_unique_mech"]),
        source_mod=vrow["source_mod"],
        hardpoints_summary=hardpoints_summary,
        loadout_id=loadout_id,
        era_tags=era_tags,
        faction_tags=faction_tags,
        loadout_locations=loadout_locations,
        inventory=inventory,
        required_to_spawn_tags=spawn_tags,
        health_summary=health_summary,
        affinities=affinities,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/meta/stats
# ---------------------------------------------------------------------------

@router.get("/meta/stats", response_model=StatsResponse)
async def get_stats(db: aiosqlite.Connection = Depends(get_db)) -> StatsResponse:
    async with db.execute(
        "SELECT COUNT(*) FROM chassis WHERE unit_type = 'mech'"
    ) as cur:
        row = await cur.fetchone()
        mech_count: int = row[0] if row else 0

    async with db.execute(
        "SELECT COUNT(*) FROM chassis WHERE unit_type IN ('vehicle', 'vtol')"
    ) as cur:
        row = await cur.fetchone()
        vehicle_count: int = row[0] if row else 0

    async with db.execute(
        "SELECT COUNT(*) FROM gear WHERE component_type = 'Weapon'"
    ) as cur:
        row = await cur.fetchone()
        weapon_count: int = row[0] if row else 0

    async with db.execute(
        "SELECT COUNT(*) FROM gear WHERE component_type != 'Weapon' OR component_type IS NULL"
    ) as cur:
        row = await cur.fetchone()
        equip_count: int = row[0] if row else 0

    return StatsResponse(mechs=mech_count, vehicles=vehicle_count, weapons=weapon_count, equipment=equip_count)


# ---------------------------------------------------------------------------
# GET /api/v1/mechs  — browse (one row per true chassis)
# ---------------------------------------------------------------------------

_MECH_ENDPOINT_UNIT_TYPES = {"mech", "battle_armor"}


@router.get("/mechs", response_model=ChassisListResponse)
async def list_mechs(
    q: Optional[str] = Query(default=None),
    weight_class: Optional[list[str]] = Query(default=None),
    era: Optional[str] = Query(default=None),
    faction: Optional[str] = Query(default=None),
    mod: Optional[str] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    unit_type: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    sort: str = Query(default="name"),
    sort_dir: str = Query(default="asc"),
    db: aiosqlite.Connection = Depends(get_db),
) -> ChassisListResponse:
    order_col = _SORT_COLUMN_MAP.get(sort, "c.ui_name")
    order_dir = "DESC" if sort_dir.lower() == "desc" else "ASC"

    resolved_unit_type = unit_type if unit_type in _MECH_ENDPOINT_UNIT_TYPES else "mech"
    conditions: list[str] = [f"c.unit_type = '{resolved_unit_type}'"]
    params: list = []

    if q:
        conditions.append("(c.ui_name LIKE ? OR v.variant_name LIKE ?)")
        params.append(f"%{q}%")
        params.append(f"%{q}%")

    if weight_class:
        placeholders = ",".join("?" * len(weight_class))
        conditions.append(f"c.weight_class IN ({placeholders})")
        params.extend(weight_class)

    if era:
        conditions.append(
            "c.prefab_base IN (SELECT DISTINCT chassis_id FROM loadout WHERE era_tags LIKE ?)"
        )
        params.append(f"%{era}%")

    if faction:
        conditions.append(
            "c.prefab_base IN (SELECT DISTINCT chassis_id FROM loadout WHERE faction_tags LIKE ?)"
        )
        params.append(f"%{faction}%")

    if mod:
        conditions.append("v.source_mod = ?")
        params.append(mod)

    if tag:
        conditions.append("v.chassis_tags LIKE ?")
        params.append(f'%"{tag}"%')

    where_clause = " AND ".join(conditions)

    count_sql = f"""
        SELECT COUNT(*)
        FROM variant v
        JOIN chassis c ON c.prefab_base = v.chassis_id
        WHERE {where_clause}
    """
    async with db.execute(count_sql, params) as cur:
        row = await cur.fetchone()
        total: int = row[0] if row else 0

    offset = (page - 1) * page_size
    data_sql = f"""
        SELECT
            v.id          AS variant_id,
            v.variant_name,
            c.prefab_base,
            c.ui_name,
            c.unit_type,
            c.weight_class,
            c.tonnage,
            c.icon
        FROM variant v
        JOIN chassis c ON c.prefab_base = v.chassis_id
        WHERE {where_clause}
        ORDER BY {order_col} {order_dir}, v.variant_name ASC
        LIMIT ? OFFSET ?
    """
    async with db.execute(data_sql, params + [page_size, offset]) as cur:
        rows = await cur.fetchall()

    results = [
        ChassisSummary(
            prefab_base=row["prefab_base"],
            ui_name=row["ui_name"],
            unit_type=row["unit_type"],
            weight_class=row["weight_class"],
            tonnage=row["tonnage"],
            icon=row["icon"],
            variant_id=row["variant_id"],
            variant_name=row["variant_name"],
        )
        for row in rows
    ]

    return ChassisListResponse(total=total, page=page, page_size=page_size, results=results)


# ---------------------------------------------------------------------------
# GET /api/v1/mechs/{prefab_base}  — chassis detail
# ---------------------------------------------------------------------------

@router.get("/mechs/{prefab_base}", response_model=ChassisDetail)
async def get_mech(
    prefab_base: str,
    db: aiosqlite.Connection = Depends(get_db),
) -> ChassisDetail:
    async with db.execute(
        "SELECT prefab_base, ui_name, unit_type, weight_class, tonnage, icon FROM chassis WHERE prefab_base = ?",
        (prefab_base,),
    ) as cur:
        chassis_row = await cur.fetchone()

    if chassis_row is None:
        raise HTTPException(status_code=404, detail="Chassis not found")

    async with db.execute(
        """
        SELECT id, variant_name, details, unit_type, weight_class, tonnage,
               movement_cap_def_id, top_speed, max_jumpjets, drop_cost_modifier,
               chassis_tags, locations_json, fixed_equipment_json,
               chassis_defaults_json, multi_defaults_json,
               lootable_unique_mech, source_mod
        FROM variant
        WHERE chassis_id = ?
        ORDER BY variant_name ASC
        """,
        (prefab_base,),
    ) as cur:
        variant_rows = await cur.fetchall()

    # Fetch all loadouts for this chassis in one query
    async with db.execute(
        """
        SELECT id, variant_id, unit_tags, era_tags, faction_tags,
               inventory_json, locations_json, required_to_spawn_tags
        FROM loadout
        WHERE chassis_id = ?
        """,
        (prefab_base,),
    ) as cur:
        loadout_rows = await cur.fetchall()

    # Map variant_id → loadout row (1:1 in practice)
    loadout_by_variant: dict[str, aiosqlite.Row] = {
        row["variant_id"]: row for row in loadout_rows
    }

    # Fetch all affinities once; resolve Global+Chassis pre-matched + quirk map for per-variant
    try:
        async with db.execute(
            "SELECT id, affinity_type, quirk_names, chassis_names, levels_json FROM affinity"
        ) as cur:
            affinity_rows = await cur.fetchall()
        chassis_affs, quirk_map = _build_affinity_context(affinity_rows, prefab_base)
    except Exception:
        chassis_affs, quirk_map = [], {}

    variants = [
        _build_variant_detail(vrow, loadout_by_variant.get(vrow["id"]), chassis_affs, quirk_map)
        for vrow in variant_rows
    ]

    return ChassisDetail(
        prefab_base=chassis_row["prefab_base"],
        ui_name=chassis_row["ui_name"],
        unit_type=chassis_row["unit_type"],
        weight_class=chassis_row["weight_class"],
        tonnage=chassis_row["tonnage"],
        icon=chassis_row["icon"],
        variants=variants,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/battle-armor/{prefab_base}  — battle armor detail
# ---------------------------------------------------------------------------

@router.get("/battle-armor/{prefab_base}", response_model=ChassisDetail)
async def get_battle_armor(
    prefab_base: str,
    db: aiosqlite.Connection = Depends(get_db),
) -> ChassisDetail:
    async with db.execute(
        "SELECT prefab_base, ui_name, unit_type, weight_class, tonnage FROM chassis WHERE prefab_base = ? AND unit_type = 'battle_armor'",
        (prefab_base,),
    ) as cur:
        chassis_row = await cur.fetchone()

    if chassis_row is None:
        raise HTTPException(status_code=404, detail="Battle armor chassis not found")

    async with db.execute(
        """
        SELECT id, variant_name, details, unit_type, weight_class, tonnage,
               movement_cap_def_id, top_speed, max_jumpjets, drop_cost_modifier,
               chassis_tags, locations_json, fixed_equipment_json,
               chassis_defaults_json, multi_defaults_json,
               lootable_unique_mech, source_mod
        FROM variant
        WHERE chassis_id = ?
        ORDER BY variant_name ASC
        """,
        (prefab_base,),
    ) as cur:
        variant_rows = await cur.fetchall()

    async with db.execute(
        """
        SELECT id, variant_id, unit_tags, era_tags, faction_tags,
               inventory_json, locations_json, required_to_spawn_tags
        FROM loadout
        WHERE chassis_id = ?
        """,
        (prefab_base,),
    ) as cur:
        loadout_rows = await cur.fetchall()

    loadout_by_variant: dict[str, aiosqlite.Row] = {
        row["variant_id"]: row for row in loadout_rows
    }

    try:
        async with db.execute(
            "SELECT id, affinity_type, quirk_names, chassis_names, levels_json FROM affinity"
        ) as cur:
            affinity_rows = await cur.fetchall()
        chassis_affs, quirk_map = _build_affinity_context(affinity_rows, prefab_base)
    except Exception:
        chassis_affs, quirk_map = [], {}

    variants = [
        _build_variant_detail(vrow, loadout_by_variant.get(vrow["id"]), chassis_affs, quirk_map)
        for vrow in variant_rows
    ]

    return ChassisDetail(
        prefab_base=chassis_row["prefab_base"],
        ui_name=chassis_row["ui_name"],
        unit_type=chassis_row["unit_type"],
        weight_class=chassis_row["weight_class"],
        tonnage=chassis_row["tonnage"],
        variants=variants,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/vehicles  — vehicle browse
# ---------------------------------------------------------------------------

@router.get("/vehicles", response_model=ChassisListResponse)
async def list_vehicles(
    q: Optional[str] = Query(default=None),
    weight_class: Optional[list[str]] = Query(default=None),
    unit_type: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    sort: str = Query(default="name"),
    sort_dir: str = Query(default="asc"),
    db: aiosqlite.Connection = Depends(get_db),
) -> ChassisListResponse:
    order_col = _SORT_COLUMN_MAP.get(sort, "c.ui_name")
    order_dir = "DESC" if sort_dir.lower() == "desc" else "ASC"

    if unit_type in ("vehicle", "vtol"):
        conditions: list[str] = [f"c.unit_type = '{unit_type}'"]
    else:
        conditions = ["c.unit_type IN ('vehicle', 'vtol')"]
    params: list = []

    if q:
        conditions.append("(c.ui_name LIKE ? OR v.variant_name LIKE ?)")
        params.append(f"%{q}%")
        params.append(f"%{q}%")

    if weight_class:
        placeholders = ",".join("?" * len(weight_class))
        conditions.append(f"c.weight_class IN ({placeholders})")
        params.extend(weight_class)

    where_clause = " AND ".join(conditions)

    count_sql = f"""
        SELECT COUNT(*)
        FROM variant v
        JOIN chassis c ON c.prefab_base = v.chassis_id
        WHERE {where_clause}
    """
    async with db.execute(count_sql, params) as cur:
        row = await cur.fetchone()
        total: int = row[0] if row else 0

    offset = (page - 1) * page_size
    data_sql = f"""
        SELECT
            v.id          AS variant_id,
            v.variant_name,
            c.prefab_base,
            c.ui_name,
            c.unit_type,
            c.weight_class,
            c.tonnage,
            c.icon
        FROM variant v
        JOIN chassis c ON c.prefab_base = v.chassis_id
        WHERE {where_clause}
        ORDER BY {order_col} {order_dir}, v.variant_name ASC
        LIMIT ? OFFSET ?
    """
    async with db.execute(data_sql, params + [page_size, offset]) as cur:
        rows = await cur.fetchall()

    results = [
        ChassisSummary(
            prefab_base=row["prefab_base"],
            ui_name=row["ui_name"],
            unit_type=row["unit_type"],
            weight_class=row["weight_class"],
            tonnage=row["tonnage"],
            icon=row["icon"],
            variant_id=row["variant_id"],
            variant_name=row["variant_name"],
        )
        for row in rows
    ]

    return ChassisListResponse(total=total, page=page, page_size=page_size, results=results)


# ---------------------------------------------------------------------------
# GET /api/v1/vehicles/{prefab_base}  — vehicle detail
# ---------------------------------------------------------------------------

@router.get("/vehicles/{prefab_base}", response_model=ChassisDetail)
async def get_vehicle(
    prefab_base: str,
    db: aiosqlite.Connection = Depends(get_db),
) -> ChassisDetail:
    async with db.execute(
        "SELECT prefab_base, ui_name, unit_type, weight_class, tonnage, icon FROM chassis WHERE prefab_base = ? AND unit_type IN ('vehicle', 'vtol')",
        (prefab_base,),
    ) as cur:
        chassis_row = await cur.fetchone()

    if chassis_row is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    async with db.execute(
        """
        SELECT id, variant_name, details, unit_type, weight_class, tonnage,
               movement_cap_def_id, top_speed, max_jumpjets, drop_cost_modifier,
               chassis_tags, locations_json, fixed_equipment_json,
               chassis_defaults_json, multi_defaults_json,
               lootable_unique_mech, source_mod
        FROM variant
        WHERE chassis_id = ?
        ORDER BY variant_name ASC
        """,
        (prefab_base,),
    ) as cur:
        variant_rows = await cur.fetchall()

    async with db.execute(
        """
        SELECT id, variant_id, unit_tags, era_tags, faction_tags,
               inventory_json, locations_json, required_to_spawn_tags
        FROM loadout WHERE chassis_id = ?
        """,
        (prefab_base,),
    ) as cur:
        loadout_rows = await cur.fetchall()

    loadout_by_variant = {row["variant_id"]: row for row in loadout_rows}

    try:
        async with db.execute(
            "SELECT id, affinity_type, quirk_names, chassis_names, levels_json FROM affinity"
        ) as cur:
            affinity_rows = await cur.fetchall()
        chassis_affs, quirk_map = _build_affinity_context(affinity_rows, prefab_base)
    except Exception:
        chassis_affs, quirk_map = [], {}

    variants = [
        _build_variant_detail(vrow, loadout_by_variant.get(vrow["id"]), chassis_affs, quirk_map)
        for vrow in variant_rows
    ]

    return ChassisDetail(
        prefab_base=chassis_row["prefab_base"],
        ui_name=chassis_row["ui_name"],
        unit_type=chassis_row["unit_type"],
        weight_class=chassis_row["weight_class"],
        tonnage=chassis_row["tonnage"],
        icon=chassis_row["icon"],
        variants=variants,
    )
