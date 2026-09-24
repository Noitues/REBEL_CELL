extends RefCounted
## Linked Bus (GDD 6.2): nudging an enemy wheel also moves your wheel the same way, free.
## Applies to nudge actions (the free nudge and RAM nudges), not to nudge cards
## (implementation decision 2026-09-24).


func handle(context: Dictionary, state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if not (state is CombatState) or int(context.get("trigger", -1)) != RC.Trigger.ON_NUDGE:
		return []
	var target: CombatantState = context.get("target")
	var action: CombatAction = context.get("action")
	if target == null or target.is_player or action == null:
		return []
	var fx: EffectInterpreter = context["fx"]
	var ring: int = action.ring
	if ring == RC.RingScope.INNER and not state.player.wheel.has_inner_ring():
		return [{"type": "linked_bus_skipped", "text": "Linked Bus: your wheel has no inner ring to move."}]
	var events: Array[Dictionary] = [{"type": "linked_bus", "text": "Linked Bus: your wheel follows the nudge."}]
	fx.nudge(state, state.player, state.player, ring, action.direction, true, events)
	return events
