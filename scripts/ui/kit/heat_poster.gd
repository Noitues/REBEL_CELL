class_name HeatPoster
extends Control
## Ransom-note Heat (STYLE_GUIDE 4): cut-out letters in mixed fonts on paper strips and
## the value in Anton. As a wanted poster in HQ (`poster = true`) it gains a border and a
## "WANTED" header. Heat bands follow the thresholds 25/50/75 (GDD 9.4).

## Colour of the number at high Heat: the campaign's corporation (set by the HQ).
var hot_color: Color = Palette.CORP_SOLACE
var heat: int = 0
var heat_max: int = 100
var poster: bool = false
var band: int = 0


func _init(p_poster: bool = false) -> void:
	poster = p_poster
	custom_minimum_size = Vector2(170, 96 if not p_poster else 150)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func set_heat(value: int, maximum: int, thresholds: Array[int] = [25, 50, 75]) -> void:
	heat = value
	heat_max = maximum
	band = 0
	for t in thresholds:
		if heat >= t:
			band += 1
	queue_redraw()


func _draw() -> void:
	var y := 0.0
	if poster:
		draw_rect(Rect2(Vector2.ZERO, size), Palette.PAPER_ALT)
		draw_rect(Rect2(Vector2.ZERO, size), Palette.INK, false, 3.0)
		draw_string(Palette.display(), Vector2(10, 30), "WANTED", HORIZONTAL_ALIGNMENT_LEFT, size.x - 20, 26, Palette.INK)
		draw_rect(Rect2(size.x * 0.3, 40, size.x * 0.4, 40), Color(0.5, 0.5, 0.5))
		draw_string(Palette.mono(), Vector2(size.x * 0.3 + 4, 64), "[OPERATIVE]", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Palette.PAPER)
		y = 84
	var letters := ["H", "E", "A", "T"]
	var fonts := [Palette.display(), Palette.marker(), Palette.mono(), Palette.display()]
	var x := 8.0
	for i in letters.size():
		var strip := Rect2(x, y + 4 + (i % 2) * 4, 24, 28)
		draw_rect(strip, Palette.PAPER if i % 2 == 0 else Palette.CELL_PINK)
		draw_rect(strip, Palette.INK, false, 1.0)
		draw_string(fonts[i], strip.position + Vector2(5, 22), letters[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Palette.INK)
		x += 28
	draw_string(Palette.display(), Vector2(x + 6, y + 30), "%d" % heat, HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Palette.CELL_PINK if band < 2 else hot_color)
	draw_string(Palette.mono(), Vector2(x + 6, y + 44), "/%d" % heat_max, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Palette.INK if poster else Palette.PAPER)
	var bar := Rect2(8, y + 44, size.x - 16, 8)
	draw_rect(bar, Color(Palette.INK, 0.3) if poster else Color(Palette.PAPER, 0.15))
	draw_rect(Rect2(bar.position, Vector2(bar.size.x * clampf(float(heat) / maxf(1.0, heat_max), 0.0, 1.0), bar.size.y)), Palette.CELL_PINK)
	for t in [25, 50, 75]:
		var tx: float = bar.position.x + bar.size.x * int(t) / float(heat_max)
		draw_line(Vector2(tx, bar.position.y - 3), Vector2(tx, bar.end.y + 3), Palette.INK if poster else Palette.PAPER, 1.0)
	draw_string(Palette.marker(), Vector2(8, y + 68), ["cool", "noticed", "flagged", "hunted"][mini(band, 3)], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Palette.INK if poster else Palette.CELL_ACID)
