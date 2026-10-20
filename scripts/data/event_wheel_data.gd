class_name EventWheelData
extends Resource
## Plan 2 EV-01 (N17 subset): a 30-tick wheel an event choice spins. The start tick is drawn
## once from the `events` RNG stream when the choice is taken (kept in the run, so a reload
## cannot reroll). The pointer is nudged one tick at a time (wrapping), the slice under it is
## named before and after every nudge, and committing resolves that slice. Nothing random
## happens after the start tick, so a preview equals the result.

@export var id: StringName = &""
## Slices in tick order from tick 0; sizes sum to RC.TICKS.
@export var slices: Array[EventWheelSliceData] = []
## Nudges that cost nothing.
@export var free_nudges: int = 0
## What one nudge past the free ones costs, by currency (0 = that currency is not offered).
@export var extra_nudge_hp: int = 0
@export var extra_nudge_heat: int = 0
@export var extra_nudge_cycles: int = 0
## Paid nudges allowed at most.
@export var max_extra_nudges: int = 0


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	var total := 0
	for s in slices:
		if s == null:
			errors.append("event_wheel_slice_null: a null slice.")
			continue
		total += s.size_ticks
		errors.append_array(s.validate())
	if total != RC.TICKS:
		errors.append("event_wheel_ticks: slice sizes sum to %d, expected %d." % [total, RC.TICKS])
	if slices.size() < 2:
		errors.append("event_wheel_slices_lt_2: %d slice(s)." % slices.size())
	if free_nudges < 0 or max_extra_nudges < 0:
		errors.append("event_wheel_nudges_lt_0: free %d, extra %d." % [free_nudges, max_extra_nudges])
	if max_extra_nudges > 0 and extra_nudge_hp <= 0 and extra_nudge_heat <= 0 and extra_nudge_cycles <= 0:
		errors.append("event_wheel_extra_unpriced: paid nudges allowed but no currency offered.")
	return errors
