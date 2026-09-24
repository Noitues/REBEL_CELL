class_name WheelState
extends RefCounted
## Runtime state of one wheel (TECH_SPEC 5.2). Layout is referenced by content id so
## the state serialises without touching Resources; position and statuses live here.

var slice_count: int = RC.SLICES
var slot_slice_ids: Array[StringName] = []
## Same length as slot_slice_ids; &"" means no Firmware in that socket.
var slot_firmware_ids: Array[StringName] = []
var hub_id: StringName = &""
## Three segment ids when an Inner Ring is installed, otherwise empty.
var ring_segment_ids: Array[StringName] = []
## Unbounded so views can animate spin direction and distance.
var rotation: int = 0
var inner_rotation: int = 0
var flipped: bool = false
var pointer_ticks: PackedInt32Array = PackedInt32Array([0])
var frozen: bool = false
## One RC.Status per slot (temporary statuses; permanent ones come from Firmware).
var slice_statuses: Array[int] = []
var passive_resistance: int = 0


## Builds the starting state of `data`, optionally with an installed Inner Ring.
static func from_wheel_data(data: WheelData, ring: InnerRingData = null) -> WheelState:
	var w := WheelState.new()
	w.slice_count = data.slice_count
	for slot in data.slots:
		w.slot_slice_ids.append(slot.slice.id if slot.slice != null else &"")
		w.slot_firmware_ids.append(slot.firmware.id if slot.firmware != null else &"")
		w.slice_statuses.append(RC.Status.NONE)
	w.hub_id = data.hub.id if data.hub != null else &""
	var ring_data := ring if ring != null else data.inner_ring
	if ring_data != null:
		for seg in ring_data.segments:
			w.ring_segment_ids.append(seg.id if seg != null else &"")
	w.pointer_ticks = data.pointer_ticks.duplicate()
	w.passive_resistance = data.passive_resistance
	return w


func has_inner_ring() -> bool:
	return not ring_segment_ids.is_empty()


func ticks_per_slice() -> int:
	return WheelMath.ticks_per_slice(slice_count)


## Outer-ring tick under pointer `pointer_index`.
func tick_at(pointer_index: int) -> int:
	return WheelMath.tick_at(rotation, pointer_ticks[pointer_index], flipped)


## Inner-ring tick under pointer `pointer_index`.
func inner_tick_at(pointer_index: int) -> int:
	return WheelMath.tick_at(inner_rotation, pointer_ticks[pointer_index], flipped)


## Slice index under pointer `pointer_index`.
func slice_at(pointer_index: int) -> int:
	return WheelMath.slice_at(tick_at(pointer_index), slice_count)


func duplicate_state() -> WheelState:
	var w := WheelState.new()
	w.slice_count = slice_count
	w.slot_slice_ids = slot_slice_ids.duplicate()
	w.slot_firmware_ids = slot_firmware_ids.duplicate()
	w.hub_id = hub_id
	w.ring_segment_ids = ring_segment_ids.duplicate()
	w.rotation = rotation
	w.inner_rotation = inner_rotation
	w.flipped = flipped
	w.pointer_ticks = pointer_ticks.duplicate()
	w.frozen = frozen
	w.slice_statuses = slice_statuses.duplicate()
	w.passive_resistance = passive_resistance
	return w


func to_dict() -> Dictionary:
	return {
		"slice_count": slice_count,
		"slot_slice_ids": _names_to_strings(slot_slice_ids),
		"slot_firmware_ids": _names_to_strings(slot_firmware_ids),
		"hub_id": String(hub_id),
		"ring_segment_ids": _names_to_strings(ring_segment_ids),
		"rotation": rotation,
		"inner_rotation": inner_rotation,
		"flipped": flipped,
		"pointer_ticks": Array(pointer_ticks),
		"frozen": frozen,
		"slice_statuses": slice_statuses.duplicate(),
		"passive_resistance": passive_resistance,
	}


static func from_dict(d: Dictionary) -> WheelState:
	var w := WheelState.new()
	w.slice_count = int(d.get("slice_count", RC.SLICES))
	w.slot_slice_ids = _strings_to_names(d.get("slot_slice_ids", []))
	w.slot_firmware_ids = _strings_to_names(d.get("slot_firmware_ids", []))
	w.hub_id = StringName(String(d.get("hub_id", "")))
	w.ring_segment_ids = _strings_to_names(d.get("ring_segment_ids", []))
	w.rotation = int(d.get("rotation", 0))
	w.inner_rotation = int(d.get("inner_rotation", 0))
	w.flipped = bool(d.get("flipped", false))
	w.pointer_ticks = PackedInt32Array()
	for t in d.get("pointer_ticks", [0]):
		w.pointer_ticks.append(int(t))
	w.frozen = bool(d.get("frozen", false))
	w.slice_statuses = []
	for s in d.get("slice_statuses", []):
		w.slice_statuses.append(int(s))
	w.passive_resistance = int(d.get("passive_resistance", 0))
	return w


static func _names_to_strings(names: Array[StringName]) -> Array:
	var out := []
	for n in names:
		out.append(String(n))
	return out


static func _strings_to_names(strings: Array) -> Array[StringName]:
	var out: Array[StringName] = []
	for s in strings:
		out.append(StringName(String(s)))
	return out
