class_name WheelMath
extends RefCounted
## Pure wheel geometry (GDD 2.3, TECH_SPEC 5.1). Static, no state, no randomness.
##
## A wheel has RC.TICKS (30) ticks. A 6-slice wheel has 5 ticks per slice; slice i is
## centred on tick 5*i. Satellites use 2-3 slices with the same functions.

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


## Ticks per slice for a wheel with `slice_count` slices (30 / count).
static func ticks_per_slice(slice_count: int) -> int:
	return TICKS / slice_count


## Index of the slice whose centre is nearest `tick`.
static func slice_at(tick: int, slice_count: int = RC.SLICES) -> int:
	var tps := ticks_per_slice(slice_count)
	return posmod(roundi(float(tick) / tps), slice_count)


## Signed distance from `tick` to the nearest slice centre (-2..+2 on 6-slice wheels).
static func offset_at(tick: int, slice_count: int = RC.SLICES) -> int:
	var tps := ticks_per_slice(slice_count)
	return tick - tps * roundi(float(tick) / tps)


## Precision tier for an offset on a 6-slice wheel. There is no Miss tier.
static func tier(offset: int) -> RC.PrecisionTier:
	match absi(offset):
		0:
			return RC.PrecisionTier.PERFECT
		1:
			return RC.PrecisionTier.GOOD
		_:
			return RC.PrecisionTier.PARTIAL


## Inner ring segment (0-2) under `inner_tick`; segment k is centred on tick 10*k.
static func ring_segment(inner_tick: int) -> int:
	return int(floor(float(posmod(inner_tick + RC.TICKS_PER_RING_SEGMENT / 2, TICKS)) / RC.TICKS_PER_RING_SEGMENT))


## Ticks (signed, shortest way) from `tick` to the centre of its nearest slice.
static func snap_delta(tick: int, slice_count: int = RC.SLICES) -> int:
	return -offset_at(tick, slice_count)


## Centre tick of slice `index`.
static func slice_center(index: int, slice_count: int = RC.SLICES) -> int:
	return posmod(index * ticks_per_slice(slice_count), TICKS)
