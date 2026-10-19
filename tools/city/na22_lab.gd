extends Control
## NA-22 lab (windowed only, through tools/run_windowed.py): the netrun city shaders on the real CityView3D.
## User args:
##   --mode=hq|street        hq: the HQ page (iso, ortho) at each look_blend; street: a perspective street pose with
##                           the wet street, streak lanes, beams and the fog volume (the calibration frame)
##   --lb=0,0.5,1            look_blend values, one shot each
##   --shots=<dir>           output folder (a beauty PNG per look_blend; street also writes capture.json)
##   --size=WxH              window / frame size (default 1920x1080)
##   --pose=<file>           street: a golden plate capture.json (its `camera` block gives lens, yaw, pitch, dist, shift)
##   --at=<lotx>,<loty>      street: the lot the pose's target is moved onto
##   --fog=<k>               street: fog density multiplier (default 1), --emit=<k> fog emit gain, --peak=<k> peak
##   --exposure=<k>          street: a linear gain on the final frame (the plate's exposure solve)
##   --settle=<frames>
## Prints NA22 lines.

const CFG := preload("res://content/config/city_config.tres")
const SETTLE_DEFAULT := 60

var view: CityView3D
var _rect: TextureRect
var _args: Dictionary = {}
var _lbs: Array[float] = []
var _i: int = -1
var _frame: int = 0
var _extras: Array[Node3D] = []
var _mats: Array = []


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	if _args.get("freeze", "0") == "1":
		Settings.set_reduce_effects(true)
		Fx.apply_settings()
	var wh := String(_args.get("size", "1920x1080")).split("x")
	DisplayServer.window_set_size(Vector2i(int(wh[0]), int(wh[1])))
	for s in String(_args.get("lb", "0,0.5,1")).split(","):
		_lbs.append(float(s))
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	view = CityView3D.new()
	view.size = Vector2i(int(wh[0]), int(wh[1]))
	add_child(view)
	_rect = TextureRect.new()
	_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_rect.texture = view.get_texture()
	_rect.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(_rect)
	view.model_ready.connect(_next, CONNECT_ONE_SHOT)


func _next() -> void:
	_i += 1
	_frame = 0
	if _i >= _lbs.size():
		get_tree().quit()
		return
	var lb := _lbs[_i]
	view.set_look_blend(lb)
	if _args.get("old", "0") == "1":
		var sh := Shader.new()
		sh.code = FileAccess.get_file_as_string(String(_args.get("oldpath", "res://tests/fixtures/na22/city_building_before.gdshader.txt")))
		view.building_material().shader = sh
	if String(_args.get("mode", "hq")) == "street":
		_street(lb)
	else:
		var at := NeonCity.hq_of(&"halcyon") + Vector2(NeonCity.HQ_LOTS * 0.5, NeonCity.HQ_LOTS * 0.5) - CityLayout.RIGHT * 11.0
		view.set_iso(CityIsoCamera.make(CFG, view.lot_world(at), 220.0, Vector2(view.size)))
	print("NA22 state lb=%s" % lb)


func _street(lb: float) -> void:
	for n in _extras:
		n.queue_free()
	_extras.clear()
	_mats.clear()
	var cam: Dictionary = {"loc": [110.5336, -99.1988, 9.7002], "tgt": [96.1767, 14.4483, 5.7], "lens": 28.0, "shift_x": -0.0548, "shift_y": 0.1172,
		"yaw": 97.0, "pitch": 5.0, "dist": 114.6201}
	if _args.has("pose"):
		cam = (JSON.parse_string(FileAccess.get_file_as_string(String(_args["pose"]))) as Dictionary)["camera"]
	for k in ["yaw", "pitch", "dist", "lens"]:
		if _args.has(k):
			cam[k] = float(_args[k])
	var pose := NetrunPose.from_json(cam)
	var at_s := String(_args.get("at", "auto")).split(",")
	var cam_lot := Vector2(34.5, 22.5)
	if at_s[0] == "auto":
		# The longest east-west street (along lot i) near the district centre: the camera stands on it.
		var rows: Dictionary = {}
		for s: Dictionary in view.model.streets:
			var l: Vector2i = s["lot"]
			if bool(s["along_i"]) and l.x >= 14 and l.x <= 54 and l.y >= 8 and l.y <= 36:
				rows[l.y] = int(rows.get(l.y, 0)) + 1
		var best_j := 22
		var best_n := -1
		var keys: Array = rows.keys()
		keys.sort()
		for j: int in keys:
			if int(rows[j]) > best_n:
				best_n = int(rows[j])
				best_j = j
		cam_lot = Vector2(34.5, float(best_j) + 0.5)
		print("NA22 street row ", best_j, " tiles ", best_n)
	else:
		cam_lot = Vector2(float(at_s[0]), float(at_s[1]))
	var cam_w: Vector3 = view.lot_world(cam_lot)
	var dr: Array = pose.dir()
	var dd: float = pose.dist
	# The camera stands on the street at the pose's height; the focus is dist ahead along the pose's view direction.
	pose.F = [cam_w.x + float(dr[0]) * dd, -cam_w.z + float(dr[1]) * dd, float(cam["loc"][2]) + float(dr[2]) * dd]
	NetrunFrustum.apply(view.camera, pose, 0.5, 3000.0)
	view.camera.current = true
	var env: Environment = view._env
	NetrunShaderKit.configure_environment(env)
	if _args.has("exposure"):
		env.tonemap_exposure = float(_args["exposure"])
	var street_a := Vector2(cam_w.x - 60.0, -cam_w.z)
	var street_c := Vector2(cam_w.x + 60.0, -cam_w.z)
	var fog_k := float(_args.get("fog", "1"))
	var fv := NetrunShaderKit.fog_volume(Vector3(cam_w.x, 0.0, cam_w.z))
	var fm := fv.material as ShaderMaterial
	fm.set_shader_parameter(&"look_blend", lb)
	fm.set_shader_parameter(&"density_mul", fog_k)
	fm.set_shader_parameter(&"emit_gain", float(_args.get("emit", "40")))
	fm.set_shader_parameter(&"peak", float(NetrunShaderKit.fog_material().get_shader_parameter(&"peak")) * float(_args.get("peak", "1")))
	fm.set_shader_parameter(&"sec_a", street_a)
	fm.set_shader_parameter(&"sec_c", street_c)
	fm.set_shader_parameter(&"sec_nrm", Vector2(0.0, 1.0))
	fm.set_shader_parameter(&"front_sym", 1.0)
	view.add_to_layer(&"props", fv)
	_extras.append(fv)
	_mats.append(fm)
	# Fog-only lights (the rule's cityglow): energy 0, volumetric energy only.
	for k in 6:
		var l := OmniLight3D.new()
		l.light_energy = 0.0
		l.light_volumetric_fog_energy = float(_args.get("glow", "6"))
		l.omni_range = 90.0
		l.light_color = Color(1.0, 0.16, 0.6) if k % 2 == 0 else Color(0.16, 0.8, 1.0)
		l.position = Vector3(cam_w.x + 10.0 + float(k) * 14.0, 12.0, cam_w.z + (9.0 if k % 2 == 0 else -9.0))
		view.add_to_layer(&"props", l)
		_extras.append(l)
	# Four traffic lanes (deterministic streaks) along the street, two each way.
	for ln in 4:
		var y: float = (-cam_w.z) + [-1.9, -0.9, 0.9, 1.9][ln]
		var streaks: Array = []
		for s in 6:
			streaks.append({"u0": float(s) * 21.0 + float(ln) * 4.0, "len": 6.0 + float((s * 5 + ln * 3) % 10), "gap": 10.0, "bright": 0.6 + 0.1 * float((s + ln) % 6)})
		var lane := {"a": [cam_w.x - 60.0, y], "b": [cam_w.x + 60.0, y], "z": 0.5, "speed": 30.0, "streaks": streaks}
		var col := Color(1.0, 0.85, 0.6) if ln < 2 else Color(1.0, 0.2, 0.15)
		var node := NetrunShaderKit.streak_node(lane, col, 1.0 if ln < 2 else -1.0)
		view.add_to_layer(&"props", node)
		_extras.append(node)
		_mats.append(node.material_override)
	# Three beams.
	for b in 3:
		var beam := {"pos": [cam_w.x + 45.0 + float(b) * 30.0, (-cam_w.z) + (10.0 if b % 2 == 0 else -10.0), 16.0], "lean": [4.0 + float(b), 7.0], "sweep_deg": 5.0, "phase": 0.3 * float(b)}
		var col2: Color = [Color(1.0, 0.16, 0.6), Color(0.16, 0.8, 1.0), Color(1.0, 0.58, 0.18)][b]
		var node2 := NetrunShaderKit.beam_node(beam, col2, 14.0)
		view.add_to_layer(&"props", node2)
		_extras.append(node2)
		_mats.append(node2.material_override)
	for m in _mats:
		(m as ShaderMaterial).set_shader_parameter(&"look_blend", lb)
	NetrunShaderKit.set_clock(_mats, 0.0, 0.0)


func _process(_delta: float) -> void:
	if _i < 0 or _i >= _lbs.size():
		return
	_frame += 1
	if _frame == int(_args.get("settle", str(SETTLE_DEFAULT))):
		var img := view.get_texture().get_image()
		var name := "%s_lb%s" % [String(_args.get("mode", "hq")), str(_lbs[_i]).replace(".", "p")]
		var dir := String(_args.get("shots", "user://na22"))
		DirAccess.make_dir_recursive_absolute(dir)
		var folder := "%s/%s" % [dir, name]
		DirAccess.make_dir_recursive_absolute(folder)
		img.save_png("%s/beauty.png" % folder)
		var cap := {"version": 1, "kind": "street" if String(_args.get("mode", "hq")) == "street" else "hq", "view": "overview", "look": "blend" if _lbs[_i] > 0.0 and _lbs[_i] < 1.0 else ("aaa2" if _lbs[_i] >= 1.0 else "mainline"),
			"look_blend": _lbs[_i], "corp": "", "resolution": [img.get_width(), img.get_height()], "layout_seed": str(CFG.city_seed), "run": "na22_lab", "anim_t": 0.0,
			"exempt": {"hover_cut": false, "red_seq": false, "flash": false}}
		FileAccess.open("%s/capture.json" % folder, FileAccess.WRITE).store_string(JSON.stringify(cap, "\t"))
		print("NA22 shot %s %dx%d" % [folder, img.get_width(), img.get_height()])
		_next()
