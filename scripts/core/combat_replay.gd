class_name CombatReplay
extends RefCounted
## A finished combat as the inputs the engine already records (ART-0 S0, DECISIONS "Art
## direction — ART-0 names pass, part 1 + saves folder"): what the fight was built from
## (CombatSession.setup, by content id), its seed, every action applied (CombatSession.history)
## and the hash of the state it ended on. Rebuilding the combat from the setup and seed and
## applying the actions again reaches the same hash (seeded replays match, CLAUDE.md rule 6).
## Pure data: SaveService writes and reads the JSON.

## The replay file's kind tag.
const KIND := "combat_replay"


## The replay of `session` as a JSON-safe dictionary. The seed (64-bit) is a string, as
## RngService stores its states.
static func record(session: CombatSession) -> Dictionary:
	var actions: Array = []
	for a in session.history:
		actions.append(a.to_dict())
	return {"kind": KIND, "setup": session.setup.duplicate(true), "seed": str(session.combat_seed), "actions": actions,
		"outcome": session.state.outcome, "result_hash": str(session.state.state_hash())}


## Rebuilds the combat `data` recorded and applies its actions again.
static func run(resolver: CombatResolver, data: Dictionary) -> CombatSession:
	var actions: Array[CombatAction] = []
	for d in data.get("actions", []):
		actions.append(CombatAction.from_dict(d))
	return CombatSession.replay(resolver, data.get("setup", {}), int(String(data.get("seed", "0"))), actions)


## True when replaying `data` ends on the hash it recorded.
static func matches(resolver: CombatResolver, data: Dictionary) -> bool:
	if String(data.get("kind", "")) != KIND:
		return false
	return str(run(resolver, data).state.state_hash()) == String(data.get("result_hash", ""))
