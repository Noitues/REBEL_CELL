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
var pointer_ticks: PackedInt32Array = PackedInt32Array([0])
var frozen: bool = false
## The wheel skipped its respin this turn (it was frozen). It cannot be frozen again until
## it has respun (decision 2026-09-24: closes the Anchor / Freeze perpetual lock).
var respin_skipped: bool = false
## One RC.Status per slot (temporary statuses; permanent ones come from Firmware).
var slice_statuses: Array[int] = []
var passive_resistance: int = 0
## Ticks every pointer moves at each start of turn (Recall Unit orbit).
var pointer_orbit: int = 0
## MIGRATE telegraph (GDD 2.11): the layout the pointers move to at the next start of
## turn; empty when no migration is pending.
var pending_pointer_ticks: PackedInt32Array = PackedInt32Array()


## Builds the starting state of `data`, optionally with an installed Inner Ring and an
## operative's own layout (slice ids and Firmware sockets) in place of the data's.
static func from_wheel_data(data: WheelData, ring: InnerRingData = null, slice_ids: Array[StringName] = [], firmware_ids: Array[StringName] = [], segment_ids: Array[StringName] = []) -> WheelState:
	var w := WheelState.new()
	w.slice_count = data.slice_count
	for i in data.slots.size():
		var slot := data.slots[i]
		w.slot_slice_ids.append(slice_ids[i] if i < slice_ids.size() else (slot.slice.id if slot.slice != null else &""))
		w.slot_firmware_ids.append(firmware_ids[i] if i < firmware_ids.size() else (slot.firmware.id if slot.firmware != null else &""))
		w.slice_statuses.append(RC.Status.NONE)
	w.pointer_orbit = data.pointer_orbit_per_turn
	w.hub_id = data.hub.id if data.hub != null else &""
	var ring_data := ring if ring != null else data.inner_ring
	if ring_data != null:
		for k in ring_data.segments.size():
			var seg := ring_data.segments[k]
			# Rank 3 segment swaps (GDD 6.4): the operative's own choice replaces the class default.
			if k < segment_ids.size() and segment_ids[k] != &"":
				w.ring_segment_ids.append(segment_ids[k])
			else:
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
	return WheelMath.tick_at(rotation, pointer_ticks[pointer_index])


## Inner-ring tick under pointer `pointer_index`.
func inner_tick_at(pointer_index: int) -> int:
	return WheelMath.tick_at(inner_rotation, pointer_ticks[pointer_index])


## Slice index under pointer `pointer_index`.
func slice_at(pointer_index: int) -> int:
	return WheelMath.slice_at(tick_at(pointer_index), slice_count)


## Mirrors the wheel across the horizontal axis (GDD 2.3, designer ruling 2026-09-24):
## the physical slices swap positions (slot i -> -i mod n, statuses and Firmware with
## them), both rings included, and the rotation is remapped so the tick under the top
## pointer becomes 15 - t. Orientation stays clockwise, so nudges and spins are unchanged.
## Flipping twice restores the wheel exactly. Docked satellites are the caller's job.
func flip() -> void:
	rotation = -rotation - WheelMath.FLIP_OFFSET
	slot_slice_ids = _mirrored_names(slot_slice_ids)
	slot_firmware_ids = _mirrored_names(slot_firmware_ids)
	var statuses: Array[int] = []
	for i in slice_statuses.size():
		statuses.append(slice_statuses[WheelMath.mirrored_slot(i, slice_count)])
	slice_statuses = statuses
	if has_inner_ring():
		inner_rotation = -inner_rotation - WheelMath.FLIP_OFFSET
		var segs: Array[StringName] = []
		for k in ring_segment_ids.size():
			segs.append(ring_segment_ids[WheelMath.mirrored_slot(k, RC.RING_SEGMENTS)])
		ring_segment_ids = segs


func _mirrored_names(names: Array[StringName]) -> Array[StringName]:
	var out: Array[StringName] = []
	for i in names.size():
		out.append(names[WheelMath.mirrored_slot(i, names.size())])
	return out


func duplicate_state() -> WheelState:
	var w := WheelState.new()
	w.slice_count = slice_count
	w.slot_slice_ids = slot_slice_ids.duplicate()
	w.slot_firmware_ids = slot_firmware_ids.duplicate()
	w.hub_id = hub_id
	w.ring_segment_ids = ring_segment_ids.duplicate()
	w.rotation = rotation
	w.inner_rotation = inner_rotation
	w.pointer_ticks = pointer_ticks.duplicate()
	w.frozen = frozen
	w.respin_skipped = respin_skipped
	w.slice_statuses = slice_statuses.duplicate()
	w.passive_resistance = passive_resistance
	w.pointer_orbit = pointer_orbit
	w.pending_pointer_ticks = pending_pointer_ticks.duplicate()
	return w


## Moves every pointer by the orbit amount (start of turn).
func orbit_pointers() -> void:
	if pointer_orbit == 0:
		return
	for i in pointer_ticks.size():
		pointer_ticks[i] = posmod(pointer_ticks[i] + pointer_orbit, RC.TICKS)


## Applies a telegraphed MIGRATE layout. Returns true when the pointers moved.
func apply_pending_pointers() -> bool:
	if pending_pointer_ticks.is_empty():
		return false
	pointer_ticks = pending_pointer_ticks.duplicate()
	pending_pointer_ticks = PackedInt32Array()
	return true


func to_dict() -> Dictionary:
	return {
		"slice_count": slice_count,
		"slot_slice_ids": _names_to_strings(slot_slice_ids),
		"slot_firmware_ids": _names_to_strings(slot_firmware_ids),
		"hub_id": String(hub_id),
		"ring_segment_ids": _names_to_strings(ring_segment_ids),
		"rotation": rotation,
		"inner_rotation": inner_rotation,
		"pointer_ticks": Array(pointer_ticks),
		"frozen": frozen,
		"respin_skipped": respin_skipped,
		"slice_statuses": slice_statuses.duplicate(),
		"passive_resistance": passive_resistance,
		"pointer_orbit": pointer_orbit,
		"pending_pointer_ticks": Array(pending_pointer_ticks),
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
	w.pointer_ticks = PackedInt32Array()
	for t in d.get("pointer_ticks", [0]):
		w.pointer_ticks.append(int(t))
	w.frozen = bool(d.get("frozen", false))
	w.respin_skipped = bool(d.get("respin_skipped", false))
	w.slice_statuses = []
	for s in d.get("slice_statuses", []):
		w.slice_statuses.append(int(s))
	w.passive_resistance = int(d.get("passive_resistance", 0))
	w.pointer_orbit = int(d.get("pointer_orbit", 0))
	w.pending_pointer_ticks = PackedInt32Array()
	for t in d.get("pending_pointer_ticks", []):
		w.pending_pointer_ticks.append(int(t))
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
