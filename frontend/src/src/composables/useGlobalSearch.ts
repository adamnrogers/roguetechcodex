import { useQuery } from '@tanstack/vue-query'
import { computed, type Ref } from 'vue'
import { apiFetch } from './useApi'

export interface SearchHit {
  id: string
  name: string
  subtitle: string
  result_type: string
  variant_id?: string
}

export interface SearchResponse {
  q: string
  chassis: SearchHit[]
  gear: SearchHit[]
}

export interface SearchPageResponse {
  total: number
  page: number
  page_size: number
  results: SearchHit[]
}

export function useGlobalSearch(query: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ['search', query.value]),
    queryFn: () => apiFetch<SearchResponse>('/api/v1/search', { q: query.value }),
    enabled: computed(() => query.value.length >= 2),
    staleTime: 5 * 60 * 1000,
  })
}
