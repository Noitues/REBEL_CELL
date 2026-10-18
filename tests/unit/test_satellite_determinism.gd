extends GutTest
## N13: fixed satellites and replacement keep the deterministic core: refused moves change
## nothing, a seeded replay matches, rewind restores a replaced satellite only within its
## checkpoint, and a save round trip keeps the state hash.


func _session() -> CombatSession:
	var first := SatelliteFixture.satellite(&"sf_first")
	var second := SatelliteFixture.satellite(&"sf_second", 7)
	var later := CombatFixture.spawn(second, SatelliteFixture.DOCK_SLOT)
	later.trigger = RC.Trigger.ON_TURN_START
	later.every_n = 2  # turn 1 start skips it; turn 2 start replaces
	var spawns: Array[SatelliteSpawnData] = [CombatFixture.spawn(first, SatelliteFixture.DOCK_SLOT), later]
	var cards: Array[CardData] = [SatelliteFixture.move_card(&"sf_nudge", RC.EffectType.NUDGE),
		SatelliteFixture.move_card(&"sf_undock_nudge", RC.EffectType.NUDGE, 1, true)]
	return SatelliteFixture.session(cards, spawns)


func _script(s: CombatSession, with_refusals: bool) -> void:
	for turn in 3:
		var sat := SatelliteFixture.sat_of(s)
		if with_refusals:
			s.apply(CombatAction.nudge(sat.id, 1))
			var i := s.state.hand.find(&"sf_nudge")
			if i >= 0:
				s.apply(CombatAction.play_card(i, sat.id))
		var u := s.state.hand.find(&"sf_undock_nudge")
		if u >= 0:
			s.apply(CombatAction.play_card(u, sat.id))
		s.apply(CombatAction.end_turn())


func test_refused_inputs_do_not_change_the_hash() -> void:
	var a := _session()
	var b := _session()
	_script(a, false)
	_script(b, true)
	assert_eq(a.state_hash(), b.state_hash())
	assert_eq(a.history.size(), b.history.size(), "refusals are not logged")


func test_seeded_replay_matches() -> void:
	var s := _session()
	_script(s, true)
	var again := CombatSession.replay(s.resolver, s.setup, s.combat_seed, s.history)
	assert_eq(again.state_hash(), s.state_hash())


func test_save_round_trip_keeps_the_hash() -> void:
	var s := _session()
	_script(s, false)
	var back := CombatSession.from_dict(s.resolver, s.to_dict())
	assert_eq(back.state_hash(), s.state_hash())


func test_rewind_never_crosses_the_checkpoint_after_a_replace() -> void:
	var s := _session()
	s.apply(CombatAction.end_turn())  # turn start replaces sf_first: a checkpoint (respins)
	assert_eq(SatelliteFixture.sat_of(s).source_id, &"sf_second")
	assert_false(s.can_rewind(), "End Turn is a checkpoint")
	var u := s.state.hand.find(&"sf_undock_nudge")
	if u < 0:
		pass_test("Undock nudge not drawn this turn")
		return
	var before := s.state_hash()
	assert_true(s.apply(CombatAction.play_card(u, SatelliteFixture.sat_of(s).id)).ok())
	assert_true(s.can_rewind())
	s.rewind()
	assert_eq(s.state_hash(), before, "undo restores the satellite")
	assert_eq(SatelliteFixture.sat_of(s).source_id, &"sf_second", "and stops at the checkpoint")
	assert_false(s.can_rewind())
