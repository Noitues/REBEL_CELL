extends GutTest
## Plan 2 N8: content validation of the stack fields (EffectData.stacks / cleanse_mode), and
## the shipped content still validating with them (the PARASITE content now authors
## OUTPUT_DOWN x2).


func _apply(status: int, stacks: int) -> EffectData:
	var e := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.TARGET_WHEEL, 0, RC.RingScope.OUTER, 1.0, status)
	e.stacks = stacks
	return e


func _codes(errors: PackedStringArray) -> Array:
	var out := []
	for e in errors:
		out.append(e.get_slice(":", 0))
	return out


func test_slice_apply_status_amount_zero_rejected() -> void:
	assert_has(_codes(_apply(RC.Status.OUTPUT_DOWN, 0).validate()), "stack_amount_lt_1")
	assert_has(_codes(_apply(RC.Status.OUTPUT_DOWN, -2).validate()), "stack_amount_lt_1")
	assert_eq(_apply(RC.Status.OUTPUT_DOWN, 1).validate().size(), 0)


func test_amount_above_cap_rejected() -> void:
	var cap := CombatFixture.config().status_stack_cap
	assert_eq(_apply(RC.Status.OUTPUT_DOWN, cap).validate(cap).size(), 0, "the cap itself is fine")
	assert_has(_codes(_apply(RC.Status.OUTPUT_DOWN, cap + 1).validate(cap)), "stack_amount_gt_cap")
	assert_eq(_apply(RC.Status.CORRUPTED, cap + 1).validate(cap).size(), 0, "CORRUPTED has no cap (Q36)")
	assert_eq(_apply(RC.Status.ENCRYPTED, cap + 1).validate(cap).size(), 0, "nor ENCRYPTED")


func test_retired_parasite_is_refused_in_content() -> void:
	assert_has(_codes(_apply(RC.Status.PARASITE, 1).validate()), "status_retired")


func test_cleanse_stack_mode_requires_valid_enum() -> void:
	var e := CombatFixture.effect(RC.EffectType.CLEANSE, RC.EffectTarget.OWN_WHEEL)
	assert_eq(e.validate().size(), 0, "ALL by default")
	e.cleanse_mode = RC.CleanseMode.ONE_STACK
	assert_eq(e.validate().size(), 0)
	e.set("cleanse_mode", 7)
	assert_has(_codes(e.validate()), "cleanse_mode_invalid")


func test_existing_content_still_validates() -> void:
	var stack_codes := ["stack_amount_lt_1", "stack_amount_gt_cap", "status_retired", "cleanse_mode_invalid"]
	for err in ContentRegistry.validate():
		for code in stack_codes:
			assert_false(err.contains(code + ":"), err)
	for id in [&"leech_worm", &"parasite_pulse"]:
		var card := ContentRegistry.get_content(id) as CardData
		assert_eq(card.effects[0].status, RC.Status.OUTPUT_DOWN, "%s plants OUTPUT_DOWN" % id)
		assert_eq(card.effects[0].stacks, CombatFixture.config().parasite_output_down_stacks, "x2 (R8)")
