import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { apiFetch } from './useApi'

export interface ChassisSummary {
  prefab_base: string
  ui_name: string
  unit_type: string
  weight_class: string | null
  tonnage: number | null
  icon: string | null
  variant_id: string
  variant_name: string | null
}

export interface ChassisListResponse {
  total: number
  page: number
  page_size: number
  results: ChassisSummary[]
}

export interface HardpointFilter {
  count: number
  loc: string
}

export type HardpointFilters = {
  ballistic: HardpointFilter
  energy:    HardpointFilter
  missile:   HardpointFilter
  special:   HardpointFilter
  wing:      HardpointFilter
  bomb:      HardpointFilter
  handheld:  HardpointFilter
}

export function defaultHardpoints(): HardpointFilters {
  return {
    ballistic: { count: 0, loc: '' },
    energy:    { count: 0, loc: '' },
    missile:   { count: 0, loc: '' },
    special:   { count: 0, loc: '' },
    wing:      { count: 0, loc: '' },
    bomb:      { count: 0, loc: '' },
    handheld:  { count: 0, loc: '' },
  }
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
  minTonnage: number | null
  maxTonnage: number | null
  hasLowerArm: boolean | null
  hasHand: boolean | null
  hardpoints: HardpointFilters
}

export function defaultMechFilters(): MechFilters {
  return {
    q: '',
    weightClass: [],
    era: '',
    faction: '',
    tag: '',
    page: 1,
    sort: 'name',
    sortDir: 'asc',
    minTonnage: null,
    maxTonnage: null,
    hasLowerArm: null,
    hasHand: null,
    hardpoints: defaultHardpoints(),
  }
}

type HpKey = keyof HardpointFilters

function hpParams(hp: HardpointFilters): Record<string, string | number> {
  const params: Record<string, string | number> = {}
  const keys = Object.keys(defaultHardpoints()) as HpKey[]
  for (const key of keys) {
    const { count, loc } = hp[key]
    if (count > 0) {
      params[`hp_${key}_count`] = count
      if (loc) params[`hp_${key}_loc`] = loc
    }
  }
  return params
}

export function useMechList(filters: Ref<MechFilters>, mode: string | Ref<string> = 'mech') {
  const modeRef = computed(() => (typeof mode === 'string' ? mode : mode.value))

  const isMech        = computed(() => modeRef.value === 'mech')
  const isVehicle     = computed(() => modeRef.value === 'vehicle')
  const isVtol        = computed(() => modeRef.value === 'vtol')
  const isBattleArmor = computed(() => modeRef.value === 'battle_armor')

  return useQuery({
    queryKey: computed(() => [modeRef.value, filters.value]),
    queryFn: () => {
      if (isMech.value || isBattleArmor.value) {
        return apiFetch<ChassisListResponse>('/api/v1/mechs', {
          q: filters.value.q || undefined,
          weight_class: filters.value.weightClass.length ? filters.value.weightClass : undefined,
          era: filters.value.era || undefined,
          faction: filters.value.faction || undefined,
          tag: filters.value.tag || undefined,
          unit_type: isBattleArmor.value ? 'battle_armor' : 'mech',
          min_tonnage: filters.value.minTonnage ?? undefined,
          max_tonnage: filters.value.maxTonnage ?? undefined,
          has_lower_arm: filters.value.hasLowerArm ?? undefined,
          has_hand: filters.value.hasHand ?? undefined,
          page: filters.value.page,
          page_size: 60,
          sort: filters.value.sort,
          sort_dir: filters.value.sortDir,
          ...hpParams(filters.value.hardpoints),
        })
      }
      return apiFetch<ChassisListResponse>('/api/v1/vehicles', {
        q: filters.value.q || undefined,
        weight_class: filters.value.weightClass.length ? filters.value.weightClass : undefined,
        unit_type: isVehicle.value ? 'vehicle' : isVtol.value ? 'vtol' : undefined,
        min_tonnage: filters.value.minTonnage ?? undefined,
        max_tonnage: filters.value.maxTonnage ?? undefined,
        page: filters.value.page,
        page_size: 60,
        sort: filters.value.sort,
        sort_dir: filters.value.sortDir,
      })
    },
    staleTime: 5 * 60 * 1000,
  })
}
