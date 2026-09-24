extends RefCounted
## Undock (GDD A.2 #14): move a satellite to an adjacent slice of its host, in the
## direction the action gives (default clockwise). Falls back to the other side when
## that slot is taken.


func handle(context: Dictionary, state: CombatState, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	var sat: CombatantState = context.get("target")
	if sat == null or not sat.is_satellite:
		return [{"type": "undock_failed", "text": "Undock needs a satellite target."}]
	var host := state.get_combatant(sat.host_id)
	var action: CombatAction = context.get("action")
	var direction: int = action.direction if action != null else 1
	var n := host.wheel.slice_count
	for step in [direction, -direction]:
		var slot := posmod(sat.dock_slot + step, n)
		if state.satellite_at(host.id, slot) == null:
			sat.dock_slot = slot
			return [{"type": "undock", "target": sat.id, "slot": slot, "text": "%s undocks to slot %d." % [sat.display_name, slot]}]
	return [{"type": "undock_failed", "text": "No free adjacent slot for %s." % sat.display_name}]
