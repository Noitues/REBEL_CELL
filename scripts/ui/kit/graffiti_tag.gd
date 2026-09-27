class_name GraffitiTag
extends Control
## Graffiti tag with drips (STYLE_GUIDE 4, HQ): marker text in cell_pink with a spray
## halo and paint drips. Original motif; the Cell mascot is a grinning hexagon "cell".

var text: String = "REBEL_CELL"


## Lettering (px), the words' left edge and the room the mascot takes at the right (px).
const FONT_SIZE := 44
const LEFT := 12.0
const MASCOT_ROOM := 80.0
const MIN_WIDTH := 340.0


## `p_text` is shown as given (the caller translates it; H24 S3); the tag is as wide as its
## words and the mascot (H24: a translated "LOOT: pick a card" ran under the mascot).
func _init(p_text: String = "REBEL_CELL") -> void:
	text = p_text
	custom_minimum_size = Vector2(maxf(MIN_WIDTH, LEFT + Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SIZE).x + MASCOT_ROOM), 104)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _draw() -> void:
	var base := Vector2(LEFT, 58)
	for i in 6:
		draw_string(Palette.marker(), base + Vector2(i - 3, (i * 7) % 5 - 2), text, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SIZE, Color(Palette.CELL_PINK, 0.08))
	DripButton.draw_drip_text(self, base, text, FONT_SIZE, DripButton.DRIP_PINK, DripButton.auto_drips(text))
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
