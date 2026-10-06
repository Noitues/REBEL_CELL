extends Node
## Parity fix TITLE-01: the title's backdrop, windowed (run_windowed.py only). One launch walks
## the states: shots of the title at 1280x720 (text 1.0 / 1.6 / 2.0 at city quality tier 2,
## tier 1, tier 0 = the 2D fallback, reduce effects = the still frame), then the perf probes
## (1920x1080, v-sync off as city_lab: tier 2 and tier 1, the whole frame and the backdrop
## city's own GPU time). Prints TITLECAP lines; with --out writes a PNG per shot.
##   res://tools/city/title_backdrop_capture.tscn -- --out=<abs dir> [--states=a,b] [--perf=<s>]
## Its own settings and save files (the player's are untouched).

const TITLE := preload("res://scenes/menu/title_scene.tscn")
## name -> [window size, text scale, city quality, reduce effects, perf]
const STATES: Dictionary = {
	"t2_text10": [Vector2i(1280, 720), 1.0, 2, false, false],
	"t2_text16": [Vector2i(1280, 720), 1.6, 2, false, false],
	"t2_text20": [Vector2i(1280, 720), 2.0, 2, false, false],
	"t1_text10": [Vector2i(1280, 720), 1.0, 1, false, false],
	"t0_text10": [Vector2i(1280, 720), 1.0, 0, false, false],
	"t2_reduced": [Vector2i(1280, 720), 1.0, 2, true, false],
	"perf_1080_t2": [Vector2i(1920, 1080), 1.0, 2, false, true],
	"perf_1080_t1": [Vector2i(1920, 1080), 1.0, 1, false, true],
}
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 90
const PERF_SECONDS_DEFAULT := 4.0

var _out := ""
var _perf_s := PERF_SECONDS_DEFAULT


func _ready() -> void:
	var names: Array = STATES.keys()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--states="):
			names.assign(a.trim_prefix("--states=").split(",", false))
		elif a.begins_with("--perf="):
			_perf_s = float(a.trim_prefix("--perf="))
	if _out != "":
		DirAccess.make_dir_recursive_absolute(_out)
	Settings.path = "user://title_backdrop_capture_settings.json"
	SaveService.save_dir = "user://saves/title_backdrop_capture"
	RunManager.scene_switching_enabled = false
	for n: String in names:
		await _state(n, STATES[n])
	get_tree().quit(0)


func _state(n: String, s: Array) -> void:
	DisplayServer.window_set_size(s[0])
	Settings.set_text_scale(float(s[1]))
	Settings.set_city_quality(int(s[2]))
	Settings.set_reduce_effects(bool(s[3]))
	await get_tree().process_frame
	var title: Control = TITLE.instantiate()
	get_tree().root.add_child(title)
	var bg: CyberdeckBackground = title.get("background")
	var waited := 0
	while bg.on_blurred_city() and not bg.blurred.city_in() and waited < MODEL_WAIT_FRAMES:
		await get_tree().process_frame
		waited += 1
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	print("TITLECAP state=%s blurred=%s city_in=%s corp=%s waited=%d" % [n, bg.on_blurred_city(), bg.blurred.city_in() if bg.blurred != null else false,
		bg.blurred.corp if bg.blurred != null else &"", waited])
	if bool(s[4]):
		await _probe(n, bg)
	elif _out != "":
		var img := get_viewport().get_texture().get_image()
		var path := "%s/%s.png" % [_out, n]
		img.save_png(path)
		print("TITLECAP shot %s %dx%d" % [path, img.get_width(), img.get_height()])
	title.queue_free()
	await get_tree().process_frame


func _probe(n: String, bg: CyberdeckBackground) -> void:
	var rid := get_viewport().get_viewport_rid()
	var vrid := bg.blurred.city.get_viewport_rid() if bg.blurred != null and bg.blurred.city != null else RID()
	RenderingServer.viewport_set_measure_render_time(rid, true)
	if vrid.is_valid():
		RenderingServer.viewport_set_measure_render_time(vrid, true)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	for i in 30:
		await get_tree().process_frame
	var t0 := Time.get_ticks_usec()
	var last := t0
	var frames := 0
	var worst := 0.0
	var gpu_all := 0.0
	var gpu_city := 0.0
	while Time.get_ticks_usec() - t0 < int(_perf_s * 1000000.0):
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		worst = maxf(worst, (now - last) / 1000.0)
		last = now
		frames += 1
		gpu_all += RenderingServer.viewport_get_measured_render_time_gpu(rid)
		if vrid.is_valid():
			gpu_city += RenderingServer.viewport_get_measured_render_time_gpu(vrid)
	var f := float(maxi(frames, 1))
	print("TITLECAP perf state=%s window=%s tier=%d frames=%d frame_avg_ms=%.2f frame_max_ms=%.2f main_gpu_ms=%.2f city_gpu_ms=%.2f budget_ms=%.1f" % [
		n, str(DisplayServer.window_get_size()), CityView3D.CONFIG.tier_for(Settings.city_quality), frames,
		(Time.get_ticks_usec() - t0) / 1000.0 / f, worst, gpu_all / f, gpu_city / f, CityView3D.CONFIG.budget_ms])
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
