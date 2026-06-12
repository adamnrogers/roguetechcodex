import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { apiFetch } from './useApi'

const ERA_TAG_MAP: Record<string, string> = {
  'Succession Wars': 'succession_wars',
  'Clan Invasion':   'clan_invasion',
  'Civil War':       'civil_war',
  'Jihad':           'jihad',
  'Republic':        'republic',
  'Dark Age':        'dark_ages',
}

export interface ChassisSummary {
  prefab_base: string
  ui_name: string
  unit_type: string
  weight_class: string | null
  tonnage: number | null
  icon: string | null
  variant_id: string
  variant_name: string | null
  variant_ui_name?: string | null
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
  ballistic:    HardpointFilter
  energy:       HardpointFilter
  missile:      HardpointFilter
  special:      HardpointFilter
  wing:         HardpointFilter
  bomb:         HardpointFilter
  handheld:     HardpointFilter
  excludeOmni:  boolean
  omniOnly:     boolean
}

export function defaultHardpoints(): HardpointFilters {
  return {
    ballistic:   { count: 0, loc: '' },
    energy:      { count: 0, loc: '' },
    missile:     { count: 0, loc: '' },
    special:     { count: 0, loc: '' },
    wing:        { count: 0, loc: '' },
    bomb:        { count: 0, loc: '' },
    handheld:    { count: 0, loc: '' },
    excludeOmni: false,
    omniOnly:    false,
  }
}

export interface MechFilters {
  q: string
  tonnage: number[]
  era: string[]
  faction: string
  tag: string
  page: number
  sort: string
  sortDir: string
  hasLowerArm: boolean | null
  hasHand: boolean | null
  hardpoints: HardpointFilters
}

export function defaultMechFilters(): MechFilters {
  return {
    q: '',
    tonnage: [],
    era: [],
    faction: '',
    tag: '',
    page: 1,
    sort: 'name',
    sortDir: 'asc',
    hasLowerArm: null,
    hasHand: null,
    hardpoints: defaultHardpoints(),
  }
}

type HpKey = Exclude<keyof HardpointFilters, 'excludeOmni' | 'omniOnly'>

function hpParams(hp: HardpointFilters): Record<string, string | number | boolean> {
  const params: Record<string, string | number | boolean> = {}
  const keys = ['ballistic', 'energy', 'missile', 'special', 'wing', 'bomb', 'handheld'] as HpKey[]
  for (const key of keys) {
    const { count, loc } = hp[key] as HardpointFilter
    if (count > 0) {
      params[`hp_${key}_count`] = count
      if (loc) params[`hp_${key}_loc`] = loc
    }
  }
  if (hp.excludeOmni) params['hp_exclude_omni'] = true
  if (hp.omniOnly)    params['hp_omni_only'] = true
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
          tonnage: filters.value.tonnage.length ? filters.value.tonnage : undefined,
          era: filters.value.era.length ? filters.value.era.map(e => ERA_TAG_MAP[e] ?? e) : undefined,
          faction: filters.value.faction || undefined,
          tag: filters.value.tag || undefined,
          unit_type: isBattleArmor.value ? 'battle_armor' : 'mech',
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
        tonnage: filters.value.tonnage.length ? filters.value.tonnage : undefined,
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
