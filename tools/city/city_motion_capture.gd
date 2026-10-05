extends Control
## ART-5 5c: windowed captures and the frame-cost probe of the city's motion layers on 5a's
## one 3D city (CityView3D + CityViewMotion, the scene-layer seam). One launch walks every
## state (view / zoom, day / night, Heat band, suspicion, reduce motion / effects, covered)
## and writes one PNG per state; or, with --mperf, measures the frame with the layers on and
## off per state. Windowed only (headless has no renderer):
##   python tools/run_windowed.py --log <f> -- --resolution 1600x900 \
##     res://tools/city/city_motion_capture.tscn -- --out=<dir> [--states=a,b] [--quality=2]
##   ... --resolution 1920x1080 res://tools/city/city_motion_capture.tscn -- --mperf=6
##       [--perf-states=grid_hunted,raid_hunted] [--quality=1]
##   --host=spike: on 1D's spike district (CitySpikeMotion) instead of the CityView3D.

## The Cell's home and the hardened nodes of the captures (lots, round the raid frame).
const HOME_LOT := Vector2(30, 27)
const HARDENED_LOTS: Array[Vector2] = [Vector2(30, 28), Vector2(34, 31), Vector2(31, 33)]
const SETTLE := 40
const WARM := 90
## The states: view, Heat band, suspicion, day, reduce motion, reduce effects, covered.
const STATES := {
	"grid_night": ["grid", 0, false, false, false, false, false],
	"grid_night_later": ["grid", 0, false, false, false, false, false],
	"grid_day": ["grid", 0, false, true, false, false, false],
	"grid_noticed": ["grid", 1, false, false, false, false, false],
	"grid_flagged": ["grid", 2, false, false, false, false, false],
	"grid_hunted": ["grid", 3, false, false, false, false, false],
	"grid_purge": ["grid", 4, false, false, false, false, false],
	"grid_suspicion_day": ["grid", 0, true, true, false, false, false],
	"raid_hunted": ["raid", 3, false, false, false, false, false],
	"raid_day": ["raid", 2, false, true, false, false, false],
	"netrun_flagged": ["netrun", 2, false, false, false, false, false],
	"close_night": ["close", 2, false, false, false, false, false],
	"close_day": ["close", 0, false, true, false, false, false],
	"grid_reduce_motion": ["grid", 3, false, false, true, false, false],
	"grid_reduce_effects": ["grid", 3, false, false, false, true, false],
}

var _args: Dictionary = {}
var _view: CityView3D
var _motion: CityViewMotion
var _queue: Array[String] = []
var _state: String = ""
var _state_frame: int = 0
var _out: String = ""
var _perf: Dictionary = {}
var _rm: bool = false
var _re: bool = false
var _q: int = -1
var _spike: Node3D
var _spike_motion: CitySpikeMotion
var _frame: int = 0


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	_rm = Settings.reduce_motion
	_re = Settings.reduce_effects
	_q = Settings.city_quality
	if _args.has("quality"):
		Settings.city_quality = int(_args["quality"])
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_out = String(_args.get("out", ""))
	if _args.has("mperf"):
		_queue.assign(String(_args.get("perf-states", "grid_hunted,raid_hunted")).split(","))
	else:
		var names: Array = STATES.keys() if not _args.has("states") else Array(String(_args["states"]).split(","))
		_queue.assign(names)
	if String(_args.get("host", "")) == "spike":
		_spike = load("res://tools/spike/city/city_spike_3d.tscn").instantiate()
		add_child(_spike)
		_spike_motion = CitySpikeMotion.attach(_spike, CityMotionConfigData.shipped(), HOME_LOT)
		return
	var box := SubViewportContainer.new()
	box.stretch = true
	box.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(box)
	_view = CityView3D.new()
	_view.size = Vector2i(get_viewport().get_visible_rect().size)
	box.add_child(_view)
	_motion = CityViewMotion.make(_view, null, HOME_LOT)
	_view.add_child(_motion)


func _layers() -> CityMotionLayers:
	return _spike_motion.layers if _spike_motion != null else _motion.layers


func _process(_delta: float) -> void:
	_frame += 1
	if _layers() == null or (_spike != null and _frame < 8):
		return
	# A quiet window never has focus: the capture keeps the layers running regardless.
	_layers().honour_focus = false
	if _state == "":
		if _queue.is_empty():
			_finish()
			return
		_state = _queue.pop_front()
		_state_frame = 0
		_apply(_state)
	_state_frame += 1
	if _args.has("mperf"):
		_probe()
		return
	var settle := int(_args.get("settle", str(SETTLE)))
	if _state == "grid_night_later":
		settle += int(_args.get("later", "15"))
	if _state_frame == settle:
		var img := get_viewport().get_texture().get_image()
		var path := _out.path_join("%s.png" % _state)
		img.save_png(path)
		var l := _layers()
		print("MOTION shot %s %dx%d tier=%d view=%d sky_cars=%d visible=%s rig=%s" % [path, img.get_width(), img.get_height(),
			l.car_tier, l.view, l.traffic.cars.size(), l.sky_cars_visible(), str([l.rig.searchlights.size(), l.rig.alarms.size(),
			l.rig.police.size(), l.rig.choppers.size(), l.rig.drones.size(), l.rig.node_lights.size()])])
		_state = ""


func _apply(name: String) -> void:
	var s: Array = STATES[name]
	Settings.reduce_motion = bool(s[4])
	Settings.reduce_effects = bool(s[5])
	Fx.apply_settings()
	Settings.changed.emit()
	var layers := _layers()
	var band := -1
	var v: Array = []
	if _spike_motion != null:
		var scfg: CityConfig = _spike.get("cfg")
		v = scfg.views[String(s[0])]
		_spike.call("apply_view", String(s[0]))
		_spike_motion.set_ortho(float(v[2]))
		band = CityLod.band(scfg, float(v[2]))
		var bands := {CityLod.Band.GRID: CityMotionLayers.View.GRID, CityLod.Band.RAID: CityMotionLayers.View.RAID,
			CityLod.Band.NETRUN: CityMotionLayers.View.NETRUN}
		layers.set_view(bands[band])
		layers.set_covered(bool(s[6]))
	else:
		_view.covered = bool(s[6])
		var cfg := _view.cfg
		v = cfg.views[String(s[0])]
		var target := CityIsoCamera.lot_to_world(cfg, Vector2(float(v[0]), float(v[1])))
		_view.set_iso(CityIsoCamera.make(cfg, target, float(v[2]), Vector2(_view.size)))
		band = _view.band
	if String(s[0]) == "close":
		# The CLOSE car tier's render check: at netrun zooms the game turns the sky-lane cars
		# off (bible 4.1); the capture shows the tier as a zoomed City Grid would.
		layers.set_view(CityMotionLayers.View.GRID)
	var nodes: Array[Vector3] = []
	for lot in HARDENED_LOTS:
		nodes.append(layers.site.lot_to_world(lot))
	layers.set_heat(int(s[1]), nodes)
	layers.set_light(CityMotionLayers.Daylight.DAY if bool(s[3]) else CityMotionLayers.Daylight.NIGHT, bool(s[2]))
	print("MOTION state %s ortho=%.0f band=%d" % [name, float(v[2]), band])


## Frame cost with the layers on, then off, after WARM frames each.
func _probe() -> void:
	var secs := float(_args["mperf"])
	var rid := get_viewport().get_viewport_rid()
	var vrid := _view.get_viewport_rid() if _view != null else rid
	if _state_frame == 1:
		RenderingServer.viewport_set_measure_render_time(rid, true)
		RenderingServer.viewport_set_measure_render_time(vrid, true)
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		Engine.max_fps = 0
		_set_layers(true)
	var phase := "on" if _layers().process_mode != Node.PROCESS_MODE_DISABLED else "off"
	var key := _state + "_" + phase
	if not _perf.has(key):
		_perf[key] = {"start": _state_frame, "n": 0, "gpu": 0.0, "cpu": 0.0, "t0": 0}
	var p: Dictionary = _perf[key]
	var now := Time.get_ticks_usec()
	if _state_frame - int(p["start"]) < WARM:
		p["t0"] = now
		return
	p["n"] = int(p["n"]) + 1
	p["gpu"] = float(p["gpu"]) + RenderingServer.viewport_get_measured_render_time_gpu(vrid) + (RenderingServer.viewport_get_measured_render_time_gpu(rid) if vrid != rid else 0.0)
	p["cpu"] = float(p["cpu"]) + RenderingServer.viewport_get_measured_render_time_cpu(vrid) + RenderingServer.get_frame_setup_time_cpu()
	if now - int(p["t0"]) >= int(secs * 1000000.0):
		var n := float(p["n"])
		print("PERF window=" + str(DisplayServer.window_get_size()) + " state=%s layers=%s size=%s quality=%s frames=%d frame_avg_ms=%.3f gpu_ms=%.3f cpu_ms=%.3f draws=%.0f prims=%.0f" % [_state,
			phase, str(get_viewport().get_visible_rect().size), str((_view.quality if _view != null else _spike.get("quality")).get("tier", -1)), int(n), (now - int(p["t0"])) / 1000.0 / n,
			float(p["gpu"]) / n, float(p["cpu"]) / n, Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
			Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)])
		if phase == "on":
			_set_layers(false)
		else:
			_state = ""


## The layers on or off (every group hidden and the clock stopped).
func _set_layers(on: bool) -> void:
	var l := _layers()
	l.process_mode = Node.PROCESS_MODE_INHERIT if on else Node.PROCESS_MODE_DISABLED
	for g: Node3D in l.groups.values():
		g.visible = on


func _finish() -> void:
	Settings.reduce_motion = _rm
	Settings.reduce_effects = _re
	Settings.city_quality = _q
	print("MOTION done")
	get_tree().quit()
