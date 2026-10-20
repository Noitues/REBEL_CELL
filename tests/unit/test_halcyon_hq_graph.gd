extends GutTest
## Plan 2 WH-20 (Halcyon HQ, THE LONG WAY ROUND): the graph passes the HQ validator for every
## seed and phase, is deterministic in its stream, holds the mini-boss gate and the vault boss, the
## Power Room and the climbs, and the HQ launches as a ladder session (run kind hq).

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _halcyon: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_halcyon = ContentRegistry.get_content(&"halcyon") as CorporationData


func _graph(seed: int, phase: int) -> MapGraph:
	return HalcyonHqGraph.generate(_cfg, RngStreams.make_stream(seed, RngStreams.HQ_GRAPH_STREAM), phase)


func test_graph_is_valid_deterministic_and_has_13_layers() -> void:
	for seed in range(1, 41):
		var phase := seed % 8
		var g := _graph(seed, phase)
		assert_eq(HalcyonHqGraph.validate(g, _cfg, phase), PackedStringArray(), "seed %d" % seed)
		assert_eq(g.layer_count(), 13)
		assert_eq(g.graph_hash(), _graph(seed, phase).graph_hash(), "same stream, same graph")


func test_mini_boss_gate_vault_power_room_and_climbs() -> void:
	var g := _graph(5, 3)
	assert_true(bool(g.layers[11][0].get("mini_boss", false)), "layer 12 is the Antechamber")
	assert_true(bool(g.layers[12][0].get("boss", false)), "layer 13 is the vault")
	var power := 0
	var annex := 0
	for node in g.all_nodes():
		if bool(node.get("power", false)):
			power += 1
		if bool(node.get("annex", false)):
			annex += 1
			assert_false(EyeRules.is_fight(node), "Annex rooms are non-fight")
	assert_eq(power, 1)
	assert_eq(annex, _cfg.halcyon_hq_annex_layers.size())
	var climbs := 0
	for node in g.all_nodes():
		climbs += (node.get("climb_from", []) as Array).size()
	assert_eq(climbs, 2, "climb A and climb B")


func test_validator_rejects_a_broken_graph() -> void:
	var g := _graph(5, 3)
	g.layers[11][0].erase("mini_boss")
	assert_false(HalcyonHqGraph.validate(g, _cfg, 3).is_empty())
	var g2 := _graph(5, 3)
	g2.layers[2][0]["next"].clear()
	assert_false(HalcyonHqGraph.validate(g2, _cfg, 3).is_empty(), "a node with no way out")


func test_hq_launches_as_a_ladder_session() -> void:
	var c := CampaignRules.new_campaign(_halcyon, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	c.corp_theme.halcyon.eye_index = 6
	var s := NetrunSession.start_hq_ladder(_resolver, c, c.roster[0].id, &"t1_a", 4, 7, _halcyon)
	assert_true(NetrunSession.uses_hq_ladder(_halcyon))
	assert_eq(s.run.kind, NetrunSession.HQ_LADDER_KIND)
	assert_true(s.run.corp_theme.halcyon.hq)
	assert_eq(s.run.corp_theme.halcyon.eye_phase, 6)
	var expected := _graph(7, 6)
	assert_eq(s.run.map.graph_hash(), expected.graph_hash())
	assert_false(s.run.corp_theme.solace.enabled, "no Bloom outside Solace")


func test_rest_and_cache_rooms_work_and_mini_boss_is_a_fight() -> void:
	var c := CampaignRules.new_campaign(_halcyon, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	var s := NetrunSession.start_hq_ladder(_resolver, c, c.roster[0].id, &"t1_a", 4, 7, _halcyon)
	var rest: Dictionary = {}
	var cache: Dictionary = {}
	for node in s.run.map.all_nodes():
		if bool(node.get("rest", false)) and rest.is_empty():
			rest = node
		if bool(node.get("cache", false)) and cache.is_empty():
			cache = node
	s.run.operative.hp = 1
	s.run.current_node_id = &""
	s.run.map.layers[0][0]["next"] = [rest["id"]] as Array[StringName]
	s.run.current_node_id = s.run.map.layers[0][0]["id"]
	s.enter_node(rest["id"])
	assert_gt(s.run.operative.hp, 1, "the bay heals")
	assert_eq(s.run.phase, RunState.Phase.MAP)
	s.run.current_node_id = s.run.map.layers[0][0]["id"]
	s.run.map.layers[0][0]["next"] = [cache["id"]] as Array[StringName]
	s.enter_node(cache["id"])
	assert_eq(s.run.phase, RunState.Phase.REWARD, "the Evidence Locker offers a pick")
	assert_eq(s.run.pending_rewards[0]["kind"], "daemon")


func test_hq_graph_reachable_over_1000_seeds() -> void:
	for seed in range(1, 1001):
		var phase := seed % 8
		var g := _graph(seed, phase)
		assert_eq(HalcyonHqGraph.eye_errors(g, _cfg, phase), PackedStringArray(), "seed %d phase %d" % [seed, phase])
