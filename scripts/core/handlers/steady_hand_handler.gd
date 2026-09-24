extends RefCounted
## Steady Hand (GDD A.2 #11): if your slice is Perfect at end of turn, +2 RAM next turn.
## Sets a per-turn flag; CombatResolver checks it during RESOLVE.


func handle(_context: Dictionary, state: CombatState, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	state.flags["steady_hand"] = int(state.flags.get("steady_hand", 0)) + 1
	return [{"type": "steady_hand_armed", "text": "Steady Hand: land a Perfect this turn for +2 RAM next turn."}]
