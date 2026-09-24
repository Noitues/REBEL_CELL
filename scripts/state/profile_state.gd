class_name ProfileState
extends RefCounted
## Permanent player profile (GDD 3.4): unlocks and records. Saved in profile.json.

var unlocks: Array[StringName] = []
var best_ice: int = -1
## corporation id (String) -> highest ICE cleared
var best_ice_by_corp: Dictionary = {}
var campaigns_started: int = 0
var campaigns_won: int = 0
var campaigns_lost: int = 0
var runs_completed: int = 0
var operatives_lost: int = 0
var raids_won: int = 0
var raids_lost: int = 0
## Achievement ids earned (Achievements.DEFS).
var achievements: Array[StringName] = []
## Counters for stats and achievements: perfects, racks, cycles, runs_by_tier...
var stats: Dictionary = {}
## The last RUN_HISTORY_CAP runs: {corporation, tier, site, outcome, cycles, banked}.
var run_history: Array[Dictionary] = []
const RUN_HISTORY_CAP := 20


func record_win(corporation_id: StringName, ice_level: int) -> void:
	campaigns_won += 1
	best_ice = maxi(best_ice, ice_level)
	best_ice_by_corp[String(corporation_id)] = maxi(int(best_ice_by_corp.get(String(corporation_id), -1)), ice_level)


func record_loss() -> void:
	campaigns_lost += 1


func best_ice_for(corporation_id: StringName) -> int:
	return int(best_ice_by_corp.get(String(corporation_id), -1))


func has_unlock(id: StringName) -> bool:
	return unlocks.has(id)


func add_stat(key: String, amount: int = 1) -> void:
	stats[key] = int(stats.get(key, 0)) + amount


func add_achievement(id: StringName) -> void:
	if not achievements.has(id):
		achievements.append(id)


func record_run(entry: Dictionary) -> void:
	run_history.push_front(entry.duplicate())
	while run_history.size() > RUN_HISTORY_CAP:
		run_history.pop_back()


func add_unlock(id: StringName) -> void:
	if not unlocks.has(id):
		unlocks.append(id)


## Highest ICE selectable for `corporation_id` (GDD 3.4, decision 2026-09-24): a win at
## ICE n unlocks up to n + 3 on that corporation; any corporation may start at the global
## best minus new_corp_ice_offset; never below `base_cap` (3) nor above `max_level` (20).
func ice_cap_for(corporation_id: StringName, new_corp_ice_offset: int, base_cap: int = 3, max_level: int = 20) -> int:
	var cap := base_cap
	cap = maxi(cap, best_ice_for(corporation_id) + 3)
	cap = maxi(cap, best_ice - new_corp_ice_offset)
	return clampi(cap, 0, max_level)


func to_dict() -> Dictionary:
	var u := []
	for x in unlocks:
		u.append(String(x))
	var a := []
	for x in achievements:
		a.append(String(x))
	return {"unlocks": u, "best_ice": best_ice, "best_ice_by_corp": best_ice_by_corp.duplicate(),
		"campaigns_started": campaigns_started, "campaigns_won": campaigns_won, "campaigns_lost": campaigns_lost,
		"runs_completed": runs_completed, "operatives_lost": operatives_lost, "raids_won": raids_won, "raids_lost": raids_lost,
		"achievements": a, "stats": stats.duplicate(), "run_history": run_history.duplicate(true)}


static func from_dict(d: Dictionary) -> ProfileState:
	var p := ProfileState.new()
	for x in d.get("unlocks", []):
		p.unlocks.append(StringName(String(x)))
	p.best_ice = int(d.get("best_ice", -1))
	for k in d.get("best_ice_by_corp", {}):
		p.best_ice_by_corp[String(k)] = int(d["best_ice_by_corp"][k])
	p.campaigns_started = int(d.get("campaigns_started", 0))
	p.campaigns_won = int(d.get("campaigns_won", 0))
	p.campaigns_lost = int(d.get("campaigns_lost", 0))
	p.runs_completed = int(d.get("runs_completed", 0))
	p.operatives_lost = int(d.get("operatives_lost", 0))
	p.raids_won = int(d.get("raids_won", 0))
	p.raids_lost = int(d.get("raids_lost", 0))
	for x in d.get("achievements", []):
		p.achievements.append(StringName(String(x)))
	for k in d.get("stats", {}):
		p.stats[String(k)] = int(d["stats"][k])
	for r in d.get("run_history", []):
		var entry := {}
		for k in r:
			entry[String(k)] = int(r[k]) if r[k] is float else r[k]
		p.run_history.append(entry)
	return p


func state_hash() -> int:
	return hash(JSON.stringify(to_dict()))
