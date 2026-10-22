extends Control
## LOOK-TOOLBOX module 3: the look lab. Loads one module's stage on a neutral set and captures it at day / night,
## at each quality tier and under each accessibility flag, with the GPU time per capture. Windowed only, through
## tools/run_windowed.py:
##   python tools/run_windowed.py --log <f> -- --resolution 1920x1080 res://addons/rc_look/lab/look_lab.tscn --
##       --module=<id> --shots=<dir> [--times=day,night] [--tiers=0,2] [--flags=none,re,rm,hc] [--settle=<frames>]
##       [--window=1920x1080]
## Writes <dir>/<module>_<time>_<state label>.png and <dir>/<module>_perf.json ({file: gpu ms}). Without --shots it
## shows the first combination and stays open. View only.

## Module id -> stage script. A module adds its stage here when it lands.
const STAGES := {
	"tokens": "res://addons/rc_look/lab/stages/tokens_stage.gd",
	"grade": "res://addons/rc_look/lab/stages/grade_stage.gd",
	"light": "res://addons/rc_look/lab/stages/light_stage.gd",
	"air": "res://addons/rc_look/lab/stages/air_stage.gd",
	"pencil": "res://addons/rc_look/lab/stages/pencil_stage.gd",
	"holo": "res://addons/rc_look/lab/stages/holo_stage.gd",
	"toon": "res://addons/rc_look/lab/stages/toon_stage.gd",
	"wet": "res://addons/rc_look/lab/stages/wet_stage.gd",
	"sign": "res://addons/rc_look/lab/stages/sign_stage.gd",
	"vinyl": "res://addons/rc_look/lab/stages/vinyl_stage.gd",
	"crt": "res://addons/rc_look/lab/stages/crt_stage.gd",
	"crt_reduce": "res://addons/rc_look/lab/stages/crt_reduce_stage.gd",
	"bits": "res://addons/rc_look/lab/stages/bits_stage.gd",
	"bits_rulings": "res://addons/rc_look/lab/stages/bits_rulings_stage.gd",
}
## The neutral set: a mid-grey ramp, darker at night (sRGB).
const SET_DAY := [Color(0.42, 0.43, 0.46), Color(0.62, 0.63, 0.66)]
const SET_NIGHT := [Color(0.035, 0.04, 0.06), Color(0.11, 0.12, 0.16)]
## Frames averaged for the GPU time readout.
const PERF_FRAMES := 30

var _args: Dictionary = {}
var _stage: RcLookLabStage
var _set: ColorRect
var _queue: Array[Dictionary] = []
var _perf: Dictionary = {}


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_args[kv[0]] = kv[1] if kv.size() > 1 else "1"
	var module := String(_args.get("module", "tokens"))
	if not STAGES.has(module):
		printerr("look_lab: unknown module ", module, "; known: ", STAGES.keys())
		get_tree().quit(2)
		return
	# --window=WxH: shots at that size (the canvas stays 1280 x 720 and scales, so vectors render sharp)
	if _args.has("window"):
		var wh := String(_args["window"]).split("x")
		get_window().size = Vector2i(int(wh[0]), int(wh[1]))
		get_window().content_scale_size = Vector2i(1280, 720)
		get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	_set = ColorRect.new()
	_set.set_anchors_preset(Control.PRESET_FULL_RECT)
	var g := ShaderMaterial.new()
	g.shader = Shader.new()
	g.shader.code = "shader_type canvas_item;\nuniform vec4 a : source_color;\nuniform vec4 b : source_color;\nvoid fragment() { COLOR = mix(a, b, UV.y); }"
	_set.material = g
	add_child(_set)
	_stage = (load(STAGES[module]) as GDScript).new()
	_stage.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_stage)
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(), true)
	for t: String in String(_args.get("times", "night,day")).split(","):
		for tier: String in String(_args.get("tiers", "2")).split(","):
			for f: String in String(_args.get("flags", "none")).split(","):
				var q := RcLookQualityState.make(int(tier), f.contains("re"), f.contains("rm"), f.contains("hc"))
				_queue.append({"module": module, "time": StringName(t), "q": q})
	_run()


func _run() -> void:
	var shots := String(_args.get("shots", ""))
	if shots != "":
		DirAccess.make_dir_recursive_absolute(shots)
	for job: Dictionary in _queue:
		_apply(job)
		var n := int(_args.get("settle", str(_stage.settle_frames())))
		for k in n:
			await get_tree().process_frame
		var ms := 0.0
		for k in PERF_FRAMES:
			await get_tree().process_frame
			ms += RenderingServer.viewport_get_measured_render_time_gpu(get_viewport().get_viewport_rid())
		var name := "%s_%s_%s" % [job["module"], job["time"], (job["q"] as RcLookQualityState).label()]
		_perf[name + ".png"] = snappedf(ms / PERF_FRAMES, 0.001)
		if shots == "":
			return
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(shots.path_join(name + ".png"))
		print("look_lab: ", name, " gpu ", _perf[name + ".png"], " ms")
	var f := FileAccess.open(shots.path_join("%s_perf.json" % _queue[0]["module"]), FileAccess.WRITE)
	f.store_string(JSON.stringify(_perf, "\t", true))
	f.close()
	get_tree().quit(0)


func _apply(job: Dictionary) -> void:
	var c: Array = SET_NIGHT if job["time"] == &"night" else SET_DAY
	(_set.material as ShaderMaterial).set_shader_parameter(&"a", c[0])
	(_set.material as ShaderMaterial).set_shader_parameter(&"b", c[1])
	_stage.apply(job["time"], job["q"])
