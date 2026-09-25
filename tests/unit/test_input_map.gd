extends GutTest
## Input map covers the GDD §9.5 bindings.

const ACTIONS: Array[StringName] = [&"nudge_left", &"nudge_right", &"cycle_target", &"end_turn", &"rewind", &"inspect",
	&"toggle_card_target", &"toggle_ring", &"toggle_nudge_wheel", &"toggle_direction", &"cycle_slot", &"respin", &"open_settings"]


func _keys_for(action: StringName) -> Array[InputEventKey]:
	var keys: Array[InputEventKey] = []
	for ev in InputMap.action_get_events(action):
		if ev is InputEventKey:
			keys.append(ev)
	return keys


func test_every_gdd_9_5_action_exists() -> void:
	for action in ACTIONS:
		assert_true(InputMap.has_action(action), "action %s" % action)


func test_nudge_is_q_and_e() -> void:
	assert_eq(_keys_for(&"nudge_left")[0].physical_keycode, KEY_Q)
	assert_eq(_keys_for(&"nudge_right")[0].physical_keycode, KEY_E)


func test_cycle_target_is_tab_and_end_turn_is_space() -> void:
	assert_eq(_keys_for(&"cycle_target")[0].physical_keycode, KEY_TAB)
	assert_eq(_keys_for(&"end_turn")[0].physical_keycode, KEY_SPACE)


func test_rewind_is_z_and_ctrl_z() -> void:
	var keys := _keys_for(&"rewind")
	assert_eq(keys.size(), 2)
	var plain := 0
	var with_ctrl := 0
	for k in keys:
		assert_eq(k.physical_keycode, KEY_Z)
		if k.ctrl_pressed:
			with_ctrl += 1
		else:
			plain += 1
	assert_eq(plain, 1, "one plain Z")
	assert_eq(with_ctrl, 1, "one Ctrl+Z")


func test_inspect_is_right_click() -> void:
	var mice := []
	for ev in InputMap.action_get_events(&"inspect"):
		if ev is InputEventMouseButton:
			mice.append(ev)
	assert_eq(mice.size(), 1, "one mouse binding (plus the M12 pad button)")
	assert_eq((mice[0] as InputEventMouseButton).button_index, MOUSE_BUTTON_RIGHT)


func test_card_picker_keys_are_d_f_and_x() -> void:
	assert_eq(_keys_for(&"toggle_direction")[0].physical_keycode, KEY_D)
	assert_eq(_keys_for(&"cycle_slot")[0].physical_keycode, KEY_F)
	assert_eq(_keys_for(&"respin")[0].physical_keycode, KEY_X)
