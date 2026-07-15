// Maps known Unity RTF hex colours (first 6 digits, uppercase) to dark-theme equivalents.
// 'inherit' means render as plain text colour (no span needed).
// Colours not present in this map are stripped (tag removed, text preserved).
const COLOUR_MAP: Record<string, string | 'inherit'> = {
  // Reds
  FF0000: '#c47a7a',
  FF4040: '#c47a7a',
  D0021B: '#c47a7a',
  CC1C12: '#c47a7a',
  E11919: '#c47a7a',
  E62E00: '#c47a7a',
  FF0066: '#c47a7a',
  // Blues
  '0000FF': '#58a6ff',
  '4040FF': '#58a6ff',
  '17A2B8': '#58a6ff',
  '3366FF': '#58a6ff',
  '0064E6': '#58a6ff',
  '099FF2': '#58a6ff',
  '00FFFF': '#58a6ff',
  // Greens
  '00FF00': '#3fb950',
  '008000': '#3fb950',
  '28A745': '#3fb950',
  '15DF37': '#3fb950',
  '2AAD3B': '#3fb950',
  // Yellows / Gold / Orange
  FFFF00: '#e3b341',
  FFD700: '#e3b341',
  FFA500: '#e3b341',
  FF8000: '#e3b341',
  FFCC00: '#e3b341',
  FFBA01: '#e3b341',
  FFEF00: '#e3b341',
  F79232: '#e3b341',
  F5B247: '#e3b341',
  // Whites
  FFFFFF: 'inherit',
}

// Replaces Unity RTF <color=#RRGGBB[AA]>…</color> tags in an already HTML-escaped string.
// Open tags are matched against COLOUR_MAP; the close tag replacement tracks whether a
// <span> was actually emitted so we don't produce stray </span> for stripped colours.
function applyColourTags(escaped: string): string {
  // Stack of booleans: true = span was emitted, false = tag was stripped
  const spanStack: boolean[] = []

  // Combined pattern matches either an open or close colour tag (already HTML-escaped)
  return escaped.replace(
    /&lt;(\/)?color(?:=#([0-9A-Fa-f]{6,8}))?&gt;/gi,
    (_match, slash: string | undefined, hex: string | undefined) => {
      if (!slash) {
        // Opening tag
        if (!hex) {
          spanStack.push(false)
          return ''
        }
        const key = hex.slice(0, 6).toUpperCase()
        const mapped = COLOUR_MAP[key]
        if (mapped === undefined) {
          spanStack.push(false)
          return ''
        }
        spanStack.push(true)
        if (mapped === 'inherit') {
          return '<span>'
        }
        return `<span style="color:${mapped}">`
      } else {
        // Closing tag
        const emitted = spanStack.pop()
        return emitted ? '</span>' : ''
      }
    },
  )
}

// Mod lore text ("Details") bakes in a "Quirk: <name>" callout line. The quirk's actual
// mechanics (and its affinity, if any) are already surfaced in the Affinity/Component
// Layout sections, so this line is redundant in the description and is stripped here.
const QUIRK_CALLOUT_RE =
  /\n*<b>\s*<color=#[0-9A-Fa-f]{6,8}>\s*Quirk:[^<]*<\/color>\s*<\/b>\n*|\n*<color=#[0-9A-Fa-f]{6,8}>\s*Quirk:[^<]*<\/color>\n*/gi

export function stripQuirkCallout(raw: string): string {
  return raw.replace(QUIRK_CALLOUT_RE, '\n\n')
}

export function renderRichText(raw: string | null | undefined): string {
  if (!raw) return ''
  const escaped = stripQuirkCallout(raw)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;') // escape first
  return applyColourTags(escaped)
    .replace(/&lt;b&gt;/g, '<strong>')
    .replace(/&lt;\/b&gt;/g, '</strong>')
    .replace(/&lt;i&gt;/g, '<em>')
    .replace(/&lt;\/i&gt;/g, '</em>')
    .replace(/\n/g, '<br>')
}
