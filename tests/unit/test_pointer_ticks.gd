extends GutTest
## Plan 2 N11 (GDD 2.1 amendment, R10; ruling Q27): a pointer may sit on any tick 0-29, at
## least 1 tick from the next. Each pointer reads (rotation + tick) mod 30 and resolves on
## its own (GDD 2.7): its own slice, offset and tier. Two pointers on one tick are invalid.


## A 6-slice wheel's readout for one pointer on `tick` at rotation 0.
func _read(tick: int) -> Dictionary:
	var shim := CombatFixture.slice(&"pt_shim", RC.SliceType.SHIM, 5)
	var c := CombatantState.new()
	c.wheel = WheelState.from_wheel_data(CombatFixture.wheel([shim, shim, shim, shim, shim, shim], null, [tick]))
	return CombatFixture.resolver([shim])._readout(CombatState.new(), c, 0)


func test_pointer_reads_rotation_plus_tick_mod_30() -> void:
	assert_eq(WheelMath.tick_at(4, 0), 4)
	assert_eq(WheelMath.tick_at(4, 14), 18)
	assert_eq(WheelMath.tick_at(27, 7), 4, "wraps mod 30")
	assert_eq(WheelMath.tick_at(-3, 1), 28, "negative rotation wraps too")


func test_ticks_1_2_3_29_read_their_slice_offset_and_tier() -> void:
	var cases := {1: [0, 1, RC.PrecisionTier.GOOD], 2: [0, 2, RC.PrecisionTier.WEAK],
		3: [1, -2, RC.PrecisionTier.WEAK], 29: [0, -1, RC.PrecisionTier.GOOD]}
	for t in cases:
		var r := _read(t)
		assert_eq([r["slice_index"], r["offset"], r["tier"]], cases[t], "pointer on tick %d" % t)


func test_all_30_ticks_resolve_with_exactly_6_perfect_and_no_miss() -> void:
	var perfect := 0
	for t in RC.TICKS:
		var r := _read(t)
		assert_between(int(r["slice_index"]), 0, RC.SLICES - 1, "tick %d has a slice" % t)
		assert_true(int(r["tier"]) in [RC.PrecisionTier.PERFECT, RC.PrecisionTier.GOOD, RC.PrecisionTier.WEAK], "tick %d has a tier (no miss)" % t)
		if int(r["tier"]) == RC.PrecisionTier.PERFECT:
			perfect += 1
	assert_eq(perfect, RC.SLICES)


## The enemy HP an operative with needles on `pointers` takes in one end of turn at rotation 4.
func _drop(pointers: Array) -> Dictionary:
	var target := PhaseFixture.enemy(&"pt_target", 500, [], RC.EnemyClass.NORMAL)
	var s := PhaseFixture.session(target, 10, pointers)
	s.state.player.wheel.rotation = 4
	var e := s.state.get_combatant(&"enemy_0")
	var before := e.hp
	var r := s.apply(CombatAction.end_turn())
	var ptrs: Array = []
	for ev in CombatFixture.events_of(r, "pointer"):
		if ev["owner"] == s.state.player.id:
			ptrs.append([ev["tick"], ev["slice_index"], ev["tier"]])
	return {"drop": before - s.state.get_combatant(&"enemy_0").hp, "pointers": ptrs}


func test_pointers_0_and_14_at_rotation_4_hit_once_each_on_their_own_slice() -> void:
	var both := _drop([0, 14])
	assert_eq(both["pointers"], [[4, 1, RC.PrecisionTier.GOOD], [18, 4, RC.PrecisionTier.WEAK]], "ticks 4 and 18, each its own slice and tier")
	var alone := int(_drop([0])["drop"]) + int(_drop([14])["drop"])
	assert_gt(int(both["drop"]), 0)
	assert_eq(int(both["drop"]), alone, "each pointer lands once, as it would alone")


func test_adjacent_pointers_both_resolve() -> void:
	var adj := _drop([0, 1])
	assert_eq(adj["pointers"].size(), 2, "both needles of a gap-1 pair resolve")
	assert_eq([adj["pointers"][0][0], adj["pointers"][1][0]], [4, 5])
	assert_eq(int(adj["drop"]), int(_drop([0])["drop"]) + int(_drop([1])["drop"]))


func test_pointer_layout_validation_names_each_problem() -> void:
	assert_eq(WheelData.pointer_errors(PackedInt32Array([0, 1, 29])), PackedStringArray(), "adjacent and wrapping ticks are valid")
	for bad in [30, -1]:
		var errs := WheelData.pointer_errors(PackedInt32Array([0, bad]))
		assert_eq(errs.size(), 1)
		assert_true(errs[0].begins_with("pointer_tick_out_of_range"), "tick %d" % bad)
	var dup := WheelData.pointer_errors(PackedInt32Array([7, 7]))
	assert_eq(dup.size(), 1)
	assert_true(dup[0].begins_with("pointer_ticks_duplicate"), "two needles on one tick are invalid (Q27)")
