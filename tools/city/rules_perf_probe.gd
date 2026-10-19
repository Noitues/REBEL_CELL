extends Control
## NA-11b: the layout rules' main-thread cost (windowed, through tools/run_windowed.py). Builds the full city on a real
## CityView3D and prints RULESPERF lines: total time to model_ready, the longest frame, frames over 50 ms.
## User args: --norules=1 (rules off: the baseline of everything else), --sync=1 builds the shared model on the main thread first (the old behaviour: rules inside finish()).
## Also times the three rule stages on this thread (make_job / run_job / land_job).

const CONFIG := preload("res://content/config/city_config.tres")
const HITCH_MS := 50.0

var _view: CityView3D
var _t0: int = 0
var _last: int = 0
var _worst: float = 0.0
var _over: Array[float] = []
var _frames: int = 0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if args.has("--stages=1"):
		_stages()
		get_tree().quit()
		return
	if args.has("--sync=1"):
		var t := Time.get_ticks_msec()
		CityModel.keep_shared(CityModel.build(CONFIG, CONFIG.city_seed))
		print("RULESPERF sync build ms=%d (one main-thread block)" % (Time.get_ticks_msec() - t))
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_view = CityView3D.new()
	if args.has("--norules=1"):
		var plain := CONFIG.duplicate() as CityConfig
		plain.layout_rules_on = false
		_view.cfg = plain
	_view.size = Vector2(1920, 1080)
	add_child(_view)
	_t0 = Time.get_ticks_msec()
	_last = _t0
	_view.model_ready.connect(_on_ready, CONNECT_ONE_SHOT)


func _process(_d: float) -> void:
	var now := Time.get_ticks_msec()
	var dt := float(now - _last)
	_last = now
	_frames += 1
	_worst = maxf(_worst, dt)
	if dt > HITCH_MS:
		_over.append(dt)


func _on_ready() -> void:
	print("RULESPERF ready ms=%d frames=%d worst_frame_ms=%.0f frames_over_%d=%s" % [Time.get_ticks_msec() - _t0, _frames,
		_worst, int(HITCH_MS), str(_over)])
	get_tree().quit()


func _stages() -> void:
	var m := CityModel.new()
	m.cfg = CONFIG
	m.city_seed = CONFIG.city_seed
	for key in CityModel.chunk_keys(CONFIG, CONFIG.city_rect):
		var r := CityModel.chunk_rect(CONFIG, key)
		var rec := CityModel.recorder(m.city_seed)
		rec.record(r)
		m.add_recording(key, r, rec)
		rec.free()
	var t := Time.get_ticks_msec()
	m.finish(true)
	print("RULESPERF finish(defer) ms=%d" % (Time.get_ticks_msec() - t))
	t = Time.get_ticks_msec()
	var job := m.layout_rules_job()
	print("RULESPERF make_job (main) ms=%d" % (Time.get_ticks_msec() - t))
	t = Time.get_ticks_msec()
	CityLayoutRuler.run_job(job)
	print("RULESPERF run_job (worker) ms=%d" % (Time.get_ticks_msec() - t))
	t = Time.get_ticks_msec()
	var n := CityLayoutRuler.land_job(m, job)
	print("RULESPERF land_job (main) ms=%d changed=%d" % [Time.get_ticks_msec() - t, n])
