extends Node3D
## ART-1 1D spike (a): the unified city in real-time Godot 3D. One district of the game's
## own layout (CityDistrict), MultiMesh building families with the toon / facet / window
## shader, ground + lane glow, sky-lane cars in three LOD tiers, one orthographic Camera3D,
## the post pass (ink, spill, fog, haze, rain, grade) and a ground pass for the see-through
## band. Windowed only (headless has no renderer). User args:
##   --view=grid|raid|netrun|close   --quality=0..2 (city_quality; -1 = default)
##   --shot=<png>  (saves the frame after --settle frames, then quits)
##   --perf=<seconds>  (frame-time probe after --settle frames: PERF lines, then quits)
##   --freeze=1  (stills: the clock stands)

const CONFIG := preload("res://tools/spike/city/city_spike_config.tres")
const BUILDING_SHADER := preload("res://tools/spike/city/shaders/city_building.gdshader")
const GROUND_SHADER := preload("res://tools/spike/city/shaders/city_ground.gdshader")
const CAR_SHADER := preload("res://tools/spike/city/shaders/city_car.gdshader")
const POST_SHADER := preload("res://tools/spike/city/shaders/city_post.gdshader")
const GROUND_LAYER := 2
const SETTLE_DEFAULT := 30

var cfg: CitySpikeConfig = CONFIG
var district: CityDistrict
var traffic: CityTraffic
var iso: CityIsoCamera
var camera: Camera3D
var quality: Dictionary = {}
var view_name: String = "grid"

var _post: ShaderMaterial
var _building_mat: ShaderMaterial
var _lane_mat: ShaderMaterial
var _car_tiers: Array[MultiMeshInstance3D] = []
var _car_mats: Array[ShaderMaterial] = []
var _ground_vp: SubViewport
var _ground_cam: Camera3D
var _sun: DirectionalLight3D
var _args: Dictionary = {}
var _frame: int = 0
var _car_tier: int = -1
var _perf: Dictionary = {}
var _build_ms: float = 0.0


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	view_name = String(_args.get("view", "grid"))
	var q := int(_args.get("quality", str(Settings.city_quality)))
	quality = CityLod.quality(cfg, q)
	var t0 := Time.get_ticks_msec()
	district = CityDistrict.from_layout(cfg)
	traffic = CityTraffic.build(cfg, district, cfg.city_seed)
	_build_environment()
	_build_buildings()
	_build_ground()
	_build_cars()
	_build_camera()
	_build_post()
	_build_ms = Time.get_ticks_msec() - t0
	print("SPIKE3D built prisms=%d buildings=%d streets=%d cars=%d in %.0f ms quality=%s" % [district.prisms.size(),
		district.buildings, district.streets.size(), traffic.cars.size(), _build_ms, str(quality)])
	apply_view(view_name)
	if _args.has("freeze"):
		# Stills: the clock stands (cars at their phases, rain and fog fixed).
		for m in _car_mats:
			m.set_shader_parameter("time_scale", 0.0)
		_post.set_shader_parameter("time_scale", 0.0)


func _build_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = cfg.sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_DISABLED
	env.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	# Bloom and spill are in the post pass (post40 order, display values), not Godot's glow.
	env.glow_enabled = false
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	_sun = DirectionalLight3D.new()
	_sun.look_at_from_position(Vector3.ZERO, -cfg.to_light, Vector3.UP)
	_sun.shadow_enabled = quality["shadows"]
	_sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	_sun.directional_shadow_max_distance = 3000.0
	RenderingServer.directional_shadow_atlas_set_size(int(quality["shadow_size"]), true)
	add_child(_sun)


func _ramp(m: ShaderMaterial) -> void:
	m.set_shader_parameter("ramp_shadow", _v3(cfg.ramp[0]))
	m.set_shader_parameter("ramp_mid", _v3(cfg.ramp[1]))
	m.set_shader_parameter("ramp_lit", _v3(cfg.ramp[2]))
	m.set_shader_parameter("ramp_edges", cfg.ramp_edges)


static func _v3(c: Color) -> Vector3:
	return Vector3(c.r, c.g, c.b)


func _build_buildings() -> void:
	_building_mat = ShaderMaterial.new()
	_building_mat.shader = BUILDING_SHADER
	_ramp(_building_mat)
	_building_mat.set_shader_parameter("tone_min", cfg.tone_min)
	_building_mat.set_shader_parameter("tone_max", cfg.tone_max)
	_building_mat.set_shader_parameter("roof_gain", cfg.roof_gain)
	var wc: Array[Vector3] = []
	for c in cfg.window_colors:
		wc.append(_v3(c))
	_building_mat.set_shader_parameter("window_colors", wc)
	_building_mat.set_shader_parameter("window_pitch", cfg.window_pitch)
	_building_mat.set_shader_parameter("window_size", cfg.window_size)
	_building_mat.set_shader_parameter("window_first", cfg.window_first)
	_building_mat.set_shader_parameter("window_share", cfg.window_share)
	_building_mat.set_shader_parameter("window_dim_min", cfg.window_dim_min)
	_building_mat.set_shader_parameter("window_gain", cfg.window_gain)
	_building_mat.set_shader_parameter("trim_bu", cfg.roof_trim_bu)
	_building_mat.set_shader_parameter("neon_gain", cfg.neon_gain)
	_building_mat.set_shader_parameter("ledge_every", cfg.ledge_every)
	_building_mat.set_shader_parameter("ledge_bu", cfg.ledge_bu)
	# Ink palette: the district's roof-trim colours, deterministic order.
	var inks: Array[Color] = []
	for pr in district.prisms:
		var c: Color = pr["ink"]
		if not inks.has(c):
			inks.append(c)
	inks.sort_custom(func(a: Color, b: Color) -> bool: return a.to_rgba32() < b.to_rgba32())
	inks.resize(mini(inks.size(), 16))
	var ink_v: Array[Vector3] = []
	for c in inks:
		ink_v.append(_v3(c))
	while ink_v.size() < 16:
		ink_v.append(Vector3.ONE)
	_building_mat.set_shader_parameter("ink_colors", ink_v)
	var fams := CityMeshKit.families(cfg, district)
	var keys: Array = fams.keys()
	keys.sort()
	for key: int in keys:
		var sides := key / 16
		var hc := key % 16
		var rows: int = cfg.height_class_rows[hc]
		var mesh := CityMeshKit.unit_prism(sides, rows, cfg.wall_columns, cfg.facet_jitter, cfg.facet_normal_jitter * 0.1, key)
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.use_custom_data = true
		mm.mesh = mesh
		var idx: Array = fams[key]
		mm.instance_count = idx.size()
		for k in idx.size():
			var pr: Dictionary = district.prisms[idx[k]]
			mm.set_instance_transform(k, CityMeshKit.instance_transform(pr["poly"], pr["y0"], pr["h"]))
			mm.set_instance_color(k, CityMeshKit.base_color(cfg, pr))
			var key_i := int(pr["key"])
			var trim := 0.0
			if float(pr["taper"]) > 0.05 and CityMeshKit.hash01(key_i, 42, 1) < cfg.roof_trim_share:
				var ii := inks.find(pr["ink"])
				trim = float(ii + 1) if ii >= 0 else 0.0
			mm.set_instance_custom_data(k, Color(float(pr["taper"]), trim, CityMeshKit.hash01(key_i, 43, 2), 0.0))
		var mi := MultiMeshInstance3D.new()
		mi.multimesh = mm
		mi.material_override = _building_mat
		mi.layers = 1
		add_child(mi)


func _build_ground() -> void:
	var gm := ShaderMaterial.new()
	gm.shader = GROUND_SHADER
	_ramp(gm)
	var g := MeshInstance3D.new()
	g.mesh = CityMeshKit.ground_mesh(cfg, district)
	g.material_override = gm
	g.layers = 1 | (1 << (GROUND_LAYER - 1))
	add_child(g)
	_lane_mat = ShaderMaterial.new()
	_lane_mat.shader = GROUND_SHADER
	_ramp(_lane_mat)
	_lane_mat.set_shader_parameter("lane", true)
	var l := MeshInstance3D.new()
	l.mesh = CityMeshKit.lane_mesh(cfg, district)
	l.material_override = _lane_mat
	l.layers = 1 | (1 << (GROUND_LAYER - 1))
	l.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(l)


func _build_cars() -> void:
	var streak := (cfg.car_length.x + cfg.car_length.y) * 0.5
	for tier in 3:
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.use_custom_data = true
		mm.mesh = CityMeshKit.car_mesh(tier, streak)
		mm.instance_count = traffic.cars.size()
		for k in traffic.cars.size():
			var car: Dictionary = traffic.cars[k]
			var ln: Dictionary = traffic.lanes[car["lane"]]
			var a: Vector3 = ln["a"]
			var b: Vector3 = ln["b"]
			var dir := (b - a).normalized()
			var side: Vector3 = ln["side"]
			var basis := Basis(dir, Vector3.UP, dir.cross(Vector3.UP))
			mm.set_instance_transform(k, Transform3D(basis, a + side * float(car["dir"])))
			mm.set_instance_color(k, car["color"])
			mm.set_instance_custom_data(k, Color(car["phase"], car["speed"], a.distance_to(b), float(car["dir"])))
		var mat := ShaderMaterial.new()
		mat.shader = CAR_SHADER
		mat.set_shader_parameter("body_alpha", cfg.car_box_alpha if tier == CityLod.CarTier.MEDIUM else 1.0)
		mat.render_priority = 10
		var mi := MultiMeshInstance3D.new()
		mi.multimesh = mm
		mi.material_override = mat
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mi.custom_aabb = AABB(Vector3(-2000, -10, -2000), Vector3(4000, 200, 4000))
		add_child(mi)
		_car_tiers.append(mi)
		_car_mats.append(mat)


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	camera.near = 1.0
	camera.far = cfg.camera_far
	add_child(camera)
	camera.make_current()
	get_viewport().scaling_3d_scale = float(quality["render_scale"])
	get_viewport().msaa_3d = Viewport.MSAA_2X if int(quality["msaa"]) > 0 else Viewport.MSAA_DISABLED
	_ground_vp = SubViewport.new()
	_ground_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_ground_vp.size = Vector2i(Vector2(DisplayServer.window_get_size()) * cfg.ground_pass_scale)
	_ground_vp.scaling_3d_scale = float(quality["render_scale"])
	add_child(_ground_vp)
	_ground_cam = Camera3D.new()
	_ground_cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	_ground_cam.keep_aspect = Camera3D.KEEP_WIDTH
	_ground_cam.near = 1.0
	_ground_cam.far = cfg.camera_far
	_ground_cam.cull_mask = 1 << (GROUND_LAYER - 1)
	var genv := Environment.new()
	genv.background_mode = Environment.BG_COLOR
	genv.background_color = cfg.sky
	genv.ambient_light_source = Environment.AMBIENT_SOURCE_DISABLED
	genv.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	_ground_cam.environment = genv
	_ground_vp.add_child(_ground_cam)


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
	_post.set_shader_parameter("ground_tex", _ground_vp.get_texture())
	_post.set_shader_parameter("see_dark", cfg.see_through_dark)
	_post.set_shader_parameter("see_chroma", cfg.see_through_chroma)
	_post.set_shader_parameter("see_window", cfg.see_through_window_gain)
	_post.set_shader_parameter("ink_on", quality["ink"])
	_post.set_shader_parameter("ink_color", _v3(cfg.ink))
	_post.set_shader_parameter("ink_normal_edge", cfg.ink_normal_edge)
	_post.set_shader_parameter("ink_depth_edge", cfg.ink_depth_edge)
	_post.set_shader_parameter("ink_wobble_px", cfg.ink_wobble_px)
	_post.set_shader_parameter("ink_width", cfg.ink_width_px)
	_post.set_shader_parameter("rain_density", cfg.rain_density)
	_post.set_shader_parameter("cam_distance", cfg.camera_distance)
	_post.set_shader_parameter("grime", cfg.grime)
	_post.set_shader_parameter("spill", cfg.spill)
	_post.set_shader_parameter("bloom", cfg.bloom)
	_post.set_shader_parameter("glow_threshold", cfg.glow_threshold)
	_post.set_shader_parameter("glow_lod", cfg.glow_mip)
	_post.set_shader_parameter("haze_color", _v3(cfg.haze))
	_post.set_shader_parameter("haze_k", cfg.haze_k)
	_post.set_shader_parameter("fog_on", quality["fog"])
	_post.set_shader_parameter("fog_color", _v3(cfg.fog))
	_post.set_shader_parameter("fog_amount", cfg.fog_amount)
	_post.set_shader_parameter("rain_on", quality["rain"])
	_post.set_shader_parameter("rain_color", _v3(cfg.rain))
	_post.set_shader_parameter("rain_alpha", cfg.rain_alpha)
	_post.set_shader_parameter("grade", _v3(cfg.grade))


## Points the camera at view `name` and applies that zoom's LOD, see-through and glow.
func apply_view(name: String) -> void:
	iso = CityIsoCamera.for_view(cfg, name, get_viewport().get_visible_rect().size)
	set_ortho(iso.ortho)


## Applies zoom `ortho` (BU wide) at the current target.
func set_ortho(ortho: float) -> void:
	iso.ortho = ortho
	camera.global_transform = iso.transform()
	camera.size = ortho
	_ground_cam.global_transform = camera.global_transform
	_ground_cam.size = ortho
	var lod := CityIsoCamera.lod_of(cfg, ortho)
	var op := CityLod.opacity(cfg, lod)
	var city := CityLod.city_share(cfg, lod)
	_post.set_shader_parameter("opacity", op)
	_post.set_shader_parameter("has_ground", op < 0.999)
	_ground_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS if op < 0.999 else SubViewport.UPDATE_DISABLED
	_post.set_shader_parameter("ortho", ortho)
	_post.set_shader_parameter("ink_alpha", cfg.ink_alpha_near if ortho < cfg.car_far_above else cfg.ink_alpha_far)
	_post.set_shader_parameter("fog_city", city)
	_lane_mat.set_shader_parameter("lane_gain", lerpf(cfg.lane_glow_management, 1.0, city))
	_building_mat.set_shader_parameter("detail", CityLod.detail(cfg, ortho))
	_car_tier = CityLod.car_tier(cfg, ortho, _car_tier)
	for k in _car_tiers.size():
		_car_tiers[k].visible = k == _car_tier
	for m in _car_mats:
		m.set_shader_parameter("gain", lerpf(cfg.sky_lane_management, 1.0, city))


func _process(_delta: float) -> void:
	_frame += 1
	if _args.has("size") and _frame <= 3:
		# The quiet window keeps Settings' resolution; the spike sizes it per run.
		var wh := String(_args["size"]).split("x")
		var want := Vector2i(int(wh[0]), int(wh[1]))
		if DisplayServer.window_get_size() != want:
			DisplayServer.window_set_size(want)
		if _frame == 3:
			_ground_vp.size = Vector2i(Vector2(DisplayServer.window_get_size()) * cfg.ground_pass_scale)
			apply_view(view_name)
	var settle := int(_args.get("settle", str(SETTLE_DEFAULT)))
	if _args.has("shot") and _frame == settle:
		var img := get_viewport().get_texture().get_image()
		var path := String(_args["shot"])
		img.save_png(path)
		print("SPIKE3D shot %s %dx%d" % [path, img.get_width(), img.get_height()])
		get_tree().quit()
	if _args.has("perf"):
		_probe(settle)


func _probe(settle: int) -> void:
	var rid := get_viewport().get_viewport_rid()
	if _frame == 2:
		RenderingServer.viewport_set_measure_render_time(rid, true)
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		Engine.max_fps = 0
	if _frame <= settle:
		_perf = {"t0": Time.get_ticks_usec(), "n": 0, "cpu": 0.0, "gpu": 0.0, "max": 0.0, "last": Time.get_ticks_usec(),
			"draws": 0.0, "prims": 0.0}
		return
	var now := Time.get_ticks_usec()
	var dt := (now - int(_perf["last"])) / 1000.0
	_perf["last"] = now
	_perf["n"] = int(_perf["n"]) + 1
	_perf["max"] = maxf(float(_perf["max"]), dt)
	_perf["cpu"] = float(_perf["cpu"]) + RenderingServer.viewport_get_measured_render_time_cpu(rid) + RenderingServer.get_frame_setup_time_cpu()
	_perf["gpu"] = float(_perf["gpu"]) + RenderingServer.viewport_get_measured_render_time_gpu(rid)
	_perf["draws"] = float(_perf["draws"]) + Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	_perf["prims"] = float(_perf["prims"]) + Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
	if now - int(_perf["t0"]) >= int(float(_args["perf"]) * 1000000.0):
		var n := float(_perf["n"])
		var wall := (now - int(_perf["t0"])) / 1000.0 / n
		print("PERF view=%s quality=%d size=%s frames=%d frame_avg_ms=%.2f frame_max_ms=%.2f cpu_ms=%.2f gpu_ms=%.2f draws=%.0f prims=%.0f tex_mb=%.1f vmem_mb=%.1f build_ms=%.0f" % [
			view_name, int(quality["tier"]), str(get_viewport().get_visible_rect().size), int(n), wall, float(_perf["max"]),
			float(_perf["cpu"]) / n, float(_perf["gpu"]) / n, float(_perf["draws"]) / n, float(_perf["prims"]) / n,
			Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0,
			Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0, _build_ms])
		get_tree().quit()
