extends Control
## NA-25b lab (windowed only, through tools/run_windowed.py): the whole dive from a live HQ click, on the real scenes and the real
## Fx (nothing stepped): the HQ's JACK IN sticker, the CRT terminal, the night-sky switch, the street dive, REVEAL ... CHOOSE, then
## the run ends on an end-of-run page and BACK TO HQ plays the jack-out: the dive backwards over the end page, the night-sky switch,
## the CRT coming back on over the HQ.
## User args:
##   --mode=perf|shots   perf: frame times only (no readbacks); shots: PNG key frames plus the night-sky flicker check
##   --seed=<n>          campaign seed (default 1)
##   --shots=<dir>       output folder (shots mode)
##   --size=WxH          window size (default 1920x1080 for perf, 1280x720 for shots)
## Prints NA25E lines: frame time p50 / p95 / p99 / max for each stretch, the flicker check, the dark-frame count.

const LUMA_MIN := 0.02
const NIGHT_TOL := 0.03
const SETTLE_FRAMES := 90
const WAIT_FRAMES := 1800
## Cover times (s into the street timeline) of the dive, REVEAL (mid-dissolve of layer 1 and the end) key frames.
const FWD_SHOTS := {"dive_1.50": 1.5, "reveal_mid": 3.70, "reveal_end": 6.60}
## Cover times (s into the reverse run) of the jack-out frames over the end page.
const REV_SHOTS := {"rev_zoom": 0.5, "rev_reveal": 4.0, "rev_dive": 8.44}

var _args: Dictionary = {}
var _mode := "perf"
var _phase := "boot"
var _frames := 0
var _hq: Control = null
var _scene: Control = null
var _shots := ""
var _all: Array[float] = []
var _dive: Array[float] = []
var _launch_to_dive: Array[float] = []
var _shot_done: Dictionary = {}
var _dark := 0
var _night_frames := 0
var _night_off_then_on := 0
var _night_seen := false
var _night_ended := false
var _night_bad := 0
var _hq_out_seen: Dictionary = {}
var _end_wait := 0
var _hq_seq := 0
var _prev_night := false


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	_mode = String(_args.get("mode", "perf"))
	var wh := String(_args.get("size", "1920x1080" if _mode == "perf" else "1280x720")).split("x")
	DisplayServer.window_set_size(Vector2i(int(wh[0]), int(wh[1])))
	get_window().size = Vector2i(int(wh[0]), int(wh[1]))
	_shots = String(_args.get("shots", "user://na25e"))
	DirAccess.make_dir_recursive_absolute(_shots)
	AudioDirector.muted = true
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(), true)
	RunManager.save_slot = "lab_na25e2e"
	RunManager.delete_save()
	RunManager.new_campaign(int(_args.get("seed", "1")))
	# This lab must outlive the scene switches: it moves to the root.
	_adopt.call_deferred()


func _adopt() -> void:
	var root := get_tree().root
	get_parent().remove_child(self)
	root.add_child(self)
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(), true)
	_hq = load(RunManager.HQ_SCENE).instantiate()
	root.add_child(_hq)
	get_tree().current_scene = _hq
	_phase = "settle"


func _process(delta: float) -> void:
	match _phase:
		"settle":
			_frames += 1
			if _frames > SETTLE_FRAMES and _hq.selected_site != &"":
				_click()
		"jack":
			_track_jack(delta)
		"choose":
			_frames += 1
			if _frames > 30:
				_end_run_and_leave()
		"out":
			_track_out(delta)


func _click() -> void:
	var btn := _hq._panel.find_child("Launch", true, false) as VerbSticker
	if btn == null:
		print("NA25E FAIL no JACK IN sticker on the HQ")
		get_tree().quit(1)
		return
	print("NA25E click: HQ is up, Site %s" % _hq.selected_site)
	_frames = 0
	btn.pressed.emit()
	_phase = "jack"


func _scene_now() -> Node:
	return get_tree().current_scene


func _luma_ok(img: Image) -> bool:
	var small := img.duplicate() as Image
	small.resize(64, 36, Image.INTERPOLATE_BILINEAR)
	var best := 0.0
	for y in small.get_height():
		for x in small.get_width():
			var c := small.get_pixel(x, y)
			best = maxf(best, 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b)
	return best > LUMA_MIN


## The five sample points (corners and centre) of a night-sky frame, as the largest distance from NIGHT_SKY.
func _night_distance(img: Image) -> float:
	var w := img.get_width()
	var h := img.get_height()
	var worst := 0.0
	for p: Vector2i in [Vector2i(4, 4), Vector2i(w - 5, 4), Vector2i(4, h - 5), Vector2i(w - 5, h - 5), Vector2i(w / 2, h / 2)]:
		var c := img.get_pixelv(p)
		worst = maxf(worst, maxf(absf(c.r - Palette.NIGHT_SKY.r), maxf(absf(c.g - Palette.NIGHT_SKY.g), absf(c.b - Palette.NIGHT_SKY.b))))
	return worst


func _track_jack(delta: float) -> void:
	_frames += 1
	if _frames > WAIT_FRAMES:
		print("NA25E FAIL the dive never reached CHOOSE")
		get_tree().quit(1)
		return
	_all.append(delta)
	var sc := _scene_now()
	var night: bool = Fx.jack_link != null and Fx.jack_link.visible and Fx.jack_link.night
	if night:
		_night_seen = true
		_night_frames += 1
		if _night_ended:
			_night_off_then_on += 1
	elif _night_seen:
		_night_ended = true
	var cover: EntryCover = sc.get("entry_cover") if sc != null and sc.has_method("play_entry") else null
	var sv: Variant = sc.get("street_view") if sc != null and sc.has_method("play_entry") else null
	if sv != null and is_instance_valid(sv) and sv.rig != null:
		RenderingServer.viewport_set_measure_render_time(sv.rig.view.get_viewport_rid(), true)
	var in_dive := false
	if cover != null and is_instance_valid(cover) and cover.playing:
		_scene = sc
		var e := cover.elapsed()
		if e <= 3.0:
			in_dive = true
			_dive.append(delta)
			if delta > 0.034:
				var rv: Variant = sc.get("street_view")
				var city_rid := RID()
				if rv != null and is_instance_valid(rv) and rv.rig != null:
					city_rid = rv.rig.view.get_viewport_rid()
				print("NA25E hitch pending chunks %d prepared %s" % [rv.rig.view._pending.size() if rv != null and is_instance_valid(rv) else -1, str(rv.rig.is_prepared()) if rv != null and is_instance_valid(rv) else "?"])
				print("NA25E hitch %.1f ms at cover %.2f s (frame %d): process %.1f ms, draw calls %d, primitives %d, root cpu %.1f gpu %.1f ms, city cpu %.1f gpu %.1f ms" % [
						delta * 1000.0, e, _frames, Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0,
						int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)), int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
						RenderingServer.viewport_get_measured_render_time_cpu(get_viewport().get_viewport_rid()),
						RenderingServer.viewport_get_measured_render_time_gpu(get_viewport().get_viewport_rid()),
						RenderingServer.viewport_get_measured_render_time_cpu(city_rid) if city_rid.is_valid() else -1.0,
						RenderingServer.viewport_get_measured_render_time_gpu(city_rid) if city_rid.is_valid() else -1.0])
		if _mode == "shots":
			_shoot_fwd(e)
	if _mode == "shots" and _frames > 1:
		var img := get_viewport().get_texture().get_image()
		if not _luma_ok(img):
			_dark += 1
			print("NA25E dark frame %d (night=%s)" % [_frames, str(night)])
		# The image read now is the frame the previous process step drew: pair it with that step's night flag.
		if _prev_night and _night_distance(img) > NIGHT_TOL:
			_night_bad += 1
			print("NA25E night frame %d off colour by %.3f" % [_frames, _night_distance(img)])
	_prev_night = night
	if in_dive and _launch_to_dive.is_empty():
		_launch_to_dive.append(float(_frames))
	if _scene != null and (cover == null or not is_instance_valid(cover)) and sc == _scene and not Fx.transitioning():
		print("NA25E the entry ended after %d frames" % _frames)
		_frames = 0
		_phase = "choose"


func _shoot_fwd(e: float) -> void:
	for tag: String in FWD_SHOTS:
		if not _shot_done.has(tag) and e >= float(FWD_SHOTS[tag]):
			_shot_done[tag] = true
			get_viewport().get_texture().get_image().save_png("%s/%s.png" % [_shots, tag])


func _end_run_and_leave() -> void:
	_report_stats("jack-in", _all)
	_report_stats("dive (first 3.0 s of the cover)", _dive)
	print("NA25E night sky: %d frames, %d lifted-then-back (flicker), %d off-colour, %d dark frames" % [_night_frames, _night_off_then_on, _night_bad, _dark])
	if _mode == "shots":
		get_viewport().get_texture().get_image().save_png("%s/choose.png" % _shots)
	var s := RunManager.netrun
	DemoSetup.end_run(s, "completed")
	_scene._report(s.last_events)
	_scene._show_current()
	_all.clear()
	_shot_done.clear()
	_frames = 0
	_end_wait = 0
	_phase = "out_wait"
	set_process(false)
	await get_tree().create_timer(1.0).timeout
	set_process(true)
	if _mode == "shots":
		get_viewport().get_texture().get_image().save_png("%s/end_page.png" % _shots)
	_phase = "out"
	_scene.finish_run()


func _track_out(delta: float) -> void:
	_frames += 1
	if _frames > WAIT_FRAMES:
		print("NA25E FAIL the jack-out never ended")
		get_tree().quit(1)
		return
	_all.append(delta)
	var sc := _scene_now()
	var cover: EntryCover = null
	if sc != null and is_instance_valid(sc) and sc.has_method("play_entry"):
		cover = sc.get("entry_cover")
	if cover != null and is_instance_valid(cover) and cover.playing and _mode == "shots":
		var e := cover.elapsed()
		for tag: String in REV_SHOTS:
			if not _shot_done.has(tag) and e >= float(REV_SHOTS[tag]):
				_shot_done[tag] = true
				get_viewport().get_texture().get_image().save_png("%s/%s.png" % [_shots, tag])
	var j: JackSequence = Fx.jack_link
	if j != null and j.visible and j.street and j.terminal != null and is_instance_valid(j.terminal) and _mode == "shots":
		if j.night and not _hq_out_seen.has("night"):
			_hq_out_seen["night"] = true
			get_viewport().get_texture().get_image().save_png("%s/hq_out_night.png" % _shots)
		elif not j.night and j.terminal.visible:
			if j.terminal.scale.x < 0.9 and j.terminal.scale.y < 0.3 and not _hq_out_seen.has("line"):
				_hq_out_seen["line"] = true
				get_viewport().get_texture().get_image().save_png("%s/hq_out_crt_on.png" % _shots)
			elif j.rain_t >= 0.4 and not _hq_out_seen.has("rain"):
				_hq_out_seen["rain"] = true
				get_viewport().get_texture().get_image().save_png("%s/hq_out_rain.png" % _shots)
	if _mode == "shots" and j != null and j.visible and j.street and _hq_seq < 60:
		_hq_seq += 1
		if _hq_seq % 4 == 0:
			get_viewport().get_texture().get_image().save_png("%s/hqseq_%02d.png" % [_shots, _hq_seq])
	var at_hq := sc != null and is_instance_valid(sc) and sc.scene_file_path == RunManager.HQ_SCENE
	if at_hq and not Fx.transitioning() and (j == null or not j.visible):
		_report_stats("jack-out", _all)
		print("NA25E done")
		get_tree().quit()


func _report_stats(label: String, times: Array[float]) -> void:
	if times.is_empty():
		print("NA25E %s: no frames" % label)
		return
	var sorted := times.duplicate()
	sorted.sort()
	var n := sorted.size()
	print("NA25E frame time %s: n=%d p50=%.2f ms p95=%.2f ms p99=%.2f ms max=%.2f ms" % [label, n,
			float(sorted[n / 2]) * 1000.0, float(sorted[mini(n - 1, int(float(n) * 0.95))]) * 1000.0,
			float(sorted[mini(n - 1, int(float(n) * 0.99))]) * 1000.0, float(sorted[n - 1]) * 1000.0])
