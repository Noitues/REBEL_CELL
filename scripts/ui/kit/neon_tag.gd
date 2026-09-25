class_name NeonTag
extends Control
## A small boxed neon word (reference: the Modem's BUY / SELL / TRADE signs). Decoration
## only; ignores the mouse.

var text: String = ""
var color: Color = Palette.NET_CYAN


func _init(p_text: String = "", p_color: Color = Palette.NET_CYAN) -> void:
	text = p_text
	color = p_color
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(78, 40)


func _draw() -> void:
	var r := Rect2(Vector2(6, 4), Vector2(size.x - 12, size.y - 8))
	draw_rect(r, Color(Palette.NIGHT_SKY, 0.85))
	draw_rect(r.grow(2), Color(color, 0.15), false, 5.0)
	draw_rect(r, color, false, 1.5)
	for k in 2:
		draw_string(Palette.display(), r.position + Vector2(0, 26), text, HORIZONTAL_ALIGNMENT_CENTER, r.size.x, 22 + k * 2, Color(color, 0.14))
	draw_string(Palette.display(), r.position + Vector2(0, 26), text, HORIZONTAL_ALIGNMENT_CENTER, r.size.x, 22, color.lightened(0.3))
