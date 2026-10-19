extends GutTest
## Plan 2 N8: the state hash carries the stacks in RC.Status order (never Dictionary order);
## seeded fights with stacks replay to the same hash; applies and cleanses draw no RNG;
## rewind restores the checkpoint's stacks and never crosses it.


func _session() -> CombatSession:
	return StatusSaveFixture.start()


func test_same_seed_same_inputs_same_state_hash_with_stacks() -> void:
	var hashes: Array = []
	for run in 2:
		var s := _session()
		var p := s.state.player
		p.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 2)
		p.wheel.set_status(3, RC.Status.CORRUPTED, 1)
		s.state.get_combatant(&"enemy_0").wheel.set_status(0, RC.Status.OUTPUT_DOWN, 3)
		var seen: Array = []
		for turn in 6:
			if s.state.is_over():
				break
			var idx := s.state.hand.find(&"ssf_overdrive")
			if idx >= 0 and s.state.ram >= 1:
				s.apply(CombatAction.play_card(idx))
			s.apply(CombatAction.end_turn())
			seen.append(s.state_hash())
		hashes.append(seen)
	assert_eq(hashes[0], hashes[1], "a 6-turn scripted fight with stacks replays exactly")


func test_hash_differs_when_stack_count_differs() -> void:
	var a := _session()
	var b := _session()
	a.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 1)
	b.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 2)
	assert_ne(a.state_hash(), b.state_hash())


func test_hash_independent_of_dict_insertion_order() -> void:
	var a := _session()
	var b := _session()
	var cap := CombatFixture.config().status_stack_cap
	a.state.player.wheel.add_stacks(2, RC.Status.CORRUPTED, 1, cap)
	a.state.player.wheel.add_stacks(2, RC.Status.OUTPUT_DOWN, 2, cap)
	b.state.player.wheel.add_stacks(2, RC.Status.OUTPUT_DOWN, 2, cap)
	b.state.player.wheel.add_stacks(2, RC.Status.CORRUPTED, 1, cap)
	assert_eq(a.state_hash(), b.state_hash())
	assert_eq(JSON.stringify(a.state.to_dict(), "", false), JSON.stringify(b.state.to_dict(), "", false), "even unsorted JSON is the same: keys go out in RC.Status order")


func test_apply_status_uses_no_global_randi() -> void:
	var s := _session()
	var rng_before := s.rng.state
	var events: Array[Dictionary] = []
	var fx := s.resolver.fx
	fx.apply_status(s.state.player, 1, RC.Status.OUTPUT_DOWN, events, 2)
	fx.apply_status(s.state.player, 1, RC.Status.ENCRYPTED, events)
	fx.apply_status(s.state.player, 1, RC.Status.CORRUPTED, events)
	fx.cleanse(s.state.player, 1, events, RC.CleanseMode.ONE_STACK)
	fx.cleanse(s.state.player, 1, events)
	assert_eq(s.rng.state, rng_before, "stacking and cleansing draw nothing")


func test_random_non_null_pick_tiebreak_by_slice_index() -> void:
	var picks: Array = []
	for run in 2:
		var s := _session()
		var e := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.SELF, 3, RC.RingScope.OUTER, 1.0, RC.Status.CORRUPTED, RC.SlicePick.RANDOM_NON_NULL)
		e.stacks = 2
		var events: Array[Dictionary] = []
		var rng := CombatFixture.rng(4242)
		s.resolver.fx.apply_effect(s.state, e, {"owner": s.state.player}, rng, events)
		picks.append(s.state.player.wheel.copy_stacks())
	assert_eq(picks[0], picks[1], "same seed, same slots, same stacks")
	assert_eq((picks[0] as Array).filter(func(d: Dictionary) -> bool: return not d.is_empty()).size(), 3, "three distinct slots, two stacks each")


func test_rewind_restores_stacks_to_checkpoint() -> void:
	var s := _session()
	s.state.player.wheel.set_status(2, RC.Status.OUTPUT_DOWN, 2)
	s._set_checkpoint()
	var at_checkpoint := s.state_hash()
	var r := s.apply(CombatAction.play_card(s.state.hand.find(&"ssf_overdrive")))
	assert_true(r.ok(), r.error)
	assert_eq(s.state.player.wheel.slice_stacks[1], {RC.Status.OVERCLOCKED: 1})
	s.rewind()
	assert_eq(s.state_hash(), at_checkpoint, "undo is clean")
	assert_eq(s.state.player.wheel.slice_stacks[2], {RC.Status.OUTPUT_DOWN: 2})


func test_rewind_cannot_cross_checkpoint_with_stack_apply() -> void:
	var s := _session()
	s.apply(CombatAction.play_card(s.state.hand.find(&"ssf_overdrive")))
	s.apply(CombatAction.end_turn())  # the respin is random: a checkpoint
	assert_false(s.can_rewind(), "nothing to undo past the respin")
	var r := s.rewind()
	assert_ne(r.error, "")
	assert_eq(s.state.player.wheel.count_status(RC.Status.CORRUPTED) + s.state.player.wheel.count_status(RC.Status.OVERCLOCKED), 1, "the stacks stay")


func test_staged_cleanse_undo_is_clean() -> void:
	var e := CombatFixture.effect(RC.EffectType.CLEANSE, RC.EffectTarget.OWN_WHEEL)
	var cleanse := CombatFixture.card(&"sd_cleanse", [e], 0, RC.WheelTarget.OWN)
	var atk := CombatFixture.slice(&"sd_atk", RC.SliceType.SHIM, 4)
	var cls := CombatFixture.operative_class(&"sd_class", 50, CombatFixture.wheel([atk, atk, atk, atk, atk, atk]), [cleanse, cleanse])
	var dummy := CombatFixture.enemy(&"sd_dummy", 50, CombatFixture.null_wheel())
	var s := CombatSession.start(CombatFixture.resolver([cls, dummy, cleanse]), cls.id, [dummy.id], 17)
	CombatFixture.land(s.state.player, 1)
	s.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 4)
	s._set_checkpoint()
	var before := s.state_hash()
	s.apply(CombatAction.play_card(0))
	assert_eq(s.state.player.wheel.slice_stacks[1], {})
	s.rewind()
	assert_eq(s.state_hash(), before)


func test_snapshot_restore_roundtrip_preserves_stacks() -> void:
	var s := _session()
	s.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 3)
	s.state.get_combatant(&"enemy_0").wheel.set_status(4, RC.Status.ENCRYPTED, 2)
	var copy := s.state.duplicate_state()
	assert_eq(copy.state_hash(), s.state.state_hash())
	copy.player.wheel.add_stacks(1, RC.Status.OUTPUT_DOWN, 1, 99)
	assert_eq(s.state.player.wheel.stacks_of(1, RC.Status.OUTPUT_DOWN), 3, "a snapshot owns its stacks (deep copy)")
	var back := CombatState.from_dict(JSON.parse_string(JSON.stringify(s.state.to_dict())))
	assert_eq(back.state_hash(), s.state.state_hash(), "through JSON and back")
	assert_eq(back.player.wheel.slice_stacks[1], {RC.Status.OUTPUT_DOWN: 3}, "keys come back as ints")
