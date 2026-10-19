extends Control
## NA-25 lab (windowed only, through tools/run_windowed.py): the street entry sequence on the game's city for a started run.
## It steps the EntryCover at a fixed 1/60 s per rendered frame, so the shots are deterministic, and writes key frames.
## User args:
##   --seed=<n>       campaign seed (default 1)
##   --shots=<dir>    output folder (one PNG per key frame: fwd_<t>.png, rev_<t>.png, skip_*.png)
##   --size=WxH       window size (default 1920x1080)
##   --times=a,b,c    forward key frames, seconds into the street timeline (default a spread over every beat)
## Prints NA25 lines: the beat times, the dark-frame check (max luma of every frame), the skip end-state check.

const STEP := 1.0 / 60.0
const DEFAULT_TIMES := "0,1.5,3.0,4.5,6.0,7.0,7.8,9.0,10.0,11.5,12.5,13.0"
const SKIP_AT := 4.0
const LUMA_MIN := 0.02
## NA-25b blotch metric: a pixel is "flat near-white" when its darkest channel is above WHITE_MIN (192 x 108 reduction); only the
## interior of a region counts (a pixel whose 3 x 3 neighbourhood is all near-white), so a lit sign, a window or a beam does not. A frame
## fails when that share of it is above FLAT_WHITE_MAX (the mid-dive cloud patches were 3 to 5 % of the frame, flat and wide).
const WHITE_MIN := 0.62
const FLAT_WHITE_MAX := 0.005

var view: StreetRouteView
var cover: EntryCover
var _args: Dictionary = {}
var _data: StreetRouteData
var _phase := "boot"
var _times: Array[float] = []
var _next_i := 0
var _t := 0.0
var _dark_frames := 0
var _frames := 0
var _end_pose: Array = []
var _shots := ""
var _white_max := 0.0


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	var wh := String(_args.get("size", "1920x1080")).split("x")
	DisplayServer.window_set_size(Vector2i(int(wh[0]), int(wh[1])))
	get_window().size = Vector2i(int(wh[0]), int(wh[1]))
	_shots = String(_args.get("shots", "user://na25"))
	DirAccess.make_dir_recursive_absolute(_shots)
	for tok in String(_args.get("times", DEFAULT_TIMES)).split(","):
		_times.append(float(tok))
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.save_slot = "lab_na25"
	RunManager.new_campaign(int(_args.get("seed", "1")))
	var s := RunManager.start_run()
	if s == null:
		print("NA25 FAIL no run")
		get_tree().quit(1)
		return
	_data = StreetRouteView.build_data(s, RunManager.corporation)
	if _data.error != "":
		print("NA25 FAIL data %s" % _data.error)
		get_tree().quit(1)
		return
	var cfg := CityView3D.CONFIG
	view = StreetRouteView.new()
	view.size = Vector2(int(wh[0]), int(wh[1]))
	add_child(view)
	var opts := NetrunPoseBuilder.successors(_data.run_graph, "")
	view.setup(_data, CityModel.shared(cfg, CityPlan.current_seed()), "", [], opts)
	view.ready_to_show.connect(func() -> void: _phase = "settle", CONNECT_ONE_SHOT)
	for row in EntryBeats.table(EntryBeats.HQ_BEATS + EntryBeats.STREET_BEATS, false, false):
		print("NA25 beat %s %.3f-%.3f" % [row["beat"], row["start"], row["end"]])


func _process(_delta: float) -> void:
	match _phase:
		"settle":
			_frames += 1
			if _frames > 90:
				_start_forward()
		"fwd":
			_step(false)
		"rev":
			_step(true)
		"skip":
			_step_skip()
		"lb":
			_step_lb()
		"hq":
			_step_hq()


func _start_cover(reverse: bool) -> void:
	if cover != null and is_instance_valid(cover):
		cover.queue_free()
	cover = EntryCover.new()
	view.add_child(cover)
	cover.set_process(false)  # stepped here at a fixed 1/60 s (the node enables its own process when it enters the tree)
	cover.start(view, reverse)
	_t = 0.0
	_next_i = 0


func _start_forward() -> void:
	_start_cover(false)
	if not cover.playing:
		print("NA25 FAIL the entry does not animate (reduce effects or an entry switched off)")
		get_tree().quit(1)
		return
	print("NA25 street timeline %.3f s; live: %s" % [cover.total_seconds(), str(EntryBeats.table(EntryBeats.STREET_BEATS))])
	_phase = "fwd"


func _luma_ok(img: Image) -> bool:
	var small := img.duplicate() as Image
	small.resize(64, 36, Image.INTERPOLATE_BILINEAR)
	var best := 0.0
	for y in small.get_height():
		for x in small.get_width():
			var c := small.get_pixel(x, y)
			best = maxf(best, 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b)
	return best > LUMA_MIN


## The share of the frame that is flat near-white (the NA-25b blotch metric).
static func flat_white(img: Image) -> float:
	var small := img.duplicate() as Image
	small.resize(192, 108, Image.INTERPOLATE_TRILINEAR)
	var w := small.get_width()
	var h := small.get_height()
	var white := PackedByteArray()
	white.resize(w * h)
	for y in h:
		for x in w:
			var c := small.get_pixel(x, y)
			white[y * w + x] = 1 if minf(c.r, minf(c.g, c.b)) > WHITE_MIN else 0
	var n := 0
	for y in range(1, h - 1):
		for x in range(1, w - 1):
			var all_white := true
			for dy in range(-1, 2):
				for dx in range(-1, 2):
					if white[(y + dy) * w + x + dx] == 0:
						all_white = false
			if all_white:
				n += 1
	return float(n) / float(w * h)


func _grab(tag: String) -> void:
	var img := get_viewport().get_texture().get_image()
	var wf := flat_white(img)
	if not tag.begins_with("hq_"):
		_white_max = maxf(_white_max, wf)
	print("NA25 flat white %s %.4f" % [tag, wf])
	if not _luma_ok(img):
		_dark_frames += 1
	img.save_png("%s/%s.png" % [_shots, tag])


func _step(reverse: bool) -> void:
	# The frame rendered since the last step shows time _t.
	if _frames > 0 and _next_i < _times.size() and _t >= _times[_next_i] - STEP * 0.5:
		_grab("%s_%05.2f" % ["rev" if reverse else "fwd", _t])
		_next_i += 1
	_frames += 1
	if not cover.playing:
		_grab("%s_end" % ["rev" if reverse else "fwd"])
		if not reverse:
			_end_pose = view.rig.pose.to_json().values()
			print("NA25 forward done at %.3f s; end view=%d dark_frames=%d" % [_t, view.current_view(), _dark_frames])
			_start_cover(true)
			_phase = "rev"
		else:
			print("NA25 reverse done at %.3f s (timeline %.3f + hold)" % [_t, cover.total_seconds()])
			_start_skip()
		return
	_t += STEP
	cover._process(STEP)
	if _frames > 1 and not _luma_ok(get_viewport().get_texture().get_image()):
		_dark_frames += 1
		print("NA25 dark frame at t=%.3f" % _t)


func _start_skip() -> void:
	view.entry_end()
	_start_cover(false)
	_phase = "skip"


func _step_skip() -> void:
	if _t < SKIP_AT:
		_t += STEP
		cover._process(STEP)
		return
	_grab("skip_before")
	cover.skip()
	_phase = "skip_done"
	await get_tree().process_frame
	await get_tree().process_frame
	_grab("skip_after")
	var got: Array = view.rig.pose.to_json().values()
	print("NA25 skip at %.1f s: end pose equals the played end pose = %s; view=%d; dark_frames=%d" % [SKIP_AT, str(got == _end_pose), view.current_view(), _dark_frames])
	# NA-25b: the look blend swept 0 .. 1 at a mid-dive pose (the wet ground must not clip to white at any blend).
	view.entry_begin()
	view.entry_dive(LB_SWEEP_U)
	_lb_i = 0
	_lb_f = 0
	_phase = "lb"


const LB_SWEEP := [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]
const LB_SWEEP_U := 0.4
var _lb_i := 0
var _lb_f := 0


func _step_lb() -> void:
	if _lb_i >= LB_SWEEP.size():
		view.rig.view.set_look_blend(1.0)
		_start_hq()
		return
	if _lb_f == 0:
		view.rig.view.set_look_blend(float(LB_SWEEP[_lb_i]))
	_lb_f += 1
	if _lb_f >= 6:
		_grab("lb_%.2f" % float(LB_SWEEP[_lb_i]))
		_lb_i += 1
		_lb_f = 0


## The HQ side (beats 3a-3c): the JackSequence street variant over the dive's first frame, in real time.
func _start_hq() -> void:
	print("NA25 blotch max flat white %.4f (limit %.3f): %s" % [_white_max, FLAT_WHITE_MAX, "ok" if _white_max <= FLAT_WHITE_MAX else "FAIL"])
	view.entry_begin()
	view.entry_dive(0.0)
	_hq_t0 = Time.get_ticks_msec()
	_hq_i = 0
	_phase = "hq"
	var vp := get_viewport_rect().size
	Fx.jack_in_link(func() -> void: pass, {"from": "RELAY_4", "to": "DEPOT_15", "street": true,
			"points": PackedVector2Array([vp * Vector2(0.3, 0.6), vp * Vector2(0.62, 0.35)])})


var _hq_t0 := 0
var _hq_i := 0


## The HQ side's key frames by the sequence's own state (not wall time: a PNG save takes many frames).
func _step_hq() -> void:
	var j := Fx.jack_link
	if j.night and _hq_i < 4:
		_grab("hq_4")
		_hq_i = 4
		return
	if _hq_i >= 4 and not j.visible or float(Time.get_ticks_msec() - _hq_t0) / 1000.0 > 30.0:
		print("NA25 hq side done (%d key frames); dark_frames=%d" % [_hq_i, _dark_frames])
		get_tree().quit()
		return
	if j.terminal == null or not is_instance_valid(j.terminal):
		return
	if _hq_i == 0 and j._text.visible_characters > 24:
		_grab("hq_0")
		_hq_i = 1
	elif _hq_i == 1 and j.rain_t >= 0.5:
		_grab("hq_1")
		_hq_i = 2
	elif _hq_i == 2 and j.terminal.scale.y < 0.3:
		_grab("hq_2")
		_hq_i = 3
