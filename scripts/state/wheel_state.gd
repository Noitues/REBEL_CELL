class_name WheelState
extends RefCounted
## Runtime state of one wheel (TECH_SPEC 5.2). Layout is referenced by content id so
## the state serialises without touching Resources; position and statuses live here.

## stack_limit() of an uncapped status (a definition, not a tuning number).
const NO_STACK_LIMIT: int = 1 << 30

var slice_count: int = RC.SLICES
## Plan 2 N12 (R11): each slot's size in ticks, clockwise from slot 0, summing to 30 (0 = an
## empty arc). Empty means the equal layout of slice_count (read it through layout()).
var slot_sizes: PackedInt32Array = PackedInt32Array()
## Plan 2 N12 (R11): each slot's authored quality map (one RC.PrecisionTier per tick), or an
## empty array for the default map of its size. Empty overall when no slot authors one.
var slot_quality: Array[PackedInt32Array] = []
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
## Plan 2 N7: the player-turn locks on this wheel, {kind: {"turns_left": int >= 1, "sources":
## Array[String] sorted by content id}}, kind LOCK_NUDGE or LOCK_RESPIN. A kind with no lock is
## absent. Every lock is removed at end of turn (ruling Q31); place them only through add_lock.
var locks: Dictionary = {}
## The kinds of lock (a definition, not a tuning number).
const LOCK_NUDGE: StringName = &"nudge"
const LOCK_RESPIN: StringName = &"respin"
## The temporary statuses of each slot (permanent ones come from Firmware), plan 2 N8:
## one Dictionary per slot, {RC.Status int: stacks >= 1}. A status with no stacks is never
## stored (its key is absent). Read them in RC.Status order through statuses_at(), never
## in Dictionary order; change them only through the stack functions below.
var slice_stacks: Array[Dictionary] = []
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
	if not data.is_auto_sized():
		w.slot_sizes = data.slot_sizes()
	w.set_quality_maps(data.slot_quality())
	for i in data.slots.size():
		var slot := data.slots[i]
		w.slot_slice_ids.append(slice_ids[i] if i < slice_ids.size() else (slot.slice.id if slot.slice != null else &""))
		w.slot_firmware_ids.append(firmware_ids[i] if i < firmware_ids.size() else (slot.firmware.id if slot.firmware != null else &""))
		w.slice_stacks.append({})
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


## Plan 2 N12: the slot sizes WheelMath reads (slot_sizes, or the equal layout of slice_count).
func layout() -> PackedInt32Array:
	return slot_sizes if slot_sizes.size() == slice_count else WheelMath.uniform_sizes(slice_count)


## Stores `maps` as the authored quality maps (all empty -> none stored).
func set_quality_maps(maps: Array[PackedInt32Array]) -> void:
	slot_quality = []
	for m in maps:
		if not m.is_empty():
			for k in maps:
				slot_quality.append(k.duplicate())
			return


## Slot `slot`'s authored quality map, or an empty array (the default for its size).
func quality_override(slot: int) -> PackedInt32Array:
	return slot_quality[slot] if slot >= 0 and slot < slot_quality.size() else PackedInt32Array()


## Slot `slot`'s size in ticks.
func slot_size(slot: int) -> int:
	return layout()[slot]


## The slot owning wheel tick `tick` (never a 0-size slot).
func slot_of_tick(tick: int) -> int:
	return WheelMath.slot_of_tick(tick, layout())


## Centre tick of slot `slot` (the lower of the middle pair on an even size).
func slot_center_tick(slot: int) -> int:
	return WheelMath.center_tick(slot, layout())


## Middle of slot `slot`'s drawn arc as a fractional wheel tick (views centre wedges on it).
func slot_arc_mid(slot: int) -> float:
	return WheelMath.arc_mid(slot, layout())


## Outer-ring tick under pointer `pointer_index`.
func tick_at(pointer_index: int) -> int:
	return WheelMath.tick_at(rotation, pointer_ticks[pointer_index])


## Inner-ring tick under pointer `pointer_index`.
func inner_tick_at(pointer_index: int) -> int:
	return WheelMath.tick_at(inner_rotation, pointer_ticks[pointer_index])


## Slice index under pointer `pointer_index`.
func slice_at(pointer_index: int) -> int:
	return WheelMath.slot_of_tick(tick_at(pointer_index), layout())


## Mirrors the wheel across the horizontal axis (GDD 2.3, designer ruling 2026-09-24):
## the physical slices swap positions (slot i -> -i mod n, statuses and Firmware with
## them), both rings included, and the rotation is remapped so the tick under the top
## pointer becomes 15 - t. Orientation stays clockwise, so nudges and spins are unchanged.
## Flipping twice restores the wheel exactly. Docked satellites are the caller's job.
## Plan 2 N12: slot sizes and quality maps mirror with their slots (a map reads backwards),
## and an even slot 0 shifts the rotation one tick (WheelMath.flip_shift) so every arc lands
## exactly on its mirror image.
func flip() -> void:
	rotation = -rotation - WheelMath.FLIP_OFFSET + WheelMath.flip_shift(layout())
	if not slot_sizes.is_empty():
		slot_sizes = WheelMath.mirrored_sizes(slot_sizes)
	if not slot_quality.is_empty():
		var maps: Array[PackedInt32Array] = []
		for i in slot_quality.size():
			var m := slot_quality[WheelMath.mirrored_slot(i, slot_quality.size())].duplicate()
			m.reverse()
			maps.append(m)
		slot_quality = maps
	slot_slice_ids = _mirrored_names(slot_slice_ids)
	slot_firmware_ids = _mirrored_names(slot_firmware_ids)
	var stacks: Array[Dictionary] = []
	for i in slice_stacks.size():
		stacks.append(slice_stacks[WheelMath.mirrored_slot(i, slice_count)])
	slice_stacks = stacks
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


## Plan 2 R6 with N8 stacks: the statuses of a change between two equal layouts
## (remap_stacks_sized with the equal sizes of each count).
static func remap_stacks(old_stacks: Array[Dictionary], old_count: int, new_count: int, cap: int) -> Array[Dictionary]:
	return remap_stacks_sized(old_stacks, WheelMath.uniform_sizes(old_count), WheelMath.uniform_sizes(new_count), cap)


## Plan 2 R6 with N8 stacks and N12 sizes: each old slot's stacks move to the new slot that
## owns the old slot's centre tick (WheelMath.center_tick; a tick on a boundary belongs to the
## slot clockwise of it, as every pointer reads it: designer W1 N12). Stacks landing on one
## slot merge: the same status adds up (to `cap`, RC.UNCAPPED_STATUSES excepted), different
## ones sit side by side. Pure; returns one entry per new slot.
static func remap_stacks_sized(old_stacks: Array[Dictionary], old_sizes: PackedInt32Array, new_sizes: PackedInt32Array, cap: int) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for j in new_sizes.size():
		out.append({})
	for i in mini(old_stacks.size(), old_sizes.size()):
		var j := WheelMath.slot_of_tick(WheelMath.center_tick(i, old_sizes), new_sizes)
		for st in sorted_statuses(old_stacks[i]):
			var n: int = mini(int(out[j].get(st, 0)) + int(old_stacks[i][st]), stack_limit(st, cap))
			out[j][st] = n
	return out


# --- Slot status stacks (plan 2 N8) ------------------------------------------------

## The keys of a slot's stack Dictionary in RC.Status order (the only order statuses are
## read in: hashing, resolving and views never use Dictionary order).
static func sorted_statuses(stacks: Dictionary) -> Array[int]:
	var status_ints: Array[int] = []
	for k in stacks.keys():
		status_ints.append(int(k))
	status_ints.sort()  # ints, not ids: plain numeric order
	return status_ints


## The most stacks `status` may hold on one slot under `cap` (CampaignConfigData
## status_stack_cap); RC.UNCAPPED_STATUSES have no limit.
static func stack_limit(status: int, cap: int) -> int:
	return NO_STACK_LIMIT if status in RC.UNCAPPED_STATUSES else maxi(1, cap)


## Stacks of `status` on slot `slot` (0 when absent).
func stacks_of(slot: int, status: int) -> int:
	if slot < 0 or slot >= slice_stacks.size():
		return 0
	return int(slice_stacks[slot].get(status, 0))


## Whether slot `slot` holds at least one stack of `status`.
func has_status(slot: int, status: int) -> bool:
	return stacks_of(slot, status) > 0


## Whether slot `slot` holds any temporary status.
func has_any_status(slot: int) -> bool:
	return slot >= 0 and slot < slice_stacks.size() and not slice_stacks[slot].is_empty()


## The statuses on slot `slot`, in RC.Status order.
func statuses_at(slot: int) -> Array[int]:
	if slot < 0 or slot >= slice_stacks.size():
		return []
	return sorted_statuses(slice_stacks[slot])


## The status a one-badge view shows for slot `slot`: the first in RC.Status order, or NONE.
func status_at(slot: int) -> int:
	var all := statuses_at(slot)
	return all[0] if not all.is_empty() else RC.Status.NONE


## How many slots carry `status`.
func count_status(status: int) -> int:
	var n := 0
	for i in slice_stacks.size():
		if has_status(i, status):
			n += 1
	return n


## Adds `amount` stacks of `status` to slot `slot`, up to stack_limit(status, cap). Returns
## the stacks actually added (0 for amount <= 0 or a full slot).
func add_stacks(slot: int, status: int, amount: int, cap: int) -> int:
	if amount <= 0 or status == RC.Status.NONE or slot < 0 or slot >= slice_stacks.size():
		return 0
	var had := stacks_of(slot, status)
	var now := mini(had + amount, stack_limit(status, cap))
	if now > had:
		slice_stacks[slot][status] = now
	return now - had


## Removes `amount` stacks of `status` from slot `slot` (amount <= 0: all of them); the key
## goes when none remain. Returns the stacks removed.
func remove_stacks(slot: int, status: int, amount: int = 0) -> int:
	var had := stacks_of(slot, status)
	if had == 0:
		return 0
	var gone := had if amount <= 0 else mini(amount, had)
	if gone == had:
		slice_stacks[slot].erase(status)
	else:
		slice_stacks[slot][status] = had - gone
	return gone


## Replaces slot `slot`'s statuses with `stacks` of `status` alone (NONE or stacks <= 0
## clears the slot). For setups, labs and tests; rules use add_stacks / remove_stacks.
func set_status(slot: int, status: int, stacks: int = 1) -> void:
	if slot < 0 or slot >= slice_stacks.size():
		return
	slice_stacks[slot] = {}
	if status != RC.Status.NONE and stacks > 0:
		slice_stacks[slot][status] = stacks


## Clears every status on slot `slot`.
func clear_slot(slot: int) -> void:
	if slot >= 0 and slot < slice_stacks.size():
		slice_stacks[slot] = {}


## A deep copy of the slot stacks (snapshots and resolution readouts).
func copy_stacks() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for d in slice_stacks:
		out.append(d.duplicate())
	return out


## One slot's stacks as JSON: String keys in RC.Status order (a hash reads the same string
## whatever order the stacks were added in).
static func stacks_to_json(stacks: Dictionary) -> Dictionary:
	var out := {}
	for st in sorted_statuses(stacks):
		out[str(st)] = int(stacks[st])
	return out


## One slot's stacks from JSON (String or number keys; numbers as floats). Entries with
## fewer than 1 stack are dropped; save validation rejects them first (SaveMigration).
static func stacks_from_json(d: Dictionary) -> Dictionary:
	var out := {}
	for k in d.keys():
		var st: int = int(String(k).to_int()) if k is String else int(k)
		var n := int(d[k])
		if st != RC.Status.NONE and n > 0:
			out[st] = n
	var ordered := {}
	for st in sorted_statuses(out):
		ordered[st] = out[st]
	return ordered


## The slot of a `count`-slice equal wheel that owns `tick`; a boundary tick belongs to the
## slot clockwise of it (plan 2 N12, designer W1 N12: as every pointer reads it).
static func covering_slot(tick: int, count: int) -> int:
	return WheelMath.slice_at(tick, count)


## Locks `kind` with `turns` turns left, named for `source`. Two locks merge: the larger
## turns_left wins (never the sum) and the sources are kept sorted by content id. Returns
## false (no lock) for turns < 1.
func add_lock(kind: StringName, source: StringName, turns: int) -> bool:
	if turns < 1:
		return false
	var entry: Dictionary = locks.get(String(kind), {"turns_left": 0, "sources": []})
	var sources: Array = entry["sources"]
	if source != &"" and not sources.has(String(source)):
		sources.append(String(source))
		IdSort.sort_ids(sources)
	entry["turns_left"] = maxi(int(entry["turns_left"]), turns)
	entry["sources"] = sources
	locks[String(kind)] = entry
	return true


## Whether `kind` is locked on this wheel.
func is_locked(kind: StringName) -> bool:
	return locks.has(String(kind))


## The sources of `kind`'s lock, sorted by content id (empty when not locked).
func lock_sources(kind: StringName) -> Array:
	if not locks.has(String(kind)):
		return []
	return (locks[String(kind)]["sources"] as Array).duplicate()


## The turns left on `kind`'s lock (0 when not locked).
func lock_turns(kind: StringName) -> int:
	return int(locks[String(kind)]["turns_left"]) if locks.has(String(kind)) else 0


## Removes every lock (end of turn, combat end).
func clear_locks() -> void:
	locks.clear()


func duplicate_state() -> WheelState:
	var w := WheelState.new()
	w.slice_count = slice_count
	w.slot_sizes = slot_sizes.duplicate()
	w.set_quality_maps(slot_quality)
	w.slot_slice_ids = slot_slice_ids.duplicate()
	w.slot_firmware_ids = slot_firmware_ids.duplicate()
	w.hub_id = hub_id
	w.ring_segment_ids = ring_segment_ids.duplicate()
	w.rotation = rotation
	w.inner_rotation = inner_rotation
	w.pointer_ticks = pointer_ticks.duplicate()
	w.frozen = frozen
	w.respin_skipped = respin_skipped
	w.locks = locks.duplicate(true)
	w.slice_stacks = copy_stacks()
	w.passive_resistance = passive_resistance
	w.pointer_orbit = pointer_orbit
	w.pending_pointer_ticks = pending_pointer_ticks.duplicate()
	return w


## Moves every pointer by the orbit amount (start of turn).
func orbit_pointers() -> void:
	pointer_ticks = orbit_ticks_after(1)


## N11: where the pointers stand after `turns` more orbits (any tick 0-29, mod 30); the
## orbit trail the wheel shows, and what `orbit_pointers` applies one turn at a time.
func orbit_ticks_after(turns: int) -> PackedInt32Array:
	var out := pointer_ticks.duplicate()
	for i in out.size():
		out[i] = posmod(out[i] + pointer_orbit * turns, RC.TICKS)
	return out


## Applies a telegraphed MIGRATE layout. Returns true when the pointers moved.
func apply_pending_pointers() -> bool:
	if pending_pointer_ticks.is_empty():
		return false
	pointer_ticks = pending_pointer_ticks.duplicate()
	pending_pointer_ticks = PackedInt32Array()
	return true


## Save v3 (N8): "slice_stacks" holds one {"<status int>": stacks} per slot, keys in
## RC.Status order (v2's "slice_statuses" int list is migrated by SaveMigration).
func to_dict() -> Dictionary:
	var stacks := []
	for d in slice_stacks:
		stacks.append(stacks_to_json(d))
	var d := {
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
		"slice_stacks": stacks,
		"passive_resistance": passive_resistance,
		"pointer_orbit": pointer_orbit,
		"pending_pointer_ticks": Array(pending_pointer_ticks),
	}
	# Save v4 (N12): absent for the equal layout and the default maps, so legacy wheels save
	# and hash exactly as before.
	if not slot_sizes.is_empty() and not WheelMath.is_uniform(slot_sizes):
		d["slot_sizes"] = Array(slot_sizes)
	if not slot_quality.is_empty():
		var maps := []
		for m in slot_quality:
			maps.append(Array(m))
		d["slot_quality"] = maps
	if not locks.is_empty():  # absent when empty: wheels without a lock hash as before N7
		var out := {}
		for kind in [String(LOCK_NUDGE), String(LOCK_RESPIN)]:
			if locks.has(kind):
				out[kind] = {"turns_left": int(locks[kind]["turns_left"]), "sources": (locks[kind]["sources"] as Array).duplicate()}
		d["locks"] = out
	return d


static func from_dict(d: Dictionary) -> WheelState:
	var w := WheelState.new()
	w.slice_count = int(d.get("slice_count", RC.SLICES))
	w.slot_sizes = PackedInt32Array()
	for t in d.get("slot_sizes", []):  # absent (v3 and the equal layout): equal slots
		w.slot_sizes.append(int(t))
	var maps: Array[PackedInt32Array] = []
	for m in d.get("slot_quality", []):
		var q := PackedInt32Array()
		if m is Array:
			for t in m:
				q.append(int(t))
		maps.append(q)
	w.set_quality_maps(maps)
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
	var saved_locks: Dictionary = d.get("locks", {})
	for kind in [String(LOCK_NUDGE), String(LOCK_RESPIN)]:
		var entry: Variant = saved_locks.get(kind)
		if entry is Dictionary and int(entry.get("turns_left", 0)) >= 1:
			var srcs: Array = []
			for x in entry.get("sources", []):
				srcs.append(String(x))
			w.locks[kind] = {"turns_left": int(entry["turns_left"]), "sources": srcs}
	w.slice_stacks = []
	for s in d.get("slice_stacks", []):
		w.slice_stacks.append(stacks_from_json(s) if s is Dictionary else {})
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
