extends SceneTree
## Flow check of the lab model (not the golden parity): plans, undo, the 3-raid leg played in both SPOOF_MODEs,
## forecast = real result for the revealed candidate, ledger reconciles on every raid.
##   godot --headless --path . -s res://tools/raid_lab_m10/flow_check.gd

var _fails: int = 0


func _ok(label: String, cond: bool) -> void:
	if not cond:
		_fails += 1
	print("%s %s" % ["PASS" if cond else "FAIL", label])


func _init() -> void:
	_rules_flow()
	for mode in ["choice", "press"]:
		for repair in ["value", "half"]:
			M10Config.reset()
			M10Config.toggles["SPOOF_MODE"] = mode
			M10Config.toggles["REPAIR"] = repair
			_play_leg(mode, repair)
	for mode in ["choice", "press"]:
		_view_flow(mode)
	M10Config.reset()
	print("FLOW %s" % ("PASS" if _fails == 0 else "FAIL"))
	quit(0 if _fails == 0 else 1)


func _rules_flow() -> void:
	M10Config.reset()
	var m := M10Model.new()
	_ok("leg starts on network 22, key 19, Heat 52", m.seed_id() == 22 and m.key == 19 and m.heat == 52)
	_ok("ghost on an empty node refused", m.why_not("ghost", Vector2i(0, 1)) != "")
	_ok("ghost on an asset node allowed", m.place("ghost", Vector2i(3, 0)))
	_ok("a ghost charges Heat at once (52 -> 57)", m.heat_now() == 57 and m.heat == 52)
	_ok("second ghost refused (scarce)", m.why_not("ghost", Vector2i(2, 0)) != "")
	_ok("decoy on an asset node refused", m.why_not("decoy", Vector2i(2, 0)) != "")
	_ok("decoy on an empty node allowed", m.place("decoy", Vector2i(3, 1)))
	_ok("a decoy charges the key at once (19 -> 16)", m.key_now() == 16 and m.key == 19)
	_ok("second decoy refused (scarce)", m.why_not("decoy", Vector2i(0, 1)) != "")
	_ok("go dark on an asset node", m.place("dark", Vector2i(0, 0)))
	_ok("dark node: income lost = v // 2 + 1 = 3", M10Rules.plan_dark_loss(m.assets, m.plan) == 3)
	_ok("a lever node takes no second lever", m.why_not("dark", Vector2i(3, 0)) != "")
	_ok("undo takes the last lever off", m.undo() and not m.plan["dark"].has(Vector2i(0, 0)))
	_ok("undo twice more clears the plan", m.undo() and m.undo() and not m.can_undo())
	_ok("Heat and key back to start after undo", m.heat_now() == 52 and m.key_now() == 19)
	m.place("ghost", Vector2i(3, 0))
	_ok("click-remove takes a placed lever off", m.remove_at(Vector2i(3, 0)) and m.plan["ghost"].is_empty())
	# The bracket is the min..max over the candidates, from the same forecast function.
	m.place("decoy", Vector2i(3, 1))
	m.place("ghost", Vector2i(3, 0))
	m.place("dark", Vector2i(0, 0))
	var fc := m.forecast_all()
	var rng := m.loss_range()
	var reps: Array = []
	for f in fc:
		reps.append(f["repair"])
	_ok("loss range = min..max of the candidate repairs", rng[0] == reps.min() and rng[1] == reps.max())
	_ok("forecast has one entry per sealed candidate", fc.size() == 3)


## A scripted play of the whole leg in one SPOOF_MODE / REPAIR setting.
func _play_leg(mode: String, repair: String) -> void:
	var m := M10Model.new()
	var tag := "[%s/%s]" % [mode, repair]
	_ok(tag + " leg is networks 22, 17, 25", M10Config.LEG_SEEDS == [22, 17, 25])
	for i in range(M10Config.LEG_SEEDS.size()):
		_ok("%s raid %d is network %d" % [tag, i + 1, M10Config.LEG_SEEDS[i]], m.seed_id() == M10Config.LEG_SEEDS[i])
		var plan_name: String = ["best_sealed", "best_both", "ghost_biggest"][i]
		m.plan = M10Data.plan_of(m.case_["plans"][plan_name])
		var fc := M10Rules.forecast(m.assets, m.b1, m.cands[m.reveal], m.own3, m.plan)
		var play := m.make_play()
		var seen: Array = []
		var landed := false
		var guard := 0
		var step_ok := true
		while not play.is_done() and guard < 4000:
			if not seen.has(play.state):
				seen.append(play.state)
			if play.state == M10Play.S.DECIDE:
				# Raid 1: aim at the line's first node. Raid 2: hold the spoof. Raid 3: aim at the last node.
				var line: Array = play.line2()
				if i == 0:
					step_ok = step_ok and not play.can_target(Vector2i(9, 9)) and play.choose_spoof(line[0])
				elif i == 1:
					step_ok = step_ok and play.pass_spoof()
				else:
					step_ok = step_ok and play.choose_spoof(line[line.size() - 1])
			elif play.state == M10Play.S.PRESS:
				# Raid 1 lands the press, raid 3 mistimes it.
				if i == 0:
					play.advance(0.0, M10Config.PRESS_PERFECT)
					landed = play.press()
				else:
					play.advance(0.0, 0.05)
			else:
				play.advance(0.05, 0.05)
			guard += 1
		_ok("%s raid %d playout finished" % [tag, i + 1], play.is_done() and step_ok)
		var order := [M10Play.S.B1, M10Play.S.UNSEAL, M10Play.S.DECIDE, M10Play.S.B2]
		var in_order := true
		for s in order:
			in_order = in_order and seen.has(s)
		_ok("%s raid %d beats seen: beam 1, unseal, decision, beam 2, hunter, beam 3" % [tag, i + 1],
			in_order and seen.has(M10Play.S.HUNTER) and seen.has(M10Play.S.B3))
		if mode == "press" and i != 1:
			_ok("%s raid %d press window was entered" % [tag, i + 1], seen.has(M10Play.S.PRESS))
		var spoof := m.spoof_of(play)
		var truth := M10Rules.found_of(m.assets, m.b1, m.cands[m.reveal], m.own3, m.plan, spoof)
		_ok("%s raid %d result = rules sweep with the spoof that landed" % [tag, i + 1], play.final["found"] == truth)
		_ok("%s raid %d finds logged beat by beat = result" % [tag, i + 1], play.logged_found() == truth)
		if spoof.is_empty():
			_ok("%s raid %d no spoof landed: forecast = result" % [tag, i + 1], fc["found"] == truth)
		if mode == "press" and i == 0:
			_ok("%s raid 1 press landed in the window" % tag, landed and not spoof.is_empty())
		if mode == "press" and i == 2:
			_ok("%s raid 3 mistimed press does not land" % tag, spoof.is_empty())
		if mode == "choice" and i == 2:
			_ok("%s raid 3 choice spoof always lands" % tag, not spoof.is_empty())
		var key_before := m.key
		var heat_before := m.heat
		var row := m.settle(play)
		var l: Dictionary = row["ledger"]
		_ok("%s raid %d ledger reconciles (key and Heat)" % [tag, i + 1], M10Rules.ledger_reconciles(l))
		_ok("%s raid %d ledger starts at the key and Heat of contact" % [tag, i + 1], l["key_before"] == key_before and l["heat_before"] == heat_before)
		_ok("%s raid %d model carries the ledger's key and Heat" % [tag, i + 1], m.key == l["key_after"] and m.heat == l["heat_after"])
		_ok("%s raid %d repair follows REPAIR=%s" % [tag, i + 1, repair], l["repair"] == M10Rules.repair(m.assets, truth, repair))
		_ok("%s raid %d decoy and ghost charged as the plan said" % [tag, i + 1],
			l["decoy"] == 3 * m.plan["decoys"].size() and l["heat_ghost"] == 5 * m.plan["ghost"].size())
		_ok("%s raid %d EVADED shows +6 key and -10 Heat, else neither" % [tag, i + 1],
			(l["evaded"] and l["evade_gain"] == 6 and l["heat_evade"] == -10) or (not l["evaded"] and l["evade_gain"] == 0 and l["heat_evade"] == 0))
		_ok("%s raid %d down count = found count" % [tag, i + 1], l["down"] == truth.size())
		if i < M10Config.LEG_SEEDS.size() - 1:
			_ok("%s raid %d next raid loads" % [tag, i + 1], m.next_raid())
	_ok(tag + " leg over after 3 raids", m.leg_over() and m.history.size() == 3)
	_ok(tag + " no further raid", not m.next_raid())


## The scene itself, driven by its own input path and _process in real-time steps: contact, plan, forecast, playout
## (decision by click, press window by SPACE), aftermath, next raid. One flow test per screen.
func _view_flow(mode: String) -> void:
	M10Config.reset()
	M10Config.toggles["SPOOF_MODE"] = mode
	var view: Control = (load("res://tools/raid_lab_m10/raid_lab_m10.tscn") as PackedScene).instantiate()
	root.add_child(view)
	var tag := "[view/%s]" % mode
	_ok(tag + " opens on the contact screen", view.phase == view.Phase.CONTACT)
	view._key(KEY_ENTER)
	_ok(tag + " Enter goes to the plan", view.phase == view.Phase.PLAN)
	view._key(KEY_1)
	view._act("cell:3,0")
	view._key(KEY_2)
	view._act("cell:3,1")
	view._key(KEY_3)
	view._act("cell:0,0")
	_ok(tag + " levers placed by key and click", view.model.plan["ghost"].size() == 1 and view.model.plan["decoys"].size() == 1 and view.model.plan["dark"].size() == 1)
	view._act("cell:1,1")
	_ok(tag + " a second dark is allowed (cap 3)", view.model.plan["dark"].size() == 2)
	view._key(KEY_Z)
	_ok(tag + " Z undoes the last lever", view.model.plan["dark"].size() == 1)
	view._key(KEY_ENTER)
	_ok(tag + " Enter shows the forecast", view.phase == view.Phase.FORECAST)
	view._key(KEY_ENTER)
	_ok(tag + " Enter launches the sweep", view.phase == view.Phase.PLAY and view.play != null)
	var guard := 0
	var clicked := false
	var pressed := false
	while view.phase == view.Phase.PLAY and guard < 4000:
		if view.play.state == M10Play.S.DECIDE and not clicked:
			view._act("cell:0,1")
			_ok(tag + " a click off the lit line is refused", view.play.state == M10Play.S.DECIDE)
			view._act("cell:2,0")
			clicked = true
		elif view.play.state == M10Play.S.PRESS and not pressed:
			view.play.press_t = M10Config.PRESS_PERFECT
			view._key(KEY_SPACE)
			pressed = true
		view._process(0.05)
		guard += 1
	_ok(tag + " the playout ends in the aftermath by itself", view.phase == view.Phase.AFTER and not view.row.is_empty())
	_ok(tag + " aftermath ledger reconciles", M10Rules.ledger_reconciles(view.row["ledger"]))
	_ok(tag + " the spoof landed (choice always, press on time)", not (view.row["spoof"] as Array).is_empty())
	var truth := M10Rules.found_of(view.model.assets, view.model.b1, view.model.cands[0], view.model.own3, view.model.plan, [1, Vector2i(2, 0)])
	_ok(tag + " aftermath = rules sweep with that spoof", view.row["found"] == truth)
	view._key(KEY_ENTER)
	_ok(tag + " Enter goes to raid 2 contact", view.phase == view.Phase.CONTACT and view.model.raid == 1)
	view.queue_free()
