extends Node
## Parity fixes TITLE-01 / TITLE-01b / LOOT-04: the blurred-city backdrops, windowed
## (run_windowed.py only). One launch walks the states: the title at 1280x720 (text 1.0 / 1.6 /
## 2.0 at city quality tier 2, tier 1, tier 0 = the 2D fallback, reduce effects = the still
## frame, `bare` = the backdrop alone for grading), the netrun's loot, event and Mainframe
## pages, then the perf probes (1920x1080, v-sync off as city_lab: tier 2 and tier 1, the whole
## frame and the backdrop city's own GPU time). --raw also prints a colour-space probe (the frame vs the
## city viewport's image). Prints TITLECAP lines; with --out writes a PNG
## per shot.
##   res://tools/city/title_backdrop_capture.tscn -- --out=<abs dir> [--states=a,b] [--perf=<s>]
## Its own settings and save files (the player's are untouched).

const TITLE := preload("res://scenes/menu/title_scene.tscn")
const NETRUN := preload("res://scenes/netrun_map/netrun_scene.tscn")
const HQ := preload("res://scenes/hq/hq_scene.tscn")
## Real time the HQ's 2D city bake gets before its picture (ms).
const HQ_BAKE_MS := 5000
const SLOT := "gut_title_backdrop_capture"
## name -> [window size, text scale, city quality, reduce effects, kind]
## kind: "title", "bare" (the title's backdrop alone), "loot", "event", "shop", "perf" (title),
## "perf_loot".
const STATES: Dictionary = {
	"t2_text10": [Vector2i(1280, 720), 1.0, 2, false, "title"],
	"t2_bare": [Vector2i(1280, 720), 1.0, 2, false, "bare"],
	"t2_text16": [Vector2i(1280, 720), 1.6, 2, false, "title"],
	"t2_text20": [Vector2i(1280, 720), 2.0, 2, false, "title"],
	"t1_text10": [Vector2i(1280, 720), 1.0, 1, false, "title"],
	"t0_text10": [Vector2i(1280, 720), 1.0, 0, false, "title"],
	"t2_reduced": [Vector2i(1280, 720), 1.0, 2, true, "title"],
	"loot_t2": [Vector2i(1280, 720), 1.0, 2, false, "loot"],
	"loot_t0": [Vector2i(1280, 720), 1.0, 0, false, "loot"],
	"event_t2": [Vector2i(1280, 720), 1.0, 2, false, "event"],
	"event_t0": [Vector2i(1280, 720), 1.0, 0, false, "event"],
	"shop_t2": [Vector2i(1280, 720), 1.0, 2, false, "shop"],
	"hq_t2": [Vector2i(1280, 720), 1.0, 2, false, "hq"],
	"perf_1080_t2": [Vector2i(1920, 1080), 1.0, 2, false, "perf"],
	"perf_1080_t1": [Vector2i(1920, 1080), 1.0, 1, false, "perf"],
	"perf_loot_1080_t2": [Vector2i(1920, 1080), 1.0, 2, false, "perf_loot"],
}
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 90
const PERF_SECONDS_DEFAULT := 4.0

## A motion strip's frame step (ms; round 33's gif: 80 ms a frame).
const STRIP_STEP_MS := 80

var _out := ""
var _perf_s := PERF_SECONDS_DEFAULT
## Frames per shot (--strip=N: a motion strip) and the raw city without the tilt-shift (--raw).
var _strip := 1
var _raw := false


func _ready() -> void:
	var names: Array = STATES.keys()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--states="):
			names.assign(a.trim_prefix("--states=").split(",", false))
		elif a.begins_with("--perf="):
			_perf_s = float(a.trim_prefix("--perf="))
		elif a.begins_with("--strip="):
			_strip = int(a.trim_prefix("--strip="))
		elif a == "--raw":
			_raw = true
	if _out != "":
		DirAccess.make_dir_recursive_absolute(_out)
	Settings.path = "user://title_backdrop_capture_settings.json"
	SaveService.save_dir = "user://saves/title_backdrop_capture"
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	for n: String in names:
		await _state(n, STATES[n])
	RunManager.delete_save()
	get_tree().quit(0)


func _state(n: String, s: Array) -> void:
	DisplayServer.window_set_size(s[0])
	Settings.set_text_scale(float(s[1]))
	Settings.set_city_quality(int(s[2]))
	Settings.set_reduce_effects(bool(s[3]))
	await get_tree().process_frame
	var kind: String = s[4]
	var root: Node
	var blurred: BlurredCityBackdrop = null
	if kind in ["title", "bare", "perf"]:
		var title: Control = TITLE.instantiate()
		get_tree().root.add_child(title)
		root = title
		blurred = (title.get("background") as CyberdeckBackground).blurred
		if kind == "bare":
			for k in ["margin", "ticker", "subtitle_strip"]:
				(title.get(k) as CanvasItem).visible = false
	elif kind == "hq":
		# The HQ page (its own backdrop, whatever main draws there today), its 2D city's bake
		# given HQ_BAKE_MS to land.
		RunManager.reset()
		var hq: Node = HQ.instantiate()
		get_tree().root.add_child(hq)
		root = hq
		await get_tree().process_frame
		await get_tree().process_frame
		hq.new_campaign(7)
		var until := Time.get_ticks_msec() + HQ_BAKE_MS
		while Time.get_ticks_msec() < until:
			await get_tree().process_frame
	else:
		RunManager.reset()
		RunManager.new_campaign(7)
		var net: Node = NETRUN.instantiate()
		get_tree().root.add_child(net)
		root = net
		await get_tree().process_frame
		await get_tree().process_frame
		net.start_run(1)
		match kind:
			"loot", "perf_loot":
				DemoSetup.offer_loot(RunManager.netrun, ["twist", "jam", "cache"])
			"event":
				DemoSetup.open_event(RunManager.netrun, &"ev_leash_on_the_floor")
			"shop":
				DemoSetup.open_shop(RunManager.netrun)
		net._show_current()
		blurred = (net.get("background") as WireframeBackground).blurred
	var waited := 0
	while blurred != null and blurred.visible and not blurred.city_in() and waited < MODEL_WAIT_FRAMES:
		await get_tree().process_frame
		waited += 1
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	if blurred != null:
		blurred.complete_motion()
	PageTransition.settle(root)
	Dialogue.finish_typing()
	Typing.finish_all(get_tree())
	for i in 4:
		await get_tree().process_frame
	print("TITLECAP state=%s blurred=%s city_in=%s corp=%s waited=%d" % [n, blurred != null and blurred.visible,
		blurred.city_in() if blurred != null else false, blurred.corp if blurred != null else &"", waited])
	if _raw and blurred != null:
		(blurred.get_node("TiltShift") as CanvasItem).visible = false
		await get_tree().process_frame
		await get_tree().process_frame
		# Colour-space probe: the window's frame against the city viewport's own image (both
		# the whole view; a decode mismatch shows as a ratio far from 1 in the mid-tones).
		if blurred.city != null:
			var shown := get_viewport().get_texture().get_image()
			var own := blurred.city.get_texture().get_image()
			own.resize(shown.get_width(), shown.get_height())
			print("TITLECAP probe state=%s frame_mean=%s viewport_mean=%s" % [n, _mean(shown), _mean(own)])
	if kind.begins_with("perf"):
		await _probe(n, blurred)
	elif _out != "":
		# A motion strip: `_strip` frames `STRIP_STEP_MS` apart (real time), else one still.
		for k in maxi(_strip, 1):
			if k > 0:
				var until := Time.get_ticks_msec() + STRIP_STEP_MS
				while Time.get_ticks_msec() < until:
					await get_tree().process_frame
			var img := get_viewport().get_texture().get_image()
			var path := "%s/%s%s.png" % [_out, n, "" if _strip <= 1 else "_f%02d" % k]
			img.save_png(path)
			print("TITLECAP shot %s %dx%d" % [path, img.get_width(), img.get_height()])
	root.queue_free()
	await get_tree().process_frame
	await get_tree().process_frame


## Mean RGB of `img` over a sparse grid (the colour-space probe).
static func _mean(img: Image) -> Vector3:
	var acc := Vector3.ZERO
	var k := 0
	for y in range(0, img.get_height(), 8):
		for x in range(0, img.get_width(), 8):
			var c := img.get_pixel(x, y)
			acc += Vector3(c.r, c.g, c.b)
			k += 1
	return acc / maxf(float(k), 1.0)


func _probe(n: String, blurred: BlurredCityBackdrop) -> void:
	var rid := get_viewport().get_viewport_rid()
	var vrid := blurred.city.get_viewport_rid() if blurred != null and blurred.city != null else RID()
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
