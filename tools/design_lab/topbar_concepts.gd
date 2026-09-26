extends Control
## Design lab (not part of the game): three top-bar (status strip) concepts over the HQ
## backdrop. Run: godot --path . res://tools/design_lab/topbar_concepts.tscn

const STATS := [["HEAT", "12", "/100", "flame"], ["SCHEMATICS", "70", "", "gear"], ["HOME", "45", "/50", "core"],
	["EXPLOITS", "1", "/3", "key"], ["RAIDS", "1", "", "alert"], ["ICE", "2", "", "ice"]]

var art: Control


func _ready() -> void:
	UiTheme.apply(self)
	var bg := CyberdeckBackground.new()
	add_child(bg)
	bg.set_district(&"meridian")
	art = Control.new()
	art.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	art.draw.connect(_draw_art)
	add_child(art)


func _draw_art() -> void:
	_label_row(Vector2(20, 18), "T1  TERMINAL TICKER")
	_ticker(Vector2(0, 30))
	_label_row(Vector2(20, 148), "T2  RANSOM-NOTE STRIP")
	_ransom(Vector2(0, 160))
	_label_row(Vector2(20, 300), "T3  NEON GAUGE CLUSTER")
	_gauges(Vector2(0, 312))


func _label_row(at: Vector2, text: String) -> void:
	art.draw_rect(Rect2(at + Vector2(-6, -14), Vector2(260, 20)), Color(0, 0, 0, 0.8))
	art.draw_string(Palette.mono(), at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Palette.CELL_ACID)


func _icon(c: Vector2, kind: String, col: Color) -> void:
	match kind:
		"flame":
			art.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -9), c + Vector2(6, 2), c + Vector2(3, 8), c + Vector2(-3, 8), c + Vector2(-6, 2)]), col)
		"gear":
			art.draw_circle(c, 6, col)
			art.draw_circle(c, 2.5, Palette.NIGHT_SKY)
			for k in 6:
				var a := TAU * k / 6.0
				art.draw_line(c + Vector2(cos(a), sin(a)) * 5, c + Vector2(cos(a), sin(a)) * 9, col, 3.0)
		"core":
			var hexa := PackedVector2Array()
			for k in 7:
				hexa.append(c + Vector2(cos(TAU * k / 6.0), sin(TAU * k / 6.0)) * 8)
			art.draw_polyline(hexa, col, 2.0)
			art.draw_circle(c, 3, col)
		"key":
			art.draw_arc(c + Vector2(-3, 0), 4, 0, TAU, 12, col, 2.0)
			art.draw_line(c + Vector2(1, 0), c + Vector2(9, 0), col, 2.0)
			art.draw_line(c + Vector2(7, 0), c + Vector2(7, 4), col, 2.0)
		"alert":
			art.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -9), c + Vector2(9, 7), c + Vector2(-9, 7)]), col)
			art.draw_string(Palette.display(), c + Vector2(-3, 6), "!", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.INK)
		"ice":
			for k in 3:
				var a := PI * k / 3.0
				art.draw_line(c - Vector2(cos(a), sin(a)) * 8, c + Vector2(cos(a), sin(a)) * 8, col, 2.0)


func _stat_col(i: int) -> Color:
	return [Palette.CELL_PINK, Palette.CELL_ACID, Palette.NET_CYAN, Palette.CRT_AMBER, Palette.CELL_PINK, Color("#8FE8FF")][i]


# T1: a black ticker band with icon chips and a scrolling DISPATCH crawl.
func _ticker(o: Vector2) -> void:
	art.draw_rect(Rect2(o, Vector2(1280, 44)), Color(0, 0, 0, 0.9))
	art.draw_rect(Rect2(o + Vector2(0, 42), Vector2(1280, 2)), Palette.CELL_PINK)
	art.draw_rect(Rect2(o, Vector2(250, 44)), Color(0.08, 0.02, 0.08, 0.95))
	art.draw_string(Palette.mono(), o + Vector2(12, 29), "01. CYBERDECK HQ", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Palette.PAPER)
	var x := 270.0
	for i in STATS.size():
		var st: Array = STATS[i]
		var col := _stat_col(i)
		art.draw_rect(Rect2(o + Vector2(x, 8), Vector2(118, 28)), Color(col, 0.08))
		art.draw_rect(Rect2(o + Vector2(x, 8), Vector2(3, 28)), col)
		_icon(o + Vector2(x + 18, 22), st[3], col)
		art.draw_string(Palette.mono(), o + Vector2(x + 32, 19), st[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 9, Color(col, 0.8))
		art.draw_string(Palette.display(), o + Vector2(x + 32, 35), st[1] + st[2], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.PAPER)
		x += 126
	art.draw_rect(Rect2(o + Vector2(0, 46), Vector2(1280, 20)), Color(0.02, 0.03, 0.07, 0.85))
	art.draw_string(Palette.mono(), o + Vector2(12, 61), "DISPATCH >> raid inbound on scrub_records // Meridian freight tariffs up 3% // the Cell says hi", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.CRT_AMBER)


# T2: cut-out ransom letters and taped paper tags hanging off a black strip.
func _ransom(o: Vector2) -> void:
	art.draw_rect(Rect2(o, Vector2(1280, 30)), Color(0, 0, 0, 0.88))
	var fonts := [Palette.display(), Palette.marker(), Palette.mono()]
	var papers := [Palette.NOTE_PAPER, Palette.STICKER_PINK, Palette.NOTE_YELLOW, Palette.PAPER]
	var x := 16.0
	for ch in "CYBERDECK HQ":
		if ch == " ":
			x += 10
			continue
		var k := ch.unicode_at(0)
		var r := Rect2(o + Vector2(x, 4 + (k % 3)), Vector2(22, 30))
		art.draw_rect(r, papers[k % 4])
		art.draw_string(fonts[k % 3], r.position + Vector2(4, 23), ch, HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Palette.INK)
		x += 25
	x = 340.0
	for i in STATS.size():
		var st: Array = STATS[i]
		var tilt := (-2.0 if i % 2 == 0 else 2.5) * PI / 180.0
		art.draw_set_transform(o + Vector2(x + 62, 40), tilt, Vector2.ONE)
		art.draw_rect(Rect2(Vector2(-58, -18) + Vector2(3, 4), Vector2(116, 62)), Palette.SHADOW)
		art.draw_rect(Rect2(Vector2(-58, -18), Vector2(116, 62)), papers[i % 4])
		art.draw_rect(Rect2(Vector2(-58, -18), Vector2(116, 62)), Color(Palette.INK, 0.5), false, 1.0)
		art.draw_rect(Rect2(Vector2(-16, -24), Vector2(32, 10)), Palette.NOTE_TAPE)
		art.draw_string(Palette.marker(), Vector2(-50, 2), st[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.INK)
		art.draw_string(Palette.display(), Vector2(-50, 36), st[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Palette.INK if i != 0 else Palette.CELL_PINK.darkened(0.3))
		art.draw_string(Palette.marker(), Vector2(-10, 36), st[2], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Palette.INK)
		art.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		x += 150


# T3: neon arc gauges in a slim terminal band (value in the ring, label under).
func _gauges(o: Vector2) -> void:
	art.draw_rect(Rect2(o, Vector2(1280, 70)), Color(0.02, 0.04, 0.1, 0.9))
	art.draw_rect(Rect2(o + Vector2(0, 68), Vector2(1280, 2)), Palette.NET_CYAN)
	art.draw_string(Palette.mono(), o + Vector2(14, 30), "01", HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Palette.CELL_PINK)
	art.draw_string(Palette.mono(), o + Vector2(14, 56), "CYBERDECK HQ", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.PAPER)
	var x := 300.0
	var fills := [0.12, 0.7, 0.9, 0.33, 1.0, 0.2]
	for i in STATS.size():
		var st: Array = STATS[i]
		var col := _stat_col(i)
		var c := o + Vector2(x, 34)
		art.draw_arc(c, 24, PI * 0.75, PI * 2.25, 32, Color(col, 0.15), 6.0)
		art.draw_arc(c, 24, PI * 0.75, PI * 0.75 + PI * 1.5 * fills[i], 32, col, 6.0)
		art.draw_string(Palette.display(), c + Vector2(-24, 7), st[1], HORIZONTAL_ALIGNMENT_CENTER, 48, 18, Palette.PAPER)
		_icon(c + Vector2(0, 20), st[3], col)
		art.draw_string(Palette.mono(), c + Vector2(34, 4), st[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 11, col)
		art.draw_string(Palette.mono(), c + Vector2(34, 18), st[2] if st[2] != "" else "-", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(Palette.PAPER, 0.6))
		x += 158
