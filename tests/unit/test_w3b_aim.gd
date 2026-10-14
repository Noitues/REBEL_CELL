extends GutTest
## Change plan 1, wave 3b (W3B-AIM): B1 stuck aim, B2 UNDO reason, B6, B7, B8. Seeded headless repros kept as regressions.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_w3b_aim"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _combat(card_id: StringName) -> Control:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	var st: CombatState = scene.engine.state()
	st.hand[0] = card_id
	scene._refresh(st)
	await _frames(2)
	return scene


## What is left of an aim on screen once no card is selected.
func _residue(scene: Control) -> Array[String]:
	var out: Array[String] = []
	if scene.selecting >= 0:
		out.append("selecting=%d" % scene.selecting)
		return out
	if scene.ram_note.aiming:
		out.append("ram_note.aiming")
	if scene.fx_layer.reticle_visible:
		out.append("reticle")
	for v in scene._views():
		if not v.valid_zones.is_empty():
			out.append("valid_zones@%s" % v.name)
		if not v.hover_zone.is_empty():
			out.append("hover_zone@%s" % v.name)
	return out


func test_w3b_b1_every_interruption_of_an_aim_leaves_no_residue() -> void:
	var failures: Array[String] = []
	for card_id in [&"fine_tune", &"brute_spin", &"jolt"]:
		for way in ["nudge", "target", "end_turn", "respin", "other_card", "undo", "rewind_key", "esc", "right_click", "confirm"]:
			var scene := await _combat(card_id)
			var base: int = scene.ram_note.pending
			scene.select_card(0)
			await _frames(2)
			if scene.selecting < 0:
				scene.get_parent().queue_free()
				continue
			match way:
				"nudge":
					scene.nudge(1)
				"target":
					scene._submit(CombatAction.target(scene.engine.state().enemies[0].id))
				"end_turn":
					scene.end_turn()
				"respin":
					scene.respin()
				"other_card":
					scene.select_card(1)
				"undo":
					scene._rewind_button.pressed.emit()
				"rewind_key":
					scene.rewind()
				"esc":
					var e := InputEventAction.new()
					e.action = &"ui_cancel"
					e.pressed = true
					scene._input(e)
				"right_click":
					var m := InputEventMouseButton.new()
					m.button_index = MOUSE_BUTTON_RIGHT
					m.pressed = true
					scene._input(m)
				"confirm":
					scene.confirm_selection()
			scene.skip_motion()
			await _frames(3)
			var res := _residue(scene)
			if way == "other_card":
				scene.cancel_selection()
				res = _residue(scene)
			if not res.is_empty() or scene.ram_note.pending != base:
				failures.append("%s/%s: %s pending %d (was %d)" % [card_id, way, res, scene.ram_note.pending, base])
			scene.get_parent().queue_free()
			await _frames(1)
	print("B1 failures: ", failures)
	assert_eq(failures, [] as Array[String], "no aim residue")


## B1 (saved game): an aim is view state, never saved; a combat saved mid-aim and restored comes back with no aim.
func test_w3b_b1_a_saved_combat_carries_no_aim() -> void:
	var scene := await _combat(&"fine_tune")
	scene.select_card(0)
	await _frames(2)
	assert_gt(scene.selecting, -1, "aiming")
	var saved: Dictionary = scene.engine.session.to_dict()
	for key in saved:
		assert_false(String(key).contains("aim") or String(key).contains("select"), "no aim key in a saved combat: %s" % key)
	var session := CombatSession.from_dict(scene.engine.resolver, JSON.parse_string(JSON.stringify(saved)))
	assert_eq(session.state_hash(), scene.engine.session.state_hash(), "same state")
	assert_eq(session.checkpoint_cause, scene.engine.session.checkpoint_cause, "same UNDO reason source")
	scene.get_parent().queue_free()


## B2: UNDO's block names the random event the checkpoint stands on, the same every time it is asked.
func test_w3b_b2_undo_block_names_the_event() -> void:
	var scene := await _combat(&"malware_drop")
	var session: CombatSession = scene.engine.session
	assert_eq(String(session.checkpoint_cause["kind"]), "turn", "turn start")
	assert_false(scene.engine.can_rewind())
	# Each random event names itself; the checkpoint (and the reason) holds until the next one.
	scene.play_card(0)
	scene.skip_motion()
	await _frames(2)
	assert_eq(String(session.checkpoint_cause["kind"]), "card", "the random pick made the checkpoint")
	assert_eq(scene.undo_block_text(), tr(scene.UNDO_BLOCKED_CARD) % "Malware Drop", "names the card")
	assert_false(scene.engine.can_rewind(), "rewind never crosses the checkpoint")
	var hash_before := session.state_hash()
	scene.rewind()
	assert_eq(session.state_hash(), hash_before, "a blocked UNDO changes nothing")
	assert_eq(scene.toast.label.text, scene.undo_block_text(), "and says why")
	assert_eq(scene._rewind_button.tooltip_text, scene.undo_block_text(), "UNDO's tooltip says the same")
	# A nudge after it is undoable; the block comes back with the same words afterwards.
	scene.nudge(1)
	scene.skip_motion()
	assert_true(scene.engine.can_rewind(), "a nudge after the roll can be undone")
	scene.rewind()
	assert_false(scene.engine.can_rewind())
	assert_eq(scene.undo_block_text(), tr(scene.UNDO_BLOCKED_CARD) % "Malware Drop", "stable: same reason")
	scene.respin()
	scene.skip_motion()
	assert_eq(scene.undo_block_text(), tr(scene.UNDO_BLOCKED_RESPIN), "a respin names itself")
	var again: CombatSession = CombatSession.from_dict(scene.engine.resolver, JSON.parse_string(JSON.stringify(session.to_dict())))
	assert_eq(again.checkpoint_cause, session.checkpoint_cause, "the reason survives a save")
	scene.get_parent().queue_free()


## B6: Q/E with no free nudge and no RAM do nothing to the wheel, and say why (the tutorial's turn 7 state).
func test_w3b_b6_nudge_key_with_no_free_nudge_says_why() -> void:
	var scene := await _combat(&"fine_tune")
	var st: CombatState = scene.engine.state()
	st.free_nudges = 0
	st.ram = 0
	scene._refresh(st)
	await _frames(2)
	var rot: int = st.player.wheel.rotation
	scene.nudge(1)
	await _frames(2)
	assert_eq(scene.engine.state().player.wheel.rotation, rot, "the needle did not move")
	assert_true(scene.toast.label.text.contains("free nudge") and scene.toast.label.text.contains("RAM"), "says why: %s" % scene.toast.label.text)
	# With a free nudge the same key moves the needle.
	st = scene.engine.state()
	st.free_nudges = 1
	scene._refresh(st)
	scene.nudge(1)
	scene.skip_motion()
	assert_ne(scene.engine.state().player.wheel.rotation, rot, "a free nudge moves it")
	scene.get_parent().queue_free()


## B7 (single tester; not reproduced from the described steps): a respin that spends RAM always turns the wheel and
## names where it landed.
func test_w3b_b7_respin_spends_ram_and_turns_the_wheel() -> void:
	for combat_seed in [5, 6, 7, 8]:
		var scene := await _combat(&"fine_tune")
		scene.start_fight(&"collections_agent", combat_seed)
		scene.skip_motion()
		var st: CombatState = scene.engine.state()
		var rot: int = st.player.wheel.rotation
		var ram: int = st.ram
		scene.respin()
		scene.skip_motion()
		await _frames(2)
		var after: CombatState = scene.engine.state()
		assert_lt(after.ram, ram, "RAM spent")
		assert_ne(after.player.wheel.rotation, rot, "seed %d: the wheel turned" % combat_seed)
		assert_true(scene.toast.label.text.begins_with("RESPIN -"), "a note names the landing: %s" % scene.toast.label.text)
		scene.get_parent().queue_free()
		await _frames(1)


## B8 (single tester; not reproduced): after SEND IT on turn 1 of an Elite, turn 2 takes input at once.
func test_w3b_b8_elite_turn_two_takes_input() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"recall_unit", 5)
	await _frames(2)
	scene.end_turn()
	scene.skip_motion()
	await _frames(3)
	assert_eq(scene.engine.state().turn, 2, "turn 2")
	assert_false(scene.motion_busy(), "no motion holds the screen")
	assert_eq(scene.selecting, -1)
	assert_false(scene._dragging, "no drag lock")
	var before: int = scene.engine.session.history.size()
	scene.nudge(1)
	await _frames(2)
	if scene.engine.state().free_nudges > 0 or scene.engine.state().ram > 0:
		assert_gt(scene.engine.session.history.size(), before, "the key acted")
	scene.respin()
	scene.end_turn()
	scene.skip_motion()
	await _frames(2)
	assert_gt(scene.engine.state().turn, 2, "SEND IT works again")
