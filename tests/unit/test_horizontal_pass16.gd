extends GutTest
## Horizontal pass 16 fixes (GAP_ANALYSIS H16): a Mirror copy is not a landing (Daemons skip
## it, it doesn't resolve the Miss) while a Shunt resolution is; a fixed boss layout stops
## an earlier orbit; arrow keys can be rebound; the combat pause menu is never clipped by
## the netrun scroll; Esc in the pause-menu Codex returns to the menu.

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


## Operative wheel Atk, Atk, Atk, Atk, Atk, Miss; Firmware `fw_id` on slot 0.
func _session(fw_id: StringName, daemons: Array) -> CombatSession:
	var atk := CombatFixture.slice(&"h16_atk", RC.SliceType.ATTACK, 6)
	var miss := CombatFixture.slice(&"h16_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)
	var deck: Array[CardData] = [CombatFixture.card(&"h16_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"h16_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, miss]), deck)
	var enemy := CombatFixture.enemy(&"h16_dummy", 300, CombatFixture.miss_wheel())
	var ids := []
	for d in daemons:
		ids.append(String(d))
	var s := CombatSession.start(CombatFixture.resolver([cls, enemy]), cls.id, [enemy.id], 3, &"", 0, {"daemon_ids": ids})
	s.state.player.wheel.slot_firmware_ids[0] = fw_id
	return s


func test_a_mirror_perfect_fires_a_daemon_once() -> void:
	var s := _session(&"mirror", [&"kernel_sync"])
	CombatFixture.land(s.state.player, 0)  # Perfect on slot 0: Mirror copies both neighbours
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "attack").size(), 2, "the landing and its Attack neighbour copy (the other neighbour is the Miss)")
	assert_eq(s.state.damage_bonus, 1, "Kernel Sync once for the one Perfect")


func test_a_mirror_copy_of_the_miss_does_not_resolve_the_miss() -> void:
	var s := _session(&"mirror", [])
	CombatFixture.land(s.state.player, 0)  # slot 5 (the Miss) is a Mirror neighbour of slot 0
	s.apply(CombatAction.end_turn())
	assert_false(s.state.miss_resolved, "only a landing resolves the Miss (Cold Exit)")


func test_a_shunt_resolution_counts_as_the_landing() -> void:
	var r := {"derived": true, "landing": true}
	assert_true(CombatResolver.is_landing(r), "a Shunt resolves instead of the landing")
	assert_false(CombatResolver.is_landing({"derived": true}), "a Mirror copy does not")
	assert_true(CombatResolver.is_landing({}))


func test_commons_array_locks_on_in_its_last_phase() -> void:
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"commons_array"], 7)
	var boss := s.state.get_combatant(&"enemy_0")
	boss.hp = int(boss.max_hp * 0.6)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.pointer_orbit, 4, "66%: orbiting")
	s.state.get_combatant(&"enemy_0").hp = int(boss.max_hp * 0.3)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.pointer_orbit, 0, "33%: the three readers lock on")


func test_arrow_keys_can_be_rebound() -> void:
	var before := Settings.key_for(&"nudge_left")
	var panel := SettingsPanel.new()
	add_child_autofree(panel)
	panel.show_section("Controls")
	await _frames()
	panel.begin_rebind(&"nudge_left")
	var down := InputEventKey.new()
	down.keycode = KEY_LEFT
	down.physical_keycode = KEY_LEFT
	down.pressed = true
	get_viewport().push_input(down)
	await _frames()
	assert_eq(Settings.key_for(&"nudge_left"), KEY_LEFT, "Left is the new nudge -1")
	assert_eq(panel.rebinding, &"", "the rebind finished")
	Settings.rebind(&"nudge_left", before)


func test_the_netrun_fight_pause_menu_is_not_clipped() -> void:
	RunManager.save_slot = "gut_test_pause_clip_h16"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var scene: Control = add_child_autofree(load("res://scenes/netrun_map/netrun_scene.tscn").instantiate())
	scene.start_run(1)
	scene.enter_node(RunManager.netrun.available_nodes()[0])
	await _frames()
	var combat: Control = scene.combat_scene
	combat.open_settings()
	await _frames()
	var rect: Rect2 = combat._settings_panel.get_global_rect()
	var view := get_viewport().get_visible_rect()
	assert_true(combat._settings_panel.get_parent() is CanvasLayer, "on its own layer, outside the netrun scroll")
	assert_true(view.encloses(rect), "the menu %s fits the %s screen" % [rect, view])
	combat.open_settings()
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_esc_in_the_codex_returns_to_the_menu() -> void:
	var menu := PauseMenu.new()
	add_child_autofree(menu)
	var resumed := []
	menu.resumed.connect(func() -> void: resumed.append(true))
	menu.show_codex()
	await _frames()
	var esc := InputEventAction.new()
	esc.action = &"ui_cancel"
	esc.pressed = true
	menu._unhandled_input(esc)
	assert_null(menu.codex_note, "the Codex closed")
	assert_eq(resumed.size(), 0, "the menu stays open")
