extends GutTest
## Plan 2 N7: LOCK_* effects, the turn lifecycle (Q31 and the two rulings), preview == result.

const NL := WheelState.LOCK_NUDGE
const RL := WheelState.LOCK_RESPIN


func test_a_players_lock_card_applies_to_the_enemy_wheel_at_once() -> void:
	var s := LockFixture.session({"enemy_lock": -1})
	var r := s.apply(CombatAction.play_card(2))
	assert_true(r.ok(), r.error)
	var e := s.state.get_combatant(&"enemy_0")
	assert_true(e.wheel.is_locked(NL))
	assert_eq(e.wheel.lock_sources(NL), [String(LockFixture.LOCK_NUDGE_CARD)])
	assert_false(s.state.player.wheel.is_locked(NL))
	assert_eq(CombatFixture.events_of(r, "lock").size(), 1)


func test_locks_are_removed_at_end_of_turn() -> void:
	var s := LockFixture.session({"enemy_lock": -1})
	s.apply(CombatAction.play_card(2))
	s.apply(CombatAction.end_turn())
	assert_true(s.state.get_combatant(&"enemy_0").wheel.locks.is_empty())
	assert_true(s.state.player.wheel.locks.is_empty())


func test_an_enemy_lock_at_resolve_is_queued_and_holds_the_next_turn_only() -> void:
	var s := LockFixture.session()
	var preview := s.preview_end_turn()
	assert_eq(preview.state.pending_locks.size(), 1, "the preview shows the queued lock")
	assert_true(preview.state.player.wheel.locks.is_empty(), "not yet in force")
	var r := s.apply(CombatAction.end_turn())
	assert_true(r.ok(), r.error)
	assert_eq(r.resolved_state.pending_locks, preview.state.pending_locks, "preview == result")
	assert_true(s.state.pending_locks.is_empty(), "applied at the start of the turn")
	assert_true(s.state.player.wheel.is_locked(NL), "locked for the player's next turn")
	assert_eq(s.state.player.wheel.lock_sources(NL), [String(LockFixture.SLICE_SOURCE)])
	assert_eq(s.resolver.validate_action(s.state, CombatAction.nudge(s.state.player.id, 1)), CombatResolver.NUDGE_LOCKED)
	# It clears at the end of that turn (this turn's enemy slice queues a fresh one).
	LockFixture.stage(s)
	s.state.get_combatant(&"enemy_0").wheel.slot_slice_ids[0] = &"lk_null"
	s.apply(CombatAction.end_turn())
	assert_true(s.state.player.wheel.locks.is_empty(), "gone the turn after")


func test_the_queued_lock_lands_after_the_start_of_turn_spin() -> void:
	var s := LockFixture.session({"enemy_lock": RC.EffectType.LOCK_RESPIN})
	var r := s.apply(CombatAction.end_turn())
	var events := r.events
	var spin_at := CombatFixture.index_of_event(r, "respin", "target", s.state.player.id)
	var lock_at := CombatFixture.index_of_event(r, "lock", "target", s.state.player.id)
	assert_gt(spin_at, -1)
	assert_gt(lock_at, spin_at, "the start-of-turn respin is never blocked")
	assert_true(events.size() > 0)
	assert_true(s.state.player.wheel.is_locked(RL))


func test_preview_of_a_lock_card_equals_the_result() -> void:
	var s := LockFixture.session({"enemy_lock": -1})
	var preview := s.preview(CombatAction.play_card(3))
	var r := s.apply(CombatAction.play_card(3))
	assert_eq(preview.state.state_hash(), r.state.state_hash())
	assert_true(r.state.get_combatant(&"enemy_0").wheel.is_locked(RL))


func test_a_lock_of_zero_turns_places_nothing() -> void:
	var s := LockFixture.session({"enemy_lock": -1})
	var events: Array[Dictionary] = []
	s.resolver.fx.place_lock(s.state, s.state.get_combatant(&"enemy_0"), NL, &"x", 0, events)
	assert_true(s.state.get_combatant(&"enemy_0").wheel.locks.is_empty())
	assert_true(events.is_empty())


func test_two_queued_locks_from_one_source_merge_by_max_turns() -> void:
	var s := LockFixture.session({"enemy_lock": -1})
	s.state.phase = CombatState.Phase.RESOLVE
	var events: Array[Dictionary] = []
	var p := s.state.player
	s.resolver.fx.place_lock(s.state, p, NL, &"b", 1, events)
	s.resolver.fx.place_lock(s.state, p, NL, &"b", 3, events)
	s.resolver.fx.place_lock(s.state, p, NL, &"a", 1, events)
	assert_eq(s.state.pending_locks.size(), 2)
	assert_eq(s.state.pending_locks[0]["source"], "a", "sorted by source id")
	assert_eq(s.state.pending_locks[1]["turns"], 3)


func test_freeze_alone_persists_past_the_end_of_turn_and_is_spent_at_start() -> void:
	var s := LockFixture.session({"enemy_lock": -1})
	var e := s.state.get_combatant(&"enemy_0")
	e.wheel.frozen = true
	e.wheel.add_lock(NL, &"x", 1)
	s.resolver.end_turn(s.state, [])
	assert_true(e.wheel.frozen, "Freeze survives end of turn")
	assert_true(e.wheel.locks.is_empty())
	var before := e.wheel.rotation
	s.resolver.start_turn(s.state, s.rng, [])
	assert_eq(e.wheel.rotation, before, "the frozen wheel skipped its initial spin")
	assert_false(e.wheel.frozen, "removed after the spin it prevented")


func test_a_lock_survives_a_boss_phase_swap() -> void:
	var s := LockFixture.session({"enemy_lock": -1})
	var e := s.state.get_combatant(&"enemy_0")
	e.wheel.add_lock(NL, &"x", 1)
	s.resolver._apply_wheel_override(e, CombatFixture.null_wheel(), [])
	assert_true(e.wheel.is_locked(NL))


func test_locks_are_cleared_when_the_combat_ends() -> void:
	var s := LockFixture.session({"enemy_lock": -1})
	s.state.player.wheel.add_lock(NL, &"x", 1)
	s.state.pending_locks.append({"wheel": "enemy_0", "kind": "nudge", "source": "x", "turns": 1})
	s.state.get_combatant(&"enemy_0").hp = 0
	s.resolver._check_outcome(s.state, [])
	assert_true(s.state.is_over())
	assert_true(s.state.player.wheel.locks.is_empty())
	assert_true(s.state.pending_locks.is_empty())
