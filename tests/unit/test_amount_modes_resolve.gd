extends GutTest
## Plan 2 N1 (R2, R5) on the resolver path: enemy slices with FLAT / PERCENT amounts resolve
## the same in preview and for real, PERCENT skips the tier factor but keeps the precision
## multiplier, corruption picks stay on the combat stream, replay and rewind still hold.

const TIER_FACTORS: Array[float] = [1.0, 1.3, 1.69, 2.2]
const SEED := 4242

var _null: SliceData
var _heal10: SliceData
var _block_pct: SliceData
var _shield_pct: SliceData
var _heal_pct: SliceData
var _infect_pct: SliceData


func before_all() -> void:
	_null = CombatFixture.slice(&"amr_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	_heal10 = CombatFixture.slice(&"amr_heal10", RC.SliceType.HOTFIX, 10, RC.TargetRule.SELF)
	_block_pct = _percent(CombatFixture.slice(&"amr_block5p", RC.SliceType.DEFRAG, 5, RC.TargetRule.SELF))
	_shield_pct = _percent(CombatFixture.slice(&"amr_shield10p", RC.SliceType.SANDBOX, 10, RC.TargetRule.SELF))
	_heal_pct = _percent(CombatFixture.slice(&"amr_heal3p", RC.SliceType.HOTFIX, 3, RC.TargetRule.SELF))
	var corrupt := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.POINTER_TARGET, 40, RC.RingScope.OUTER, 1.0, RC.Status.CORRUPTED, RC.SlicePick.RANDOM_NON_NULL)
	corrupt.amount_mode = RC.AmountMode.PERCENT
	var te: Array[TriggeredEffectData] = [CombatFixture.triggered(RC.Trigger.ON_SLICE_TRIGGER, [corrupt])]
	_infect_pct = CombatFixture.slice(&"amr_infect40p", RC.SliceType.INFECT, 0, RC.TargetRule.POINTER, te)


func _percent(s: SliceData) -> SliceData:
	s.amount_mode = RC.AmountMode.PERCENT
	return s


## Operative on an all-NULL wheel (does nothing) vs. one enemy (200 HP) on the fixture wheel.
func _session(factor: float, p_seed: int = SEED) -> CombatSession:
	var player_wheel := CombatFixture.wheel([_null, _null, _null, _null, _null, _null])
	var deck: Array[CardData] = [CombatFixture.card(&"amr_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"amr_class", 60, player_wheel, deck)
	# The operative's wheel has non-NULL slices for the corruption case on a second class.
	var enemy := CombatFixture.enemy(&"amr_enemy", 200, CombatFixture.wheel([_heal10, _block_pct, _shield_pct, _heal_pct, _infect_pct, _null]))
	var resolver := CombatFixture.resolver([cls, enemy, _target_class()])
	return CombatSession.start(resolver, cls.id, [enemy.id], p_seed, &"", 0, {"enemy_output_scale": factor})


## A class with five SHIM slices (corruption targets) that never hits hard enough to matter.
func _target_class() -> ClassData:
	var poke := CombatFixture.slice(&"amr_poke", RC.SliceType.SHIM, 1)
	var deck: Array[CardData] = [CombatFixture.card(&"amr_noop2", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	return CombatFixture.operative_class(&"amr_target", 60, CombatFixture.wheel([poke, poke, poke, poke, poke, _null]), deck)


func _enemy(s: CombatSession) -> CombatantState:
	return s.state.get_combatant(&"enemy_0")


func _first(r: CombatResult, type: String) -> Dictionary:
	var ev := CombatFixture.events_of(r, type)
	return ev[0] if not ev.is_empty() else {}


func _end_turn_preview_and_result(s: CombatSession, type: String) -> Array:
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	return [_first(pv, type), _first(r, type), pv, r]


func test_preview_equals_result_flat_heal_slice_at_t3() -> void:
	var s := _session(TIER_FACTORS[2])
	_enemy(s).hp = 50
	CombatFixture.land(_enemy(s), 0)
	var got := _end_turn_preview_and_result(s, "heal")
	assert_eq(int(got[1].get("amount", -1)), 17, "HOTFIX 10 at factor 1.69")
	assert_eq(got[0].get("amount"), got[1].get("amount"), "preview == result")
	assert_eq((got[2] as CombatResult).resolved_state.state_hash() if (got[2] as CombatResult).resolved_state != null else 0,
		(got[3] as CombatResult).resolved_state.state_hash() if (got[3] as CombatResult).resolved_state != null else 0)


func test_preview_equals_result_percent_block_not_rescaled() -> void:
	for f in TIER_FACTORS:
		var s := _session(f)
		CombatFixture.land(_enemy(s), 1)
		var got := _end_turn_preview_and_result(s, "block")
		assert_eq(int(got[1].get("amount", -1)), 10, "5 %% of 200 at factor %s" % f)
		assert_eq(got[0].get("amount"), got[1].get("amount"), "preview == result")


func test_percent_shield_on_enemy() -> void:
	var s := _session(TIER_FACTORS[3])
	CombatFixture.land(_enemy(s), 2)
	var got := _end_turn_preview_and_result(s, "shield")
	assert_eq(int(got[1].get("requested", -1)), 20, "10 % of 200, not x2.2")
	assert_eq(got[0].get("amount"), got[1].get("amount"))


func test_weak_tier_halves_percent_amount() -> void:
	# Formula: round(percent_of(max_hp, pct) x weak_multiplier); the percent comes first.
	var s := _session(TIER_FACTORS[3])
	_enemy(s).hp = 50
	CombatFixture.land(_enemy(s), 3, 2)
	var got := _end_turn_preview_and_result(s, "heal")
	var expected := roundi(EffectInterpreter.percent_of(200, 3) * s.resolver.config.weak_multiplier)
	assert_eq(int(got[1].get("amount", -1)), expected)
	assert_eq(got[0].get("amount"), got[1].get("amount"))


func test_preview_equals_result_percent_corruption_count() -> void:
	var resolver := _session(1.0).resolver
	var s := CombatSession.start(resolver, &"amr_target", [&"amr_enemy"], SEED, &"", 0, {"enemy_output_scale": TIER_FACTORS[1]})
	CombatFixture.land(s.state.player, 5)
	CombatFixture.land(_enemy(s), 4)
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	var pv_slots := CombatFixture.events_of(pv, "status").map(func(e: Dictionary) -> int: return int(e["slot"]))
	var r_slots := CombatFixture.events_of(r, "status").map(func(e: Dictionary) -> int: return int(e["slot"]))
	assert_eq(r_slots.size(), 2, "40 % of 5 non-NULL slices")
	assert_eq(pv_slots, r_slots, "preview names the same slices")


func test_seeded_replay_same_state_hash() -> void:
	# No hand-parked wheels: the turn-start respins pick the landings, so replay rebuilds them.
	var s := _session(TIER_FACTORS[2])
	var amounts := 0
	for i in 12:
		var r := s.apply(CombatAction.end_turn())
		for type in ["heal", "block", "shield", "status"]:
			amounts += CombatFixture.events_of(r, type).size()
		if s.state.is_over():
			break
	var again := CombatSession.replay(s.resolver, s.setup, s.combat_seed, s.history)
	assert_gt(amounts, 0, "the run exercised the amount slices")
	assert_eq(again.state_hash(), s.state_hash(), "seeded replay matches")


func test_undo_restores_state_and_never_crosses_the_checkpoint() -> void:
	# No hand-parked wheel here: undo rebuilds from the checkpoint, which never saw one.
	var s := _session(TIER_FACTORS[3])
	var before := s.state_hash()
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	s.rewind()
	assert_eq(s.state_hash(), before, "undo restores the pre-action state")
	s.apply(CombatAction.end_turn())
	assert_false(s.can_rewind(), "END TURN is a checkpoint: undo stops there")
