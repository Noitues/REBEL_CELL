class_name GraffitiTag
extends Control
## Graffiti tag with drips (STYLE_GUIDE 4, HQ): marker text in cell_pink with a spray
## halo and paint drips. Original motif; the Cell mascot is a grinning hexagon "cell".

var text: String = "REBEL_CELL"


func _init(p_text: String = "REBEL_CELL") -> void:
	text = p_text
	custom_minimum_size = Vector2(340, 90)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _draw() -> void:
	var base := Vector2(12, 58)
	for i in 6:
		draw_string(Palette.marker(), base + Vector2(i - 3, (i * 7) % 5 - 2), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 44, Color(Palette.CELL_PINK, 0.08))
	draw_string(Palette.marker(), base + Vector2(2, 2), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 44, Palette.INK)
	draw_string(Palette.marker(), base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, 44, Palette.CELL_PINK)
	for i in 7:
		var x := 24.0 + i * 44.0 + float((i * 13) % 9)
		var len := 10.0 + float((i * 29) % 22)
		draw_line(Vector2(x, 60), Vector2(x, 60 + len), Palette.CELL_PINK, 3.0)
		draw_circle(Vector2(x, 60 + len), 2.5, Palette.CELL_PINK)
	# The Cell mascot: a grinning hexagon.
	var c := Vector2(size.x - 40, 40)
	var pts := PackedVector2Array()
	for k in 6:
		pts.append(c + Vector2(cos(k * TAU / 6.0), sin(k * TAU / 6.0)) * 22)
	draw_colored_polygon(pts, Palette.CELL_ACID)
	draw_polyline(pts + PackedVector2Array([pts[0]]), Palette.INK, 2.0)
	draw_circle(c + Vector2(-7, -5), 3, Palette.INK)
	draw_circle(c + Vector2(7, -5), 3, Palette.INK)
	draw_arc(c + Vector2(0, 2), 10, 0.3, PI - 0.3, 12, Palette.INK, 2.0)
