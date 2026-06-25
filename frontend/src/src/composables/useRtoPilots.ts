import { useQuery } from '@tanstack/vue-query'
import { apiFetch } from './useApi'

export interface RtoPilotTag {
  tag: string
  label: string | null
  description: string | null
}

export interface RtoPilotRef {
  id: string
  name: string | null
}

export interface RtoPilotRequirements {
  hiring_requirements: string[]
  hiring_visibility_requirements: string[]
  required_system_owner: string[]
  required_system_core_ids: string[]
  required_pilot_ids: RtoPilotRef[]
  conflicting_pilot_ids: RtoPilotRef[]
}

export interface RtoPilotDetail {
  id: string
  ui_name: string
  first_name: string | null
  last_name: string | null
  callsign: string | null
  gender: string | null
  faction: string | null
  age: number | null
  details: string | null
  icon: string | null
  can_pilot: string[]
  tags: RtoPilotTag[]
  requirements: RtoPilotRequirements | null
  source_mod: string | null
}

export function useRtoPilots() {
  return useQuery({
    queryKey: ['rto-pilots'],
    queryFn: () => apiFetch<RtoPilotDetail[]>('/api/v1/rto-pilots'),
    staleTime: 10 * 60 * 1000,
  })
}
