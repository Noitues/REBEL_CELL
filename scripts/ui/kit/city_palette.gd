class_name CityPalette
extends RefCounted
## City-only tones (ART_BIBLE §9, §2 CITY; art pass W7). The city's neon inks are the five
## Palette tokens (CRT_AMBER, NEON_VIOLET, CELL_PINK, NET_CYAN, CORP_SOLACE); the tones here
## are the building masses, ground, slate paint, haze and small light sources that exist only
## inside the CITY material and never carry a UI role (§3.3). Every value is named; views
## never write a literal colour. (The static visual lint counts this file like a token file:
## its colours live here so that neon_city.gd and the city layers carry none.)

## §9.1 / STYLE_GUIDE 1.1: the five neon inks, in NeonCity.INKS order (amber, violet, pink,
## cyan, green). The per-ink glow gains in content/config/city_look.tres follow this order.
const INKS: Array[Color] = [Palette.CRT_AMBER, Palette.NEON_VIOLET, Palette.CELL_PINK, Palette.NET_CYAN, Palette.CORP_SOLACE]

## §9.1 building masses: black, dark grey-blue, dark grey.
const FILLS: Array[Color] = [Color("#06070B"), Color("#141B2C"), Color("#1D2027")]
## §9.1 the ground plane between lots, and the street surface (wet asphalt at night).
const GROUND := Color("#0A0C14")
const STREET := Color("#050609")
## §9.1 the lit face of a mass (light from the signs above).
const FACE_LIGHT := Color("#2A3350")
## §9.1 the paler ink sets' tints (design review options: FADED PRINT, COOL HAZE).
const INK_TINT_FADED := Color("#C9BFD9")
const INK_TINT_COOL := Color("#D6F2FF")
## §9.1 painted slate (STYLE_GUIDE 1.1 "tinted-slate buildings"): the wall base tones (light,
## dark), the cool light the walls catch at the top, and the concrete-grain speck tone.
const SLATE_TONES: Array[Color] = [Color("#4A556F"), Color("#232A3A")]
const SLATE_LIGHT := Color("#B8C4DE")
const SLATE_GRAIN := Color("#8A97C8")
## §9.1 ink shadow (hairlines, recesses, ledges): pure black at the alpha each use gives it,
## and the near-black of a pen hatch.
const SHADE := Color(0, 0, 0)
const HAIR_DARK := Color("#030305")
## §9.2 the white-hot core of a traffic dash and of a window pane's hottest pixels.
const HOT_CORE := Color("#FFFFFF")

## §9.1 lighting: the colour of the haze bands (a cold violet-blue smog lit from below).
const HAZE := Color("#3A3F78")
## §9.2 aircraft navigation lights (port red, starboard/strobe white). City-only: never HARM.
const NAV_RED := Color("#FF2E4C")
const NAV_WHITE := Color("#E8F0FF")
## §9.3 searchlight beams (NOTICED): a cold, slightly blue white.
const SEARCHLIGHT := Color("#CFE3FF")
## §9.3 FLAGGED rim flicker on corp buildings: police red and police blue. City-only tones
## (the red is not HARM: it lights buildings, it never marks damage).
const POLICE_RED := Color("#FF2238")
const POLICE_BLUE := Color("#2A6BFF")
## §9.4 the silhouette pre-render: the masses' faces (dark, lit) and its window glow tone
## before the context grade.
const SIL_FACE_DARK := Color("#070A16")
const SIL_FACE_LIT := Color("#111830")
const SIL_ROOF := Color("#18203D")
const SIL_WINDOW := Color("#FFC872")
