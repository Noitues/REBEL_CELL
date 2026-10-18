extends GutTest
## Plan 2 N1 (R5): `amount_mode` on EffectData / SliceData. Old content loads FLAT; validate()
## refuses PERCENT outside 0..100 or on a type without a percent reading, with a stable code.


func _effect(type: int, amount: int, mode: int, status: int = RC.Status.NONE) -> EffectData:
	var e := CombatFixture.effect(type, RC.EffectTarget.SELF, amount, RC.RingScope.OUTER, 1.0, status)
	e.amount_mode = mode
	return e


func _has_code(errors: PackedStringArray, code: String) -> bool:
	for e in errors:
		if e.begins_with(code + ":"):
			return true
	return false


func test_enum_int_values_stable() -> void:
	assert_eq(int(RC.AmountMode.FLAT), 0, "FLAT = 0 so .tres files without the field load FLAT")
	assert_eq(int(RC.AmountMode.PERCENT), 1)


func test_default_amount_mode_is_flat_on_old_content() -> void:
	assert_eq(EffectData.new().amount_mode, RC.AmountMode.FLAT)
	assert_eq(SliceData.new().amount_mode, RC.AmountMode.FLAT)
	var hub := (load("res://content/enemies/renewal_engine.tres") as EnemyData).wheel.hub
	var found := 0
	for te in hub.passive_effects:
		for e in te.effects:
			if e.type == RC.EffectType.HEAL:
				found += 1
				assert_eq(e.amount_mode, RC.AmountMode.FLAT, "a .tres without the field loads FLAT")
	assert_gt(found, 0, "the Auto-Renew heal is there")


func test_effect_validate_rejects_percent_over_100_and_negative() -> void:
	assert_true(_has_code(_effect(RC.EffectType.HEAL, 101, RC.AmountMode.PERCENT).validate(), "percent_out_of_range"))
	assert_true(_has_code(_effect(RC.EffectType.HEAL, -1, RC.AmountMode.PERCENT).validate(), "percent_out_of_range"))
	assert_eq(_effect(RC.EffectType.HEAL, 100, RC.AmountMode.PERCENT).validate().size(), 0)
	assert_eq(_effect(RC.EffectType.HEAL, 0, RC.AmountMode.PERCENT).validate().size(), 0)
	assert_eq(_effect(RC.EffectType.HEAL, 250, RC.AmountMode.FLAT).validate().size(), 0, "FLAT has no range")


func test_amount_mode_rejected_on_damage_effect() -> void:
	assert_true(_has_code(_effect(RC.EffectType.DEAL_DAMAGE, 10, RC.AmountMode.PERCENT).validate(), "mode_unsupported_for_type"))
	assert_true(_has_code(_effect(RC.EffectType.APPLY_STATUS, 10, RC.AmountMode.PERCENT, RC.Status.OVERCLOCKED).validate(), "mode_unsupported_for_type"))


func test_effect_validate_accepts_percent_on_heal_block_shield_corruption() -> void:
	for t in [RC.EffectType.HEAL, RC.EffectType.GAIN_BLOCK, RC.EffectType.GAIN_SHIELD]:
		assert_eq(_effect(t, 5, RC.AmountMode.PERCENT).validate().size(), 0, RC.EffectType.keys()[t])
	assert_eq(_effect(RC.EffectType.APPLY_STATUS, 40, RC.AmountMode.PERCENT, RC.Status.CORRUPTED).validate().size(), 0)


func test_slice_validate_accepts_mode_on_hotfix_defrag_sandbox() -> void:
	for t in [RC.SliceType.HOTFIX, RC.SliceType.DEFRAG, RC.SliceType.SANDBOX]:
		var s := CombatFixture.slice(&"am_s", t, 5, RC.TargetRule.SELF)
		s.amount_mode = RC.AmountMode.PERCENT
		assert_eq(s.validate().size(), 0, RC.SliceType.keys()[t])
	var shim := CombatFixture.slice(&"am_shim", RC.SliceType.SHIM, 5)
	shim.amount_mode = RC.AmountMode.PERCENT
	assert_true(_has_code(shim.validate(), "mode_unsupported_for_type"))
	var big := CombatFixture.slice(&"am_big", RC.SliceType.HOTFIX, 120, RC.TargetRule.SELF)
	big.amount_mode = RC.AmountMode.PERCENT
	assert_true(_has_code(big.validate(), "percent_out_of_range"))


func test_slice_validate_reports_its_extra_effects_modes() -> void:
	var bad := _effect(RC.EffectType.APPLY_STATUS, 140, RC.AmountMode.PERCENT, RC.Status.CORRUPTED)
	var te: Array[TriggeredEffectData] = [CombatFixture.triggered(RC.Trigger.ON_SLICE_TRIGGER, [bad])]
	var s := CombatFixture.slice(&"am_dose", RC.SliceType.INFECT, 0, RC.TargetRule.POINTER, te)
	assert_true(_has_code(s.validate(), "percent_out_of_range"))


func test_shipped_content_has_no_amount_mode_errors() -> void:
	for p in ContentRegistry.validate():
		assert_false(p.contains("percent_out_of_range") or p.contains("mode_unsupported_for_type"), p)
