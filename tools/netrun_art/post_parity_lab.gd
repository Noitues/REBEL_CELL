extends Node
## L3 post parity lab (windowed only, through tools/run_windowed.py): one linear HDR frame through the real city_post aaa chain.
##   python tools/run_windowed.py --log <f> -- res://tools/netrun_art/post_parity_lab.tscn -- --in=<frame.f32> --w=960 --h=540
##     --out=<dir> [--exposure=2.4] [--modes=calib,nobloom,full,ca,grain]
## <frame.f32>: raw little-endian float32 RGB, row 0 = top (tools/netrun_art/post_parity.py writes it).
## Modes: calib (no post quad: checks the frame plumbing), nobloom (aaa with bloom weights 0), full (aaa), ca (aaa + chromatic
## aberration), grain (aaa + grain). Rain and wet reflections are off in every mode (they have no plate counterpart on a still).
## Writes <out>/<mode>.png and prints "POSTPAR <mode> <path>".

const SETTLE := 8

var _args: Dictionary = {}
var _modes: PackedStringArray = PackedStringArray()
var _step := -1
var _tick := 0
var _sv: SubViewport = null
var _post: MeshInstance3D = null
var _mat: ShaderMaterial = null


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	var w := int(_args.get("w", "960"))
	var h := int(_args.get("h", "540"))
	var raw := FileAccess.get_file_as_bytes(String(_args["in"]))
	var img := Image.create_from_data(w, h, false, Image.FORMAT_RGBF, raw)
	DirAccess.make_dir_recursive_absolute(String(_args["out"]))
	_modes = PackedStringArray(String(_args.get("modes", "calib,nobloom,full,ca,grain")).split(","))
	_sv = SubViewport.new()
	_sv.size = Vector2i(w, h)
	_sv.own_world_3d = true
	_sv.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_sv.msaa_3d = Viewport.MSAA_DISABLED
	_sv.screen_space_aa = Viewport.SCREEN_SPACE_AA_DISABLED
	_sv.use_taa = false
	_sv.use_debanding = false
	_sv.scaling_3d_scale = 1.0
	add_child(_sv)
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color.BLACK
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.tonemap_exposure = 1.0
	env.glow_enabled = false
	var we := WorldEnvironment.new()
	we.environment = env
	_sv.add_child(we)
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 10.0
	cam.attributes = CameraAttributesPractical.new()
	_sv.add_child(cam)
	cam.current = true
	var fm := ShaderMaterial.new()
	fm.shader = load("res://tools/netrun_art/post_parity_frame.gdshader")
	fm.set_shader_parameter(&"src", ImageTexture.create_from_image(img))
	_add_quad(cam, fm, -20.0)
	_mat = ShaderMaterial.new()
	_mat.shader = load("res://shaders/city/city_post.gdshader")
	_post = _add_quad(cam, _mat, -10.0)
	_next()


func _add_quad(cam: Camera3D, m: Material, z: float) -> MeshInstance3D:
	var qm := QuadMesh.new()
	qm.size = Vector2(2.0, 2.0)
	var mi := MeshInstance3D.new()
	mi.mesh = qm
	mi.material_override = m
	mi.extra_cull_margin = 16384.0
	mi.position = Vector3(0.0, 0.0, z)
	cam.add_child(mi)
	return mi


func _next() -> void:
	_step += 1
	_tick = 0
	if _step >= _modes.size():
		get_tree().quit()
		return
	var mode := _modes[_step]
	_post.visible = mode != "calib"
	NetrunShaderKitAaa.setup_post(_mat, true, float(_args.get("exposure", "2.4")))
	var p: Dictionary = NetrunShaderKitAaa.cfg()["post"]
	_mat.set_shader_parameter(&"aaa_rain_on", 0.0)
	_mat.set_shader_parameter(&"aaa_wr_on", false)
	_mat.set_shader_parameter(&"aaa_ca", Vector3(float(p["ca_px"]) if mode == "ca" else 0.0, float(p["ca_r0"]), float(p["ca_pow"])))
	_mat.set_shader_parameter(&"aaa_grain", Vector2(float(p["grain"]) if mode == "grain" else 0.0, float(p["grain_lum"])))
	if mode == "nobloom":
		_mat.set_shader_parameter(&"aaa_bloom_w", Vector3.ZERO)


func _process(_dt: float) -> void:
	if _step >= _modes.size():
		return
	_tick += 1
	if _tick < SETTLE:
		return
	var path := String(_args["out"]).path_join(_modes[_step] + ".png")
	_sv.get_texture().get_image().save_png(path)
	print("POSTPAR %s %s" % [_modes[_step], path])
	_next()
