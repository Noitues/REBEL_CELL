class_name CampaignState
extends RefCounted
## Campaign-level state a netrun touches (GDD 3, 4.3, 11): Heat, Schematics, the
## roster and the Armory. M3 adds the City Grid, territory, thresholds and raids.

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


## Recruits a fresh operative of `class_data` (GDD 5.4).
func recruit(class_data: ClassData, p_name: String = "") -> OperativeState:
	var id := StringName("op_%d" % next_operative_number)
	next_operative_number += 1
	var o := OperativeState.from_class(class_data, id, p_name if p_name != "" else "%s %d" % [class_data.display_name, next_operative_number - 1])
	roster.append(o)
	return o


func duplicate_state() -> CampaignState:
	return from_dict(to_dict())


func to_dict() -> Dictionary:
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
	return c


func state_hash() -> int:
	return hash(JSON.stringify(to_dict()))
