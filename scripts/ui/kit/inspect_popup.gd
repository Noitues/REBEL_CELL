class_name InspectPopup
extends PanelContainer
## The inspect text for keyboard and pad players (H20): what a tooltip shows the mouse,
## shown beside the inspected thing until the player moves on. Terminal glass, clean
## system text. View only.

const WIDTH := 300.0
const MARGIN := 8.0

var label: RichTextLabel


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	var sb := StyleBoxFlat.new()
	sb.bg_color = Palette.TERMINAL_BG
	sb.border_color = Palette.TERMINAL_EDGE
	PaletteSkins.track_box(sb)  # ART-12 12s-b: the glass and edge follow the skin
	sb.set_border_width_all(1)
	sb.set_content_margin_all(MARGIN)
	add_theme_stylebox_override("panel", sb)
	label = RichTextLabel.new()
	label.fit_content = true
	label.bbcode_enabled = false
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override("default_color", Palette.TERMINAL_TEXT)
	add_child(label)


## Shows `text` beside `target` (global rect), kept inside `bounds` (global).
func show_for(text: String, target: Rect2, bounds: Rect2) -> void:
	if text == "":
		hide()
		return
	label.text = text
	label.custom_minimum_size.x = WIDTH * Settings.text_scale
	reset_size()
	var sz := get_combined_minimum_size()
	var pos := Vector2(target.end.x + MARGIN, target.position.y)
	if pos.x + sz.x > bounds.end.x:
		pos.x = target.position.x - sz.x - MARGIN
	pos.x = clampf(pos.x, bounds.position.x, maxf(bounds.position.x, bounds.end.x - sz.x))
	pos.y = clampf(pos.y, bounds.position.y, maxf(bounds.position.y, bounds.end.y - sz.y))
	global_position = pos.floor()
	visible = true


func text() -> String:
	return label.get_parsed_text() if visible else ""
