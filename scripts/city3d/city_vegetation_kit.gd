class_name CityVegetationKit
extends RefCounted
## LOOK L5 (whole-city plate parity): light vegetation on the green land, as the Blender plate's scattered trees: low domes
## (CityParkKit's) on the land past the city (a sample every `veg_step` lots, kept by the land's forest share between
## `veg_density` x and y, none on water, steep or snowy ground) and on the city's bare lots (`veg_bare_share` of them). One
## MultiMesh, an instance colour each from `park_tree_colors`. Pure: hashed per lot, no RNG stream.

const SEED_PICK := 7770
const SEED_AT := 7771
const SEED_SIZE := 7772
const SEED_COL := 7773


## The vegetation of `terrain` (city seed `city_seed`) with the city's built rect `hole` skipped (null when none grows).
static func multimesh(cfg: CityConfig, terrain: CityA2Terrain, city_seed: int, hole: Rect2i) -> MultiMesh:
	if terrain == null:
		return null
	var xfs: Array[Transform3D] = []
	var cols: Array[Color] = []
	var cr := terrain.coarse_rect
	var s := maxi(cfg.veg_step, 1)
	var r: Dictionary = cfg.terrain_rule
	var k: float = cfg.terrain_h_scale
	var ras := CityPlan.for_seed(city_seed).a2
	for j in range(cr.position.y, cr.end.y, s):
		for i in range(cr.position.x, cr.end.x, s):
			if hole.has_point(Vector2i(i, j)):
				continue
			var at := Vector2(i, j) + Vector2(CityMeshKit.hash01(SEED_AT, i, j), CityMeshKit.hash01(SEED_AT + 1, i, j)) * float(s)
			var h := terrain.height_at(at.x, at.y)
			if h <= cfg.veg_min_h or terrain.is_water_at(at.x, at.y) or h > float(r["snow_h"]) * k:
				continue
			if CityTerrainColor.slope_at(cfg, terrain, Vector2i(at)) > cfg.veg_max_slope:
				continue
			if _near_sea(ras, Vector2i(at), cfg.veg_coast_clear):
				continue
			var f := clampf(float(r["forest_from"]) + h / (float(r["forest_h"]) * k), 0.0, 1.0)
			if CityMeshKit.hash01(SEED_PICK, i, j) >= lerpf(cfg.veg_density.x, cfg.veg_density.y, f):
				continue
			_add(cfg, terrain, at, i, j, xfs, cols)
	for l in CityParkKit.lots_of(city_seed, hole, CityA2Builder.K_BARE):
		if _near_sea(ras, l, cfg.veg_coast_clear):
			continue
		if CityMeshKit.hash01(SEED_PICK + 1, l.x, l.y) < cfg.veg_bare_share:
			_add(cfg, terrain, Vector2(l) + Vector2(0.5, 0.5), l.x, l.y, xfs, cols)
	if xfs.is_empty():
		return null
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.mesh = _unit_dome(cfg)
	mm.instance_count = xfs.size()
	for n in xfs.size():
		mm.set_instance_transform(n, xfs[n])
		mm.set_instance_color(n, cols[n])
	return mm


## Whether a sea lot (water, not river) of `ras` lies within `n` lots (Chebyshev) of lot `l` (false off the raster).
static func _near_sea(ras: CityA2Raster, l: Vector2i, n: int) -> bool:
	if ras == null or n <= 0 or not ras.rect.has_point(l):
		return false
	for dj in range(-n, n + 1):
		for di in range(-n, n + 1):
			if ras.is_water(l.x + di, l.y + dj) and not ras.is_river(l.x + di, l.y + dj):
				return true
	return false


static func _add(cfg: CityConfig, terrain: CityA2Terrain, at: Vector2, i: int, j: int, xfs: Array[Transform3D],
		cols: Array[Color]) -> void:
	var rr := lerpf(cfg.veg_r.x, cfg.veg_r.y, CityMeshKit.hash01(SEED_SIZE, i, j))
	var p := CityIsoCamera.lot_to_world(cfg, at, terrain.height_at(at.x, at.y))
	xfs.append(Transform3D(Basis.from_scale(Vector3(rr * cfg.park_tree_w, rr, rr * cfg.park_tree_w)), p))
	var tc: Array = cfg.park_tree_colors
	var c: Color = tc[int(CityMeshKit.hash01(SEED_COL, i, j) * tc.size()) % tc.size()]
	var g := lerpf(0.8, 1.15, CityMeshKit.hash01(SEED_COL + 1, i, j))
	cols.append(Color(c.r * g, c.g * g, c.b * g))


## One white dome of radius 1 and height 1 (CityParkKit._dome) for the instances to scale.
static func _unit_dome(cfg: CityConfig) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	CityParkKit._dome(st, cfg, Vector3.ZERO, 1.0, 1.0, Color.WHITE)
	st.generate_normals()
	return st.commit()
