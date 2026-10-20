extends SceneTree
## BalanceSim CLI (docs/handoff/plan2/BALANCE_SIM.md S1). Logic only: no scene, no window.
##   godot --headless --path . -s tools/balance/balance_sim.gd -- <mode> [options] --out <file.json>
## modes: campaign | fight | boss | netrun
## options (all optional):
##   --seeds 1000:1019 | 1000,1004      seeds (inclusive range or list)           [1000:1004]
##   --policy builtin|heuristic|reference   --lookahead 1|2 (heuristic)           [builtin]
##                                      reference = heuristic at reference_lookahead (BAL-01, default 2)
##   --skill 0..1                       share of combat turns played well         [1.0]
##   --ice N   --corp ID   --class ID   --max-runs N                              [0 solace breaker 60]
##   --set <id>.<prop>=<json>           data override on a COPY (repeatable); also  *=  and  +=
##   --variant file.json                {"name": "...", "set": ["a=b", ...]}      (repeatable)
##   --fast                             metrics only: no per-fight pools (smaller reports, less work)
##   --no-quiet                         keep event texts (default: skipped, results identical)
##   fight:  --enemy ID[,ID]|all  --tiers 1,2,3,4  --categories enemy,elite,mini_boss
##   netrun: --tier N              boss: --source campaign|fresh|save  [--state FILE|DIR] [--dump-state DIR]
## The driver tools/balance/balance.py shards seeds, merges and writes the markdown report.

const BalanceRunner := preload("res://tools/balance/balance_runner.gd")


func _init() -> void:
	process_frame.connect(_run, CONNECT_ONE_SHOT)  # the autoloads (ContentRegistry) exist after a frame


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.is_empty():
		push_error("balance_sim: usage: -- <campaign|fight|boss|netrun> [--seeds a:b] [--set path=value] --out file.json")
		quit(2)
		return
	var mode := String(args[0])
	var opts := {}
	var specs: Array = []
	var seeds: Array = [1000, 1001, 1002, 1003, 1004]
	var out_path := ""
	var i := 1
	while i < args.size():
		var key := String(args[i])
		if key == "--fast" or key == "--no-quiet":
			opts["fast" if key == "--fast" else "quiet"] = key == "--fast"
			i += 1
			continue
		var val := String(args[i + 1]) if i + 1 < args.size() else ""
		i += 2
		match key:
			"--seeds":
				seeds = _parse_seeds(val)
			"--policy":
				opts["policy"] = val
			"--lookahead":
				opts["lookahead"] = int(val)
			"--skill":
				opts["skill"] = float(val)
			"--ice":
				opts["ice"] = int(val)
			"--corp":
				opts["corp"] = val
			"--class":
				opts["class"] = val
			"--max-runs":
				opts["max_runs"] = int(val)
			"--tier":
				opts["tier"] = int(val)
			"--tiers":
				opts["tiers"] = _ints(val)
			"--enemy":
				opts["enemy"] = Array(val.split(",", false))
			"--categories":
				opts["categories"] = Array(val.split(",", false))
			"--source":
				opts["source"] = val
			"--state":
				opts["state"] = val
			"--dump-state":
				opts["dump_state"] = val
			"--set":
				specs.append(val)
			"--variant":
				var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(val))
				if not (parsed is Dictionary):
					push_error("balance_sim: cannot read variant '%s'" % val)
					quit(2)
					return
				for sp in parsed.get("set", []):
					specs.append(String(sp))
			"--out":
				out_path = val
			_:
				push_error("balance_sim: unknown option '%s'" % key)
				quit(2)
				return
	var registry: Node = root.get_node_or_null(^"ContentRegistry")
	var runner := BalanceRunner.new(registry, opts, specs)
	if not runner.errors.is_empty():
		for e in runner.errors:
			push_error("balance_sim: " + e)
		quit(2)
		return
	var report := runner.run(mode, seeds)
	var text := JSON.stringify(report, "", true)
	if out_path != "":
		var f := FileAccess.open(out_path, FileAccess.WRITE)
		if f == null:
			push_error("balance_sim: cannot write '%s'" % out_path)
			quit(2)
			return
		f.store_string(text)
		f.close()
	else:
		print(text)
	print("BALANCE_SIM: %s %d records%s" % [mode, report["records"].size(), " -> " + out_path if out_path != "" else ""])
	quit(0)


static func _parse_seeds(text: String) -> Array:
	if ":" in text:
		var ends := text.split(":")
		var out: Array = []
		for sd in range(int(ends[0]), int(ends[1]) + 1):
			out.append(sd)
		return out
	return _ints(text)


static func _ints(text: String) -> Array:
	var out: Array = []
	for p in text.split(",", false):
		out.append(int(p))
	return out
