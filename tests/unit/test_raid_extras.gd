extends GutTest
## Raid triggers and threat abilities beyond the M3 set (GDD 4.4, 7.1, 3.3): retaliation,
## story and node-built raids; Icebreakers open locked links, Lockdown Units freeze one;
## stationed operatives return from Disabled nodes; ICE progression on the profile.

var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _corp: CorporationData
var _breaker: ClassData


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"solace") as CorporationData
	_breaker = ContentRegistry.get_content(&"breaker") as ClassData


func _campaign() -> CampaignState:
	var c := CampaignRules.new_campaign(_corp, _cfg, _lookup, 2, _breaker, GridFixture.home_node())
	c.schematics = 200
	return c


func _run(site_id: StringName) -> RunState:
	var r := RunState.new()
	r.site_id = site_id
	return r


func _raids(c: CampaignState) -> Array:
	var out := []
	for p in c.pending_raids:
		out.append(p["raid_id"])
	return out


func test_exploits_and_heat_objectives_trigger_retaliation_from_the_cleared_site() -> void:
	var c := _campaign()
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	assert_eq(c.pending_raids.size(), 0, "a plain Site provokes nothing")
	var events := CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t2_intel"))
	assert_true(_raids(c).has("raid_retaliation"))
	var raid: Dictionary = c.pending_raids[c.pending_raids.size() - 1]
	assert_eq(int(raid["source"]), RC.RaidTriggerSource.RETALIATION)
	assert_eq(raid["site_id"], "t2_intel", "threats enter where you struck")
	assert_eq(CampaignRules.raid_entries(c, _corp, raid), [&"t2_intel"])
	c.pending_raids.clear()
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"scrub_records"))
	assert_eq(_raids(c), ["raid_retaliation"])


func test_a_story_beat_can_trigger_a_story_raid() -> void:
	var c := _campaign()
	c.story_path_id = &"sp_ghost_patient"
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_a"))
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_b"))
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t2_intel"))
	assert_false(_raids(c).has("raid_story"), "beat 1 is quiet")
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t2_breach"))
	assert_true(_raids(c).has("raid_story"), "Ghost Patient II triggers the story raid")


func test_icebreaker_opens_a_locked_link_that_stays_open() -> void:
	var c := _campaign()
	assert_false(c.grid.is_link_open(&"t1_a", &"t1_b"))
	var raid := _lookup.get_content(&"raid_retaliation") as RaidData
	var result := RaidResolver.resolve(c, _corp.city_grid, raid, _lookup, _cfg, [&"t1_a"])
	var altered := 0
	for e in result.events:
		if e.get("type", "") == "link_altered" and e.get("b") != &"":
			altered += 1
			assert_eq(e["a"], &"t1_a")
			assert_eq(e["b"], &"t1_b")
	assert_eq(altered, 1)
	assert_true(result.grid_after.is_link_open(&"t1_a", &"t1_b"))
	assert_false(c.grid.is_link_open(&"t1_a", &"t1_b"), "the projection touches nothing")
	RaidResolver.apply(c, result, raid, _cfg)
	assert_true(c.grid.is_link_open(&"t1_a", &"t1_b"), "the route stays open after the raid")
	assert_eq(CampaignRules.project_raid(c, _corp, _cfg, _lookup, {"raid_id": "raid_retaliation", "site_id": "t1_a"}).summary_hash(),
		RaidResolver.resolve(c, _corp.city_grid, raid, _lookup, _cfg, [&"t1_a"]).summary_hash(), "projection = playout")


func test_lockdown_unit_freezes_the_busiest_link_to_home_for_one_raid() -> void:
	var grid := GridFixture.chain_grid([&"c1"])
	var c := GridFixture.campaign(grid, {&"c1": &"firewall_relay"})
	GridFixture.deploy(c, &"c1", &"turret")
	var raid := GridFixture.raid(&"lockdown", [&"lockdown_unit"])
	var result := RaidResolver.resolve(c, grid, raid, _lookup, _cfg)
	var frozen := 0
	for e in result.events:
		if e.get("type", "") == "link_frozen":
			frozen += 1
			assert_eq(e["a"], &"home")
			assert_eq(e["b"], &"c1")
	assert_eq(frozen, 1)
	assert_true(result.grid_after.is_link_frozen(&"home", &"c1"))
	# With the only link to home frozen, the threat camps on c1 and never reaches home.
	assert_eq(result.threats_reached_home, 0)
	assert_eq(result.home_after, result.home_before)
	RaidResolver.apply(c, result, raid, _cfg)
	assert_eq(c.grid.frozen_links.size(), 0, "freezes last one raid")
	assert_eq(c.grid.neighbors(&"home", grid), [&"c1"], "the link is usable again")


func test_stationed_operative_returns_from_a_disabled_node() -> void:
	var grid := GridFixture.chain_grid([&"c1"])
	var c := GridFixture.campaign(grid, {&"c1": &"safehouse"})
	c.recruit(_breaker, "Vex")
	CampaignRules.station(c, _lookup, c.roster[0].id, &"c1")
	assert_eq(c.grid.stationed_on(&"c1"), c.roster[0].id)
	var raid := GridFixture.raid(&"heavy", [&"enforcer", &"enforcer", &"enforcer"])
	var result := RaidResolver.resolve(c, grid, raid, _lookup, _cfg)
	assert_true(result.disabled.has("c1") or result.seized.has("c1"), "the Safehouse falls")
	var recalled := false
	for e in result.events:
		if e.get("type", "") == "recalled":
			recalled = true
	var events := RaidResolver.apply(c, result, raid, _cfg)
	for e in events:
		if e.get("type", "") == "recalled":
			recalled = true
	assert_true(recalled, "the operative is reported back in the reserves")
	assert_eq(c.grid.stationed_on(&"c1"), &"")
	assert_true(c.roster[0].alive, "unharmed")


func test_profile_ice_cap_follows_wins() -> void:
	var p := ProfileState.new()
	assert_eq(p.ice_cap_for(&"solace", _cfg.new_corp_ice_offset), 3, "fresh profile: ICE 0-3")
	p.record_win(&"solace", 3)
	assert_eq(p.ice_cap_for(&"solace", _cfg.new_corp_ice_offset), 6, "a win at n unlocks n + 3")
	assert_eq(p.ice_cap_for(&"other", _cfg.new_corp_ice_offset), 3, "another corporation starts at global best - 5, never below 3")
	p.record_win(&"solace", 12)
	assert_eq(p.ice_cap_for(&"solace", _cfg.new_corp_ice_offset), 15)
	assert_eq(p.ice_cap_for(&"other", _cfg.new_corp_ice_offset), 7)
	p.record_win(&"solace", 19)
	assert_eq(p.ice_cap_for(&"solace", _cfg.new_corp_ice_offset), 20, "capped at 20")
	var again := ProfileState.from_dict(p.to_dict())
	assert_eq(again.ice_cap_for(&"solace", _cfg.new_corp_ice_offset), 20)
