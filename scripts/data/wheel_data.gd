class_name WheelData
extends Resource
## A wheel's starting layout. Runtime position, remaining resistance and
## statuses live in a separate state object, never on this resource.

## The number of slots: 6 for operatives (CampaignConfigData.operative_slice_cap), any
## count up to enemy_slice_cap for enemies (plan 2 N12), 2-3 for satellites.
@export_range(1, 30) var slice_count: int = RC.SLICES
@export var slots: Array[WheelSlotData] = []
@export var hub: HubCoreData
@export var inner_ring: InnerRingData
## Tick positions of this wheel's pointers. Bosses can have several.
@export var pointer_ticks: PackedInt32Array = PackedInt32Array([0])
## Passive-trait resistance (enemies).
@export var passive_resistance: int = 0
## Non-boss orbit: every pointer moves this many ticks at each start of turn
## (Recall Unit: +2). Bosses use BossPhaseData instead.
@export var pointer_orbit_per_turn: int = 0
@export var resistance_refresh: RC.ResistanceRefresh = RC.ResistanceRefresh.EACH_PLAYER_TURN


func ticks_per_slice() -> int:
	return RC.TICKS / slice_count


## Whether every slot takes an equal share (RC.SIZE_AUTO): the legacy layout.
func is_auto_sized() -> bool:
	for slot in slots:
		if slot != null and slot.size_ticks != RC.SIZE_AUTO:
			return false
	return true


## Plan 2 N12: the slot sizes in ticks, clockwise from slot 0 (WheelMath's layout). All AUTO
## is the equal layout (30 / slice_count each); otherwise each slot's own size_ticks.
func slot_sizes() -> PackedInt32Array:
	if is_auto_sized():
		return WheelMath.uniform_sizes(slice_count)
	var out := PackedInt32Array()
	for slot in slots:
		out.append(slot.size_ticks if slot != null else 0)
	return out


## Plan 2 N12: each slot's authored quality map (an empty array = the default for its size).
func slot_quality() -> Array[PackedInt32Array]:
	var out: Array[PackedInt32Array] = []
	for slot in slots:
		out.append(slot.tick_quality.duplicate() if slot != null else PackedInt32Array())
	return out


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if is_auto_sized() and RC.TICKS % slice_count != 0:
		errors.append("slice_count %d does not divide %d ticks." % [slice_count, RC.TICKS])
	if slots.size() != slice_count:
		errors.append("Wheel needs %d slots, has %d." % [slice_count, slots.size()])
	for i in slots.size():
		if slots[i] == null or slots[i].slice == null:
			errors.append("Slot %d has no slice." % i)
		elif slots[i].firmware and not slots[i].firmware.allowed_slice_types.is_empty() \
				and not slots[i].slice.slice_type in slots[i].firmware.allowed_slice_types:
			errors.append("Slot %d firmware does not fit its slice type." % i)
	if slots.size() == slice_count:
		errors.append_array(size_errors())
	if pointer_ticks.is_empty():
		errors.append("Wheel needs at least one pointer.")
	errors.append_array(pointer_errors(pointer_ticks))
	if inner_ring:
		errors.append_array(inner_ring.validate())
	return errors


## Plan 2 N12 (R11, Q20): the slot-size problems, each starting with its reason name.
## size_mixed: AUTO and sized slots on one wheel; size_range: a size outside 0-30;
## size_sum: sizes that do not add up to 30; quality_length: a quality map whose length is
## not its slot's size; quality_tier: a map entry that is not a precision tier.
func size_errors() -> PackedStringArray:
	var errors := PackedStringArray()
	var sized := 0
	for slot in slots:
		if slot != null and slot.size_ticks != RC.SIZE_AUTO:
			sized += 1
	if sized > 0 and sized < slots.size():
		errors.append("size_mixed: %d of %d slots have a size; size all of them or none." % [sized, slots.size()])
		return errors
	var sizes := slot_sizes()
	var total := 0
	for i in sizes.size():
		if sizes[i] < 0 or sizes[i] > RC.TICKS:
			errors.append("size_range: Slot %d is %d ticks; sizes run 0-%d." % [i, sizes[i], RC.TICKS])
		total += sizes[i]
	if total != RC.TICKS:
		errors.append("size_sum: Slot sizes add up to %d, not %d." % [total, RC.TICKS])
	for i in slots.size():
		var q := slots[i].tick_quality if slots[i] != null else PackedInt32Array()
		if q.is_empty():
			continue
		if q.size() != sizes[i]:
			errors.append("quality_length: Slot %d has %d quality entries for %d ticks." % [i, q.size(), sizes[i]])
		for t in q:
			if t < RC.PrecisionTier.WEAK or t > RC.PrecisionTier.PERFECT:
				errors.append("quality_tier: Slot %d has quality %d, not a precision tier." % [i, t])
				break
	return errors


## Plan 2 N12 (Q20): the config limits. A slot with ticks is a slice; 0-size slots are empty
## arcs and do not count (slice_cap: more slices than `max_slices`). A non-zero size under
## `min_size` is size_range.
func slice_cap_errors(max_slices: int, min_size: int) -> PackedStringArray:
	var errors := PackedStringArray()
	if size_errors().size() > 0 or slots.size() != slice_count:
		return errors
	var sizes := slot_sizes()
	var slices := 0
	for i in sizes.size():
		if sizes[i] > 0:
			slices += 1
			if sizes[i] < min_size:
				errors.append("size_range: Slot %d is %d ticks; the smallest slice is %d." % [i, sizes[i], min_size])
	if slices > max_slices:
		errors.append("slice_cap: %d slices; the cap is %d." % [slices, max_slices])
	return errors


## N11 (GDD 2.1, Q27): a pointer layout's problems, each starting with its reason name.
## Pointers sit on any tick 0-29 (pointer_tick_out_of_range), at least 1 tick apart: two
## on one tick is pointer_ticks_duplicate. The count cap (too_many_pointers) needs the
## config: EnemyData.validate checks it.
static func pointer_errors(ticks: PackedInt32Array) -> PackedStringArray:
	var errors := PackedStringArray()
	var seen := {}
	for t in ticks:
		if t < 0 or t >= RC.TICKS:
			errors.append("pointer_tick_out_of_range: Pointer tick %d is outside 0-%d." % [t, RC.TICKS - 1])
		elif seen.has(t):
			errors.append("pointer_ticks_duplicate: Two pointers on tick %d." % t)
		seen[t] = true
	return errors
