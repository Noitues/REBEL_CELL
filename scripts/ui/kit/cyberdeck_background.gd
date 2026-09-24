class_name CyberdeckBackground
extends Control
## The physical world (STYLE_GUIDE 1): a diegetic cyberdeck. Rain-streaked window with
## neon behind it, worn metal deck, an amber CRT panel. Rain animates unless
## reduce-effects. Searchlights sweep past the window as Heat rises (GDD 9.4).

var heat_band: int = 0
var _rain_offset: float = 0.0
var _search_t: float = 0.0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _process(delta: float) -> void:
	if Settings.reduce_effects:
		return
	_rain_offset = fmod(_rain_offset + delta * 220.0, 60.0)
	_search_t += delta
	queue_redraw()


func _draw() -> void:
	# Window (top band) with neon glow and rain.
	var window := Rect2(0, 0, size.x, size.y * 0.42)
	draw_rect(window, Color("#070912"))
	draw_rect(Rect2(0, window.size.y * 0.55, size.x, 3), Color(Palette.CELL_PINK, 0.8))
	draw_rect(Rect2(0, window.size.y * 0.55 + 3, size.x, 18), Color(Palette.CELL_PINK, 0.12))
	for i in 9:
		var bx := size.x * (0.05 + i * 0.11)
		var bh := window.size.y * (0.3 + float((i * 37) % 50) / 100.0)
		draw_rect(Rect2(bx, window.size.y - bh, size.x * 0.07, bh), Color("#0F1424"))
		for w in 6:
			draw_rect(Rect2(bx + 6 + w * 12, window.size.y - bh + 10 + (w % 3) * 22, 6, 6), Color(Palette.CRT_AMBER if (i + w) % 4 == 0 else Palette.NET_CYAN, 0.5))
	if heat_band > 0:
		var sx := fmod(_search_t * 120.0 * heat_band, size.x + 200.0) - 100.0
		draw_colored_polygon(PackedVector2Array([Vector2(sx, window.size.y), Vector2(sx + 60, window.size.y), Vector2(sx + 220, 0), Vector2(sx + 100, 0)]), Color(Palette.PAPER, 0.06 * heat_band))
	for i in 40:
		var rx := float((i * 97) % int(maxf(size.x, 1.0)))
		var ry := fmod(float((i * 53) % 400) + _rain_offset * (1.0 + (i % 3) * 0.3), window.size.y)
		draw_line(Vector2(rx, ry), Vector2(rx - 3, ry + 18), Color(Palette.NET_CYAN, 0.25), 1.0)
	# Deck: worn metal with a highlight edge and screws.
	var deck := Rect2(0, window.size.y, size.x, size.y - window.size.y)
	draw_rect(deck, Palette.DESK_DARK)
	draw_rect(Rect2(0, window.size.y, size.x, 6), Palette.DESK_METAL)
	for i in 8:
		draw_circle(Vector2(30 + i * (size.x - 60) / 7.0, window.size.y + 22), 4, Palette.DESK_METAL)
	# CRT panel (amber readout) on the right of the deck.
	var crt := Rect2(size.x * 0.66, window.size.y + 40, size.x * 0.3, size.y * 0.3)
	draw_rect(crt, Color("#0B0A06"))
	draw_rect(crt, Palette.DESK_METAL, false, 4.0)
	for k in int(crt.size.y / 4.0):
		draw_line(Vector2(crt.position.x + 6, crt.position.y + 6 + k * 4), Vector2(crt.end.x - 6, crt.position.y + 6 + k * 4), Color(Palette.CRT_AMBER, 0.05), 1.0)
	draw_string(Palette.mono(), crt.position + Vector2(14, 28), "[DECK CRT] REBEL_CELL v0.9", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(Palette.CRT_AMBER, 0.8))
	draw_string(Palette.mono(), crt.position + Vector2(14, 50), "DISPATCH: standing by.", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(Palette.CRT_AMBER, 0.6))
