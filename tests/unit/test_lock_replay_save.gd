extends GutTest
## Plan 2 N7: seeded replay, rewind and save with locks; preview == result on 50 seeded cases.


func _play(s: CombatSession) -> void:
	s.apply(CombatAction.play_card(3))  # lock the enemy's respins
	s.apply(CombatAction.end_turn())    # the enemy slice queues a nudge lock on the operative
	s.apply(CombatAction.play_card(0))  # a nudge card still works
	s.apply(CombatAction.end_turn())


func test_seeded_replay_with_locks_gives_the_same_hash() -> void:
	var s := LockFixture.session({"seed": 4242})
	var setup_hash_before := s.state_hash()
	assert_ne(setup_hash_before, 0)
	_play(s)
	var replay_session := LockFixture.session({"seed": 4242})
	for a in s.history:
		replay_session.apply(a)
	assert_eq(replay_session.state_hash(), s.state_hash())


func test_rewind_restores_a_lock_placed_this_turn_and_never_crosses_the_checkpoint() -> void:
	var s := LockFixture.session({"enemy_lock": -1})
	s.apply(CombatAction.play_card(3))
	assert_true(s.state.get_combatant(&"enemy_0").wheel.is_locked(WheelState.LOCK_RESPIN))
	assert_true(s.can_rewind())
	s.rewind()
	assert_false(s.state.get_combatant(&"enemy_0").wheel.is_locked(WheelState.LOCK_RESPIN), "undo is clean")
	assert_false(s.can_rewind(), "nothing before the checkpoint")
	# A random event (the RAM respin) makes a checkpoint that a lock placed before it cannot be undone across.
	s.apply(CombatAction.play_card(2))
	s.apply(CombatAction.respin())
	assert_false(s.can_rewind())
	assert_true(s.state.get_combatant(&"enemy_0").wheel.is_locked(WheelState.LOCK_NUDGE))


func test_a_session_saved_with_locks_loads_equal() -> void:
	var s := LockFixture.session()
	s.apply(CombatAction.play_card(2))
	var d: Dictionary = JSON.parse_string(JSON.stringify(s.state.to_dict()))
	assert_eq(CombatState.from_dict(d).state_hash(), s.state_hash())


func test_preview_equals_result_on_fifty_seeded_cases() -> void:
	for sd in range(2000, 2050):
		var s := LockFixture.session({"seed": sd})
		var pick := sd % 3
		var action := CombatAction.end_turn() if pick == 2 else CombatAction.play_card(2 + pick)
		var preview := s.preview(action) if pick < 2 else s.preview_end_turn()
		var r := s.apply(action)
		assert_true(r.ok(), r.error)
		var compared := r.state if pick < 2 else r.resolved_state
		assert_eq(preview.state.state_hash(), compared.state_hash(), "sd %d" % sd)
