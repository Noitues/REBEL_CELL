extends SceneTree
## Frame-time profile (dev tool, Animation pass ANIM-6): loads a scene (default the HQ with
## `--demo-hq`), lets it settle, then times FRAMES frames with vsync off and prints the mean
## and 95th-percentile frame time, the CPU render time and the process time. Needs a real
## display (the city is baked on the GPU); never headless.
##
##   godot --path . -s tools/design_lab/profile_frames.gd -- --demo-hq [--scene=res://...]
##     [--reduce] (reduce effects on: the city's live layer off)

const WARMUP := 120
const FRAMES := 600

var _frame := 0
var _times: Array[float] = []
var _cpu: Array[float] = []
var _gpu: Array[float] = []
var _last := 0
var _vp: RID


func _initialize() -> void:
	var path := "res://scenes/hq/hq_scene.tscn"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--scene="):
			path = a.trim_prefix("--scene=")
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	var scene: Node = (load(path) as PackedScene).instantiate()
	root.add_child(scene)
	_vp = root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(_vp, true)


func _process(_delta: float) -> bool:
	_frame += 1
	if _frame < WARMUP:
		# The Settings autoload applies its own vsync on start: switch it off again.
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		Engine.max_fps = 0
	if _frame == 1 and OS.get_cmdline_user_args().has("--reduce"):
		# Reduce effects for this run only (not saved): the live layers stop.
		var settings := root.get_node("Settings")
		settings.set("reduce_effects", true)
		settings.emit_signal("changed")
	var now := Time.get_ticks_usec()
	if _frame > WARMUP:
		_times.append((now - _last) / 1000.0)
		_cpu.append(RenderingServer.viewport_get_measured_render_time_cpu(_vp) + RenderingServer.get_frame_setup_time_cpu())
		_gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(_vp))
	_last = now
	if _frame >= WARMUP + FRAMES:
		_report()
		return true
	return false


func _report() -> void:
	_times.sort()
	var mean := 0.0
	for t in _times:
		mean += t
	mean /= maxf(1.0, _times.size())
	var cpu := 0.0
	for t in _cpu:
		cpu += t
	cpu /= maxf(1.0, _cpu.size())
	var gpu := 0.0
	for t in _gpu:
		gpu += t
	gpu /= maxf(1.0, _gpu.size())
	print("profile_frames: %d frames: mean %.3f ms (%.0f fps), p95 %.3f ms, render cpu %.3f ms, gpu %.3f ms" % [
		_times.size(), mean, 1000.0 / maxf(0.001, mean), _times[int(_times.size() * 0.95)], cpu, gpu])
