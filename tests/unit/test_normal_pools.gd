extends GutTest
## Plan 2 N22 (ruling Q12): EASY / HARD normal-fight pools. The first
## config.easy_normal_fights normal fights of a run draw EASY, later ones HARD; elites and
## the final Rack's mini-boss are unaffected; an empty pool falls back to the other one; the
## combat stream takes exactly one randi_range per pick (then the fight seed), as before.

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


## The enemy ids of `n` Router fights started back to back (no map walk needed for the pick).
func _normal_picks(s: NetrunSession, n: int) -> Array[StringName]:
	var out: Array[StringName] = []
	for i in n:
		s._start_combat(false)
		out.append(s.combat.state.get_combatant(&"enemy_0").source_id)
	return out


func test_pools_split_the_normals_by_their_authored_pool_sorted_by_id() -> void:
	var s := _start()
	var p := s.pools()
	var easy: Array = p["easy_enemies"]
	var hard: Array = p["hard_enemies"]
	assert_eq(easy.size() + hard.size(), p["enemies"].size(), "every normal is in exactly one pool")
	for id in easy:
		assert_eq((ContentRegistry.get_content(id) as EnemyData).normal_pool, RC.NormalPool.EASY, "%s is EASY" % id)
		assert_false(hard.has(id))
	for id in hard:
		assert_eq((ContentRegistry.get_content(id) as EnemyData).normal_pool, RC.NormalPool.HARD, "%s is HARD" % id)
	var sorted_easy := easy.duplicate()
	sorted_easy.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	assert_eq(easy, sorted_easy, "EASY sorted by content id")
	for id in p["elites"] + p["mini_bosses"]:
		assert_false(easy.has(id) or hard.has(id), "%s (elite / mini-boss) is in no normal pool" % id)


func test_first_two_normal_fights_are_easy_then_hard() -> void:
	var s := _start()
	assert_false(s.pools()["easy_enemies"].is_empty(), "Solace ships EASY normals")
	var picks := _normal_picks(s, 5)
	for i in picks.size():
		var want: String = "easy_enemies" if i < _cfg.easy_normal_fights else "hard_enemies"
		assert_true(s.pools()[want].has(picks[i]), "fight %d (%s) is from %s" % [i + 1, picks[i], want])
	assert_eq(s.run.normal_fights_started, 5)


func test_elite_and_final_rack_fights_do_not_count_or_use_the_normal_pools() -> void:
	var s := _start()
	s._start_combat(true)
	assert_true(s.pools()["elites"].has(s.combat.state.get_combatant(&"enemy_0").source_id), "an elite node draws an elite")
	assert_eq(s.run.normal_fights_started, 0, "an elite fight is not a normal fight")
	s.run.current_node_id = s.run.map.final_node_id()
	s._start_combat(true)
	assert_true(s.pools()["mini_bosses"].has(s.combat.state.get_combatant(&"enemy_0").source_id), "the final Rack draws a mini-boss")
	assert_eq(s.run.normal_fights_started, 0)


func test_one_pick_advances_the_combat_stream_by_one_draw_on_the_chosen_pool() -> void:
	var s := _start()
	for i in 4:
		var rng := s.streams.get_stream(&"combat")
		var copy := RandomNumberGenerator.new()
		copy.seed = rng.seed
		copy.state = rng.state
		var pool := s.normal_pool()
		var want: StringName = pool[copy.randi_range(0, pool.size() - 1)]
		copy.randi()  # the fight seed
		s._start_combat(false)
		assert_eq(s.combat.state.get_combatant(&"enemy_0").source_id, want, "pick %d" % (i + 1))
		assert_eq(rng.state, copy.state, "pick %d: one randi_range + the fight seed, nothing more" % (i + 1))


func test_empty_easy_pool_falls_back_to_hard_and_the_reverse() -> void:
	var s := _start()
	var easy: Array = s._pools["easy_enemies"]
	var hard: Array = s._pools["hard_enemies"]
	s._pools["easy_enemies"] = []
	assert_eq(s.normal_pool(), hard, "no EASY normals: the first fights draw HARD")
	s._pools["easy_enemies"] = easy
	s._pools["hard_enemies"] = []
	s.run.normal_fights_started = _cfg.easy_normal_fights
	assert_eq(s.normal_pool(), easy, "no HARD normals: later fights draw EASY")
	var rng := s.streams.get_stream(&"combat")
	var copy := RandomNumberGenerator.new()
	copy.seed = rng.seed
	copy.state = rng.state
	copy.randi_range(0, easy.size() - 1)
	copy.randi()
	s._start_combat(false)
	assert_true(easy.has(s.combat.state.get_combatant(&"enemy_0").source_id))
	assert_eq(rng.state, copy.state, "the fallback costs no extra draw")


func test_same_seed_same_encounter_sequence() -> void:
	assert_eq(_normal_picks(_start(23), 6), _normal_picks(_start(23), 6))


func test_preview_of_a_fight_does_not_count_a_normal_fight() -> void:
	var s := _start()
	var copy := RngStreams.from_dict(s.streams.to_dict())
	var setup := s._combat_setup(false, false, copy.get_stream(&"combat"))
	assert_eq(s.run.normal_fights_started, 0, "a setup drawn from a copy changes nothing")
	s._start_combat(false)
	assert_eq(s.combat.state.get_combatant(&"enemy_0").source_id, setup["enemy_id"], "preview == result")


func test_validate_refuses_easy_on_a_non_normal() -> void:
	var e := EnemyData.new()
	e.id = &"n22_elite"
	e.is_elite = true
	e.normal_pool = RC.NormalPool.EASY
	assert_true(",".join(e.validate(_cfg)).contains("pool_on_non_normal"), "EASY elite refused by name")
	e.normal_pool = RC.NormalPool.HARD
	assert_false(",".join(e.validate(_cfg)).contains("pool_on_non_normal"), "the default HARD is fine on an elite")
	var n := EnemyData.new()
	n.id = &"n22_normal"
	n.normal_pool = RC.NormalPool.EASY
	assert_false(",".join(n.validate(_cfg)).contains("pool_on_non_normal"), "a normal may be EASY")
