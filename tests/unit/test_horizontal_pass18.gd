extends GutTest
## Horizontal pass 18 fixes (GAP_ANALYSIS H18): Reset to defaults keeps the pad buttons;
## the combat pause menu uses the game theme and text scale; subtitles follow the text
## scale; a copy doesn't carry the neighbour's statuses; Stolen Intent doesn't carry
## permanent statuses.

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _has_pad(action: StringName) -> bool:
	for ev in InputMap.action_get_events(action):
		if ev is InputEventJoypadButton:
			return true
	return false


func test_reset_to_defaults_keeps_the_pad_buttons() -> void:
	Settings.reset_keybinds()
	for action in Settings.CONTROLLER_BINDS:
		if InputMap.has_action(action):
			assert_true(_has_pad(action), "%s keeps its pad button after a reset" % action)


func test_the_combat_pause_menu_follows_the_text_scale() -> void:
	RunManager.save_slot = "gut_test_pause_theme_h18"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var scene: Control = add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())
	scene.start_fight(&"triage_unit", 7)
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	scene.open_settings()
	await _frames()
	var menu: Control = scene._settings_panel
	assert_not_null(menu.theme, "the menu has the game theme")
	var b := menu.find_children("*", "Button", true, false)[0] as Button
	assert_eq(b.get_theme_font_size("font_size"), scene._end_turn_button.get_theme_font_size("font_size"), "same scaled size as the combat screen")
	scene.open_settings()
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_subtitles_follow_the_text_scale() -> void:
	Settings.set_text_scale(1.0)
	var small := Dialogue.text_label.get_theme_font_size("normal_font_size")
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var big := Dialogue.text_label.get_theme_font_size("normal_font_size")
	assert_eq(big, roundi(Dialogue.TEXT_FONT_SIZE * Settings.TEXT_SCALE_MAX))
	assert_true(big > small)


func test_a_copy_carries_none_of_the_neighbours_statuses() -> void:
	var atk := CombatFixture.slice(&"h18_atk", RC.SliceType.ATTACK, 6)
	var miss := CombatFixture.slice(&"h18_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)
	var deck: Array[CardData] = [CombatFixture.card(&"h18_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"h18_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, miss]), deck)
	var enemy := CombatFixture.enemy(&"h18_dummy", 300, CombatFixture.miss_wheel())
	var s := CombatSession.start(CombatFixture.resolver([cls, enemy]), cls.id, [enemy.id], 3)
	s.state.player.wheel.slot_firmware_ids[0] = &"mirror"
	s.state.player.wheel.slice_statuses[1] = RC.Status.OVERCLOCKED
	CombatFixture.land(s.state.player, 0, 1)  # Good towards slot 1: Mirror copies it
	var r := s.apply(CombatAction.end_turn())
	var amounts := []
	for e in CombatFixture.events_of(r, "attack"):
		amounts.append(int(e["amount"]))
	assert_eq(amounts, [6, 6], "the copy of an Overclocked slot is not boosted")
	assert_eq(s.state.player.wheel.slice_statuses[1], RC.Status.OVERCLOCKED, "the slot keeps its Overclock for its own landing")


func test_stolen_intent_swaps_no_permanent_status() -> void:
	var atk := CombatFixture.slice(&"h18_atk", RC.SliceType.ATTACK, 6)
	var miss := CombatFixture.slice(&"h18_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)
	var hit := CombatFixture.slice(&"h18_hit", RC.SliceType.ATTACK, 10)
	var deck: Array[CardData] = [CombatFixture.card(&"h18_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"h18_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, miss]), deck)
	var enemy := CombatFixture.enemy(&"h18_hitter", 300, CombatFixture.wheel([hit, hit, hit, hit, hit, hit]))
	var s := CombatSession.start(CombatFixture.resolver([cls, enemy]), cls.id, [enemy.id], 3, &"", 0, {"daemon_ids": ["stolen_intent"]})
	s.state.player.wheel.slot_firmware_ids[5] = &"burner"  # permanent Overclock on the Miss socket
	CombatFixture.land(s.state.player, 5, 1)  # a Good on the Miss: Stolen Intent swaps it
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "stolen_intent").size(), 1)
	var mine := CombatFixture.events_of(r, "attack").filter(func(e: Dictionary) -> bool: return e["attacker"] == &"player")
	assert_eq(int(mine[0]["amount"]), 10, "the stolen Attack 10 resolves without Burner's 1.5x")
