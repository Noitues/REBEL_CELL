class_name NetrunFgrid
extends RefCounted
## AAA-2 facet grit as geometry (A-022 / MATERIAL_SPEC 3): the walls of a street building are a grid of flat-shaded triangles, not a
## shader trick. Per wall: `nu` x `nv` cells of `aaa.grit.cell` BU (nu = clamp(round(width / cell), nu_min, nu_max), nv likewise from
## the height), the interior points jittered by `aaa.grit.jitter` of a cell along the wall and `aaa.grit.normal` BU along its normal,
## the diagonal alternating by (i + j) parity. Walls that are not long and tall enough (`min_len`, `min_h`) are two triangles. The mesh
## is in the unit space of the building family (the same instance transform and the same UV / UV2 / CUSTOM0 contract as
## `CityMeshKit.unit_prism`, so `city_building` reads it unchanged) but sized by the building's real BU dimensions. Deterministic: hashes
## of the building's seed (its prism key) and the wall / cell indices, no RNG.


## The unit-space mesh of the building `poly` (world X/Z corners), base `y0`, height `h`, seed `seed_i`.
static func mesh_of(poly: PackedVector2Array, y0: float, h: float, seed_i: int) -> ArrayMesh:
	var g: Dictionary = CityShaderConfigData.shipped().aaa["grit"]
	var cell: float = float(g["cell"])
	var jit: float = float(g["jitter"])
	var njit: float = float(g["normal"])
	var nu_r: Array = g["nu"]
	var nv_r: Array = g["nv"]
	var sides := poly.size()
	var basis: Basis = CityMeshKit.instance_transform(poly, y0, h).basis
	var fp := CityMeshKit.unit_footprint(sides)
	var verts := PackedVector3Array()
	var uvs := PackedVector2Array()
	var uv2s := PackedVector2Array()
	var cust := PackedFloat32Array()
	var tri := 0
	for k in sides:
		var a := fp[k]
		var b := fp[(k + 1) % sides]
		var e := b - a
		var nrm := Vector2(e.y, -e.x).normalized()
		if nrm.dot((a + b) * 0.5) < 0.0:
			nrm = -nrm
		var wall_len: float = (basis * Vector3(e.x, 0.0, e.y)).length()
		var n_scale: float = maxf((basis * Vector3(nrm.x, 0.0, nrm.y)).length(), 0.0001)
		var fine: bool = wall_len > float(g["min_len"]) and h > float(g["min_h"])
		var cols: int = clampi(roundi(wall_len / cell), int(nu_r[0]), int(nu_r[1])) if fine else 1
		var rows: int = clampi(roundi(h / cell), int(nv_r[0]), int(nv_r[1])) if fine else 1
		var grid: Array[PackedVector3Array] = []
		for j in rows + 1:
			var row := PackedVector3Array()
			for i in cols + 1:
				var p := a.lerp(b, float(i) / float(cols))
				var y := float(j) / float(rows)
				if i > 0 and i < cols and j > 0 and j < rows:
					var ju := (CityMeshKit.hash01(k * 131 + i, j, seed_i) - 0.5) * 2.0 * jit / float(cols)
					var jv := (CityMeshKit.hash01(k * 131 + i, j, seed_i + 1) - 0.5) * 2.0 * jit / float(rows)
					# Along the wall by a share of a cell, up by a share of a cell, out by up to `normal` BU (unit space: / the wall's scale).
					var jn := (CityMeshKit.hash01(k * 131 + i, j, seed_i + 2) - 0.5) * 2.0 * njit / n_scale
					p += e * ju + nrm * jn
					y += jv
				row.append(Vector3(p.x, y, p.y))
			grid.append(row)
		for j in rows:
			for i in cols:
				var p00 := grid[j][i]
				var p10 := grid[j][i + 1]
				var p11 := grid[j + 1][i + 1]
				var p01 := grid[j + 1][i]
				var quads: Array = [[p00, p11, p10], [p00, p01, p11]] if (i + j) % 2 == 0 else [[p00, p01, p10], [p10, p01, p11]]
				for t3: Array in quads:
					var tone := CityMeshKit.hash01(tri, seed_i, 7)
					tri += 1
					for q: Vector3 in t3:
						verts.append(q)
						uvs.append(a)
						uv2s.append(e)
						cust.append_array([tone, 0.0, 0.0, 0.0])
	# Roof: the fan of the family prism.
	var top_c := Vector3(0.0, 1.0, 0.0)
	for k in sides:
		var a := fp[k]
		var b := fp[(k + 1) % sides]
		var tone := CityMeshKit.hash01(tri, seed_i, 9)
		tri += 1
		for q: Array in [[top_c, 0.0], [Vector3(b.x, 1.0, b.y), 1.0], [Vector3(a.x, 1.0, a.y), 1.0]]:
			verts.append(q[0])
			uvs.append(Vector2.ZERO)
			uv2s.append(Vector2.ZERO)
			cust.append_array([tone, CityMeshKit.ROOF, float(q[1]), 0.0])
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = verts
	arr[Mesh.ARRAY_TEX_UV] = uvs
	arr[Mesh.ARRAY_TEX_UV2] = uv2s
	arr[Mesh.ARRAY_CUSTOM0] = cust
	var normals := PackedVector3Array()
	normals.resize(verts.size())
	normals.fill(Vector3.UP)
	arr[Mesh.ARRAY_NORMAL] = normals
	var m := ArrayMesh.new()
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr, [], {}, Mesh.ARRAY_CUSTOM_RGBA_FLOAT << Mesh.ARRAY_FORMAT_CUSTOM0_SHIFT)
	return m


## The triangle count of that mesh without building it (tests, the perf report).
static func triangle_count(poly: PackedVector2Array, y0: float, h: float) -> int:
	var g: Dictionary = CityShaderConfigData.shipped().aaa["grit"]
	var sides := poly.size()
	var basis: Basis = CityMeshKit.instance_transform(poly, y0, h).basis
	var fp := CityMeshKit.unit_footprint(sides)
	var n := sides
	for k in sides:
		var e := fp[(k + 1) % sides] - fp[k]
		var wall_len: float = (basis * Vector3(e.x, 0.0, e.y)).length()
		var fine: bool = wall_len > float(g["min_len"]) and h > float(g["min_h"])
		var cols: int = clampi(roundi(wall_len / float(g["cell"])), int(g["nu"][0]), int(g["nu"][1])) if fine else 1
		var rows: int = clampi(roundi(h / float(g["cell"])), int(g["nv"][0]), int(g["nv"][1])) if fine else 1
		n += 2 * cols * rows
	return n
