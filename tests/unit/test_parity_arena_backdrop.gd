extends GutTest
## Parity fix S-ARENA (designer group ruling 2026-10-05: combat matches the concept; CMB-01,
## BOSS-03, BACKDROP-01, BACKDROP-02, MOTION-07): the combat backdrop's city close-up keeps the
## concept's lit city once it settles (no drop to near black), the HUD and the wheels keep their
## contrast over it, every corporation's HQ landmark stands whole in the frame for a boss fight
## and a Site fight frames its Site's building.
##
## The settled close-up is measured on fixtures: `tests/fixtures/arena_backdrop/<shot>.png`,
## point samples (256x144) of each close-up's own render (CityView3D.get_texture, before the
## backdrop's shader) from the windowed `hq_run_lab --raw`. The backdrop's shader receives
## that texture as linear values (measured windowed: with the grade off the frame shows the
## render's linear values, its mid-tones ~4x darker: MOTION-07's settle step), so the model
## below decodes each sample to linear, applies CombatBackdrop.graded (the shader's mirror)
## and measures what the screen shows.

const FIXTURES := "res://tests/fixtures/arena_backdrop/"
const STILLS := "res://assets/backdrops/combat/"
const SHOTS: Array[String] = ["hq_meridian", "hq_solace", "hq_halcyon", "hq_orbital", "hq_rebel_cell",
	"site_meridian", "site_solace", "site_halcyon", "site_orbital"]
const CORPS: Array[StringName] = [&"meridian", &"solace", &"halcyon", &"orbital"]
## The view sizes the framing is checked at (the design size and 1080p).
const SIZES: Array[Vector2] = [Vector2(1280, 720), Vector2(1920, 1080)]
## WCAG 2.1 floors: words 4.5:1, a component's edge 3:1.
const TEXT_MIN := 4.5
const EDGE_MIN := 3.0
## Where a wheel's HP number and its rim stand, in disc radii from the wheel's centre (the
## HP arc's numbers sit just under the frame; the rim is the disc's edge).
const HP_AT := 1.1
const RIM_AT := 1.0
## Pixel step when measuring the stills (1280x720 JPEGs).
const STILL_STEP := 4


func _cfg() -> CityConfig:
	return CityView3D.CONFIG


## Mean relative luminance of image `img` (sRGB pixels, mapped by `fn` first when valid) over
## the rows between the top bar's band and the hand's (the shader's top_band / bottom_band).
func _mid_luma(img: Image, step: int, fn: Callable = Callable()) -> float:
	var h := img.get_height()
	var y0 := int(h * 0.1)
	var y1 := int(h * 0.76)
	var total := 0.0
	var n := 0
	for y in range(y0, y1, step):
		for x in range(0, img.get_width(), step):
			var c := img.get_pixel(x, y)
			if fn.is_valid():
				c = fn.call(c)
			total += Palette.luminance(c)
			n += 1
	return total / maxf(1.0, float(n))


func _fixture(shot: String) -> Image:
	return Image.load_from_file(ProjectSettings.globalize_path(FIXTURES + shot + ".png"))


## What the screen shows for a fixture sample: the render's value reaching the shader as linear,
## through the grade.
func _shown(c: Color) -> Color:
	return CombatBackdrop.graded(_cfg(), c.srgb_to_linear())


## The same with the grade off (main before the fix: the linear values shown as they are).
func _shown_ungraded(c: Color) -> Color:
	return c.srgb_to_linear()


func test_the_luma_band_is_the_concept_stills() -> void:
	var band := _cfg().backdrop_luma_band
	for corp in [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]:
		for kind in ["hq", "site"]:
			var path := ProjectSettings.globalize_path("%s%s_%s_night.jpg" % [STILLS, corp, kind])
			var img := Image.load_from_file(path)
			assert_not_null(img, "%s loads" % path)
			if img == null:
				continue
			var l := _mid_luma(img, STILL_STEP)
			assert_between(l, band.x, band.y, "%s_%s_night (the concept bake) sits in backdrop_luma_band" % [corp, kind])


func test_the_settled_close_up_stays_in_the_concept_band() -> void:
	var band := _cfg().backdrop_luma_band
	for shot in SHOTS:
		var img := _fixture(shot)
		assert_not_null(img, "fixture %s" % shot)
		if img == null:
			continue
		var l := _mid_luma(img, 1, _shown)
		assert_between(l, band.x, band.y, "%s: the settled close-up keeps the concept's light (%.3f)" % [shot, l])


func test_without_the_grade_the_close_up_drops_below_the_band() -> void:
	# MOTION-07's settle step reproduced: the city's render shown as linear values.
	for shot in SHOTS:
		var img := _fixture(shot)
		if img == null:
			continue
		var l := _mid_luma(img, 1, _shown_ungraded)
		assert_lt(l, _cfg().backdrop_luma_band.x, "%s ungraded is the near-black look (%.3f)" % [shot, l])


func test_the_grade_keeps_the_neon_hue_and_the_ink_dark() -> void:
	var cfg := _cfg()
	for c in [Palette.CELL_PINK, Palette.CELL_ACID, Color("#3DFFE0")]:
		var g := CombatBackdrop.graded(cfg, (c as Color).srgb_to_linear())
		assert_almost_eq(g.h, (c as Color).srgb_to_linear().h, 0.03, "%s keeps its hue (no clip to white)" % c.to_html())
		assert_lt(maxf(g.r, maxf(g.g, g.b)), 1.0001, "no channel past 1")
	var ink := CombatBackdrop.graded(cfg, Palette.INK.srgb_to_linear())
	assert_lt(Palette.luminance(ink), 0.01, "the ink lines stay near black")
	var off := cfg.duplicate() as CityConfig
	off.backdrop_exposure = 1.0
	off.backdrop_tint = Color(1, 1, 1)
	off.backdrop_saturation = 1.0
	var grey := Color(0.3, 0.3, 0.3)
	assert_true(CombatBackdrop.graded(off, grey).is_equal_approx(grey), "exposure 1, no tint, full saturation: identity")


## The shader's darkening of a pool at `d` disc radii from its wheel (pool_at; CityConfig
## backdrop_pool_dark / backdrop_pool_falloff).
func _pool_factor(d: float) -> float:
	var pool := exp(-pow(d / CombatBackdrop.POOL_REACH, _cfg().backdrop_pool_falloff))
	return 1.0 - _cfg().backdrop_pool_dark * pool


func test_hud_and_wheel_rims_keep_their_contrast_over_the_backdrop() -> void:
	var accents: Array[Color] = [Palette.CELL_PINK]
	for corp in CORPS:
		accents.append(Palette.corp_color(corp))
	for shot in SHOTS:
		var img := _fixture(shot)
		if img == null:
			continue
		# What is behind a word or a rim: the backdrop's local mean (the pool blurs it).
		var mean_l := _mid_luma(img, 1, _shown)
		var hp_l := mean_l * _pool_factor(HP_AT)
		var rim_l := mean_l * _pool_factor(RIM_AT)
		assert_gte(_contrast_l(Palette.luminance(WheelView.HP_COLOR), hp_l), TEXT_MIN,
			"%s: the HP number over the backdrop under its wheel" % shot)
		for a in accents:
			# A wheel's edge marks: its accent ring, its HP arc (WheelView.HP_COLOR) and its ink
			# frame; the disc reads when the best of them reaches 3:1 (WCAG 1.4.11).
			var edge := 0.0
			for mark: Color in [a, WheelView.HP_COLOR, Palette.INK]:
				edge = maxf(edge, _contrast_l(Palette.luminance(mark), rim_l))
			assert_gte(edge, EDGE_MIN, "%s: a %s wheel's edge against the backdrop" % [shot, a.to_html()])
		# The slice words (white on the slice fills, which only darken) over the pool's middle.
		var slice_l := mean_l * _pool_factor(0.0)
		assert_gte(_contrast_l(1.0, slice_l), TEXT_MIN, "%s: the slice numbers over the pool" % shot)


static func _contrast_l(a: float, b: float) -> float:
	return (maxf(a, b) + 0.05) / (minf(a, b) + 0.05)


## The 8 corners of `box` on screen through `cam` at `size`.
func _screen_box(cam: CityIsoCamera, box: AABB, size: Vector2) -> Rect2:
	var c := cam.copy()
	c.viewport = size
	var r := Rect2(c.project(box.get_endpoint(0)), Vector2.ZERO)
	for k in range(1, 8):
		r = r.expand(c.project(box.get_endpoint(k)))
	return r


func test_each_corps_hq_landmark_stands_whole_in_the_frame() -> void:
	var cfg := _cfg()
	for corp in CORPS:
		for size in SIZES:
			var shot := BackdropCatalog.city_shot(cfg, BackdropCatalog.place(corp, true, false), {}, size)
			assert_eq(shot["focus"], "hq", "%s boss: its HQ" % corp)
			var path := BackdropCatalog.hq_landmark_path(corp)
			assert_ne(path, "", "%s has an HQ landmark" % corp)
			var hq := NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
			var box := BackdropCatalog.landmark_box(cfg, path, hq, corp)
			var on := _screen_box(shot["camera"], box, size)
			var frame: Rect2 = cfg.backdrop_hq_frame_by_corp.get(corp, cfg.backdrop_hq_frame)
			var want := Rect2(frame.position * size, frame.size * size).grow(1.0)
			assert_true(want.encloses(on), "%s at %s: the landmark %s stands in its frame %s" % [corp, size, on, want])
			assert_gte(on.position.y, 0.0, "%s: its top (Solace's helix tip) is in the view" % corp)
			# OURS NOW / the won ellipse aim at the landmark's own top and middle.
			var top: Vector3 = shot["top"]
			assert_almost_eq(top.y, box.end.y, 0.01, "%s: the shot's top is the landmark's" % corp)


func test_site_fights_frame_the_site_lot() -> void:
	var cfg := _cfg()
	for corp in CORPS:
		var cd := RunManager.lookup().get_content(corp) as CorporationData
		var lots := CityLayout.site_points(cd)
		var ids: Array = lots.keys()
		ids.sort()
		for site: StringName in ids:
			var lot: Vector2 = lots[site]
			var inside := BackdropCatalog.site_close_up_lot(cfg, lot)
			var r := Rect2(cfg.city_rect).grow(-float(cfg.backdrop_site_inset))
			assert_true(r.grow(0.001).has_point(inside), "%s %s: the close-up stands it inside the city" % [corp, site])
			if r.has_point(lot):
				assert_eq(inside, lot, "%s %s: a Site well inside keeps its own lot" % [corp, site])
			var shot := BackdropCatalog.city_shot(cfg, BackdropCatalog.place(corp, false, false, site), lots, SIZES[0])
			assert_eq(shot["won_site"], site, "%s %s: the won lights go on this Site" % [corp, site])
			var landmark := CityLandmarks.site_path(corp)
			if landmark != "":
				assert_eq(shot["focus"], "site_landmark", "%s: its Site building stands on the lot" % corp)
				assert_eq(shot["landmark"], corp)
				assert_eq(shot["lot"], inside.floor() + Vector2(0.5, 0.5), "%s %s: on the Site's lot block" % [corp, site])
				var box := BackdropCatalog.landmark_box(cfg, landmark, shot["lot"])
				for size in SIZES:
					var cam := BackdropCatalog.city_shot(cfg, BackdropCatalog.place(corp, false, false, site), lots, size)["camera"] as CityIsoCamera
					var on := _screen_box(cam, box, size)
					var want := Rect2(cfg.backdrop_site_frame.position * size, cfg.backdrop_site_frame.size * size).grow(1.0)
					assert_true(want.encloses(on), "%s %s at %s: the Site building %s fills its frame %s" % [corp, site, size, on, want])
			else:
				assert_eq(shot["focus"], "site", "%s: no Site landmark: the lot's own building" % corp)
				var cam: CityIsoCamera = (shot["camera"] as CityIsoCamera).copy()
				cam.viewport = SIZES[0]
				var at := cam.project(CityIsoCamera.lot_to_world(cfg, inside, cfg.backdrop_site_lift))
				assert_almost_eq(at, SIZES[0] * 0.5, Vector2(1, 1), "%s %s: the Site lot at the view's centre" % [corp, site])


func test_the_close_up_look_keeps_the_rain_and_the_lit_landmarks_per_shot() -> void:
	var cfg := _cfg()
	var hq := BackdropCatalog.city_look(cfg, "hq")
	var site := BackdropCatalog.city_look(cfg, "site_landmark")
	var canyon := BackdropCatalog.city_look(cfg, "compound")
	for look in [hq, site, canyon]:
		assert_true(bool(look["night"]), "night kept: rain and fog stay")
		assert_eq((look["ramp"] as Array).size(), 3, "shadow, mid, lit")
	assert_eq(bool(hq["landmarks_night"]), cfg.backdrop_hq_landmarks_night, "an HQ in its configured look (the pale helix)")
	assert_eq(bool(site["landmarks_night"]), cfg.backdrop_site_landmarks_night, "a Site building lit at night (the cross)")
	assert_true(bool(canyon["landmarks_night"]), "the DISPATCH canyon keeps its neon night")


func test_tier_0_keeps_the_stills_ungraded_and_headless_never_builds_the_city() -> void:
	var cfg := _cfg()
	assert_false(BackdropCatalog.city_mode(cfg, 0, true), "tier 0: the stills")
	assert_true(BackdropCatalog.city_mode(cfg, 1, true), "tier 1: the city")
	assert_false(BackdropCatalog.city_mode(cfg, 2, false), "no renderer: the stills")
	var bd := CombatBackdrop.new()
	add_child_autofree(bd)
	bd.show_place(BackdropCatalog.place(&"solace", true, false))
	assert_null(bd.city, "headless: no city close-up")
	assert_false(bd.on_city())
	assert_false(bool(bd._mat.get_shader_parameter(&"city_grade")), "the stills are never graded (they are the concept)")
	bd.play_won(true)
	assert_eq(bd.won, 1.0, "the won look lands at once (reduce effects / skip)")
	assert_true(bool(bd._mat.get_shader_parameter(&"use_mask")), "the stills keep their won-light mask")
