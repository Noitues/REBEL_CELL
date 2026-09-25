extends GutTest
## Horizontal pass 15 fixes (GAP_ANALYSIS H15): Daemons fire once per landing, nothing
## acts behind the pause menu, its Options is never clipped, Intel shows the real phase
## layouts, a Flip can't refresh Firmware limits, Repair shows its price, fixed statuses
## preview as fixed, ICE achievement levels come from the config.

var _cfg: CampaignConfigData
var _text_scale_before: float = 1.0


func before_all() -> void:
	_cfg = CombatFixture.config()
	_text_scale_before = Settings.text_scale


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func test_a_daemon_fires_once_per_perfect_even_when_the_slice_resolves_twice() -> void:
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"triage_unit"], 5, &"", 0, {"daemon_ids": ["kernel_sync"]})
	CombatFixture.land(s.state.player, 0)  # Perfect: the Breaker Core resolves it twice
	var r := s.apply(CombatAction.end_turn())
	assert_true(CombatFixture.events_of(r, "retrigger").size() > 0, "the slice resolved more than once")
	assert_eq(s.state.damage_bonus, 1, "Kernel Sync: +1 per Perfect, as its text says")


func _begin(slot: String) -> void:
	RunManager.save_slot = slot
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func _end() -> void:
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _press(keycode: Key) -> void:
	var down := InputEventKey.new()
	down.keycode = keycode
	down.physical_keycode = keycode
	down.pressed = true
	get_viewport().push_input(down)
	var up := down.duplicate() as InputEventKey
	up.pressed = false
	get_viewport().push_input(up)


func test_hotkeys_do_nothing_behind_the_pause_menu() -> void:
	_begin("gut_test_pause_keys_h15")
	var scene: Control = add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())
	scene.start_fight(&"triage_unit", 7)
	await _frames()
	scene.open_settings()
	await _frames()
	var turn: int = scene.engine.state().turn
	_press(KEY_SPACE)
	_press(KEY_1)
	_press(KEY_E)
	await _frames()
	assert_eq(scene.engine.state().turn, turn, "Space did not end the turn behind the menu")
	scene.open_settings()
	await _frames()
	_press(KEY_SPACE)
	await _frames()
	assert_eq(scene.engine.state().turn, turn + 1, "with the menu closed Space ends the turn again")
	_end()


func test_pause_menu_options_grow_with_their_section() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var menu := PauseMenu.new()
	add_child_autofree(menu)
	menu.show_options()
	await _frames()
	for section in ["Accessibility", "Controls", "Language"]:
		menu.settings_panel.show_section(section)
		await _frames()
		var need := menu.settings_panel._paper_panel.content.get_combined_minimum_size()
		assert_true(menu.settings_panel.get_combined_minimum_size().y >= need.y, "%s: the panel is as tall as its content" % section)
		assert_true(need.x <= PauseMenu.MENU_SIZE.x, "%s: %d px fits the %d px menu" % [section, need.x, PauseMenu.MENU_SIZE.x])


func test_intel_shows_the_layout_the_boss_will_use() -> void:
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"renewal_engine"], 7, &"", 0, {"remove_boss_pointers": 1})
	s.state.flags["boss_pointer_removal"] = 1
	var data := ContentRegistry.get_content(&"renewal_engine") as EnemyData
	assert_eq(CombatResolver.phase_layout(s.state, data, PackedInt32Array([0, 15])).size(), 1, "Breach removes one reader from the 66% layout")


func test_a_flip_cannot_refresh_firmware_limits() -> void:
	var r := CombatFixture.resolver()
	var s := CombatSession.start(r, &"breaker", [&"triage_unit"], 5)
	s.state.player.wheel.slot_firmware_ids[0] = &"skimmer"
	s.state.player.wheel.slot_firmware_ids[2] = &"skimmer"
	var fw := ContentRegistry.get_content(&"skimmer") as FirmwareData
	var res := {"owner": s.state.player, "slice": r.lookup.get_content(s.state.player.wheel.slot_slice_ids[0]), "firmware": fw, "segment": null, "slice_index": 0}
	var listener: Dictionary = r._slice_listeners(s.state, res)[1]
	assert_false(listener.has("limit_key"), "one counter per Firmware id, whatever slot it sits in after a Flip")
	assert_eq(listener["limit_scale"], 2, "two copies, twice the charges")


func test_repair_shows_what_it_charges() -> void:
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var lookup := GridFixture.lookup()
	var c := CampaignRules.new_campaign(corp, _cfg, lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	var site: StringName = &"t1_a"
	var s := c.grid.site(site)
	s["status"] = GridState.SiteStatus.CLAIMED
	s["node_type"] = "firewall_relay"
	s["condition"] = GridState.Condition.DISABLED
	c.schematics = 500
	var price := CampaignRules.repair_cost(c, _cfg, lookup, site)
	assert_true(price > 0)
	CampaignRules.repair(c, _cfg, lookup, site)
	assert_eq(c.schematics, 500 - price)


func test_only_random_status_picks_are_marked_random() -> void:
	var fx := CombatFixture.resolver().fx
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"triage_unit"], 5)
	var events: Array[Dictionary] = []
	var dose := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.SELF, 0, RC.RingScope.OUTER, 1.0, RC.Status.CORRUPTED, RC.SlicePick.RANDOM_NON_MISS)
	fx.apply_effect(s.state, dose, {"owner": s.state.player, "target": s.state.player}, CombatFixture.rng(3), events)
	var fixed := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.SELF, 0, RC.RingScope.OUTER, 1.0, RC.Status.OVERCLOCKED, RC.SlicePick.UNDER_POINTER)
	fx.apply_effect(s.state, fixed, {"owner": s.state.player, "target": s.state.player, "pointer_index": 0}, CombatFixture.rng(3), events)
	var statuses := events.filter(func(e: Dictionary) -> bool: return e.get("type", "") == "status")
	assert_eq(statuses.size(), 2)
	assert_true(statuses[0].get("random", false), "DOSE-style pick is random")
	assert_false(statuses[1].get("random", false), "a pointer pick is not")


func test_ice_achievement_levels_come_from_the_config() -> void:
	var cfg: CampaignConfigData = _cfg.duplicate()
	cfg.achievement_ice_low = 2
	var p := ProfileState.new()
	var c := CampaignState.new()
	c.outcome = CampaignState.Outcome.WON
	c.ice_level = 2
	assert_true(Achievements.check(p, c, [], 20, cfg).has(&"ice_5"))
	assert_false(Achievements.check(p, c, [], 20, _cfg).has(&"ice_5"))
