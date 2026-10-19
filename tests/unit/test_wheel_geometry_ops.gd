extends GutTest
## Plan 2 N12 (R10, R11, Q20): flip, snap, nudge, spin and the neighbour rules on uneven
## wheels. Flip is an involution and lands every arc exactly on its mirror image; snap goes
## to the nearest best tick (a tie counter-clockwise); a resize takes its ticks from the fixed
## clockwise neighbour and keeps the sum at 30.

const W := RC.PrecisionTier.WEAK
const G := RC.PrecisionTier.GOOD
const P := RC.PrecisionTier.PERFECT


## The slot (by content id) under the screen position `x` ticks from pointer 0.
func _slot_at_screen(w: WheelState, x: int) -> StringName:
	return w.slot_slice_ids[w.slot_of_tick(posmod(w.rotation + x, 30))]


func test_flip_is_an_involution_on_uneven_wheels() -> void:
	for seed in 100:
		var w := WheelFixtures.state(WheelFixtures.random_sizes(seed))
		w.rotation = seed * 7 - 40
		var before := w.to_dict()
		w.flip()
		w.flip()
		assert_eq(w.to_dict(), before, "seed %d" % seed)


func test_flip_mirrors_every_screen_tick() -> void:
	# GDD 2.3: the content at screen position x arrives at 15 - x.
	for seed in 100:
		var w := WheelFixtures.state(WheelFixtures.random_sizes(seed))
		w.rotation = seed * 3
		var before := []
		for x in 30:
			before.append(_slot_at_screen(w, x))
		w.flip()
		for x in 30:
			assert_eq(_slot_at_screen(w, posmod(15 - x, 30)), before[x], "seed %d screen tick %d" % [seed, x])


func test_flip_reverses_order_keeps_sizes() -> void:
	var w := WheelFixtures.state(PackedInt32Array([6, 4, 3, 5, 5, 7]))
	w.flip()
	assert_eq(w.slot_sizes, PackedInt32Array([6, 7, 5, 5, 3, 4]))
	assert_eq(w.slot_slice_ids[1], &"slot_5")


func test_flip_reverses_an_authored_quality_map() -> void:
	var w := WheelFixtures.state(PackedInt32Array([5, 4, 21]))
	var maps: Array[PackedInt32Array] = [PackedInt32Array(), PackedInt32Array([W, W, G, P]), PackedInt32Array()]
	w.set_quality_maps(maps)
	w.flip()
	assert_eq(w.quality_override(2), PackedInt32Array([P, G, W, W]), "slot 1 moved to slot 2 and reads backwards")


func test_snap_to_center_moves_to_nearest_best_tick() -> void:
	var sizes := PackedInt32Array([5, 4, 5, 6, 5, 5])
	# slot 1 = ticks 3-6, W G G W: from tick 3 the nearest best is tick 4; from 6, tick 5
	var tiers := WheelMath.default_quality(4, 1)
	assert_eq(WheelMath.snap_delta_in(3, sizes, tiers), 1)
	assert_eq(WheelMath.snap_delta_in(6, sizes, tiers), -1)
	assert_eq(WheelMath.snap_delta_in(4, sizes, tiers), 0, "already on a best tick")
	# odd slot: the Perfect centre
	assert_eq(WheelMath.snap_delta_in(28, sizes, WheelMath.default_quality(5, 1)), 2)


func test_snap_tie_goes_to_the_lower_tick() -> void:
	var sizes := PackedInt32Array([5, 5, 5, 5, 5, 5])
	# a map G W G on ticks 28-0 of a 5-slice... authored: W G W G W -> from the middle, both
	# Goods are 1 away: the lower (counter-clockwise) one wins.
	var tiers := PackedInt32Array([W, G, W, G, W])
	assert_eq(WheelMath.snap_delta_in(0, sizes, tiers), -1)


func test_snap_on_size4_lands_on_good_not_perfect() -> void:
	var sizes := PackedInt32Array([4, 26])
	var tiers := WheelMath.default_quality(4, 1)
	for t in [28, 29, 0, 1]:
		var to := WheelMath.index_in_slot(posmod(t + WheelMath.snap_delta_in(t, sizes, tiers), 30), sizes)
		assert_eq(tiers[to], G, "tick %d snaps onto a GOOD tick" % t)


func test_snap_on_legacy_wheel_matches_old_snap() -> void:
	var sizes := WheelMath.uniform_sizes(6)
	for t in 30:
		assert_eq(WheelMath.snap_delta_in(t, sizes, WheelMath.default_quality(5, 1)), WheelMath.snap_delta(t), "tick %d" % t)


func test_neighbor_resize_is_fixed_and_keeps_30() -> void:
	var sizes := PackedInt32Array([5, 5, 5, 5, 5, 5])
	assert_eq(WheelMath.resized(sizes, 2, 7), PackedInt32Array([5, 5, 7, 3, 5, 5]), "slot 3 gives 2")
	assert_eq(WheelMath.resized(sizes, 5, 3), PackedInt32Array([7, 5, 5, 5, 5, 3]), "slot 0 (clockwise of 5) takes 2")
	assert_eq(WheelMath.resized(sizes, 2, 11), PackedInt32Array(), "refused: the neighbour would go below 0")
	assert_eq(WheelMath.resized(sizes, 2, 10), PackedInt32Array([5, 5, 10, 0, 5, 5]), "the neighbour may become an empty arc")
	for seed in 50:
		var s := WheelFixtures.random_sizes(seed)
		if s.size() < 2:
			continue
		var out := WheelMath.resized(s, 0, 0)
		if not out.is_empty():
			var total := 0
			for x in out:
				total += x
			assert_eq(total, 30, "seed %d" % seed)


func test_nudge_wraps_and_spin_by_30_is_identity() -> void:
	var w := WheelFixtures.state(PackedInt32Array([6, 4, 3, 5, 5, 7]))
	w.rotation = 29
	var under := w.slice_at(0)
	w.rotation += 1
	assert_eq(w.tick_at(0), 0)
	w.rotation += 29
	assert_eq(w.slice_at(0), under, "a full turn lands on the same slot")


func test_pointer_on_odd_tick_resolves() -> void:
	var w := WheelFixtures.state(PackedInt32Array([6, 4, 4, 6, 4, 6]))
	w.pointer_ticks = PackedInt32Array([0, 14])
	assert_eq(w.slice_at(0), 0)
	assert_eq(w.slice_at(1), 3, "tick 14 is in slot 3 (11-16)")
