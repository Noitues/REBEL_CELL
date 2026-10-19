class_name StreetR2Props
extends RefCounted
## Street r2 renderer, prop half: places the street kit glb (assets/street_kit, wall plane z = 0, +Z out, metres = BU) as MultiMeshes, one per
## kit file, from the plan's facade props, kerb lamps and crowns. Wall props stand on the wall frame (glb X along the wall, Y up, Z out).

const KIT_DIR := "res://assets/street_kit/"

var _mats: StreetR2Materials
var _meshes: Dictionary = {}
## kit file -> Array of [Transform3D, Color tint (a = 0 for none)].
var _inst: Dictionary = {}


func _init(mats: StreetR2Materials) -> void:
	_mats = mats


## The mesh of kit file `file` (no extension) with the slot materials, loaded once.
func mesh_of(file: String) -> Mesh:
	if not _meshes.has(file):
		var ps := load(KIT_DIR + file + ".glb") as PackedScene
		var inst := ps.instantiate()
		var src: Mesh = null
		for c in inst.find_children("*", "MeshInstance3D", true, false):
			src = (c as MeshInstance3D).mesh
			break
		var m: Mesh = src.duplicate()
		for s in m.get_surface_count():
			var slot := String(src.surface_get_material(s).resource_name) if src.surface_get_material(s) != null else ""
			m.surface_set_material(s, _mats.for_slot(slot))
		inst.free()
		_meshes[file] = m
	return _meshes[file]


## The reference size (the glb's bounding box) of kit file `file`.
func aabb_of(file: String) -> AABB:
	return mesh_of(file).get_aabb()


## The wall frame basis of a face on plan axis `axis` whose out direction is `out` (+1 / -1 along the other axis), with `scale` (x, y, z).
static func wall_basis(axis: int, out: float, scale: Vector3) -> Basis:
	var out_w := Vector3(0, 0, -out) if axis == 0 else Vector3(out, 0, 0)
	var x_w := Vector3.UP.cross(out_w)
	return Basis(x_w * scale.x, Vector3.UP * scale.y, out_w * scale.z)


## Queues one instance of `file` at transform `t`; `tint` (alpha 1) recolours the emissive slots, alpha 0 keeps the authored colour.
func add(file: String, t: Transform3D, tint: Color) -> void:
	if not _inst.has(file):
		_inst[file] = []
	(_inst[file] as Array).append([t, tint])


## Queues a facade prop of the plan (`kind`, `axis`, `out`, `face`, `u0` `u1` `z0` `z1`, `depth`, `col`), the face plane pushed by `push`.
func add_facade_prop(p: Dictionary, push: float) -> String:
	var kits: Dictionary = StreetR2RenderConfigData.shipped().props["kits"]
	var kind := String(p["kind"])
	var axis := int(p["axis"])
	var out := float(p["out"])
	var w := float(p["u1"]) - float(p["u0"])
	var h := float(p["z1"]) - float(p["z0"])
	var uc := (float(p["u0"]) + float(p["u1"])) * 0.5
	var plane := float(p["face"]) + out * push
	var file := String(kits.get(kind, ""))
	var tint := Color(float(p["col"][0]), float(p["col"][1]), float(p["col"][2]), 1.0)
	var sc := Vector3.ONE
	var y := float(p["z0"])
	match kind:
		"ac":
			file = String(kits["ac"])
			var bb := aabb_of(file)
			sc = Vector3(w / bb.size.x, h / bb.size.y, float(p["depth"]) / bb.size.z)
			tint.a = 0.0
		"pipe":
			var bb := aabb_of(file)
			sc = Vector3(1.0, h / bb.size.y, 1.0)
			tint.a = 0.0
		"awning":
			var bb := aabb_of(file)
			sc = Vector3(w / bb.size.x, 1.0, float(p["depth"]) / bb.size.z)
			y = float(p["z1"])
		"small_sign":
			if bool(p.get("blade", false)):
				file = String(kits["small_blade"])
			var bb := aabb_of(file)
			sc = Vector3(w / bb.size.x, h / bb.size.y, 1.0)
		"lit_room":
			var bb := aabb_of(file)
			sc = Vector3(w / bb.size.x, h / bb.size.y, 1.0)
		_:
			return ""
	var pos := _plan_to_world(axis, uc, plane, y)
	add(file, Transform3D(wall_basis(axis, out, sc), pos), tint)
	return file


## Queues a kerb lamp of the plan (`pos` [x, y, 0], `side`, `col`) with its arm toward the street line `line` of axis `axis`.
func add_lamp(l: Dictionary, axis: int, line: float, post_h: float) -> void:
	var file := String(StreetR2RenderConfigData.shipped().props["lamp"])
	var pos: Array = l["pos"]
	var toward := Vector3.ZERO
	if axis == 0:
		toward = Vector3(0, 0, -1.0 if line > float(pos[1]) else 1.0)
	else:
		toward = Vector3(1.0 if line > float(pos[0]) else -1.0, 0, 0)
	var yaw := atan2(toward.x, toward.z)
	var k := post_h / float(StreetR2RenderConfigData.shipped().lamps["pole_scale_from"])
	var b := Basis(Vector3.UP, yaw) * Basis.from_scale(Vector3(k, k, k))
	var tint := Color(float(l["col"][0]), float(l["col"][1]), float(l["col"][2]), 1.0)
	add(file, Transform3D(b, Vector3(float(pos[0]), float(pos[2]), -float(pos[1]))), tint)


## World point of a wall position: `u` along `axis`, `plane` across it, height `z`.
static func _plan_to_world(axis: int, u: float, plane: float, z: float) -> Vector3:
	return Vector3(u, z, -plane) if axis == 0 else Vector3(plane, z, -u)


## The MultiMeshInstance3D nodes of everything queued, in kit-file text order (a Dictionary key order is insertion order, so sort).
func flush(parent: Node3D) -> Dictionary:
	var counts := {}
	var files: Array = _inst.keys()
	IdSort.sort_ids(files)
	for file: String in files:
		var list: Array = _inst[file]
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_custom_data = true
		mm.mesh = mesh_of(file)
		mm.instance_count = list.size()
		for i in list.size():
			mm.set_instance_transform(i, list[i][0])
			mm.set_instance_custom_data(i, list[i][1])
		var mi := MultiMeshInstance3D.new()
		mi.name = "kit_" + file
		mi.multimesh = mm
		parent.add_child(mi)
		counts[file] = list.size()
	return counts
