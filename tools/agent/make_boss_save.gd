extends SceneTree
## Plays a campaign with the HeuristicStrategist (as state_agent.py --strategist heuristic) and stops
## at the first moment it would launch the Genome Core breach, then writes that campaign through the
## game's real save path (change plan 1 V4; docs/process/05_CLAUDE_PLAYTESTER.md "Boss save (V4)").
##   godot --headless --path . -s tools/agent/make_boss_save.gd -- seed=<n> out=<abs dir> [slot=1]
##         [ice=0] [class=breaker] [corp=solace] [max_runs=60]
## Prints one summary line; exit 1 when the seed never reaches a breach within max_runs.

const BossStopSimulator := preload("res://tools/agent/boss_stop_simulator.gd")
const HeuristicStrategist := preload("res://tools/agent/heuristic_strategist.gd")


func _init() -> void:
	process_frame.connect(_run, CONNECT_ONE_SHOT)


func _run() -> void:
	var opts := {"out": "", "seed": "1000", "slot": "1", "ice": "0", "class": "breaker", "corp": "solace", "max_runs": "60"}
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=", true, 1)
		if kv.size() == 2 and opts.has(kv[0]):
			opts[kv[0]] = kv[1]
	var out := String(opts["out"])
	if out == "":
		push_error("make_boss_save: out= must name a folder")
		quit(2)
		return
	DirAccess.make_dir_recursive_absolute(out)
	var registry: Node = root.get_node(^"ContentRegistry")
	var lookup := ContentLookup.new().add_registry(registry)
	var resolver := CombatResolver.new(registry.config, lookup)
	var sim = BossStopSimulator.new(resolver, out, [], StringName(opts["corp"]), StringName(opts["class"]))
	sim.strategist = HeuristicStrategist.new(HeuristicStrategistConfigData.shipped(), sim.lookup)
	sim.run_campaign(int(opts["seed"]), int(opts["ice"]), int(opts["max_runs"]))
	if not sim.reached_breach:
		print("MAKE_BOSS_SAVE: seed %s never reached a breach in %s runs" % [opts["seed"], opts["max_runs"]])
		quit(1)
		return
	var err: Error = BossSaveWriter.write(root.get_node(^"SaveService"), root.get_node(^"RngService"), sim.final_campaign, out, String(opts["slot"]))
	if err != OK:
		push_error("make_boss_save: write failed (%d)" % err)
		quit(2)
		return
	print("MAKE_BOSS_SAVE: " + BossSaveWriter.summary(sim.final_campaign))
	quit(0)
