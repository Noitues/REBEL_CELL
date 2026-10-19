extends GutTest
## Plan 2 N20: riders draw no RNG, a seeded replay of a rider fight matches the original's
## state hash, and the hit order is fixed (hit, then the target's needle index).

const F := preload("res://tests/helpers/rider_fixture.gd")


func _play(s: CombatSession, turns: int) -> void:
	for t in turns:
		s.apply(CombatAction.nudge(&"enemy_0", 1 if t % 2 == 0 else -1))
		s.apply(CombatAction.end_turn())


func test_seeded_replay_same_hash() -> void:
	var iv := F.rider(&"rd_rep_iv", 2, 2, 4.0, true, RC.Status.CORRUPTED, 1)
	var s := F.session(&"rd_rep", iv, [0, 15])
	F.corrupt(s, [1, 3])
	var corrupted := s.state.player.wheel.slice_stacks.duplicate(true)
	_play(s, 5)
	assert_true(s.state.player.hp < 999, "the riders dealt damage")
	# Replay rebuilds from setup and seed; re-stage the hand-set statuses the same way.
	var a := CombatSession.replay(s.resolver, s.setup, s.combat_seed, [])
	var b := CombatSession.replay(s.resolver, s.setup, s.combat_seed, [])
	for r: CombatSession in [a, b]:
		for i in r.state.player.wheel.pointer_ticks.size():
			CombatFixture.land(r.state.player, 0, 0, i)
		CombatFixture.land(r.state.get_combatant(&"enemy_0"), 0)
		r.state.player.wheel.slice_stacks = corrupted.duplicate(true)
		for act in s.history:
			assert_true(r.apply(act).ok())
	assert_eq(a.state_hash(), b.state_hash(), "two replays match")
	assert_eq(a.state_hash(), s.state_hash(), "the replay matches the original")


func test_riders_add_no_rng_draws() -> void:
	var plain := F.session(&"rd_rng0", F.rider(&"rd_rng0_shim", 5))
	var riders := F.session(&"rd_rng1", F.rider(&"rd_rng1_shim", 5, 4, 4.0, true))
	assert_eq(plain.rng.state, riders.rng.state, "same seed, same start")
	var a: CombatResult = F.end(plain)["result"]
	var b: CombatResult = F.end(riders)["result"]
	assert_true(a.ok() and b.ok())
	assert_eq(plain.rng.state, riders.rng.state, "the riders drew nothing from the RNG")


func test_hit_order_is_hit_then_target_needle() -> void:
	var s := F.session(&"rd_ord", F.rider(&"rd_ord_shim", 5, 2), [0, 15])
	s.state.player.evade_charges = 1
	s.state.player.block = 5
	var r: CombatResult = F.end(s)["result"]
	var hits := F.hits_of(r.events, s.state.player.id)
	assert_eq(hits.map(func(e: Dictionary) -> String: return String(e["type"])), ["evaded", "damage", "damage", "damage"])
	var dmg := hits.slice(1)
	assert_eq(dmg.map(func(e: Dictionary) -> int: return int(e["blocked"])), [5, 0, 0], "BLOCK is spent hit by hit, in order")
