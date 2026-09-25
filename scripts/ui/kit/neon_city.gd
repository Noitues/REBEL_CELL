class_name NeonCity
extends Control
## The neon-night backdrop (STYLE_GUIDE 1, "Neon city"): one isometric city seen from
## above. Buildings are near-black, dark blue-grey and dark grey masses inked with neon
## outlines (roof edges and verticals) in amber, purple, pink, cyan and green; a sketch
## shader wobbles the lines so they read hand-drawn. The city is split into organic
## territories: each corporation owns one (its own building mix, more ink in its colour,
## a unique landmark HQ), with the neutral Sprawl between them. The camera looks at the
## territory named by `district` (or pans the whole city, `pan`). Geometry is built once
## per size into one triangle array; a light overlay animates traffic, beacons and rain
## unless reduce-effects. Every building's roof outline is kept (`roof_of`) so map
## overlays can mark real buildings. Pure view: deterministic, never touches game state.

## Emitted after the city geometry is rebuilt (overlays re-read roofs and positions).
signal rebuilt

const SKETCH_SHADER := preload("res://shaders/city_sketch.gdshader")

## Tile half-width / half-height of the isometric grid (2:1).
const TILE_A := 34.0
const TILE_B := 17.0
## Streets are one lot wide; blocks between them run BLOCK_MIN..BLOCK_MAX lots, so the
## grid is irregular. (STREET_EVERY is the typical spacing, for overlays.)
const STREET_EVERY := 6
const BLOCK_MIN := 3
const BLOCK_MAX := 6
const GRID_RANGE := 260
## Neon ink colours (every district uses all five, weighted to its corporation).
const INKS: Array[Color] = [Color("#FFB000"), Color("#B04DFF"), Color("#FF3DA8"), Color("#5CE1FF"), Color("#3DFF8B")]
## Building masses: black, dark grey-blue, dark grey.
const FILLS: Array[Color] = [Color("#06070B"), Color("#141B2C"), Color("#1D2027")]
const GROUND := Color("#0A0C14")
const STREET := Color("#050609")
const FACE_LIGHT := Color("#2A3350")

## District profiles: building mix weights [box, stepped, cylinder, hex, taper, needle,
## warehouse], height scale, share of lines in the corporation colour, layout seed.
const DISTRICTS := {
	&"solace": {"mix": [3, 2, 4, 1, 1, 1, 1], "height": 1.0, "corp_ink": 0.58, "seed": 11},
	&"meridian": {"mix": [3, 2, 0, 0, 0, 0, 6], "height": 0.7, "corp_ink": 0.58, "seed": 23},
	&"halcyon": {"mix": [3, 4, 1, 0, 4, 0, 1], "height": 1.0, "corp_ink": 0.58, "seed": 37},
	&"orbital": {"mix": [2, 1, 2, 1, 1, 5, 0], "height": 1.35, "corp_ink": 0.58, "seed": 41},
	&"rebel_cell": {"mix": [2, 2, 1, 5, 1, 1, 1], "height": 0.95, "corp_ink": 0.58, "seed": 53},
	&"": {"mix": [4, 3, 2, 1, 1, 1, 2], "height": 1.0, "corp_ink": 0.0, "seed": 7},
}
enum Shape { BOX, STEPPED, CYLINDER, HEX, TAPER, NEEDLE, WAREHOUSE,
	PYRAMID, OBELISK, MASTABA, PAGODA, GABLE, CLOCKTOWER, DOME, MINARET, STEP_TEMPLE }

## Culture themes (design review): building mixes over every Shape, cyberpunk-inked.
const CULTURES := {
	"egyptian": [2, 1, 0, 0, 0, 0, 1, 4, 3, 5, 0, 0, 0, 0, 0, 0],
	"chinese": [3, 2, 0, 0, 0, 1, 0, 0, 0, 0, 6, 2, 0, 0, 0, 0],
	"english": [3, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 7, 1, 0, 0, 0],
	"mayan": [2, 4, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 5],
	"arabic": [3, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 3, 0],
}

## Territory centres (grid lots) and their pull (bigger = larger territory). The
## corporations' HQs stand on their centres; &"" entries are the neutral Sprawl.
const TERRITORIES: Array[Dictionary] = [
	{"id": &"", "at": Vector2(0, 0), "pull": 1.0},
	{"id": &"solace", "at": Vector2(-34, -4), "pull": 1.15},
	{"id": &"meridian", "at": Vector2(4, -36), "pull": 1.25},
	{"id": &"halcyon", "at": Vector2(36, 2), "pull": 1.0},
	{"id": &"orbital", "at": Vector2(-6, 34), "pull": 0.9},
	{"id": &"rebel_cell", "at": Vector2(30, 32), "pull": 0.8},
	{"id": &"", "at": Vector2(-36, -40), "pull": 0.9},
	{"id": &"", "at": Vector2(40, -38), "pull": 0.8},
]
## How far territory borders wander (lots).
const BORDER_WARP := 11.0
## Ink palettes: 0 = full neon; 1-3 paler options (lerped toward a tint).
const INK_SETS: Array[Dictionary] = [
	{"name": "NEON", "tint": Color.WHITE, "amount": 0.0},
	{"name": "PASTEL NEON", "tint": Color.WHITE, "amount": 0.3},
	{"name": "FADED PRINT", "tint": Color("#C9BFD9"), "amount": 0.38},
	{"name": "COOL HAZE", "tint": Color("#D6F2FF"), "amount": 0.32},
]
## Pan margin (px beyond the screen on every side) and speed.
const PAN_MARGIN := 360.0

## Decoration seed (a view hash, not game randomness).
var city_seed: int = 7
## 0 = full brightness, 1 = black. Keeps panels readable over the city.
var dim: float = 0.25
## The territory the camera looks at (&"" = the whole city from the Sprawl).
var district: StringName = &"":
	set(v):
		if v != district:
			district = v
			refresh()
## Slowly pan around the city (main menu). Frozen under reduce-effects.
var pan: bool = false:
	set(v):
		pan = v
		_apply_pan_margin()
## Ink palette (INK_SETS index).
## Camera override: this grid point lands on `focus_anchor` (a screen fraction).
var focus_grid: Vector2 = Vector2.INF
var focus_anchor: Vector2 = Vector2(0.5, 0.5)
## Culture theme per territory (corp id -> CULTURES key); empty = the base mixes.
var cultures: Dictionary = {}
## Design review: big territory names over each HQ (the zoomed-out overview).
var territory_labels: bool = false
var ink_set: int = 3:
	set(v):
		ink_set = v
		refresh()
## Corporation colour (follows the district) and Heat creep (0-1, GDD 9.4).
var corp_color: Color = Palette.CORP_SOLACE
var corp_creep: float = 0.0
## Diagonal rain streaks (the physical world, seen through the HQ window).
var rain: bool = false
## Net mode: lanes read as circuit traces, a touch more cyan.
var net_mode: bool = false
## Animation clock, advanced unless reduce-effects.
var anim_t: float = 0.0
## Where the corporation HQ stands, as a fraction of the screen (ground point).
var hq_anchor: Vector2 = Vector2(0.8, 0.62)

var _fx: Control
var _built_for: Vector2 = Vector2.ZERO
var _trails: Array[Dictionary] = []
var _beacons: Array[Dictionary] = []
var _signs: Array[Dictionary] = []
var _verts := PackedVector2Array()
var _cols := PackedColorArray()
var _ox: float = 0.0
var _oy: float = 0.0
var _hq_rect: Rect2i = Rect2i()
var _profile: Dictionary = {}
## Territory of the lot being drawn and its corporation colour.
var _terr: StringName = &""
var _terr_col: Color = Color.WHITE
var _hq_rects: Dictionary = {}  # corp id -> Rect2i
var _pan_t: float = 0.0
var _inks: Array[Color] = []
## Roof outline (screen points, local) of the building on each lot: Vector2i -> Dictionary
## {"roof": PackedVector2Array, "base": Vector2, "shape": int, "height": float}.
var _roofs: Dictionary = {}
## Street rows/columns and each lot's index inside its block (built per draw).
var _street_i: Dictionary = {}
var _street_j: Dictionary = {}
var _local_i: Dictionary = {}
var _local_j: Dictionary = {}


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	material = ShaderMaterial.new()
	material.shader = SKETCH_SHADER
	_fx = Control.new()
	_fx.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fx.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fx.use_parent_material = true
	_fx.draw.connect(_draw_fx)
	add_child(_fx)
	resized.connect(queue_redraw)


func _ready() -> void:
	Settings.changed.connect(_apply_effects)
	_apply_effects()


func _apply_effects() -> void:
	var sm := material as ShaderMaterial
	sm.set_shader_parameter("scan_strength", 0.0 if Settings.reduce_effects else 0.07)
	sm.set_shader_parameter("flicker", 0.0 if Settings.reduce_effects else 0.012)


## Rebuilds the static city (after a district, colour or creep change).
func refresh() -> void:
	_built_for = Vector2.ZERO
	queue_redraw()


func _process(delta: float) -> void:
	if Settings.reduce_effects or not is_visible_in_tree():
		return
	anim_t += delta
	if pan:
		# A slow Lissajous drift across the city (about 6 px/s at its fastest).
		_pan_t += delta
		var dx := sin(_pan_t * 0.019) * PAN_MARGIN * 0.9
		var dy := sin(_pan_t * 0.013 + 1.0) * PAN_MARGIN * 0.7
		offset_left = -PAN_MARGIN + dx
		offset_right = PAN_MARGIN + dx
		offset_top = -PAN_MARGIN + dy
		offset_bottom = PAN_MARGIN + dy
	_fx.queue_redraw()


## Deterministic 0-1 hash of three integers (view decoration only).
func _h(a: int, b: int, c: int = 0) -> float:
	var n := (a * 73856093) ^ (b * 19349663) ^ (c * 83492791) ^ (city_seed * 2654435761)
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65535.0


## Line colour: the corporation's ink for its share of buildings, else any of the five.
func _ink(a: int, b: int) -> Color:
	var share: float = float(_profile.get("corp_ink", 0.0))
	if _terr == district and district != &"":
		share += corp_creep * 0.35
	if _terr != &"" and _h(a, b, 12) < share:
		return _terr_col
	if net_mode and _h(a, b, 13) < 0.25:
		return _pale(Palette.NET_CYAN)
	return _inks[int(_h(a, b, 11) * _inks.size()) % _inks.size()]


## Applies the ink palette's paleness to a colour.
func _pale(c: Color) -> Color:
	var set_def: Dictionary = INK_SETS[clampi(ink_set, 0, INK_SETS.size() - 1)]
	return c.lerp(set_def["tint"], float(set_def["amount"]))


## Smooth value noise in 0-1 (for territory borders).
func _vnoise(x: float, y: float, salt: int) -> float:
	var xi := floori(x)
	var yi := floori(y)
	var fx := x - xi
	var fy := y - yi
	var u := fx * fx * (3.0 - 2.0 * fx)
	var v := fy * fy * (3.0 - 2.0 * fy)
	var a := lerpf(_h(xi, yi, salt), _h(xi + 1, yi, salt), u)
	var b := lerpf(_h(xi, yi + 1, salt), _h(xi + 1, yi + 1, salt), u)
	return lerpf(a, b, v)


## The territory owning lot (i, j): nearest centre (weighted by pull) after warping the
## lot by two octaves of noise, so borders are organic rather than straight.
func territory_at(i: int, j: int) -> StringName:
	var w := Vector2(_vnoise(i * 0.07, j * 0.07, 70) - 0.5, _vnoise(i * 0.07, j * 0.07, 71) - 0.5) * BORDER_WARP * 2.0
	w += Vector2(_vnoise(i * 0.2, j * 0.2, 72) - 0.5, _vnoise(i * 0.2, j * 0.2, 73) - 0.5) * BORDER_WARP * 0.6
	var p := Vector2(i, j) + w
	var best: StringName = &""
	var best_d := INF
	for t in TERRITORIES:
		var d: float = p.distance_to(t["at"]) / float(t["pull"])
		if d < best_d:
			best_d = d
			best = t["id"]
	return best


## Where a corporation's HQ stands (grid), or the city centre.
static func hq_of(corporation_id: StringName) -> Vector2:
	for t in TERRITORIES:
		if t["id"] == corporation_id:
			return t["at"]
	return Vector2.ZERO


func _set_lot_context(i: int, j: int) -> void:
	_terr = territory_at(i, j)
	_profile = DISTRICTS.get(_terr, DISTRICTS[&""])
	_terr_col = _pale(Palette.corp_color(_terr)) if _terr != &"" else Color.WHITE


## Screen position (local to this control) of grid point (x, y) with the current camera.
func grid_to_local(x: float, y: float) -> Vector2:
	return _iso(x, y)


## The building on lot (i, j): {"roof", "base", "shape", "height"} or {}.
func roof_of(i: int, j: int) -> Dictionary:
	return _roofs.get(Vector2i(i, j), {})


## The nearest lot with a building to (x, y) within `radius` lots, avoiding `taken`.
func nearest_building(x: float, y: float, radius: int = 4, taken: Dictionary = {}) -> Vector2i:
	var best := Vector2i(roundi(x), roundi(y))
	var best_d := INF
	for di in range(-radius, radius + 1):
		for dj in range(-radius, radius + 1):
			var l := Vector2i(roundi(x) + di, roundi(y) + dj)
			if not _roofs.has(l) or taken.has(l):
				continue
			var d := Vector2(l).distance_to(Vector2(x, y))
			if d < best_d:
				best_d = d
				best = l
	return best


## True when lot (i, j) is a street (for overlays that route along streets).
func is_street(i: int, j: int) -> bool:
	return _street_i.has(i) or _street_j.has(j)


func _apply_pan_margin() -> void:
	var m := PAN_MARGIN if pan else 0.0
	offset_left = -m
	offset_top = -m
	offset_right = m
	offset_bottom = m


## Grid space (lots) to screen.
func _iso(x: float, y: float) -> Vector2:
	return Vector2(_ox + (x - y) * TILE_A, _oy + (x + y) * TILE_B)


func _grid_of(p: Vector2) -> Vector2:
	var d := (p.x - _ox) / TILE_A
	var s := (p.y - _oy) / TILE_B
	return Vector2((s + d) * 0.5, (s - d) * 0.5)


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Palette.NIGHT_SKY)
	if size.x < 2.0 or size.y < 2.0:
		return
	_inks.clear()
	for c in INKS:
		_inks.append(_pale(c))
	if district != &"":
		corp_color = _pale(Palette.corp_color(district))
	_trails.clear()
	_beacons.clear()
	_signs.clear()
	_roofs.clear()
	_verts = PackedVector2Array()
	_cols = PackedColorArray()
	# Camera: the focused HQ lands on hq_anchor; the whole city centres the Sprawl.
	var focus := hq_of(district) + Vector2(2.5, 2.5) if district != &"" else Vector2(0, 0)
	var anchor := Vector2(size.x * hq_anchor.x, size.y * hq_anchor.y) if district != &"" else size * 0.5
	if pan:
		anchor = size * 0.5
	if focus_grid != Vector2.INF:
		focus = focus_grid
		anchor = size * focus_anchor
	_ox = anchor.x - (focus.x - focus.y) * TILE_A
	_oy = anchor.y - (focus.x + focus.y) * TILE_B
	_hq_rects.clear()
	for t in TERRITORIES:
		if t["id"] != &"":
			var at: Vector2 = t["at"]
			_hq_rects[t["id"]] = Rect2i(int(at.x), int(at.y), 5, 5)
	_hq_rect = _hq_rects.get(district, Rect2i())
	_build_streets()
	var s_min := int(floor((-40.0 - _oy) / TILE_B)) - 2
	var s_max := int((size.y + 420.0 - _oy) / TILE_B) + 2
	var d_min := int(floor((-80.0 - _ox) / TILE_A)) - 1
	var d_max := int((size.x + 80.0 - _ox) / TILE_A) + 1
	for s in range(s_min, s_max):
		for d in range(d_min, d_max + 1):
			if posmod(s + d, 2) != 0:
				continue
			var i := (s + d) / 2
			var j := (s - d) / 2
			_set_lot_context(i, j)
			var in_hq := &""
			for cid in _hq_rects:
				if (_hq_rects[cid] as Rect2i).has_point(Vector2i(i, j)):
					in_hq = cid
					break
			if in_hq != &"":
				_plaza(i, j)
				var hr: Rect2i = _hq_rects[in_hq]
				if i == hr.end.x - 1 and j == hr.end.y - 1:
					_hq(in_hq, hr)
				continue
			var street_i := _street_i.has(i)
			var street_j := _street_j.has(j)
			if street_i or street_j:
				_street(i, j, street_i, street_j)
				continue
			_lot(i, j)
	var idx := PackedInt32Array()
	idx.resize(_verts.size())
	for k in _verts.size():
		idx[k] = k
	if not _verts.is_empty():
		RenderingServer.canvas_item_add_triangle_array(get_canvas_item(), idx, _verts, _cols)
	_verts = PackedVector2Array()
	_cols = PackedColorArray()
	if not pan:
		# Haze: darker towards the top for text; vignette at the sides.
		var top := Color(Palette.NIGHT_SKY, 0.7)
		var clear := Color(Palette.NIGHT_SKY, 0.0)
		draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(size.x, 0), Vector2(size.x, size.y * 0.28), Vector2(0, size.y * 0.28)]), PackedColorArray([top, top, clear, clear]))
		var v := Color(0, 0, 0, 0.5)
		var c0 := Color(0, 0, 0, 0)
		draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(size.x * 0.16, 0), Vector2(size.x * 0.16, size.y), Vector2(0, size.y)]), PackedColorArray([v, c0, c0, v]))
		draw_polygon(PackedVector2Array([Vector2(size.x * 0.84, 0), Vector2(size.x, 0), Vector2(size.x, size.y), Vector2(size.x * 0.84, size.y)]), PackedColorArray([c0, v, v, c0]))
	if dim > 0.0:
		draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.NIGHT_SKY, dim))
	_built_for = size
	_fx.queue_redraw()
	rebuilt.emit()


## Irregular street spacing along both axes (deterministic per district).
func _build_streets() -> void:
	for axis in 2:
		var streets := {}
		var local := {}
		var pos := -GRID_RANGE
		while pos < GRID_RANGE:
			streets[pos] = true
			var block := BLOCK_MIN + int(_h(pos, axis, 60) * (BLOCK_MAX - BLOCK_MIN + 1))
			for k in block:
				local[pos + 1 + k] = k
			pos += block + 1
		if axis == 0:
			_street_i = streets
			_local_i = local
		else:
			_street_j = streets
			_local_j = local


## Traffic 0-1 of a street lot: some avenues are busy, and everything near the HQ is.
func _traffic(i: int, j: int, along_i: bool) -> float:
	var t := _h(i if along_i else 0, 0 if along_i else j, 61)
	t = t * t
	var d := _hq_distance(i, j)
	t = maxf(t, clampf(1.0 - d / 12.0, 0.0, 1.0))
	return t


## Distance (lots) to the nearest corporation HQ centre.
func _hq_distance(i: int, j: int) -> float:
	var best := INF
	for cid in _hq_rects:
		best = minf(best, Vector2(i, j).distance_to(Vector2((_hq_rects[cid] as Rect2i).get_center())))
	return best


# --- Primitives ---------------------------------------------------------------------------

func _tri(a: Vector2, b: Vector2, c: Vector2, ca: Color, cb: Color, cc: Color) -> void:
	_verts.append_array([a, b, c])
	_cols.append_array([ca, cb, cc])


func _quad(a: Vector2, b: Vector2, c: Vector2, d: Vector2, ca: Color, cb: Color, cc: Color, cd: Color) -> void:
	_tri(a, b, c, ca, cb, cc)
	_tri(a, c, d, ca, cc, cd)


func _poly(pts: PackedVector2Array, col: Color) -> void:
	var c := Vector2.ZERO
	for p in pts:
		c += p
	c /= pts.size()
	for k in pts.size():
		_tri(c, pts[k], pts[(k + 1) % pts.size()], col, col, col)


## An inked line, drawn like a pen stroke: a soft glow, then a slightly bowed core in
## short segments (the sketch shader's wobble bends them further) whose thickness wanders
## and tapers, overshooting the corners by a varying amount, then a faint second pass a
## hair off the first, as if the line was gone over again.
func _ink_line(a: Vector2, b: Vector2, col: Color, width: float = 1.3, glow: bool = true) -> void:
	var length := a.distance_to(b)
	if length < 0.5:
		return
	var seed_a := int(a.x * 7.0 + b.y * 3.0)
	var seed_b := int(a.y * 5.0 + b.x * 11.0)
	var dir := (b - a) / length
	var n := dir.orthogonal()
	var over0 := 0.5 + _h(seed_a, seed_b, 22) * 3.5
	var over1 := 0.5 + _h(seed_b, seed_a, 23) * 3.5
	var a0 := a - dir * over0
	var b0 := b + dir * over1
	if glow:
		var g := Color(col, 0.15)
		_quad(a0 - n * 3.5, b0 - n * 3.5, b0 + n * 3.5, a0 + n * 3.5, g, g, g, g)
	var bow := (_h(seed_a, seed_b, 24) - 0.5) * minf(4.0, length * 0.05)
	_stroke(a0, b0, n, bow, width, Color(col, col.a * 0.95), seed_a)
	# The second pass: offset, shorter at one end, fainter and thinner.
	var shift := n * (0.8 + _h(seed_a, seed_b, 25) * 1.2) * (1.0 if _h(seed_b, seed_a, 26) < 0.5 else -1.0)
	var trim := dir * (_h(seed_a, seed_b, 27) * 4.0)
	_stroke(a0 + shift + trim, b0 + shift - trim * 0.5, n, -bow * 0.6, width * 0.65, Color(col, col.a * 0.45), seed_b)


func _stroke(a: Vector2, b: Vector2, n: Vector2, bow: float, width: float, col: Color, key: int) -> void:
	var steps := maxi(2, int(a.distance_to(b) / 5.0))
	var prev_l := Vector2.ZERO
	var prev_r := Vector2.ZERO
	for k in steps + 1:
		var t := float(k) / steps
		var p := a.lerp(b, t) + n * sin(t * PI) * bow
		var taper := clampf(minf(t, 1.0 - t) * 6.0, 0.65, 1.0)
		var w := width * taper * (0.75 + 0.5 * _h(key, k, 21))
		var l := p - n * w * 0.5
		var r := p + n * w * 0.5
		if k > 0:
			_quad(prev_l, l, r, prev_r, col, col, col, col)
		prev_l = l
		prev_r = r


## Grid rectangle footprint (lots) as screen points: back, right, front, left.
func _rect_pts(x0: float, y0: float, x1: float, y1: float) -> PackedVector2Array:
	return PackedVector2Array([_iso(x0, y0), _iso(x1, y0), _iso(x1, y1), _iso(x0, y1)])


## A grid rectangle turned by `angle` (radians) about its centre, as screen points.
func _turned(angle: float, x0: float, y0: float, x1: float, y1: float) -> PackedVector2Array:
	if absf(angle) < 0.001:
		return _rect_pts(x0, y0, x1, y1)
	var c := Vector2((x0 + x1) * 0.5, (y0 + y1) * 0.5)
	var pts := PackedVector2Array()
	for q in [Vector2(x0, y0), Vector2(x1, y0), Vector2(x1, y1), Vector2(x0, y1)]:
		var v: Vector2 = (q - c).rotated(angle) + c
		pts.append(_iso(v.x, v.y))
	return pts


## Regular n-gon footprint of grid radius r around (cx, cy).
func _ngon(cx: float, cy: float, r: float, n: int, rot: float = 0.0) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in n:
		var t := rot + TAU * k / n
		pts.append(_iso(cx + cos(t) * r, cy + sin(t) * r))
	return pts


## Extrudes a convex ground footprint: faces shaded by facing (left faces catch the
## city glow), a roof, window rows on vertical faces, and neon ink on the roof edge and
## the visible verticals. `z0` lifts the base (tiers); `top_scale` < 1 tapers it.
## Returns the roof points.
func _extrude(base: PackedVector2Array, z0: float, h: float, top_scale: float, fill: Color, ink: Color, lit: float = 0.2, key: int = 0) -> PackedVector2Array:
	var n := base.size()
	var c := Vector2.ZERO
	for p in base:
		c += p
	c /= n
	var bot := PackedVector2Array()
	var top := PackedVector2Array()
	for p in base:
		bot.append(p + Vector2(0, -z0))
		top.append(c + (p - c) * top_scale + Vector2(0, -z0 - h))
	var faces: Array[Dictionary] = []
	for k in n:
		var a := bot[k]
		var b := bot[(k + 1) % n]
		var e := b - a
		var nrm := Vector2(e.y, -e.x).normalized()
		if nrm.dot((a + b) * 0.5 - (c + Vector2(0, -z0))) < 0.0:
			nrm = -nrm
		if top_scale >= 0.99 and nrm.y <= 0.02:
			continue
		faces.append({"k": k, "n": nrm, "y": (a.y + b.y) * 0.5})
	faces.sort_custom(func(f1: Dictionary, f2: Dictionary) -> bool: return f1["y"] < f2["y"])
	var visible_v := {}
	for f in faces:
		var k: int = f["k"]
		var k2 := (k + 1) % n
		var nrm: Vector2 = f["n"]
		var light := clampf(0.5 - nrm.x * 0.5, 0.0, 1.0)
		var up_col := fill.lerp(FACE_LIGHT, 0.12 + light * 0.35)
		var low_col := fill.darkened(0.35)
		_quad(bot[k], bot[k2], top[k2], top[k], low_col, low_col, up_col, up_col)
		if nrm.y > 0.02:
			visible_v[k] = true
			visible_v[k2] = true
		if top_scale >= 0.99 and h > 14.0:
			_windows(bot[k], bot[k2], h, lit, key * 31 + k, nrm.x < 0.0)
	if top_scale > 0.05:
		_poly(top, fill.lerp(FACE_LIGHT, 0.25))
		for k in n:
			_ink_line(top[k], top[(k + 1) % n], ink)
	for k in visible_v:
		# Verticals at the silhouette and the front corners.
		_ink_line(bot[k], top[k], ink, 1.7, true)
	return top


func _windows(a: Vector2, b: Vector2, h: float, lit: float, key: int, bright: bool) -> void:
	var cols_n := maxi(1, int(a.distance_to(b) / 11.0))
	var rows := int((h - 6.0) / 8.0)
	var step := (b - a) / cols_n
	for ci in cols_n:
		for r in rows:
			var roll := _h(key, ci, r)
			if roll > lit:
				continue
			var o := a + step * (ci + 0.3) + Vector2(0, -5.0 - r * 8.0)
			var w := step * 0.4
			var wc: Color
			var t := roll / maxf(lit, 0.001)
			if t < 0.4:
				wc = Color(_inks[0], 0.75)
			elif t < 0.62:
				wc = Color(_inks[3], 0.7)
			elif t < 0.78:
				wc = Color(_terr_col if _terr != &"" else _inks[4], 0.75)
			elif t < 0.9:
				wc = Color(_inks[2], 0.7)
			else:
				wc = Color(_inks[1], 0.75)
			if not bright:
				wc = wc.darkened(0.3)
			_quad(o, o + w, o + w + Vector2(0, -3.2), o + Vector2(0, -3.2), wc, wc, wc, wc)


# --- Lots ---------------------------------------------------------------------------------

func _street(i: int, j: int, along_i: bool, along_j: bool) -> void:
	var p := _rect_pts(i, j, i + 1, j + 1)
	_quad(p[0], p[1], p[2], p[3], STREET, STREET, STREET, STREET)
	if along_i and along_j:
		return  # crossings stay dark; the strokes overshoot into them
	var traffic := _traffic(i, j, along_i)
	var col := _pale(Palette.NET_CYAN) if net_mode and _h(i, j, 62) < 0.5 else _ink(i if along_i else 0, j if along_j else 0)
	var a := _iso(i + 0.5, j) if along_i else _iso(i, j + 0.5)
	var b := _iso(i + 0.5, j + 1) if along_i else _iso(i + 1, j + 0.5)
	var nn := (b - a).orthogonal().normalized()
	if traffic > 0.4:
		# Busy streets: a broad painted band, then the band re-stroked two or three times
		# with slight offsets (hand-inked, gone over again), and a bright centre line.
		var k := (traffic - 0.4) / 0.6
		var band := lerpf(14.0, 28.0, k)
		var g := Color(col, 0.1 + k * 0.08)
		_quad(a - nn * band, b - nn * band, b + nn * band, a + nn * band, g, g, g, g)
		var passes := 2 + int(k * 1.99)
		for pss in passes:
			var off := (_h(i, j, 80 + pss) - 0.5) * band * 0.35
			var along := (b - a).normalized() * (_h(j, i, 90 + pss) - 0.5) * 6.0
			_ink_line(a + nn * off + along, b + nn * off - along, Color(col, 0.42 + k * 0.18), band * lerpf(0.85, 0.55, float(pss) / passes), false)
		_ink_line(a, b, Color(col.lightened(0.4), 0.9), 2.2 + k * 2.0, false)
		_ink_line(a + nn * 1.5, b + nn * 1.5, Color(col.lightened(0.4), 0.4), 1.4 + k, false)
	else:
		var gw := 4.0 + traffic * 9.0
		var g := Color(col, 0.07 + traffic * 0.12)
		_quad(a - nn * gw, b - nn * gw, b + nn * gw, a + nn * gw, g, g, g, g)
		_ink_line(a, b, Color(col, 0.45 + traffic * 0.45), 0.8 + traffic * 3.2, false)
	_trails.append({"a": a, "b": b, "color": col, "phase": _h(i, j, 3), "width": 1.5 + traffic * 2.5})
	if traffic > 0.6:
		_trails.append({"a": a, "b": b, "color": _inks[0], "phase": _h(i, j, 4), "width": 1.5 + traffic * 2.0})


func _plaza(i: int, j: int) -> void:
	var p := _rect_pts(i, j, i + 1, j + 1)
	var col := GROUND.lerp(_terr_col, 0.06)
	_quad(p[0], p[1], p[2], p[3], col, col, col, col)


## Merged cells inside a block: lots pair up in 2x2 quadrants (when the quadrant fits
## inside the block) as one 2x2, two slabs, or singles. Returns the cell of lot (i, j).
func _cell_of(i: int, j: int) -> Rect2i:
	var li: int = _local_i.get(i, 0)
	var lj: int = _local_j.get(j, 0)
	var qi := i - li % 2
	var qj := j - lj % 2
	var wide := not _street_i.has(qi + 1) and not _street_i.has(qi)
	var deep := not _street_j.has(qj + 1) and not _street_j.has(qj)
	var mode := int(_h(qi, qj, 30) * 6.0)
	if mode == 0 and wide and deep:
		return Rect2i(qi, qj, 2, 2)
	if mode == 1 and wide:
		return Rect2i(qi, j, 2, 1)
	if mode == 2 and deep:
		return Rect2i(i, qj, 1, 2)
	return Rect2i(i, j, 1, 1)


func _lot(i: int, j: int) -> void:
	var p := _rect_pts(i, j, i + 1, j + 1)
	_quad(p[0], p[1], p[2], p[3], GROUND, GROUND, GROUND, GROUND)
	var cell := _cell_of(i, j)
	# A merged building is drawn once, from its front lot (correct depth order).
	if i != cell.end.x - 1 or j != cell.end.y - 1:
		return
	_building(cell)


func _pick_shape(ci: int, cj: int) -> int:
	var mix: Array = _profile["mix"]
	if cultures.has(_terr):
		mix = CULTURES.get(cultures[_terr], mix)
	var total := 0
	for w in mix:
		total += int(w)
	var roll := _h(ci, cj, 40 + int(_profile.get("seed", 0))) * total
	for k in mix.size():
		roll -= int(mix[k])
		if roll < 0.0:
			return k
	return Shape.BOX


func _building(cell: Rect2i) -> void:
	var ci := cell.position.x
	var cj := cell.position.y
	var big := cell.size.x * cell.size.y
	var district_h := _h(floori(ci / float(STREET_EVERY)), floori(cj / float(STREET_EVERY)), 9)
	var r := _h(ci, cj, 2)
	var hs: float = _profile["height"]
	var h := (8.0 + pow(r, 2.7) * 100.0 + district_h * 28.0) * hs * (1.0 + 0.12 * (big - 1))
	if r > 0.965:
		h += 90.0 * hs
	# Low-rise around each HQ: its busy streets and the landmark read clearly.
	h *= lerpf(0.3, 1.0, clampf((_hq_distance(ci, cj) - 3.0) / 6.0, 0.0, 1.0))
	var fill := FILLS[int(_h(ci, cj, 5) * FILLS.size()) % FILLS.size()]
	var ink := _ink(ci, cj)
	var lit := 0.12 + district_h * 0.22
	var inset := 0.1 + _h(ci, cj, 1) * 0.14
	var x0 := ci + inset
	var y0 := cj + inset
	var x1 := cell.end.x - inset
	var y1 := cell.end.y - inset
	# Off the grid: nudge the footprint and turn some buildings a little.
	var jx := (_h(ci, cj, 15) - 0.5) * inset * 1.4
	var jy := (_h(ci, cj, 16) - 0.5) * inset * 1.4
	x0 += jx
	x1 += jx
	y0 += jy
	y1 += jy
	var cx := (x0 + x1) * 0.5
	var cy := (y0 + y1) * 0.5
	var half := minf(x1 - x0, y1 - y0) * 0.5
	var turn := (_h(ci, cj, 17) - 0.5) * 0.7 if _h(ci, cj, 18) < 0.45 else 0.0
	var shape := _pick_shape(ci, cj)
	var key := ci * 97 + cj
	var roof: PackedVector2Array
	match shape:
		Shape.STEPPED:
			var h1 := h * 0.5
			_extrude(_turned(turn, x0, y0, x1, y1), 0.0, h1, 1.0, fill, ink, lit, key)
			var k := 0.14 + _h(ci, cj, 6) * 0.08
			roof = _extrude(_turned(turn, x0 + k, y0 + k, x1 - k, y1 - k), h1, h * 0.35, 1.0, fill, ink, lit, key + 1)
			if big > 1 or h > 60.0:
				roof = _extrude(_turned(turn, x0 + k * 2.0, y0 + k * 2.0, x1 - k * 2.0, y1 - k * 2.0), h1 + h * 0.35, h * 0.3 + 10.0, 1.0, fill, ink, lit, key + 2)
		Shape.CYLINDER:
			roof = _extrude(_ngon(cx, cy, half, 8, PI / 8.0), 0.0, h + 10.0, 1.0, fill, ink, lit, key)
			if _h(ci, cj, 7) < 0.5:
				_extrude(_ngon(cx, cy, half * 0.6, 8, PI / 8.0), h + 10.0, 8.0, 0.55, fill, ink, 0.0, key + 1)
		Shape.HEX:
			roof = _extrude(_ngon(cx, cy, half, 6, _h(ci, cj, 8) * PI + turn), 0.0, h, 1.0, fill, ink, lit, key)
		Shape.TAPER:
			roof = _extrude(_turned(turn, x0, y0, x1, y1), 0.0, h * 1.1 + 20.0, 0.5, fill, ink, lit, key)
		Shape.NEEDLE:
			var nh := h * 1.3 + 40.0
			roof = _extrude(_ngon(cx, cy, half * 0.55, 6, 0.3), 0.0, nh, 1.0, fill, ink, lit, key)
			var tip := _iso(cx, cy) + Vector2(0, -nh)
			_ink_line(tip, tip + Vector2(0, -26), ink, 1.0, false)
			_beacons.append({"pos": tip + Vector2(0, -27), "color": ink, "phase": _h(ci, cj, 8)})
		Shape.WAREHOUSE:
			var wh := 9.0 + r * 16.0
			roof = _extrude(_turned(turn, x0, y0, x1, y1), 0.0, wh, 1.0, fill, ink, lit * 0.5, key)
			for k in 3:
				var t := (k + 1) / 4.0
				_ink_line(_iso(lerpf(x0, x1, t), y0) + Vector2(0, -wh), _iso(lerpf(x0, x1, t), y1) + Vector2(0, -wh), Color(ink, 0.35), 1.0, false)
		Shape.PYRAMID:
			roof = _extrude(_rect_pts(x0, y0, x1, y1), 0.0, 30.0 + h * 0.6, 0.03, fill, ink, lit, key)
		Shape.OBELISK:
			var oh := h * 1.1 + 40.0
			var k := (x1 - x0) * 0.36
			_extrude(_rect_pts(cx - k, cy - k, cx + k, cy + k), 0.0, oh, 0.7, fill, ink, lit, key)
			roof = _extrude(_rect_pts(cx - k * 0.7, cy - k * 0.7, cx + k * 0.7, cy + k * 0.7), oh, 12.0, 0.03, fill, ink, 0.0, key + 1)
		Shape.MASTABA:
			roof = _extrude(_rect_pts(x0, y0, x1, y1), 0.0, 12.0 + r * 14.0, 0.82, fill, ink, lit * 0.5, key)
		Shape.PAGODA:
			var tiers := 3 + int(_h(ci, cj, 50) * 2.0)
			var z := 0.0
			var th := maxf(14.0, h / tiers)
			for t in tiers:
				var k := (x1 - x0) * (0.1 + t * 0.07)
				_extrude(_rect_pts(x0 + k, y0 + k, x1 - k, y1 - k), z, th * 0.7, 1.0, fill, ink, lit, key + t * 3)
				z += th * 0.7
				var e := (x1 - x0) * (0.02 + t * 0.07)
				roof = _extrude(_rect_pts(x0 + e - 0.08, y0 + e - 0.08, x1 - e + 0.08, y1 - e + 0.08), z, th * 0.3, 0.55, fill.lerp(FACE_LIGHT, 0.2), ink, 0.0, key + t * 3 + 1)
				z += th * 0.3
		Shape.GABLE:
			var wall := 14.0 + h * 0.45
			_extrude(_rect_pts(x0, y0, x1, y1), 0.0, wall, 1.0, fill, ink, lit, key)
			roof = _gable(x0, y0, x1, y1, wall, 10.0 + (y1 - y0) * 12.0, fill, ink)
		Shape.CLOCKTOWER:
			var ch := h * 1.2 + 60.0
			var k := (x1 - x0) * 0.25
			_extrude(_rect_pts(x0 + k, y0 + k, x1 - k, y1 - k), 0.0, ch, 1.0, fill, ink, lit, key)
			roof = _extrude(_rect_pts(x0 + k, y0 + k, x1 - k, y1 - k), ch, 24.0, 0.03, fill, ink, 0.0, key + 1)
			var face := _iso(x1 - k, (y0 + y1) * 0.5) + Vector2(-TILE_A * 0.25, -ch + 16)
			var fc := Color(_inks[0], 0.9)
			for q in 12:
				var a0 := TAU * q / 12.0
				var a1 := TAU * (q + 1) / 12.0
				_ink_line(face + Vector2(cos(a0) * 7, sin(a0) * 8), face + Vector2(cos(a1) * 7, sin(a1) * 8), fc, 1.2, false)
			_ink_line(face, face + Vector2(0, -6), fc, 1.2, false)
			_ink_line(face, face + Vector2(4, 1), fc, 1.2, false)
		Shape.DOME:
			var dh := 12.0 + h * 0.5
			roof = _extrude(_ngon(cx, cy, half, 10, 0.1), 0.0, dh, 1.0, fill, ink, lit, key)
			_dome(_iso(cx, cy) + Vector2(0, -dh), half * TILE_A, fill, ink)
		Shape.MINARET:
			var mh := h * 1.3 + 70.0
			var k := half * 0.4
			_extrude(_ngon(cx, cy, k, 8, 0.2), 0.0, mh, 1.0, fill, ink, lit, key)
			_extrude(_ngon(cx, cy, k * 1.6, 8, 0.2), mh * 0.72, 4.0, 1.0, fill, ink, 0.0, key + 1)
			roof = _extrude(_ngon(cx, cy, k, 8, 0.2), mh, 16.0, 0.05, fill, ink, 0.0, key + 2)
			_beacons.append({"pos": _iso(cx, cy) + Vector2(0, -mh - 18), "color": ink, "phase": _h(ci, cj, 8)})
		Shape.STEP_TEMPLE:
			var steps := 4
			var sh := maxf(10.0, (h * 0.8 + 30.0) / (steps + 1))
			for t in steps:
				var k := (x1 - x0) * t * 0.09
				roof = _extrude(_rect_pts(x0 + k, y0 + k, x1 - k, y1 - k), t * sh, sh, 1.0, fill, ink, 0.0, key + t)
			var k2 := (x1 - x0) * 0.33
			roof = _extrude(_rect_pts(x0 + k2, y0 + k2, x1 - k2, y1 - k2), steps * sh, sh * 1.1, 1.0, fill.lerp(FACE_LIGHT, 0.2), ink, lit, key + 9)
			# Stair up the front face.
			var st_a := _iso((x0 + x1) * 0.5, y1)
			_ink_line(st_a + Vector2(-5, 0), st_a + Vector2(-5, -steps * sh) + Vector2(0, (x1 - x0) * TILE_B * 0.3), Color(ink, 0.7), 1.0, false)
			_ink_line(st_a + Vector2(5, 0), st_a + Vector2(5, -steps * sh) + Vector2(0, (x1 - x0) * TILE_B * 0.3), Color(ink, 0.7), 1.0, false)
		_:
			roof = _extrude(_turned(turn, x0, y0, x1, y1), 0.0, h, 1.0, fill, ink, lit, key)
	# Roof clutter: antennae, a lit sign, a beacon on the tall ones.
	var rc := Vector2.ZERO
	for q in roof:
		rc += q
	rc /= maxf(1.0, roof.size())
	var rec := {"roof": roof, "base": _iso(cx, cy), "shape": shape, "height": h, "cell": cell}
	for li in range(cell.position.x, cell.end.x):
		for lj in range(cell.position.y, cell.end.y):
			_roofs[Vector2i(li, lj)] = rec
	var clutter := _h(ci, cj, 14)
	if clutter < 0.18 and h > 30.0:
		_ink_line(rc, rc + Vector2(0, -12.0 - clutter * 60.0), Color(ink, 0.8), 1.0, false)
	elif clutter > 0.86 and roof.size() >= 4:
		var sc := Color(_ink(ci + 5, cj), 0.85)
		_quad(rc + Vector2(-6, -2), rc + Vector2(6, -2), rc + Vector2(6, -9), rc + Vector2(-6, -9), sc, sc, sc, sc)
	if r > 0.92:
		_beacons.append({"pos": rc + Vector2(0, -3), "color": ink, "phase": _h(ci, cj, 8)})


## A gabled roof on a wall of height `z`: ridge along i, slopes and gable ends; returns
## the ridge-and-eaves outline as the roof points.
func _gable(x0: float, y0: float, x1: float, y1: float, z: float, rh: float, fill: Color, ink: Color) -> PackedVector2Array:
	var up := Vector2(0, -z)
	var cy := (y0 + y1) * 0.5
	var b0 := _iso(x0, y0) + up
	var b1 := _iso(x1, y0) + up
	var f0 := _iso(x0, y1) + up
	var f1 := _iso(x1, y1) + up
	var ra := _iso(x0, cy) + up + Vector2(0, -rh)
	var rb := _iso(x1, cy) + up + Vector2(0, -rh)
	var back := fill.lerp(FACE_LIGHT, 0.1)
	var front := fill.lerp(FACE_LIGHT, 0.3)
	_quad(b0, b1, rb, ra, back, back, back, back)
	_tri(b0, f0, ra, back, back, back)
	_quad(f0, f1, rb, ra, front, front, front, front)
	_tri(b1, f1, rb, fill.darkened(0.2), fill.darkened(0.2), fill.darkened(0.2))
	_ink_line(ra, rb, ink)
	_ink_line(f0, f1, ink)
	_ink_line(f0, ra, ink)
	_ink_line(f1, rb, ink)
	_ink_line(b1, rb, Color(ink, 0.7), 1.1, false)
	return PackedVector2Array([ra, rb, f1, f0])


## A dome over a drum top centred at `c`, screen radius `rad`.
func _dome(c: Vector2, rad: float, fill: Color, ink: Color) -> void:
	var pts := PackedVector2Array()
	for k in 13:
		var a := PI + PI * k / 12.0
		pts.append(c + Vector2(cos(a) * rad, sin(a) * rad * 1.1))
	var body := pts.duplicate()
	body.append(c + Vector2(rad, 0))
	_poly(body, fill.lerp(FACE_LIGHT, 0.3))
	for k in 12:
		_ink_line(pts[k], pts[k + 1], ink, 1.3, k % 3 == 0)
	_ink_line(pts[6], pts[6] + Vector2(0, -10), ink, 1.1, false)
	_ink_line(c + Vector2(0, -rad * 1.1), c + Vector2(0, -rad * 0.2), Color(ink, 0.4), 1.0, false)


# --- Corporation HQs ----------------------------------------------------------------------

## The district's landmark, one per corporation, standing on its plaza.
func _hq(corp: StringName, rect: Rect2i) -> void:
	var cx := rect.position.x + 2.5
	var cy := rect.position.y + 2.5
	var col := _pale(Palette.corp_color(corp))
	var dark := FILLS[0]
	var mid := FILLS[1]
	var base := _iso(cx, cy)
	var ring := _ngon(cx, cy, 2.3, 24)
	for k in ring.size():
		_ink_line(ring[k], ring[(k + 1) % ring.size()], Color(col, 0.5), 1.0, false)
	match corp:
		&"solace":
			# Helix Spire: a round tower wrapped in floating care-rings under a halo cap.
			_extrude(_ngon(cx, cy, 1.1, 12), 0.0, 250.0, 1.0, mid, col, 0.3, 900)
			_extrude(_ngon(cx, cy, 0.7, 12), 250.0, 40.0, 0.35, dark, col, 0.0, 901)
			for k in 5:
				var hh := 40.0 + k * 46.0
				var rr := _ngon(cx, cy, 1.55 + 0.15 * sin(k * 1.7), 24, k * 0.4)
				for m in rr.size():
					if rr[m].y > base.y - 2.0 or m % 2 == 0:
						_ink_line(rr[m] + Vector2(0, -hh), rr[(m + 1) % rr.size()] + Vector2(0, -hh), col, 1.4)
			_beacons.append({"pos": base + Vector2(0, -292), "color": col, "phase": 0.2})
			_sign(base + Vector2(-40, -330), "SOLACE", col)
		&"meridian":
			# Freight Ziggurat: stacked terraces, container stacks and a crane arm.
			_extrude(_rect_pts(cx - 2.0, cy - 2.0, cx + 2.0, cy + 2.0), 0.0, 44.0, 1.0, mid, col, 0.25, 910)
			_extrude(_rect_pts(cx - 1.4, cy - 1.4, cx + 1.4, cy + 1.4), 44.0, 44.0, 1.0, dark, col, 0.25, 911)
			for k in 4:
				var bx := cx - 1.35 + k * 0.4
				var cc: Color = [_inks[0], _inks[3], _inks[2], col][k]
				_extrude(_rect_pts(bx, cy + 1.45, bx + 0.34, cy + 1.95), 44.0, 10.0 + (k % 2) * 10.0, 1.0, dark, cc, 0.0, 913 + k)
			_extrude(_rect_pts(cx - 0.7, cy - 0.7, cx + 0.7, cy + 0.7), 88.0, 110.0, 1.0, mid, col, 0.35, 912)
			var mast := _iso(cx + 0.7, cy - 0.7) + Vector2(0, -198)
			_ink_line(mast, mast + Vector2(0, -40), col, 1.6)
			var jib := mast + Vector2(-150, -30)
			_ink_line(mast + Vector2(0, -40), jib, col, 1.6)
			_ink_line(mast + Vector2(0, -40), mast + Vector2(40, -20), col, 1.2)
			_ink_line(jib, jib + Vector2(0, 50), Color(col, 0.8), 1.0, false)
			var box := jib + Vector2(0, 50)
			_quad(box + Vector2(-12, 0), box + Vector2(12, 0), box + Vector2(12, 14), box + Vector2(-12, 14), dark, dark, dark, dark)
			for e in [[Vector2(-12, 0), Vector2(12, 0)], [Vector2(12, 0), Vector2(12, 14)], [Vector2(12, 14), Vector2(-12, 14)], [Vector2(-12, 14), Vector2(-12, 0)]]:
				_ink_line(box + e[0], box + e[1], _inks[0], 1.2, false)
			_beacons.append({"pos": mast + Vector2(0, -42), "color": col, "phase": 0.5})
			_sign(base + Vector2(-50, -262), "MERIDIAN", col)
		&"halcyon":
			# Civic Pyramid: a stepped civic pyramid under a floating ring of light.
			for k in 4:
				var r := 2.0 - k * 0.45
				_extrude(_rect_pts(cx - r, cy - r, cx + r, cy + r), k * 38.0, 38.0, 1.0 if k < 3 else 0.2, mid if k % 2 == 0 else dark, col, 0.2, 920 + k)
			var apex := base + Vector2(0, -190)
			var halo := PackedVector2Array()
			for k in 25:
				halo.append(apex + Vector2(cos(TAU * k / 24.0) * 46.0, sin(TAU * k / 24.0) * 14.0 - 20.0))
			for k in 24:
				_ink_line(halo[k], halo[k + 1], col, 1.5)
			_ink_line(apex, apex + Vector2(0, -44), Color(col, 0.8), 1.2, false)
			_beacons.append({"pos": apex + Vector2(0, -46), "color": col, "phase": 0.7})
			_sign(base + Vector2(-46, -268), "HALCYON", col)
		&"orbital":
			# Orbital Tether: a hex needle on a ring platform, its tether beam into the sky.
			_extrude(_ngon(cx, cy, 2.0, 8, PI / 8.0), 0.0, 22.0, 1.0, mid, col, 0.2, 930)
			_extrude(_ngon(cx, cy, 0.6, 6), 22.0, 300.0, 0.7, dark, col, 0.35, 931)
			var tip := base + Vector2(0, -322)
			var beam := Color(col, 0.12)
			_quad(tip + Vector2(-9, 0), tip + Vector2(9, 0), Vector2(tip.x + 5, 0), Vector2(tip.x - 5, 0), beam, beam, Color(col, 0.03), Color(col, 0.03))
			_ink_line(tip, Vector2(tip.x, 0), Color(col, 0.7), 1.2, false)
			for k in 3:
				var y := tip.y * (0.25 + k * 0.25)
				_ink_line(Vector2(tip.x - 16, y), Vector2(tip.x + 16, y), Color(col, 0.6), 1.0, false)
			_beacons.append({"pos": tip, "color": col, "phase": 0.1})
			_sign(base + Vector2(30, -160), "ORBITAL", col)
		&"rebel_cell":
			# The Hive: a honeycomb cluster of hex towers, the tallest crowned with the Cell.
			var offs := [Vector2(-1.1, 0.0), Vector2(0.0, -1.1), Vector2(1.1, 0.0), Vector2(0.0, 1.1), Vector2(0.0, 0.0)]
			var hs := [90.0, 130.0, 70.0, 50.0, 220.0]
			for idx in [1, 0, 2, 4, 3]:
				var o: Vector2 = offs[idx]
				_extrude(_ngon(cx + o.x, cy + o.y, 0.62, 6, PI / 6.0), 0.0, hs[idx], 1.0, mid if idx % 2 == 0 else dark, col if idx != 4 else _inks[2], 0.3, 940 + idx)
			var crown := base + Vector2(0, -238)
			var hexa := PackedVector2Array()
			for k in 6:
				hexa.append(crown + Vector2(cos(TAU * k / 6.0), sin(TAU * k / 6.0)) * 16.0)
			_poly(hexa, Color(Palette.CELL_ACID, 0.9))
			for k in 6:
				_ink_line(hexa[k], hexa[(k + 1) % 6], _inks[2], 1.4)
			_sign(base + Vector2(-58, -280), "REBEL_CELL", _inks[2])


## A neon name plate floating over an HQ (drawn by the overlay).
func _sign(at: Vector2, text: String, col: Color) -> void:
	_signs.append({"pos": at, "text": text, "color": col})


func _draw_fx() -> void:
	if _built_for != size:
		return
	if territory_labels:
		var inv := 1.0 / maxf(0.01, scale.x)
		for t in TERRITORIES:
			var name := "THE SPRAWL" if t["id"] == &"" else String(t["id"]).to_upper()
			var at: Vector2 = t["at"]
			var p := _iso(at.x + 2.5, at.y + 2.5) + Vector2(-120, -40) * inv
			var col := Palette.PAPER if t["id"] == &"" else Palette.corp_color(t["id"])
			_fx.draw_rect(Rect2(p - Vector2(8, 30) * inv, Vector2(260, 40) * inv), Color(0, 0, 0, 0.75))
			_fx.draw_string(Palette.display(), p, name, HORIZONTAL_ALIGNMENT_LEFT, -1, int(30 * inv), col)
	for sg in _signs:
		var p: Vector2 = sg["pos"]
		var col: Color = sg["color"]
		var w := Palette.mono().get_string_size(sg["text"], HORIZONTAL_ALIGNMENT_LEFT, -1, 14).x + 14
		_fx.draw_rect(Rect2(p, Vector2(w, 22)), Color(Palette.NIGHT_SKY, 0.85))
		_fx.draw_rect(Rect2(p, Vector2(w, 22)), Color(col, 0.2), false, 5.0)
		_fx.draw_rect(Rect2(p, Vector2(w, 22)), col, false, 1.2)
		_fx.draw_string(Palette.mono(), p + Vector2(7, 16), sg["text"], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, col.lightened(0.3))
	# Traffic: bright dashes sliding along the lanes.
	for t in _trails:
		var a: Vector2 = t["a"]
		var b: Vector2 = t["b"]
		var k := fmod(float(t["phase"]) + anim_t * 0.35, 1.0)
		var p := a.lerp(b, k)
		var col: Color = t["color"]
		_fx.draw_line(p, p + (b - a) * 0.35, Color(col, 0.6), float(t.get("width", 2.0)))
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
