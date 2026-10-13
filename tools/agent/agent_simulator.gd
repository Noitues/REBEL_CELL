extends CampaignSimulator
## CampaignSimulator whose decisions go to an outside agent (docs/process/05_CLAUDE_PLAYTESTER.md
## §11). At each decision it writes the state and a menu of options to `<dir>/req_<n>.json` and
## waits for `<dir>/resp_<n>.json` ({"choice": i, "reason": "..."}); the menu's option 0 is
## always what the built-in policy would do, so a timeout or `builtin` for a kind keeps the
## simulator's behaviour. Decision kinds: combat (whole-turn plans from turn_planner.gd), node,
## reward, event, launch, raid. Shops and HQ upkeep stay with the built-in policy (v1).

const TurnPlanner := preload("res://tools/agent/turn_planner.gd")
const POLL_MS := 15
const TIMEOUT_MS := 600000

var dir: String = ""
## kinds answered here by option 0 (the built-in choice) without asking
var builtin: Dictionary = {}
var seq: int = 0
var decisions: Array[Dictionary] = []
var transcript: Array[String] = []


func _init(p_resolver: CombatResolver, p_dir: String, p_builtin: Array, corporation_id: StringName = &"solace", class_id: StringName = &"breaker") -> void:
	super(p_resolver, corporation_id, class_id)
	dir = p_dir
	for k in p_builtin:
		builtin[String(k)] = true


## Asks the agent; returns {"choice": int, "reason": String}.
func ask(kind: String, state: Dictionary, options: Array[String]) -> Dictionary:
	seq += 1
	if builtin.has(kind) or options.size() <= 1:
		decisions.append({"seq": seq, "kind": kind, "choice": 0, "reason": "builtin", "options": options.size()})
		return {"choice": 0, "reason": "builtin"}
	var req := "%s/req_%06d.json" % [dir, seq]
	var resp := "%s/resp_%06d.json" % [dir, seq]
	var tmp := req + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	f.store_string(JSON.stringify({"seq": seq, "kind": kind, "state": state, "options": options}))
	f.close()
	DirAccess.rename_absolute(tmp, req)
	var waited := 0
	while not FileAccess.file_exists(resp) and waited < TIMEOUT_MS:
		OS.delay_msec(POLL_MS)
		waited += POLL_MS
	var out := {"choice": 0, "reason": "timeout"}
	if FileAccess.file_exists(resp):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(resp))
		if parsed is Dictionary:
			out = {"choice": clampi(int(parsed.get("choice", 0)), 0, options.size() - 1), "reason": String(parsed.get("reason", ""))}
	decisions.append({"seq": seq, "kind": kind, "choice": out["choice"], "reason": out["reason"], "options": options.size()})
	transcript.append("[%s] %s  <- %s" % [kind, options[int(out["choice"])], out["reason"]])
	return out


# --- Campaign ----------------------------------------------------------------------------------

func _campaign_state(c: CampaignState) -> Dictionary:
	var ops := PackedStringArray()
	for op in c.living_operatives():
		ops.append("%s (%s R%d, %d HP)" % [op.name, op.class_id, op.rank, op.max_hp])
	return {"heat": c.heat, "schematics": c.schematics, "home": "%d/%d" % [c.grid.home_integrity, c.grid.home_max_integrity],
		"exploits": c.exploits.size(), "operatives": ", ".join(ops), "armory": c.armory.size(),
		"claimed_nodes": c.grid.claimed_ids().size(), "raids_won": c.raids_won, "raids_lost": c.raids_lost}


func _pick_launch(c: CampaignState) -> Dictionary:
	var default := super(c)
	if default.is_empty():
		return default
	var picks: Array[Dictionary] = [default]
	var options: Array[String] = [_launch_text(c, default)]
	var targets := CampaignRules.launchable_sites(c, corp, config)
	targets.append_array(CampaignRules.patrol_sites(c, corp))
	for site in targets:
		if c.grid.is_taken(site.id):
			continue
		for op in c.living_operatives():
			var cls := lookup.get_content(op.class_id) as ClassData
			if CampaignRules.launch_error(c, corp, config, op, cls, site) != "":
				continue
			if op == default["op"] and site == default["site"]:
				continue
			picks.append({"op": op, "site": site})
			options.append(_launch_text(c, picks[-1]))
	var r := ask("launch", _campaign_state(c), options)
	return picks[int(r["choice"])]


func _launch_text(c: CampaignState, pick: Dictionary) -> String:
	var site: SiteData = pick["site"]
	var op: OperativeState = pick["op"]
	var objective: String = RC.SiteObjective.keys()[CampaignRules.site_objective(c, site)]
	if CampaignRules.is_patrol(c, site):
		objective = "PATROL (no objective)"
	return "Send %s (R%d) to %s: tier %d, objective %s, Heat change %+d" % [op.name, op.rank, site.display_name, site.tier, objective, site.heat_change]


func _fight_raids(c: CampaignState, stats: Dictionary) -> void:
	var guard := 0
	while not c.pending_raids.is_empty() and not c.is_over() and guard < 10:
		guard += 1
		_place_for_raid(c)
		var raid_id := String(c.pending_raids[0].get("raid_id", ""))
		CampaignRules.fight_raid(c, corp, config, lookup, c.pending_raids[0])
		stats["raids"] = int(stats["raids"]) + 1
		stats["log"].append("  raid %s: %s, home %d/%d" % [raid_id, "won" if bool(c.last_raid.get("won", false)) else "lost", c.grid.home_integrity, c.grid.home_max_integrity])
		stats["heat_peak"] = maxi(int(stats["heat_peak"]), c.heat)


## Raid setup: a few placement plans, each with the exact projected outcome (raids are deterministic).
func _place_for_raid(c: CampaignState) -> void:
	if c.armory.is_empty():
		return
	var plans: Array[Dictionary] = []
	plans.append({"name": "spread from home outward (default)", "order": c.grid.claimed_ids()})
	plans.append({"name": "everything on the home server", "order": [c.grid.home_site_id]})
	var others := c.grid.claimed_ids().filter(func(id: StringName) -> bool: return id != c.grid.home_site_id)
	if not others.is_empty():
		var rev := others.duplicate()
		rev.append(c.grid.home_site_id)
		plans.append({"name": "outer nodes first, home last", "order": rev})
	var options: Array[String] = []
	for p in plans:
		var trial := c.duplicate_state()
		_deploy_in_order(trial, p["order"])
		var proj := CampaignRules.project_raid(trial, corp, config, lookup, trial.pending_raids[0])
		options.append("%s: projected %s, home %d -> %d, threats destroyed %d, reached home %d, DOWN %s, TAKEN %s" % [
			p["name"], "CELL HOLDS" if proj.won else ("BREACHED" if proj.campaign_lost else "lost"), proj.home_before, proj.home_after,
			proj.threats_destroyed, proj.threats_reached_home, ",".join(proj.down) if not proj.down.is_empty() else "none",
			",".join(proj.taken) if not proj.taken.is_empty() else "none"])
	var state := _campaign_state(c)
	state["raid"] = String(c.pending_raids[0].get("raid_id", ""))
	var r := ask("raid", state, options)
	_deploy_in_order(c, plans[int(r["choice"])]["order"])


func _deploy_in_order(c: CampaignState, order: Array) -> void:
	for site_id in order:
		while not c.armory.is_empty() and c.grid.is_active_node(site_id) \
				and c.grid.assets_on(site_id).size() < CampaignRules.asset_slots(c, lookup, site_id, config):
			if CampaignRules.deploy_asset(c, config, lookup, 0, site_id)[0]["type"] == "refused":
				break


# --- Run ----------------------------------------------------------------------------------------

func _run_state(s: NetrunSession) -> Dictionary:
	var op := s.run.operative
	var deck := PackedStringArray()
	for id in op.deck:
		var card := lookup.get_content(id) as CardData
		deck.append(card.display_name if card != null else String(id))
	return {"hp": "%d/%d" % [op.hp, op.max_hp], "cycles": s.run.cycles, "tier": s.run.tier, "deck": ", ".join(deck),
		"firmware": ", ".join(op.slot_firmware_ids.filter(func(x: StringName) -> bool: return x != &"")),
		"daemons": ", ".join(op.daemon_ids), "heat": s.campaign.heat}


func _play_run(s: NetrunSession, stats: Dictionary) -> void:
	var steps := 0
	while not s.run.is_over() and steps < MAX_STEPS_PER_RUN:
		steps += 1
		match s.run.phase:
			RunState.Phase.MAP:
				var next := _pick_node(s)
				if next == &"":
					break
				s.enter_node(next)
			RunState.Phase.COMBAT:
				_play_fight(s, stats)
				if s.in_combat():
					break
			RunState.Phase.REWARD:
				_take_reward(s)
			RunState.Phase.EVENT:
				_choose_event(s)
			RunState.Phase.SHOP:
				var bug := s.run.operative.deck.find(&"bug")
				if bug >= 0 and s.run.cycles >= s.card_removal_price():
					s.remove_card(bug)
				s.leave_shop()
			RunState.Phase.RAID:
				for i in range(s.run_assets().size() - 1, -1, -1):
					s.raid_deploy_run_asset(i, s.campaign.grid.home_site_id)
				s.raid_fight()
				stats["raids"] = int(stats["raids"]) + 1
			_:
				break


func _play_fight(s: NetrunSession, stats: Dictionary) -> void:
	stats["fights"] = int(stats["fights"]) + 1
	var turns := 0
	var hp_in := s.combat.state.player.hp
	var foes := PackedStringArray()
	for e in s.combat.state.living_enemies(false):
		foes.append(String(e.source_id))
	while s.in_combat() and turns < MAX_TURNS_PER_FIGHT:
		turns += 1
		CombatBot._retarget(s.combat, s.combat_action)
		var plans := TurnPlanner.plans(s.combat)
		var options: Array[String] = []
		for p in plans:
			options.append(String(p["text"]))
		var st := _run_state(s)
		st["turn"] = s.combat.state.turn
		st["ram"] = s.combat.state.ram
		st["fight"] = ", ".join(foes)
		var r := ask("combat", st, options)
		for a in plans[int(r["choice"])]["actions"]:
			var res := s.combat_action(a)
			if res == null or not res.ok():
				break
		if s.in_combat():
			s.combat_action(CombatAction.end_turn())
	stats["turns"] = int(stats["turns"]) + turns
	var outcome := "died" if s.run.outcome == RunState.Outcome.DIED else ("stuck" if s.in_combat() else "won")
	if outcome == "stuck":
		stats["stuck"] = int(stats["stuck"]) + 1
	stats["log"].append("  FIGHT %s vs %s: %d turns, HP %d -> %d" % [outcome, ", ".join(foes), turns, hp_in, s.run.operative.hp])


func _pick_node(s: NetrunSession) -> StringName:
	var default := super(s)
	var ids: Array[StringName] = [default]
	for id in s.available_nodes():
		if id != default:
			ids.append(id)
	var options: Array[String] = []
	for id in ids:
		var node := s.run.map.get_node(id)
		var kind: String = RC.InfilNodeType.keys()[int(node["type"])]
		if node["elite"]:
			kind = "ELITE " + kind
		options.append("%s at layer %d (Heat %+d)" % [kind, int(node["layer"]), s.node_heat(id)])
	return ids[int(ask("node", _run_state(s), options)["choice"])]


func _take_reward(s: NetrunSession) -> void:
	var offer := s.current_reward()
	var kind := String(offer["kind"])
	if kind not in ["card", "firmware", "daemon"]:
		super(s)
		return
	var picks: Array = []  # [index, slot] or [] for skip
	var options: Array[String] = []
	var raw: Array = offer["options"]
	for i in raw.size():
		var res := lookup.get_content(StringName(String(raw[i])))
		var name: String = res.get("display_name") if res != null else String(raw[i])
		var desc: String = res.get("description") if res != null else ""
		if kind == "firmware":
			for slot in range(1, s.run.operative.slot_slice_ids.size()):
				if s.run.operative.slot_firmware_ids[slot] != &"":
					continue
				var slice := lookup.get_content(s.run.operative.slot_slice_ids[slot]) as SliceData
				picks.append([i, slot])
				options.append("Firmware %s into slot %d (%s): %s" % [name, slot + 1, slice.display_name if slice != null else "?", desc])
		else:
			picks.append([i, -1])
			options.append("%s %s: %s" % [kind.capitalize(), name, desc])
	picks.insert(0, [])
	options.insert(0, "Skip this reward")
	var r := ask("reward", _run_state(s), options)
	var pick: Array = picks[int(r["choice"])]
	if pick.is_empty():
		s.skip_reward()
		return
	var ev := s.choose_reward(int(pick[0]), int(pick[1]))
	if not ev.is_empty() and String(ev[ev.size() - 1].get("type", "")) == "refused":
		s.skip_reward()


func _choose_event(s: NetrunSession) -> void:
	var ev := s.current_event()
	var idx: Array[int] = []
	var options: Array[String] = []
	for i in ev.choices.size():
		var ch := ev.choices[i]
		if s.choice_error(ch) != "":
			continue
		idx.append(i)
		var costs := s.choice_costs(ch)
		options.append("%s%s" % [ch.label, (" (" + costs + ")") if costs != "" else ""])
	if idx.is_empty():
		s.choose_event_option(ev.choices.size() - 1)
		return
	# Option 0 = the built-in policy's pick (the last allowed choice).
	idx.reverse()
	options.reverse()
	var st := _run_state(s)
	st["event"] = "%s: %s" % [ev.title, ev.text.substr(0, 400)]
	s.choose_event_option(idx[int(ask("event", st, options)["choice"])])
