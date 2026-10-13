extends SceneTree
## Agent bridge (docs/process/05_CLAUDE_PLAYTESTER.md §11): plays one campaign headless with
## AgentSimulator, handing each decision to an outside agent through request/response files,
## or, with `strategist=heuristic`, to the in-process HeuristicStrategist (no files, no LLM;
## `lookahead=2` turns on its 2-turn combat lookahead).
##   godot --headless --path . -s tools/agent/agent_bridge.gd -- dir=<abs dir> [seed=1000] [ice=0]
##         [class=breaker] [corp=solace] [builtin=combat,node] [max_runs=60]
##         [strategist=heuristic] [lookahead=1|2]
## Writes <dir>/report.json (the CampaignSimulator report plus every decision and its reason)
## and <dir>/done. Needs the autoloads, so it waits a frame like simulate_campaign.gd.

const AgentSimulator := preload("res://tools/agent/agent_simulator.gd")
const HeuristicStrategist := preload("res://tools/agent/heuristic_strategist.gd")


func _init() -> void:
	process_frame.connect(_run, CONNECT_ONE_SHOT)


func _run() -> void:
	var opts := {"dir": "", "seed": "1000", "ice": "0", "class": "breaker", "corp": "solace", "builtin": "", "max_runs": "60",
		"strategist": "", "lookahead": ""}
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=", true, 1)
		if kv.size() == 2 and opts.has(kv[0]):
			opts[kv[0]] = kv[1]
	var dir := String(opts["dir"])
	if dir == "" or not DirAccess.dir_exists_absolute(dir):
		push_error("agent_bridge: dir= must name an existing folder")
		quit(2)
		return
	var registry: Node = root.get_node_or_null(^"ContentRegistry")
	var lookup := ContentLookup.new().add_registry(registry)
	var resolver := CombatResolver.new(registry.config, lookup)
	var builtin: Array = String(opts["builtin"]).split(",", false)
	var sim = AgentSimulator.new(resolver, dir, builtin, StringName(opts["corp"]), StringName(opts["class"]))
	if String(opts["strategist"]) == "heuristic":
		var h = HeuristicStrategist.new(HeuristicStrategistConfigData.shipped(), sim.lookup)
		if String(opts["lookahead"]) != "":
			h.lookahead_turns = int(opts["lookahead"])
		sim.strategist = h
	var t0 := Time.get_ticks_msec()
	var report: Dictionary = sim.run_campaign(int(opts["seed"]), int(opts["ice"]), int(opts["max_runs"]))
	report["decisions"] = sim.decisions
	report["transcript"] = sim.transcript
	report["ms"] = Time.get_ticks_msec() - t0
	var f := FileAccess.open(dir + "/report.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(report, "  "))
	f.close()
	FileAccess.open(dir + "/done", FileAccess.WRITE).close()
	print("AGENT_BRIDGE: %s in %d runs (%d deaths), %d raids, Heat peak %d, %d decisions [%d ms]" % [
		report["outcome"], report["runs"], report["deaths"], report["raids"], report["heat_peak"], sim.decisions.size(), report["ms"]])
	quit(0)
