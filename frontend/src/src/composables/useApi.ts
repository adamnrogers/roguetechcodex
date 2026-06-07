export const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

export async function apiFetch<T>(path: string, params?: Record<string, any>): Promise<T> {
  const url = new URL(API_BASE + path)
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v === null || v === undefined || v === '') return
      if (Array.isArray(v)) {
        v.forEach(item => url.searchParams.append(k, String(item)))
      } else {
        url.searchParams.set(k, String(v))
      }
    })
  }
  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json()
}
