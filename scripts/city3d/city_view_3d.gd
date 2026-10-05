class_name CityView3D
extends SubViewport
## ART-5 5a: the one 3D city (bible §4.1 "one model, one camera", §6.1): the whole CityModel
## rendered by one orthographic Camera3D (CityIsoCamera), hosting the City Grid, raid,
## netrun and HQ-run views by zoom band (CityLod.band) with no scene change. A SubViewport
## (its own World3D) whose texture the 2D host draws (NeonCity in city-3D mode on the Grid).
##
## Built from 1D's spike scene: a WorldEnvironment with no ambient and no glow, one key
## light (`to_light`), the building families as MultiMeshes PER CHUNK (frustum culling) with
## LOD0/1/2 meshes swapped by camera ortho with hysteresis (CityLod.building_lod), ground and
## lane glow per chunk on render layers 1 and 2, the post quad (ink, see-through composite,
## spill, bloom, fog, haze, rain, grade), and a half-resolution ground-only pass (layer 2)
## that the post shows under see-through buildings (1D's band lod 1.50-1.595 from config).
## The network ground decal (CityNetworkData) draws on layer 2 with an x-ray pass.
##
## SEAMS for the other city agents (DECISIONS "Art direction — ART-5 5a city model"):
## - Scene layers: `layer(name)` returns the Node3D of a named layer (LAYERS: ground,
##   network, buildings, landmarks, props, traffic, sky, heat, fx); `add_to_layer(name,
##   node, ground_pass)` parents a node there (ground_pass: also drawn in the ground-only
##   pass, so it shows under see-through buildings). `camera_changed(iso)` /
##   `band_changed(band)` / `building_lod_changed(lod)` tell layers the zoom;
##   `ambient_scale` (0 paused or frozen, 1 live) with `ambient_changed` drives every
##   ambient layer (map covered, window unfocused, reduce effects / reduce motion).
##   `landmark_slot(corp)` / `hide_stand_in(corp)` place a landmark on its HQ lot.
## - Picking (pure, by this viewport's pixels): `pick(p)` -> {"prism", "building", "cell",
##   "lot", "terr", "world"}, `lot_at(p)`, `project(world)`, `unproject(p, height)`,
##   `top_at(lot)`, `lot_world(lot, height)`.
## A view: it never changes game state.

signal camera_changed(cam: CityIsoCamera)
signal band_changed(band: int)
signal building_lod_changed(lod: int)
signal ambient_changed(scale: float)
## The model is built and its chunks are placed (layers can read `model`).
signal model_ready

const CONFIG := preload("res://content/config/city_config.tres")
## Render layers (bit numbers): 1 the world, 2 the ground-only pass under see-through.
const WORLD_LAYER := 1
const GROUND_LAYER := 2
## The scene layers, bottom to top (bible §4.2 order where it applies).
const LAYERS: Array[StringName] = [&"ground", &"network", &"buildings", &"landmarks", &"props", &"traffic", &"sky",
	&"heat", &"fx"]
## Chunks given nodes per frame while the city fills in (nearest the camera first).
const CHUNKS_PER_FRAME := 6
## The ground beyond the city rect (BU, a plane under it all).
const OUTER_GROUND_BU := 8000.0
## Margin (BU) the network decal's quad keeps round the network.
const NET_MARGIN_BU := 60.0

var cfg: CityConfig = CONFIG
## The layout's look seed (NeonCity.city_seed: the game's city is seed 7 everywhere).
var city_seed: int = 7
var model: CityModel = null
var iso: CityIsoCamera = null
var camera: Camera3D
var quality: Dictionary = {}
var building_lod: int = -1
var band: int = -1
## 0 paused / frozen .. 1 live (every ambient layer follows it).
var ambient_scale: float = 1.0
## The host covers the map (a full panel over it): ambient layers pause, nothing renders.
var covered: bool = false:
	set(v):
		if v != covered:
			covered = v
			_sync_ambient()
			_sync_update()
var network: CityNetworkData = null
## The view band the host holds whatever the zoom (-1: by zoom, CityLod.band). The City
## Grid holds Band.GRID: solid buildings and the city's full life at any player zoom (the
## raid and netrun views take theirs by zoom when they move onto the city).
var band_lock: int = -1:
	set(v):
		if v != band_lock:
			band_lock = v
			if iso != null and camera != null:
				set_iso(iso)

var _layers: Dictionary = {}
var _chunks: Dictionary = {}  # Vector2i -> {"families": {int: MultiMeshInstance3D}, "ground": MeshInstance3D}
var _pending: Array[Vector2i] = []
var _hidden_hq: Dictionary = {}
## World X/Z rects whose procedural buildings give way to a landmark's own (the art pass's
## glTF stands there instead: never two cities on one lot).
var _cleared: Array[Rect2] = []
## The landmarks placed (corp -> Node3D), 5b's glTFs.
var landmarks: Dictionary = {}
var _inks: Array[Color] = []
var _building_mat: ShaderMaterial
var _ground_mat: ShaderMaterial
var _lane_mat: ShaderMaterial
var _post: ShaderMaterial
var _ground_vp: SubViewport
var _ground_cam: Camera3D
var _sun: DirectionalLight3D
var _net_mi: MeshInstance3D
var _net_xray_mi: MeshInstance3D
var _net_mat: ShaderMaterial
var _net_xray_mat: ShaderMaterial
var _focused: bool = true

## Async model builds in flight, by config path and seed: {"task", "recs", "keys", "rects"}.
static var _jobs: Dictionary = {}


## True where a 3D city can be drawn (not the headless test runner).
static func can_render() -> bool:
	return DisplayServer.get_name() != "headless"


func _init() -> void:
	own_world_3d = true
	transparent_bg = false
	handle_input_locally = false
	gui_disable_input = true
	render_target_update_mode = SubViewport.UPDATE_ALWAYS
	msaa_3d = Viewport.MSAA_DISABLED
	for n in LAYERS:
		var l := Node3D.new()
		l.name = String(n).capitalize().replace(" ", "")
		_layers[n] = l
		add_child(l)


func _ready() -> void:
	quality = CityLod.quality(cfg, Settings.city_quality)
	_build_scene()
	Settings.changed.connect(_sync_ambient)
	_sync_ambient()
	if iso == null:
		set_iso(CityIsoCamera.make(cfg, Vector3.ZERO, cfg.grid_ortho, Vector2(size)))
	if model != null:
		_on_model(model)
	else:
		_start_model()


func _notification(what: int) -> void:
	match what:
		NOTIFICATION_APPLICATION_FOCUS_OUT:
			_focused = false
			_sync_ambient()
		NOTIFICATION_APPLICATION_FOCUS_IN:
			_focused = true
			_sync_ambient()


# --- Scene layer API --------------------------------------------------------------------------

## The Node3D of scene layer `layer_name` (one of LAYERS).
func layer(layer_name: StringName) -> Node3D:
	return _layers.get(layer_name)


## Parents `node` under layer `layer_name`; `ground_pass`: its visual instances also draw
## in the ground-only pass (seen under see-through buildings).
func add_to_layer(layer_name: StringName, node: Node3D, ground_pass: bool = false) -> void:
	layer(layer_name).add_child(node)
	if ground_pass:
		set_ground_pass(node, true)


## Puts every VisualInstance3D in `node`'s branch in (or out of) the ground-only pass.
static func set_ground_pass(node: Node, on: bool) -> void:
	if node is VisualInstance3D:
		var vi := node as VisualInstance3D
		vi.set_layer_mask_value(GROUND_LAYER, on)
	for c in node.get_children():
		set_ground_pass(c, on)


## Where corporation `corp`'s landmark stands: its HQ lot's centre on the ground, facing
## the camera's yaw (Transform3D() when the city has no such HQ).
func landmark_slot(corp: StringName) -> Transform3D:
	if model == null or not model.hqs.has(corp):
		return Transform3D()
	var r: Rect2i = model.hqs[corp]
	return Transform3D(Basis(), lot_world(Vector2(r.get_center())))


## Hides (or shows again) the stepped stand-in tower on `corp`'s HQ lot (a landmark took
## its place).
func hide_stand_in(corp: StringName, hidden: bool = true) -> void:
	if hidden == _hidden_hq.has(corp):
		return
	if hidden:
		_hidden_hq[corp] = true
	else:
		_hidden_hq.erase(corp)
	if model == null or not model.hqs.has(corp):
		return
	var r: Rect2i = model.hqs[corp]
	var c := Vector2(r.get_center())
	var key := Vector2i(floori(c.x / cfg.chunk_lots), floori(c.y / cfg.chunk_lots))
	if _chunks.has(key):
		_free_chunk(key)
		_build_chunk(key)


## Sets light spill sources (LightSpill.uniforms_3d input) on the buildings and streets.
func set_spill(sources: Array) -> void:
	CityMaterials.set_spill([_building_mat, _ground_mat], sources)


## ART-5 5e: true while the host pauses the city's ambience (the map covered or the window
## unfocused). Reduce effects / reduce motion are not a pause: the layers apply their own
## rules (end state; street traffic at 40 % without streaks, bible 5.4).
func host_paused() -> bool:
	return covered or not _focused


## ART-5 5e: the day-look call (5c's open question to 5a). Lerps the city's night look (the
## config's ramp, sky, window and neon gains, haze and grade) toward `day` by night share
## `n` (1 night .. 0 day), on the buildings, streets, post and sky, and switches the
## landmarks' materials to their day or night look. `day` keys: "ramp" (3 Colors: shadow,
## mid, lit), "sky", "window_gain", "neon_gain", "haze", "grade" (CityViewMotion.day_look
## builds it from the motion config). By day there is no rain, and no fog below the Grid.
func set_night_share(n: float, day: Dictionary) -> void:
	night_share = clampf(n, 0.0, 1.0)
	if _building_mat == null or day.is_empty():
		return
	var names: Array[StringName] = [&"ramp_shadow", &"ramp_mid", &"ramp_lit"]
	var day_ramp: Array = day["ramp"]
	for k in 3:
		var col := (day_ramp[k] as Color).lerp(cfg.ramp[k], night_share)
		for m in [_building_mat, _ground_mat, _lane_mat]:
			(m as ShaderMaterial).set_shader_parameter(names[k], Vector3(col.r, col.g, col.b))
	_building_mat.set_shader_parameter(&"window_gain", lerpf(float(day["window_gain"]), cfg.window_gain, night_share))
	_building_mat.set_shader_parameter(&"neon_gain", lerpf(float(day["neon_gain"]), cfg.neon_gain, night_share))
	var hz := (day["haze"] as Color).lerp(cfg.haze, night_share)
	_post.set_shader_parameter(&"haze_color", Vector3(hz.r, hz.g, hz.b))
	var gr := (day["grade"] as Color).lerp(cfg.grade, night_share)
	_post.set_shader_parameter(&"grade", Vector3(gr.r, gr.g, gr.b))
	var night := night_share >= 0.5
	_post.set_shader_parameter(&"rain_on", bool(quality.get("rain", true)) and night)
	_post.set_shader_parameter(&"fog_on", bool(quality.get("fog", true)) and (night or band == CityLod.Band.GRID))
	_env.background_color = (day["sky"] as Color).lerp(cfg.sky, night_share)
	if night != _landmarks_night:
		_landmarks_night = night
		_restyle_landmarks()


## The share of the night look the city shows (1 night .. 0 day; set_night_share).
var night_share: float = 1.0
var _landmarks_night: bool = true
var _env: Environment


# --- Picking API ------------------------------------------------------------------------------

## What is under pixel `p` of this viewport ({} until the model is built).
func pick(p: Vector2) -> Dictionary:
	if model == null or iso == null:
		return {}
	return model.pick_info(iso, p)


## The ground lot under pixel `p`.
func lot_at(p: Vector2) -> Vector2i:
	var l := CityIsoCamera.world_to_lot(cfg, iso.unproject(p, 0.0))
	return Vector2i(floori(l.x), floori(l.y))


## The pixel of world point `w`.
func project(w: Vector3) -> Vector2:
	return iso.project(w)


## The world point at `height` under pixel `p`.
func unproject(p: Vector2, height: float = 0.0) -> Vector3:
	return iso.unproject(p, height)


## The world point of lot point `lot` (lots, not lot centres) at `height` BU.
func lot_world(lot: Vector2, height: float = 0.0) -> Vector3:
	return CityIsoCamera.lot_to_world(cfg, lot, height)


## The tallest roof (BU) over lot `lot` (0 before the model is built).
func top_at(lot: Vector2i) -> float:
	return model.top_at(lot) if model != null else 0.0


# --- Camera -----------------------------------------------------------------------------------

## Points the camera (`cam`'s target and ortho; its viewport is this viewport's size) and
## applies the zoom's LOD, see-through band, lane glow and network look.
func set_iso(cam: CityIsoCamera) -> void:
	iso = cam.copy()
	iso.viewport = Vector2(size)
	if camera == null:
		return
	camera.global_transform = iso.transform()
	camera.size = iso.ortho
	_ground_cam.global_transform = camera.global_transform
	_ground_cam.size = iso.ortho
	var lod := CityIsoCamera.lod_of(cfg, iso.ortho)
	if band_lock == CityLod.Band.GRID:
		lod = maxf(lod, cfg.see_through_lod_to)
	var op := CityLod.opacity(cfg, lod)
	var city := CityLod.city_share(cfg, lod)
	_post.set_shader_parameter("opacity", op)
	_post.set_shader_parameter("has_ground", op < 0.999)
	_ground_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS if op < 0.999 and not covered else SubViewport.UPDATE_DISABLED
	_post.set_shader_parameter("ortho", iso.ortho)
	_post.set_shader_parameter("ink_alpha", cfg.ink_alpha_near if iso.ortho < cfg.car_far_above else cfg.ink_alpha_far)
	_post.set_shader_parameter("fog_city", city)
	_lane_mat.set_shader_parameter("lane_gain", lerpf(cfg.lane_glow_management, 1.0, city))
	_building_mat.set_shader_parameter("detail", CityLod.detail(cfg, iso.ortho))
	for m in [_net_mat, _net_xray_mat]:
		(m as ShaderMaterial).set_shader_parameter("bu_per_px", iso.bu_per_px())
		(m as ShaderMaterial).set_shader_parameter("city_share", city)
	_net_xray_mat.set_shader_parameter("strength", lerpf(1.0, cfg.net_xray, city))
	var lod_now := CityLod.building_lod(cfg, iso.ortho, building_lod)
	if lod_now != building_lod:
		building_lod = lod_now
		_apply_building_lod()
		building_lod_changed.emit(building_lod)
	var band_now := band_lock if band_lock >= 0 else CityLod.band(cfg, iso.ortho, band)
	if band_now != band:
		band = band_now
		band_changed.emit(band)
	camera_changed.emit(iso)


## Resizes the viewport (and the ground pass) to `px` and keeps the camera's frame.
func set_view_size(px: Vector2i) -> void:
	px = px.max(Vector2i(2, 2))
	if px == size:
		return
	size = px
	if _ground_vp != null:
		_ground_vp.size = (Vector2(px) * cfg.ground_pass_scale).max(Vector2(2, 2))
	if iso != null:
		set_iso(iso)


# --- Network decal ----------------------------------------------------------------------------

## Shows network `d` on the ground (null: none). Read-only data (CityNetworkData).
func set_network(d: CityNetworkData) -> void:
	network = d
	if _net_mi == null:
		return
	var on := d != null and (not d.nodes.is_empty() or not d.segments.is_empty())
	_net_mi.visible = on
	_net_xray_mi.visible = on
	if not on:
		return
	var nodes_tex := ImageTexture.create_from_image(d.node_image(cfg.net_nodes_max))
	var segs_tex := ImageTexture.create_from_image(d.segment_image(cfg.net_points_max))
	for m in [_net_mat, _net_xray_mat]:
		var sm := m as ShaderMaterial
		sm.set_shader_parameter("nodes_tex", nodes_tex)
		sm.set_shader_parameter("segs_tex", segs_tex)
		sm.set_shader_parameter("node_count", mini(d.nodes.size(), cfg.net_nodes_max))
		sm.set_shader_parameter("seg_count", mini(d.segments.size(), cfg.net_points_max))
	var b := d.bounds().grow(NET_MARGIN_BU)
	var pm := PlaneMesh.new()
	pm.size = b.size
	_net_mi.mesh = pm
	_net_xray_mi.mesh = pm
	var at := Vector3(b.get_center().x, cfg.lane_stroke_bu, b.get_center().y)
	_net_mi.position = at
	_net_xray_mi.position = at


# --- Ambient (pause, reduce effects / motion) -----------------------------------------------

func _sync_ambient() -> void:
	var live := not covered and _focused and not Settings.reduce_effects and not Settings.reduce_motion
	var s := 1.0 if live else 0.0
	if _post != null:
		_post.set_shader_parameter("time_scale", s)
		_net_mat.set_shader_parameter("time_scale", s)
		_net_xray_mat.set_shader_parameter("time_scale", s)
	if not is_equal_approx(s, ambient_scale):
		ambient_scale = s
		ambient_changed.emit(s)


func _sync_update() -> void:
	render_target_update_mode = SubViewport.UPDATE_DISABLED if covered else SubViewport.UPDATE_ALWAYS
	if iso != null and camera != null:
		set_iso(iso)


# --- Building ---------------------------------------------------------------------------------

func _build_scene() -> void:
	var env := Environment.new()
	_env = env
	env.background_mode = Environment.BG_COLOR
	env.background_color = cfg.sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_DISABLED
	env.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.glow_enabled = false
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	_sun = DirectionalLight3D.new()
	add_child(_sun)
	_sun.look_at_from_position(Vector3.ZERO, -cfg.to_light, Vector3.UP)
	_sun.shadow_enabled = quality["shadows"]
	_sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	_sun.directional_shadow_max_distance = cfg.camera_far * 0.5
	if can_render():
		RenderingServer.directional_shadow_atlas_set_size(int(quality["shadow_size"]), true)
	scaling_3d_scale = float(quality["render_scale"])
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	camera.near = 1.0
	camera.far = cfg.camera_far
	add_child(camera)
	camera.current = true
	_ground_vp = SubViewport.new()
	_ground_vp.name = "GroundPass"
	_ground_vp.size = (Vector2(size) * cfg.ground_pass_scale).max(Vector2(2, 2))
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
	_ground_cam.current = true
	_building_mat = CityMaterials.building(cfg, _inks)
	_ground_mat = CityMaterials.ground(cfg, false)
	_lane_mat = CityMaterials.ground(cfg, true)
	var outer := MeshInstance3D.new()
	outer.name = "OuterGround"
	# The ground shader takes its colour from the vertices (asphalt).
	var h := OUTER_GROUND_BU * 0.5
	outer.mesh = CityMeshKit.ground_mesh_of(cfg, Rect2(-h, -h, OUTER_GROUND_BU, OUTER_GROUND_BU), [], [])
	outer.position = Vector3(0, -0.05, 0)
	var om := CityMaterials.ground(cfg, false)
	outer.material_override = om
	outer.layers = (1 << (WORLD_LAYER - 1)) | (1 << (GROUND_LAYER - 1))
	layer(&"ground").add_child(outer)
	_post = CityMaterials.post(cfg, quality, _ground_vp.get_texture())
	var qm := QuadMesh.new()
	qm.size = Vector2(2, 2)
	var post_mi := MeshInstance3D.new()
	post_mi.name = "Post"
	post_mi.mesh = qm
	post_mi.material_override = _post
	post_mi.extra_cull_margin = 16384.0
	post_mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	post_mi.layers = 1 << (WORLD_LAYER - 1)
	camera.add_child(post_mi)
	post_mi.position = Vector3(0, 0, -10)
	_net_mat = CityMaterials.network(cfg, false)
	_net_xray_mat = CityMaterials.network(cfg, true)
	_net_mi = MeshInstance3D.new()
	_net_mi.name = "NetworkDecal"
	_net_mi.material_override = _net_mat
	_net_mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_net_mi.layers = (1 << (WORLD_LAYER - 1)) | (1 << (GROUND_LAYER - 1))
	_net_mi.visible = false
	layer(&"network").add_child(_net_mi)
	_net_xray_mi = MeshInstance3D.new()
	_net_xray_mi.name = "NetworkXray"
	_net_xray_mi.material_override = _net_xray_mat
	_net_xray_mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_net_xray_mi.layers = 1 << (WORLD_LAYER - 1)
	_net_xray_mi.visible = false
	layer(&"network").add_child(_net_xray_mi)
	if network != null:
		set_network(network)


## Uses model `m` (tests and tools: a part of the city; before or after entering the tree).
func use_model(m: CityModel) -> void:
	model = m
	if camera != null:
		_on_model(m)


func _start_model() -> void:
	var m := CityModel.shared_if_built(cfg, city_seed)
	if m != null:
		_on_model(m)
		return
	var k := "%s|%d" % [cfg.resource_path, city_seed]
	if not _jobs.has(k):
		var keys := CityModel.chunk_keys(cfg, cfg.city_rect)
		var recs: Array[CityLayoutRecorder] = []
		var rects: Array[Rect2i] = []
		for key in keys:
			recs.append(CityModel.recorder(city_seed))
			rects.append(CityModel.chunk_rect(cfg, key))
		var task := WorkerThreadPool.add_group_task(func(i: int) -> void: recs[i].record(rects[i]), keys.size(), -1, true,
			"CityModel")
		_jobs[k] = {"task": task, "recs": recs, "keys": keys, "rects": rects}
	set_process(true)


func _process(_delta: float) -> void:
	if model == null:
		_poll_model()
		return
	var n := 0
	while not _pending.is_empty() and n < CHUNKS_PER_FRAME:
		_build_chunk(_pending.pop_front())
		n += 1
	if _pending.is_empty():
		set_process(false)
		model_ready.emit()


func _poll_model() -> void:
	var m := CityModel.shared_if_built(cfg, city_seed)
	if m != null:
		_on_model(m)
		return
	var k := "%s|%d" % [cfg.resource_path, city_seed]
	var job: Dictionary = _jobs.get(k, {})
	if job.is_empty() or not WorkerThreadPool.is_group_task_completed(int(job["task"])):
		return
	WorkerThreadPool.wait_for_group_task_completion(int(job["task"]))
	_jobs.erase(k)
	m = CityModel.new()
	m.cfg = cfg
	m.city_seed = city_seed
	var recs: Array[CityLayoutRecorder] = job["recs"]
	var keys: Array[Vector2i] = job["keys"]
	var rects: Array[Rect2i] = job["rects"]
	for i in keys.size():
		m.add_recording(keys[i], rects[i], recs[i])
		recs[i].free()
	m.finish()
	CityModel.keep_shared(m)
	_on_model(m)


## Takes model `m` and queues its chunks, nearest the camera first.
func _on_model(m: CityModel) -> void:
	model = m
	for key: Vector2i in _chunks.keys():
		_free_chunk(key)
	_inks = CityMeshKit.ink_palette(m.prisms)
	CityMaterials.set_inks(_building_mat, _inks)
	if iso != null:
		set_iso(iso)
	if can_render():
		place_landmarks()
	_pending = m.keys()
	var at := Vector2(iso.target.x, iso.target.z) if iso != null else Vector2.ZERO
	_pending.sort_custom(func(a: Vector2i, b: Vector2i) -> bool:
		var da := _chunk_centre(a).distance_squared_to(at)
		var db := _chunk_centre(b).distance_squared_to(at)
		if not is_equal_approx(da, db):
			return da < db
		return a.y < b.y if a.y != b.y else a.x < b.x)
	if not can_render():
		# Headless: the model answers picking; nothing is drawn.
		_pending.clear()
		model_ready.emit()
		return
	set_process(true)


func _chunk_centre(key: Vector2i) -> Vector2:
	var r: Rect2i = model.chunks[key]["rect"]
	var w := lot_world(Vector2(r.get_center()))
	return Vector2(w.x, w.z)


func _build_chunk(key: Vector2i) -> void:
	var ch: Dictionary = model.chunks[key]
	var idx := PackedInt32Array()
	for n: int in ch["prisms"]:
		var pr := model.prisms[n]
		if pr.get("hq", false) and _hidden_hq.has(pr["terr"]):
			continue
		if _in_cleared(pr["centre"]):
			continue
		idx.append(n)
	var fams := CityMeshKit.families_of(cfg, model.prisms, idx)
	var keys: Array = fams.keys()
	keys.sort()
	var node := Node3D.new()
	node.name = "Chunk_%d_%d" % [key.x, key.y]
	var entry := {"node": node, "families": {}}
	for fk: int in keys:
		var ids: PackedInt32Array = fams[fk]
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.use_custom_data = true
		mm.mesh = CityMeshKit.family_mesh(cfg, fk, maxi(0, building_lod))
		mm.instance_count = ids.size()
		mm.buffer = CityMeshKit.instance_buffer(cfg, model.prisms, ids, _inks)
		# A buffer written whole does not refresh the MultiMesh's bounds: the chunk's box
		# (its prisms) is the cull box.
		mm.custom_aabb = model.chunk_aabb(key)
		var mi := MultiMeshInstance3D.new()
		mi.multimesh = mm
		mi.material_override = _building_mat
		mi.layers = 1 << (WORLD_LAYER - 1)
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if quality["shadows"] else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		node.add_child(mi)
		entry["families"][fk] = mi
	layer(&"buildings").add_child(node)
	var r: Rect2i = ch["rect"]
	var a := lot_world(Vector2(r.position))
	var b := lot_world(Vector2(r.end))
	var area := Rect2(Vector2(minf(a.x, b.x), minf(a.z, b.z)), Vector2(absf(b.x - a.x), absf(b.z - a.z)))
	var plazas: Array = []
	for n: int in ch["plazas"]:
		plazas.append(model.plazas[n])
	var streets: Array = []
	for n: int in ch["streets"]:
		streets.append(model.streets[n])
	var g := MeshInstance3D.new()
	g.mesh = CityMeshKit.ground_mesh_of(cfg, area, plazas, streets)
	g.material_override = _ground_mat
	g.layers = (1 << (WORLD_LAYER - 1)) | (1 << (GROUND_LAYER - 1))
	g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	node.add_child(g)
	var lm := CityMeshKit.lane_mesh_of(cfg, streets)
	if lm != null:
		var l := MeshInstance3D.new()
		l.mesh = lm
		l.material_override = _lane_mat
		l.layers = (1 << (WORLD_LAYER - 1)) | (1 << (GROUND_LAYER - 1))
		l.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		node.add_child(l)
	_chunks[key] = entry


func _free_chunk(key: Vector2i) -> void:
	var e: Dictionary = _chunks.get(key, {})
	if e.is_empty():
		return
	(e["node"] as Node).queue_free()
	_chunks.erase(key)


func _apply_building_lod() -> void:
	for key: Vector2i in _chunks:
		var fams: Dictionary = _chunks[key]["families"]
		for fk: int in fams:
			(fams[fk] as MultiMeshInstance3D).multimesh.mesh = CityMeshKit.family_mesh(cfg, fk, building_lod)


## Chunks placed so far (tests, the perf probe).
func chunks_built() -> int:
	return _chunks.size()


# --- Landmarks: the art pass's own models (5b), never re-modelled -----------------------------

## Where 5b's landmark glTFs live (assets/city/landmarks/<corp>/<file>, with a manifest).
const LANDMARKS_DIR := "res://assets/city/landmarks"
## The Cell's district (5b): its own street grid of buildings whose windows draw the fist.
const CELL := &"rebel_cell"
const CELL_DISTRICT_FILE := "rebel_cell_district.glb"
## Share of a landmark's ground box its procedural neighbours give way inside (its edges
## keep the street's own buildings).
const CLEAR_SHARE := 0.92


## Places every corporation's HQ landmark glTF on its HQ lot (the stand-in tower goes) and
## the Cell's district glTF on the Cell's district (the procedural buildings under it go),
## with 5b's LandmarkMaterials (night). A landmark whose file is missing keeps the stand-in.
func place_landmarks() -> void:
	var look := load(LandmarkMaterials.LOOK_PATH) as LandmarkLook
	var corps: Array = model.hqs.keys()
	corps.sort()
	for corp: StringName in corps:
		var path := "%s/%s/%s_hq.glb" % [LANDMARKS_DIR, corp, corp]
		if _place_landmark(corp, path, landmark_slot(corp), look):
			hide_stand_in(corp)
	var centre := NeonCity.hq_of(CELL) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
	_place_landmark(CELL, "%s/%s/%s" % [LANDMARKS_DIR, CELL, CELL_DISTRICT_FILE], Transform3D(Basis(), lot_world(centre)), look)


func _place_landmark(corp: StringName, path: String, at: Transform3D, look: LandmarkLook) -> bool:
	if landmarks.has(corp) or not ResourceLoader.exists(path):
		return false
	var scene := load(path) as PackedScene
	if scene == null:
		return false
	var node := scene.instantiate() as Node3D
	node.name = "Landmark_%s" % corp
	landmark_mats[corp] = LandmarkMaterials.apply(node, look, _landmark_corp(corp), not _landmarks_night)
	node.transform = at
	add_to_layer(&"landmarks", node)
	landmarks[corp] = node
	var box := _ground_box(node)
	if box.has_area():
		_cleared.append(Rect2(box.get_center() - box.size * CLEAR_SHARE * 0.5, box.size * CLEAR_SHARE))
	if corp == CELL:
		LandmarkMaterials.set_reveal(landmark_mats[corp], cell_reveal)
		LandmarkMaterials.show_dispatch(node, cell_dispatch)
	return true


## ART-5 5e: the materials of each placed landmark (key -> LandmarkMaterials.apply's
## result), for the reveal and the day / night look.
var landmark_mats: Dictionary = {}
## ART-5 5e: the Cell's blackout reveal (0 the sector fully lit .. 1 the fist revealed) and
## which fist its windows draw (DISPATCH's when true, else home's).
var cell_reveal: float = 1.0
var cell_dispatch: bool = false
## ART-5 5e: the Site landmark placed (5b's `<corp>_site.glb`): {"corp", "lot"} or {}.
var site_landmark: Dictionary = {}
## Key of the Site landmark in `landmarks` / `landmark_mats`.
const SITE_KEY := &"site"


## The corporation whose tint a landmark key takes (the Site landmark's is its corp's).
func _landmark_corp(key: StringName) -> StringName:
	return StringName(site_landmark.get("corp", key)) if key == SITE_KEY else key


## ART-5 5e: the Cell's blackout reveal (bible 4.4, round 34 `map_fist_reveal`): 0 the
## sector fully lit and washed out, 1 the ring and the hand's lines dark and the fist shown.
func set_cell_reveal(q: float) -> void:
	cell_reveal = clampf(q, 0.0, 1.0)
	if landmark_mats.has(CELL):
		LandmarkMaterials.set_reveal(landmark_mats[CELL], cell_reveal)


## ART-5 5e: the Cell's district shows DISPATCH's fist (the REBEL_CELL campaign) or home's.
func show_cell_dispatch(on: bool) -> void:
	cell_dispatch = on
	if landmarks.has(CELL):
		LandmarkMaterials.show_dispatch(landmarks[CELL], on)


## ART-5 5e: places corporation `corp`'s Site landmark (5b's `<corp>_site.glb`) centred on
## lot point `lot` (lots; its 6 x 6 block's centre), facing lot +y as the locked renders;
## the procedural buildings under it give way (their chunks are rebuilt). An empty `corp`
## or a corp without a Site landmark removes it. Returns true when one stands.
func set_site_landmark(corp: StringName, lot: Vector2) -> bool:
	var want := {"corp": corp, "lot": lot} if corp != &"" else {}
	if want == site_landmark:
		return landmarks.has(SITE_KEY)
	_remove_site_landmark()
	site_landmark = want
	if want.is_empty() or model == null:
		return false
	var path := CityLandmarks.site_path(corp)
	if path == "":
		return false
	var look := load(LandmarkMaterials.LOOK_PATH) as LandmarkLook
	var before := _cleared.size()
	if not _place_landmark(SITE_KEY, path, Transform3D(Basis(), lot_world(lot)), look):
		return false
	_rebuild_under(_cleared[before] if _cleared.size() > before else Rect2())
	return true


func _remove_site_landmark() -> void:
	if not landmarks.has(SITE_KEY):
		return
	var node: Node3D = landmarks[SITE_KEY]
	var box := _ground_box(node)
	var r := Rect2(box.get_center() - box.size * CLEAR_SHARE * 0.5, box.size * CLEAR_SHARE)
	for k in range(_cleared.size() - 1, -1, -1):
		if _cleared[k].is_equal_approx(r):
			_cleared.remove_at(k)
	node.queue_free()
	landmarks.erase(SITE_KEY)
	landmark_mats.erase(SITE_KEY)
	_rebuild_under(r)


## Rebuilds the built chunks whose ground meets world X/Z rect `r`.
func _rebuild_under(r: Rect2) -> void:
	if not r.has_area() or model == null:
		return
	for key: Vector2i in _chunks.keys():
		var b := model.chunk_aabb(key)
		if Rect2(Vector2(b.position.x, b.position.z), Vector2(b.size.x, b.size.z)).intersects(r):
			_free_chunk(key)
			_build_chunk(key)


## Every placed landmark's materials again in the day or night look (set_night_share).
func _restyle_landmarks() -> void:
	var look := load(LandmarkMaterials.LOOK_PATH) as LandmarkLook
	for key: StringName in landmarks:
		landmark_mats[key] = LandmarkMaterials.apply(landmarks[key], look, _landmark_corp(key), not _landmarks_night)
	set_cell_reveal(cell_reveal)


## The X/Z box of every mesh under `node` (world).
static func _ground_box(node: Node3D) -> Rect2:
	var out := Rect2()
	var first := true
	for mi in node.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m.mesh == null:
			continue
		var b := m.global_transform * m.mesh.get_aabb() if m.is_inside_tree() else (node.transform * m.transform) * m.mesh.get_aabb()
		var r := Rect2(Vector2(b.position.x, b.position.z), Vector2(b.size.x, b.size.z))
		out = r if first else out.merge(r)
		first = false
	return out


func _in_cleared(c: Vector2) -> bool:
	for r in _cleared:
		if r.has_point(c):
			return true
	return false
