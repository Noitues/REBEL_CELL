extends GutTest
## LOOK-TOOLBOX module 8 (fast tier): wet and water. The shipped config validates and is pinned to the game's live
## numbers (CityShaderConfigData wet for the street and the plinth, CityConfig.water_plane for the water); each preset's
## F0 follows its view's policy; Schlick runs from F0 overhead to 1 at grazing; the puddle roughness runs dry to wet
## across the noise range; GGX integrates its projected lobe to about 1 and sharpens as roughness falls; the ridge is 1
## on the mid line; the shore fade halves every len x ln 2.


func test_shipped_config_validates() -> void:
	assert_eq(RcLookWet.default_config().validate(), PackedStringArray())
	for n in RcLookWet.REQUIRED:
		assert_not_null(RcLookWet.preset(n), "preset %s" % n)


func test_a_bad_preset_is_reported() -> void:
	var p := RcLookWetPreset.new()
	p.noise_scale = 0.0
	p.octaves = 9
	p.rough_noise = Vector2(0.6, 0.4)
	p.ior = 0.5
	assert_eq(p.validate().size(), 4, str(p.validate()))
	var cfg := RcLookWetConfig.new()
	cfg.presets = {&"street": p}
	assert_eq(cfg.validate().size(), 6, "missing plinth + water + four: %s" % str(cfg.validate()))


func test_presets_are_pinned_to_the_game() -> void:
	var wet: Dictionary = CityShaderConfigData.shipped().wet
	for n: StringName in [&"street", &"plinth"]:
		var p := RcLookWet.preset(n)
		assert_almost_eq(p.noise_scale, float(wet["noise_scale"]), 1e-6, n)
		assert_eq(p.octaves, int(wet["noise_octaves"]), n)
		assert_almost_eq(p.rough_noise.x, float(wet["rough_noise"][0]), 1e-6, n)
		assert_almost_eq(p.rough_noise.y, float(wet["rough_noise"][1]), 1e-6, n)
		assert_almost_eq(p.rough_wet.x, float(wet["rough_wet"][0]), 1e-6, n)
		assert_almost_eq(p.rough_wet.y, float(wet["rough_wet"][1]), 1e-6, n)
		assert_almost_eq(p.specular, float(wet["specular"]), 1e-6, n)
	var plane: Dictionary = (load("res://content/config/city_config.tres") as CityConfig).water_plane
	var w := RcLookWet.preset(&"water")
	assert_almost_eq(w.ior, float(plane["ior"]), 1e-6)
	assert_almost_eq(w.fresnel_boost, float(plane["fresnel_boost"]), 1e-6)


func test_each_preset_keeps_its_views_f0_policy() -> void:
	assert_almost_eq(RcLookWet.preset(&"street").f0(), 0.16 * 0.7, 1e-6, "wet_street: 0.08 x amount x 2")
	assert_almost_eq(RcLookWet.preset(&"plinth").f0(), 0.08 * 0.7, 1e-6, "city_building: 0.08 x wet_spec")
	assert_almost_eq(RcLookWet.preset(&"water").f0(), 0.0200593, 1e-6, "water plane: IOR 1.33")


func test_fresnel_runs_from_f0_to_one() -> void:
	assert_almost_eq(RcLookWet.fresnel(1.0, 0.04), 0.04, 1e-6, "overhead: F0")
	assert_almost_eq(RcLookWet.fresnel(0.0, 0.04), 1.0, 1e-6, "grazing: all")
	var last := 2.0
	for k in 21:
		var f := RcLookWet.fresnel(k / 20.0, 0.04)
		assert_true(f <= last, "falls toward overhead (%d)" % k)
		last = f


func test_puddle_roughness_runs_dry_to_wet() -> void:
	var p := RcLookWet.preset(&"street")
	assert_almost_eq(RcLookWet.puddle_rough(0.0, p.rough_noise, p.rough_wet), p.rough_wet.x, 1e-6, "dry")
	assert_almost_eq(RcLookWet.puddle_rough(1.0, p.rough_noise, p.rough_wet), p.rough_wet.y, 1e-6, "puddle")
	var mid := RcLookWet.puddle_rough((p.rough_noise.x + p.rough_noise.y) * 0.5, p.rough_noise, p.rough_wet)
	assert_almost_eq(mid, (p.rough_wet.x + p.rough_wet.y) * 0.5, 1e-6, "smoothstep's middle")


func test_ggx_is_normalised_and_sharpens() -> void:
	const STEPS := 4000
	for a: float in [0.09, 0.25, 0.6]:
		# integral of D(h) (n . h) over the hemisphere = 1; dω = 2π sin θ dθ.
		var s := 0.0
		for i in STEPS:
			var th := (float(i) + 0.5) / STEPS * PI * 0.5
			s += RcLookWet.ggx_d(cos(th), a) * cos(th) * 2.0 * PI * sin(th) * (PI * 0.5 / STEPS)
		assert_almost_eq(s, 1.0, 0.01, "normalised at a=%s" % a)
	assert_true(RcLookWet.ggx_d(1.0, 0.01) > RcLookWet.ggx_d(1.0, 0.1), "a smoother surface peaks higher")


func test_ridge_and_shore() -> void:
	assert_almost_eq(RcLookWet.ridge(0.5, 0.22), 1.0, 1e-6, "on the mid line")
	assert_almost_eq(RcLookWet.ridge(0.0, 0.22), 0.0, 1e-6, "far from it")
	assert_almost_eq(RcLookWet.shore(0.0, 14.0), 1.0, 1e-6)
	assert_almost_eq(RcLookWet.shore(14.0 * log(2.0), 14.0), 0.5, 1e-6, "halves every len ln 2")
