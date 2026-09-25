class_name HudStats
extends Control
## Ransom-note stat tags for the top bar: each stat on its own taped paper tag (paper,
## pink, yellow), a marker name and the value in Anton, tilted a little and hanging just
## below the band. Decoration of numbers the scene provides; ignores the mouse.

const TAG_SIZE := Vector2(92, 44)
const PAPERS: Array[Color] = [Color("#E9DFC6"), Color("#F5AFCB"), Color("#F2DC7A"), Color("#F2EEE4")]

## [[name, value, suffix], ...]
var items: Array = []


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(0, 54)


func _draw() -> void:
	var x := 0.0
	var step := TAG_SIZE.x + 8.0
	for i in items.size():
		var it: Array = items[i]
		var tilt := (-2.0 if i % 2 == 0 else 2.5) * PI / 180.0
		draw_set_transform(Vector2(x + TAG_SIZE.x * 0.5, 29), tilt, Vector2.ONE)
		var r := Rect2(-TAG_SIZE * 0.5, TAG_SIZE)
		draw_rect(Rect2(r.position + Vector2(3, 4), r.size), Palette.SHADOW)
		draw_rect(r, PAPERS[i % PAPERS.size()])
		draw_rect(r, Color(Palette.INK, 0.45), false, 1.0)
		draw_rect(Rect2(Vector2(-13, r.position.y - 5), Vector2(26, 9)), Palette.NOTE_TAPE)
		draw_string(Palette.marker(), r.position + Vector2(6, 14), String(it[0]), HORIZONTAL_ALIGNMENT_LEFT, TAG_SIZE.x - 10, 10, Palette.INK)
		var value := String(it[1])
		draw_string(Palette.display(), r.position + Vector2(6, 38), value, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Palette.INK)
		if it.size() > 2 and String(it[2]) != "":
			var vw := Palette.display().get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, 22).x
			draw_string(Palette.marker(), r.position + Vector2(10 + vw, 37), String(it[2]), HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Palette.INK)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		x += step
