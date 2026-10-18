class_name WheelData
extends Resource
## A wheel's starting layout. Runtime position, remaining resistance and
## statuses live in a separate state object, never on this resource.

## 6 for operatives and enemies; 2-3 for satellites.
@export_range(2, 6) var slice_count: int = RC.SLICES
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


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if RC.TICKS % slice_count != 0:
		errors.append("slice_count %d does not divide %d ticks." % [slice_count, RC.TICKS])
	if slots.size() != slice_count:
		errors.append("Wheel needs %d slots, has %d." % [slice_count, slots.size()])
	for i in slots.size():
		if slots[i] == null or slots[i].slice == null:
			errors.append("Slot %d has no slice." % i)
		elif slots[i].firmware and not slots[i].firmware.allowed_slice_types.is_empty() \
				and not slots[i].slice.slice_type in slots[i].firmware.allowed_slice_types:
			errors.append("Slot %d firmware does not fit its slice type." % i)
	if pointer_ticks.is_empty():
		errors.append("Wheel needs at least one pointer.")
	errors.append_array(pointer_errors(pointer_ticks))
	if inner_ring:
		errors.append_array(inner_ring.validate())
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
