class_name CombatOutcome
extends RefCounted
## What an action or the End Turn resolve changes, as a diff of the state before and after
## plus the campaign effects reported as events (GDD 2.10: the preview shows the full
## outcome). Pure: views turn it into chips on the spinners, the RAM bar and the Heat
## poster; nothing here changes state.

## Combatant id -> Dictionary with the before/after values the HUD can show:
## hp, max_hp, block, shield, evade, resistance, breached, alive, statuses
## (Array of {slot, before, after}), rotation, inner_rotation, dealt (damage this
## combatant's pointers dealt, summed).
var combatants: Dictionary = {}
var ram_delta: int = 0
var cards_drawn: int = 0
## Campaign effects, raw (the caller scales Heat with HeatRules.scaled_delta).
var heat: int = 0
var cycles: int = 0
var schematics: int = 0
var free_nudges_next_turn: int = 0
var damage_bonus_delta: int = 0
var outcome: int = CombatState.Outcome.NONE
## Drones the operative gains (count).
var drones_gained: int = 0


static func between(before: CombatState, after: CombatState, events: Array[Dictionary]) -> CombatOutcome:
	var o := CombatOutcome.new()
	var ids: Array[StringName] = []
	for c in _all(before):
		ids.append(c.id)
	for c in _all(after):
		if not ids.has(c.id):
			ids.append(c.id)
	for id in ids:
		var b := before.get_combatant(id)
		var a := after.get_combatant(id)
		o.combatants[id] = _diff(b, a)
	o.ram_delta = after.ram - before.ram
	o.cards_drawn = maxi(0, after.hand.size() - before.hand.size())
	o.free_nudges_next_turn = after.free_nudges_next_turn - before.free_nudges_next_turn
	o.damage_bonus_delta = after.damage_bonus - before.damage_bonus
	o.outcome = after.outcome
	o.drones_gained = maxi(0, after.drones.size() - before.drones.size())
	for e in events:
		match String(e.get("type", "")):
			"campaign_effect":
				var amount := int(e.get("amount", 0))
				match int(e.get("effect", -1)):
					RC.EffectType.MODIFY_HEAT:
						o.heat += amount
					RC.EffectType.GAIN_CYCLES:
						o.cycles += amount
					RC.EffectType.GAIN_SCHEMATICS:
						o.schematics += amount
			"attack", "afflict":
				var src := StringName(String(e.get("attacker", "")))
				if o.combatants.has(src):
					o.combatants[src]["dealt"] = int(o.combatants[src]["dealt"]) + int(e.get("amount", 0))
	return o


static func _all(s: CombatState) -> Array[CombatantState]:
	var out: Array[CombatantState] = [s.player]
	out.append_array(s.enemies)
	out.append_array(s.drones)
	return out


static func _diff(b: CombatantState, a: CombatantState) -> Dictionary:
	var d := {"dealt": 0}
	var src := a if a != null else b
	d["name"] = src.display_name
	d["is_satellite"] = src.is_satellite
	d["host"] = src.host_id
	d["max_hp"] = src.max_hp
	for key in ["hp", "block", "shield", "resistance"]:
		d[key + "_before"] = int(b.get(key)) if b != null else 0
		d[key + "_after"] = int(a.get(key)) if a != null else 0
	d["evade_before"] = b.evade_charges if b != null else 0
	d["evade_after"] = a.evade_charges if a != null else 0
	d["alive_before"] = b != null and b.is_alive()
	d["alive_after"] = a != null and a.is_alive()
	d["breached"] = a != null and a.is_hub_breached() and not (b != null and b.is_hub_breached())
	var statuses: Array[Dictionary] = []
	if a != null and b != null and a.wheel != null and b.wheel != null:
		for i in mini(a.wheel.slice_statuses.size(), b.wheel.slice_statuses.size()):
			if a.wheel.slice_statuses[i] != b.wheel.slice_statuses[i]:
				statuses.append({"slot": i, "before": b.wheel.slice_statuses[i], "after": a.wheel.slice_statuses[i]})
		d["rotation_before"] = b.wheel.rotation
		d["rotation_after"] = a.wheel.rotation
		d["inner_before"] = b.wheel.inner_rotation
		d["inner_after"] = a.wheel.inner_rotation
	d["statuses"] = statuses
	return d


## The diff for one combatant ({} when unknown).
func of(id: StringName) -> Dictionary:
	return combatants.get(id, {})


## Whether anything at all changes (used to skip empty chip rows).
func is_empty() -> bool:
	if ram_delta != 0 or cards_drawn != 0 or heat != 0 or cycles != 0 or schematics != 0 or drones_gained != 0:
		return false
	if free_nudges_next_turn != 0 or damage_bonus_delta != 0 or outcome != CombatState.Outcome.NONE:
		return false
	for id in combatants:
		var d: Dictionary = combatants[id]
		for key in ["hp", "block", "shield", "resistance", "evade"]:
			if int(d[key + "_before"]) != int(d[key + "_after"]):
				return false
		if d["alive_before"] != d["alive_after"] or bool(d["breached"]) or not (d["statuses"] as Array).is_empty():
			return false
	return true
