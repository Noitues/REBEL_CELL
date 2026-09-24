extends RefCounted
## Kernel Sync (GDD 6.2): each Perfect gives +1 damage for the rest of the combat.


func handle(context: Dictionary, state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if int(context.get("trigger", -1)) != RC.Trigger.ON_PERFECT or not (state is CombatState):
		return []
	state.damage_bonus += 1
	return [{"type": "kernel_sync", "amount": state.damage_bonus, "text": "Kernel Sync: +1 damage (now +%d)." % state.damage_bonus}]
