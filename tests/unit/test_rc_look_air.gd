extends GutTest
## LOOK-TOOLBOX module 7 (fast tier): atmosphere. The shipped config validates; the air is zero before its start,
## grows with distance toward 1 and thins with height down to `high`; seen through no air a colour is unchanged and
## through full air it is the air; the sky meets the horizon colour at the horizon and tends to the top overhead.

const STEPS := 20


func test_shipped_config_validates() -> void:
	assert_eq(RcLookAir.default_config().validate(), PackedStringArray())
	for n in RcLookAirConfig.REQUIRED:
		assert_not_null(RcLookAir.preset(n), "preset %s" % n)


func test_a_bad_preset_is_reported() -> void:
	var cfg := RcLookAirConfig.new()
	var p := RcLookAirPreset.new()
	p.height = 0.0
	p.high = 2.0
	cfg.presets = {&"day": p}
	# missing night + height + high
	assert_eq(cfg.validate().size(), 3, str(cfg.validate()))


func test_air_grows_with_distance_and_thins_with_height() -> void:
	var p := RcLookAirPreset.new()
	p.start = 10.0
	p.density = 0.02
	p.height = 30.0
	p.high = 0.2
	assert_eq(RcLookAir.amount(p, 5.0, 0.0), 0.0, "nothing before the start")
	var last := -1.0
	for i in STEPS + 1:
		var a := RcLookAir.amount(p, 10.0 + 40.0 * i, 0.0)
		assert_true(a > last or (i == 0 and a == 0.0), "grows at step %d" % i)
		last = a
	assert_almost_eq(RcLookAir.amount(p, 1e6, 0.0), 1.0, 1e-6, "far away: all air")
	assert_almost_eq(RcLookAir.amount(p, 1e6, 1e6), 0.2, 1e-6, "high up: thinned to `high`")
	assert_true(RcLookAir.amount(p, 200.0, 40.0) < RcLookAir.amount(p, 200.0, 0.0), "thinner higher up")


func test_mix_ends() -> void:
	var c := Color(0.7, 0.2, 0.4, 0.5)
	var air := Color(0.1, 0.1, 0.3)
	assert_true(RcLookAir.mix(c, air, 0.0).is_equal_approx(c), "no air: unchanged")
	var full := RcLookAir.mix(c, air, 1.0)
	assert_true(Color(full.r, full.g, full.b).is_equal_approx(air), "full air: the air")
	assert_eq(full.a, 0.5, "alpha kept")


func test_sky_meets_the_horizon_and_tends_to_the_top() -> void:
	for n in RcLookAirConfig.REQUIRED:
		var p := RcLookAir.preset(n)
		assert_true(RcLookAir.sky(p, 0.0).is_equal_approx(Color(p.sky_horizon.r, p.sky_horizon.g, p.sky_horizon.b)),
				"%s: horizon colour at e = 0" % n)
		var up := RcLookAir.sky(p, 1.0)
		assert_true(absf(up.r - p.sky_top.r) < 0.02 and absf(up.b - p.sky_top.b) < 0.02, "%s: near the top overhead" % n)
		var down := RcLookAir.sky(p, -1.0)
		assert_true(down.is_equal_approx(Color(p.sky_ground.r, p.sky_ground.g, p.sky_ground.b)), "%s: ground below" % n)


func test_far_things_converge_on_the_horizon() -> void:
	# Art-pass 2026-10-22: aerial perspective ends on the sky's horizon colour, or depth reads wrong.
	for n in RcLookAirConfig.REQUIRED:
		var p := RcLookAir.preset(n)
		var far := RcLookAir.mix(Palette.DESK_METAL, p.air_color(), RcLookAir.amount(p, 1e6, 0.0))
		assert_true(far.is_equal_approx(RcLookAir.sky(p, 0.0)), "%s: the far facade is the horizon" % n)


func test_night_air_keeps_the_skyline_dark() -> void:
	# Art-pass 2026-10-22 (squint test against hq_solace_overview): the air never lifts the near plane, and far towers
	# stay clearly darker than the sky behind them; depth comes from window density and size, not a grey wash.
	var p := RcLookAir.preset(&"night")
	assert_lt(RcLookAir.amount(p, 20.0, 0.0), 0.05, "the near plane (20 BU) is not lifted")
	var far := RcLookAir.mix(Palette.DESK_DARK, p.air_color(), RcLookAir.amount(p, 480.0, 0.0))
	assert_lt(Palette.luminance(far), Palette.luminance(RcLookAir.sky(p, 0.02)) * 0.8, "far towers darker than the sky")


func test_the_air_pass_carries_the_preset() -> void:
	var p := RcLookAir.preset(&"night")
	var n := RcLookAir.pass_node(p, 2.0, {"density": 0.0008, "start": 300.0})
	var m := n.material_override as ShaderMaterial
	assert_not_null(m, "a shader material")
	var a := p.air_color()
	assert_eq(m.get_shader_parameter(&"air"), Vector3(a.r, a.g, a.b), "the horizon colour")
	assert_eq(m.get_shader_parameter(&"air_a"), Vector4(300.0, 0.0008, p.height, p.high), "overrides applied, the rest kept")
	assert_eq(float(m.get_shader_parameter(&"ground_y")), 2.0)
	n.free()
