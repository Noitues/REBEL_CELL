extends GutTest
## Rewind restores exactly and cannot cross a checkpoint; checkpoints survive
## save/load (M1 acceptance, GDD 2.10).

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


func _spin_card_index(session: CombatSession) -> int:
	for id in [&"jolt", &"brute_spin"]:
		var i := session.state.hand.find(id)
		if i >= 0:
			return i
	return -1


func test_rewind_restores_the_exact_previous_state() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"collections_agent"], 5, &"rank:1")
	var h0 := s.state_hash()
	assert_false(s.can_rewind(), "nothing to undo right after the start-of-turn checkpoint")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	var h1 := s.state_hash()
	s.apply(CombatAction.play_card(_spin_card_index(s), &"enemy_0"))
	var h2 := s.state_hash()
	assert_ne(h0, h1)
	assert_ne(h1, h2)
	assert_true(s.can_rewind())
	assert_true(s.rewind().ok())
	assert_eq(s.state_hash(), h1, "one action undone")
	assert_true(s.rewind().ok())
	assert_eq(s.state_hash(), h0, "back at the checkpoint")
	assert_eq(s.history.size(), 0)


func test_rewind_cannot_cross_the_start_of_turn_checkpoint() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"collections_agent"], 5, &"rank:1")
	var r := s.rewind()
	assert_false(r.ok())
	assert_string_contains(r.error, "checkpoint")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.turn, 2)
	assert_false(s.can_rewind(), "the respin is a random event: new checkpoint")
	assert_false(s.rewind().ok())
	assert_eq(s.state.turn, 2, "still turn 2")


func test_random_card_effect_creates_a_checkpoint_mid_turn() -> void:
	var respin := CombatFixture.card(&"rw_respin", [CombatFixture.effect(RC.EffectType.RESPIN, RC.EffectTarget.OWN_WHEEL, 0, RC.RingScope.WHOLE_WHEEL)], 0, RC.WheelTarget.OWN)
	var deck: Array[CardData] = [respin, respin, respin]
	var cls := CombatFixture.operative_class(&"rw_class", 60, CombatFixture.miss_wheel(), deck)
	var dummy := CombatFixture.enemy(&"rw_dummy", 50, CombatFixture.miss_wheel())
	var s := CombatSession.start(CombatFixture.resolver([cls, dummy]), cls.id, [dummy.id], 8)
	s.apply(CombatAction.nudge(&"player", 1))
	assert_true(s.can_rewind())
	var before_respin := s.state_hash()
	s.apply(CombatAction.play_card(0))
	assert_false(s.can_rewind(), "respin consumed RNG: checkpoint moved here")
	assert_ne(s.state_hash(), before_respin)
	s.apply(CombatAction.nudge(&"player", -1))
	assert_true(s.rewind().ok())
	assert_false(s.can_rewind(), "cannot undo the respin itself")


func test_rewind_replays_the_remaining_actions_in_order() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"compliance_officer"], 13, &"rank:1")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	s.apply(CombatAction.target(&"enemy_0"))
	var h_after_two := 0
	var replica := CombatSession.start(_resolver, &"breaker", [&"compliance_officer"], 13, &"rank:1")
	replica.apply(CombatAction.nudge(&"enemy_0", 1))
	replica.apply(CombatAction.nudge(&"enemy_0", 1))
	h_after_two = replica.state_hash()
	s.rewind()
	assert_eq(s.state_hash(), h_after_two)
	assert_eq(s.actions_since_checkpoint.size(), 2)


func test_checkpoints_survive_save_and_load() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"collections_agent"], 5, &"rank:1")
	var h0 := s.state_hash()
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	var h1 := s.state_hash()
	s.apply(CombatAction.play_card(_spin_card_index(s), &"enemy_0"))
	var h2 := s.state_hash()
	var json := JSON.stringify(s.to_dict())
	var loaded := CombatSession.from_dict(_resolver, JSON.parse_string(json))
	assert_eq(loaded.state_hash(), h2, "live state round-trips")
	assert_eq(loaded.checkpoint_state.state_hash(), s.checkpoint_state.state_hash(), "checkpoint round-trips")
	assert_eq(loaded.rng.state, s.rng.state)
	assert_eq(loaded.actions_since_checkpoint.size(), 2)
	assert_true(loaded.rewind().ok())
	assert_eq(loaded.state_hash(), h1)
	assert_true(loaded.rewind().ok())
	assert_eq(loaded.state_hash(), h0)
	assert_false(loaded.rewind().ok(), "still cannot cross the checkpoint after a reload")


func test_reloading_cannot_reroll_the_next_respin() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"dosage_dispenser"], 99, &"rank:1")
	var loaded := CombatSession.from_dict(_resolver, JSON.parse_string(JSON.stringify(s.to_dict())))
	s.apply(CombatAction.end_turn())
	loaded.apply(CombatAction.end_turn())
	assert_eq(loaded.state_hash(), s.state_hash(), "same random outcome after a reload")
