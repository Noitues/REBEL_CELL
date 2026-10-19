extends GutTest
## Plan 2 Q19: the forecast. Known parts equal the executed result, random parts are marked
## unknown and never sampled, the forecast draws no RNG and changes no state, a respin keeps the
## needle where it is, a compound play is exact except for its random part, and a rewind leaves
## no stale forecast (the forecast is a pure function of state + RNG state).

const L = preload("res://tests/helpers/listener_fixture.gd")
const SEEDS := 200


func _arena(seed: int, listeners: Array[ListenerData] = [] as Array[ListenerData]) -> CombatSession:
	var s := L.session(listeners, {"seed": seed, "shims": [0, 2, 4], "prefix": "pu"})
	return s


func _hit_status_card() -> CardData:
	var dmg := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.TARGET_WHEEL, 3)
	var blk := CombatFixture.effect(RC.EffectType.GAIN_BLOCK, RC.EffectTarget.SELF, 2)
	var st := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.TARGET_WHEEL, 0, RC.RingScope.OUTER, 1.0, RC.Status.OVERCLOCKED, RC.SlicePick.RANDOM_NON_NULL)
	st.stacks = 1
	return CombatFixture.card(&"pu_combo", [dmg, blk, st], 1)


## An arena whose enemy wheel has live slices (so a random pick has candidates) and a combo card.
func _combo_session(seed: int) -> CombatSession:
	var null_slice := CombatFixture.slice(&"pu_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var shim := CombatFixture.slice(&"pu_shim", RC.SliceType.SHIM, 5)
	var combo := _hit_status_card()
	var deck: Array[CardData] = [combo, combo, combo, combo, combo]
	var cls := CombatFixture.operative_class(&"pu_class", 100, CombatFixture.wheel([shim, null_slice, shim, null_slice, shim, null_slice]), deck)
	var foe := CombatFixture.enemy(&"pu_foe", 300, CombatFixture.wheel([shim, null_slice, shim, null_slice, shim, null_slice]))
	var r := CombatFixture.resolver([cls, foe, combo, shim, null_slice])
	var s := CombatSession.start(r, cls.id, [foe.id], seed)
	var hand: Array[StringName] = [&"pu_combo"]
	s.state.hand = hand
	s.state.ram = 6
	s._set_checkpoint()
	return s


func test_nudges_forecast_equals_result_over_seeds() -> void:
	var zero_draw := true
	var unchanged := true
	for seed in SEEDS:
		var s := _arena(seed)
		var action := CombatAction.nudge(&"player", 1 if seed % 2 == 0 else -1)
		var hash_before := s.state_hash()
		var rng_before := s.rng.state
		var f := s.forecast(action)
		zero_draw = zero_draw and s.rng.state == rng_before
		unchanged = unchanged and s.state_hash() == hash_before
		assert_false(f.has_unknown(), "a nudge is fully known (seed %d)" % seed)
		var r := s.apply(action)
		if f.state().state_hash() != r.state.state_hash():
			fail_test("forecast != result at seed %d" % seed)
			return
	assert_true(zero_draw, "the forecast draws 0 numbers")
	assert_true(unchanged, "the forecast changes no state")


func test_deterministic_card_forecast_equals_result_over_seeds() -> void:
	for seed in SEEDS:
		var s := _arena(seed)
		L.stage(s, [L.ZAP], 6)
		var f := s.forecast(CombatAction.play_card(0))
		assert_false(f.has_unknown())
		var r := s.apply(CombatAction.play_card(0))
		if f.state().state_hash() != r.state.state_hash():
			fail_test("card forecast != result at seed %d" % seed)
			return


func test_respin_marks_unknown_and_keeps_the_needle() -> void:
	var s := _arena(7)
	L.stage(s, [], 6)
	var rot := s.state.player.wheel.rotation
	var rng_before := s.rng.state
	var hash_before := s.state_hash()
	var f := s.forecast(CombatAction.respin())
	assert_true(f.ok())
	assert_true(f.is_unknown(PreviewResult.RESPIN, &"player"))
	assert_eq(f.state().player.wheel.rotation, rot, "the ghost needle: the forecast does not move the wheel")
	assert_lt(f.state().ram, 6, "the RAM cost is known")
	assert_eq(s.rng.state, rng_before, "0 draws")
	assert_eq(s.state_hash(), hash_before, "no mutation")
	var r := s.apply(CombatAction.respin())
	assert_eq(r.state.ram, f.state().ram, "the known part (RAM) equals the result")
	assert_ne(r.state.player.wheel.rotation, rot, "the executed respin turns the wheel")


func test_compound_play_exact_except_random_part() -> void:
	for seed in [11, 12, 13, 14]:
		var s := _combo_session(seed)
		var rng_before := s.rng.state
		var f := s.forecast(CombatAction.play_card(0, &"enemy_0"))
		assert_true(f.ok(), f.result.error if f.result != null else "")
		assert_eq(s.rng.state, rng_before)
		assert_true(f.is_unknown(PreviewResult.RANDOM_SLICE, &"enemy_0"), "the status slice is random")
		var r := s.apply(CombatAction.play_card(0, &"enemy_0"))
		var fe := f.state().get_combatant(&"enemy_0")
		var re := r.state.get_combatant(&"enemy_0")
		assert_eq(fe.hp, re.hp, "damage is exact (seed %d)" % seed)
		assert_eq(fe.block, re.block)
		assert_eq(f.state().player.block, r.state.player.block, "block is exact")
		assert_eq(f.state().ram, r.state.ram)
		var forecast_statuses := 0
		for i in fe.wheel.slot_slice_ids.size():
			forecast_statuses += fe.wheel.stacks_of(i, RC.Status.OVERCLOCKED)
		assert_eq(forecast_statuses, 0, "the unknown status is not shown on any slot")
		var real_statuses := 0
		for i in re.wheel.slot_slice_ids.size():
			real_statuses += re.wheel.stacks_of(i, RC.Status.OVERCLOCKED)
		assert_eq(real_statuses, 1, "after execution the unknown part is resolved")


func test_listener_reaction_known_parts_stay_exact() -> void:
	var s := _arena(5, [L.listener(RC.Trigger.ON_RAM_SPENT, [L.block(3)])])
	L.stage(s, [], 6)
	var f := s.forecast(CombatAction.respin())
	var r := s.apply(CombatAction.respin())
	assert_eq(f.state().get_combatant(&"enemy_0").block, r.state.get_combatant(&"enemy_0").block, "the reaction's block is known")
	assert_true(f.is_unknown(PreviewResult.RESPIN, &"player"))
	for u in f.unknowns:
		assert_false(bool(u["listener"]), "the respin landing is the play's own random part, not the reaction's")


func test_rewind_leaves_no_stale_forecast() -> void:
	var s := _arena(9)
	L.stage(s, [], 6)
	var before := s.forecast(CombatAction.respin())
	s.apply(CombatAction.nudge(&"player", 1))
	var moved := s.forecast(CombatAction.respin())
	assert_ne(moved.state().state_hash(), before.state().state_hash(), "the forecast follows the state")
	s.rewind()
	var after := s.forecast(CombatAction.respin())
	assert_eq(after.state().state_hash(), before.state().state_hash(), "the forecast after a rewind is the one before the play")
	assert_eq(after.unknowns.size(), before.unknowns.size())
	# The random respin is a checkpoint: a rewind never crosses it, and the next forecast is of the new state.
	var rolled_from := s.forecast(CombatAction.respin()).state().state_hash()
	s.apply(CombatAction.respin())
	assert_false(s.can_rewind(), "a rewind never crosses the respin's checkpoint")
	assert_ne(s.forecast(CombatAction.respin()).state().state_hash(), rolled_from, "no stale forecast after the roll")
