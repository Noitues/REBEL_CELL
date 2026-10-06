class_name CityMotionLayers
extends Node3D
## ART-5 5c: the unified city's motion layers (ART_BIBLE §4.1 car LOD, §4.2 city motion, §4.3
## Heat on maps, §5.3 VfxTier T0, §5.4, §6.1), on any city model through one seam
## (CityMotionSite). Bottom to top: street traffic (night head / tail lights, day small
## coloured cars), the sky lanes (guide dots + cars in three LOD tiers moved in the vertex
## shader along baked paths), holo billboards, aviation lights, the Heat and suspicion rig
## (searchlights, alarm beacons, police strobes, choppers and drones with spotlights, the
## hardened nodes' rings and circling lights).
##
## A view: it reads the city's look and the game's Heat from its host and never changes
## state (Signal Up, Call Down). Calls down: setup, set_ortho, set_view, set_light,
## set_heat, set_covered, set_focus_point. Signals up: the host's fog / rain clock, its
## day / night look and the light spill its toon materials take. Every motion has its
## `ui_motion.tres` entry (MOTION_IDS, T0): its period, share or angle; the layer asks
## Motion.live for it every frame. Pauses when the map is covered or the window loses
## focus or the host pauses its ambience; reduce effects shows every layer's end state;
## reduce motion pauses them in their steady look (CityMotionClock). The layer and its
## groups sit at the world origin of their host's 3D world.

## The host's fog and rain clock scale (0 while the layers are paused or held).
signal ambient_scale_changed(scale: float)
## The share of the night look (1 night .. 0 day) the host's city should show.
signal night_share_changed(share: float)
## Light spill sources for the host's toon materials (LightSpill.uniforms_3d's input:
## {position, radius, color, intensity}, nearest the camera first).
signal spill_changed(sources: Array)

enum View { GRID, RAID, NETRUN }
enum Daylight { NIGHT, DAY }

## Motion entries, one per layer (CityMotionClock.Layer order), then the light crossfade.
const SKY_CARS := &"sky_lane_cars"
const STREET_CARS := &"street_cars"
const BILLBOARD := &"holo_billboard"
const AVIATION := &"aviation_blink"
const SEARCHLIGHT := &"searchlight_sweep"
const CHOPPER := &"chopper_orbit"
const DRONE := &"drone_orbit"
const STROBE := &"police_strobe"
const ALARM := &"alarm_beacon"
const NODE_LIGHT := &"heat_node_light"
const LIGHT_FADE := &"city_light_fade"
const MOTION_IDS: Array[StringName] = [SKY_CARS, STREET_CARS, BILLBOARD, AVIATION, SEARCHLIGHT, CHOPPER, DRONE, STROBE,
	ALARM, NODE_LIGHT, LIGHT_FADE]

const CAR_SHADER := preload("res://shaders/city/sky_car.gdshader")
const GLOW_SHADER := preload("res://shaders/city/city_glow.gdshader")
const GLOW_XRAY_SHADER := preload("res://shaders/city/city_glow_xray.gdshader")
const POOL_XRAY_SHADER := preload("res://shaders/city/city_pool_xray.gdshader")
const BEAM_SHADER := preload("res://shaders/city/city_beam.gdshader")
const POOL_SHADER := preload("res://shaders/city/city_pool.gdshader")
const BILLBOARD_SHADER := preload("res://shaders/city/holo_billboard.gdshader")
## Round 26's billboard panel atlas (cm._billboard_tex; four panels side by side), exported by
## tools/art_pipeline/parity/export_billboards.py.
const BILLBOARD_PANELS := preload("res://assets/city/billboards/panels.png")
## Glow modes (city_glow.gdshader).
enum GlowMode { STEADY, BLINK, STROBE, BEACON, CIRCLE }
## A pool's mode (city_pool.gdshader).
enum PoolMode { DISC, RING }
## Ground pools sit this far above the street so they never fight it for depth (BU).
const POOL_LIFT := 0.08
## A sprite never draws under this many screen pixels.
const MIN_PX := 2.5
## The layer groups, as the host's scene layers name them (CityView3D.LAYERS): street
## traffic, the sky lanes, billboards and aviation lights, the Heat / suspicion rig. The
## traffic, sky and heat groups also draw under see-through buildings (bible 4.1: ground,
## lanes and cars render under them).
const GROUPS: Array[StringName] = [&"traffic", &"sky", &"props", &"heat"]
const GROUND_PASS_GROUPS: Array[StringName] = [&"traffic", &"sky", &"heat"]

var cfg: CityMotionConfigData
var site: CityMotionSite
var lanes: CitySkyLanes
var traffic: CitySkyTraffic
var props: CityAmbientProps
var rig: CityHeatRig
var clock: CityMotionClock = CityMotionClock.new()
## The pause inputs: the map is covered (the host says), the window lost focus.
var covered: bool = false
var unfocused: bool = false
## Quiet windowed runs (tools/run_windowed.py) never have focus: they keep the layers going.
var honour_focus: bool = true
## The host's ambient scale (CityView3D.ambient_scale: 0 when it pauses or holds its own
## ambient layers): 0 pauses every layer here too.
var host_ambient: float = 1.0
## The host's render layer (bit number) for its ground-only pass, 0 for none.
var ground_pass_layer: int = 0
## The groups' nodes (GROUPS), children of this node until a host moves them to its layers.
var groups: Dictionary = {}
var view: int = View.GRID
var daylight: int = Daylight.NIGHT
var suspicion: bool = false
var heat_band: int = CityHeatRig.Band.COOL
var hardened: Array[Vector3] = []
var ortho: float = 440.0
var car_tier: int = -1
var night_share: float = 1.0

var _seed: int = 0
var _bu_per_px: float = 0.23
var _focus: Vector3 = Vector3.ZERO
var _ambient_scale: float = -1.0
var _car_mmis: Array[MultiMeshInstance3D] = []
var _car_mats: Array[ShaderMaterial] = []
var _street_mmi: MultiMeshInstance3D
var _street_mat: ShaderMaterial
var _guide_mmi: MultiMeshInstance3D
var _guide_mat: ShaderMaterial
var _billboard_mmi: MultiMeshInstance3D
var _billboard_mat: ShaderMaterial
var _aviation_mmi: MultiMeshInstance3D
var _aviation_mat: ShaderMaterial
var _rig_root: Node3D
var _search_mmi: MultiMeshInstance3D
var _spot_mmi: MultiMeshInstance3D
var _pool_mmi: MultiMeshInstance3D
var _ring_mmi: MultiMeshInstance3D
var _node_mmi: MultiMeshInstance3D
var _node_mat: ShaderMaterial
var _strobe_mmi: MultiMeshInstance3D
var _strobe_mat: ShaderMaterial
var _alarm_mmi: MultiMeshInstance3D
var _alarm_mat: ShaderMaterial
var _air_light_mmi: MultiMeshInstance3D
var _air_light_mat: ShaderMaterial
var _choppers: Array[Node3D] = []
var _drones: Array[Node3D] = []
var _air_mats: Array[ShaderMaterial] = []
var _aircraft_neon_mat: StandardMaterial3D
var _aabb: AABB = AABB()
var _spill: Dictionary = {}
var _spill_sources: Array = []


## Builds every layer on `p_site` from `p_cfg`, seeded by the city's seed `seed`.
func setup(p_cfg: CityMotionConfigData, p_site: CityMotionSite, seed: int) -> void:
	cfg = p_cfg
	site = p_site
	_seed = seed
	honour_focus = not Settings.quiet_window()
	for g: Node3D in groups.values():
		g.queue_free()
	for c in get_children():
		c.queue_free()
	groups.clear()
	for name_ in GROUPS:
		var g := Node3D.new()
		g.name = String(name_).capitalize()
		add_child(g)
		groups[name_] = g
	_car_mmis.clear()
	_car_mats.clear()
	lanes = CitySkyLanes.build(cfg, site)
	traffic = CitySkyTraffic.build(cfg, lanes, seed, _period(SKY_CARS), _period(STREET_CARS), site.lot_bu)
	props = CityAmbientProps.build(cfg, site, seed)
	_aabb = lanes.aabb().merge(site.bounds).grow(cfg.searchlight_length + cfg.chopper_altitude)
	_focus = site.home
	_build_street()
	_build_sky()
	_build_billboards()
	_build_aviation()
	_rig_root = groups[&"heat"]
	_rebuild_rig()
	set_ortho(ortho)
	_apply_light(true)


## The camera zoom (ortho width, BU) and the viewport's width (px): car LOD with
## hysteresis, sprite minimum sizes.
func set_ortho(p_ortho: float, viewport_width: float = 1920.0) -> void:
	ortho = p_ortho
	_bu_per_px = ortho / maxf(viewport_width, 1.0)
	if cfg == null:
		return
	car_tier = CitySkyTraffic.car_tier(cfg, ortho, car_tier)
	_apply_visibility()
	for m: ShaderMaterial in [_guide_mat, _aviation_mat, _strobe_mat, _alarm_mat, _node_mat, _air_light_mat]:
		if m != null:
			m.set_shader_parameter(&"bu_per_px", _bu_per_px)


## Which view the city is showing (GRID, RAID, NETRUN): sky lanes at the management share
## in raid and netrun, sky-lane cars off in the netrun transit (bible 4.1).
func set_view(p_view: int) -> void:
	view = p_view
	if cfg == null:
		return
	var g := 1.0 if view == View.GRID else cfg.management_gain
	for m in _car_mats:
		m.set_shader_parameter(&"line_gain", g)
	if _guide_mat != null:
		_guide_mat.set_shader_parameter(&"gain", g)
	_apply_visibility()


## Day or night, and suspicion (round 6: police, choppers and drones round the Cell).
func set_light(p_daylight: int, p_suspicion: bool) -> void:
	var rebuild := p_suspicion != suspicion
	daylight = p_daylight
	suspicion = p_suspicion
	if cfg == null:
		return
	if rebuild:
		_rebuild_rig()
	if not Motion.live(LIGHT_FADE):
		_apply_light(true)


## The Heat band (CityHeatRig.Band) and the hardened nodes (world, node-id order).
func set_heat(band: int, p_hardened: Array[Vector3]) -> void:
	heat_band = band
	hardened = p_hardened.duplicate()
	if cfg != null:
		_rebuild_rig()


## The host says whether the map is covered (a screen or modal over it): pauses every layer.
func set_covered(value: bool) -> void:
	covered = value
	_update_ambient_scale()


## Where the camera looks (world): the spill sources nearest it go to the toon materials.
func set_focus_point(p: Vector3) -> void:
	_focus = p
	if cfg != null:
		_update_spill()


## The host's ambient scale (0 pauses every layer: the host's map is covered or unfocused,
## or it holds its ambience under reduce effects / reduce motion).
func set_host_ambient(scale: float) -> void:
	host_ambient = scale
	_update_ambient_scale()


## Marks the groups that draw under see-through buildings for the host's ground-only pass
## (render layer bit `bit`; 0: none).
func set_ground_pass_layer(bit: int) -> void:
	ground_pass_layer = bit
	_mark_ground_pass()


## True while every layer is stopped (covered, the window unfocused, or the host paused).
func paused() -> bool:
	return covered or (honour_focus and unfocused) or host_ambient <= 0.0


## True when the sky-lane cars draw.
func sky_cars_visible() -> bool:
	return not _car_mmis.is_empty() and CityMotionClock.sky_cars_shown(Settings.reduce_motion, view == View.NETRUN,
		car_tier == CitySkyTraffic.CarTier.CLOSE)


## Layer time of CityMotionClock layer `layer` (s).
func layer_time(layer: int) -> float:
	return clock.times[layer]


## The spill uniforms last sent (LightSpill.uniforms_3d).
func spill_uniforms() -> Dictionary:
	return _spill


## The spill sources last sent (LightSpill.uniforms_3d's input).
func spill_sources() -> Array:
	return _spill_sources


func _mark_ground_pass() -> void:
	if ground_pass_layer <= 0:
		return
	for name_ in GROUND_PASS_GROUPS:
		if groups.has(name_):
			_set_mask(groups[name_], ground_pass_layer)


static func _set_mask(node: Node, bit: int) -> void:
	if node is VisualInstance3D:
		(node as VisualInstance3D).set_layer_mask_value(bit, true)
	for c in node.get_children():
		_set_mask(c, bit)


func _notification(what: int) -> void:
	match what:
		NOTIFICATION_APPLICATION_FOCUS_OUT:
			unfocused = true
			_update_ambient_scale()
		NOTIFICATION_APPLICATION_FOCUS_IN:
			unfocused = false
			_update_ambient_scale()


func _process(delta: float) -> void:
	if cfg == null:
		return
	var rm := Settings.reduce_motion
	var stop := paused()
	var lives := _lives()
	var rates := PackedFloat64Array()
	for k in CityMotionClock.COUNT:
		rates.append(CityMotionClock.rate(cfg, k, stop, rm, lives[k]))
	clock.advance(delta, rates, lives)
	_push_clocks(rm, lives)
	_update_rig(rm, lives)
	_step_light(delta, stop)
	_update_ambient_scale()


## Each layer's motion asked whether it plays now (CityMotionClock.Layer order).
func _lives() -> Array[bool]:
	var out: Array[bool] = []
	out.append(Motion.live(SKY_CARS))
	out.append(Motion.live(STREET_CARS))
	out.append(Motion.live(BILLBOARD))
	out.append(Motion.live(AVIATION))
	out.append(Motion.live(SEARCHLIGHT))
	out.append(Motion.live(CHOPPER))
	out.append(Motion.live(DRONE))
	out.append(Motion.live(STROBE))
	out.append(Motion.live(ALARM))
	out.append(Motion.live(NODE_LIGHT))
	return out


func _period(id: StringName) -> float:
	return maxf(Motion.seconds(id), 0.01)


func _push_clocks(rm: bool, lives: Array[bool]) -> void:
	for m in _car_mats:
		m.set_shader_parameter(&"clock", clock.times[CityMotionClock.Layer.SKY_CARS])
	if _street_mat != null:
		_street_mat.set_shader_parameter(&"clock", clock.times[CityMotionClock.Layer.STREET_CARS])
		_street_mat.set_shader_parameter(&"streak_on", CityMotionClock.street_streaks(rm))
	var glow := [[_billboard_mat, CityMotionClock.Layer.BILLBOARDS], [_aviation_mat, CityMotionClock.Layer.AVIATION], [_strobe_mat, CityMotionClock.Layer.STROBES],
		[_alarm_mat, CityMotionClock.Layer.ALARMS], [_node_mat, CityMotionClock.Layer.NODE_LIGHTS], [_air_light_mat, CityMotionClock.Layer.STROBES]]
	for g in glow:
		var m: ShaderMaterial = g[0]
		if m == null:
			continue
		m.set_shader_parameter(&"clock", clock.times[g[1]])
		m.set_shader_parameter(&"steady", CityMotionClock.steady(g[1], rm, lives[g[1]]))
	_apply_visibility()


func _apply_visibility() -> void:
	var shown := sky_cars_visible()
	for k in _car_mmis.size():
		_car_mmis[k].visible = shown and k == car_tier


## Day / night: the layers' own gains, and the host's look through night_share_changed.
func _step_light(delta: float, stop: bool) -> void:
	var target := 1.0 if daylight == Daylight.NIGHT else 0.0
	if is_equal_approx(night_share, target):
		return
	if stop:
		return
	if Motion.live(LIGHT_FADE):
		night_share = move_toward(night_share, target, delta / _period(LIGHT_FADE))
		_apply_light(false)
	else:
		_apply_light(true)


func _apply_light(snap: bool) -> void:
	if snap:
		night_share = 1.0 if daylight == Daylight.NIGHT else 0.0
	var n := night_share
	for m in _car_mats:
		m.set_shader_parameter(&"night", n)
		m.set_shader_parameter(&"gain", _car_gain())
	if _street_mat != null:
		_street_mat.set_shader_parameter(&"night", n)
	if _billboard_mat != null:
		_billboard_mat.set_shader_parameter(&"gain", lerpf(cfg.billboard_gain_day, cfg.billboard_gain_night, n))
	if _aviation_mat != null:
		_aviation_mat.set_shader_parameter(&"gain", lerpf(cfg.aviation_gain_day, cfg.aviation_gain_night, n))
	night_share_changed.emit(n)
	_update_spill()


func _car_gain() -> float:
	return lerpf(cfg.day_car_gain, 1.0, night_share)


func _update_ambient_scale() -> void:
	var s := 0.0 if paused() or Settings.reduce_motion or not Motion.animating() else 1.0
	if s != _ambient_scale:
		_ambient_scale = s
		ambient_scale_changed.emit(s)


# ---- building -------------------------------------------------------------------------

func _mmi(mesh: Mesh, count: int, mat: Material, name_: String, parent: Node = self) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.use_custom_data = true
	mm.mesh = mesh
	mm.instance_count = count
	var mi := MultiMeshInstance3D.new()
	mi.name = name_
	mi.multimesh = mm
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.custom_aabb = _aabb
	parent.add_child(mi)
	return mi


func _glow_mat(mode: int, id: StringName, xray: bool = false) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = GLOW_XRAY_SHADER if xray else GLOW_SHADER
	m.set_shader_parameter(&"off_level", cfg.blink_off_level)
	m.set_shader_parameter(&"mode", mode)
	m.set_shader_parameter(&"min_px", MIN_PX)
	m.set_shader_parameter(&"bu_per_px", _bu_per_px)
	if id != &"":
		m.set_shader_parameter(&"period", _period(id))
		m.set_shader_parameter(&"duty", Motion.amplitude(id))
	return m


func _quad(size: float = 1.0) -> QuadMesh:
	var q := QuadMesh.new()
	q.size = Vector2(size, size)
	return q


func _path_texture(list: Array[Dictionary]) -> ImageTexture:
	return ImageTexture.create_from_image(lanes.bake(list))


func _car_mat(tex: Texture2D) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = CAR_SHADER
	m.set_shader_parameter(&"path_tex", tex)
	m.set_shader_parameter(&"end_fade", cfg.end_fade)
	m.set_shader_parameter(&"headlight", _v3(cfg.headlight))
	m.set_shader_parameter(&"headlight_gain", cfg.headlight_gain)
	m.set_shader_parameter(&"taillight", _v3(cfg.street_tail))
	m.set_shader_parameter(&"street_head", _v3(cfg.street_head))
	m.set_shader_parameter(&"body_color", _v3(cfg.body_color))
	m.set_shader_parameter(&"band_hi", ToonInkMaterial.BAND_HI)
	m.set_shader_parameter(&"band_lo", ToonInkMaterial.BAND_LO)
	m.set_shader_parameter(&"shade_mid", ToonInkMaterial.SHADE_MID)
	m.set_shader_parameter(&"shade_low", ToonInkMaterial.SHADE_LOW)
	m.render_priority = 10
	return m


static func _v3(c: Color) -> Vector3:
	return Vector3(c.r, c.g, c.b)


func _build_sky() -> void:
	if lanes.rows.is_empty():
		return
	var tex := _path_texture(lanes.rows)
	for tier in 3:
		var m := _car_mat(tex)
		m.set_shader_parameter(&"body_alpha", cfg.medium_alpha if tier == CitySkyTraffic.CarTier.MEDIUM else 1.0)
		m.set_shader_parameter(&"body_lane_fill", tier == CitySkyTraffic.CarTier.MEDIUM)
		m.set_shader_parameter(&"toon", tier == CitySkyTraffic.CarTier.CLOSE)
		if tier == CitySkyTraffic.CarTier.CLOSE:
			m.set_shader_parameter(&"body_color", _v3(cfg.close_body_color))
		var mi := _mmi(CityMotionMeshes.car(cfg, tier), traffic.cars.size(), m, "SkyCars%d" % tier, groups[&"sky"])
		for k in traffic.cars.size():
			var car: Dictionary = traffic.cars[k]
			mi.multimesh.set_instance_transform(k, Transform3D.IDENTITY)
			mi.multimesh.set_instance_color(k, cfg.lane_colors[int(car["color"])])
			mi.multimesh.set_instance_custom_data(k, Color(car["phase"], car["speed"], float(car["row"]), car["streak"]))
		_car_mmis.append(mi)
		_car_mats.append(m)
	var dots := lanes.guide_dots(cfg)
	_guide_mat = _glow_mat(GlowMode.STEADY, &"")
	_guide_mat.set_shader_parameter(&"alpha", cfg.guide_alpha)
	_guide_mat.set_shader_parameter(&"min_px", 1.0)
	_guide_mmi = _mmi(_quad(), dots.size(), _guide_mat, "LaneGuides", groups[&"sky"])
	for k in dots.size():
		_guide_mmi.multimesh.set_instance_transform(k, Transform3D(Basis.IDENTITY, dots[k]["pos"]))
		_guide_mmi.multimesh.set_instance_color(k, cfg.lane_colors[int(dots[k]["color"])])
		_guide_mmi.multimesh.set_instance_custom_data(k, Color(0.0, cfg.guide_size, 0.0, 0.0))


func _build_street() -> void:
	if lanes.street_rows.is_empty():
		return
	_street_mat = _car_mat(_path_texture(lanes.street_rows))
	_street_mat.set_shader_parameter(&"street", true)
	_street_mmi = _mmi(CityMotionMeshes.street_car(cfg), traffic.street_cars.size(), _street_mat, "StreetCars",
		groups[&"traffic"])
	for k in traffic.street_cars.size():
		var car: Dictionary = traffic.street_cars[k]
		_street_mmi.multimesh.set_instance_transform(k, Transform3D.IDENTITY)
		# Night: head lights one way, tail lights the other (a negative streak marks a tail);
		# by day the car's own lane colour.
		_street_mmi.multimesh.set_instance_color(k, cfg.lane_colors[int(car["color"])])
		var streak := float(car["streak"]) * (-1.0 if bool(car["tail"]) else 1.0)
		_street_mmi.multimesh.set_instance_custom_data(k, Color(car["phase"], car["speed"], float(car["row"]), streak))


## An aircraft node (`CityMotionMeshes.aircraft`'s model): the toon body in `toon`, and the concept's
## lit parts (nav lights, searchlight frame, belly plate) as one unshaded vertex-colour mesh.
func _aircraft_body(model: Dictionary, toon: ShaderMaterial) -> Node3D:
	var holder := Node3D.new()
	var scl := Vector3.ONE * float(model["scale"])
	var body := MeshInstance3D.new()
	body.mesh = model["body"] as Mesh
	body.material_override = toon
	body.scale = scl
	body.position = model["offset"] as Vector3
	holder.add_child(body)
	if model["neon"] != null:
		if _aircraft_neon_mat == null:
			_aircraft_neon_mat = StandardMaterial3D.new()
			_aircraft_neon_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			_aircraft_neon_mat.vertex_color_use_as_albedo = true
		var lit := MeshInstance3D.new()
		lit.mesh = model["neon"] as Mesh
		lit.material_override = _aircraft_neon_mat
		lit.scale = scl
		lit.position = model["offset"] as Vector3
		holder.add_child(lit)
	return holder


func _build_billboards() -> void:
	_billboard_mat = ShaderMaterial.new()
	_billboard_mat.shader = BILLBOARD_SHADER
	_billboard_mat.set_shader_parameter(&"hold", _period(BILLBOARD))
	_billboard_mat.set_shader_parameter(&"wipe", Motion.delay_of(BILLBOARD))
	_billboard_mat.set_shader_parameter(&"dropout", Motion.amplitude(BILLBOARD))
	_billboard_mat.set_shader_parameter(&"size", cfg.billboard_size)
	_billboard_mat.set_shader_parameter(&"scanlines", cfg.billboard_scanlines)
	_billboard_mat.set_shader_parameter(&"panels", cfg.billboard_panels)
	_billboard_mat.set_shader_parameter(&"panel_tex", BILLBOARD_PANELS)
	_billboard_mmi = _mmi(_quad(), props.billboards.size(), _billboard_mat, "HoloBillboards", groups[&"props"])
	for k in props.billboards.size():
		var b: Dictionary = props.billboards[k]
		_billboard_mmi.multimesh.set_instance_transform(k, Transform3D(Basis.IDENTITY, b["pos"]))
		_billboard_mmi.multimesh.set_instance_color(k, cfg.lane_colors[int(b["color"])])
		_billboard_mmi.multimesh.set_instance_custom_data(k, Color(b["phase"], float(b["panel"]), 0.0, 0.0))


func _build_aviation() -> void:
	_aviation_mat = _glow_mat(GlowMode.BLINK, AVIATION)
	_aviation_mmi = _mmi(_quad(), props.aviation.size(), _aviation_mat, "AviationLights", groups[&"props"])
	for k in props.aviation.size():
		var a: Dictionary = props.aviation[k]
		_aviation_mmi.multimesh.set_instance_transform(k, Transform3D(Basis.IDENTITY, (a["pos"] as Vector3) + Vector3.UP * cfg.aviation_size))
		_aviation_mmi.multimesh.set_instance_color(k, cfg.aviation_color)
		_aviation_mmi.multimesh.set_instance_custom_data(k, Color(a["phase"], cfg.aviation_size, 0.0, 0.0))


## (Re)places the Heat and suspicion rig for the current band, hardened nodes and light.
func _rebuild_rig() -> void:
	for c in _rig_root.get_children():
		c.queue_free()
	_choppers.clear()
	_drones.clear()
	_air_mats.clear()
	rig = CityHeatRig.build(cfg, site, heat_band, hardened, suspicion)
	var beam := ShaderMaterial.new()
	beam.shader = BEAM_SHADER
	beam.render_priority = 11
	var cone := CityMotionMeshes.cone()
	_search_mmi = _mmi(cone, rig.searchlights.size(), beam, "Searchlights", _rig_root)
	var spots := rig.choppers.size() + rig.drones.size()
	_spot_mmi = _mmi(cone, spots, beam, "Spotlights", _rig_root)
	var pool := ShaderMaterial.new()
	pool.shader = POOL_SHADER
	pool.set_shader_parameter(&"mode", PoolMode.DISC)
	var flat := PlaneMesh.new()
	flat.size = Vector2(2.0, 2.0)
	_pool_mmi = _mmi(flat, spots + rig.police.size(), pool, "Pools", _rig_root)
	# The hardened nodes' rings and lights are node markers: drawn through buildings, as the
	# network decal is.
	var ring := ShaderMaterial.new()
	ring.shader = POOL_XRAY_SHADER
	ring.set_shader_parameter(&"mode", PoolMode.RING)
	_ring_mmi = _mmi(flat, rig.node_lights.size(), ring, "NodeRings", _rig_root)
	_node_mat = _glow_mat(GlowMode.CIRCLE, NODE_LIGHT, true)
	_node_mmi = _mmi(_quad(), rig.node_lights.size(), _node_mat, "NodeLights", _rig_root)
	for k in rig.node_lights.size():
		var nl: Dictionary = rig.node_lights[k]
		var p: Vector3 = nl["pos"]
		var r := cfg.node_ring_radius
		_ring_mmi.multimesh.set_instance_transform(k, Transform3D(Basis.IDENTITY.scaled(Vector3(r, 1.0, r)), p + Vector3.UP * POOL_LIFT))
		_ring_mmi.multimesh.set_instance_color(k, Palette.HEAT_B)
		_ring_mmi.multimesh.set_instance_custom_data(k, Color(1.0, cfg.node_ring_width / r, 0.0, 0.0))
		_node_mmi.multimesh.set_instance_transform(k, Transform3D(Basis.IDENTITY, p + Vector3.UP * cfg.node_light_height))
		_node_mmi.multimesh.set_instance_color(k, cfg.police_blue if bool(nl["blue"]) else cfg.police_red)
		_node_mmi.multimesh.set_instance_custom_data(k, Color(nl["phase"], cfg.node_light_size, r, 0.0))
	_strobe_mat = _glow_mat(GlowMode.STROBE, STROBE)
	_strobe_mmi = _mmi(_quad(), rig.police.size() * 2, _strobe_mat, "PoliceStrobes", _rig_root)
	for k in rig.police.size():
		var pc: Dictionary = rig.police[k]
		var p: Vector3 = pc["pos"]
		for s in 2:
			var i := k * 2 + s
			var side := Vector3(float(s * 2 - 1) * cfg.strobe_size * 0.6, cfg.strobe_size * 0.6, 0.0)
			_strobe_mmi.multimesh.set_instance_transform(i, Transform3D(Basis.IDENTITY, p + side))
			_strobe_mmi.multimesh.set_instance_color(i, cfg.police_blue if s == 1 else cfg.police_red)
			_strobe_mmi.multimesh.set_instance_custom_data(i, Color(fposmod(float(pc["phase"]) + 0.5 * s, 1.0), cfg.strobe_size, 0.0, 0.0))
		var j := spots + k
		_pool_mmi.multimesh.set_instance_transform(j, Transform3D(Basis.IDENTITY.scaled(Vector3.ONE * cfg.strobe_pool), p + Vector3.UP * POOL_LIFT))
		_pool_mmi.multimesh.set_instance_color(j, cfg.police_red.lerp(cfg.police_blue, 0.5))
		_pool_mmi.multimesh.set_instance_custom_data(j, Color(cfg.pool_alpha * 0.5, 0.0, 0.0, 0.0))
	_alarm_mat = _glow_mat(GlowMode.BEACON, ALARM)
	_alarm_mmi = _mmi(_quad(), rig.alarms.size(), _alarm_mat, "AlarmBeacons", _rig_root)
	for k in rig.alarms.size():
		var al: Dictionary = rig.alarms[k]
		_alarm_mmi.multimesh.set_instance_transform(k, Transform3D(Basis.IDENTITY, (al["pos"] as Vector3) + Vector3.UP * cfg.strobe_size))
		_alarm_mmi.multimesh.set_instance_color(k, cfg.alarm_color)
		_alarm_mmi.multimesh.set_instance_custom_data(k, Color(al["phase"], cfg.strobe_size * 1.4, 0.0, 0.0))
	# Aircraft: toon bodies with ink (ToonInkMaterial), rotor blur discs, blinking nav lights.
	var chopper_model := CityMotionMeshes.chopper(cfg.chopper_length)
	var rotor := CityMotionMeshes.rotor(float(chopper_model["rotor_r"]))
	var rotor_mat := StandardMaterial3D.new()
	rotor_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	rotor_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	rotor_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	rotor_mat.albedo_color = Color(cfg.chopper_color, 0.22)
	for k in rig.choppers.size():
		var m := ToonInkMaterial.make(cfg.chopper_color)
		var body := _aircraft_body(chopper_model, m)
		_air_mats.append(m)
		var disc := MeshInstance3D.new()
		disc.mesh = rotor
		disc.material_override = rotor_mat
		disc.position = Vector3(0.0, float(chopper_model["rotor_y"]), 0.0)
		body.add_child(disc)
		var n := Node3D.new()
		n.name = "Chopper%d" % k
		n.add_child(body)
		_rig_root.add_child(n)
		_choppers.append(n)
	var drone_model := CityMotionMeshes.drone(cfg.drone_size)
	for k in rig.drones.size():
		var m := ToonInkMaterial.make(cfg.drone_color, ToonInkMaterial.INK_PX * 0.6)
		var body := _aircraft_body(drone_model, m)
		_air_mats.append(m)
		var n := Node3D.new()
		n.name = "Drone%d" % k
		n.add_child(body)
		_rig_root.add_child(n)
		_drones.append(n)
	_air_light_mat = _glow_mat(GlowMode.STROBE, STROBE)
	_air_light_mmi = _mmi(_quad(), (rig.choppers.size() + rig.drones.size()) * 2, _air_light_mat, "AirLights", _rig_root)
	for k in _air_light_mmi.multimesh.instance_count:
		_air_light_mmi.multimesh.set_instance_color(k, cfg.police_blue if k % 2 == 1 else cfg.police_red)
		_air_light_mmi.multimesh.set_instance_custom_data(k, Color(0.5 * float(k % 2), cfg.strobe_size * 0.7, 0.0, 0.0))
	_update_rig(Settings.reduce_motion, _lives())
	_update_spill()
	_mark_ground_pass()


## Moves the CPU-placed parts of the rig (searchlight sweeps, aircraft orbits, their spots
## and pools) to the layer times. Held layers sit at time 0: searchlights at rest, aircraft
## parked at their first orbit point.
func _update_rig(rm: bool, lives: Array[bool]) -> void:
	if rig == null or _search_mmi == null:
		return
	var t_s := clock.times[CityMotionClock.Layer.SEARCHLIGHTS]
	var sweep := deg_to_rad(Motion.amplitude(SEARCHLIGHT))
	var lean := deg_to_rad(cfg.searchlight_lean)
	for k in rig.searchlights.size():
		var sl: Dictionary = rig.searchlights[k]
		var yaw := float(sl["yaw"])
		if not CityMotionClock.steady(CityMotionClock.Layer.SEARCHLIGHTS, rm, lives[CityMotionClock.Layer.SEARCHLIGHTS]):
			yaw += sweep * sin(TAU * (t_s / _period(SEARCHLIGHT) + float(sl["phase"])))
		var d := Vector3(sin(lean) * cos(yaw), cos(lean), sin(lean) * sin(yaw))
		_search_mmi.multimesh.set_instance_transform(k, _beam(sl["pos"], d, cfg.searchlight_length, cfg.searchlight_radius))
		_search_mmi.multimesh.set_instance_color(k, cfg.searchlight_color)
		_search_mmi.multimesh.set_instance_custom_data(k, Color(float(sl["alpha"]), 0.0, 0.0, 0.0))
	var i := 0
	var light := 0
	var t_c := clock.times[CityMotionClock.Layer.CHOPPERS]
	var wob := Motion.amplitude(CHOPPER)
	for k in rig.choppers.size():
		var ch: Dictionary = rig.choppers[k]
		var th := TAU * (float(ch["dir"]) * t_c / _period(CHOPPER) + float(ch["phase"]))
		var c: Vector3 = ch["centre"]
		var r := float(ch["radius"])
		var pos := c + Vector3(cos(th) * r, cfg.chopper_altitude, sin(th) * r)
		var head := Vector3(-sin(th), 0.0, cos(th)) * float(ch["dir"])
		_choppers[k].transform = Transform3D(_heading_basis(head), pos)
		var tgt := c + Vector3(cos(th) * r * 0.35 + wob * sin(t_c * 1.7 + k), 0.0, sin(th) * r * 0.35 + wob * cos(t_c * 1.3 + k))
		_spot(i, pos - Vector3.UP * cfg.chopper_length * 0.25, tgt, cfg.chopper_spot_radius)
		_air_lights(light, pos, head, cfg.chopper_length)
		i += 1
		light += 2
	var t_d := clock.times[CityMotionClock.Layer.DRONES]
	var dwob := Motion.amplitude(DRONE)
	for k in rig.drones.size():
		var dr: Dictionary = rig.drones[k]
		var th := TAU * (float(dr["dir"]) * t_d / _period(DRONE) + float(dr["phase"]))
		var c: Vector3 = dr["centre"]
		var pos := c + Vector3(cos(th) * cfg.drone_orbit, cfg.drone_altitude, sin(th) * cfg.drone_orbit)
		_drones[k].transform = Transform3D(Basis.IDENTITY, pos)
		var tgt := Vector3(pos.x + dwob * sin(t_d * 2.1 + k), 0.0, pos.z + dwob * cos(t_d * 1.7 + k))
		_spot(i, pos, tgt, cfg.drone_spot_radius)
		_air_lights(light, pos, Vector3.RIGHT, cfg.drone_size)
		i += 1
		light += 2


## Spot beam `i` from `from` down to `to` (a pool of `radius` there).
func _spot(i: int, from: Vector3, to: Vector3, radius: float) -> void:
	var d := from - to
	_spot_mmi.multimesh.set_instance_transform(i, _beam(from, -d.normalized(), d.length(), radius))
	_spot_mmi.multimesh.set_instance_color(i, cfg.spot_color)
	_spot_mmi.multimesh.set_instance_custom_data(i, Color(cfg.spot_alpha, 0.0, 0.0, 0.0))
	_pool_mmi.multimesh.set_instance_transform(i, Transform3D(Basis.IDENTITY.scaled(Vector3.ONE * radius * 1.3), to + Vector3.UP * POOL_LIFT))
	_pool_mmi.multimesh.set_instance_color(i, cfg.spot_color)
	_pool_mmi.multimesh.set_instance_custom_data(i, Color(cfg.pool_alpha, 0.0, 0.0, 0.0))


## The red and blue nav lights of an aircraft at `pos` heading `head`, `size` BU long.
func _air_lights(i: int, pos: Vector3, head: Vector3, size: float) -> void:
	var side := Vector3(-head.z, 0.0, head.x) * size * 0.35
	_air_light_mmi.multimesh.set_instance_transform(i, Transform3D(Basis.IDENTITY, pos + side))
	_air_light_mmi.multimesh.set_instance_transform(i + 1, Transform3D(Basis.IDENTITY, pos - side))


## The unit cone placed with its apex at `apex`, opening along `dir`, `length` long and
## `radius` wide at its end.
static func _beam(apex: Vector3, dir: Vector3, length: float, radius: float) -> Transform3D:
	var y := -dir.normalized()
	var ref := Vector3.RIGHT if absf(y.x) < 0.9 else Vector3.FORWARD
	var x := ref.cross(y).normalized()
	var z := x.cross(y).normalized()
	return Transform3D(Basis(x * radius, y * length, z * radius), apex)


static func _heading_basis(head: Vector3) -> Basis:
	var x := head.normalized()
	var z := x.cross(Vector3.UP).normalized()
	return Basis(x, Vector3.UP, z)


## The spill sources (billboards and searchlight roofs) nearest the focus point, as
## LightSpill.uniforms_3d packs them; sent up and set on the aircraft's toon materials.
func _update_spill() -> void:
	var src: Array[Dictionary] = []
	var n := night_share
	for b in props.billboards:
		src.append({"position": b["pos"], "radius": cfg.billboard_spill_radius, "color": cfg.lane_colors[int(b["color"])],
			"intensity": cfg.billboard_spill * cfg.spill_gain * lerpf(cfg.billboard_gain_day, cfg.billboard_gain_night, n) / cfg.billboard_gain_night})
	if rig != null:
		for sl in rig.searchlights:
			src.append({"position": sl["pos"], "radius": cfg.searchlight_spill_radius, "color": cfg.searchlight_color,
				"intensity": cfg.searchlight_spill * cfg.spill_gain})
	var f := _focus
	src.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var da := (a["position"] as Vector3).distance_squared_to(f)
		var db := (b["position"] as Vector3).distance_squared_to(f)
		if da != db:
			return da < db
		var pa: Vector3 = a["position"]
		var pb: Vector3 = b["position"]
		return pa.x < pb.x if pa.x != pb.x else pa.z < pb.z)
	_spill = LightSpill.uniforms_3d(src)
	_spill_sources = src.slice(0, LightSpill.MAX_3D)
	for m in _air_mats:
		ToonInkMaterial.set_spill(m, _spill_sources)
	spill_changed.emit(_spill_sources)
