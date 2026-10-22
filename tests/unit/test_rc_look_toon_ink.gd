extends GutTest
## LOOK-TOOLBOX modules 4 / 5 (fast tier): toon and ink. The shipped configs validate and are pinned to the game's
## live numbers (ToonInkMaterial for the props and the hull, CityConfig for the city bands and the post ink, its
## backdrop_post for the backdrop's); bands step at their edges and only up; the band tint is the shadow tint in the
## shadow band and white when lit; the rim is 0 facing and 1 edge-on; the hull grows its vertex exactly width_px px on
## screen and its wobble stays within the share; the post edges fire past their thresholds only.


func test_shipped_configs_validate() -> void:
	assert_eq(RcLookToon.default_config().validate(), PackedStringArray())
	assert_eq(RcLookInk.default_config().validate(), PackedStringArray())
	for n in RcLookToon.REQUIRED:
		assert_not_null(RcLookToon.preset(n), "toon preset %s" % n)
	for n in RcLookInk.REQUIRED:
		assert_not_null(RcLookInk.preset(n), "ink preset %s" % n)


func test_bad_presets_are_reported() -> void:
	var t := RcLookToonPreset.new()
	t.lo = 0.6
	t.hi = 0.5
	t.shade_low = 0.9
	t.ramp = PackedColorArray([Color.RED])
	assert_eq(t.validate().size(), 3, str(t.validate()))
	var cfg := RcLookToonConfig.new()
	cfg.presets = {&"props": t}
	assert_eq(cfg.validate().size(), 4, "missing city + the preset's three: %s" % str(cfg.validate()))
	var i := RcLookInkPreset.new()
	i.width_px = 0.0
	i.wobble = 2.0
	i.alpha = -1.0
	i.depth_edge = 0.0
	assert_eq(i.validate().size(), 4, str(i.validate()))


func test_presets_are_pinned_to_the_game() -> void:
	var props := RcLookToon.preset(&"props")
	assert_eq(props.lo, ToonInkMaterial.BAND_LO)
	assert_eq(props.hi, ToonInkMaterial.BAND_HI)
	assert_eq(props.shade_mid, ToonInkMaterial.SHADE_MID)
	assert_eq(props.shade_low, ToonInkMaterial.SHADE_LOW)
	var city_cfg := load("res://content/config/city_config.tres") as CityConfig
	var city := RcLookToon.preset(&"city")
	assert_almost_eq(city.lo, city_cfg.ramp_edges.x, 1e-6)
	assert_almost_eq(city.hi, city_cfg.ramp_edges.y, 1e-6)
	var hull := RcLookInk.preset(&"hull")
	assert_eq(hull.width_px, ToonInkMaterial.INK_PX)
	assert_eq(hull.wobble, ToonInkMaterial.INK_WOBBLE)
	var post := RcLookInk.preset(&"post")
	assert_almost_eq(post.normal_edge, city_cfg.ink_normal_edge, 1e-6)
	assert_almost_eq(post.depth_edge, city_cfg.ink_depth_edge, 1e-6)
	var back := RcLookInk.preset(&"post_backdrop")
	assert_almost_eq(back.normal_edge, float(city_cfg.backdrop_post["ink_normal_edge"]), 1e-6)
	assert_almost_eq(back.depth_edge, float(city_cfg.backdrop_post["ink_depth_edge"]), 1e-6)
	assert_almost_eq(back.wobble_px, float(city_cfg.backdrop_post["ink_wobble_px"]), 1e-6)


func test_bands_step_at_their_edges_and_only_up() -> void:
	var p := RcLookToon.preset(&"props")
	assert_eq(RcLookToon.band(p.lo, p.lo, p.hi), 0, "the edge itself is still below")
	assert_eq(RcLookToon.band(p.lo + 1e-4, p.lo, p.hi), 1)
	assert_eq(RcLookToon.band(p.hi + 1e-4, p.lo, p.hi), 2)
	var last := -1.0
	for k in 41:
		var s := RcLookToon.band_shade(-1.0 + k * 0.05, p.lo, p.hi, p.shade_mid, p.shade_low)
		assert_true(s >= last, "never darker with more light (step %d)" % k)
		assert_true(s == p.shade_low or s == p.shade_mid or s == 1.0, "only the three shades")
		last = s


func test_band_tint_runs_from_the_shadow_tint_to_white() -> void:
	var p := RcLookToon.preset(&"props")
	assert_eq(RcLookToon.band_tint(p.shade_low, p.shade_low, p.shadow_tint), Color(p.shadow_tint, 1.0))
	assert_eq(RcLookToon.band_tint(1.0, p.shade_low, p.shadow_tint), Color(1, 1, 1))


func test_rim_is_dark_facing_and_full_edge_on() -> void:
	assert_almost_eq(RcLookToon.rim(Vector3.BACK, Vector3.BACK, 3.0), 0.0, 1e-6)
	assert_almost_eq(RcLookToon.rim(Vector3.RIGHT, Vector3.BACK, 3.0), 1.0, 1e-6)
	assert_almost_eq(RcLookToon.rim(Vector3.FORWARD, Vector3.BACK, 3.0), 1.0, 1e-6, "back faces clamp to edge-on")


func test_hull_grows_its_vertex_width_px_on_screen() -> void:
	var view := Vector2(1920.0, 1080.0)
	var clip := Vector4(0.2, -0.1, 0.5, 4.0)
	var out := RcLookInk.hull_clip(clip, Vector2(1.0, 0.0), 2.5, view)
	var ndc_dx := out.x / out.w - clip.x / clip.w
	assert_almost_eq(ndc_dx * 0.5 * view.x, 2.5, 1e-4, "2.5 px on screen whatever the depth")
	assert_eq(out.z, clip.z)
	assert_eq(out.w, clip.w)
	var hull := RcLookInk.preset(&"hull")
	assert_almost_eq(RcLookInk.hull_width(hull.width_px, hull.wobble, 0.5), hull.width_px, 1e-6, "mid noise: no wobble")
	assert_almost_eq(RcLookInk.hull_width(hull.width_px, hull.wobble, 1.0), hull.width_px * (1.0 + hull.wobble), 1e-6)
	assert_almost_eq(RcLookInk.hull_width(hull.width_px, hull.wobble, 0.0), hull.width_px * (1.0 - hull.wobble), 1e-6)


func test_post_edges_fire_past_their_thresholds_only() -> void:
	var post := RcLookInk.preset(&"post")
	var flat := Vector4(0.0, 0.0, 1.0, 0.0)
	assert_eq(RcLookInk.normal_edge(flat, flat, post.normal_edge), 0.0)
	assert_eq(RcLookInk.normal_edge(flat, Vector4(0.0, 0.0, 1.0, 1.0), post.normal_edge), 1.0, "a material change")
	assert_eq(RcLookInk.normal_edge(flat, Vector4(1.0, 0.0, 0.0, 0.0), post.normal_edge), 1.0, "a crease")
	var thr := RcLookInk.depth_thr(post.depth_edge, 440.0, RcLookInk.default_config().ortho_ref)
	assert_almost_eq(thr, post.depth_edge * 440.0 / 300.0, 1e-6)
	assert_eq(RcLookInk.depth_edge(10.0, 10.0 + thr * 0.99, thr), 0.0)
	assert_eq(RcLookInk.depth_edge(10.0, 10.0 + thr * 1.01, thr), 1.0)
