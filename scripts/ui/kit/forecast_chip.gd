class_name ForecastChip
extends RaidTerminal
## The raid setup's forecast as a small CRT terminal chip beside the work order (art bible
## §1.2, A-073: the corp paper carries only corp fields and stamps, so the Cell's forecast is
## not drawn on it). `> IF THE RAID RUNS NOW:` over the verdict ("HOME -5", "CELL HOLDS") in the
## verdict's colour, its icon before it. Still a forecast, not a result: the same words and
## colour logic as `ForecastStamp` (which the raid playout keeps). Display only (no focus; its
## tooltip explains the projection).

## The verdict's icon radius share of the chip (px at text 1.0).
const ICON_PX := 22.0
## The chip's width (px at text 1.0): the caption wraps to two lines inside it.
const WIDTH_PX := 184.0

var caption: String = ""
var verdict: String = ""
var color: Color = Palette.CELL_PINK
var icon_kind: StringName = &""

var _verdict_label: Label = null


func _init(p_caption: String = "", p_verdict: String = "", p_color: Color = Palette.CELL_PINK, p_icon: StringName = &"") -> void:
	# A-076 A4: the edge is the Cell's CRT cyan; the verdict keeps its own colour and glyph.
	super._init(tr(p_caption).replace("\n", " "))  # the default accent: the Cell's cyan
	name = "Projection"
	caption = p_caption
	verdict = p_verdict
	color = p_color
	icon_kind = p_icon
	tag_label.text = ""
	# The caption wraps in the chip's width (it is narrow: it stands over the map's left margin).
	custom_minimum_size.x = WIDTH_PX * Settings.text_scale
	var head := find_child("TerminalTitle", true, false) as Label
	if head != null:
		UiWrap.whole_words(head)
	crt.label.autowrap_mode = TextServer.AUTOWRAP_WORD
	mouse_filter = Control.MOUSE_FILTER_PASS  # its tooltip explains the forecast
	focus_mode = Control.FOCUS_NONE
	var row := HBoxContainer.new()
	row.name = "ForecastRow"
	row.add_theme_constant_override("separation", 8)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if icon_kind != &"":
		var icon := _IconDraw.new(icon_kind, color)
		icon.custom_minimum_size = Vector2(ICON_PX, ICON_PX) * Settings.text_scale
		icon.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		row.add_child(icon)
	_verdict_label = Label.new()
	_verdict_label.name = "ForecastVerdict"
	_verdict_label.text = shown_verdict()
	_verdict_label.add_theme_font_override("font", Palette.display())
	_verdict_label.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.TITLE))
	_verdict_label.add_theme_color_override("font_color", color)
	_verdict_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(_verdict_label)
	body.add_child(row)


## A-076 A1: one live what-if line under the verdict (`HOME 50 → 40 (-10)`), `text` as shown, in `tint`.
func add_line(line_name: String, text: String, tint: Color) -> Label:
	var l := Label.new()
	l.name = line_name
	l.text = text
	l.add_theme_font_override("font", Palette.mono_arrows())
	l.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	l.add_theme_color_override("font_color", tint)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_child(l)
	return l


## The caption as drawn: translated.
func shown_caption() -> String:
	return tr(caption)


## The verdict as drawn: translated when it is a catalogue key, as given when built from parts
## (RaidVerdict: "HOME -5\n1 DOWN").
func shown_verdict() -> String:
	return tr(verdict) if TextDb.has_message(verdict) else verdict


## The verdict's lines (one per loss).
func verdict_lines() -> PackedStringArray:
	return shown_verdict().split("\n")


## The icon, drawn in the verdict's colour.
class _IconDraw extends Control:
	var kind: StringName
	var tint: Color

	func _init(p_kind: StringName, p_tint: Color) -> void:
		kind = p_kind
		tint = p_tint
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		StatIcon.draw(self, size * 0.5, minf(size.x, size.y) * 0.5, kind, tint)
