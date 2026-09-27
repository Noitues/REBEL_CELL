extends SceneTree
## Frame-time probe for the city backdrop (H20). Non-headless only:
##   godot --path . --resolution 1280x720 -s tools/city_perf_probe.gd -- --probe-scene=res://scenes/hq/hq_scene.tscn --demo-hq
## Loads the scene, turns vsync off, skips WARMUP frames, then averages frame time,
## the root viewport's measured render time (CPU and GPU) over SAMPLE_USEC (8 s of
## frames) and prints PROBE lines (plus the bake cache; --probe-dump=<dir> saves its
## images). Uses the scene's own --demo-* save slot (back up profile.json first).

const WARMUP := 120
const SAMPLE_USEC := 8_000_000
var _sample_start: int = 0

var _frame: int = 0
var _deltas: Array[float] = []
var _cpu: float = 0.0
var _gpu: float = 0.0
var _proc: float = 0.0
var _last_us: int = 0
var _first_us: int = 0
var _scene_path: String = ""


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--probe-scene="):
			_scene_path = a.trim_prefix("--probe-scene=")
	var packed := load(_scene_path) as PackedScene
	if packed == null:
		print("PROBE no scene %s" % _scene_path)
		quit(1)
		return
	_first_us = Time.get_ticks_usec()
	root.add_child(packed.instantiate())
	RenderingServer.viewport_set_measure_render_time(root.get_viewport_rid(), true)


func _process(_delta: float) -> bool:
	_frame += 1
	if DisplayServer.window_get_vsync_mode() != DisplayServer.VSYNC_DISABLED:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	if _frame == 2:
		print("PROBE first frames %.1f ms" % ((Time.get_ticks_usec() - _first_us) / 1000.0))
	if _frame == WARMUP and OS.get_cmdline_user_args().has("--probe-stop"):
		for n in root.find_children("*", "Control", true, false):
			if _cls(n) == "CityMapOverlay" or (_cls(n) == "NeonCity" and not OS.get_cmdline_user_args().has("--probe-stop-overlay-only")):
				n.set_process(false)
	if _frame == WARMUP and OS.get_cmdline_user_args().has("--probe-hide"):
		for n in root.find_children("*", "Control", true, false):
			if _cls(n) == "NeonCity":
				(n as Control).visible = false
	var now := Time.get_ticks_usec()
	if _frame > WARMUP:
		_deltas.append((now - _last_us) / 1000.0)
		_cpu += RenderingServer.viewport_get_measured_render_time_cpu(root.get_viewport_rid()) + RenderingServer.get_frame_setup_time_cpu()
		_gpu += RenderingServer.viewport_get_measured_render_time_gpu(root.get_viewport_rid())
		_proc += Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0
	_last_us = now
	if _frame == WARMUP + 1:
		_sample_start = now
	if _frame > WARMUP + 1 and now - _sample_start >= SAMPLE_USEC:
		var sorted := _deltas.duplicate()
		sorted.sort()
		var total := 0.0
		for d in _deltas:
			total += d
		var n := float(_deltas.size())
		print("PROBE %s frame avg %.2f ms p95 %.2f max %.2f | render cpu %.2f gpu %.2f | process %.2f ms | fps %.0f | vram %.1f MB | tex %.1f MB" % [
			_scene_path.get_file(), total / n, sorted[int(n * 0.95)], sorted[-1], _cpu / n, _gpu / n, _proc / n, 1000.0 * n / total,
			Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0,
			Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0])
		if not ResourceLoader.exists("res://scripts/ui/kit/city_bake_cache.gd"):
			quit()
			return false
		var cache: GDScript = load("res://scripts/ui/kit/city_bake_cache.gd")
		print("PROBE bakes %d, cache %d entries, %.1f MB" % [cache.bakes_done, cache._entries.size(), cache.memory_bytes() / 1048576.0])
		for a in OS.get_cmdline_user_args():
			if a.begins_with("--probe-dump="):
				var idx := 0
				for k in cache._entries:
					var e: Dictionary = cache._entries[k]
					print("PROBE entry %d region %s scale %s failed %s" % [idx, e.get("region"), e.get("scale"), e.has("failed")])
					if e.has("texture"):
						(e["texture"] as Texture2D).get_image().save_png("%s/bake_%d.png" % [a.trim_prefix("--probe-dump="), idx])
					idx += 1
		quit()
	return false


func _cls(n: Node) -> String:
	var s: Script = n.get_script()
	return String(s.get_global_name()) if s != null else ""
