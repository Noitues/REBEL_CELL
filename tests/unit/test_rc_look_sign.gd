extends GutTest
## LOOK-TOOLBOX module 11 (fast tier): signage and neon. The shipped config validates; the flicker and blink numbers
## are pinned to dress_neon / city_glow's live ones; the "flat" tube is today's flat colour everywhere, "lighten" the
## same mix across the tube, "hot" reaches its core colour only on the centre line and keeps the tube colour at the
## edge; the hot mix toward white is beam_shaft's; the tube coverage is 1 inside, half on the edge, 0 outside; the
## flicker stays in 0..1 and is dark between bursts; the beacon peaks at phase 0.


func test_shipped_config_validates() -> void:
	assert_eq(RcLookSign.default_config().validate(), PackedStringArray())
	for n in RcLookSign.REQUIRED:
		assert_not_null(RcLookSign.preset(n), "preset %s" % n)


func test_a_bad_preset_is_reported() -> void:
	var p := RcLookSignPreset.new()
	p.half_w_px = 0.0
	p.core_share = 2.0
	p.hot = 0.5
	assert_eq(p.validate().size(), 3, "width, core share, a flat tube with a core: %s" % str(p.validate()))
	var cfg := RcLookSignConfig.new()
	cfg.presets = {&"flat": RcLookSignPreset.new()}
	cfg.burst_len = 1.0
	assert_eq(cfg.validate().size(), 3, "missing lighten + hot + burst_len: %s" % str(cfg.validate()))


func test_flicker_and_blink_are_the_games() -> void:
	var cfg := RcLookSign.default_config()
	var neon := (load("res://shaders/city/dress_neon.gdshader") as Shader).code
	assert_string_contains(neon, "rcl_flicker(t, k, cust.y, %.2f, %.1f, %.1f)" % [cfg.burst_len, cfg.hum_hz, cfg.hum_floor],
			"dress_neon flickers through rc_sign with these numbers")
	var glow_code := FileAccess.get_file_as_string("res://shaders/city/city_glow.gdshaderinc")
	assert_string_contains(glow_code, "uniform float duty = %.2f;" % cfg.blink_duty)
	assert_string_contains(glow_code, "uniform float off_level = %.2f;" % cfg.blink_off)


func test_treatments() -> void:
	var pink := Palette.NEON_TUBE
	var flat := RcLookSign.preset(&"flat")
	for d: float in [0.0, 2.0, 4.0]:
		assert_eq(RcLookSign.tube_color(flat, pink, d), pink, "flat at %s px" % d)
	var lit := RcLookSign.preset(&"lighten")
	assert_eq(RcLookSign.tube_color(lit, pink, 0.0), RcLookSign.tube_color(lit, pink, lit.half_w_px), "even across")
	var hot := RcLookSign.preset(&"hot")
	var centre := RcLookSign.tube_color(hot, pink, 0.0)
	assert_eq(centre, RcLookSign.hot_to(pink, hot.core_color, hot.hot), "the centre line reaches hot x core")
	assert_eq(RcLookSign.tube_color(hot, pink, hot.half_w_px * hot.core_share), pink, "the tube colour past the core")
	assert_true(centre.get_luminance() > pink.get_luminance(), "the core is brighter than the tube")


func test_hot_is_beam_shafts_mix() -> void:
	var c := Color(1.0, 0.4, 0.7)
	assert_eq(RcLookSign.hot(c, 0.0, 0.5), c)
	var h := RcLookSign.hot(c, 1.0, 0.5)
	assert_almost_eq(h.g, 0.4 + (1.0 - 0.4) * 0.5, 1e-6, "mix(beam_col, white, hot x core)")
	assert_almost_eq(RcLookSign.gauss(0.13, 0.13), exp(-0.5), 1e-6)


func test_tube_coverage_and_core() -> void:
	assert_eq(RcLookSign.tube_cov(0.0, 4.0, 1.0), 1.0)
	assert_almost_eq(RcLookSign.tube_cov(4.0, 4.0, 1.0), 0.5, 1e-6, "half on the edge")
	assert_eq(RcLookSign.tube_cov(6.0, 4.0, 1.0), 0.0)
	assert_eq(RcLookSign.tube_core(0.0, 1.4), 1.0)
	assert_eq(RcLookSign.tube_core(1.4, 1.4), 0.0)


func test_flicker_beacon_blink() -> void:
	var cfg := RcLookSign.default_config()
	for k in 200:
		var f := RcLookSign.flicker(k / 200.0, 2.0, 0.3, cfg.burst_len, cfg.hum_hz, cfg.hum_floor)
		assert_true(f >= 0.0 and f <= 1.0, "in 0..1 (%d)" % k)
	assert_eq(RcLookSign.flicker(0.25, 1.0, 0.0, cfg.burst_len, cfg.hum_hz, cfg.hum_floor), 0.0, "dark between bursts")
	assert_almost_eq(RcLookSign.beacon(0.0), 1.0, 1e-6)
	assert_almost_eq(RcLookSign.beacon(0.5), 0.2, 1e-6)
	assert_eq(RcLookSign.blink(0.1, cfg.blink_duty, cfg.blink_off), 1.0)
	assert_eq(RcLookSign.blink(0.9, cfg.blink_duty, cfg.blink_off), cfg.blink_off)
