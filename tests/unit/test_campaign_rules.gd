extends GutTest
## Campaign rules over the real Solace content (GDD 3, 4.1, 5.3, 7.3, 11.4, 11.7).

var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _corp: CorporationData
var _breaker: ClassData


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"solace") as CorporationData
	_breaker = ContentRegistry.get_content(&"breaker") as ClassData


## A fresh campaign; `rich` tops up Schematics so purchases are not the thing under test.
func _campaign(seed: int = 1, rich: bool = true) -> CampaignState:
	var c := CampaignRules.new_campaign(_corp, _cfg, _lookup, seed, _breaker, GridFixture.home_node())
	if rich:
		c.schematics = 100
	return c


func _ids(sites: Array[SiteData]) -> Array[StringName]:
	var out: Array[StringName] = []
	for s in sites:
		out.append(s.id)
	return out


func _run(site_id: StringName, kind: String = "netrun") -> RunState:
	var r := RunState.new()
	r.site_id = site_id
	r.kind = kind
	return r


func test_solace_content_validates_and_has_the_a6_grid() -> void:
	assert_eq(_corp.validate(_cfg.min_exploits_for_breach).size(), 0, str(_corp.validate()))
	assert_eq(_corp.city_grid.sites.size(), 32, "GDD 4.1: 30-40 Sites")
	assert_eq(_corp.city_grid.size_warnings().size(), 0)
	assert_eq(_corp.story_paths.size(), 5)
	assert_eq(_corp.exploits.size(), 3)
	assert_eq(_corp.raids.size(), 8, "threshold x4, claim, retaliation, story, node-built")
	assert_true(_corp.final_boss.is_boss)


func test_new_campaign_opens_with_two_rookies_home_claimed_and_a_story_path() -> void:
	var c := _campaign(1, false)
	assert_eq(c.roster.size(), _cfg.starting_rookies)
	assert_eq(c.schematics, _cfg.starting_schematics)
	assert_true(c.grid.is_claimed(&"home"))
	assert_eq(c.grid.home_integrity, 50)
	assert_true(c.grid.is_corporate(&"t1_a"))
	assert_ne(c.story_path_id, &"")
	assert_eq(_campaign(1, false).story_path_id, _campaign(1, false).story_path_id, "same seed, same path")


func test_launchable_sites_follow_the_tier_chains_and_the_breach_gate() -> void:
	var c := _campaign()
	var opening := _ids(CampaignRules.launchable_sites(c, _corp, _cfg))
	assert_eq(opening.size(), 10, "every T1 Site touches home")
	for id in [&"t1_a", &"t1_b", &"t1_c"]:
		assert_true(opening.has(id))
	assert_false(opening.has(&"t2_intel"))
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	assert_true(c.grid.is_cleared(&"t1_a"))
	var after := _ids(CampaignRules.launchable_sites(c, _corp, _cfg))
	assert_true(after.has(&"scrub_records") and after.has(&"t2_intel"), "t1_a opened its chain and the Heat objective")
	assert_false(after.has(&"t1_a"), "cleared Sites are used up")
	for id in [&"t1_b", &"t1_c", &"t2_intel", &"t2_breach", &"t2_virus", &"t3_core"]:
		CampaignRules.on_run_completed(c, _corp, _cfg, _run(id))
	assert_eq(c.exploits.size(), 3)
	assert_true(_ids(CampaignRules.launchable_sites(c, _corp, _cfg)).has(&"renewal_engine_site"), "3 Exploits open the breach")
	var c2 := _campaign()
	for id in [&"t1_a", &"t2_intel", &"t3_core"]:
		CampaignRules.on_run_completed(c2, _corp, _cfg, _run(id))
	assert_false(_ids(CampaignRules.launchable_sites(c2, _corp, _cfg)).has(&"renewal_engine_site"), "one Exploit is not enough")


func test_rank_gates_netrun_tiers() -> void:
	var c := _campaign()
	var op := c.roster[0]
	assert_eq(CampaignRules.max_tier_for(op, _breaker), 1)
	op.rank = 1
	assert_eq(CampaignRules.max_tier_for(op, _breaker), 2)
	op.rank = 3
	assert_eq(CampaignRules.max_tier_for(op, _breaker), 4)
	op.rank = 0
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	var t2 := CampaignRules.site_data(_corp, &"t2_intel")
	assert_string_contains(CampaignRules.launch_error(c, _corp, _cfg, op, _breaker, t2), "Rank")
	op.rank = 1
	assert_eq(CampaignRules.launch_error(c, _corp, _cfg, op, _breaker, t2), "")
	var t1 := CampaignRules.site_data(_corp, &"t1_b")
	assert_eq(CampaignRules.launch_error(c, _corp, _cfg, op, _breaker, t1), "")
	var boss := CampaignRules.site_data(_corp, &"renewal_engine_site")
	assert_string_contains(CampaignRules.launch_error(c, _corp, _cfg, op, _breaker, boss), "Exploits")


func test_exploit_site_adds_heat_reveals_a_beat_and_intel_opens_links() -> void:
	var c := _campaign()
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	var heat := c.heat
	var events := CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t2_intel"))
	assert_eq(c.exploits, [RC.ExploitType.INTEL])
	assert_eq(c.heat, heat + _cfg.exploit_heat, "+10 Heat")
	assert_eq(c.story_beats_revealed, 1)
	var beats := CampaignRules.revealed_beats(c, _corp)
	assert_eq(beats.size(), 1)
	var beat_events := 0
	var links := 0
	for e in events:
		if e.get("type", "") == "story_beat":
			beat_events += 1
		if e.get("type", "") == "link_opened":
			links += 1
	assert_eq(beat_events, 1)
	assert_true(links >= 2, "Intel opened every locked link (%d)" % links)
	assert_true(c.grid.is_link_open(&"t1_a", &"t1_b"))
	assert_true(c.grid.neighbors(&"t1_a", _corp.city_grid).has(&"t1_b"))


func test_heat_objective_site_reduces_heat() -> void:
	var c := _campaign()
	c.heat = 20
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"scrub_records"))
	assert_eq(c.heat, 15, "Scrub Records -5")


func test_claiming_needs_a_cleared_site_a_relay_path_and_schematics() -> void:
	var c := _campaign()
	assert_string_contains(CampaignRules.claim_error(c, _corp, _cfg, _lookup, &"t1_a", &"relay"), "not a cleared")
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t2_intel"))
	assert_string_contains(CampaignRules.claim_error(c, _corp, _cfg, _lookup, &"t2_intel", &"safehouse"), "beyond your Relays", "t2 is not next to home")
	assert_eq(CampaignRules.claim_error(c, _corp, _cfg, _lookup, &"t1_a", &"safehouse"), "")
	var schematics := c.schematics
	var events := CampaignRules.claim(c, _corp, _cfg, _lookup, &"t1_a", &"safehouse")
	assert_true(c.grid.is_claimed(&"t1_a"))
	assert_eq(c.grid.node_type_of(&"t1_a"), &"safehouse")
	assert_eq(c.schematics, schematics - 20)
	assert_string_contains(CampaignRules.claim_error(c, _corp, _cfg, _lookup, &"t2_intel", &"relay"), "beyond your Relays", "a Safehouse does not extend reach")
	assert_true(c.schematics >= 20, "still affordable, so the refusal is about reach")
	var provoked := false
	for e in events:
		if e.get("type", "") == "raid_pending":
			provoked = true
	assert_true(provoked, "t1_a touches corporate Sites: a claim raid is queued")
	assert_eq(c.pending_raids[c.pending_raids.size() - 1]["source"], RC.RaidTriggerSource.TERRITORY_CLAIM)
	c.grid.site(&"t1_a")["node_type"] = "relay"
	assert_eq(CampaignRules.claim_error(c, _corp, _cfg, _lookup, &"t2_intel", &"relay"), "", "a Relay extends reach")
	c.schematics = 5
	assert_string_contains(CampaignRules.claim_error(c, _corp, _cfg, _lookup, &"t2_intel", &"relay"), "Schematics")


func test_repair_costs_half_the_install_and_restores_the_node() -> void:
	var c := _campaign()
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	CampaignRules.claim(c, _corp, _cfg, _lookup, &"t1_a", &"firewall_relay")
	var s := c.grid.site(&"t1_a")
	s["condition"] = GridState.Condition.DISABLED
	s["integrity"] = 0
	var schematics := c.schematics
	CampaignRules.repair(c, _cfg, _lookup, &"t1_a")
	assert_eq(c.schematics, schematics - 15, "50% of 30")
	assert_true(c.grid.is_active_node(&"t1_a"))
	assert_eq(int(s["integrity"]), 30)
	var events := CampaignRules.repair(c, _cfg, _lookup, &"t1_a")
	assert_eq(events[0]["type"], "refused", "nothing to repair")


func test_recruit_station_and_heat_purchase() -> void:
	var c := _campaign()
	var schematics := c.schematics
	CampaignRules.recruit(c, _cfg, _breaker)
	assert_eq(c.roster.size(), 3)
	assert_eq(c.schematics, schematics - _cfg.rookie_cost)
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	CampaignRules.claim(c, _corp, _cfg, _lookup, &"t1_a", &"safehouse")
	var events := CampaignRules.station(c, _lookup, c.roster[2].id, &"t1_a")
	assert_eq(events[0]["type"], "stationed")
	assert_eq(CampaignRules.stationed_site(c, c.roster[2].id), &"t1_a")
	assert_eq(CampaignRules.station(c, _lookup, c.roster[0].id, &"t1_a")[0]["type"], "refused", "one slot")
	c.heat = 30
	c.schematics = 100
	assert_eq(CampaignRules.heat_purchase_price(c, _cfg), 25)
	CampaignRules.buy_heat_reduction(c, _cfg)
	assert_eq(c.heat, 25)
	assert_eq(c.schematics, 75)
	assert_eq(CampaignRules.heat_purchase_price(c, _cfg), 35, "+10 per purchase")


func test_deployed_assets_persist_can_be_repositioned_and_the_armory_is_capped() -> void:
	var c := _campaign()
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	CampaignRules.claim(c, _corp, _cfg, _lookup, &"t1_a", &"firewall_relay")
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	assert_eq(CampaignRules.deploy_asset(c, _cfg, _lookup, 0, &"t1_a")[0]["type"], "deployed")
	assert_eq(c.armory, [&"ice_lock", &"decoy"])
	assert_eq(c.grid.assets_on(&"t1_a"), [&"turret"])
	CampaignRules.deploy_asset(c, _cfg, _lookup, 0, &"t1_a")
	assert_eq(CampaignRules.deploy_asset(c, _cfg, _lookup, 0, &"t1_a")[0]["type"], "refused", "two slots on a Firewall Relay")
	# Persist through a save and a raid, then reposition.
	var reloaded := CampaignState.from_dict(JSON.parse_string(JSON.stringify(c.to_dict())))
	assert_eq(reloaded.grid.assets_on(&"t1_a"), [&"turret", &"ice_lock"])
	var pending := {"raid_id": "raid_claim", "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "t2_intel"}
	CampaignRules.fight_raid(c, _corp, _cfg, _lookup, pending)
	assert_eq(c.grid.assets_on(&"t1_a"), [&"turret", &"ice_lock"], "deployed assets persist after the raid")
	assert_eq(CampaignRules.move_asset(c, _cfg, _lookup, &"t1_a", 0, &"home")[0]["type"], "moved")
	assert_eq(c.grid.assets_on(&"home"), [&"turret"])
	assert_eq(CampaignRules.move_asset(c, _cfg, _lookup, &"t1_a", 0, &"")[0]["type"], "withdrawn")
	assert_eq(c.armory, [&"decoy", &"ice_lock"])
	c.armory = [&"turret", &"turret", &"turret", &"turret", &"turret", &"turret"]
	assert_eq(CampaignRules.move_asset(c, _cfg, _lookup, &"home", 0, &"")[0]["type"], "refused", "Armory cap 6")


func test_claim_raid_seizes_or_holds_and_updates_counters() -> void:
	var c := _campaign()
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	CampaignRules.claim(c, _corp, _cfg, _lookup, &"t1_a", &"relay")
	var pending := CampaignRules.pending_raid(c)
	assert_eq(pending["raid_id"], "raid_claim")
	var projection := CampaignRules.project_raid(c, _corp, _cfg, _lookup, pending)
	var events := CampaignRules.fight_raid(c, _corp, _cfg, _lookup, pending)
	assert_eq(c.pending_raids.size(), 0)
	assert_eq(c.last_raid["home_after"], projection.home_after, "projection matched the playout")
	assert_eq(c.raids_won + c.raids_lost, 1)


func test_boss_win_and_home_loss_end_the_campaign() -> void:
	var c := _campaign()
	var events := CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"renewal_engine_site", "boss"))
	assert_eq(c.outcome, CampaignState.Outcome.WON)
	assert_eq(events[0]["type"], "campaign_won")
	assert_eq(events[1]["type"], "story_beat", "finale")
	var c2 := _campaign()
	var grid := GridFixture.chain_grid([])
	var raid := GridFixture.raid(&"kill", [&"enforcer", &"enforcer", &"enforcer", &"enforcer", &"enforcer", &"enforcer"])
	c2.grid = GridState.from_grid(grid, GridFixture.home_node())
	var result := RaidResolver.resolve(c2, grid, raid, _lookup, _cfg, [&"entry"])
	RaidResolver.apply(c2, result, raid, _cfg)
	assert_eq(c2.outcome, CampaignState.Outcome.LOST)


func test_boss_overrides_follow_the_exploits_held() -> void:
	var c := _campaign()
	assert_eq(CampaignRules.boss_overrides(c, _corp), {"remove_boss_pointers": 0, "boss_corrupt_slices": 0, "reveal_phases": false})
	c.exploits = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
	var o := CampaignRules.boss_overrides(c, _corp)
	assert_eq(o["remove_boss_pointers"], 1)
	assert_eq(o["boss_corrupt_slices"], 2)
	assert_true(o["reveal_phases"])


func test_campaign_save_load_round_trip_is_exact() -> void:
	var c := _campaign(7)
	c.heat = 33
	HeatRules.add_heat(c, 5, _cfg, "t")
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t2_intel"))
	CampaignRules.claim(c, _corp, _cfg, _lookup, &"t1_a", &"firewall_relay")
	c.armory = [&"turret", &"decoy"]
	CampaignRules.deploy_asset(c, _cfg, _lookup, 0, &"t1_a")
	CampaignRules.station(c, _lookup, c.roster[1].id, &"home")
	c.roster[0].rank = 2
	c.roster[0].daemon_ids.append(&"scrubber")
	var json := JSON.stringify(c.to_dict())
	var loaded := CampaignState.from_dict(JSON.parse_string(json))
	assert_eq(loaded.state_hash(), c.state_hash(), "hash identical")
	assert_eq(JSON.stringify(loaded.to_dict()), json, "byte-identical serialisation")
	assert_eq(loaded.grid.assets_on(&"t1_a"), [&"turret"])
	assert_eq(loaded.pending_raids.size(), c.pending_raids.size())
	assert_eq(loaded.grid.opened_links, c.grid.opened_links)
	assert_eq(loaded.exploits, c.exploits)
