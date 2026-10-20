class_name RunState
extends RefCounted
## One netrun (GDD 4.2): the map, the operative's working copy, Cycles, banking, the
## current node and whatever sub-screen is open (combat, reward, event, shop).

## RAID = a mid-run raid interlude between map nodes (GDD 4.4, designer ruling 2026-09-24).
## RG-02/03: REST and WORKSHOP are the node pages of those kinds (appended, saved ints survive).
enum Phase { MAP, COMBAT, REWARD, EVENT, SHOP, ENDED, RAID, REST, WORKSHOP }
## ABORTED = the campaign ended (home server lost) during the run.
enum Outcome { NONE, COMPLETED, DIED, ABORTED }

var run_seed: int = 0
var tier: int = 1
var site_id: StringName = &""
## "netrun" (full map), "boss" (single breach combat) or "reclaim" (single combat).
var kind: String = "netrun"
## Special runs fight this enemy instead of a pooled one.
var forced_enemy_id: StringName = &""
## Extra CombatSession overrides for special runs (Exploit effects on the boss).
var combat_overrides: Dictionary = {}
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
## Mainframe stock: {"cards": [ids], "firmware": [ids], "daemons": [ids], "slices": [ids],
## "removal_price": int}.
var shop: Dictionary = {}
var combats_won: int = 0
## Plan 2 N22 (ruling Q12): normal fights started this run from a Router (EASY pool while under
## CampaignConfigData.easy_normal_fights). -1 only between loading a save that predates it and
## NetrunSession.from_dict resolving it (the layer rule there).
var normal_fights_started: int = 0
## Server Racks captured this run (the "racks" stat).
var racks_captured: int = 0
## Launched as a patrol of an already cleared or claimed Site: completion changes nothing,
## even if a raid Takes the Site mid-run.
var patrol: bool = false
var elites_defeated: int = 0
## Cold Exit: did the operative's NULL slice resolve at any point this run?
var null_resolved: bool = false
var card_removals: int = 0
var heat_gained: int = 0
## Run-only cards from boosts (removed from the deck on completion).
var temp_cards: Array[StringName] = []
## Botnet drones carried between fights: {"source_id", "hp", "dock_slot"}.
var drones: Array[Dictionary] = []
var streams: Dictionary = {}
## Plan 2 WH-02: the corporation themes' netrun fields (RunThemeState). Saved as "corp_theme"
## only when a field is not default, so older saves load it as defaults and a run without
## theme data hashes as before.
var corp_theme: RunThemeState = RunThemeState.new()
## RG-02/03: the open REST or WORKSHOP page ({} when none): REST {"kind": "rest", "done", "mode", "swaps",
## "undo_hp", "undo_fw"}; WORKSHOP {"kind": "workshop", "offers", "bought"}. Saved only when not empty.
var node_state: Dictionary = {}


func current_node() -> Dictionary:
	return map.get_node(current_node_id) if map != null and current_node_id != &"" else {}


func is_over() -> bool:
	return outcome != Outcome.NONE


## JSON-normalised (numbers as floats) so a saved-and-reloaded run hashes identically.
func to_dict() -> Dictionary:
	return JSON.parse_string(JSON.stringify(_raw_dict()))


func _raw_dict() -> Dictionary:
	var rewards := []
	for r in pending_rewards:
		rewards.append(r.duplicate(true))
	var out := {
		"run_seed": str(run_seed), "tier": tier, "site_id": String(site_id),
		"kind": kind, "forced_enemy_id": String(forced_enemy_id), "combat_overrides": combat_overrides.duplicate(true),
		"operative": operative.to_dict() if operative != null else {},
		"cycles": cycles, "map": map.to_dict() if map != null else {},
		"current_node_id": String(current_node_id), "visited": _strings(visited),
		"phase": phase, "outcome": outcome,
		"banked_schematics": banked_schematics, "banked_assets": _strings(banked_assets),
		"unbanked_assets": _strings(unbanked_assets), "combat": combat.duplicate(true),
		"pending_rewards": rewards, "event_id": String(event_id), "shop": shop.duplicate(true),
		"combats_won": combats_won, "normal_fights_started": normal_fights_started, "elites_defeated": elites_defeated, "racks_captured": racks_captured, "patrol": patrol,
		"null_resolved": null_resolved, "card_removals": card_removals,
		"heat_gained": heat_gained, "streams": streams.duplicate(true),
		"temp_cards": _strings(temp_cards),
		"drones": drones.duplicate(true),
	}
	var theme := corp_theme.to_dict()
	if not theme.is_empty():  # absent at defaults: runs without theme data hash as before WH-02
		out["corp_theme"] = theme
	if not node_state.is_empty():  # RG-02: absent when no node page is open
		out["node_state"] = node_state.duplicate(true)
	return out


static func from_dict(d: Dictionary) -> RunState:
	var r := RunState.new()
	r.run_seed = int(String(d.get("run_seed", "0")))
	r.tier = int(d.get("tier", 1))
	r.site_id = StringName(String(d.get("site_id", "")))
	r.kind = String(d.get("kind", "netrun"))
	r.forced_enemy_id = StringName(String(d.get("forced_enemy_id", "")))
	r.combat_overrides = d.get("combat_overrides", {}).duplicate(true)
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
	r.normal_fights_started = int(d.get("normal_fights_started", -1))
	r.racks_captured = int(d.get("racks_captured", 0))
	r.patrol = bool(d.get("patrol", false))
	r.elites_defeated = int(d.get("elites_defeated", 0))
	r.null_resolved = bool(d.get("null_resolved", false))
	r.card_removals = int(d.get("card_removals", 0))
	r.heat_gained = int(d.get("heat_gained", 0))
	r.streams = d.get("streams", {}).duplicate(true)
	r.temp_cards = _names(d.get("temp_cards", []))
	for dd in d.get("drones", []):
		r.drones.append({"source_id": String(dd.get("source_id", "")), "hp": int(dd.get("hp", 1)), "dock_slot": int(dd.get("dock_slot", 0))})
	r.node_state = d.get("node_state", {}).duplicate(true)
	var theme: Variant = d.get("corp_theme", {})
	if theme is Dictionary:
		r.corp_theme.load_dict(theme)
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
