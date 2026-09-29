class_name StatField
extends HBoxContainer
## One number with its icon (ART_BIBLE 12: glyphs and numbers stand alone from words): a
## StatIcon drawn beside a Label holding only the number ("60/60"). The dossier's HP,
## deck and Daemons fields (W5; critique `scr`: "HP 60/60 DECK 10" read as a sentence).
## Named "Stat<KIND>"; the icon's word is the tooltip. View only.

## Icon side as a share of the number's font size, and the gap after it (px at 1.0).
const ICON_SHARE := 1.1
const GAP := 4

var kind: StringName = &""
var value_label: Label
var icon: Control
var _color: Color = Palette.INK


func _init(p_kind: StringName, text: String, font_size: int, col: Color) -> void:
	kind = p_kind
	_color = col
	name = "Stat%s" % String(p_kind).to_upper()
	mouse_filter = Control.MOUSE_FILTER_PASS
	tooltip_text = tr(StatIcon.NAMES.get(p_kind, String(p_kind)))
	add_theme_constant_override("separation", roundi(GAP * Settings.text_scale))
	icon = Control.new()
	icon.name = "Icon"
	icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
	icon.custom_minimum_size = Vector2.ONE * roundf(font_size * ICON_SHARE)
	icon.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	icon.draw.connect(_draw_icon)
	add_child(icon)
	value_label = Label.new()
	value_label.name = "Value"
	value_label.text = text
	value_label.add_theme_font_override("font", Palette.mono())
	value_label.add_theme_font_size_override("font_size", font_size)
	value_label.add_theme_color_override("font_color", col)
	value_label.add_theme_color_override("font_shadow_color", Color(col, 0.0))
	add_child(value_label)


func _draw_icon() -> void:
	var r := icon.size.y * 0.5
	StatIcon.draw(icon, icon.size * 0.5, r * 0.9, kind, _color)


## Changes the number shown.
func set_value(text: String) -> void:
	value_label.text = text


## Recolours the number and icon (high contrast).
func set_color(col: Color) -> void:
	_color = col
	value_label.add_theme_color_override("font_color", col)
	icon.queue_redraw()
