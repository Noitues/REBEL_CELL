extends GutTest
## Wheel math matches GDD 2.3 for all 30 ticks, flipped and unflipped (M1 acceptance).
## Expected values are re-derived here with integer arithmetic, independently of
## WheelMath, so the table is a real cross-check.


func _expected_slice(tick: int) -> int:
	return int((tick + 2) / 5) % 6


func _expected_offset(tick: int) -> int:
	var off := tick - 5 * _expected_slice(tick)
	if off > 2:
		off -= 30
	return off


func test_tick_under_pointer_for_every_rotation_pointer_and_flip() -> void:
	for rotation in 30:
		for pointer in [0, 10, 15, 20]:
			for flipped in [false, true]:
				var expected: int = (rotation + pointer + (15 if flipped else 0)) % 30
				assert_eq(WheelMath.tick_at(rotation, pointer, flipped), expected,
					"rotation %d pointer %d flipped %s" % [rotation, pointer, flipped])


func test_tick_under_pointer_handles_negative_and_large_rotations() -> void:
	assert_eq(WheelMath.tick_at(-1, 0, false), 29)
	assert_eq(WheelMath.tick_at(-31, 0, false), 29)
	assert_eq(WheelMath.tick_at(90, 0, false), 0)
	assert_eq(WheelMath.tick_at(29, 0, true), 14)


func test_slice_and_offset_table_for_all_30_ticks() -> void:
	for tick in 30:
		assert_eq(WheelMath.slice_at(tick), _expected_slice(tick), "slice at tick %d" % tick)
		assert_eq(WheelMath.offset_at(tick), _expected_offset(tick), "offset at tick %d" % tick)


func test_slice_and_offset_table_flipped_for_all_30_ticks() -> void:
	for rotation in 30:
		var tick := WheelMath.tick_at(rotation, 0, true)
		assert_eq(WheelMath.slice_at(tick), _expected_slice((rotation + 15) % 30), "flipped slice at rotation %d" % rotation)
		assert_eq(WheelMath.offset_at(tick), _expected_offset((rotation + 15) % 30), "flipped offset at rotation %d" % rotation)


func test_slice_centres_and_edges() -> void:
	assert_eq(WheelMath.slice_at(0), 0)
	assert_eq(WheelMath.slice_at(2), 0)
	assert_eq(WheelMath.slice_at(3), 1)
	assert_eq(WheelMath.slice_at(28), 0)
	assert_eq(WheelMath.slice_at(27), 5)
	assert_eq(WheelMath.offset_at(28), -2)
	assert_eq(WheelMath.offset_at(3), -2)
	assert_eq(WheelMath.offset_at(7), 2)
	assert_eq(WheelMath.slice_center(3), 15)


func test_precision_tiers_have_no_miss_tier() -> void:
	assert_eq(WheelMath.tier(0), RC.PrecisionTier.PERFECT)
	assert_eq(WheelMath.tier(1), RC.PrecisionTier.GOOD)
	assert_eq(WheelMath.tier(-1), RC.PrecisionTier.GOOD)
	assert_eq(WheelMath.tier(2), RC.PrecisionTier.PARTIAL)
	assert_eq(WheelMath.tier(-2), RC.PrecisionTier.PARTIAL)
	assert_eq(RC.PrecisionTier.keys().size(), 3, "exactly Partial, Good, Perfect")
	assert_false(RC.PrecisionTier.keys().has("MISS"))
	for tick in 30:
		assert_true(absi(WheelMath.offset_at(tick)) <= 2, "every tick is within 2 of a centre")


func test_ring_segments_are_three_ten_tick_arcs_centred_on_0_10_20() -> void:
	for tick in 30:
		var expected := 0
		if tick >= 5 and tick <= 14:
			expected = 1
		elif tick >= 15 and tick <= 24:
			expected = 2
		assert_eq(WheelMath.ring_segment(tick), expected, "segment at inner tick %d" % tick)


func test_satellite_wheels_use_the_same_functions() -> void:
	assert_eq(WheelMath.ticks_per_slice(3), 10)
	assert_eq(WheelMath.ticks_per_slice(2), 15)
	for d in range(-4, 5):
		assert_eq(WheelMath.slice_at(posmod(10 + d, 30), 3), 1, "3-slice tick %d" % (10 + d))
		assert_eq(WheelMath.slice_at(posmod(20 + d, 30), 3), 2)
		assert_eq(WheelMath.slice_at(posmod(d, 30), 3), 0)
	for d in range(-7, 8):
		assert_eq(WheelMath.slice_at(posmod(15 + d, 30), 2), 1, "2-slice tick %d" % (15 + d))
		assert_eq(WheelMath.slice_at(posmod(d, 30), 2), 0)


func test_snap_delta_moves_to_nearest_centre() -> void:
	for tick in 30:
		var snapped := posmod(tick + WheelMath.snap_delta(tick), 30)
		assert_eq(WheelMath.offset_at(snapped), 0, "tick %d snaps to a centre" % tick)
		assert_eq(WheelMath.slice_at(snapped), WheelMath.slice_at(tick), "tick %d keeps its slice" % tick)
