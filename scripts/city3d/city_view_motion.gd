class_name CityViewMotion
extends Node
## ART-5 5c: puts the city's motion layers (CityMotionLayers) on 5a's one 3D city
## (CityView3D) through its scene-layer seam. Once the view's model is built it makes the
## site (CityMotionSite.from_model), builds the layers and moves their groups into the
## view's layers (traffic, sky, props, heat; traffic, sky and heat also in the ground-only
## pass under see-through buildings), then wires the view's signals down to them: the zoom
## (camera_changed: car LOD, sprite sizes, spill focus), the band (band_changed: GRID / RAID
## / NETRUN), the ambient scale (ambient_changed: 0 pauses every layer). Up from the layers:
## the light spill to `CityView3D.set_spill`, and the day / night look onto the view's city
## materials (the view has no day-look call yet: DECISIONS asks 5a for one). A view: no
## game state changes. Add it as a child of the CityView3D.

var view: CityView3D
var layers: CityMotionLayers
var motion_cfg: CityMotionConfigData
## The Cell's district centre (lots), where suspicion gathers.
var home_lot: Vector2 = Vector2.INF
var _night: Dictionary = {}


## A CityViewMotion for `p_view` with config `cfg` (the shipped one by default).
static func make(p_view: CityView3D, cfg: CityMotionConfigData = null, p_home_lot: Vector2 = Vector2.INF) -> CityViewMotion:
	var m := CityViewMotion.new()
	m.name = "CityMotion"
	m.view = p_view
	m.motion_cfg = cfg if cfg != null else CityMotionConfigData.shipped()
	m.home_lot = p_home_lot
	return m


func _ready() -> void:
	if view == null:
		view = get_parent() as CityView3D
	if motion_cfg == null:
		motion_cfg = CityMotionConfigData.shipped()
	if view.model != null and view.camera != null:
		_attach()
	else:
		view.model_ready.connect(_attach, CONNECT_ONE_SHOT)


func _attach() -> void:
	var site := CityMotionSite.from_model(view.model, view.cfg, home_lot)
	layers = CityMotionLayers.new()
	view.add_to_layer(&"fx", layers)
	var c := view.cfg
	_night = {"ramp": c.ramp.duplicate(), "sky": c.sky, "window_gain": c.window_gain, "neon_gain": c.neon_gain,
		"haze": c.haze, "grade": c.grade}
	layers.night_share_changed.connect(_on_night_share)
	layers.spill_changed.connect(_on_spill)
	layers.setup(motion_cfg, site, view.city_seed)
	for name_ in CityMotionLayers.GROUPS:
		var g: Node3D = layers.groups[name_]
		g.reparent(view.layer(name_), false)
	layers.set_ground_pass_layer(CityView3D.GROUND_LAYER)
	view.camera_changed.connect(_on_camera)
	view.band_changed.connect(_on_band)
	view.ambient_changed.connect(layers.set_host_ambient)
	layers.set_host_ambient(view.ambient_scale)
	if view.band >= 0:
		_on_band(view.band)
	if view.iso != null:
		_on_camera(view.iso)


func _on_camera(cam: CityIsoCamera) -> void:
	layers.set_ortho(cam.ortho, cam.viewport.x)
	layers.set_focus_point(cam.target)


## CityLod.Band (NETRUN, RAID, GRID) to the layers' view.
func _on_band(b: int) -> void:
	var v := CityMotionLayers.View.GRID
	if b == CityLod.Band.RAID:
		v = CityMotionLayers.View.RAID
	elif b == CityLod.Band.NETRUN:
		v = CityMotionLayers.View.NETRUN
	layers.set_view(v)


func _on_spill(sources: Array) -> void:
	view.set_spill(sources)


## The night look lerped toward the config's day look by night share `n` (1 night, 0 day).
func _on_night_share(n: float) -> void:
	var ramp: Array = _night["ramp"]
	var names := [&"ramp_shadow", &"ramp_mid", &"ramp_lit"]
	var mats: Array[ShaderMaterial] = []
	for key in ["_building_mat", "_ground_mat", "_lane_mat"]:
		var m: ShaderMaterial = view.get(key)
		if m != null:
			mats.append(m)
	for k in 3:
		var col := (motion_cfg.day_ramp[k] as Color).lerp(ramp[k], n)
		for m in mats:
			m.set_shader_parameter(names[k], Vector3(col.r, col.g, col.b))
	var b: ShaderMaterial = view.get("_building_mat")
	if b != null:
		b.set_shader_parameter(&"window_gain", lerpf(motion_cfg.day_window_gain, float(_night["window_gain"]), n))
		b.set_shader_parameter(&"neon_gain", lerpf(motion_cfg.day_neon_gain, float(_night["neon_gain"]), n))
	var post: ShaderMaterial = view.get("_post")
	if post != null:
		var hz := motion_cfg.day_haze.lerp(_night["haze"], n)
		post.set_shader_parameter(&"haze_color", Vector3(hz.r, hz.g, hz.b))
		var gr := motion_cfg.day_grade.lerp(_night["grade"], n)
		post.set_shader_parameter(&"grade", Vector3(gr.r, gr.g, gr.b))
		# Bible 4.2: no fog at raid zoom by day; rain is night rain only.
		var night := n >= 0.5
		post.set_shader_parameter(&"rain_on", bool(view.quality.get("rain", true)) and night)
		post.set_shader_parameter(&"fog_on", bool(view.quality.get("fog", true)) and (night or layers.view == CityMotionLayers.View.GRID))
	for ch in view.get_children():
		if ch is WorldEnvironment:
			(ch as WorldEnvironment).environment.background_color = motion_cfg.day_sky.lerp(_night["sky"], n)
