extends Control
## Design lab: the MODEM CYBER SHOP sign on the city backdrop. Neon border with rounded
## corners, MODEM in the drawn cybernetic face (pink) with circuit traces, CYBER SHOP in
## the same face (cyan), BUY / SELL / TRADE as sticky notes.
## Run: godot --path . res://tools/design_lab/modem_backdrops.tscn -- --store=1|2|3

var store: int = 1
var art: Control


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--store="):
			store = int(a.trim_prefix("--store="))
	var bg := WireframeBackground.new()
	bg.city.dim = 0.3
	add_child(bg)
	art = Control.new()
	art.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	art.draw.connect(_draw_art)
	add_child(art)


func _draw_art() -> void:
	match store:
		1:
			_sign_horizontal(Vector2(250, 180))
		2:
			_sign_vertical(Vector2(50, 60))
		_:
			_sign_stacked(Vector2(330, 150))
	art.draw_rect(Rect2(0, 0, 1280, 30), Color(0, 0, 0, 0.9))
	art.draw_string(Palette.mono(), Vector2(12, 21), ["", "SIGN 1  WIDE PANEL", "SIGN 2  VERTICAL BLADE (left edge of the Modem screen)", "SIGN 3  STACKED BADGE"][store], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.CELL_ACID)


## A rounded neon tube border (glow passes, then the core).
func _rounded_border(r: Rect2, radius: float, col: Color) -> void:
	var pts := PackedVector2Array()
	var corners := [[Vector2(r.end.x - radius, r.position.y + radius), -PI * 0.5], [Vector2(r.end.x - radius, r.end.y - radius), 0.0],
		[Vector2(r.position.x + radius, r.end.y - radius), PI * 0.5], [Vector2(r.position.x + radius, r.position.y + radius), PI]]
	for cr in corners:
		for k in 9:
			var a: float = cr[1] + PI * 0.5 * k / 8.0
			pts.append(cr[0] + Vector2(cos(a), sin(a)) * radius)
	art.draw_colored_polygon(pts, Color(0.02, 0.02, 0.05, 0.93))
	pts.append(pts[0])
	art.draw_polyline(pts, Color(col, 0.12), 22.0, true)
	art.draw_polyline(pts, Color(col, 0.3), 10.0, true)
	art.draw_polyline(pts, col.lightened(0.35), 3.5, true)


func _sticky(at: Vector2, text: String, paper: Color, tilt: float) -> void:
	art.draw_set_transform(at, tilt, Vector2.ONE)
	art.draw_rect(Rect2(Vector2(-54 + 4, -34 + 5), Vector2(108, 68)), Palette.SHADOW)
	art.draw_rect(Rect2(Vector2(-54, -34), Vector2(108, 68)), paper)
	art.draw_rect(Rect2(Vector2(-54, 18), Vector2(108, 16)), paper.darkened(0.06))
	art.draw_rect(Rect2(Vector2(-22, -40), Vector2(44, 13)), Palette.NOTE_TAPE)
	art.draw_string(Palette.marker(), Vector2(-54, 14), text, HORIZONTAL_ALIGNMENT_CENTER, 108, 30, Palette.INK)
	art.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _stickies(at: Vector2, gap: float) -> void:
	_sticky(at, "BUY", Palette.NOTE_YELLOW, -0.08)
	_sticky(at + Vector2(gap, 8), "SELL", Palette.STICKER_PINK, 0.06)
	_sticky(at + Vector2(gap * 2, -4), "TRADE", Palette.NOTE_PAPER, -0.04)


## SIGN 1: one wide panel, MODEM big, CYBER SHOP under it, stickies along the bottom edge.
func _sign_horizontal(at: Vector2) -> void:
	var u := 17.0
	var r := Rect2(at, Vector2(780, 330))
	_rounded_border(r, 34, Palette.CELL_PINK)
	var mw := CyberType.width("MODEM", u)
	CyberType.draw_text(art, at + Vector2((r.size.x - mw) * 0.5, 44), "MODEM", u, Palette.CELL_PINK, 4.0)
	var cw := CyberType.width("CYBER SHOP", 7.0)
	CyberType.draw_text(art, at + Vector2((r.size.x - cw) * 0.5, 186), "CYBER SHOP", 7.0, Palette.NET_CYAN, 2.4, false)
	_stickies(at + Vector2(210, 310), 180)


## SIGN 2 (revised): the tall blade for the left edge of the Modem screen. MODEM
## stacked down it and CYBER SHOP (cyan) at its foot, both inside the pink border, both
## sprouting circuit traces; traces also run off the border; BUY and SELL sticky notes
## overlap the bottom-right corner.
func _sign_vertical(at: Vector2) -> void:
	var u := 12.0
	var r := Rect2(at, Vector2(170, 560))
	_rounded_border(r, 30, Palette.CELL_PINK)
	_border_traces(r, Palette.CELL_PINK)
	for i in 5:
		var ch := "MODEM"[i]
		CyberType.draw_text(art, at + Vector2((r.size.x - 4.0 * u) * 0.5, 28 + i * 84), ch, u, Palette.CELL_PINK, 3.5, i == 0 or i == 4, 0.75)
	var cu := 4.8
	for k in 2:
		var word: String = ["CYBER", "SHOP"][k]
		CyberType.draw_text(art, at + Vector2((r.size.x - CyberType.width(word, cu)) * 0.5, 452 + k * 46), word, cu, Palette.NET_CYAN, 2.0, false, 0.35)
	_sticky(at + Vector2(168, 548), "BUY", Palette.NOTE_YELLOW, 0.1)
	_sticky(at + Vector2(206, 606), "SELL", Palette.STICKER_PINK, -0.07)


## Circuit traces running off the sign's border: out from the edge, a 45-degree jog, a pad.
func _border_traces(r: Rect2, col: Color) -> void:
	var specs := [[Vector2(r.position.x, r.position.y + 90), Vector2(-1, 0), Vector2(-1, -1)], [Vector2(r.position.x, r.position.y + 260), Vector2(-1, 0), Vector2(-1, 1)],
		[Vector2(r.position.x, r.position.y + 400), Vector2(-1, 0), Vector2(-1, 0)], [Vector2(r.end.x, r.position.y + 70), Vector2(1, 0), Vector2(1, -1)],
		[Vector2(r.end.x, r.position.y + 200), Vector2(1, 0), Vector2(1, 1)], [Vector2(r.end.x, r.position.y + 330), Vector2(1, 0), Vector2(1, -1)],
		[Vector2(r.position.x + 50, r.position.y), Vector2(0, -1), Vector2(-1, -1)], [Vector2(r.position.x + 120, r.position.y), Vector2(0, -1), Vector2(1, -1)],
		[Vector2(r.position.x + 40, r.end.y), Vector2(0, 1), Vector2(-1, 1)], [Vector2(r.end.x, r.position.y + 440), Vector2(1, 0), Vector2(1, 1)]]
	for k in specs.size():
		var sp: Array = specs[k]
		var a: Vector2 = sp[0]
		var b: Vector2 = a + sp[1] * (18.0 + (k % 3) * 10.0)
		var c: Vector2 = b + (sp[2] as Vector2).normalized() * (14.0 + (k % 2) * 12.0)
		var pts := PackedVector2Array([a, b, c])
		art.draw_polyline(pts, Color(col, 0.2), 7.0, true)
		art.draw_polyline(pts, Color(col, 0.85), 2.0, true)
		art.draw_circle(c, 5.0, Color(col, 0.9))
		art.draw_circle(c, 2.2, Palette.NIGHT_SKY)


## SIGN 3: a stacked badge, MODEM in a rounded box, CYBER SHOP on its own rounded strip
## below, stickies fanned to the right.
func _sign_stacked(at: Vector2) -> void:
	var u := 13.0
	var top := Rect2(at, Vector2(470, 170))
	_rounded_border(top, 40, Palette.CELL_PINK)
	CyberType.draw_text(art, at + Vector2((top.size.x - CyberType.width("MODEM", u)) * 0.5, 44), "MODEM", u, Palette.CELL_PINK, 3.5)
	var strip := Rect2(at + Vector2(40, 196), Vector2(390, 80))
	_rounded_border(strip, 36, Palette.NET_CYAN)
	CyberType.draw_text(art, strip.position + Vector2((strip.size.x - CyberType.width("CYBER SHOP", 5.2)) * 0.5, 24), "CYBER SHOP", 5.2, Palette.NET_CYAN, 2.2, false)
	_sticky(at + Vector2(560, 40), "BUY", Palette.NOTE_YELLOW, 0.09)
	_sticky(at + Vector2(590, 140), "SELL", Palette.STICKER_PINK, -0.06)
	_sticky(at + Vector2(565, 240), "TRADE", Palette.NOTE_PAPER, 0.04)
