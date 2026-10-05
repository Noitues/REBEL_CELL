extends Node3D
## ART-5 5b: the landmark review lab (windowed only; headless has no renderer). Renders every landmark glTF in the
## real-time technique 1D chose (the landmark toon material + the spike's ink / bloom / spill post pass, night and
## the cool day) at its reference camera from the corp manifest, and at the game's iso camera, then quits:
##   python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/art_pipeline/city/landmark_review.tscn
##       -- --out=<folder> [--only=<job,...>]
## One frame per shot: <out>/<job>[_<variant>]_<cam>_<mode>.png. Never part of the game: it reads the manifests.

const LANDMARKS := "res://assets/city/landmarks"
const CORPS: Array[String] = ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]
const SPIKE_CONFIG := preload("res://tools/spike/city/city_spike_config.tres")
const POST_SHADER := preload("res://shaders/city/city_post.gdshader")
const LOOK := preload("res://assets/city/landmarks/landmark_look.tres")
## Review-only framing and look numbers (the game's own come from the city config).
const SETTLE_FRAMES := 12
const ISO_ORTHO := 176.0
const SKY_DAY := Color(0.52, 0.58, 0.68)
const GROUND := Color(0.13, 0.13, 0.16)
const GROUND_BU := 3000.0
const PERSP_INK_ORTHO := 600.0

var cfg: CitySpikeConfig = SPIKE_CONFIG
var _args: Dictionary = {}
var _shots: Array[Dictionary] = []
var _env: Environment
var _cam: Camera3D
var _post: ShaderMaterial
var _holder: Node3D
var _frame: int = 0
var _shot: int = -1


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	DirAccess.make_dir_recursive_absolute(String(_args.get("out", "user://landmark_review")))
	_build_world()
	_plan_shots()
	print("LANDMARK REVIEW shots=%d" % _shots.size())
	_next_shot()


func _build_world() -> void:
	_env = Environment.new()
	_env.background_mode = Environment.BG_COLOR
	_env.ambient_light_source = Environment.AMBIENT_SOURCE_DISABLED
	_env.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
	_env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	_env.glow_enabled = false
	var we := WorldEnvironment.new()
	we.environment = _env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.look_at_from_position(Vector3.ZERO, -cfg.to_light, Vector3.UP)
	sun.shadow_enabled = true
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	sun.directional_shadow_max_distance = 1500.0
	add_child(sun)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	st.set_color(Color(GROUND.r, GROUND.g, GROUND.b, 0.0))
	var h := GROUND_BU
	for v in [Vector3(-h, -0.05, -h), Vector3(h, -0.05, -h), Vector3(h, -0.05, h), Vector3(-h, -0.05, -h), Vector3(h, -0.05, h), Vector3(-h, -0.05, h)]:
		st.add_vertex(v)
	var ground := MeshInstance3D.new()
	ground.mesh = st.commit()
	ground.material_override = LandmarkMaterials.make("lm_toon", LOOK, &"meridian", false)
	ground.name = "ground"
	add_child(ground)
	_cam = Camera3D.new()
	_cam.near = 0.5
	_cam.far = 6000.0
	_cam.keep_aspect = Camera3D.KEEP_WIDTH
	add_child(_cam)
	_cam.make_current()
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
	_cam.add_child(mi)
	mi.position = Vector3(0, 0, -10)
	for kv in [["ink_color", _v3(cfg.ink)], ["ink_normal_edge", cfg.ink_normal_edge], ["ink_depth_edge", cfg.ink_depth_edge],
			["ink_wobble_px", cfg.ink_wobble_px], ["ink_width", cfg.ink_width_px], ["rain_density", cfg.rain_density],
			["grime", cfg.grime], ["spill", cfg.spill], ["bloom", cfg.bloom], ["glow_threshold", cfg.glow_threshold],
			["glow_lod", cfg.glow_mip], ["haze_color", _v3(cfg.haze)], ["haze_k", cfg.haze_k], ["fog_on", false],
			["rain_on", true], ["rain_color", _v3(cfg.rain)], ["rain_alpha", cfg.rain_alpha], ["grade", _v3(cfg.grade)],
			["time_scale", 0.0], ["cam_distance", 2600.0]]:
		_post.set_shader_parameter(kv[0], kv[1])


func _plan_shots() -> void:
	var only := PackedStringArray(String(_args.get("only", "")).split(",", false))
	for corp in CORPS:
		var man: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("%s/%s/manifest.json" % [LANDMARKS, corp]))
		for e: Dictionary in man["landmarks"]:
			if e.get("kind", "") == "mask" or (not only.is_empty() and not only.has(e["job"])):
				continue
			var variants: Array[String] = [""]
			if e["job"] == "orbital_hq":
				variants = ["closed", "open"]
			elif e["kind"] == "district":
				variants = ["lit", "home", "dispatch"]
			var cams: Array[String] = ["iso"]
			if e["reference_camera"]["kind"] == "perspective":
				cams = ["ref", "iso"]
			for v in variants:
				for cam in cams:
					for mode in (["night", "day"] if v in ["", "closed", "home"] and cam == "ref" else ["night"]):
						_shots.append({"corp": corp, "entry": e, "variant": v, "cam": cam, "mode": mode})


func _next_shot() -> void:
	_shot += 1
	if _shot >= _shots.size():
		print("LANDMARK REVIEW DONE")
		get_tree().quit(0)
		return
	var s: Dictionary = _shots[_shot]
	var e: Dictionary = s["entry"]
	var day: bool = s["mode"] == "day"
	if _holder != null:
		_holder.free()
	var ps: PackedScene = load("%s/%s/%s" % [LANDMARKS, s["corp"], e["file"]])
	_holder = ps.instantiate()
	add_child(_holder)
	var mats := LandmarkMaterials.apply(_holder, LOOK, StringName(s["corp"]), day)
	if s["variant"] == "lit":
		LandmarkMaterials.set_reveal(mats, 0.0)
	LandmarkMaterials.show_dispatch(_holder, s["variant"] == "dispatch")
	for n in _holder.find_children("*__state_*", "Node3D", true, false):
		if String(n.name).get_slice("__state_", 1).contains("__"):
			continue  # a mesh inside a state node
		(n as Node3D).visible = s["variant"] == "" or String(n.name).ends_with(s["variant"])
	_env.background_color = SKY_DAY if day else cfg.sky
	var rc: Dictionary = e["reference_camera"]
	if s["cam"] == "ref":
		_cam.projection = Camera3D.PROJECTION_PERSPECTIVE
		_cam.fov = float(rc["hfov_deg"])
		var p := Vector3(rc["position"][0], rc["position"][1], rc["position"][2])
		var t := Vector3(rc["target"][0], rc["target"][1], rc["target"][2])
		_cam.look_at_from_position(p, t, Vector3.UP)
		_post.set_shader_parameter("ortho", PERSP_INK_ORTHO)
	else:
		var iso := CityIsoCamera.new()
		iso.yaw_deg = cfg.yaw_deg
		iso.pitch_deg = cfg.pitch_deg
		var ortho := float(rc.get("ortho", ISO_ORTHO))
		var lift := float(rc.get("target_up_bu", 0.0))
		if rc.get("kind", "") != "iso":  # frame the model's middle: half its height, up the screen
			lift = 0.5 * float(e["footprint"]["max"][1]) * cos(deg_to_rad(cfg.pitch_deg))
		_cam.projection = Camera3D.PROJECTION_ORTHOGONAL
		_cam.size = ortho
		_cam.look_at_from_position(iso.up() * lift - iso.forward() * 2600.0, iso.up() * lift, Vector3.UP)
		_post.set_shader_parameter("ortho", ortho)
	var ground := get_node("ground") as MeshInstance3D
	ground.material_override = LandmarkMaterials.make("lm_toon", LOOK, StringName(s["corp"]), day)
	_frame = 0


func _process(_delta: float) -> void:
	if _shot < 0 or _shot >= _shots.size():
		return
	_frame += 1
	if _frame < SETTLE_FRAMES:
		return
	var s: Dictionary = _shots[_shot]
	var tag := String(s["entry"]["job"]) + ("_" + String(s["variant"]) if s["variant"] != "" else "")
	var path := "%s/%s_%s_%s.png" % [String(_args.get("out", "user://landmark_review")), tag, s["cam"], s["mode"]]
	get_viewport().get_texture().get_image().save_png(path)
	print("SHOT ", path)
	_next_shot()


static func _v3(c: Color) -> Vector3:
	return Vector3(c.r, c.g, c.b)
