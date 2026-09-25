extends GutTest
## Horizontal pass 3 fixes (GAP_ANALYSIS H3): lost-raid Heat names the next raid for the
## corporation, a built REBEL_CELL's elite pool is its own Mirrors only, Mirror and final
## final numbers come from the config, the boss launch message, pad focus and inspect.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func test_a_lost_raid_names_the_next_raid_for_the_corporation() -> void:
	var corp := ContentRegistry.get_content(&"meridian") as CorporationData
	var c := CampaignRules.new_campaign(corp, _cfg, _lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	HeatRules.add_heat(c, 26, _cfg, "test")
	c.heat = 50 - _cfg.lost_raid_heat
	var events := CampaignRules.fight_raid(c, corp, _cfg, _lookup, c.pending_raids[0])
	var names := []
	for e in events:
		if e.get("type", "") == "raid_pending":
			names.append(e["text"])
	assert_true(names.has("Raid incoming: Route Audit."), "%s" % [names])


func test_a_built_rebel_cells_elites_are_its_own_mirrors_only() -> void:
	var template := ContentRegistry.get_content(&"rebel_cell") as CorporationData
	var lookup := GridFixture.lookup()
	var first := RebelCellBuilder.build(template, {"classes": ["breaker"], "daemons": [], "nodes": ["relay"], "assets": ["turret"]}, lookup)
	lookup.add(first)
	var second := RebelCellBuilder.build(template, {"classes": ["ghost"], "daemons": [], "nodes": ["relay"], "assets": ["turret"]}, lookup)
	lookup.add(second)
	var resolver := CombatResolver.new(_cfg, lookup)
	var c := CampaignRules.new_campaign(second, _cfg, lookup, 3, ContentRegistry.get_content(&"ghost") as ClassData, GridFixture.home_node())
	var s := NetrunSession.start(resolver, c, c.roster[0].id, 1, &"r1_a", 5, second)
	assert_eq(s.pools()["elites"], [&"rc_mirror_ghost"], "the earlier Mirror Breaker does not leak in")


func test_mirror_and_final_final_numbers_come_from_the_config() -> void:
	var cfg: CampaignConfigData = _cfg.duplicate()
	cfg.mirror_output_factor = 2.0
	cfg.mirror_resistance = 3
	cfg.mirror_threat_damage_bonus = 5
	var template := ContentRegistry.get_content(&"rebel_cell") as CorporationData
	var corp := RebelCellBuilder.build(template, {"classes": ["breaker"], "daemons": [], "nodes": ["relay"], "assets": ["turret"]}, _lookup, cfg)
	var mirror := corp.elites[0]
	assert_eq(mirror.wheel.passive_resistance, 3)
	assert_eq(mirror.wheel.slots[1].slice.base_output, 12, "Atk 6 at 2x -> Atk 12")
	var turret := ContentRegistry.get_content(&"turret") as DefenseAssetData
	assert_eq(corp.raids[0].waves[0].threats[0].damage, turret.damage + 5)
	RebelCellBuilder.build(template, {"classes": ["breaker"], "daemons": [], "nodes": ["relay"], "assets": ["turret"]}, _lookup, _cfg)  # restore defaults
	var p := ProfileState.new()
	var corps := [&"solace", &"meridian"]
	for id in corps + [&"rebel_cell"]:
		p.best_ice_by_corp[String(id)] = 5
	assert_true(Achievements.check(p, null, corps, 5).has(&"final_final"))
	assert_false(Achievements.check(p, null, corps, 6).has(&"final_final"))


func test_the_boss_needs_a_path_once_the_exploits_are_in() -> void:
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var cls := ContentRegistry.get_content(&"breaker") as ClassData
	var c := CampaignRules.new_campaign(corp, _cfg, _lookup, 3, cls, GridFixture.home_node())
	c.roster[0].rank = 3
	var boss := CampaignRules.site_data(corp, corp.city_grid.boss_site_id)
	assert_true(CampaignRules.launch_error(c, corp, _cfg, c.roster[0], cls, boss).contains("Exploits"))
	c.exploits = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
	assert_true(CampaignRules.launch_error(c, corp, _cfg, c.roster[0], cls, boss).contains("cleared or claimed Site next to it"))


func test_every_combat_action_is_reachable_from_a_pad() -> void:
	var actions := [&"nudge_left", &"nudge_right", &"cycle_target", &"end_turn", &"rewind", &"inspect", &"respin", &"open_settings"]
	for action in actions:
		var pad := false
		for ev in InputMap.action_get_events(action):
			pad = pad or ev is InputEventJoypadButton
		assert_true(pad, "%s has a pad button" % action)
	for ui in [&"ui_accept", &"ui_cancel", &"ui_up", &"ui_down", &"ui_left", &"ui_right"]:
		var ok := false
		for ev in InputMap.action_get_events(ui):
			ok = ok or ev is InputEventJoypadButton
		assert_true(ok, "%s navigates with the pad (cards and the combat pickers are reached by focus)" % ui)


func test_space_ends_the_turn_instead_of_pressing_the_focused_button() -> void:
	for ev in InputMap.action_get_events(&"ui_accept"):
		if ev is InputEventKey:
			assert_ne((ev as InputEventKey).keycode, KEY_SPACE)
			assert_ne((ev as InputEventKey).physical_keycode, KEY_SPACE)


func test_panels_and_the_combat_hand_take_focus() -> void:
	RunManager.save_slot = "gut_test_focus"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
	hq.show_start()
	await get_tree().process_frame
	await get_tree().process_frame
	var owner := get_viewport().gui_get_focus_owner()
	assert_not_null(owner, "the start panel focuses a button")
	RunManager.new_campaign(1)
	var scene: Control = add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())
	scene.start_fight(&"triage_unit", 7)
	await get_tree().process_frame
	await get_tree().process_frame
	owner = get_viewport().gui_get_focus_owner()
	assert_not_null(owner)
	assert_true(owner is ZineCard or owner is BaseButton, "a card or button has focus: %s" % owner)
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
