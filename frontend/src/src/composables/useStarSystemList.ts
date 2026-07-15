import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { apiFetch } from './useApi'

export interface StarSystemSummary {
  id: string
  ui_name: string
  difficulty: number | null
  population: string | null
  biomes: string[]
}

export interface StarSystemListResponse {
  total: number
  page: number
  page_size: number
  results: StarSystemSummary[]
}

export interface StarSystemDetail {
  id: string
  ui_name: string
  details: string | null
  difficulty: number | null
  star_type: string | null
  owner_id: string | null
  jump_distance: number | null
  fueling_station: boolean
  population: string | null
  size: string | null
  biomes: string[]
  tags: string[]
  source_mod: string | null
}

export interface StarSystemFilters {
  q: string
  biomes: string[]
  population: string[]
  tags: string[]
  minDifficulty: number | null
  maxDifficulty: number | null
  page: number
  sort: string
  sortDir: string
}

export function useStarSystemList(filters: Ref<StarSystemFilters>) {
  return useQuery({
    queryKey: computed(() => ['star-systems', filters.value]),
    queryFn: () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any -- query params are a heterogeneous string/number/boolean/array bag
      const params: Record<string, any> = {
        page: filters.value.page,
        page_size: 60,
        sort: filters.value.sort,
        sort_dir: filters.value.sortDir,
      }
      if (filters.value.q) params.q = filters.value.q
      if (filters.value.biomes.length) params.biomes = filters.value.biomes
      if (filters.value.population.length) params.population = filters.value.population
      if (filters.value.tags.length) params.tags = filters.value.tags
      if (filters.value.minDifficulty !== null) params.min_difficulty = filters.value.minDifficulty
      if (filters.value.maxDifficulty !== null) params.max_difficulty = filters.value.maxDifficulty
      return apiFetch<StarSystemListResponse>('/api/v1/star-systems', params)
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useStarSystemDetail(systemId: Ref<string> | string) {
  const id = typeof systemId === 'string' ? { value: systemId } : systemId
  return useQuery({
    queryKey: computed(() => ['star-system', id.value]),
    queryFn: () => apiFetch<StarSystemDetail>(`/api/v1/star-systems/${id.value}`),
    staleTime: 10 * 60 * 1000,
  })
}
