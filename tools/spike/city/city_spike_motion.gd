class_name CitySpikeMotion
extends RefCounted
## ART-5 5c: a test host for the city's motion layers (CityMotionLayers) on 1D's spike city
## (`city_spike_3d.tscn`), for windowed render checks next to 5a's CityView3D (the game's
## host is CityViewMotion).
## `attach` builds the site from the spike's district (CityMotionSite.from_district), adds
## the layers at the spike's world origin, retires the spike's own prototype car tiers, and
## wires the layers' signals up to the spike's look: the fog / rain clock, the day / night
## look (the night look lerped toward CityMotionConfigData's day look), and the light spill
## onto the spike's building and ground materials (CityMaterials.set_spill).
## Calls down only: the spike never changes game state either.

const GROUND_SHADER := preload("res://shaders/city/city_ground.gdshader")

var spike: Node3D
var layers: CityMotionLayers
var motion_cfg: CityMotionConfigData
var _night: Dictionary = {}
var _ground_mats: Array[ShaderMaterial] = []
var _env: Environment


## Attaches the motion layers to `p_spike` (after its _ready), the Cell's home at `home_lot`.
static func attach(p_spike: Node3D, cfg: CityMotionConfigData, home_lot: Vector2) -> CitySpikeMotion:
	var m := CitySpikeMotion.new()
	m.spike = p_spike
	m.motion_cfg = cfg
	var spike_cfg: CityConfig = p_spike.get("cfg")
	var site := CityMotionSite.from_district(p_spike.get("district"), spike_cfg, home_lot)
	for mi: MultiMeshInstance3D in p_spike.get("_car_tiers"):
		mi.queue_free()
	(p_spike.get("_car_tiers") as Array).clear()
	(p_spike.get("_car_mats") as Array).clear()
	m.layers = CityMotionLayers.new()
	m.layers.name = "CityMotion"
	p_spike.add_child(m.layers)
	for c in p_spike.get_children():
		if c is MeshInstance3D and (c as MeshInstance3D).material_override is ShaderMaterial:
			var sm := (c as MeshInstance3D).material_override as ShaderMaterial
			if sm.shader == GROUND_SHADER:
				m._ground_mats.append(sm)
		if c is WorldEnvironment:
			m._env = (c as WorldEnvironment).environment
	m._night = {"ramp": spike_cfg.ramp.duplicate(), "sky": spike_cfg.sky, "window_gain": spike_cfg.window_gain,
		"neon_gain": spike_cfg.neon_gain, "haze": spike_cfg.haze, "grade": spike_cfg.grade}
	m.layers.ambient_scale_changed.connect(m._on_ambient_scale)
	m.layers.night_share_changed.connect(m._on_night_share)
	m.layers.spill_changed.connect(m._on_spill)
	m.layers.setup(cfg, site, spike_cfg.city_seed)
	return m


## Applies the spike's zoom and the layers' LOD together.
func set_ortho(ortho: float) -> void:
	spike.call("set_ortho", ortho)
	layers.set_ortho(ortho, spike.get_viewport().get_visible_rect().size.x)
	var iso: CityIsoCamera = spike.get("iso")
	layers.set_focus_point(iso.target)


func _on_spill(sources: Array) -> void:
	var mats: Array[ShaderMaterial] = [spike.get("_building_mat")]
	mats.append_array(_ground_mats)
	CityMaterials.set_spill(mats, sources)


func _on_ambient_scale(scale: float) -> void:
	var post: ShaderMaterial = spike.get("_post")
	if post != null:
		post.set_shader_parameter(&"time_scale", scale)


func _on_night_share(n: float) -> void:
	var ramp: Array = _night["ramp"]
	var names := [&"ramp_shadow", &"ramp_mid", &"ramp_lit"]
	var mats: Array[ShaderMaterial] = [spike.get("_building_mat"), spike.get("_lane_mat")]
	mats.append_array(_ground_mats)
	for k in 3:
		var c := (motion_cfg.day_ramp[k] as Color).lerp(ramp[k], n)
		for m in mats:
			if m != null:
				m.set_shader_parameter(names[k], Vector3(c.r, c.g, c.b))
	var b: ShaderMaterial = spike.get("_building_mat")
	if b != null:
		b.set_shader_parameter(&"window_gain", lerpf(motion_cfg.day_window_gain, float(_night["window_gain"]), n))
		b.set_shader_parameter(&"neon_gain", lerpf(motion_cfg.day_neon_gain, float(_night["neon_gain"]), n))
	var post: ShaderMaterial = spike.get("_post")
	if post != null:
		var hz := motion_cfg.day_haze.lerp(_night["haze"], n)
		post.set_shader_parameter(&"haze_color", Vector3(hz.r, hz.g, hz.b))
		var gr := motion_cfg.day_grade.lerp(_night["grade"], n)
		post.set_shader_parameter(&"grade", Vector3(gr.r, gr.g, gr.b))
		# Bible 4.2: day has no fog at raid zoom (nor rain: night rain only).
		var quality: Dictionary = spike.get("quality")
		var night := n >= 0.5
		post.set_shader_parameter(&"rain_on", bool(quality.get("rain", true)) and night)
		post.set_shader_parameter(&"fog_on", bool(quality.get("fog", true)) and (night or layers.view == CityMotionLayers.View.GRID))
	if _env != null:
		_env.background_color = motion_cfg.day_sky.lerp(_night["sky"], n)
