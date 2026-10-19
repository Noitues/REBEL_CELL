extends GutTest
## Plan 2 N7: the lock records on a wheel (add, merge, sort, hash, save).

const NL := WheelState.LOCK_NUDGE
const RL := WheelState.LOCK_RESPIN


func _wheel() -> WheelState:
	return WheelState.from_wheel_data(CombatFixture.null_wheel())


func test_new_wheel_and_new_combat_have_no_locks() -> void:
	var w := _wheel()
	assert_false(w.is_locked(NL))
	assert_false(w.is_locked(RL))
	var s := LockFixture.session()
	for c in s.state.combatants_in_order():
		assert_true(c.wheel.locks.is_empty(), String(c.id))
	assert_true(s.state.pending_locks.is_empty())


func test_locks_are_per_wheel_and_per_kind() -> void:
	var a := _wheel()
	var b := _wheel()
	assert_true(a.add_lock(NL, &"citation", 1))
	assert_true(a.is_locked(NL))
	assert_false(a.is_locked(RL))
	assert_false(b.is_locked(NL))
	assert_eq(a.lock_sources(NL), ["citation"])
	assert_eq(a.lock_turns(NL), 1)


func test_two_locks_merge_to_the_larger_turns_and_sorted_sources() -> void:
	var w := _wheel()
	w.add_lock(NL, &"zeta", 1)
	w.add_lock(NL, &"alpha", 3)
	w.add_lock(NL, &"zeta", 2)
	assert_eq(w.lock_turns(NL), 3, "the larger wins, not the sum")
	assert_eq(w.lock_sources(NL), ["alpha", "zeta"], "sorted by content id")


func test_turns_below_one_leave_no_lock() -> void:
	var w := _wheel()
	assert_false(w.add_lock(NL, &"x", 0))
	assert_false(w.add_lock(RL, &"x", -2))
	assert_true(w.locks.is_empty())


func test_clear_locks_and_duplicate_are_independent() -> void:
	var w := _wheel()
	w.add_lock(NL, &"x", 2)
	var d := w.duplicate_state()
	w.clear_locks()
	assert_false(w.is_locked(NL))
	assert_true(d.is_locked(NL), "the copy keeps its own lock")
	d.add_lock(RL, &"y", 1)
	assert_false(w.is_locked(RL))


func test_state_hash_differs_with_a_lock_and_a_pending_lock() -> void:
	var s := LockFixture.session()
	var base := s.state_hash()
	var locked := s.state.duplicate_state()
	locked.player.wheel.add_lock(NL, &"x", 1)
	assert_ne(locked.state_hash(), base)
	var queued := s.state.duplicate_state()
	queued.pending_locks.append({"wheel": "enemy_0", "kind": "nudge", "source": "x", "turns": 1})
	assert_ne(queued.state_hash(), base)
	assert_eq(s.state.duplicate_state().state_hash(), base, "a copy hashes the same")


func test_save_round_trip_keeps_locks_and_pending() -> void:
	var s := LockFixture.session()
	s.state.player.wheel.add_lock(NL, &"b", 2)
	s.state.player.wheel.add_lock(NL, &"a", 1)
	s.state.get_combatant(&"enemy_0").wheel.add_lock(RL, &"c", 1)
	s.state.pending_locks.append({"wheel": "enemy_0", "kind": "nudge", "source": "x", "turns": 2})
	var d := s.state.to_dict()
	var back := CombatState.from_dict(JSON.parse_string(JSON.stringify(d)))
	assert_eq(back.state_hash(), s.state.state_hash())
	assert_eq(back.player.wheel.lock_turns(NL), 2)
	assert_eq(back.player.wheel.lock_sources(NL), ["a", "b"])
	assert_true(back.get_combatant(&"enemy_0").wheel.is_locked(RL))
	assert_eq(back.pending_locks.size(), 1)


func test_a_save_without_lock_fields_loads_with_no_locks() -> void:
	var s := LockFixture.session()
	var d := s.state.to_dict()
	assert_false(d.has("pending_locks"), "absent when empty: old hashes and saves are unchanged")
	assert_false((d["player"]["wheel"] as Dictionary).has("locks"))
	var back := CombatState.from_dict(JSON.parse_string(JSON.stringify(d)))
	assert_true(back.player.wheel.locks.is_empty())
	assert_true(back.pending_locks.is_empty())
