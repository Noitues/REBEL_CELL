extends SceneTree
## Frame-time profile (dev tool, Animation pass ANIM-6): loads a scene (default the HQ with
## `--demo-hq`), lets it settle, then times FRAMES frames with vsync off and prints the mean
## and 95th-percentile frame time, the CPU render time and the process time. Needs a real
## display (the city is baked on the GPU); never headless.
##
##   godot --path . -s tools/design_lab/profile_frames.gd -- --demo-hq [--scene=res://...]
##     [--reduce] (reduce effects on: the city's live layer off)
##
## ANIM-R1 M2: `--timeline` times every frame from the first (no warm-up) for `--frames=N`
## (default FRAMES) and prints the longest frame and every frame over SPIKE_MS with its
## number, so a flow (e.g. `--demo-playout-delay=<frames>`: the raid setup, then START
## DEFENSE) can be read for hitches frame by frame.
##
## ANIM-R2 R1: `--probe-map` (with --timeline) also prints, frame by frame, when each map on
## screen has its nodes placed (a CityMapOverlay's nodes with a roof, of all), when its city's
## view is covered by a finished bake, when the bake has faded in, and the jack's cover, with
## the game time: "probe f12 +0.19s: map 32/32 nodes", "probe f140 +2.31s: city covered".

const WARMUP := 120
const FRAMES := 600
## ANIM-R1 M2: a frame longer than this (ms) is listed as a hitch in --timeline.
const SPIKE_MS := 50.0

var _frame := 0
var _times: Array[float] = []
var _cpu: Array[float] = []
var _gpu: Array[float] = []
var _proc: Array[float] = []
var _last := 0
var _vp: RID
var _timeline: bool = false
var _frames: int = FRAMES
var _warmup: int = WARMUP
var _probe: bool = false
var _probe_state: Dictionary = {}
var _t0: int = 0


func _initialize() -> void:
	var path := "res://scenes/hq/hq_scene.tscn"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--scene="):
			path = a.trim_prefix("--scene=")
		elif a == "--timeline":
			_timeline = true
			_warmup = 1
		elif a.begins_with("--frames="):
			_frames = int(a.trim_prefix("--frames="))
		elif a == "--probe-map":
			_probe = true
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	var scene: Node = (load(path) as PackedScene).instantiate()
	root.add_child(scene)
	_t0 = Time.get_ticks_usec()
	_vp = root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(_vp, true)


func _process(_delta: float) -> bool:
	_frame += 1
	if _frame < _warmup or (_timeline and _frame < 3):
		# The Settings autoload applies its own vsync on start: switch it off again.
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		Engine.max_fps = 0
	if _frame == 1 and OS.get_cmdline_user_args().has("--reduce"):
		# Reduce effects for this run only (not saved): the live layers stop.
		var settings := root.get_node("Settings")
		settings.set("reduce_effects", true)
		settings.emit_signal("changed")
	var now := Time.get_ticks_usec()
	if _frame > _warmup:
		_times.append((now - _last) / 1000.0)
		_cpu.append(RenderingServer.viewport_get_measured_render_time_cpu(_vp) + RenderingServer.get_frame_setup_time_cpu())
		_gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(_vp))
		_proc.append(Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0)
	_last = now
	if _probe:
		_probe_frame()
	if _frame >= _warmup + _frames:
		_report()
		return true
	return false


func _report() -> void:
	if _timeline:
		var spikes := PackedStringArray()
		var worst := 0.0
		for i in _times.size():
			worst = maxf(worst, _times[i])
			if _times[i] > SPIKE_MS:
				# ANIM-R2: what the frame spent: its scripts and process, and the render's CPU.
				spikes.append("f%d %.0f ms (process %.0f, render cpu %.0f)" % [i + _warmup + 1, _times[i], _proc[i], _cpu[i]])
		print("profile_frames timeline: %d frames, max %.1f ms; over %.0f ms: %s" % [_times.size(), worst, SPIKE_MS, ", ".join(spikes) if not spikes.is_empty() else "none"])
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


## ANIM-R2 R1: prints each change of what the maps on screen show (see the notes above).
func _probe_frame() -> void:
	var now := {}
	for n in root.find_children("*", "Control", true, false):
		var c := n as Control
		if not c.is_visible_in_tree():
			continue
		var cls := _cls(c)
		if cls == "CityMapOverlay":
			var nodes: Array = c.get("nodes")
			var placed := 0
			for d: Dictionary in nodes:
				var at: Vector2 = c.call("icon_at", d["id"])
				if at.x != INF:
					placed += 1
			now["map %s" % c.get_instance_id()] = "map %d/%d nodes" % [placed, nodes.size()]
		elif cls == "NeonCity" and bool(c.call("is_baked")):
			var covered: bool = c.call("view_covered")
			var fv: Variant = c.get("bake_fade")
			var fade: float = float(fv) if fv != null else 1.0
			now["city %s" % c.get_instance_id()] = "city %s%s" % ["covered" if covered else "sky/stand-in", "" if fade >= 1.0 else " fading"]
	var fx := root.get_node_or_null("Fx")
	if fx != null:
		now["jack"] = "jack cover" if bool(fx.call("transitioning")) else "no jack"
	for k in now:
		if _probe_state.get(k, "") != now[k]:
			print("probe f%d +%.2fs: %s" % [_frame, (Time.get_ticks_usec() - _t0) / 1000000.0, now[k]])
	_probe_state = now


func _cls(n: Node) -> String:
	var sc: Script = n.get_script()
	return String(sc.get_global_name()) if sc != null else ""
