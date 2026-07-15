from __future__ import annotations

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Affinity sub-models
# ---------------------------------------------------------------------------


class AffinityLevel(BaseModel):
    missions_required: int
    level_name: str
    description: str


class AffinityEntry(BaseModel):
    id: str
    affinity_type: str  # "Global" | "Chassis" | "Quirk" | "Tag"
    quirk_name: str  # quirk ID (Quirk type only, used for /quirks/:id link)
    quirk_ui_name: str = ""  # UIName from gear table (Quirk type only)
    levels: list[AffinityLevel]


class QuirkEffect(BaseModel):
    id: str  # quirk gear ID, used for /quirks/:id link
    ui_name: str = ""
    bonus_descriptions: list[str]


# ---------------------------------------------------------------------------
# Hardpoint / location sub-models (from variant.locations_json)
# ---------------------------------------------------------------------------


class Hardpoint(BaseModel):
    weapon_mount_id: str
    omni: bool


class VariantLocation(BaseModel):
    location: str
    hardpoints: list[Hardpoint]
    max_armor: int
    max_rear_armor: int
    internal_structure: float
    inventory_slots: int


# ---------------------------------------------------------------------------
# Loadout sub-models (from loadout table)
# ---------------------------------------------------------------------------


class LoadoutLocation(BaseModel):
    location: str
    current_armor: int
    current_rear_armor: int
    current_internal_structure: float


class InventoryItem(BaseModel):
    mounted_location: str
    component_def_id: str
    component_def_type: str
    hardpoint_slot: int
    weapon_category: str | None = None
    ui_name: str | None = None
    blacklisted: bool = False


class EquipmentItem(BaseModel):
    mounted_location: str
    component_def_id: str
    component_def_type: str
    hardpoint_slot: int
    weapon_category: str | None = None
    ui_name: str | None = None
    blacklisted: bool = False


# ---------------------------------------------------------------------------
# Variant detail - chassisdef + embedded loadout
# ---------------------------------------------------------------------------


class VariantDetail(BaseModel):
    id: str  # chassisdef id
    variant_name: str | None
    details: str | None
    unit_type: str
    weight_class: str | None
    tonnage: float | None
    top_speed: float | None
    max_jumpjets: int | None
    drop_cost_modifier: float | None
    chassis_tags: list[str]
    locations: list[VariantLocation]
    fixed_equipment: list[EquipmentItem]
    chassis_defaults: list
    multi_defaults: list
    lootable_unique_mech: bool
    is_unique: bool  # UniqueMech chassis tag or unit_rarity_chassis_unique loadout tag
    source_mod: str | None
    hardpoints_summary: str  # e.g. "4B 3E 5M 1S 20JJ"
    # Embedded loadout (None if no mechdef exists)
    loadout_id: str | None
    era_tags: list[str]
    faction_tags: list[str]
    loadout_locations: list[LoadoutLocation]
    inventory: list[InventoryItem]
    required_to_spawn_tags: list[str]
    health_summary: str  # e.g. "A=600/730 S=291"
    affinities: list[AffinityEntry]
    quirks: list[QuirkEffect] = []


# ---------------------------------------------------------------------------
# Chassis summary - browse page (one per prefab_base)
# ---------------------------------------------------------------------------


class ChassisSummary(BaseModel):
    prefab_base: str
    ui_name: str
    unit_type: str
    weight_class: str | None
    tonnage: float | None
    icon: str | None
    variant_id: str
    variant_name: str | None
    variant_ui_name: str | None = None
    is_unique: bool = False


class ChassisListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[ChassisSummary]


# ---------------------------------------------------------------------------
# Chassis detail - full page (GET /api/v1/mechs/{prefab_base})
# ---------------------------------------------------------------------------


class ChassisDetail(BaseModel):
    prefab_base: str
    ui_name: str
    unit_type: str
    weight_class: str | None
    tonnage: float | None
    icon: str | None
    variants: list[VariantDetail]


# ---------------------------------------------------------------------------
# Gear - equipment, weapons, jump jets, heat sinks, ammo
# ---------------------------------------------------------------------------


class GearSummary(BaseModel):
    id: str
    ui_name: str
    component_type: str | None
    weapon_category: str | None
    tonnage: float | None
    slots: int | None
    cost: int | None
    damage: float | None
    heat_generated: float | None
    manufacturer: str | None
    source_mod: str | None


class GearListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[GearSummary]


class UsedByChassis(BaseModel):
    prefab_base: str
    ui_name: str
    unit_type: str | None = None
    variant_id: str
    variant_name: str | None = None


class GearDetail(BaseModel):
    id: str
    ui_name: str
    details: str | None
    component_type: str | None
    component_subtype: str | None
    weapon_category: str | None
    tonnage: float | None
    slots: int | None
    cost: int | None
    rarity: int | None
    purchasable: bool
    manufacturer: str | None
    model: str | None
    bonus_value_a: str | None
    bonus_value_b: str | None
    allowed_locations: str | None
    disallowed_locations: str | None
    component_tags: list[str]
    weapon_type: str | None
    weapon_subtype: str | None
    damage: float | None
    heat_generated: float | None
    min_range: int | None
    max_range: int | None
    ammo_category: str | None
    shots_when_fired: int | None
    battle_value: int | None
    # Extended weapon stats
    instability: float | None
    heat_damage: float | None
    accuracy_modifier: float | None
    evasion_pips_ignored: float | None
    attack_recoil: float | None
    projectiles_per_shot: int | None
    crit_chance_mult: float | None
    ap_shards_mod: float | None
    ap_crit_chance_mult: float | None
    range_short: int | None
    range_medium: int | None
    range_long: int | None
    indirect_fire_capable: bool | None
    bonus_descriptions: list[str]
    modes: list[dict]
    source_mod: str | None
    used_by_mechs: list[UsedByChassis]
    used_by_vehicles: list[UsedByChassis]
    related_affinities: list[AffinityEntry]  # populated for Quirk_ items


# ---------------------------------------------------------------------------
# Stats / health
# ---------------------------------------------------------------------------


class StatsResponse(BaseModel):
    mechs: int
    vehicles: int
    weapons: int
    equipment: int


# ---------------------------------------------------------------------------
# Global search
# ---------------------------------------------------------------------------


class SearchHit(BaseModel):
    id: str
    name: str
    subtitle: str
    result_type: str  # mech | vehicle | vtol | battle_armor | equipment | weapon | quirk
    variant_id: str | None = None


class SearchResponse(BaseModel):
    q: str
    chassis: list[SearchHit]
    gear: list[SearchHit]


class SearchPageResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[SearchHit]


# ---------------------------------------------------------------------------
# Star systems
# ---------------------------------------------------------------------------


class StarSystemSummary(BaseModel):
    id: str
    ui_name: str
    difficulty: int | None
    population: str | None
    biomes: list[str]


class StarSystemListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[StarSystemSummary]


class StarSystemDetail(BaseModel):
    id: str
    ui_name: str
    details: str | None
    difficulty: int | None
    star_type: str | None
    owner_id: str | None
    jump_distance: int | None
    fueling_station: bool
    population: str | None
    size: str | None
    biomes: list[str]
    tags: list[str]
    source_mod: str | None


# ---------------------------------------------------------------------------
# RTO Pilots
# ---------------------------------------------------------------------------


class RtoPilotTag(BaseModel):
    tag: str
    label: str | None
    description: str | None


class RtoPilotRef(BaseModel):
    id: str
    name: str | None


class RtoPilotRequirements(BaseModel):
    hiring_requirements: list[str]
    hiring_visibility_requirements: list[str]
    required_system_owner: list[str]
    required_system_core_ids: list[str]
    required_pilot_ids: list[RtoPilotRef]
    conflicting_pilot_ids: list[RtoPilotRef]


class RtoPilotDetail(BaseModel):
    id: str
    ui_name: str
    first_name: str | None
    last_name: str | None
    callsign: str | None
    gender: str | None
    faction: str | None
    age: int | None
    details: str | None
    icon: str | None
    can_pilot: list[str]
    tags: list[RtoPilotTag]
    requirements: RtoPilotRequirements | None
    source_mod: str | None
