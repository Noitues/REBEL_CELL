class_name DossierFacts
extends RefCounted
## ART-11 4D: what the corporation's audit dossier says about the Cell (ART_BIBLE v2 §4.8
## "campaign summary = the corp's audit dossier"), read from the campaign at its end. Only
## facts the game keeps (no invented days, peaks or kills): the runs, the raids, the Exploits,
## the network at closure, the Heat and the thresholds it crossed, the crew and who is still at
## large, the story the Cell uncovered and the profile's records. Pure: it reads, never writes.

## The campaign was won (the corporation's file on a Cell that beat it).
var won: bool = false
var corporation_id: StringName = &""
## The profile's campaign count (the Cell's number on the file's tab).
var cell_number: int = 0
var runs_started: int = 0
var runs_completed: int = 0
var deaths: int = 0
var raids_won: int = 0
var raids_lost: int = 0
var exploits_held: int = 0
var exploits_total: int = 0
var schematics: int = 0
var held: int = 0
var down: int = 0
var taken: int = 0
var home_now: int = 0
var home_max: int = 0
var heat: int = 0
var heat_max: int = 0
## The Heat thresholds the campaign crossed (each set a raid off), ascending, and the major
## Heat levels (the config's), the trace's rules.
var heat_marks: Array[int] = []
var heat_levels: Array[int] = []
## The crew: [{"name", "class_id", "class_name", "rank", "alive", "runs", "post"}] in roster
## order; `post` is the Site a living operative is stationed on ("" = in reserve).
var crew: Array[Dictionary] = []
## The operative with the most runs, living or not (ties: roster order); {} with no crew.
var most_troublesome: Dictionary = {}
## The story beats uncovered: [{"title", "text"}] (translated).
var beats: Array[Dictionary] = []
var campaigns_won: int = 0
var campaigns_lost: int = 0
var best_ice: int = -1
var next_ice: int = 0
var corporation_name: String = ""
var boss_name: String = ""


## The facts of campaign `c` against `corp` on `profile` under `cfg`. `site_name`
## (StringName) -> String names a Site; `class_name_of` (StringName) -> String names a class;
## `beats` are the uncovered beats' {"title", "text"}; `next_ice` is the next campaign's ICE cap.
static func build(c: CampaignState, corp: CorporationData, profile: ProfileState, cfg: CampaignConfigData, site_name: Callable,
		class_name_of: Callable, p_beats: Array[Dictionary], p_next_ice: int) -> DossierFacts:
	var f := DossierFacts.new()
	f.won = c.outcome == CampaignState.Outcome.WON
	f.corporation_id = c.corporation_id
	f.runs_started = c.runs_started
	f.runs_completed = c.runs_completed
	f.deaths = c.deaths
	f.raids_won = c.raids_won
	f.raids_lost = c.raids_lost
	f.exploits_held = c.exploits.size()
	f.exploits_total = corp.exploits.size() if corp != null else 0
	f.schematics = c.schematics
	f.heat = c.heat
	f.heat_max = cfg.heat_max
	f.heat_levels = cfg.major_heat_levels()
	f.heat_marks.assign(c.thresholds_fired.duplicate())
	f.heat_marks.sort()
	var g := c.grid
	f.home_now = g.home_integrity
	f.home_max = g.home_max_integrity
	var ids: Array = g.sites.keys()
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id: StringName in ids:
		if g.is_home(id):
			continue
		if g.is_taken(id):
			f.taken += 1
		elif g.is_claimed(id):
			if g.is_active_node(id):
				f.held += 1
			else:
				f.down += 1
	var posts := {}
	for id: StringName in ids:
		var who := g.stationed_on(id)
		if who != &"":
			posts[who] = site_name.call(id)
	for o in c.roster:
		var row := {"name": o.name, "class_id": o.class_id, "class_name": String(class_name_of.call(o.class_id)), "rank": o.rank,
			"alive": o.alive, "runs": o.runs_completed, "post": String(posts.get(o.id, ""))}
		f.crew.append(row)
		if f.most_troublesome.is_empty() or o.runs_completed > int(f.most_troublesome["runs"]):
			f.most_troublesome = row
	f.beats = p_beats
	if profile != null:
		f.cell_number = profile.campaigns_won + profile.campaigns_lost
		f.campaigns_won = profile.campaigns_won
		f.campaigns_lost = profile.campaigns_lost
		f.best_ice = profile.best_ice
	f.next_ice = p_next_ice
	f.corporation_name = TextDb.t(corp, "display_name") if corp != null else String(c.corporation_id)
	f.boss_name = TextDb.t(corp.final_boss, "display_name") if corp != null and corp.final_boss != null else ""
	return f


## Living operatives (still at large).
func at_large() -> int:
	var n := 0
	for r in crew:
		if r["alive"]:
			n += 1
	return n
