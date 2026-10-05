extends Node3D
## ART-8 8p review lab (windowed only; headless has no renderer): each HQ compound glTF in
## the 1D spike's look (hq_compound_toon.gdshader + the spike's post pass and light) at the
## compound reference camera (bible 4.7: city azimuth, 55 deg, orthographic), with the
## layout table's anchors marked. One launch walks every corporation:
##   python tools/run_windowed.py --log <f> -- --resolution 1920x1080
##     res://tools/art_pipeline/city/hq_compound_lab.tscn -- --size=1920x1080 --out=<dir>
##     [--corps=meridian,solace] [--settle=40]
## Writes <out>/<corp>_model.png (model only) and <out>/<corp>_anchors.png (with anchors).

const CONFIG := preload("res://tools/spike/city/city_spike_config.tres")
const POST_SHADER := preload("res://shaders/city/city_post.gdshader")
const TOON_SHADER := preload("res://tools/art_pipeline/city/hq_compound_toon.gdshader")
const ROLES := {"hq_toon": 0, "hq_lit": 1, "hq_neon": 2, "hq_win": 3, "hq_sign": 4, "hq_beam": 2}
const CORPS := ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]
const PITCH_DEG := 55.0
const GROUND_HALF := 400.0
const MARK_PX := 11.0

var cfg: CitySpikeConfig = CONFIG
var camera: Camera3D
var _post: ShaderMaterial
var _args: Dictionary = {}
var _corps: PackedStringArray = PackedStringArray()
var _current: Node3D
var _manifest: Dictionary = {}
var _layout: HqCompoundLayoutData
var _overlay: Control
var _frame: int = 0
var _step: int = 0
var _phase: int = 0


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	_corps = PackedStringArray(String(_args.get("corps", ",".join(CORPS))).split(","))
	_build_environment()
	_build_ground()
	_build_camera()
	_build_post()
	var layer := CanvasLayer.new()
	add_child(layer)
	_overlay = Control.new()
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.draw.connect(_draw_anchors)
	layer.add_child(_overlay)
	_load(_corps[0])


func _build_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = cfg.sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_DISABLED
	env.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.glow_enabled = false
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.look_at_from_position(Vector3.ZERO, -cfg.to_light, Vector3.UP)
	sun.shadow_enabled = true
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	sun.directional_shadow_max_distance = 3000.0
	add_child(sun)


func _toon(role: int, tint: Vector3) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = TOON_SHADER
	m.set_shader_parameter("ramp_shadow", _v3(cfg.ramp[0]))
	m.set_shader_parameter("ramp_mid", _v3(cfg.ramp[1]))
	m.set_shader_parameter("ramp_lit", _v3(cfg.ramp[2]))
	m.set_shader_parameter("ramp_edges", cfg.ramp_edges)
	m.set_shader_parameter("ramp_tint", tint)
	m.set_shader_parameter("role", role)
	m.set_shader_parameter("neon_gain", cfg.neon_gain)
	m.set_shader_parameter("window_gain", cfg.window_gain)
	return m


static func _v3(c: Color) -> Vector3:
	return Vector3(c.r, c.g, c.b)


func _build_ground() -> void:
	# The street level around the compound (ART-5's city goes here later): the concept's ground colour.
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var g := cfg.ground
	g.a = 1.0
	for p in [Vector3(-1, 0, -1), Vector3(1, 0, -1), Vector3(1, 0, 1), Vector3(-1, 0, -1), Vector3(1, 0, 1), Vector3(-1, 0, 1)]:
		st.set_color(g)
		st.add_vertex(p * GROUND_HALF + Vector3(0, -0.06, 0))
	var mi := MeshInstance3D.new()
	mi.mesh = st.commit()
	mi.material_override = _toon(0, Vector3.ONE)
	add_child(mi)


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	camera.near = 1.0
	camera.far = cfg.camera_far
	add_child(camera)
	camera.make_current()


func _build_post() -> void:
	_post = ShaderMaterial.new()
	_post.shader = POST_SHADER
	_post.render_priority = -100
	var qm := QuadMesh.new()
	qm.size = Vector2(2, 2)
	var mi := MeshInstance3D.new()
	mi.mesh = qm
	mi.material_override = _post
	mi.extra_cull_margin = 16384.0
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	camera.add_child(mi)
	mi.position = Vector3(0, 0, -10)
	for kv in [["see_dark", cfg.see_through_dark], ["see_chroma", cfg.see_through_chroma], ["ink_on", true],
			["ink_color", _v3(cfg.ink)], ["ink_normal_edge", cfg.ink_normal_edge], ["ink_depth_edge", cfg.ink_depth_edge],
			["ink_wobble_px", cfg.ink_wobble_px], ["ink_width", cfg.ink_width_px], ["rain_density", cfg.rain_density],
			["cam_distance", cfg.camera_distance], ["grime", cfg.grime], ["spill", cfg.spill], ["bloom", cfg.bloom],
			["glow_threshold", cfg.glow_threshold], ["glow_lod", cfg.glow_mip], ["haze_color", _v3(cfg.haze)],
			["haze_k", cfg.haze_k], ["fog_on", true], ["fog_color", _v3(cfg.fog)], ["fog_amount", cfg.fog_amount],
			["rain_on", true], ["rain_color", _v3(cfg.rain)], ["rain_alpha", cfg.rain_alpha], ["grade", _v3(cfg.grade)],
			["opacity", 1.0], ["has_ground", false], ["time_scale", 0.0], ["ink_alpha", cfg.ink_alpha_near], ["fog_city", 0.0]]:
		_post.set_shader_parameter(kv[0], kv[1])


func _load(corp: String) -> void:
	if _current != null:
		_current.queue_free()
	var dir := "res://assets/city/hq_compounds/%s" % corp
	var f := FileAccess.open(dir + "/manifest.json", FileAccess.READ)
	_manifest = JSON.parse_string(f.get_as_text()) if f != null else {}
	_layout = load("res://content/city/hq_compounds/%s.tres" % corp) as HqCompoundLayoutData
	var settings: Dictionary = _manifest.get("settings", {})
	var tint_a: Array = settings.get("ramp_tint", [1, 1, 1])
	var tint := Vector3(float(tint_a[0]), float(tint_a[1]), float(tint_a[2]))
	var scene := load("%s/%s_compound.glb" % [dir, corp]) as PackedScene
	_current = scene.instantiate() as Node3D
	add_child(_current)
	_skin(_current, tint)
	var cam: Dictionary = settings.get("reference_camera", {})
	var t: Array = cam.get("target", [0, 0, 0])
	var target := Vector3(float(t[0]), float(t[1]), float(t[2]))
	var el := deg_to_rad(PITCH_DEG)
	var back := Vector3(0.70710678 * cos(el), sin(el), 0.70710678 * cos(el))
	camera.size = float(cam.get("ortho", 150.0))
	camera.look_at_from_position(target + back * cfg.camera_distance, target, Vector3.UP)
	_post.set_shader_parameter("ortho", camera.size)
	_overlay.visible = false
	_overlay.queue_redraw()


func _skin(n: Node, tint: Vector3) -> void:
	if n is MeshInstance3D:
		var mi := n as MeshInstance3D
		for s in mi.mesh.get_surface_count():
			var mat := mi.mesh.surface_get_material(s)
			var role := int(ROLES.get(mat.resource_name if mat != null else "", 0))
			mi.set_surface_override_material(s, _toon(role, tint))
	for c in n.get_children():
		_skin(c, tint)


func _draw_anchors() -> void:
	if _layout == null:
		return
	var font := ThemeDB.fallback_font
	var prev: Array[Vector2] = []
	for layer in range(1, _layout.layer_rows() + 1):
		var row: Array[Vector2] = []
		for s in _layout.slots_per_layer:
			row.append(camera.unproject_position(_layout.slot_position(layer, s)))
		for a in prev:
			for b in row:
				_overlay.draw_line(a, b, Color(1, 1, 1, 0.18), 1.0)
		for s in row.size():
			_overlay.draw_circle(row[s], MARK_PX, Color(0.05, 0.04, 0.09, 0.9))
			_overlay.draw_arc(row[s], MARK_PX, 0, TAU, 24, Color(1.0, 0.55, 0.1), 3.0)
			_overlay.draw_string(font, row[s] + Vector2(-9, 5), "%d%s" % [layer, "abcd"[s]], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color.WHITE)
		prev = row
	var sv := camera.unproject_position(_layout.central_server)
	for a in prev:
		_overlay.draw_line(a, sv, Color(1, 1, 1, 0.18), 1.0)
	_overlay.draw_arc(sv, MARK_PX * 2.0, 0, TAU, 32, Color(1.0, 0.15, 0.2), 4.0)
	_overlay.draw_string(font, sv + Vector2(-30, -28), "CENTRAL SERVER", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(1.0, 0.85, 0.3))
	var en := camera.unproject_position(_layout.entry)
	_overlay.draw_arc(en, MARK_PX, 0, TAU, 4, Color(0.8, 1.0, 0.2), 3.0)


func _process(_delta: float) -> void:
	_frame += 1
	if _args.has("size") and _frame <= 3:
		var wh := String(_args["size"]).split("x")
		var want := Vector2i(int(wh[0]), int(wh[1]))
		if DisplayServer.window_get_size() != want:
			DisplayServer.window_set_size(want)
	var settle := int(_args.get("settle", "40"))
	if _frame < settle:
		return
	var out := String(_args.get("out", "user://hq_compound_lab"))
	DirAccess.make_dir_recursive_absolute(out)
	var corp := _corps[_step]
	var img := get_viewport().get_texture().get_image()
	if _phase == 0:
		img.save_png("%s/%s_model.png" % [out, corp])
		_overlay.visible = true
		_overlay.queue_redraw()
		_phase = 1
		_frame = settle - 3
		return
	img.save_png("%s/%s_anchors.png" % [out, corp])
	print("HQLAB shot %s %dx%d" % [corp, img.get_width(), img.get_height()])
	_phase = 0
	_step += 1
	if _step >= _corps.size():
		get_tree().quit()
		return
	_frame = 0
	_load(_corps[_step])
