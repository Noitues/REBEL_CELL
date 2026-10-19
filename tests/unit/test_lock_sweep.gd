extends GutTest
## Plan 2 N7 (full tier): 200 seeded fights with locks never deadlock and replay to the same hash.


func _fight(sd: int) -> CombatSession:
	var s := LockFixture.session({"seed": sd})
	for turn in 4:
		if s.state.is_over():
			break
		LockFixture.stage(s)
		s.apply(CombatAction.play_card(2 + (sd + turn) % 2))
		s.apply(CombatAction.nudge(s.state.player.id, 1))
		var r := s.apply(CombatAction.end_turn())
		assert_true(r.ok(), "End Turn is always legal (sd %d)" % sd)
	return s


func test_two_hundred_seeds_never_deadlock_and_are_stable() -> void:
	for sd in range(1000, 1200):
		var a := _fight(sd)
		var b := _fight(sd)
		assert_eq(a.state_hash(), b.state_hash(), "sd %d" % sd)
