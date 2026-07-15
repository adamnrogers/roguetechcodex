export const API_BASE = import.meta.env.VITE_API_BASE ?? ''

// eslint-disable-next-line @typescript-eslint/no-explicit-any -- caller-supplied query params are a heterogeneous string/number/boolean/array bag
export async function apiFetch<T>(path: string, params?: Record<string, any>): Promise<T> {
  const base = API_BASE || window.location.origin
  const url = new URL(base + path)
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v === null || v === undefined || v === '') return
      if (Array.isArray(v)) {
        v.forEach((item) => url.searchParams.append(k, String(item)))
      } else {
        url.searchParams.set(k, String(v))
      }
    })
  }
  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json()
}
