extends GutTest
## Art pass W7, the city (ART_BIBLE §9, §2 CITY, §8 T0, §12, §13): the Heat band gives the
## city its state; reduce effects stops the life; reduce motion cuts the camera; map mode dims
## the city 40%; the grade per context and the campaign lean; the territory is a hatch and
## tags, not the khaki tint; the silhouette is skyline masses, not flat blocks; the life is
## deterministic; calm zones; the bake cache survives a freed painter. Headless has no GPU:
## these test the logic and the state handed to the shaders; the looks are proven by the
## windowed captures in docs/art_review/W7/.

const SCREEN := Rect2(0, 0, 1280, 720)

var _reduce: bool
var _motion: bool
var _hc: bool


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_motion = Settings.reduce_motion
	_hc = Settings.high_contrast
	Motion.force_live = false
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.simulate = false
	CityBakeCache.shutdown()
	Motion.force_live = false
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if Settings.reduce_motion != _motion:
		Settings.set_reduce_motion(_motion)
	if Settings.high_contrast != _hc:
		Settings.set_high_contrast(_hc)


## A city on screen (1280x720) with its atmosphere, following no campaign.
func _city(net: bool = true) -> NeonCity:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = net
	city.district = &"solace"
	holder.add_child(city)
	city.atmosphere().follow_campaign(false)
	return city


func _push(city: NeonCity) -> void:
	city.atmosphere()._push()


func _vm(city: NeonCity) -> ShaderMaterial:
	return city._view.material as ShaderMaterial


# --- Item 4: the Heat band gives the city its state -------------------------------------------

func test_the_heat_band_from_the_config_gives_the_city_state() -> void:
	var levels := (load(ContentRegistry.CONFIG_PATH) as CampaignConfigData).major_heat_levels()
	assert_eq(levels.size(), 3, "three MAJOR levels: NOTICED, FLAGGED, HUNTED")
	var s := CityState.new()
	for heat in [0, levels[0] - 1, levels[0], levels[1], levels[2], 100]:
		s.set_heat(heat)
		assert_eq(s.band, Palette.heat_band(heat), "band of %d from Palette.heat_band" % heat)
	s.set_heat(levels[0] - 1)
	assert_eq(s.band_name(), "COOL")
	assert_false(s.searchlights())
	s.set_heat(levels[0])
	assert_eq(s.band_name(), "NOTICED")
	assert_true(s.searchlights() and not s.patrols(), "NOTICED: searchlights only")
	s.set_heat(levels[1])
	assert_true(s.patrols() and not s.hunted(), "FLAGGED: patrols and rim flicker")
	s.set_heat(levels[2])
	assert_true(s.hunted(), "HUNTED")


func test_each_heat_band_changes_what_the_city_shows() -> void:
	var levels := (load(ContentRegistry.CONFIG_PATH) as CampaignConfigData).major_heat_levels()
	var city := _city()
	await wait_frames(2)
	var atm := city.atmosphere()
	atm.set_campaign_progress(0.0, &"solace")
	atm.set_heat(0)
	_push(city)
	assert_eq(_vm(city).get_shader_parameter("search_count"), 0, "COOL: no searchlights")
	var calm_rims: int = _vm(city).get_shader_parameter("rim_count")
	var cool_sat: float = atm.grade["saturation"]
	atm.set_heat(levels[0])
	_push(city)
	assert_gt(int(_vm(city).get_shader_parameter("search_count")), 0, "NOTICED: searchlights over the corp's district")
	atm.set_heat(levels[1])
	_push(city)
	assert_gt(int(_vm(city).get_shader_parameter("rim_count")), calm_rims, "FLAGGED: red/blue rim lights on corp buildings")
	assert_eq(int(_vm(city).get_shader_parameter("flicker_from")), calm_rims, "the added lights are the flickering ones")
	assert_lte(float(_vm(city).get_shader_parameter("flicker_hz")), 1.0, "the rim flicker is at most 1 Hz (§9.3)")
	var cfg := CityLookData.shipped()
	var patrol := CityLife.frame(0.0, 7, atm.state, Rect2(0, 0, 1280, 720), cfg, false, [] as Array[Dictionary], PackedVector2Array([Vector2(640, 360)]))
	var patrols := patrol.filter(func(it: Dictionary) -> bool: return it["kind"] == &"drone" and bool(it["patrol"]))
	assert_eq(patrols.size(), cfg.flagged_drones, "FLAGGED: patrol drones out")
	atm.set_heat(levels[2])
	_push(city)
	assert_almost_eq(float(atm.grade["saturation"]), cool_sat * (1.0 - cfg.hunted_desaturate), 0.001, "HUNTED: saturation -25%")
	assert_almost_eq(float(_vm(city).get_shader_parameter("haze_gain")), cfg.hunted_haze_gain, 0.001, "HUNTED: heavier haze")


# --- Item 3 / 7: reduce effects stops the life --------------------------------------------------

func test_reduce_effects_stops_the_life_at_its_static_end_state() -> void:
	var cfg := CityLookData.shipped()
	var s := CityState.new()
	s.set_heat(90)
	var boards: Array[Dictionary] = [{"at": Vector2(100, 100), "corp": &"solace"}, {"at": Vector2(300, 200), "corp": &"meridian"}]
	var patrols := PackedVector2Array([Vector2(640, 360)])
	var live_a := CityLife.frame(1.0, 7, s, SCREEN, cfg, false, boards, patrols)
	var live_b := CityLife.frame(4.0, 7, s, SCREEN, cfg, false, boards, patrols)
	assert_ne(live_a, live_b, "the life moves with time")
	var still_a := CityLife.frame(1.0, 7, s, SCREEN, cfg, true, boards, patrols)
	var still_b := CityLife.frame(123.0, 7, s, SCREEN, cfg, true, boards, patrols)
	assert_eq(still_a, still_b, "under reduce effects the draw list never changes")
	for it: Dictionary in still_a:
		assert_eq(it["kind"], &"billboard", "nothing that moves is drawn (aircraft, drones)")
		assert_eq(int(it["frame"]), 0, "billboards hold their first frame")
	var city := _city()
	await wait_frames(2)
	city.atmosphere().set_campaign_progress(0.0, &"solace")
	city.atmosphere().set_heat(90)
	Settings.set_reduce_effects(true)
	_push(city)
	assert_eq(int(_vm(city).get_shader_parameter("rim_count")), int(_vm(city).get_shader_parameter("flicker_from")), "no rim flicker under reduce effects")
	var t0 := city.atmosphere().life.t
	await wait_frames(5)
	assert_eq(city.atmosphere().life.t, t0, "the life's clock stands still")


# --- Item 7: reduce motion cuts the camera ---------------------------------------------------------

func test_reduce_motion_cuts_the_city_camera_to_its_end_framing() -> void:
	Motion.force_live = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var wf := WireframeBackground.new()
	holder.add_child(wf)
	await wait_frames(3)
	Settings.set_reduce_motion(true)
	var secs := wf.frame_points(PackedVector2Array([Vector2(3, 4), Vector2(12, -6)]), Rect2(100, 100, 800, 500), 1.6, 0.6)
	assert_eq(secs, 0.0, "the fight framing takes no time")
	assert_false(wf.camera_easing(), "nothing is held or eased")
	assert_eq(wf.rig.position, Vector2.ZERO, "the picture is at its end framing")
	wf.hold_camera()
	assert_false(wf.camera_easing(), "hold_camera holds nothing")
	# The title's pan holds its first framing.
	var city := _city(false)
	city.pan = true
	await wait_frames(2)
	city._process(0.5)
	var pos := city.position
	city._process(0.5)
	assert_eq(city._pan_t, 0.0, "the menu pan does not drift")
	assert_eq(city.position, pos, "the city stays put")
	Settings.set_reduce_motion(false)
	city._process(0.5)
	assert_gt(city._pan_t, 0.0, "(and drifts again without reduce motion: %s)" % Motion.camera_moves_allowed())


# --- Item 6: map mode dims the city 40% ------------------------------------------------------------

func test_map_mode_dims_the_city_forty_percent_and_blurs_it() -> void:
	var city := _city()
	await wait_frames(2)
	var atm := city.atmosphere()
	atm.set_map_mode(true)
	_push(city)
	assert_almost_eq(float(atm.grade["map_dim"]), 0.4, 0.0001, "§9.5: dimmed 40%")
	assert_almost_eq(float(_vm(city).get_shader_parameter("g_map_dim")), 0.4, 0.0001, "the composite dims it")
	assert_gt(float(_vm(city).get_shader_parameter("blur_px")), 0.0, "and blurs it slightly")
	var k := CityGrade.brightness(atm.grade)
	assert_almost_eq(city._lights_layer.self_modulate.r, k, 0.0001, "the window lights dim with it")
	assert_almost_eq(atm.life.modulate.r, k, 0.0001, "and the life")
	assert_almost_eq(k, (1.0 - float(atm.grade["dim"])) * 0.6, 0.0001)
	atm.set_map_mode(false)
	_push(city)
	assert_eq(float(_vm(city).get_shader_parameter("g_map_dim")), 0.0, "off: no map dim")
	assert_eq(float(_vm(city).get_shader_parameter("blur_px")), 0.0, "off: no blur")


# --- Item 2: the grade per context and the campaign lean --------------------------------------------

func test_each_context_has_its_grade() -> void:
	var cfg := CityLookData.shipped()
	var s := CityState.new()
	var g := {}
	for c in CityLookData.CONTEXTS:
		s.context = c
		g[c] = CityGrade.params(s, cfg)
	assert_gt(float(g[&"hq"]["warmth"]), 0.0, "HQ warm")
	assert_gt(float(g[&"hq"]["lift"]), 0.0, "and dirty (lifted blacks)")
	assert_lt(float(g[&"net"]["warmth"]), 0.0, "the net cool")
	assert_gt(float(g[&"net"]["contrast"]), float(g[&"title"]["contrast"]), "and high-contrast")
	assert_gt(float(g[&"combat"]["contrast"]), float(g[&"title"]["contrast"]), "combat raises contrast")
	assert_almost_eq(float(g[&"combat"]["dim"]), 0.35, 0.0001, "and dims the city 35%")
	s.context = &"combat"
	assert_almost_eq(float(CityGrade.params(s, cfg, 0.55)["dim"]), 0.0, 0.0001, "a darker veil already set is not darkened twice")
	var warm := CityGrade.apply(Palette.NET_CYAN, g[&"hq"])
	var cool := CityGrade.apply(Palette.NET_CYAN, g[&"net"])
	assert_gt(warm.r / maxf(warm.b, 0.001), cool.r / maxf(cool.b, 0.001), "the HQ grade is warmer than the net's")
	# The screens name the context; the city passes it to its composite.
	var city := _city()
	await wait_frames(2)
	assert_eq(city.atmosphere().state.context, &"net", "a net city starts in the net context")
	city.atmosphere().set_context(&"combat")
	_push(city)
	assert_almost_eq(float(_vm(city).get_shader_parameter("g_contrast")), float(g[&"combat"]["contrast"]), 0.0001)


func test_campaign_progress_leans_the_grade_up_to_twenty_percent_toward_the_corp() -> void:
	var cfg := CityLookData.shipped()
	var s := CityState.new()
	s.corp_id = &"meridian"
	for p in [0.0, 0.5, 1.0, 3.0]:
		s.progress = p
		var g := CityGrade.params(s, cfg)
		assert_almost_eq(float(g["tint_amount"]), clampf(p, 0.0, 1.0) * 0.2, 0.0001, "progress %.1f" % p)
		assert_eq(g["tint"], Palette.CORP_MERIDIAN, "toward the target corp's hue")
	var city := _city()
	await wait_frames(2)
	city.atmosphere().set_campaign_progress(0.5, &"halcyon")
	_push(city)
	assert_almost_eq(float(_vm(city).get_shader_parameter("g_tint_amount")), 0.1, 0.0001)


# --- Item 4: the territory is a hatch and tags, not the khaki tint ---------------------------------

func test_claimed_territory_is_a_hatch_tags_and_haze_light_not_the_khaki_tint() -> void:
	var city := _city()
	await wait_frames(3)
	var hq := NeonCity.hq_of(&"solace") + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
	var claims := PackedVector2Array([hq + Vector2(-9, 3), hq + Vector2(3, -10)])
	city.atmosphere().set_territory(claims)
	_push(city)
	await wait_frames(2)
	var turf := city.atmosphere().turf
	assert_gt(turf.hatched_roofs, 0, "the claimed buildings carry a CELL_TURF hatch (%d)" % turf.hatched_roofs)
	assert_eq(turf.tags_drawn, claims.size() * CityLookData.shipped().tags_per_site, "spray tags on each claimed Site's buildings")
	assert_eq(int(_vm(city).get_shader_parameter("leak_count")), claims.size(), "light leaks into the haze")
	assert_eq(_vm(city).get_shader_parameter("leak_color"), Palette.CELL_TURF)
	var fm := city._front_layer.material as ShaderMaterial
	assert_gt(float(fm.get_shader_parameter("hatch_px")), 0.0, "the lasting wash is a hatch, not a flat fill")
	assert_lt(float(fm.get_shader_parameter("wash_gain")), 1.0, "and turned down")
	assert_lt(NeonCity.INFLUENCE_GROUND_TINT, 0.16, "the ground leans less toward acid (the khaki)")
	var src := FileAccess.get_file_as_string("res://shaders/influence_reveal.gdshader")
	assert_true(src.contains("spread * wash * lines"), "the wash goes through the hatch lines")


# --- Item 5: no flat-block fallback -------------------------------------------------------------------

func test_the_city_waiting_for_its_bake_shows_skyline_masses_not_flat_blocks() -> void:
	CityBakeCache.simulate = true
	var city := _city()
	await BoundedWait.until(get_tree(), func() -> bool: return city.silhouette_done and city.silhouette_roofs > 0, 8.0)
	assert_true(city._sil.visible, "the silhouette layer shows while the bake runs")
	assert_gt(CitySilhouette.last_masses, 20, "masses from the placement (%d)" % CitySilhouette.last_masses)
	assert_gt(CitySilhouette.last_tall, CitySilhouette.last_masses * 0.8, "at building height, not the old 10 px lift")
	assert_gt(CitySilhouette.last_real, 0, "at the placement's real heights")
	assert_gt(CitySilhouette.last_windows, 0, "with a few lit windows")
	assert_eq(city._sil.material, city.atmosphere()._grade_mat, "drawn in the context grade")
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/neon_city.gd")
	assert_false(src.contains("SILHOUETTE_LIFT"), "the flat-block placeholder is gone")


# --- Item 3: the life is deterministic and within T0 ----------------------------------------------

func test_the_life_is_deterministic_and_within_t0() -> void:
	var cfg := CityLookData.shipped()
	var s := CityState.new()
	s.set_heat(60)
	var boards: Array[Dictionary] = [{"at": Vector2(100, 100), "corp": &"orbital"}]
	var patrols := PackedVector2Array([Vector2(500, 300), Vector2(900, 200)])
	for t in [0.0, 2.5, 17.25]:
		var a := CityLife.frame(t, 11, s, SCREEN, cfg, false, boards, patrols)
		var b := CityLife.frame(t, 11, s, SCREEN, cfg, false, boards, patrols)
		assert_eq(a, b, "same time and seed, same draw list (t %.2f)" % t)
	assert_ne(CityLife.frame(3.0, 11, s, SCREEN, cfg, false, boards, patrols), CityLife.frame(3.0, 12, s, SCREEN, cfg, false, boards, patrols), "the seed places it")
	assert_eq(CityLookData.T0_MIN_PERIOD, VfxTier.T0_MIN_PERIOD, "the config's T0 floor is VfxTier's")
	assert_eq(cfg.validate(), PackedStringArray(), "every T0 period >= 3 s, rim flicker <= 1 Hz")
	for p in [cfg.aircraft_blink_period, cfg.drone_period, cfg.billboard_period, cfg.window_period_min, cfg.haze_drift_period, cfg.searchlight_period]:
		assert_gte(p, VfxTier.T0_MIN_PERIOD)
	# Density follows Heat.
	var cool := CityState.new()
	var hot := CityState.new()
	hot.set_heat(90)
	var n_cool := CityLife.frame(0.0, 11, cool, SCREEN, cfg, false, boards, patrols).filter(func(it: Dictionary) -> bool: return it["kind"] == &"aircraft").size()
	var n_hot := CityLife.frame(0.0, 11, hot, SCREEN, cfg, false, boards, patrols).filter(func(it: Dictionary) -> bool: return it["kind"] == &"aircraft").size()
	assert_gt(n_hot, n_cool, "more aircraft as Heat rises")
	# The blinking window lights never toggle faster than T0.
	var city := _city()
	await wait_frames(2)
	assert_gte(float((city._lights_layer.material as ShaderMaterial).get_shader_parameter("min_period")), VfxTier.T0_MIN_PERIOD)


# --- Item 1: the UI calm zones -----------------------------------------------------------------------

func test_calm_zones_dim_the_city_and_stop_its_motion_behind_text() -> void:
	var city := _city()
	await wait_frames(2)
	var atm := city.atmosphere()
	var panel: Control = add_child_autofree(Control.new())
	panel.position = Vector2(100, 100)
	panel.size = Vector2(400, 300)
	atm.set_calm_controls([panel] as Array[Control])
	_push(city)
	assert_eq(int(_vm(city).get_shader_parameter("calm_count")), 1, "the composite knows the zone")
	assert_eq(int((city._lights_layer.material as ShaderMaterial).get_shader_parameter("calm_count")), 1, "the blinking lights hide in it")
	assert_eq(int((city._fx.material as ShaderMaterial).get_shader_parameter("mode")), 1, "the traffic and signs layer hides its motion in it")
	var zone: Vector4 = (_vm(city).get_shader_parameter("calm") as PackedVector4Array)[0]
	assert_true(zone.x < zone.z and zone.y < zone.w, "a real rect")
	var plain: float = atm.grade["calm_dim"]
	Settings.set_high_contrast(true)
	_push(city)
	assert_gt(float(atm.grade["calm_dim"]), plain, "high contrast dims the city further behind panels")
	# Life inside the zone is left out.
	atm.life.boards = [{"at": Vector2(300, 250) - Vector2(city._ox, city._oy), "corp": &"solace"}] as Array[Dictionary]
	atm.life.calm_local = atm.calm_local()
	atm.life.refresh_items()
	assert_eq(atm.life.last_items.filter(func(it: Dictionary) -> bool: return it["kind"] == &"billboard").size(), 0, "a billboard behind the panel is not drawn")


# --- The bake cache: a painter freed mid-bake ---------------------------------------------------------

func test_stopping_a_bake_whose_painter_was_freed_raises_no_error() -> void:
	var painter := NeonCity.new()
	var rec := {"painter": painter, "vp": SubViewport.new()}
	painter.free()
	CityBakeCache._stop(rec)
	assert_false(is_instance_valid(rec["vp"]), "its viewport freed")
	assert_null(CityBakeCache._alive_painter(rec["painter"]), "a freed painter reads as none")
