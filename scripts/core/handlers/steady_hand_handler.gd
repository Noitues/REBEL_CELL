extends RefCounted
## Steady Hand (GDD A.2 #11): if your slice is Perfect at end of turn, +2 RAM next turn.
## Adds the effect's amount to a per-turn flag; CombatResolver pays it during RESOLVE.


func handle(context: Dictionary, state: CombatState, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	var e: EffectData = context.get("effect")
	var amount := e.amount if e != null else 0
	state.flags["steady_hand"] = int(state.flags.get("steady_hand", 0)) + amount
	return [{"type": "steady_hand_armed", "text": "Steady Hand: land a Perfect this turn for +%d RAM next turn." % amount}]
