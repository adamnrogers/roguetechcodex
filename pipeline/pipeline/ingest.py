"""
RogueTech Codex — data ingestion pipeline

Three-tier hierarchy:
  chassis  (PrefabBase grouping)
  variant  (one per chassisdef_*.json)
  loadout  (one per mechdef_*.json)

Two-phase load:
  Phase 1: Walk all JSON files under RT_ROOT, classify by filename prefix.
  Phase 2: Write to SQLite — chassis first, then variants, then loadouts.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────

CHASSIS_PREFIXES = ("chassisdef_",)
LOADOUT_PREFIXES = ("mechdef_",)

VEHICLE_CHASSIS_PREFIXES = ("vehiclechassisdef_",)
VEHICLE_LOADOUT_PREFIXES = ("vehicledef_",)

AFFINITY_PREFIXES = ("AffinityDef_",)

# Case-insensitive prefixes — gear files are named Gear_*.json, Weapon_*.json, etc.
# (not upgradedef_* as originally assumed)
GEAR_PREFIXES_LOWER = (
    "gear_", "weapon_", "special_", "ammo_", "ammunitionbox_",
    "heatsink_", "jumpjet_", "turret_", "unique_",
    "quirk_",   # e.g. Quirk_AccurateWeaponCategory_Ballistics.json
)

GEAR_COMPONENT_TYPES = frozenset({
    "Upgrade", "Weapon", "HeatSink", "AmmunitionBox", "JumpJet",
})

ALL_CHASSIS_PREFIXES = CHASSIS_PREFIXES + VEHICLE_CHASSIS_PREFIXES
ALL_LOADOUT_PREFIXES = LOADOUT_PREFIXES + VEHICLE_LOADOUT_PREFIXES

EXCLUDED_FRAGMENTS = ("MonsterMashup",)

SYSTEM_TAG_PREFIXES = (
    "unit_", "lance_", "pilot_", "mr-", "ai_", "tag_", "argo_",
    "apply_", "TBAS_",
)

EXCLUDED_TAGS = frozenset({"BLACKLISTED", "component_type_stock"})

# ── Helpers ───────────────────────────────────────────────────────────────────

def should_exclude(path: Path) -> bool:
    return any(frag in str(path) for frag in EXCLUDED_FRAGMENTS)


def classify(stem: str) -> str | None:
    if any(stem.startswith(p) for p in ALL_CHASSIS_PREFIXES):
        return "variant"   # chassisdef / vehiclechassisdef → variant tier
    if any(stem.startswith(p) for p in ALL_LOADOUT_PREFIXES):
        return "loadout"   # mechdef / vehicledef → loadout tier
    if any(stem.startswith(p) for p in AFFINITY_PREFIXES):
        return "affinity"
    stem_lower = stem.lower()
    if any(stem_lower.startswith(p) for p in GEAR_PREFIXES_LOWER):
        return "gear"
    return None


def detect_unit_type(data: dict) -> str:
    tags = data.get("ChassisTags", {}).get("items", [])
    tag_set = set(t.lower() for t in tags if isinstance(t, str))
    if "unit_ba" in tag_set or any("battlearmor" in t for t in tag_set):
        return "battle_armor"
    # VTOLs have ChassisTags "VTOL" and movementType "Wheeled" (not "VTOL")
    if "vtol" in tag_set:
        return "vtol"
    movement_type = (data.get("movementType") or "").lower()
    if movement_type == "vtol":
        return "vtol"
    if movement_type in ("wheeled", "tracked", "hover", "naval"):
        return "vehicle"
    return "mech"


def source_mod(path: Path, rt_root: Path) -> str:
    try:
        parts = path.relative_to(rt_root).parts
        return f"{parts[0]}/{parts[1]}" if len(parts) >= 2 else parts[0]
    except ValueError:
        return "unknown"


def chassis_key(entity_id: str, data: dict) -> str:
    """Derive the chassis group key from chassisdef data.

    Primary: Custom.AssemblyVariant.PrefabID (explicit mod author intent).
    Fallback: strip VariantName suffix from entity_id body.

    chassisdef_adder_ADR-Prime  + PrefabID "adder"  → "adder"
    chassisdef_archer_ARC-2R_Morgan + PrefabID "archer" → "archer"
    """
    prefab_id = data.get("Custom", {}).get("AssemblyVariant", {}).get("PrefabID", "")
    if prefab_id:
        return prefab_id.lower()

    prefix = "chassisdef_"
    if not entity_id.startswith(prefix):
        return entity_id
    body = entity_id[len(prefix):]
    variant_name = data.get("VariantName", "")
    if variant_name:
        suffix = f"_{variant_name}"
        if body.endswith(suffix):
            return body[: -len(suffix)]
    # Fallback: strip last underscore-delimited segment
    parts = body.rsplit("_", 1)
    return parts[0] if len(parts) > 1 else body


def vehicle_chassis_key(entity_id: str, data: dict) -> str:
    """Derive chassis group key for vehiclechassisdef files.

    Always prefixed with "v_" to avoid collisions with mech chassis that share
    the same name (e.g. mech "ajax" vs vehicle "ajax").

    Uses Custom.VAssemblyVariant.PrefabID when present:
      vehiclechassisdef_AJAX  → "v_ajax"
      vehiclechassisdef_BANDIT → "v_bandit"

    Falls back to first component of the ID body before the first [-_]:
      vehiclechassisdef_AJAX_A → "v_ajax"
      vehiclechassisdef_BANDIT-A → "v_bandit"
    """
    prefab_id = data.get("Custom", {}).get("VAssemblyVariant", {}).get("PrefabID", "")
    if prefab_id:
        return "v_" + prefab_id.lower()
    prefix = "vehiclechassisdef_"
    body = entity_id[len(prefix):]
    parts = re.split(r"[-_]", body, maxsplit=1)
    return "v_" + parts[0].lower()


def vehicle_variant_name(entity_id: str) -> str:
    """Derive variant name from vehiclechassisdef ID (no VariantName field).

    vehiclechassisdef_BANDIT   → "Prime"
    vehiclechassisdef_BANDIT-A → "A"
    vehiclechassisdef_AJAX_A   → "A"
    vehiclechassisdef_AJAX_SEALED → "SEALED"
    """
    prefix = "vehiclechassisdef_"
    body = entity_id[len(prefix):]
    parts = re.split(r"[-_]", body, maxsplit=1)
    return parts[1] if len(parts) > 1 else "Prime"


def extract_tags(items: list) -> tuple[str, str]:
    """Split tag items into (era_csv, faction_csv)."""
    era, faction = [], []
    for t in items:
        if not isinstance(t, str):
            continue
        if t in EXCLUDED_TAGS:
            continue
        if t.startswith("unit_era_"):
            era.append(t[len("unit_era_"):])
        elif not any(t.startswith(p) for p in SYSTEM_TAG_PREFIXES):
            faction.append(t)
    return ",".join(era), ",".join(faction)


def filter_chassis_tags(items: list) -> list:
    """Remove mr-resize-* noise tags."""
    return [t for t in items if isinstance(t, str) and not t.startswith("mr-resize")]


# ── Structural defaults (Cockpit, actuators, etc.) ────────────────────────────

# MechEngineer CT category IDs — used to identify chassisdef FixedEquipment items that
# are user-replaceable (ct_dynamic) and to build CT slot labels from structural defaults.
_CT_CATEGORIES = frozenset([
    "Armor", "Structure", "Cooling", "Gyro",
    "EngineShield", "EngineHeatBlock", "EngineCore",
])

# Structural default DefIDs that are internal placeholders and should not be surfaced.
_EXCLUDED_STRUCTURAL_DEF_IDS = frozenset({"Gear_EngineCore_Dummy"})

# Chassisdef FixedEquipment ComponentDefIDs that are passive markers / internal tags
# and should not appear in the component layout (they have no meaningful slot display).
_HIDDEN_FIXED_COMPONENT_IDS = frozenset({
    "Quirk_Melee_Weapon",
    "Quirk_Melee_Weapon_YLW",
    "Quirk_Melee_Samurai",
})

# ── Hardpoint pre-aggregation ─────────────────────────────────────────────────

_HP_SKIP_MOUNTS = frozenset({"AntiPersonnel", "BattleArmor", ""})
_HP_ALL_TYPES = (
    "Ballistic", "Energy", "Missile", "Special",
    "WingMountedWeapon", "InternalBombBay", "SpecialHandHeld",
)
_HP_MECH_LOCATIONS = (
    "Head", "LeftArm", "LeftTorso", "LeftLeg",
    "RightArm", "RightTorso", "RightLeg", "CenterTorso",
)


def compute_hardpoints_json(locations_raw: list) -> str:
    """Pre-aggregate hardpoint counts by location and type.

    Returns JSON: {location: {type: count, ..., "Omni": count}}
    All 8 locations and all 7 types + Omni are always present (zero-filled).
    Omni=true hardpoints are counted under "Omni", not their WeaponMountID.
    AntiPersonnel, BattleArmor, and empty mounts are skipped.
    """
    result: dict[str, dict[str, int]] = {
        loc: {t: 0 for t in _HP_ALL_TYPES} | {"Omni": 0}
        for loc in _HP_MECH_LOCATIONS
    }
    for loc_data in locations_raw:
        loc_name = loc_data.get("Location", "")
        if loc_name not in result:
            continue
        for hp in loc_data.get("Hardpoints", []):
            mount_id = hp.get("WeaponMountID", "")
            if mount_id in _HP_SKIP_MOUNTS:
                continue
            if hp.get("Omni", False):
                result[loc_name]["Omni"] += 1
            elif mount_id in result[loc_name]:
                result[loc_name][mount_id] += 1
    return json.dumps(result)


def load_mech_global_defaults(
    rt_root: Path,
) -> tuple[list[dict], dict[str, dict[str, set[str]]]]:
    """Parse Defaults_MechEngineer.json and Categories_Actuators.json.

    Returns:
        structural_categories: head + actuator default entries (CT categories excluded)
        actuator_exclusions: {category_name: {unit_type_tag: set_of_excluded_locs}}
          where 'All' in the set means all locations are excluded.
    """
    me_files = list(rt_root.rglob("Defaults_MechEngineer.json"))
    cat_files = list(rt_root.rglob("Categories_Actuators.json"))
    if not me_files or not cat_files:
        return [], {}

    try:
        me_data = json.loads(me_files[0].read_text(encoding="utf-8", errors="replace"))
        cat_data = json.loads(cat_files[0].read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return [], {}

    structural_categories: list[dict] = []
    for entry in me_data.get("Settings", []):
        cid = entry.get("CategoryID", "")
        defaults = [
            (d["Location"], d["DefID"], d.get("Type", "Upgrade"))
            for d in entry.get("Defaults", [])
            if "Location" in d and "DefID" in d
        ]
        unit_type_overrides: dict[str, list] = {}
        for ut in entry.get("UnitTypes", []):
            utype = ut.get("UnitType", "")
            overrides = [
                (d["Location"], d["DefID"], d.get("Type", "Upgrade"))
                for d in ut.get("Defaults", [])
                if "Location" in d and "DefID" in d
            ]
            if utype and overrides:
                unit_type_overrides[utype] = overrides
        if defaults:
            structural_categories.append({
                "CategoryID": cid,
                "Defaults": defaults,
                "UnitTypeOverrides": unit_type_overrides,
            })

    actuator_exclusions: dict[str, dict[str, set[str]]] = {}
    for entry in cat_data.get("Settings", []):
        name = entry.get("Name", "")
        excl: dict[str, set[str]] = {}
        for ul in entry.get("UnitLimits", []):
            utype = ul.get("UnitType", "")
            for limit in ul.get("Limits", []):
                if limit.get("Max", 1) == 0:
                    loc = limit.get("Location", "")
                    excl.setdefault(utype, set()).add(loc)  # 'All' or specific loc
        if excl:
            actuator_exclusions[name] = excl

    return structural_categories, actuator_exclusions


def build_structural_defaults(
    chassis_tags: list[str],
    unit_type: str,
    structural_categories: list[dict],
    actuator_exclusions: dict[str, dict[str, set[str]]],
    skip_ct_categories: set[str] | None = None,
) -> list[dict]:
    """Return structural default items to prepend to a mech's fixed_equipment_json.

    Only applies to mechs (not vehicles, VTOLs, or battle armor).
    Applies unit-type overrides and actuator exclusions from the two config files.
    skip_ct_categories: CT category IDs already covered by chassisdef FixedEquipment;
        slot-label defaults for those categories are omitted to avoid redundancy.
    """
    if unit_type != "mech":
        return []

    skip = skip_ct_categories or set()
    tag_set = set(chassis_tags)
    result: list[dict] = []

    for category in structural_categories:
        cid = category["CategoryID"]
        if cid in skip:
            continue
        effective = list(category["Defaults"])

        # Apply last matching unit-type override
        for utype, overrides in category["UnitTypeOverrides"].items():
            if utype in tag_set:
                effective = overrides

        # Compute excluded locations for this category
        excluded: set[str] = set()
        for utype, locs in actuator_exclusions.get(cid, {}).items():
            if utype in tag_set:
                excluded.update(locs)

        for loc, def_id, comp_type in effective:
            if def_id in _EXCLUDED_STRUCTURAL_DEF_IDS:
                continue
            if "All" not in excluded and loc not in excluded:
                result.append({
                    "MountedLocation": loc,
                    "ComponentDefID": def_id,
                    "ComponentDefType": comp_type,
                    "HardpointSlot": 0,
                })

    return result


# ── SQLite schema ─────────────────────────────────────────────────────────────

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

DROP_ALL = """
DROP TABLE IF EXISTS loadout;
DROP TABLE IF EXISTS variant;
DROP TABLE IF EXISTS chassis;
DROP TABLE IF EXISTS gear;
DROP TABLE IF EXISTS gear_usage;
DROP TABLE IF EXISTS affinity;
DROP TABLE IF EXISTS bonus_descriptions_lookup;
DROP TABLE IF EXISTS pipeline_run;
DROP TABLE IF EXISTS fts_entity;
DROP TABLE IF EXISTS variant_equipment;
DROP TABLE IF EXISTS variant_weapon;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS weapon;
"""

# ── Phase 1: scan & classify ──────────────────────────────────────────────────

def scan(rt_root: Path) -> tuple[dict, dict, dict, dict, int]:
    """Return (variant_data, loadout_data, affinity_data, gear_data, files_scanned).
    Each dict maps entity id → (parsed_dict, Path).
    Affinity files use their top-level 'id' field; gear uses Description.Id.
    """
    variant_data: dict[str, tuple[dict, Path]] = {}
    loadout_data: dict[str, tuple[dict, Path]] = {}
    affinity_data: dict[str, tuple[dict, Path]] = {}
    gear_data: dict[str, tuple[dict, Path]] = {}
    files_scanned = 0

    for path in sorted(rt_root.rglob("*.json")):
        files_scanned += 1
        if should_exclude(path):
            continue
        kind = classify(path.stem)
        if not kind:
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            continue

        if not isinstance(data, dict):
            continue

        if kind == "affinity":
            entity_id = data.get("id", "").strip()
        else:
            entity_id = data.get("Description", {}).get("Id", "").strip()

        if not entity_id:
            continue

        if kind == "variant":
            variant_data[entity_id] = (data, path)
        elif kind == "loadout":
            loadout_data[entity_id] = (data, path)
        elif kind == "affinity":
            affinity_data[entity_id] = (data, path)
        elif kind == "gear":
            gear_data[entity_id] = (data, path)

    return variant_data, loadout_data, affinity_data, gear_data, files_scanned


# ── Phase 2: write to DB ──────────────────────────────────────────────────────

def _chassis_group_key(entity_id: str, data: dict) -> str:
    """Dispatch to the correct chassis key function based on entity type."""
    if entity_id.startswith("vehiclechassisdef_"):
        return vehicle_chassis_key(entity_id, data)
    return chassis_key(entity_id, data)


def insert_chassis(con: sqlite3.Connection, variant_data: dict) -> None:
    """Derive and insert one chassis row per unique chassis_key."""
    chassis: dict[str, dict] = {}
    for entity_id, (data, path) in variant_data.items():
        key = _chassis_group_key(entity_id, data)
        if key not in chassis:
            desc = data.get("Description", {})
            v_prefab = data.get("Custom", {}).get("VAssemblyVariant", {}).get("PrefabID", "")
            ui_name = v_prefab or desc.get("UIName") or desc.get("Name") or key
            raw_icon = desc.get("Icon", "")
            chassis[key] = {
                "prefab_base": key,
                "ui_name": ui_name,
                "unit_type": detect_unit_type(data),
                "weight_class": data.get("weightClass"),
                "tonnage": data.get("Tonnage"),
                "icon": raw_icon.strip() or None,
            }

    rows = [
        (c["prefab_base"], c["ui_name"], c["unit_type"], c["weight_class"], c["tonnage"], c["icon"])
        for c in chassis.values()
    ]
    con.executemany(
        "INSERT OR IGNORE INTO chassis (prefab_base, ui_name, unit_type, weight_class, tonnage, icon) VALUES (?,?,?,?,?,?)",
        rows,
    )
    con.commit()
    print(f"  chassis rows inserted : {len(rows):,}")


def _enrich_category(items: list, cat_map: dict) -> list:
    """Inject weapon_category into each item dict where the gear_category_map has a match."""
    result = []
    for item in items:
        cid = item.get("ComponentDefID", "")
        cat = cat_map.get(cid)
        result.append({**item, "weapon_category": cat} if cat else item)
    return result


def insert_variants(
    con: sqlite3.Connection,
    variant_data: dict,
    rt_root: Path,
    gear_category_map: dict[str, str] | None = None,
    ct_category_map: dict[str, str] | None = None,  # gear_id → CT CategoryID
) -> dict[str, str]:
    """Insert one variant row per chassisdef file.
    Returns {variant_id: prefab_base} map for loadout linkage.
    """
    known_chassis = {r[0] for r in con.execute("SELECT prefab_base FROM chassis")}
    structural_categories, actuator_exclusions = load_mech_global_defaults(rt_root)
    cat_map = gear_category_map or {}
    ct_map = ct_category_map or {}  # gear_id → CT CategoryID
    rows = []
    variant_to_chassis: dict[str, str] = {}

    for entity_id, (data, path) in variant_data.items():
        prefab_base = _chassis_group_key(entity_id, data)
        if prefab_base not in known_chassis:
            continue

        is_vehicle = entity_id.startswith("vehiclechassisdef_")
        desc = data.get("Description", {})
        custom = data.get("Custom", {})

        # VariantName: explicit field for mechs, derived from UIName for vehicles
        ui_name = desc.get("UIName") or desc.get("Name") or entity_id
        if is_vehicle:
            # UIName "Bandit Prime" → "Prime", "Dauntless 0" → "0", "Ajax Sealed" → "Sealed"
            ui_parts = ui_name.rsplit(" ", 1)
            variant_name = ui_parts[1] if len(ui_parts) > 1 else vehicle_variant_name(entity_id)
        else:
            variant_name = data.get("VariantName") or ""

        drop_cost = custom.get("DropCostFactor", {}).get("DropModifier")
        lootable_block = custom.get("LootableUniqueMech", {}).get("BlockAssembly", False)
        chassis_defaults = custom.get("ChassisDefaults") or []
        multi_defaults = custom.get("MultiDefaults") or []
        raw_tags = data.get("ChassisTags", {}).get("items", [])
        unit_type = detect_unit_type(data)

        # Structural defaults (cockpit, life support, actuators, CT slot labels) are
        # defined globally in Defaults_MechEngineer.json, not per-chassisdef.
        # CT slot labels are skipped for categories already present in chassisdef
        # FixedEquipment to avoid showing both the label and the actual item.
        chassis_fixed_raw = [
            item for item in data.get("FixedEquipment", [])
            if item.get("ComponentDefID", "") not in _HIDDEN_FIXED_COMPONENT_IDS
        ]
        ct_categories_present = {
            ct_map[item["ComponentDefID"]]
            for item in chassis_fixed_raw
            if ct_map.get(item.get("ComponentDefID", ""))
        }
        structural = build_structural_defaults(
            raw_tags, unit_type, structural_categories, actuator_exclusions,
            skip_ct_categories=ct_categories_present,
        )
        fixed_equipment = _enrich_category(structural + chassis_fixed_raw, cat_map)

        locations_raw = data.get("Locations", [])
        hardpoints_json_val = compute_hardpoints_json(locations_raw)

        variant_to_chassis[entity_id] = prefab_base
        rows.append((
            entity_id,
            prefab_base,
            ui_name,
            variant_name,
            desc.get("Details"),
            unit_type,
            data.get("weightClass"),
            data.get("Tonnage"),
            data.get("MovementCapDefID"),
            data.get("TopSpeed"),
            data.get("MaxJumpjets"),
            drop_cost,
            json.dumps(filter_chassis_tags(raw_tags)),
            json.dumps(locations_raw),
            json.dumps(fixed_equipment),
            json.dumps(chassis_defaults),
            json.dumps(multi_defaults),
            1 if lootable_block else 0,
            data.get("movementType"),
            str(path.relative_to(rt_root)),
            source_mod(path, rt_root),
            hardpoints_json_val,
        ))

    con.executemany(
        """INSERT OR REPLACE INTO variant
           (id, chassis_id, ui_name, variant_name, details, unit_type, weight_class,
            tonnage, movement_cap_def_id, top_speed, max_jumpjets, drop_cost_modifier,
            chassis_tags, locations_json, fixed_equipment_json, chassis_defaults_json,
            multi_defaults_json, lootable_unique_mech, movement_type, source_file, source_mod,
            hardpoints_json)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    con.commit()
    print(f"  variant rows inserted : {len(rows):,}")
    return variant_to_chassis


def insert_loadouts(
    con: sqlite3.Connection,
    loadout_data: dict,
    variant_to_chassis: dict[str, str],
    rt_root: Path,
    gear_category_map: dict[str, str] | None = None,
) -> tuple[int, int]:
    """Insert one loadout row per mechdef file. Returns (inserted, skipped)."""
    known_variants = {r[0] for r in con.execute("SELECT id FROM variant")}
    cat_map = gear_category_map or {}
    rows = []
    skipped = 0

    for entity_id, (data, path) in loadout_data.items():
        variant_id = data.get("ChassisID", "").strip()
        if not variant_id or variant_id not in known_variants:
            skipped += 1
            continue

        chassis_id = variant_to_chassis.get(variant_id, "")
        tags = data.get("MechTags", data.get("VehicleTags", {})).get("items", [])
        era_tags, faction_tags = extract_tags(tags)
        spawn_tags = data.get("RequiredToSpawnCompanyTags", {})
        spawn_items = spawn_tags.get("items", []) if isinstance(spawn_tags, dict) else []

        rows.append((
            entity_id,
            variant_id,
            chassis_id,
            json.dumps(tags),
            era_tags,
            faction_tags,
            json.dumps(_enrich_category(data.get("inventory", []), cat_map)),
            json.dumps(data.get("Locations", [])),
            json.dumps(spawn_items),
            str(path.relative_to(rt_root)),
            source_mod(path, rt_root),
        ))

    con.executemany(
        """INSERT OR REPLACE INTO loadout
           (id, variant_id, chassis_id, unit_tags, era_tags, faction_tags,
            inventory_json, locations_json, required_to_spawn_tags, source_file, source_mod)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    con.commit()
    return len(rows), skipped


def _affinity_desc(container: dict) -> str:
    """Extract human-readable description from an affinity level or affinityData block."""
    desc = container.get("decription") or container.get("description") or ""
    if desc:
        return desc
    # Fall back to first effectData entry's Details text
    for eff in container.get("effectData", []):
        d = eff.get("Description", {}).get("Details", "")
        if d:
            return d
    # Fall back to formatting skill bonuses (affinities array)
    parts = []
    for a in container.get("affinities", []):
        bonus = a.get("bonus", 0)
        atype = a.get("type", "")
        if bonus and atype:
            parts.append(f"+{bonus} {atype}")
    return " | ".join(parts)


def insert_gear_usage(
    con: sqlite3.Connection,
    variant_data: dict,
    loadout_data: dict,
    variant_to_chassis: dict[str, str],
) -> int:
    """Populate gear_usage junction table for fast gear→chassis reverse lookups."""
    pairs: set[tuple[str, str]] = set()

    for entity_id, (data, _path) in variant_data.items():
        chassis_id = variant_to_chassis.get(entity_id, "")
        if not chassis_id:
            continue
        for item in data.get("FixedEquipment", []):
            gid = item.get("ComponentDefID", "")
            if gid:
                pairs.add((gid, chassis_id))

    for _entity_id, (data, _path) in loadout_data.items():
        variant_id = data.get("ChassisID", "").strip()
        chassis_id = variant_to_chassis.get(variant_id, "")
        if not chassis_id:
            continue
        for item in data.get("inventory", []):
            gid = item.get("ComponentDefID", "")
            if gid:
                pairs.add((gid, chassis_id))

    con.executemany(
        "INSERT OR IGNORE INTO gear_usage(gear_id, chassis_id) VALUES (?,?)",
        pairs,
    )
    con.commit()
    return len(pairs)


def insert_affinities(con: sqlite3.Connection, affinity_data: dict) -> int:
    """Insert one affinity row per AffinityDef file."""
    rows = []
    for entity_id, (data, path) in affinity_data.items():
        aff_type = data.get("affinityType", "")
        aff_data = data.get("affinityData", {})

        if aff_type == "Global":
            # Single level defined directly in affinityData (no affinityLevels array)
            levels = [{
                "missions_required": aff_data.get("missionsRequired", 0),
                "level_name": aff_data.get("levelName", ""),
                "description": _affinity_desc(aff_data),
            }]
            quirk_names: list = []
            chassis_names: list = []
        else:
            # Quirk, Chassis, Tag types use affinityLevels array
            levels = []
            for lv in aff_data.get("affinityLevels", []):
                levels.append({
                    "missions_required": lv.get("missionsRequired", 0),
                    "level_name": lv.get("levelName", ""),
                    "description": _affinity_desc(lv),
                })
            quirk_names = aff_data.get("quirkNames", [])
            # Chassis type: primary chassisNames are AssemblyVariant IDs with a tonnage suffix
            # (e.g. "annihilatoriic_100"). Strip the trailing _NNN and lowercase to match
            # our chassis.prefab_base values.
            chassis_names = []
            if aff_type == "Chassis":
                chassis_names = [
                    re.sub(r"_\d+$", "", n).lower()
                    for n in aff_data.get("chassisNames", [])
                ]

        rows.append((
            entity_id,
            aff_type,
            json.dumps(quirk_names),
            json.dumps(chassis_names),
            json.dumps(levels),
        ))
    con.executemany(
        "INSERT OR REPLACE INTO affinity (id, affinity_type, quirk_names, chassis_names, levels_json) VALUES (?,?,?,?,?)",
        rows,
    )
    con.commit()
    print(f"  affinity rows inserted : {len(rows):,}")
    return len(rows)


def ingest_bonus_descriptions(con: sqlite3.Connection, rt_root: Path) -> int:
    """Walk all BonusDescriptions_*.json files and populate bonus_descriptions_lookup."""
    rows: list[tuple] = []
    for path in sorted(rt_root.rglob("BonusDescriptions_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            continue
        for entry in data.get("Settings", []):
            key = entry.get("Bonus", "").strip()
            if not key:
                continue
            rows.append((
                key,
                entry.get("Short", ""),
                entry.get("Long", ""),
                entry.get("Full", ""),
            ))
    con.executemany(
        "INSERT OR REPLACE INTO bonus_descriptions_lookup (key, short, long, full) VALUES (?,?,?,?)",
        rows,
    )
    con.commit()
    print(f"  bonus_descriptions entries : {len(rows):,}")
    return len(rows)


def _resolve_bonus_param(template: str, params: list[str]) -> str:
    """Substitute {0}, {1}, ... placeholders in a template string."""
    result = template
    for i, p in enumerate(params):
        result = result.replace(f"{{{i}}}", p.strip())
    return result


def resolve_bonus_descriptions(raw_list: list, lookup: dict[str, tuple]) -> list[str]:
    """Resolve a BonusDescriptions array to human-readable Full strings.

    lookup: {key: (short, long, full)} from bonus_descriptions_lookup.
    Falls back to the raw string if no mapping found.
    """
    results: list[str] = []
    for raw in raw_list:
        if not isinstance(raw, str):
            continue
        raw = raw.strip()
        if not raw:
            continue
        # Split "KeyName: param1/param2" → key + params
        if ":" in raw:
            key, params_str = raw.split(":", 1)
            key = key.strip()
            params = [p.strip() for p in params_str.strip().replace(",", "/").split("/") if p.strip()]
        else:
            key = raw
            params = []
        entry = lookup.get(key)
        if entry:
            _short, _long, full = entry
            resolved = _resolve_bonus_param(full, params) if full else (_resolve_bonus_param(_long, params) or raw)
            results.append(resolved.strip())
        else:
            results.append(raw)
    return results


def compute_modes(weapon_data: dict) -> list[dict]:
    """Compute effective per-mode stats by merging base weapon stats with mode overrides.

    Range fields in mode objects are DELTAS added to the base range values.
    All other fields are ABSOLUTE overrides when present.
    Returns a list of mode dicts ready for JSON storage.
    """
    base_min = weapon_data.get("MinRange") or 0
    base_short = (weapon_data.get("RangeSplit") or [0])[0] if weapon_data.get("RangeSplit") else 0
    base_medium = (weapon_data.get("RangeSplit") or [0, 0])[1] if len(weapon_data.get("RangeSplit") or []) > 1 else base_short
    base_long = (weapon_data.get("RangeSplit") or [0, 0, 0])[2] if len(weapon_data.get("RangeSplit") or []) > 2 else base_medium
    base_max = weapon_data.get("MaxRange") or 0

    base = {
        "damage": weapon_data.get("Damage"),
        "heat_generated": weapon_data.get("HeatGenerated"),
        "instability": weapon_data.get("Instability"),
        "heat_damage": weapon_data.get("HeatDamage"),
        "accuracy_modifier": weapon_data.get("AccuracyModifier"),
        "evasion_pips_ignored": weapon_data.get("EvasivePipsIgnored"),
        "attack_recoil": weapon_data.get("AttackRecoil"),
        "shots_when_fired": weapon_data.get("ShotsWhenFired"),
        "projectiles_per_shot": weapon_data.get("ProjectilesPerShot"),
        "crit_chance_mult": weapon_data.get("CriticalChanceMultiplier"),
        "ap_shards_mod": weapon_data.get("APArmorShardsMod"),
        "ap_crit_chance_mult": weapon_data.get("APCriticalChanceMultiplier"),
        "ammo_category": weapon_data.get("AmmoCategory"),
        "indirect_fire_capable": weapon_data.get("IndirectFireCapable", False),
        "min_range": base_min,
        "range_short": base_short,
        "range_medium": base_medium,
        "range_long": base_long,
        "max_range": base_max,
    }

    modes_raw = weapon_data.get("Modes", [])
    if not modes_raw:
        # No modes — return a single synthetic base entry
        return [{
            "mode_id": "base",
            "mode_ui_name": "Base",
            "mode_description": "",
            "is_base_mode": True,
            **base,
        }]

    result = []
    for mode in modes_raw:
        if not isinstance(mode, dict):
            continue
        m: dict = {
            "mode_id": mode.get("Id", ""),
            "mode_ui_name": mode.get("UIName", ""),
            "mode_description": mode.get("Description", ""),
            "is_base_mode": bool(mode.get("isBaseMode", False)),
        }
        # Numeric fields: mode values are deltas added on top of base
        for src, dst in [
            ("DamagePerShot",             "damage"),
            ("HeatGenerated",             "heat_generated"),
            ("Instability",               "instability"),
            ("HeatDamage",                "heat_damage"),
            ("AccuracyModifier",          "accuracy_modifier"),
            ("EvasivePipsIgnored",        "evasion_pips_ignored"),
            ("AttackRecoil",              "attack_recoil"),
            ("ShotsWhenFired",            "shots_when_fired"),
            ("ProjectilesPerShot",        "projectiles_per_shot"),
            ("CriticalChanceMultiplier",  "crit_chance_mult"),
            ("APArmorShardsMod",          "ap_shards_mod"),
            ("APCriticalChanceMultiplier","ap_crit_chance_mult"),
        ]:
            if src in mode:
                m[dst] = (base[dst] or 0) + mode[src]
            else:
                m[dst] = base[dst]
        # Non-numeric fields: absolute override when present
        for src, dst in [
            ("AmmoCategory",       "ammo_category"),
            ("IndirectFireCapable","indirect_fire_capable"),
        ]:
            m[dst] = mode[src] if src in mode else base[dst]
        # Range deltas
        m["min_range"] = base_min + (mode.get("MinRange") or 0)
        m["range_short"] = base_short + (mode.get("ShortRange") or 0)
        m["range_medium"] = base_medium + (mode.get("MediumRange") or 0)
        m["range_long"] = base_long + (mode.get("LongRange") or 0)
        m["max_range"] = base_max + (mode.get("MaxRange") or 0)
        result.append(m)

    return result


def insert_gear(con: sqlite3.Connection, gear_data: dict, rt_root: Path) -> int:
    """Insert one gear row per upgradedef_*.json or weapondef_*.json file."""
    GEAR_EXCLUDED_TAGS = frozenset({"BLACKLISTED"})

    # Build in-memory lookup from bonus_descriptions_lookup table
    bd_lookup: dict[str, tuple] = {}
    for row in con.execute("SELECT key, short, long, full FROM bonus_descriptions_lookup"):
        bd_lookup[row[0]] = (row[1], row[2], row[3])

    rows = []
    for entity_id, (data, path) in gear_data.items():
        if should_exclude(path):
            continue
        if entity_id.startswith("Weapon_MeleeAttackEx"):
            continue
        ct = data.get("ComponentType")
        if ct not in GEAR_COMPONENT_TYPES:
            continue  # skip non-gear files that matched a gear prefix (e.g. turret AI files)
        tags = data.get("ComponentTags", {}).get("items", [])
        if any(t in GEAR_EXCLUDED_TAGS for t in tags if isinstance(t, str)):
            continue
        raw_bonus_descs = data.get("Custom", {}).get("BonusDescriptions", [])
        if "ROI" in raw_bonus_descs:
            continue
        desc = data.get("Description", {})
        is_weapon = ct == "Weapon"

        resolved_bonus = resolve_bonus_descriptions(raw_bonus_descs, bd_lookup) if raw_bonus_descs else []
        modes = compute_modes(data) if is_weapon else []

        custom_categories = data.get("Custom", {}).get("Category", [])
        weapon_category_id: str | None = None
        if isinstance(custom_categories, list):
            for cat in custom_categories:
                if isinstance(cat, dict):
                    cid = cat.get("CategoryID", "")
                    if isinstance(cid, str) and (cid.startswith("w/") or cid.startswith("LAM")):
                        weapon_category_id = cid
                        break

        rows.append((
            entity_id,
            desc.get("UIName") or desc.get("Name") or entity_id,
            desc.get("Details"),
            data.get("ComponentType"),
            data.get("ComponentSubType"),
            data.get("Tonnage"),
            data.get("InventorySize"),
            desc.get("Cost"),
            desc.get("Rarity"),
            1 if desc.get("Purchasable", True) else 0,
            desc.get("Manufacturer"),
            desc.get("Model"),
            data.get("BonusValueA"),
            data.get("BonusValueB"),
            data.get("AllowedLocations"),
            data.get("DisallowedLocations"),
            json.dumps([t for t in tags if isinstance(t, str)]),
            # Weapon-specific fields (None for non-weapons)
            data.get("Category"),
            data.get("Type") if is_weapon else None,
            data.get("WeaponSubType") if is_weapon else None,
            data.get("Damage"),
            data.get("HeatGenerated"),
            data.get("MinRange"),
            data.get("MaxRange"),
            data.get("AmmoCategory"),
            data.get("ShotsWhenFired"),
            data.get("BattleValue"),
            # Extended weapon stats
            data.get("Instability") if is_weapon else None,
            data.get("HeatDamage") if is_weapon else None,
            data.get("AccuracyModifier") if is_weapon else None,
            data.get("EvasivePipsIgnored") if is_weapon else None,
            data.get("AttackRecoil") if is_weapon else None,
            data.get("ProjectilesPerShot") if is_weapon else None,
            data.get("CriticalChanceMultiplier") if is_weapon else None,
            data.get("APArmorShardsMod") if is_weapon else None,
            data.get("APCriticalChanceMultiplier") if is_weapon else None,
            (data.get("RangeSplit") or [None])[0] if is_weapon else None,
            (data.get("RangeSplit") or [None, None])[1] if is_weapon and len(data.get("RangeSplit") or []) > 1 else None,
            (data.get("RangeSplit") or [None, None, None])[2] if is_weapon and len(data.get("RangeSplit") or []) > 2 else None,
            1 if (is_weapon and data.get("IndirectFireCapable")) else (0 if is_weapon else None),
            json.dumps(resolved_bonus) if resolved_bonus else None,
            json.dumps(modes) if modes else None,
            str(path.relative_to(rt_root)),
            source_mod(path, rt_root),
            weapon_category_id,
        ))
    con.executemany(
        """INSERT OR REPLACE INTO gear
           (id, ui_name, details, component_type, component_subtype, tonnage, slots,
            cost, rarity, purchasable, manufacturer, model, bonus_value_a, bonus_value_b,
            allowed_locations, disallowed_locations, component_tags,
            weapon_category, weapon_type, weapon_subtype, damage, heat_generated, min_range, max_range,
            ammo_category, shots_when_fired, battle_value,
            instability, heat_damage, accuracy_modifier, evasion_pips_ignored,
            attack_recoil, projectiles_per_shot, crit_chance_mult,
            ap_shards_mod, ap_crit_chance_mult,
            range_short, range_medium, range_long, indirect_fire_capable,
            bonus_descriptions, modes_json,
            source_file, source_mod, weapon_category_id)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    con.commit()
    print(f"  gear rows inserted     : {len(rows):,}")
    return len(rows)


# ── Entry point ───────────────────────────────────────────────────────────────

def run(rt_root: Path, db_path: Path, full_rebuild: bool) -> None:
    t0 = time.monotonic()
    print(f"RT_ROOT  : {rt_root}")
    print(f"DB_PATH  : {db_path}")
    print(f"Mode     : {'full rebuild' if full_rebuild else 'incremental (stub)'}")
    print()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode = DELETE")
    con.execute("PRAGMA foreign_keys = ON")

    if full_rebuild:
        print("Dropping existing tables...")
        con.executescript(DROP_ALL)

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    con.executescript(schema_sql)

    print("Phase 1 — scanning JSON files...")
    variant_data, loadout_data, affinity_data, gear_data, files_scanned = scan(rt_root)
    mech_variants = sum(1 for k in variant_data if k.startswith("chassisdef_"))
    vehicle_variants = sum(1 for k in variant_data if k.startswith("vehiclechassisdef_"))
    mech_loadouts = sum(1 for k in loadout_data if k.startswith("mechdef_"))
    vehicle_loadouts = sum(1 for k in loadout_data if k.startswith("vehicledef_"))
    print(f"  chassisdef files        : {mech_variants:,}")
    print(f"  vehiclechassisdef files : {vehicle_variants:,}")
    print(f"  mechdef files           : {mech_loadouts:,}")
    print(f"  vehicledef files        : {vehicle_loadouts:,}")
    print(f"  affinity files          : {len(affinity_data):,}")
    print(f"  gear files              : {len(gear_data):,}")
    print(f"  files scanned           : {files_scanned:,}")
    print()

    # Build in-memory weapon category lookup from gear_data before any DB writes.
    # insert_variants runs before insert_gear, so querying the DB won't work here.
    gear_category_map: dict[str, str] = {
        eid: data.get("Category")
        for eid, (data, _) in gear_data.items()
        if data.get("Category")
    }
    # Map gear_id → MechEngineer CT CategoryID (Armor, Gyro, etc.) for ct_dynamic marking.
    ct_category_map: dict[str, str] = {}
    for eid, (data, _) in gear_data.items():
        for cat in data.get("Custom", {}).get("Category", []):
            cid = cat.get("CategoryID", "")
            if cid in _CT_CATEGORIES:
                ct_category_map[eid] = cid
                break

    print("Phase 2 — writing to database...")
    insert_chassis(con, variant_data)
    variant_to_chassis = insert_variants(con, variant_data, rt_root, gear_category_map, ct_category_map)
    inserted, skipped = insert_loadouts(con, loadout_data, variant_to_chassis, rt_root, gear_category_map)
    print(f"  loadout rows inserted : {inserted:,}")
    if skipped:
        print(f"  loadouts skipped (no matching variant) : {skipped:,}")
    usage_pairs = insert_gear_usage(con, variant_data, loadout_data, variant_to_chassis)
    print(f"  gear_usage pairs      : {usage_pairs:,}")
    insert_affinities(con, affinity_data)
    ingest_bonus_descriptions(con, rt_root)
    insert_gear(con, gear_data, rt_root)
    print()

    chassis_count = con.execute("SELECT COUNT(*) FROM chassis").fetchone()[0]
    variant_count = con.execute("SELECT COUNT(*) FROM variant").fetchone()[0]
    gear_count = con.execute("SELECT COUNT(*) FROM gear").fetchone()[0]
    affinity_count = con.execute("SELECT COUNT(*) FROM affinity").fetchone()[0]

    duration = time.monotonic() - t0
    con.execute(
        """INSERT INTO pipeline_run
           (run_at, rt_root, files_scanned, chassis_count, variant_count,
            loadout_count, duration_sec)
           VALUES (?,?,?,?,?,?,?)""",
        (
            datetime.now(timezone.utc).isoformat(),
            str(rt_root),
            files_scanned,
            chassis_count,
            variant_count,
            inserted,
            round(duration, 2),
        ),
    )
    con.commit()
    con.close()

    db_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"Done in {duration:.1f}s  —  DB size: {db_size_mb:.1f} MB")
    print(f"  chassis    : {chassis_count:,}")
    print(f"  variants   : {variant_count:,}")
    print(f"  loadouts   : {inserted:,}")
    print(f"  affinities : {affinity_count:,}")
    print(f"  gear       : {gear_count:,}")


def main() -> None:
    parser = argparse.ArgumentParser(description="RogueTech Codex data ingestion pipeline")
    parser.add_argument("--full-rebuild", action="store_true",
                        help="Drop and recreate all tables before ingesting")
    parser.add_argument("--rt-root", default=None, help="Override RT_ROOT env var")
    parser.add_argument("--db-path", default=None, help="Override DB_PATH env var")
    args = parser.parse_args()

    rt_root_str = args.rt_root or os.environ.get("RT_ROOT", "")
    db_path_str = args.db_path or os.environ.get("DB_PATH", "roguetech.db")

    if not rt_root_str:
        print("ERROR: RT_ROOT not set. Use --rt-root or set the RT_ROOT environment variable.",
              file=sys.stderr)
        sys.exit(1)

    rt_root = Path(rt_root_str)
    if not rt_root.is_dir():
        print(f"ERROR: RT_ROOT does not exist or is not a directory: {rt_root}", file=sys.stderr)
        sys.exit(1)

    run(rt_root, Path(db_path_str), args.full_rebuild)


if __name__ == "__main__":
    main()
