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
	&"rebel_cell": {"mix": [4, 3, 2, 1, 1, 1, 2], "height": 1.0, "corp_ink": 0.58, "seed": 53},
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
## HQ plaza size (lots); the landmarks are drawn at HQ_SCALE of their base design.
const HQ_LOTS := 10
const HQ_SCALE := 2.0
## How far territory borders wander (lots), and how wide the mixed band along them is.
const BORDER_WARP := 11.0
const BORDER_BLEND := 7.0
## Ink palettes: 0 = full neon; 1-3 paler options (lerped toward a tint).
const INK_SETS: Array[Dictionary] = [
	{"name": "NEON", "tint": Color.WHITE, "amount": 0.0},
	{"name": "PASTEL NEON", "tint": Color.WHITE, "amount": 0.3},
	{"name": "FADED PRINT", "tint": Color("#C9BFD9"), "amount": 0.38},
	{"name": "COOL HAZE", "tint": Color("#D6F2FF"), "amount": 0.32},
]
## The Cell has no tower: its territory is ordinary city, and its roads etch a raised
## fist (traced from the reference icon; polygons in 0-1 image space, y down) that reads
## from above. FIST_SIZE is the fist's size on screen (px at zoom 1); the roads are
## FIST_ROAD_HALF px half-wide and lots within FIST_CLEAR px of a road stay empty. No
## ordinary street runs inside the fist: streets end on its outline and the blocks
## inside are built up like the rest of the city.
const FIST_TERRITORY := &"rebel_cell"
const FIST_SIZE := Vector2(1000, 1070)
const FIST_ROAD_HALF := 17.0
const FIST_CLEAR := 27.0
const FIST_POLYS := [
	[Vector2(0.545, 0.458), Vector2(0.425, 0.491), Vector2(0.487, 0.515)],
	[Vector2(0.909, 0.379), Vector2(0.724, 0.579), Vector2(0.779, 0.636), Vector2(0.994, 0.461)],
	[Vector2(0.88, 0.33), Vector2(0.76, 0.245), Vector2(0.558, 0.509), Vector2(0.682, 0.552)],
	[Vector2(0.227, 0.2), Vector2(0, 0.515), Vector2(0.347, 0.888), Vector2(0.328, 0.997), Vector2(0.776, 0.997), Vector2(0.773, 0.915), Vector2(0.89, 0.779), Vector2(0.919, 0.585), Vector2(0.782, 0.691), Vector2(0.672, 0.597), Vector2(0.464, 0.552), Vector2(0.662, 0.845), Vector2(0.701, 0.873), Vector2(0.636, 0.879), Vector2(0.614, 0.948), Vector2(0.584, 0.879), Vector2(0.519, 0.885), Vector2(0.594, 0.821), Vector2(0.399, 0.539), Vector2(0.247, 0.488), Vector2(0.299, 0.445), Vector2(0.289, 0.367), Vector2(0.315, 0.367), Vector2(0.367, 0.433), Vector2(0.471, 0.43), Vector2(0.542, 0.397), Vector2(0.549, 0.327)],
	[Vector2(0.584, 0.112), Vector2(0.49, 0.258), Vector2(0.604, 0.312), Vector2(0.601, 0.367), Vector2(0.727, 0.185)],
	[Vector2(0.396, 0), Vector2(0.289, 0.167), Vector2(0.438, 0.23), Vector2(0.536, 0.082)],
]
## The fist's whole silhouette (its pieces with the gaps between them closed): no
## ordinary street runs inside it.
const FIST_HULL := [Vector2(0.396, 0.000), Vector2(0.282, 0.188), Vector2(0.263, 0.203), Vector2(0.227, 0.200), Vector2(0.000, 0.515), Vector2(0.338, 0.879), Vector2(0.344, 0.918), Vector2(0.328, 0.997), Vector2(0.776, 0.997), Vector2(0.773, 0.921), Vector2(0.890, 0.779), Vector2(0.919, 0.600), Vector2(0.903, 0.545), Vector2(0.994, 0.458), Vector2(0.886, 0.364), Vector2(0.880, 0.330), Vector2(0.727, 0.227), Vector2(0.724, 0.182), Vector2(0.584, 0.112), Vector2(0.555, 0.109), Vector2(0.532, 0.079)]
## Wall textures (design review options): 0 none, 1 panel seams, 2 pen hatching (dark
## ink), 3 grime stipple, 4 concrete grain, 5 matte stone, 6 brushed metal, 7 hatching on
## stone, 8 hatching on metal. 4-8 use the sketch shader's `wall_mode` (1 grain, 2 stone,
## 3 metal) on the dark grey fills.
const TEXTURE_NAMES: Array[String] = ["NONE", "PANEL SEAMS", "PEN HATCHING", "GRIME STIPPLE", "CONCRETE GRAIN",
	"MATTE STONE", "BRUSHED METAL", "HATCHING + STONE", "HATCHING + METAL"]
const TEXTURE_SHADER_MODE: Array[int] = [0, 0, 0, 0, 1, 2, 3, 2, 3]
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
var territory_label_px: float = 30.0
## Wall texture (TEXTURE_NAMES index).
var face_texture: int = 0:
	set(v):
		face_texture = v
		(material as ShaderMaterial).set_shader_parameter("wall_mode", TEXTURE_SHADER_MODE[clampi(v, 0, TEXTURE_SHADER_MODE.size() - 1)])
		refresh()
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
var hq_anchor: Vector2 = Vector2(0.8, 0.8)

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
var _terr_next: StringName = &""
var _border: float = 0.0
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
var _fist_segs: Array[PackedVector2Array] = []
var _fist_box: Rect2 = Rect2()
var _fist_hull := PackedVector2Array()
var _fist_cache: Dictionary = {}


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


## A street's ink: like `_ink` but at full neon strength (no palette paleness).
func _street_ink(a: int, b: int) -> Color:
	var share: float = float(_profile.get("corp_ink", 0.0))
	if _terr != &"" and _h(a, b, 12) < share:
		return Palette.corp_color(_terr)
	return INKS[int(_h(a, b, 11) * INKS.size()) % INKS.size()]


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
	return _territory_pair(i, j)[0]


## [owner, runner-up, border 0-1]: border is 1 on the dividing line, 0 deep inside.
func _territory_pair(i: int, j: int) -> Array:
	var w := Vector2(_vnoise(i * 0.07, j * 0.07, 70) - 0.5, _vnoise(i * 0.07, j * 0.07, 71) - 0.5) * BORDER_WARP * 2.0
	w += Vector2(_vnoise(i * 0.2, j * 0.2, 72) - 0.5, _vnoise(i * 0.2, j * 0.2, 73) - 0.5) * BORDER_WARP * 0.6
	var p := Vector2(i, j) + w
	var best: StringName = &""
	var best_d := INF
	var second: StringName = &""
	var second_d := INF
	for t in TERRITORIES:
		var d: float = p.distance_to(t["at"]) / float(t["pull"])
		if d < best_d:
			second = best
			second_d = best_d
			best_d = d
			best = t["id"]
		elif d < second_d:
			second_d = d
			second = t["id"]
	# Within ~BORDER_BLEND lots of the dividing line the two territories mix.
	var border := clampf(1.0 - (second_d - best_d) / BORDER_BLEND, 0.0, 1.0)
	return [best, second, border]


## Where a corporation's HQ stands (grid), or the city centre.
static func hq_of(corporation_id: StringName) -> Vector2:
	for t in TERRITORIES:
		if t["id"] == corporation_id:
			return t["at"]
	return Vector2.ZERO


func _set_lot_context(i: int, j: int) -> void:
	_apply_context(_territory_pair(i, j))


func _apply_context(pair: Array) -> void:
	_terr = pair[0]
	_terr_next = pair[1]
	_border = pair[2]
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
	return _is_street_lot(i, j)


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
	var focus := hq_of(district) + Vector2(HQ_LOTS * 0.5, HQ_LOTS * 0.5) if district != &"" else Vector2(0, 0)
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
			_hq_rects[t["id"]] = Rect2i(int(at.x), int(at.y), HQ_LOTS, HQ_LOTS)
	_hq_rect = _hq_rects.get(district, Rect2i())
	_build_streets()
	_build_fist()
	var s_min := int(floor((-40.0 - _oy) / TILE_B)) - 2
	var s_max := int((size.y + 420.0 - _oy) / TILE_B) + 2
	var d_min := int(floor((-80.0 - _ox) / TILE_A)) - 1
	var d_max := int((size.x + 80.0 - _ox) / TILE_A) + 1
	# Every lot in back-to-front order with its territory context.
	var lots: Array[Vector2i] = []
	var ctx: Array = []
	for s in range(s_min, s_max):
		for d in range(d_min, d_max + 1):
			if posmod(s + d, 2) != 0:
				continue
			var i := (s + d) / 2
			var j := (s - d) / 2
			lots.append(Vector2i(i, j))
			ctx.append(_territory_pair(i, j))
	# Pass 1, the ground (streets, plazas, lot floors); then the Cell's fist roads on top
	# of it; pass 2, everything standing, back to front, so towers overlap the roads.
	for n in lots.size():
		var l := lots[n]
		_apply_context(ctx[n])
		if _hq_at(l.x, l.y) != &"":
			_plaza(l.x, l.y)
		elif _is_street_lot(l.x, l.y):
			_street(l.x, l.y, _street_i.has(l.x), _street_j.has(l.y))
		else:
			var p := _rect_pts(l.x, l.y, l.x + 1, l.y + 1)
			_quad(p[0], p[1], p[2], p[3], GROUND, GROUND, GROUND, GROUND)
	_fist_roads()
	for n in lots.size():
		var l := lots[n]
		_apply_context(ctx[n])
		var in_hq := _hq_at(l.x, l.y)
		if in_hq != &"":
			var hr: Rect2i = _hq_rects[in_hq]
			if l.x == hr.end.x - 1 and l.y == hr.end.y - 1:
				_hq(in_hq, hr)
			continue
		if _is_street_lot(l.x, l.y):
			continue
		_lot(l.x, l.y)
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
	t = maxf(t, clampf(1.0 - d / 16.0, 0.0, 1.0))
	return t


## The corporation whose HQ plaza covers lot (i, j), or &"" (the Cell has none).
func _hq_at(i: int, j: int) -> StringName:
	for cid in _hq_rects:
		if cid != FIST_TERRITORY and (_hq_rects[cid] as Rect2i).has_point(Vector2i(i, j)):
			return cid
	return &""


## Screen segments of the fist roads (with the current camera) and their bounds.
func _build_fist() -> void:
	_fist_segs.clear()
	_fist_hull.clear()
	_fist_cache.clear()
	if not _hq_rects.has(FIST_TERRITORY):
		_fist_box = Rect2()
		return
	var hr: Rect2i = _hq_rects[FIST_TERRITORY]
	var c := _iso(hr.position.x + HQ_LOTS * 0.5, hr.position.y + HQ_LOTS * 0.5)
	for v: Vector2 in FIST_HULL:
		_fist_hull.append(c + (v - Vector2(0.5, 0.5)) * FIST_SIZE)
	for poly: Array in FIST_POLYS:
		for q in poly.size():
			var a: Vector2 = c + (poly[q] - Vector2(0.5, 0.5)) * FIST_SIZE
			var b: Vector2 = c + (poly[(q + 1) % poly.size()] - Vector2(0.5, 0.5)) * FIST_SIZE
			_fist_segs.append(PackedVector2Array([a, b]))
	_fist_box = Rect2(c - FIST_SIZE * 0.5, FIST_SIZE).grow(FIST_ROAD_HALF * 2.0)


## Screen distance (px) from lot (i, j)'s centre to the nearest fist road, or INF.
func _fist_dist(i: int, j: int) -> float:
	var key := Vector2i(i, j)
	if _fist_cache.has(key):
		return _fist_cache[key]
	var p := _iso(i + 0.5, j + 0.5)
	var best := INF
	if not _fist_segs.is_empty() and _fist_box.has_point(p):
		for sg in _fist_segs:
			best = minf(best, p.distance_to(Geometry2D.get_closest_point_to_segment(p, sg[0], sg[1])))
	_fist_cache[key] = best
	return best


## True when lot (i, j) lies inside the fist (its shapes or its roads).
func _in_fist(i: int, j: int) -> bool:
	if _fist_dist(i, j) < FIST_ROAD_HALF * 2.0:
		return true
	var p := _iso(i + 0.5, j + 0.5)
	if not _fist_box.has_point(p):
		return false
	return Geometry2D.is_point_in_polygon(p, _fist_hull)


## True for an ordinary street lot (streets stop at the fist's outline).
func _is_street_lot(i: int, j: int) -> bool:
	return (_street_i.has(i) or _street_j.has(j)) and not _in_fist(i, j)


## The fist roads: like the busiest streets (many skinny marker strokes side by side),
## wider still, in the Cell's full-strength colour.
func _fist_roads() -> void:
	var col := Palette.corp_color(FIST_TERRITORY)
	var strokes := 28
	for n in _fist_segs.size():
		var a: Vector2 = _fist_segs[n][0]
		var b: Vector2 = _fist_segs[n][1]
		if a.distance_to(b) < 1.0:
			continue
		var dir := (b - a).normalized()
		var nn := dir.orthogonal()
		# Dark roadbed first, overshooting so the corners join.
		var e0 := a - dir * FIST_ROAD_HALF
		var e1 := b + dir * FIST_ROAD_HALF
		var bed := STREET
		_quad(e0 - nn * (FIST_ROAD_HALF + 4.0), e1 - nn * (FIST_ROAD_HALF + 4.0), e1 + nn * (FIST_ROAD_HALF + 4.0), e0 + nn * (FIST_ROAD_HALF + 4.0), bed, bed, bed, bed)
		var g := Color(col, 0.14)
		_quad(e0 - nn * (FIST_ROAD_HALF + 6.0), e1 - nn * (FIST_ROAD_HALF + 6.0), e1 + nn * (FIST_ROAD_HALF + 6.0), e0 + nn * (FIST_ROAD_HALF + 6.0), g, g, g, g)
		for k in strokes:
			var t := (float(k) + 0.5) / strokes * 2.0 - 1.0
			var lane := t * FIST_ROAD_HALF + (_h(n, k, 87) - 0.5) * 1.6
			var over := FIST_ROAD_HALF * (0.4 + 0.6 * _h(k, n, 88))
			var alpha := 0.55 + 0.4 * _h(n + k, 5, 89)
			_ink_line(a + nn * lane - dir * over, b + nn * lane + dir * over, Color(col, alpha), 0.9 + _h(k, n, 86) * 0.6, false)


## Distance (lots) to the nearest corporation HQ centre (the Cell has no HQ).
func _hq_distance(i: int, j: int) -> float:
	var best := INF
	for cid in _hq_rects:
		if cid == FIST_TERRITORY:
			continue
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
	var steps := clampi(int(a.distance_to(b) / 5.0), 2, 400)
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
		if face_texture in [1, 2, 3, 7, 8] and h > 6.0:
			_texture_face(bot[k], bot[k2], top[k2], top[k], nrm.x > 0.0, key * 31 + k)
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


## Wall texture on the face a-b (bottom) / d-c (top), under the windows.
func _texture_face(a: Vector2, b: Vector2, c: Vector2, d: Vector2, shaded: bool, key: int) -> void:
	var wpx := a.distance_to(b)
	var hpx := a.distance_to(d)
	if wpx < 3.0 or hpx < 3.0:
		return
	var tone := Color("#8A97C8")
	match 2 if face_texture >= 7 else face_texture:
		1:
			# Panel seams: a floor line every two storeys, a joint every ~24 px.
			var rows := int(hpx / 16.0)
			for r in range(1, rows + 1):
				var v := (r * 16.0 - 1.5) / hpx
				_hair(a.lerp(d, v), b.lerp(c, v), Color(tone, 0.4 if r % 3 else 0.65), 1.0)
			var cols := int(wpx / 24.0)
			for q in range(1, cols + 1):
				var u := float(q) / (cols + 1)
				_hair(a.lerp(b, u), d.lerp(c, u), Color(tone, 0.32), 0.9)
		2:
			# Pen hatching at 45 degrees in dark ink: close on the shaded side, open on the
			# lit side.
			var gap := 3.5 if shaded else 5.0
			var rise := hpx / wpx
			var u0 := -rise
			while u0 < 1.0:
				var v_lo := maxf(0.0, -u0 / rise)
				var v_hi := minf(1.0, (1.0 - u0) / rise)
				if v_hi > v_lo:
					var p0 := a.lerp(b, u0 + rise * v_lo).lerp(d.lerp(c, u0 + rise * v_lo), v_lo)
					var p1 := a.lerp(b, u0 + rise * v_hi).lerp(d.lerp(c, u0 + rise * v_hi), v_hi)
					_hair(p0, p1, Color(0.01, 0.01, 0.02, 0.7 if shaded else 0.55), 1.1)
				u0 += gap / wpx
		3:
			# Grime: specks gathering toward the street, lighter and darker.
			var n := mini(420, int(wpx * hpx / 22.0))
			for q in n:
				var u := _h(key, q, 90)
				var v := pow(_h(key, q, 91), 2.2)
				var p := a.lerp(b, u).lerp(d.lerp(c, u), v)
				var sc := Color(tone, 0.55) if q % 3 else Color(0, 0, 0, 0.55)
				var s := 0.7 + _h(q, key, 92) * 1.1
				_quad(p + Vector2(-s, 0), p + Vector2(0, -s), p + Vector2(s, 0), p + Vector2(0, s), sc, sc, sc, sc)


## A plain straight hairline (one quad), for dense texture work.
func _hair(a: Vector2, b: Vector2, col: Color, width: float) -> void:
	var n := (b - a).orthogonal().normalized() * width * 0.5
	_quad(a - n, b - n, b + n, a + n, col, col, col, col)


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
	# Streets keep the original full-strength neon (only the buildings take the paler
	# palette), so the street grid reads over the city.
	var col := Palette.NET_CYAN if net_mode and _h(i, j, 62) < 0.5 else _street_ink(i if along_i else 0, j if along_j else 0)
	var a := _iso(i + 0.5, j) if along_i else _iso(i, j + 0.5)
	var b := _iso(i + 0.5, j + 1) if along_i else _iso(i + 1, j + 0.5)
	var nn := (b - a).orthogonal().normalized()
	var dir := (b - a).normalized()
	# Fine-tip marker: the street's width is built from many skinny strokes laid side by
	# side, each a little crooked and overlapping its neighbours. Busy streets get more
	# strokes (up to ~12) and so read wider; quiet ones 2-3.
	var strokes := 7 + int(traffic * 23.0)
	var half := 1.5 + strokes * 0.42
	var g := Color(col, 0.05 + traffic * 0.08)
	_quad(a - nn * (half + 3.0), b - nn * (half + 3.0), b + nn * (half + 3.0), a + nn * (half + 3.0), g, g, g, g)
	# Each stroke keeps its lane along the whole street (keyed by the street, not the
	# lot) so it reads as one long pen line; per-lot it only wanders a little.
	var street_key := i if along_i else j
	for k in strokes:
		var t := (float(k) + 0.5) / strokes * 2.0 - 1.0
		var lane := t * half + (_h(street_key, k, 81) - 0.5) * 1.8
		var w0 := (_h(i, j * 7 + k, 82) - 0.5) * 0.9
		var w1 := (_h(i, j * 7 + k + 1, 82) - 0.5) * 0.9
		var alpha := 0.45 + 0.4 * _h(street_key + k, 3, 85) + traffic * 0.15
		_ink_line(a + nn * (lane + w0) - dir * 2.0, b + nn * (lane + w1) + dir * 2.0, Color(col, alpha), 0.8 + _h(k, street_key, 86) * 0.6, false)


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
	# Merged buildings never straddle a fist road.
	if mode <= 2 and _fist_box.has_point(_iso(qi + 1.0, qj + 1.0)):
		for di in 2:
			for dj in 2:
				if _fist_dist(qi + di, qj + dj) < FIST_CLEAR:
					return Rect2i(i, j, 1, 1)
	if mode == 0 and wide and deep:
		return Rect2i(qi, qj, 2, 2)
	if mode == 1 and wide:
		return Rect2i(qi, j, 2, 1)
	if mode == 2 and deep:
		return Rect2i(i, qj, 1, 2)
	return Rect2i(i, j, 1, 1)


func _lot(i: int, j: int) -> void:
	if _fist_dist(i, j) < FIST_CLEAR:
		return  # a fist road runs here
	var cell := _cell_of(i, j)
	# A merged building is drawn once, from its front lot (correct depth order).
	if i != cell.end.x - 1 or j != cell.end.y - 1:
		return
	_building(cell)


func _pick_shape(ci: int, cj: int) -> int:
	var mix: Array = _profile["mix"]
	var owner := _terr
	# Border blend: near the dividing line some buildings take the neighbour's style.
	if _border > 0.0 and _h(ci, cj, 41) < _border * 0.5:
		owner = _terr_next
		mix = DISTRICTS.get(owner, DISTRICTS[&""])["mix"]
	if cultures.has(owner):
		mix = CULTURES.get(cultures[owner], mix)
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
	h *= lerpf(0.3, 1.0, clampf((_hq_distance(ci, cj) - 6.0) / 7.0, 0.0, 1.0))
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
	var k := HQ_SCALE
	var cx := rect.position.x + HQ_LOTS * 0.5
	var cy := rect.position.y + HQ_LOTS * 0.5
	var col := _pale(Palette.corp_color(corp))
	var dark := FILLS[0]
	var mid := FILLS[1]
	var grey := FILLS[2]
	var base := _iso(cx, cy)
	# Plaza: two rings, spokes and corner lamps.
	for rr in [2.3 * k, 2.0 * k]:
		var ring := _ngon(cx, cy, rr, 32)
		for m in ring.size():
			_ink_line(ring[m], ring[(m + 1) % ring.size()], Color(col, 0.45), 1.0, false)
	for m in 8:
		var a := TAU * m / 8.0
		_ink_line(_iso(cx + cos(a) * 2.0 * k, cy + sin(a) * 2.0 * k), _iso(cx + cos(a) * 2.3 * k, cy + sin(a) * 2.3 * k), Color(col, 0.6), 1.0, false)
		if m % 2 == 0:
			var lamp := _iso(cx + cos(a + 0.4) * 2.45 * k, cy + sin(a + 0.4) * 2.45 * k)
			_ink_line(lamp, lamp + Vector2(0, -18), Color(col, 0.8), 1.0, false)
			_beacons.append({"pos": lamp + Vector2(0, -20), "color": col, "phase": m * 0.13})
	match String(cultures.get(corp, "")):
		"chinese":
			_hq_pagoda(cx, cy, k, col, base)
			_sign(base + Vector2(-50, -330.0 * k), String(corp).to_upper(), col)
			return
		"egyptian":
			_hq_pyramid(cx, cy, k, col, base)
			_sign(base + Vector2(-46, -250.0 * k), String(corp).to_upper(), col)
			return
		"english":
			_hq_big_ben(cx, cy, k, col, base)
			_sign(base + Vector2(40.0 * k, -200.0 * k), String(corp).to_upper(), col)
			return
	match corp:
		&"solace":
			# The Double Helix: a podium with pods, and on it the tower as a DNA strand, two
			# helices wound round each other and joined by bridges (the base pairs).
			_extrude(_ngon(cx, cy, 1.9 * k, 8, PI / 8.0), 0.0, 30.0 * k, 1.0, grey, col, 0.35, 900)
			_hq_dna(cx, cy, k, col, 30.0 * k, 340.0 * k)
			_sign(base + Vector2(-40, -395.0 * k), "SOLACE", col)
		&"meridian":
			# Freight Ziggurat: terraces with loading bays, container yards, a tower with a
			# helipad and a big crane swinging a container.
			_extrude(_rect_pts(cx - 2.0 * k, cy - 2.0 * k, cx + 2.0 * k, cy + 2.0 * k), 0.0, 44.0 * k, 1.0, mid, col, 0.25, 910)
			for m in 5:
				var bay := _iso(cx - 2.0 * k + (m + 0.6) * 0.75 * k, cy + 2.0 * k)
				_quad(bay, bay + Vector2(20, -10), bay + Vector2(20, -38), bay + Vector2(0, -28), Color(_inks[0], 0.25), Color(_inks[0], 0.25), Color(_inks[0], 0.25), Color(_inks[0], 0.25))
				_ink_line(bay + Vector2(0, -28), bay + Vector2(20, -38), _inks[0], 1.2, false)
			_extrude(_rect_pts(cx - 1.4 * k, cy - 1.4 * k, cx + 1.4 * k, cy + 1.4 * k), 44.0 * k, 44.0 * k, 1.0, dark, col, 0.25, 911)
			for row in 2:
				for m in 6:
					var bx := cx - 1.3 * k + m * 0.43 * k
					var cc: Color = [_inks[0], _inks[3], _inks[2], col, _inks[1], _inks[4]][(m + row) % 6]
					_extrude(_rect_pts(bx, cy + 1.45 * k + row * 0.25 * k, bx + 0.36 * k, cy + 1.66 * k + row * 0.25 * k), 44.0 * k, (10.0 + ((m + row) % 3) * 8.0) * k, 1.0, dark, cc, 0.0, 913 + m + row * 6)
			_extrude(_rect_pts(cx - 0.7 * k, cy - 0.7 * k, cx + 0.7 * k, cy + 0.7 * k), 88.0 * k, 110.0 * k, 1.0, mid, col, 0.35, 912)
			var pad := _ngon(cx, cy, 0.5 * k, 24)
			for q in pad.size():
				_ink_line(pad[q] + Vector2(0, -198.0 * k), pad[(q + 1) % pad.size()] + Vector2(0, -198.0 * k), _inks[0], 1.2, false)
			var hc := base + Vector2(0, -198.0 * k)
			_ink_line(hc + Vector2(-8, -6), hc + Vector2(-8, 6), _inks[0], 1.6, false)
			_ink_line(hc + Vector2(8, -6), hc + Vector2(8, 6), _inks[0], 1.6, false)
			_ink_line(hc + Vector2(-8, 0), hc + Vector2(8, 0), _inks[0], 1.6, false)
			var mast := _iso(cx + 0.7 * k, cy - 0.7 * k) + Vector2(0, -198.0 * k)
			_ink_line(mast, mast + Vector2(0, -40.0 * k), col, 2.0)
			for q in 4:
				_ink_line(mast + Vector2(-4, -q * 10.0 * k), mast + Vector2(4, -(q + 1) * 10.0 * k), Color(col, 0.6), 1.0, false)
			var jib := mast + Vector2(-150.0 * k, -30.0 * k)
			_ink_line(mast + Vector2(0, -40.0 * k), jib, col, 2.0)
			_ink_line(mast + Vector2(0, -40.0 * k), mast + Vector2(40.0 * k, -20.0 * k), col, 1.6)
			for q in 6:
				var t := (q + 1) / 7.0
				_ink_line((mast + Vector2(0, -40.0 * k)).lerp(jib, t), (mast + Vector2(0, -34.0 * k)).lerp(jib + Vector2(0, 6), t + 0.07), Color(col, 0.5), 1.0, false)
			_ink_line(jib, jib + Vector2(0, 50.0 * k), Color(col, 0.8), 1.0, false)
			var box := jib + Vector2(0, 50.0 * k)
			var bw := 12.0 * k
			_quad(box + Vector2(-bw, 0), box + Vector2(bw, 0), box + Vector2(bw, 14.0 * k), box + Vector2(-bw, 14.0 * k), dark, dark, dark, dark)
			for e in [[Vector2(-bw, 0), Vector2(bw, 0)], [Vector2(bw, 0), Vector2(bw, 14.0 * k)], [Vector2(bw, 14.0 * k), Vector2(-bw, 14.0 * k)], [Vector2(-bw, 14.0 * k), Vector2(-bw, 0)]]:
				_ink_line(box + e[0], box + e[1], _inks[0], 1.4, false)
			for q in 4:
				_ink_line(box + Vector2(-bw + (q + 1) * bw * 0.4, 2), box + Vector2(-bw + (q + 1) * bw * 0.4, 14.0 * k - 2), Color(_inks[0], 0.5), 1.0, false)
			_beacons.append({"pos": mast + Vector2(0, -42.0 * k), "color": col, "phase": 0.5})
			_sign(base + Vector2(-50, -262.0 * k), "MERIDIAN", col)
		&"halcyon":
			# Civic Pyramid: four tiers with colonnades and a grand stair, flanking obelisks,
			# banners and a floating halo.
			for m in [Vector2(-2.1, 2.1), Vector2(2.1, -2.1)]:
				var ox: float = cx + m.x * k
				var oy: float = cy + m.y * k
				_extrude(_rect_pts(ox - 0.18 * k, oy - 0.18 * k, ox + 0.18 * k, oy + 0.18 * k), 0.0, 90.0 * k, 0.7, dark, col, 0.0, 925)
				_extrude(_rect_pts(ox - 0.13 * k, oy - 0.13 * k, ox + 0.13 * k, oy + 0.13 * k), 90.0 * k, 10.0 * k, 0.03, dark, col, 0.0, 926)
			for t in 4:
				var r := (2.0 - t * 0.45) * k
				_extrude(_rect_pts(cx - r, cy - r, cx + r, cy + r), t * 38.0 * k, 38.0 * k, 1.0 if t < 3 else 0.2, mid if t % 2 == 0 else dark, col, 0.2, 920 + t)
				# Colonnade on the front faces.
				if t < 3:
					for q in 7:
						var f := float(q + 1) / 8.0
						var p0 := _iso(cx - r + 2.0 * r * f, cy + r) + Vector2(0, -t * 38.0 * k)
						_ink_line(p0 + Vector2(0, -4), p0 + Vector2(0, -34.0 * k), Color(col, 0.35), 1.0, false)
			# The grand stair up the front.
			var st0 := _iso(cx, cy + 2.0 * k)
			for q in 12:
				var y := -q * 12.0 * k
				var w := (18.0 - q * 0.9) * k
				_ink_line(st0 + Vector2(-w * 0.5, y), st0 + Vector2(w * 0.5, y - w * 0.25), Color(col, 0.7), 1.0, false)
			var apex := base + Vector2(0, -190.0 * k)
			var halo := PackedVector2Array()
			for q in 33:
				halo.append(apex + Vector2(cos(TAU * q / 32.0) * 46.0 * k, sin(TAU * q / 32.0) * 14.0 * k - 20.0 * k))
			for q in 32:
				_ink_line(halo[q], halo[q + 1], col, 1.8)
			for sx in [-1.0, 1.0]:
				var pole := base + Vector2(sx * 120.0 * k, -80.0 * k)
				_ink_line(pole, pole + Vector2(0, -60.0 * k), Color(col, 0.8), 1.2, false)
				var ban := PackedVector2Array([pole + Vector2(0, -60.0 * k), pole + Vector2(sx * 22.0 * k, -56.0 * k), pole + Vector2(sx * 20.0 * k, -30.0 * k), pole + Vector2(0, -34.0 * k)])
				_poly(ban, Color(col, 0.45))
			_ink_line(apex, apex + Vector2(0, -44.0 * k), Color(col, 0.8), 1.2, false)
			_beacons.append({"pos": apex + Vector2(0, -46.0 * k), "color": col, "phase": 0.7})
			_sign(base + Vector2(-46, -268.0 * k), "HALCYON", col)
		&"orbital":
			# Orbital Tether: a ring platform with docking arms, a needle with collars every
			# storey band, a counterweight and its tether beam into the sky.
			_extrude(_ngon(cx, cy, 2.0 * k, 12, PI / 12.0), 0.0, 22.0 * k, 1.0, mid, col, 0.2, 930)
			for m in 6:
				var a := TAU * m / 6.0
				var p0 := _iso(cx + cos(a) * 2.0 * k, cy + sin(a) * 2.0 * k) + Vector2(0, -22.0 * k)
				var p1 := _iso(cx + cos(a) * 2.6 * k, cy + sin(a) * 2.6 * k) + Vector2(0, -30.0 * k)
				_ink_line(p0, p1, col, 1.4)
				_beacons.append({"pos": p1, "color": col, "phase": m * 0.2})
			_extrude(_ngon(cx, cy, 0.6 * k, 6), 22.0 * k, 300.0 * k, 0.7, dark, col, 0.35, 931)
			for q in 5:
				var hh := (60.0 + q * 52.0) * k
				var rr := _ngon(cx, cy, (0.75 - q * 0.05) * k, 6)
				for m in rr.size():
					_ink_line(rr[m] + Vector2(0, -hh), rr[(m + 1) % rr.size()] + Vector2(0, -hh), col, 1.4)
			var tip := base + Vector2(0, -322.0 * k)
			_extrude(_ngon(cx, cy, 0.35 * k, 8), 322.0 * k, 14.0 * k, 1.0, grey, col, 0.0, 932)
			var beam := Color(col, 0.12)
			_quad(tip + Vector2(-9.0 * k, 0), tip + Vector2(9.0 * k, 0), Vector2(tip.x + 5.0 * k, -2000), Vector2(tip.x - 5.0 * k, -2000), beam, beam, Color(col, 0.0), Color(col, 0.0))
			_ink_line(tip, Vector2(tip.x, -2000), Color(col, 0.7), 1.4, false)
			_beacons.append({"pos": tip + Vector2(0, -16.0 * k), "color": col, "phase": 0.1})
			_sign(base + Vector2(30.0 * k, -160.0 * k), "ORBITAL", col)


## Chinese HQ: a seven-tier pagoda tower, every tier under a sweeping roof whose four
## corners turn up, a spire of rings on top.
func _hq_pagoda(cx: float, cy: float, k: float, col: Color, base: Vector2) -> void:
	_extrude(_rect_pts(cx - 1.9 * k, cy - 1.9 * k, cx + 1.9 * k, cy + 1.9 * k), 0.0, 14.0 * k, 1.0, FILLS[2], col, 0.2, 960)
	var z := 14.0 * k
	for t in 7:
		var r := (1.25 - t * 0.12) * k
		var body := (32.0 - t * 2.0) * k
		_extrude(_rect_pts(cx - r, cy - r, cx + r, cy + r), z, body, 1.0, FILLS[1] if t % 2 == 0 else FILLS[0], col, 0.35, 961 + t * 2)
		z += body
		z = _pagoda_roof(cx, cy, r * 1.45, r * 0.55, z, (12.0 - t * 0.8) * k, col)
	var tip := base + Vector2(0, -z)
	for q in 5:
		var rr := (7.0 - q) * k * 0.9
		_ink_line(tip + Vector2(-rr, -q * 7.0 * k), tip + Vector2(rr, -q * 7.0 * k), col, 1.4)
	_ink_line(tip, tip + Vector2(0, -48.0 * k), col, 1.8)
	_beacons.append({"pos": tip + Vector2(0, -50.0 * k), "color": col, "phase": 0.3})


## One pagoda roof from half-width `r0` (eaves) up to `r1` at the ridge; its four eave
## corners flick outward and up. Returns the height reached.
func _pagoda_roof(cx: float, cy: float, r0: float, r1: float, z: float, h: float, col: Color) -> float:
	_extrude(_rect_pts(cx - r0, cy - r0, cx + r0, cy + r0), z, h, r1 / r0, FILLS[0].lerp(col, 0.12), col, 0.0, 990)
	for q in [Vector2(-1, -1), Vector2(1, -1), Vector2(1, 1), Vector2(-1, 1)]:
		var c := _iso(cx + q.x * r0, cy + q.y * r0) + Vector2(0, -z)
		var out := (c - _iso(cx, cy) - Vector2(0, -z)).normalized()
		var tip := c + out * h * 0.9 + Vector2(0, -h * 0.9)
		var mid := c + out * h * 0.6 + Vector2(0, -h * 0.1)
		_ink_line(c, mid, col, 1.6, false)
		_ink_line(mid, tip, col, 1.6, false)
		_beacons.append({"pos": tip, "color": col, "phase": 0.05 * q.x + 0.1})
	return z + h


## Egyptian HQ: a large sloped (truncated pyramid) base, a ramp up its front flanked by
## obelisks, and a great pyramid standing on the base.
func _hq_pyramid(cx: float, cy: float, k: float, col: Color, base: Vector2) -> void:
	var half := 1.75 * k
	var bh := 52.0 * k
	var ts := 0.8
	_extrude(_rect_pts(cx - half, cy - half, cx + half, cy + half), 0.0, bh, ts, FILLS[1], col, 0.25, 970)
	# Coursed stone lines on the two visible slopes.
	for q in 5:
		var f := float(q + 1) / 6.0
		var hh := bh * f
		var rr := half * lerpf(1.0, ts, f)
		_ink_line(_iso(cx - rr, cy + rr) + Vector2(0, -hh), _iso(cx + rr, cy + rr) + Vector2(0, -hh), Color(col, 0.35), 1.0, false)
		_ink_line(_iso(cx + rr, cy - rr) + Vector2(0, -hh), _iso(cx + rr, cy + rr) + Vector2(0, -hh), Color(col, 0.25), 1.0, false)
	# The ramp: from the plaza in front up to the top edge of the base.
	var rw := 0.42 * k
	var g0 := _iso(cx - rw, cy + half + 0.9 * k)
	var g1 := _iso(cx + rw, cy + half + 0.9 * k)
	var t0 := _iso(cx - rw, cy + half * ts) + Vector2(0, -bh)
	var t1 := _iso(cx + rw, cy + half * ts) + Vector2(0, -bh)
	var ramp := FILLS[2].lerp(col, 0.15)
	_quad(g0, g1, t1, t0, ramp, ramp, ramp.lightened(0.1), ramp.lightened(0.1))
	_ink_line(g0, t0, col, 1.6)
	_ink_line(g1, t1, col, 1.6)
	for q in 9:
		var f := float(q + 1) / 10.0
		_ink_line(g0.lerp(t0, f), g1.lerp(t1, f), Color(col, 0.4), 1.0, false)
	for sx in [-1.0, 1.0]:
		var ox: float = cx + sx * (rw + 0.35 * k)
		var oy: float = cy + half + 0.75 * k
		_extrude(_rect_pts(ox - 0.14 * k, oy - 0.14 * k, ox + 0.14 * k, oy + 0.14 * k), 0.0, 80.0 * k, 0.65, FILLS[0], col, 0.0, 975)
		_extrude(_rect_pts(ox - 0.09 * k, oy - 0.09 * k, ox + 0.09 * k, oy + 0.09 * k), 80.0 * k, 9.0 * k, 0.03, FILLS[0], col, 0.0, 976)
		_beacons.append({"pos": _iso(ox, oy) + Vector2(0, -92.0 * k), "color": col, "phase": 0.4 + sx * 0.1})
	# The flat terrace on top of the base: a parapet rim and paving lines, so the pyramid
	# stands on level ground (slope, flat, slope).
	var tr := half * ts
	var rim := [_iso(cx - tr, cy - tr), _iso(cx + tr, cy - tr), _iso(cx + tr, cy + tr), _iso(cx - tr, cy + tr)]
	for q in 4:
		_ink_line(rim[q] + Vector2(0, -bh - 4.0 * k), rim[(q + 1) % 4] + Vector2(0, -bh - 4.0 * k), Color(col, 0.7), 1.2, false)
	var pr := tr * 0.66
	for q in 3:
		var f := lerpf(pr, tr, float(q + 1) / 4.0)
		_ink_line(_iso(cx - f, cy + f) + Vector2(0, -bh), _iso(cx + f, cy + f) + Vector2(0, -bh), Color(col, 0.3), 1.0, false)
		_ink_line(_iso(cx + f, cy - f) + Vector2(0, -bh), _iso(cx + f, cy + f) + Vector2(0, -bh), Color(col, 0.22), 1.0, false)
	# The great pyramid on the terrace, with a gilded cap.
	# Colonnades along the terrace's two front edges (either side of the ramp head).
	var gold := _pale(Palette.RESIST_GOLD)
	for side in 2:
		var cols_n := 9
		var prev_top := Vector2.INF
		for q in cols_n:
			var f := lerpf(-0.92, 0.92, float(q) / (cols_n - 1))
			if side == 0 and absf(f * tr) < rw * 1.3:
				prev_top = Vector2.INF
				continue
			var g := Vector2(cx + f * tr, cy + tr * 0.94) if side == 0 else Vector2(cx + tr * 0.94, cy + f * tr)
			var foot := _iso(g.x, g.y) + Vector2(0, -bh)
			var top := foot + Vector2(0, -16.0 * k)
			_ink_line(foot, top, Color(col, 0.85), 2.2, false)
			_hair(top + Vector2(-3, 0), top + Vector2(3, 0), gold, 1.4)
			if prev_top != Vector2.INF:
				_hair(prev_top + Vector2(0, -1.5), top + Vector2(0, -1.5), Color(gold, 0.8), 1.6)
			prev_top = top
	# Hieroglyph friezes: a band of little signs round the base's two visible slopes.
	_frieze(_iso(cx - half, cy + half), _iso(cx + half, cy + half), _iso(cx - tr, cy + tr) + Vector2(0, -bh), _iso(cx + tr, cy + tr) + Vector2(0, -bh), 0.42, 0.58, 26, 0.09, gold, 0)
	_frieze(_iso(cx + half, cy + half), _iso(cx + half, cy - half), _iso(cx + tr, cy + tr) + Vector2(0, -bh), _iso(cx + tr, cy - tr) + Vector2(0, -bh), 0.42, 0.58, 26, 0.0, gold, 1)
	# Braziers on the terrace corners.
	for cc in [Vector2(-1, 1), Vector2(1, 1), Vector2(1, -1)]:
		var bp := _iso(cx + cc.x * tr * 0.97, cy + cc.y * tr * 0.97) + Vector2(0, -bh)
		_ink_line(bp, bp + Vector2(0, -12.0 * k), Color(gold, 0.9), 1.6, false)
		_beacons.append({"pos": bp + Vector2(0, -14.0 * k), "color": Palette.CRT_AMBER, "phase": cc.x * 0.2 + cc.y * 0.1})
	# The great pyramid on the terrace: gentler slopes, stone courses, a gilded cap and
	# an entrance where the ramp arrives.
	var ph := 82.0 * k
	_extrude(_rect_pts(cx - pr, cy - pr, cx + pr, cy + pr), bh, ph, 0.12, FILLS[1].lerp(col, 0.06), col, 0.2, 977)
	for q in 7:
		var f := float(q + 1) / 8.0
		var hh := bh + ph * f
		var rr := pr * lerpf(1.0, 0.12, f)
		_hair(_iso(cx - rr, cy + rr) + Vector2(0, -hh), _iso(cx + rr, cy + rr) + Vector2(0, -hh), Color(col, 0.3), 1.0)
		_hair(_iso(cx + rr, cy - rr) + Vector2(0, -hh), _iso(cx + rr, cy + rr) + Vector2(0, -hh), Color(col, 0.22), 1.0)
	# The same gold frieze round the pyramid, above the doorway.
	var pt := pr * 0.12
	var ptop := bh + ph
	_frieze(_iso(cx - pr, cy + pr) + Vector2(0, -bh), _iso(cx + pr, cy + pr) + Vector2(0, -bh), _iso(cx - pt, cy + pt) + Vector2(0, -ptop), _iso(cx + pt, cy + pt) + Vector2(0, -ptop), 0.3, 0.42, 18, 0.0, gold, 2)
	_frieze(_iso(cx + pr, cy + pr) + Vector2(0, -bh), _iso(cx + pr, cy - pr) + Vector2(0, -bh), _iso(cx + pt, cy + pt) + Vector2(0, -ptop), _iso(cx + pt, cy - pt) + Vector2(0, -ptop), 0.3, 0.42, 18, 0.0, gold, 3)
	# Entrance: a dark doorway with a gold lintel on the front slope.
	var dw := 0.16 * k
	var d0 := _iso(cx - dw, cy + pr) + Vector2(0, -bh)
	var d1 := _iso(cx + dw, cy + pr) + Vector2(0, -bh)
	var dz := ph * 0.2
	var dr := pr * lerpf(1.0, 0.12, 0.2)
	var d2 := _iso(cx + dw * 0.7, cy + dr) + Vector2(0, -bh - dz)
	var d3 := _iso(cx - dw * 0.7, cy + dr) + Vector2(0, -bh - dz)
	_quad(d0, d1, d2, d3, FILLS[0], FILLS[0], FILLS[0], FILLS[0])
	_hair(d3 + Vector2(-4, 0), d2 + Vector2(4, 0), gold, 2.0)
	_hair(d0, d3, Color(col, 0.8), 1.2)
	_hair(d1, d2, Color(col, 0.8), 1.2)
	# The cap, and a gold seam up the pyramid's front edge.
	_hair(_iso(cx + pr, cy + pr) + Vector2(0, -bh), _iso(cx + pr * 0.12, cy + pr * 0.12) + Vector2(0, -bh - ph), Color(gold, 0.55), 1.4)
	_extrude(_rect_pts(cx - pr * 0.12, cy - pr * 0.12, cx + pr * 0.12, cy + pr * 0.12), bh + ph, 16.0 * k, 0.03, Palette.RESIST_GOLD.darkened(0.4), Palette.RESIST_GOLD, 0.0, 978)
	_beacons.append({"pos": base + Vector2(0, -(bh + ph + 20.0 * k)), "color": col, "phase": 0.7})


## Solace's tower: a DNA double helix from height z0 to z1. Two strands (thick tubes)
## wind round a vertical axis; every few steps a bridge joins them, each half in one of
## the paired base colours. Pieces are sorted back to front so the strands pass in front
## of and behind each other; the far side is drawn dimmer.
func _hq_dna(cx: float, cy: float, k: float, col: Color, z0: float, z1: float) -> void:
	var r := 1.5 * k
	var turns := 2.5
	var n := 110
	var tube := 14.0 * k
	var pairs := [[_inks[0], _inks[3]], [_inks[2], col]]
	var pieces: Array[Dictionary] = []
	var pts: Array = [[], []]
	for q in n + 1:
		var t := float(q) / n
		for sn in 2:
			var a := t * turns * TAU + sn * PI
			var g := Vector2(cx + cos(a) * r, cy + sin(a) * r)
			pts[sn].append({"g": g, "p": _iso(g.x, g.y) + Vector2(0, -lerpf(z0, z1, t))})
	for sn in 2:
		for q in n:
			var g0: Vector2 = pts[sn][q]["g"]
			var g1: Vector2 = pts[sn][q + 1]["g"]
			pieces.append({"d": (g0.x + g0.y + g1.x + g1.y) * 0.5, "kind": 0, "a": pts[sn][q]["p"], "b": pts[sn][q + 1]["p"], "q": q})
	for q in range(2, n - 1, 4):
		var pa: Vector2 = pts[0][q]["p"]
		var pb: Vector2 = pts[1][q]["p"]
		var mid := (pa + pb) * 0.5
		var ga: Vector2 = pts[0][q]["g"]
		var gb: Vector2 = pts[1][q]["g"]
		var pair: Array = pairs[(q / 4) % 2]
		var flip := (q / 8) % 2 == 1
		pieces.append({"d": (ga.x + ga.y + cx + cy) * 0.5, "kind": 1, "a": pa, "b": mid, "col": pair[1 if flip else 0]})
		pieces.append({"d": (gb.x + gb.y + cx + cy) * 0.5, "kind": 1, "a": mid, "b": pb, "col": pair[0 if flip else 1]})
	pieces.sort_custom(func(p1: Dictionary, p2: Dictionary) -> bool: return p1["d"] < p2["d"])
	var centre := cx + cy
	for pc in pieces:
		var a: Vector2 = pc["a"]
		var b: Vector2 = pc["b"]
		# 0 on the far side of the axis, 1 on the near side.
		var near := clampf((float(pc["d"]) - centre) / (2.0 * r) + 0.5, 0.0, 1.0)
		var dir := (b - a).normalized()
		var nn := dir.orthogonal()
		if pc["kind"] == 0:
			var e0 := a - dir * tube * 0.15
			var e1 := b + dir * tube * 0.15
			var body := FILLS[1].lerp(col, 0.12 + near * 0.12).darkened(0.3 * (1.0 - near))
			_quad(e0 - nn * tube * 0.5, e1 - nn * tube * 0.5, e1 + nn * tube * 0.5, e0 + nn * tube * 0.5, body, body, body, body)
			# Neon tube outline: a wide soft glow, then a bright core on each edge.
			var glow := Color(col, 0.1 + 0.14 * near)
			var edge := Color(col.lightened(0.25), 0.55 + 0.45 * near)
			for side in [-1.0, 1.0]:
				var o: Vector2 = nn * tube * 0.5 * side
				_hair(e0 + o, e1 + o, glow, 9.0)
				_hair(e0 + o, e1 + o, Color(col, 0.35 + 0.3 * near), 4.0)
				_hair(e0 + o, e1 + o, edge, 2.0)
			_hair(a + nn * tube * 0.12, b + nn * tube * 0.12, Color(col.lightened(0.5), 0.15 + 0.4 * near), tube * 0.18)
			if near > 0.55 and int(pc["q"]) % 3 == 0:
				var w := (a + b) * 0.5 - nn * tube * 0.2
				var wc := Color(_inks[int(pc["q"]) % _inks.size()], 0.8)
				_quad(w + Vector2(-2, 0), w + Vector2(0, -2), w + Vector2(2, 0), w + Vector2(0, 2), wc, wc, wc, wc)
		else:
			# A bridge: a deck with a rail, in the base's colour.
			var bc: Color = pc["col"]
			var deck := FILLS[0].lerp(bc, 0.35)
			var hw := tube * 0.22
			_quad(a - nn * hw, b - nn * hw, b + nn * hw, a + nn * hw, deck, deck, deck, deck)
			_hair(a, b, Color(bc, 0.12 + 0.1 * near), hw * 2.0 + 8.0)
			_hair(a - nn * hw, b - nn * hw, Color(bc.lightened(0.2), 0.6 + 0.4 * near), 2.0)
			_hair(a + nn * hw, b + nn * hw, Color(bc, 0.45 + 0.4 * near), 1.4)
	# Caps: a node on each strand's top, and a beacon over the axis.
	for sn in 2:
		var tp: Vector2 = pts[sn][n]["p"]
		_quad(tp + Vector2(-tube * 0.6, 0), tp + Vector2(0, -tube * 0.6), tp + Vector2(tube * 0.6, 0), tp + Vector2(0, tube * 0.6), col, col, col, col)
		_beacons.append({"pos": tp + Vector2(0, -tube), "color": col, "phase": 0.2 + sn * 0.3})
	_beacons.append({"pos": _iso(cx, cy) + Vector2(0, -z1 - 40.0 * k), "color": col, "phase": 0.5})


## A gold hieroglyph frieze on a sloped face (bottom edge p00-p10, top edge p01-p11):
## two rules at heights v0 and v1 (0-1 up the face) with `count` little signs between
## them; `gap` leaves the middle of the band open (for a ramp).
func _frieze(p00: Vector2, p10: Vector2, p01: Vector2, p11: Vector2, v0: float, v1: float, count: int, gap: float, gold: Color, salt: int) -> void:
	var band_col := Color(gold, 0.6)
	_hair(p00.lerp(p01, v0), p10.lerp(p11, v0), band_col, 1.2)
	_hair(p00.lerp(p01, v1), p10.lerp(p11, v1), band_col, 1.2)
	for q in count:
		var u := (q + 0.5) / count
		if absf(u - 0.5) < gap:
			continue
		var gp := p00.lerp(p10, u).lerp(p01.lerp(p11, u), (v0 + v1) * 0.5)
		var gh := (v1 - v0) * p00.lerp(p10, u).distance_to(p01.lerp(p11, u)) * 0.32
		var gc := Color(gold, 0.75)
		match int(_h(q, salt, 95) * 4.0):
			0:
				_hair(gp + Vector2(0, -gh), gp + Vector2(0, gh), gc, 1.2)
			1:
				for m in 6:
					var a0 := TAU * m / 6.0
					_hair(gp + Vector2(cos(a0), sin(a0)) * gh * 0.7, gp + Vector2(cos(a0 + TAU / 6.0), sin(a0 + TAU / 6.0)) * gh * 0.7, gc, 1.0)
			2:
				_hair(gp + Vector2(-gh * 0.6, gh * 0.4), gp + Vector2(0, -gh * 0.5), gc, 1.0)
				_hair(gp + Vector2(0, -gh * 0.5), gp + Vector2(gh * 0.6, gh * 0.4), gc, 1.0)
			_:
				_hair(gp + Vector2(-gh * 0.6, -gh * 0.3), gp + Vector2(gh * 0.6, -gh * 0.3), gc, 1.0)
				_hair(gp + Vector2(0, -gh * 0.3), gp + Vector2(0, gh), gc, 1.0)


## English HQ: a great clock tower (Big Ben style) with glowing clock faces, a belfry and a
## pinnacled spire, beside a long gabled hall.
func _hq_big_ben(cx: float, cy: float, k: float, col: Color, base: Vector2) -> void:
	# The hall behind and to the side.
	_extrude(_rect_pts(cx - 2.2 * k, cy - 1.9 * k, cx + 2.2 * k, cy - 0.9 * k), 0.0, 34.0 * k, 1.0, FILLS[1], col, 0.3, 980)
	_gable(cx - 2.2 * k, cy - 1.9 * k, cx + 2.2 * k, cy - 0.9 * k, 34.0 * k, 22.0 * k, FILLS[0], col)
	var r := 0.55 * k
	var th := 230.0 * k
	_extrude(_rect_pts(cx - r, cy - r, cx + r, cy + r), 0.0, th, 1.0, FILLS[1], col, 0.35, 981)
	# Vertical tracery up the two visible faces.
	for q in 3:
		var f := float(q + 1) / 4.0
		var pa := _iso(cx - r + 2.0 * r * f, cy + r)
		var pb := _iso(cx + r, cy - r + 2.0 * r * f)
		_ink_line(pa + Vector2(0, -6), pa + Vector2(0, -th + 6), Color(col, 0.35), 1.0, false)
		_ink_line(pb + Vector2(0, -6), pb + Vector2(0, -th + 6), Color(col, 0.25), 1.0, false)
	# Clock stage, a little wider, with a face on each visible side.
	var cr := 0.68 * k
	var ch := 58.0 * k
	_extrude(_rect_pts(cx - cr, cy - cr, cx + cr, cy + cr), th, ch, 1.0, FILLS[0], col, 0.0, 982)
	var face_col := Color(Palette.CRT_AMBER, 0.95)
	for side in 2:
		var fc: Vector2
		var u: Vector2
		if side == 0:
			fc = _iso(cx, cy + cr) + Vector2(0, -th - ch * 0.5)
			u = (_iso(1, 0) - _iso(0, 0)).normalized()
		else:
			fc = _iso(cx + cr, cy) + Vector2(0, -th - ch * 0.5)
			u = (_iso(0, 1) - _iso(0, 0)).normalized()
		var rad := cr * TILE_A * 0.72
		var ring := PackedVector2Array()
		for q in 33:
			var a := TAU * q / 32.0
			ring.append(fc + u * cos(a) * rad + Vector2(0, -1) * sin(a) * rad * 0.95)
		_poly(ring, Color(Palette.CRT_AMBER, 0.25))
		for q in 32:
			_ink_line(ring[q], ring[q + 1], face_col, 1.4, false)
		for q in 12:
			var a := TAU * q / 12.0
			var p0 := fc + u * cos(a) * rad * 0.8 + Vector2(0, -1) * sin(a) * rad * 0.8
			_ink_line(p0, fc + u * cos(a) * rad * 0.92 + Vector2(0, -1) * sin(a) * rad * 0.92, face_col, 1.0, false)
		_ink_line(fc, fc + Vector2(0, -rad * 0.62), face_col, 1.8, false)
		_ink_line(fc, fc + u * rad * 0.45, face_col, 1.8, false)
	# Belfry, then the spire with corner pinnacles.
	var br := 0.5 * k
	_extrude(_rect_pts(cx - br, cy - br, cx + br, cy + br), th + ch, 30.0 * k, 1.0, FILLS[1], col, 0.4, 983)
	_extrude(_rect_pts(cx - br, cy - br, cx + br, cy + br), th + ch + 30.0 * k, 80.0 * k, 0.05, FILLS[0], col, 0.0, 984)
	for q in [Vector2(-1, -1), Vector2(1, -1), Vector2(1, 1), Vector2(-1, 1)]:
		var p0 := _iso(cx + q.x * br, cy + q.y * br) + Vector2(0, -(th + ch + 30.0 * k))
		_ink_line(p0, p0 + Vector2(0, -22.0 * k), col, 1.3, false)
	_beacons.append({"pos": base + Vector2(0, -(th + ch + 118.0 * k)), "color": col, "phase": 0.2})


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
			var k := territory_label_px / 30.0 * inv
			var p := _iso(at.x + HQ_LOTS * 0.5, at.y + HQ_LOTS * 0.5) + Vector2(-120, -40) * k
			if t["id"] == FIST_TERRITORY:
				p.y -= FIST_SIZE.y * 0.56  # above the fist, not over it
			var col := Palette.PAPER if t["id"] == &"" else Palette.corp_color(t["id"])
			_fx.draw_rect(Rect2(p - Vector2(8, 30) * k, Vector2(260, 40) * k), Color(0, 0, 0, 0.75))
			_fx.draw_string(Palette.display(), p, name, HORIZONTAL_ALIGNMENT_LEFT, -1, int(30 * k), col)
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
