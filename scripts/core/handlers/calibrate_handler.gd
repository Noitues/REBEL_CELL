extends RefCounted
## Calibrate (GDD A.2 #9): your next N nudges this turn are free (N = effect amount).


func handle(context: Dictionary, state: CombatState, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	var effect: EffectData = context["effect"]
	var n: int = maxi(1, effect.amount)
	state.free_nudges += n
	return [{"type": "calibrate", "amount": n, "text": "Calibrate: %d free nudges this turn (%d available)." % [n, state.free_nudges]}]
