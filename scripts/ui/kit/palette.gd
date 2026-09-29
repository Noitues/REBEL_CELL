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
const CORP_SOLACE := Color("#3DFF8B")
## REBEL_CELL (the handler AI): a deep blood red, clearly apart from the Cell pink in hue
## and lightness (H20 #14; was #FF2A6D, nearly the Cell pink).
const CORP_REBEL_CELL := Color("#E8141E")
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
const TERMINAL_BG := Color(0.02, 0.05, 0.11, 0.95)
const TERMINAL_BG_HOT := Color(0.16, 0.04, 0.16, 0.92)
const TERMINAL_EDGE := Color(0.36, 0.88, 1.0, 0.75)
const TERMINAL_TEXT := Color("#CFF6FF")
const NOTE_PAPER := Color("#E9DFC6")
const NOTE_PINK := Color("#F4C3CF")
const NOTE_YELLOW := Color("#F2DC7A")
## Softened hot pink for pink card stickers: black text stays readable on it.
const STICKER_PINK := Color("#F5AFCB")
const NOTE_TAPE := Color(0.93, 0.89, 0.78, 0.7)
const SHADOW := Color(0, 0, 0, 0.45)

# --- ART_BIBLE §3.3 semantic tokens -------------------------------------------------------
# A semantic hue means one thing everywhere and is always paired with a glyph, shape or word.
## Harm: damage taken, losses, costs, LETHAL, enemy projectiles, refusals (never CELL_PINK).
const HARM := Color("#FF4433")
## Gain: healing, gains, a positive outcome.
const GAIN := Color("#7BE07B")
## Protect: block, shield, evade, guards (the net's neutral cyan).
const PROTECT := NET_CYAN
## Warn: caution (low HP, NOTICED Heat, a pending raid).
const WARN := CRT_AMBER
## Focus: keyboard/pad focus, aim, legal drop zones, the current target.
const FOCUS := CELL_ACID
## Disabled: the outline and label of an unavailable control (never a faded active colour).
const DISABLED := Color("#6A7080")
## Text on dark: primary.
const TEXT_HI := Color("#F2F6FF")
## Text on dark: secondary.
const TEXT_MID := Color("#AFC0D6")
## Text on dark: tertiary (never for information the player needs).
const TEXT_LO := Color("#7A889C")
## The dim laid behind every glass panel and modal over the city (with SCRIM_BLUR_PX blur).
const SCRIM := Color(0.00784314, 0.0117647, 0.0392157, 0.55)
## The scrim's blur radius in reference pixels (§3.3).
const SCRIM_BLUR_PX := 6
## Heat FLAGGED band (§3.5): between WARN and HARM.
const HEAT_FLAGGED := Color("#FF7A1A")

const FONT_MARKER := "res://assets/fonts/PermanentMarker-Regular.ttf"
const FONT_DISPLAY := "res://assets/fonts/Anton-Regular.ttf"
const FONT_MONO := "res://assets/fonts/ShareTechMono-Regular.ttf"

## A glyph for every slice type (STYLE_GUIDE 4): readable without colour.
const SLICE_GLYPHS := {
	RC.SliceType.ATTACK: "▲", RC.SliceType.CRIT: "✦", RC.SliceType.DEFEND: "■", RC.SliceType.EVADE: "◇",
	RC.SliceType.SHIELD: "⬢", RC.SliceType.DEPLOY: "⬡", RC.SliceType.HEAL: "✚", RC.SliceType.AFFLICT: "◈",
	RC.SliceType.MISS: "✕",
}
const SLICE_NAMES := {
	RC.SliceType.ATTACK: "ATK", RC.SliceType.CRIT: "CRIT", RC.SliceType.DEFEND: "DEF", RC.SliceType.EVADE: "EVD", # TR
	RC.SliceType.SHIELD: "SHD", RC.SliceType.DEPLOY: "DEP", RC.SliceType.HEAL: "HEAL", RC.SliceType.AFFLICT: "AFL", # TR
	RC.SliceType.MISS: "MISS", # TR
}
## Whole words for the tags over the spinners (H21: new players read DEF / AFL / BLK as
## noise).
const SLICE_WORDS := {
	RC.SliceType.ATTACK: "ATTACK", RC.SliceType.CRIT: "CRITICAL", RC.SliceType.DEFEND: "DEFEND", RC.SliceType.EVADE: "EVADE", # TR
	RC.SliceType.SHIELD: "SHIELD", RC.SliceType.DEPLOY: "DEPLOY", RC.SliceType.HEAL: "HEAL", RC.SliceType.AFFLICT: "AFFLICT", # TR
	RC.SliceType.MISS: "MISS", # TR
}
const STATUS_WORDS := {RC.Status.NONE: "", RC.Status.CORRUPTED: "CORRUPTED", RC.Status.OVERCLOCKED: "OVERCLOCKED", RC.Status.ENCRYPTED: "ENCRYPTED", RC.Status.PARASITE: "PARASITE"} # TR
## How well a needle lands, in plain words.
const TIER_WORDS := {RC.PrecisionTier.PERFECT: "perfect aim", RC.PrecisionTier.GOOD: "good aim", RC.PrecisionTier.PARTIAL: "half power"} # TR
## A glyph and tag for every status, also readable without colour.
const STATUS_GLYPHS := {RC.Status.NONE: "", RC.Status.CORRUPTED: "☠", RC.Status.OVERCLOCKED: "⚡", RC.Status.ENCRYPTED: "⌗", RC.Status.PARASITE: "✺"}
const STATUS_TAGS := {RC.Status.NONE: "", RC.Status.CORRUPTED: "CRPT", RC.Status.OVERCLOCKED: "OVCL", RC.Status.ENCRYPTED: "ENC", RC.Status.PARASITE: "PRST"}
const TIER_NAMES := {RC.PrecisionTier.PERFECT: "PERFECT", RC.PrecisionTier.GOOD: "GOOD", RC.PrecisionTier.PARTIAL: "PARTIAL"} # TR

## Corporation glow colour (each corporation has its own; see STYLE_GUIDE).
static func corp_color(corporation_id: StringName) -> Color:
	match corporation_id:
		&"solace":
			return CORP_SOLACE
		&"meridian":
			return Color("#FF8C1A")
		&"halcyon":
			return Color("#8C7BFF")
		&"orbital":
			return Color("#DDE3FF")
		&"rebel_cell":
			return CORP_REBEL_CELL
		_:
			return NET_CYAN


static func slice_color(type: int) -> Color:
	match type:
		RC.SliceType.ATTACK, RC.SliceType.CRIT:
			return CELL_PINK
		RC.SliceType.DEFEND, RC.SliceType.SHIELD:
			return NET_CYAN
		RC.SliceType.EVADE, RC.SliceType.HEAL:
			return Color("#7BE07B")
		RC.SliceType.AFFLICT:
			return Color("#C85AFF")
		RC.SliceType.DEPLOY:
			return Color("#B08CFF")
		_:
			return Color("#6A6A6A")


static var _fonts: Dictionary = {}


## Loads a style-guide font once (falls back to the theme default when missing).
static func font(path: String) -> Font:
	if _fonts.has(path):
		return _fonts[path]
	var f: Font = load(path) if ResourceLoader.exists(path) else null
	if f == null:
		f = ThemeDB.fallback_font
	_fonts[path] = f
	return f


static func marker() -> Font:
	return font(FONT_MARKER)


static func display() -> Font:
	return font(FONT_DISPLAY)


static func mono() -> Font:
	return font(FONT_MONO)


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
