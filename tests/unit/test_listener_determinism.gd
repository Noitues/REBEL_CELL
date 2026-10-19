extends GutTest
## Plan 2 N6: listeners are deterministic. A seeded replay reaches the same state hash, the
## combat RNG stream moves exactly as it would without listeners, the listener code calls
## no global random function, and fires depend on inputs only (not the seed).

const L = preload("res://tests/helpers/listener_fixture.gd")
const SEEDS: Array[int] = [1000, 1001, 1002]


func _listeners() -> Array[ListenerData]:
	return [L.listener(RC.Trigger.ON_NUDGE, [L.hit(2), L.block(1)], 2),
		L.listener(RC.Trigger.ON_CARD_PLAYED, [L.block(2)], 2),
		L.listener(RC.Trigger.ON_RAM_SPENT, [L.hit(1)], 3),
		L.listener(RC.Trigger.ON_PERFECT, [L.hit(3)]),
		L.listener(RC.Trigger.ON_HIT_DEALT, [L.block(1)], 3, 5)]


## Three turns of fixed inputs: nudges, a card when one is in hand, End Turn.
func _play(s: CombatSession) -> Array:
	var fire_log := []
	for turn in 3:
		for a in [CombatAction.nudge(&"player", 1), CombatAction.nudge(&"enemy_0", -1), CombatAction.play_card(0), CombatAction.nudge(&"player", -1), CombatAction.end_turn()]:
			if s.state.is_over():
				return fire_log
			var r := s.apply(a as CombatAction)
			if r.ok():
				for f in L.fires(r):
					fire_log.append("%d:%s:%s:%d" % [turn, f["owner"], f["listener"], int(f["amount"])])
	return fire_log


func test_no_listeners_means_no_listener_state() -> void:
	var s := L.session([], {"seed": SEEDS[0]})
	assert_eq(_play(s), [], "no fires")
	for c in s.state.enemies:
		assert_true(c.listener_fires_combat.is_empty())


func test_seeded_replay_same_hash() -> void:
	for seed in SEEDS:
		var s := L.session(_listeners(), {"seed": seed})
		var fire_log := _play(s)
		assert_gt(fire_log.size(), 0, "listeners fired (seed %d)" % seed)
		var again := CombatSession.replay(s.resolver, s.setup, seed, s.history)
		assert_eq(again.state.state_hash(), s.state.state_hash(), "replay hash (seed %d)" % seed)


func test_listeners_use_no_rng() -> void:
	for seed in SEEDS:
		var heard := L.session(_listeners(), {"seed": seed})
		var deaf := L.session([], {"seed": seed})
		for turn in 3:
			for a in [CombatAction.nudge(&"player", 1), CombatAction.play_card(0), CombatAction.end_turn()]:
				if heard.state.is_over() or deaf.state.is_over():
					break
				heard.apply(a)
				deaf.apply(a)
				assert_eq(heard.rng.state, deaf.rng.state, "the stream moves as without listeners (seed %d)" % seed)
		var events: Array[Dictionary] = []
		var rng := CombatFixture.rng(seed)
		var before := rng.state
		heard.resolver.fire_listeners(heard.state.duplicate_state(), RC.Trigger.ON_NUDGE, {}, rng, events)
		assert_eq(rng.state, before, "a direct fire draws nothing")


func test_listener_source_has_no_global_random() -> void:
	var sources := [FileAccess.get_file_as_string("res://scripts/data/listener_data.gd")]
	var resolver := FileAccess.get_file_as_string("res://scripts/core/combat_resolver.gd")
	var start := resolver.find("func fire_listeners(")
	var stop := resolver.find("## The operative's Daemons as listeners")
	assert_true(start > 0 and stop > start, "found fire_listeners")
	sources.append(resolver.substr(start, stop - start))
	for src in sources:
		for banned in ["randi(", "randf(", "randomize(", "randi_range(", "randf_range("]:
			assert_eq(src.find(banned), -1, "no %s in listener code" % banned)


func test_different_seed_same_inputs_same_listener_fires() -> void:
	# Action-time fires are input-driven: the nudge / card / RAM fires of turn 1 match across seeds.
	var logs := []
	for seed in SEEDS:
		var s := L.session(_listeners(), {"seed": seed, "deck": [L.ZAP, L.ZAP, L.ZAP, L.ZAP, L.ZAP]})
		var fire_log := []
		for a in [CombatAction.nudge(&"player", 1), CombatAction.nudge(&"player", 1), CombatAction.play_card(0), CombatAction.nudge(&"player", -1)]:
			for f in L.fires(s.apply(a)):
				fire_log.append("%s:%d" % [f["listener"], int(f["amount"])])
		logs.append(fire_log)
	assert_eq(logs[0], logs[1])
	assert_eq(logs[1], logs[2])
	assert_gt((logs[0] as Array).size(), 0)
