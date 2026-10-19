class_name WheelMath
extends RefCounted
## Pure wheel geometry (GDD 2.3, TECH_SPEC 5.1). Static, no state, no randomness.
##
## A wheel has RC.TICKS (30) ticks split into slots of any size 0-30 that sum to 30 (plan 2
## N12, R11, ruling Q20): the layout is the slot sizes, read clockwise from slot 0, and every
## boundary is cumulative. Slot 0 starts at tick -(size / 2), so an odd slot 0 is centred on
## tick 0 and a legacy wheel of equal slots reads exactly as it always has (6 x 5: slot i
## is centred on tick 5i). A 0-size slot is an empty arc: it owns no tick and is never
## landed on. The centre of a slot is its middle tick; for an even size the lower tick of the
## middle pair (designer, W1 N12). Satellites use the same functions with 2-3 equal slots.

const TICKS: int = RC.TICKS
const FLIP_OFFSET: int = RC.TICKS / 2


## Tick under a pointer: (rotation + pointer_tick) mod 30.
static func tick_at(rotation: int, pointer_tick: int) -> int:
	return posmod(rotation + pointer_tick, TICKS)


## Where tick `tick` lands when the wheel is mirrored across the horizontal axis through
## pointer `axis_pointer` (GDD 2.3): 2p + 15 - t. The slice opposite the pointer arrives
## at the pointer and slice order reverses. Applying it twice is the identity.
static func mirror_tick(tick: int, axis_pointer: int = 0) -> int:
	return posmod(2 * axis_pointer + FLIP_OFFSET - tick, TICKS)


## Slot index that holds slot `index`'s content after a mirror: -index mod count.
## Slot 0 stays, 1 <-> 5, 2 <-> 4, 3 stays on a 6-slice wheel.
static func mirrored_slot(index: int, slice_count: int = RC.SLICES) -> int:
	return posmod(-index, slice_count)


## Mirrored slot sizes: the size slot -i mod n had (the layout a flip leaves).
static func mirrored_sizes(sizes: PackedInt32Array) -> PackedInt32Array:
	var out := PackedInt32Array()
	for i in sizes.size():
		out.append(sizes[mirrored_slot(i, sizes.size())])
	return out


## The rotation shift a flip adds after -rotation - 15 so the mirrored layout lands on its
## own boundaries: 0 when slot 0 has an odd size (it is symmetric about tick 0), else -1.
## A flip stays an involution (the shift depends on slot 0, which a flip keeps).
static func flip_shift(sizes: PackedInt32Array) -> int:
	return 0 if sizes.is_empty() or sizes[0] % 2 == 1 else -1


## Ticks per slice for a wheel of `slice_count` equal slots (30 / count).
static func ticks_per_slice(slice_count: int) -> int:
	return TICKS / slice_count


## The sizes of a wheel of `slice_count` equal slots (the legacy layout; 6 -> six 5s).
static func uniform_sizes(slice_count: int) -> PackedInt32Array:
	var out := PackedInt32Array()
	for i in slice_count:
		out.append(TICKS / slice_count)
	return out


## Whether `sizes` is the equal layout of its slot count.
static func is_uniform(sizes: PackedInt32Array) -> bool:
	return not sizes.is_empty() and TICKS % sizes.size() == 0 and sizes == uniform_sizes(sizes.size())


## Index of a slot's centre tick inside the slot: the middle tick, the lower of the middle
## pair for an even size (designer, W1 N12); 0 for an empty slot.
static func center_index(size: int) -> int:
	return maxi(0, (size - 1) / 2)


## First tick (0-29) of every slot, cumulative from slot 0's start -(size / 2). A 0-size
## slot's start is the tick its clockwise neighbour starts on.
static func slot_starts(sizes: PackedInt32Array) -> PackedInt32Array:
	var out := PackedInt32Array()
	var at := -(sizes[0] / 2) if not sizes.is_empty() else 0
	for s in sizes:
		out.append(posmod(at, TICKS))
		at += s
	return out


## Index of the slot owning `tick` (never a 0-size slot). A tick belongs to exactly one slot.
static func slot_of_tick(tick: int, sizes: PackedInt32Array) -> int:
	if sizes.is_empty():
		return 0
	var t := posmod(tick + sizes[0] / 2, TICKS)
	var acc := 0
	for i in sizes.size():
		acc += sizes[i]
		if t < acc:
			return i
	return sizes.size() - 1


## Position of `tick` inside the slot that owns it (0 = the slot's first, counter-clockwise tick).
static func index_in_slot(tick: int, sizes: PackedInt32Array) -> int:
	var slot := slot_of_tick(tick, sizes)
	return posmod(tick - slot_starts(sizes)[slot], TICKS)


## Signed ticks from the centre of the owning slot to `tick` (-2..+2 on a 5-tick slot; -1..+2
## on a 4-tick one: the centre is the lower of the middle pair).
static func offset_in(tick: int, sizes: PackedInt32Array) -> int:
	var slot := slot_of_tick(tick, sizes)
	return index_in_slot(tick, sizes) - center_index(sizes[slot])


## Which side of its slot's true middle `tick` lies on: -1 counter-clockwise, +1 clockwise,
## 0 exactly on it (only the centre tick of an odd slot). Mirror and Shunt pick a neighbour by it.
static func side_in(tick: int, sizes: PackedInt32Array) -> int:
	var slot := slot_of_tick(tick, sizes)
	return signi(2 * index_in_slot(tick, sizes) - (sizes[slot] - 1))


## Centre tick (0-29) of slot `index`.
static func center_tick(index: int, sizes: PackedInt32Array) -> int:
	return posmod(slot_starts(sizes)[index] + center_index(sizes[index]), TICKS)


## The middle of slot `index` as a fractional tick (a drawn arc runs from start - 0.5 to
## start + size - 0.5): where a view centres the slot's wedge. Unwrapped near slot 0's start.
static func arc_mid(index: int, sizes: PackedInt32Array) -> float:
	var at := -(sizes[0] / 2)
	for j in index:
		at += sizes[j]
	return float(at) - 0.5 + float(sizes[index]) * 0.5


## The nearest non-empty slot from `index` going `side` (+1 clockwise, -1 counter-clockwise);
## `index` itself when no other slot has ticks. Mirror and Shunt read this neighbour.
static func neighbor_slot(index: int, side: int, sizes: PackedInt32Array) -> int:
	var n := sizes.size()
	for k in range(1, n):
		var j := posmod(index + side * k, n)
		if sizes[j] > 0:
			return j
	return index


## Default sub-tick quality map of a slot of `size` ticks (R11), one RC.PrecisionTier per
## tick: distance d from the slot's true middle; d = 0 PERFECT, d <= `good_reach` GOOD,
## else WEAK. With reach 1: 2 = G G, 3 = G P G, 4 = W G G W, 5 = W G P G W, 6 = W W G G W W.
static func default_quality(size: int, good_reach: int) -> PackedInt32Array:
	var out := PackedInt32Array()
	for i in size:
		var d2 := absi(2 * i - (size - 1))  # twice the distance
		if d2 == 0:
			out.append(RC.PrecisionTier.PERFECT)
		elif d2 <= 2 * good_reach:
			out.append(RC.PrecisionTier.GOOD)
		else:
			out.append(RC.PrecisionTier.WEAK)
	return out


## `tier` raised `step` tiers (Calibrated), capped at PERFECT and never below WEAK.
static func raised_tier(tier: int, step: int) -> int:
	return clampi(tier + step, RC.PrecisionTier.WEAK, RC.PrecisionTier.PERFECT)


## Ticks (signed, shortest way) that bring `tick` onto the best tick of its own slot under
## `tiers` (that slot's quality map): the highest tier, the nearest one, a tie to the lower
## index (counter-clockwise). 0 when `tick` already sits on a best tick.
static func snap_delta_in(tick: int, sizes: PackedInt32Array, tiers: PackedInt32Array) -> int:
	var here := index_in_slot(tick, sizes)
	var best := -1
	var best_d := TICKS + 1
	var top := -1
	for t in tiers:
		top = maxi(top, t)
	for i in tiers.size():
		if tiers[i] != top:
			continue
		var d := absi(i - here)
		if d < best_d:
			best_d = d
			best = i
	return 0 if best < 0 else best - here


## Sizes after slot `index` becomes `new_size` with its fixed neighbour (the next slot
## clockwise) giving or taking the difference, so the sum stays 30 (ruling Q20). Empty when
## refused: `new_size` outside 0-30, or the neighbour would drop below 0.
static func resized(sizes: PackedInt32Array, index: int, new_size: int) -> PackedInt32Array:
	if sizes.size() < 2 or index < 0 or index >= sizes.size() or new_size < 0 or new_size > TICKS:
		return PackedInt32Array()
	var j := posmod(index + 1, sizes.size())
	var out := sizes.duplicate()
	out[j] -= new_size - sizes[index]
	out[index] = new_size
	if out[j] < 0:
		return PackedInt32Array()
	return out


## Index of the slice owning `tick` on a wheel of `slice_count` equal slots.
static func slice_at(tick: int, slice_count: int = RC.SLICES) -> int:
	return slot_of_tick(tick, uniform_sizes(slice_count))


## Signed distance from `tick` to its slot's centre on a wheel of `slice_count` equal slots
## (-2..+2 on 6-slice wheels).
static func offset_at(tick: int, slice_count: int = RC.SLICES) -> int:
	return offset_in(tick, uniform_sizes(slice_count))


## Precision tier for an offset on a 6-slice wheel. There is no Miss tier.
static func tier(offset: int) -> RC.PrecisionTier:
	match absi(offset):
		0:
			return RC.PrecisionTier.PERFECT
		1:
			return RC.PrecisionTier.GOOD
		_:
			return RC.PrecisionTier.WEAK


## Inner ring segment (0-2) under `inner_tick`; segment k is centred on tick 10*k.
static func ring_segment(inner_tick: int) -> int:
	return int(floor(float(posmod(inner_tick + RC.TICKS_PER_RING_SEGMENT / 2, TICKS)) / RC.TICKS_PER_RING_SEGMENT))


## Signed ticks from the centre of the inner-ring segment under `inner_tick` (-5..+4; a tick
## half way goes to the clockwise segment, as ring_segment reads it).
static func ring_offset(inner_tick: int) -> int:
	var half := RC.TICKS_PER_RING_SEGMENT / 2
	return posmod(inner_tick + half, TICKS) % RC.TICKS_PER_RING_SEGMENT - half


## Ticks (signed, shortest way) from `tick` to the centre of its slot on a wheel of
## `slice_count` equal slots.
static func snap_delta(tick: int, slice_count: int = RC.SLICES) -> int:
	return -offset_at(tick, slice_count)


## Centre tick of slice `index` on a wheel of `slice_count` equal slots.
static func slice_center(index: int, slice_count: int = RC.SLICES) -> int:
	return center_tick(index, uniform_sizes(slice_count))
