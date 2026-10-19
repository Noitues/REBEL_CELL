class_name IdCapture
extends RefCounted
## NA-ID: the general Godot id capture (PIPELINE_SPEC 12.0). One `write()` call stores `beauty.png`, `id.png`, `depth.png` and
## `capture.json` for the current camera of a CityView3D (street rig, HQ compound page, landmark or city frame). Views are read, never
## changed for good: the id pass swaps materials, hides the ground / network / sky and the fog, and every swap is restored; no
## RNG, no save, no world state is touched. Classes and the byte rules: `IdCaptureClasses`, NA_ID_CLASSES.md.

const FLAT := preload("res://shaders/city/id_flat.gdshader")
const DEPTH := preload("res://shaders/city/route_depth.gdshader")
## Frames the renderer gets after a pass change before the pixels are read.
const SETTLE_FRAMES := 3

var view: CityView3D = null
var rig: RouteRig = null
var _tree: SceneTree = null
var _mats: Dictionary = {}  # class -> ShaderMaterial
var _saved: Array = []  # [mesh, previous material_override, previous visible]


## `p_view`: the CityView3D to read; `p_rig`: its RouteRig when the frame is the street netrun (its rooms, fog and clock join the pass).
func _init(p_tree: SceneTree, p_view: CityView3D, p_rig: RouteRig = null) -> void:
	_tree = p_tree
	view = p_view
	rig = p_rig


## Writes the capture into `dir` (made if missing). `meta` keys: `kind`, `view`, `look`, `look_blend`, `corp`, `exempt`, `run`,
## `layout_seed` (decimal string; default the city seed), `camera` (a pose dictionary; default read from the view's camera) and
## `anim_t` (the clock the frame is frozen at, then restored; omitted: frozen where it stands). Returns {"ok", "counts" (id.png
## pixels per class), "beauty", "id", "depth"} (the images).
func write(dir: String, meta: Dictionary) -> Dictionary:
	DirAccess.make_dir_recursive_absolute(dir)
	var anim := _freeze(meta)
	var beauty := view.get_texture().get_image()
	beauty.save_png("%s/beauty.png" % dir)
	_begin_id()
	await _frames()
	var idimg := view.get_texture().get_image()
	idimg.save_png("%s/id.png" % dir)
	# depth.png: 16-bit linear camera depth, BU x 100, nearest-sampled, no UI.
	var quad: MeshInstance3D = null
	if rig != null:
		rig.set_depth_pass(true)
	else:
		quad = make_depth_quad()
		view.camera.add_child(quad)
	await _frames()
	var dimg := view.get_texture().get_image()
	Png16.save_gray16("%s/depth.png" % dir, dimg.get_width(), dimg.get_height(), Png16.samples_from_rg(dimg))
	if rig != null:
		rig.set_depth_pass(false)
	else:
		quad.queue_free()
	_end_id()
	_thaw(anim)
	var cap := capture_dict(view, beauty.get_width(), beauty.get_height(), meta, float(anim["t"]))
	var f := FileAccess.open("%s/capture.json" % dir, FileAccess.WRITE)
	if f == null:
		return {"ok": false}
	f.store_string(IdCaptureClasses.capture_json(cap))
	f.close()
	return {"ok": true, "counts": IdCaptureClasses.count_classes(idimg), "beauty": beauty, "id": idimg, "depth": dimg}


## The capture.json dictionary (before canonical rounding) for a `w` x `h` frame.
static func capture_dict(p_view: CityView3D, w: int, h: int, meta: Dictionary, anim_t: float) -> Dictionary:
	var cap: Dictionary = {"version": 1, "resolution": [w, h], "anim_t": anim_t,
		"layout_seed": String(meta.get("layout_seed", str(CityView3D.CONFIG.city_seed))), "run": String(meta.get("run", "")),
		"camera": meta["camera"] if meta.has("camera") else camera_block(p_view.camera)}
	for k: String in ["kind", "view", "look", "look_blend", "corp", "exempt"]:
		if meta.has(k):
			cap[k] = meta[k]
	return cap


## A pose dictionary of `cam` (position, rotation in degrees, projection, size / fov, near, far).
static func camera_block(cam: Camera3D) -> Dictionary:
	var t := cam.global_transform
	var ortho := cam.projection == Camera3D.PROJECTION_ORTHOGONAL
	var block: Dictionary = {"position": t.origin, "rotation_deg": t.basis.get_euler() * (180.0 / PI),
		"projection": "orthogonal" if ortho else "perspective", "near": cam.near, "far": cam.far}
	block["size" if ortho else "fov"] = cam.size if ortho else cam.fov
	return block


## The depth pass quad (see route_depth.gdshader); add it under the camera, free it after the capture.
static func make_depth_quad() -> MeshInstance3D:
	var q := QuadMesh.new()
	q.size = Vector2(2, 2)
	var mi := MeshInstance3D.new()
	mi.name = "DepthPass"
	mi.mesh = q
	mi.extra_cull_margin = 16384.0
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var m := ShaderMaterial.new()
	m.shader = DEPTH
	mi.material_override = m
	return mi


## The id pass on (for tests and callers that read the pixels themselves): flat class colours, black sky, no fog. `end_id` undoes it.
func begin_id() -> void:
	_begin_id()


## Undoes `begin_id`.
func end_id() -> void:
	_end_id()


## The class of every mesh the pass overrides: {GeometryInstance3D: class} (landmark layer meshes 1; `id_link` groups 3; `id_mover` groups 6,
## a mover under a landmark staying 6; with no rig every other visible mesh outside the buildings is class 2).
func classify() -> Dictionary:
	var out: Dictionary = {}
	var lm := view.layer(&"landmarks")
	if lm != null:
		for m in _meshes(lm):
			out[m] = IdCaptureClasses.LANDMARK
	for pair: Array in [[IdCaptureClasses.GROUP_LINK, IdCaptureClasses.LINK], [IdCaptureClasses.GROUP_MOVER, IdCaptureClasses.MOVER]]:
		for n in _tree.get_nodes_in_group(pair[0]):
			if view.is_ancestor_of(n):
				for m in _meshes(n):
					out[m] = pair[1]
	if rig == null:
		# Everything else still visible (roof props, dressing, heat and fx) is city; the buildings carry their own id_mode and keep it.
		for g in view.find_children("*", "GeometryInstance3D", true, false):
			var gi := g as GeometryInstance3D
			if out.has(gi) or view.camera.is_ancestor_of(gi) or not gi.is_visible_in_tree() or gi.material_override == view.building_material():
				continue
			out[gi] = IdCaptureClasses.CITY
	return out


func _meshes(root: Node) -> Array[GeometryInstance3D]:
	var out: Array[GeometryInstance3D] = []
	if root is GeometryInstance3D:
		out.append(root as GeometryInstance3D)
	for c in root.find_children("*", "GeometryInstance3D", true, false):
		out.append(c as GeometryInstance3D)
	return out


func _is_beam(g: GeometryInstance3D) -> bool:
	var mi := g as MeshInstance3D
	if mi == null or mi.mesh == null:
		return false
	for i in mi.mesh.get_surface_count():
		var m := mi.get_active_material(i)
		if m != null and m.resource_name == LandmarkMaterials.BEAM:
			return true
	return false


func _class_material(cls: int) -> ShaderMaterial:
	if not _mats.has(cls):
		var m := ShaderMaterial.new()
		m.shader = FLAT
		m.set_shader_parameter(&"id_rgb", Vector3(cls, 0, 0))
		_mats[cls] = m
	return _mats[cls]


func _begin_id() -> void:
	if rig != null:
		rig.set_id_pass(true)
	else:
		view.set_id_pass(true, true)
	var cls := classify()
	for mi: GeometryInstance3D in cls:
		_saved.append([mi, mi.material_override, mi.visible])
		if _is_beam(mi):
			mi.visible = false  # a light cone is not geometry: it never carries a class
		else:
			mi.material_override = _class_material(int(cls[mi]))


func _end_id() -> void:
	for s: Array in _saved:
		var mi := s[0] as GeometryInstance3D
		if is_instance_valid(mi):
			mi.material_override = s[1]
			mi.visible = s[2]
	_saved.clear()
	if rig != null:
		rig.set_id_pass(false)
	else:
		view.set_id_pass(false)


func _frames() -> void:
	for _i in SETTLE_FRAMES:
		await _tree.process_frame


## Freezes the scene clock (the rig's) at meta `anim_t`, or where it stands. Returns {"t": the frozen time, "prev": the time to put back}.
func _freeze(meta: Dictionary) -> Dictionary:
	if rig == null:
		return {"t": float(meta.get("anim_t", 0.0)), "prev": 0.0}
	var prev := rig.anim_t()
	var t := float(meta["anim_t"]) if meta.has("anim_t") else prev
	rig.freeze_anim(true, t)
	return {"t": t, "prev": prev}


func _thaw(anim: Dictionary) -> void:
	if rig != null:
		rig.freeze_anim(false, float(anim["prev"]))
