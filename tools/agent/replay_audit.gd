extends SceneTree
## Replay audit (docs/process/05_CLAUDE_PLAYTESTER.md §11): rebuilds the fights a screen tester
## played (the game's combat replays: setup, seed, every action) and, at every turn, compares what
## the tester did with what was available: the best whole-turn plan (turn_planner.gd), whether any
## plan lands the player's pointer on a Perfect, and where the pointer would have landed with no
## action. One JSON line per turn. Ground truth for "can testers see and reach Perfects?".
##   godot --headless --path . -s tools/agent/replay_audit.gd -- in=<folder of replay_*.json> out=<file.jsonl> [tag=PB-010/halfmoon]

const TurnPlanner := preload("res://tools/agent/turn_planner.gd")


func _init() -> void:
	process_frame.connect(_run, CONNECT_ONE_SHOT)


func _run() -> void:
	var opts := {"in": "", "out": "", "tag": ""}
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=", true, 1)
		if kv.size() == 2 and opts.has(kv[0]):
			opts[kv[0]] = kv[1]
	var registry: Node = root.get_node_or_null(^"ContentRegistry")
	var lookup := ContentLookup.new().add_registry(registry)
	var resolver := CombatResolver.new(registry.config, lookup)
	var out := FileAccess.open(String(opts["out"]), FileAccess.WRITE)
	var files := DirAccess.get_files_at(String(opts["in"]))
	var turns_total := 0
	var fights := 0
	for name in files:
		if not name.begins_with("replay_") or not name.ends_with(".json"):
			continue
		var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(String(opts["in"]).path_join(name)))
		if not data is Dictionary or String(data.get("kind", "")) != CombatReplay.KIND:
			continue
		var actions: Array[CombatAction] = []
		for d in data.get("actions", []):
			actions.append(CombatAction.from_dict(d))
		var setup: Dictionary = data.get("setup", {})
		var enemy_ids: Array[StringName] = []
		for id in setup.get("enemy_ids", []):
			enemy_ids.append(StringName(String(id)))
		var session := CombatSession.start(resolver, StringName(String(setup.get("class_id", ""))), enemy_ids,
			int(String(data.get("seed", "0"))), StringName(String(setup.get("ring_id", ""))),
			int(setup.get("heat_majors_crossed", 0)), setup.get("overrides", {}))
		fights += 1
		var i := 0
		while i < actions.size() and not session.state.is_over():
			# A turn: the tester's actions up to and including END_TURN.
			var turn := session.state.turn
			var plans := TurnPlanner.plans(session)
			var any_perfect := false
			for p in plans:
				if bool(p["outcome"]["own_perfect"]):
					any_perfect = true
			var start := TurnPlanner._finish(session, {"state": session.state, "actions": [] as Array[CombatAction]})
			var mine: Array[CombatAction] = []
			while i < actions.size() and actions[i].type != CombatAction.Type.END_TURN:
				var r := session.apply(actions[i])
				if r.ok() and actions[i].type != CombatAction.Type.TARGET:
					mine.append(actions[i])
				i += 1
			# What the tester's setup would resolve to (the state now, before END_TURN).
			var did := TurnPlanner._finish(session, {"state": session.state, "actions": [] as Array[CombatAction]})
			var best: Dictionary = plans[0]
			out.store_line(JSON.stringify({"tag": opts["tag"], "replay": name, "turn": turn,
				"tester_actions": mine.size(), "tester": {"dealt": did["outcome"]["dealt"], "taken": did["outcome"]["taken"],
					"own_perfect": did["outcome"]["own_perfect"], "pointers": did["outcome"]["pointers"]},
				"no_action": {"dealt": start["outcome"]["dealt"], "taken": start["outcome"]["taken"], "own_perfect": start["outcome"]["own_perfect"]},
				"best": {"text": best["text"], "dealt": best["outcome"]["dealt"], "taken": best["outcome"]["taken"], "own_perfect": best["outcome"]["own_perfect"]},
				"perfect_available": any_perfect}))
			turns_total += 1
			if i < actions.size():
				session.apply(actions[i])  # END_TURN
				i += 1
	out.close()
	print("REPLAY_AUDIT: %d fights, %d turns -> %s" % [fights, turns_total, opts["out"]])
	quit(0)
