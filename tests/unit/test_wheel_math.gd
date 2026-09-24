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


func test_tick_under_pointer_for_every_rotation_and_pointer() -> void:
	for rotation in 30:
		for pointer in [0, 10, 15, 20]:
			var expected: int = (rotation + pointer) % 30
			assert_eq(WheelMath.tick_at(rotation, pointer), expected, "rotation %d pointer %d" % [rotation, pointer])


func test_tick_under_pointer_handles_negative_and_large_rotations() -> void:
	assert_eq(WheelMath.tick_at(-1, 0), 29)
	assert_eq(WheelMath.tick_at(-31, 0), 29)
	assert_eq(WheelMath.tick_at(90, 0), 0)


func test_slice_and_offset_table_for_all_30_ticks() -> void:
	for tick in 30:
		assert_eq(WheelMath.slice_at(tick), _expected_slice(tick), "slice at tick %d" % tick)
		assert_eq(WheelMath.offset_at(tick), _expected_offset(tick), "offset at tick %d" % tick)


func test_mirror_tick_matches_gdd_2_3_for_all_30_ticks() -> void:
	for pointer in [0, 10, 15]:
		for tick in 30:
			var expected: int = posmod(2 * pointer + 15 - tick, 30)
			assert_eq(WheelMath.mirror_tick(tick, pointer), expected, "mirror of tick %d about pointer %d" % [tick, pointer])
			assert_eq(WheelMath.mirror_tick(WheelMath.mirror_tick(tick, pointer), pointer), tick, "mirroring twice is the identity")
	assert_eq(WheelMath.mirror_tick(0), 15, "the opposite slice arrives at the pointer")
	assert_eq(WheelMath.mirror_tick(1), 14, "slice order reverses")


func test_flipped_wheel_table_for_all_30_rotations() -> void:
	# State-level table: after a flip, the tick under the pointer is 15 - t, the slice
	# under the pointer is the one that sat opposite, and the offset is mirrored.
	for rotation in 30:
		var w := WheelState.new()
		for i in 6:
			w.slot_slice_ids.append(StringName("s%d" % i))
			w.slot_firmware_ids.append(&"")
			w.slice_statuses.append(RC.Status.NONE)
		w.rotation = rotation
		var old_tick := w.tick_at(0)
		var opposite_slice := w.slot_slice_ids[WheelMath.slice_at((old_tick + 15) % 30)]
		w.flip()
		assert_eq(w.tick_at(0), WheelMath.mirror_tick(old_tick), "rotation %d: tick under pointer" % rotation)
		assert_eq(w.slot_slice_ids[w.slice_at(0)], opposite_slice, "rotation %d: opposite slice at the pointer" % rotation)
		assert_eq(WheelMath.offset_at(w.tick_at(0)), -_expected_offset(old_tick), "rotation %d: offset mirrored" % rotation)
		assert_eq(w.slot_slice_ids, [&"s0", &"s5", &"s4", &"s3", &"s2", &"s1"], "slice order reversed")
		w.flip()
		assert_eq(w.tick_at(0), old_tick, "rotation %d: flipping twice restores the tick" % rotation)
		assert_eq(w.slot_slice_ids, [&"s0", &"s1", &"s2", &"s3", &"s4", &"s5"], "and the layout")


func test_mirrored_slot_pairs() -> void:
	assert_eq(WheelMath.mirrored_slot(0), 0)
	assert_eq(WheelMath.mirrored_slot(1), 5)
	assert_eq(WheelMath.mirrored_slot(2), 4)
	assert_eq(WheelMath.mirrored_slot(3), 3)
	assert_eq(WheelMath.mirrored_slot(1, 2), 1)
	assert_eq(WheelMath.mirrored_slot(1, 3), 2)


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
