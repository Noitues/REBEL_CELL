extends RefCounted
## Ring Lock (GDD A.2 #4): this turn, spins do not move your inner ring.


func handle(_context: Dictionary, state: CombatState, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	state.ring_locked = true
	return [{"type": "ring_lock", "text": "Ring Lock: spins leave the inner ring alone this turn."}]
