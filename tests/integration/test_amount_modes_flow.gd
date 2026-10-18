extends GutTest
## Plan 2 N1: the HEALED / GAINED chips the combat HUD builds (ResultChipModel, the model the
## scene draws) carry the interpreter's number for FLAT x tier and PERCENT amounts, and the
## previewed chips equal the resolved ones.

const FACTOR := 2.2


func _session() -> CombatSession:
	var nul := CombatFixture.slice(&"amf_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var heal_pct := CombatFixture.slice(&"amf_heal4p", RC.SliceType.HOTFIX, 4, RC.TargetRule.SELF)
	heal_pct.amount_mode = RC.AmountMode.PERCENT
	var block10 := CombatFixture.slice(&"amf_block10", RC.SliceType.DEFRAG, 10, RC.TargetRule.SELF)
	var deck: Array[CardData] = [CombatFixture.card(&"amf_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"amf_class", 60, CombatFixture.wheel([nul, nul, nul, nul, nul, nul]), deck)
	var enemy := CombatFixture.enemy(&"amf_enemy", 250, CombatFixture.wheel([heal_pct, block10, nul, nul, nul, nul], null, [0, 5]))
	var resolver := CombatFixture.resolver([cls, enemy])
	return CombatSession.start(resolver, cls.id, [enemy.id], 9, &"", 0, {"enemy_output_scale": FACTOR})


func _chips(s: CombatSession, r: CombatResult, before: CombatState) -> Array[Dictionary]:
	var after := r.resolved_state if r.resolved_state != null else r.state
	return RealChips.build(s.resolver, before, null, after, r.events, &"enemy_0", RC.Status.NONE, 0)


func test_chip_numbers_match_the_resolved_amounts() -> void:
	var s := _session()
	var e := s.state.get_combatant(&"enemy_0")
	e.hp = 100
	CombatFixture.land(e, 0, 0, 0)
	CombatFixture.land(e, 1, 0, 1)
	var before := s.state.duplicate_state()
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	var heal := CombatFixture.events_of(r, "heal")
	var block := CombatFixture.events_of(r, "block")
	assert_eq(heal.size(), 1)
	assert_eq(block.size(), 1)
	assert_eq(int(heal[0]["amount"]), 10, "4 % of 250, not rescaled")
	assert_eq(int(block[0]["amount"]), 22, "FLAT 10 x 2.2")
	var real := _chips(s, r, before)
	var shown := _chips(s, pv, before)
	assert_eq(ResultChipModel.value_of(real, ResultChipModel.HEALED), 10, "the HEALED chip says the heal")
	assert_eq(ResultChipModel.value_of(shown, ResultChipModel.HEALED), ResultChipModel.value_of(real, ResultChipModel.HEALED), "preview chip == result chip")
	assert_eq(ResultChipModel.value_of(shown, ResultChipModel.GAINED), ResultChipModel.value_of(real, ResultChipModel.GAINED))
