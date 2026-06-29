import { useQuery } from '@tanstack/vue-query'
import { computed, type Ref } from 'vue'
import { apiFetch } from './useApi'

export interface AffinityLevel {
  missions_required: number
  level_name: string
  description: string
}

export interface AffinityEntry {
  id: string
  affinity_type: string   // "Global" | "Chassis" | "Quirk"
  quirk_name: string      // quirk ID for /quirks/:id link (Quirk type only)
  quirk_ui_name?: string  // gear table UIName for Quirk type (e.g. "Morrigan C3i")
  levels: AffinityLevel[]
}

export interface Hardpoint {
  weapon_mount_id: string
  omni: boolean
}

export interface VariantLocation {
  location: string
  hardpoints: Hardpoint[]
  max_armor: number
  max_rear_armor: number
  internal_structure: number
  inventory_slots: number
}

export interface LoadoutLocation {
  location: string
  current_armor: number
  current_rear_armor: number
  current_internal_structure: number
}

export interface InventoryItem {
  mounted_location: string
  component_def_id: string
  component_def_type: string
  hardpoint_slot: number
  weapon_category: string | null
  ui_name?: string | null
  blacklisted?: boolean
}

export interface EquipmentItem {
  mounted_location: string
  component_def_id: string
  component_def_type: string
  hardpoint_slot: number
  weapon_category: string | null
  ui_name?: string | null
  blacklisted?: boolean
}

export interface VariantDetail {
  id: string
  variant_name: string | null
  details: string | null
  unit_type: string
  weight_class: string | null
  tonnage: number | null
  top_speed: number | null
  max_jumpjets: number | null
  drop_cost_modifier: number | null
  chassis_tags: string[]
  locations: VariantLocation[]
  fixed_equipment: EquipmentItem[]
  chassis_defaults: unknown[]
  multi_defaults: unknown[]
  lootable_unique_mech: boolean
  source_mod: string | null
  hardpoints_summary: string
  loadout_id: string | null
  era_tags: string[]
  faction_tags: string[]
  loadout_locations: LoadoutLocation[]
  inventory: InventoryItem[]
  required_to_spawn_tags: string[]
  health_summary: string
  affinities: AffinityEntry[]
}

export interface ChassisDetail {
  prefab_base: string
  ui_name: string
  unit_type: string
  weight_class: string | null
  tonnage: number | null
  icon: string | null
  variants: VariantDetail[]
}

export function useChassisDetail(
  prefabBase: Ref<string> | string,
  isVehicle: Ref<boolean> | boolean = false,
  isBattleArmor: Ref<boolean> | boolean = false,
) {
  const id = typeof prefabBase === 'string' ? { value: prefabBase } : prefabBase
  const vehicle = typeof isVehicle === 'boolean' ? { value: isVehicle } : isVehicle
  const battleArmor = typeof isBattleArmor === 'boolean' ? { value: isBattleArmor } : isBattleArmor
  return useQuery({
    queryKey: computed(() => ['chassis', id.value, vehicle.value, battleArmor.value]),
    queryFn: () => {
      const endpoint = vehicle.value
        ? `/api/v1/vehicles/${id.value}`
        : battleArmor.value
          ? `/api/v1/battle-armor/${id.value}`
          : `/api/v1/mechs/${id.value}`
      return apiFetch<ChassisDetail>(endpoint)
    },
    staleTime: 10 * 60 * 1000,
  })
}
