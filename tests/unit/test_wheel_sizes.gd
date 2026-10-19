extends GutTest
## Plan 2 N12 (R11, Q20): cumulative slot boundaries. The legacy 6 x 5 wheel reads exactly as
## the old 5-tick tables; uneven layouts map every tick to exactly one non-empty slot; the
## default sub-tick maps match the R11 table; the centre of an even slot is the lower tick of
## the middle pair (designer, W1 N12). Expected values are derived independently here.

const W := RC.PrecisionTier.WEAK
const G := RC.PrecisionTier.GOOD
const P := RC.PrecisionTier.PERFECT


func _legacy_slice(tick: int) -> int:
	return int((tick + 2) / 5) % 6


func _legacy_offset(tick: int) -> int:
	var off := tick - 5 * _legacy_slice(tick)
	return off - 30 if off > 2 else off


func test_uniform_5x6_matches_legacy_tables() -> void:
	var sizes := WheelMath.uniform_sizes(6)
	for tick in 30:
		assert_eq(WheelMath.slot_of_tick(tick, sizes), _legacy_slice(tick), "slice at %d" % tick)
		assert_eq(WheelMath.offset_in(tick, sizes), _legacy_offset(tick), "offset at %d" % tick)
		var tiers := WheelMath.default_quality(5, CombatFixture.config().tick_quality_good_reach)
		assert_eq(tiers[WheelMath.index_in_slot(tick, sizes)], WheelMath.tier(_legacy_offset(tick)), "tier at %d" % tick)
	for i in 6:
		assert_eq(WheelMath.center_tick(i, sizes), 5 * i, "centre of slot %d" % i)


func test_slice_at_cumulative_boundaries() -> void:
	var sizes := PackedInt32Array([6, 4, 4, 6, 4, 6])
	# slot 0 starts at -(6 / 2) = tick 27: 27-2 | 3-6 | 7-10 | 11-16 | 17-20 | 21-26
	var want := []
	for t in 30:
		var u := posmod(t - 27, 30)
		want.append(0 if u < 6 else (1 if u < 10 else (2 if u < 14 else (3 if u < 20 else (4 if u < 24 else 5)))))
	for t in 30:
		assert_eq(WheelMath.slot_of_tick(t, sizes), want[t], "tick %d" % t)
	assert_eq(WheelMath.slot_starts(sizes), PackedInt32Array([27, 3, 7, 11, 17, 21]))


func test_every_tick_maps_to_exactly_one_slice() -> void:
	for seed in 200:
		var sizes := WheelFixtures.random_sizes(seed)
		var counts := PackedInt32Array()
		counts.resize(sizes.size())
		for t in 30:
			counts[WheelMath.slot_of_tick(t, sizes)] += 1
		assert_eq(counts, sizes, "seed %d: each slot owns exactly its size %s" % [seed, sizes])


func test_default_maps_match_r11_table() -> void:
	var reach := CombatFixture.config().tick_quality_good_reach
	assert_eq(reach, 1, "the shipped default reach")
	assert_eq(WheelMath.default_quality(2, reach), PackedInt32Array([G, G]))
	assert_eq(WheelMath.default_quality(3, reach), PackedInt32Array([G, P, G]))
	assert_eq(WheelMath.default_quality(4, reach), PackedInt32Array([W, G, G, W]))
	assert_eq(WheelMath.default_quality(5, reach), PackedInt32Array([W, G, P, G, W]))
	assert_eq(WheelMath.default_quality(6, reach), PackedInt32Array([W, W, G, G, W, W]))
	assert_eq(WheelMath.default_quality(7, reach), PackedInt32Array([W, W, G, P, G, W, W]))
	assert_eq(WheelMath.default_quality(1, reach), PackedInt32Array([P]))
	assert_eq(WheelMath.default_quality(0, reach), PackedInt32Array())


func test_size4_has_no_perfect() -> void:
	assert_false(P in WheelMath.default_quality(4, 1), "a 4-tick slice is never Perfect by default")


func test_even_size_centre_is_lower_of_middle_pair() -> void:
	assert_eq(WheelMath.center_index(4), 1, "4 ticks: index 1 of 0-3")
	assert_eq(WheelMath.center_index(6), 2)
	assert_eq(WheelMath.center_index(5), 2)
	var sizes := PackedInt32Array([5, 4, 5, 6, 5, 5])
	# slot 1 runs 3-6: centre tick 4 (lower of 4, 5); offsets -1, 0, +1, +2
	assert_eq(WheelMath.center_tick(1, sizes), 4)
	assert_eq([WheelMath.offset_in(3, sizes), WheelMath.offset_in(4, sizes), WheelMath.offset_in(5, sizes), WheelMath.offset_in(6, sizes)], [-1, 0, 1, 2])
	assert_eq([WheelMath.side_in(4, sizes), WheelMath.side_in(5, sizes)], [-1, 1], "an even slot has no middle tick: each half has a side")


func test_boundary_tick_belongs_to_the_clockwise_slice() -> void:
	# 3 x 10 (a satellite): tick 5 starts slot 1, as WheelMath read it before N12
	assert_eq(WheelMath.slice_at(5, 3), 1)
	assert_eq(WheelMath.slice_at(4, 3), 0)
	assert_eq(WheelMath.slice_at(25, 3), 0)
	assert_eq(WheelMath.slice_at(8, 2), 1)
	assert_eq(WheelMath.slice_at(7, 2), 0)


func test_zero_size_slot_owns_no_tick() -> void:
	var sizes := PackedInt32Array([5, 0, 10, 0, 15])
	for t in 30:
		var s := WheelMath.slot_of_tick(t, sizes)
		assert_ne(s, 1, "tick %d" % t)
		assert_ne(s, 3, "tick %d" % t)
	assert_eq(WheelMath.neighbor_slot(0, 1, sizes), 2, "the clockwise neighbour skips the empty arc")
	assert_eq(WheelMath.neighbor_slot(2, 1, sizes), 4)
	assert_eq(WheelMath.neighbor_slot(4, 1, sizes), 0)
	assert_eq(WheelMath.neighbor_slot(2, -1, sizes), 0)
	var w := WheelFixtures.state(sizes)
	for r in 30:
		w.rotation = r
		assert_true(w.slice_at(0) in [0, 2, 4], "a pointer never lands on an empty arc (rotation %d)" % r)


func test_offset_signed_from_centre() -> void:
	var sizes := PackedInt32Array([5, 5, 5, 5, 5, 5])
	for t in [28, 29, 0, 1, 2]:
		assert_eq(WheelMath.offset_in(t, sizes), [-2, -1, 0, 1, 2][[28, 29, 0, 1, 2].find(t)])


func test_no_fixed_tick_arithmetic_left_in_geometry() -> void:
	for path in ["res://scripts/core/wheel_math.gd", "res://scripts/core/combat_resolver.gd", "res://scripts/core/effect_interpreter.gd", "res://scripts/state/wheel_state.gd"]:
		var src := FileAccess.get_file_as_string(path)
		assert_false(src.contains("5 * i"), "%s has no 5 * i" % path)
		assert_false(src.contains("round(t / 5)") or src.contains("roundi(float(tick) / tps)"), "%s has no rounding to a 5-tick grid" % path)
