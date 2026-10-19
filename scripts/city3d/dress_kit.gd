class_name DressKit
extends RefCounted
## NA-24: primitives of the street dressing: the neon / plume materials, the unit meshes, plan -> world piece transforms and the
## chunked MultiMesh groups with their config `visibility_range` (`DressReveal`). Plan coordinates are (x, y, height); world is
## (x, height, -y), as everywhere in the netrun view.

const NEON := preload("res://shaders/city/dress_neon.gdshader")
const SOLID := preload("res://shaders/city/dress_solid.gdshader")
const SIGN := preload("res://shaders/city/dress_sign.gdshader")
const PLUME := preload("res://shaders/city/dress_plume.gdshader")
const SHAPE_SOLID := 0
const SHAPE_DISC := 1
const SHAPE_FLICKER := 2
## A sign piece (the `dress_sign` material; NA-24c).
const SHAPE_SIGN := 3

static var _box: BoxMesh = null
static var _quad: QuadMesh = null


## Plan vector (x, y) as a world direction.
static func dir_w(v: Array) -> Vector3:
	return Vector3(float(v[0]), 0.0, -float(v[1]))


## Plan point (x, y, z) as a world position.
static func pos_w(p: Array) -> Vector3:
	return Vector3(float(p[0]), float(p[2]), -float(p[1]))


## A neon material of `shape` with emission `emit`.
static func neon_material(shape: int, emit: float) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SOLID if shape == SHAPE_SOLID else NEON
	m.set_shader_parameter(&"shape", shape)
	m.set_shader_parameter(&"emit", emit)
	m.set_shader_parameter(&"loop_s", float(CityShaderConfigData.shipped().streak["loop_s"]))
	var b: Array = DressingConfigData.shipped().sign["flicker_bursts"]
	m.set_shader_parameter(&"bursts", Vector2(float(b[0]), float(b[1])))
	if shape == SHAPE_FLICKER:
		_sign_params(m)
	return m


## The opaque sign panel material (`dress_sign`, NA-24c) with the sign numbers from the config.
static func sign_material() -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SIGN
	_sign_params(m)
	return m


static func _sign_params(m: ShaderMaterial) -> void:
	var sg: Dictionary = DressingConfigData.shipped().sign
	for k: String in ["panel_level", "core_level", "core_max", "frame_w", "stroke_h", "fill", "cell_gap", "bright_var", "side_dim", "core_px"]:
		m.set_shader_parameter(StringName(k), float(sg[k]))
	var c: Array = sg["cell"]
	m.set_shader_parameter(&"cell", Vector2(float(c[0]), float(c[1])))


## `c` packed 0xRRGGBB as an exact float (24 bits), for `item`'s `sec`.
static func pack_rgb(c: Color) -> float:
	return float((int(round(c.r * 255.0)) << 16) | (int(round(c.g * 255.0)) << 8) | int(round(c.b * 255.0)))


## Tells a sign tier material which tier covers it (`DressReveal.range_of` of `cover_group`), so the far block fades out as the
## covering tier fades in and the two never sum.
static func set_yield(m: ShaderMaterial, cover_group: String) -> void:
	var r: Dictionary = DressReveal.range_of(cover_group)
	m.set_shader_parameter(&"yield_range", Vector2(float(r["end"]), float(r["near"])))


## The plume material from the config.
static func plume_material() -> ShaderMaterial:
	var p: Dictionary = DressingConfigData.shipped().plume
	var m := ShaderMaterial.new()
	m.shader = PLUME
	for k: String in ["loop_s", "rise", "size0", "size1", "alpha", "emit"]:
		m.set_shader_parameter(StringName(k), float(p[k]))
	var c: Array = p["col"]
	m.set_shader_parameter(&"col", Vector3(float(c[0]), float(c[1]), float(c[2])))
	return m


## The unit box mesh (size 1).
static func box_mesh() -> BoxMesh:
	if _box == null:
		_box = BoxMesh.new()
		_box.size = Vector3.ONE
	return _box


## The unit quad mesh (size 1, facing +Z, UV 0..1).
static func quad_mesh() -> QuadMesh:
	if _quad == null:
		_quad = QuadMesh.new()
		_quad.size = Vector2.ONE
	return _quad


## `puffs` camera-facing unit quads in one mesh; vertex colour red = the puff's phase `i / puffs`; UV 0..1 over the quad.
static func plume_mesh(puffs: int) -> ArrayMesh:
	var verts := PackedVector3Array()
	var uvs := PackedVector2Array()
	var cols := PackedColorArray()
	var idx := PackedInt32Array()
	for i in puffs:
		var base := verts.size()
		var c := Color(float(i) / float(puffs), 0.0, 0.0, 1.0)
		for q: Vector2 in [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)]:
			verts.append(Vector3(q.x - 0.5, q.y - 0.5, 0.0))
			uvs.append(q)
			cols.append(c)
		idx.append_array(PackedInt32Array([base, base + 1, base + 2, base, base + 2, base + 3]))
	var arr: Array = []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = verts
	arr[Mesh.ARRAY_TEX_UV] = uvs
	arr[Mesh.ARRAY_COLOR] = cols
	arr[Mesh.ARRAY_INDEX] = idx
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	mesh.custom_aabb = AABB(Vector3(-8, 0, -8), Vector3(16, 24, 16))
	return mesh


## The transform of a box piece standing at plan point `p` (x, y, z = its bottom): `along` BU along the unit plan direction `eu`,
## `out` BU along the plan direction `ev`, `up` BU high; `a0` / `o0` offsets of its near corner from `p`.
static func piece(p: Array, eu: Array, ev: Array, a0: float, a1: float, o0: float, o1: float, z0: float, z1: float) -> Transform3D:
	var ux := dir_w(eu)
	var vx := dir_w(ev)
	var c: Vector3 = pos_w(p) + ux * ((a0 + a1) * 0.5) + vx * ((o0 + o1) * 0.5) + Vector3.UP * ((z0 + z1) * 0.5)
	return Transform3D(Basis(ux * absf(a1 - a0), Vector3.UP * absf(z1 - z0), vx * absf(o1 - o0)), c)


## A vertical soft disc (a quad) of radius `r` centred at plan point `p` (x, y, z = its centre), facing plan direction `ev`.
static func wall_disc(p: Array, eu: Array, ev: Array, r: float) -> Transform3D:
	return Transform3D(Basis(dir_w(eu) * 2.0 * r, Vector3.UP * 2.0 * r, dir_w(ev)), pos_w(p))


## A flat soft disc of radius `r` on the ground at plan point `p` (z = its height).
static func ground_disc(p: Array, r: float) -> Transform3D:
	return Transform3D(Basis(Vector3.RIGHT * 2.0 * r, Vector3(0, 0, -1) * 2.0 * r, Vector3.UP), pos_w(p))


## One instance of a group: transform, colour, and `custom` (seed, phase, gain).
static func item(xf: Transform3D, col: Color, seed01: float = 0.0, phase: float = 0.0, gain: float = 1.0, sec: float = 0.0) -> Dictionary:
	return {"xf": xf, "col": col, "custom": Color(seed01, phase, gain, sec)}


## The chunked MultiMesh nodes of reveal group `group` (one per `caps.chunk_bu` world cell, sorted by cell), each with the group's
## `visibility_range` from the config. `items` come from `item`; `mat` is shared by the chunks.
static func group_nodes(group: String, mesh: Mesh, mat: Material, items: Array) -> Array[MultiMeshInstance3D]:
	var cell: float = float(DressingConfigData.shipped().caps["chunk_bu"])
	var by_cell: Dictionary = {}
	for it: Dictionary in items:
		var o: Vector3 = (it["xf"] as Transform3D).origin
		var k := Vector2i(floori(o.x / cell), floori(o.z / cell))
		if not by_cell.has(k):
			by_cell[k] = []
		(by_cell[k] as Array).append(it)
	var keys: Array = by_cell.keys()
	IdSort.sort_ids(keys)
	var out: Array[MultiMeshInstance3D] = []
	for k: Vector2i in keys:
		var list: Array = by_cell[k]
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.use_custom_data = true
		mm.mesh = mesh
		mm.instance_count = list.size()
		for i in list.size():
			mm.set_instance_transform(i, list[i]["xf"])
			mm.set_instance_color(i, list[i]["col"])
			mm.set_instance_custom_data(i, list[i]["custom"])
		var mi := MultiMeshInstance3D.new()
		mi.name = "%s_%d_%d" % [group, k.x, k.y]
		mi.multimesh = mm
		mi.material_override = mat
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		DressReveal.apply(mi, group)
		out.append(mi)
	return out


## `a` lightened the way the hero panels are (`0.6 c + 0.4`, spec 9.1).
static func lighten(c: Color) -> Color:
	return Color(0.6 * c.r + 0.4, 0.6 * c.g + 0.4, 0.6 * c.b + 0.4, 1.0)
