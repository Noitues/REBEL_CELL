extends GutTest
## Animation pass ANIM-R2 (the second fix batch), combat, events and screens (DECISIONS
## "Animation pass — ANIM-R2 combat, events and screens"): an event can be finished with the
## pad alone and its held choices read (E1, E2); one press shows the story and its subtitle
## together; a menu never drops a fast Enter or a click on a line (E3); hits fly one at a
## time in their side's colour and every HP change has a number of exactly its size, the
## result holding before the respin (E4); a break flashes its own wheel, VICTORY lands on
## the enemies' side, the result reads before the break (E5); the Modem's chip and Daemon
## tiles show their whole text (seeds 1-6, English and pseudolocalised, 1.0 / 1.3 / 1.6) and
## a slice shows one price (E6); the entering plate never hides the forecast, chips shrink
## before they fold, satellites keep off the values (E7); loot keeps its tip off Skip and its
## cards apart (E8); refusals wrap, drops that pick land beside, the ghost reads, the wallet
## rolls with the top bar, RAM spent floats, the money flashes, PLAYING X (E9); the
## fx layer's fractions are named (E10); no helper acts under the jack's cover.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const ENEMIES: Array[StringName] = [&"collections_agent", &"compliance_officer", &"geostationary_guard", &"care_swarm"]
const EVENT := &"ev_leash_on_the_floor"

var _scale: float = 1.0
var _reduce: bool = false
var _typing: bool = true
var _pad: bool = false


class Counter extends Node:
	## Counts the presses that reach it (it sits before the helper in the tree, so the
	## helper sees each event first).
	var got: int = 0

	func _input(event: InputEvent) -> void:
		if event.is_pressed() and not event.is_echo():
			got += 1


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects
	_typing = Settings.subtitle_typing
	_pad = Settings.pad_active


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r2"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Fx._jacking = false
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.subtitle_typing != _typing:
		Settings.set_subtitle_typing(_typing)
	Settings.set_pad_active(_pad)
	_pseudo(false)
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


func _event(scene: Control) -> void:
	var run := RunManager.netrun.run
	run.event_id = EVENT
	run.phase = RunState.Phase.EVENT
	scene._show_current()


func _pad_button(b: JoyButton, pressed: bool = true) -> InputEventJoypadButton:
	var e := InputEventJoypadButton.new()
	e.button_index = b
	e.pressed = pressed
	return e


func _key(k: Key, pressed: bool = true) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = pressed
	return e


## Waits out a page entrance (PageTransition: under 0.25 s) without completing it: a
## settle would also show the typing words whole. Test suite: bounded waits: until the
## page says its entrance ended (bounded by its seconds), not a fixed time.
func _entrance(scene: Control) -> void:
	await BoundedWait.until(get_tree(), func() -> bool: return scene._panel != null and not PageTransition.running(scene._panel),
		BoundedWait.motion_limit([&"panel_in", &"panel_drop"]))
	await _frames(1)


func _tap(e_down: InputEvent, e_up: InputEvent) -> void:
	get_viewport().push_input(e_down)
	get_viewport().push_input(e_up)


# --- E1 / E2: the event -------------------------------------------------------------------------

func test_an_event_can_be_finished_with_the_pad_alone() -> void:
	var scene := await _netrun()
	_live()
	Settings.set_subtitle_typing(true)
	Settings.set_pad_active(true)
	_event(scene)
	await _entrance(scene)
	assert_true(scene.choices_held(), "the story types in")
	var owner := get_viewport().gui_get_focus_owner()
	assert_not_null(owner, "a choice has focus while the words type (E1: nothing had focus)")
	assert_true(owner != null and String(owner.name).begins_with("Choice"), "the focus is on a choice")
	# A: the words (and the subtitle) show whole; the choice is not taken.
	_tap(_pad_button(JOY_BUTTON_A), _pad_button(JOY_BUTTON_A, false))
	await _frames(2)
	assert_false(scene.choices_held(), "one A shows the words whole")
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.EVENT, "and takes no choice")
	# The D-pad walks the choices; A takes the focused one.
	_tap(_pad_button(JOY_BUTTON_DPAD_DOWN), _pad_button(JOY_BUTTON_DPAD_DOWN, false))
	await _frames(1)
	_tap(_pad_button(JOY_BUTTON_DPAD_UP), _pad_button(JOY_BUTTON_DPAD_UP, false))
	await _frames(1)
	var focused := get_viewport().gui_get_focus_owner() as Button
	assert_not_null(focused, "the D-pad keeps a choice focused")
	if focused != null and focused.disabled:
		# A refused choice (a cost the run can't pay): walk to one that acts.
		for b in scene._panel.find_children("Choice*", "Button", true, false):
			if not (b as Button).disabled:
				(b as Button).grab_focus()
				break
	_tap(_pad_button(JOY_BUTTON_A), _pad_button(JOY_BUTTON_A, false))
	await _frames(2)
	assert_ne(RunManager.netrun.run.phase, RunState.Phase.EVENT, "A on a choice takes it: the event is done with the pad alone")
	await _close(scene)


func test_held_choices_read_and_carry_a_typing_mark() -> void:
	var scene := await _netrun()
	_live()
	Settings.set_subtitle_typing(true)
	_event(scene)
	await BoundedWait.frozen_frames(get_tree(), 1)  # the story must still be typing after the frame
	var c1 := scene._panel.find_child("Choice1", true, false) as Button
	assert_true(scene.choices_held(), "the story types in")
	assert_false(c1.disabled, "a held choice is not disabled (its paper stays readable)")
	assert_true(c1.has_meta(scene.HELD_META), "it waits")
	assert_not_null(c1.get_node_or_null(^"EventHeldMark"), "with the typing mark")
	assert_not_null(c1.find_child("OutcomeRow", false, false), "its outcome icons show")
	var paper := c1.get_theme_stylebox(&"normal") as StyleBoxFlat
	assert_not_null(paper)
	if paper != null:
		assert_eq(paper.bg_color, Palette.NOTE_PAPER, "on its paper note (OutcomeRow read Godot's grey box before the theme)")
	var ink := c1.get_theme_color(&"font_color")
	assert_gt(ink.a, 0.6, "its words stay readable (a disabled note was ink at 0.45 on paper at 0.45)")
	# A click on it while held shows the words and takes nothing.
	scene._press_choice(0)
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.EVENT, "a held choice never chooses")
	await _frames(2)
	assert_false(c1.has_meta(scene.HELD_META), "the words whole release it")
	assert_null(c1.get_node_or_null(^"EventHeldMark"), "and its mark goes")
	await _close(scene)


func test_one_press_shows_the_story_and_its_subtitle() -> void:
	var scene := await _netrun()
	_live()
	Settings.set_subtitle_typing(true)
	scene._spoken_events.clear()
	_event(scene)
	await _entrance(scene)
	var text := scene._panel.find_child("EventPanel", true, false).find_children("*", "RichTextLabel", true, false)[0] as Control
	assert_true(Typing.typing(text), "the story types")
	assert_true(Dialogue.typing(), "and the subtitle")
	var key := _key(KEY_SEMICOLON)
	get_viewport().push_input(key)
	assert_false(Typing.typing(text), "one press shows the story")
	assert_false(Dialogue.typing(), "and the subtitle with it")
	assert_true(get_viewport().is_input_handled(), "and does nothing else")
	await _close(scene)


func test_the_event_top_bar_keeps_one_row_and_the_choices_show_at_big_text() -> void:
	Settings.set_text_scale(LayoutScales.VERIFIED_MAX)  # the event page's top bar is W8's (HudBar at 2.0)
	var scene := await _netrun()
	_event(scene)
	await _frames(4)
	assert_eq(scene.hud.stats.rows, 1, "the top bar keeps one row at 1.6 (two pushed the page down)")
	for b in scene._panel.find_children("Choice*", "Button", true, false):
		var r := (b as Control).get_global_rect()
		assert_true(SCREEN.encloses(r), "%s on screen at 1.6" % b.name)
	await _close(scene)


# --- E3: menus pass their own presses --------------------------------------------------------------

func _menu() -> Array:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var counter := Counter.new()
	holder.add_child(counter)
	var box := VBoxContainer.new()
	box.position = Vector2(100, 100)
	holder.add_child(box)
	var pressed: Array = []
	for t in ["Continue", "Campaigns", "Tutorial"]:
		var b := Button.new()
		b.text = t
		b.name = t
		b.custom_minimum_size = Vector2(300, 40)
		b.pressed.connect(func() -> void: pressed.append(t))
		box.add_child(b)
	return [holder, counter, box, pressed]


func test_a_fast_enter_after_a_focus_move_activates_the_new_line() -> void:
	_live()
	var m := _menu()
	var box: VBoxContainer = m[2]
	var pressed: Array = m[3]
	var mm := MenuMotion.attach(box)
	await _frames(2)
	(box.get_child(0) as Button).grab_focus()
	await _frames(1)
	_tap(_key(KEY_DOWN), _key(KEY_DOWN, false))
	assert_true(mm.typing() or mm.sliding(), "the new line types in")
	_tap(_key(KEY_ENTER), _key(KEY_ENTER, false))
	await _frames(1)
	assert_eq(pressed, ["Campaigns"], "Down then Enter the next frame activates the new line (E3)")
	assert_false(mm.typing(), "and the Enter completed its typing")


func test_a_click_on_another_line_passes_and_other_presses_are_consumed() -> void:
	_live()
	var m := _menu()
	var counter: Counter = m[1]
	var box: VBoxContainer = m[2]
	var pressed: Array = m[3]
	var mm := MenuMotion.attach(box)
	await _frames(2)
	(box.get_child(0) as Button).grab_focus()
	(box.get_child(1) as Button).grab_focus()
	assert_true(mm.typing())
	var line := (box.get_child(2) as Button).get_global_rect().get_center()
	var down := InputEventMouseButton.new()
	down.button_index = MOUSE_BUTTON_LEFT
	down.pressed = true
	down.position = line
	down.global_position = line
	var up := down.duplicate() as InputEventMouseButton
	up.pressed = false
	assert_true(mm.works_menu(down), "a click on one of the menu's lines works the menu")
	get_viewport().push_input(down)
	assert_false(mm.typing(), "it completes the line's typing and passes on (works_menu: never consumed; it was eaten within 0.18 s)")
	get_viewport().push_input(up)
	await _frames(1)
	assert_true(pressed.is_empty() or pressed == ["Tutorial"], "only the clicked line can act")
	# A press that works nothing in the menu completes the typing and is consumed.
	(box.get_child(0) as Button).grab_focus()
	assert_true(mm.typing())
	var before := counter.got
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(mm.typing(), "a stray key completes the typing")
	assert_eq(counter.got, before, "and is consumed")


# --- Under the jack ----------------------------------------------------------------------------------

func test_no_helper_acts_on_a_press_under_the_jack() -> void:
	_live()
	Settings.set_subtitle_typing(true)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var label := Label.new()
	label.text = "The grid is listening, and it keeps what it hears."
	holder.add_child(label)
	assert_gt(Typing.type_in(label), 0.0)
	Fx._jacking = true
	assert_true(Fx.transitioning())
	var key := _key(KEY_SEMICOLON)
	assert_false(MotionSkip.is_press(key), "nothing is a press under the jack")
	get_viewport().push_input(key)
	assert_true(Typing.typing(label), "the typing goes on: no helper acted")
	var page := Control.new()
	page.size = Vector2(300, 200)
	holder.add_child(page)
	var done := [false]
	PageTransition.enter(page, PageTransition.Look.GLASS, func() -> void: done[0] = true)
	var pad := _pad_button(JOY_BUTTON_Y)
	get_viewport().push_input(pad)
	assert_false(done[0], "a page entrance is not completed by a press under the jack")
	Fx._jacking = false
	PageTransition.settle(page)
	assert_true(MotionSkip.is_press(key), "after the jack a key is a press again")
	get_viewport().push_input(_key(KEY_APOSTROPHE))
	assert_false(Typing.typing(label), "and completes the typing")
	PageTransition.settle(holder)


# --- E4: SEND IT reads -------------------------------------------------------------------------------

func _turns(enemy: StringName, combat_seed: int, turns: int, visit: Callable) -> void:
	var scene := await _combat(enemy, 1.0, combat_seed)
	_live()
	for t in turns:
		if scene.engine.state().is_over():
			break
		var before: CombatState = scene.engine.state().duplicate_state()
		scene.end_turn()
		scene.skip_motion()
		var events: Array[Dictionary] = scene._last_events
		visit.call(scene, before, events, scene.engine.state())
	await _close(scene)


func test_hits_fly_one_at_a_time_and_the_result_holds_before_the_respin() -> void:
	for enemy in ENEMIES:
		for combat_seed in [1, 5, 9]:
			await _turns(enemy, combat_seed, 3, func(scene: Control, before: CombatState, events: Array[Dictionary], _after: CombatState) -> void:
				var beats := ResolveBeats.build(before, events, scene.engine.resolver.lookup)
				var sch: Dictionary = scene.sequence_schedule(beats)
				var times: PackedFloat32Array = sch["times"]
				var timing: Dictionary = scene.beat_timing()
				var last_fly := -INF
				var settled := 0.0
				for k in beats.size():
					var b := beats[k]
					if b["phase"] == "turn_start":
						continue
					if ResolveBeats.flies(b):
						assert_true(times[k] - last_fly >= Motion.seconds(&"hit_line") - 0.0001,
							"%s seed %d: one projectile at a time (%.2f after the last)" % [enemy, combat_seed, times[k] - last_fly])
						last_fly = times[k]
					settled = maxf(settled, times[k] + ResolveBeats.settle_after(b, timing))
				assert_true(float(sch["result_at"]) >= settled - 0.0001, "%s: THIS TURN once every HP roll has finished" % enemy)
				if float(sch["spin_at"]) >= 0.0:
					assert_true(float(sch["spin_at"]) - float(sch["result_at"]) >= Motion.seconds(&"resolve_result_hold") - 0.0001,
						"%s: the result holds %.1f s before the respin" % [enemy, Motion.seconds(&"resolve_result_hold")]))


func test_every_hp_change_has_a_number_of_exactly_its_size() -> void:
	var checked := [0]
	for enemy in ENEMIES:
		for combat_seed in [1, 2, 3, 5, 7, 9]:
			await _turns(enemy, combat_seed, 4, func(scene: Control, before: CombatState, events: Array[Dictionary], after: CombatState) -> void:
				var beats := ResolveBeats.build(before, events, scene.engine.resolver.lookup)
				var hp := {}
				var shown := {}
				for c in [before.player] + before.enemies + before.drones:
					hp[c.id] = c.hp
					shown[c.id] = 0
				for b in beats:
					if not (b["kind"] in ResolveBeats.HP_KINDS) or int(b["hp_after"]) < 0:
						continue
					var id := StringName(String(b["target"]))
					var change := int(b["hp_after"]) - int(hp.get(id, 0))
					hp[id] = int(b["hp_after"])
					var nums: Array = scene.numbers_for(b, before, after).filter(func(n: Dictionary) -> bool: return n.has("hp"))
					if change == 0:
						assert_true(nums.is_empty(), "%s: no HP number when the HP didn't move" % enemy)
						continue
					assert_eq(nums.size(), 1, "%s seed %d: an HP change has one number" % [enemy, combat_seed])
					if nums.is_empty():
						continue
					var n: Dictionary = nums[0]
					var signed_hp := -int(n["hp"]) if String(b["kind"]) != "heal" else int(n["hp"])
					assert_eq(signed_hp, change, "%s seed %d: the number is the HP change (%d)" % [enemy, combat_seed, change])
					assert_string_contains(String(n["text"]), str(absi(change)), "and says it")
					shown[id] = int(shown[id]) + signed_hp
					if int(b["soaked"]) > 0 and ResolveBeats.is_hit(b) and n.has("raw"):
						assert_eq(String(n["raw"]), "-%d" % int(b["raw"]), "%s: the raw hit shows first" % enemy)
						assert_true(int(b["raw"]) >= int(b["amount"]) + int(b["soaked"]),
							"raw = what got through + what the guard took (more when it overkilled)")
						# ANIM-R3 A6e (expectation changed): the guard's part is a glyph and its number.
						var guard: Array = scene.numbers_for(b, before, after).filter(func(g: Dictionary) -> bool: return int(g.get("icon", -1)) >= 0 and String(g["text"]) == str(int(b["soaked"])))
						assert_eq(guard.size(), 1, "%s: the guard's part shows as a shield and its number" % enemy)
					checked[0] += 1
				# The floated total equals the HP roll for every wheel, satellites and drones too.
				for id in hp:
					var start: CombatantState = before.get_combatant(id)
					assert_eq(int(shown[id]), int(hp[id]) - start.hp, "%s seed %d: %s's numbers add up to its HP roll" % [enemy, combat_seed, start.display_name]))
	assert_gt(checked[0], 20, "the sweep saw many HP changes")


func test_a_hit_flies_in_its_sides_colour_with_its_raw_number_and_its_guard_chip() -> void:
	var scene := await _combat()
	_live()
	var state: CombatState = scene.engine.state()
	var before := state.duplicate_state()
	var enemy: CombatantState = state.enemies[0]
	var base := {"event_index": 0, "phase": "resolve", "pass": "offensive", "source": enemy.id, "pointer_index": 0,
		"target": state.player.id, "crit": false, "slot": -1, "status": 0, "tier": -1, "host": &"", "source_slot": 0}
	var hit := base.duplicate()
	hit.merge({"kind": "damage", "amount": 9, "soaked": 5, "raw": 14, "blocked": 5, "shielded": 0, "hp_after": state.player.hp - 9}, true)
	scene._play_beat(hit, before, state)
	var lines: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "line")
	assert_eq(lines.size(), 1, "the hit flies")
	assert_eq(lines[0]["color"], scene.ENEMY_HIT_COLOR, "in the enemies' colour, not the slice's")
	assert_eq(String(lines[0]["label"]), "14", "its raw number rides with it")
	var travel: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "travel")
	assert_eq(travel.size(), 1)
	# ANIM-R4 C6c (expectation changed): the raw hit meets its guard where it struck (sword 14
	# − shield 5 = 9), then what gets through pops fresh in the hub and travels (no raw number
	# morphing into it, no separate guard number).
	assert_eq(String(travel[0].get("raw", "")), "", "no raw number morphs in the hub")
	assert_eq(String(travel[0]["text"]), "-9", "what gets through travels into the HP")
	assert_almost_eq(float(travel[0]["delay"]), CombatFxLayer.impact_seconds() + Motion.seconds(&"hit_absorb"), 0.001, "after the impact's equation")
	# Art pass W3 (critique 3.4, expectation changed): one number per hit: what got through, in
	# WARN (a guard took part), with its guard's part beside it ("14 − 5"), no second mark.
	assert_eq(travel[0]["color"], Palette.WARN, "a partly guarded hit's number is amber")
	var subs: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "number" and String(s["text"]) == "14 %s 5" % CombatFxLayer.EQ_MINUS)
	assert_eq(subs.size(), 1, "the guard's part beside it")
	assert_eq(scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "impact").size(), 0, "no second number where it struck")
	scene.skip_motion()
	# The operative's hits in the operative's colour; a blocked hit still flies and shows it.
	var mine := base.duplicate()
	mine.merge({"kind": "damage", "source": state.player.id, "target": enemy.id, "amount": 0, "soaked": 4, "raw": 4, "blocked": 4, "hp_after": enemy.hp}, true)
	scene._play_beat(mine, before, state)
	lines = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "line")
	assert_eq(lines.size(), 1, "a fully blocked hit still flies (who hit whom)")
	if not lines.is_empty():
		assert_eq(lines[0]["color"], scene.PLAYER_HIT_COLOR, "in the operative's colour")
	# ANIM-R3 A6a (expectation changed): "0" with a shield where it struck, on impact.
	var marks: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "impact")
	assert_eq(marks.size(), 1)
	if not marks.is_empty():
		assert_eq(String(marks[0]["text"]), "0", "and shows 0 with a shield on impact")
		assert_eq(int(marks[0]["icon"]), RC.SliceType.DEFEND)
	scene.skip_motion()
	await _close(scene)


func test_a_wheel_hurt_and_healed_back_stamps_nothing() -> void:
	var scene := await _combat()
	var state: CombatState = scene.engine.state()
	var beats: Array[Dictionary] = [
		{"kind": "damage", "phase": "resolve", "target": state.player.id, "amount": 5, "soaked": 0, "hp_after": state.player.hp - 5},
		{"kind": "heal", "phase": "resolve", "target": state.player.id, "amount": 5, "soaked": 0, "hp_after": state.player.hp},
	]
	var stamps: Dictionary = scene.result_stamps(beats, state)
	assert_false(stamps.has(state.player.id), "damage and an equal heal: no NO DAMAGE (E4f)")
	assert_eq(stamps.get(state.enemies[0].id), tr("NO DAMAGE"), "an untouched wheel still says so")
	await _close(scene)


func test_the_forecast_caption_says_what_send_it_does() -> void:
	assert_eq(WheelView.forecast_caption(), tr("IF YOU SEND IT"), "the tag's tape (NEXT TURN read as 'not this turn')")
	var src := FileAccess.get_file_as_string("res://scripts/ui/wheel_view.gd")
	assert_false(src.contains("tr(\"NEXT TURN\")"), "NEXT TURN is gone from the tag")


# --- E5: the break ---------------------------------------------------------------------------------

func test_the_result_reads_before_the_break_which_flashes_its_own_wheel() -> void:
	var scene := await _combat()
	_live()
	var state: CombatState = scene.engine.state()
	var enemy: CombatantState = state.enemies[0]
	var p := state.player.id
	var beats: Array[Dictionary] = [
		{"kind": "land", "phase": "resolve", "pass": "", "target": p, "source": p, "amount": 0, "soaked": 0, "hp_after": -1},
		{"kind": "damage", "phase": "resolve", "pass": "offensive", "target": enemy.id, "source": p, "amount": enemy.hp, "soaked": 0, "hp_after": 0},
		{"kind": "died", "phase": "resolve", "pass": "offensive", "target": enemy.id, "source": &"", "amount": 0, "soaked": 0, "hp_after": 0, "wheel": true},
		{"kind": "end", "phase": "resolve", "pass": "offensive", "target": &"", "source": &"", "amount": 0, "soaked": 0, "hp_after": -1},
	]
	var sch: Dictionary = scene.sequence_schedule(beats)
	var times: PackedFloat32Array = sch["times"]
	assert_true(float(sch["result_at"]) < times[2], "THIS TURN and the stamps show before the break (E5)")
	assert_true(times[2] - times[1] >= scene.death_lead() - 0.0001, "the break still waits for HP 0")
	assert_true(times[3] > times[2], "VICTORY after the break")
	# The break flashes the wheel, never the screen.
	var flashes: int = Fx.limiter.count() if Fx.limiter.has_method("count") else -1
	scene._death_beat(enemy.id, state)
	var discs: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "disc")
	assert_eq(discs.size(), 1, "a local flash on the breaking wheel")
	var ev: WheelView = scene._view_of(enemy.id)
	assert_eq(discs[0]["at"], ev.global_center(), "centred on it")
	assert_eq(discs[0]["color"], Color.WHITE, "white, short")
	scene._end_beat(CombatState.Outcome.VICTORY)
	if flashes >= 0:
		assert_eq(Fx.limiter.count(), flashes, "no full-screen flash")
	var words: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "word")
	assert_eq(words.size(), 1)
	var pv: WheelView = scene._player_view
	assert_false(pv.get_global_rect().has_point(words[0]["at"]), "VICTORY never lands on the operative's wheel")
	assert_false(FileAccess.get_file_as_string("res://scripts/ui/combat_scene.gd").contains("Fx.flash(Palette.CELL_ACID"), "the olive full-screen flash is gone")
	scene.skip_motion()
	await _close(scene)


# --- E6: the Modem at big text ----------------------------------------------------------------------

func test_modem_tiles_show_their_whole_text_over_seeds_languages_and_sizes() -> void:
	var failures: Array[String] = []
	var tiles := 0
	for pseudo in [false, true]:
		_pseudo(pseudo)
		for scale in [1.0, 1.3, LayoutScales.VERIFIED_MAX]:
			Settings.set_text_scale(scale)
			for seed in range(1, 7):
				var scene := await _netrun(seed)
				RunManager.netrun.run.cycles = 999
				RunManager.netrun._open_shop()
				scene._show_current()
				await _frames(3)
				for row in ["Chips", "Daemons"]:
					var holder: Node = scene._panel.find_child(row, true, false)
					for c in holder.get_children():
						var zc := c as ZineCard
						if zc == null or zc.sold_stub:
							continue
						tiles += 1
						if not zc.text_whole():
							var parts := zc.tile_parts()
							failures.append("seed %d x%.1f%s %s: %d of %d rows at %d px" % [seed, scale, " pseudo" if pseudo else "", zc.card_title,
								int(parts["rows"]), (parts["desc_lines"] as PackedStringArray).size(), int(parts["dfs"])])
				# One price on a slice (E6: "BUY 100-150" wrapped onto three lines).
				for c in scene._panel.find_child("Slices", true, false).get_children():
					var tile := c as ZineCard
					if tile != null and not tile.sold_stub:
						assert_false(tile.price_words().contains("-"), "a slice shows one price")
						assert_lte(tile.buy_button._lines.size(), 2, "its BUY sticker keeps to two lines")
				await _close(scene)
	_pseudo(false)
	assert_gt(tiles, 36, "the sweep saw the chips and Daemons")
	assert_eq(failures.size(), 0, "every chip and Daemon tile shows its whole text:\n" + "\n".join(failures))


# --- E7: big text combat -----------------------------------------------------------------------------

func test_the_entering_plate_never_hides_the_forecast() -> void:
	var scene := await _combat(&"collections_agent", Settings.TEXT_SCALE_MAX)
	_live()
	var ev: WheelView = scene._enemy_views.values()[0]
	ev.play_enter()
	await BoundedWait.frozen_frames(get_tree(), 1)  # still entering after the frame
	assert_true(ev.enter_slide > 0.0, "the enemy is entering")
	assert_true(ev.intent_rect().has_area(), "its forecast tag is laid out")
	var src := FileAccess.get_file_as_string("res://scripts/ui/wheel_view.gd")
	assert_true(src.contains("if tag.has_area() and not replaying:"), "the tag draws while the enemy enters")
	scene.skip_motion()
	await _close(scene)


func test_chips_shrink_before_they_fold_at_big_text() -> void:
	var scene := await _combat(&"collections_agent", Settings.TEXT_SCALE_MAX)
	var v: WheelView = scene._player_view
	v.intent = {"text": "DEFEND", "type": RC.SliceType.DEFEND, "chips": [
		{"text": "+3 BLOCK", "color": Palette.NET_CYAN}, {"text": "? RANDOM STATUS", "color": Palette.CELL_ACID},
		{"text": "RAM +4", "color": Palette.NOTE_YELLOW}, {"text": "+2 SHIELD", "color": Palette.NET_CYAN}]}
	var full := v._chip_rows_at(roundi(WheelView.CHIP_FONT_SIZE * Settings.text_scale))
	var fitted := v._chip_rows()
	var hidden := func(rows: Array) -> int:
		var n := 0
		for r in rows:
			for c in r:
				if bool((c as Dictionary).get("more", false)):
					n += String(c["text"]).to_int()
		return n
	assert_true(v.chip_font() <= roundi(WheelView.CHIP_FONT_SIZE * Settings.text_scale), "the chips may shrink")
	assert_true(v.chip_font() >= roundi(WheelView.CHIP_FONT_SIZE * WheelView.BIG_TEXT), "never under their 1.3 size")
	assert_true(hidden.call(fitted) <= hidden.call(full), "shrinking hides no more than folding did")
	await _close(scene)


func test_satellites_keep_off_the_slice_values_and_the_tag() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		for enemy in [&"collections_agent", &"geostationary_guard"]:
			var scene := await _combat(enemy, scale)
			for turn in 3:
				if scene.engine.state().is_over():
					break
				_check_satellites(scene, scale)
				scene.end_turn()
				scene.skip_motion()
				await _frames(1)
			await _close(scene)


func _check_satellites(scene: Control, scale: float) -> void:
	for v in scene._views():
		var wv := v as WheelView
		for sat in wv.satellites:
			var p := wv._satellite_pos(sat)
			var tok := WheelView.SATELLITE_TOKEN * Settings.text_scale
			if wv.intent_rect().has_area():
				assert_false(wv.intent_rect().intersects(Rect2(p - Vector2(tok, tok), Vector2(tok, tok) * 2.0)), "x%.1f: %s's token keeps off the tag" % [scale, sat.display_name])
			var c := wv.combatant
			var tps := c.wheel.ticks_per_slice()
			for i in c.wheel.slice_count:
				var a := WheelView._ang(i * tps - wv.shown_rotation())
				var vs := WheelView._fs(WheelView.VALUE_FONT_SIZE)
				var centre := wv.global_center() + Vector2(cos(a), sin(a)) * (wv._radius() + WheelView.VALUE_OUT)
				var w := Palette.display().get_string_size(WheelView.VALUE_WIDEST, HORIZONTAL_ALIGNMENT_LEFT, -1, vs).x
				var box := Rect2(centre - Vector2(w * 0.5, vs * 0.5), Vector2(w, vs)).grow(-1.0)
				var nearest := Vector2(clampf(p.x, box.position.x, box.end.x), clampf(p.y, box.position.y, box.end.y))
				assert_true(nearest.distance_to(p) >= tok * 0.9, "x%.1f: %s's token keeps off slice %d's value" % [scale, sat.display_name, i])


# --- E8: loot ------------------------------------------------------------------------------------------

func _loot(scene: Control) -> void:
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	PageTransition.settle(scene)


func test_loot_cards_keep_apart_and_the_first_focus_shows_no_tip() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var scene := await _netrun()
		_loot(scene)
		await _frames(3)
		var stickers: Node = scene._panel.find_child("Stickers", true, false)
		var cards: Array[Node] = stickers.get_children()
		for i in range(1, cards.size()):
			var a := cards[i - 1] as ZineCard
			var b := cards[i] as ZineCard
			var tilt := sin(deg_to_rad(ZineCard.REST_TILT_MAX)) * b.size.y
			assert_true(b.get_global_rect().position.x - a.get_global_rect().end.x >= tilt - 0.5,
				"x%.1f: %s keeps its tilt's room from %s (CACHE lay on JAM's cost)" % [scale, b.card_title, a.card_title])
		var first := cards[0] as ZineCard
		assert_null(FocusTip.tip_of(first), "x%.1f: the page's own focus shows no tip over Skip" % scale)
		await _close(scene)


func test_a_focus_tip_folds_narrower_to_keep_off_skip_at_big_text() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	Settings.set_pad_active(true)
	var scene := await _netrun()
	_loot(scene)
	await _frames(3)
	var stickers: Node = scene._panel.find_child("Stickers", true, false)
	var card := stickers.get_child(1) as ZineCard
	card.grab_focus()
	await _frames(3)
	var tip := FocusTip.tip_of(card)
	assert_not_null(tip, "a pad focus shows the whole text")
	if tip != null:
		var skip := scene._panel.find_child("Skip", true, false) as Control
		var r := tip.get_global_rect()
		assert_true(SCREEN.encloses(r), "on screen")
		assert_false(r.intersects(skip.get_global_rect()), "off Skip")
		for c in stickers.get_children():
			assert_false(r.intersects((c as Control).get_global_rect().grow(-2.0)), "off the loot cards (%s)" % (c as ZineCard).card_title)
	await _close(scene)


func test_the_crt_roll_waits_for_the_glass_to_show() -> void:
	_live()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var page := Control.new()
	page.size = Vector2(400, 300)
	holder.add_child(page)
	var pt := PageTransition.enter(page, PageTransition.Look.GLASS, Callable())
	assert_not_null(pt, "the glass enters")
	await BoundedWait.frozen_frames(get_tree(), 2)  # still the entrance's first frames
	var first := page.get_node_or_null(^"CrtRoll") as Control
	assert_true(first == null or not first.visible,
		"no roll band on the entrance's first frames (it read as a half-drawn screen on loot_pick's first frame)")
	# ANIM-R3 A8: then, frame by frame on the transition's own clock, the roll shows only once
	# the glass is fully shown (a fixed wait could outlast the fade under a loaded machine).
	for i in 120:
		await _frames(1)
		if not is_instance_valid(pt) or not PageTransition.running(page):
			break
		var roll := page.get_node_or_null(^"CrtRoll") as Control
		var k := pt.progress()
		if roll != null and roll.visible:
			assert_true(k >= PageTransition.FADE_SHARE - 0.0001,
				"the roll band shows only once the glass is fully shown: at %.2f" % k)
	PageTransition.settle(holder)


# --- E9 ----------------------------------------------------------------------------------------------------

func test_a_long_refusal_note_shows_all_its_lines() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var long := "CORE has no free asset slot. Take one off first, or put this asset on another Site with room; the Armory keeps the rest for the next raid."
	var t := ToastNote.show_on(holder, long + " " + long, true)
	await _frames(3)
	assert_true(t.whole(), "every line shows (a drag's refusal showed '...has no f')")
	assert_true(SCREEN.encloses(t.get_global_rect()), "inside the screen")


func test_a_drop_that_picks_lands_beside_its_button() -> void:
	var r := Rect2(600, 300, 160, 48)
	var at := DropLayer.beside_spot(r, Vector2(90, 40), SCREEN.size)
	var box := Rect2(at - Vector2(45, 20), Vector2(90, 40))
	assert_false(box.intersects(r), "beside JACK IN, never on its words")
	var edge := DropLayer.beside_spot(Rect2(10, 300, 160, 48), Vector2(90, 40), SCREEN.size)
	assert_true(edge.x > 170.0, "to the right when the left has no room")
	assert_true(DropLayer.LAND_BESIDE_KINDS.has("jack"))


func test_the_drag_ghost_reads() -> void:
	assert_gte(Motion.amplitude(&"drag_ghost_follow"), 0.9, "a dragged card is solid enough to read (0.6 was washed out)")


func test_the_wallet_rolls_with_the_top_bar() -> void:
	var scene := await _netrun()
	_live()
	RunManager.netrun.run.cycles = 100
	RunManager.netrun._open_shop()
	scene._show_current()
	await _frames(2)
	RunManager.netrun.run.cycles = 140
	scene._show_current()
	await _frames(2)
	var wallet := scene._panel.find_child("Wallet", true, false) as HudStats
	var bar: HudStats = scene.hud.stats
	var k := -1
	for i in bar.items.size():
		if String(bar.items[i][0]) == TextDb.mark("CYCLES"):
			k = i
	assert_true(k >= 0)
	assert_eq(wallet.shown_value(0), bar.shown_value(k), "the wallet shows what the top bar shows mid-roll (119 vs 120)")
	await _close(scene)


func test_spent_ram_floats_and_a_refused_buy_flashes_the_money() -> void:
	_live()
	var bar := RamBar.new()
	add_child_autofree(bar)
	bar.set_ram(10, 12)
	bar.set_ram(6, 12)
	assert_eq(bar.spend_text, tr("-%d RAM") % 4, "a respin's spend floats off the count")
	bar.finish_motion()
	assert_eq(bar.spend_text, "", "a skip ends it")
	var scene := await _netrun()
	RunManager.netrun.run.cycles = 10
	RunManager.netrun._open_shop()
	scene._show_current()
	await _frames(2)
	scene.price_refused(69)
	assert_eq(scene.hud.stats.refusal_text(), tr("NEED %d · HAVE %d") % [69, 10], "the CYCLES tag flashes NEED PRICE · HAVE CYCLES (ANIM-R3 A6j)")
	var wallet := scene._panel.find_child("Wallet", true, false) as HudStats
	assert_eq(wallet.refusal_text(), tr("NEED %d · HAVE %d") % [69, 10], "and the wallet")
	await _close(scene)


func test_the_preview_chip_says_playing() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/combat_scene.gd")
	assert_true(src.contains("tr(\"YOU PLAY %s\")"), "YOU PLAY JOLT (ANIM-R3 A6j), not IF JOLT or PLAYING JOLT")
	assert_false(src.contains("tr(\"IF %s\")"))


# --- E10 ----------------------------------------------------------------------------------------------------

func test_the_fx_layer_names_its_fractions() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/combat_fx_layer.gd")
	for inline in ["lerpf(1.35", "lerpf(0.6", "lerpf(1.0, 0.6", "p < 0.5", "p >= 0.5", "p * 2.0"]:
		assert_false(src.contains(inline), "no inline %s" % inline)


# --- New ids and words -------------------------------------------------------------------------------------

func test_new_motion_ids_are_required_and_words_are_translated_once() -> void:
	for id in [&"hit_absorb", &"ram_spend_float", &"price_refusal"]:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(Motion.has(id), "%s is in the table" % id)
	var csv := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for key in ["IF YOU SEND IT", "YOU PLAY %s", "-%d RAM", "TERMINAL EVENT"]:
		assert_true(csv.contains(key), "%s is exported for translation" % key)
