extends GutTest
## Plan 2 N6: undo (rewind) reverses listener effects and fire counters exactly, never
## crosses a checkpoint, leaves nothing queued, and a redo matches the first result.

const L = preload("res://tests/helpers/listener_fixture.gd")


func _session() -> CombatSession:
	var listeners: Array[ListenerData] = [L.listener(RC.Trigger.ON_NUDGE, [L.hit(2), L.block(1)], 3, 4),
		L.listener(RC.Trigger.ON_CARD_PLAYED, [L.block(2)], 2),
		L.listener(RC.Trigger.ON_RAM_SPENT, [L.hit(1)], 5)]
	var s := L.session(listeners)
	L.stage(s, [L.ZAP, L.ZAP, L.FREE], 12)
	return s


func test_undo_nudge_reverts_listener_effects() -> void:
	var s := _session()
	var h0 := s.state.state_hash()
	var r := s.apply(CombatAction.nudge(&"player", 1))
	assert_gt(L.fires(r).size(), 0)
	assert_ne(s.state.state_hash(), h0)
	s.rewind()
	assert_eq(s.state.state_hash(), h0, "state hash equals the pre-nudge hash")
	assert_true(s.state.get_combatant(&"enemy_0").listener_fires_turn.is_empty())


func test_undo_card_reverts_counter_so_a_replay_fires_again() -> void:
	var s := _session()
	var first := s.apply(CombatAction.play_card(0))
	assert_eq(L.combat_fires(s.state, 1), 1)
	s.rewind()
	assert_eq(L.combat_fires(s.state, 1), 0, "counter back to 0")
	var again := s.apply(CombatAction.play_card(0))
	assert_eq(L.fires(again).size(), L.fires(first).size(), "fires again")
	assert_eq(again.state.state_hash(), first.state.state_hash())


func test_undo_stack_of_five_actions_returns_to_checkpoint_hash() -> void:
	var s := _session()
	var h0 := s.state.state_hash()
	var actions := [CombatAction.nudge(&"player", 1), CombatAction.play_card(0), CombatAction.nudge(&"enemy_0", -1),
		CombatAction.play_card(0), CombatAction.nudge(&"player", 1)]
	for a in actions:
		assert_true(s.apply(a).ok())
	for i in actions.size():
		s.rewind()
	assert_eq(s.state.state_hash(), h0)
	assert_false(s.can_rewind())


func test_rewind_cannot_cross_checkpoint_with_listener_fires() -> void:
	var s := _session()
	s.apply(CombatAction.nudge(&"player", 1))
	var fired := L.combat_fires(s.state, 0)
	assert_eq(fired, 1)
	assert_true(s.apply(CombatAction.respin()).ok(), "a respin draws RNG: a checkpoint")
	var after_respin := s.state.state_hash()
	assert_false(s.can_rewind(), "nothing to undo past the respin")
	s.rewind()
	assert_eq(s.state.state_hash(), after_respin)
	assert_eq(L.combat_fires(s.state, 0), fired, "the earlier fire stays")


func test_listener_fires_during_staging_do_not_leak_into_resolve() -> void:
	var a := _session()
	var b := _session()
	a.apply(CombatAction.nudge(&"player", 1))
	a.apply(CombatAction.play_card(0))
	a.rewind()
	a.rewind()
	var ra := a.apply(CombatAction.end_turn())
	var rb := b.apply(CombatAction.end_turn())
	assert_eq(ra.state.state_hash(), rb.state.state_hash(), "staged then undone == never staged")
	assert_eq(L.fires(ra).size(), L.fires(rb).size())


func test_redo_after_undo_matches_original_result() -> void:
	var s := _session()
	var first := s.apply(CombatAction.nudge(&"player", 1))
	var second := s.apply(CombatAction.play_card(0))
	var h := s.state.state_hash()
	s.rewind()
	var redo := s.apply(CombatAction.play_card(0))
	assert_eq(redo.state.state_hash(), h)
	assert_eq(L.fires(redo).size(), L.fires(second).size())
	assert_gt(L.fires(first).size(), 0)
