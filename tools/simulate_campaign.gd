extends SceneTree
## Balance simulation (gap analysis V4): plays bot campaigns and prints pacing against
## GDD 11.8 (average campaign ≈ 24 runs / 6 h 35 m; ≈ 7 raids; Heat peaks 85-90 at ICE 5).
##   godot --headless --path . -s tools/simulate_campaign.gd -- [seeds=5] [ice=0]
## Needs the autoloads (content registry), so it runs as a main-loop script that waits a
## frame for them before simulating.

func _init() -> void:
	process_frame.connect(_run, CONNECT_ONE_SHOT)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var seeds := int(args[0]) if args.size() > 0 else 5
	var ice := int(args[1]) if args.size() > 1 else 0
	var verbose := args.has("verbose")
	var registry: Node = root.get_node_or_null(^"ContentRegistry")
	var lookup := ContentLookup.new().add_registry(registry)
	var resolver := CombatResolver.new(registry.config, lookup)
	var sim := CampaignSimulator.new(resolver)
	var wins := 0
	var totals := {"runs": 0.0, "raids": 0.0, "heat_peak": 0.0, "deaths": 0.0, "est_hours": 0.0}
	for i in seeds:
		var start := Time.get_ticks_msec()
		var r := sim.run_campaign(1000 + i, ice)
		if r["outcome"] == "WON":
			wins += 1
		for k in totals:
			totals[k] += float(r[k])
		print("seed %d ICE %d: %s in %d runs (%d completed, %d deaths), %d raids (%d won), Heat peak %d, breach at Heat %d, ~%.1f h, %d fights, %d stuck [%d ms]" % [
			r["seed"], ice, r["outcome"], r["runs"], r["completed"], r["deaths"], r["raids"], r["raids_won"], r["heat_peak"],
			r["heat_at_breach"], r["est_hours"], r["fights"], r["stuck"], Time.get_ticks_msec() - start])
		if verbose:
			for line in r["log"]:
				print("    ", line)
	print("SIMULATION: ICE %d, %d/%d won; mean runs %.1f, raids %.1f, Heat peak %.1f, deaths %.1f, ~%.1f h" % [ice, wins, seeds,
		totals["runs"] / seeds, totals["raids"] / seeds, totals["heat_peak"] / seeds, totals["deaths"] / seeds, totals["est_hours"] / seeds])
	quit(0)
