class_name CorpGlyphField
extends HBoxContainer
## Art pass W8d (ART_BIBLE §12, §3.6, §7.4): one number beside a corporation's landmark
## glyph (W8a's baked `assets/art/landmarks/<corp>.svg`), for the campaign end's ICE records
## ("each corporation keeps its own ladder"): the glyph in INK on paper, the number in mono.
## The corp reads by its glyph's shape; its name is the tooltip. A corporation without a
## glyph shows its name's first letter instead. View only.

## The glyph's side as a share of the number's size, and the gap after it (px at 1.0).
const ICON_SHARE := 1.2
const GAP := UiTheme.SP_XS
## The fallback initial's size as a share of the glyph's side.
const INITIAL_SHARE := 0.8

var corp_id: StringName = &""
var glyph: Control
var value_label: Label
var _tex: Texture2D = null
var _ink: Color = Palette.INK
var _initial: String = ""


func _init(p_corp_id: StringName, corp_name: String, text: String, font_size: int, ink: Color = Palette.INK) -> void:
	corp_id = p_corp_id
	_ink = ink
	name = "Corp%s" % String(p_corp_id).to_upper()
	mouse_filter = Control.MOUSE_FILTER_PASS
	tooltip_text = corp_name
	add_theme_constant_override("separation", roundi(GAP * Settings.text_scale))
	var side := roundf(font_size * ICON_SHARE)
	var path := SvgArt.landmark_path(p_corp_id)
	_tex = SvgArt.texture(path, side) if path != "" else null
	_initial = corp_name.left(1).to_upper()
	glyph = Control.new()
	glyph.name = "Glyph"
	glyph.mouse_filter = Control.MOUSE_FILTER_IGNORE
	glyph.custom_minimum_size = Vector2(side, side)
	glyph.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	glyph.draw.connect(_draw_glyph)
	add_child(glyph)
	value_label = Label.new()
	value_label.name = "Value"
	value_label.text = text
	value_label.add_theme_font_override("font", Palette.mono())
	value_label.add_theme_font_size_override("font_size", font_size)
	value_label.add_theme_color_override("font_color", ink)
	add_child(value_label)


func _draw_glyph() -> void:
	var r := Rect2(Vector2.ZERO, glyph.size)
	if _tex != null:
		glyph.draw_texture_rect(_tex, r, false, _ink)
	else:
		var f := Palette.display()
		var px := roundi(r.size.y * INITIAL_SHARE)
		glyph.draw_string(f, Vector2(0, (r.size.y + f.get_ascent(px) - f.get_descent(px)) * 0.5), _initial, HORIZONTAL_ALIGNMENT_CENTER, r.size.x, px, _ink)


## True when the corp's baked glyph is drawn (tests).
func has_glyph() -> bool:
	return _tex != null
