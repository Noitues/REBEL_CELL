class_name ScreenHeader
extends Control
## Screen title strip (STYLE_GUIDE 4, "Neon city"): "01. CYBERDECK HQ" in system mono on
## a black band with a hot-pink brush underline. Pure decoration; ignores the mouse.

var number: String = ""
var title: String = ""


func _init(p_number: String = "", p_title: String = "") -> void:
	number = p_number
	title = p_title
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(_text_width() + 34, 38)


func _text_width() -> float:
	return Palette.mono().get_string_size(_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, 22).x


func _text() -> String:
	return ("%s. %s" % [number, title]) if number != "" else title


func _draw() -> void:
	var w := _text_width() + 28
	draw_rect(Rect2(0, 0, w, 32), Color(0, 0, 0, 0.88))
	draw_string(Palette.mono(), Vector2(12, 24), _text(), HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Palette.PAPER)
	# Brush underline: a tapered pink stroke that runs a little past the band.
	var pts := PackedVector2Array([Vector2(4, 33), Vector2(w + 20, 31), Vector2(w + 26, 34), Vector2(w * 0.4, 37), Vector2(2, 36)])
	draw_colored_polygon(pts, Palette.CELL_PINK)
	draw_line(Vector2(w + 30, 33), Vector2(w + 36, 33), Color(Palette.CELL_PINK, 0.6), 2.0)
