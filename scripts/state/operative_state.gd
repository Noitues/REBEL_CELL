class_name OperativeState
extends RefCounted
## One operative (GDD 5.1): class, current wheel layout (slices + Firmware sockets),
## deck, Daemons, HP and Rank. Content is referenced by id. Lives in the campaign
## roster; a netrun works on a copy that is written back only on completion.

var id: StringName = &""
var name: String = ""
var class_id: StringName = &""
var rank: int = 0
var hp: int = 1
var max_hp: int = 1
var deck: Array[StringName] = []
var slot_slice_ids: Array[StringName] = []
var slot_firmware_ids: Array[StringName] = []
var daemon_ids: Array[StringName] = []
var alive: bool = true
## Netruns survived with this operative (informational; Rank is the rule value).
var runs_completed: int = 0


static func from_class(class_data: ClassData, p_id: StringName, p_name: String = "") -> OperativeState:
	var o := OperativeState.new()
	o.id = p_id
	o.name = p_name if p_name != "" else String(p_id)
	o.class_id = class_data.id
	o.max_hp = class_data.base_hp
	o.hp = class_data.base_hp
	for c in class_data.starting_deck:
		if c != null:
			o.deck.append(c.id)
	for slot in class_data.starting_wheel.slots:
		o.slot_slice_ids.append(slot.slice.id if slot.slice != null else &"")
		o.slot_firmware_ids.append(slot.firmware.id if slot.firmware != null else &"")
	return o


## Ring id understood by CombatSession ("rank:N") for the highest reward this rank has.
func ring_id(class_data: ClassData) -> StringName:
	var best := 0
	for reward in class_data.rank_rewards:
		if reward != null and reward.inner_ring != null and reward.rank <= rank and reward.rank > best:
			best = reward.rank
	return StringName("rank:%d" % best) if best > 0 else &""


func has_daemon(daemon_id: StringName) -> bool:
	return daemon_ids.has(daemon_id)


func duplicate_state() -> OperativeState:
	return from_dict(to_dict())


func to_dict() -> Dictionary:
	return {
		"id": String(id), "name": name, "class_id": String(class_id), "rank": rank,
		"hp": hp, "max_hp": max_hp,
		"deck": _strings(deck), "slot_slice_ids": _strings(slot_slice_ids),
		"slot_firmware_ids": _strings(slot_firmware_ids), "daemon_ids": _strings(daemon_ids),
		"alive": alive, "runs_completed": runs_completed,
	}


static func from_dict(d: Dictionary) -> OperativeState:
	var o := OperativeState.new()
	o.id = StringName(String(d.get("id", "")))
	o.name = String(d.get("name", ""))
	o.class_id = StringName(String(d.get("class_id", "")))
	o.rank = int(d.get("rank", 0))
	o.hp = int(d.get("hp", 1))
	o.max_hp = int(d.get("max_hp", 1))
	o.deck = _names(d.get("deck", []))
	o.slot_slice_ids = _names(d.get("slot_slice_ids", []))
	o.slot_firmware_ids = _names(d.get("slot_firmware_ids", []))
	o.daemon_ids = _names(d.get("daemon_ids", []))
	o.alive = bool(d.get("alive", true))
	o.runs_completed = int(d.get("runs_completed", 0))
	return o


static func _strings(names: Array[StringName]) -> Array:
	var out := []
	for n in names:
		out.append(String(n))
	return out


static func _names(strings: Array) -> Array[StringName]:
	var out: Array[StringName] = []
	for s in strings:
		out.append(StringName(String(s)))
	return out
