class_name L7Board
extends SubViewportContainer
## The 3D board behind the lab's 2D overlay: the Blender target frames' slab, grid, copper links, towers, pylons, skyline and
## data motes, in a SubViewport the size of the screen, seen through L7Cam's camera (so the overlay's projected positions
## land on it). It draws no rule and holds no state of its own: the view hands it the status of every cell each frame
## (`apply`) and it rebuilds only the cells whose look changed. Palette and materials: docs/design/raid_concepts/raid_target
## README; geometry: tools/raid_concepts/target/raid_scene.py.

const COBALT := Color8(61, 107, 255)
const COBALT_HOT := Color8(159, 192, 255)
const GOLD := Color8(255, 210, 77)
const AMBER := Color8(255, 176, 32)
const COPPER := Color8(201, 116, 26)
const CYAN := Color8(92, 225, 255)
const SKY_WIRE := Color8(58, 143, 208)
const DEAD := Color8(35, 37, 44)
const DEAD_RING := Color8(90, 96, 112)
const WARM_METAL := Color8(43, 32, 24)
const STEEL := Color8(26, 30, 46)
const RED := Color8(255, 61, 77)

const EDGE_SHADER := """
shader_type spatial;
render_mode unshaded, cull_disabled;
uniform vec4 line_color : source_color = vec4(0.2, 0.5, 0.8, 1.0);
uniform vec4 fill_color : source_color = vec4(0.0, 0.01, 0.03, 1.0);
uniform float width = 0.1;
uniform float energy = 1.0;
varying vec3 lp;
varying vec3 sc;
void vertex() {
	lp = VERTEX;
	sc = vec3(length(MODEL_MATRIX[0].xyz), length(MODEL_MATRIX[1].xyz), length(MODEL_MATRIX[2].xyz));
}
void fragment() {
	vec3 d = (vec3(0.5) - abs(lp)) * sc;
	float n = step(d.x, width) + step(d.y, width) + step(d.z, width);
	float edge = step(2.0, n);
	ALBEDO = mix(fill_color.rgb, line_color.rgb * energy, edge);
	ALPHA = mix(fill_color.a, 1.0, edge);
}
"""

const GRID_SHADER := """
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never;
uniform vec4 line_color : source_color = vec4(0.36, 0.88, 1.0, 1.0);
uniform float spacing = 1.0;
uniform float width = 0.025;
uniform float energy = 0.3;
varying vec3 wpos;
void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}
void fragment() {
	vec2 g = abs(fract(wpos.xz / spacing + 0.5) - 0.5) * spacing;
	float line = 1.0 - smoothstep(width * 0.5, width, min(g.x, g.y));
	ALBEDO = line_color.rgb * energy;
	ALPHA = line;
}
"""

var vp: SubViewport
var cam: Camera3D
var _mats: Dictionary = {}
var _cells: Dictionary = {}
var _cell_key: Dictionary = {}
var _cell_ring: Dictionary = {}
var _cell_light: Dictionary = {}
var _cell_body: Dictionary = {}
var _pylon_eye: Dictionary = {}
var _pylon_lit: Dictionary = {}
var _static_root: Node3D
var _sky_t: float = 0.0
var _motes: MultiMeshInstance3D


func _init() -> void:
	stretch = true
	size = L7Cam.VIEW
	position = Vector2.ZERO
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	vp = SubViewport.new()
	vp.size = Vector2i(L7Cam.VIEW)
	vp.msaa_3d = Viewport.MSAA_4X
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.handle_input_locally = false
	add_child(vp)
	_build()


# ---------- materials ----------
func _emit(col: Color, energy: float, alpha: float = 1.0) -> StandardMaterial3D:
	var k := "e%s|%s|%s" % [col.to_html(), energy, alpha]
	if _mats.has(k):
		return _mats[k]
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	# Unshaded ignores emission, so the light is the albedo itself, above 1 where it should bloom.
	m.albedo_color = Color(col.r * energy * 0.55, col.g * energy * 0.55, col.b * energy * 0.55, alpha)
	if alpha < 0.999:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_mats[k] = m
	return m


func _solid(col: Color, rough: float = 0.5, metal: float = 0.0) -> StandardMaterial3D:
	var k := "s%s|%s|%s" % [col.to_html(), rough, metal]
	if _mats.has(k):
		return _mats[k]
	var m := StandardMaterial3D.new()
	m.albedo_color = col
	m.roughness = rough
	m.metallic = metal
	_mats[k] = m
	return m


func _edge_mat(line: Color, fill: Color, width: float, energy: float) -> ShaderMaterial:
	var k := "w%s|%s|%s|%s" % [line.to_html(), fill.to_html(true), width, energy]
	if _mats.has(k):
		return _mats[k]
	var sh := Shader.new()
	sh.code = EDGE_SHADER
	var m := ShaderMaterial.new()
	m.shader = sh
	m.set_shader_parameter("line_color", line)
	m.set_shader_parameter("fill_color", fill)
	m.set_shader_parameter("width", width)
	m.set_shader_parameter("energy", energy)
	_mats[k] = m
	return m


# ---------- mesh helpers (board coordinates: x right, y away, z up) ----------
func _inst(parent: Node, mesh: Mesh, mat: Material, bpos: Vector3, rot_y: float = 0.0) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.position = L7Cam.to_godot(bpos)
	mi.rotation.y = rot_y
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)
	return mi


var _unit_box: BoxMesh = null


func _box(parent: Node, bpos: Vector3, bsize: Vector3, mat: Material, rot: float = 0.0) -> MeshInstance3D:
	if _unit_box == null:
		_unit_box = BoxMesh.new()
		_unit_box.size = Vector3.ONE
	var mi := _inst(parent, _unit_box, mat, bpos, rot)
	mi.scale = Vector3(bsize.x, bsize.z, bsize.y)
	return mi


func _cyl(parent: Node, bpos: Vector3, r: float, h: float, verts: int, mat: Material, rot: float = 0.0, r2: float = -1.0) -> MeshInstance3D:
	var cm := CylinderMesh.new()
	cm.top_radius = r if r2 < 0.0 else r2
	cm.bottom_radius = r
	cm.height = h
	cm.radial_segments = verts
	cm.rings = 1
	return _inst(parent, cm, mat, bpos, rot)


## A flat ring (annulus) in the board plane at height z, `verts` sides (6 = the hex ring).
func _ring(parent: Node, bpos: Vector3, r_out: float, r_in: float, verts: int, mat: Material, rot: float = 0.0) -> MeshInstance3D:
	var vtx := PackedVector3Array()
	var idx := PackedInt32Array()
	for i in range(verts):
		var a: float = TAU * float(i) / verts
		vtx.append(Vector3(cos(a) * r_out, 0.0, sin(a) * r_out))
		vtx.append(Vector3(cos(a) * r_in, 0.0, sin(a) * r_in))
	for i in range(verts):
		var j: int = (i + 1) % verts
		var o0 := i * 2
		var i0 := i * 2 + 1
		var o1 := j * 2
		var i1 := j * 2 + 1
		idx.append_array([o0, o1, i0, i0, o1, i1])
	var arr: Array = []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = vtx
	arr[Mesh.ARRAY_INDEX] = idx
	var normals := PackedVector3Array()
	for _k in range(vtx.size()):
		normals.append(Vector3.UP)
	arr[Mesh.ARRAY_NORMAL] = normals
	var am := ArrayMesh.new()
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	var mi := _inst(parent, am, mat, bpos, rot)
	mi.mesh = am
	return mi


## Flat ribbons on the floor: segs = [[Vector2 a, Vector2 b], ...] in board xy, merged into one mesh.
func _ribbons(parent: Node, segs: Array, width: float, mat: Material, z: float) -> MeshInstance3D:
	var vtx := PackedVector3Array()
	var idx := PackedInt32Array()
	var nrm := PackedVector3Array()
	for s in segs:
		var a: Vector2 = s[0]
		var b: Vector2 = s[1]
		var d := (b - a)
		if d.length() < 0.00001:
			continue
		d = d.normalized()
		var n := Vector2(-d.y, d.x) * (width * 0.5)
		var base := vtx.size()
		for p in [a - n, a + n, b + n, b - n]:
			var pp: Vector2 = p
			vtx.append(Vector3(pp.x, z, -pp.y))
			nrm.append(Vector3.UP)
		idx.append_array([base, base + 1, base + 2, base, base + 2, base + 3])
	var arr: Array = []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = vtx
	arr[Mesh.ARRAY_INDEX] = idx
	arr[Mesh.ARRAY_NORMAL] = nrm
	var am := ArrayMesh.new()
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	var mi := MeshInstance3D.new()
	mi.mesh = am
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)
	return mi


func _octa(parent: Node, bpos: Vector3, r: float, sq: float, mat: Material) -> MeshInstance3D:
	var top := Vector3(0, r * sq, 0)
	var bot := Vector3(0, -r * sq, 0)
	var rv := [Vector3(r, 0, 0), Vector3(0, 0, r), Vector3(-r, 0, 0), Vector3(0, 0, -r)]
	var vtx := PackedVector3Array()
	var nrm := PackedVector3Array()
	for i in range(4):
		var j := (i + 1) % 4
		for tri in [[top, rv[i], rv[j]], [bot, rv[j], rv[i]]]:
			var a: Vector3 = tri[0]
			var b: Vector3 = tri[1]
			var c: Vector3 = tri[2]
			var n := (b - a).cross(c - a).normalized()
			for p in [a, b, c]:
				vtx.append(p)
				nrm.append(n)
	var arr: Array = []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = vtx
	arr[Mesh.ARRAY_NORMAL] = nrm
	var am := ArrayMesh.new()
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	return _inst(parent, am, mat, bpos, deg_to_rad(20.0))


# ---------- the static set ----------
func _build() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color8(3, 5, 15)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color8(40, 52, 96)
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.glow_enabled = true
	env.glow_intensity = 0.9
	env.glow_strength = 1.1
	env.glow_bloom = 0.08
	env.glow_hdr_threshold = 0.85
	env.glow_blend_mode = Environment.GLOW_BLEND_MODE_SCREEN
	var we := WorldEnvironment.new()
	we.environment = env
	vp.add_child(we)

	cam = Camera3D.new()
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	cam.fov = L7Cam.hfov_deg()
	cam.near = 1.0
	cam.far = 900.0
	vp.add_child(cam)
	cam.look_at_from_position(L7Cam.to_godot(L7Cam.CAM_POS), L7Cam.to_godot(L7Cam.aim_point()), Vector3.UP)

	_static_root = Node3D.new()
	vp.add_child(_static_root)
	_build_lights()
	_build_floor()
	_build_skyline()
	_build_pylons()
	_build_motes()
	for c: Vector2i in _all_cells():
		var root := Node3D.new()
		root.position = L7Cam.to_godot(Vector3(L7Cam.COLS[c.x], L7Cam.ROWS[c.y], 0.0))
		vp.add_child(root)
		_cells[c] = root
		var lt := OmniLight3D.new()
		lt.light_color = COBALT
		lt.omni_range = 7.0
		lt.light_energy = 0.0
		lt.position = Vector3(0, 2.2, 0)
		root.add_child(lt)
		_cell_light[c] = lt


func _all_cells() -> Array:
	var out: Array = []
	for y in range(3):
		for x in range(4):
			out.append(Vector2i(x, y))
	return out


func _build_lights() -> void:
	var key := DirectionalLight3D.new()
	key.light_color = Color(0.55, 0.62, 1.0)
	key.light_energy = 0.9
	key.rotation_degrees = Vector3(-52, -25, 0)
	vp.add_child(key)
	var warm := OmniLight3D.new()
	warm.light_color = Color(1.0, 0.7, 0.4)
	warm.light_energy = 1.1
	warm.omni_range = 15.0
	warm.position = L7Cam.to_godot(Vector3(4.4, 3.5, 9.0))
	vp.add_child(warm)
	var rim := OmniLight3D.new()
	rim.light_color = Color(0.35, 0.5, 1.0)
	rim.light_energy = 1.6
	rim.omni_range = 30.0
	rim.position = L7Cam.to_godot(Vector3(15, 12, 8))
	vp.add_child(rim)


func _build_floor() -> void:
	_box(_static_root, Vector3(4.35, 12, -0.30), Vector3(400, 400, 0.3), _solid(Color8(6, 10, 24), 0.85))
	var slab_c := Vector3((L7Cam.SLAB_X0 + L7Cam.SLAB_X1) * 0.5, (L7Cam.SLAB_Y0 + L7Cam.SLAB_Y1) * 0.5, -0.12)
	_box(_static_root, slab_c, Vector3(L7Cam.SLAB_X1 - L7Cam.SLAB_X0, L7Cam.SLAB_Y1 - L7Cam.SLAB_Y0, 0.24), _solid(Color8(14, 22, 44), 0.38, 0.1))
	# The slab's rim (the Cell's territory, warm and faint).
	var x0: float = L7Cam.SLAB_X0
	var x1: float = L7Cam.SLAB_X1
	var y0: float = L7Cam.SLAB_Y0
	var y1: float = L7Cam.SLAB_Y1
	var rim_pts := [Vector2(x0, y0), Vector2(x1, y0), Vector2(x1, y1), Vector2(x0, y1)]
	var rim: Array = []
	for i in range(4):
		rim.append([rim_pts[i], rim_pts[(i + 1) % 4]])
	_ribbons(_static_root, rim, 0.08, _emit(AMBER, 1.7), 0.02)
	# The grid on the slab (cool, faint) and the far floor's coarser one.
	var grid_m := ShaderMaterial.new()
	var gs := Shader.new()
	gs.code = GRID_SHADER
	grid_m.shader = gs
	grid_m.set_shader_parameter("spacing", 1.0)
	grid_m.set_shader_parameter("width", 0.022)
	grid_m.set_shader_parameter("energy", 0.11)
	var pm := PlaneMesh.new()
	pm.size = Vector2(x1 - x0, y1 - y0)
	_inst(_static_root, pm, grid_m, Vector3((x0 + x1) * 0.5, (y0 + y1) * 0.5, 0.012))
	var far_m := ShaderMaterial.new()
	far_m.shader = gs
	far_m.set_shader_parameter("spacing", 4.0)
	far_m.set_shader_parameter("width", 0.08)
	far_m.set_shader_parameter("energy", 0.12)
	var pf := PlaneMesh.new()
	pf.size = Vector2(300, 300)
	_inst(_static_root, pf, far_m, Vector3(4.4, 60.0, -0.2))
	# The Cell's own wires between neighbouring nodes.
	var links: Array = []
	for r in range(3):
		for c in range(3):
			links.append([Vector2(L7Cam.COLS[c], L7Cam.ROWS[r]), Vector2(L7Cam.COLS[c + 1], L7Cam.ROWS[r])])
	for c in range(4):
		for r in range(2):
			links.append([Vector2(L7Cam.COLS[c], L7Cam.ROWS[r]), Vector2(L7Cam.COLS[c], L7Cam.ROWS[r + 1])])
	_ribbons(_static_root, links, 0.13, _emit(COPPER, 1.2), 0.035)


func _build_skyline() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 77
	var m := _edge_mat(SKY_WIRE, Color(0.004, 0.008, 0.024, 1.0), 0.12, 0.85)
	for i in range(70):
		var x := rng.randf_range(-40, 52)
		var y := rng.randf_range(12, 46)
		var w := rng.randf_range(2.0, 6.5)
		var d := rng.randf_range(2.0, 6.5)
		var h := rng.randf_range(7, 34) * (1.0 + (y - 10) / 60.0)
		if rng.randf() < 0.08:
			h *= 1.9
		if y < 11.0 and x > -4.0 and x < 13.0:
			continue
		_box(_static_root, Vector3(x, y, h * 0.5 - 0.3), Vector3(w, d, h), m)
	var spk := _emit(Color8(255, 154, 61), 2.2)
	for i in range(80):
		_box(_static_root, Vector3(rng.randf_range(-60, 80), rng.randf_range(30, 120), rng.randf_range(1, 18)), Vector3(0.35, 0.35, 0.35), spk)
	_box(_static_root, Vector3(4.4, 200, 40), Vector3(600, 0.2, 140), _emit(Color8(91, 42, 154), 0.7))
	_box(_static_root, Vector3(4.4, 190, 8), Vector3(600, 0.2, 30), _emit(Color8(176, 77, 255), 0.9))


func _pylon_pos(key: String) -> Vector3:
	var p: PackedStringArray = key.split(":")
	match p[0]:
		"L":
			return Vector3(L7Cam.PYLON_X[0], L7Cam.ROWS[int(p[1])], 0.0)
		"R":
			return Vector3(L7Cam.PYLON_X[1], L7Cam.ROWS[int(p[1])], 0.0)
	return Vector3(L7Cam.COLS[int(p[1])], L7Cam.PYLON_Y, 0.0)


func _build_pylons() -> void:
	var body := _solid(Color8(18, 23, 42), 0.35, 0.7)
	var keys: Array = []
	for r in range(3):
		keys.append("L:%d" % r)
		keys.append("R:%d" % r)
	for c in range(4):
		keys.append("T:%d" % c)
	for k: String in keys:
		var p := _pylon_pos(k)
		var root := Node3D.new()
		root.position = L7Cam.to_godot(p)
		_static_root.add_child(root)
		var face := Vector3(1.1, 1.6, 2.6)
		if k.begins_with("T"):
			face = Vector3(1.6, 1.1, 2.6)
		_box(root, Vector3(0, 0, 1.3), face, body)
		_box(root, Vector3(0, 0, 2.9), Vector3(face.x * 0.64, face.y * 0.7, 0.5), body)
		var eye := _box(root, Vector3(0, 0, 2.9), Vector3(face.x * 0.7, face.y * 0.7, 0.24), _emit(COBALT, 0.9))
		_pylon_eye[k] = eye
		_pylon_lit[k] = false


## Cobalt-eyed pylons: those named in `keys` are lit hot (the lines that start there), the rest dim.
func light_pylons(keys: Array) -> void:
	for k: String in _pylon_eye:
		var on: bool = keys.has(k)
		if _pylon_lit[k] != on:
			_pylon_lit[k] = on
			(_pylon_eye[k] as MeshInstance3D).material_override = _emit(COBALT_HOT if on else COBALT, 4.5 if on else 0.9)


func _build_motes() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 2026
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	var bm := BoxMesh.new()
	bm.size = Vector3(0.09, 0.09, 0.09)
	mm.mesh = bm
	mm.instance_count = 110
	for i in range(110):
		var p := Vector3(rng.randf_range(-8, 15), rng.randf_range(-5, 12), rng.randf_range(0.3, 8.0))
		var t := Transform3D(Basis(Vector3.UP, rng.randf_range(0, 3.0)), L7Cam.to_godot(p))
		mm.set_instance_transform(i, t)
		mm.set_instance_color(i, Color(1.0, 0.69, 0.13) if i % 3 != 0 else Color(0.36, 0.88, 1.0))
	_motes = MultiMeshInstance3D.new()
	_motes.multimesh = mm
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.vertex_color_use_as_albedo = true
	mat.albedo_color = Color(1.1, 1.1, 1.1)
	_motes.material_override = mat
	_motes.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	vp.add_child(_motes)


# ---------- the cells ----------
## Apply the view's picture of the board. `st`: {values: cell -> int, home: cell, status: cell -> "OK"/"DOWN"/"TAKEN",
## ghost / dark / decoys: Array of cells, spent: Array of decoy cells already hit, home_hit: 0..1 red flash,
## flash: cell -> 0..1 (a beam just touched it), shake: cell -> Vector2 (x, y in board units), flip: cell -> 0..1}.
func apply(st: Dictionary) -> void:
	var vals: Dictionary = st["values"]
	var home: Vector2i = st["home"]
	var status: Dictionary = st["status"]
	for c: Vector2i in _all_cells():
		var kind := "empty"
		var n := 0
		if c == home:
			kind = "home"
		elif (st["decoys"] as Array).has(c):
			kind = "decoy_spent" if (st["spent"] as Array).has(c) else "decoy"
		elif vals.has(c):
			n = maxi(1, int(vals[c]) / 2)
			var s: String = status.get(c, "OK")
			if (st["ghost"] as Array).has(c):
				kind = "ghost%d" % n
			elif (st["dark"] as Array).has(c) and s == "OK":
				kind = "dark"
			else:
				kind = "%s%d" % [s.to_lower(), n]
		var key := "%s|%s" % [kind, "hit" if (c == home and float(st.get("home_hit", 0.0)) > 0.05) else ""]
		if _cell_key.get(c, "") != key:
			_cell_key[c] = key
			_rebuild_cell(c, kind, n, key.ends_with("hit"))
		var root: Node3D = _cells[c]
		var base := L7Cam.to_godot(Vector3(L7Cam.COLS[c.x], L7Cam.ROWS[c.y], 0.0))
		var sh: Vector2 = (st["shake"] as Dictionary).get(c, Vector2.ZERO)
		root.position = base + Vector3(sh.x, 0.0, -sh.y)
		var fl: float = float((st["flash"] as Dictionary).get(c, 0.0))
		var flip: float = float((st["flip"] as Dictionary).get(c, 1.0))
		root.scale = Vector3(1.0, maxf(0.04, absf(flip * 2.0 - 1.0) if flip < 1.0 else 1.0), 1.0)
		(_cell_light[c] as OmniLight3D).light_energy = fl * 5.0
		if _cell_ring.has(c) and _cell_ring[c] != null:
			var rm: StandardMaterial3D = _cell_ring[c]
			var rc: Color = rm.get_meta("col", GOLD)
			var k: float = float(rm.get_meta("base", 3.0)) * 0.55 * (1.0 + fl * 3.0)
			rm.albedo_color = Color(rc.r * k, rc.g * k, rc.b * k)


func _clear(root: Node3D) -> void:
	for ch in root.get_children():
		if ch is OmniLight3D:
			continue
		root.remove_child(ch)
		ch.queue_free()


func _pedestal(root: Node3D, ring_col: Color, ring_e: float, rad: float = 1.05, c: Vector2i = Vector2i(-1, -1)) -> void:
	_cyl(root, Vector3(0, 0, 0.12), rad, 0.24, 6, _solid(STEEL, 0.4, 0.6), deg_to_rad(30))
	var rm := StandardMaterial3D.new()
	rm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	rm.albedo_color = Color(ring_col.r * ring_e * 0.55, ring_col.g * ring_e * 0.55, ring_col.b * ring_e * 0.55)
	rm.set_meta("col", ring_col)
	rm.set_meta("base", ring_e)
	_ring(root, Vector3(0, 0, 0.255), rad + 0.16, rad + 0.01, 6, rm, deg_to_rad(30))
	_cell_ring[c] = rm


func _rebuild_cell(c: Vector2i, kind: String, n: int, hit: bool) -> void:
	var root: Node3D = _cells[c]
	_clear(root)
	_cell_ring[c] = null
	_cell_body[c] = null
	if kind == "empty":
		_ring(root, Vector3(0, 0, 0.04), 0.34, 0.2, 24, _emit(COPPER, 1.5))
		return
	if kind == "home":
		_cyl(root, Vector3(0, 0, 0.14), 1.5, 0.28, 6, _solid(STEEL, 0.4, 0.6), deg_to_rad(30))
		var rm := StandardMaterial3D.new()
		rm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		var hc: Color = RED if hit else GOLD
		rm.albedo_color = Color(hc.r * 3.8 * 0.55, hc.g * 3.8 * 0.55, hc.b * 3.8 * 0.55)
		rm.set_meta("col", hc)
		rm.set_meta("base", 3.8)
		_ring(root, Vector3(0, 0, 0.3), 1.72, 1.52, 6, rm, deg_to_rad(30))
		_cell_ring[c] = rm
		var body := _solid(Color8(58, 42, 30), 0.35, 0.6)
		var win := _emit(Color8(255, 176, 160) if hit else Color8(255, 226, 168), 4.5 if hit else 2.6)
		for i in range(3):
			var z := 0.65 + i * 0.8
			var s := 1.35 - i * 0.12
			_box(root, Vector3(0, 0, z), Vector3(s, s, 0.7), body)
			for k in range(3):
				_box(root, Vector3(0, -s * 0.5 - 0.005, z - 0.22 + k * 0.22), Vector3(s * 0.78, 0.02, 0.06), win)
				_box(root, Vector3(s * 0.5 + 0.005, 0, z - 0.22 + k * 0.22), Vector3(0.02, s * 0.78, 0.06), win)
		return
	if kind.begins_with("decoy"):
		_pedestal(root, GOLD, 3.0, 0.9, c)
		if kind == "decoy":
			var dm := StandardMaterial3D.new()
			dm.albedo_color = Color8(255, 192, 64)
			dm.metallic = 0.95
			dm.roughness = 0.22
			dm.emission_enabled = true
			dm.emission = Color8(255, 154, 16)
			dm.emission_energy_multiplier = 1.1
			_octa(root, Vector3(0, 0, 1.45), 0.85, 1.5, dm)
			_ring(root, Vector3(0, 0, 0.05), 1.55, 1.42, 48, _emit(GOLD, 3.0))
		else:
			var rr := RandomNumberGenerator.new()
			rr.seed = c.x * 31 + c.y * 7
			for q in range(9):
				_box(root, Vector3(rr.randf_range(-1, 1), rr.randf_range(-1, 1), 0.3 + rr.randf_range(0, 1.0)), Vector3(0.2, 0.2, 0.2), _emit(Color8(255, 194, 74), 3.0), rr.randf_range(0, 3))
		return
	if kind == "dark":
		_pedestal(root, Color8(74, 83, 104), 0.9, 1.05, c)
		var sm := SphereMesh.new()
		sm.radius = 0.95
		sm.height = 1.9
		sm.radial_segments = 24
		sm.rings = 12
		var dome := _inst(root, sm, _solid(Color8(8, 9, 14), 0.15, 0.8), Vector3(0, 0, 0.24))
		dome.scale = Vector3(1.0, 1.15, 1.0)
		_box(root, Vector3(0, -0.93, 0.6), Vector3(0.5, 0.02, 0.05), _emit(Color8(108, 120, 148), 1.6))
		return
	if kind.begins_with("ghost"):
		var gm := _edge_mat(GOLD, Color(1.0, 0.82, 0.3, 0.07), 0.05, 2.4)
		for i in range(n):
			_box(root, Vector3(0, 0, 0.45 + i * 0.36), Vector3(0.85, 0.85, 0.32), gm)
		var dash: Array = []
		for k in range(14):
			var a0: float = k * TAU / 14.0
			var a1: float = a0 + 0.26 * TAU / 14.0 * 2.2
			dash.append([Vector2(1.3 * cos(a0), 1.3 * sin(a0)), Vector2(1.3 * cos(a1), 1.3 * sin(a1))])
		_ribbons(root, dash, 0.1, _emit(GOLD, 3.2), 0.05)
		return
	# stacks: ok / down / taken
	var st := kind.rstrip("0123456789")
	var down := st == "down"
	var taken := st == "taken"
	var ring_col := DEAD_RING if down else (COBALT if taken else AMBER)
	_pedestal(root, ring_col, 1.0 if down else 3.2, 1.05, c)
	if down:
		var rr2 := RandomNumberGenerator.new()
		rr2.seed = c.x * 31 + c.y * 7
		for i in range(n):
			_box(root, Vector3(rr2.randf_range(-0.55, 0.55), rr2.randf_range(-0.55, 0.55), 0.34 + (i % 2) * 0.1), Vector3(0.7, 0.7, 0.26), _solid(DEAD, 0.6, 0.3), rr2.randf_range(0, 3.1))
		return
	var body_col := Color8(14, 20, 52) if taken else WARM_METAL
	var glow := _emit(COBALT_HOT if taken else AMBER, 2.6)
	var cap := _emit(COBALT if taken else GOLD, 2.2)
	var body := _solid(body_col, 0.38, 0.55)
	for i in range(n):
		var z := 0.5 + i * 0.5
		_box(root, Vector3(0, 0, z), Vector3(0.9, 0.9, 0.42), body)
		_box(root, Vector3(0, -0.445, z), Vector3(0.66, 0.02, 0.07), glow)
		_box(root, Vector3(0.445, 0, z), Vector3(0.02, 0.66, 0.07), glow)
	_box(root, Vector3(0, 0, 0.5 + (n - 1) * 0.5 + 0.235), Vector3(0.94, 0.94, 0.05), cap)
