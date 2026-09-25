extends RefCounted
## Kernel Sync (GDD 6.2): each Perfect gives +amount damage for the rest of the combat.


func handle(context: Dictionary, state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if int(context.get("trigger", -1)) != RC.Trigger.ON_PERFECT or not (state is CombatState):
		return []
	var d: DaemonData = context.get("daemon")
	var amount := d.amount if d != null else 0
	state.damage_bonus += amount
	return [{"type": "kernel_sync", "amount": state.damage_bonus, "text": "Kernel Sync: +%d damage (now +%d)." % [amount, state.damage_bonus]}]
