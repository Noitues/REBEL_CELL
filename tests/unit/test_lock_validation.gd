extends GutTest
## Plan 2 N7: a locked action is refused with a named reason and costs nothing.

const NL := WheelState.LOCK_NUDGE
const RL := WheelState.LOCK_RESPIN


func _player(s: CombatSession) -> StringName:
	return s.state.player.id


func test_locked_nudge_is_refused_free_and_paid_with_the_source_named() -> void:
	var s := LockFixture.session()
	s.state.player.wheel.add_lock(NL, &"citation", 1)
	var act := CombatAction.nudge(_player(s), 1)
	assert_eq(s.resolver.validate_action(s.state, act), CombatResolver.NUDGE_LOCKED)
	var info := s.resolver.lock_refusal(s.state, act)
	assert_eq(info["code"], "NUDGE_LOCKED")
	assert_eq(info["sources"], ["citation"])
	s.state.free_nudges = 0
	assert_eq(s.resolver.validate_action(s.state, act), CombatResolver.NUDGE_LOCKED, "a paid nudge too")


func test_a_refused_nudge_costs_nothing_and_leaves_the_free_nudge() -> void:
	var s := LockFixture.session()
	s.state.player.wheel.add_lock(NL, &"x", 1)
	var hash_before := s.state_hash()
	var hist := s.history.size()
	var r := s.apply(CombatAction.nudge(_player(s), 1))
	assert_false(r.ok())
	assert_eq(s.state.ram, 6)
	assert_eq(s.state.free_nudges, 1)
	assert_eq(s.state_hash(), hash_before)
	assert_eq(s.history.size(), hist, "the refusal is not in the undo stack")


func test_nudge_cards_still_work_under_a_nudge_lock() -> void:
	var s := LockFixture.session()
	s.state.player.wheel.add_lock(NL, &"x", 1)
	var before := s.state.player.wheel.rotation
	var r := s.apply(CombatAction.play_card(0))
	assert_true(r.ok(), r.error)
	assert_ne(s.state.player.wheel.rotation, before, "the card moved the wheel")


func test_respin_card_and_ram_respin_are_refused_under_a_respin_lock() -> void:
	var s := LockFixture.session()
	s.state.player.wheel.add_lock(RL, &"x", 1)
	assert_eq(s.resolver.validate_action(s.state, CombatAction.play_card(1)), CombatResolver.RESPIN_LOCKED)
	var r := s.apply(CombatAction.respin())
	assert_false(r.ok())
	assert_eq(r.error, CombatResolver.RESPIN_LOCKED)
	assert_eq(s.state.ram, 6, "no RAM spent")
	assert_eq(s.resolver.lock_refusal(s.state, CombatAction.respin())["code"], "RESPIN_LOCKED")


func test_the_start_of_turn_respin_is_never_blocked() -> void:
	var s := LockFixture.session()
	s.state.player.wheel.add_lock(RL, &"x", 1)
	var events: Array[Dictionary] = []
	var before := s.state.player.wheel.rotation
	s.resolver.start_turn(s.state, s.rng, events)
	assert_ne(s.state.player.wheel.rotation, before)
	var respins := events.filter(func(e: Dictionary) -> bool: return e.get("type", "") == "respin" and e.get("target", &"") == s.state.player.id)
	assert_eq(respins.size(), 1)


func test_spin_flip_freeze_and_nudge_locks_do_not_touch_other_actions() -> void:
	var s := LockFixture.session()
	s.state.player.wheel.add_lock(NL, &"x", 1)
	s.state.player.wheel.add_lock(RL, &"y", 1)
	# The nudge card (index 0) and a plain target action are not lock business.
	assert_eq(s.resolver.validate_action(s.state, CombatAction.play_card(0)), "")
	assert_eq(s.resolver.validate_action(s.state, CombatAction.target(&"enemy_0")), "")
	assert_eq(s.resolver.validate_action(s.state, CombatAction.end_turn()), "")
	var spin := CombatFixture.card(&"lk_spin", [CombatFixture.effect(RC.EffectType.SPIN, RC.EffectTarget.OWN_WHEEL, 1, RC.RingScope.WHOLE_WHEEL)], 0, RC.WheelTarget.OWN)
	var flip := CombatFixture.card(&"lk_flip", [CombatFixture.effect(RC.EffectType.FLIP, RC.EffectTarget.OWN_WHEEL, 0, RC.RingScope.WHOLE_WHEEL)], 0, RC.WheelTarget.OWN)
	var freeze := CombatFixture.card(&"lk_freeze", [CombatFixture.effect(RC.EffectType.FREEZE, RC.EffectTarget.OWN_WHEEL, 0, RC.RingScope.WHOLE_WHEEL)], 0, RC.WheelTarget.OWN)
	var res := CombatFixture.resolver([spin, flip, freeze])
	s.state.hand = [spin.id, flip.id, freeze.id]
	for i in 3:
		assert_eq(res.validate_action(s.state, CombatAction.play_card(i)), "", str(i))


func test_the_lock_is_named_before_missing_ram() -> void:
	var s := LockFixture.session()
	s.state.player.wheel.add_lock(NL, &"x", 1)
	s.state.player.wheel.add_lock(RL, &"x", 1)
	s.state.free_nudges = 0
	s.state.ram = 0
	assert_eq(s.resolver.validate_action(s.state, CombatAction.nudge(_player(s), 1)), CombatResolver.NUDGE_LOCKED)
	assert_eq(s.resolver.validate_action(s.state, CombatAction.respin()), CombatResolver.RESPIN_LOCKED)


func test_a_lock_on_an_enemy_wheel_blocks_the_players_nudge_of_it_only() -> void:
	var s := LockFixture.session()
	s.state.get_combatant(&"enemy_0").wheel.add_lock(NL, &"x", 1)
	assert_eq(s.resolver.validate_action(s.state, CombatAction.nudge(&"enemy_0", 1)), CombatResolver.NUDGE_LOCKED)
	assert_eq(s.resolver.validate_action(s.state, CombatAction.nudge(_player(s), 1)), "", "the operative's own wheel is free")


func test_the_refusal_texts_are_us_english_and_in_the_text_table() -> void:
	var csv := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for key in [CombatResolver.NUDGE_LOCKED, CombatResolver.RESPIN_LOCKED, "NUDGE LOCKED", "RESPIN LOCKED"]:
		assert_true(csv.contains("\n" + key + ","), key)
