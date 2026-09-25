class_name NeonCity
extends Control
## The neon-night backdrop (STYLE_GUIDE 1, "Neon city"): an isometric city seen from
## above, dark blocks with lit windows, neon roof edges and glowing streets. The city
## geometry is built once per size into a single triangle array (cheap to draw); a
## lightweight overlay animates traffic trails, roof beacons and rain unless
## reduce-effects. Pure view: deterministic from `city_seed`, never touches game state.

## Tile half-width / half-height of the isometric grid (2:1).
const TILE_A := 34.0
const TILE_B := 17.0
## Every Nth row and column of lots starts an avenue STREET_WIDTH lots wide.
const STREET_EVERY := 6
const STREET_WIDTH := 2

## Decoration seed (a view hash, not game randomness).
var city_seed: int = 7
## 0 = full brightness, 1 = black. Keeps panels readable over the city.
var dim: float = 0.25
## Neon accent colours (roof edges, signs, street trails).
var accents: Array[Color] = [Palette.CELL_PINK, Palette.NET_CYAN, Palette.NEON_VIOLET]
## Corporate wireframe creeping over the city as Heat rises (0-1, GDD 9.4).
var corp_color: Color = Palette.CORP_SOLACE
var corp_creep: float = 0.0
## Diagonal rain streaks (the physical world, seen through the HQ window).
var rain: bool = false
## Net mode: streets read as circuit traces (cyan), fewer warm windows.
var net_mode: bool = false
## Animation clock, advanced unless reduce-effects.
var anim_t: float = 0.0

var _fx: Control
var _built_for: Vector2 = Vector2.ZERO
var _trails: Array[Dictionary] = []
var _beacons: Array[Dictionary] = []


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fx = Control.new()
	_fx.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fx.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fx.draw.connect(_draw_fx)
	add_child(_fx)
	resized.connect(queue_redraw)


## Rebuilds the static city (after a colour or creep change).
func refresh() -> void:
	_built_for = Vector2.ZERO
	queue_redraw()


func _process(delta: float) -> void:
	if Settings.reduce_effects or not is_visible_in_tree():
		return
	anim_t += delta
	_fx.queue_redraw()


## Deterministic 0-1 hash of three integers (view decoration only).
func _h(a: int, b: int, c: int = 0) -> float:
	var n := (a * 73856093) ^ (b * 19349663) ^ (c * 83492791) ^ (city_seed * 2654435761)
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65535.0


func _accent(a: int, b: int) -> Color:
	var col := accents[int(_h(a, b, 11) * accents.size()) % accents.size()]
	if corp_creep > 0.0 and _h(a, b, 12) < corp_creep * 0.7:
		col = corp_color
	return col


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Palette.NIGHT_SKY)
	if size.x < 2.0 or size.y < 2.0:
		return
	_trails.clear()
	_beacons.clear()
	var verts := PackedVector2Array()
	var cols := PackedColorArray()
	var ox := size.x * 0.5
	var oy := -size.y * 0.35
	var s_max := int((size.y - oy + 300.0) / TILE_B) + 2
	var d_max := int(size.x / (2.0 * TILE_A)) + 3
	var haze_a := accents[0]
	var haze_b := accents[1 % accents.size()]
	for s in range(0, s_max):
		for d in range(-d_max, d_max + 1):
			if (s + d) % 2 != 0:
				continue
			var i := (s + d) / 2
			var j := (s - d) / 2
			var c := Vector2(ox + d * TILE_A, oy + s * TILE_B)
			if c.y < -TILE_B * 2.0:
				continue
			var street_i := posmod(i, STREET_EVERY) < STREET_WIDTH
			var street_j := posmod(j, STREET_EVERY) < STREET_WIDTH
			if street_i or street_j:
				_street(verts, cols, c, street_i, street_j, i, j)
				continue
			_building(verts, cols, c, i, j, haze_a, haze_b)
	var idx := PackedInt32Array()
	idx.resize(verts.size())
	for k in verts.size():
		idx[k] = k
	if not verts.is_empty():
		RenderingServer.canvas_item_add_triangle_array(get_canvas_item(), idx, verts, cols)
	# Haze: a soft glow band near the bottom and darkening towards the top for text.
	var haze := PackedColorArray([Color(Palette.NIGHT_SKY, 0.75), Color(Palette.NIGHT_SKY, 0.75), Color(Palette.NIGHT_SKY, 0.0), Color(Palette.NIGHT_SKY, 0.0)])
	draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(size.x, 0), Vector2(size.x, size.y * 0.3), Vector2(0, size.y * 0.3)]), haze)
	if dim > 0.0:
		draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.NIGHT_SKY, dim))
	# Vignette.
	var v := Color(0, 0, 0, 0.55)
	var clear := Color(0, 0, 0, 0)
	draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(size.x * 0.18, 0), Vector2(size.x * 0.18, size.y), Vector2(0, size.y)]), PackedColorArray([v, clear, clear, v]))
	draw_polygon(PackedVector2Array([Vector2(size.x * 0.82, 0), Vector2(size.x, 0), Vector2(size.x, size.y), Vector2(size.x * 0.82, size.y)]), PackedColorArray([clear, v, v, clear]))
	_built_for = size
	_fx.queue_redraw()


func _quad(verts: PackedVector2Array, cols: PackedColorArray, a: Vector2, b: Vector2, c: Vector2, d: Vector2, ca: Color, cb: Color, cc: Color, cd: Color) -> void:
	verts.append_array([a, b, c, a, c, d])
	cols.append_array([ca, cb, cc, ca, cc, cd])


func _diamond(c: Vector2, scale: float) -> Array[Vector2]:
	return [c + Vector2(0, -TILE_B * scale), c + Vector2(TILE_A * scale, 0), c + Vector2(0, TILE_B * scale), c + Vector2(-TILE_A * scale, 0)]


func _street(verts: PackedVector2Array, cols: PackedColorArray, c: Vector2, along_i: bool, along_j: bool, i: int, j: int) -> void:
	var p := _diamond(c, 1.0)
	var col := Palette.NIGHT_STREET
	_quad(verts, cols, p[0], p[1], p[2], p[3], col, col, col, col)
	# Street trail segments (the overlay animates light along them).
	var trail_col := Palette.NET_CYAN if net_mode else _accent(i if along_i else 0, j if along_j else 0)
	# Lane markings only on the avenue's far row; the near row stays dark asphalt.
	if (along_i and posmod(i, STREET_EVERY) != 1) or (along_j and posmod(j, STREET_EVERY) != 1):
		along_i = along_i and posmod(i, STREET_EVERY) == 1
		along_j = along_j and posmod(j, STREET_EVERY) == 1
		if not (along_i or along_j):
			return
	if along_i and not along_j:
		_trails.append({"a": (p[0] + p[1]) * 0.5, "b": (p[3] + p[2]) * 0.5, "color": trail_col, "phase": _h(i, j, 3)})
	elif along_j and not along_i:
		_trails.append({"a": (p[0] + p[3]) * 0.5, "b": (p[1] + p[2]) * 0.5, "color": trail_col, "phase": _h(i, j, 4)})
	var glow := Color(trail_col, 0.3 if net_mode else 0.22)
	# A street at fixed i runs along j (screen -A,+B); at fixed j it runs along i.
	var mid_a := (p[0] + p[1]) * 0.5 if along_i else (p[0] + p[3]) * 0.5
	var mid_b := (p[3] + p[2]) * 0.5 if along_i else (p[1] + p[2]) * 0.5
	if along_i != along_j:
		var n := (mid_b - mid_a).orthogonal().normalized()
		_quad(verts, cols, mid_a - n * 5.0, mid_b - n * 5.0, mid_b + n * 5.0, mid_a + n * 5.0, Color(glow, glow.a * 0.4), Color(glow, glow.a * 0.4), Color(glow, glow.a * 0.4), Color(glow, glow.a * 0.4))
		var core := Color(trail_col, 0.75 if net_mode else 0.55)
		_quad(verts, cols, mid_a - n, mid_b - n, mid_b + n, mid_a + n, core, core, core, core)


func _building(verts: PackedVector2Array, cols: PackedColorArray, c: Vector2, i: int, j: int, haze_a: Color, haze_b: Color) -> void:
	var inset := 0.78 + _h(i, j, 1) * 0.12
	var p := _diamond(c, inset)
	var district := _h(i / STREET_EVERY, j / STREET_EVERY, 9)
	var tall := _h(i, j, 2)
	var h := 8.0 + tall * tall * 60.0 + district * 34.0
	if tall > 0.94:
		h += 110.0 + district * 80.0
	var up := Vector2(0, -h)
	var base_tint := haze_a.lerp(haze_b, _h(i, j, 5))
	var left_top := Palette.NIGHT_BLOCK_LIT
	var left_bot := Palette.NIGHT_BLOCK.lerp(base_tint, 0.06)
	var right_top := Palette.NIGHT_BLOCK
	var right_bot := Palette.NIGHT_STREET.lerp(base_tint, 0.04)
	# Left face L-B, right face B-R, roof.
	_quad(verts, cols, p[3], p[2], p[2] + up, p[3] + up, left_bot, left_bot, left_top, left_top)
	_quad(verts, cols, p[2], p[1], p[1] + up, p[2] + up, right_bot, right_bot, right_top, right_top)
	var roof := Palette.NIGHT_BLOCK_LIT.lightened(0.08)
	_quad(verts, cols, p[0] + up, p[1] + up, p[2] + up, p[3] + up, roof, roof, roof.darkened(0.2), roof)
	# Windows: parallelograms on both faces, a share lit.
	var rows := int(h / 8.0)
	var lit_share := 0.18 + district * 0.25
	for face in 2:
		var a := p[3] if face == 0 else p[2]
		var b := p[2] if face == 0 else p[1]
		var step := (b - a) / 3.0
		for col_i in 3:
			for r in rows:
				var roll := _h(i * 7 + face, j * 13 + col_i, r)
				if roll > lit_share:
					continue
				var o := a + step * (col_i + 0.28) + Vector2(0, -6.0 - r * 8.0)
				var w := step * 0.44
				var wc := _window_color(roll / maxf(lit_share, 0.001), i, j)
				if face == 1:
					wc = wc.darkened(0.3)
				_quad(verts, cols, o, o + w, o + w + Vector2(0, -3.5), o + Vector2(0, -3.5), wc, wc, wc, wc)
	# Neon: roof outline on some buildings, a vertical sign on others.
	var n_roll := _h(i, j, 6)
	if n_roll < 0.16 or tall > 0.93:
		var nc := _accent(i, j)
		for e in 4:
			_neon(verts, cols, p[e] + up, p[(e + 1) % 4] + up, nc)
	elif n_roll < 0.26 and h > 50.0:
		var s0 := p[3].lerp(p[2], 0.5) + Vector2(0, -h * 0.25)
		_neon(verts, cols, s0, s0 + Vector2(0, -h * 0.5), _accent(i + 3, j))
	if tall > 0.9:
		_beacons.append({"pos": p[0] + up + Vector2(0, -2), "color": _accent(i, j + 1), "phase": _h(i, j, 8)})


## A neon tube: a soft wide glow and a crisp core, as quads in the city's draw order.
func _neon(verts: PackedVector2Array, cols: PackedColorArray, a: Vector2, b: Vector2, col: Color) -> void:
	var n := (b - a).orthogonal().normalized()
	var glow := Color(col, 0.16)
	var core := Color(col, 0.95)
	_quad(verts, cols, a - n * 3.0, b - n * 3.0, b + n * 3.0, a + n * 3.0, glow, glow, glow, glow)
	_quad(verts, cols, a - n * 0.7, b - n * 0.7, b + n * 0.7, a + n * 0.7, core, core, core, core)


func _window_color(t: float, i: int, j: int) -> Color:
	if net_mode:
		return Color(Palette.NET_CYAN, 0.55) if t < 0.7 else Color(_accent(i, j), 0.7)
	if t < 0.45:
		return Color(Palette.CRT_AMBER, 0.7)
	if t < 0.7:
		return Color(Palette.NET_CYAN, 0.65)
	if t < 0.88:
		return Color(Palette.CELL_PINK, 0.65)
	return Color(Palette.NEON_VIOLET, 0.7)


func _draw_fx() -> void:
	if _built_for != size:
		return
	# Traffic: bright dashes sliding along the streets.
	for t in _trails:
		var a: Vector2 = t["a"]
		var b: Vector2 = t["b"]
		var k := fmod(float(t["phase"]) + anim_t * 0.35, 1.0)
		var p := a.lerp(b, k)
		var col: Color = t["color"]
		_fx.draw_line(p, p + (b - a) * 0.35, Color(col, 0.55), 2.0)
	for bcn in _beacons:
		var on := fmod(float(bcn["phase"]) * 3.0 + anim_t, 1.6) < 0.8
		var col: Color = bcn["color"]
		_fx.draw_circle(bcn["pos"], 5.0 if on else 3.0, Color(col, 0.25 if on else 0.1))
		_fx.draw_circle(bcn["pos"], 1.6, Color(col, 0.95 if on else 0.4))
	if rain:
		var off := fmod(anim_t * 480.0, 80.0)
		for k in 70:
			var rx := fmod(float(k * 97 + city_seed * 13), size.x + 80.0) - 40.0
			var ry := fmod(float((k * 53) % 720) + off * (1.0 + (k % 3) * 0.35), size.y)
			_fx.draw_line(Vector2(rx, ry), Vector2(rx - 5, ry + 22), Color(Palette.NET_CYAN, 0.18), 1.0)
