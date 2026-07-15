import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { apiFetch } from './useApi'
import type { AffinityEntry } from './useChassisDetail'

export type { AffinityEntry }

export interface GearSummary {
  id: string
  ui_name: string
  component_type: string | null
  weapon_category: string | null
  tonnage: number | null
  slots: number | null
  cost: number | null
  damage: number | null
  heat_generated: number | null
  manufacturer: string | null
  source_mod: string | null
}

export interface GearListResponse {
  total: number
  page: number
  page_size: number
  results: GearSummary[]
}

export interface GearFilters {
  q: string
  componentType: string
  includeTypes: string[]
  excludeTypes: string[]
  includeCategories: string[]
  excludeCategories: string[]
  includeLocations: string[]
  excludeLocations: string[]
  weaponTypes: string[]
  weaponSubtypes: string[]
  weaponCategoryIds: string[]
  minTonnage: number | null
  maxTonnage: number | null
  minHeat: number | null
  maxHeat: number | null
  minSlots: number | null
  maxSlots: number | null
  page: number
  sort: string
  sortDir: string
}

export interface WeaponMode {
  mode_id: string
  mode_ui_name: string
  mode_description: string
  is_base_mode: boolean
  damage: number | null
  heat_generated: number | null
  instability: number | null
  heat_damage: number | null
  accuracy_modifier: number | null
  evasion_pips_ignored: number | null
  attack_recoil: number | null
  shots_when_fired: number | null
  projectiles_per_shot: number | null
  crit_chance_mult: number | null
  ap_shards_mod: number | null
  ap_crit_chance_mult: number | null
  ammo_category: string | null
  indirect_fire_capable: boolean | null
  min_range: number
  range_short: number
  range_medium: number
  range_long: number
  max_range: number
}

export interface GearDetail {
  id: string
  ui_name: string
  details: string | null
  component_type: string | null
  component_subtype: string | null
  weapon_category: string | null
  tonnage: number | null
  slots: number | null
  cost: number | null
  rarity: number | null
  purchasable: boolean
  manufacturer: string | null
  model: string | null
  bonus_value_a: string | null
  bonus_value_b: string | null
  allowed_locations: string | null
  disallowed_locations: string | null
  component_tags: string[]
  weapon_type: string | null
  weapon_subtype: string | null
  damage: number | null
  heat_generated: number | null
  min_range: number | null
  max_range: number | null
  ammo_category: string | null
  shots_when_fired: number | null
  battle_value: number | null
  instability: number | null
  heat_damage: number | null
  accuracy_modifier: number | null
  evasion_pips_ignored: number | null
  attack_recoil: number | null
  projectiles_per_shot: number | null
  crit_chance_mult: number | null
  ap_shards_mod: number | null
  ap_crit_chance_mult: number | null
  range_short: number | null
  range_medium: number | null
  range_long: number | null
  indirect_fire_capable: boolean | null
  bonus_descriptions: string[]
  modes: WeaponMode[]
  source_mod: string | null
  used_by_mechs: {
    prefab_base: string
    ui_name: string
    unit_type: string | null
    variant_id: string
    variant_name: string | null
  }[]
  used_by_vehicles: {
    prefab_base: string
    ui_name: string
    unit_type: string | null
    variant_id: string
    variant_name: string | null
  }[]
  related_affinities: AffinityEntry[]
}

export function useGearList(filters: Ref<GearFilters>) {
  return useQuery({
    queryKey: computed(() => ['gear', filters.value]),
    queryFn: () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any -- query params are a heterogeneous string/number/boolean/array bag
      const params: Record<string, any> = {
        page: filters.value.page,
        page_size: 60,
        sort: filters.value.sort,
        sort_dir: filters.value.sortDir,
      }
      if (filters.value.q) params.q = filters.value.q
      if (filters.value.componentType) params.component_type = filters.value.componentType
      if (filters.value.includeTypes.length) params.include_types = filters.value.includeTypes
      if (filters.value.excludeTypes.length) params.exclude_types = filters.value.excludeTypes
      if (filters.value.includeCategories.length)
        params.include_categories = filters.value.includeCategories
      if (filters.value.excludeCategories.length)
        params.exclude_categories = filters.value.excludeCategories
      if (filters.value.includeLocations.length)
        params.include_locations = filters.value.includeLocations
      if (filters.value.excludeLocations.length)
        params.exclude_locations = filters.value.excludeLocations
      if (filters.value.weaponTypes.length) params.include_weapon_types = filters.value.weaponTypes
      if (filters.value.weaponSubtypes.length)
        params.include_weapon_subtypes = filters.value.weaponSubtypes
      if (filters.value.weaponCategoryIds.length)
        params.include_weapon_category_ids = filters.value.weaponCategoryIds
      if (filters.value.minTonnage !== null) params.min_tonnage = filters.value.minTonnage
      if (filters.value.maxTonnage !== null) params.max_tonnage = filters.value.maxTonnage
      if (filters.value.minHeat !== null) params.min_heat = filters.value.minHeat
      if (filters.value.maxHeat !== null) params.max_heat = filters.value.maxHeat
      if (filters.value.minSlots !== null) params.min_slots = filters.value.minSlots
      if (filters.value.maxSlots !== null) params.max_slots = filters.value.maxSlots
      if (import.meta.env.VITE_HIDE_BLACKLISTED === 'true') params.hide_blacklisted = true
      return apiFetch<GearListResponse>('/api/v1/gear', params)
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useGearDetail(gearId: Ref<string> | string) {
  const id = typeof gearId === 'string' ? { value: gearId } : gearId
  return useQuery({
    queryKey: computed(() => ['gear', id.value]),
    queryFn: () => apiFetch<GearDetail>(`/api/v1/gear/${id.value}`),
    staleTime: 10 * 60 * 1000,
  })
}
