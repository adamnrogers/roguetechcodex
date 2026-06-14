-- RogueTech Codex SQLite schema
-- Applied by ingest.py at startup (CREATE TABLE IF NOT EXISTS)

-- True chassis - one row per PrefabBase (e.g. "adder")
CREATE TABLE IF NOT EXISTS chassis (
    prefab_base     TEXT PRIMARY KEY,   -- "adder"
    ui_name         TEXT NOT NULL,      -- "Adder"
    unit_type       TEXT NOT NULL,      -- 'mech'|'vehicle'|'vtol'|'battle_armor'
    weight_class    TEXT,               -- 'LIGHT'|'MEDIUM'|'HEAVY'|'ASSAULT'
    tonnage         REAL,
    icon            TEXT
);

-- Variants - one row per chassisdef_*.json file
CREATE TABLE IF NOT EXISTS variant (
    id                      TEXT PRIMARY KEY,   -- "chassisdef_adder_ADR-Prime"
    chassis_id              TEXT NOT NULL REFERENCES chassis(prefab_base) ON DELETE CASCADE,
    ui_name                 TEXT NOT NULL,      -- "Adder"
    variant_name            TEXT,               -- "ADR-Prime"
    details                 TEXT,               -- lore text
    unit_type               TEXT NOT NULL,
    weight_class            TEXT,
    tonnage                 REAL,
    movement_cap_def_id     TEXT,               -- "movedef_lightmech"
    top_speed               REAL,               -- kph, for Base Move display
    max_jumpjets            INTEGER,
    drop_cost_modifier      REAL,               -- Custom.DropCostFactor.DropModifier
    chassis_tags            TEXT,               -- JSON array (mr-resize-* excluded)
    locations_json          TEXT,               -- Locations[] - hardpoints, max armor, structure
    fixed_equipment_json    TEXT,               -- FixedEquipment[]
    chassis_defaults_json   TEXT,               -- Custom.ChassisDefaults
    multi_defaults_json     TEXT,               -- Custom.MultiDefaults
    lootable_unique_mech    INTEGER DEFAULT 0,  -- Custom.LootableUniqueMech.BlockAssembly
    movement_type           TEXT,               -- NULL for mechs; 'Wheeled'|'Tracked'|'Hover'|'VTOL'
    source_file             TEXT,
    source_mod              TEXT,               -- e.g. "Eras/ClanInvasion3061"
    hardpoints_json         TEXT                -- pre-aggregated counts: {loc: {type: count, Omni: count}}
);

-- Loadouts - one row per mechdef_*.json file
CREATE TABLE IF NOT EXISTS loadout (
    id                      TEXT PRIMARY KEY,   -- "mechdef_adder_ADR-Prime"
    variant_id              TEXT NOT NULL REFERENCES variant(id) ON DELETE CASCADE,
    chassis_id              TEXT NOT NULL,      -- denormalized prefab_base
    unit_tags               TEXT,               -- JSON array (MechTags/VehicleTags items)
    era_tags                TEXT,               -- comma-separated extracted era values
    faction_tags            TEXT,               -- comma-separated faction values
    inventory_json          TEXT,               -- JSON array of equipped items
    locations_json          TEXT,               -- JSON array of per-location armor values
    required_to_spawn_tags  TEXT,               -- JSON array from RequiredToSpawnCompanyTags
    source_file             TEXT,
    source_mod              TEXT
);

CREATE INDEX IF NOT EXISTS idx_chassis_unit_type    ON chassis(unit_type);
CREATE INDEX IF NOT EXISTS idx_chassis_weight       ON chassis(weight_class);
CREATE INDEX IF NOT EXISTS idx_variant_chassis      ON variant(chassis_id);
CREATE INDEX IF NOT EXISTS idx_variant_unit_type    ON variant(unit_type);
CREATE INDEX IF NOT EXISTS idx_variant_weight       ON variant(weight_class);
CREATE INDEX IF NOT EXISTS idx_variant_tonnage      ON variant(tonnage);
CREATE INDEX IF NOT EXISTS idx_variant_source       ON variant(source_mod);
CREATE INDEX IF NOT EXISTS idx_loadout_variant      ON loadout(variant_id);
CREATE INDEX IF NOT EXISTS idx_loadout_chassis      ON loadout(chassis_id);

-- Gear - one row per upgradedef_*.json or weapondef_*.json
CREATE TABLE IF NOT EXISTS gear (
    id                   TEXT PRIMARY KEY,
    ui_name              TEXT NOT NULL,
    details              TEXT,
    component_type       TEXT,   -- 'Weapon'|'Upgrade'|'HeatSink'|'AmmunitionBox'
    component_subtype    TEXT,
    tonnage              REAL,
    slots                INTEGER,
    cost                 INTEGER,
    rarity               INTEGER,
    purchasable          INTEGER DEFAULT 1,
    manufacturer         TEXT,
    model                TEXT,
    bonus_value_a        TEXT,
    bonus_value_b        TEXT,
    allowed_locations    TEXT,
    disallowed_locations TEXT,
    component_tags       TEXT,   -- JSON array
    weapon_category      TEXT,   -- 'Ballistic'|'Energy'|'Missile'|'Melee'|'Support' (weapons only)
    weapon_type          TEXT,   -- e.g. 'LRM', 'Autocannon', 'Laser'
    weapon_subtype       TEXT,   -- e.g. 'LRM20', 'AC10'
    weapon_category_id   TEXT,   -- e.g. 'w/a/a/ac', 'w/m/s/srm' from Custom.Category[].CategoryID
    damage               REAL,
    heat_generated       REAL,
    min_range            INTEGER,
    max_range            INTEGER,
    ammo_category        TEXT,
    shots_when_fired     INTEGER,
    battle_value         INTEGER,
    -- Extended weapon stats (weapons only)
    instability          REAL,
    heat_damage          REAL,
    accuracy_modifier    REAL,
    evasion_pips_ignored REAL,
    attack_recoil        REAL,
    projectiles_per_shot INTEGER,
    crit_chance_mult     REAL,
    ap_shards_mod        REAL,
    ap_crit_chance_mult  REAL,
    range_short          INTEGER,
    range_medium         INTEGER,
    range_long           INTEGER,
    indirect_fire_capable INTEGER,
    bonus_descriptions   TEXT,   -- JSON array of resolved human-readable trait strings
    modes_json           TEXT,   -- JSON array of computed per-mode stat objects
    source_file          TEXT,
    source_mod           TEXT
);

CREATE INDEX IF NOT EXISTS idx_gear_component_type  ON gear(component_type);
CREATE INDEX IF NOT EXISTS idx_gear_weapon_category ON gear(weapon_category);
CREATE INDEX IF NOT EXISTS idx_gear_weapon_type        ON gear(weapon_type);
CREATE INDEX IF NOT EXISTS idx_gear_weapon_subtype     ON gear(weapon_subtype);
CREATE INDEX IF NOT EXISTS idx_gear_weapon_category_id ON gear(weapon_category_id);
CREATE INDEX IF NOT EXISTS idx_gear_tonnage         ON gear(tonnage);
CREATE INDEX IF NOT EXISTS idx_gear_heat            ON gear(heat_generated);
CREATE INDEX IF NOT EXISTS idx_gear_source_mod      ON gear(source_mod);

-- Affinities - one row per AffinityDef_*.json
CREATE TABLE IF NOT EXISTS affinity (
    id            TEXT PRIMARY KEY,   -- "AffinityDef_quirk_Barrage"
    affinity_type TEXT,               -- "Global"|"Chassis"|"Quirk"|"Tag"
    quirk_names   TEXT,               -- JSON array (Quirk type only)
    chassis_names TEXT,               -- JSON array of AssemblyVariant IDs (Chassis type only)
    levels_json   TEXT                -- JSON array of {missions_required, level_name, description}
);

CREATE TABLE IF NOT EXISTS gear_usage (
    gear_id    TEXT NOT NULL,
    variant_id TEXT NOT NULL,
    PRIMARY KEY (gear_id, variant_id)
);
CREATE INDEX IF NOT EXISTS idx_gear_usage_gear    ON gear_usage(gear_id);
CREATE INDEX IF NOT EXISTS idx_gear_usage_variant ON gear_usage(variant_id);

-- BonusDescriptions localisation lookup - populated from BonusDescriptions_*.json files
CREATE TABLE IF NOT EXISTS bonus_descriptions_lookup (
    key   TEXT PRIMARY KEY,
    short TEXT,
    long  TEXT,
    full  TEXT
);

CREATE TABLE IF NOT EXISTS pipeline_run (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at           TEXT,
    rt_root          TEXT,
    files_scanned    INTEGER,
    chassis_count    INTEGER,
    variant_count    INTEGER,
    loadout_count    INTEGER,
    duration_sec     REAL
);
