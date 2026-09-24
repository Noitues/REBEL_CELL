extends RefCounted
## Momentum (GDD A.2 #5): Spin 2; Spin 5 instead if you already spun this turn.
## The Breaker spin bonus applies as it does to any spin card.


func handle(context: Dictionary, state: CombatState, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	var fx: EffectInterpreter = context["fx"]
	var owner: CombatantState = context["owner"]
	var target: CombatantState = context.get("target", owner)
	var amount: int = 5 if state.spins_this_turn > 0 else 2
	amount += int(context.get("spin_bonus", 0))
	var events: Array[Dictionary] = [{"type": "momentum", "amount": amount, "text": "Momentum: spin %d." % amount}]
	fx.spin(state, owner, target, amount, events)
	return events
