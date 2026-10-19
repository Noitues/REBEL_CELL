extends GutTest
## N9: the preview equals the result with OUTPUT_DOWN / TIER_DOWN / CORRUPTED in play, UNDO
## refunds the exact (doubled) RAM, a respin checkpoint is not crossed, and a seeded replay
## matches. The cost and status paths consume no RNG.

var _atk: SliceData
var _null: SliceData
var _cls: ClassData
var _enemy: EnemyData
var _res: CombatResolver


func before_each() -> void:
	_atk = CombatFixture.slice(&"n9p_atk", RC.SliceType.SHIM, 8)
	_null = CombatFixture.slice(&"n9p_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var block: Array[EffectData] = [CombatFixture.effect(RC.EffectType.GAIN_BLOCK, RC.EffectTarget.SELF, 2)]
	var deck: Array[CardData] = [CombatFixture.card(&"n9p_c1", block, 1, RC.WheelTarget.OWN), CombatFixture.card(&"n9p_c2", block, 2, RC.WheelTarget.OWN)]
	_cls = CombatFixture.operative_class(&"n9p_class", 60, CombatFixture.wheel([_atk, _atk, _atk, _atk, _atk, _null]), deck)
	_enemy = CombatFixture.enemy(&"n9p_enemy", 500, CombatFixture.wheel([_atk, _atk, _atk, _atk, _atk, _null]))
	_res = CombatFixture.resolver([_cls, _enemy])


func _session(seed: int = 4242) -> CombatSession:
	var s := CombatSession.start(_res, _cls.id, [_enemy.id], seed)
	CombatFixture.land(s.state.player, 1)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 1)
	return s


func test_end_turn_preview_equals_result_for_each_status_stack_count() -> void:
	for status in [RC.Status.OUTPUT_DOWN, RC.Status.TIER_DOWN, RC.Status.CORRUPTED]:
		for stacks in 4:
			var s := _session()
			if stacks > 0:
				s.state.player.wheel.set_status(1, status, stacks)
				s.state.get_combatant(&"enemy_0").wheel.set_status(1, status, stacks)
			var preview := s.preview_end_turn()
			var result := s.apply(CombatAction.end_turn())
			assert_eq(preview.resolved_state.player.hp, result.resolved_state.player.hp, "%s x%d" % [RC.Status.keys()[status], stacks])
			assert_eq(preview.resolved_state.get_combatant(&"enemy_0").hp, result.resolved_state.get_combatant(&"enemy_0").hp)
			assert_eq(preview.resolved_state.ram, result.resolved_state.ram)


func test_action_preview_ram_equals_the_real_ram() -> void:
	var s := _session()
	s.state.player.wheel.set_status(1, RC.Status.CORRUPTED, 1)
	s.state.ram = 9
	for action in [CombatAction.play_card(0), CombatAction.play_card(1), CombatAction.respin(), CombatAction.nudge(&"enemy_0", 1)]:
		var preview := s.preview(action)
		assert_true(preview.ok(), preview.error)
		assert_eq(s.state.ram - preview.state.ram, RamCost.of_action(s.state, action, _res), "forecast == preview")


func test_undo_refunds_the_doubled_ram_exactly() -> void:
	var s := _session()
	s.state.player.wheel.set_status(1, RC.Status.CORRUPTED, 1)
	s._set_checkpoint()  # the rewind target holds the setup
	var before := s.state_hash()
	var ram := s.state.ram
	assert_true(s.apply(CombatAction.play_card(s.state.hand.find(&"n9p_c2"))).ok())
	assert_eq(ram - s.state.ram, 4)
	assert_true(s.rewind().ok())
	assert_eq(s.state.ram, ram)
	assert_eq(s.state_hash(), before)


func test_a_respin_checkpoint_is_not_crossed() -> void:
	var s := _session()
	s.state.player.wheel.set_status(1, RC.Status.CORRUPTED, 1)
	s.state.ram = 12
	var r := s.apply(CombatAction.respin())
	assert_true(r.ok(), r.error)
	assert_false(s.can_rewind(), "the respin is a random event: a checkpoint")
	assert_false(s.rewind().ok())


func test_cost_and_status_paths_consume_no_rng() -> void:
	var s := _session()
	s.state.player.wheel.set_status(1, RC.Status.CORRUPTED, 1)
	var rng := CombatFixture.rng(77)
	var snapshot := rng.state
	_res.apply(s.state, CombatAction.play_card(0), rng)
	_res.apply(s.state, CombatAction.nudge(&"enemy_0", 1), rng)
	assert_eq(rng.state, snapshot, "no draw")


func _record(seed: int) -> CombatSession:
	var s := _session(seed)
	s.state.player.wheel.set_status(1, RC.Status.CORRUPTED, 1)
	s.state.get_combatant(&"enemy_0").wheel.set_status(1, RC.Status.OUTPUT_DOWN, 2)
	s.state.get_combatant(&"enemy_0").wheel.set_status(1, RC.Status.TIER_DOWN, 1)
	for turn in 3:
		s.apply(CombatAction.play_card(0))
		s.apply(CombatAction.nudge(&"enemy_0", 1))
		s.apply(CombatAction.end_turn())
	return s


func test_same_seed_and_inputs_give_the_same_final_state() -> void:
	var a := _record(4242)
	var b := _record(4242)
	assert_ne(a.history.size(), 0)
	assert_eq(a.state_hash(), b.state_hash())
	assert_eq(a.state.ram, b.state.ram)
	assert_ne(_record(4243).state_hash(), a.state_hash(), "a different seed differs")
