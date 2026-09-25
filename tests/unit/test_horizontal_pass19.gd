extends GutTest
## Horizontal pass 19 fixes (GAP_ANALYSIS H19): a refused rebind never widens Options past
## the screen; every combat key hint follows the binds and refreshes on a rebind; a Mirror
## copy of a Parasite'd slot is still halved.

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.reset_keybinds()


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func test_a_refused_rebind_keeps_the_panel_on_screen() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var menu := PauseMenu.new()
	menu.position = Vector2((1280 - PauseMenu.MENU_SIZE.x) / 2.0, 100)
	add_child_autofree(menu)
	menu.show_options()
	await _frames()
	menu.settings_panel.show_section("Controls")
	await _frames()
	var before := menu.settings_panel.get_combined_minimum_size().x
	menu.settings_panel.begin_rebind(&"nudge_left")
	var taken := InputEventKey.new()
	taken.physical_keycode = Settings.key_for(&"toggle_direction")
	taken.pressed = true
	menu.settings_panel.handle_key(taken)
	await _frames()
	assert_string_contains((menu.settings_panel.find_child("BindNote", true, false) as Label).text, "press another key")
	assert_true(menu.settings_panel.get_combined_minimum_size().x <= maxf(before, PauseMenu.MENU_SIZE.x), "the refusal wraps instead of widening the grid")


func test_combat_key_hints_follow_a_rebind() -> void:
	RunManager.save_slot = "gut_test_hints_h19"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var scene: Control = add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())
	scene.start_fight(&"triage_unit", 7)
	await _frames()
	Settings.rebind(&"toggle_ring", KEY_G)
	Settings.rebind(&"rewind", KEY_B)
	await _frames()
	var g := OS.get_keycode_string(KEY_G)
	assert_string_contains(scene._nudge_ring_option.get_item_text(0), "[%s]" % g)
	assert_string_contains(scene._rewind_button.text, "[%s]" % OS.get_keycode_string(KEY_B))
	assert_string_contains(scene._settings_button.text, "[%s]" % Settings.key_text(&"open_settings"))
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_a_mirror_copy_of_a_parasited_slot_is_halved() -> void:
	var atk := CombatFixture.slice(&"h19_atk", RC.SliceType.ATTACK, 6)
	var miss := CombatFixture.slice(&"h19_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)
	var deck: Array[CardData] = [CombatFixture.card(&"h19_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"h19_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, miss]), deck)
	var enemy := CombatFixture.enemy(&"h19_dummy", 300, CombatFixture.miss_wheel())
	var s := CombatSession.start(CombatFixture.resolver([cls, enemy]), cls.id, [enemy.id], 3)
	s.state.player.wheel.slot_firmware_ids[0] = &"mirror"
	s.state.player.wheel.slice_statuses[1] = RC.Status.PARASITE
	CombatFixture.land(s.state.player, 0, 1)  # Good towards slot 1: Mirror copies it
	var r := s.apply(CombatAction.end_turn())
	var amounts := []
	for e in CombatFixture.events_of(r, "attack"):
		amounts.append(int(e["amount"]))
	assert_eq(amounts, [6, 3], "the Parasite halves the copy as it halves the slot")
