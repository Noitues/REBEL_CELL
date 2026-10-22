extends GutTest

## LOOK-TOOLBOX module 16 (fast tier): binary bits. The shipped config validates; the mirror (RcLookBits) equals BitsPath
## for the same seeds (hash, control point, ease, Bezier, flight, phase, spin, plan, arrivals); the config and the
## include's constants equal the live ones in BitsPath, BinaryBits, BitsSeam, combat_fx_layer and binary_bits.gdshader;
## the presets are today's looks; reduce effects gives zero arrivals; the bits files call no global randf / randi.

const BITS_FILES: Array[String] = ["res://addons/rc_look/scripts/rc_look_bits.gd",
	"res://addons/rc_look/scripts/rc_look_bits_config.gd", "res://addons/rc_look/scripts/rc_look_bits_preset.gd",
	"res://addons/rc_look/shaders/rc_bits.gdshaderinc", "res://addons/rc_look/lab/stages/bits_stage.gd",
	"res://addons/rc_look/lab/stages/bits_rulings_stage.gd", "res://addons/rc_look/lab/stages/bits_ruled_stage.gd", "res://addons/rc_look/lab/stages/bits_flash_stage.gd", "res://addons/rc_look/lab/rc_look_bits_view.gd"]
const SEEDS: Array[int] = [0, 1, 7, 1234567, -42, 9007199254740993]
const FX_LAYER := "res://scripts/ui/kit/combat_fx_layer.gd"


func test_shipped_config_validates() -> void:
	assert_eq(RcLookBits.default_config().validate(), PackedStringArray())
	for n in RcLookBits.REQUIRED:
		assert_not_null(RcLookBits.preset(n), "preset %s" % n)


func test_a_bad_config_is_reported() -> void:
	var cfg := RcLookBitsConfig.new()
	cfg.rim_control = 1.0
	cfg.spin_min = 5.0
	cfg.spin_max = 2.0
	cfg.cpu_max = 80
	assert_eq(cfg.validate().size(), 6 + 3, "rim, spin, cpu_max, six missing presets: %s" % str(cfg.validate()))


func test_hash_is_kit_noise() -> void:
	for s in SEEDS:
		for i in 70:
			for c in [0, 31, 32, 33, 34]:
				assert_eq(RcLookBits.h01(s, i, c), KitNoise.h01(s, i, c), "h01(%s, %s, %s)" % [s, i, c])


func test_ease_and_bezier_are_bitspath() -> void:
	for k in 41:
		var t := float(k) / 40.0
		assert_eq(RcLookBits.eased(t), BitsPath.eased(t), "eased %s" % t)
	assert_eq(RcLookBits.eased(-1.0), 0.0)
	assert_eq(RcLookBits.eased(2.0), BitsPath.eased(1.0))
	var a := Vector2(10, 20)
	var c := Vector2(300, -40)
	var b := Vector2(-80, 90)
	for k in 11:
		var t := float(k) / 10.0
		assert_eq(RcLookBits.at(a, c, b, t), BitsPath.at(a, c, b, t), "at %s" % t)


func test_control_point_is_bitspath() -> void:
	var centre := Vector2(100, 100)
	var cases: Array[Array] = [[Vector2(160, 100), Vector2(100, 40)], [Vector2(160, 100), Vector2(40, 100)],
		[Vector2(300, 300), Vector2(100, 100)]]
	for cs in cases:
		assert_eq(RcLookBits.control_point(cs[0], cs[1], centre, 60.0), BitsPath.control_point(cs[0], cs[1], centre, 60.0))
		assert_eq(RcLookBits.control_point(cs[0], cs[1]), BitsPath.control_point(cs[0], cs[1]), "free")


func test_plan_and_arrivals_are_bitspath() -> void:
	var starts := BitsPath.points_in_rect(Rect2(20, 30, 200, 80), 36)
	for s in SEEDS:
		var mine := RcLookBits.plan(starts, Vector2(500, 60), 0.55, 0.12, s, Vector2(400, 200), 90.0)
		var theirs := BitsPath.plan(starts, Vector2(500, 60), 0.55, 0.12, s, Vector2(400, 200), 90.0)
		assert_eq(mine, theirs, "plan for seed %s" % s)
		assert_eq(RcLookBits.arrivals(mine), BitsPath.arrivals(theirs), "arrivals for seed %s" % s)
		assert_eq(RcLookBits.plan(starts, Vector2(500, 60), 0.55, 0.12, s), BitsPath.plan(starts, Vector2(500, 60), 0.55, 0.12, s))
	assert_true(RcLookBits.plan(PackedVector2Array(), Vector2.ZERO, 0.5, 0.1, 0).is_empty())


func test_reduce_effects_gives_zero_arrivals() -> void:
	var starts := BitsPath.points_in_rect(Rect2(0, 0, 100, 100), 20)
	var p := RcLookBits.plan(starts, Vector2(300, 300), 0.55, 0.12, 5)
	var none := RcLookBits.arrivals(p, false)
	assert_eq(none.size(), 20)
	for v in none:
		assert_eq(v, 0.0)
	var live := RcLookBits.arrivals(p, true)
	assert_gt(live[live.size() - 1], 0.0)


func test_flip_spin_and_colour() -> void:
	var cfg := RcLookBits.default_config()
	assert_eq(RcLookBits.flip_frame(0.0, cfg.flip_seconds, 0.0), 0)
	assert_eq(RcLookBits.flip_frame(cfg.flip_seconds * 1.01, cfg.flip_seconds, 0.0), 1)
	assert_eq(RcLookBits.flip_frame(cfg.flip_seconds * 2.01, cfg.flip_seconds, 0.0), 0)
	assert_eq(RcLookBits.flip_frame(-1.0, cfg.flip_seconds, 0.0), 0, "before the spawn it shows frame 0")
	assert_almost_eq(RcLookBits.flip_channel(0.0, cfg.flip_seconds, 0.0, cfg.frames), 0.5 / 4.0, 1e-9)
	assert_almost_eq(RcLookBits.spin_angle(1.0, 5.0, 0.5, 6.28), 5.0 + 3.14, 1e-9)
	assert_almost_eq(RcLookBits.spin_angle(1.0, 5.0, 0.5, 6.28, false), 5.0, 1e-9, "the CPU fallback has no phase offset")
	var hot := Color(1, 1, 1)
	var col := Color(1.0, 0.24, 0.66)
	assert_eq(RcLookBits.bit_color(hot, col, 0.0, 0.08), hot)
	assert_eq(RcLookBits.bit_color(hot, col, 0.08, 0.08), col)
	assert_eq(RcLookBits.bit_color(hot, col, 1.0, 0.08), col)
	assert_eq(RcLookBits.scale_at(0.0), 1.0)
	assert_almost_eq(RcLookBits.scale_at(1.0), cfg.end_scale, 1e-9)


func test_config_is_the_games_constants() -> void:
	var c := RcLookBits.default_config()
	assert_eq(c.rim_control, BitsPath.RIM_CONTROL)
	assert_eq(c.free_bow, BitsPath.FREE_BOW)
	assert_eq(c.flight_spread, BitsPath.FLIGHT_SPREAD)
	assert_eq(c.spin_min, BitsPath.SPIN_MIN)
	assert_eq(c.spin_max, BitsPath.SPIN_MAX)
	assert_eq(c.flip_seconds, BinaryBits.FLIP_SECONDS)
	assert_eq(c.frames, BinaryBits.FRAMES)
	assert_eq(c.bit_scale, BinaryBits.BIT_SCALE)
	assert_eq(c.linger, BinaryBits.LINGER)
	assert_eq(c.max_bits, BinaryBits.MAX_BITS)
	assert_eq(c.cpu_max, BinaryBits.CPU_MAX)
	assert_eq(c.pool_size, BinaryBits.POOL_SIZE)
	assert_eq(c.rect_bits, BinaryBits.RECT_BITS)
	assert_eq(c.rim_alpha, BitsSeam.RIM_ALPHA)
	assert_eq(c.outline_share, BitsSeam.OUTLINE_SHARE)
	assert_eq(c.rim_px, BitsSeam.RIM_PX)
	assert_eq(c.trail_alpha, BitsSeam.TRAIL_ALPHA)
	assert_eq(c.trail_lag, BitsSeam.TRAIL_LAG)
	assert_eq(c.min_px, BitsSeam.MIN_PX)
	assert_eq(c.rim_control, BitPath.RIM_CONTROL, "the CPU streams use the same rim control")
	var fx := FileAccess.get_file_as_string(FX_LAYER)
	for pair: Array in [["STREAM_STAGGER", c.stream_stagger], ["STREAM_TRAVEL", c.stream_travel],
			["STREAM_TRAVEL_LONG", c.stream_travel_long], ["STREAM_BOW", c.stream_bow], ["SHARD_FREE", c.shard_free],
			["SHARD_STAGGER", c.shard_stagger], ["SHARD_TRAVEL", c.shard_travel], ["SHARD_SPREAD", c.shard_spread],
			["SHARD_MIN_SHARE", c.shard_min_share]]:
		var rx := RegEx.create_from_string("const %s := ([0-9.]+)" % pair[0])
		var m := rx.search(fx)
		assert_not_null(m, "%s in combat_fx_layer" % pair[0])
		if m != null:
			assert_almost_eq(float(m.get_string(1)), float(pair[1]), 1e-9, pair[0])


func test_include_constants_are_the_shaders() -> void:
	var c := RcLookBits.default_config()
	var inc := FileAccess.get_file_as_string("res://addons/rc_look/shaders/rc_bits.gdshaderinc")
	var shader := (load("res://shaders/kit/binary_bits.gdshader") as Shader).code
	for line: String in ["const float RCL_BITS_EASE_SMOOTH = %s;" % _g(c.ease_smooth), "const float RCL_BITS_EASE_QUAD = %s;" % _g(c.ease_quad),
			"const float RCL_BITS_END_SCALE = %s;" % _g(c.end_scale), "const float RCL_BITS_TURN = 6.28;",
			"const float RCL_BITS_FLIP_SPREAD = %s;" % _g(c.flip_spread)]:
		assert_string_contains(inc, line)
	assert_string_contains(shader, "* 0.35 + t * t * 0.65;", "binary_bits.gdshader's ease")
	assert_string_contains(shader, "mix(1.0, 0.55, t)", "binary_bits.gdshader's end scale")
	assert_string_contains(shader, "k.z * 6.28", "binary_bits.gdshader's turn")
	assert_string_contains(shader, "k.z * 7.0", "binary_bits.gdshader's flip spread")
	assert_string_contains(shader, "uniform float flip_seconds = %s;" % _g(c.flip_seconds))
	assert_string_contains(shader, "uniform float frames = %s;" % _g(float(c.frames)))


func test_presets_are_todays_looks() -> void:
	var wheel := RcLookBits.preset(&"wheel")
	assert_eq(wheel.path, RcLookBitsPreset.Path.RIM)
	assert_eq(wheel.hot_color, Palette.WHITE_HOT, "the GPU bits start WHITE_HOT")
	assert_eq(wheel.outline, RcLookBitsPreset.Outline.SAME_COLOUR)
	assert_eq(wheel.life, RcLookBitsPreset.Life.FLIP_TUMBLE)
	assert_true(wheel.spin_phase)
	assert_eq(RcLookBits.preset(&"free").path, RcLookBitsPreset.Path.FREE)
	var cpu := RcLookBits.preset(&"cpu")
	assert_false(cpu.spin_phase, "the CPU fallback has no spin phase offset today")
	assert_eq(cpu.hot_color, Palette.WHITE_HOT)
	var stream := RcLookBits.preset(&"seam")
	assert_eq(stream.hot_color, Palette.PAPER, "BitsSeam starts PAPER")
	assert_eq(stream.outline, RcLookBitsPreset.Outline.NIGHT_RIM)
	assert_eq(stream.life, RcLookBitsPreset.Life.TRAIL)
	for n in RcLookBits.REQUIRED:
		assert_almost_eq(RcLookBits.preset(n).spin_turn, 6.28, 1e-9, "%s keeps today's 6.28" % n)


func test_no_global_randomness() -> void:
	var rx := RegEx.create_from_string("\\b(randf|randi|randf_range|randi_range|randomize|rand_range)\\s*\\(")
	for f in BITS_FILES:
		var code := FileAccess.get_file_as_string(f)
		assert_ne(code, "", "%s exists" % f)
		assert_null(rx.search(code), "%s calls no global random" % f)


## A float as the shader files spell it (one decimal at least).
func _g(v: float) -> String:
	var s := str(v)
	return s if s.contains(".") else s + ".0"


## The designer's rulings (DIRECTION_REVIEW 2026-10-22): PAPER hot on every system, the NIGHT_SKY rim, a bursts preset that
## flips and tumbles with the per-bit spin phase, a stream preset with a steady glyph and a trail copy, the turn 6.28.
func test_ruled_presets() -> void:
	for n: StringName in [&"burst", &"stream"]:
		var p := RcLookBits.preset(n)
		assert_eq(p.hot_color, Palette.PAPER, "%s starts PAPER" % n)
		assert_eq(p.outline, RcLookBitsPreset.Outline.NIGHT_RIM, "%s has the NIGHT_SKY rim" % n)
		assert_true(p.spin_phase, "%s: per-bit spin phase" % n)
		assert_almost_eq(p.spin_turn, 6.28, 1e-9, "%s keeps 6.28" % n)
	assert_eq(RcLookBits.preset(&"burst").life, RcLookBitsPreset.Life.FLIP_TUMBLE)
	assert_eq(RcLookBits.preset(&"burst").path, RcLookBitsPreset.Path.RIM)
	assert_true(RcLookBits.preset(&"burst").bold_stroke, "the burst keeps the old stroke weight under the rim")
	assert_false(RcLookBits.preset(&"stream").bold_stroke, "the stream keeps the thin glyph inside the rim")
	assert_eq(RcLookBits.preset(&"stream").life, RcLookBitsPreset.Life.TRAIL)
	assert_eq(RcLookBits.preset(&"stream").path, RcLookBitsPreset.Path.FREE)
	assert_eq(RcLookBits.default_config().rim_alpha, 0.95, "the rim at 95 %")
