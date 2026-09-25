class_name DripLabel
extends Control
## The Cell's dripping marker as a drop-in text control: Permanent Marker with paint drips
## hanging from chosen letters (DripButton.draw_drip_text). Set `drips` explicitly or leave
## it empty to get automatic drips (DripButton.auto_drips). Decoration; ignores the mouse.

var text: String = "":
	set(v):
		text = v
		_resize()
var font_size: int = 44:
	set(v):
		font_size = v
		_resize()
var color: Color = DripButton.DRIP_PINK
var drips: Array = []
var shadow: bool = true


func _init(p_text: String = "", p_size: int = 44, p_color: Color = DripButton.DRIP_PINK, p_drips: Array = []) -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	color = p_color
	drips = p_drips
	font_size = p_size
	text = p_text


func _resize() -> void:
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
	custom_minimum_size = Vector2(w + 16, font_size * 1.05 + 44.0 * font_size / 44.0 + 8)
	queue_redraw()


func _draw() -> void:
	var d := drips if not drips.is_empty() else DripButton.auto_drips(text)
	DripButton.draw_drip_text(self, Vector2(6, font_size), text, font_size, color, d, shadow)
