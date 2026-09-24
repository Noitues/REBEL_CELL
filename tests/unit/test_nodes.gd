extends GutTest
## Remote node types (GDD 3.2, 11.4, 3.4): Compiler Rack, Vault Terminal and Proxy Relay
## with their passives and adjacency bonuses, node upgrades, Profile unlock gating and
## purchase, home-server variants, and HQ netrun boosts.

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


func _campaign(home_variant: HomeServerVariantData = null) -> CampaignState:
	var home := home_variant.core if home_variant != null else GridFixture.home_node()
	var c := CampaignRules.new_campaign(_corp, _cfg, _lookup, 3, _breaker, home, 0, home_variant)
	c.schematics = 300
	return c


func _run(site_id: StringName) -> RunState:
	var r := RunState.new()
	r.site_id = site_id
	return r


func _clear_and_claim(c: CampaignState, site_id: StringName, node: StringName) -> void:
	c.grid.site(site_id)["status"] = GridState.SiteStatus.CLEARED
	var events := CampaignRules.claim(c, _corp, _cfg, _lookup, site_id, node)
	assert_eq(events[0]["type"], "claimed", str(events))
	c.pending_raids.clear()  # claim raids are tested elsewhere


func test_the_seven_node_types_exist_and_the_new_ones_are_profile_unlocks() -> void:
	var expected := {&"relay": RC.NetworkNodeType.RELAY, &"firewall_relay": RC.NetworkNodeType.FIREWALL_RELAY,
		&"safehouse": RC.NetworkNodeType.SAFEHOUSE, &"compiler_rack": RC.NetworkNodeType.COMPILER_RACK,
		&"vault_terminal": RC.NetworkNodeType.VAULT_TERMINAL, &"proxy_relay": RC.NetworkNodeType.PROXY_RELAY,
		&"home_server": RC.NetworkNodeType.HOME_SERVER}
	for id in expected:
		var node := _lookup.get_content(id) as NetworkNodeData
		assert_not_null(node, String(id))
		assert_eq(node.node_type, expected[id], String(id))
	for id in [&"compiler_rack", &"vault_terminal", &"proxy_relay"]:
		var node := _lookup.get_content(id) as NetworkNodeData
		assert_true(node.profile_unlock_required)
		assert_not_null(CampaignRules.unlock_for(_lookup, node), "%s has an unlock" % id)
	assert_null(CampaignRules.unlock_for(_lookup, _lookup.get_content(&"relay")))


func test_locked_node_types_need_the_profile_unlock() -> void:
	var c := _campaign()
	var profile := ProfileState.new()
	c.grid.site(&"t1_a")["status"] = GridState.SiteStatus.CLEARED
	assert_string_contains(CampaignRules.claim_error(c, _corp, _cfg, _lookup, &"t1_a", &"vault_terminal", profile), "locked")
	assert_eq(CampaignRules.claim_error(c, _corp, _cfg, _lookup, &"t1_a", &"vault_terminal"), "", "no profile = no gating (tests)")
	var events := CampaignRules.purchase_unlock(c, profile, _lookup, &"unlock_vault_terminal")
	assert_eq(events[0]["type"], "unlocked", str(events))
	assert_eq(c.schematics, 270)
	assert_true(profile.has_unlock(&"unlock_vault_terminal"))
	assert_eq(CampaignRules.purchase_unlock(c, profile, _lookup, &"unlock_vault_terminal")[0]["type"], "refused", "already unlocked")
	assert_eq(CampaignRules.claim_error(c, _corp, _cfg, _lookup, &"t1_a", &"vault_terminal", profile), "")
	c.schematics = 5
	assert_string_contains(CampaignRules.purchase_unlock(c, profile, _lookup, &"unlock_proxy_relay")[0]["text"], "Schematics")


func test_vault_and_proxy_passives_fire_on_run_completion_with_adjacency() -> void:
	var c := _campaign()
	c.heat = 12
	c.thresholds_fired = [10]
	_clear_and_claim(c, &"t1_a", &"vault_terminal")
	_clear_and_claim(c, &"t1_b", &"proxy_relay")
	var schematics := c.schematics
	var events := CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_c"), _lookup)
	assert_eq(c.schematics - schematics, 3, "Vault +3")
	assert_eq(c.heat, 11, "Proxy -1")
	var passives := 0
	for e in events:
		if e.get("type", "") == "node_passive":
			passives += 1
	assert_eq(passives, 2)
	# A Firewall Relay next to the Vault (the Intel link t1_a - t1_b, opened): +2 more.
	c.grid.open_link(&"t1_a", &"t1_b")
	c.grid.site(&"t1_b")["status"] = GridState.SiteStatus.CLEARED
	_clear_and_claim(c, &"t1_b", &"firewall_relay")
	schematics = c.schematics
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t3_core"), _lookup)
	assert_eq(c.schematics - schematics, 5, "Vault +3, hardened +2")
	# Disabled nodes give nothing.
	c.grid.site(&"t1_a")["condition"] = GridState.Condition.DISABLED
	schematics = c.schematics
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t1_c"), _lookup)
	assert_eq(c.schematics - schematics, 0)


func test_vault_terminal_build_provokes_the_node_built_raid_and_raids_prioritise_it() -> void:
	var c := _campaign()
	c.grid.site(&"t1_a")["status"] = GridState.SiteStatus.CLEARED
	var events := CampaignRules.claim(c, _corp, _cfg, _lookup, &"t1_a", &"vault_terminal")
	assert_eq(events[events.size() - 1]["type"], "raid_pending")
	assert_eq(c.pending_raids[0]["raid_id"], "raid_node_built")
	assert_eq(int(c.pending_raids[0]["source"]), RC.RaidTriggerSource.NODE_BUILT)
	assert_eq((_lookup.get_content(&"vault_terminal") as NetworkNodeData).raid_priority, 2)


func test_compiler_rack_gives_a_bonus_card_offer_at_run_start() -> void:
	var c := _campaign()
	_clear_and_claim(c, &"t1_a", &"compiler_rack")
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 2, &"t2_intel", 7, _corp)
	assert_eq(s.run.phase, RunState.Phase.REWARD, "bonus offer first")
	assert_eq(s.current_reward()["kind"], "card")
	assert_eq(s.current_reward()["options"].size(), _cfg.card_reward_choices)
	s.choose_reward(0)
	assert_eq(s.run.phase, RunState.Phase.MAP)
	assert_eq(s.run.operative.deck.size(), _breaker.starting_deck.size() + 1)
	var elsewhere := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"t1_c", 7, _corp)
	assert_eq(elsewhere.run.phase, RunState.Phase.MAP, "t1_c is not next to the Rack")


func test_node_upgrades_cost_30_then_60_and_add_integrity_and_slots() -> void:
	var c := _campaign()
	_clear_and_claim(c, &"t1_a", &"firewall_relay")
	assert_eq(CampaignRules.upgrade_cost(c, _cfg, &"t1_a"), 30)
	assert_eq(CampaignRules.asset_slots(c, _lookup, &"t1_a", _cfg), 2)
	var schematics := c.schematics
	var events := CampaignRules.upgrade_node(c, _cfg, _lookup, &"t1_a")
	assert_eq(events[0]["type"], "upgraded", str(events))
	assert_eq(c.schematics, schematics - 30)
	assert_eq(int(c.grid.site(&"t1_a")["max_integrity"]), 45, "30 + 50%")
	assert_eq(int(c.grid.site(&"t1_a")["integrity"]), 45)
	assert_eq(CampaignRules.asset_slots(c, _lookup, &"t1_a", _cfg), 3)
	assert_eq(CampaignRules.upgrade_cost(c, _cfg, &"t1_a"), 60)
	CampaignRules.upgrade_node(c, _cfg, _lookup, &"t1_a")
	assert_eq(int(c.grid.site(&"t1_a")["max_integrity"]), 60)
	assert_eq(CampaignRules.asset_slots(c, _lookup, &"t1_a", _cfg), 4)
	assert_eq(CampaignRules.upgrade_node(c, _cfg, _lookup, &"t1_a")[0]["type"], "refused", "fully upgraded")
	c.armory = [&"turret", &"turret", &"turret", &"turret"]
	for i in 4:
		assert_eq(CampaignRules.deploy_asset(c, _cfg, _lookup, 0, &"t1_a")[0]["type"], "deployed", "slot %d" % i)
	var again := CampaignState.from_dict(c.to_dict())
	assert_eq(again.grid.upgrade_level_of(&"t1_a"), 2, "upgrade level survives save/load")
	assert_eq(CampaignRules.upgrade_node(c, _cfg, _lookup, &"home")[0]["type"], "refused", "home is not upgradable here")


func test_bunker_home_variant_folds_its_internal_node_into_the_home_server() -> void:
	var bunker := _lookup.get_content(&"home_bunker") as HomeServerVariantData
	assert_eq(bunker.validate().size(), 0)
	var c := _campaign(bunker)
	assert_eq(c.home_variant_id, &"home_bunker")
	assert_eq(c.grid.home_max_integrity, 70)
	assert_eq(c.grid.home_integrity, 70)
	assert_eq(c.grid.home_asset_slots, 3)
	assert_eq(c.grid.home_built_in, ["bunker_turret"])
	assert_eq(CampaignRules.asset_slots(c, _lookup, &"home", _cfg), 3)
	# The built-in turret fires from home during a raid.
	var raid := _lookup.get_content(&"raid_heat_25") as RaidData
	var result := RaidResolver.resolve(c, _corp.city_grid, raid, _lookup, _cfg, [&"t1_a"])
	var shots := 0
	for e in result.events:
		if e.get("type", "") == "shot" and e.get("asset") == &"bunker_turret":
			shots += 1
	assert_true(shots > 0, "bunker turret shot at least once")
	var standard := _campaign()
	assert_eq(standard.grid.home_max_integrity, 50)
	assert_eq(standard.grid.home_asset_slots, 2)
	var again := CampaignState.from_dict(c.to_dict())
	assert_eq(again.grid.home_built_in, ["bunker_turret"])


func test_netrun_boosts_are_bought_at_hq_and_consumed_by_the_next_run() -> void:
	var c := _campaign()
	assert_eq(_cfg.netrun_boosts.size(), 3)
	var schematics := c.schematics
	for id in [&"boost_warm_cache", &"boost_overclocked_deck", &"boost_field_kit"]:
		assert_eq(CampaignRules.buy_boost(c, _cfg, id)[0]["type"], "boost_bought", String(id))
	assert_eq(c.schematics, schematics - 45)
	assert_eq(CampaignRules.buy_boost(c, _cfg, &"boost_warm_cache")[0]["type"], "refused", "already queued")
	var deck_size := c.roster[0].deck.size()
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"t1_a", 4, _corp)
	assert_eq(c.pending_boosts.size(), 0, "consumed")
	assert_eq(s.run.cycles, 40)
	assert_eq(s.run.operative.deck.size(), deck_size + 2)
	assert_eq(s.run.temp_cards, [&"jolt", &"jolt"])
	s.enter_node(s.available_nodes()[0])
	assert_eq(s.combat.state.max_ram, _breaker.max_ram + 2, "Field Kit")
	# Complete the run: temp cards leave the deck.
	s._complete_run()
	assert_eq(c.get_operative(c.roster[0].id).deck.size(), deck_size)
	var none := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"t1_b", 4, _corp)
	assert_eq(none.run.cycles, 0, "boosts are one-time")
