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


func to_dict() -> Dictionary:
	var u := []
	for x in unlocks:
		u.append(String(x))
	return {"unlocks": u, "best_ice": best_ice, "best_ice_by_corp": best_ice_by_corp.duplicate(),
		"campaigns_started": campaigns_started, "campaigns_won": campaigns_won, "campaigns_lost": campaigns_lost,
		"runs_completed": runs_completed, "operatives_lost": operatives_lost, "raids_won": raids_won, "raids_lost": raids_lost}


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
	return p


func state_hash() -> int:
	return hash(JSON.stringify(to_dict()))
