extends GutTest
## Plan 2 N7: LOCK_* effect content validation.


func _lock(type: int, turns: int) -> EffectData:
	return CombatFixture.effect(type, RC.EffectTarget.TARGET_WHEEL, turns)


func test_zero_or_negative_turns_are_rejected() -> void:
	for t in [0, -1]:
		for type in [RC.EffectType.LOCK_NUDGE, RC.EffectType.LOCK_RESPIN]:
			var errors := _lock(type, t).validate()
			assert_eq(errors.size(), 1, "%d" % t)
			assert_true(errors[0].begins_with("lock_turns_lt_1"), errors[0])


func test_one_or_more_turns_are_accepted() -> void:
	assert_eq(_lock(RC.EffectType.LOCK_NUDGE, 1).validate().size(), 0)
	assert_eq(_lock(RC.EffectType.LOCK_RESPIN, 3).validate().size(), 0)


func test_the_new_effect_types_are_appended_after_custom() -> void:
	assert_gt(RC.EffectType.LOCK_NUDGE, RC.EffectType.CUSTOM)
	assert_eq(RC.EffectType.LOCK_RESPIN, RC.EffectType.LOCK_NUDGE + 1)
