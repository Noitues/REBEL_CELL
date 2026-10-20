class_name CityA2Terrain
extends RefCounted
## CITY-A2 step 2: the ground of the planner city A2, a heightfield (BU above sea level, which is 0) the city stands on,
## in lots. Seed-independent (A2 is fixed): built once per config from the A2 raster (CityA2Builder.terrain).
##
## Height = (A2's hills + the land beyond) x the beach, 0 on the water:
## - hills: A2's Gaussians (art-pass terrain_a2.py form: east / north offsets turned by the hill's rotation), height_m x
##   lot_bu / metres per lot x `city_a2_hill_exag` (247 m -> 12 BU);
## - beyond: outside the outer ring road (`city_a2_outer_ring`), foothills and mountains rising with the distance past it
##   (`city_a2_foot` / `city_a2_mountain` x their heights), shaped by value noise whose lattice comes from the RNG
##   stream `city_terrain` of `city_a2_terrain_seed`, kept off the shore (`city_a2_mountain_shore`);
## - beach: the land falls to 0 over `city_a2_beach` lots from the water.
## Two grids of corner samples (lot points): `fine` every lot over the raster (the city rect grown by the raster margin;
## water from the raster), `coarse` every `city_a2_land_step` lots over the city rect grown by `city_a2_land_margin`
## (water from A2's ocean polygon and lakes; past the polygon's box the sea or land of its nearest edge goes on).
## `height_at` reads the fine grid inside it, else the coarse one (bilinear). Pure: no Node; one named RNG stream.

const DIAG := 1.41421356

var fine_rect: Rect2i = Rect2i()
## Corner heights over `fine_rect` ((size.x + 1) x (size.y + 1), row order).
var fine: PackedFloat32Array = PackedFloat32Array()
## The coarse grid's lots (a whole number of steps) and step.
var coarse_rect: Rect2i = Rect2i()
var step: int = 1
var coarse: PackedFloat32Array = PackedFloat32Array()
## 1 where a coarse corner is in the sea or a lake.
var coarse_water: PackedByteArray = PackedByteArray()
## The mountain term (BU, before the beach) on the coarse grid: the fine grid reads it bilinearly.
var _mount: PackedFloat32Array = PackedFloat32Array()
var _cw: int = 0
var _ch: int = 0
var _fw: int = 0


## The terrain of raster `ras` (its plan, metres per lot and water) with config `cfg`'s numbers; heights in BU of `lot_bu`.
static func make(ras: CityA2Raster, cfg: CampaignConfigData, city_rect: Rect2i, lot_bu: float) -> CityA2Terrain:
	var t := CityA2Terrain.new()
	t.step = maxi(cfg.city_a2_land_step, 1)
	var outer := city_rect.grow(cfg.city_a2_land_margin)
	var cw := ceili(float(outer.size.x) / t.step)
	var ch := ceili(float(outer.size.y) / t.step)
	t.coarse_rect = Rect2i(outer.position, Vector2i(cw, ch) * t.step)
	t._cw = cw + 1
	t._ch = ch + 1
	t._coarse(ras, cfg, lot_bu)
	t.fine_rect = ras.rect
	t._fine(ras, cfg, lot_bu)
	return t


## The ground (BU) at lot point (x, y).
func height_at(x: float, y: float) -> float:
	if x >= fine_rect.position.x and y >= fine_rect.position.y and x <= fine_rect.end.x and y <= fine_rect.end.y:
		return _bilerp(fine, _fw, fine_rect.position, 1, x, y)
	return _bilerp(coarse, _cw, coarse_rect.position, step, x, y)


## The ground (BU) at the centre of lot (i, j) (streets, plazas, lot markers).
func lot_height(i: int, j: int) -> float:
	return height_at(i + 0.5, j + 0.5)


## The ground (BU) a building on lots `cell` stands on: the lowest of its corners, so no side floats on a slope.
func cell_ground(cell: Rect2i) -> float:
	var lo := INF
	for c: Vector2i in [cell.position, Vector2i(cell.end.x, cell.position.y), cell.end, Vector2i(cell.position.x, cell.end.y)]:
		lo = minf(lo, height_at(c.x, c.y))
	return lo


## The ground heights of the lot corners of `r` (lots), row by row ((size.x + 1) x (size.y + 1)), rounded to `decimals`.
func corner_grid(r: Rect2i, decimals: int) -> Array:
	var out: Array = []
	var k := pow(10.0, decimals)
	for j in range(r.position.y, r.end.y + 1):
		var row: Array = []
		for i in range(r.position.x, r.end.x + 1):
			row.append(roundf(height_at(i, j) * k) / k)
		out.append(row)
	return out


static func _bilerp(g: PackedFloat32Array, w: int, at: Vector2i, s: int, x: float, y: float) -> float:
	var h := g.size() / w
	var u := clampf((x - at.x) / s, 0.0, w - 1.0)
	var v := clampf((y - at.y) / s, 0.0, h - 1.0)
	var i0 := mini(floori(u), w - 2)
	var j0 := mini(floori(v), h - 2)
	var fu := u - i0
	var fv := v - j0
	var a := g[j0 * w + i0] * (1.0 - fu) + g[j0 * w + i0 + 1] * fu
	var b := g[(j0 + 1) * w + i0] * (1.0 - fu) + g[(j0 + 1) * w + i0 + 1] * fu
	return a * (1.0 - fv) + b * fv


static func _smooth(x: float, a: float, b: float) -> float:
	var t := clampf((x - a) / maxf(b - a, 0.0001), 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)


## A2's hills at lot point `p` (BU).
static func _hills(ras: CityA2Raster, p: Vector2, k_bu: float) -> float:
	var m := ras.metres_of(p)
	var h := 0.0
	for hl: Dictionary in ras.a2.hills:
		var c: Vector2 = hl["centre"]
		var s: Vector2 = hl["sigma"]
		var dx := m.x - c.x
		var dy := m.y - c.y
		var reach := 4.0 * maxf(s.x, s.y)
		if absf(dx) > reach or absf(dy) > reach:
			continue
		var r := float(hl["rotation"])
		var u := dx * cos(r) + dy * sin(r)
		var v := -dx * sin(r) + dy * cos(r)
		h += float(hl["height"]) * k_bu * exp(-0.5 * (u * u / (s.x * s.x) + v * v / (s.y * s.y)))
	return h


## True when A2 point `m` (metres) is in the sea or a lake; past the ocean polygon's box, the point clamped into it.
static func _wet(a2: CityPlanA2, box: Rect2, m: Vector2) -> bool:
	var q := Vector2(clampf(m.x, box.position.x + 1.0, box.end.x - 1.0), clampf(m.y, box.position.y + 1.0, box.end.y - 1.0))
	if Geometry2D.is_point_in_polygon(q, a2.ocean):
		return true
	for l in a2.lakes:
		if Geometry2D.is_point_in_polygon(m, l):
			return true
	return false


## Chamfer distance (in grid cells) of every cell from the cells where `src` is 1.
static func _chamfer(src: PackedByteArray, w: int, h: int) -> PackedFloat32Array:
	var d := PackedFloat32Array()
	d.resize(w * h)
	for k in w * h:
		d[k] = 0.0 if src[k] != 0 else 1e9
	for j in h:
		for i in w:
			var k := j * w + i
			var v := d[k]
			if i > 0:
				v = minf(v, d[k - 1] + 1.0)
			if j > 0:
				v = minf(v, d[k - w] + 1.0)
				if i > 0:
					v = minf(v, d[k - w - 1] + DIAG)
				if i < w - 1:
					v = minf(v, d[k - w + 1] + DIAG)
			d[k] = v
	for j in range(h - 1, -1, -1):
		for i in range(w - 1, -1, -1):
			var k := j * w + i
			var v := d[k]
			if i < w - 1:
				v = minf(v, d[k + 1] + 1.0)
			if j < h - 1:
				v = minf(v, d[k + w] + 1.0)
				if i < w - 1:
					v = minf(v, d[k + w + 1] + DIAG)
				if i > 0:
					v = minf(v, d[k + w - 1] + DIAG)
			d[k] = v
	return d


## Value noise in [0, 1) at (x, y) (lattice units) over lattice `g` (`gw` wide).
static func _vnoise(g: PackedFloat32Array, gw: int, x: float, y: float) -> float:
	var x0 := floori(x)
	var y0 := floori(y)
	var fx := x - x0
	var fy := y - y0
	var sx := fx * fx * (3.0 - 2.0 * fx)
	var sy := fy * fy * (3.0 - 2.0 * fy)
	var a := g[y0 * gw + x0] * (1.0 - sx) + g[y0 * gw + x0 + 1] * sx
	var b := g[(y0 + 1) * gw + x0] * (1.0 - sx) + g[(y0 + 1) * gw + x0 + 1] * sx
	return a * (1.0 - sy) + b * sy


func _coarse(ras: CityA2Raster, cfg: CampaignConfigData, lot_bu: float) -> void:
	var a2 := ras.a2
	var n := _cw * _ch
	var box := Rect2(a2.ocean[0], Vector2.ZERO)
	for q in a2.ocean:
		box = box.expand(q)
	var ring := PackedVector2Array()
	var rd := a2.road(cfg.city_a2_outer_ring)
	if not rd.is_empty():
		ring = rd["polyline"]
	coarse_water.resize(n)
	var inside := PackedByteArray()
	inside.resize(n)
	for j in _ch:
		for i in _cw:
			var m := ras.metres_of(Vector2(coarse_rect.position) + Vector2(i, j) * step)
			coarse_water[j * _cw + i] = 1 if _wet(a2, box, m) else 0
			inside[j * _cw + i] = 1 if ring.size() >= 3 and Geometry2D.is_point_in_polygon(m, ring) else 0
	var d_out := _chamfer(inside, _cw, _ch)
	var d_w := _chamfer(coarse_water, _cw, _ch)
	# The noise lattices (broad, fine, ridge), drawn in that order from the terrain stream.
	var rng := RngStreams.make_stream(cfg.city_a2_terrain_seed, RngStreams.CITY_TERRAIN_STREAM)
	var cells := [cfg.city_a2_noise_cells.x, cfg.city_a2_noise_cells.y, cfg.city_a2_noise_cells.z]
	var lat: Array[PackedFloat32Array] = []
	var lw: Array[int] = []
	for c: float in cells:
		var gw := int(float(coarse_rect.size.x) / c) + 3
		var gh := int(float(coarse_rect.size.y) / c) + 3
		var g := PackedFloat32Array()
		g.resize(gw * gh)
		for k in gw * gh:
			g[k] = rng.randf()
		lat.append(g)
		lw.append(gw)
	_mount.resize(n)
	coarse.resize(n)
	var k_bu := lot_bu / ras.metres_per_lot * cfg.city_a2_hill_exag
	for j in _ch:
		for i in _cw:
			var k := j * _cw + i
			var x := float(i * step)
			var y := float(j * step)
			var na := _vnoise(lat[0], lw[0], x / cells[0], y / cells[0]) * 0.65 + _vnoise(lat[1], lw[1], x / cells[1], y / cells[1]) * 0.35
			var rid := 1.0 - absf(2.0 * _vnoise(lat[2], lw[2], x / cells[2], y / cells[2]) - 1.0)
			var d := d_out[k] * step
			var mt := cfg.city_a2_foot_h * _smooth(d, cfg.city_a2_foot.x, cfg.city_a2_foot.y) * (0.35 + na) \
				+ cfg.city_a2_mountain_h * pow(_smooth(d, cfg.city_a2_mountain.x, cfg.city_a2_mountain.y), 1.35) * (0.4 + 0.85 * rid + 0.35 * na)
			mt *= _smooth(d_w[k] * step, cfg.city_a2_mountain_shore.x, cfg.city_a2_mountain_shore.y)
			_mount[k] = mt
			if coarse_water[k] != 0:
				coarse[k] = 0.0
			else:
				var p := Vector2(coarse_rect.position) + Vector2(i, j) * step
				coarse[k] = (_hills(ras, p, k_bu) + mt) * _smooth(d_w[k] * step, cfg.city_a2_beach.x, cfg.city_a2_beach.y)


func _fine(ras: CityA2Raster, cfg: CampaignConfigData, lot_bu: float) -> void:
	_fw = fine_rect.size.x + 1
	var fh := fine_rect.size.y + 1
	fine.resize(_fw * fh)
	var k_bu := lot_bu / ras.metres_per_lot * cfg.city_a2_hill_exag
	for j in fh:
		for i in _fw:
			var p := Vector2i(fine_rect.position.x + i, fine_rect.position.y + j)
			# The four lots round the corner: a water lot keeps the corner at sea level; else the nearest shore.
			var near := INF
			for q: Vector2i in [p, p - Vector2i(1, 0), p - Vector2i(0, 1), p - Vector2i(1, 1)]:
				near = minf(near, float(ras.depth[ras.index(q.x, q.y)]))
			if near <= 0.0:
				fine[j * _fw + i] = 0.0
				continue
			var pf := Vector2(p)
			var mt := _bilerp(_mount, _cw, coarse_rect.position, step, pf.x, pf.y)
			fine[j * _fw + i] = (_hills(ras, pf, k_bu) + mt) * _smooth(near, cfg.city_a2_beach.x, cfg.city_a2_beach.y)
