extends GutTest
## Parity fix S-ARENA (designer group ruling 2026-10-05: combat matches the concept; CMB-01,
## BOSS-03, BACKDROP-01, BACKDROP-02, MOTION-07): the combat backdrop's city close-up keeps the
## concept's lit city once it settles (no drop to near black), the HUD and the wheels keep their
## contrast over it, every corporation's HQ landmark stands whole in the frame for a boss fight
## and a Site fight frames its own Site's building as the subject with the HQ ahead (round 2:
## the concept's low angle, no bare plane or blank lots in the frame).
##
## The settled close-up is measured on fixtures: `tests/fixtures/arena_backdrop/<shot>.png`,
## point samples (256x144) of the windowed hq_run_lab frame of each shot once settled (the
## backdrop as the screen shows it: grade, subject focus and bands, no HUD), recaptured with
## the lab when the look changes (DECISIONS "Parity fix — combat backdrop, round 2").

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


## Mean relative luminance of image `img` (sRGB pixels) over the rows between the top bar's
## band and the hand's (the shader's top_band / bottom_band).
func _mid_luma(img: Image, step: int) -> float:
	var h := img.get_height()
	var y0 := int(h * 0.1)
	var y1 := int(h * 0.76)
	var total := 0.0
	var n := 0
	for y in range(y0, y1, step):
		for x in range(0, img.get_width(), step):
			total += Palette.luminance(img.get_pixel(x, y))
			n += 1
	return total / maxf(1.0, float(n))


func _fixture(shot: String) -> Image:
	return Image.load_from_file(ProjectSettings.globalize_path(FIXTURES + shot + ".png"))


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
		var l := _mid_luma(img, 1)
		assert_between(l, band.x, band.y, "%s: the settled close-up keeps the concept's light (%.3f)" % [shot, l])


func test_the_grade_lifts_the_linear_close_up_into_the_band() -> void:
	# MOTION-07: the close-up's texture reaches the shader as linear values; shown as they are
	# its mid-tones sit ~4x down. The grade lifts a dark mid-tone several times over (hue kept).
	var cfg := _cfg()
	for v in [0.03, 0.06, 0.1]:
		var raw := Color(v, v * 1.05, v * 1.2)
		var g := CombatBackdrop.graded(cfg, raw)
		assert_gt(Palette.luminance(g), Palette.luminance(raw) * 3.0, "a dark mid-tone %.2f is lifted" % v)
		assert_lt(Palette.luminance(g), 0.6, "but not blown out")


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
		var mean_l := _mid_luma(img, 1)
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


## Every Site of every corporation, with its layout lots.
func _all_sites() -> Array:
	var out := []
	for corp in CORPS:
		var cd := RunManager.lookup().get_content(corp) as CorporationData
		var lots := CityLayout.site_points(cd)
		var ids: Array = lots.keys()
		ids.sort()
		for site: StringName in ids:
			out.append([corp, site, lots])
	return out


func test_site_fights_frame_the_fought_sites_own_lot() -> void:
	# Designer round 2: each Site fight frames its own Site's lot (never moved, no repeated
	# landmark); the corp's Site landmark stands only on the Site that carries it.
	var cfg := _cfg()
	for row in _all_sites():
		var corp: StringName = row[0]
		var site: StringName = row[1]
		var lots: Dictionary = row[2]
		var shot := BackdropCatalog.city_shot(cfg, BackdropCatalog.place(corp, false, false, site), lots, SIZES[0])
		assert_eq(shot["focus"], "site", "%s %s: a Site shot" % [corp, site])
		assert_eq(shot["won_site"], site, "%s %s: the won lights go on this Site" % [corp, site])
		var own := CityLandmarks.site_of(cfg, corp) == site and CityLandmarks.site_path(corp) != ""
		assert_eq(shot.has("landmark"), own, "%s %s: the Site landmark only on its own Site" % [corp, site])
		var want: Vector2 = CityLandmarks.site_lot(cfg, corp, lots) if own else lots[site]
		assert_eq(shot["lot"], want, "%s %s: the fought Site's own lot, not moved" % [corp, site])


func test_the_site_building_is_the_large_subject_with_the_hq_behind() -> void:
	var cfg := _cfg()
	# Concept-derived share of the view the subject takes (its larger of width and height share):
	# site_solace_night.jpg's clinic spans 0.38 x 0.37; the range runs from the configured floor to 0.6.
	var most := 0.6
	for row in _all_sites():
		var corp: StringName = row[0]
		var site: StringName = row[1]
		for size in SIZES:
			var shot := BackdropCatalog.city_shot(cfg, BackdropCatalog.place(corp, false, false, site), row[2], size)
			var cam: CityIsoCamera = shot["camera"]
			var on := _screen_box(cam, shot["subject"], size)
			var share := maxf(on.size.x / size.x, on.size.y / size.y)
			assert_between(share, cfg.backdrop_site_subject_min - 0.02, most, "%s %s at %s: the subject's share of the width (%.2f)" % [corp, site, size, share])
			var frame := Rect2(cfg.backdrop_site_frame.position * size, cfg.backdrop_site_frame.size * size)
			assert_true(frame.grow(size.x * 0.05).has_point(on.get_center()), "%s %s: the subject in its frame" % [corp, site])
			# The camera looks from the Site toward its HQ (one of the city's diagonal views).
			var hq: AABB = shot["hq_box"]
			var f := Vector2(cos(deg_to_rad(cam.yaw_deg)), -sin(deg_to_rad(cam.yaw_deg)))
			var to_hq := Vector2(hq.get_center().x, hq.get_center().z) - Vector2((shot["subject"] as AABB).get_center().x, (shot["subject"] as AABB).get_center().z)
			assert_gt(f.dot(to_hq.normalized()), 0.0, "%s %s: the HQ lies ahead, in the back of the shot" % [corp, site])
			assert_true(is_equal_approx(fposmod(cam.yaw_deg - cfg.yaw_deg, 90.0), 0.0) or is_equal_approx(fposmod(cam.yaw_deg - cfg.yaw_deg, 90.0), 90.0),
				"%s %s: one of the city's own diagonal views" % [corp, site])
			assert_almost_eq(cam.pitch_deg, cfg.backdrop_site_pitch_deg, 0.001)
	assert_between(cfg.backdrop_site_pitch_deg, 22.0, 30.0, "the concept's low angle (designer: 22-30)")
	assert_between(cfg.backdrop_hq_pitch_deg, 22.0, 30.0, "the concept's low angle for the boss view too")


func test_no_empty_lot_shows_in_the_frame() -> void:
	# Every ground point of the frame above the hand lands on city: inside city_rect, or in a
	# chunk the close-up records past its edge (BackdropCatalog.extension_keys).
	var cfg := _cfg()
	var shots := []
	for row in _all_sites():
		shots.append([BackdropCatalog.place(row[0], false, false, row[1]), row[2]])
	for corp in CORPS:
		shots.append([BackdropCatalog.place(corp, true, false), {}])
	var rect := Rect2(cfg.city_rect).grow(-cfg.backdrop_site_edge_margin)
	for s in shots:
		var shot := BackdropCatalog.city_shot(cfg, s[0], s[1], SIZES[0])
		var cam: CityIsoCamera = (shot["camera"] as CityIsoCamera).copy()
		cam.viewport = SIZES[0]
		var extra := BackdropCatalog.extension_keys(cfg, shot["lot"], {})
		var have := {}
		for k in extra:
			have[k] = true
		var bad := 0
		for j in 6:
			for i in 9:
				var uv := Vector2(0.06 + 0.11 * i, 0.12 + 0.12 * j)
				var lot := CityIsoCamera.world_to_lot(cfg, cam.unproject(uv * SIZES[0]))
				var key := Vector2i(floori(lot.x / cfg.chunk_lots), floori(lot.y / cfg.chunk_lots))
				if not rect.has_point(lot) and not have.has(key):
					bad += 1
		assert_eq(bad, 0, "%s: no bare plane past the city in the frame" % str(s[0]))


func test_landmarks_clear_only_the_lots_they_stand_on() -> void:
	# The blank lots (designer round 2): a landmark's whole ground box used to clear the city's
	# buildings; now only its footprint does (not Meridian's open yard corners, not the ground
	# under Halcyon's eye beam).
	var cfg := _cfg()
	for corp in [&"meridian", &"halcyon"]:
		var path := BackdropCatalog.hq_landmark_path(corp)
		var node := (load(path) as PackedScene).instantiate() as Node3D
		var lots := CityView3D.footprint_lots(node, cfg)
		var box := CityView3D._ground_box(node)
		node.free()
		if lots.is_empty():
			pending("%s: no mesh arrays headless" % corp)
			continue
		var area := (box.size.x / cfg.lot_bu) * (box.size.y / cfg.lot_bu)
		assert_lt(float(lots.size()), area * 0.9, "%s: the footprint is less than its box (%d of %.0f lots)" % [corp, lots.size(), area])
		assert_gt(lots.size(), 4, "%s: it still clears where it stands" % corp)
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
