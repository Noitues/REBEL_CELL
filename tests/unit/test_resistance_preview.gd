extends GutTest
## Plan 2 N21 (rulings Q16, Q31): the turn's zero-and-refresh keeps preview == result (End
## Turn and the nudge after it), undo never crosses the turn checkpoint, the "+N" amount
## survives a save round trip, an old save without it loads, and a seeded replay matches.


func _session(seed: int = 77) -> CombatSession:
	var e := PhaseFixture.enemy(&"n21_pv", 999, [], RC.EnemyClass.ELITE, CombatFixture.null_wheel(3))
	e.phases.clear()
	return PhaseFixture.session(e, 2, [0], seed)


func test_end_turn_preview_equals_the_result_across_the_refresh() -> void:
	var s := _session()
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	var pv := s.preview(CombatAction.end_turn())
	var r := s.apply(CombatAction.end_turn())
	assert_eq(pv.state.state_hash(), r.state.state_hash(), "preview == result after the refresh")
	assert_eq(pv.state.get_combatant(&"enemy_0").resistance, 3)
	var pe := s.preview_end_turn()
	var r2 := s.preview(CombatAction.end_turn())
	assert_eq(pe.resolved_state.state_hash(), r2.resolved_state.state_hash(), "End Turn preview == apply's resolved state")


func test_nudge_preview_after_the_refresh_equals_the_result() -> void:
	var s := _session()
	s.apply(CombatAction.end_turn())
	var pv := s.preview(CombatAction.nudge(&"enemy_0", 1))
	var r := s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(pv.state.state_hash(), r.state.state_hash())
	assert_eq(r.state.get_combatant(&"enemy_0").resistance, 2)


func test_undo_never_crosses_the_turn_checkpoint() -> void:
	var s := _session()
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	s.apply(CombatAction.end_turn())
	assert_false(s.can_rewind(), "nothing to undo right after the turn's refresh")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 2)
	s.rewind()
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 3, "back to the refreshed value, not before it")
	assert_eq(s.state.get_combatant(&"enemy_0").resistance_gain, 3)


func test_save_round_trip_keeps_the_refresh() -> void:
	var s := _session()
	s.apply(CombatAction.end_turn())
	var back := CombatSession.from_dict(s.resolver, s.to_dict())
	assert_eq(back.state_hash(), s.state_hash())
	assert_eq(back.state.get_combatant(&"enemy_0").resistance_gain, 3)


func test_an_old_save_without_the_gain_loads() -> void:
	var c := CombatantState.new()
	c.resistance = 2
	var d := c.to_dict()
	assert_false(d.has("resistance_gain"), "only written when non-zero")
	var back := CombatantState.from_dict(d)
	assert_eq(back.resistance, 2)
	assert_eq(back.resistance_gain, 0)


func test_seeded_replay_matches() -> void:
	var a := _session(5)
	var b := _session(5)
	for i in 3:
		a.apply(CombatAction.nudge(&"enemy_0", 1))
		b.apply(CombatAction.nudge(&"enemy_0", 1))
		a.apply(CombatAction.end_turn())
		b.apply(CombatAction.end_turn())
	assert_eq(a.state_hash(), b.state_hash())
	var replayed := CombatSession.replay(a.resolver, a.setup, a.combat_seed, a.history)
	assert_eq(replayed.state_hash(), a.state_hash(), "replay of the history matches")
