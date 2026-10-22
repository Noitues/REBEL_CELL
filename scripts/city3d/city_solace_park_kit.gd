class_name CitySolaceParkKit
extends RefCounted
## LOOK Solace park (A-069 / A-070 layout, concept round 5 D_raid_park_r5 / D_night_park_r5): the Solace district's park drawn
## from the layout's own data (CitySolacePark.build, the `solace_park` of city.json, lot space): a lime-green lawn on the park
## lots, the footpaths and lanes (gravel ribbons with a lit lime line at night), the ponds, and the HQ's 3-tier plinth
## with its N / E / S / W stairs (radius of the layout, 35 BU). Pure geometry (no RNG: hashed per lot); one ArrayMesh in world
## space. The vertex colour is the base colour and its alpha the part (PART_*), read by city_solace_park.gdshader, which draws
## it in the cel map look and in the AAA-2 look.

const PART_LAWN := 0.2
const PART_PATH := 0.4
const PART_LIT := 0.6
const PART_WATER := 0.8
const PART_STONE := 1.0
const SALT_LAWN := 9150
const RING_SEGS := 48

static var _cache: Dictionary = {}


## The park of the Solace territory of seed `city_seed` ({} when the plan has none): CityA2Builder.lots_for(...)["solace"].
static func data(city_seed: int) -> Dictionary:
	if _cache.has(city_seed):
		return _cache[city_seed]
	var out := {}
	var p := CityPlan.for_seed(city_seed)
	if p != null and p.a2 != null and p.has_territory(&"solace"):
		var lots := CityA2Builder.lots_for(p, CityPlan.plan_config(), NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY,
				1.0 / CityView3D.CONFIG.height_px_bu)
		out = lots.get("solace", {})
	_cache[city_seed] = out
	return out


## The park lots of seed `city_seed` as a set (Vector2i -> true; empty without a Solace park).
static func lot_set(city_seed: int) -> Dictionary:
	var out := {}
	for l: Vector2i in data(city_seed).get("lots", []):
		out[l] = true
	return out


## Forgets the cached parks (tests, a new campaign).
static func forget() -> void:
	_cache.clear()


## The park as one mesh (world space), null without data. `terrain` may be null (flat ground).
static func mesh(cfg: CityConfig, park: Dictionary, terrain: CityA2Terrain) -> ArrayMesh:
	if park.is_empty():
		return null
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	_lawn(st, cfg, park, terrain)
	_paths(st, cfg, park, terrain)
	_ponds(st, cfg, park, terrain)
	_plinth(st, cfg, park, terrain)
	st.generate_normals()
	return st.commit()


static func _h(terrain: CityA2Terrain, p: Vector2) -> float:
	return terrain.height_at(p.x, p.y) if terrain != null else 0.0


static func _w(cfg: CityConfig, p: Vector2, terrain: CityA2Terrain, lift: float) -> Vector3:
	return CityIsoCamera.lot_to_world(cfg, p, _h(terrain, p) + lift)


static func _v(st: SurfaceTool, v: Vector3, c: Color, part: float) -> void:
	st.set_color(Color(c.r, c.g, c.b, part))
	st.add_vertex(v)


static func _quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, col: Color, part: float) -> void:
	for v: Vector3 in [a, b, c, a, c, d]:
		_v(st, v, col, part)


## Lawn: every park lot in `park_lawn_div` x `park_lawn_div` cells, two lime-green tones by a hashed field (as CityParkKit).
static func _lawn(st: SurfaceTool, cfg: CityConfig, park: Dictionary, terrain: CityA2Terrain) -> void:
	var nd := maxi(cfg.park_lawn_div, 1)
	var lift := cfg.solace_park_lift
	var s := 1.0 / float(nd)
	for l: Vector2i in park["lots"]:
		for vj in nd:
			for vi in nd:
				var q := Vector2(l) + Vector2(vi, vj) * s
				var t := CityMeshKit.hash01(SALT_LAWN + l.x * 7, l.y * nd + vj, vi + l.x * nd)
				var col := cfg.solace_park_lawn_a.lerp(cfg.solace_park_lawn_b, t)
				_quad(st, _w(cfg, q, terrain, lift), _w(cfg, q + Vector2(0, s), terrain, lift), _w(cfg, q + Vector2(s, s), terrain, lift),
					_w(cfg, q + Vector2(s, 0), terrain, lift), col, PART_LAWN)


static func _ribbon(st: SurfaceTool, cfg: CityConfig, pts: PackedVector2Array, width_bu: float, lift: float, col: Color, part: float,
		terrain: CityA2Terrain) -> void:
	if pts.size() < 2:
		return
	var left: Array[Vector3] = []
	var right: Array[Vector3] = []
	for i in pts.size():
		var a := _w(cfg, pts[maxi(i - 1, 0)], terrain, 0.0)
		var b := _w(cfg, pts[mini(i + 1, pts.size() - 1)], terrain, 0.0)
		var t := Vector2(b.x - a.x, b.z - a.z)
		if t.length() < 0.0001:
			t = Vector2.RIGHT
		t = t.normalized()
		var n := Vector3(-t.y, 0.0, t.x) * width_bu * 0.5
		var c := _w(cfg, pts[i], terrain, lift)
		left.append(c - n)
		right.append(c + n)
	for i in pts.size() - 1:
		_quad(st, left[i], right[i], right[i + 1], left[i + 1], col, part)


## Paths and lanes: a gravel (or lane) ribbon of the layout's width; footpaths and stairs carry a lit lime centre line.
static func _paths(st: SurfaceTool, cfg: CityConfig, park: Dictionary, terrain: CityA2Terrain) -> void:
	for p: Dictionary in park["paths"]:
		var kind := String(p["kind"])
		var w := float(p["width_bu"])
		var pts: PackedVector2Array = p["points"]
		_ribbon(st, cfg, pts, w, cfg.solace_park_lift * 2.0, cfg.solace_park_lane if kind == "lane" else cfg.solace_park_gravel, PART_PATH, terrain)
		if kind != "lane":
			_ribbon(st, cfg, pts, minf(cfg.solace_park_line_w, w * 0.5), cfg.solace_park_lift * 3.0, cfg.solace_lime, PART_LIT, terrain)


static func _ponds(st: SurfaceTool, cfg: CityConfig, park: Dictionary, terrain: CityA2Terrain) -> void:
	var lift := cfg.solace_park_lift * 2.5
	for p: Dictionary in park["ponds"]:
		var c: Vector2 = p["centre"]
		var poly: PackedVector2Array = p["points"]
		var cw := _w(cfg, c, terrain, lift)
		for i in poly.size():
			var a := _w(cfg, poly[i], terrain, lift)
			var b := _w(cfg, poly[(i + 1) % poly.size()], terrain, lift)
			for v: Vector3 in [cw, a, b]:
				_v(st, v, cfg.solace_park_water, PART_WATER)


static func _ring(st: SurfaceTool, c: Vector3, r: float, w: float, col: Color, part: float) -> void:
	for k in RING_SEGS:
		var a0 := TAU * float(k) / RING_SEGS
		var a1 := TAU * float(k + 1) / RING_SEGS
		var p0 := Vector3(cos(a0), 0.0, sin(a0))
		var p1 := Vector3(cos(a1), 0.0, sin(a1))
		_quad(st, c + p0 * (r - w * 0.5), c + p0 * (r + w * 0.5), c + p1 * (r + w * 0.5), c + p1 * (r - w * 0.5), col, part)


static func _line(st: SurfaceTool, a: Vector3, b: Vector3, side: Vector3, w: float, col: Color) -> void:
	_quad(st, a - side * w * 0.5, a + side * w * 0.5, b + side * w * 0.5, b - side * w * 0.5, col, PART_LIT)


## The plinth: stone tiers (radius ratios `solace_plinth_tiers`, rising to `solace_plinth_top` BU), a lit lime ring on every tier edge,
## the pink and lime rings on the top, and a stair flight at each of the layout's stairs (N = -z, E = +x, S = +z, W = -x).
static func _plinth(st: SurfaceTool, cfg: CityConfig, park: Dictionary, terrain: CityA2Terrain) -> void:
	var pl: Dictionary = park.get("plinth", {})
	if pl.is_empty():
		return
	var R := float(pl["radius_bu"])
	var cl: Vector2 = pl["centre"]
	var base := CityIsoCamera.lot_to_world(cfg, cl, _h(terrain, cl))
	var tiers := cfg.solace_plinth_tiers
	var top_h := cfg.solace_plinth_top
	var n_t := tiers.size()
	var stone := cfg.solace_park_stone
	for ti in n_t:
		var r := R * tiers[ti]
		var z1 := base.y + top_h * float(ti + 1) / float(n_t)
		var z0 := base.y
		for k in RING_SEGS:
			var a0 := TAU * float(k) / RING_SEGS
			var a1 := TAU * float(k + 1) / RING_SEGS
			var b0 := base + Vector3(cos(a0), 0.0, sin(a0)) * r
			var b1 := base + Vector3(cos(a1), 0.0, sin(a1)) * r
			_quad(st, Vector3(b0.x, z0, b0.z), Vector3(b1.x, z0, b1.z), Vector3(b1.x, z1, b1.z), Vector3(b0.x, z1, b0.z), stone, PART_STONE)
			for v: Vector3 in [Vector3(base.x, z1, base.z), Vector3(b1.x, z1, b1.z), Vector3(b0.x, z1, b0.z)]:
				_v(st, v, stone, PART_STONE)
		_ring(st, Vector3(base.x, z1 + 0.02, base.z), r - 0.12, cfg.solace_park_line_w * 0.7, cfg.solace_lime, PART_LIT)
	var topc := Vector3(base.x, base.y + top_h + 0.03, base.z)
	_ring(st, topc, R * cfg.solace_plinth_rings.x, cfg.solace_park_line_w * 0.5, cfg.solace_pink, PART_LIT)
	_ring(st, topc, R * cfg.solace_plinth_rings.y, cfg.solace_park_line_w * 0.8, cfg.solace_lime, PART_LIT)
	var hw := R * cfg.solace_plinth_stair.x
	var r0 := R * tiers[n_t - 1] - 0.2
	var r1 := R * cfg.solace_plinth_stair.y
	var ns := 12
	var dirs := {"N": Vector3(0, 0, -1), "E": Vector3(1, 0, 0), "S": Vector3(0, 0, 1), "W": Vector3(-1, 0, 0)}
	for s: Dictionary in pl["stairs"]:
		var d: Vector3 = dirs.get(String(s["dir"]), Vector3.ZERO)
		if d == Vector3.ZERO:
			continue
		var side := Vector3(-d.z, 0.0, d.x)
		for k in ns:
			var a := r0 + (r1 - r0) * float(k) / ns
			var b := r0 + (r1 - r0) * float(k + 1) / ns
			var z1 := base.y + top_h * (1.0 - float(k) / ns) - 0.02
			var pa := base + d * a
			var pb := base + d * b
			_quad(st, Vector3(pa.x, z1, pa.z) - side * hw, Vector3(pa.x, z1, pa.z) + side * hw, Vector3(pb.x, z1, pb.z) + side * hw,
				Vector3(pb.x, z1, pb.z) - side * hw, stone.lightened(0.15), PART_STONE)
			_quad(st, Vector3(pb.x, base.y, pb.z) - side * hw, Vector3(pb.x, base.y, pb.z) + side * hw, Vector3(pb.x, z1, pb.z) + side * hw,
				Vector3(pb.x, z1, pb.z) - side * hw, stone, PART_STONE)
		for sg: float in [-1.0, 1.0]:
			var ea := base + d * r0 + side * hw * sg + Vector3(0, top_h + 0.05, 0)
			var eb := base + d * r1 + side * hw * sg + Vector3(0, 0.1, 0)
			_line(st, ea, eb, Vector3.UP, cfg.solace_park_line_w * 0.5, cfg.solace_lime)
