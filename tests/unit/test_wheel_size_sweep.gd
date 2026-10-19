extends GutTest
## Plan 2 N12 (full tier): a seeded property sweep over 2000 random layouts (sizes 0-30 summing
## to 30). Every tick has one owner of its slot's size, centres sit inside their slot, a flip is
## an involution, snap stays in the slot on a best tick, and the remap keeps every stack.


func test_random_layouts_all_ticks_covered() -> void:
	for seed in 2000:
		var sizes := WheelFixtures.random_sizes(seed)
		var counts := PackedInt32Array()
		counts.resize(sizes.size())
		for t in 30:
			var slot := WheelMath.slot_of_tick(t, sizes)
			counts[slot] += 1
			assert_true(sizes[slot] > 0)
		if counts != sizes:
			assert_eq(counts, sizes, "seed %d" % seed)
			return
		for i in sizes.size():
			if sizes[i] > 0 and WheelMath.slot_of_tick(WheelMath.center_tick(i, sizes), sizes) != i:
				fail_test("seed %d slot %d: its centre is outside it" % [seed, i])
				return
	pass_test("2000 layouts")


func test_flip_snap_and_remap_hold_on_random_layouts() -> void:
	var cap := CombatFixture.config().status_stack_cap
	for seed in 2000:
		var sizes := WheelFixtures.random_sizes(seed)
		var w := WheelFixtures.state(sizes)
		w.rotation = seed % 61 - 30
		var d := w.to_dict()
		w.flip()
		w.flip()
		if w.to_dict() != d:
			fail_test("seed %d: flip twice is not the identity" % seed)
			return
		var t := posmod(seed * 7, 30)
		var slot := WheelMath.slot_of_tick(t, sizes)
		var tiers := WheelMath.default_quality(sizes[slot], 1)
		var to := posmod(t + WheelMath.snap_delta_in(t, sizes, tiers), 30)
		var top := 0
		for x in tiers:
			top = maxi(top, x)
		if WheelMath.slot_of_tick(to, sizes) != slot or tiers[WheelMath.index_in_slot(to, sizes)] != top:
			fail_test("seed %d: snap from %d left the slot or missed its best tick" % [seed, t])
			return
		var old: Array[Dictionary] = []
		for i in sizes.size():
			old.append({RC.Status.CORRUPTED: 1} if sizes[i] > 0 else {})
		var other := WheelFixtures.random_sizes(seed + 7919)
		var out := WheelState.remap_stacks_sized(old, sizes, other, cap)
		var before := 0
		var after := 0
		for x in old:
			before += int(x.get(RC.Status.CORRUPTED, 0))
		for x in out:
			after += int(x.get(RC.Status.CORRUPTED, 0))
		if before != after:
			fail_test("seed %d: remap lost CORRUPTED stacks" % seed)
			return
	pass_test("2000 layouts")
