extends GutTest
## Plan 2 N22: the run's normal-fight counter survives a save / load mid-run, and a save
## written before it existed loads by the layer rule (designer call 2026-10-18): 0 while the
## current node is in layers 1..easy_normal_fights (or no node entered), easy_normal_fights
## (EASY exhausted) once the current node lies past that layer.

var _resolver: CombatResolver
var _cfg: CampaignConfigData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = _resolver.config


func _start(seed: int = 11) -> NetrunSession:
	var c := CampaignState.new()
	c.campaign_seed = 99
	c.schematics = _cfg.starting_schematics
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	return NetrunSession.start(_resolver, c, &"op_1", 1, &"t1_a", seed)


func _reload(s: NetrunSession, drop_counter: bool = false) -> NetrunSession:
	var d := s.to_dict()
	if drop_counter:
		(d["run"] as Dictionary).erase("normal_fights_started")
	return NetrunSession.from_dict(_resolver, s.campaign, JSON.parse_string(JSON.stringify(d)))


func test_counter_survives_save_and_load_mid_run_and_the_next_picks_match() -> void:
	var s := _start()
	s._start_combat(false)
	assert_eq(s.run.normal_fights_started, 1)
	var back := _reload(s)
	assert_eq(back.run.normal_fights_started, 1, "the counter is saved")
	assert_eq(back.state_hash(), s.state_hash(), "the reloaded run hashes the same")
	for i in 3:
		s._start_combat(false)
		back._start_combat(false)
		assert_eq(back.combat.state.get_combatant(&"enemy_0").source_id, s.combat.state.get_combatant(&"enemy_0").source_id,
			"pick %d after the reload matches" % (i + 2))
	assert_eq(back.run.normal_fights_started, 4)


func test_old_save_before_any_node_loads_as_zero() -> void:
	var s := _start()
	s.run.normal_fights_started = 1
	assert_eq(_reload(s, true).run.normal_fights_started, 0)


func test_old_save_inside_the_easy_layers_loads_as_zero() -> void:
	var s := _start()
	s.run.normal_fights_started = 2
	s.run.current_node_id = s.run.map.nodes_in_layer(_cfg.easy_normal_fights)[0]["id"]
	assert_eq(_reload(s, true).run.normal_fights_started, 0)


func test_old_save_past_the_easy_layers_loads_as_easy_exhausted() -> void:
	var s := _start()
	s.run.current_node_id = s.run.map.nodes_in_layer(_cfg.easy_normal_fights + 1)[0]["id"]
	var back := _reload(s, true)
	assert_eq(back.run.normal_fights_started, _cfg.easy_normal_fights)
	assert_eq(back.normal_pool(), back.pools()["hard_enemies"], "the next normal fight draws HARD")
