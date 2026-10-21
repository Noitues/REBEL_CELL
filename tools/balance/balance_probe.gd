extends RefCounted
## BalanceProbe (BALANCE_SIM S2): the metrics collector. Plugged into CampaignSimulator /
## AgentSimulator through their `probe` hook and into a NetrunSession through `combat_observer`;
## it only reads the state it is handed. Collects three kinds of records:
##   fights  one per combat: turns, damage dealt / taken, HP lost, Perfect rate, RAM left, enemy self-heal, boss phases
##   runs    one per netrun: HP on arrival per layer (the attrition curve), heal HP, terminals, outcome, Heat
##   campaign Heat curve, raids (flatline Heat vs actions), Schematics income / spend, recruits
## "Perfect" counts the player's first pointer (the read head the Perfect streak uses), as the resolver does.

var lookup: ContentLookup = null
var config: CampaignConfigData = null

var fights: Array[Dictionary] = []
var runs: Array[Dictionary] = []
var raids: Array[Dictionary] = []
## Heat after each run (the campaign's Heat curve).
var heat_curve: Array = []
var schematics_income: int = 0
var schematics_spent: int = 0
## Campaign figures read at the last hook (the simulators' reports do not all carry them).
var schematics_last: int = 0
var recruits: int = 0
var raid_causes: Dictionary = {"flatline": 0, "heat_actions": 0, "other": 0}

var _fight: Dictionary = {}
var metrics_enabled: bool = true  # N19: off only in the purity test
var _metrics: SimMetrics = null  # N19: observational per-phase metrics of the fight in progress
var _run: Dictionary = {}
var _sch_mark: int = -1
## Diagnostic: a file the probe appends a timestamped line to at every run start, fight start and combat action (tool-only).
var trace_path: String = ""


func _init(p_lookup: ContentLookup, p_config: CampaignConfigData) -> void:
	lookup = p_lookup
	config = p_config


# --- Simulator hooks --------------------------------------------------------------------------

func on_maintain(c: CampaignState, schematics_before: int) -> void:
	if _sch_mark < 0:
		_sch_mark = schematics_before
	if schematics_before > _sch_mark:
		schematics_income += schematics_before - _sch_mark
	schematics_spent += maxi(0, schematics_before - c.schematics)
	_sch_mark = c.schematics
	trace("maintain heat=%d schematics=%d->%d heat_purchases=%d" % [c.heat, schematics_before, c.schematics, c.heat_purchases])


## Appends one line to `trace_path` (no-op when unset).
func trace(msg: String) -> void:
	if trace_path == "":
		return
	var f := FileAccess.open(trace_path, FileAccess.READ_WRITE if FileAccess.file_exists(trace_path) else FileAccess.WRITE)
	if f != null:
		f.seek_end()
		f.store_line("%d %s" % [Time.get_ticks_msec(), msg])
		f.close()


func on_run_start(c: CampaignState, op: OperativeState, _site: SiteData, s: NetrunSession) -> void:
	trace("run_start site=%s rank=%d" % [_site.id if _site != null else "-", op.rank])
	attach(s)
	begin_run(c, op, s)


## Starts a run record (also used by the netrun and fight modes, which build their own session).
func begin_run(c: CampaignState, op: OperativeState, s: NetrunSession) -> void:
	var terminals := 0
	for n in s.run.map.all_nodes():
		if int(n["type"]) == RC.InfilNodeType.TERMINAL:
			terminals += 1
	_run = {"tier": s.run.tier, "kind": s.run.kind, "operative": String(op.id), "rank": op.rank, "hp_max": op.max_hp,
		"layer_hp": [], "layer_frac": [], "heal_hp": 0, "hp_mark": s.run.operative.hp, "heat_before": c.heat,
		"queued_before": _queued(c), "terminals": terminals, "fights": 0}


## Routes the session's combat actions to observe().
func attach(s: NetrunSession) -> void:
	s.combat_observer = Callable(self, "observe")


func on_node(s: NetrunSession) -> void:
	if _run.is_empty():
		return
	var hp := s.run.operative.hp
	if hp > int(_run["hp_mark"]):
		_run["heal_hp"] = int(_run["heal_hp"]) + hp - int(_run["hp_mark"])
	_run["hp_mark"] = hp
	_run["layer_hp"].append(hp)
	_run["layer_frac"].append(snappedf(float(hp) / maxf(1.0, float(s.run.operative.max_hp)), 0.0001))


func on_fight_begin(s: NetrunSession) -> void:
	trace("fight_begin tier=%d kind=%s" % [s.run.tier, s.run.kind])
	begin_fight(s.combat.state, s.run.tier, s.run.kind, s.run.visited.size())
	_run["fights"] = int(_run.get("fights", 0)) + 1


## Starts a fight record from a live combat state.
func begin_fight(state: CombatState, tier: int, kind: String, layer: int) -> void:
	var foe: CombatantState = null
	var hp_total := 0
	for e in state.enemies:
		if e.is_satellite:
			continue
		if foe == null:
			foe = e
		hp_total += e.max_hp
	var data := lookup.get_content(foe.source_id) as EnemyData if foe != null else null
	var category := "enemy"
	if data != null:
		category = "boss" if data.is_boss else ("mini_boss" if data.is_mini_boss else ("elite" if data.is_elite else "enemy"))
	_metrics = SimMetrics.new(state.player.id) if metrics_enabled else null
	_fight = {"enemy": String(foe.source_id) if foe != null else "", "category": category, "tier": tier, "kind": kind, "layer": layer,
		"turns": 0, "hp_in": state.player.hp, "hp_max": state.player.max_hp, "hp_out": state.player.hp, "dealt": 0, "taken": 0, "enemy_hp": hp_total,
		"pointers": 0, "perfects": 0, "heal_turns": 0, "heal_total": 0, "ram_left": 0, "ram_mark": state.ram,
		"phase_turns": [1], "player_hp": [], "enemy_frac": [], "won": false, "dead": false, "stuck": false, "done": false,
		"_prev_player": state.player.hp, "_prev_enemy": _enemy_hp(state)}


## One accepted combat action: (action, result, state after it).
func observe(action: CombatAction, result: CombatResult, state: CombatState) -> void:
	trace("action turn=%d" % state.turn)
	if _fight.is_empty() or bool(_fight["done"]):
		return
	if _metrics != null:
		_metrics.observe(action.type == CombatAction.Type.END_TURN, result.events, _enrage_max(state))
	if action.type != CombatAction.Type.END_TURN:
		_fight["ram_mark"] = state.ram
	else:
		_fight["turns"] = int(_fight["turns"]) + 1
		_fight["ram_left"] = int(_fight["ram_left"]) + int(_fight["ram_mark"])
		var healed_this_turn := false
		for ev in result.events:
			match String(ev.get("type", "")):
				"pointer":
					if ev["owner"] == state.player.id and int(ev["pointer_index"]) == 0:
						_fight["pointers"] = int(_fight["pointers"]) + 1
						if int(ev["tier"]) == RC.PrecisionTier.PERFECT:
							_fight["perfects"] = int(_fight["perfects"]) + 1
				"heal":
					if ev["target"] != state.player.id and int(ev["amount"]) > 0:
						_fight["heal_total"] = int(_fight["heal_total"]) + int(ev["amount"])
						healed_this_turn = true
				"boss_phase":
					_fight["phase_turns"].append(int(_fight["turns"]) + 1)
		if healed_this_turn:
			_fight["heal_turns"] = int(_fight["heal_turns"]) + 1
		var enemy_now := _enemy_hp(state)
		var player_now := state.player.hp
		_fight["dealt"] = int(_fight["dealt"]) + maxi(0, int(_fight["_prev_enemy"]) - enemy_now)
		_fight["taken"] = int(_fight["taken"]) + maxi(0, int(_fight["_prev_player"]) - player_now)
		_fight["_prev_enemy"] = enemy_now
		_fight["_prev_player"] = player_now
		_fight["player_hp"].append(player_now)
		_fight["enemy_frac"].append(snappedf(float(enemy_now) / maxf(1.0, float(_fight["enemy_hp"])), 0.0001))
		_fight["ram_mark"] = state.ram
	if state.is_over():
		if action.type != CombatAction.Type.END_TURN:
			_fight["turns"] = int(_fight["turns"]) + 1  # a card finished it mid-turn
			if _metrics != null:
				_metrics.finish_mid_turn()
			_fight["dealt"] = int(_fight["dealt"]) + maxi(0, int(_fight["_prev_enemy"]) - _enemy_hp(state))
			_fight["taken"] = int(_fight["taken"]) + maxi(0, int(_fight["_prev_player"]) - state.player.hp)
		_fight["won"] = state.outcome == CombatState.Outcome.VICTORY
		_fight["dead"] = state.outcome == CombatState.Outcome.DEFEAT
		_fight["hp_out"] = maxi(0, state.player.hp)
		_finish_fight()


func on_fight_end(_s: NetrunSession, _turns: int) -> void:
	if not _fight.is_empty() and not bool(_fight["done"]):
		_fight["stuck"] = true
		_fight["hp_out"] = int(_fight["_prev_player"])
		_finish_fight()
	_fight = {}


func on_run_end(c: CampaignState, s: NetrunSession, _op: OperativeState, _site: SiteData) -> void:
	end_run(c, s)
	trace("run_end site=%s tier=%d kind=%s outcome=%s exploits=%d heat=%d" % [_site.id if _site != null else "-", s.run.tier, s.run.kind, RunState.Outcome.keys()[s.run.outcome], c.exploits.size(), c.heat])
	heat_curve.append(c.heat)
	schematics_last = c.schematics
	recruits = c.next_operative_number - 1 - config.starting_rookies
	if _sch_mark >= 0:
		schematics_income += maxi(0, c.schematics - _sch_mark)
	_sch_mark = c.schematics


## Closes the run record: outcome, layers, terminals, Heat and where its new raids came from.
func end_run(c: CampaignState, s: NetrunSession) -> void:
	if _run.is_empty():
		return
	var visited_terminals := 0
	for id in s.run.visited:
		if int(s.run.map.get_node(id)["type"]) == RC.InfilNodeType.TERMINAL:
			visited_terminals += 1
	var died := s.run.outcome == RunState.Outcome.DIED
	var heat_delta := c.heat - int(_run["heat_before"])
	var death_heat := HeatRules.death_heat(c, config, s.run.tier) if died else 0
	var new_raids := _queued(c) - int(_run["queued_before"])
	var causes := {"flatline": 0, "heat_actions": 0, "other": 0}
	if new_raids > 0:
		var first := maxi(0, c.pending_raids.size() - new_raids)
		for i in range(first, c.pending_raids.size()):
			var entry: Dictionary = c.pending_raids[i]
			if int(entry.get("source", -1)) != RC.RaidTriggerSource.HEAT_THRESHOLD:
				causes["other"] += 1
			elif died and int(_run["heat_before"]) + maxi(0, heat_delta - death_heat) < int(entry.get("heat", 0)):
				causes["flatline"] += 1
			else:
				causes["heat_actions"] += 1
		# raids already fought inside the run (interlude) are no longer pending: they came from the run's own Heat
		causes["heat_actions"] += maxi(0, new_raids - (c.pending_raids.size() - first))
	for k in causes:
		raid_causes[k] = int(raid_causes[k]) + int(causes[k])
	_run["outcome"] = RunState.Outcome.keys()[s.run.outcome]
	_run["died"] = died
	_run["layers"] = s.run.visited.size()
	_run["terminals_visited"] = visited_terminals
	_run["cycles"] = s.run.cycles
	_run["hp_end"] = s.run.operative.hp
	_run["heat_delta"] = heat_delta
	_run["raid_causes"] = causes
	_run.erase("hp_mark")
	_run.erase("queued_before")
	_run.erase("heat_before")
	runs.append(_run)
	_run = {}


func on_raid(c: CampaignState) -> void:
	schematics_last = c.schematics
	raids.append({"won": bool(c.last_raid.get("won", false)), "heat": c.heat})
	if _sch_mark >= 0:
		schematics_income += maxi(0, c.schematics - _sch_mark)
	_sch_mark = c.schematics


# --- Helpers ----------------------------------------------------------------------------------

func _finish_fight() -> void:
	_fight["done"] = true
	var f := _fight.duplicate(true)
	f.erase("_prev_player")
	f.erase("_prev_enemy")
	f.erase("ram_mark")
	f["metrics"] = _metrics.to_dict(bool(f["won"])) if _metrics != null else null
	f["hp_lost"] = int(f["hp_in"]) - int(f["hp_out"])
	fights.append(f)
	_fight["done"] = true


static func _enrage_max(state: CombatState) -> int:
	var top := 0
	for e in state.enemies:
		top = maxi(top, e.enrage_step)
	return top


static func _enemy_hp(state: CombatState) -> int:
	var total := 0
	for e in state.enemies:
		if e.is_alive() and not e.is_satellite:
			total += e.hp
	return total


static func _queued(c: CampaignState) -> int:
	return c.pending_raids.size() + c.raids_won + c.raids_lost
