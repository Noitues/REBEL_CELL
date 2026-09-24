class_name CampaignState
extends RefCounted
## Campaign-level state a netrun touches (GDD 3, 4.3, 11): Heat, Schematics, the
## roster and the Armory. M3 adds the City Grid, territory, thresholds and raids.

enum Outcome { NONE, WON, LOST }

var corporation_id: StringName = &"solace"
var campaign_seed: int = 0
var heat: int = 0
var schematics: int = 0
var roster: Array[OperativeState] = []
## Banked defense asset ids (Armory, GDD 7.3).
var armory: Array[StringName] = []
## Exploit types (RC.ExploitType) extracted so far.
var exploits: Array[int] = []
var runs_started: int = 0
var runs_completed: int = 0
var deaths: int = 0
var next_operative_number: int = 1
## Heat thresholds already crossed (their one-time events fired), by heat value.
var thresholds_fired: Array[int] = []
## ICE difficulty level for this campaign (0 = none; ladder arrives with the profile).
var ice_level: int = 0
## City Grid runtime state (null until CampaignRules.new_campaign builds it).
var grid: GridState = null
## Story path chosen at campaign start and how many beats have been revealed.
var story_path_id: StringName = &""
var story_beats_revealed: int = 0
## Raids waiting to be fought at HQ: {"raid_id", "source", "heat"|"site_id"}.
var pending_raids: Array[Dictionary] = []
## Netrun complications from MINOR thresholds, consumed by the next run:
## {"type": RC.RuleModifierType, "value": float}.
var pending_complications: Array[Dictionary] = []
var heat_purchases: int = 0
var raids_won: int = 0
var raids_lost: int = 0
## Result of the last raid (RaidResult.to_dict()) for the summary screen.
var last_raid: Dictionary = {}
var outcome: int = Outcome.NONE


func is_over() -> bool:
	return outcome != Outcome.NONE


func has_exploit(exploit_type: int) -> bool:
	return exploits.has(exploit_type)


func get_operative(id: StringName) -> OperativeState:
	for o in roster:
		if o.id == id:
			return o
	return null


func living_operatives() -> Array[OperativeState]:
	var out: Array[OperativeState] = []
	for o in roster:
		if o.alive:
			out.append(o)
	return out


## Adds `delta` Heat within [0, heat_max]. Returns the change actually applied.
func add_heat(delta: int, config: CampaignConfigData) -> int:
	var before := heat
	heat = clampi(heat + delta, 0, config.heat_max)
	return heat - before


## MAJOR thresholds at or below the current Heat (CORRUPTED scales with this).
func heat_majors_crossed(config: CampaignConfigData) -> int:
	var n := 0
	for t in config.heat_thresholds:
		if t != null and t.kind == RC.ThresholdKind.MAJOR and heat >= t.heat:
			n += 1
	return n


## Sum of a RuleModifierType over every ongoing Heat-threshold modifier active now
## (thresholds at or below the current Heat) and every ICE level up to `ice_level`.
func rule_modifier(config: CampaignConfigData, type: int) -> float:
	var total := 0.0
	for t in config.heat_thresholds:
		if t == null or heat < t.heat:
			continue
		for m in t.ongoing_modifiers:
			if m != null and m.type == type:
				total += m.value
	for level in config.ice_ladder:
		if level == null or level.level > ice_level:
			continue
		for m in level.modifiers:
			if m != null and m.type == type:
				total += m.value
	return total


## Elite Router frequency bonus in percent (Heat 25+, ICE 3+).
func elite_frequency_pct(config: CampaignConfigData) -> float:
	return rule_modifier(config, RC.RuleModifierType.ELITE_FREQUENCY_PCT)


## Recruits a fresh operative of `class_data` (GDD 5.4).
func recruit(class_data: ClassData, p_name: String = "") -> OperativeState:
	var id := StringName("op_%d" % next_operative_number)
	next_operative_number += 1
	var o := OperativeState.from_class(class_data, id, p_name if p_name != "" else "%s %d" % [class_data.display_name, next_operative_number - 1])
	roster.append(o)
	return o


func duplicate_state() -> CampaignState:
	return from_dict(to_dict())


## JSON-normalised (numbers as floats) so a saved-and-reloaded campaign hashes identically.
func to_dict() -> Dictionary:
	return JSON.parse_string(JSON.stringify(_raw_dict()))


func _raw_dict() -> Dictionary:
	var ops := []
	for o in roster:
		ops.append(o.to_dict())
	var armory_out := []
	for a in armory:
		armory_out.append(String(a))
	return {
		"corporation_id": String(corporation_id), "campaign_seed": str(campaign_seed),
		"heat": heat, "schematics": schematics, "roster": ops, "armory": armory_out,
		"exploits": exploits.duplicate(), "runs_started": runs_started, "runs_completed": runs_completed,
		"deaths": deaths, "next_operative_number": next_operative_number,
		"thresholds_fired": thresholds_fired.duplicate(),
		"ice_level": ice_level,
		"grid": grid.to_dict() if grid != null else {},
		"story_path_id": String(story_path_id), "story_beats_revealed": story_beats_revealed,
		"pending_raids": pending_raids.duplicate(true), "pending_complications": pending_complications.duplicate(true),
		"heat_purchases": heat_purchases, "raids_won": raids_won, "raids_lost": raids_lost,
		"last_raid": last_raid.duplicate(true), "outcome": outcome,
	}


static func from_dict(d: Dictionary) -> CampaignState:
	var c := CampaignState.new()
	c.corporation_id = StringName(String(d.get("corporation_id", "solace")))
	c.campaign_seed = int(String(d.get("campaign_seed", "0")))
	c.heat = int(d.get("heat", 0))
	c.schematics = int(d.get("schematics", 0))
	for od in d.get("roster", []):
		c.roster.append(OperativeState.from_dict(od))
	for a in d.get("armory", []):
		c.armory.append(StringName(String(a)))
	for e in d.get("exploits", []):
		c.exploits.append(int(e))
	c.runs_started = int(d.get("runs_started", 0))
	c.runs_completed = int(d.get("runs_completed", 0))
	c.deaths = int(d.get("deaths", 0))
	c.next_operative_number = int(d.get("next_operative_number", 1))
	for t in d.get("thresholds_fired", []):
		c.thresholds_fired.append(int(t))
	c.ice_level = int(d.get("ice_level", 0))
	var gd: Dictionary = d.get("grid", {})
	c.grid = GridState.from_dict(gd) if not gd.is_empty() else null
	c.story_path_id = StringName(String(d.get("story_path_id", "")))
	c.story_beats_revealed = int(d.get("story_beats_revealed", 0))
	for r in d.get("pending_raids", []):
		c.pending_raids.append(_norm(r))
	for m in d.get("pending_complications", []):
		c.pending_complications.append({"type": int(m.get("type", 0)), "value": float(m.get("value", 0.0))})
	c.heat_purchases = int(d.get("heat_purchases", 0))
	c.raids_won = int(d.get("raids_won", 0))
	c.raids_lost = int(d.get("raids_lost", 0))
	c.last_raid = d.get("last_raid", {}).duplicate(true)
	c.outcome = int(d.get("outcome", Outcome.NONE))
	return c


## Normalises a pending-raid entry read from JSON (ints back from floats, strings kept).
static func _norm(r: Dictionary) -> Dictionary:
	var out := {}
	for k in r:
		var v: Variant = r[k]
		out[String(k)] = int(v) if v is float else v
	return out


func state_hash() -> int:
	return hash(JSON.stringify(to_dict()))
