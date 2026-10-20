class_name CityParkKit
extends RefCounted
## LOOK L5 (whole-city plate parity, hybrid port): the city's park lots as lawn with tree clumps, ported from the Blender
## plate build (art-pass city_all_corps/scripts/city_world_a2.py `park_trees`, city_preset PARKS): `park_tree_share` of
## the park lots carry `park_clumps` clumps of `park_trees` trees, each a low dome in one of the tree colours. Pure: hashed
## per lot, no RNG stream.

const SEED_PICK := 7740
const SEED_TREE := 7741
const DOME_SIDES := 6


## The park lots (CityA2Builder K_PARK) of seed `city_seed` inside `r` (lots).
static func parks_in(city_seed: int, r: Rect2i) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	var p := CityPlan.for_seed(city_seed)
	if p.a2 == null:
		return out
	var lots := CityA2Builder.lots_for(p, CityPlan.plan_config(), NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY,
			1.0 / CityView3D.CONFIG.height_px_bu)
	var R: Rect2i = lots["rect"]
	var kind: PackedByteArray = lots["kind"]
	var b := r.intersection(R)
	for j in range(b.position.y, b.end.y):
		for i in range(b.position.x, b.end.x):
			if kind[(j - R.position.y) * R.size.x + (i - R.position.x)] == CityA2Builder.K_PARK:
				out.append(Vector2i(i, j))
	return out


## Lawn quads and tree domes for `parks` on `terrain` (null when there are none).
static func mesh(cfg: CityConfig, parks: Array[Vector2i], terrain: CityA2Terrain) -> ArrayMesh:
	if parks.is_empty() or terrain == null:
		return null
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var cols: Array = cfg.park_tree_colors
	for l in parks:
		var q: Array[Vector3] = []
		for c: Vector2i in [l, l + Vector2i(1, 0), l + Vector2i(1, 1), l + Vector2i(0, 1)]:
			q.append(CityIsoCamera.lot_to_world(cfg, Vector2(c), terrain.height_at(c.x, c.y) + cfg.park_lawn_lift))
		CityMeshKit._quad(st, q[0], q[1], q[2], q[3], cfg.park_lawn)
		if CityMeshKit.hash01(SEED_PICK, l.x, l.y) >= cfg.park_tree_share:
			continue
		var n := 0
		for cl in cfg.park_clumps:
			var cu := Vector2(0.2 + 0.6 * CityMeshKit.hash01(SEED_TREE, l.x * 31 + cl, l.y), 0.2 + 0.6 * CityMeshKit.hash01(SEED_TREE + 1, l.x, l.y * 31 + cl))
			var count := cfg.park_trees.x + int(CityMeshKit.hash01(SEED_TREE + 2, l.x + cl, l.y) * float(cfg.park_trees.y - cfg.park_trees.x + 1))
			for t in count:
				n += 1
				var hs := func(s: int) -> float: return CityMeshKit.hash01(SEED_TREE + s, l.x * 977 + n, l.y * 613 + cl)
				var at := Vector2(l) + cu + Vector2(hs.call(3) - 0.5, hs.call(4) - 0.5) * cfg.park_clump_spread
				var r := lerpf(cfg.park_tree_r.x, cfg.park_tree_r.y, hs.call(5))
				var col: Color = cols[int(hs.call(6) * cols.size()) % cols.size()]
				var g := lerpf(0.8, 1.15, hs.call(7))
				_dome(st, cfg, CityIsoCamera.lot_to_world(cfg, at, terrain.height_at(at.x, at.y)), r * cfg.park_tree_w, r,
						Color(col.r * g, col.g * g, col.b * g))
	st.generate_normals()
	return st.commit()


## A low cone-dome of radius `w` (BU) and height `h` at `base` (a ring of DOME_SIDES faces to an apex).
static func _dome(st: SurfaceTool, cfg: CityConfig, base: Vector3, w: float, h: float, col: Color) -> void:
	var apex := base + Vector3(0.0, h * cfg.park_tree_h, 0.0)
	var mid := base + Vector3(0.0, h * cfg.park_tree_h * 0.45, 0.0)
	for s in DOME_SIDES:
		var a0 := TAU * float(s) / float(DOME_SIDES)
		var a1 := TAU * float(s + 1) / float(DOME_SIDES)
		var p0 := mid + Vector3(cos(a0), 0.0, sin(a0)) * w
		var p1 := mid + Vector3(cos(a1), 0.0, sin(a1)) * w
		var b0 := base + Vector3(cos(a0), 0.0, sin(a0)) * w * 0.6
		var b1 := base + Vector3(cos(a1), 0.0, sin(a1)) * w * 0.6
		for v: Vector3 in [apex, p1, p0, p0, p1, b1, p0, b1, b0]:
			st.set_color(col)
			st.add_vertex(v)
