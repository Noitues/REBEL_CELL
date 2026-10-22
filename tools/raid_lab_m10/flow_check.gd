extends SceneTree
## Flow check of the L2 lab (not the golden parity): the lever rules and undo, golden leg 0 played on its planned
## line through the model (forecast with the chosen spoof = result, ledger reconciles, between step = golden), a naive
## line played until it breaches on every golden leg where it does, and the scene driven through its own input path
## (planned raid, repair step, and a breach leg).
##   godot --headless --path . -s res://tools/raid_lab_m10/flow_check.gd

var _fails: int = 0
var _checks: int = 0


func _ok(label: String, cond: bool) -> void:
	_checks += 1
	if not cond:
		_fails += 1
	print("%s %s" % ["PASS" if cond else "FAIL", label])


func _init() -> void:
	_rules_flow()
	_planned_leg0()
	_naive_legs()
	_view_planned()
	_view_breach()
	L2Config.reset()
	print("%d checks" % _checks)
	print("FLOW %s" % ("PASS" if _fails == 0 else "FAIL"))
	quit(0 if _fails == 0 else 1)


func _score_of(step: Dictionary) -> int:
	return int(step["score_after"])


func _rules_flow() -> void:
	L2Config.reset()
	var m := L2Model.new(0)
	_ok("leg 0 opens on raid 1 at Heat 44, bank 10, HOME 3", m.raid == 0 and m.state.heat == 44 and m.state.bank == 10 and m.state.home_hp == 3)
	_ok("the network has 6 assets, all OK, and HOME", m.state.status.size() == 6 and m.state.count("OK") == 6 and m.home() != L2Rules.NONE)
	_ok("heat bands: 49 none, 50 one, 74 one, 75 two", L2Rules.extra_count(49) == 0 and L2Rules.extra_count(50) == 1 and L2Rules.extra_count(74) == 1 and L2Rules.extra_count(75) == 2)
	var cells: Array = m.values().keys()
	var asset: Vector2i = cells[0]
	var empty := L2Rules.NONE
	for c in L2Rules.nodes():
		if not m.values().has(c) and c != m.home():
			empty = c
			break
	_ok("ghost on an empty node refused", m.why_not("ghost", empty) != "")
	_ok("ghost can hide HOME", m.place("ghost", m.home()))
	_ok("a ghost charges Heat at once (44 -> 49)", m.heat_now() == 49 and m.state.heat == 44)
	_ok("second ghost refused (scarce)", m.why_not("ghost", asset) != "")
	_ok("decoy on an asset refused", m.why_not("decoy", asset) != "")
	_ok("decoy on an empty node allowed", m.place("decoy", empty))
	_ok("a decoy charges the bank at once (10 -> 7)", m.bank_now() == 7 and m.state.bank == 10)
	_ok("second decoy refused (scarce)", m.why_not("decoy", Vector2i(-5, 0)) != "")
	_ok("go dark on a live asset", m.place("dark", asset))
	_ok("second dark refused (cap 1)", m.why_not("dark", cells[1]) != "")
	_ok("a lever node takes no second lever", m.why_not("ghost", asset) != "")
	_ok("undo takes the last lever off", m.undo() and (m.plan["dark"] as Array).is_empty())
	_ok("undo twice more clears the plan", m.undo() and m.undo() and not m.can_undo())
	_ok("Heat and bank back to start after undo", m.heat_now() == 44 and m.bank_now() == 10)
	m.place("ghost", asset)
	_ok("click-remove takes a placed lever off", m.remove_at(asset) and (m.plan["ghost"] as Array).is_empty())
	_ok("dark refused on a TAKEN asset", _taken_refused())
	# Strength follows the ghost: a state at Heat 47 crosses the 50 line with the ghost's +5.
	var m2 := L2Model.new(0)
	m2.state.heat = 47
	_ok("at Heat 47 no extra beam", m2.extra_now() == 0)
	m2.place("ghost", asset)
	_ok("the ghost's +5 Heat (47 -> 52) adds a known beam", m2.extra_now() == 1)
	var fc := m2.forecast()
	_ok("forecast has one entry per sealed candidate", fc.size() == 3)
	for i in range(3):
		_ok("forecast %d best spoof is never worse than holding" % i, L2Rules.score(m2.leg, fc[i]["best_state"]) >= L2Rules.score(m2.leg, fc[i]["state"]))


func _taken_refused() -> bool:
	var m := L2Model.new(0)
	var c: Vector2i = m.values().keys()[0]
	m.state.status[c] = "TAKEN"
	return m.why_not("dark", c) != "" and m.why_not("ghost", c) != ""


## Run one raid through the model + play with a plan and a spoof; returns the settled row.
func _run_raid(m: L2Model, alloc: Dictionary, spoof: Vector2i) -> Dictionary:
	for lv in [["ghost", "ghost"], ["decoys", "decoy"], ["dark", "dark"]]:
		for c: Vector2i in alloc[lv[0]]:
			if not m.place(lv[1], c):
				return {}
	var fc := m.forecast()
	var extra := m.extra_now()
	var play := m.make_play()
	var seen: Array = []
	var guard := 0
	while not play.is_done() and guard < 4000:
		if not seen.has(play.state):
			seen.append(play.state)
		if play.state == L2Play.S.DECIDE:
			if spoof == L2Rules.NONE:
				play.pass_spoof()
			else:
				play.choose_spoof(spoof)
		else:
			play.advance(0.05)
		guard += 1
	_ok("raid %d playout finished and passed every beat" % (m.raid + 1), play.is_done() and seen.has(L2Play.S.DECIDE) and seen.has(L2Play.S.TURN) and seen.has(L2Play.S.UNSEAL))
	var row := m.settle(play)
	row["play"] = play
	row["forecast"] = fc
	row["extra_planned"] = extra
	return row


func _planned_leg0() -> void:
	L2Config.reset()
	var m := L2Model.new(0)
	var steps: Array = m.leg["planned"]
	var tag := "[planned leg 0]"
	_ok(tag + " the golden planned line has 3 raids", steps.size() == 3)
	for i in range(steps.size()):
		var s: Dictionary = steps[i]
		var alloc := L2Data.alloc_of(s["alloc"])
		var spoof := L2Data.spoof_of(s["spoof"])
		_ok("%s raid %d starts at the golden state" % [tag, i + 1], m.state.to_array() == L2State.from_golden(s["before"]).to_array())
		var row := _run_raid(m, alloc, spoof)
		_ok("%s raid %d levers accepted" % [tag, i + 1], not row.is_empty())
		var fc: Array = row["forecast"]
		var strength_before: int = row["extra_planned"]
		_ok("%s raid %d heat band at the sweep = extra beams in the trace" % [tag, i + 1],
			strength_before == int(row["ledger"]["extra"]) and (row["beams"] as Array).size() == 3 + strength_before)
		var play: L2Play = row["play"]
		var want_touches := _touched_arr(s["touched"])
		_ok("%s raid %d touches = golden" % [tag, i + 1], _touched_arr_of(row["touches"]) == want_touches)
		_ok("%s raid %d touches logged beat by beat = result" % [tag, i + 1], play.logged_touches() == want_touches)
		_ok("%s raid %d after the raid = golden" % [tag, i + 1], (row["after_raid"] as L2State).to_array() == L2State.from_golden(s["after_raid"]).to_array())
		# Forecast = result with the chosen spoof: the planner's spoof is the forecast's best for the revealed line.
		var f: Dictionary = fc[L2Config.REVEAL]
		if spoof == L2Rules.NONE:
			_ok("%s raid %d forecast (no spoof) = result" % [tag, i + 1], _touched_arr_of(f["touches"]) == want_touches and not f["saves"])
		else:
			_ok("%s raid %d forecast (best spoof) = result with the chosen spoof" % [tag, i + 1], f["best_spoof"] == spoof and _touched_arr_of(f["best_touches"]) == want_touches)
		_ok("%s raid %d forecast of the chosen spoof equals the real sweep" % [tag, i + 1], _touched_arr_of(play.preview(spoof)["touches"]) == _touched_arr_of(row["touches"]))
		_ok("%s raid %d forecast summary = result summary" % [tag, i + 1], (f["best_summary"] if spoof != L2Rules.NONE else f["summary"]) == row["summary"])
		_ok("%s raid %d ledger reconciles" % [tag, i + 1], L2Model.ledger_reconciles(row["ledger"]))
		_ok("%s raid %d ledger starts at the contact numbers" % [tag, i + 1], int(row["ledger"]["bank_before"]) == int(s["before"]["bank"]) and int(row["ledger"]["heat_before"]) == int(s["before"]["heat"]))
		if i < steps.size() - 1:
			_ok("%s raid %d the between step is open" % [tag, i + 1], m.between_open())
			var bank_raid := m.state.bank
			var heat_raid := m.state.heat
			for c: Vector2i in L2Data.cells(s["repairs"]):
				m.toggle_repair(c)
			var pv := m.between_preview()
			_ok("%s raid %d between ledger reconciles" % [tag, i + 1], bank_raid - int(pv["repair_cost"]) + int(pv["income"]) == (pv["state"] as L2State).bank and heat_raid + L2Config.RUN_HEAT == (pv["state"] as L2State).heat)
			_ok("%s raid %d finish_between" % [tag, i + 1], m.finish_between())
			_ok("%s raid %d next contact = golden after" % [tag, i + 1], m.state.to_array() == L2State.from_golden(s["after"]).to_array())
			_ok("%s raid %d the network persists (same asset cells)" % [tag, i + 1], m.state.status.size() == 6)
		else:
			_ok("%s the last raid has no between step" % tag, not m.between_open() and m.leg_over())
	_ok(tag + " leg score = golden", m.final_score() == _score_of(steps.back()))
	_ok(tag + " the planned line does not breach", not m.breached and m.history.size() == 3)
	_ok(tag + " statuses persisted over the leg (some asset not OK or all repaired)", m.state.status.size() == 6)


func _touched_arr(raw: Array) -> Array:
	var out: Array = []
	for t in raw:
		out.append([int(t[0]), int(t[1]), String(t[2])])
	return out


func _touched_arr_of(touches: Array) -> Array:
	var out: Array = []
	for t: Dictionary in touches:
		out.append([t["cell"].x, t["cell"].y, t["kind"]])
	return out


## The naive policy through the model on every golden leg; it breaches on legs 0, 5 and 8.
func _naive_legs() -> void:
	var breached_legs: Array = []
	for seed_id in L2Config.LEGS:
		L2Config.reset()
		var m := L2Model.new(seed_id)
		var steps: Array = m.leg["naive"]
		var guard := 0
		while not m.leg_over() and guard < 5:
			var d := L2Rules.naive_decide(m.leg, m.raid, m.state)
			var row := _run_raid(m, d["alloc"], d["spoof"])
			_ok("[naive %d] raid %d ledger reconciles" % [seed_id, row["raid"] + 1], L2Model.ledger_reconciles(row["ledger"]))
			if m.breached:
				break
			if m.between_open():
				for c: Vector2i in L2Rules.naive_repairs(m.leg, m.state):
					m.toggle_repair(c)
				m.finish_between()
			guard += 1
		_ok("[naive %d] ends as the golden naive line (score %d)" % [seed_id, _score_of(steps.back())], m.final_score() == _score_of(steps.back()))
		if m.breached:
			breached_legs.append(seed_id)
			_ok("[naive %d] BREACHED: score -100, the leg is over, no between step" % seed_id, m.final_score() == -100 and m.leg_over() and not m.between_open() and m.state.home_hp == 0)
	_ok("naive breaches on legs 0, 5 and 8", breached_legs == [0, 5, 8])


# ---------- the scene, through its own input path ----------
func _make_view(seed_id: int) -> Control:
	L2Config.reset()
	var view: Control = (load("res://tools/raid_lab_m10/raid_lab_m10.tscn") as PackedScene).instantiate()
	root.add_child(view)
	view.model.new_leg(seed_id)
	return view


## One raid through the view: levers by key and click, forecast, launch, the spoof by click or hold, to the end of the
## playout. Leaves the view on AFTER or BREACH.
func _view_raid(view: Control, alloc: Dictionary, spoof: Vector2i) -> void:
	view._key(KEY_ENTER)
	_ok("Enter goes to the plan", view.phase == view.Phase.PLAN)
	for pair in [["ghost", KEY_1, "ghost"], ["decoy", KEY_2, "decoys"], ["dark", KEY_3, "dark"]]:
		for c: Vector2i in alloc[pair[2]]:
			view._key(pair[1])
			view._act("cell:%d,%d" % [c.x, c.y])
	_ok("levers placed by key and click", (view.model.plan["ghost"] as Array).size() == (alloc["ghost"] as Array).size() and (view.model.plan["decoys"] as Array).size() == (alloc["decoys"] as Array).size())
	view._key(KEY_ENTER)
	_ok("Enter shows the forecast", view.phase == view.Phase.FORECAST)
	view._key(KEY_ENTER)
	_ok("Enter launches the sweep", view.phase == view.Phase.PLAY and view.play != null)
	var guard := 0
	var clicked := false
	while view.phase == view.Phase.PLAY and guard < 4000:
		if view.play.state == L2Play.S.DECIDE and not clicked:
			for off in L2Rules.nodes():
				if not view.play.b2.has(off):
					view._act("cell:%d,%d" % [off.x, off.y])
					break
			_ok("a click off the lit line is refused", view.play.state == L2Play.S.DECIDE)
			if spoof == L2Rules.NONE:
				view._key(KEY_H)
			else:
				view._act("cell:%d,%d" % [spoof.x, spoof.y])
			clicked = true
		view._process(0.05)
		guard += 1
	_ok("the playout ends by itself", view.phase in [view.Phase.AFTER, view.Phase.BREACH] and not view.row.is_empty())


func _view_planned() -> void:
	var view := _make_view(0)
	var tag := "[view planned]"
	_ok(tag + " opens on the contact screen", view.phase == view.Phase.CONTACT)
	var steps: Array = view.model.leg["planned"]
	var s: Dictionary = steps[0]
	_view_raid(view, L2Data.alloc_of(s["alloc"]), L2Data.spoof_of(s["spoof"]))
	_ok(tag + " aftermath, not a breach", view.phase == view.Phase.AFTER)
	_ok(tag + " aftermath = golden", (view.row["after_raid"] as L2State).to_array() == L2State.from_golden(s["after_raid"]).to_array())
	_ok(tag + " aftermath ledger reconciles", L2Model.ledger_reconciles(view.row["ledger"]))
	view._key(KEY_ENTER)
	_ok(tag + " Enter opens the repair step", view.phase == view.Phase.REPAIR)
	var down: Array = []
	for c: Vector2i in view.model.state.status:
		if view.model.state.status[c] == "DOWN":
			down.append(c)
	_ok(tag + " the golden raid 1 left DOWN assets to repair", not down.is_empty())
	view._act("cell:%d,%d" % [down[0].x, down[0].y])
	_ok(tag + " clicking a DOWN asset picks its repair", view.model.pending_repairs.has(down[0]))
	view._act("cell:%d,%d" % [down[0].x, down[0].y])
	_ok(tag + " clicking again takes it back", view.model.pending_repairs.is_empty())
	for c: Vector2i in L2Data.cells(s["repairs"]):
		view._act("cell:%d,%d" % [c.x, c.y])
	view._key(KEY_ENTER)
	_ok(tag + " Enter goes to raid 2 contact with the golden state", view.phase == view.Phase.CONTACT and view.model.raid == 1 and view.model.state.to_array() == L2State.from_golden(s["after"]).to_array())
	view.queue_free()


func _view_breach() -> void:
	var view := _make_view(0)
	var tag := "[view breach]"
	var guard := 0
	while view.phase != view.Phase.BREACH and guard < 4:
		var d := L2Rules.naive_decide(view.model.leg, view.model.raid, view.model.state)
		_view_raid(view, d["alloc"], d["spoof"])
		if view.phase == view.Phase.AFTER:
			view._key(KEY_ENTER)
			for c: Vector2i in L2Rules.naive_repairs(view.model.leg, view.model.state):
				view._act("cell:%d,%d" % [c.x, c.y])
			view._key(KEY_ENTER)
		guard += 1
	_ok(tag + " the naive line ends in the full-screen BREACH", view.phase == view.Phase.BREACH)
	_ok(tag + " breach on raid 3 with HOME 0", view.model.raid == 2 and view.model.state.home_hp == 0 and view.model.breached)
	view._key(KEY_ENTER)
	_ok(tag + " Enter shows the leg record", view.phase == view.Phase.RECORD)
	_ok(tag + " the record scores -100", view.model.final_score() == -100)
	view._key(KEY_ENTER)
	_ok(tag + " Enter starts the leg again", view.phase == view.Phase.CONTACT and view.model.raid == 0 and view.model.state.home_hp == 3)
	view.queue_free()
