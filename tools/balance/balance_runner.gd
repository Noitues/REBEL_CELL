extends RefCounted
## BalanceRunner (BALANCE_SIM S1/S2): the four modes over a BalanceContent copy of the content.
##   campaign  whole campaigns            -> one record per seed
##   fight     enemy x tier x seed        -> one record per fight (a starter operative against one foe)
##   boss      the final breach fight     -> one record per seed (from a campaign played to the breach, or fresh)
##   netrun    one run from a fresh start -> one record per seed
## A record is {group, seed, scalars{name: number}, series{name: [numbers]}, pools{name: [numbers]}}.
## Pure logic: no scenes, no files except the defaults JSON. The CLI is balance_sim.gd; the shard /
## merge / report / compare driver is balance.py.

const BalanceContent := preload("res://tools/balance/balance_content.gd")
const BalanceProbe := preload("res://tools/balance/balance_probe.gd")
const BalanceSkill := preload("res://tools/balance/balance_skill.gd")
const BalanceBossStop := preload("res://tools/balance/balance_boss_stop.gd")
const AgentSimulator := preload("res://tools/agent/agent_simulator.gd")
const BossStopSimulator := preload("res://tools/agent/boss_stop_simulator.gd")
const HeuristicStrategist := preload("res://tools/agent/heuristic_strategist.gd")

const DEFAULTS_PATH := "res://tools/balance/balance_defaults.json"
const SCHEMA := 1
const KINDS: Array[String] = ["combat", "node", "reward", "event", "launch", "raid", "shop", "hq"]

var content: BalanceContent
var opts: Dictionary = {}
var resolver: CombatResolver
## Errors from the overrides (an empty list = all applied).
var errors: PackedStringArray = PackedStringArray()
## The combat of the last fight-mode fight (the determinism test replays it).
var last_combat: CombatSession = null
var _skill: BalanceSkill
var _strategist_specs: Array = []
## N19: false switches the per-phase metrics off (the purity test compares both).
var collect_metrics: bool = true


## `registry` is the ContentRegistry (or anything with all_ids / get_content / config); `p_opts` overrides
## the defaults file; `specs` are the --set strings (variants are expanded by the caller).
func _init(registry: Object, p_opts: Dictionary = {}, specs: Array = []) -> void:
	opts = defaults()
	for k in p_opts:
		opts[k] = p_opts[k]
	for k in opts:  # JSON numbers are floats: whole numbers are ints (skill stays a float)
		if k != "skill" and opts[k] is float:
			opts[k] = int(opts[k])
		elif opts[k] is Array:
			for i in opts[k].size():
				if opts[k][i] is float:
					opts[k][i] = int(opts[k][i])
	if is_reference():  # BAL-01: the named reference policy = the heuristic bot at the configured lookahead
		opts["lookahead"] = int(opts["reference_lookahead"])
	content = BalanceContent.new(registry)
	var content_specs: Array = []
	for sp in specs:  # `strategist.<prop>=<json>` edits a COPY of the heuristic policy's own config (Q8), not game content
		if String(sp).begins_with("strategist."):
			_strategist_specs.append(String(sp))
		else:
			content_specs.append(sp)
	errors = content.apply_all(content_specs)
	resolver = CombatResolver.new(content.config, content.lookup)
	resolver.quiet = bool(opts["quiet"])
	_skill = BalanceSkill.new(float(opts["skill"]), int(opts["novice_max_actions"]))


## BAL-01: true for the named reference policy (`--policy reference`): HeuristicStrategist at `reference_lookahead`
## (default 2), deterministic. Its report equals `--policy heuristic --lookahead 2` except for the policy name.
func is_reference() -> bool:
	return String(opts["policy"]) == "reference"


static func defaults() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DEFAULTS_PATH))
	return parsed if parsed is Dictionary else {}


## Runs `mode` over `seeds` and returns the report: {schema, mode, opts, overrides, errors, records}.
func run(mode: String, seeds: Array) -> Dictionary:
	var records: Array = []
	match mode:
		"campaign":
			for sd in seeds:
				records.append(run_campaign(int(sd)))
		"fight":
			for enemy in fight_enemies():
				for tier in opts["tiers"]:
					for sd in seeds:
						records.append(run_fight(StringName(enemy), int(tier), int(sd)))
		"boss":
			for sd in seeds:
				records.append(run_boss(int(sd)))
		"netrun":
			for sd in seeds:
				records.append(run_netrun(int(sd), int(opts["tier"])))
		_:
			errors.append("unknown mode '%s'" % mode)
	return {"schema": SCHEMA, "mode": mode, "opts": opts, "overrides": content.applied, "errors": errors, "records": records}


# --- Campaign ---------------------------------------------------------------------------------

## One whole campaign; the record carries the Heat curve, raid causes, economy and attrition.
func run_campaign(campaign_seed: int) -> Dictionary:
	var probe := BalanceProbe.new(content.lookup, content.config)
	probe.trace_path = String(opts["trace"])
	var sim := _make_sim(probe)
	_skill.reseed(campaign_seed)
	var rep: Dictionary = sim.run_campaign(campaign_seed, int(opts["ice"]), int(opts["max_runs"]))
	var rec := _record("campaign@ice%d" % int(opts["ice"]), campaign_seed)
	var sc: Dictionary = rec["scalars"]
	sc["won"] = 1 if rep["outcome"] == "WON" else 0
	sc["lost"] = 1 if rep["outcome"] == "LOST" else 0
	sc["end_hash"] = rep["hash"]
	for k in ["runs", "completed", "deaths", "raids", "raids_won", "raids_lost", "heat_peak", "heat_end", "exploits", "fights", "turns", "stuck"]:
		sc[k] = rep[k]
	if int(rep["heat_at_breach"]) >= 0:
		sc["heat_at_breach"] = rep["heat_at_breach"]
	sc["minutes"] = snappedf(float(rep["est_hours"]) * 60.0, 0.1)
	sc["raids_from_flatline"] = probe.raid_causes["flatline"]
	sc["raids_from_heat_actions"] = probe.raid_causes["heat_actions"]
	sc["raids_other"] = probe.raid_causes["other"]
	sc["schematics_income"] = probe.schematics_income
	sc["schematics_spent"] = probe.schematics_spent
	sc["schematics_unspent"] = probe.schematics_last
	sc["recruits"] = probe.recruits
	sc["deaths_per_run"] = snappedf(float(rep["deaths"]) / maxf(1.0, float(rep["runs"])), 0.0001)
	rec["series"]["heat_curve"] = probe.heat_curve
	_add_run_metrics(rec, probe, "")
	_add_fight_pools(rec, probe)
	return rec


# --- Fight ------------------------------------------------------------------------------------

## Ids of the enemies a fight sweep covers: `--enemy` ids, or every non-boss enemy of the corporation.
func fight_enemies() -> Array:
	var wanted: Variant = opts["enemy"]
	if wanted is Array and not wanted.is_empty() and wanted[0] != "all":
		return wanted
	var cats: Array = opts["categories"]
	var out: Array = []
	for id in content.lookup.ids_of_class(&"EnemyData"):
		var e := content.lookup.get_content(id) as EnemyData
		if e.corporation_id != StringName(String(opts["corp"])) or e.is_boss or e.wheel == null or e.wheel.slice_count != RC.SLICES:
			continue
		var cat := "mini_boss" if e.is_mini_boss else ("elite" if e.is_elite else "enemy")
		if cats.has(cat):
			out.append(String(id))
	return out


## One fight: a starter operative of the class against `enemy_id` at `tier` (enemy HP / damage scaled by
## the tier as in a netrun), played with the policy. Equal to a CombatResolver replay of the same seed.
func run_fight(enemy_id: StringName, tier: int, fight_seed: int) -> Dictionary:
	var sim := _make_sim(null)
	var c := _fresh_campaign(sim, fight_seed)
	var op: OperativeState = c.living_operatives()[0]
	var s := NetrunSession.start_special(resolver, c, op.id, "reclaim", sim.corp.city_grid.home_site_id, tier, fight_seed, enemy_id,
		{}, sim.corp)
	var probe := BalanceProbe.new(content.lookup, content.config)
	probe.metrics_enabled = collect_metrics
	var rec := _record("fight:%s@t%d" % [enemy_id, tier], fight_seed)
	if s == null:
		rec["scalars"]["error"] = 1
		return rec
	probe.attach(s)
	probe.begin_run(c, op, s)
	s.enter_node(s.run.map.first_layer_ids()[0])
	if not s.in_combat():
		rec["scalars"]["error"] = 1
		return rec
	last_combat = s.combat
	_skill.reseed(fight_seed)
	probe.on_fight_begin(s)
	_play_fight(sim, s)
	probe.on_fight_end(s, 0)
	var f: Dictionary = probe.fights.back() if not probe.fights.is_empty() else {}
	_fight_scalars(rec["scalars"], f)
	_add_metrics(rec, f)
	rec["scalars"]["combat_hash"] = last_combat.state.state_hash()
	rec["category"] = String(f.get("category", ""))
	return rec


# --- Netrun -----------------------------------------------------------------------------------

## One netrun from a fresh campaign at `tier`: HP on arrival at every layer, heals, outcome.
func run_netrun(run_seed: int, tier: int) -> Dictionary:
	var probe := BalanceProbe.new(content.lookup, content.config)
	var sim := _make_sim(probe)
	var c := _fresh_campaign(sim, run_seed)
	var op: OperativeState = c.living_operatives()[0]
	var launchable := CampaignRules.launchable_sites(c, sim.corp, content.config)
	var site_id: StringName = launchable[0].id if not launchable.is_empty() else sim.corp.city_grid.home_site_id
	var s := NetrunSession.start(resolver, c, op.id, tier, site_id, run_seed, sim.corp)
	_skill.reseed(run_seed)
	probe.on_run_start(c, op, null, s)
	sim._play_run(s, _run_stats())
	probe.on_run_end(c, s, op, null)
	var rec := _record("netrun@t%d" % tier, run_seed)
	_add_run_metrics(rec, probe, "")
	if not probe.runs.is_empty():
		var r: Dictionary = probe.runs[0]
		rec["scalars"]["died"] = 1 if r["died"] else 0
		rec["scalars"]["completed"] = 0 if r["died"] else 1
		rec["scalars"]["layers"] = r["layers"]
		rec["scalars"]["cycles"] = r["cycles"]
		rec["scalars"]["hp_end_frac"] = snappedf(float(r["hp_end"]) / maxf(1.0, float(r["hp_max"])), 0.0001)
		rec["scalars"]["heal_hp"] = r["heal_hp"]
		rec["scalars"]["heals_available"] = r["terminals"]
		rec["scalars"]["heals_used"] = r["terminals_visited"]
		rec["series"]["layer_hp_frac"] = r["layer_frac"]
		rec["series"]["layer_hp"] = r["layer_hp"]
	_add_fight_pools(rec, probe)
	return rec


# --- Boss -------------------------------------------------------------------------------------

## The final boss fight. `source` "campaign": play the campaign to the first breach launch and fight
## with the crew it would send; "fresh": a starter operative at the breach.
func run_boss(campaign_seed: int) -> Dictionary:
	var rec := _record("boss@ice%d" % int(opts["ice"]), campaign_seed)
	var probe := BalanceProbe.new(content.lookup, content.config)
	var sim = _make_sim(null, true)
	_skill.reseed(campaign_seed)
	var c: CampaignState
	if String(opts["source"]) == "fresh":
		c = _fresh_campaign(sim, campaign_seed)
	elif String(opts["source"]) == "save":  # BAL-03: the boss from a saved campaign state (tool-only)
		c = load_saved_state(String(opts["state"]), campaign_seed)
		if c == null:
			rec["scalars"]["no_state"] = 1
			return rec
	else:
		var to_breach: Dictionary = sim.run_campaign(campaign_seed, int(opts["ice"]), int(opts["max_runs"]))
		if not sim.reached_breach:
			rec["scalars"]["no_breach"] = 1
			return rec
		# Q8 pacing: what the campaign cost up to the first breach launch (the boss attempts come on top).
		for k in ["runs", "deaths", "raids", "exploits", "heat_peak", "stuck"]:
			rec["scalars"][k + "_to_breach"] = to_breach[k]
		rec["scalars"]["minutes_to_breach"] = snappedf(float(to_breach["est_hours"]) * 60.0, 0.1)
		c = sim.final_campaign
		if String(opts["dump_state"]) != "":
			dump_state(String(opts["dump_state"]), campaign_seed, c)
	var site: SiteData = null
	for sd in sim.corp.city_grid.sites:
		if sd != null and sd.objective == RC.SiteObjective.CENTRAL_SERVER:
			site = sd
	var ops := c.living_operatives()
	ops.sort_custom(func(a: OperativeState, b: OperativeState) -> bool: return a.rank > b.rank if a.rank != b.rank else String(a.id) < String(b.id))
	if site == null or ops.is_empty():
		rec["scalars"]["no_breach"] = 1
		return rec
	var op := ops[0]
	rec["scalars"]["heat"] = c.heat
	rec["scalars"]["operative_rank"] = op.rank
	rec["scalars"]["operative_hp_max"] = op.max_hp
	rec["scalars"]["deck_size"] = op.deck.size()
	sim.probe = probe
	var s: NetrunSession = sim._start(c, op, site, campaign_seed)
	_skill.reseed(campaign_seed)
	probe.on_run_start(c, op, site, s)
	sim._play_run(s, _run_stats())
	probe.on_run_end(c, s, op, site)
	var f: Dictionary = probe.fights.back() if not probe.fights.is_empty() else {}
	_fight_scalars(rec["scalars"], f)
	rec["scalars"]["won"] = 1 if (not f.is_empty() and bool(f["won"])) else 0
	_add_metrics(rec, f)
	rec["scalars"]["phases"] = f.get("phase_turns", [1]).size()
	if not f.is_empty():
		var starts: Array = f["phase_turns"]
		for i in starts.size():
			var end_turn: int = int(starts[i + 1]) if i + 1 < starts.size() else int(f["turns"]) + 1
			rec["scalars"]["turns_phase_%d" % (i + 1)] = end_turn - int(starts[i])
		rec["series"]["player_hp"] = f["player_hp"]
		rec["series"]["boss_hp_frac"] = f["enemy_frac"]
	return rec


## BAL-03: a campaign state from `path` for `campaign_seed`. `path` is a state file, or a directory holding
## `boss_<seed>.json` (as `--dump-state` writes). A file is either a bare CampaignState dict or a game save
## ({"campaign": {...}}). Returns null when the file is missing or unreadable.
static func load_saved_state(path: String, campaign_seed: int) -> CampaignState:
	var file := path
	if DirAccess.dir_exists_absolute(path):
		file = path.path_join("boss_%d.json" % campaign_seed)
		if not FileAccess.file_exists(file):  # a seed beyond the dump reuses a dumped state with a new combat seed
			file = path.path_join("boss_%d.json" % (1000 + campaign_seed % 1000))
	if not FileAccess.file_exists(file):
		return null
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(file))
	if not (parsed is Dictionary):
		return null
	var d: Dictionary = parsed.get("campaign", parsed)
	return CampaignState.from_dict(d)


## BAL-03: writes the breach campaign state of `campaign_seed` to `dir/boss_<seed>.json` (a bare CampaignState dict).
static func dump_state(dir: String, campaign_seed: int, c: CampaignState) -> void:
	DirAccess.make_dir_recursive_absolute(dir)
	var f := FileAccess.open(dir.path_join("boss_%d.json" % campaign_seed), FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(c.to_dict()))
		f.close()


# --- Shared ----------------------------------------------------------------------------------

## Builds the simulator for the policy: builtin = CombatBot, heuristic = the HeuristicStrategist (lookahead N), reference = heuristic at reference_lookahead.
func _make_sim(probe: Object, boss_stop: bool = false) -> CampaignSimulator:
	var corp := StringName(String(opts["corp"]))
	var cls := StringName(String(opts["class"]))
	var sim: CampaignSimulator
	if String(opts["policy"]) == "heuristic" or is_reference():
		sim = (BossStopSimulator if boss_stop else AgentSimulator).new(resolver, "", [], corp, cls)
		var scfg := HeuristicStrategistConfigData.shipped().duplicate() as HeuristicStrategistConfigData
		for sp in _strategist_specs:
			var kv := String(sp).trim_prefix("strategist.").split("=", true, 1)
			var parsed: Variant = JSON.parse_string(kv[1]) if kv.size() == 2 else null
			if kv.size() == 2 and parsed != null and kv[0] in scfg:
				scfg.set(kv[0], parsed)
			else:
				errors.append("override '%s': bad strategist property" % sp)
		var h := HeuristicStrategist.new(scfg, sim.lookup)
		h.lookahead_turns = int(opts["lookahead"])
		sim.set("strategist", h)
	elif boss_stop:
		sim = BalanceBossStop.new(resolver, corp, cls)
	else:
		sim = CampaignSimulator.new(resolver, corp, cls)
	sim.probe = probe
	if float(opts["skill"]) < 1.0:
		sim.turn_override = Callable(_skill, "play")
	return sim


func _fresh_campaign(sim: CampaignSimulator, campaign_seed: int) -> CampaignState:
	return CampaignRules.new_campaign(sim.corp, content.config, content.lookup, campaign_seed, sim.class_data, sim.home.core, int(opts["ice"]), sim.home)


func _play_fight(sim: CampaignSimulator, s: NetrunSession) -> void:
	if sim.has_method("_play_fight"):
		sim._play_fight(s, _run_stats())
		return
	var turns := 0
	while s.in_combat() and turns < CampaignSimulator.MAX_TURNS_PER_FIGHT:
		turns += 1
		if not (sim.turn_override.is_valid() and sim.turn_override.call(s)):
			CombatBot.play_turn(s.combat, s.combat_action)


func _run_stats() -> Dictionary:
	return {"runs": 0, "completed": 0, "deaths": 0, "raids": 0, "heat_peak": 0, "stuck": 0, "turns": 0, "fights": 0, "log": []}


func _record(group: String, record_seed: int) -> Dictionary:
	return {"group": group, "seed": record_seed, "scalars": {}, "series": {}, "pools": {}}


## Per-fight scalars (a fight record, or the boss fight).
func _fight_scalars(sc: Dictionary, f: Dictionary) -> void:
	if f.is_empty():
		sc["error"] = 1
		return
	var turns := maxi(1, int(f["turns"]))
	sc["turns"] = f["turns"]
	sc["won"] = 1 if f["won"] else 0
	sc["died"] = 1 if f["dead"] else 0
	sc["stuck"] = 1 if f["stuck"] else 0
	sc["hp_in"] = f["hp_in"]
	sc["hp_lost"] = f["hp_lost"]
	sc["hp_lost_frac"] = snappedf(float(f["hp_lost"]) / maxf(1.0, float(f["hp_max"])), 0.0001)
	sc["hp_end"] = f["hp_out"]
	sc["dealt"] = f["dealt"]
	sc["taken"] = f["taken"]
	sc["dealt_per_turn"] = snappedf(float(f["dealt"]) / turns, 0.01)
	sc["taken_per_turn"] = snappedf(float(f["taken"]) / turns, 0.01)
	sc["perfect_rate"] = snappedf(float(f["perfects"]) / maxf(1.0, float(f["pointers"])), 0.0001)
	sc["heal_turns"] = f["heal_turns"]
	sc["heal_total"] = f["heal_total"]
	sc["ram_left_per_turn"] = snappedf(float(f["ram_left"]) / turns, 0.01)


## N19: the fight's per-phase metrics (SimMetrics) as `rec.metrics` plus flat scalars for the aggregates.
func _add_metrics(rec: Dictionary, f: Dictionary) -> void:
	var m = f.get("metrics")
	if m == null:
		return
	rec["metrics"] = m
	var sc: Dictionary = rec["scalars"]
	var parked := 0
	var intake := 0
	var absorbed := 0
	for p in m["phases"]:
		parked += int(p["parked"])
		intake += int(p["intake"])
		absorbed += int(p["resistance_absorbed"])
	var tm: Dictionary = m["turn_manipulation"]
	var turns := int(tm["own"]) + int(tm["enemy"]) + int(tm["both"]) + int(tm["none"])
	sc["parked"] = parked
	sc["intake"] = intake
	sc["resistance_absorbed"] = absorbed
	sc["enrage_step"] = m["enrage_step"]
	sc["turns_both_share"] = snappedf(float(tm["both"]) / maxf(1.0, float(turns)), 0.0001)


## Attrition and heal metrics of the probe's netrun records (pooled by tier and layer).
func _add_run_metrics(rec: Dictionary, probe: BalanceProbe, _prefix: String) -> void:
	var pools: Dictionary = rec["pools"]
	var runs := probe.runs
	var sc: Dictionary = rec["scalars"]
	if not runs.is_empty() and rec["group"].begins_with("campaign"):
		var layers := 0
		var heal := 0
		var avail := 0
		var used := 0
		for r in runs:
			layers += int(r["layers"])
			heal += int(r["heal_hp"])
			avail += int(r["terminals"])
			used += int(r["terminals_visited"])
		sc["layers_per_run"] = snappedf(float(layers) / runs.size(), 0.01)
		sc["heal_hp_per_run"] = snappedf(float(heal) / runs.size(), 0.01)
		sc["heals_available_per_run"] = snappedf(float(avail) / runs.size(), 0.01)
		sc["heals_used_per_run"] = snappedf(float(used) / runs.size(), 0.01)
	for r in runs:
		if r["kind"] != "netrun":
			continue
		var fr: Array = r["layer_frac"]
		for i in fr.size():
			var key := "hp_frac_arrival.t%d.l%d" % [int(r["tier"]), i + 1]
			pools.get_or_add(key, []).append(fr[i])


## Fight pools of a campaign / netrun: turns and HP lost by enemy category and tier.
func _add_fight_pools(rec: Dictionary, probe: BalanceProbe) -> void:
	if bool(opts["fast"]):
		return  # --fast: metrics only, no per-fight pools
	var pools: Dictionary = rec["pools"]
	for f in probe.fights:
		var key := "%s.t%d" % [f["category"], int(f["tier"])]
		pools.get_or_add("fight_turns." + key, []).append(f["turns"])
		pools.get_or_add("fight_hp_lost." + key, []).append(f["hp_lost"])
		pools.get_or_add("fight_win." + key, []).append(1 if f["won"] else 0)
