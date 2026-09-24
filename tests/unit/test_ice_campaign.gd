extends GutTest
## Campaign-side ICE modifiers (GDD 11.9): Heat gain/sink scaling, the pulled-down Purge,
## fewer Heat-objective Sites, death and Exploit Heat, Cycle prices, repair costs, Seized
## raid strength and the extra raid wave. Each reads the ladder through
## CampaignState.rule_modifier at the ICE level that introduces it.

var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _corp: CorporationData
var _breaker: ClassData
var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = _resolver.config
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"solace") as CorporationData
	_breaker = ContentRegistry.get_content(&"breaker") as ClassData


func _campaign(ice: int) -> CampaignState:
	var c := CampaignRules.new_campaign(_corp, _cfg, _lookup, 5, _breaker, GridFixture.home_node(), ice)
	c.schematics = 200
	return c


func _run(site_id: StringName, kind: String = "netrun") -> RunState:
	var r := RunState.new()
	r.site_id = site_id
	r.kind = kind
	return r


func test_heat_gain_and_sink_scale_with_ice_1_and_6() -> void:
	var c := _campaign(1)
	HeatRules.add_heat(c, 20, _cfg, "test")
	assert_eq(c.heat, 22, "ICE 1: +10% gain")
	var c6 := _campaign(6)
	c6.heat = 50
	c6.thresholds_fired = [10, 20, 25, 30, 40, 50]
	HeatRules.add_heat(c6, -20, _cfg, "sink")
	assert_eq(c6.heat, 33, "ICE 6: sinks -15% (-17)")
	HeatRules.add_heat(c6, -1, _cfg, "tiny sink")
	assert_eq(c6.heat, 32, "a sink never rounds to nothing")


func test_ice_17_pulls_the_purge_down_to_90() -> void:
	var c := _campaign(17)
	HeatRules.add_heat(c, 90, _cfg, "test")
	assert_true(c.thresholds_fired.has(100), "the Purge (100) fired at 90")
	assert_eq(c.pending_raids[c.pending_raids.size() - 1]["raid_id"], "raid_purge")
	var c0 := _campaign(0)
	HeatRules.add_heat(c0, 90, _cfg, "test")
	assert_false(c0.thresholds_fired.has(100))


func test_ice_2_switches_off_a_heat_objective_site() -> void:
	var c := _campaign(2)
	assert_eq(c.disabled_objectives, [&"scrub_records"])
	var scrub := CampaignRules.site_data(_corp, &"scrub_records")
	assert_eq(CampaignRules.site_objective(c, scrub), RC.SiteObjective.NONE)
	c.heat = 30
	c.thresholds_fired = [10, 20, 25, 30]
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"scrub_records"))
	assert_eq(c.heat, 30, "no Heat reduction: the objective is off")
	assert_eq(_campaign(0).disabled_objectives.size(), 0)
	var again := CampaignState.from_dict(c.to_dict())
	assert_eq(again.disabled_objectives, [&"scrub_records"], "survives save/load")


func test_ice_8_adds_5_heat_to_deaths_and_ice_16_adds_5_to_exploits() -> void:
	var c := _campaign(8)
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 2, &"t1_a", 3)
	s.enter_node(s.available_nodes()[0])
	s.combat.state.player.hp = 1
	CombatFixture.land(s.combat.state.player, 5)
	var e := s.combat.state.get_combatant(&"enemy_0")
	for i in e.wheel.slot_slice_ids.size():
		if (_lookup.get_content(e.wheel.slot_slice_ids[i]) as SliceData).slice_type == RC.SliceType.ATTACK:
			CombatFixture.land(e, i)
			break
	var guard := 0
	while s.in_combat() and guard < 20:
		guard += 1
		s.combat.state.player.hp = 1
		CombatFixture.land(s.combat.state.player, 5)
		s.combat_action(CombatAction.end_turn())
	assert_eq(s.run.outcome, RunState.Outcome.DIED)
	assert_eq(c.heat, roundi((10 + 2 + 5) * 1.1), "death: (10 + tier + ICE 8) x ICE 1 gain")
	var c16 := _campaign(16)
	CampaignRules.on_run_completed(c16, _corp, _cfg, _run(&"t1_a"))
	var before := c16.heat
	CampaignRules.on_run_completed(c16, _corp, _cfg, _run(&"t2_intel"))
	assert_eq(c16.heat - before, roundi(15 * 1.1), "Exploit: (10 + ICE 16) x ICE 1 gain")


func test_ice_4_raises_every_modem_price_by_10_percent() -> void:
	var c := _campaign(4)
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"t1_a", 3)
	assert_eq(s.card_removal_price(), 55)
	assert_eq(s.slice_overwrite_price(5), 165, "Miss slot 150 x 1.1")
	assert_eq(s.slice_overwrite_price(0), 110)
	s._open_shop()
	for p in s.run.shop["card_prices"]:
		assert_true(int(p) >= 55 and int(p) <= 83, "card price %d scaled from 50-75" % int(p))


func test_ice_13_makes_repairs_cost_25_percent_more() -> void:
	var c := _campaign(13)
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	CampaignRules.claim(c, _corp, _cfg, _lookup, &"t1_a", &"firewall_relay")
	var s := c.grid.site(&"t1_a")
	s["condition"] = GridState.Condition.DISABLED
	s["integrity"] = 0
	var schematics := c.schematics
	CampaignRules.repair(c, _cfg, _lookup, &"t1_a")
	assert_eq(schematics - c.schematics, 19, "15 x 1.25 = 18.75 -> 19")


func test_ice_14_strengthens_raids_from_seized_sites_and_ice_19_adds_a_wave() -> void:
	var c := _campaign(14)
	c.grid.site(&"t1_a")["status"] = GridState.SiteStatus.SEIZED
	var pending := {"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "site_id": "t1_a"}
	assert_eq(CampaignRules.raid_strength_pct(c, _cfg, pending, _corp), 25.0 + 15.0, "ICE 5 +15 and Seized +25")
	var plain := {"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "site_id": "t1_b"}
	assert_eq(CampaignRules.raid_strength_pct(c, _cfg, plain, _corp), 15.0)
	var c19 := _campaign(19)
	assert_eq(CampaignRules.raid_extra_waves(c19, _cfg), 1)
	var raid := _lookup.get_content(&"raid_heat_25") as RaidData
	var one := RaidResolver.resolve(c19, _corp.city_grid, raid, _lookup, _cfg, [&"t1_a"], 0.0, 0)
	var two := RaidResolver.resolve(c19, _corp.city_grid, raid, _lookup, _cfg, [&"t1_a"], 0.0, 1)
	var entered_one := 0
	var entered_two := 0
	for e in one.events:
		if e.get("type", "") == "threat_enters":
			entered_one += 1
	for e in two.events:
		if e.get("type", "") == "threat_enters":
			entered_two += 1
	assert_eq(entered_two, entered_one * 2, "the last wave comes again")
	assert_eq(CampaignRules.project_raid(c19, _corp, _cfg, _lookup, plain).steps_run, two.steps_run, "projection uses the extra wave")
