class_name CitySeabedKit
extends RefCounted
## LOOK L5 (whole-city plate parity, the designer's ruling: terrain first, then one textured water plane over it): the land
## under the sea as real ground, as the Blender plate builds it (city_world_a2.sea_depth / isl_bed): a `seabed_shelf_bu`
## shelf at the shore falling on a smoothstep over `seabed_reach` lots of the shore field to `seabed_max_bu`, broken by the
## terrain's broad noise (`seabed_noise_k`); the bay islands (CityWater.islands_of) stand on shoal banks and rise out of it
## as hills. Sand to rock over `seabed_tone` lots from the land, the islands sand / meadow / forest by height. One indexed grid every `seabed_step` lots over the wet cells; the
## same bed as a depth texture (`depth_image`) for the water plane. Pure.

const SEED_TONE := 7780
const COAST_KERNEL: Array[int] = [1, 4, 6, 4, 1]


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
			var z := bed_z(cfg, terrain, at, dc, wt, islands)
			var k := cj * nx + ci
			touch[k] = 1 if wt else 0
			verts[k] = CityIsoCamera.lot_to_world(cfg, at, z)
			var tone := lerpf(0.85, 1.15, CityMeshKit.hash01(SEED_TONE, li, lj))
			var c: Color
			if z > 0.0:
				var f := clampf(z / maxf(cfg.island_h_bu, 0.001), 0.0, 1.0)
				c = (tc["beach"] as Color).lerp(tc["meadow"], smoothstep(0.0, 0.35, f)).lerp(tc["forest"], smoothstep(0.4, 0.9, f))
			else:
				c = cfg.seabed_sand.lerp(cfg.seabed_deep, clampf((dc - cfg.seabed_tone.x) / (cfg.seabed_tone.y - cfg.seabed_tone.x), 0.0, 1.0))
			cols[k] = Color(c.r * tone, c.g * tone, c.b * tone)
	var idx := PackedInt32Array()
	# Godot's front faces wind clockwise seen from the front: the up-facing order is the one whose cross product points down.
	var down := (verts[1] - verts[0]).cross(verts[nx] - verts[0]).y < 0.0
	for cj in ny - 1:
		for ci in nx - 1:
			var a := cj * nx + ci
			var b := a + 1
			var c2 := a + nx + 1
			var e := a + nx
			if touch[a] == 0 and touch[b] == 0 and touch[c2] == 0 and touch[e] == 0:
				continue
			if down:
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


## The bed's height (BU, below 0 under water) at lot point `at`: shore field `dc` lots, `wt` when it touches water.
static func bed_z(cfg: CityConfig, terrain: CityA2Terrain, at: Vector2, dc: float, wt: bool,
		islands: Array[Dictionary]) -> float:
	# The plate's sea_depth: a shelf at the shore, falling on a smoothstep over seabed_reach lots to seabed_max_bu.
	var t := smoothstep(cfg.seabed_reach.x, cfg.seabed_reach.y, dc)
	var z := -(cfg.seabed_shelf_bu + (cfg.seabed_max_bu - cfg.seabed_shelf_bu) * t) \
			* (1.0 + cfg.seabed_noise_k * (terrain.noise_at(at.x, at.y) * 2.0 - 1.0))
	if not wt:
		# Designer 2026-10-20 (the stepped coast): a dry vertex sinks `seabed_under_bu` below the ground (drawn 0.02 under
		# its heights), so the bed's 2-lot triangles never poke through the low shore as dark wedges.
		z = minf(terrain.height_at(at.x, at.y), 0.0) - cfg.seabed_under_bu
	for it: Dictionary in islands:
		# The plate's isl_bed: each island stands on a shoal bank, not on a pillar.
		var r := float(it["r"])
		var rq := CityWater.island_rho(cfg, it, at)
		z = maxf(z, -cfg.island_shoal_bu - maxf(0.0, (rq - cfg.island_shoal_k) * r) * cfg.lot_bu * cfg.island_shoal_slope)
		var rho := rq / cfg.island_spread
		if rho < 1.0:
			z = lerpf(z, cfg.island_h_bu, pow(1.0 - rho * rho, 1.5))
	return z


## The water's depth over `r` (a texel a lot, BU below sea level, 0 above it) for the water plane: the same bed as `mesh`,
## so the plane's thickness follows the ground under it without the depth buffer.
## `flood` (lots): the drowned quarter's polygon, baked as water `whole_drowned_depth_bu` deep over its ground, so the
## one plane covers it like the sea.
static func depth_image(cfg: CityConfig, terrain: CityA2Terrain, r: Rect2i, wet: PackedByteArray, d: PackedFloat32Array,
		islands: Array[Dictionary], flood: PackedVector2Array = PackedVector2Array(), ras: CityA2Raster = null) -> Image:
	var w := r.size.x
	var h := r.size.y
	var img := Image.create_empty(w, h, false, Image.FORMAT_RGBF)
	var dep := PackedFloat32Array()
	dep.resize(w * h)
	var sea := PackedFloat32Array()
	sea.resize(w * h)
	var shore := PackedFloat32Array()
	shore.resize(w * h)
	for j in h:
		for i in w:
			var at := Vector2(r.position.x + i + 0.5, r.position.y + j + 0.5)
			var wt := wet[j * w + i] != 0
			# Dry land below sea level stays dry: the plane draws nothing where the bake holds no depth.
			var z := bed_z(cfg, terrain, at, d[j * w + i], wt, islands) if wt else 0.0
			dep[j * w + i] = maxf(-z, 0.0)
			sea[j * w + i] = 1.0 if z < 0.0 else 0.0
			shore[j * w + i] = d[j * w + i]
			if not wt and flood.size() >= 3 and Geometry2D.is_point_in_polygon(at, flood):
				dep[j * w + i] = cfg.whole_drowned_depth_bu
				sea[j * w + i] = 1.0
				shore[j * w + i] = maxf(d[j * w + i], cfg.whole_drowned_shore_lots)
			# LOOK L5 (designer 2026-10-20): a river's texel carries its shore distance negated (-(d + 1)), so the plane
			# keeps the sea's beach strip off the rivers.
			if wt and ras != null and ras.is_river(r.position.x + i, r.position.y + j):
				shore[j * w + i] = -(d[j * w + i] + 1.0)
	# Blue: the water mask blurred (binomial 5 x 5), so the plane's edge cuts a smooth coast across the lot staircase.
	for j in h:
		for i in w:
			var s := 0.0
			var n := 0.0
			for oy in range(-2, 3):
				for ox in range(-2, 3):
					var ii := clampi(i + ox, 0, w - 1)
					var jj := clampi(j + oy, 0, h - 1)
					var k := float(COAST_KERNEL[ox + 2] * COAST_KERNEL[oy + 2])
					s += sea[jj * w + ii] * k
					n += k
			img.set_pixel(i, j, Color(dep[j * w + i], shore[j * w + i], s / n))
	return img


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
