extends GutTest
## Animation pass ANIM-R6 (the sixth fix batch), netrun screens (DECISIONS "Animation pass —
## ANIM-R6 netrun screens"): the loot's deal on MotionSkip, its invisible stickers taking no
## click (B1); dev flags through DemoSetup, never the view (B2); frame waits that end with
## the scene (B3); the flatline's run end baked during the fight (B4); the run end's lines
## and title agreeing with the verdict (B5); the route's kept bake let go at the run's end
## (B6); the toast's hold at a slow speed, the landing pulse's delay and its lab demo on the
## real bar (B7); one wording for the socket list (B8); the combat end demo in context (B9);
## the loot window naming what paid out, RAM with its icon (B10); the Mainframe's glyphs (B11);
## the event's story off the subtitle bar and its outcome stamped on its own page (B12); the
## jack's destination large with its tier (B13); a twin route choice that says what it is
## (B14).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const LAB := "res://tools/design_lab/motion_lab.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const EVENT := &"ev_leash_on_the_floor"
const CHIP := "barbed_wire"

var _scale: float = 1.0
var _reduce: bool = false
var _typing: bool = true


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects
	_typing = Settings.subtitle_typing


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r6"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	Motion.use_config(null)
	Engine.time_scale = 1.0
	CityBakeCache.simulate = false
	CityBakeCache.clear()
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.subtitle_typing != _typing:
		Settings.set_subtitle_typing(_typing)
	Dialogue.clear()
	Dialogue.dock_default()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _live() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Fx.apply_settings()
	Motion.force_live = true


func _netrun(scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames()
	return scene


func _close(scene: Control) -> void:
	if is_instance_valid(scene) and scene.get_parent() != null:
		scene.get_parent().queue_free()
	await _frames(2)


func _click(at: Vector2) -> void:
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = true
	e.position = at
	e.global_position = at
	get_viewport().push_input(e)


# --- B1: the loot's deal ----------------------------------------------------------------------

func test_the_loot_deal_is_a_motion_and_an_invisible_sticker_takes_no_click() -> void:
	var scene := await _netrun()
	_live()
	DemoSetup.offer_loot(RunManager.netrun, ["twist", "jam", "cache"])
	scene._show_current()
	# Hold the clock: the deal starts (deferred) and the last sticker sits in its delay.
	await BoundedWait.frozen_frames(get_tree(), 3)
	var row := scene.fanning_row() as Control
	assert_not_null(row, "the loot fans in")
	assert_true(scene.motion_running(), "the deal is a motion of the screen (MotionSkip)")
	assert_true(MotionSkip.running(scene).has(scene), "registered with MotionSkip")
	var last := row.get_child(row.get_child_count() - 1) as ZineCard
	assert_eq(last.modulate.a, 0.0, "the last sticker is still invisible (its delay)")
	assert_eq(last.mouse_filter, Control.MOUSE_FILTER_IGNORE, "an invisible sticker takes no click")
	assert_true(scene.motion_keeps().has(row), "the deal keeps the stickers' presses")
	# A click where the invisible sticker is: the deal lands, nothing is picked.
	Engine.time_scale = 1.0
	_click(last.get_global_rect().get_center())
	await _frames(2)
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.REWARD, "nothing picked: the offer is still open")
	assert_null(scene.fanning_row(), "the press landed the deal")
	for c in row.get_children():
		var card := c as ZineCard
		assert_false(card.dealing(), "%s in its slot" % card.card_title)
		assert_eq(card.modulate.a, 1.0, "%s shows" % card.card_title)
		assert_ne(card.mouse_filter, Control.MOUSE_FILTER_IGNORE, "%s takes clicks again" % card.card_title)
	await _close(scene)


func test_a_sticker_takes_clicks_once_it_shows_unpressed() -> void:
	var scene := await _netrun()
	_live()
	DemoSetup.offer_loot(RunManager.netrun, ["twist", "jam", "cache"])
	scene._show_current()
	assert_true(await BoundedWait.until(get_tree(), func() -> bool: return scene.fanning_row() == null,
		BoundedWait.motion_limit([&"loot_fan", &"loot_fan", &"loot_fan", &"panel_in"])), "the deal ends by itself")
	var row := scene._panel.find_child("Stickers", true, false) as Control
	for c in row.get_children():
		assert_eq((c as ZineCard).mouse_filter, Control.MOUSE_FILTER_STOP, "a shown sticker takes clicks")
	assert_false(scene.motion_running())
	await _close(scene)


# --- B2: views never write game state ---------------------------------------------------------

## Writes to game state a view must never make (the dev flags did them in the netrun scene).
const STATE_WRITES := [
	"\\.(cycles|phase|event_id|hp|rank|heat|schematics|current_node_id|outcome)\\s*(=|\\+=|-=)[^=]",
	"\\.(pending_rewards|daemon_ids|visited|roster|armory|deck)\\.(append|append_array|clear|erase|push_back|remove_at)\\(",
	"HeatRules\\.add_heat\\(",
	"\\.call\\(&?\"_(die|complete_run|open_shop|maybe_raid_interlude)\"",
	"netrun\\._[a-z]",
]


func _writes_in(path: String) -> PackedStringArray:
	var out := PackedStringArray()
	var res: Array[RegEx] = []
	for p in STATE_WRITES:
		res.append(RegEx.create_from_string(p))
	var n := 0
	for line in FileAccess.get_file_as_string(path).split("\n"):
		n += 1
		var code := line.strip_edges()
		if code.begins_with("#"):
			continue
		for re in res:
			if re.search(code) != null:
				out.append("%s:%d: %s" % [path.get_file(), n, code])
	return out


func test_the_netrun_view_writes_no_game_state() -> void:
	var bad := _writes_in("res://scripts/ui/netrun_scene.gd")
	for b in bad:
		gut.p("state write in a view: %s" % b)
	assert_eq(bad.size(), 0, "the netrun scene never writes game state (dev flags go through DemoSetup)")
	var hq := FileAccess.get_file_as_string("res://scripts/ui/hq_scene.gd")
	assert_false(hq.contains("op.rank = "), "the HQ's loadout demo sets the Rank through DemoSetup")


func test_demo_setup_reaches_the_states_the_dev_flags_ask_for() -> void:
	RunManager.new_campaign(1)
	RunManager.start_run()
	var s := RunManager.netrun
	DemoSetup.open_shop(s, 77)
	assert_eq(s.run.phase, RunState.Phase.SHOP)
	assert_eq(s.run.cycles, 77)
	DemoSetup.open_event(s, EVENT)
	assert_eq(s.run.phase, RunState.Phase.EVENT)
	assert_eq(s.current_event().id, EVENT)
	DemoSetup.offer_loot(s, [CHIP], "firmware")
	assert_eq(s.run.phase, RunState.Phase.REWARD)
	assert_eq(String(s.current_reward()["kind"]), "firmware")
	DemoSetup.end_run(s, "died")
	assert_eq(s.run.outcome, RunState.Outcome.DIED, "the session's own flatline")
	assert_false(s.last_events.is_empty(), "with its events")
	var st := CombatState.new()
	st.player = CombatantState.new()
	st.player.hp = 30
	DemoSetup.one_hit_from_end(st, false)
	assert_eq(st.player.hp, 1)


# --- B3: frame waits end with the scene -------------------------------------------------------

func test_freeing_the_scene_mid_wait_logs_nothing() -> void:
	var scene := await _netrun()
	scene._raid_map_area = Control.new()
	scene.add_child(scene._raid_map_area)
	scene._frame_raid_map()
	assert_true(scene._raid_map_framing, "the framing waits a frame")
	assert_true(get_tree().process_frame.is_connected(scene._frame_raid_map_now), "on a one-shot connection")
	scene.get_parent().free()
	await _frames(3)
	assert_engine_error_count(0, "nothing resumed on the freed scene")
	# The combat end demo's waits too.
	var again := await _netrun()
	again.enter_node(RunManager.netrun.available_nodes()[0])
	again._demo_combat_end("win")
	await _frames(2)
	again.get_parent().free()
	await _frames(4)
	assert_engine_error_count(0, "the demo's waits went with the scene")


# --- B4: the flatline's run end bakes during the fight -----------------------------------------

func test_a_lost_fight_bakes_the_run_end_look_before_its_page() -> void:
	CityBakeCache.simulate = true
	CityBakeCache.clear()
	var scene := await _netrun()
	scene.enter_node(RunManager.netrun.available_nodes()[0])
	assert_not_null(scene.combat_scene, "a fight")
	scene._demo_combat_end("lose")
	var over := await BoundedWait.until(get_tree(), func() -> bool: return RunManager.netrun.run.is_over(), 5.0)
	assert_true(over, "the fight was lost")
	if not over:
		await _close(scene)
		return
	assert_eq(RunManager.netrun.run.outcome, RunState.Outcome.DIED)
	assert_ne(scene.run_end_prebake, "", "the run end's look was asked for as the fight ended")
	assert_eq(scene._shown_screen, "combat", "while the fight still shows")
	var key: String = scene.run_end_prebake
	scene._leave_fight()
	await _frames(3)
	assert_eq(scene._shown_screen, "run_end")
	var city: NeonCity = scene.background.city
	assert_true(CityBakeCache.is_pending(key) or CityBakeCache.has(key), "the bake is running or done")
	assert_eq(CityBakeCache.find_pending(city.look_key(), city.view_rect()), key, "and it covers the run end's view, in its look")
	# A city that was hidden (the fight) shows a bake that landed meanwhile at once: the sky it
	# showed before is off the screen (it faded in over the silhouette).
	city.set(&"_sky_shown", true)
	scene.background.visible = false
	assert_false(bool(city.get(&"_sky_shown")), "hidden, no sky is on screen to fade from")
	scene.background.visible = true
	await _close(scene)


# --- B5: the run end agrees with its verdict ----------------------------------------------------

func test_the_run_end_title_and_lines_agree_with_the_verdict() -> void:
	var script: GDScript = load("res://scripts/ui/netrun_scene.gd")
	assert_eq(script.end_title(RunState.Outcome.DIED), "NETRUN // FLATLINED")
	assert_eq(script.end_title(RunState.Outcome.COMPLETED), "NETRUN // JACK OUT")
	assert_eq(script.end_title(RunState.Outcome.ABORTED), "NETRUN // HOME FELL")
	var scene := await _netrun()
	var s := RunManager.netrun
	scene.enter_node(s.available_nodes()[0])
	await _frames(2)
	# The fight's defeat bark (its scope: the fight), then DISPATCH's line for the run's end.
	Dialogue.clear()
	var combat: GDScript = load("res://scripts/ui/combat_scene.gd")
	Dialogue.bark(s.run.operative.class_id, "defeat", 1, combat.BARK_SCOPE)
	assert_true(Dialogue.is_showing(), "the operative's defeat bark shows in the fight")
	DemoSetup.end_run(s, "died")
	scene._report(s.last_events)
	scene._show_current()
	await _frames(2)
	assert_eq(scene.hud._title, tr("NETRUN // FLATLINED"), "the title says what the stamp says")
	assert_eq(Dialogue.shown_scope(), "run_end", "DISPATCH's line shows on the run's end")
	for l in Dialogue._queue:
		assert_ne(int(l.get("speaker", -1)), RC.Voice.STREET_MERC, "the dead operative never speaks after it: %s" % l)
	await _close(scene)


# --- B6: the route's kept bake --------------------------------------------------------------------

func test_the_route_bake_is_let_go_at_the_run_end() -> void:
	var scene := await _netrun()
	CityBakeCache.keep(scene.ROUTE_KEEP, "gut_route_look@x")
	DemoSetup.end_run(RunManager.netrun, "completed")
	scene._show_current()
	assert_eq(CityBakeCache.kept_key(scene.ROUTE_KEEP), "", "the run's end lets the route's bake go")
	var slot: StringName = scene.ROUTE_KEEP
	CityBakeCache.keep(slot, "gut_route_look@y")
	await _close(scene)
	assert_eq(CityBakeCache.kept_key(slot), "", "and so does the scene leaving")


# --- B7: the toast at a slow speed, the landing pulse ------------------------------------------

func test_the_toast_holds_longer_at_a_slow_speed_never_shorter() -> void:
	var raw := Motion.entry(ToastNote.HOLD_MOTION).duration
	Motion.set_speed(1.0)
	assert_almost_eq(ToastNote.hold_seconds(), raw, 0.001)
	Motion.set_speed(Motion.SPEED_MIN)
	assert_almost_eq(ToastNote.hold_seconds(), raw / Motion.SPEED_MIN, 0.001, "slowed down, the words stay longer")
	Motion.set_speed(Motion.SPEED_MAX)
	assert_almost_eq(ToastNote.hold_seconds(), raw, 0.001, "a faster speed never cuts the reading time")


func test_the_landing_pulse_waits_its_delay() -> void:
	_live()
	var cfg := (load(Motion.CONFIG_PATH) as UiMotionData).duplicate(true)
	cfg.find(HudStats.LAND_PULSE).delay = 0.3
	Motion.use_config(cfg)
	var bar: HudBar = add_child_autofree(HudBar.new())
	bar.set_stats([["CARDS", "10", ""]])
	await _frames(2)
	assert_eq(bar.land_pulse("card"), bar.stats, "a card pulses CARDS")
	var l: Dictionary = bar.stats._landing["CARDS"]
	var tw: Tween = l["tween"]
	# Stepped by hand (game time, not the clock): nothing during the delay, then the pulse.
	tw.pause()
	tw.custom_step(0.25)
	assert_eq(float(l["t"]), 0.0, "still waiting its delay")
	tw.custom_step(0.1)
	assert_gt(float(l["t"]), 0.0, "then the pulse plays")


func test_the_lab_demo_plays_the_pops_on_the_real_bar() -> void:
	_live()
	var lab: Control = load(LAB).instantiate()
	lab.set("_loop", false)
	add_child_autofree(lab)
	await _frames(1)
	lab.set("_id", &"flight_land_pulse")
	lab.call("_play")
	var seen := [false]
	var popped := await BoundedWait.until(get_tree(), func() -> bool:
		var b := lab.find_child("LandBar", true, false) as HudBar
		if b == null or b.daemon_button.scale == Vector2.ONE or b.loadout_button.scale == Vector2.ONE:
			return false
		seen[0] = not b.stats.landing().is_empty()
		return true,
		BoundedWait.motion_limit([&"flight_land_pulse"]))
	assert_true(popped, "the DAEMONS icon and VIEW LOADOUT pop (the netrun's own path)")
	assert_true(seen[0], "and CARDS pulses")


# --- B8 / B10: the loot's words ----------------------------------------------------------------

func test_the_loot_names_what_paid_out_and_its_socket_list_as_the_mainframe_does() -> void:
	var scene := await _netrun()
	var s := RunManager.netrun
	DemoSetup.offer_loot(s, [CHIP], "firmware")
	scene._show_current()
	await _frames(2)
	var word := scene._panel.find_child("SocketWord", true, false) as Label
	assert_not_null(word, "the chip's slot list has its words")
	assert_eq(word.text, tr("Chips go into:"), "the Mainframe's words (it said Socket into slot:)")
	var win := scene._panel.find_child("LootWindow", true, false) as TerminalWindow
	assert_false(win.title.contains(tr("RACK BREACHED")), "no Rack breached before any node: '%s'" % win.title)
	var script: GDScript = load("res://scripts/ui/netrun_scene.gd")
	# A fight's node pays FIGHT WON; the Rack RACK BREACHED; an Elite ELITE DOWN.
	for n in s.run.map.all_nodes():
		s.run.current_node_id = n["id"]
		var said: String = script.loot_source(s)
		match int(n["type"]):
			RC.InfilNodeType.ROUTER:
				assert_eq(said, "ELITE DOWN" if bool(n["elite"]) else "FIGHT WON")
			RC.InfilNodeType.SERVER_RACK:
				assert_eq(said, "RACK BREACHED")
			RC.InfilNodeType.TERMINAL:
				assert_eq(said, "EVENT PAYOUT")
	await _close(scene)


func test_ram_on_a_card_has_its_icon() -> void:
	var cache := RunManager.lookup().get_content(&"cache") as CardData
	var p: Array[Dictionary] = ZineCard.pictos_of(cache)
	assert_eq(p[0].get("icon", &""), StatIcon.RAM, "Cache's RAM+3 carries the RAM icon")
	assert_string_contains(String(p[0]["text"]), "+3")
	for k in [StatIcon.RAM, StatIcon.CART, StatIcon.SHRED]:
		assert_true(StatIcon.ALL.has(k), "%s is an icon" % k)


# --- B11: the Mainframe's glyphs ------------------------------------------------------------------------

func test_the_mainframe_says_what_it_does_with_glyphs() -> void:
	assert_eq(MainframeSign.SIGN_GLYPH, StatIcon.SHOP, "a shop bag on the sign")
	assert_eq(MainframeSign.NOTE_GLYPHS, [StatIcon.CART, StatIcon.SHRED] as Array[StringName], "a cart on BUY, a shredder on SHRED")
	var scene := await _netrun()
	DemoSetup.open_shop(RunManager.netrun)
	scene._show_current()
	await _frames(2)
	var icon := scene._panel.find_child("LeaveIcon", true, false) as IconMark
	assert_not_null(icon, "LEAVE MAINFRAME has its exit glyph")
	assert_eq(icon.kind, StatIcon.EXIT)
	await _close(scene)


# --- B12: the event ---------------------------------------------------------------------------------

func test_the_event_story_is_on_its_paper_not_repeated_in_the_bar() -> void:
	var scene := await _netrun()
	Dialogue.clear()
	var before := Dialogue.history.size()
	DemoSetup.open_event(RunManager.netrun, EVENT)
	scene._show_current()
	await _frames(2)
	var story := TextDb.t(RunManager.netrun.current_event(), "text")
	assert_false(Dialogue.is_showing() and Dialogue.current_text().contains(story.substr(0, 20)), "the bar doesn't repeat the story")
	assert_eq(Dialogue.history.size(), before + 1, "it is still in the history (voice-over)")
	assert_eq(Dialogue.history[-1]["text"], story)
	await _close(scene)


func test_the_chosen_outcome_stamps_on_the_event_page_before_it_leaves() -> void:
	var scene := await _netrun()
	DemoSetup.open_event(RunManager.netrun, EVENT)
	scene._show_current()
	await _frames(2)
	Typing.finish_all(get_tree())
	_live()
	scene.choose_event(0)
	assert_ne(RunManager.netrun.run.phase, RunState.Phase.EVENT, "the choice went through")
	assert_eq(scene._shown_screen, "event", "the event page stays while its outcome stamps")
	assert_true(scene.loot_leaving(), "inert, waiting")
	assert_gt(FlightFx.active_count(scene), 0, "the stamp plays")
	var left := await BoundedWait.until(get_tree(), func() -> bool: return not scene.loot_leaving(),
		BoundedWait.motion_limit([&"event_choice_stamp", &"loot_reject"]))
	assert_true(left, "the page leaves once the stamp has played")
	assert_eq(FlightFx.active_count(scene), 0, "no stamp over the next page")
	assert_ne(scene._shown_screen, "event")
	await _close(scene)


# --- B13: the jack's destination ----------------------------------------------------------------

func test_the_jack_names_its_destination_large_with_the_tier() -> void:
	RunManager.new_campaign(1)
	var site := RunManager.launchable_sites()[0] as SiteData
	assert_eq(RunManager.jack_tier(site.id), site.tier, "the Site's tier")
	Fx._destination = "Scrub Records"
	Fx._destination_tier = 2
	Fx._show_connect()
	assert_true(Fx.connect_dest.visible, "the destination has a line of its own")
	assert_eq(Fx.connect_dest.text, "SCRUB RECORDS")
	assert_gt(Fx.connect_dest.get_theme_font_size("font_size"), Fx.connect_label.get_theme_font_size("font_size"), "larger than CONNECTING TO")
	assert_eq(Fx.connect_dest.get_theme_color("font_color"), Palette.PAPER, "bright, not dim teal")
	assert_true(Fx.connect_site.visible, "with the tier icon")
	assert_eq(Fx.connect_site.tier, 2)
	assert_lt(Fx.connect_site.get_global_rect().end.x, Fx.connect_dest.get_global_rect().position.x + 1.0, "before the name")
	assert_lte(Fx.connect_dest.get_global_rect().end.y, Fx.connect_bar.position.y + 0.5, "above the bar")
	assert_string_contains(Fx.connect_words(), "CONNECTING TO SCRUB RECORDS")
	Fx._hide_connect()
	assert_false(Fx.connect_dest.visible)
	assert_false(Fx.connect_site.visible)


# --- B9 / B14 -----------------------------------------------------------------------------------------

func test_the_combat_end_demo_is_not_taken_for_the_run_end() -> void:
	var script: GDScript = load("res://scripts/ui/netrun_scene.gd")
	assert_eq(script.run_end_demo(PackedStringArray(["--demo-end=died"])), "died")
	assert_eq(script.run_end_demo(PackedStringArray(["--demo-combat", "--demo-end=lose"])), "", "with --demo-combat it is the fight's own end")


func test_a_twin_route_choice_says_what_it_is() -> void:
	var scene := await _netrun()
	var s := RunManager.netrun
	var twins: Dictionary = scene.choice_twins(s)
	var open := s.available_nodes()
	for i in open.size():
		if not twins.has(open[i]):
			continue
		var b := scene.find_child("Node%d" % (i + 1), true, false) as Button
		assert_string_contains(b.text, tr("(same road as choice %d)") % (int(twins[open[i]]) + 1))
		assert_string_contains(b.tooltip_text, "road ahead", "its tip explains it")
	await _close(scene)
