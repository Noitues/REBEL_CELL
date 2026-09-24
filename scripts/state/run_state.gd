class_name RunState
extends RefCounted
## One netrun (GDD 4.2): the map, the operative's working copy, Cycles, banking, the
## current node and whatever sub-screen is open (combat, reward, event, shop).

enum Phase { MAP, COMBAT, REWARD, EVENT, SHOP, ENDED }
enum Outcome { NONE, COMPLETED, DIED }

var run_seed: int = 0
var tier: int = 1
var site_id: StringName = &""
var operative: OperativeState = null
var cycles: int = 0
var map: MapGraph = null
var current_node_id: StringName = &""
var visited: Array[StringName] = []
var phase: int = Phase.MAP
var outcome: int = Outcome.NONE
## Schematics banked at Server Racks (safe even if the operative dies).
var banked_schematics: int = 0
## Defense assets found this run: safe once a Rack banks them.
var banked_assets: Array[StringName] = []
var unbanked_assets: Array[StringName] = []
## Live combat, serialised (CombatSession.to_dict()); empty when not fighting.
var combat: Dictionary = {}
## Queue of offers: {"kind": "card"|"firmware"|"daemon", "options": [ids]}.
var pending_rewards: Array[Dictionary] = []
var event_id: StringName = &""
## Modem stock: {"cards": [ids], "firmware": [ids], "daemons": [ids], "slices": [ids],
## "removal_price": int}.
var shop: Dictionary = {}
var combats_won: int = 0
var elites_defeated: int = 0
## Cold Exit: did the operative's Miss slice resolve at any point this run?
var miss_resolved: bool = false
var card_removals: int = 0
var heat_gained: int = 0
var streams: Dictionary = {}


func current_node() -> Dictionary:
	return map.get_node(current_node_id) if map != null and current_node_id != &"" else {}


func is_over() -> bool:
	return outcome != Outcome.NONE


func to_dict() -> Dictionary:
	var rewards := []
	for r in pending_rewards:
		rewards.append(r.duplicate(true))
	return {
		"run_seed": str(run_seed), "tier": tier, "site_id": String(site_id),
		"operative": operative.to_dict() if operative != null else {},
		"cycles": cycles, "map": map.to_dict() if map != null else {},
		"current_node_id": String(current_node_id), "visited": _strings(visited),
		"phase": phase, "outcome": outcome,
		"banked_schematics": banked_schematics, "banked_assets": _strings(banked_assets),
		"unbanked_assets": _strings(unbanked_assets), "combat": combat.duplicate(true),
		"pending_rewards": rewards, "event_id": String(event_id), "shop": shop.duplicate(true),
		"combats_won": combats_won, "elites_defeated": elites_defeated,
		"miss_resolved": miss_resolved, "card_removals": card_removals,
		"heat_gained": heat_gained, "streams": streams.duplicate(true),
	}


static func from_dict(d: Dictionary) -> RunState:
	var r := RunState.new()
	r.run_seed = int(String(d.get("run_seed", "0")))
	r.tier = int(d.get("tier", 1))
	r.site_id = StringName(String(d.get("site_id", "")))
	var od: Dictionary = d.get("operative", {})
	r.operative = OperativeState.from_dict(od) if not od.is_empty() else null
	r.cycles = int(d.get("cycles", 0))
	var md: Dictionary = d.get("map", {})
	r.map = MapGraph.from_dict(md) if not md.is_empty() else null
	r.current_node_id = StringName(String(d.get("current_node_id", "")))
	r.visited = _names(d.get("visited", []))
	r.phase = int(d.get("phase", Phase.MAP))
	r.outcome = int(d.get("outcome", Outcome.NONE))
	r.banked_schematics = int(d.get("banked_schematics", 0))
	r.banked_assets = _names(d.get("banked_assets", []))
	r.unbanked_assets = _names(d.get("unbanked_assets", []))
	r.combat = d.get("combat", {}).duplicate(true)
	for rd in d.get("pending_rewards", []):
		r.pending_rewards.append(rd.duplicate(true))
	r.event_id = StringName(String(d.get("event_id", "")))
	r.shop = d.get("shop", {}).duplicate(true)
	r.combats_won = int(d.get("combats_won", 0))
	r.elites_defeated = int(d.get("elites_defeated", 0))
	r.miss_resolved = bool(d.get("miss_resolved", false))
	r.card_removals = int(d.get("card_removals", 0))
	r.heat_gained = int(d.get("heat_gained", 0))
	r.streams = d.get("streams", {}).duplicate(true)
	return r


func state_hash() -> int:
	return hash(JSON.stringify(to_dict()))


static func _strings(names: Array[StringName]) -> Array:
	var out := []
	for n in names:
		out.append(String(n))
	return out


static func _names(strings: Array) -> Array[StringName]:
	var out: Array[StringName] = []
	for s in strings:
		out.append(StringName(String(s)))
	return out
