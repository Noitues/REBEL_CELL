extends GutTest
## Horizontal pass 11 fixes (GAP_ANALYSIS H11): a stationed operative leaves its post to
## run and a dead one frees it, an empty roster can always recruit, Heat labels show the
## applied Heat, ICE 13 raises home repairs, HQ boosts reach special runs, a Firewall Relay
## shares every class's station bonus, and the new config numbers are used.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _corp: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"solace") as CorporationData


func _campaign(ice: int = 0) -> CampaignState:
	return CampaignRules.new_campaign(_corp, _cfg, _lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node(), ice)


func test_a_stationed_operative_leaves_its_post_to_run_and_death_frees_it() -> void:
	var c := _campaign()
	var op := c.roster[0]
	c.grid.site(c.grid.home_site_id)["stationed"] = String(op.id)  # the home server holds a station slot
	assert_eq(CampaignRules.stationed_site(c, op.id), c.grid.home_site_id)
	var s := NetrunSession.start(_resolver, c, op.id, 1, &"t1_a", 5, _corp)
	assert_eq(CampaignRules.stationed_site(c, op.id), &"", "launching recalls the operative")
	var recalled := false
	for e in s.last_events:
		recalled = recalled or e.get("type", "") == "recalled"
	assert_true(recalled, "the log says so")
	var other := c.roster[1]
	c.grid.site(c.grid.home_site_id)["stationed"] = String(other.id)
	var special := NetrunSession.start_special(_resolver, c, other.id, "reclaim", &"t1_a", 1, 5, &"triage_unit", {}, _corp)
	assert_eq(CampaignRules.stationed_site(c, other.id), &"", "special runs recall too")
	c.grid.site(c.grid.home_site_id)["stationed"] = String(other.id)  # stale post from an old save
	special._die()
	assert_eq(c.grid.stationed_on(c.grid.home_site_id), &"", "a dead operative frees the post")


func test_an_empty_roster_can_always_recruit() -> void:
	var c := _campaign()
	assert_eq(CampaignRules.rookie_price(c, _cfg), _cfg.rookie_cost)
	for op in c.roster:
		op.alive = false
	c.schematics = 0
	assert_eq(CampaignRules.rookie_price(c, _cfg), _cfg.emergency_rookie_cost)
	var events := CampaignRules.recruit(c, _cfg, ContentRegistry.get_content(&"breaker") as ClassData)
	assert_eq(events[0]["type"], "recruited")
	assert_eq(c.living_operatives().size(), 1)
	assert_eq(CampaignRules.rookie_price(c, _cfg), _cfg.rookie_cost, "full price once someone is alive")


func _level_with(type: int) -> int:
	for level in _cfg.ice_ladder:
		for m in level.modifiers:
			if m != null and m.type == type:
				return level.level
	return -1


func test_map_heat_labels_match_the_heat_applied() -> void:
	var ice := _level_with(RC.RuleModifierType.HEAT_GAIN_PCT)
	assert_true(ice >= 0, "some ICE level scales Heat gain")
	var c := _campaign(ice)
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 3, &"t1_a", 5, _corp)
	var checked := 0
	for node in s.run.map.all_nodes():
		if int(node["heat"]) != 0:
			assert_eq(s.node_heat(node["id"]), HeatRules.scaled_delta(c, int(node["heat"]), _cfg))
			assert_eq(int(s.map_heat()[node["id"]]), s.node_heat(node["id"]))
			checked += 1
	assert_true(checked > 0, "the map has Heat nodes")
	for id in s.available_nodes():
		var node := s.run.map.get_node(id)
		if node["elite"] and node["type"] == RC.InfilNodeType.ROUTER:
			var before := c.heat
			var shown := s.node_heat(id)
			s.enter_node(id)
			assert_eq(c.heat - before, shown, "entering adds what was shown")


func test_ice_13_raises_home_repairs() -> void:
	var ice := _level_with(RC.RuleModifierType.REPAIR_COST_PCT)
	assert_true(ice >= 0)
	var plain := _campaign()
	var hard := _campaign(ice)
	for c in [plain, hard]:
		c.grid.home_integrity = c.grid.home_max_integrity - 10
		c.schematics = 999
	assert_true(CampaignRules.home_repair_price(hard, _cfg) > CampaignRules.home_repair_price(plain, _cfg))
	var price := CampaignRules.home_repair_price(hard, _cfg)
	CampaignRules.repair_home(hard, _cfg)
	assert_eq(hard.schematics, 999 - price, "charged what was shown")


func test_hq_boosts_reach_special_runs() -> void:
	var c := _campaign()
	var kit: NetrunBoostData = null
	for b in _cfg.netrun_boosts:
		if b != null and b.max_ram_bonus > 0:
			kit = b
	assert_not_null(kit)
	c.pending_boosts.append(kit.id)
	var s := NetrunSession.start_special(_resolver, c, c.roster[0].id, "boss", &"t1_a", 1, 5, &"triage_unit", {}, _corp)
	var cls := ContentRegistry.get_content(&"breaker") as ClassData
	assert_eq(int(s.run.combat_overrides.get("max_ram", 0)), cls.max_ram + kit.max_ram_bonus)
	assert_true(c.pending_boosts.is_empty(), "the boost is spent")


func test_a_firewall_relay_shares_every_station_bonus() -> void:
	var grid := GridFixture.chain_grid([&"c1", &"c2"])
	var c := GridFixture.campaign(grid, {&"c1": &"firewall_relay", &"c2": &"safehouse"})
	c.recruit(ContentRegistry.get_content(&"ghost") as ClassData, "Op")
	CampaignRules.station(c, _lookup, c.roster[0].id, &"c2")
	var here := RaidResolver.station_bonuses(c, c.grid, grid, _lookup, &"c2")
	var relay := RaidResolver.station_bonuses(c, c.grid, grid, _lookup, &"c1")
	assert_true(int(here["hold"]) > 0)
	assert_eq(relay["hold"], here["hold"], "the relay shares the Ghost's hold")


func test_new_config_numbers_are_used() -> void:
	var p := ProfileState.new()
	assert_eq(p.ice_cap_for(&"solace", _cfg.new_corp_ice_offset, _cfg.ice_base_cap, _cfg.max_ice_level(), _cfg.ice_unlock_step), _cfg.ice_base_cap)
	p.best_ice_by_corp["solace"] = 4
	assert_eq(p.ice_cap_for(&"solace", 5, 3, 20, 5), 9, "the unlock step comes from the caller")
	assert_eq(_cfg.max_ice_level(), 20)
	var cfg: CampaignConfigData = _cfg.duplicate()
	cfg.shop_card_stock = 5
	var c := _campaign()
	var s := NetrunSession.start(CombatResolver.new(cfg, _lookup), c, c.roster[0].id, 1, &"t1_a", 5, _corp)
	s._open_shop()
	assert_eq(s.run.shop["cards"].size(), 5)
