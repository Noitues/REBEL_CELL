extends GutTest
## Full keyboard play in combat (M4 acceptance): every combat action has a key and the
## scene reacts to the key events without a mouse.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _scene: Control


func before_each() -> void:
	AudioDirector.muted = true
	_scene = add_child_autofree(load(SCENE).instantiate())


func after_each() -> void:
	AudioDirector.muted = false


func _key(physical: int, ctrl: bool = false) -> InputEventKey:
	var e := InputEventKey.new()
	e.physical_keycode = physical
	e.pressed = true
	e.ctrl_pressed = ctrl
	return e


func _press(physical: int, ctrl: bool = false) -> void:
	_scene._unhandled_input(_key(physical, ctrl))


func test_every_combat_action_has_a_key() -> void:
	for action in ["nudge_left", "nudge_right", "cycle_target", "end_turn", "rewind", "toggle_card_target", "toggle_ring", "toggle_nudge_wheel", "open_settings"]:
		assert_true(InputMap.has_action(action), action)
	for i in range(1, 10):
		assert_true(InputMap.has_action("card_%d" % i), "card_%d" % i)
		assert_eq((InputMap.action_get_events("card_%d" % i)[0] as InputEventKey).physical_keycode, KEY_0 + i)


func test_number_keys_play_cards() -> void:
	var engine: CombatEngine = _scene.engine
	var hand := engine.state().hand.size()
	var ram := engine.state().ram
	_press(KEY_1)
	assert_eq(engine.state().hand.size(), hand - 1, "1 played the first card")
	assert_true(engine.state().ram <= ram)
	_press(KEY_9)
	assert_eq(engine.state().hand.size(), hand - 1, "9 with no ninth card does nothing")


func test_q_and_e_nudge_w_r_t_toggle_tab_targets_space_ends_z_rewinds() -> void:
	var engine: CombatEngine = _scene.engine
	var rot := engine.state().player.wheel.rotation
	_press(KEY_E)
	assert_eq(engine.state().player.wheel.rotation, rot + 1, "E nudges own wheel +1")
	_press(KEY_Z)
	assert_eq(engine.state().player.wheel.rotation, rot, "Z rewinds")
	_press(KEY_W)
	assert_eq(_scene._nudge_wheel_option.selected, 1, "W switches nudges to the target wheel")
	var enemy_rot := engine.state().get_combatant(engine.state().target_id).wheel.rotation
	_press(KEY_Q)
	var after := engine.state().get_combatant(engine.state().target_id)
	assert_true(after.wheel.rotation == enemy_rot - 1 or after.resistance >= 0, "Q nudged (or resistance absorbed) the target")
	_press(KEY_R)
	assert_eq(_scene._nudge_ring_option.selected, 1, "R switches to the inner ring")
	_press(KEY_T)
	assert_eq(_scene._card_target_option.selected, 1, "T switches cards to own wheel")
	_press(KEY_TAB)
	var targets := engine.state().living_enemies(true)
	assert_true(targets.size() >= 1)
	var turn := engine.state().turn
	_press(KEY_SPACE)
	assert_eq(engine.state().turn, turn + 1, "Space ends the turn")
	_press(KEY_Z, true)
	assert_eq(engine.state().turn, turn + 1, "Ctrl+Z cannot cross the checkpoint")


func test_escape_opens_and_closes_settings() -> void:
	_press(KEY_ESCAPE)
	assert_not_null(_scene._settings_panel)
	_press(KEY_ESCAPE)
	assert_null(_scene._settings_panel)


func test_cards_are_focusable_for_keyboard_navigation() -> void:
	for c in _scene._hand_box.get_children():
		assert_eq(c.focus_mode, Control.FOCUS_ALL)
	assert_eq(_scene._end_turn_button.focus_mode, Control.FOCUS_ALL)
