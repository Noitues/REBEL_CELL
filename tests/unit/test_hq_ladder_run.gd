extends GutTest
## Plan 2 W2 HQ-LAUNCH (Solace): the HQ breach runs through the GENOME CORE ladder (run kind
## "hq"). Entering the Solace HQ starts a ladder session (stream `hq_graph`), a mid-ladder won
## fight continues the run, the crown win completes it (campaign WON), CAUGHT abandons by the
## Q24.1 path, a save mid-ladder resumes to the same hash, ACROSS previews equal results and the
## whole thing is deterministic by seed. Other corporations keep the single-node boss run.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _solace: CorporationData
var _meridian: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_solace = ContentRegistry.get_content(&"solace") as CorporationData
	_meridian = ContentRegistry.get_content(&"meridian") as CorporationData


func _campaign(corp: CorporationData) -> CampaignState:
	return CampaignRules.new_campaign(corp, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())


func _ladder(seed: int = 5) -> NetrunSession:
	var c := _campaign(_solace)
	return NetrunSession.start_hq_ladder(_resolver, c, c.roster[0].id, &"t1_a", 4, seed, _solace)


func _win_fight(s: NetrunSession) -> void:
	s.combat.state.player.max_hp = 9999
	var turns := 0
	while s.in_combat() and turns < 40:
		turns += 1
		s.combat.state.player.hp = 9999
		for e in s.combat.state.living_enemies():
			e.hp = 1
		CombatFixture.land(s.combat.state.player, 0, 0)
		s.combat_action(CombatAction.end_turn())


func _settle(s: NetrunSession) -> void:
	# Takes the payout the way PROCEED does, back to the map.
	if s.run.phase == RunState.Phase.REWARD:
		s.proceed_rewards()


func test_entry_starts_a_ladder_session_from_the_hq_graph_stream() -> void:
	var s := _ladder(7)
	assert_eq(s.run.kind, NetrunSession.HQ_LADDER_KIND)
	assert_eq(s.run.map.layer_count(), _cfg.solace_hq_rungs + 2)
	var expected := SolaceHqGraph.generate(_cfg, RngStreams.make_stream(7, RngStreams.HQ_GRAPH_STREAM))
	assert_eq(s.run.map.graph_hash(), expected.graph_hash())
	assert_true(s.run.corp_theme.solace.enabled)
	assert_eq(s.available_nodes().size(), 1, "the Clinic Gate")
	assert_true(NetrunSession.uses_hq_ladder(_solace))
	assert_false(NetrunSession.uses_hq_ladder(_meridian), "other HQs keep the single-node boss run")


func test_the_launch_kind_for_the_solace_central_server_is_the_ladder() -> void:
	var c := _campaign(_solace)
	var site: SiteData = null
	for sd in _solace.city_grid.sites:
		if sd != null and sd.objective == RC.SiteObjective.CENTRAL_SERVER:
			site = sd
	assert_not_null(site)
	assert_eq(CampaignRules.run_kind_for(c, site), "boss", "the rule kind is still the HQ breach")
	var s := NetrunSession.start_hq_ladder(_resolver, c, c.roster[0].id, site.id, site.tier, 3, _solace)
	assert_eq(s.run.site_id, site.id)
	assert_eq(s.run.kind, "hq")


func test_a_mid_ladder_win_continues_the_run() -> void:
	var s := _ladder(5)
	s.run.corp_theme.solace.front_milli = -90000
	s.enter_node(s.available_nodes()[0])
	assert_true(s.in_combat(), "the gate is a fight")
	_win_fight(s)
	_settle(s)
	assert_false(s.run.is_over(), "not 'netrun complete'")
	assert_eq(s.run.phase, RunState.Phase.MAP)
	assert_eq(s.run.combats_won, 1)
	assert_eq(s.available_nodes().size(), 2, "UP or ACROSS")
	assert_eq(s.campaign.outcome, CampaignState.Outcome.NONE)


func test_the_crown_win_completes_the_hq_run_and_wins_the_campaign() -> void:
	var s := _ladder(5)
	var g := s.run.map
	s.run.corp_theme.solace.front_milli = -90000
	var crown: Dictionary = g.layers[g.layer_count() - 1][0]
	s.run.current_node_id = g.layers[g.layer_count() - 2][0]["id"]
	s.enter_node(crown["id"])
	assert_true(s.in_combat())
	assert_eq(s.combat.state.enemies[0].source_id, &"renewal_engine")
	_win_fight(s)
	assert_true(s.run.is_over())
	assert_eq(s.run.outcome, RunState.Outcome.COMPLETED)
	assert_eq(s.campaign.outcome, CampaignState.Outcome.WON, "today's HQ-complete outcome")
	assert_eq(s.run.racks_captured, 0, "the ladder has no Rack captures")


func test_a_mini_boss_win_is_mid_ladder_and_is_not_a_rack_capture() -> void:
	var s := _ladder(5)
	var g := s.run.map
	s.run.corp_theme.solace.front_milli = -90000
	var mb: Dictionary = g.nodes_in_layer(_cfg.solace_hq_mini_boss_rung + 1)[0]
	s.run.current_node_id = g.nodes_in_layer(_cfg.solace_hq_mini_boss_rung)[0]["id"]
	s.enter_node(mb["id"])
	assert_true(s.in_combat())
	_win_fight(s)
	_settle(s)
	assert_false(s.run.is_over())
	assert_eq(s.run.racks_captured, 0)


func test_caught_abandons_the_hq_run_by_the_q24_1_path() -> void:
	var s := _ladder(5)
	var b := s.run.corp_theme.solace
	b.front_milli = 1000 - 100
	var id := s.available_nodes()[0]
	assert_true(bool(s.bloom_preview()[id]["caught"]))
	var op_id := s.run.operative.id
	s.enter_node(id)
	assert_true(b.caught)
	assert_eq(s.run.outcome, RunState.Outcome.DIED)
	assert_false(s.campaign.get_operative(op_id).alive)
	assert_eq(s.campaign.outcome, CampaignState.Outcome.NONE, "no win")


func test_save_mid_ladder_and_mid_fight_resumes_with_the_same_hash() -> void:
	var s := _ladder(11)
	s.run.corp_theme.solace.front_milli = -90000
	s.enter_node(s.available_nodes()[0])
	assert_true(s.in_combat())
	var json := JSON.stringify(s.to_dict())
	var back := NetrunSession.from_dict(_resolver, s.campaign, JSON.parse_string(json), _solace)
	assert_eq(back.state_hash(), s.state_hash())
	assert_eq(back.run.kind, "hq")
	assert_eq(back.run.map.graph_hash(), s.run.map.graph_hash(), "the ladder is saved, not regenerated")
	assert_true(back.in_combat())
	_win_fight(s)
	_settle(s)
	var json2 := JSON.stringify(s.to_dict())
	var back2 := NetrunSession.from_dict(_resolver, s.campaign, JSON.parse_string(json2), _solace)
	assert_eq(back2.state_hash(), s.state_hash(), "on the map between rooms")
	assert_eq(back2.available_nodes(), s.available_nodes())


func test_across_preview_equals_the_result_on_the_ladder_run() -> void:
	var s := _ladder(5)
	var source: Dictionary = s.run.map.layers[3][0]
	s.run.current_node_id = source["id"]
	var b := s.run.corp_theme.solace
	b.layer_milli = int(source["layer"]) * 1000
	b.front_milli = 0
	var target_id: StringName = source["next"][1]
	assert_true(NetrunSession.entered_across(s.run.map.get_node(target_id), source["id"]))
	var predicted := int(s.bloom_preview()[target_id]["gap_milli"])
	s.enter_node(target_id)
	assert_eq(BloomRules.gap_milli(b), predicted)
	assert_eq(b.front_milli, _cfg.bloom_hq_pace_node_milli + _cfg.bloom_pace_cross_milli)


func test_the_same_seed_gives_the_same_ladder_run() -> void:
	var hashes := []
	for i in 2:
		var s := _ladder(13)
		s.run.corp_theme.solace.front_milli = -90000
		s.enter_node(s.available_nodes()[0])
		_win_fight(s)
		_settle(s)
		hashes.append([s.state_hash(), s.run.map.graph_hash()])
	assert_eq(hashes[0], hashes[1])
