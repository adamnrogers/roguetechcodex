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
  page: number
  sort: string
  sortDir: string
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
  damage: number | null
  heat_generated: number | null
  min_range: number | null
  max_range: number | null
  ammo_category: string | null
  shots_when_fired: number | null
  battle_value: number | null
  source_mod: string | null
  used_by_mechs: { prefab_base: string; ui_name: string }[]
  used_by_vehicles: { prefab_base: string; ui_name: string }[]
  related_affinities: AffinityEntry[]
}

export function useGearList(filters: Ref<GearFilters>) {
  return useQuery({
    queryKey: computed(() => ['gear', filters.value]),
    queryFn: () => {
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
      if (filters.value.includeCategories.length) params.include_categories = filters.value.includeCategories
      if (filters.value.excludeCategories.length) params.exclude_categories = filters.value.excludeCategories
      if (filters.value.includeLocations.length) params.include_locations = filters.value.includeLocations
      if (filters.value.excludeLocations.length) params.exclude_locations = filters.value.excludeLocations
      return apiFetch<GearListResponse>('/api/v1/gear', params)
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useGearDetail(gearId: string) {
  return useQuery({
    queryKey: ['gear', gearId],
    queryFn: () => apiFetch<GearDetail>(`/api/v1/gear/${gearId}`),
    staleTime: 10 * 60 * 1000,
  })
}
