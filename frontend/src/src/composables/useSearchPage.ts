import { useQuery } from '@tanstack/vue-query'
import { computed, type Ref } from 'vue'
import { apiFetch } from './useApi'
import type { SearchPageResponse } from './useGlobalSearch'

export function useChassisSearch(query: Ref<string>, page: Ref<number>) {
  return useQuery({
    queryKey: computed(() => ['search/chassis', query.value, page.value]),
    queryFn: () =>
      apiFetch<SearchPageResponse>('/api/v1/search/chassis', {
        q: query.value,
        page: page.value,
        page_size: 20,
      }),
    enabled: computed(() => query.value.length >= 2),
    staleTime: 0,
  })
}

export function useGearSearch(query: Ref<string>, page: Ref<number>) {
  return useQuery({
    queryKey: computed(() => ['search/gear', query.value, page.value]),
    queryFn: () =>
      apiFetch<SearchPageResponse>('/api/v1/search/gear', {
        q: query.value,
        page: page.value,
        page_size: 20,
      }),
    enabled: computed(() => query.value.length >= 2),
    staleTime: 0,
  })
}
