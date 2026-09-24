class_name Palette
extends RefCounted
## Colour tokens, glyphs and fonts from STYLE_GUIDE 2-4. Views never hard-code colours.

const CELL_PINK := Color("#FF3DA8")
const CELL_ACID := Color("#D4FF00")
const PAPER := Color("#F2EEE4")
const PAPER_ALT := Color("#E9E4D6")
const INK := Color("#111111")
const NET_CYAN := Color("#5CE1FF")
const NET_BG_INNER := Color("#0D1440")
const NET_BG_OUTER := Color("#02030A")
const CORP_SOLACE := Color("#3DFF8B")
const CRT_AMBER := Color("#FFB000")
const RESIST_GOLD := Color("#FFD24D")
const DESK_DARK := Color("#1B1D21")
const DESK_METAL := Color("#34383E")
const TAPE := Color(0.95, 0.9, 0.6, 0.55)

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
	RC.SliceType.ATTACK: "ATK", RC.SliceType.CRIT: "CRIT", RC.SliceType.DEFEND: "DEF", RC.SliceType.EVADE: "EVD",
	RC.SliceType.SHIELD: "SHD", RC.SliceType.DEPLOY: "DEP", RC.SliceType.HEAL: "HEAL", RC.SliceType.AFFLICT: "AFL",
	RC.SliceType.MISS: "MISS",
}
## A glyph and tag for every status, also readable without colour.
const STATUS_GLYPHS := {RC.Status.NONE: "", RC.Status.CORRUPTED: "☠", RC.Status.OVERCLOCKED: "⚡", RC.Status.ENCRYPTED: "⌗", RC.Status.PARASITE: "✺"}
const STATUS_TAGS := {RC.Status.NONE: "", RC.Status.CORRUPTED: "CRPT", RC.Status.OVERCLOCKED: "OVCL", RC.Status.ENCRYPTED: "ENC", RC.Status.PARASITE: "PRST"}
const CLASS_COLORS := {&"breaker": Color("#FF3DA8"), &"ghost": Color("#9FE8FF"), &"rigger": Color("#FFB347"), &"botnet": Color("#B08CFF")}
const TIER_NAMES := {RC.PrecisionTier.PERFECT: "PERFECT", RC.PrecisionTier.GOOD: "GOOD", RC.PrecisionTier.PARTIAL: "PARTIAL"}

## Corporation glow colour (each corporation gets its own; Solace for now).
static func corp_color(corporation_id: StringName) -> Color:
	match corporation_id:
		&"solace":
			return CORP_SOLACE
		&"meridian":
			return Color("#FF8C1A")
		_:
			return NET_CYAN


static func slice_color(type: int) -> Color:
	match type:
		RC.SliceType.ATTACK, RC.SliceType.CRIT:
			return Color("#FF5A5A")
		RC.SliceType.DEFEND, RC.SliceType.SHIELD:
			return Color("#4FA8FF")
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
