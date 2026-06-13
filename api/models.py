from __future__ import annotations
from typing import Optional
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
    affinity_type: str       # "Global" | "Chassis" | "Quirk" | "Tag"
    quirk_name: str          # quirk ID (Quirk type only, used for /quirks/:id link)
    quirk_ui_name: str = ""  # UIName from gear table (Quirk type only)
    levels: list[AffinityLevel]


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
    weapon_category: Optional[str] = None
    ui_name: Optional[str] = None


class EquipmentItem(BaseModel):
    mounted_location: str
    component_def_id: str
    component_def_type: str
    hardpoint_slot: int
    weapon_category: Optional[str] = None
    ui_name: Optional[str] = None


# ---------------------------------------------------------------------------
# Variant detail — chassisdef + embedded loadout
# ---------------------------------------------------------------------------

class VariantDetail(BaseModel):
    id: str                             # chassisdef id
    variant_name: Optional[str]
    details: Optional[str]
    unit_type: str
    weight_class: Optional[str]
    tonnage: Optional[float]
    top_speed: Optional[float]
    max_jumpjets: Optional[int]
    drop_cost_modifier: Optional[float]
    chassis_tags: list[str]
    locations: list[VariantLocation]
    fixed_equipment: list[EquipmentItem]
    chassis_defaults: list
    multi_defaults: list
    lootable_unique_mech: bool
    source_mod: Optional[str]
    hardpoints_summary: str             # e.g. "4B 3E 5M 1S 20JJ"
    # Embedded loadout (None if no mechdef exists)
    loadout_id: Optional[str]
    era_tags: list[str]
    faction_tags: list[str]
    loadout_locations: list[LoadoutLocation]
    inventory: list[InventoryItem]
    required_to_spawn_tags: list[str]
    health_summary: str                 # e.g. "A=600/730 S=291"
    affinities: list[AffinityEntry]


# ---------------------------------------------------------------------------
# Chassis summary — browse page (one per prefab_base)
# ---------------------------------------------------------------------------

class ChassisSummary(BaseModel):
    prefab_base: str
    ui_name: str
    unit_type: str
    weight_class: Optional[str]
    tonnage: Optional[float]
    icon: Optional[str]
    variant_id: str
    variant_name: Optional[str]
    variant_ui_name: Optional[str] = None


class ChassisListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[ChassisSummary]


# ---------------------------------------------------------------------------
# Chassis detail — full page (GET /api/v1/mechs/{prefab_base})
# ---------------------------------------------------------------------------

class ChassisDetail(BaseModel):
    prefab_base: str
    ui_name: str
    unit_type: str
    weight_class: Optional[str]
    tonnage: Optional[float]
    icon: Optional[str]
    variants: list[VariantDetail]


# ---------------------------------------------------------------------------
# Gear — equipment, weapons, jump jets, heat sinks, ammo
# ---------------------------------------------------------------------------

class GearSummary(BaseModel):
    id: str
    ui_name: str
    component_type: Optional[str]
    weapon_category: Optional[str]
    tonnage: Optional[float]
    slots: Optional[int]
    cost: Optional[int]
    damage: Optional[float]
    heat_generated: Optional[float]
    manufacturer: Optional[str]
    source_mod: Optional[str]


class GearListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[GearSummary]


class UsedByChassis(BaseModel):
    prefab_base: str
    ui_name: str
    unit_type: Optional[str] = None
    variant_id: str
    variant_name: Optional[str] = None


class GearDetail(BaseModel):
    id: str
    ui_name: str
    details: Optional[str]
    component_type: Optional[str]
    component_subtype: Optional[str]
    weapon_category: Optional[str]
    tonnage: Optional[float]
    slots: Optional[int]
    cost: Optional[int]
    rarity: Optional[int]
    purchasable: bool
    manufacturer: Optional[str]
    model: Optional[str]
    bonus_value_a: Optional[str]
    bonus_value_b: Optional[str]
    allowed_locations: Optional[str]
    disallowed_locations: Optional[str]
    component_tags: list[str]
    weapon_type: Optional[str]
    weapon_subtype: Optional[str]
    damage: Optional[float]
    heat_generated: Optional[float]
    min_range: Optional[int]
    max_range: Optional[int]
    ammo_category: Optional[str]
    shots_when_fired: Optional[int]
    battle_value: Optional[int]
    # Extended weapon stats
    instability: Optional[float]
    heat_damage: Optional[float]
    accuracy_modifier: Optional[float]
    evasion_pips_ignored: Optional[float]
    attack_recoil: Optional[float]
    projectiles_per_shot: Optional[int]
    crit_chance_mult: Optional[float]
    ap_shards_mod: Optional[float]
    ap_crit_chance_mult: Optional[float]
    range_short: Optional[int]
    range_medium: Optional[int]
    range_long: Optional[int]
    indirect_fire_capable: Optional[bool]
    bonus_descriptions: list[str]
    modes: list[dict]
    source_mod: Optional[str]
    used_by_mechs: list[UsedByChassis]
    used_by_vehicles: list[UsedByChassis]
    related_affinities: list[AffinityEntry]   # populated for Quirk_ items


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
    result_type: str   # mech | vehicle | vtol | battle_armor | equipment | weapon | quirk
    variant_id: Optional[str] = None


class SearchResponse(BaseModel):
    q: str
    chassis: list[SearchHit]
    gear: list[SearchHit]


class SearchPageResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[SearchHit]
