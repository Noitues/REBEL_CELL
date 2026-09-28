extends GutTest
## Animation pass ANIM-R1 (the first fix batch), campaign and screens: a second JACK IN,
## drop or scene press during a jack does nothing (one run, one scene change; the rules
## refuse a launch over a run under way); a motion entry switched off is its end state at
## once (the jack, the Heat pulse and creep, SAVED, the map ring); the raid playout reads
## at fight scale and still ends on the resolved campaign; territory changes leave a
## lasting mark; the Heat pulse is small and the number and banner carry it; the route's
## choice labels follow the move; the jack lands on a built screen; the event's choices
## wait for its words; nothing is cut; the Modem keeps its tiles in place after a buy.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const HQ_SCRIPT := preload("res://scripts/ui/hq_scene.gd")

var _reduce: bool
var _speed: float
var _scale: float
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _scene_asks: Array[String] = []


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_speed = Motion.speed
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r1"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	_scene_asks.clear()
	SignalBus.scene_change_requested.connect(_on_scene_ask)


func after_each() -> void:
	SignalBus.scene_change_requested.disconnect(_on_scene_ask)
	Motion.use_config(null)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Fx.apply_settings()
	Motion.force_live = false
	Motion.speed = _speed
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _on_scene_ask(path: String) -> void:
	_scene_asks.append(path)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _seconds(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(2)


func _live() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
		Fx.apply_settings()


## A copy of the motion table with entry `id` switched off (the loaded table never changes).
func _switch_off(ids: Array) -> void:
	var dup: UiMotionData = Motion.config().duplicate(true)
	for id in ids:
		dup.find(StringName(id)).enabled = false
	Motion.use_config(dup)


## The HQ with a campaign like --demo-raid: the first Site cleared and claimed, an asset on
## it, a raid pending.
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


# --- M1: one jack, one run, one scene change -----------------------------------------------------

func test_the_rules_refuse_a_launch_while_a_run_is_under_way() -> void:
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var op := c.living_operatives()[0]
	var cls := RunManager.lookup().get_content(op.class_id) as ClassData
	var site := RunManager.launchable_sites()[0]
	assert_eq(CampaignRules.launch_error(c, corp, RunManager.config(), op, cls, site), "", "free to launch")
	assert_eq(CampaignRules.launch_error(c, corp, RunManager.config(), op, cls, site, true), CampaignRules.RUN_IN_PROGRESS,
		"refused while a run is under way (pure rule)")
	assert_true(hq.launch(site.id, op.id), "the first JACK IN starts the run")
	var run := RunManager.netrun
	var after := c.state_hash()
	assert_ne(RunManager.launch_error(op.id, site.id), "", "RunManager passes the run under way")
	assert_false(hq.launch(site.id, op.id), "a second JACK IN starts nothing")
	assert_same(RunManager.netrun, run, "the first run stays")
	assert_eq(c.state_hash(), after, "the campaign is unchanged by the second press")
	await _close(hq)


func test_a_second_press_during_the_jack_does_nothing() -> void:
	_live()
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var c := RunManager.campaign
	var op := c.living_operatives()[0]
	var site := RunManager.launchable_sites()[0]
	var switched := [0]
	var second := [0]
	Fx.jack_in(func() -> void: switched[0] += 1)
	assert_true(Fx.transitioning(), "the jack runs")
	assert_true(RunManager.scene_change_pending())
	assert_eq(Fx.jack_cover.mouse_filter, Control.MOUSE_FILTER_STOP, "the cover takes the mouse while jacking")
	var before := c.state_hash()
	var asks := _scene_asks.size()
	assert_false(hq.launch(site.id, op.id), "JACK IN during the jack does nothing")
	assert_null(RunManager.netrun, "no run started")
	RunManager.go_to_netrun()
	RunManager.go_to_hq()
	RunManager.go_to_title()
	assert_eq(_scene_asks.size(), asks, "no second scene change is asked for")
	Fx.jack_in(func() -> void: second[0] += 1)
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	Fx._input(click)
	assert_true(get_viewport().is_input_handled(), "a press during the jack reaches no screen")
	while Fx.transitioning():
		await get_tree().process_frame
	assert_eq(switched[0], 1, "the jack switched once")
	assert_eq(second[0], 0, "the jack asked for during it never switches")
	assert_eq(c.state_hash(), before, "the campaign is unchanged")
	assert_eq(Fx.jack_cover.mouse_filter, Control.MOUSE_FILTER_IGNORE, "input comes back after")
	await _close(hq)


func test_netrun_leave_buttons_ask_once_during_the_jack() -> void:
	_live()
	var run := _scene(NETRUN)
	run.new_campaign(1)
	run.start_run(1)
	Fx.jack_out(func() -> void: pass)
	var asks := _scene_asks.size()
	var saved := RunManager.netrun
	run.save_and_quit()
	run.finish_run()
	assert_eq(_scene_asks.size(), asks, "Save & quit / Go to HQ during the jack ask for nothing")
	assert_same(RunManager.netrun, saved, "the run is not cleared by a press during the jack")
	while Fx.transitioning():
		await get_tree().process_frame
	await _close(run)


func test_a_saved_run_is_resumed_from_the_hq_jack_in() -> void:
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var op := RunManager.campaign.living_operatives()[0]
	var site := RunManager.launchable_sites()[0]
	assert_true(hq.launch(site.id, op.id))
	var run := RunManager.netrun
	hq.show_hq()
	await _frames(2)
	var asks := _scene_asks.size()
	var jack := hq._panel.find_child("JackIn", true, false) as BaseButton
	jack.pressed.emit()
	assert_eq(_scene_asks.size(), asks + 1, "JACK IN goes back into the run left")
	assert_eq(_scene_asks[_scene_asks.size() - 1], RunManager.NETRUN_SCENE)
	assert_same(RunManager.netrun, run, "the same run")
	await _close(hq)


# --- M3: an entry switched off is its end state at once --------------------------------------------

func test_jack_in_switched_off_switches_at_once() -> void:
	_live()
	_switch_off([&"jack_in"])
	var seen := []
	Fx.jack_in(func() -> void: seen.append(Fx.jack_cover.visible))
	assert_eq(seen, [false], "switched at once, no cover")
	assert_false(Fx.transitioning())


func test_heat_pulse_and_ring_switched_off_show_nothing() -> void:
	_live()
	_switch_off([&"heat_pulse", &"select_ring_pulse"])
	var n := Fx.heat_pulses
	Fx.heat_pulse()
	assert_eq(Fx.heat_pulses, n + 1, "still counted")
	assert_false(Fx.distortion.visible, "no distortion")
	var overlay := CityMapOverlay.new()
	assert_eq(overlay.pulse_amplitude(), 0.0, "the selection ring holds still")
	overlay.free()


func test_saved_switched_off_shows_still_then_goes_at_once() -> void:
	_live()
	_switch_off([&"saved_stamp"])
	await Fx.show_saved()
	assert_eq(Fx.saved_label.modulate.a, 1.0, "SAVED shows")
	await _seconds(Motion.delay_of(&"saved_stamp") * 0.5)
	assert_eq(Fx.saved_label.modulate.a, 1.0, "no fade: it holds still")
	await _seconds(Motion.delay_of(&"saved_stamp") + Motion.seconds(&"saved_stamp") + 0.2)
	assert_eq(Fx.saved_label.modulate.a, 0.0, "then goes at once")


func test_no_inline_fractions_are_left_in_fx() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/autoload/fx.gd")
	for inline in ["else 0.0) * 0.5", "seconds * 0.5", "JACK_ARRIVE_SHARE"]:
		assert_false(src.contains(inline), "no inline share of an entry's time in Fx: %s" % inline)
	var fx_layer := FileAccess.get_file_as_string("res://scripts/ui/kit/raid_fx_layer.gd")
	assert_false(fx_layer.contains("dur * 0.5"), "the raid hit is timed by the table, not half a trace")
	var overlay := FileAccess.get_file_as_string("res://scripts/ui/kit/city_map_overlay.gd")
	assert_false(overlay.contains("PULSE_AMPLITUDE") or overlay.contains("PULSE_SPEED"), "the ring's pulse is in the table")
	for id in [&"jack_arrive", &"jack_arrival_wait", &"select_ring_pulse"]:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(Motion.has(id), "%s is in the table" % id)


# --- M2: bakes never freeze a frame ------------------------------------------------------------------

func test_a_painter_builds_ahead_and_submits_in_chunks() -> void:
	assert_true(CityBakeCache.threaded, "bakes build their geometry off the main thread")
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	var region := Rect2(-400, -300, 800, 600)
	var painter := city.make_painter(region, 1.0)
	var was := NeonCity.emit_triangles
	NeonCity.emit_triangles = true
	painter.prebuild()  # as the worker thread runs it: before the painter is in the tree
	NeonCity.emit_triangles = was
	var verts := painter._verts.size()
	assert_gt(verts, 0, "the geometry is built ahead")
	assert_eq(verts % 3, 0, "whole triangles")
	var vp := SubViewport.new()
	vp.size = Vector2i(800, 600)
	holder.add_child(vp)
	vp.add_child(painter)
	var chunks := 0
	var at := 0
	while at >= 0:
		at = painter.submit_chunk(at)
		if at >= 0:
			chunks += 1
	assert_eq(chunks, ceili(float(verts) / NeonCity.CHUNK_VERTS), "a chunk a frame, CHUNK_VERTS each")
	assert_eq(painter._verts.size(), 0, "the vertex arrays let go once submitted")
	painter.free_chunks()
	assert_eq(city.prebake(region), "", "headless never bakes (nothing to wait on)")


# --- M4: the raid reads at fight scale -----------------------------------------------------------------

func _fixture_raid() -> RaidResolver.RaidResult:
	var grid := GridFixture.chain_grid([&"c1", &"c2"])
	var c := GridFixture.campaign(grid, {&"c1": &"firewall_relay", &"c2": &"relay"})
	GridFixture.deploy(c, &"c1", &"turret")
	var raid := GridFixture.raid(&"two", [&"collector", &"enforcer"])
	return RaidResolver.resolve(c, grid, raid, _lookup, _cfg)


func test_each_shot_reads_shot_then_hit_then_number() -> void:
	var result := _fixture_raid()
	var trace := RaidBeats.raw_seconds(&"turret_trace")
	var hit := RaidBeats.raw_seconds(&"raid_hit_effect")
	var shots := 0
	for g in RaidBeats.group(result.events):
		var tl := RaidBeats.timeline(g)
		var ends := {}
		for b: Dictionary in tl["beats"]:
			if b["type"] == "shot":
				shots += 1
				assert_almost_eq(float(b["dur"]), trace + hit, 0.0001, "a shot is its trace, then its hit")
				ends[String(b["event"]["threat"])] = float(b["t0"]) + float(b["dur"])
			elif b["type"] == "threat_destroyed" and ends.has(String(b["event"]["threat"])):
				assert_true(float(b["t0"]) >= float(ends[String(b["event"]["threat"])]) - 0.0001, "a threat breaks up after the shot that kills it has hit")
	assert_gt(shots, 0, "the fixture raid fires")
	var layer := RaidFxLayer.new()
	add_child_autofree(layer)
	for e in result.events:
		if e["type"] == "shot":
			layer.play_beat({"event": e, "type": "shot", "dur": trace + hit}, 1.0)
			break
	var order := {}
	for f in layer._fx:
		order[f["kind"]] = float(f["t0"])
	assert_almost_eq(order["trace"], 1.0, 0.0001, "the shot first")
	assert_almost_eq(order["hit"], 1.0 + trace, 0.0001, "the hit when the trace arrives")
	if order.has("number"):
		assert_almost_eq(order["number"], 1.0 + trace + hit, 0.0001, "the number after the hit")


func test_the_camera_frames_each_fight_before_it_plays() -> void:
	var result := _fixture_raid()
	for g in RaidBeats.group(result.events):
		for e: Dictionary in g:
			if e["type"] == "shot":
				var sites := RaidBeats.focus_sites(g, {})
				assert_true(sites.has(StringName(String(e["site"]))), "the firing defence is in frame before its shot")
	# The panel waits for the camera's ease before a step's beats.
	var panel := RaidPlayoutPanel.new()
	add_child_autofree(panel)
	var asked: Array = []
	panel.framer = func(sites: Array[StringName]) -> float:
		asked.append(sites)
		return 0.5
	panel.play(result.events, false)
	# ANIM-R2 R6 (changed on purpose): a step with nothing to show is not framed, and a
	# step's beats set off FRAME_WAIT_SHARE of the way through the ease (the playout opened
	# on ~2 s of a still map).
	var tl0 := RaidBeats.timeline(panel._steps[0])
	var framed := not (tl0["beats"] as Array).is_empty()
	assert_eq(asked.size(), 1 if framed else 0, "the first step asked for its frame (when it shows something)")
	assert_almost_eq(panel._next_at, (0.5 * RaidPlayoutPanel.FRAME_WAIT_SHARE if framed else 0.0) + float(tl0["seconds"]), 0.0001, "and its beats set off while the camera eases")
	panel.skip_to_end()
	assert_true(panel.is_done())


func test_home_hits_fly_into_the_counter_and_end_on_the_resolved_raid() -> void:
	var hq := _hq_raid()
	await _frames()
	_live()
	var c := RunManager.campaign
	hq.fight_raid()
	var r := c.last_raid
	assert_eq(hq.hud_home_shown, int(r["home_before"]), "HOME shows the home before the raid while it plays")
	var shown := [0]
	hq.playout.fx.home_hit_shown.connect(func(d: int, _s: StringName) -> void: shown[0] += d)
	hq.playout.skip_to_end()
	assert_eq(shown[0], int(r["home_before"]) - int(r["home_after"]), "every hit on home shows once, adding up to the resolved loss")
	assert_eq(hq.playout.fx.home_shown, int(r["home_after"]), "the home bar ends on the resolved value")
	await _frames()
	assert_eq(hq.hud_home_shown, -1, "the top bar shows the campaign's own HOME after")
	for n in hq.city_overlay.nodes:
		for k in (n.get("assets", []) as Array).size():
			assert_ne(hq.city_overlay.asset_slot(n, k, (n["assets"] as Array).size()), Vector2(INF, INF), "a placed defence has its marker")
	var g := CityLayout.grid_graph(c, RunManager.corporation, CityLayout.threat_paths(c, RunManager.corporation))
	for e: Dictionary in g["edges"]:
		if e.get("dashed", false):
			assert_true(e.get("arrows", false), "a threat route carries chevrons (apart from the Cell's links)")
	await _close(hq)


# --- M5: territory changes leave marks -------------------------------------------------------------------

func test_a_territory_change_leaves_a_claimed_or_seized_mark() -> void:
	var before := {"corp": &"solace", "sources": [], "sway": 0.0}
	var after := {"corp": &"solace", "sources": [{"id": &"a", "at": Vector2(10, 10), "w": CityInfluence.WEIGHT_CLAIMED}], "sway": 0.0}
	var m := InfluenceSpread.marks(before, after)
	assert_eq(m.size(), 1)
	assert_eq(m[0]["word"], InfluenceSpread.MARK_CLAIMED, "claimed toward the Cell")
	assert_eq(m[0]["color"], Palette.CELL_PINK)
	var lost := {"corp": &"solace", "sources": [{"id": &"a", "at": Vector2(10, 10), "w": CityInfluence.WEIGHT_SEIZED}], "sway": 0.0}
	var m2 := InfluenceSpread.marks(after, lost)
	assert_eq(m2[0]["word"], InfluenceSpread.MARK_SEIZED, "seized away from it")
	var city := NeonCity.new()
	add_child_autofree(city)
	var got := []
	city.territory_marked.connect(func(marks: Array) -> void: got.append(marks))
	city.mark_changes(before, after)
	assert_eq(got.size(), 1, "the city says a change landed (the counter bumps)")
	assert_eq(city.marks.size(), 1, "the mark stays")
	assert_eq(city.mark_t, 1.0, "headless: stamped at once")


# --- M6 / M16: the Heat poster -------------------------------------------------------------------------------

func test_a_heat_crossing_rolls_the_number_and_stamps_a_banner_then_goes() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var poster := HeatPoster.new(true)
	holder.add_child(poster)
	poster.set_heat(20, 100, [25, 50, 75] as Array[int])
	await _frames()
	_live()
	poster.set_heat(30, 100, [25, 50, 75] as Array[int])
	# ANIM-R2 R8 (changed on purpose): the number rolls to the threshold first; the banner
	# stamps when it gets there, naming the threshold crossed.
	assert_eq(poster.banner_alpha, 0.0, "no banner before the number crosses")
	# Frame by frame up to the stamp (bounded), keeping the number's largest scale: a fixed
	# number_roll + 0.1 s sometimes landed after the pop under loaded parallel shards
	# (DECISIONS "Animation pass - bake crash").
	var peak := poster.number_scale
	var t0 := Time.get_ticks_msec()
	while poster.banner_alpha < 1.0 and Time.get_ticks_msec() - t0 < int(Motion.seconds(&"number_roll") * 4000.0):
		await get_tree().process_frame
		peak = maxf(peak, poster.number_scale)
	assert_gt(peak, 1.0, "the number grows on the crossing")
	assert_eq(poster.banner_alpha, 1.0, "the banner stamps on")
	assert_string_contains(poster.banner_text(), "25")
	await _seconds(Motion.delay_of(&"heat_banner") + Motion.seconds(&"heat_banner") + Motion.seconds(&"number_roll") + 0.3)
	assert_eq(poster.banner_alpha, 0.0, "nothing stays on")
	assert_eq(poster.number_scale, 1.0)
	assert_almost_eq(poster.shown_heat, 30.0, 0.01, "the number rolled to the Heat")
	assert_lt(Motion.amplitude(&"heat_pulse"), 0.5, "the screen distortion is smaller than ANIM-5's")


func test_the_heat_number_stays_on_the_poster_whatever_the_word() -> void:
	var poster := HeatPoster.new(true)
	add_child_autofree(poster)
	poster.size = poster.custom_minimum_size
	for count in range(1, HeatPoster.RANSOM_LETTERS_MAX + 1):
		var lay := poster.letter_layout(count)
		assert_true(float(lay["num_x"]) + float(lay["num_w"]) <= poster.size.x + 0.01, "%d letters: the number and /100 fit" % count)
		assert_gt(float(lay["strip"]), 0.0)


# --- M7: the route after a move --------------------------------------------------------------------------------

func test_after_a_move_the_choice_labels_sit_on_the_new_next_nodes() -> void:
	var scene := _scene(NETRUN)
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames()
	var s := RunManager.netrun
	var from := s.run.current_node_id
	var to: StringName = s.available_nodes()[0]
	var overlay: CityMapOverlay = scene.city_overlay
	var landed := [false]
	overlay.travel(from, to, func() -> void: landed[0] = true)
	assert_true(landed[0], "headless: the move lands at once")
	# The run's state after a move, drawn on the map as the pulse lands.
	if not s.run.visited.has(s.run.current_node_id):
		s.run.visited.append(s.run.current_node_id)
	var r: Dictionary = scene.route_graph()
	for n: Dictionary in r["nodes"]:
		if n.get("next", false):
			assert_ne(String(n["label"]), "", "a next node carries its choice label")
		if s.run.visited.has(n["id"]) and n["id"] != s.run.current_node_id:
			assert_true(n.get("visited", false), "a node passed through is marked visited")
	overlay.set_graph(r["nodes"], r["edges"])
	for n in overlay.nodes:
		if n.get("visited", false):
			assert_false(overlay.is_dimmed(n["id"]), "visited reads apart from unreachable")
	await _close(scene)


# --- M8: the jack lands on a built screen ------------------------------------------------------------------------

func test_the_arriving_screens_say_when_they_are_ready() -> void:
	var scene := _scene(NETRUN)
	assert_true(scene.has_method(Fx.ARRIVAL_READY_METHOD))
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames()
	assert_true(scene.arrival_ready(), "the route is built (headless: no bake to wait for)")
	scene._panel = null
	assert_false(scene.arrival_ready(), "no page yet: the cover stays")
	await _close(scene)
	var hq := _scene(HQ)
	assert_true(hq.has_method(Fx.ARRIVAL_READY_METHOD))
	hq.new_campaign(1)
	await _frames()
	assert_true(hq.arrival_ready())
	assert_gt(Motion.seconds(&"jack_arrival_wait"), 0.0, "the cover waits at most this long")
	await _close(hq)


# --- M9: the event's choices wait for its words ---------------------------------------------------------------

func test_the_event_choices_wait_for_the_words() -> void:
	var scene := _scene(NETRUN)
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames()
	_live()
	var typing_before := Settings.subtitle_typing
	Settings.subtitle_typing = true
	var run := RunManager.netrun.run
	run.event_id = &"ev_leash_on_the_floor"
	run.phase = RunState.Phase.EVENT
	scene._show_current()
	await _frames(1)
	var c1 := scene._panel.find_child("Choice1", true, false) as Button
	assert_true(scene.choices_held(), "the words are typing")
	# ANIM-R2 E1/E2 (on purpose): a held choice waits readable and focusable, not disabled.
	assert_true(c1.has_meta(scene.HELD_META), "a choice waits while the words type")
	assert_false(c1.disabled, "readable and focusable, not disabled")
	for n in scene._panel.find_children("*", "RichTextLabel", true, false):
		Typing.finish(n as Control)
	await _frames(2)
	assert_false(scene.choices_held())
	var err := RunManager.netrun.choice_error(RunManager.netrun.current_event().choices[0])
	assert_eq(c1.disabled, err != "", "whole words: the choice acts (a refused one stays refused)")
	Settings.subtitle_typing = typing_before
	await _close(scene)


func test_outcome_rows_wrap_inside_their_choice_at_big_text() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var scene := _scene(NETRUN)
	scene.new_campaign(1)
	scene.start_run(1)
	var run := RunManager.netrun.run
	run.event_id = &"ev_leash_on_the_floor"
	run.phase = RunState.Phase.EVENT
	scene._show_current()
	await _frames(4)
	for b in scene._panel.find_children("Choice*", "Button", true, false):
		var row := b.find_child("OutcomeRow", false, false) as OutcomeRow
		if row == null:
			continue
		assert_true(Rect2(Vector2.ZERO, (b as Control).size).grow(1.0).encloses(Rect2(row.position, row.size)), "%s: the row inside its choice" % b.name)
		assert_true((b as Control).get_global_rect().end.x <= SCREEN.size.x + 0.5, "%s on screen" % b.name)
	var many: Array[Dictionary] = []
	for i in 3:
		many.append_array(OutcomeRow.no_change())
	var row2 := OutcomeRow.new(many)
	add_child_autofree(row2)
	assert_gt(row2.lines_at(10.0).size(), 1, "a narrow row wraps")
	await _close(scene)


# --- M10 / M11: the Modem and loot -----------------------------------------------------------------------------

func test_modem_items_show_their_whole_text_and_keep_their_places_after_a_buy() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var scene := _scene(NETRUN)
		scene.new_campaign(1)
		scene.start_run(1)
		RunManager.netrun.run.cycles = 999
		RunManager.netrun._open_shop()
		scene._show_current()
		await _frames(3)
		for row in ["Stickers", "Chips", "Daemons"]:
			var holder: Node = scene._panel.find_child(row, true, false)
			for c in holder.get_children():
				var zc := c as ZineCard
				assert_true(zc.fit_whole, "x%.1f %s: fits its text" % [scale, zc.card_title])
				assert_true(zc.text_whole(), "x%.1f %s: the whole text shows" % [scale, zc.card_title])
		var stickers: Node = scene._panel.find_child("Stickers", true, false)
		var n: int = stickers.get_child_count()
		var xs := []
		var variants := []
		for c in stickers.get_children():
			xs.append((c as Control).position.x)
			variants.append((c as ZineCard).variant)
		scene.buy("cards", 0)
		await _frames(2)
		stickers = scene._panel.find_child("Stickers", true, false)
		assert_eq(stickers.get_child_count(), n, "x%.1f: the bought card keeps its place" % scale)
		assert_true((stickers.get_child(0) as ZineCard).sold_stub, "as a SOLD stub")
		for i in range(1, n):
			assert_almost_eq((stickers.get_child(i) as Control).position.x, float(xs[i]), 0.5, "the others don't move")
			assert_eq((stickers.get_child(i) as ZineCard).variant, variants[i], "or change colour")
		scene.buy("cards", 0)
		await _frames(1)
		assert_eq(RunManager.netrun.run.shop["cards"].size(), n - 2, "buying the first live card again buys the next one")
		await _close(scene)


func test_loot_rejects_fall_the_tip_keeps_off_skip_and_cards_off_the_bar() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var scene := _scene(NETRUN)
	scene.new_campaign(1)
	scene.start_run(1)
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	PageTransition.settle(scene)
	await _frames(3)
	var skip := scene._panel.find_child("Skip", true, false) as Control
	for c in scene._panel.find_child("Stickers", true, false).get_children():
		assert_true((c as Control).get_global_rect().end.y < skip.get_global_rect().position.y, "%s clear of the Skip bar" % (c as ZineCard).card_title)
	var card := scene._panel.find_child("Stickers", true, false).get_child(0) as Control
	var tip_at := FocusTip.spot(card.get_global_rect(), Vector2(300, 90), SCREEN, [skip.get_global_rect()] as Array[Rect2])
	assert_false(Rect2(tip_at, Vector2(300, 90)).intersects(skip.get_global_rect()), "the tip keeps off Skip")
	_live()
	scene.choose_reward(1)
	var falls := FlightFx.existing(scene).flights.filter(func(f: Dictionary) -> bool: return f["id"] == &"loot_reject")
	assert_eq(falls.size(), 2, "the two offers not taken fall away")
	await _close(scene)


func test_a_long_refusal_toast_wraps_on_screen() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var t := ToastNote.show_on(holder, "t1_a has no free asset slot. ".repeat(8), true)
	await _frames(2)
	assert_true(Rect2(Vector2.ZERO, SCREEN.size).encloses(Rect2(t.position, t.size)), "the whole note on screen")


# --- M12: the HQ at big text ----------------------------------------------------------------------------------

func test_the_hq_at_big_text_shows_hp_and_keeps_saved_off_the_tags() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var hq := _scene(HQ)
	hq.new_campaign(1)
	await _frames(4)
	var op := RunManager.campaign.roster[0]
	var dossier := hq._panel.find_child("Crew_%s" % op.id, true, false) as CrewCard
	var hp_line: Label = null
	for l in dossier.find_children("*", "Label", true, false):
		if (l as Label).text.begins_with("HP"):
			hp_line = l
	assert_not_null(hp_line)
	assert_true(hp_line.get_global_rect().end.y <= SCREEN.size.y, "the dossier's HP shows on the first screen")
	var avoid := Fx.avoid_rects(hq)
	for r in hq.hud.stats.tag_rects():
		var g := Rect2(hq.hud.stats.get_global_transform() * r.position, r.size)
		var hit := false
		for a in avoid:
			if a.is_equal_approx(g):
				hit = true
		assert_true(hit, "the SAVED stamp keeps off the top bar's tags")
	Settings.set_text_scale(1.0)
	hq.show_hq()
	await _frames(3)
	var scrub := hq._panel.find_child("ScrubHeat", true, false) as Button
	var mark := scrub.get_node(^"PriceIcon") as Control
	var font := scrub.get_theme_font(&"font")
	var text_end := font.get_string_size(scrub.text, HORIZONTAL_ALIGNMENT_LEFT, -1, scrub.get_theme_font_size(&"font_size")).x
	assert_lt(mark.position.x, scrub.get_theme_stylebox(&"normal").get_margin(SIDE_LEFT) + float(scrub.icon.get_width()) + 40.0 + text_end, "the Schematics icon right after the price")
	await _close(hq)


# --- M15: loops on measured geometry end ---------------------------------------------------------------------

func test_placement_loops_end_on_geometry_that_is_not_finite() -> void:
	var t0 := Time.get_ticks_msec()
	var spot := Fx.saved_spot(Vector2(40, 20), Rect2(0, 0, INF, INF), [] as Array[Rect2])
	assert_true(spot.is_finite() or spot == Vector2.ZERO, "SAVED on an unbounded screen")
	Fx.saved_spot(Vector2(NAN, NAN), Rect2(0, 0, 1280, 720), [] as Array[Rect2])
	assert_lt(Time.get_ticks_msec() - t0, 500, "returns at once")
	assert_gt(HQ_SCRIPT.RAID_CHECKS_MAX, 0, "the raid page's framing is bounded")
	assert_gt(LegendSpot.SPOTS_MAX, 0)
