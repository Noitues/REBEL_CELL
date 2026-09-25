class_name GraffitiScrawl
extends Control
## A hot-pink marker scrawl ("NEVER SLEEP", "TRUST NO ONE") with the Cell's crown doodle
## (STYLE_GUIDE 1: the Cell's voice). Decoration only: ignores the mouse and never sits
## over wheels or controls (callers place it in free space).

var text: String = ""
var tilt: float = -8.0
var font_size: int = 26


func _init(p_text: String = "NEVER SLEEP", p_tilt: float = -8.0, p_size: int = 26) -> void:
	text = p_text
	tilt = p_tilt
	font_size = p_size
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var lines := text.split("\n")
	var w := 0.0
	for l in lines:
		w = maxf(w, Palette.marker().get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x)
	custom_minimum_size = Vector2(w + 30, lines.size() * font_size * 1.1 + 22 + font_size * 0.8)


func _ready() -> void:
	pivot_offset = size / 2.0
	rotation_degrees = tilt


func _draw() -> void:
	var lines := text.split("\n")
	for i in lines.size():
		var p := Vector2(6, font_size + i * font_size * 1.1)
		draw_string(Palette.marker(), p + Vector2(0, 0), lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, Color(Palette.CELL_PINK, 0.25))
		DripButton.draw_drip_text(self, p + Vector2(-1, -1), lines[i], font_size, Palette.CELL_PINK, DripButton.auto_drips(lines[i], 2) if i == lines.size() - 1 else [], false)
	# The crown doodle under the last line.
	var base := Vector2(size.x - 34, size.y - 8)
	var crown := PackedVector2Array([base, base + Vector2(2, -12), base + Vector2(8, -5), base + Vector2(13, -14), base + Vector2(18, -5), base + Vector2(24, -12), base + Vector2(26, 0), base])
	draw_polyline(crown, Palette.CELL_PINK, 2.0)
