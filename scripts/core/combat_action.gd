class_name CombatAction
extends RefCounted
## One player input as plain data (TECH_SPEC 5.4). Recorded for rewind and replay.

enum Type { PLAY_CARD, NUDGE, TARGET, END_TURN }

var type: int = Type.END_TURN
## PLAY_CARD: index into CombatState.hand.
var hand_index: int = -1
## NUDGE: combatant whose wheel moves. PLAY_CARD with wheel_target ANY/SATELLITE: the
## chosen wheel. TARGET: the new target. Empty means "use the current target".
var wheel_id: StringName = &""
## NUDGE: RC.RingScope.OUTER or INNER. For cards, -1 keeps the effect's own ring_scope.
var ring: int = -1
## NUDGE: +1 clockwise, -1 counter-clockwise.
var direction: int = 1
## Cards whose effect picks a slice (SlicePick.CHOSEN).
var slot_index: int = -1


static func play_card(index: int, wheel: StringName = &"", slot: int = -1) -> CombatAction:
	var a := CombatAction.new()
	a.type = Type.PLAY_CARD
	a.hand_index = index
	a.wheel_id = wheel
	a.slot_index = slot
	return a


static func nudge(wheel: StringName, p_direction: int, p_ring: int = RC.RingScope.OUTER) -> CombatAction:
	var a := CombatAction.new()
	a.type = Type.NUDGE
	a.wheel_id = wheel
	a.direction = signi(p_direction)
	a.ring = p_ring
	return a


static func target(wheel: StringName) -> CombatAction:
	var a := CombatAction.new()
	a.type = Type.TARGET
	a.wheel_id = wheel
	return a


static func end_turn() -> CombatAction:
	var a := CombatAction.new()
	a.type = Type.END_TURN
	return a


func to_dict() -> Dictionary:
	return {
		"type": type,
		"hand_index": hand_index,
		"wheel_id": String(wheel_id),
		"ring": ring,
		"direction": direction,
		"slot_index": slot_index,
	}


static func from_dict(d: Dictionary) -> CombatAction:
	var a := CombatAction.new()
	a.type = int(d.get("type", Type.END_TURN))
	a.hand_index = int(d.get("hand_index", -1))
	a.wheel_id = StringName(String(d.get("wheel_id", "")))
	a.ring = int(d.get("ring", -1))
	a.direction = int(d.get("direction", 1))
	a.slot_index = int(d.get("slot_index", -1))
	return a


func describe() -> String:
	match type:
		Type.PLAY_CARD:
			return "play card %d" % hand_index
		Type.NUDGE:
			return "nudge %s %s %s" % [wheel_id, "+1" if direction > 0 else "-1", "inner" if ring == RC.RingScope.INNER else "outer"]
		Type.TARGET:
			return "target %s" % wheel_id
		_:
			return "end turn"
