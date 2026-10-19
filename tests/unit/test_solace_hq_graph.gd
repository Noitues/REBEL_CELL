extends GutTest
## Plan 2 WH-10 (Solace HQ, THE GENOME CORE), fast tier: the ladder graph passes the HQ
## validator for every seed, is longer than 7 layers (D10), is deterministic in its stream, ACROSS
## costs the config's cross pace (preview == result), the ward rest room pushes the front back,
## and the boss keeps at least 3 phases (N3) with a mini-boss on the mini-boss rung.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _solace: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_solace = ContentRegistry.get_content(&"solace") as CorporationData


func _graph(seed: int) -> MapGraph:
	return SolaceHqGraph.generate(_cfg, RngStreams.make_stream(seed, RngStreams.HQ_GRAPH_STREAM))


func _session(seed: int = 5) -> NetrunSession:
	var c := CampaignRules.new_campaign(_solace, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 4, &"t1_a", seed, _solace)
	s.run.map = _graph(seed)
	BloomRules.begin(s.run.corp_theme.solace, _cfg, _solace, 4, true)
	return s


func test_graph_passes_the_hq_validator_for_every_seed_and_is_longer_than_seven_layers() -> void:
	for seed in range(1, 41):
		var g := _graph(seed)
		assert_eq(SolaceHqGraph.validate(g, _cfg), PackedStringArray(), "seed %d" % seed)
		assert_eq(g.layer_count(), _cfg.solace_hq_rungs + 2)
		assert_gt(g.layer_count(), 7, "D10: HQ runs exceed 7 layers")


func test_the_validator_rejects_a_broken_ladder() -> void:
	var g := _graph(3)
	g.layers[3][0]["next"] = [MapGraph.make_id(5, 0)] as Array[StringName]
	assert_false(SolaceHqGraph.validate(g, _cfg).is_empty(), "a room without its ACROSS edge")
	g = _graph(3)
	g.layers[4][1]["across_from"] = [] as Array[StringName]
	assert_false(SolaceHqGraph.validate(g, _cfg).is_empty(), "a missing across_from")
	g = _graph(3)
	g.layers[4][1]["across"] = true
	assert_false(SolaceHqGraph.validate(g, _cfg).is_empty(), "a node-wide across flag")
	g = _graph(3)
	g.layers[_cfg.solace_hq_rungs + 1][0].erase("boss")
	assert_false(SolaceHqGraph.validate(g, _cfg).is_empty(), "a crown that is not the boss")


func test_rung_one_fights_rest_rungs_and_mini_boss_rung_come_from_config() -> void:
	var g := _graph(9)
	for node in g.nodes_in_layer(2):
		assert_eq(int(node["type"]), RC.InfilNodeType.ROUTER)
		assert_false(node["elite"])
	for r in _cfg.solace_hq_ward_rest_rungs:
		assert_true(bool(g.layers[r][0].get("rest", false)), "Ward rest at rung %d" % r)
	for node in g.nodes_in_layer(_cfg.solace_hq_mini_boss_rung + 1):
		assert_true(bool(node.get("mini_boss", false)))
	assert_true(bool(g.layers[g.layer_count() - 1][0].get("boss", false)))


func test_same_seed_same_graph_and_the_round_trip_keeps_the_ladder_keys() -> void:
	var a := _graph(21)
	var b := _graph(21)
	assert_eq(a.graph_hash(), b.graph_hash())
	var back := MapGraph.from_dict(a.to_dict())
	assert_eq(back.graph_hash(), a.graph_hash())
	assert_eq(SolaceHqGraph.validate(back, _cfg), PackedStringArray())
	var differs := false
	for seed in range(22, 30):
		differs = differs or _graph(seed).graph_hash() != a.graph_hash()
	assert_true(differs, "the stream decides the room kinds")


func test_a_street_map_dictionary_has_no_ladder_keys() -> void:
	var g := MapGenerator.generate(2, _cfg, RngStreams.make_stream(4, &"map"))
	for node in g.to_dict()["layers"][0]:
		for k in MapGraph.OPTIONAL_KEYS:
			assert_false(node.has(k))
		assert_false(node.has("across_from"))


func _walk(seed: int, walk_seed: int) -> Array:
	var g := _graph(seed)
	var rng := RngStreams.make_stream(walk_seed, &"walk")
	var b := BloomState.new()
	BloomRules.begin(b, _cfg, _solace, 4, true)
	var cur: Dictionary = g.layers[0][0]
	var steps := []
	while not cur["next"].is_empty():
		var nxt: StringName = cur["next"][rng.randi_range(0, cur["next"].size() - 1)]
		var node := g.get_node(nxt)
		var across := NetrunSession.entered_across(node, cur["id"])
		if bool(node.get("rest", false)):
			BloomRules.push(b, _cfg)
		var caught := BloomRules.enter(b, _cfg, 4, int(node["layer"]), across)
		steps.append([nxt, across, b.front_milli, caught])
		if caught:
			break
		cur = node
	return steps


func test_a_seeded_walk_through_the_graph_is_deterministic() -> void:
	for seed in [2, 7, 13]:
		assert_eq(_walk(seed, 99), _walk(seed, 99), "seed %d" % seed)
	var any_across := false
	for w in range(1, 12):
		for step in _walk(5, w):
			any_across = any_across or bool(step[1])
	assert_true(any_across, "some walks cross")


func test_across_costs_the_cross_pace_and_the_preview_equals_the_result() -> void:
	for target_tower in [0, 1]:
		var s := _session()
		var source: Dictionary = s.run.map.layers[3][0]  # rung 2, Ward
		s.run.current_node_id = source["id"]
		var b := s.run.corp_theme.solace
		b.layer_milli = int(source["layer"]) * 1000
		b.front_milli = 0
		var target_id: StringName = source["next"][0] if target_tower == 0 else source["next"][1]
		var target := s.run.map.get_node(target_id)
		var is_across: bool = target_tower == 1
		assert_eq(NetrunSession.entered_across(target, source["id"]), is_across)
		var predicted := int(s.bloom_preview()[target_id]["gap_milli"])
		s.enter_node(target_id)
		assert_eq(BloomRules.gap_milli(b), predicted, "preview == result")
		var expected_front := _cfg.bloom_hq_pace_node_milli + (_cfg.bloom_pace_cross_milli if is_across else 0)
		assert_eq(b.front_milli, expected_front)


func test_the_ward_rest_room_binds_to_ward_rest_and_opens_no_event_or_fight() -> void:
	var s := _session()
	var g := s.run.map
	var rest: Dictionary = g.layers[_cfg.solace_hq_ward_rest_rungs[0]][0]
	var before: Dictionary = g.get_node(MapGraph.make_id(int(rest["layer"]) - 1, 0))
	s.run.current_node_id = before["id"]
	var b := s.run.corp_theme.solace
	b.layer_milli = int(before["layer"]) * 1000
	b.front_milli = b.layer_milli - 3000
	var expected := b.front_milli + _cfg.bloom_hq_pace_node_milli - _cfg.bloom_dose_push_milli
	s.enter_node(rest["id"])
	assert_eq(b.front_milli, expected)
	assert_eq(s.run.phase, RunState.Phase.MAP)
	assert_false(s.in_combat())
	assert_true(s.available_nodes().size() == 2, "the ladder goes on")


func test_the_crown_fights_the_genome_core_and_the_mini_boss_rung_a_mini_boss() -> void:
	var s := _session()
	var g := s.run.map
	var b := s.run.corp_theme.solace
	b.front_milli = -9000
	var mb: Dictionary = g.nodes_in_layer(_cfg.solace_hq_mini_boss_rung + 1)[0]
	s.run.current_node_id = g.nodes_in_layer(_cfg.solace_hq_mini_boss_rung)[0]["id"]
	s.enter_node(mb["id"])
	assert_true(s.in_combat())
	var mini := _lookup.get_content(s.combat.state.enemies[0].source_id) as EnemyData
	assert_true(mini.is_mini_boss, "mini-boss rung holds a mini-boss")
	var s2 := _session()
	var crown: Dictionary = s2.run.map.layers[s2.run.map.layer_count() - 1][0]
	s2.run.corp_theme.solace.front_milli = -9000
	s2.run.current_node_id = s2.run.map.layers[s2.run.map.layer_count() - 2][0]["id"]
	s2.enter_node(crown["id"])
	assert_true(s2.in_combat())
	assert_eq(s2.combat.state.enemies[0].source_id, &"renewal_engine")


func test_the_boss_keeps_at_least_three_phases_and_the_mini_boss_stands() -> void:
	var boss := _solace.final_boss
	assert_eq(boss.id, &"renewal_engine")
	assert_true(boss.is_boss)
	assert_gte(boss.phases.size() + 1, _cfg.phase_count_min_by_class[3], "N3 minimum")
	assert_gte(boss.phases.size() + 1, 3)
	assert_true((ContentRegistry.get_content(&"account_manager") as EnemyData).is_mini_boss)
