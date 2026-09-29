extends SceneTree
## City frame-time probe (art pass W7, ART_BIBLE 13): loads a scene, waits until every city
## bake has landed and the city has settled, then times SAMPLE frames with vsync off and
## prints the mean, median and 95th-percentile frame time and the GPU time of the root
## viewport. Real display only (the city bakes on the GPU); run it through
## tools/run_windowed.py with a private APPDATA:
##
##   python tools/run_windowed.py --log out.log -- --resolution 1920x1080 \
##       -s tools/design_lab/city_perf.gd -- --scene=res://scenes/menu/title_scene.tscn
##   ... -- --demo-grid                      (the HQ scene's Grid; the default scene)
##   ... -- --scene=res://scenes/combat/combat_scene.tscn
##   --reduce   reduce effects on for this run (never saved)
##   --tier=N   the city's quality tier (CityAtmosphere.quality; see city_look.tres)
##   --legacy   the pre-W7 look (CityAtmosphere.enabled off): the "before" in one build

## Frames the scene gets before the bake wait starts, frames sampled, and the longest the
## wait may take (frames) before sampling anyway.
const START_FRAMES := 30
const SAMPLE := 900
const SETTLE_FRAMES := 120
const WAIT_MAX := 3000

var _frame: int = 0
var _state: int = 0
var _settled: int = 0
var _times: Array[float] = []
var _gpu: Array[float] = []
var _last: int = 0
var _vp: RID


func _initialize() -> void:
	var path := "res://scenes/hq/hq_scene.tscn"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--scene="):
			path = a.trim_prefix("--scene=")
	var scene: Node = (load(path) as PackedScene).instantiate()
	root.add_child(scene)
	_vp = root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(_vp, true)


func _process(_delta: float) -> bool:
	_frame += 1
	# (Setting the mode every frame rebuilds the swapchain: only when Settings changed it.)
	if DisplayServer.window_get_vsync_mode() != DisplayServer.VSYNC_DISABLED:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	if _frame == 2:
		var settings := root.get_node("Settings")
		if OS.get_cmdline_user_args().has("--reduce"):
			settings.set("reduce_effects", true)
			settings.emit_signal("changed")
		var path := "res://scripts/ui/kit/city_atmosphere.gd"
		for a in OS.get_cmdline_user_args():
			if a.begins_with("--tier=") and ResourceLoader.exists(path):
				(load(path) as Script).set("quality", int(a.trim_prefix("--tier=")))
			elif a == "--legacy" and ResourceLoader.exists(path):
				(load(path) as Script).set("enabled", false)
		# Every city pushes its state again (the tier and the switch are read on a push).
		for n in root.find_children("*", "Control", true, false):
			if n.has_method("atmosphere") and not bool(n.get("_painter")):
				n.call("atmosphere").call("_mark")
	var now := Time.get_ticks_usec()
	match _state:
		0:
			# Wait for the bakes (and a settle) before sampling.
			if _frame > START_FRAMES:
				_settled = _settled + 1 if int(_cache().call("busy")) == 0 else 0
				if _settled >= SETTLE_FRAMES or _frame > WAIT_MAX:
					_state = 1
					print("city_perf: sampling from frame %d" % _frame)
		1:
			_times.append((now - _last) / 1000.0)
			_gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(_vp))
			if _times.size() >= SAMPLE:
				_report()
				return true
	_last = now
	return false


func _report() -> void:
	var mean := _mean(_times)
	var gpu := _mean(_gpu)
	_times.sort()
	_gpu.sort()
	print("city_perf: %d frames: mean %.3f ms (%.0f fps), p50 %.3f, p95 %.3f, gpu mean %.3f p95 %.3f ms" % [
		_times.size(), mean, 1000.0 / maxf(0.001, mean), _times[_times.size() / 2], _times[int(_times.size() * 0.95)],
		gpu, _gpu[int(_gpu.size() * 0.95)]])


## The bake cache's script (loaded at run time: a -s script compiles before the autoloads
## its class depends on exist).
func _cache() -> Script:
	return load("res://scripts/ui/kit/city_bake_cache.gd")


func _mean(a: Array[float]) -> float:
	var s := 0.0
	for t in a:
		s += t
	return s / maxf(1.0, a.size())
