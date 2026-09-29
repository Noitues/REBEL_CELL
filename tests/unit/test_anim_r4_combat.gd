extends GutTest
## Animation pass ANIM-R4 (the fourth fix batch), combat, input and screens (DECISIONS
## "Animation pass — ANIM-R4 combat, input and screens"): LOOT / CONTINUE translated once and
## fitting (C1); one press rule in every helper, with the pause menu, occlusion and the
## button mask (C2); no leaks or orphans (C3); nudge key hints off the tags (C4); motion
## shares in the table (C5); SEND IT for a beginner: one side then the other, cause before
## effect, one notation for a hit and its guard, side colours, no forecast spoiler, preview =
## result, statuses as good / bad icons, the break and VICTORY apart, RAM floats (C6); the
## run's screens: loot that falls within its page, fitting tags and tips, BUY off the text,
## refusals that wrap, an event that types quickly (C7).

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.3, 1.6]
## A projectile must be seen in flight at least this long (s) at 1x (C6d).
const FLIGHT_FLOOR := 0.25

var _scale: float = 1.0
var _reduce: bool = false
var _typing: bool = true
var _pad: bool = false
var _translation: Translation = null
var _locale_before: String = ""


class Counter extends Node:
	## Counts the presses that reach it (it sits before the helper in the tree, so the
	## helper sees each event first).
	var got: int = 0

	func _input(event: InputEvent) -> void:
		if MotionSkip.is_press(event):
			got += 1


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects
	_typing = Settings.subtitle_typing
	_pad = Settings.pad_active


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r4"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	Fx._jacking = false
	Engine.time_scale = 1.0
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.subtitle_typing != _typing:
		Settings.set_subtitle_typing(_typing)
	Settings.set_pad_active(_pad)
	_pseudo(false)
	if _translation != null:
		TranslationServer.remove_translation(_translation)
		TranslationServer.set_locale(_locale_before)
		_translation = null
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


func _live() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Fx.apply_settings()
	Motion.force_live = true


func _pseudo(on: bool) -> void:
	if TranslationServer.pseudolocalization_enabled == on:
		return
	ProjectSettings.set_setting("internationalization/pseudolocalization/replace_with_accents", on)
	ProjectSettings.set_setting("internationalization/pseudolocalization/double_vowels", on)
	ProjectSettings.set_setting("internationalization/pseudolocalization/override", false)
	TranslationServer.pseudolocalization_enabled = on
	TranslationServer.reload_pseudolocalization()


func _translate(pairs: Dictionary) -> void:
	_locale_before = TranslationServer.get_locale()
	TranslationServer.set_locale("xx")
	_translation = Translation.new()
	_translation.locale = "xx"
	for k in pairs:
		_translation.add_message(String(k), String(pairs[k]))
	TranslationServer.add_translation(_translation)


func _combat(enemy: StringName = &"collections_agent", scale: float = 1.0, combat_seed: int = 5) -> Control:
	Settings.set_text_scale(scale)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, combat_seed)
	await _frames()
	return scene


func _netrun(campaign_seed: int = 1) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var counter := Counter.new()
	holder.add_child(counter)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(campaign_seed)
	scene.start_run(1)
	await _frames()
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(2)


func _holder() -> Array:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var counter := Counter.new()
	holder.add_child(counter)
	return [holder, counter]


func _key(k: Key, pressed: bool = true) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = pressed
	return e


func _click(at: Vector2, button: MouseButton = MOUSE_BUTTON_LEFT, pressed: bool = true) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = button
	e.pressed = pressed
	e.position = at
	e.global_position = at
	return e


func _hover(at: Vector2) -> void:
	var m := InputEventMouseMotion.new()
	m.position = at
	m.global_position = at
	get_viewport().push_input(m)


func _action(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


# --- C1: LOOT / CONTINUE translated once, and fitting -------------------------------------------------------

func test_loot_and_continue_translate_once_and_fit_what_is_drawn() -> void:
	var scene := await _combat()
	var b: DripButton = scene._continue_button
	_pseudo(true)
	for key in ["LOOT", "CONTINUE"]:
		scene.show_continue(key)
		assert_eq(b.tag_text, key, "%s: the button gets the key" % key)
		var shown: String = b.shown_lettering()[0]
		assert_eq(shown, String(TranslationServer.translate(key)), "%s: drawn translated once" % key)
		assert_false(shown.begins_with("[["), "%s: never twice (%s)" % [key, shown])
		assert_lte(b.drawn_width(), b.get_combined_minimum_size().x + 0.5, "%s: the words drawn fit the button (%.0f in %.0f)" % [key, b.drawn_width(), b.get_combined_minimum_size().x])
		assert_eq(b.tooltip_text, tr(key), "%s: the tooltip arrives translated" % key)
		assert_eq(b.tooltip_auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED, "%s: and is shown as given" % key)
	_pseudo(false)
	_translate({"LOOT": "XX_LOOT", "CONTINUE": "XX_CONTINUE"})
	scene.show_continue("CONTINUE")
	scene.show_continue("LOOT")
	assert_eq(String(b.shown_lettering()[0]), "XX_LOOT", "an xx catalogue's word is what is drawn")
	assert_eq(b.tooltip_text, "XX_LOOT")
	assert_true(FileAccess.get_file_as_string("res://scripts/ui/netrun_scene.gd").contains("TextDb.mark(\"LOOT\")"), "the netrun passes the key")
	await _close(scene)


func test_drawn_tags_that_arrive_translated_are_not_translated_again() -> void:
	_pseudo(true)
	var words := tr("LOOT: pick a %s") % tr("card")
	var tag := GraffitiTag.new(words).fit_width(900.0)
	add_child_autofree(tag)
	assert_true(tag.words_width() + GraffitiTag.LEFT + GraffitiTag.MASCOT_ROOM <= tag.custom_minimum_size.x + 0.5, "the words and the mascot fit the tag")
	assert_lte(tag.custom_minimum_size.x, 900.0 + 0.5, "the tag fits the loot's row")
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/graffiti_tag.gd")
	assert_true(src.contains("true, true, false)"), "the tag draws its words as given")
	assert_true(FileAccess.get_file_as_string("res://scripts/ui/kit/graffiti_scrawl.gd").contains("false, true, false)"), "so does the scrawl")


# --- C2: one press rule everywhere ---------------------------------------------------------------------------

func test_the_verdict_trusts_the_hovered_control_the_mask_and_the_pause_menu() -> void:
	var h := _holder()
	var holder: Control = h[0]
	var button := Button.new()
	button.text = "GO"
	button.position = Vector2(100, 100)
	button.size = Vector2(200, 60)
	holder.add_child(button)
	var cover := Panel.new()
	cover.position = Vector2(200, 90)
	cover.size = Vector2(200, 100)
	cover.mouse_filter = Control.MOUSE_FILTER_STOP
	holder.add_child(cover)
	await _frames(1)
	var open := Vector2(140, 130)
	var covered := Vector2(260, 130)
	_hover(open)
	await _frames(1)
	assert_eq(MotionSkip.verdict(_click(open), holder), MotionSkip.Verdict.PASS, "a click on a usable button passes")
	assert_eq(MotionSkip.verdict(_click(open, MOUSE_BUTTON_RIGHT), holder), MotionSkip.Verdict.CONSUME, "a right-click works no left-click button")
	assert_eq(MotionSkip.verdict(_click(open), holder, [button]), MotionSkip.Verdict.CONSUME, "a kept button's click is the helper's")
	_hover(covered)
	await _frames(1)
	assert_eq(MotionSkip.verdict(_click(covered), holder), MotionSkip.Verdict.CONSUME, "a button under a panel is not clicked (the hovered panel is trusted; hovered: %s)" % get_viewport().gui_get_hovered_control())
	assert_eq(MotionSkip.verdict(_key(KEY_LEFT), holder), MotionSkip.Verdict.PASS, "a focus move passes")
	assert_eq(MotionSkip.verdict(_key(KEY_ESCAPE), holder), MotionSkip.Verdict.PASS, "the Settings key passes")
	assert_eq(MotionSkip.verdict(_key(KEY_SEMICOLON), holder), MotionSkip.Verdict.CONSUME, "a press that works nothing is consumed")
	var menu := PauseMenu.new()
	holder.add_child(menu)
	await _frames(1)
	assert_eq(MotionSkip.verdict(_key(KEY_SEMICOLON), holder), MotionSkip.Verdict.IGNORE, "an open pause menu keeps every press")
	menu.queue_free()
	await _frames(1)


func test_page_entrances_follow_the_one_rule() -> void:
	_live()
	var h := _holder()
	var holder: Control = h[0]
	var counter: Counter = h[1]
	var page := Panel.new()
	page.size = Vector2(300, 200)
	holder.add_child(page)
	await _frames(1)
	var t := PageTransition.enter(page)
	assert_not_null(t, "the page enters")
	get_viewport().push_input(_key(KEY_LEFT))
	assert_false(PageTransition.running(page), "a focus move completes the entrance")
	assert_eq(counter.got, 1, "and passes on")
	var menu := PauseMenu.new()
	holder.add_child(menu)
	await _frames(1)
	PageTransition.enter(page)
	await BoundedWait.frozen_frames(get_tree(), 1)
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_true(PageTransition.running(page), "with the pause menu open the entrance plays on (its presses are the menu's)")
	menu.free()
	var got := counter.got
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(PageTransition.running(page), "a stray key completes it")
	assert_eq(counter.got, got, "and is consumed")


func test_flights_and_drops_follow_the_one_rule() -> void:
	_live()
	var h := _holder()
	var holder: Control = h[0]
	var counter: Counter = h[1]
	FlightFx.fly_node(holder, ColorRect.new(), Rect2(10, 10, 40, 40), Vector2(600, 300), &"buy_fly")
	get_viewport().push_input(_key(KEY_LEFT))
	assert_eq(FlightFx.active_count(holder), 0, "a focus move lands the flight")
	assert_eq(counter.got, 1, "and passes on")
	var layer := DropLayer.new()
	holder.add_child(layer)
	layer._stamp(Vector2(100, 100), 10.0)
	get_viewport().push_input(_key(KEY_LEFT))
	assert_false(layer.busy(), "a focus move completes the stamp")
	assert_eq(counter.got, 2, "and passes on")
	var menu := PauseMenu.new()
	holder.add_child(menu)
	await _frames(1)
	FlightFx.fly_node(holder, ColorRect.new(), Rect2(10, 10, 40, 40), Vector2(600, 300), &"buy_fly")
	layer._stamp(Vector2(100, 100), 10.0)
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_eq(FlightFx.active_count(holder), 1, "the pause menu keeps the press: the flight flies on")
	assert_true(layer.busy(), "and the stamp plays on")
	menu.free()
	var got := counter.got
	# One press each: the helper nearest the front ends its motion and consumes the press.
	get_viewport().push_input(_key(KEY_SEMICOLON))
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_eq(FlightFx.active_count(holder), 0)
	assert_false(layer.busy())
	assert_eq(counter.got, got, "a stray key is consumed")
	FlightFx.finish_all(holder)


func test_a_menu_line_lets_the_settings_key_through() -> void:
	var box := VBoxContainer.new()
	add_child_autofree(box)
	for w in ["ONE", "TWO"]:
		var b := Button.new()
		b.text = w
		box.add_child(b)
	var m := MenuMotion.attach(box)
	assert_true(m.works_menu(_action(&"open_settings")), "Esc while a pause-menu line types closes the menu at once")
	assert_true(m.works_menu(_key(KEY_DOWN)))
	assert_false(m.works_menu(_key(KEY_SEMICOLON)))


func test_the_route_move_follows_the_one_rule() -> void:
	var scene := await _netrun()
	var counter: Counter = scene.get_parent().get_child(0)
	scene._travelling = true
	var got := counter.got
	get_viewport().push_input(_key(KEY_LEFT))
	assert_false(scene._travelling, "a focus move ends the route move")
	assert_eq(counter.got, got + 1, "and passes on")
	scene._travelling = true
	var menu := PauseMenu.new()
	scene.get_parent().add_child(menu)
	await _frames(1)
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_true(scene._travelling, "the pause menu keeps its presses")
	menu.free()
	got = counter.got
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(scene._travelling)
	assert_eq(counter.got, got, "a stray key is consumed")
	await _close(scene)


func test_the_combat_replay_follows_the_one_rule_and_keeps_its_own_buttons() -> void:
	var scene := await _combat()
	_live()
	var turn: int = scene.engine.state().turn
	scene.end_turn()
	assert_not_null(scene._seq, "the replay plays")
	get_viewport().push_input(_key(KEY_LEFT))
	assert_null(scene._seq, "a focus move ends the replay")
	assert_false(get_viewport().is_input_handled(), "and passes on")
	turn = scene.engine.state().turn
	scene.end_turn()
	var at: Vector2 = scene._end_turn_button.get_global_rect().get_center()
	_hover(at)
	var click := _click(at)
	get_viewport().push_input(click)
	assert_null(scene._seq, "a click on SEND IT ends the replay")
	assert_true(get_viewport().is_input_handled(), "and does nothing else")
	assert_eq(scene.engine.state().turn, turn + 1, "no second turn is played blind")
	get_viewport().push_input(_click(at, MOUSE_BUTTON_LEFT, false))
	scene.end_turn()
	var menu := PauseMenu.new()
	scene.get_parent().add_child(menu)
	await _frames(1)
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_not_null(scene._seq, "an open pause menu leaves the replay playing")
	menu.free()
	scene.skip_motion()
	await _close(scene)


# --- C3: leaks and orphans ------------------------------------------------------------------------------------

func test_options_opened_and_closed_five_times_leave_no_controls() -> void:
	var holder: Control = add_child_autofree(Control.new())
	var p0 := SettingsPanel.new()
	holder.add_child(p0)
	p0.free()
	await _frames(2)
	var nodes := Performance.get_monitor(Performance.OBJECT_NODE_COUNT)
	var orphans := Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)
	for k in 5:
		var p := SettingsPanel.new()
		holder.add_child(p)
		for s in ["Display", "Controls", "Audio", "Language", "Controls", "Accessibility"]:
			p.show_section(s)
		p.queue_free()
		await _frames(2)
	assert_eq(Performance.get_monitor(Performance.OBJECT_NODE_COUNT), nodes, "no Control is left behind (49 leaked per Options)")
	assert_eq(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT), orphans, "and none waits off the tree")


func test_a_hand_rebuild_leaves_no_orphans_the_same_frame() -> void:
	var scene := await _combat()
	var orphans := Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)
	for k in 3:
		scene._build_hand(scene.engine.state())
	assert_eq(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT), orphans, "the old cards are freed at once")
	await _close(scene)


func test_no_test_instantiates_the_combat_scene_for_its_statics() -> void:
	for path in ["res://tests/unit/test_horizontal_pass23.gd", "res://tests/unit/test_horizontal_pass24.gd"]:
		assert_false(FileAccess.get_file_as_string(path).contains("instantiate().get_script()"), "%s frees what it makes" % path)


# --- C4: nudge key hints off the tags ------------------------------------------------------------------------

func test_nudge_key_hints_keep_off_the_tags_at_every_text_size() -> void:
	for scale in SCALES:
		var scene := await _combat(&"collections_agent", scale)
		await _frames(2)
		var hints := 0
		for v in scene._views():
			var wv := v as WheelView
			for hr in wv.arrow_hint_rects():
				hints += 1
				for other in scene._views():
					var tag: Rect2 = (other as WheelView).intent_rect()
					if tag.has_area():
						assert_false(hr.intersects(tag), "x%.1f: a key hint on %s's tag" % [scale, (other as WheelView).combatant.display_name])
		assert_gt(hints, 0, "x%.1f: the driven wheel shows its key hints" % scale)
		assert_eq(scene.layout_violations(), [] as Array[String], "x%.1f: no layout violation" % scale)
		await _close(scene)


# --- C5: motion numbers in the table -------------------------------------------------------------------------

func test_motion_shares_live_in_the_table() -> void:
	var ids: Array[StringName] = [&"hit_line_flight", &"ride_swap", &"ride_shrink", &"ride_perfect", &"break_crack", &"modem_sign_strike",
		&"modem_sign_flicker", &"resolve_side_gap", &"resolve_attacker_gap", &"ram_refill_float", &"event_type"]
	var lab := FileAccess.get_file_as_string("res://tools/design_lab/motion_lab.gd")
	for id in ids:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(Motion.has(id), "%s is in the table" % id)
		assert_true(lab.contains("&\"%s\":" % id), "%s has a lab demo" % id)
	var gone := {"res://scripts/ui/kit/combat_fx_layer.gd": ["RIDE_SWAP_SHARE :=", "RIDE_SHRINK_TO :=", "CRACK_SHARE :=", "LINE_DRAW_SHARE :="],
		"res://scripts/ui/combat_scene.gd": ["PERFECT_RIDE_SCALE :="], "res://scripts/ui/kit/modem_sign.gd": ["STRIKE_SHARE :=", "FLICKER_SHARE :="]}
	for path in gone:
		var src := FileAccess.get_file_as_string(path)
		for c in gone[path]:
			assert_false(src.contains(c), "%s: %s is a table entry now" % [path, c])
	assert_true(FileAccess.get_file_as_string("res://scripts/ui/wheel_view.gd").contains("TICK_SHARE := 0.32  # drawing, not motion"), "the tick's size is documented as drawing")
	var style := FileAccess.get_file_as_string("res://docs/STYLE_GUIDE.md")
	assert_false(style.contains("stamps BLOCKED or EVADED on impact"), "STYLE_GUIDE 5.2 says what the replay does now")


# --- C6a: one side, then the other ---------------------------------------------------------------------------

func _hit(src: StringName, side: String, target: StringName, amount: int, hp_after: int) -> Dictionary:
	return {"kind": "damage", "event_index": 0, "phase": "resolve", "pass": "offensive", "source": src, "pointer_index": 0, "target": target,
		"amount": amount, "crit": false, "hp_after": hp_after, "slot": -1, "status": 0, "tier": -1, "soaked": 0, "host": &"",
		"source_slot": -1, "source_tier": -1, "raw": amount, "blocked": 0, "shielded": 0, "side": side, "wheel_source": true}


func test_my_hits_land_in_full_then_a_gap_then_the_enemys() -> void:
	var timing: Dictionary = load("res://scripts/ui/combat_scene.gd").beat_timing()
	var beats: Array[Dictionary] = [
		_hit(&"player", "player", &"e0", 5, 25), _hit(&"player", "player", &"e0", 4, 21), _hit(&"drone_0", "player", &"e0", 2, 19),
		_hit(&"e0", "enemy", &"player", 6, 54), _hit(&"sat_0", "enemy", &"player", 3, 51)]
	beats[2]["wheel_source"] = false
	beats[4]["wheel_source"] = false
	var sch := ResolveBeats.schedule(beats, 2.0, 0.1, 0.0, 0.3, 0.5, 0.0, timing)
	var t: PackedFloat32Array = sch["times"]
	var settled := 0.0
	for k in 3:
		settled = maxf(settled, t[k] + ResolveBeats.settle_after(beats[k], timing))
	assert_gte(t[3], settled + float(timing["side_gap"]) - 0.0001, "the enemy's first hit waits until my hits' rolls are done, and a gap")
	assert_gte(t[2], t[1] + ResolveBeats.arrive_after(beats[1], timing) + float(timing["attacker_gap"]) - 0.0001, "my drone's hit comes after mine, staggered")
	assert_gte(t[4], t[3] + ResolveBeats.arrive_after(beats[3], timing) + float(timing["attacker_gap"]) - 0.0001, "the satellite's after its host's, staggered")
	assert_gt(float(timing["side_gap"]), 0.0)


func test_real_resolves_play_one_side_after_the_other() -> void:
	var sides_seen := 0
	for combat_seed in [3, 5, 7]:
		var scene := await _combat(&"collections_agent", 1.0, combat_seed)
		_live()
		for turn in 3:
			if scene.engine.state().is_over():
				break
			var before: CombatState = scene.engine.state().duplicate_state()
			scene.end_turn()
			var beats := ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup)
			var timing: Dictionary = scene.beat_timing()
			var times: PackedFloat32Array = scene.sequence_schedule(beats)["times"]
			var settled := -1.0
			var last_side := ""
			for k in beats.size():
				var b := beats[k]
				if b["phase"] == "turn_start":
					break
				if ResolveBeats.flies(b):
					assert_ne(String(b["side"]), "", "every hit knows its side")
					if last_side != "" and String(b["side"]) != last_side:
						sides_seen += 1
						assert_gte(times[k], settled + float(timing["side_gap"]) - 0.0001, "seed %d: a new side waits for every roll" % combat_seed)
					last_side = String(b["side"])
				settled = maxf(settled, times[k] + ResolveBeats.settle_after(b, timing))
			scene.skip_motion()
		await _close(scene)
	assert_gt(sides_seen, 0, "the sweep saw both sides hit in one turn")


# --- C6b: cause before effect --------------------------------------------------------------------------------

func test_a_hit_leaves_from_the_slice_under_its_needle_and_its_number_waits_for_it() -> void:
	var checked := 0
	for combat_seed in [3, 5, 9]:
		var scene := await _combat(&"collections_agent", 1.0, combat_seed)
		_live()
		var before: CombatState = scene.engine.state().duplicate_state()
		scene.end_turn()
		await _frames(1)
		var beats := ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup)
		for b in beats:
			if not ResolveBeats.is_hit(b) or int(b["source_slot"]) < 0 or b["phase"] == "turn_start":
				continue
			var v: WheelView = scene._host_view(StringName(String(b["source"])), before)
			if v == null or v.combatant.id != StringName(String(b["source"])):
				continue
			var spot: Vector2 = scene._source_spot(b, before)
			assert_eq(_shown_slot(v, spot), int(b["source_slot"]), "seed %d: the hit leaves from its landed slice" % combat_seed)
			# That slice is the one its needle's own resolution landed on.
			var found := false
			for e in scene._last_events:
				if String(e.get("type", "")) == "pointer" and StringName(String(e.get("owner", ""))) == StringName(String(b["source"])) \
						and int(e.get("pointer_index", -1)) == int(b["pointer_index"]) and int(e.get("slice_index", -1)) == int(b["source_slot"]):
					found = true
			assert_true(found, "seed %d: the source slice is a landing of that needle" % combat_seed)
			checked += 1
		scene.skip_motion()
		await _close(scene)
	assert_gt(checked, 0, "hits were checked")
	var scene := await _combat()
	_live()
	var state: CombatState = scene.engine.state()
	var hit := _hit(state.enemies[0].id, "enemy", state.player.id, 7, state.player.hp - 7)
	hit["source_slot"] = 0
	scene._play_beat(hit, state.duplicate_state(), state)
	for s in scene.fx_layer.sprites:
		if String(s["kind"]) in ["travel", "number", "impact"]:
			assert_gte(float(s.get("delay", 0.0)), CombatFxLayer.impact_seconds() - 0.0001, "%s shows only when the projectile arrives" % s["kind"])
	scene.skip_motion()
	await _close(scene)


## The slice under global `point` on `v` as it shows now (the replay shows the wheel as it
## landed, not the state's rotation after the turn start).
func _shown_slot(v: WheelView, point: Vector2) -> int:
	var local := point - v.global_position - v._center()
	var x := -(rad_to_deg(atan2(local.y, local.x)) + 90.0) / WheelView.DEG_PER_TICK
	return WheelMath.slice_at(posmod(roundi(x + v.shown_rotation()), RC.TICKS), v._shown().wheel.slice_count)


# --- C6c: one notation for a hit and its guard ---------------------------------------------------------------

func test_a_hit_meets_its_guard_in_one_notation_everywhere() -> void:
	var script: Script = load("res://scripts/ui/combat_scene.gd")
	var whole := _hit(&"e0", "enemy", &"player", 0, 50)
	whole.merge({"soaked": 8, "raw": 8, "blocked": 8}, true)
	var eq: Array = script.hit_equation(whole)
	assert_eq(eq.map(func(it: Dictionary) -> String: return String(it["text"])), ["8", "8", "0"], "sword 8 − shield 8 = 0")
	assert_eq(eq.map(func(it: Dictionary) -> int: return int(it["icon"])), [RC.SliceType.ATTACK, RC.SliceType.DEFEND, -1], "as glyphs")
	assert_eq(eq.map(func(it: Dictionary) -> String: return String(it["sep"])), ["", CombatFxLayer.EQ_MINUS, "="], "joined by minus and equals")
	var shield := whole.duplicate()
	shield.merge({"blocked": 0, "shielded": 8}, true)
	assert_eq(int(script.hit_equation(shield)[1]["icon"]), RC.SliceType.DEFEND, "a shield's soak wears the same glyph (one notation)")
	var part := _hit(&"e0", "enemy", &"player", 9, 41)
	part.merge({"soaked": 5, "raw": 14, "blocked": 5}, true)
	assert_eq((script.hit_equation(part) as Array).map(func(it: Dictionary) -> String: return String(it["text"])), ["14", "5", "9"], "sword 14 − shield 5 = 9")
	var dodge := _hit(&"e0", "enemy", &"player", 6, 50)
	dodge["kind"] = "evaded"
	assert_eq((script.hit_equation(dodge) as Array).map(func(it: Dictionary) -> String: return String(it["text"])), ["6", "6", "0"], "an evade: sword 6 − evade 6 = 0")
	assert_true((script.hit_equation(_hit(&"e0", "enemy", &"player", 6, 44)) as Array).is_empty(), "a hit no guard touched: its number says it")
	# The icon row under the HP speaks the same way.
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	pv.last_turn = "LAST TURN: -1 HP"
	pv.last_turn_icons = {"hit": 11, "soaked": 11, "evaded": 0, "hp": 0, "dealt": 0}
	var row := pv.icon_row_items()
	assert_eq(row.map(func(it: Dictionary) -> String: return String(it["text"])), ["11", "11", "0"], "the row: sword 11 − shield 11 = 0")
	assert_false(row.any(func(it: Dictionary) -> bool: return String(it["sep"]) == "arrow"), "no arrow formula")
	pv.last_turn_icons = {"hit": 6, "soaked": 5, "evaded": 0, "hp": 2, "dealt": 1}
	row = pv.icon_row_items()
	assert_eq(String(row[row.size() - 1]["sep"]), "·", "an HP change the hits don't explain follows after a dot")
	assert_string_contains(String(row[row.size() - 1]["text"]), "+3")
	await _close(scene)


func test_each_hits_number_spawns_fresh() -> void:
	var scene := await _combat()
	_live()
	var state: CombatState = scene.engine.state()
	var part := _hit(state.enemies[0].id, "enemy", state.player.id, 9, state.player.hp - 9)
	part.merge({"soaked": 5, "raw": 14, "blocked": 5, "source_slot": 0}, true)
	scene._play_beat(part, state.duplicate_state(), state)
	for s in scene.fx_layer.sprites:
		if String(s["kind"]) == "travel":
			assert_eq(String(s.get("raw", "")), "", "the raw number never morphs into what got through in the hub")
		if String(s["kind"]) == "number":
			assert_lt(int(s.get("icon", -1)), 0, "no separate guard number: the equation says it")
	scene.skip_motion()
	await _close(scene)


# --- C6d: side colours, a projectile seen ---------------------------------------------------------------------

func test_projectiles_wear_their_sides_colour_and_are_seen() -> void:
	var scene := await _combat(&"collections_agent", 1.0, 5)
	var s: CombatState = scene.engine.state()
	assert_eq(scene.hit_color(s.player.id, s), scene.PLAYER_HIT_COLOR, "mine in acid")
	for e in s.enemies:
		assert_eq(scene.hit_color(e.id, s), scene.ENEMY_HIT_COLOR, "%s in red" % e.display_name)
	for d in s.drones:
		assert_eq(scene.hit_color(d.id, s), scene.PLAYER_HIT_COLOR, "my drones in acid")
	assert_gte(Motion.seconds(&"hit_line") * CombatFxLayer.line_share(), FLIGHT_FLOOR, "a projectile is seen in flight long enough")
	assert_gt(CombatFxLayer.PROJECTILE_HEAD, 1.3, "its head is bigger")
	await _close(scene)


# --- C6e: no spoiler; preview = result ------------------------------------------------------------------------

func test_the_forecast_waits_for_a_spin_to_land() -> void:
	var scene := await _combat()
	_live()
	scene.engine.state().ram = scene.engine.state().max_ram
	scene._refresh(scene.engine.state())
	scene.respin()
	assert_true(scene.card_forecast_held(), "a respin's spin holds the forecast")
	for v in scene._views():
		assert_true((v as WheelView).intent.is_empty(), "no tag tells where it lands while it turns")
	var ok := await BoundedWait.until(get_tree(), func() -> bool: return not scene.card_forecast_held(), BoundedWait.motion_limit([&"wheel_respin"], 1.0))
	assert_true(ok, "the hold ends when the spin lands")
	assert_false((scene._player_view as WheelView).intent.is_empty(), "then the forecast shows")
	scene.respin()
	scene.skip_motion()
	assert_false(scene.card_forecast_held(), "a skip shows it at once")
	await _close(scene)


func test_the_tag_names_the_slices_the_resolve_lands_on() -> void:
	var checked := 0
	for enemy in [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]:
		for combat_seed in [1, 4, 7]:
			var scene := await _combat(enemy, 1.0, combat_seed)
			for turn in 3:
				var state: CombatState = scene.engine.state()
				if state.is_over():
					break
				var shown := {}
				for r in scene.engine.resolver.pointer_readouts(state, state.player):
					shown[int(r["pointer_index"])] = int(r["slice_index"])
				var title: String = scene._landing_title(state, state.player)["text"]
				scene.end_turn()
				var landed := {}
				for e in scene._last_events:
					if String(e.get("type", "")) == "pointer" and StringName(String(e.get("owner", ""))) == state.player.id and not landed.has(int(e["pointer_index"])):
						landed[int(e["pointer_index"])] = int(e["slice_index"])
				assert_eq(landed, shown, "%s seed %d: the tag (%s) names where the needles land" % [enemy, combat_seed, title])
				checked += 1
			await _close(scene)
	assert_gt(checked, 10)
	var lab := FileAccess.get_file_as_string("res://tools/design_lab/motion_lab.gd")
	assert_false(lab.contains("DEMO_HITS"), "the number demo plays a real SEND IT (its made-up hits contradicted the tag)")


# --- C6f: statuses as good / bad icons ------------------------------------------------------------------------

func test_statuses_show_whose_win_they_are() -> void:
	assert_true(WheelView.status_good_for_you(RC.Status.OVERCLOCKED, true))
	assert_false(WheelView.status_good_for_you(RC.Status.CORRUPTED, true), "CORRUPTED on your wheel is bad for you")
	assert_true(WheelView.status_good_for_you(RC.Status.CORRUPTED, false), "on theirs, good for you")
	assert_eq(WheelView.status_color(RC.Status.CORRUPTED, true), WheelView.LOSS_COLOR, "in red")
	assert_eq(WheelView.status_color(RC.Status.ENCRYPTED, true), WheelView.HP_COLOR, "in green")
	var script: Script = load("res://scripts/ui/combat_scene.gd")
	var chip: Dictionary = script.random_status_chip(RC.Status.CORRUPTED, true)
	assert_eq(int(chip["glyph"]), RC.Status.CORRUPTED, "which status (a drawn StatIcon since art pass W3)")
	assert_string_contains(String(chip["text"]), tr("CORRUPTED"))
	assert_eq(chip["color"], script.CHIP_LOSS, "bad for you: red")
	assert_string_contains(String(chip["tooltip"]), "Bad for you")
	var scene := await _combat()
	_live()
	var state: CombatState = scene.engine.state()
	var pv: WheelView = scene._player_view
	pv.shown_state = state.player.duplicate_state()
	var b := {"kind": "status", "event_index": 0, "phase": "resolve", "pass": "statuses", "source": state.enemies[0].id, "pointer_index": 0,
		"target": state.player.id, "amount": 0, "crit": false, "hp_after": -1, "slot": 1, "status": RC.Status.CORRUPTED, "tier": -1,
		"soaked": 0, "host": &"", "source_slot": 0, "source_tier": -1, "raw": 0, "blocked": 0, "shielded": 0, "side": "enemy"}
	scene._play_beat(b, state.duplicate_state(), state)
	var stamps: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "stamp")
	assert_eq(stamps.size(), 1, "the status lands as its glyph")
	if not stamps.is_empty():
		assert_eq(stamps[0]["color"], WheelView.LOSS_COLOR, "in red on your wheel")
	state.player.wheel.slice_statuses[1] = RC.Status.CORRUPTED
	assert_string_contains(pv._slice_label(1), "Bad for you", "the slice says so on hover")
	scene.skip_motion()
	await _close(scene)


# --- C6g: the break and VICTORY apart --------------------------------------------------------------------------

func test_victory_stands_clear_of_the_beaten_wheel_and_defeated_wears_its_colour() -> void:
	for scale in SCALES:
		var scene := await _combat(&"collections_agent", scale)
		var ev: WheelView = scene._enemy_views.values()[0]
		var word := tr("VICTORY")
		var at: Vector2 = scene.end_word_spot(true)
		var fs: int = scene.end_word_size(true, word)
		var r := CombatFxLayer.word_rect(at, word, fs if fs > 0 else roundi(CombatFxLayer.WORD_FONT * Settings.text_scale))
		assert_false(r.intersects(ev.wheel_rect()), "x%.1f: VICTORY never covers the breaking wheel (%s vs %s)" % [scale, r, ev.wheel_rect()])
		assert_true(ev.get_global_rect().grow(1.0).encloses(r), "x%.1f: on the enemy's side" % scale)
		assert_eq(ev.defeated_color(), ev.wheel_color, "DEFEATED wears the enemy's own colour")
		await _close(scene)


# --- C6h: RAM floats -------------------------------------------------------------------------------------------

func test_ram_says_refill_and_never_floats_a_refusal() -> void:
	for scale in SCALES:
		var scene := await _combat(&"collections_agent", scale)
		_live()
		var bar: RamBar = scene.ram_note
		bar.float_spend(4)
		assert_eq(bar.spend_text, tr("-%d RAM") % 4)
		for p in [0.0, 0.25, 0.5, 1.0]:
			bar.spend_p = p
			assert_false(bar.spend_rect().intersects(bar.label_rect()), "x%.1f p %.2f: the float keeps off the RAM label" % [scale, p])
		bar.flash_short(4)
		assert_eq(bar.spend_text, "", "x%.1f: a refusal floats no loss (NEED / HAVE says it)" % scale)
		bar.hold(2)
		bar.play_refill()
		assert_string_contains(bar.spend_text, "+", "x%.1f: the refill floats +N RAM" % scale)
		assert_eq(bar.spend_color, Palette.NET_CYAN)
		bar.finish_motion()
		await _close(scene)


# --- C7: the run's screens ------------------------------------------------------------------------------------

func test_loot_not_taken_falls_before_the_page_leaves() -> void:
	var scene := await _netrun()
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	PageTransition.settle(scene)
	await _frames(3)
	_live()
	var stickers: Control = scene._panel.find_child("Stickers", true, false)
	scene.choose_reward(0)
	assert_true(scene.loot_leaving(), "the loot page stays while the rest falls")
	assert_not_null(scene._panel.find_child("Stickers", true, false), "the loot page is still up (not the route)")
	var ok := await BoundedWait.until(get_tree(), func() -> bool: return not scene.loot_leaving(), BoundedWait.motion_limit([&"loot_reject"]))
	assert_true(ok, "the page leaves once they have fallen")
	assert_eq(FlightFx.active_count(scene), 0, "no loot is left flying over the next page")
	assert_false(is_instance_valid(stickers) and stickers.is_inside_tree(), "the loot page is gone")
	await _close(scene)


func test_the_loot_tag_fits_its_window_under_pseudolocalisation() -> void:
	_pseudo(true)
	var scene := await _netrun()
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	PageTransition.settle(scene)
	await _frames(3)
	var tag: Array[Node] = scene._panel.find_children("*", "GraffitiTag", true, false)
	assert_eq(tag.size(), 1)
	if not tag.is_empty():
		var t := tag[0] as GraffitiTag
		var win: Rect2 = scene.loot_window_rect(t)
		assert_true(win.grow(0.5).encloses(t.get_global_rect()), "the tag stays in its window")
		assert_lte(t.words_width() + GraffitiTag.LEFT + GraffitiTag.MASCOT_ROOM, t.size.x + 0.5, "the mascot sits after the words")
	await _close(scene)


func test_focus_tips_keep_a_readable_width() -> void:
	assert_gte(FocusTip.FOLD_MIN, 20, "a tip never folds to a word a line")
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/focus_tip.gd")
	assert_true(src.contains("c is ModemSign"), "tips keep off the MODEM sign")


func test_buy_keeps_off_the_cards_text_while_it_flaps() -> void:
	var card := ZineCard.new("TRACER", -1, "ATK or CRIT slice strips 1 resistance from the target on a Perfect.", 0)
	card.price = 76
	card.size = Vector2(120, 150)
	add_child_autofree(card)
	card.with_buy()
	await _frames(1)
	var reach := card.buy_button.size.x * 0.5 * absf(sin(deg_to_rad(Motion.amplitude(&"note_flap"))))
	assert_lte(card.size.y - card.buy_room(), card.buy_button.position.y - reach + 0.5, "the text's foot is above the sticker's flapped corner")


func test_a_refusal_under_a_tag_wraps_at_its_dot() -> void:
	var lines := HudStats.refusal_lines("NEED 53 · HAVE 5", 40.0, 20)
	assert_eq(lines, PackedStringArray(["NEED 53", "HAVE 5"]), "wider than its tag: two lines")
	assert_eq(HudStats.refusal_lines("NEED 53 · HAVE 5", 2000.0, 20).size(), 1, "one when it fits")


func test_an_event_types_its_story_quickly_on_a_panel_its_size() -> void:
	assert_lte(Motion.amplitude(&"event_type"), 1.0, "the whole story types within a second")
	var h := _holder()
	var label := Label.new()
	label.text = "A bricked implant hums in the gutter, its last owner long gone. ".repeat(6)
	(h[0] as Control).add_child(label)
	_live()
	Settings.set_subtitle_typing(true)
	await _frames(1)
	var secs := Typing.type_in(label, &"event_type")
	assert_gt(secs, 0.0, "it types")
	assert_lte(secs, Motion.amplitude(&"event_type") + 0.001, "within the cap (it took %.1f s a char at a time)" % (label.get_total_character_count() * Motion.seconds(&"dispatch_type")))
	Typing.finish(label)
	var src := FileAccess.get_file_as_string("res://scripts/ui/netrun_scene.gd")
	assert_true(src.contains("Typing.type_in(text, &\"event_type\")"), "the event page uses it")
	assert_true(src.contains("_fit_paper"), "the paper is as tall as its words (art pass W8c)")


func test_new_words_are_exported_once() -> void:
	var csv := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for key in ["ON A RANDOM SLICE:", "Good for you: %s", "Bad for you: %s", "+%d RAM", "CONTINUE"]:
		assert_true(csv.contains(key), "%s is exported for translation" % key)
