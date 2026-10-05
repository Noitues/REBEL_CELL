extends GutTest
## Animation pass ANIM-R2 (the second fix batch), city, maps and transitions: a map screen
## draws its nodes and labels on its first frame (the baked city's placement answers at once;
## the image fades in when its bake lands), a bake is asked for only once the camera holds
## still and waits on a running one that will cover it, a partial stand-in never shows,
## the jack blocks input before the scene sees it, the bake cache frees everything it holds,
## the Heat banner fits its poster, and the raid playout's step skip takes the one press
## rule. Headless has no renderer: `CityBakeCache.simulate` makes the cities take the baked
## path with nothing built (a test lands a bake with `store`).

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
## Bound on a threaded test bake: seconds of game time and at least this many frames (the
## old frame-only bound).
const BAKE_WAIT_LIMIT := 20.0
const BAKE_WAIT_FRAMES := 600

var _reduce: bool
var _scale: float


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r2_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.simulate = false
	CityBakeCache.shutdown()
	Motion.force_live = false
	Motion.use_config(null)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Fx._set_jacking(false)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _placed_nodes(overlay: CityMapOverlay) -> int:
	var n := 0
	for d: Dictionary in overlay.nodes:
		if overlay.icon_at(d["id"]).x != INF:
			n += 1
	return n


# --- R1: a map is never empty -----------------------------------------------------------------

func test_the_grid_draws_its_nodes_before_any_bake_lands() -> void:
	CityBakeCache.simulate = true
	var hq: Control = _scene(HQ)
	await _frames(1)
	hq.new_campaign(1)
	hq.show_grid()
	await _frames(1)
	var city: NeonCity = hq.wireframe.city
	assert_true(city.is_baked(), "the city takes the baked path")
	# ART-5 5a: the Grid is the unified 3D city: no bake, it covers its view at once.
	assert_true(city.city3d and city.view_covered(), "the 3D city covers the Grid at once")
	var overlay: CityMapOverlay = hq.city_overlay
	assert_eq(_placed_nodes(overlay), overlay.nodes.size(), "every node is placed on the first frame")
	assert_false(overlay.label_rects().is_empty(), "and the labels")
	assert_true(city.camera_settled(), "the fit's passes ran under the placement")
	assert_true(hq.arrival_ready(), "a jack lands on it without waiting for the image")


func test_the_route_and_the_raid_setup_draw_their_nodes_before_any_bake() -> void:
	CityBakeCache.simulate = true
	var nr: Control = _scene(NETRUN)
	await _frames(1)
	nr.new_campaign(1)
	nr.start_run(1)
	await _frames(1)
	assert_eq(_placed_nodes(nr.city_overlay), nr.city_overlay.nodes.size(), "route: every node on its first frame")
	assert_false(nr.background.city.view_covered(), "no bake has landed")
	assert_true(nr.arrival_ready(), "the jack in lands on it")
	var hq: Control = _scene(HQ)
	await _frames(1)
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 100
	var first: StringName = RunManager.corporation.city_grid.get_site(c.grid.home_site_id).links[0]
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	assert_false(RunManager.pending_raid().is_empty(), "the claim brings a raid")
	hq.show_raid()
	await _frames(1)
	assert_eq(_placed_nodes(hq.city_overlay), hq.city_overlay.nodes.size(), "raid setup: every node on its first frame")


func test_the_placement_answers_before_the_image_and_keeps_when_it_lands() -> void:
	CityBakeCache.simulate = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var bg := WireframeBackground.new()
	holder.add_child(bg)
	RunManager.new_campaign(1)
	bg.set_district(RunManager.campaign.corporation_id)
	var overlay := CityMapOverlay.new(bg.city)
	bg.city.add_child(overlay)
	var g := CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, [])
	overlay.set_graph(g["nodes"], g["edges"])
	await _frames(2)
	var city := bg.city
	var id: StringName = g["nodes"][0]["id"]
	var before := overlay.icon_at(id)
	assert_ne(before.x, INF, "placed without an image")
	assert_eq(city.bake_fade, 0.0, "the sky shows (nothing fades yet)")
	# Streets come from the placement too (the baked city had none: routes cut blocks).
	var streets := 0
	for i in range(-6, 6):
		if city.is_street(i, 0):
			streets += 1
	assert_gt(streets, 0, "the baked city knows its streets")
	# The image lands.
	var look := city.look_key()
	var region := city.bake_region()
	var img := Image.create(8, 8, false, Image.FORMAT_RGBA8)
	CityBakeCache.store(look + "@" + var_to_str(Rect2i(region)), {"look": look, "region": region, "texture": ImageTexture.create_from_image(img), "scale": 1.0,
		"roofs": {}, "beacons": [] as Array[Dictionary], "lights": [] as Array[Dictionary], "trails": [] as Array[Dictionary], "signs": [] as Array[Dictionary]})
	await _frames(2)
	assert_true(city.view_covered(), "the image covers the view")
	assert_eq(city.bake_fade, 1.0, "headless: faded in at once (the end state)")
	assert_eq(overlay.icon_at(id), before, "the nodes stay where they were")


func test_a_bake_is_asked_for_once_the_camera_holds_still() -> void:
	CityBakeCache.simulate = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	# A fit moves the camera every frame for a few frames: no bake is asked for meanwhile.
	for k in 5:
		city.focus_grid = Vector2(k * 7, 3)
		city.refresh()
		await _frames(1)
		assert_true(CityBakeCache._pending.is_empty(), "frame %d: the camera still moves, no bake" % k)
	await _frames(NeonCity.BAKE_SETTLE_FRAMES + 2)
	assert_eq(CityBakeCache._pending.size(), 1, "once it holds still, one bake is asked for")
	# A move inside the region the running bake covers waits on it (no second bake).
	city.focus_grid = Vector2(4 * 7, 3) + Vector2(0.5, 0)
	city.refresh()
	await _frames(NeonCity.BAKE_SETTLE_FRAMES + 2)
	assert_eq(CityBakeCache._pending.size(), 1, "a view the running bake will cover waits on it")


func test_a_partial_stand_in_never_shows() -> void:
	CityBakeCache.simulate = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	await _frames(1)
	city._camera()
	var look := city.look_key()
	var view := city.view_rect()
	var tex := ImageTexture.create_from_image(Image.create(4, 4, false, Image.FORMAT_RGBA8))
	# A strip over a quarter of the view: the sky reads better.
	CityBakeCache.store("strip", {"look": look, "region": Rect2(view.position, Vector2(view.size.x, view.size.y * 0.25)), "texture": tex})
	assert_eq(city._stand_in(look, view), "", "a strip is no stand-in")
	CityBakeCache.store("most", {"look": look, "region": Rect2(view.position, Vector2(view.size.x, view.size.y * 0.95)), "texture": tex})
	assert_eq(city._stand_in(look, view), "most", "nearly all of the view is")


# --- R3: the jack blocks input before the scene sees it -------------------------------------------

var _presses: int = 0


func _count(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		_presses += 1


func test_the_jack_blocks_input_before_the_scene_sees_it() -> void:
	await _frames(1)
	var gate: JackInputGate = Fx.input_gate
	assert_not_null(gate, "the gate is up")
	assert_true(gate.is_inside_tree(), "under the root")
	var scene := InputProbe.new()
	scene.seen.connect(_count)
	get_tree().root.add_child(scene)
	await _frames(1)
	_presses = 0
	var key := InputEventKey.new()
	key.keycode = KEY_SPACE
	key.physical_keycode = KEY_SPACE
	key.pressed = true
	get_viewport().push_input(key)
	assert_eq(_presses, 1, "no jack: the scene's own _input sees the press")
	Fx._set_jacking(true)
	# The arriving scene is added under the root after the gate: the gate moves behind it.
	var arriving := InputProbe.new()
	arriving.seen.connect(_count)
	get_tree().root.add_child(arriving)
	await _frames(1)
	_presses = 0
	var stopped := gate.stopped
	get_viewport().push_input(key)
	var enter := InputEventKey.new()
	enter.keycode = KEY_ENTER
	enter.physical_keycode = KEY_ENTER
	enter.pressed = true
	get_viewport().push_input(enter)
	assert_eq(_presses, 0, "during the jack no scene handler sees Space or Enter")
	assert_eq(gate.stopped - stopped, 2, "the gate stopped both")
	Fx._set_jacking(false)
	get_viewport().push_input(key)
	assert_eq(_presses, 2, "after the jack presses reach the scenes again")
	scene.queue_free()
	arriving.queue_free()


# --- R10 / R11: the bake cache lets go of everything --------------------------------------------

func test_clear_frees_every_baked_texture() -> void:
	var tex := ImageTexture.create_from_image(Image.create(4, 4, false, Image.FORMAT_RGBA8))
	var ref: WeakRef = weakref(tex)
	CityBakeCache.store("a", {"look": "x", "region": Rect2(0, 0, 10, 10), "texture": tex})
	tex = null
	assert_not_null(ref.get_ref(), "the cache holds it")
	CityBakeCache.clear()
	assert_null(ref.get_ref(), "clear() lets it go")
	assert_eq(CityBakeCache.memory_bytes(), 0)


func test_shutdown_stops_a_running_bake_and_frees_its_painter() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	var painter := city.make_painter(Rect2(-1200, -800, 2400, 1600), 1.0)
	var ref: WeakRef = weakref(painter)
	CityBakeCache.request("running", city.look_key(), painter, city)
	CityBakeCache.request("queued", city.look_key(), city.make_painter(Rect2(0, 0, 256, 256), 1.0), city)
	assert_eq(CityBakeCache.busy(), 2, "one builds, one waits for the slot")
	assert_eq(CityBakeCache._building, 1, "one build at a time (R11)")
	CityBakeCache.shutdown()
	assert_null(ref.get_ref(), "the running bake's painter is freed")
	assert_eq(CityBakeCache.busy(), 0, "nothing runs or waits")
	assert_true(CityBakeCache._pending.is_empty())
	await _frames(3)
	assert_false(CityBakeCache.has("running"), "a stopped bake never lands")


func test_a_painter_copies_the_influence() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	var city := NeonCity.new()
	holder.add_child(city)
	city.bind_campaign(RunManager.campaign, RunManager.corporation)
	assert_false(city.influence.is_empty())
	var painter := city.make_painter(Rect2(0, 0, 64, 64), 1.0)
	assert_true(painter.influence == city.influence, "the same values")
	assert_false(is_same(painter.influence, city.influence), "not the same dictionary (its workers read it)")
	painter.free()


func test_a_threaded_bake_builds_in_slices_and_lets_the_slot_go() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	CityBakeCache.request("small", city.look_key(), city.make_painter(Rect2(0, 0, 256, 192), 1.0), city)
	var rec: Dictionary = CityBakeCache._live.get("small", {})
	assert_false(rec.is_empty(), "the bake runs")
	# A worker thread's pace, bounded in game time as well as frames (Test suite: bounded
	# waits: 600 fast frames can pass before a loaded worker is done).
	await BoundedWait.until(get_tree(), func() -> bool: return rec.has("vp") and CityBakeCache._building == 0, BAKE_WAIT_LIMIT, BAKE_WAIT_FRAMES)
	# (The dummy renderer never draws a frame, so a headless bake stops at its readback.)
	assert_true(rec.has("vp"), "the sliced build ran through and its chunks went in")
	assert_eq(CityBakeCache._building, 0, "the build slot is free for the next bake")
	var painter: NeonCity = rec["painter"]
	assert_true(painter._slices.is_empty(), "the slices are freed")
	assert_true(painter._parts.is_empty(), "the geometry was handed over")


## Waits a frame at a time until `cond` holds or `limit` seconds of game time (and
## BoundedWait's frame floor) have passed (Test suite: bounded waits: was the wall clock).
func _until(cond: Callable, limit: float) -> void:
	await BoundedWait.until(get_tree(), cond, limit)


func _live() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
		Fx.apply_settings()


func _hq_raid() -> Control:
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 100
	var grid_data := RunManager.corporation.city_grid
	var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
	return hq


# --- R5: the jack names where it connects --------------------------------------------------------

func test_the_jack_says_where_it_connects_while_the_screen_builds() -> void:
	await _frames(1)
	_live()
	var switched := [false]
	Fx.jack_in(func() -> void: switched[0] = true, -1.0, "Test Site")
	# Bounded by the jack's own seconds in game time, not 240 frames (Test suite: bounded
	# waits: fast frames could end a frame-count wait before the push did).
	var jack_limit := BoundedWait.motion_limit([&"jack_in", &"jack_arrive", Fx.ARRIVAL_WAIT_MOTION, Fx.CONNECT_MOTION])
	var saw := await BoundedWait.until(get_tree(), Fx.connecting, jack_limit)
	var words := Fx.connect_words() if saw else ""  # ANIM-R6 B13: the name has a line of its own
	assert_true(switched[0], "the switch happened under the cover")
	assert_true(saw, "CONNECTING shows on the opaque cover")
	assert_string_contains(words, "TEST SITE", "naming the place")
	await BoundedWait.until(get_tree(), func() -> bool: return not Fx.transitioning(), jack_limit)
	assert_false(Fx.connecting(), "and goes with the cover")
	assert_eq(RunManager.jack_destination(), tr("the net"), "no run: the net")


# --- R6: raid playout readability and the press rule ---------------------------------------------

func test_a_press_skips_a_playout_step_but_its_buttons_stay_clickable() -> void:
	var probe := InputProbe.new()
	add_child_autofree(probe)
	var seen := [0]
	probe.seen.connect(func(e: InputEvent) -> void:
		if MotionSkip.is_press(e):
			seen[0] += 1)
	var grid := GridFixture.chain_grid([&"c1", &"c2"])
	var c := GridFixture.campaign(grid, {&"c1": &"firewall_relay", &"c2": &"relay"})
	GridFixture.deploy(c, &"c1", &"turret")
	var raid := GridFixture.raid(&"two", [&"collector", &"enforcer"])
	var result := RaidResolver.resolve(c, grid, raid, GridFixture.lookup(), CombatFixture.config())
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var panel := RaidPlayoutPanel.new()
	holder.add_child(panel)
	_live()
	panel.play(result.events, false)
	await _frames(1)
	panel._clock = 0.0
	var next := panel._next_at
	var key := InputEventKey.new()
	key.keycode = KEY_X
	key.physical_keycode = KEY_X
	key.pressed = true
	get_viewport().push_input(key)
	assert_almost_eq(panel._clock, next, 0.0001, "a press (any key, the one rule) ends the step's motion")
	assert_eq(seen[0], 0, "and is consumed: nothing behind the playout sees it")
	var echo := key.duplicate() as InputEventKey
	echo.echo = true
	panel._clock = 0.0
	get_viewport().push_input(echo)
	assert_eq(panel._clock, 0.0, "a held key's repeat is no press")
	# A click on its own Skip button is the button's, not a step skip.
	await _frames(1)
	var skip := panel.find_child("Skip", true, false) as Button
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = skip.get_global_rect().get_center()
	click.global_position = click.position
	assert_true(panel._for_own_button(click), "a click on Skip is Skip's")


func test_the_raid_ends_with_staggered_outcomes_and_a_result_banner() -> void:
	var hq := _hq_raid()
	await _frames()
	hq.show_raid()
	await _frames(2)
	var c := RunManager.campaign
	var events := RunManager.fight_raid()
	# Headless the screen's playout is instant and moves on to the summary; play it on the
	# setup's map here to read its end state.
	var panel := RaidPlayoutPanel.new(hq.city_overlay)
	add_child_autofree(panel)
	panel.attach_fx(c.last_raid, c.grid.home_site_id, c.grid.home_max_integrity, Palette.CORP_SOLACE)
	panel.play(events, true)
	var fx: RaidFxLayer = panel.fx
	assert_not_null(fx)
	var r: Dictionary = c.last_raid
	var lost := int(r.get("home_before", 0)) - int(r.get("home_after", 0))
	var want := (CityMapOverlay.tr_word(RaidFxLayer.BANNER_HOME) % ("-%d" % lost)) if lost > 0 else CityMapOverlay.tr_word(RaidFxLayer.BANNER_HOLDS)
	assert_eq(fx.banner_text(), want, "the result banner says what home lost")
	var starts: Array[float] = []
	for id in fx._stamps:
		starts.append(float(fx._stamps[id]["t0"]))
	starts.sort()
	# ANIM-R3 B5: every node but home stamps its outcome (home's verdict is the banner).
	assert_gt(starts.size(), 0, "every node stamps its outcome")
	assert_eq(fx.stamp_word(c.grid.home_site_id), "", "home has no stamp of its own")
	for i in range(1, starts.size()):
		assert_gt(starts[i], starts[i - 1], "the outcomes stamp one after another")
	assert_eq(RaidFxLayer.TOKEN_SCALE, 3.0, "threat tokens read at map scale")


func test_an_asset_drop_waits_for_the_camera_then_lands_with_its_name() -> void:
	var hq := _hq_raid()
	await _frames()
	hq.show_raid()
	await _frames(4)
	_live()
	var target: StringName = hq.selected_site
	var moving := [true]
	hq.city_overlay.drop_asset(target, func() -> bool: return not moving[0], "TURRET")
	assert_true(hq.city_overlay.drop_waiting(), "it waits while the camera pans")
	assert_eq(hq.city_overlay.drop_t, 0.0)
	moving[0] = false
	await _frames(2)
	assert_false(hq.city_overlay.drop_waiting(), "then drops")
	await _until(func() -> bool: return hq.city_overlay.drop_t == 1.0 and hq.city_overlay.drop_stamp_t == 1.0, BoundedWait.motion_limit([&"asset_drop", &"asset_drop_stamp"]))
	assert_eq(hq.city_overlay.drop_t, 1.0, "it lands")
	assert_eq(hq.city_overlay.drop_stamp_t, 1.0, "and stamps")
	assert_eq(String(hq.city_overlay._drop.get("label", "")), "TURRET", "its name stays under it")


# --- R7: the district keeps its tint -----------------------------------------------------------------

func test_a_territory_change_leaves_a_lasting_tint() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var before := CityInfluence.of(c, RunManager.corporation)
	var first: StringName = RunManager.corporation.city_grid.get_site(c.grid.home_site_id).links[0]
	c.schematics = 100
	var hq := _scene(HQ)
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	holder.add_child(city)
	await _frames(1)
	city.set_influence(CityInfluence.of(c, RunManager.corporation))
	city._start_spread(before)
	assert_gt(city.lasting_tint().a, 0.0, "headless (no spread plays): the end state is the tint")
	assert_almost_eq(city.lasting_tint().a, Motion.amplitude(&"influence_tint"), 0.001, "at influence_tint's strength")


# --- R8: the Heat crossing in order, the banner fits ------------------------------------------------

func test_a_multi_band_rise_rolls_to_each_threshold_and_stamps_a_banner_each() -> void:
	RunManager.new_campaign(1)
	HeatPoster._seen_heat.clear()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var poster := HeatPoster.new(true)
	holder.add_child(poster)
	var marks: Array[int] = [25, 50, 75]
	poster.set_heat(20, 100, marks)
	await _frames()
	_live()
	var pulses := Fx.heat_pulses
	poster.set_heat(60, 100, marks)
	assert_eq(poster.banner_alpha, 0.0, "nothing before the number reaches 25")
	assert_eq(Fx.heat_pulses, pulses, "no distortion before the crossing")
	# Waits for each stamp (bounded) rather than a fixed number_roll + 0.08 s: under a loaded
	# parallel run one frame outlasted that slack (DECISIONS "Animation pass - bake crash").
	await _until(func() -> bool: return Fx.heat_pulses > pulses, Motion.seconds(&"number_roll") * 4.0)
	assert_string_contains(poster.banner_text(), "25", "the first banner names 25")
	assert_eq(Fx.heat_pulses, pulses + 1, "one distortion at 25")
	assert_false(Fx.distortion.get_rect().encloses(Rect2(Vector2.ZERO, get_viewport().get_visible_rect().size)), "round the poster, not the screen")
	await _until(func() -> bool: return Fx.heat_pulses > pulses + 1, Motion.seconds(&"number_roll") * 4.0)
	assert_string_contains(poster.banner_text(), "50", "then one for 50")
	assert_eq(Fx.heat_pulses, pulses + 2)
	await _until(func() -> bool: return is_equal_approx(poster.shown_heat, 60.0) and not Fx.distortion.visible,
		(Motion.seconds(&"number_roll") + Motion.seconds(&"heat_pulse")) * 4.0)
	assert_almost_eq(poster.shown_heat, 60.0, 0.01, "the number ends on the Heat")
	assert_false(Fx.distortion.visible, "the distortion is brief")
	assert_true(Motion.seconds(&"heat_pulse") <= 0.3, "at most 0.3 s")
	# A drop across a band re-stamps the band word only.
	var banner := poster.banner_alpha
	poster.set_heat(20, 100, marks)
	assert_gt(poster.stamp_scale, 1.0, "the band word stamps again")
	assert_eq(Fx.heat_pulses, pulses + 2, "no distortion going down")
	assert_true(poster.banner_alpha <= banner, "and no new banner")


func test_the_heat_banner_fits_its_poster_at_every_text_size_and_a_long_translation() -> void:
	RunManager.new_campaign(1)
	var tr_long := Translation.new()
	tr_long.locale = "xx"
	tr_long.add_message("hunted", "activement recherché")
	tr_long.add_message("HEAT %d - %s", "CHALEUR %d - %s")
	TranslationServer.add_translation(tr_long)
	var locale := TranslationServer.get_locale()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		for loc in [locale, "xx"]:
			TranslationServer.set_locale(loc)
			var poster := HeatPoster.new(true)
			holder.add_child(poster)
			poster.size = poster.custom_minimum_size
			poster.heat = 80
			poster._banner_at = 75
			var fs := poster.banner_font_size()
			# ANIM-R3 B7: the banner wraps to two lines before it shrinks under its readable floor.
			var span := HeatPoster.banner_span(Palette.display(), poster.banner_lines()["lines"], fs)
			assert_true(span <= poster.size.x - HeatPoster.BANNER_MARGIN * 2.0 + 0.5, "%s at %.1f (%s): %.0f px in %.0f" % [poster.banner_text(), scale, loc, span, poster.size.x])
			poster.queue_free()
	TranslationServer.set_locale(locale)
	TranslationServer.remove_translation(tr_long)


# --- R9: the label layout is worked out once per change -----------------------------------------------

func test_the_label_layout_is_cached_until_something_changes() -> void:
	var hq: Control = _scene(HQ)
	await _frames(1)
	hq.new_campaign(1)
	hq.show_grid()
	await _frames(3)
	var overlay: CityMapOverlay = hq.city_overlay
	var a := overlay._layout_labels()
	assert_true(is_same(a, overlay._layout_labels()), "the same layout while nothing changed")
	overlay.hover_id = overlay.nodes[0]["id"]
	assert_false(is_same(a, overlay._layout_labels()), "a new layout when the focus moves")


# --- R12: equal route choices say so ------------------------------------------------------------------

func test_equal_route_choices_say_they_are_the_same() -> void:
	var nr: Control = _scene(NETRUN)
	await _frames(1)
	nr.new_campaign(1)
	nr.start_run(1)
	await _frames(2)
	var s := RunManager.netrun
	var twins: Dictionary = nr.choice_twins(s)
	assert_false(twins.is_empty(), "seed 1's first choices are three plain fights")
	var open := s.available_nodes()
	for i in open.size():
		var b := nr.find_child("Node%d" % (i + 1), true, false) as Button
		if twins.has(open[i]):
			assert_string_contains(b.text, tr(nr.TWIN_WORDS) % (int(twins[open[i]]) + 1), "a twin choice says which it equals (ANIM-R6 B14: the same road)")
		else:
			assert_false(b.text.contains("(same road"), "a choice unlike the others says nothing")
	for n: Dictionary in nr.city_overlay.nodes:
		if twins.has(n["id"]):
			assert_string_contains(String(n["label"]), "(same road", "and so does its map label")


# --- R13: big text -------------------------------------------------------------------------------------

func test_big_text_raid_key_folds_and_the_crew_orders_show() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var hq := _hq_raid()
	await _frames()
	hq.show_raid()
	await _frames(6)
	assert_true(hq.raid_legend_is_strip(), "at TEXT_SCALE_MAX the raid key is the folding strip")
	assert_true(hq.raid_legend.foldable() and hq.raid_legend.is_folded(), "folded to its MAP KEY line")
	hq.show_hq()
	await _frames(6)
	var screen := hq.get_global_rect()
	var found := 0
	for b in hq.find_children("Loadout", "Button", true, false):
		found += 1
		assert_true(screen.encloses((b as Button).get_global_rect()), "a dossier's Loadout is on the first screen at TEXT_SCALE_MAX")
	assert_gt(found, 0, "the dossiers have their Loadout")
