class_name StreetR2SignBoards
extends RefCounted
## Street r2 renderer, sign half: one textured quad per planned sign on its facade plane (`d`, pushed by the building's `push`), a dark frame
## of four beams, and the draw list rasterized in a SubViewport (`StreetR2SignCanvas`, UPDATE_ONCE).

var _root: Node3D
var _mats: StreetR2Materials
var _fonts: Dictionary
## Sign id -> `{w, h}` of its texture, for tests.
var textures: Dictionary = {}


func _init(root: Node3D, mats: StreetR2Materials, fonts: Dictionary) -> void:
	_root = root
	_mats = mats
	_fonts = fonts


## The four plan corners of sign `s` (BL, BR, TR, TL as the street sees them) on plane `d`.
static func corners(s: Dictionary, d: float) -> Array:
	var u0 := float(s["u0"])
	var u1 := float(s["u1"])
	var z0 := float(s["z0"])
	var z1 := float(s["z1"])
	var out := float(s["out"])
	var flip := (int(s["axis"]) == 0 and out > 0.0) or (int(s["axis"]) == 1 and out < 0.0)
	if flip:
		var t := u0
		u0 = u1
		u1 = t
	var q: Array = []
	for uz: Array in [[u0, z0], [u1, z0], [u1, z1], [u0, z1]]:
		q.append([float(uz[0]), d, float(uz[1])] if int(s["axis"]) == 0 else [d, float(uz[0]), float(uz[1])])
	return q


## Adds sign `s` with draw list `spec` as a child of the root; `push` is the facade push of its building. Returns the pixel size.
func add(s: Dictionary, spec: Dictionary, push: float) -> Vector2i:
	var cfg: StreetR2RenderConfigData = StreetR2RenderConfigData.shipped()
	var d := float(s["d"]) + float(s["out"]) * push
	var q := corners(s, d)
	var aspect := (float(s["u1"]) - float(s["u0"])) / maxf(0.05, float(s["z1"]) - float(s["z0"]))
	var px := StreetR2SignCanvas.size_of(spec, aspect)
	var vp := SubViewport.new()
	vp.name = "tex_" + String(s["id"])
	vp.size = px
	vp.disable_3d = true
	vp.transparent_bg = false
	vp.render_target_update_mode = SubViewport.UPDATE_ONCE
	var canvas := StreetR2SignCanvas.new()
	canvas.setup(spec, _fonts, px)
	vp.add_child(canvas)
	_root.add_child(vp)
	var verts := PackedVector3Array()
	for p: Array in q:
		verts.append(StreetR2Geometry.world(p))
	var out := float(s["out"])
	var out_w := Vector3(0, 0, -out) if int(s["axis"]) == 0 else Vector3(out, 0, 0)
	var arr: Array = []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = verts
	arr[Mesh.ARRAY_NORMAL] = PackedVector3Array([out_w, out_w, out_w, out_w])
	arr[Mesh.ARRAY_TEX_UV] = PackedVector2Array([Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)])
	arr[Mesh.ARRAY_INDEX] = PackedInt32Array([0, 1, 2, 0, 2, 3])
	var m := ArrayMesh.new()
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	var emit := float(s["emit"]) * float(cfg.signs["emit_k"])
	m.surface_set_material(0, _mats.sign_board(vp.get_texture(), emit))
	var mi := MeshInstance3D.new()
	mi.name = "sign_" + String(s["id"])
	mi.mesh = m
	_root.add_child(mi)
	textures[String(s["id"])] = px
	return px


## The frame of sign `s` (four beams round the board, a little in front of it) as face records for the `solid` material.
static func frame_faces(s: Dictionary, push: float) -> Array:
	var cfg: Dictionary = StreetR2RenderConfigData.shipped().signs
	var fw := float(cfg["frame_w"])
	var off := float(cfg["frame_off"])
	var out := float(s["out"])
	var q := corners(s, float(s["d"]) + out * (push + off))
	var col: Array = cfg["frame_col"]
	var faces: Array = []
	for k in 4:
		var a: Array = q[k]
		var b: Array = q[(k + 1) % 4]
		faces.append_array(StreetR2Geometry.beam_faces(a, b, fw, col))
	return faces
