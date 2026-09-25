extends Control
## Design lab: three Modem storefront backdrops (the shop as a real corner store in the
## city, MODEM sign on the building, BUY / SELL / TRADE as signage, not buttons).
## Run: godot --path . res://tools/design_lab/modem_backdrops.tscn -- --store=1|2|3

var store: int = 1
var art: Control


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--store="):
			store = int(a.trim_prefix("--store="))
	var bg := WireframeBackground.new()
	bg.city.dim = 0.45
	add_child(bg)
	bg.set_district(&"")
	art = Control.new()
	art.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	art.draw.connect(_draw_art)
	add_child(art)


func _draw_art() -> void:
	# Street-level dusk: fade the top of the city into a dark sky, a wet street below.
	art.draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(1280, 0), Vector2(1280, 720), Vector2(0, 720)]),
		PackedColorArray([Color(0.02, 0.02, 0.06, 0.85), Color(0.02, 0.02, 0.06, 0.85), Color(0.02, 0.02, 0.06, 0.2), Color(0.02, 0.02, 0.06, 0.2)]))
	match store:
		1:
			_corner_store()
		2:
			_kiosk()
		_:
			_basement()
	art.draw_rect(Rect2(0, 0, 1280, 30), Color(0, 0, 0, 0.9))
	art.draw_string(Palette.mono(), Vector2(12, 21), ["", "S1  CORNER STORE (isometric, like the reference)", "S2  NIGHT MARKET KIOSK (front-on stall)", "S3  BASEMENT DEN (stairs down under the sign)"][store], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.CELL_ACID)


func _ink(a: Vector2, b: Vector2, col: Color, w: float = 2.0) -> void:
	art.draw_line(a, b, Color(col, 0.18), w * 4.0)
	art.draw_line(a, b, col, w)


func _neon_text(at: Vector2, text: String, size: int, col: Color, vertical: bool = false) -> void:
	if vertical:
		for i in text.length():
			_neon_text(at + Vector2(0, i * size * 1.02), text[i], size, col)
		return
	for k in 3:
		art.draw_string(Palette.display(), at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size + k * 3, Color(col, 0.1))
	art.draw_string(Palette.display(), at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col.lightened(0.35))


func _sign_box(r: Rect2, col: Color) -> void:
	art.draw_rect(r, Color(0.02, 0.02, 0.05, 0.95))
	art.draw_rect(r.grow(3), Color(col, 0.18), false, 6.0)
	art.draw_rect(r, col, false, 2.0)


## S1: an isometric two-storey corner shop on a street corner, a tall vertical MODEM
## blade sign on the corner, BUY / SELL / TRADE lightboxes over the windows.
func _corner_store() -> void:
	var c := Vector2(620, 640)
	var w := 360.0
	var d := 170.0
	var h := 250.0
	var left := c + Vector2(-w, -w * 0.5)
	var right := c + Vector2(d * 2.0, -d)
	var up := Vector2(0, -h)
	var wall_l := Color("#141B2C")
	var wall_r := Color("#0B0F1A")
	art.draw_colored_polygon(PackedVector2Array([left, c, c + up, left + up]), wall_l)
	art.draw_colored_polygon(PackedVector2Array([c, right, right + up, c + up]), wall_r)
	art.draw_colored_polygon(PackedVector2Array([left + up, c + up, right + up, left + up + (right - c)]), Color("#1C2A55"))
	for e in [[left, c], [c, right], [left + up, c + up], [c + up, right + up], [left, left + up], [c, c + up], [right, right + up]]:
		_ink(e[0], e[1], Palette.CELL_PINK, 1.8)
	# Shop windows: lit glass along the ground floor with shelves of chips.
	for k in 3:
		var a := left.lerp(c, 0.08 + k * 0.31)
		var b := left.lerp(c, 0.33 + k * 0.31)
		var glass := PackedVector2Array([a + Vector2(0, -20), b + Vector2(0, -20), b + Vector2(0, -130), a + Vector2(0, -130)])
		art.draw_colored_polygon(glass, Color(Palette.NET_CYAN, 0.2))
		art.draw_polyline(glass + PackedVector2Array([glass[0]]), Palette.NET_CYAN, 1.5)
		for s in 3:
			art.draw_line(a.lerp(b, 0.1) + Vector2(0, -45 - s * 30), a.lerp(b, 0.9) + Vector2(0, -45 - s * 30), Color(Palette.CELL_ACID, 0.5), 2.0)
	# Door on the right face.
	var da := c.lerp(right, 0.3)
	var db := c.lerp(right, 0.55)
	art.draw_colored_polygon(PackedVector2Array([da, db, db + Vector2(0, -120), da + Vector2(0, -120)]), Color(Palette.CRT_AMBER, 0.35))
	_ink(da + Vector2(0, -120), db + Vector2(0, -120), Palette.CRT_AMBER)
	# Awning.
	var aw := PackedVector2Array([left + Vector2(0, -140), c + Vector2(0, -140), c + Vector2(20, -118), left + Vector2(20, -118)])
	art.draw_colored_polygon(aw, Color(Palette.CELL_PINK, 0.55))
	for k in 8:
		var p := left.lerp(c, k / 8.0) + Vector2(0, -140)
		art.draw_line(p, p + Vector2(20, 22), Color(Palette.PAPER, 0.4), 3.0)
	# Signage over the windows: BUY SELL TRADE lightboxes (signage, not buttons).
	var labels := [["BUY", Palette.NET_CYAN], ["SELL", Palette.CELL_PINK], ["TRADE", Palette.CRT_AMBER]]
	for k in 3:
		var p := left.lerp(c, 0.1 + k * 0.31) + Vector2(0, -165)
		art.draw_set_transform(p, 0.46, Vector2.ONE)
		_sign_box(Rect2(-6, -30, 96, 40), labels[k][1])
		_neon_text(Vector2(4, 2), labels[k][0], 30, labels[k][1])
		art.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	# The MODEM blade sign on the corner.
	var blade := Rect2(c + Vector2(-44, -h - 200), Vector2(88, 380))
	_sign_box(blade, Palette.CELL_PINK)
	_neon_text(blade.position + Vector2(14, 70), "MODEM", 66, Palette.CELL_PINK, true)
	art.draw_set_transform(c + Vector2(70, -h + 70), -0.46, Vector2.ONE)
	art.draw_string(Palette.marker(), Vector2.ZERO, "CYBER SHOP", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Palette.NET_CYAN)
	art.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	# Wet street reflection.
	art.draw_rect(Rect2(blade.position.x + 10, 650, 66, 70), Color(Palette.CELL_PINK, 0.12))


## S2: a front-on night-market kiosk: roller shutter half up, a cable-hung MODEM sign,
## signage strip, crates of chips, the city behind.
func _kiosk() -> void:
	var r := Rect2(300, 250, 680, 360)
	art.draw_rect(r, Color("#0B0F1A"))
	art.draw_rect(Rect2(r.position, Vector2(r.size.x, 110)), Color("#1D2027"))
	for k in 10:
		art.draw_line(r.position + Vector2(0, k * 11), r.position + Vector2(r.size.x, k * 11), Color(1, 1, 1, 0.08), 1.0)
	var counter := Rect2(r.position + Vector2(0, 110), Vector2(r.size.x, 250))
	art.draw_rect(counter, Color(Palette.CRT_AMBER, 0.12))
	for k in 5:
		art.draw_rect(Rect2(counter.position + Vector2(30 + k * 130, 150), Vector2(100, 70)), Color("#141B2C"))
		art.draw_rect(Rect2(counter.position + Vector2(30 + k * 130, 150), Vector2(100, 70)), Palette.NET_CYAN, false, 1.5)
		for m in 3:
			art.draw_rect(Rect2(counter.position + Vector2(40 + k * 130 + m * 28, 160), Vector2(20, 20)), Color(Palette.CELL_ACID, 0.6))
	_ink(r.position, r.position + Vector2(r.size.x, 0), Palette.CELL_PINK)
	_ink(r.position, r.position + Vector2(0, r.size.y), Palette.CELL_PINK)
	_ink(r.position + Vector2(r.size.x, 0), r.end, Palette.CELL_PINK)
	# Hanging MODEM sign.
	var sign_r := Rect2(470, 110, 340, 100)
	_ink(Vector2(500, 30), sign_r.position + Vector2(30, 0), Color(1, 1, 1, 0.4), 1.0)
	_ink(Vector2(780, 30), sign_r.position + Vector2(310, 0), Color(1, 1, 1, 0.4), 1.0)
	_sign_box(sign_r, Palette.CELL_PINK)
	_neon_text(sign_r.position + Vector2(40, 84), "MODEM", 78, Palette.CELL_PINK)
	# Signage strip.
	var strip := Rect2(r.position + Vector2(0, 110), Vector2(r.size.x, 40))
	art.draw_rect(strip, Color(0, 0, 0, 0.8))
	_neon_text(strip.position + Vector2(60, 32), "BUY", 30, Palette.NET_CYAN)
	_neon_text(strip.position + Vector2(280, 32), "SELL", 30, Palette.CELL_PINK)
	_neon_text(strip.position + Vector2(500, 32), "TRADE", 30, Palette.CRT_AMBER)
	art.draw_string(Palette.marker(), Vector2(1000, 300), "CYBER\nSHOP", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Palette.NET_CYAN)


## S3: a basement den: stairs down from the street under a big angled MODEM sign, the
## doorway glowing, signage painted on the wall.
func _basement() -> void:
	var wall := PackedVector2Array([Vector2(160, 170), Vector2(1120, 170), Vector2(1120, 640), Vector2(160, 640)])
	art.draw_colored_polygon(wall, Color("#101832"))
	for k in 12:
		art.draw_line(Vector2(160, 190 + k * 38), Vector2(1120, 190 + k * 38), Color(1, 1, 1, 0.04), 1.0)
	# Stairwell.
	var top_l := Vector2(480, 460)
	var top_r := Vector2(800, 460)
	art.draw_colored_polygon(PackedVector2Array([top_l, top_r, Vector2(740, 640), Vector2(540, 640)]), Color(0.01, 0.01, 0.02))
	for k in 6:
		var y := 470 + k * 28
		var t := float(k) / 6.0
		art.draw_line(Vector2(lerpf(480, 540, t), y), Vector2(lerpf(800, 740, t), y), Color(Palette.CRT_AMBER, 0.35 + t * 0.4), 2.0)
	art.draw_rect(Rect2(590, 560, 100, 80), Color(Palette.CRT_AMBER, 0.5))
	_ink(top_l, Vector2(540, 640), Palette.NET_CYAN)
	_ink(top_r, Vector2(740, 640), Palette.NET_CYAN)
	# The big angled MODEM sign over the stairs.
	art.draw_set_transform(Vector2(640, 330), -0.06, Vector2.ONE)
	_sign_box(Rect2(-240, -80, 480, 150), Palette.CELL_PINK)
	_neon_text(Vector2(-200, 45), "MODEM", 110, Palette.CELL_PINK)
	art.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	# Painted signage.
	_neon_text(Vector2(210, 300), "BUY", 44, Palette.NET_CYAN)
	_neon_text(Vector2(210, 380), "SELL", 44, Palette.CELL_PINK)
	_neon_text(Vector2(930, 300), "TRADE", 44, Palette.CRT_AMBER)
	art.draw_string(Palette.marker(), Vector2(900, 400), "CYBER SHOP ↓", HORIZONTAL_ALIGNMENT_LEFT, -1, 32, Palette.NET_CYAN)
