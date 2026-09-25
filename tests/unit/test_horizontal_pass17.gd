extends GutTest
## Horizontal pass 17 fixes (GAP_ANALYSIS H17): the pause menu blocks the mouse over the
## whole screen; a Shunt resolution is the landing for statuses, Stolen Intent and drones;
## a copy doesn't take the neighbour's Firmware or its permanent status; rebinding refuses
## reserved keys and keys another action holds.

var _atk: SliceData
var _miss: SliceData
var _deploy: SliceData


func before_each() -> void:
	_atk = CombatFixture.slice(&"h17_atk", RC.SliceType.ATTACK, 6)
	_miss = CombatFixture.slice(&"h17_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)
	_deploy = CombatFixture.slice(&"h17_deploy", RC.SliceType.DEPLOY, 1, RC.TargetRule.SELF)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _session(slices: Array, daemons: Array = [], hub: HubCoreData = null, enemy_slices: Array = []) -> CombatSession:
	var deck: Array[CardData] = [CombatFixture.card(&"h17_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"h17_class", 60, CombatFixture.wheel(slices, hub), deck)
	var enemy := CombatFixture.enemy(&"h17_dummy", 300, CombatFixture.miss_wheel() if enemy_slices.is_empty() else CombatFixture.wheel(enemy_slices))
	var ids := []
	for d in daemons:
		ids.append(String(d))
	return CombatSession.start(CombatFixture.resolver([cls, enemy]), cls.id, [enemy.id], 3, &"", 0, {"daemon_ids": ids})


## Lands pointer 0 on `slot` one tick clockwise of centre (a Good, towards slot + 1).
func _land_good(s: CombatSession, slot: int) -> void:
	CombatFixture.land(s.state.player, slot, 1)


func test_the_pause_menu_backdrop_covers_the_screen_and_eats_clicks() -> void:
	var menu := PauseMenu.new()
	menu.position = Vector2(200, 100)
	add_child_autofree(menu)
	await _frames()
	var backdrop: ColorRect = menu.get_node("Backdrop")
	assert_eq(backdrop.mouse_filter, Control.MOUSE_FILTER_STOP)
	assert_eq(backdrop.get_index(), 0, "drawn behind the menu")
	assert_true(backdrop.get_global_rect().encloses(get_viewport().get_visible_rect()), "covers the whole screen")


func test_a_shunt_onto_an_overclocked_slot_burns_it_out() -> void:
	var s := _session([_atk, _atk, _atk, _atk, _atk, _miss])
	s.state.player.wheel.slot_firmware_ids[0] = &"shunt"
	s.state.player.wheel.slice_statuses[1] = RC.Status.OVERCLOCKED
	_land_good(s, 0)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.player.wheel.slice_statuses[1], RC.Status.CORRUPTED, "the shunted slot burns out like a landing")


func test_a_copy_does_not_take_the_neighbours_burner() -> void:
	var s := _session([_atk, _atk, _atk, _atk, _atk, _miss])
	s.state.player.wheel.slot_firmware_ids[0] = &"shunt"
	s.state.player.wheel.slot_firmware_ids[1] = &"burner"
	var r := s.resolver
	var base := r._readout(s.state, s.state.player, 0)
	var copy: Dictionary = r._neighbor_resolution(s.state, base, 1, 1.0)
	assert_eq(copy["firmware"], null)
	assert_eq(copy["permanent_status"], RC.Status.NONE, "no free permanent Overclock")


func test_stolen_intent_fires_on_a_shunted_miss() -> void:
	var s := _session([_atk, _atk, _atk, _atk, _atk, _miss], [&"stolen_intent"], null, [_atk, _atk, _atk, _atk, _atk, _atk])
	s.state.player.wheel.slot_firmware_ids[4] = &"shunt"
	_land_good(s, 4)  # a Good towards slot 5: the Shunt resolves the Miss instead
	var res := s.apply(CombatAction.end_turn())
	assert_true(CombatFixture.events_of(res, "stolen_intent").size() > 0, "Stolen Intent swapped the shunted Miss")


func test_drones_follow_the_slot_a_shunt_resolves() -> void:
	var s := _session([_atk, _atk, _atk, _atk, _atk, _miss])
	var r := s.resolver
	s.state.player.wheel.slot_firmware_ids[2] = &"shunt"
	_land_good(s, 2)
	var slots := []
	for res in r._collect_resolutions(s.state):
		if res["owner"] == s.state.player and CombatResolver.is_landing(res):
			slots.append(int(res["slice_index"]))
	assert_eq(slots, [3], "slot 3 resolves, so a drone on slot 3 is the one that fires")


func test_rebinding_refuses_card_keys_and_keys_in_use() -> void:
	assert_string_contains(Settings.bind_error(&"end_turn", KEY_1), "reserved")
	var nudge := Settings.key_for(&"nudge_left")
	assert_string_contains(Settings.bind_error(&"end_turn", nudge), "used by")
	assert_eq(Settings.bind_error(&"nudge_left", nudge), "", "its own key is fine")
	var panel := SettingsPanel.new()
	add_child_autofree(panel)
	panel.show_section("Controls")
	await _frames()
	var before := Settings.key_for(&"end_turn")
	panel.begin_rebind(&"end_turn")
	var one := InputEventKey.new()
	one.physical_keycode = KEY_1
	one.pressed = true
	assert_true(panel.handle_key(one))
	assert_eq(Settings.key_for(&"end_turn"), before, "the card key was refused")
	assert_eq(panel.rebinding, &"end_turn", "still waiting for another key")
	var esc := InputEventKey.new()
	esc.physical_keycode = KEY_ESCAPE
	esc.pressed = true
	panel.handle_key(esc)
