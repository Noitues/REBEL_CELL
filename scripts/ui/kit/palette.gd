class_name Palette
extends RefCounted
## Colour tokens, glyphs and fonts from STYLE_GUIDE 2-4. Views never hard-code colours.

const CELL_PINK := Color("#FF3DA8")
const CELL_ACID := Color("#D4FF00")
## ANIM-R3 B6: the Cell's territory (claimed Sites, its network links, the district tint and
## the CLAIMED marks): the Cell's acid, never `cell_pink` (pink is damage on every map and
## in every fight, so a pink claim read as a hit). At least 40 degrees of hue from every
## corporation's colour (Meridian's orange is the nearest; ANIM-R4 H9 corrected "furthest"),
## so it is always carried with a non-colour mark too (spray ring, hatch, stamp word).
const CELL_TURF := Color("#D4FF00")
const PAPER := Color("#F2EEE4")
const PAPER_ALT := Color("#E9E4D6")
const INK := Color("#111111")
const NET_CYAN := Color("#5CE1FF")
const NET_BG_INNER := Color("#0D1440")
const NET_BG_OUTER := Color("#02030A")
## ART_BIBLE v2 §2.4 corporation kits (LOCKED, round 18 values; ART-1 1A): each corporation
## owns hue + material + crest + landmark, never hue alone, and a corp hue is never used for
## a §2.2 UI role. Greyscale pair: the corp's material and crest (and its name in words).
## Solace: leaf green, kept off the Cell's lime (Solace never appears on a link or ring).
const CORP_SOLACE := Color("#96FF46")
## Meridian Freight: orange.
const CORP_MERIDIAN := Color("#FF8C1A")
## Halcyon Civic: violet.
const CORP_HALCYON := Color("#B06EFF")
## Orbital Commons: ice white (near TEXT_HI: its material and crest MUST carry it).
const CORP_ORBITAL := Color("#CDF0FF")
## REBEL_CELL (DISPATCH): a deep blood red, clearly apart from the Cell pink in hue and
## lightness (H20 #14).
const CORP_REBEL_CELL := Color("#E8141E")
## §2.4 secondary hues (a corp wheel's tier II): Meridian hot red, Solace pink, Halcyon amber,
## Orbital white, REBEL_CELL pale pink (the paled ring colour, so its dashes read).
const CORP_MERIDIAN_2 := Color("#FF2E28")
const CORP_SOLACE_2 := Color("#FF4696")
const CORP_HALCYON_2 := Color("#FFAA28")
const CORP_ORBITAL_2 := Color("#FFFFFF")
const CORP_REBEL_CELL_2 := Color("#FFAAAC")
## §2.4: Solace vehicles, deliberately greener than the Cell's lime.
const CORP_SOLACE_VEHICLE := Color(0.42, 1.0, 0.16)
const CRT_AMBER := Color("#FFB000")
const RESIST_GOLD := Color("#FFD24D")
const DESK_DARK := Color("#1B1D21")
const DESK_METAL := Color("#34383E")
const TAPE := Color(0.95, 0.9, 0.6, 0.55)
## Neon-night look (STYLE_GUIDE 2, "Neon city" row): the isometric city backdrop, the
## terminal panels laid over it and the taped paper notes.
const NIGHT_SKY := Color("#060816")
const NIGHT_BLOCK := Color("#101832")
const NIGHT_BLOCK_LIT := Color("#1C2A55")
const NIGHT_STREET := Color("#0A0E22")
const NEON_VIOLET := Color("#B04DFF")
## §2.1 CRT terminal ("Screens & Data", the Cell's own systems): navy glass rgba(5,13,28,.95),
## a NET_CYAN edge at 78 %, TERMINAL_TEXT lettering.
const TERMINAL_BG := Color(5.0 / 255.0, 13.0 / 255.0, 28.0 / 255.0, 0.95)
## A terminal surface under the pointer (hover): the navy glass lit by its cyan edge (v2: the
## hover is a lit edge, a glow and a caret, never the pink of the committing verb).
const TERMINAL_BG_HOT := Color(10.0 / 255.0, 34.0 / 255.0, 54.0 / 255.0, 0.95)
const TERMINAL_EDGE := Color(NET_CYAN, 0.78)
const TERMINAL_TEXT := Color("#CFF6FF")
## §6.4: the live-number rim (bare Anton: HP, Heat, damage numbers).
const LIVE_NUMBER_RIM := Color("#06060A")
const NOTE_PAPER := Color("#E9DFC6")
const NOTE_PINK := Color("#F4C3CF")
const NOTE_YELLOW := Color("#F2DC7A")
## Softened hot pink for pink card stickers: black text stays readable on it.
const STICKER_PINK := Color("#F5AFCB")
const NOTE_TAPE := Color(0.93, 0.89, 0.78, 0.7)
const SHADOW := Color(0, 0, 0, 0.45)
## "No colour given": a default parameter meaning "use the element's own colour" (never drawn).
const AUTO := Color(0, 0, 0, 0)
## ART-0 audit C1 / D2: the named colours the views used as plain `Color.*` constants are
## tokens here, so the static lint counts every other one.
## Plain white as a multiplier: a modulate, a shader's carrier rect (the shader makes the
## colour), a mask or tile fill, a "no tint" default. Never a white the player reads as one.
const NO_TINT := Color(1, 1, 1, 1)
## Fully transparent: an empty fill (a box that draws only its border).
const CLEAR := Color(0, 0, 0, 0)
## The white of a hot moment: a victory disc flash, a binary bit's white-hot start.
const WHITE_HOT := Color(1, 1, 1, 1)
## High contrast's panel colour behind TEXT_HI (ART_BIBLE §12 "TEXT_HI on #000").
const HC_BG := Color(0, 0, 0, 1)

# --- ART_BIBLE §2.2 semantic tokens (art pass W1, ported in ART-0 E) ----------------------
# A semantic hue means one thing everywhere and is always paired with a glyph, shape or word.
# Views migrate their own call sites in ART-1..12; nothing on main reads these yet.
## Harm: damage taken, losses, costs, LETHAL, refusals (never CELL_PINK).
const HARM := Color("#FF4433")
## Gain: healing, gains, a positive outcome.
const GAIN := Color("#7BE07B")
## HARM and GAIN as ink on paper: the screen hues are too light on paper stock; these meet
## 4.5:1 on every PAPER_STOCKS colour.
const HARM_INK := Color("#AB2E22")
const GAIN_INK := Color("#396739")
## The paper stocks the paper inks are checked against (4.5:1).
const PAPER_STOCKS: Array[Color] = [PAPER, PAPER_ALT, NOTE_PAPER, NOTE_YELLOW]
## Protect: block, shield, evade, guards (the net's neutral cyan).
const PROTECT := NET_CYAN
## Warn: caution (low HP, NOTICED Heat, a pending raid).
const WARN := CRT_AMBER
## Focus: keyboard/pad focus, aim, legal drop zones, the current target.
const FOCUS := CELL_ACID
## Disabled: the outline of an unavailable control (never a faded active colour).
const DISABLED := Color("#6A7080")
## Text on dark: primary.
const TEXT_HI := Color("#F2F6FF")
## Text on dark: secondary.
const TEXT_MID := Color("#AFC0D6")
## Text on dark: tertiary (never for information the player needs).
const TEXT_LO := Color("#7A889C")
## The dim laid behind every glass panel and modal over the city (with SCRIM_BLUR_PX blur).
const SCRIM := Color(0.00784314, 0.0117647, 0.0392157, 0.55)
## The scrim's blur radius in reference pixels.
const SCRIM_BLUR_PX := 6
## Heat FLAGGED band (§2.8): between WARN and HARM.
const HEAT_FLAGGED := Color("#FF7A1A")

# --- ART_BIBLE v2 §2.2 new tokens, §2.6-2.8, §2.10 (ART-1 1A) -------------------------------
## Grease pencil (§1.2, §2.2): yellow = our plan / valid; red = threat / invalid / loss; the
## dark under-shadow that makes the wax read day and night. Paired with: solid (will happen)
## vs dashed (what-if) strokes and the written word.
const PENCIL_PLAN := Color("#FFE200")
const PENCIL_THREAT := Color("#FF1C2C")
const PENCIL_SHADOW := Color(6.0 / 255.0, 3.0 / 255.0, 8.0 / 255.0, 0.85)
## The world Heat tint on maps (§2.2, §2.8).
const HEAT_B := Color("#CE5412")
## Netrun rings (§2.2; Appendix C #22: the run orange until the designer says otherwise).
## Paired with: the ring's glyph and its state word (AVAILABLE / CUT).
const RING_AVAILABLE := Color("#FF8C1A")
const RING_UNAVAILABLE := Color("#F2F6FF")
## "Dim grey" (§2.2 gives no value): the NULL slice grey.
const RING_CUT := Color("#6A6A6A")

## §2.8 Heat colour per band. Paired with: the band word, always printed (never colour
## alone). Heat is never green. PURGE has its own token with HUNTED's look until the art
## gives it one (designer ruling 2026-10-05, five Heat bands).
const HEAT_COOL := TEXT_MID
const HEAT_NOTICED := WARN
const HEAT_HUNTED := HARM
const HEAT_PURGE := HEAT_HUNTED

## §2.6 Daemon trigger families (LOCKED, round 34 phosphors, `fwlib.FAM`). Paired with: each
## Daemon's own sigil and the family word in its tooltip. NULL is the bible's MISS family
## (it fires on the NULL slice, renamed from MISS by the 2026-10-05 ruling).
const DAEMON_PERFECT := Color("#FFD640")
const DAEMON_NULL := Color("#EC303A")
const DAEMON_TURN := Color("#5CE1FF")
const DAEMON_ACTION := Color("#BA92FF")
const DAEMON_RUN := Color("#96FF6E")
const DAEMON_HEAT := Color("#FF8C3C")
## Family id -> colour (ids lower case, as content will name them).
const DAEMON_FAMILY_COLORS := {
	&"perfect": DAEMON_PERFECT, &"null": DAEMON_NULL, &"turn": DAEMON_TURN,
	&"action": DAEMON_ACTION, &"run": DAEMON_RUN, &"heat": DAEMON_HEAT,
}

## §2.7 rarity (firmware chips and Daemon tiles; round 34 `fwlib.RAR_COL`): common cool white
## LED on gunmetal, uncommon cyan, rare gold. Paired with: pips (1 / 2 / 3, RARITY_PIPS).
const RARITY_COMMON := Color("#D6DEEC")
const RARITY_GUNMETAL := Color("#3A4048")
const RARITY_UNCOMMON := NET_CYAN
const RARITY_RARE := Color("#FFD640")
const RARITY_COLORS: Array[Color] = [RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE]
const RARITY_PIPS: Array[int] = [1, 2, 3]

## §2.10 state chrome. ON / selected: a cyan fill plus a word (lime is focus only, never ON).
const SELECTED := NET_CYAN
## Lettering on a SELECTED (cyan) fill: the terminal's deep navy.
const ON_SELECTED := NET_BG_OUTER
## Two-sticker choice: yellow (top to bottom of the vinyl) = the safe / back-out choice and the
## screen-title stickers; pink = the committing verb; grey vinyl only when disabled (the
## sticker art at STICKER_DISABLED_GREY greyscale).
const STICKER_SAFE := Color("#FFEE60")
const STICKER_SAFE_LOW := Color("#FFB60E")
const STICKER_COMMIT := CELL_PINK
const STICKER_DISABLED_GREY := 0.8
## The die-cut border of a vinyl sticker and its ink keyline (§1.2).
const STICKER_DIE_CUT := Color("#FFFFFF")

## §5.1 "never colour alone": what each meaningful colour token is paired with (a greyscale
## reader gets the same information). The token table test checks every entry is filled.
const PAIRED_WITH := {
	&"HARM": "a down mark / minus sign and the word",
	&"GAIN": "an up mark / plus sign",
	&"HARM_INK": "as HARM, on paper",
	&"GAIN_INK": "as GAIN, on paper",
	&"PROTECT": "the shield / block glyph",
	&"WARN": "the warning word (LOW, NOTICED, RAID PENDING)",
	&"FOCUS": "corner brackets and the > caret (a shape, not a fill)",
	(&"DISABLED"): "a lock or the reason in words; grey vinyl for stickers",
	&"SELECTED": "the ON / selected word beside the fill",
	&"PENCIL_PLAN": "solid vs dashed stroke and the written word",
	&"PENCIL_THREAT": "solid vs dashed stroke and the written word",
	&"RING_AVAILABLE": "the ring's state glyph and word",
	&"RING_UNAVAILABLE": "the ring's state glyph and word",
	&"RING_CUT": "the cut mark and the word CUT",
	&"HEAT_COOL": "the band word COOL",
	&"HEAT_NOTICED": "the band word NOTICED",
	&"HEAT_FLAGGED": "the band word FLAGGED",
	&"HEAT_HUNTED": "the band word HUNTED",
	&"HEAT_PURGE": "the band word PURGE",
	&"HEAT_B": "the Heat value and band word on the HUD",
	&"CORP_*": "the corp's material, crest and name",
	&"CLASS_ACCENTS": "the class portrait, name and hub emblem",
	&"SLICE_*": "the slice's glyph and program word",
	&"DAEMON_*": "the Daemon's own sigil and the family word in its tooltip",
	&"RARITY_*": "1 / 2 / 3 pips",
	&"STICKER_SAFE": "the verb word (CANCEL) and default focus",
	&"STICKER_COMMIT": "the verb word (SEND IT, BURN IT)",
}

## ART_BIBLE v2 §2.9 grease pencil face: Permanent Marker, rendered as wax, for plans and
## threats only (never UI chrome, body text or numbers).
const FONT_PENCIL := "res://assets/fonts/PermanentMarker-Regular.ttf"

# --- ART-1 1B material kit (ART_BIBLE v2 §1.2; round 3 combined_v2 kit palette; the pencil
# inks and the die-cut white are 1A's PENCIL_PLAN / PENCIL_THREAT / PENCIL_SHADOW / STICKER_DIE_CUT)
## Vinyl: the lower stop of the white die-cut's gradient (STICKER_DIE_CUT on top) and the
## adhesive back a peel shows.
const VINYL_WHITE_LO := Color("#EFEDE7")
const VINYL_BACKING := Color("#E0DDD6")
## Vinyl: the printed keyline ink and the darker extrude under it.
const VINYL_INK := Color("#141118")
const VINYL_EXTRUDE := Color("#09080C")
## Kraft note-card stock and its fibres.
const KRAFT := Color("#B68E5C")
const KRAFT_FIBRE := Color("#5F4224")
## Sticker word fills (kit gradients, top to bottom): the Cell's verbs, threat words, ours.
const STICKER_FILL_PINK: Array[Color] = [Color("#FF60AC"), Color("#DE1270")]
const STICKER_FILL_RED: Array[Color] = [Color("#FF5850"), Color("#CC1416")]
const STICKER_FILL_YELLOW: Array[Color] = [STICKER_SAFE, STICKER_SAFE_LOW]
## CRT terminal glass: the navy top and bottom of the panel's glass.
const CRT_GLASS_TOP := Color("#0B1630")
const CRT_GLASS_BOTTOM := Color("#050A1A")
## Corp paper: the letterhead rule and the typewriter ink.
const PAPER_TYPE_INK := Color("#1E1A16")
## The near-opaque scrim laid behind a decrypted holo panel (§1.2: 0.88).
const HOLO_SCRIM := Color(0.00784314, 0.0117647, 0.0392157, 0.88)
## Toon ink lines (3D city and props).
const TOON_INK := Color("#0C0A16")

## §2.9 sticker / display face: Anton (stickers, titles, stamps, bare live numbers).
const FONT_DISPLAY :="res://assets/fonts/Anton-Regular.ttf"
## §2.9 terminal face: Share Tech Mono (the Cell's systems).
const FONT_MONO := "res://assets/fonts/ShareTechMono-Regular.ttf"
## ART_BIBLE §2.9 body face: IBM Plex Sans Condensed (OFL) for text blocks over 3 lines and
## tooltips; the Medium weight for emphasis (RichTextLabel bold).
const FONT_BODY := "res://assets/fonts/IBMPlexSansCondensed-Regular.ttf"
const FONT_BODY_MEDIUM := "res://assets/fonts/IBMPlexSansCondensed-Medium.ttf"
## ART_BIBLE §2.9 corp paper face: Courier Prime (OFL) Regular for fields, Bold for titles.
const FONT_PAPER := "res://assets/fonts/CourierPrime-Regular.ttf"
const FONT_PAPER_BOLD := "res://assets/fonts/CourierPrime-Bold.ttf"
## Every face the game ships.
const FONT_FACES: Array[String] = [FONT_PENCIL, FONT_DISPLAY, FONT_MONO, FONT_BODY, FONT_BODY_MEDIUM, FONT_PAPER, FONT_PAPER_BOLD]
## The MSDF switch every face's tracked `.import` file carries (ART_BIBLE §2.9: every face
## imports as MSDF). On since ART-1 1A (with the layouts it moved: whole lines are measured
## with `UiTheme.line_px`, MSDF heights are fractional).
const FONTS_MSDF := true
## The MSDF field range each face imports with (6-8 px outlines stay inside the field).
const FONTS_MSDF_RANGE := 16

## A glyph for every slice type (STYLE_GUIDE 4): readable without colour.
const SLICE_GLYPHS := {
	RC.SliceType.SHIM: "▲", RC.SliceType.OVERFLOW: "✦", RC.SliceType.DEFRAG: "■", RC.SliceType.DETOUR: "◇",
	RC.SliceType.SANDBOX: "⬢", RC.SliceType.TROJAN: "⬡", RC.SliceType.HOTFIX: "✚", RC.SliceType.INFECT: "◈",
	RC.SliceType.NULL: "✕",
}
const SLICE_NAMES := {
	RC.SliceType.SHIM: "SHIM", RC.SliceType.OVERFLOW: "OVFL", RC.SliceType.DEFRAG: "DFRG", RC.SliceType.DETOUR: "DTOR", # TR
	RC.SliceType.SANDBOX: "SBOX", RC.SliceType.TROJAN: "TRJN", RC.SliceType.HOTFIX: "HFIX", RC.SliceType.INFECT: "INFC", # TR
	RC.SliceType.NULL: "NULL", # TR
}
## Whole words for the tags over the spinners (H21: new players read DEF / AFL / BLK as
## noise).
const SLICE_WORDS := {
	RC.SliceType.SHIM: "SHIM", RC.SliceType.OVERFLOW: "OVERFLOW", RC.SliceType.DEFRAG: "DEFRAG", RC.SliceType.DETOUR: "DETOUR", # TR
	RC.SliceType.SANDBOX: "SANDBOX", RC.SliceType.TROJAN: "TROJAN", RC.SliceType.HOTFIX: "HOTFIX", RC.SliceType.INFECT: "INFECT", # TR
	RC.SliceType.NULL: "NULL", # TR
}
## A corporation's own word for a program on its wheels (DECISIONS "Designer rulings: names
## for M14", D3 / D4): Meridian's OVERFLOW shows as AIRMAIL, Solace's HOTFIX as GROWTH.
const CORP_SLICE_WORDS := {
	&"meridian": {RC.SliceType.OVERFLOW: "AIRMAIL"}, # TR
	&"solace": {RC.SliceType.HOTFIX: "GROWTH"}, # TR
}


## The whole word for slice type `type` on a wheel of corporation `corporation_id` ("" for the
## Cell's own): the corporation's word when it has one, else SLICE_WORDS. Untranslated (a key).
static func slice_word(type: int, corporation_id: StringName = &"") -> String:
	var own: Dictionary = CORP_SLICE_WORDS.get(corporation_id, {})
	return String(own.get(type, SLICE_WORDS.get(type, "?")))


const STATUS_WORDS := {RC.Status.NONE: "", RC.Status.CORRUPTED: "CORRUPTED", RC.Status.OVERCLOCKED: "OVERCLOCKED", RC.Status.ENCRYPTED: "ENCRYPTED", RC.Status.PARASITE: "PARASITE"} # TR
## How well a needle lands, in plain words.
const TIER_WORDS := {RC.PrecisionTier.PERFECT: "perfect aim", RC.PrecisionTier.GOOD: "good aim", RC.PrecisionTier.WEAK: "half power"} # TR
## A glyph and tag for every status, also readable without colour.
const STATUS_GLYPHS := {RC.Status.NONE: "", RC.Status.CORRUPTED: "☠", RC.Status.OVERCLOCKED: "⚡", RC.Status.ENCRYPTED: "⌗", RC.Status.PARASITE: "✺"}
const STATUS_TAGS := {RC.Status.NONE: "", RC.Status.CORRUPTED: "CRPT", RC.Status.OVERCLOCKED: "OVCL", RC.Status.ENCRYPTED: "ENC", RC.Status.PARASITE: "PRST"}
const TIER_NAMES := {RC.PrecisionTier.PERFECT: "PERFECT", RC.PrecisionTier.GOOD: "GOOD", RC.PrecisionTier.WEAK: "WEAK"} # TR

## Corporation glow colour (each corporation has its own; see STYLE_GUIDE).
static func corp_color(corporation_id: StringName) -> Color:
	match corporation_id:
		&"solace":
			return CORP_SOLACE
		&"meridian":
			return CORP_MERIDIAN
		&"halcyon":
			return CORP_HALCYON
		&"orbital":
			return CORP_ORBITAL
		&"rebel_cell":
			return CORP_REBEL_CELL
		_:
			return NET_CYAN


## A corporation's secondary hue (§2.4, its wheels' tier II): TEXT_HI for an unknown id.
static func corp_secondary(corporation_id: StringName) -> Color:
	match corporation_id:
		&"solace":
			return CORP_SOLACE_2
		&"meridian":
			return CORP_MERIDIAN_2
		&"halcyon":
			return CORP_HALCYON_2
		&"orbital":
			return CORP_ORBITAL_2
		&"rebel_cell":
			return CORP_REBEL_CELL_2
		_:
			return TEXT_HI


## ART_BIBLE §2.3 slice colours: the colour means slice type on any wheel, not its owner.
const SLICE_HOTFIX := Color("#7BE07B")
const SLICE_INFECT := Color("#C85AFF")
const SLICE_TROJAN := Color("#B08CFF")
const SLICE_NULL := Color("#6A6A6A")


## The colour of a slice type (§2.3): attack/crit pink, defrag/sandbox cyan, evade/heal
## green, afflict violet, trojan lilac, null grey.
static func slice_color(type: int) -> Color:
	match type:
		RC.SliceType.SHIM, RC.SliceType.OVERFLOW:
			return CELL_PINK
		RC.SliceType.DEFRAG, RC.SliceType.SANDBOX:
			return NET_CYAN
		RC.SliceType.DETOUR, RC.SliceType.HOTFIX:
			return SLICE_HOTFIX
		RC.SliceType.INFECT:
			return SLICE_INFECT
		RC.SliceType.TROJAN:
			return SLICE_TROJAN
		_:
			return SLICE_NULL


## ART_BIBLE §2.5 class accents, keyed by the class content id (content/classes/*.tres).
## Accents sit only on the class's portrait, hub glow, beacon and dossier stripe. v2 values
## (LOCKED round 22 `class_colours_v2`, round 38 portraits; ART-1 1A, App. C #4).
const CLASS_ACCENTS := {
	&"breaker": CELL_PINK,
	&"wrecker": Color("#FF6E32"),
	&"ghost": Color("#5BE0FF"),
	&"phantom": Color("#DBC1FF"),
	&"rigger": Color("#7AE07A"),
	&"overclocker": Color("#FFB040"),
	&"botnet": Color("#6072FF"),
	&"hivemind": Color("#C659FF"),
}
## The accent for a class id nobody listed (a new or modded class): the neutral text tone.
const CLASS_ACCENT_FALLBACK := TEXT_MID


## The accent colour of a class (CLASS_ACCENT_FALLBACK for an unknown id).
static func class_accent(class_id: StringName) -> Color:
	return CLASS_ACCENTS.get(class_id, CLASS_ACCENT_FALLBACK)


# --- ART_BIBLE §2.8 HP and Heat scales, contrast ---------------------------------------------
## HP at or above this fraction of max reads GAIN; below it, WARN.
const HP_WARN_BELOW := 0.5
## HP below this fraction of max reads HARM.
const HP_HARM_BELOW := 0.25
## Heat colour per band: COOL, NOTICED, FLAGGED, HUNTED, PURGE (§2.8; GDD 4.3). Heat is never
## green. PURGE has its own token (HEAT_PURGE) with HUNTED's look until the art gives it one (designer ruling
## 2026-10-05, five Heat bands).
const HEAT_BAND_COLORS: Array[Color] = [HEAT_COOL, HEAT_NOTICED, HEAT_FLAGGED, HEAT_HUNTED, HEAT_PURGE]
## The content registry's script, for its config path only (Palette also compiles in `-s`
## tool scripts, before any autoload exists).
const _REGISTRY_SCRIPT := preload("res://scripts/autoload/content_registry.gd")
## WCAG 2.x relative-luminance weights and flare term (the standard's own constants).
const _WCAG_R := 0.2126
const _WCAG_G := 0.7152
const _WCAG_B := 0.0722
const _WCAG_FLARE := 0.05

static var _heat_levels: Array[int] = []


## The HP colour for `frac` = hp / max_hp: GAIN, then WARN under HP_WARN_BELOW, then HARM
## under HP_HARM_BELOW.
static func hp_color(frac: float) -> Color:
	if frac < HP_HARM_BELOW:
		return HARM
	if frac < HP_WARN_BELOW:
		return WARN
	return GAIN


## The Heat band for `heat`: how many band levels it has reached (0 COOL, 1 NOTICED,
## 2 FLAGGED, 3 HUNTED, 4 PURGE, capped at the last band). `major_levels` are the ascending
## band levels (`CampaignConfigData.heat_band_levels()`: the MAJOR levels and the PURGE
## level); empty reads them from the campaign config, so the bands never duplicate the
## game's numbers.
static func heat_band(heat: int, major_levels: Array[int] = []) -> int:
	var levels := major_levels if not major_levels.is_empty() else _config_heat_levels()
	var band := 0
	for level in levels:
		if heat >= level:
			band += 1
	return mini(band, HEAT_BAND_COLORS.size() - 1)


## The Heat colour for `heat`: COOL TEXT_MID, NOTICED WARN, FLAGGED HEAT_FLAGGED, HUNTED
## and PURGE HARM. Never GAIN. `major_levels` as in heat_band().
static func heat_color(heat: int, major_levels: Array[int] = []) -> Color:
	return HEAT_BAND_COLORS[heat_band(heat, major_levels)]


## The Heat band levels from the campaign config (read once; the Resource is never changed).
static func _config_heat_levels() -> Array[int]:
	if _heat_levels.is_empty():
		var cfg := load(_REGISTRY_SCRIPT.CONFIG_PATH) as CampaignConfigData
		if cfg != null:
			_heat_levels = cfg.heat_band_levels()
	return _heat_levels


## WCAG 2.x relative luminance of `c` (sRGB, alpha ignored).
static func luminance(c: Color) -> float:
	var l := c.srgb_to_linear()
	return _WCAG_R * l.r + _WCAG_G * l.g + _WCAG_B * l.b


## The WCAG contrast ratio of `a` against `b` (1.0 to 21.0; order doesn't matter). Both are
## read as opaque: composite a translucent colour onto its background with over() first.
static func contrast(a: Color, b: Color) -> float:
	var la := luminance(a)
	var lb := luminance(b)
	return (maxf(la, lb) + _WCAG_FLARE) / (minf(la, lb) + _WCAG_FLARE)


## `fg` alpha-composited over `bg` (Porter-Duff "over", sRGB as the 2D renderer blends),
## e.g. over(city_pixel, SCRIM) for the colour behind a glass panel.
static func over(bg: Color, fg: Color) -> Color:
	return bg.blend(fg)


static var _fonts: Dictionary = {}


## ANIM-R5 P17: lets the cached fonts go (Fx at exit): a Font held by a script's static
## variable is otherwise freed when the script is, after the text server has shut down,
## which crashed the process at exit now and then.
static func release_fonts() -> void:
	_fonts.clear()


## Loads a style-guide font once (falls back to the theme default when missing).
static func font(path: String) -> Font:
	if _fonts.has(path):
		return _fonts[path]
	var f: Font = load(path) if ResourceLoader.exists(path) else null
	if f == null:
		f = ThemeDB.fallback_font
	_fonts[path] = f
	return f


## The Cell's own lettering on its fixed objects (the role the zine marker held: verbs, tags,
## stamps, name plates, card names): ART_BIBLE v2 §2.9 gives that role to the sticker face,
## Anton (ART-1 1A; Permanent Marker is now grease pencil only, `pencil()`). The screens move
## to their v2 components (stickers, terminals) in ART-2..12.
static func marker() -> Font:
	return font(FONT_DISPLAY)


## The grease pencil face (§2.9): Permanent Marker, for plans and threats drawn as wax.
static func pencil() -> Font:
	return font(FONT_PENCIL)


## The corp paper face (§2.9): Courier Prime Regular, typewriter fields.
static func paper() -> Font:
	return font(FONT_PAPER)


## The corp paper face's Bold: document titles.
static func paper_bold() -> Font:
	return font(FONT_PAPER_BOLD)


static func display() -> Font:
	return font(FONT_DISPLAY)


static func mono() -> Font:
	return font(FONT_MONO)


## The body face (§2.9): long text and tooltips, never headings or labels.
static func body() -> Font:
	return font(FONT_BODY)


## The body face's Medium weight (emphasis inside body text).
static func body_medium() -> Font:
	return font(FONT_BODY_MEDIUM)


## ANIM-R4 H11b: the mono lettering with the display face as its fallback for the glyphs
## Share Tech Mono lacks (the change arrows "→ ▲ ▼"): a variation of its own (the loaded font
## file is never changed). Only text that carries those glyphs uses it (`mono_for`): a
## fallback raises the font's line height, so everything else keeps the plain face.
static func mono_arrows() -> Font:
	if not _fonts.has(MONO_WITH_ARROWS):
		var v := FontVariation.new()
		v.base_font = font(FONT_MONO)
		v.fallbacks = [display()]
		_fonts[MONO_WITH_ARROWS] = v
	return _fonts[MONO_WITH_ARROWS]


## The cache key of the mono lettering with its fallback.
const MONO_WITH_ARROWS := "mono+arrows"
## The glyphs the mono face lacks that the screens write (a change: "a → b ▲").
const ARROW_GLYPHS := "→▲▼"


## True when `text` carries a glyph the mono face lacks (ARROW_GLYPHS).
static func has_arrows(text: String) -> bool:
	for ch in ARROW_GLYPHS:
		if text.contains(ch):
			return true
	return false


## The mono lettering for `text`: with the arrows' fallback when it needs it.
static func mono_for(text: String) -> Font:
	return mono_arrows() if has_arrows(text) else mono()


# --- ART-11 4D: campaign end and run end (ART_BIBLE v2 §1.2, §4.8; refs campaign_end/) ----------
# The campaign end's own stock (manila, post-its, ballpoint, stamp red, desk, house backs);
# the vinyl and the paper material are 1B's. Values from tag
# art-concepts-r43 (round 20 lost20.py, round 21 dossier21.py).
## The desk under the dossier, the lamp's warm pool, the manila folder and its fold, the
## report's and annex's stock, the typed ink and its soft (meta) ink.
const END_DESK := Color("#1E181E")
const END_DESK_LAMP := Color("#4A3524")
const END_MANILA := Color("#DEC48C")
const END_MANILA_EDGE := Color("#AA8C5A")
const END_REPORT := Color("#F0ECE2")
const END_ANNEX := Color("#E8E4D8")
const END_TYPE_INK := Color("#221E22")
const END_TYPE_SOFT := Color("#5A565A")
## The auditor's blue ballpoint and the rubber stamp's red.
const END_BALLPOINT := Color("#1C286E")
const END_STAMP_RED := Color("#C41E28")
## The auditor's post-its.
const END_NOTE_PINK := Color("#FF78AA")
const END_NOTE_YELLOW := Color("#FFE85A")
const END_NOTE_BLUE := Color("#96DCFF")
const END_NOTE_GREEN := Color("#B4F08C")
## Each corporation's ransomware house style (round 20 CORP_STYLE): the notice's back. The
## hue is `corp_color`, the accent `corp_secondary` (1A's round 18 kits).
const END_HOUSE_BACK := {&"halcyon": Color("#120C28"), &"meridian": Color("#221206"), &"solace": Color("#06180C"),
	&"orbital": Color("#040E1C"), &"rebel_cell": Color("#1E0406")}
## The notice's light words (head line, field values) on the house back.
const END_HOUSE_TEXT := Color("#F4F1E9")

# --- ART-1 1C: glyph atlas colours (ART_BIBLE 2.1 INK row, 3.5) -------------------------
## A glyph's flat white silhouette (bible 3.5: white on the read plate).
const GLYPH_FILL := Color("#FFFFFF")
## The dark rounded outline added at render time (bible 2.1: glyph outline #0C0A16).
const GLYPH_INK := Color("#0C0A16")
