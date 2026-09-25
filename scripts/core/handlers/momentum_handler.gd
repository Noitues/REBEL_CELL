extends RefCounted
## Momentum (GDD A.2 #5): Spin `amount` (2); Spin amount x multiplier (5) instead if you
## already spun this turn. The Breaker spin bonus applies as it does to any spin card.


func handle(context: Dictionary, state: CombatState, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	var fx: EffectInterpreter = context["fx"]
	var owner: CombatantState = context["owner"]
	var target: CombatantState = context.get("target", owner)
	var e: EffectData = context.get("effect")
	var base := e.amount if e != null else 0
	var amount: int = roundi(base * e.multiplier) if e != null and state.spins_this_turn > 0 else base
	amount += int(context.get("spin_bonus", 0))
	var events: Array[Dictionary] = [{"type": "momentum", "amount": amount, "text": "Momentum: spin %d." % amount}]
	fx.spin(state, owner, target, amount, events)
	return events
