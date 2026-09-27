extends GutTest
## Horizontal pass 21, combat (GAP_ANALYSIS H21 1-9, 16-20): pad nudges choose wheel and
## ring on the triggers; a device switch keeps focus; satellite and Undock aiming take
## their way from the side; random resolve picks show odds; the preview after a
## reshuffling card equals the result; HITS counts landed damage; tags and HP stay in view
## and the toast sits over the hand; last-turn lines; plain words; card pictograms; the
## Modem spinner runs the same way round; old keybinds are dropped.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_pass21"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(false)
	Settings.reset_keybinds()
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


func _combat(enemy: StringName = &"compliance_officer", scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, 5)
	await _frames()
	return scene


func _hand(scene: Control, cards: Array[StringName]) -> void:
	var s: CombatState = scene.engine.state()
	s.hand = cards
	s.ram = s.max_ram
	var none: Array[Dictionary] = []
	scene.engine.state_changed.emit(s, none)


func _trigger(scene: Control, axis: int, value: float) -> void:
	var m := InputEventJoypadMotion.new()
	m.axis = axis
	m.axis_value = value
	scene._unhandled_input(m)


func test_the_pad_triggers_choose_the_nudge_wheel_and_ring() -> void:
	var scene := await _combat()
	assert_eq(scene._nudge_wheel_option.selected, 0)
	_trigger(scene, JOY_AXIS_TRIGGER_LEFT, 0.7)
	_trigger(scene, JOY_AXIS_TRIGGER_LEFT, 0.9)  # still held: no second toggle
	assert_eq(scene._nudge_wheel_option.selected, 1, "LT switches the nudges to the target, once per squeeze")
	_trigger(scene, JOY_AXIS_TRIGGER_LEFT, 0.0)
	_trigger(scene, JOY_AXIS_TRIGGER_LEFT, 0.8)
	assert_eq(scene._nudge_wheel_option.selected, 0, "a second squeeze switches back")
	_trigger(scene, JOY_AXIS_TRIGGER_RIGHT, 0.8)
	assert_eq(scene._nudge_ring_option.selected, 1, "RT switches the ring")
	Settings.set_pad_active(true)
	await _frames()
	assert_string_contains(scene._status.text, "[LT]", "the status line names the triggers on a pad")


func test_switching_to_the_pad_keeps_focus_on_the_hand() -> void:
	var scene := await _combat()
	var card: Control = scene._hand_box.get_child(1)
	card.grab_focus()
	await _frames(1)
	Settings.set_pad_active(true)
	await _frames(2)
	var owner := get_viewport().gui_get_focus_owner()
	assert_not_null(owner, "something keeps focus")
	assert_eq(owner.get_parent(), scene._hand_box, "a card keeps it")


func test_a_nudge_card_on_a_satellite_goes_the_way_of_the_side() -> void:
	var scene := await _combat(&"collections_agent")
	_hand(scene, [&"fine_tune"])
	var s: CombatState = scene.engine.state()
	var sat: CombatantState = null
	for e in s.living_enemies(true):
		if e.is_satellite:
			sat = e
	assert_not_null(sat, "Collections Agent brings a drone")
	scene.select_card(0)
	var host: WheelView = scene._enemy_views[sat.host_id]
	var rot := sat.wheel.rotation
	var res := sat.resistance
	host.drag_dropped.emit({"kind": "satellite", "id": sat.id, "direction": -1}, {"hand_index": 0})
	var after: CombatantState = scene.engine.state().get_combatant(sat.id)
	assert_true(after.wheel.rotation < rot or after.resistance < res, "the anticlockwise side nudges it back")


func test_undock_offers_both_sides() -> void:
	var scene := await _combat(&"collections_agent")
	_hand(scene, [&"undock"])
	var ways := {}
	for a in CardTargeting.options(scene.engine.resolver, scene.engine.state(), 0):
		ways[a.direction] = true
	assert_true(ways.has(1) and ways.has(-1), "Undock can go either way")


func test_random_resolve_picks_show_odds_not_the_slot() -> void:
	var scene := await _combat(&"dosage_dispenser")
	for turn in 4:
		var preview: CombatResult = scene.engine.preview_end_turn()
		var random := false
		for e in preview.events:
			random = random or (String(e.get("type", "")) == "status" and bool(e.get("random", false)))
		if random:
			var v: WheelView = scene._player_view
			assert_eq((v.outcome.get("statuses", []) as Array).size(), 0, "no ghost on the rolled slot")
			var texts := PackedStringArray()
			for c in v.intent.get("chips", []):
				texts.append(String(c["text"]))
			assert_true(" ".join(texts).contains("RANDOM"), "odds instead (%s)" % [texts])
			return
		scene.end_turn()
	pass_test("no random pick in these turns")


func test_the_preview_after_a_reshuffling_card_equals_the_result() -> void:
	var scene := await _combat(&"dosage_dispenser")
	var s: CombatState = scene.engine.state()
	s.discard_pile.append_array(s.draw_pile)
	s.draw_pile.clear()
	s.hand = [&"pull"]
	s.ram = s.max_ram
	var a := CombatAction.play_card(0, &"player")
	var predicted: CombatResult = scene.engine.preview_turn_after(a)
	assert_not_null(predicted)
	scene.engine.submit(a)
	var real: CombatResult = scene.engine.session.apply(CombatAction.end_turn())
	assert_eq(predicted.state.player.wheel.slice_statuses, real.resolved_state.player.wheel.slice_statuses, "same statuses")
	assert_eq(predicted.state.player.hp, real.resolved_state.player.hp, "same HP")


func test_hits_count_the_damage_that_lands() -> void:
	var scene := await _combat()
	for turn in 3:
		var preview: CombatResult = scene.engine.preview_end_turn()
		var o := CombatOutcome.between(scene.engine.state(), preview.state, preview.events)
		var totals := {}
		for e in preview.events:
			if String(e.get("type", "")) == "damage":
				var src := String(e["attacker"])
				totals[src] = int(totals.get(src, 0)) + int(e["amount"])
		for id in o.combatants:
			assert_eq(int(o.combatants[id]["dealt"]), int(totals.get(String(id), 0)), "%s dealt" % id)
		scene.end_turn()
		if scene.engine.state().is_over():
			break


func test_tags_and_hp_stay_in_view_and_the_toast_sits_over_the_hand() -> void:
	for scale in [1.3, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"compliance_officer", scale)
		scene._show_respin_odds()
		await _frames(1)
		for v in scene._views():
			assert_true(v.get_global_rect().grow(0.5).encloses(v.intent_rect()), "tag inside its view at %.1f" % scale)
		scene.engine.state().ram = 0
		scene.respin()
		await _frames(1)
		assert_eq(scene.layout_violations(), [], "no violation with the toast up at %.1f" % scale)
		assert_true(scene._hand_box.get_global_rect().intersects(scene.toast.get_global_rect()), "the toast sits over the hand")


func test_send_it_leaves_a_last_turn_line_until_the_player_acts() -> void:
	var scene := await _combat()
	scene.end_turn()
	await _frames(1)
	assert_string_contains(scene._player_view.last_turn, "LAST TURN", "what the resolve did")
	for v in scene._enemy_views.values():
		assert_string_contains(v.last_turn, "LAST TURN")
	scene.nudge_wheel(&"player", 1)
	assert_eq(scene._player_view.last_turn, "", "the next action clears it")


func test_tags_speak_in_words() -> void:
	var scene := await _combat()
	var title := String(scene._player_view.intent.get("text", ""))
	var worded := false
	for w in Palette.SLICE_WORDS.values():
		worded = worded or title.begins_with(String(w))
	assert_true(worded, "whole words on the tag (%s)" % title)
	for c in scene._player_view.intent.get("chips", []):
		assert_false(String(c["text"]).contains("BLK"), "BLOCK, not BLK")


func test_every_card_draws_what_it_does() -> void:
	for id in ContentRegistry.all_ids():
		var card := ContentRegistry.get_content(id) as CardData
		if card == null:
			continue
		var p := ZineCard.pictos_of(card)
		var mapped := false
		for e in card.effects:
			mapped = mapped or (e != null and e.type != RC.EffectType.CUSTOM and e.type != RC.EffectType.MODIFY_HEAT)
		if mapped:
			assert_false(p.is_empty(), "%s has pictograms" % id)


func test_the_modem_spinner_runs_the_same_way_as_combat() -> void:
	var breaker := ContentRegistry.get_content(&"breaker") as ClassData
	var ids: Array[StringName] = []
	var fw: Array[StringName] = []
	for s in breaker.starting_wheel.slots:
		ids.append(s.slice.id)
		fw.append(&"")
	var view := SpinnerView.new(ids, fw, ContentLookup.new().add_registry(ContentRegistry))
	add_child_autofree(view)
	assert_true(view._angle(1) < -PI * 0.5, "slot 1 anticlockwise of slot 0, as the combat wheel draws it")


func test_retired_keybinds_are_dropped_on_load() -> void:
	var saved := Settings.to_dict()
	var d := saved.duplicate(true)
	d["keybinds"] = {"toggle_direction": KEY_G, "nudge_left": KEY_H}
	Settings.from_dict(d)
	assert_false(Settings.keybinds.has("toggle_direction"))
	assert_true(Settings.keybinds.has("nudge_left"))
	Settings.from_dict(saved)
