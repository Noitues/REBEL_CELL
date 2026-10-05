extends Node3D
## ART-5 5c: windowed captures and the frame-cost probe of the city's motion layers on 1D's
## spike city (through CitySpikeMotion, the seam). One launch walks every state (view /
## zoom, day / night, Heat band, suspicion, reduce motion / effects) and writes one PNG per
## state; or, with --mperf, measures the frame with the layers on and off. Windowed only:
##   python tools/run_windowed.py --log <f> -- --resolution 1600x900 \
##     res://tools/spike/city/city_motion_capture.tscn -- --size=1600x900 --out=<dir> [--states=a,b]
##   ... --size=1920x1080 --quality=2 --mperf=6 [--perf-states=grid_hunted,raid_hunted]
## The spike reads --size and --quality itself.

const SPIKE := preload("res://tools/spike/city/city_spike_3d.tscn")
## The Cell's home and the hardened nodes of the captures (lots, round the raid frame).
const HOME_LOT := Vector2(30, 27)
const HARDENED_LOTS: Array[Vector2] = [Vector2(30, 28), Vector2(34, 31), Vector2(31, 33)]
## Frames the spike takes to size its window and frame its view.
const BOOT_FRAMES := 8
const SETTLE := 40
const WARM := 90
## The states: view, Heat band, suspicion, day, reduce motion, reduce effects.
const STATES := {
	"grid_night": ["grid", 0, false, false, false, false],
	"grid_night_later": ["grid", 0, false, false, false, false],
	"grid_day": ["grid", 0, false, true, false, false],
	"grid_noticed": ["grid", 1, false, false, false, false],
	"grid_flagged": ["grid", 2, false, false, false, false],
	"grid_hunted": ["grid", 3, false, false, false, false],
	"grid_purge": ["grid", 4, false, false, false, false],
	"grid_suspicion_day": ["grid", 0, true, true, false, false],
	"raid_hunted": ["raid", 3, false, false, false, false],
	"raid_day": ["raid", 2, false, true, false, false],
	"netrun_flagged": ["netrun", 2, false, false, false, false],
	"close_night": ["close", 2, false, false, false, false],
	"close_day": ["close", 0, false, true, false, false],
	"grid_reduce_motion": ["grid", 3, false, false, true, false],
	"grid_reduce_effects": ["grid", 3, false, false, false, true],
}
const VIEWS := {"grid": CityMotionLayers.View.GRID, "raid": CityMotionLayers.View.RAID,
	"netrun": CityMotionLayers.View.NETRUN, "close": CityMotionLayers.View.NETRUN}

var _args: Dictionary = {}
var _spike: Node3D
var _motion: CitySpikeMotion
var _frame: int = 0
var _queue: Array[String] = []
var _state: String = ""
var _state_frame: int = 0
var _out: String = ""
var _perf: Dictionary = {}
var _rm: bool = false
var _re: bool = false


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	_rm = Settings.reduce_motion
	_re = Settings.reduce_effects
	_spike = SPIKE.instantiate()
	add_child(_spike)
	_motion = CitySpikeMotion.attach(_spike, CityMotionConfigData.shipped(), HOME_LOT)
	# A quiet window never has focus; the capture keeps the layers running regardless.
	_motion.layers.honour_focus = false
	_out = String(_args.get("out", ""))
	if _args.has("mperf"):
		_queue.assign(String(_args.get("perf-states", "grid_hunted,raid_hunted")).split(","))
	else:
		var names: Array = STATES.keys() if not _args.has("states") else Array(String(_args["states"]).split(","))
		_queue.assign(names)


func _process(_delta: float) -> void:
	_frame += 1
	if _frame < BOOT_FRAMES:
		return
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
		print("MOTION shot %s %dx%d tier=%d sky_cars=%d visible=%s rig=%s" % [path, img.get_width(), img.get_height(),
			_motion.layers.car_tier, _motion.layers.traffic.cars.size(), _motion.layers.sky_cars_visible(),
			str([_motion.layers.rig.searchlights.size(), _motion.layers.rig.alarms.size(), _motion.layers.rig.police.size(),
			_motion.layers.rig.choppers.size(), _motion.layers.rig.drones.size(), _motion.layers.rig.node_lights.size()])])
		_state = ""


func _apply(name: String) -> void:
	var s: Array = STATES[name]
	Settings.reduce_motion = bool(s[4])
	Settings.reduce_effects = bool(s[5])
	Fx.apply_settings()
	_spike.call("apply_view", String(s[0]))
	var layers := _motion.layers
	layers.set_view(VIEWS[String(s[0])])
	var iso: CityIsoCamera = _spike.get("iso")
	_motion.set_ortho(iso.ortho)
	var nodes: Array[Vector3] = []
	for lot in HARDENED_LOTS:
		nodes.append(layers.site.lot_to_world(lot))
	layers.set_heat(int(s[1]), nodes)
	layers.set_light(CityMotionLayers.Daylight.DAY if bool(s[3]) else CityMotionLayers.Daylight.NIGHT, bool(s[2]))
	print("MOTION state %s ortho=%.0f" % [name, iso.ortho])


## Frame cost with the layers on, then off, after WARM frames each.
func _probe() -> void:
	var secs := float(_args["mperf"])
	var rid := get_viewport().get_viewport_rid()
	if _state_frame == 1:
		RenderingServer.viewport_set_measure_render_time(rid, true)
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		Engine.max_fps = 0
		_set_layers(true)
	var phase := "on" if _motion.layers.visible else "off"
	var key := _state + "_" + phase
	if not _perf.has(key):
		_perf[key] = {"start": _state_frame, "n": 0, "gpu": 0.0, "cpu": 0.0, "t0": 0, "last": 0}
	var p: Dictionary = _perf[key]
	var now := Time.get_ticks_usec()
	if _state_frame - int(p["start"]) < WARM:
		p["t0"] = now
		return
	p["n"] = int(p["n"]) + 1
	p["gpu"] = float(p["gpu"]) + RenderingServer.viewport_get_measured_render_time_gpu(rid)
	p["cpu"] = float(p["cpu"]) + RenderingServer.viewport_get_measured_render_time_cpu(rid) + RenderingServer.get_frame_setup_time_cpu()
	if now - int(p["t0"]) >= int(secs * 1000000.0):
		var n := float(p["n"])
		print("PERF state=%s layers=%s size=%s frames=%d frame_avg_ms=%.3f gpu_ms=%.3f cpu_ms=%.3f draws=%.0f prims=%.0f" % [_state, phase,
			str(get_viewport().get_visible_rect().size), int(n), (now - int(p["t0"])) / 1000.0 / n, float(p["gpu"]) / n,
			float(p["cpu"]) / n, Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
			Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)])
		if phase == "on":
			_set_layers(false)
		else:
			_state = ""


func _set_layers(on: bool) -> void:
	_motion.layers.visible = on
	_motion.layers.process_mode = Node.PROCESS_MODE_INHERIT if on else Node.PROCESS_MODE_DISABLED


func _finish() -> void:
	Settings.reduce_motion = _rm
	Settings.reduce_effects = _re
	print("MOTION done")
	get_tree().quit()
