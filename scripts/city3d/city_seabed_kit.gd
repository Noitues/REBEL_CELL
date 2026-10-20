class_name CitySeabedKit
extends RefCounted
## LOOK L5 (whole-city plate parity, the designer's ruling: terrain first, then one textured water plane over it): the land
## under the sea as real ground. The bed falls from the shore (0 at the coast) toward `seabed_max_bu` over
## `seabed_reach_lots` lots of the shore field, its depth broken by the terrain's broad noise (`seabed_noise_k`) into shelves
## and trenches; the bay islands (CityWater.islands_of) rise out of it as hills. Coloured sand in the shallows to dark rock
## deep, the islands sand / meadow / forest by height. One indexed grid every `seabed_step` lots over the wet cells. Pure.

const SEED_TONE := 7780


## The seabed over `r` (lots) of `terrain`: `wet` and the shore field `d` (CityWater.shore_field) in row order over `r`,
## `islands` from CityWater.islands_of; null when nothing is wet.
static func mesh(cfg: CityConfig, terrain: CityA2Terrain, r: Rect2i, wet: PackedByteArray, d: PackedFloat32Array,
		islands: Array[Dictionary]) -> ArrayMesh:
	var g := maxi(cfg.seabed_step, 1)
	var w := r.size.x
	var h := r.size.y
	var nx := w / g + 1
	var ny := h / g + 1
	var verts := PackedVector3Array()
	var cols := PackedColorArray()
	verts.resize(nx * ny)
	cols.resize(nx * ny)
	var touch := PackedByteArray()
	touch.resize(nx * ny)
	var tc: Dictionary = cfg.terrain_colors
	for cj in ny:
		for ci in nx:
			var li := ci * g
			var lj := cj * g
			var s := 0.0
			var n := 0
			var wt := false
			for o: Vector2i in [Vector2i(-1, -1), Vector2i(0, -1), Vector2i(-1, 0), Vector2i(0, 0)]:
				var ii := li + o.x
				var jj := lj + o.y
				if ii >= 0 and ii < w and jj >= 0 and jj < h:
					s += d[jj * w + ii]
					n += 1
					wt = wt or wet[jj * w + ii] != 0
			var at := Vector2(r.position.x + li, r.position.y + lj)
			var dc := s / float(maxi(n, 1))
			var z := -cfg.seabed_max_bu * (1.0 - exp(-dc / cfg.seabed_reach_lots)) \
					* (1.0 + cfg.seabed_noise_k * (terrain.noise_at(at.x, at.y) * 2.0 - 1.0))
			z = minf(z, -cfg.seabed_shore_bu) if wt else minf(terrain.height_at(at.x, at.y), 0.0) - cfg.seabed_shore_bu
			for it: Dictionary in islands:
				var rho := at.distance_to(it["c"]) / (float(it["r"]) * cfg.island_spread)
				if rho < 1.0:
					z = lerpf(z, cfg.island_h_bu, pow(1.0 - rho * rho, 1.5))
			var k := cj * nx + ci
			touch[k] = 1 if wt else 0
			verts[k] = CityIsoCamera.lot_to_world(cfg, at, z)
			var tone := lerpf(0.85, 1.15, CityMeshKit.hash01(SEED_TONE, li, lj))
			var c: Color
			if z > 0.0:
				var f := clampf(z / maxf(cfg.island_h_bu, 0.001), 0.0, 1.0)
				c = (tc["beach"] as Color).lerp(tc["meadow"], smoothstep(0.0, 0.35, f)).lerp(tc["forest"], smoothstep(0.4, 0.9, f))
			else:
				c = cfg.seabed_sand.lerp(cfg.seabed_deep, 1.0 - exp(z / cfg.seabed_tone_bu))
			cols[k] = Color(c.r * tone, c.g * tone, c.b * tone)
	var idx := PackedInt32Array()
	var up := (verts[1] - verts[0]).cross(verts[nx] - verts[0]).y > 0.0
	for cj in ny - 1:
		for ci in nx - 1:
			var a := cj * nx + ci
			var b := a + 1
			var c2 := a + nx + 1
			var e := a + nx
			if touch[a] == 0 and touch[b] == 0 and touch[c2] == 0 and touch[e] == 0:
				continue
			if up:
				idx.append_array([a, b, c2, a, c2, e])
			else:
				idx.append_array([a, c2, b, a, e, c2])
	if idx.is_empty():
		return null
	var nrm := PackedVector3Array()
	nrm.resize(verts.size())
	for t in range(0, idx.size(), 3):
		var fn := (verts[idx[t + 1]] - verts[idx[t]]).cross(verts[idx[t + 2]] - verts[idx[t]])
		for q in 3:
			nrm[idx[t + q]] += fn
	for v in nrm.size():
		nrm[v] = nrm[v].normalized() if nrm[v].length_squared() > 0.0 else Vector3.UP
		if nrm[v].y < 0.0:
			nrm[v] = -nrm[v]
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = verts
	arr[Mesh.ARRAY_NORMAL] = nrm
	arr[Mesh.ARRAY_COLOR] = cols
	arr[Mesh.ARRAY_INDEX] = idx
	var m := ArrayMesh.new()
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	return m


## The water plane: one quad `outer_bu` wide at `y`, round the origin.
static func plane_mesh(outer_bu: float, y: float) -> ArrayMesh:
	var hw := outer_bu * 0.5
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = PackedVector3Array([Vector3(-hw, y, -hw), Vector3(hw, y, -hw), Vector3(hw, y, hw), Vector3(-hw, y, hw)])
	arr[Mesh.ARRAY_NORMAL] = PackedVector3Array([Vector3.UP, Vector3.UP, Vector3.UP, Vector3.UP])
	arr[Mesh.ARRAY_INDEX] = PackedInt32Array([0, 1, 2, 0, 2, 3])
	var m := ArrayMesh.new()
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	return m
