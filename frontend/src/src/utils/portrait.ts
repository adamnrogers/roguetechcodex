export function portraitUrl(icon: string | null | undefined): string | null {
  if (!icon) return null
  return `/portraits/${icon.toLowerCase()}.png`
}
