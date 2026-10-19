extends GutTest
## N9 (R8, R9): OUTPUT_DOWN cuts output per stack (additive, half-up rounding, floored at 0),
## TIER_DOWN lowers the landing tier one step per stack (floored at WEAK) and so silences
## Perfect hooks, and the PARASITE alias stays OUTPUT_DOWN x2.

var _cfg: CampaignConfigData
var _atk: SliceData
var _null: SliceData
var _cls: ClassData
var _dummy: EnemyData


func before_each() -> void:
	_cfg = CombatFixture.config()
	_atk = CombatFixture.slice(&"n9_atk8", RC.SliceType.SHIM, 8)
	_null = CombatFixture.slice(&"n9_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	_cls = CombatFixture.operative_class(&"n9_class", 60, CombatFixture.wheel([_atk, _atk, _atk, _atk, _atk, _null]), [])
	_dummy = CombatFixture.enemy(&"n9_dummy", 500, CombatFixture.null_wheel())


func _session() -> CombatSession:
	var s := CombatSession.start(CombatFixture.resolver([_cls, _dummy]), _cls.id, [_dummy.id], 21)
	CombatFixture.land(s.state.player, 1)
	return s


func _damage_with(status: int, stacks: int) -> int:
	var s := _session()
	if stacks > 0:
		s.state.player.wheel.set_status(1, status, stacks)
	var r := s.apply(CombatAction.end_turn())
	var hits := CombatFixture.events_of(r, "damage")
	return int(hits[0]["amount"]) if not hits.is_empty() else 0


func test_output_down_is_additive_and_floors_at_zero() -> void:
	assert_eq(_damage_with(RC.Status.OUTPUT_DOWN, 0), 8)
	assert_eq(_damage_with(RC.Status.OUTPUT_DOWN, 1), 6)
	assert_eq(_damage_with(RC.Status.OUTPUT_DOWN, 2), 4, "additive, not 0.75 squared (4.5)")
	assert_eq(_damage_with(RC.Status.OUTPUT_DOWN, 3), 2)
	assert_eq(_damage_with(RC.Status.OUTPUT_DOWN, 4), 0)
	assert_eq(CombatResolver.output_down_factor(5, _cfg), 0.0, "never negative")


func test_output_down_rounding_is_half_up() -> void:
	# 5 x 0.75 = 3.75 -> 4; 5 x 0.5 = 2.5 -> 3; 5 x 0.25 = 1.25 -> 1.
	for pair in [[1, 4], [2, 3], [3, 1]]:
		assert_eq(roundi(5 * CombatResolver.output_down_factor(pair[0], _cfg)), pair[1], "%d stacks" % pair[0])


func test_parasite_reads_as_output_down_two_on_20_values() -> void:
	for base in range(1, 21):
		var halved := roundi(base * 0.5)
		var now := roundi(base * CombatResolver.output_down_factor(_cfg.parasite_output_down_stacks, _cfg))
		assert_eq(now, halved, "base %d" % base)


func test_tier_down_lowers_one_step_per_stack_floored_at_weak() -> void:
	assert_eq(CombatResolver.downgraded_tier(RC.PrecisionTier.PERFECT, 1), RC.PrecisionTier.GOOD)
	assert_eq(CombatResolver.downgraded_tier(RC.PrecisionTier.PERFECT, 2), RC.PrecisionTier.WEAK)
	assert_eq(CombatResolver.downgraded_tier(RC.PrecisionTier.GOOD, 1), RC.PrecisionTier.WEAK)
	assert_eq(CombatResolver.downgraded_tier(RC.PrecisionTier.WEAK, 3), RC.PrecisionTier.WEAK, "the floor")
	assert_eq(CombatResolver.downgraded_tier(RC.PrecisionTier.GOOD, 0), RC.PrecisionTier.GOOD)


func test_tier_down_changes_the_readout_and_the_output() -> void:
	var s := _session()
	assert_eq(s.resolver.pointer_readouts(s.state, s.state.player)[0]["tier"], RC.PrecisionTier.PERFECT)
	s.state.player.wheel.set_status(1, RC.Status.TIER_DOWN, 1)
	assert_eq(s.resolver.pointer_readouts(s.state, s.state.player)[0]["tier"], RC.PrecisionTier.GOOD)
	assert_eq(_damage_with(RC.Status.TIER_DOWN, 1), 8, "GOOD is full output")
	assert_eq(_damage_with(RC.Status.TIER_DOWN, 2), roundi(8 * _cfg.weak_multiplier), "two steps: WEAK")


func test_tier_down_silences_perfect_hooks() -> void:
	var hook := CombatFixture.triggered(RC.Trigger.ON_PERFECT, [CombatFixture.effect(RC.EffectType.GAIN_BLOCK, RC.EffectTarget.SELF, 5)])
	var hub := CombatFixture.hub(&"n9_hub", 0, [], hook)
	var cls := CombatFixture.operative_class(&"n9_hook_class", 60, CombatFixture.wheel([_atk, _atk, _atk, _atk, _atk, _null], hub), [])
	var res := CombatFixture.resolver([cls, _dummy, hub])
	var clean := CombatSession.start(res, cls.id, [_dummy.id], 3)
	CombatFixture.land(clean.state.player, 1)
	var with_hook := clean.apply(CombatAction.end_turn())
	var downed := CombatSession.start(res, cls.id, [_dummy.id], 3)
	CombatFixture.land(downed.state.player, 1)
	downed.state.player.wheel.set_status(1, RC.Status.TIER_DOWN, 1)
	var without := downed.apply(CombatAction.end_turn())
	assert_gt(CombatFixture.events_of(with_hook, "block").size(), 0, "the Perfect hook fires")
	assert_eq(CombatFixture.events_of(without, "block").size(), 0, "not on a downgraded landing")


func test_encrypted_absorbs_a_new_tier_down() -> void:
	var s := _session()
	var player := s.state.player
	player.wheel.set_status(1, RC.Status.ENCRYPTED, 1)
	var events: Array[Dictionary] = []
	s.resolver.fx.apply_status(player, 1, RC.Status.TIER_DOWN, events)
	assert_eq(player.wheel.stacks_of(1, RC.Status.TIER_DOWN), 0)
	assert_eq(events[0]["type"], "status_absorbed")


func test_tier_down_stacks_cap_and_enum_ints_stay() -> void:
	var s := _session()
	var player := s.state.player
	var events: Array[Dictionary] = []
	for i in _cfg.status_stack_cap + 2:
		s.resolver.fx.apply_status(player, 2, RC.Status.TIER_DOWN, events)
	assert_eq(player.wheel.stacks_of(2, RC.Status.TIER_DOWN), _cfg.status_stack_cap)
	assert_true(RC.Status.TIER_DOWN in RC.STORED_STATUSES)
	assert_eq(RC.Status.PARASITE, 4, "old enum ints stay")
	assert_eq(RC.Status.OUTPUT_DOWN, 5)
	assert_eq(RC.Status.TIER_DOWN, 6, "appended")
