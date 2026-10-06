class_name CityViewMotion
extends Node
## ART-5 5c: puts the city's motion layers (CityMotionLayers) on 5a's one 3D city
## (CityView3D) through its scene-layer seam. Once the view's model is built it makes the
## site (CityMotionSite.from_model), builds the layers and moves their groups into the
## view's layers (traffic, sky, props, heat; traffic, sky and heat also in the ground-only
## pass under see-through buildings), then wires the view's signals down to them: the zoom
## (camera_changed: car LOD, sprite sizes, spill focus), the band (band_changed: GRID / RAID
## / NETRUN), the host's pause (host_pause_changed: covered or unfocused pauses every layer;
## ART-5 5e: not the view's ambient scale, which is 0 under reduce motion while the street
## traffic keeps moving at 40 %, bible 5.4). Up from the layers: the light spill to
## `CityView3D.set_spill`, and the day / night look through the view's day-look call
## (`CityView3D.set_night_share`, landmarks included). A view: no game state changes. Add it
## as a child of the CityView3D.

var view: CityView3D
var layers: CityMotionLayers
var motion_cfg: CityMotionConfigData
## The Cell's district centre (lots), where suspicion gathers.
var home_lot: Vector2 = Vector2.INF
## ART-5 5e: the Heat look asked before the layers were built (band, hardened nodes), or [].
var _heat: Array = []


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
		# Deferred: the host sets the home lot and the Heat look in the same frame.
		_attach.call_deferred()
	else:
		view.model_ready.connect(_attach, CONNECT_ONE_SHOT)


func _attach() -> void:
	var site := CityMotionSite.from_model(view.model, view.cfg, home_lot)
	layers = CityMotionLayers.new()
	view.add_to_layer(&"fx", layers)
	layers.night_share_changed.connect(_on_night_share)
	layers.spill_changed.connect(_on_spill)
	layers.setup(motion_cfg, site, view.city_seed)
	for name_ in CityMotionLayers.GROUPS:
		var g: Node3D = layers.groups[name_]
		g.reparent(view.layer(name_), false)
	layers.set_ground_pass_layer(CityView3D.GROUND_LAYER)
	view.camera_changed.connect(_on_camera)
	view.band_changed.connect(_on_band)
	view.host_pause_changed.connect(_on_host_pause)
	_on_host_pause(view.host_paused())
	if view.band >= 0:
		_on_band(view.band)
	if view.iso != null:
		_on_camera(view.iso)
	if not _heat.is_empty():
		layers.set_heat(int(_heat[0]), _heat[1])


## ART-5 5e: the Grid's Heat look (CityHeatRig.Band and the hardened nodes, world points);
## kept until the layers are built.
func set_heat(band: int, hardened: Array[Vector3]) -> void:
	_heat = [band, hardened]
	if layers != null:
		layers.set_heat(band, hardened)


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


## ART-5 5e: the host's pause to the layers (0 paused, 1 live; their own reduce rules apply).
func _on_host_pause(paused: bool) -> void:
	layers.set_host_ambient(0.0 if paused else 1.0)


## ART-5 5e: the motion config's day look as CityView3D.set_night_share takes it.
static func day_look(mcfg: CityMotionConfigData) -> Dictionary:
	return {"ramp": mcfg.day_ramp.duplicate(), "sky": mcfg.day_sky, "window_gain": mcfg.day_window_gain,
		"neon_gain": mcfg.day_neon_gain, "haze": mcfg.day_haze, "grade": mcfg.day_grade}


## The night look lerped toward the config's day look by night share `n` (1 night, 0 day).
func _on_night_share(n: float) -> void:
	view.set_night_share(n, day_look(motion_cfg))
