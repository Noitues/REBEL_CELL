extends GutTest
## Animation pass ANIM-R3 (the third fix batch), combat, input and screens (DECISIONS
## "Animation pass — ANIM-R3 combat, input and screens"): drone and satellite numbers for
## every class against every enemy (A1); the raid playout, ambient typing and subtitles let
## presses that work the screen through (A2, A3); a consumed pad press switches the prompts
## (A4); the result never shows mid-roll, under load (A5); SEND IT legibility: the hit's
## outcome where it struck, ALL BLOCKED on impact, the forecast kept and ticked, the aim's
## multiplier, one hit at a time into the HP, guards as glyphs, the icon row, the real
## wheel breaking with a skull, the next step's action after a win, the card gone before
## its spin, the words (A6); the Mainframe's first focus and sign, flights of fresh copies,
## loot falling within its window, the empty-set mark, the swap chips' pictogram, every
## event choice's icons, discards off the stickers (A7).

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const CLASSES: Array[StringName] = [&"botnet", &"breaker", &"ghost", &"hivemind", &"overclocker", &"phantom", &"rigger", &"wrecker"]
const RING := &"rank:1"

var _scale: float = 1.0
var _reduce: bool = false
var _typing: bool = true
var _pad: bool = false


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
	RunManager.save_slot = "gut_anim_r3"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
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


func _key(k: Key, pressed: bool = true) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = pressed
	return e


func _pad_button(b: JoyButton, pressed: bool = true) -> InputEventJoypadButton:
	var e := InputEventJoypadButton.new()
	e.button_index = b
	e.pressed = pressed
	return e


func _click(at: Vector2, pressed: bool = true) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = pressed
	e.position = at
	e.global_position = at
	return e


func _action(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


## Every enemy in content the combat resolver knows (as test_anim_r1_combat's sweep).
func _enemy_ids(lookup: ContentLookup) -> Array[StringName]:
	var out: Array[StringName] = []
	for id in RunManager.lookup().ids_of_class(&"EnemyData"):
		if lookup.has(id):
			out.append(id)
	out.sort()
	return out


# --- A1: numbers for every class against every enemy --------------------------------------------------------

func test_every_hp_change_has_one_number_of_its_size_for_every_class_and_enemy() -> void:
	var scene := await _combat()
	var enemies := _enemy_ids(scene.engine.resolver.lookup)
	var checked := [0]
	var late_drones := [0]
	var failures: Array[String] = []
	for cls in CLASSES:
		for enemy in enemies:
			scene.engine.start_fight(cls, [enemy] as Array[StringName], 3, RING)
			for turn in 3:
				if scene.engine.state().is_over():
					break
				var before: CombatState = scene.engine.state().duplicate_state()
				scene.end_turn()
				var after: CombatState = scene.engine.state()
				var beats := ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup)
				var hp := {}
				var shown := {}
				var start_hp := {}
				for c in [before.player] + before.enemies + before.drones:
					hp[c.id] = c.hp
					start_hp[c.id] = c.hp
					shown[c.id] = 0
				for b in beats:
					var id := StringName(String(b["target"]))
					if b["kind"] == "spawn":
						hp[id] = int(b["hp_after"])
						start_hp[id] = int(b["hp_after"])
						shown[id] = 0
						continue
					if not (b["kind"] in ResolveBeats.HP_KINDS) or int(b["hp_after"]) < 0:
						continue
					var change := int(b["hp_after"]) - int(hp.get(id, 0))
					hp[id] = int(b["hp_after"])
					var nums: Array = scene.numbers_for(b, before, after).filter(func(n: Dictionary) -> bool: return n.has("hp"))
					if change == 0:
						if not nums.is_empty():
							failures.append("%s vs %s: a number for no HP change" % [cls, enemy])
						continue
					if before.get_combatant(id) == null:
						late_drones[0] += 1
					if nums.size() != 1:
						failures.append("%s vs %s turn %d: %s's HP change %d has %d numbers" % [cls, enemy, turn, id, change, nums.size()])
						continue
					var n: Dictionary = nums[0]
					var signed_hp := -int(n["hp"]) if String(b["kind"]) != "heal" else int(n["hp"])
					if signed_hp != change:
						failures.append("%s vs %s: %s's number %d is not its HP change %d" % [cls, enemy, id, signed_hp, change])
					shown[id] = int(shown.get(id, 0)) + signed_hp
					checked[0] += 1
				for id in hp:
					var from := int(start_hp.get(id, hp[id]))
					if int(shown.get(id, 0)) != int(hp[id]) - from:
						failures.append("%s vs %s: %s's numbers add to %d, its HP rolled %d" % [cls, enemy, id, int(shown.get(id, 0)), int(hp[id]) - from])
	assert_eq(failures.size(), 0, "every HP change has exactly one number of its size (A1: drones deployed mid-resolve had none):\n" + "\n".join(failures.slice(0, 30)))
	assert_gt(checked[0], 500, "the sweep saw many HP changes (%d)" % checked[0])
	assert_gt(late_drones[0], 0, "and HP changes on drones deployed during the resolve (Botnet, Hivemind)")
	await _close(scene)


func test_a_drone_deployed_mid_resolve_shows_its_hit_and_its_number() -> void:
	var scene := await _combat()
	_live()
	var found := false
	for enemy in [&"collections_agent", &"compliance_officer", &"care_swarm", &"triage_unit"]:
		for combat_seed in range(1, 12):
			if found:
				break
			Motion.force_live = false
			scene.engine.start_fight(&"botnet", [enemy] as Array[StringName], combat_seed, RING)
			for turn in 4:
				if found or scene.engine.state().is_over():
					break
				var before: CombatState = scene.engine.state().duplicate_state()
				scene.end_turn()
				var after: CombatState = scene.engine.state()
				for b in ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup):
					var t := StringName(String(b["target"]))
					var s := StringName(String(b["source"]))
					var late_target := before.get_combatant(t) == null and after.get_combatant(t) != null and ResolveBeats.changes_hp(b)
					var late_source := s != &"" and before.get_combatant(s) == null and after.get_combatant(s) != null and ResolveBeats.is_hit(b)
					if not (late_target or late_source):
						continue
					found = true
					Motion.force_live = true
					scene.skip_motion()
					scene._play_beat(b, before, after)
					if late_source:
						var lines: Array = scene.fx_layer.sprites.filter(func(sp: Dictionary) -> bool: return sp["kind"] == "line")
						assert_eq(lines.size(), 1, "a drone deployed this turn fires its projectile")
						if not lines.is_empty():
							assert_eq(lines[0]["color"], scene.PLAYER_HIT_COLOR, "in the operative's side's colour")
					if late_target:
						var nums: Array = scene.fx_layer.sprites.filter(func(sp: Dictionary) -> bool: return sp["kind"] in ["number", "travel"])
						assert_gt(nums.size(), 0, "a drone deployed this turn shows its HP change")
					scene.skip_motion()
					break
	assert_true(found, "the search met a drone deployed and hit (or hitting) in the same resolve")
	await _close(scene)


# --- A2: the raid playout ------------------------------------------------------------------------------------

func _playout() -> Array:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var counter := Counter.new()
	holder.add_child(counter)
	var panel := RaidPlayoutPanel.new()
	holder.add_child(panel)
	var events: Array[Dictionary] = []
	for step in range(1, 5):
		events.append({"type": "step", "step": step, "text": "Step %d." % step})
		events.append({"type": "move", "step": step, "threat": &"t0", "from": &"a", "to": &"b", "text": "A threat moves."})
	events.append({"type": "raid_end", "text": "Raid over."})
	return [holder, counter, panel, events]


func test_the_raid_playout_lets_presses_that_work_the_screen_through() -> void:
	_live()
	var p := _playout()
	var counter: Counter = p[1]
	var panel: RaidPlayoutPanel = p[2]
	panel.play(p[3], false)
	await _frames(2)
	var skip := panel.find_child("Skip", true, false) as Button
	var two := panel.find_child("Speed2x", true, false) as Button
	assert_not_null(two, "the speed buttons are named")
	skip.grab_focus()
	await _frames(1)
	# A focus move passes (keys and the pad reach Skip and 2x / 4x) and skips no step.
	var clock := panel.clock()
	var got := counter.got
	get_viewport().push_input(_key(KEY_LEFT))
	assert_eq(counter.got, got + 1, "a focus move passes on")
	assert_almost_eq(panel.clock(), clock, 0.0001, "and skips no step")
	await _frames(1)
	two.grab_focus()
	await _frames(1)
	get_viewport().push_input(_key(KEY_ENTER))
	get_viewport().push_input(_key(KEY_ENTER, false))
	await _frames(1)
	assert_almost_eq(panel.speed, 2.0, 0.001, "accept on the focused 2x is 2x's")
	# The Settings key passes too.
	got = counter.got
	get_viewport().push_input(_key(KEY_ESCAPE))
	assert_eq(counter.got, got + 1, "the Settings key passes on")
	# Any other press skips one step and is consumed.
	panel._clock = 0.0
	var next := panel._next_at
	got = counter.got
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_almost_eq(panel._clock, next, 0.0001, "another press ends the step's motion")
	assert_eq(counter.got, got, "and is consumed")
	# A click on a usable button is the button's.
	got = counter.got
	var at := skip.get_global_rect().get_center()
	assert_true(panel._for_own_button(_click(at)), "a click on Skip is Skip's")
	Motion.set_speed(1.0)


func test_the_raid_playout_leaves_presses_to_an_open_pause_menu() -> void:
	_live()
	var p := _playout()
	var holder: Control = p[0]
	var panel: RaidPlayoutPanel = p[2]
	panel.play(p[3], false)
	await _frames(2)
	var menu := PauseMenu.new()
	holder.add_child(menu)
	await _frames(1)
	assert_true(MotionSkip.pause_open(panel), "an open pause menu is seen")
	panel._clock = 0.0
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_eq(panel._clock, 0.0, "no step is skipped while the menu is open: its presses are its own")
	menu.queue_free()
	await _frames(1)
	assert_false(MotionSkip.pause_open(panel))


# --- A3: typing over menus ---------------------------------------------------------------------------------

## A holder with a press counter behind the rest (it sees a press only if nothing before
## it consumed it), a typing label and a button.
func _typing_page() -> Array:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var counter := Counter.new()
	holder.add_child(counter)
	var label := Label.new()
	label.text = "PIRATE RADIO: the grid is listening, and it keeps what it hears. Stay low."
	label.position = Vector2(40, 40)
	label.size = Vector2(500, 40)
	holder.add_child(label)
	var button := Button.new()
	button.text = "City Grid"
	button.position = Vector2(40, 200)
	button.size = Vector2(200, 50)
	holder.add_child(button)
	var pressed := [0]
	button.pressed.connect(func() -> void: pressed[0] += 1)
	return [holder, counter, label, button, pressed]


func test_typing_passes_presses_that_work_a_button_and_eats_those_at_its_words() -> void:
	_live()
	Settings.set_subtitle_typing(true)
	var t := _typing_page()
	var counter: Counter = t[1]
	var label: Label = t[2]
	var button: Button = t[3]
	var pressed: Array = t[4]
	await _frames(1)
	# A click on the button while the radio types: the words show whole and the click passes
	# on to the button (A3: it was eaten, so the first click on City Grid did nothing).
	assert_gt(Typing.type_in(label, &"radio_type"), 0.0, "the radio types")
	var got := counter.got
	var at := button.get_global_rect().get_center()
	assert_true(MotionSkip.works_ui(_click(at), label), "a click on a usable button works the screen")
	get_viewport().push_input(_click(at), true)
	assert_false(Typing.typing(label), "the words show whole")
	assert_eq(counter.got, got + 1, "and the click passes on to the button")
	get_viewport().push_input(_click(at, false), true)
	# Accept on the focused button passes too, and the button takes it.
	Typing.type_in(label, &"radio_type")
	button.grab_focus()
	await _frames(1)
	var before_press: int = pressed[0]
	get_viewport().push_input(_key(KEY_ENTER))
	get_viewport().push_input(_key(KEY_ENTER, false))
	await BoundedWait.frozen_frames(get_tree(), 1)  # ANIM-R6 D9: the press ended it, not the clock
	assert_false(Typing.typing(label))
	assert_eq(pressed[0], before_press + 1, "accept on the focused button works while the words type")
	# A press aimed at the words (a click on them) shows them and is consumed.
	Typing.type_in(label, &"radio_type")
	got = counter.got
	get_viewport().push_input(_click(label.get_global_rect().get_center()), true)
	assert_false(Typing.typing(label), "a click on the words shows them whole")
	assert_eq(counter.got, got, "and does nothing else")
	# So does a key that works nothing.
	Typing.type_in(label, &"radio_type")
	button.release_focus()
	got = counter.got
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(Typing.typing(label))
	assert_eq(counter.got, got, "a stray key is consumed")


func test_a_subtitle_over_a_menu_passes_a_click_on_a_button() -> void:
	_live()
	Settings.set_subtitle_typing(true)
	var t := _typing_page()
	var counter: Counter = t[1]
	var button: Button = t[3]
	await _frames(1)
	Dialogue.say(RC.Voice.DISPATCH, "Jacking you in. The rack is two hops out: keep your Heat down and your head lower.", 0.0)
	await _frames(1)
	if not Dialogue.typing():
		pass_test("the subtitle shows whole at once here")
		return
	var got := counter.got
	var at := button.get_global_rect().get_center()
	get_viewport().push_input(_click(at), true)
	get_viewport().push_input(_click(at, false), true)
	assert_false(Dialogue.typing(), "the subtitle shows whole")
	assert_eq(counter.got, got + 1, "and the click on the button passes on (Dialogue lines over menus ate it)")
	Dialogue.say(RC.Voice.DISPATCH, "Jacking you in. The rack is two hops out: keep your Heat down and your head lower.", 0.0)
	await _frames(1)
	if Dialogue.typing():
		got = counter.got
		get_viewport().push_input(_key(KEY_SEMICOLON))
		assert_eq(counter.got, got, "a press that works nothing is the subtitle's")


func test_the_first_press_on_the_city_grid_works_while_the_radio_types() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var counter := Counter.new()
	holder.add_child(counter)
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.show_hq()
	await _frames(4)
	PageTransition.settle(hq)
	await _frames(1)
	_live()
	Settings.set_subtitle_typing(true)
	var grid: Array = hq._panel.find_children("*", "Button", true, false).filter(func(b: Node) -> bool: return String((b as Button).text).begins_with(tr("City Grid")))
	assert_eq(grid.size(), 1, "the HQ has its City Grid button")
	if grid.is_empty():
		return
	var radio: Label = null
	for n in hq._panel.find_children("*", "Label", true, false):
		if (n as Label).is_visible_in_tree() and Typing.type_in(n as Label, &"radio_type") > 0.0:
			radio = n
			break
	assert_not_null(radio, "the pirate radio types in on the HQ page")
	# A click on City Grid passes on to it (the typing only shows its words).
	var got := counter.got
	var at := (grid[0] as Control).get_global_rect().get_center()
	get_viewport().push_input(_click(at), true)
	assert_false(Typing.typing(radio), "the radio's words show whole")
	assert_eq(counter.got, got + 1, "the click on City Grid is not eaten")
	get_viewport().push_input(_click(at, false), true)
	await _frames(1)
	# Accept on City Grid (the pad's A) opens the Grid at the first press.
	if String(hq.panel_name) != "grid":
		Typing.type_in(radio, &"radio_type")
		(grid[0] as Control).grab_focus()
		await _frames(1)
		get_viewport().push_input(_key(KEY_ENTER))
		get_viewport().push_input(_key(KEY_ENTER, false))
		await _frames(2)
	assert_eq(String(hq.panel_name), "grid", "the first press on City Grid opens it (A3: the typing ate it)")
	await _close(hq)


# --- A4: a consumed pad press switches the prompts ---------------------------------------------------------

func test_a_pad_press_that_ends_a_motion_switches_the_prompts() -> void:
	_live()
	Settings.set_subtitle_typing(true)
	Settings.set_pad_active(false)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var label := Label.new()
	label.text = "The grid is listening, and it keeps what it hears."
	holder.add_child(label)
	await _frames(1)
	assert_gt(Typing.type_in(label), 0.0)
	get_viewport().push_input(_pad_button(JOY_BUTTON_Y))
	assert_false(Typing.typing(label), "the pad press ends the typing (and is consumed)")
	assert_true(Settings.pad_active, "and the prompts switch to the pad all the same (A4)")
	Typing.type_in(label)
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(Settings.pad_active, "a key ending a motion switches them back")


# --- A5: the result never shows mid-roll ------------------------------------------------------------------

func test_this_turn_never_shows_while_an_hp_counter_rolls_under_load() -> void:
	var scene := await _combat(&"collections_agent", 1.0, 5)
	_live()
	var checked := 0
	for turn in 4:
		if scene.engine.state().is_over():
			break
		scene.end_turn()
		# Load: every frame of the replay stalls a little (a loaded machine's long frames).
		var seen := [false]
		var ok := await BoundedWait.until(get_tree(), func() -> bool:
			OS.delay_msec(12)
			for v in scene._views():
				var wv := v as WheelView
				if wv.caption != "" and not seen[0]:
					seen[0] = true
					assert_false(scene.fx_layer.travelling(), "no number is still on its way when THIS TURN shows")
					assert_false(wv.hp_rolling(), "%s: no HP counter still rolls when THIS TURN shows" % wv.combatant.display_name)
			return seen[0] or scene._seq == null, BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
		assert_true(ok)
		if seen[0]:
			checked += 1
		scene.skip_motion()
	assert_gt(checked, 0, "THIS TURN was seen")
	await _close(scene)


func test_finish_hp_ends_a_roll_on_its_value() -> void:
	var scene := await _combat()
	_live()
	var pv: WheelView = scene._player_view
	var hp := float(pv.combatant.hp)
	pv.anim_hp = hp
	pv.play_hp(hp - 7.0)
	assert_true(pv.hp_rolling())
	assert_true(pv.finish_hp(), "a roll was running")
	assert_almost_eq(pv.shown_hp(), hp - 7.0, 0.001, "it ends on its value")
	assert_false(pv.hp_rolling())
	await _close(scene)


# --- A6: SEND IT legibility --------------------------------------------------------------------------------

func _base(state: CombatState, enemy: CombatantState) -> Dictionary:
	return {"event_index": 0, "phase": "resolve", "pass": "offensive", "source": enemy.id, "pointer_index": 0,
		"target": state.player.id, "crit": false, "slot": -1, "status": 0, "tier": -1, "host": &"", "source_slot": 0, "source_tier": -1}


func test_a_hit_soaked_whole_shows_zero_with_a_shield_where_it_struck_and_all_blocked_then() -> void:
	var scene := await _combat()
	_live()
	var state: CombatState = scene.engine.state()
	var before := state.duplicate_state()
	var enemy: CombatantState = state.enemies[0]
	var pv: WheelView = scene._player_view
	var hit := _base(state, enemy)
	hit.merge({"kind": "damage", "amount": 0, "soaked": 6, "raw": 6, "blocked": 6, "shielded": 0, "hp_after": state.player.hp,
		"final_stamp": tr("ALL BLOCKED"), "final_hold": 1.0}, true)
	scene._play_beat(hit, before, state)
	var lines: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "line")
	assert_eq(lines.size(), 1, "the enemy's hit flies")
	if not lines.is_empty():
		assert_eq(lines[0]["color"], scene.ENEMY_HIT_COLOR, "red")
		assert_eq(lines[0]["to"], pv.hp_ring_spot(), "to the operative's HP ring")
	var marks: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "impact")
	assert_eq(marks.size(), 1, "its outcome shows where it struck")
	if not marks.is_empty():
		assert_eq(String(marks[0]["text"]), "0", "0 got through")
		assert_eq(int(marks[0]["icon"]), RC.SliceType.DEFRAG, "with the shield glyph")
		assert_eq(marks[0]["at"], pv.hp_ring_spot(), "at the impact")
		assert_almost_eq(float(marks[0]["delay"]), CombatFxLayer.impact_seconds(), 0.001, "on impact")
	var tags: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "tag")
	assert_eq(tags.size(), 1, "ALL BLOCKED stamps")
	if not tags.is_empty():
		assert_eq(String(tags[0]["text"]), tr("ALL BLOCKED"))
		assert_eq(String(tags[0]["icon"]), CombatFxLayer.GUARD_NULL, "with its shield-over-empty-set mark")
		assert_almost_eq(float(tags[0]["delay"]), CombatFxLayer.impact_seconds(), 0.001, "at the impact moment, not later")
	# ANIM-R4 C6c (expectation changed): the guard's part is in the impact's equation (sword 6
	# − shield 6 = 0), not a separate number under the hub.
	if not marks.is_empty():
		var texts: Array = (marks[0]["items"] as Array).map(func(it: Dictionary) -> String: return String(it["text"]))
		assert_eq(texts, ["6", "6", "0"], "sword 6 − shield 6 = 0")
	for s in scene.fx_layer.sprites:
		assert_false(String(s.get("text", "")).contains(tr("BLOCKED")) and s["kind"] == "number", "no BLOCKED word badge")
	scene.skip_motion()
	await _close(scene)


func test_all_blocked_is_marked_on_the_last_hits_impact() -> void:
	for combat_seed in [1, 2, 3, 5, 7, 9, 11, 13]:
		var scene := await _combat(&"collections_agent", 1.0, combat_seed)
		_live()
		for turn in 4:
			if scene.engine.state().is_over():
				break
			var before: CombatState = scene.engine.state().duplicate_state()
			scene.end_turn()
			var beats := ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup)
			var stamps: Dictionary = scene.result_stamps(beats, before)
			for id in stamps:
				var marked: bool = scene._impact_stamped.has(id)
				assert_eq(marked, String(stamps[id]) == tr("ALL BLOCKED"), "ALL BLOCKED stamps on impact; NO DAMAGE at the result")
			scene.skip_motion()
		await _close(scene)


func test_the_forecast_stays_through_the_replay_and_every_line_ticks() -> void:
	var ticked := 0
	for enemy in [&"collections_agent", &"compliance_officer", &"geostationary_guard", &"care_swarm"]:
		var scene := await _combat(enemy, 1.0, 5)
		_live()
		var tags := {}
		for v in scene._views():
			tags[(v as WheelView).combatant.id] = (v as WheelView).intent.duplicate(true)
		scene.end_turn()
		for v in scene._views():
			var wv := v as WheelView
			if (tags[wv.combatant.id] as Dictionary).is_empty():
				continue
			assert_true(wv.replaying, "the replay plays")
			assert_false(wv.replay_tag.is_empty(), "%s: the forecast stays up (A6b)" % wv.combatant.display_name)
			assert_eq(String(wv.replay_tag.get("text", "")), String(tags[wv.combatant.id].get("text", "")), "the same forecast")
			assert_true(wv.intent_rect().has_area(), "and is drawn where it was")
		# Every line ticks by the time the result holds.
		await BoundedWait.until(get_tree(), func() -> bool:
			for v in scene._views():
				if (v as WheelView).caption != "":
					return true
			return scene._seq == null, BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
		await _frames(2)
		for v in scene._views():
			var wv := v as WheelView
			if wv.replay_tag.is_empty():
				continue
			var chips: Array = wv.replay_tag.get("chips", [])
			for i in chips.size():
				assert_true(wv.tag_ticks.has(i), "%s: '%s' ticked once the result holds" % [enemy, chips[i]["text"]])
				ticked += 1
			assert_true(wv.caption == tr("THIS TURN"), "the tape reads THIS TURN once the result holds")
		scene.skip_motion()
		for v in scene._views():
			assert_true((v as WheelView).replay_tag.is_empty(), "a skip drops the held forecast")
		await _close(scene)
	assert_gt(ticked, 4, "the sweep ticked forecast lines")


func test_forecast_ticks_follow_their_beats() -> void:
	var beats: Array[Dictionary] = [
		{"kind": "damage", "phase": "resolve", "source": &"enemy_0", "target": &"player", "amount": 4, "soaked": 0, "hp_after": 36},
		{"kind": "block", "phase": "resolve", "source": &"player", "target": &"player", "amount": 3, "soaked": 0, "hp_after": -1},
	]
	var times := PackedFloat32Array([0.4, 1.0])
	var timing := {"impact": 0.15, "settle": 0.6, "absorb": 0.3}
	var chips := [
		{"text": "HITS YOU 4", "beats": ForecastTicks.filter(["damage", "evaded"], &"enemy_0", &"player")},
		{"text": "YOU TAKE 4 HP", "beats": ForecastTicks.filter(ResolveBeats.HP_KINDS, &"", &"player", true)},
		{"text": "+3 BLOCK", "beats": ForecastTicks.filter(["block", "damage"], &"", &"player")},
		{"text": "RAM +4"},
	]
	var t := ForecastTicks.schedule(chips, beats, times, timing, 2.0)
	assert_almost_eq(float(t[0]), 0.4 + 0.15, 0.001, "a hit's line ticks on its impact")
	assert_almost_eq(float(t[1]), 0.4 + 0.15 + 0.6, 0.001, "an HP line once its number has settled")
	assert_almost_eq(float(t[2]), 1.0, 0.001, "a guard line when it lands")
	assert_almost_eq(float(t[3]), 2.0, 0.001, "a line no beat makes ticks when the result holds")


func test_the_hit_shows_its_aim() -> void:
	var scene := await _combat()
	var state: CombatState = scene.engine.state()
	var enemy: CombatantState = state.enemies[0]
	var slot := -1
	var base := 0
	for i in state.player.wheel.slot_slice_ids.size():
		var sd := scene.engine.content(state.player.wheel.slot_slice_ids[i]) as SliceData
		if sd != null and sd.slice_type == RC.SliceType.SHIM and sd.base_output >= 2:
			slot = i
			base = sd.base_output
			break
	assert_gt(slot, -1, "the operative has a SHIM slice")
	var hit := _base(state, enemy)
	hit.merge({"kind": "damage", "source": state.player.id, "target": enemy.id, "amount": base / 2, "soaked": 0, "raw": base / 2,
		"source_slot": slot, "source_tier": RC.PrecisionTier.WEAK, "hp_after": enemy.hp - base / 2}, true)
	var ride: Dictionary = scene.ride_for(hit, state)
	assert_eq(String(ride["from"]), str(base), "the slice's own value first (%d)" % base)
	assert_eq(String(ride["label"]), str(base / 2), "then what it deals, a whole number (ANIM-R6 A4: never a fraction)")
	hit["source_tier"] = RC.PrecisionTier.PERFECT
	hit["raw"] = base + base / 2
	ride = scene.ride_for(hit, state)
	assert_gt(float(ride["scale"]), 1.0, "a PERFECT hit's number rides bigger")
	hit["source_tier"] = RC.PrecisionTier.GOOD
	hit["raw"] = base
	ride = scene.ride_for(hit, state)
	assert_eq(String(ride["from"]), "", "a GOOD hit rides its plain number")
	await _close(scene)


func test_a_hit_launches_only_once_the_last_number_has_entered_the_hp() -> void:
	for enemy in [&"collections_agent", &"compliance_officer", &"geostationary_guard", &"care_swarm"]:
		for combat_seed in [1, 5, 9]:
			var scene := await _combat(enemy, 1.0, combat_seed)
			_live()
			for turn in 3:
				if scene.engine.state().is_over():
					break
				var before: CombatState = scene.engine.state().duplicate_state()
				scene.end_turn()
				scene.skip_motion()
				var beats := ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup)
				var sch: Dictionary = scene.sequence_schedule(beats)
				var times: PackedFloat32Array = sch["times"]
				var timing: Dictionary = scene.beat_timing()
				var ready := -INF
				for k in beats.size():
					var b := beats[k]
					if not ResolveBeats.flies(b):
						continue
					assert_true(times[k] >= ready - 0.0001, "%s seed %d: a hit waits for the last one's number to enter the HP (%.2f < %.2f)" % [enemy, combat_seed, times[k], ready])
					ready = maxf(ready, times[k] + ResolveBeats.arrive_after(b, timing))
			await _close(scene)


func test_one_hp_roll_per_hit() -> void:
	var scene := await _combat()
	_live()
	var pv: WheelView = scene._player_view
	var hp := float(pv.combatant.hp)
	pv.anim_hp = hp
	pv.play_hp(hp - 5.0)
	await _frames(1)
	pv.play_hp(hp - 9.0)
	assert_almost_eq(pv.shown_hp(), hp - 5.0, 0.001, "the first roll ends on its own value before the second starts (no value no hit left)")
	pv.finish_hp()
	await _close(scene)


func test_the_icon_row_under_the_hp_says_the_last_turn() -> void:
	var before := CombatState.new()
	before.player = CombatantState.new()
	before.player.id = &"player"
	before.player.is_player = true
	before.player.hp = 40
	before.player.wheel = WheelState.new()
	var foe := CombatantState.new()
	foe.id = &"enemy_0"
	foe.hp = 30
	foe.wheel = WheelState.new()
	before.enemies = [foe]
	var events: Array[Dictionary] = [
		{"type": "resolve_start"},
		{"type": "damage", "attacker": "enemy_0", "target": "player", "amount": 6, "blocked": 5, "shielded": 0, "hp_damage": 1},
		{"type": "damage", "attacker": "player", "target": "enemy_0", "amount": 4, "blocked": 4, "shielded": 0, "hp_damage": 0},
		{"type": "turn_start"},
		{"type": "heal", "target": "player", "amount": 3},
	]
	var icons: Dictionary = load("res://scripts/ui/combat_scene.gd").last_turn_icons(before, events)
	assert_eq(icons[&"player"], {"hit": 6, "soaked": 5, "evaded": 0, "hp": -1, "dealt": 1}, "sword 6 − shield 5 = 1 (the turn start's heal is not the resolve's)")
	assert_eq(icons[&"enemy_0"], {"hit": 4, "soaked": 4, "evaded": 0, "hp": 0, "dealt": 0}, "a hit soaked whole: = 0 with a shield")
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"collections_agent", scale)
		_live()
		for turn in 3:
			if scene.engine.state().is_over():
				break
			scene.end_turn()
			scene.skip_motion()
		await _frames(2)
		for v in scene._views():
			var wv := v as WheelView
			if wv.last_turn == "" or wv.icon_row_items().is_empty():
				continue
			var lay := wv.hp_layout()
			var r: Rect2 = lay["icons"]
			assert_true(r.has_area(), "x%.1f: %s's icon row is laid out" % [scale, wv.combatant.display_name])
			assert_true(Rect2(Vector2.ZERO, wv.size).grow(0.5).encloses(r), "x%.1f: it stays in its view" % scale)
			assert_false(r.intersects(lay["hp"]), "x%.1f: off the HP number" % scale)
			if (lay["next"] as Rect2).has_area():
				assert_false(r.intersects(lay["next"]), "x%.1f: off NEXT" % scale)
		assert_eq(scene.layout_violations(), [] as Array[String], "x%.1f: no layout violation with the icon row" % scale)
		await _close(scene)


func test_the_real_wheel_breaks_with_its_art_and_the_beaten_side_carries_a_skull() -> void:
	var scene := await _combat()
	var ev: WheelView = scene._enemy_views.values()[0]
	var pieces: Array = ev.slice_pieces()
	var slices := 0
	var hubs := 0
	for p in pieces:
		var art: Dictionary = p[2]
		if art.has("type"):
			slices += 1
			assert_true(art.has("icon_at") and art.has("rim"), "a slice piece keeps its icon and rim")
		else:
			hubs += 1
	assert_eq(slices, ev.combatant.wheel.slice_count, "every slice falls with its art")
	assert_eq(hubs, ev.combatant.wheel.slice_count, "and the hub cracks into a piece per slice")
	var src := FileAccess.get_file_as_string("res://scripts/ui/wheel_view.gd")
	assert_true(src.contains("draw_skull(self"), "the DEFEATED spot draws a skull")
	await _close(scene)


func test_after_a_win_the_next_step_replaces_send_it_at_once() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	var node: StringName = &""
	for id in RunManager.netrun.available_nodes():
		if int(RunManager.netrun.run.map.get_node(id).get("type", -1)) == RC.InfilNodeType.ROUTER:
			node = id
			break
	if node == &"":
		node = RunManager.netrun.available_nodes()[0]
	scene.enter_node(node)
	await _frames(3)
	var combat: Control = scene.combat_scene
	assert_not_null(combat, "a fight")
	if combat == null:
		return
	_live()
	var send: Control = combat._end_turn_button
	for turn in 30:
		var st: CombatState = combat.engine.state()
		if st.is_over():
			break
		st.player.hp = st.player.max_hp
		for e in st.enemies:
			e.hp = mini(e.hp, 1)
			e.block = 0
			e.shield = 0
			e.evade_charges = 0
		combat.end_turn()
		if not combat.engine.state().is_over():
			combat.skip_motion()
	assert_true(combat.engine.state().is_over(), "the fight is won")
	assert_eq(combat.engine.state().outcome, CombatState.Outcome.VICTORY)
	# ANIM-R5 combat 1: the next step waits for the replay to land VICTORY (it no longer shows
	# before the killing hit); then it replaces SEND IT, and pressing it moves on at once.
	await BoundedWait.until(get_tree(), _outcome_landed.bind(combat), BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
	assert_false(send.visible, "SEND IT is gone once VICTORY lands (A6h, R5)")
	assert_false(combat._sticker_box.visible, "and RESPIN / UNDO")
	assert_true(combat.continue_shown(), "the next step's action shows in its place, replay or not")
	assert_eq((combat._continue_button as DripButton).tag_text, "LOOT" if RunManager.netrun.run.phase == RunState.Phase.REWARD else "CONTINUE", "named for the next step")
	# Pressing it moves on at once.
	(combat._continue_button as Button).emit_signal(&"pressed")
	await _frames(2)
	assert_null(scene.combat_scene, "the netrun moved on at once")
	await _close(scene)


func test_a_played_card_is_gone_before_its_effect() -> void:
	_live()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var fx := CombatFxLayer.new()
	holder.add_child(fx)
	var card := ZineCard.new("JOLT", 1, "Spin the target 3 ticks.", 0)
	var wait := fx.play_card(card, Rect2(100, 500, 120, 160), 0.0, Vector2(600, 300), false)
	assert_almost_eq(wait, Motion.seconds(&"card_play") + Motion.seconds(&"card_stamp") + Motion.seconds(&"effect_burst"), 0.001,
		"the effect (and the wheel's spin) waits for the card's dissolve (A6i: it covered the spinning wheel)")
	fx.clear()


func test_the_words_say_who_plays_and_what_is_missing() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/combat_scene.gd")
	assert_true(FileAccess.get_file_as_string("res://scripts/ui/wheel_view.gd").contains("tr(\"YOUR %s\")"), "YOUR JOLT on the tape (ANIM-R6 A13; PLAYING read as the enemy playing it)")
	assert_false(src.contains("tr(\"PLAYING %s\")"))
	var bar := RamBar.new()
	add_child_autofree(bar)
	bar.set_ram(2, 10)
	bar.flash_short(3)
	assert_eq(bar.refusal_text(), tr("NEED %d · HAVE %d") % [3, 2], "NEED 3 · HAVE 2, not 3 > 2")


func test_next_and_last_turn_explain_themselves() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	pv.outcome = {"hp_after": pv.combatant.hp - 4}
	pv.last_turn = "LAST TURN: -2 HP · GOT CORRUPTED"
	pv.last_turn_tip = "LAST TURN: -2 HP · GOT CORRUPTED\n" + Codex.status_text(RC.Status.CORRUPTED)
	pv.queue_redraw()
	var lay := pv.hp_layout()
	var next: Rect2 = lay["next"]
	assert_true(next.has_area(), "NEXT shows")
	assert_true(pv._get_tooltip(next.get_center()).contains(str(pv.combatant.hp - 4)), "NEXT has a tooltip that says what it is")
	var last: Rect2 = lay["last"]
	assert_true(pv._get_tooltip(last.get_center()).contains(Codex.status_text(RC.Status.CORRUPTED)), "LAST TURN's tooltip explains GOT CORRUPTED")
	var tips: Dictionary = load("res://scripts/ui/combat_scene.gd").last_turn_tips({&"player": "LAST TURN: GOT CORRUPTED"},
		[{"type": "status", "target": "player", "status": RC.Status.CORRUPTED, "slot": 0}] as Array[Dictionary])
	assert_true(String(tips[&"player"]).contains(Codex.status_text(RC.Status.CORRUPTED)), "the scene builds it from the turn's statuses")
	await _close(scene)


func test_a_status_marks_its_slice_as_it_lands() -> void:
	var scene := await _combat()
	_live()
	var ev: WheelView = scene._enemy_views.values()[0]
	ev.shown_state = ev.combatant.duplicate_state()
	ev.replaying = true
	ev.show_slice_status(1, RC.Status.CORRUPTED)
	assert_eq(int(ev.shown_state.wheel.slice_statuses[1]), RC.Status.CORRUPTED, "the view's snapshot shows it on the slice")
	assert_true(ev.status_flash.has(1), "with a ring as it lands")
	assert_eq(int(ev.combatant.wheel.slice_statuses[1]), int(scene.engine.state().get_combatant(ev.combatant.id).wheel.slice_statuses[1]), "the state is untouched")
	scene.skip_motion()
	await _close(scene)


func test_the_tape_never_clips_the_tag() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"collections_agent", scale)
		for v in scene._views():
			var wv := v as WheelView
			var tag := wv.intent_rect()
			if not tag.has_area():
				continue
			assert_true(tag.size.x >= minf(WheelView.tape_width(), wv.size.x * WheelView.TAG_MAX_SHARE) - 0.5, "x%.1f: the tag is as wide as its tape's words" % scale)
			assert_true(tag.position.y - wv.global_position.y >= WheelView.tape_height() - WheelView.TAPE_INSET * Settings.text_scale - 0.5,
				"x%.1f: the tape stands above the tag, inside the view" % scale)
		await _close(scene)


# --- A7: screens -----------------------------------------------------------------------------------------

func test_the_mainframe_first_focus_is_the_first_item() -> void:
	for rich in [true, false]:
		var scene := await _netrun()
		Settings.set_pad_active(true)
		RunManager.netrun.run.cycles = 999 if rich else 0
		RunManager.netrun._open_shop()
		scene._show_current()
		PageTransition.settle(scene)
		await _frames(3)
		var owner := get_viewport().gui_get_focus_owner()
		assert_true(owner is ZineCard, "%s: the first focus is an item tile (the prompt says A Buy), not %s" % ["rich" if rich else "broke", owner])
		assert_false(owner is OptionButton, "never the socket list")
		await _close(scene)


func test_the_mainframe_sign_is_whole_before_its_warm_up_ends() -> void:
	var sign := MainframeSign.new()
	add_child_autofree(sign)
	var lit_at := MainframeSign.strike_share() + MainframeSign.flicker_share()
	assert_lt(lit_at, 0.8, "every tube holds lit well before the warm-up ends")
	sign.warm = lit_at + 0.01
	for id in 12:
		assert_eq(sign.tube(id), 1.0, "tube %d is lit" % id)
	sign.warm = MainframeSign.strike_share() * 0.5 + MainframeSign.flicker_share()
	var lit := 0
	for id in 6:
		if sign.tube(id) >= 1.0:
			lit += 1
	assert_gt(lit, 1, "half-way, more than one letter is lit (a still showed one: it read as broken)")
	assert_lte(Motion.entry(&"mainframe_sign_warmup").duration, 0.5, "a shorter warm-up")


func test_a_flying_card_is_a_fresh_copy_and_loot_falls_within_its_window() -> void:
	_live()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var card := ZineCard.new("JAM", 1, "Jam a needle.", 0)
	card.position = Vector2(200, 200)
	card.size = Vector2(150, 170)
	holder.add_child(card)
	card.modulate.a = 0.0  # still dealing in
	var pic := FlightFx.picture_of(card)
	assert_true(pic is ZineCard, "a card flies as a fresh copy of itself (a snapshot of a card dealing in was a grey blank)")
	pic.free()
	var clip := Rect2(150, 150, 400, 260)
	var node := FlightFx.fly(holder, card, Vector2(275, 500), &"loot_reject", "", 0.0, clip)
	assert_not_null(node, "it falls")
	if node != null:
		var box := node.get_parent() as Control
		assert_true(box.clip_contents, "clipped")
		assert_eq(box.get_global_rect(), clip, "to its window")
	FlightFx.finish_all(holder)
	var scene := await _netrun()
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	PageTransition.settle(scene)
	await _frames(3)
	var sticker := scene._panel.find_child("Stickers", true, false).get_child(1) as Control
	var win: Rect2 = scene.loot_window_rect(sticker)
	assert_true(win.has_area() and win.encloses(sticker.get_global_rect()), "a loot card's window is found")
	await _close(scene)


func test_the_empty_set_mark_stays_inside_its_icon() -> void:
	var r := OutcomeRow.ICON_R
	var ring := r * OutcomeRow.NULL_RING
	var reach := ring * OutcomeRow.NULL_SLASH * sqrt(2.0)
	assert_true(reach <= ring + 0.01, "the slash ends on the ring (it ran over the note's border)")
	assert_true(ring < r, "inside the icon's box")


func test_every_event_choice_shows_its_outcome_icons() -> void:
	var scene := await _netrun()
	var failures: Array[String] = []
	for id in RunManager.lookup().ids_of_class(&"TerminalEventData"):
		var run := RunManager.netrun.run
		run.event_id = id
		run.phase = RunState.Phase.EVENT
		scene._show_current()
		for b in scene._panel.find_children("Choice*", "Button", true, false):
			var row := (b as Node).find_child("OutcomeRow", false, false) as OutcomeRow
			if row == null or row.items.is_empty():
				failures.append("%s %s" % [id, b.name])
	assert_eq(failures.size(), 0, "every event choice shows icons:\n" + "\n".join(failures))
	await _close(scene)


func test_the_loadout_swap_chips_carry_a_ring_pictogram() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.show_hq()
	await _frames(3)
	var op: OperativeState = RunManager.campaign.living_operatives()[0]
	op.rank = 3
	hq.open_loadout(op)
	await _frames(2)
	var view := hq.get_node("LoadoutView") as LoadoutView
	view.show_spinner()
	await _frames(3)
	var chips := view.find_children("Swap_*", "Button", true, false)
	assert_gt(chips.size(), 0, "the swaps show at Rank 3")
	for c in chips:
		assert_not_null((c as Node).get_node_or_null(^"SegmentMark"), "%s carries the ring pictogram" % c.name)
	await _close(hq)


func test_discarded_cards_keep_off_respin_and_undo() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"collections_agent", scale)
		var spot: Vector2 = scene._discard_spot()
		var card: Vector2 = ZineCard.STICKER_SIZE * scene._hand_scale * CombatFxLayer.DISCARD_SCALE
		var landed := Rect2(spot - card * 0.5, card)
		for key in scene._stickers:
			assert_false(landed.intersects((scene._stickers[key] as Control).get_global_rect()), "x%.1f: a discard lands off %s" % [scale, key])
		assert_true(scene._hand_box.get_global_rect().grow(0.5).encloses(landed), "x%.1f: within the hand's row" % scale)
		await _close(scene)


# --- New ids and words -------------------------------------------------------------------------------------

func test_new_motion_ids_are_required_and_words_are_translated_once() -> void:
	for id in [&"impact_mark", &"forecast_tick", &"forecast_fade", &"status_mark"]:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(Motion.has(id), "%s is in the table" % id)
	var lab := FileAccess.get_file_as_string("res://tools/design_lab/motion_lab.gd")
	for id in ["impact_mark", "forecast_tick", "forecast_fade", "status_mark"]:
		assert_true(lab.contains("&\"%s\":" % id), "%s has a lab demo" % id)
	var csv := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for key in ["YOUR %s", "NEED %d · HAVE %d", "LOOT", "HP now: %d of %d."]:
		assert_true(csv.contains(key), "%s is exported for translation" % key)


## ANIM-R5 combat 1: the fight's outcome has landed on screen.
func _outcome_landed(combat: Control) -> bool:
	return not combat.outcome_pending()
