/**
 * Convert a raw tag/ID string into human-readable text.
 *
 * Handles: camelCase, underscores, hyphens, and mixed-case identifiers.
 *   "ClanWolfInExile"      → "Clan Wolf In Exile"
 *   "aurigandirectorate"   → "Aurigandirectorate"  (no word boundaries to split)
 *   "clan_invasion"        → "Clan Invasion"
 *   "ClanInvasion3061"     → "Clan Invasion 3061"
 */
export function humanizeTag(raw: string): string {
  return raw
    .replace(/[_\-]/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/([A-Z]{2,})([A-Z][a-z])/g, '$1 $2')
    .replace(/([a-zA-Z])(\d{2,})/g, '$1 $2')
    .replace(/\s{2,}/g, ' ')
    .trim()
    .replace(/\b\w/g, c => c.toUpperCase())
}

function splitIdWords(s: string): string[] {
  return s.replace(/([a-z])([A-Z])/g, '$1 $2').split(/[\s_]+/).filter(Boolean)
}

export function gearQualifier(id: string, uiName: string): string | null {
  const prefixes = ['Quirk_', 'Weapon_', 'Gear_', 'emod_', 'Ammo_']
  let rest = id
  for (const p of prefixes) {
    if (id.startsWith(p)) { rest = id.slice(p.length); break }
  }
  const nameWordSet = new Set(splitIdWords(uiName).map(w => w.toLowerCase()))
  const extra = splitIdWords(rest).filter(w => !nameWordSet.has(w.toLowerCase()))
  if (!extra.length) return null
  return extra.map(w => w[0].toUpperCase() + w.slice(1)).join(' ')
}

/**
 * Convert a NoBiome_* chassis tag into a human-readable biome name.
 *   "NoBiome_lunarVacuum"   → "Lunar Vacuum"
 *   "NoBiome_martianVacuum" → "Martian Vacuum"
 */
export function humanizeBiomeTag(tag: string): string {
  const body = tag.startsWith('NoBiome_') ? tag.slice('NoBiome_'.length) : tag
  return humanizeTag(body)
}

/**
 * Maps raw faction tags to canonical display names.
 * All keys are lowercase - canonicalizeFaction uses case-insensitive lookup,
 * so both "clanwolf" and "ClanWolf" resolve correctly.
 *
 * Era suffixes (3025, 3031, 3050, 3150, etc.) are stripped at lookup time so
 * "kurita3031" → strips to "kurita" → 'Draconis Combine'. Only add an era-
 * suffixed key here when the era variant resolves to a DIFFERENT display name
 * than its base faction (e.g. ClanSeaFox3150 ≠ ClanDiamondShark).
 */
const FACTION_MAP: Record<string, string> = {
  // ── Inner Sphere great houses ───────────────────────────────────────────
  davion:                       'Federated Suns',
  steiner:                      'Lyran Commonwealth',
  kurita:                       'Draconis Combine',
  liao:                         'Capellan Confederation',
  marik:                        'Free Worlds League',
  marikstewart:                 'Free Worlds League',
  republic:                     'Republic of the Sphere',
  federatedcommonwealth:        'Federated Commonwealth',

  // ── Periphery states ────────────────────────────────────────────────────
  taurianconcordat:             'Taurian Concordat',
  calderonprotectorate:         'Calderon Protectorate',
  magistracyofcanopus:          'Magistracy of Canopus',
  magistracycentrella:          'Magistracy Centrella',
  marian:                       'Marian Hegemony',
  illyrian:                     'Illyrian Palatinate',
  lothian:                      'Lothian League',
  outworld:                     'Outworlds Alliance',
  rasalhague:                   'Free Rasalhague Republic',
  rasalhaguedominion:           'Rasalhague Dominion',
  circinus:                     'Circinus Federation',
  oberon:                       'Oberon Confederation',
  newoberonconfederation:       'New Oberon Confederation',
  tortuga:                      'Tortuga Dominions',
  chainelane:                   'Chain Lane Pirates',
  valkyrate:                    'Valkyrate',
  aurigandirectorate:           'Aurigan Directorate',
  auriganrestoration:           'Aurigan Restoration',
  auriganpirates:               'Aurigan Pirates',
  auriganmercenaries:           'Aurigan Mercenaries',
  hanse:                        'Hanse Davion Forces',
  ives:                         'St. Ives Compact',
  froncreaches:                 'Fronc Reaches',
  filtveltcoalition:            'Filtvelt Coalition',
  galateanleague:               'Galatean League',
  alynamercantileleague:        'Alyina Mercantile League',
  arcroyal:                     'Arc-Royal',
  arcroyal_libertycoalition:    'Arc-Royal Liberty Coalition',
  arcroyllibertycoalition:      'Arc-Royal Liberty Coalition',
  tamarindabbey:                'Tamarind Abbey',
  tamarpact:                    'Tamar Pact',
  orienteprotectorate:          'Oriente Protectorate',
  regulanfiefs:                 'Regulan Fiefs',
  duchyofandurien:              'Duchy of Andurien',
  rimcommonality:               'Rim Commonality',
  rim:                          'Rim',
  rimterritories:               'Rim Territories',
  rimworldsrepublic:            'Rim Worlds Republic',
  ferriscollective:             'Ferris Collective',
  timbuktucollective:           'Timbuktu Collective',
  vespermarches:                'Vesper Marches',
  republicofthebarrens:         'Republic of the Barrens',
  ragnarokunion:                'Ragnarok Union',
  amarisempire:                 'Amaris Empire',
  terranhegemony:               'Terran Hegemony',
  tikonovfreerepublic:          'Tikonov Free Republic',
  finmarkfreerepublic:          'Finmark Free Republic',
  delphi:                       'New Delphi Compact',
  elysia:                       'Elysia',
  jarnfolk:                     'Jarnfolk',
  axumite:                      'Axumite Providence',
  castile:                      'Kingdom of Castile',
  kitteryprefecture:            'Kittery Prefecture',
  havens:                       'Haven Worlds',
  nautilus:                     'Nautilus',
  umayyadcaliphate:             'Umayyad Caliphate',
  majestymetals:                'Majesty Metals',
  sldf:                         'SLDF',
  sldfinexile:                  'SLDF in Exile',

  // ── Clans ────────────────────────────────────────────────────────────────
  clansgeneric:                 'Clans (Generic)',
  clanwolf:                     'Clan Wolf',
  clanwolfinexile:              'Clan Wolf-in-Exile',
  wolfempire:                   'Wolf Empire',
  clanjadefalcon:               'Clan Jade Falcon',
  clanghostbear:                'Clan Ghost Bear',
  ghostbeardominion:            'Ghost Bear Dominion',
  clansmokejaguar:              'Clan Smoke Jaguar',
  clansnowraven:                'Clan Snow Raven',
  ravenalliance:                'Raven Alliance',
  clanicehellion:               'Clan Ice Hellion',
  clanhellshorses:              'Clan Hell\'s Horses',
  clandiamondshark:             'Clan Diamond Shark',
  clanseafox:                   'Clan Sea Fox',
  ClanSeaFox3150:               'Clan Sea Fox',
  clannovacat:                  'Clan Nova Cat',
  clanprotectorate:             'Clan Nova Cat Protectorate',
  clanstaradder:                'Clan Star Adder',
  clansteelviper:               'Clan Steel Viper',
  clancoyote:                   'Clan Coyote',
  clancloudcobra:               'Clan Cloud Cobra',
  clanfiremandrill:             'Clan Fire Mandrill',
  clangoliathscorpion:          'Clan Goliath Scorpion',
  escorpionimperio:             'Escorpión Imperio',
  scorpionempire:               'Scorpion Empire',
  clanburrock:                  'Clan Burrock',
  clanbloodspirit:              'Clan Blood Spirit',
  clanstonelion:                'Clan Stone Lion',
  clanwidowmaker:               'Clan Widowmaker',
  clanwolverine:                'Clan Wolverine',
  clanmongoose:                 'Clan Mongoose',
  minnesotatribe:               'Minnesota Tribe',
  darkcaste:                    'Dark Caste',
  society:                      'The Society',
  greenghosts:                  'Green Ghosts',
  shadowdivisions:              'Shadow Divisions',

  // ── Other factions ──────────────────────────────────────────────────────
  comstar:                      'ComStar',
  wordofblake:                  'Word of Blake',
  solaris7:                     'Solaris VII',

  // ── Mercenaries & independent units ────────────────────────────────────
  kellhounds:                   'Kell Hounds',
  graydeathlegion:              'Gray Death Legion',
  blackwidowcompany:            'Black Widow Company',
  masonsmarauders:              'Mason\'s Marauders',
  marauders:                    'Marauders',
  steelbeast:                   'Steel Beast',
  redhareregiment:              'Red Hare Regiment',
  razorbackmercs:               'Razorback Mercs',
  hostilemercenaries:           'Hostile Mercenaries',
  flakjackals:                  'Flak Jackals',
  emeralddawn:                  'Emerald Dawn',
  siantriumphant:               'Sian Triumphant',
  housenakano:                  'House Nakano',
  housekhulan:                  'House Khulan',
  edcorbu:                      'Ed Corbu\'s Unit',
  securitysolutionsinc:         'Security Solutions Inc.',
  paladinprotectionllc:         'Paladin Protection LLC',
  baumanngroup:                 'Baumann Group',
  bountyhunterassociates:       'Bounty Hunter Associates',
  betrayers:                    'Betrayers',
  profhorvat:                   'Prof. Horvat\'s Unit',
  selfemployed:                 'Self-Employed',
  selfemployed_yang:            'Yang\'s Workshop',
  mercenaryreviewboard:         'Mercenary Review Board',

  // ── Locals / pirates / misc ─────────────────────────────────────────────
  locals:                       'Locals',
  localsbrockwayrefugees:       'Brockway Refugees',
  blackcalderadefense:          'Black Caldera Defense',
  blackcalderadefense_hidden:   'Black Caldera Defense',
}

/**
 * Tags that are system/metadata flags, not faction affiliations.
 * Lookup is case-insensitive, so "nofaction" and "NoFaction" both match.
 */
const SYSTEM_TAGS = new Set([
  'no_rp_tool',
  'skip_heatcheck',
  'skip_aerospace_tool',
  'nosalvage',
  'wikiignore',
  'wikiwl',
  'wikibl',
  'invalid_unset',
  'faction_employer',
  'faction_neutral',
  'faction_target',
  'faction_targetsally',
  'contract_drone_uav_large',
  'contract_drone_uav_small',
  'owner',
  'player1smercunit',
  'player2smercunit',
  'superheavy',
  'tools_weight_class_assault',
  'tools_weight_class_light',
  'tools_skip_ammo_check',
  'tools_skip_slots_adjust',
  'nofaction',
  'unknown',
  'roguepirates',
  'unit_convoy_cargo',
  'unit_convoy_command',
  'unit_convoy_medical',
  'unit_convoy_technical',
  'unit_convoy_troops',
  'for_sweetpoppajellyroll',
  'thebabayiscanonicallyacombatvehicleescapepod',
  'this damn thing is at it\'s armor limit of 900 points',
])

// Derived at module load - avoids per-call Object.entries overhead.
const FACTION_MAP_LOWER: Record<string, string> = Object.fromEntries(
  Object.entries(FACTION_MAP).map(([k, v]) => [k.toLowerCase(), v])
)

/**
 * Canonical display name for a raw faction tag.
 * Returns null for system/metadata tags that should not appear in the UI.
 *
 * Lookup order:
 *   1. Exact match in FACTION_MAP
 *   2. Case-insensitive match (handles "ClanWolf" vs "clanwolf")
 *   3. Strip trailing 4-digit era year and retry (handles "kurita3031" → "kurita")
 *   4. Fall through to humanizeTag
 */
export function canonicalizeFaction(raw: string): string | null {
  const lower = raw.toLowerCase()
  if (SYSTEM_TAGS.has(lower)) return null

  if (raw in FACTION_MAP) return FACTION_MAP[raw]
  if (lower in FACTION_MAP_LOWER) return FACTION_MAP_LOWER[lower]

  // Strip trailing 4-digit era year (3025, 3031, 3050, 3150, …) and retry
  const base = raw.replace(/\d{4}$/, '')
  if (base.length && base !== raw) {
    const baseLower = base.toLowerCase()
    if (base in FACTION_MAP) return FACTION_MAP[base]
    if (baseLower in FACTION_MAP_LOWER) return FACTION_MAP_LOWER[baseLower]
  }

  return humanizeTag(raw)
}

/**
 * Humanize a source_mod path like "Eras/ClanInvasion3061".
 * Shows the last path segment only, humanized.
 *   "Eras/ClanInvasion3061"      → "Clan Invasion 3061"
 *   "Core/RogueTechCore"         → "Rogue Tech Core"
 *   "DLC/RogueHeavyMetalModule"  → "Rogue Heavy Metal Module"
 */
export function humanizeMod(sourceMod: string): string {
  const last = sourceMod.split('/').pop() ?? sourceMod
  return humanizeTag(last)
}
