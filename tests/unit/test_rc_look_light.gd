extends GutTest
## LOOK-TOOLBOX module 6 (fast tier): light, spill, glow, bloom. The shipped config validates; the falloffs hit their
## marks (exp: 1/e at reach; pow: 0 at reach) and fall monotonically; adding light never darkens, leaves the base alone
## at zero light and never passes white; the bright pass is zero below the knee, continuous through it and linear
## above; bloom strength follows the quality tier.

const STEPS := 24


func test_shipped_config_validates() -> void:
	assert_eq(RcLookLight.default_config().validate(), PackedStringArray())
	for n in RcLookLightConfig.REQUIRED:
		assert_not_null(RcLookLight.preset(n), "preset %s" % n)


func test_a_bad_config_is_reported() -> void:
	var cfg := RcLookLightConfig.new()
	var p := RcLookLightPreset.new()
	p.reach = 0.0
	cfg.presets = {&"glow": p, &"x": 3}
	cfg.bloom_knee = 0.0
	# missing halo, pool, spill, spill_ui (4) + x not a preset + glow reach + knee
	assert_eq(cfg.validate().size(), 7, str(cfg.validate()))


func test_falloffs_hit_their_marks_and_fall() -> void:
	assert_almost_eq(RcLookLight.fall_exp(2.0, 2.0, 2.0), exp(-1.0), 1e-6, "exp: 1/e at reach")
	assert_almost_eq(RcLookLight.fall_exp(0.0, 2.0, 1.0), 1.0, 1e-6)
	assert_eq(RcLookLight.fall_pow(2.0, 2.0, 1.6), 0.0, "pow: 0 at reach")
	assert_eq(RcLookLight.fall_pow(5.0, 2.0, 1.6), 0.0, "and past it")
	for n in RcLookLightConfig.REQUIRED:
		var p := RcLookLight.preset(n)
		var last := INF
		for i in STEPS + 1:
			var v := RcLookLight.at(p, 2.0 * float(i) / STEPS)
			assert_true(v <= last, "%s falls at step %d" % [n, i])
			last = v


func test_light_add_never_darkens_and_never_passes_white() -> void:
	for b: float in [0.0, 0.05, 0.3, 0.8, 1.0]:
		var base := Color(b, b * 0.5, 1.0 - b)
		assert_true(RcLookLight.light_add(base, Color(0, 0, 0)).is_equal_approx(base), "no light: base kept (%s)" % base)
		var last := -1.0
		for i in STEPS + 1:
			var l := 4.0 * float(i) / STEPS
			var o := RcLookLight.light_add(base, Color(l, l, l))
			assert_true(o.r >= base.r - 1e-6 and o.g >= base.g - 1e-6 and o.b >= base.b - 1e-6, "never darker")
			assert_true(o.r <= 1.0 + 1e-6 and o.g <= 1.0 + 1e-6 and o.b <= 1.0 + 1e-6, "never past white")
			assert_true(o.r >= last - 1e-6, "brighter with more light")
			last = o.r
	var small := RcLookLight.light_add(Color(0, 0, 0), Color(0.01, 0, 0)).srgb_to_linear()
	assert_almost_eq(small.r, 0.01, 1e-3, "a little light on black adds about itself")


func test_bright_pass_has_a_soft_knee() -> void:
	var t := 0.8
	var k := 0.4
	assert_eq(RcLookLight.bright(Color(0.3, 0.3, 0.3), t, k).r, 0.0, "below the knee: nothing")
	var hi := RcLookLight.bright(Color(2.0, 1.0, 0.0), t, k)
	assert_almost_eq(hi.r, 2.0 - t, 1e-5, "above: linear past the threshold")
	assert_almost_eq(hi.g / hi.r, 0.5, 1e-5, "the hue kept")
	var last := 0.0
	for i in STEPS + 1:
		var l := (t - k) + 2.0 * k * float(i) / STEPS
		var v := RcLookLight.bright(Color(l, l, l), t, k).r
		assert_true(v >= last - 1e-6, "monotone through the knee at %.3f" % l)
		assert_true(absf(v - last) < 0.06, "continuous at %.3f" % l)
		last = v


func test_bloom_strength_follows_the_tier() -> void:
	var lo := RcLookLight.bloom_material(RcLookQualityState.make(0))
	var hi := RcLookLight.bloom_material(RcLookQualityState.make(2))
	assert_eq(float(lo.get_shader_parameter(&"strength")), 0.0, "low tier: no bloom")
	assert_eq(float(hi.get_shader_parameter(&"strength")), 1.0, "high tier: full")
	assert_eq(float(RcLookLight.bloom_material(RcLookQualityState.make(2, true)).get_shader_parameter(&"strength")), 1.0,
			"reduce effects keeps the static bloom")


func test_the_2d_key_blooms_neon_never_paper() -> void:
	var c := RcLookLight.default_config()
	var paper := RcLookLight.bright(Palette.PAPER.srgb_to_linear(), c.bloom_threshold, c.bloom_knee, c.bloom_key)
	assert_eq(paper.r + paper.g + paper.b, 0.0, "paper never blooms")
	var white := RcLookLight.bright(Color(1, 1, 1), c.bloom_threshold, c.bloom_knee, c.bloom_key)
	assert_eq(white.r, 0.0, "nor does white")
	for n: Color in [Palette.CELL_PINK, Palette.NET_CYAN, Palette.CELL_ACID]:
		var b := RcLookLight.bright(n.srgb_to_linear(), c.bloom_threshold, c.bloom_knee, c.bloom_key)
		assert_gt(maxf(b.r, maxf(b.g, b.b)), 0.0, "neon %s blooms" % n.to_html(false))


func test_added_light_keeps_its_hue() -> void:
	# Designer 2026-10-21: overlapping neon holds its colour instead of drifting to white.
	var pink := Palette.CELL_PINK.srgb_to_linear()
	for k: float in [0.5, 2.0, 8.0]:
		var o := RcLookLight.light_add(Color(0, 0, 0), Color(pink.r * k, pink.g * k, pink.b * k)).srgb_to_linear()
		assert_almost_eq(o.g / o.r, pink.g / pink.r, 1e-3, "x%.1f: pink stays pink" % k)
		assert_almost_eq(o.b / o.r, pink.b / pink.r, 1e-3, "x%.1f" % k)


func test_ui_spill_reaches_half_the_citys() -> void:
	# Designer 2026-10-21: separate values; UI spill about half the city's so panels stay crisp.
	assert_almost_eq(RcLookLight.preset(&"spill_ui").reach, RcLookLight.preset(&"spill").reach * 0.5, 1e-6)


func test_facing_fades_edge_on() -> void:
	var v := Vector3(0, 0, 1)
	assert_almost_eq(RcLookLight.facing(Vector3(0, 0, 3), v, 1.5), 1.0, 1e-6, "face-on: full")
	assert_almost_eq(RcLookLight.facing(Vector3(0, 0, -1), v, 1.5), 1.0, 1e-6, "either side (cull disabled)")
	assert_almost_eq(RcLookLight.facing(Vector3(1, 0, 0), v, 1.5), 0.0, 1e-6, "edge-on: nothing")
	assert_almost_eq(RcLookLight.facing(Vector3(1, 0, 1), v, 2.0), 0.5, 1e-6, "45 degrees, soft 2: a half")
