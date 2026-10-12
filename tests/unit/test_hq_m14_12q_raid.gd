extends GutTest
## M14 12Q-RAID (docs/handoff/m14_12q/qa_matrix_audit.md; DECISIONS "M14 12Q-RAID"): the raid
## pages at big text and the colour-blind setting. The top bar's stat tags keep one row at 1.6 /
## 2.0 (never under the 1.0 size; past that the names fold, two rows last); the raid report's
## BACK TO THE GRID is whole on screen and its paper starts under the top bar; START DEFENSE peels
## under the playout's page; the Heat note leaves a spot a later page covers; with the
## colour-blind setting on the hostile routes carry hazard ticks and their marks a reticle; the
## Grid's drag demo carries an operative; the 3D city shows its current look once built.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const BIG: Array[float] = [1.6, 2.0]
const MARKS: Array[int] = [25, 50, 75]
const CITY_CONFIG := preload("res://content/config/city_config.tres")
## The stat tags of the raid pages (HudStats items: name, value, suffix).
const TAGS: Array = [["SCHEMATICS", "100", ""], ["HOME", "50", "/50"], ["EXPLOITS", "0", "/3"], ["RAIDS", "1", ""], ["ICE", "0", ""], ["CREW", "2", ""]]

var _scale: float = 1.0
var _reduce: bool = false
var _cb: StringName = &"off"


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects
	_cb = Settings.colorblind_mode


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_hq_m14_12q_raid"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if Settings.colorblind_mode != _cb:
		Settings.set_colorblind_mode(_cb)
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


func _close(scene: Control) -> void:
	if is_instance_valid(scene) and scene.get_parent() != null:
		scene.get_parent().queue_free()
	await _frames(2)


func _raid_campaign(corp: StringName = &"") -> void:
	if corp == &"":
		RunManager.new_campaign(7)
	else:
		for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
			RunManager.profile.add_unlock(u)
		for id in ["solace", "meridian", "halcyon", "orbital"]:
			RunManager.profile.best_ice_by_corp[id] = 10
		RunManager.new_campaign(7, corp)
	var c := RunManager.campaign
	var g := RunManager.corporation.city_grid
	var first: StringName = g.get_site(g.home_site_id).links[0]
	DemoSetup.set_schematics(c, 100)
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	var armory: Array[StringName] = [&"turret", &"ice_lock", &"decoy"]
	DemoSetup.set_armory(c, armory)
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)


func _one_row(st: HudStats, what: String) -> void:
	assert_eq(st.rows, 1, "%s: the stat tags keep one row" % what)
	assert_true(st.tag_scale >= HudStats.one_row_floor(Settings.text_scale) - 0.01, "%s: never under the 1.0 size past 1.0 (%.2f)" % [what, st.tag_scale])
	for r in st.tag_rects():
		assert_true(r.end.x <= st.size.x + 0.5, "%s: every tag inside the row" % what)


# --- L51 / L29: one row of stat tags; the report's exit on screen ------------------------------

func test_the_raid_pages_keep_one_row_of_stat_tags_and_the_report_exit_on_screen() -> void:
	for corp in [&"", &"meridian"]:
		for scale in [1.0, 1.6, 2.0]:
			Settings.set_text_scale(scale)
			_raid_campaign(corp)
			var hq := _scene(HQ)
			await _frames(1)
			hq.show_raid()
			await _frames(2)
			hq.fight_raid()
			await _frames(4)
			var what := "%s %.1f" % [corp, scale]
			_one_row(hq.hud.stats, what + " playout")
			hq.show_raid_summary()
			await _frames(6)
			_one_row(hq.hud.stats, what + " report")
			var bar_end: float = hq.hud.get_global_rect().end.y
			var back := hq._panel.find_child("ReportBack", true, false) as Control
			var paper := hq._panel.find_child("RaidReport", true, false) as Control
			assert_true(SCREEN.encloses(back.get_global_rect()), "%s: BACK TO THE GRID whole on screen (%s)" % [what, back.get_global_rect()])
			assert_true(back.get_global_rect().position.y >= bar_end - 0.5, "%s: the exit under the top bar" % what)
			assert_true(paper.get_global_rect().position.y >= bar_end - 0.5, "%s: the paper starts under the top bar (%s, bar %.0f)" % [what, paper.get_global_rect(), bar_end])
			await _close(hq)
			RunManager.reset()


func test_with_motion_the_report_opens_on_its_exit_under_the_top_bar() -> void:
	Settings.set_text_scale(2.0)
	_raid_campaign()
	var hq := _scene(HQ)
	await _frames(2)
	hq.show_raid()
	await _frames(4)
	Motion.force_live = true
	hq.fight_raid()
	await _frames(2)
	hq.show_raid_summary()
	# The page's entrance ends with its first focus, MAP KEY at the war table's foot (the scroll
	# followed it down the column's foot: the letterhead under the bar, the exit above the screen).
	var back := hq._panel.find_child("ReportBack", true, false) as Control
	var focused := await BoundedWait.until(get_tree(), func() -> bool: return hq.get_viewport().gui_get_focus_owner() != null, BoundedWait.SLACK * 2.0)
	assert_true(focused, "the page's first focus has landed")
	await _frames(30)
	var key := hq._panel.find_child("KeyToggle", true, false) as Control
	assert_not_null(key, "MAP KEY on the war table")
	if key != null:
		assert_true(SCREEN.encloses(key.get_global_rect()), "MAP KEY (the first focus) on screen (%s)" % key.get_global_rect())
	assert_eq((hq._panel_host.get_parent() as ScrollContainer).scroll_vertical, 0, "the page stays at its top")
	var bar_end: float = hq.hud.get_global_rect().end.y
	assert_true(SCREEN.encloses(back.get_global_rect()) and back.get_global_rect().position.y >= bar_end - 0.5, "the exit whole on screen under the bar (%s)" % back.get_global_rect())
	var paper := hq._panel.find_child("RaidReport", true, false) as Control
	assert_true(paper.get_global_rect().position.y >= bar_end - 0.5, "the paper starts under the bar")
	Motion.force_live = false
	await _close(hq)


func test_the_netrun_raid_interlude_keeps_one_row_of_stat_tags() -> void:
	for scale in BIG:
		Settings.set_text_scale(scale)
		var net := _scene(NETRUN)
		RunManager.new_campaign(1)
		net.start_run(1)
		DemoSetup.queue_raid_interlude(RunManager.netrun, RunManager.config())
		await _frames(2)
		net._show_current()
		PageTransition.settle(net)
		await _frames(4)
		_one_row(net.hud.stats, "interlude %.1f" % scale)
		await _close(net)
		RunManager.reset()


func test_past_the_one_row_floor_the_names_fold_before_two_rows() -> void:
	Settings.set_text_scale(2.0)
	var st := HudStats.new()
	add_child_autofree(st)
	st.items = TAGS
	var fitted := st._fitted_width(0, TAGS.size())
	var compact := st.compact_width(1.0)
	assert_true(compact < fitted, "the folded tags are narrower than the named ones")
	# Room for the named tags at the 1.0 size: one row of names.
	st.size = Vector2(fitted + 1.0, 60)
	st._relayout()
	assert_eq([st.rows, st.compact], [1, false], "names on one row down to the 1.0 size")
	assert_true(st.tag_scale >= HudStats.ROW_FLOOR - 0.01)
	# Less: the names fold (each in its tag's tooltip), one row, never under the 1.0 size.
	st.size = Vector2((fitted + compact) * 0.5, 60)
	st._relayout()
	assert_eq([st.rows, st.compact], [1, true], "the names fold before the row wraps")
	assert_true(st.tag_scale >= HudStats.ROW_FLOOR - 0.01, "folded tags at the 1.0 size at least (%.2f)" % st.tag_scale)
	# Narrower than that: two rows, the last resort.
	st.size = Vector2(compact * 0.6, 60)
	st._relayout()
	assert_eq(st.rows, 2, "two rows only when even folded tags do not fit")
	# At 1.0 nothing changes: the 0.85 share still holds before the row wraps.
	assert_almost_eq(HudStats.one_row_floor(1.0), HudStats.fit_floor(1.0), 0.001)


# --- L36: START DEFENSE peels under the playout's page -----------------------------------------

func test_start_defense_peels_under_the_playout_page() -> void:
	_raid_campaign()
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(6)
	Motion.force_live = true
	hq.fight_raid()
	await _frames(1)
	var peel := hq.get_node_or_null(^"StartPeel") as RaidSticker
	assert_not_null(peel, "START DEFENSE peels off as the playout starts")
	if peel != null:
		assert_lt(peel.get_index(), hq.page_root().get_index(), "drawn under the page (the LIVE RAID FEED and its strip over it)")
		assert_gt(peel.get_index(), hq.wireframe.get_index(), "over the city")
		var gone := await BoundedWait.until(get_tree(), func() -> bool: return hq.get_node_or_null(^"StartPeel") == null, Motion.seconds(VinylSticker.PEEL) + BoundedWait.SLACK)
		assert_true(gone, "gone once it has peeled")
	Motion.force_live = false
	await _close(hq)


# --- L58: the Heat note leaves a spot a later page covers --------------------------------------

func test_the_heat_note_moves_off_words_laid_out_after_it() -> void:
	Settings.set_reduce_effects(true)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var p := HeatPoster.new(true)
	holder.add_child(p)
	p.position = Vector2(40, 100)
	p.size = p.custom_minimum_size
	p.set_heat(10, 100, MARKS)
	p.set_heat(30, 100, MARKS)
	p.complete_motion()
	await _frames(2)
	assert_true(p.note_showing(), "the crossing's note shows (its reading hold)")
	var note: Control = p._note
	var was := note.get_global_rect()
	# A page's title laid out afterwards where the note stands (the raid interlude's RAID // line).
	var title := Label.new()
	title.text = "RAID // COLLECTIONS: FIRST NOTICE"
	holder.add_child(title)
	title.position = was.position
	title.size = was.size
	await _frames(HeatPoster.NOTE_RECHECK_FRAMES + 2)
	assert_true(p.note_showing(), "still in its hold")
	assert_false(note.get_global_rect().intersects(title.get_global_rect()), "the note left the title (%s, title %s)" % [note.get_global_rect(), title.get_global_rect()])
	# A panel taller than 16 slides (the interlude at 1.6): the note slides on to a free spot.
	title.position = Vector2(0, 60)
	title.size = Vector2(700, 520)
	await _frames(HeatPoster.NOTE_RECHECK_FRAMES + 2)
	assert_false(note.get_global_rect().intersects(title.get_global_rect()), "past the tall panel too (%s)" % note.get_global_rect())
	assert_true(SCREEN.encloses(note.get_global_rect()), "on the screen")
	p.free()


func test_the_raid_interlude_heat_note_keeps_off_the_raid_panel_under_reduce_effects() -> void:
	Settings.set_reduce_effects(true)
	for scale in [1.0, 1.6, 2.0]:
		Settings.set_text_scale(scale)
		var net := _scene(NETRUN)
		RunManager.new_campaign(1)
		net.start_run(1)
		await _frames(2)
		DemoSetup.queue_raid_interlude(RunManager.netrun, RunManager.config())
		net._show_current()
		await _frames(HeatPoster.NOTE_FIRST_RECHECK + 3)
		var gauge: HeatPoster = net.hud.heat_gauge
		if gauge.note_showing():
			var note: Control = gauge._note
			for w in net._panel.find_children("*", "TerminalWindow", true, false):
				var head: Label = (w as TerminalWindow)._head
				if head != null and head.is_visible_in_tree() and head.text.contains("RAID"):
					assert_false(note.get_global_rect().intersects((w as Control).get_global_rect()), "%.1f: the note clear of the %s panel" % [scale, head.text])
		await _close(net)
		RunManager.reset()


# --- L45: hostile by shape with the colour-blind setting on ------------------------------------

func test_hazard_ticks_cross_the_route_and_the_reticle_rings_the_mark() -> void:
	var line := PackedVector2Array([Vector2(0, 0), Vector2(200, 0), Vector2(200, 100)])
	var ticks := RaidPencil.hazard_ticks(line, 40.0, 6.0)
	assert_eq(ticks.size(), int((300.0 - 40.0 - 40.0 * RaidPencil.TICK_LEAD) / 40.0) + 1, "one tick a step, none in the arrow head's room")
	for t in ticks:
		assert_almost_eq(t[0].distance_to(t[1]), 12.0, 0.01, "a tick is twice its half length")
		var mid: Vector2 = (t[0] + t[1]) * 0.5
		assert_true(is_equal_approx(mid.y, 0.0) or is_equal_approx(mid.x, 200.0), "each tick is centred on the route")
		var d: Vector2 = t[1] - t[0]
		assert_true(is_zero_approx(d.x) or is_zero_approx(d.y), "and across it")
	var ret := RaidPencil.reticle_ticks(Vector2(50, 50), Vector2(30, 20))
	assert_eq(ret.size(), 4, "four reticle ticks")
	for t in ret:
		var a: Vector2 = (t[0] - Vector2(50, 50)) / Vector2(30, 20)
		assert_almost_eq(a.length(), RaidPencil.RETICLE_FROM, 0.01, "a tick starts outside the ring")


func test_the_raid_routes_carry_hazard_ticks_only_with_the_colour_blind_setting() -> void:
	_raid_campaign()
	for mode in [&"off", &"deutan"]:
		Settings.set_colorblind_mode(mode)
		var hq := _scene(HQ)
		await _frames(1)
		hq.show_raid()
		await _frames(6)
		var layers: Array[Node] = hq.city_overlay.find_children("*", "RaidRouteLayer", true, false)
		assert_eq(layers.size(), 1, "%s: the routes in pencil" % mode)
		var layer := layers[0] as RaidRouteLayer
		layer.complete_motion()
		layer._laid_sig = 0
		layer._lay()
		var keys: Array = layer._pool._marks.keys().filter(func(k: String) -> bool: return k.begins_with("ticks_") or k.begins_with("reticle_"))
		var used: Array = keys.filter(func(k: String) -> bool: return layer._pool._used.has(k))
		if mode == &"off":
			assert_eq(used.size(), 0, "off: the approved look, no ticks")
		else:
			assert_gt(used.size(), 0, "deutan: the hostile routes are barbed and their entries ringed")
		assert_eq(RaidPencil.hostile_cues(), mode != &"off")
		await _close(hq)
	Settings.set_colorblind_mode(&"off")


## M14 12Q-ACCESS (L79): the Grid's pending raid (the HQ's dashed what-if route, before RAID SETUP)
## is barbed too with the colour-blind setting on; off, it keeps the approved look.
func test_the_grids_pending_raid_route_is_barbed_with_the_colour_blind_setting() -> void:
	_raid_campaign()
	for mode in [&"off", &"deutan"]:
		Settings.set_colorblind_mode(mode)
		var hq := _scene(HQ)
		await _frames(6)
		var layers: Array[Node] = hq.city_overlay.find_children("*", "RaidRouteLayer", true, false)
		assert_eq(layers.size(), 1, "%s: the pending raid's route in pencil" % mode)
		var layer := layers[0] as RaidRouteLayer
		assert_gt(layer.what_if.size(), 0, "the Grid shows the what-if route")
		layer.complete_motion()
		layer._laid_sig = 0
		layer._lay()
		var used: Array = layer._pool._marks.keys().filter(func(k: String) -> bool: return k.begins_with("whatif_ticks_") and layer._pool._used.has(k))
		if mode == &"off":
			assert_eq(used.size(), 0, "off: no ticks")
		else:
			assert_gt(used.size(), 0, "deutan: the what-if route is barbed")
		await _close(hq)
	Settings.set_colorblind_mode(&"off")


# --- L46: the Grid's drag demo carries an operative --------------------------------------------

func test_the_grid_drag_demo_carries_an_operative_to_jack_in() -> void:
	RunManager.new_campaign(7)
	var hq := _scene(HQ)
	await _frames(2)
	hq._demo_drag("drag_crew")
	var layer: DropLayer = hq.drops
	var carried := await BoundedWait.until(get_tree(), func() -> bool: return layer.mode == DropLayer.Mode.CARRY, BoundedWait.SLACK * 4.0, 240)
	assert_true(carried, "an operative is carried")
	if carried:
		assert_eq(String(layer.payload.get("kind", "")), "crew", "the crew polaroid's payload")
	await _close(hq)


# --- L64: the 3D city's current look ----------------------------------------------------------

func test_the_3d_city_shows_its_current_look_once_built() -> void:
	var view := CityView3D.new()
	assert_false(view.built(), "no model yet")
	view.use_model(CityModel.build(CITY_CONFIG, 7, Rect2i(10, 0, 10, 10)))
	add_child_autofree(view)
	await _frames(2)
	assert_true(view.built(), "built and placed")
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	holder.add_child(city)
	await _frames(1)
	city.bake_fade = 0.0  # a 2D frame showed the sky, waiting on its bake
	city.city3d = true
	assert_eq(city.bake_fade, 1.0, "the 3D city has no 2D bake to fade in: its lights at full")
	await _frames(1)
	assert_true(city.is_baked(), "the 3D city counts as baked (it never draws procedurally)")
	assert_true(city.showing_current_look(), "with no bake to wait for, it shows its current look (no 3D view headless)")
