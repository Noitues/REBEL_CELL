class_name ModemSign
extends Control
## The Modem's vertical neon sign (left edge of the shop): a rounded pink border, a dense
## printed-circuit board inside it with traces running in from the border, MODEM stacked
## in the drawn cybernetic face (pink) and CYBER SHOP under it (cyan), both sprouting
## traces, and BUY / SELL sticky notes overlapping the bottom-right corner. Decoration.

const PINK := Color("#FF3DA8")


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(210, 540)


func _draw() -> void:
	var r := Rect2(Vector2(6, 6), Vector2(size.x - 44, size.y - 40))
	_rounded_border(r, 26, PINK)
	_board_traces(r.grow(-12), PINK, 80)
	_border_traces(r, PINK)
	var step := (r.size.y - 160.0) / 5.0
	var u := minf(11.0, step / 8.2)
	for i in 5:
		CyberType.draw_text(self, r.position + Vector2((r.size.x - 4.0 * u) * 0.5, 26 + i * step), "MODEM"[i], u, PINK, 3.2, i == 0 or i == 4, 0.7)
	var cu := 4.4
	for k in 2:
		var word: String = ["CYBER", "SHOP"][k]
		CyberType.draw_text(self, r.position + Vector2((r.size.x - CyberType.width(word, cu)) * 0.5, r.size.y - 118 + k * 42), word, cu, Palette.NET_CYAN, 2.0, false, 0.8)
	_sticky(r.end + Vector2(-8, -54), "BUY", Palette.NOTE_YELLOW, 0.1)
	_sticky(r.end + Vector2(14, 4), "SELL", Palette.STICKER_PINK, -0.07)


func _rounded_border(r: Rect2, radius: float, col: Color) -> void:
	var pts := PackedVector2Array()
	var corners := [[Vector2(r.end.x - radius, r.position.y + radius), -PI * 0.5], [Vector2(r.end.x - radius, r.end.y - radius), 0.0],
		[Vector2(r.position.x + radius, r.end.y - radius), PI * 0.5], [Vector2(r.position.x + radius, r.position.y + radius), PI]]
	for cr in corners:
		for k in 9:
			var a: float = cr[1] + PI * 0.5 * k / 8.0
			pts.append(cr[0] + Vector2(cos(a), sin(a)) * radius)
	draw_colored_polygon(pts, Color(0.02, 0.02, 0.05, 0.94))
	pts.append(pts[0])
	draw_polyline(pts, Color(col, 0.12), 20.0, true)
	draw_polyline(pts, Color(col, 0.3), 9.0, true)
	draw_polyline(pts, col.lightened(0.35), 3.2, true)


func _board_traces(r: Rect2, col: Color, count: int) -> void:
	var dirs := [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1), Vector2(1, 1).normalized(), Vector2(-1, 1).normalized(), Vector2(1, -1).normalized(), Vector2(-1, -1).normalized()]
	for n in count:
		var h := absi(hash([n, 17]))
		var p := r.position + Vector2(float(h % 1000) / 1000.0 * r.size.x, float((h / 1000) % 1000) / 1000.0 * r.size.y)
		var pts := PackedVector2Array([p])
		var d: Vector2 = dirs[(h / 7) % 4]
		for seg in 2 + (h / 13) % 2:
			var q := (p + d * (8.0 + float((h / (17 + seg)) % 22))).clamp(r.position, r.end)
			pts.append(q)
			p = q
			d = dirs[4 + (h / (29 + seg)) % 4] if seg % 2 == 0 else dirs[(h / (31 + seg)) % 4]
		draw_polyline(pts, Color(col, 0.28), 1.4, true)
		if (h / 3) % 3 == 0:
			draw_circle(pts[0], 2.2, Color(col, 0.35))
		var end := pts[pts.size() - 1]
		if (h / 5) % 2 == 0:
			draw_circle(end, 3.2, Color(col, 0.55))
			draw_circle(end, 1.3, Palette.NIGHT_SKY)
		else:
			draw_rect(Rect2(end - Vector2(2.5, 2.5), Vector2(5, 5)), Color(col, 0.45))


func _border_traces(r: Rect2, col: Color) -> void:
	for side in [-1.0, 1.0]:
		var n := int((r.size.y - 80.0) / 34.0)
		for q in n:
			var y := r.position.y + 44.0 + q * 34.0
			var a := Vector2(r.position.x if side < 0 else r.end.x, y)
			var b := a + Vector2(-side * (10.0 + (q % 3) * 7.0), 0)
			var c := b + Vector2(-side, (1.0 if q % 2 == 0 else -1.0)).normalized() * (8.0 + (q % 4) * 4.0)
			var pts := PackedVector2Array([a, b, c])
			draw_polyline(pts, Color(col, 0.2), 6.0, true)
			draw_polyline(pts, Color(col, 0.85), 1.8, true)
			draw_circle(c, 4.0, Color(col, 0.9))
			draw_circle(c, 1.6, Palette.NIGHT_SKY)


func _sticky(at: Vector2, text: String, paper: Color, tilt: float) -> void:
	draw_set_transform(at, tilt, Vector2.ONE)
	draw_rect(Rect2(Vector2(-44 + 4, -26 + 5), Vector2(88, 52)), Palette.SHADOW)
	draw_rect(Rect2(Vector2(-44, -26), Vector2(88, 52)), paper)
	draw_rect(Rect2(Vector2(-18, -31), Vector2(36, 11)), Palette.NOTE_TAPE)
	draw_string(Palette.marker(), Vector2(-44, 10), text, HORIZONTAL_ALIGNMENT_CENTER, 88, 24, Palette.INK)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
