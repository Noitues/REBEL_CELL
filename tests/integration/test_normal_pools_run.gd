extends GutTest
## Plan 2 N22 (ruling Q12), whole runs: walking the map (Routers preferred), the first
## config.easy_normal_fights Router fights are EASY normals and later ones HARD; elite and
## final-Rack fights are untouched; the same seed walks the same encounters; a save / load
## between fights does not change the sequence.

var _resolver: CombatResolver
var _cfg: CampaignConfigData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = _resolver.config


func _start(seed: int, corp_id: StringName = &"solace") -> NetrunSession:
	var c := CampaignState.new()
	c.campaign_seed = 99
	c.corporation_id = corp_id
	c.schematics = _cfg.starting_schematics
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	return NetrunSession.start(_resolver, c, &"op_1", 1, &"t1_a", seed)


func _auto_fight(s: NetrunSession) -> void:
	var turns := 0
	while s.in_combat() and turns < 80:
		s.combat.state.player.hp = s.combat.state.player.max_hp
		CombatFixture.land(s.combat.state.player, 0)
		for i in range(s.combat.state.hand.size() - 1, -1, -1):
			if i < s.combat.state.hand.size():
				s.combat_action(CombatAction.play_card(i, s.combat.state.target_id))
		s.combat_action(CombatAction.end_turn())
		turns += 1


func _settle(s: NetrunSession) -> void:
	var guard := 0
	while not s.run.is_over() and s.run.phase != RunState.Phase.MAP and guard < 20:
		guard += 1
		match s.run.phase:
			RunState.Phase.REWARD:
				s.proceed_rewards()
			RunState.Phase.EVENT:
				s.choose_event_option(s.current_event().choices.size() - 1)
			RunState.Phase.SHOP:
				s.leave_shop()
			_:
				return


## Walks the run to its end, Routers first (lowest id among the open ones), optionally saving
## and reloading after every fight. Returns [{enemy_id, elite, mini_boss}] per fight started.
func _walk(s: NetrunSession, reload_each: bool = false) -> Array[Dictionary]:
	var fights: Array[Dictionary] = []
	var steps := 0
	while not s.run.is_over() and steps < 20:
		steps += 1
		var open := s.available_nodes()
		if open.is_empty():
			break
		open.sort()
		var pick := open[0]
		for id in open:
			var n := s.run.map.get_node(id)
			if n["type"] == RC.InfilNodeType.ROUTER and not n["elite"]:
				pick = id
				break
		for e in s.enter_node(pick):
			if e.get("type", "") == "combat_start":
				fights.append({"enemy_id": e["enemy_id"], "elite": e["elite"], "mini_boss": e["mini_boss"]})
		_auto_fight(s)
		_settle(s)
		if reload_each and not s.run.is_over():
			s = NetrunSession.from_dict(_resolver, s.campaign, JSON.parse_string(JSON.stringify(s.to_dict())))
	return fights


func _check_run(seed: int, corp_id: StringName) -> void:
	var s := _start(seed, corp_id)
	var fights := _walk(s)
	var normals := 0
	for f in fights:
		if f["mini_boss"]:
			assert_true(s.pools()["mini_bosses"].has(f["enemy_id"]), "%s: final Rack is a mini-boss" % f["enemy_id"])
		elif f["elite"]:
			assert_true(s.pools()["elites"].has(f["enemy_id"]), "%s: elite node is an elite" % f["enemy_id"])
		else:
			var want: String = "easy_enemies" if normals < _cfg.easy_normal_fights else "hard_enemies"
			if s.pools()[want].is_empty():
				want = "enemies"
			assert_true(s.pools()[want].has(f["enemy_id"]), "%s seed %d normal fight %d (%s) from %s" % [corp_id, seed, normals + 1, f["enemy_id"], want])
			normals += 1
	assert_true(normals >= _cfg.easy_normal_fights + 1, "%s seed %d: the walk saw EASY and HARD fights (%d normals)" % [corp_id, seed, normals])
	assert_eq(s.run.normal_fights_started, normals)


func test_runs_draw_easy_then_hard_for_every_corp() -> void:
	for corp_id in [&"solace", &"halcyon", &"meridian", &"orbital"]:
		for seed in [5, 6]:
			_check_run(seed, corp_id)


func test_same_seed_same_encounters_and_reload_between_fights_changes_nothing() -> void:
	var a := _walk(_start(31))
	var b := _walk(_start(31))
	var c := _walk(_start(31), true)
	assert_eq(a, b, "same seed, same encounter sequence")
	assert_eq(a, c, "a save / load after every fight keeps the sequence")
