import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { apiFetch } from './useApi'

export interface ChassisSummary {
  prefab_base: string
  ui_name: string
  unit_type: string
  weight_class: string | null
  tonnage: number | null
  variant_count: number
  icon: string | null
}

export interface ChassisListResponse {
  total: number
  page: number
  page_size: number
  results: ChassisSummary[]
}

export interface MechFilters {
  q: string
  weightClass: string[]
  era: string
  faction: string
  tag: string
  page: number
  sort: string
  sortDir: string
}

export function useMechList(filters: Ref<MechFilters>, mode: string | Ref<string> = 'mech') {
  const modeRef = computed(() => (typeof mode === 'string' ? mode : mode.value))

  const isMech    = computed(() => modeRef.value === 'mech')
  const isVehicle = computed(() => modeRef.value === 'vehicle')
  const isVtol    = computed(() => modeRef.value === 'vtol')

  return useQuery({
    queryKey: computed(() => [modeRef.value, filters.value]),
    queryFn: () => {
      if (isMech.value) {
        return apiFetch<ChassisListResponse>('/api/v1/mechs', {
          q: filters.value.q || undefined,
          weight_class: filters.value.weightClass.length ? filters.value.weightClass : undefined,
          era: filters.value.era || undefined,
          faction: filters.value.faction || undefined,
          tag: filters.value.tag || undefined,
          page: filters.value.page,
          page_size: 60,
          sort: filters.value.sort,
          sort_dir: filters.value.sortDir,
        })
      }
      return apiFetch<ChassisListResponse>('/api/v1/vehicles', {
        q: filters.value.q || undefined,
        weight_class: filters.value.weightClass.length ? filters.value.weightClass : undefined,
        unit_type: isVehicle.value ? 'vehicle' : isVtol.value ? 'vtol' : undefined,
        page: filters.value.page,
        page_size: 60,
        sort: filters.value.sort,
        sort_dir: filters.value.sortDir,
      })
    },
    staleTime: 5 * 60 * 1000,
  })
}
