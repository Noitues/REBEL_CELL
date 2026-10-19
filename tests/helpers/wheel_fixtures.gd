class_name WheelFixtures
extends RefCounted
## Plan 2 N12: wheels with uneven slot sizes for the size tests. Content builders only; the
## random layouts use a local RandomNumberGenerator with a fixed seed (never the game RNG).


## A WheelData of `slices` with slot sizes `sizes` (and optional quality maps / Firmware).
static func make_layout(sizes: Array, slices: Array, quality: Array = [], firmware: Array = [], pointers: Array = [0]) -> WheelData:
	var w := CombatFixture.wheel(slices, null, pointers, 0, null, firmware)
	for i in w.slots.size():
		w.slots[i].size_ticks = int(sizes[i])
		if i < quality.size() and quality[i] != null:
			w.slots[i].tick_quality = PackedInt32Array(quality[i])
	return w


## A random layout from `seed`: 1-12 slots, sizes 0-30 summing to 30, at least one non-empty.
static func random_sizes(seed: int, allow_empty: bool = true) -> PackedInt32Array:
	var r := RandomNumberGenerator.new()
	r.seed = seed
	var n := r.randi_range(1, 12)
	var out := PackedInt32Array()
	var left := RC.TICKS
	for i in n - 1:
		var lo := 0 if allow_empty else 1
		var hi := left - (n - 1 - i) * lo
		var s := r.randi_range(lo, mini(hi, 10))
		out.append(s)
		left -= s
	out.append(left)
	return out


## A WheelState with `sizes` (slot ids "slot_<i>"), rotation 0, one pointer on tick 0.
static func state(sizes: PackedInt32Array) -> WheelState:
	var w := WheelState.new()
	w.slice_count = sizes.size()
	w.slot_sizes = sizes.duplicate()
	for i in sizes.size():
		w.slot_slice_ids.append(StringName("slot_%d" % i))
		w.slot_firmware_ids.append(&"")
		w.slice_stacks.append({})
	return w
