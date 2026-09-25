extends GutTest
## Horizontal pass 2 fixes (GAP_ANALYSIS H2): raid names and warning keys per corporation,
## held-at-home threats deal no damage, the combat scene records met enemies, DISPATCH's
## boss line, ICE records and the start panel cap, Shatter, share codes after a death,
## Heat bands from the config, no Solace text in shared content.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func _campaign(corp_id: StringName) -> CampaignState:
	return CampaignRules.new_campaign(ContentRegistry.get_content(corp_id) as CorporationData, _cfg, _lookup, 3,
		ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())


func test_threshold_raids_announce_the_corporations_own_name() -> void:
	var c := _campaign(&"meridian")
	var events := HeatRules.add_heat(c, 26, _cfg, "test")
	CampaignRules.name_pending_raids(c, _lookup, events)
	var text := ""
	for e in events:
		if e.get("type", "") == "raid_pending":
			text = e["text"]
	assert_eq(text, "Raid incoming: Delivery Exception.")


func test_mid_run_raid_interludes_carry_the_queued_id_for_the_voice() -> void:
	var corp := ContentRegistry.get_content(&"meridian") as CorporationData
	var c := _campaign(&"meridian")
	HeatRules.add_heat(c, 26, _cfg, "test")
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"m1_a", 5, corp)
	s._maybe_raid_interlude()
	var queued := ""
	for e in s.last_events:
		if e.get("type", "") == "raid_interlude":
			queued = String(e.get("queued_raid_id", ""))
	assert_eq(queued, "raid_heat_25")
	assert_true(Dialogue.raid_warning(&"meridian", StringName(queued)).begins_with("MERIDIAN"), "the specific line plays, not raid:any")


func test_a_threat_held_at_home_does_no_damage_while_held() -> void:
	var grid := GridFixture.chain_grid([&"c1"])
	var c := GridFixture.campaign(grid)
	c.grid.home_built_in.append("ghost_lock")
	var raid := GridFixture.raid(&"probe", [&"collector"])
	var result := RaidResolver.resolve(c, grid, raid, _lookup, _cfg)
	var held_steps := []
	var damage_steps := []
	for e in result.events:
		if e.get("type", "") in ["ice_lock", "held"] and e.get("site", &"") == c.grid.home_site_id:
			held_steps.append(int(e["step"]))
		if e.get("type", "") == "home_damage" or String(e.get("text", "")).contains("reaches the HOME"):
			damage_steps.append(int(e["step"]))
	assert_false(held_steps.is_empty(), "held at the door")
	assert_false(damage_steps.is_empty())
	assert_true(damage_steps.min() >= held_steps.max(), "no home damage while the hold lasts (%s vs %s)" % [damage_steps, held_steps])


func test_the_combat_scene_records_met_enemies_for_the_codex() -> void:
	RunManager.save_slot = "gut_test_seen"
	RunManager.scene_switching_enabled = false
	RunManager.new_campaign(1)
	RunManager.profile.stats.erase("use_seen:triage_unit")
	var scene: Control = add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())
	scene.start_fight(&"triage_unit", 7)
	assert_true(RunManager.profile.stats.has("use_seen:triage_unit"))
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_dispatch_speaks_its_boss_line_when_a_boss_run_starts() -> void:
	RunManager.save_slot = "gut_test_boss_line"
	RunManager.scene_switching_enabled = false
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	c.exploits = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
	c.roster[0].rank = 3
	var grid_data := RunManager.corporation.city_grid
	for sd in grid_data.sites:
		if sd.links.has(grid_data.boss_site_id):
			c.grid.site(sd.id)["status"] = GridState.SiteStatus.CLEARED
			break
	var before := Dialogue.history.size()
	var s := RunManager.start_run(c.roster[0].id, RunManager.corporation.city_grid.boss_site_id)
	assert_not_null(s, "the boss run starts")
	var spoke := false
	for h in Dialogue.history.slice(before):
		spoke = spoke or int(h["speaker"]) == RC.Voice.DISPATCH
	assert_true(spoke, "DISPATCH briefs the boss")
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_ice_records_and_the_start_panel_cap() -> void:
	RunManager.save_slot = "gut_test_records"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.profile.best_ice_by_corp["solace"] = 6
	var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
	var text: String = hq.ice_records_text()
	assert_true(text.contains("Solace Biosystems 6"), text)
	assert_false(text.contains("REBEL_CELL"), "no spoiler while it is locked")
	hq.show_start()
	var spin := hq.find_child("IceSpin", true, false) as SpinBox
	assert_eq(int(spin.max_value), RunManager.ice_cap(&"solace"), "the cap follows the first Target")
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_shatter_breaches_and_strips() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"compliance_officer"], 4)
	s.state.hand[0] = &"shatter"
	s.state.ram = s.state.max_ram
	var e := s.state.get_combatant(&"enemy_0")
	var res_before := e.resistance
	var r := s.apply(CombatAction.play_card(0, &"enemy_0"))
	assert_true(r.ok(), r.error)
	e = s.state.get_combatant(&"enemy_0")
	assert_true(e.is_hub_breached())
	assert_true(e.resistance <= maxi(0, res_before - 1), "strip 1 (and the breached Hub drops its own resistance)")


func test_the_share_code_survives_the_first_operative() -> void:
	var c := _campaign(&"solace")
	c.start_class_id = &"ghost"
	c.roster[0].alive = false
	assert_eq(CampaignCode.of(c, c.start_class_id), "RC1-solace-0-3-home_standard-ghost")
	assert_eq(CampaignState.from_dict(c.to_dict()).start_class_id, &"ghost")


func test_heat_bands_come_from_the_config() -> void:
	assert_eq(_cfg.major_heat_levels(), [25, 50, 75])
	var c := _campaign(&"solace")
	c.heat = 60
	assert_eq(c.heat_majors_crossed(_cfg), 2)


func test_a_built_rebel_cell_keeps_its_unlock_gate() -> void:
	var template := ContentRegistry.get_content(&"rebel_cell") as CorporationData
	var built := RebelCellBuilder.build(template, RebelCellBuilder.snapshot(null, &"breaker"), _lookup)
	var lookup := GridFixture.lookup([built])
	assert_not_null(CampaignRules.unlock_for(lookup, built), "matched by id")
	assert_false(CampaignRules.corporation_available(ProfileState.new(), lookup, built), "still locked on a fresh profile")


func test_shared_content_never_names_a_corporation() -> void:
	for id in _lookup.ids_of_class(&"TerminalEventData"):
		var ev := _lookup.get_content(id) as TerminalEventData
		if ev.corporation_id != &"":
			continue
		for corp in ["Solace", "Meridian", "Halcyon", "Orbital"]:
			assert_false(ev.text.contains(corp), "%s mentions %s" % [id, corp])
	var barks := ContentRegistry.get_content(&"barks_breaker") as LineSetData
	for l in barks.lines:
		assert_false(l.text.contains("Solace"), l.text)
