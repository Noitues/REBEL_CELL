extends SceneTree
const BalanceContent := preload("res://tools/balance/balance_content.gd")
## Phase 2b tool: plays Solace campaigns with the builtin bot and prints one line per seed for the Infected Tide's pacing:
##   godot --headless --path . -s tools/raid_tide/tide_sim.gd -- --seeds 1000:1019 [--careless] [--set config.solace_tide_raid_every=4]
## Line: seed outcome runs deaths raids raids_lost heat_end. `--careless` plays every raid with no sentry and HOLD (the careless
## player); without it the automatic defense plays (the skilled player). Raids per netrun = raids / runs.

func _init() -> void:
	process_frame.connect(_run, CONNECT_ONE_SHOT)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var seeds: Array = []
	var specs: Array = []
	var careless := false
	var i := 0
	while i < args.size():
		match String(args[i]):
			"--seeds":
				var p := String(args[i + 1]).split(":")
				for s in range(int(p[0]), int(p[1]) + 1):
					seeds.append(s)
				i += 2
			"--set":
				specs.append(String(args[i + 1]))
				i += 2
			"--careless":
				careless = true
				i += 1
			_:
				i += 1
	var content := BalanceContent.new(root.get_node(^"ContentRegistry"))
	var errors := content.apply_all(specs)
	if not errors.is_empty():
		printerr("tide_sim: ", errors)
	var resolver := CombatResolver.new(content.config, content.lookup)
	resolver.quiet = true
	for sd in seeds:
		var sim := CampaignSimulator.new(resolver, &"solace", &"breaker")
		if careless:
			sim.raid_plan = {"place": {"sentries": {}, "ghost": &""}, "resp": ["HOLD"]}
		var r: Dictionary = sim.run_campaign(sd, 0, 60)
		print("TIDE %d %s %d %d %d %d %d" % [sd, r["outcome"], r["runs"], r["deaths"], r["raids"], r["raids_lost"], r["heat_end"]])
	quit(0)
