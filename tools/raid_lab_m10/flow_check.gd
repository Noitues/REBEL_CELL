extends SceneTree
## Flow check of the L3 lab (not the golden parity): the leg kit and lever rules with undo, the forecast (it names no
## best spoof, only the nodes a spoof could save and the range), golden leg 0 played on its planned line through the
## model (forecast = result for the chosen spoof, ledger reconciles, the kit is conserved, the between step = golden), the
## naive line on every golden leg ending as the golden (breach on legs 0, 5, 8), the no-words scramble, and the scene
## driven through its own input path (a planned raid with the between screen, and a full naive breach leg to the record).
##   godot --headless --path . -s res://tools/raid_lab_m10/flow_check.gd

var _fails: int = 0
var _checks: int = 0
var _seen_states: Array = []


func _ok(label: String, cond: bool) -> void:
	_checks += 1
	if not cond:
		_fails += 1
	print("%s %s" % ["PASS" if cond else "FAIL", label])


func _init() -> void:
	_rules_flow()
	_between_flow()
	_scramble()
	_planned_leg0()
	_naive_legs()
	_view_planned()
	_view_breach()
	L3Config.reset()
	print("%d checks" % _checks)
	print("FLOW %s" % ("PASS" if _fails == 0 else "FAIL"))
	quit(0 if _fails == 0 else 1)


func _score_of(step: Dictionary) -> int:
	return int(step["score_after"])


func _kit_total(st: L3State) -> int:
	return int(st.kit["ghost"]) + int(st.kit["decoy"]) + int(st.kit["spoof"])


func _rules_flow() -> void:
	L3Config.reset()
	var m := L3Model.new(0)
	_ok("leg 0 opens on raid 1 at Heat 44, bank 10, HOME 3", m.raid == 0 and m.state.heat == 44 and m.state.bank == 10 and m.state.home_hp == 3)
	_ok("the leg kit starts at 2 ghosts, 2 decoys, 2 spoofs", m.state.kit["ghost"] == 2 and m.state.kit["decoy"] == 2 and m.state.kit["spoof"] == 2)
	_ok("the network has 6 assets, all OK, and HOME", m.state.status.size() == 6 and m.state.count("OK") == 6 and m.home() != L3Rules.NONE)
	_ok("heat bands: 49 none, 50 one, 74 one, 75 two", L3Rules.extra_count(49) == 0 and L3Rules.extra_count(50) == 1 and L3Rules.extra_count(74) == 1 and L3Rules.extra_count(75) == 2)
	_ok("tiers: evaded, holds, damaged, breached", L3Rules.tier(3, 3, 0) == "EVADED" and L3Rules.tier(3, 3, 2) == "HOLDS" and L3Rules.tier(3, 2, 2) == "DAMAGED" and L3Rules.tier(1, 0, 2) == "BREACHED")
	var cells: Array = m.values().keys()
	var asset: Vector2i = cells[0]
	var empties: Array = []
	for c in L3Rules.nodes():
		if not m.values().has(c) and c != m.home():
			empties.append(c)
	var empty: Vector2i = empties[0]
	_ok("ghost on an empty node refused", m.why_not("ghost", empty) != "")
	_ok("ghost can hide HOME", m.place("ghost", m.home()))
	_ok("a ghost charges Heat at once (44 -> 49)", m.heat_now() == 49 and m.state.heat == 44)
	_ok("second ghost in one raid refused (1 a raid)", m.why_not("ghost", asset) != "")
	_ok("the kit tray shows 1 ghost left after the plan", int(m.kit_left()["ghost"]) == 1 and int(m.state.kit["ghost"]) == 2)
	_ok("decoy on an asset refused", m.why_not("decoy", asset) != "")
	_ok("two decoys allowed on empty nodes", m.place("decoy", empties[0]) and m.place("decoy", empties[1]))
	_ok("a decoy costs no Schematics (bank stays 10)", m.state.bank == 10 and int(m.kit_left()["decoy"]) == 0)
	_ok("third decoy refused (the kit is empty, 2 a raid)", m.why_not("decoy", empties[2]) != "")
	_ok("go dark on a live asset", m.place("dark", asset))
	_ok("second dark refused (cap 1)", m.why_not("dark", cells[1]) != "")
	_ok("a lever node takes no second lever", m.why_not("decoy", asset) != "")
	_ok("undo takes the last lever off", m.undo() and (m.plan["dark"] as Array).is_empty())
	_ok("undo twice more takes the decoys off", m.undo() and m.undo() and (m.plan["decoys"] as Array).is_empty())
	m.undo()
	_ok("the plan is clear again; Heat back to 44", not m.can_undo() and m.heat_now() == 44)
	m.place("ghost", asset)
	_ok("click-remove takes a placed lever off", m.remove_at(asset) and (m.plan["ghost"] as Array).is_empty())
	# A spent kit refuses the lever, whatever the per-raid cap.
	var m0 := L3Model.new(0)
	m0.state.kit["ghost"] = 0
	m0.state.kit["decoy"] = 1
	_ok("ghost refused with an empty kit", m0.why_not("ghost", asset) != "")
	_ok("one decoy left: first allowed, second refused", m0.place("decoy", empties[0]) and m0.why_not("decoy", empties[1]) != "")
	_ok("dark refused on a TAKEN asset", _taken_refused())
	# Strength follows the ghost: a state at Heat 47 crosses the 50 line with the ghost's +5.
	var m2 := L3Model.new(0)
	m2.state.heat = 47
	_ok("at Heat 47 no extra beam", m2.extra_now() == 0)
	m2.place("ghost", asset)
	_ok("the ghost's +5 Heat (47 -> 52) adds a known beam", m2.extra_now() == 1)
	var fc := m2.forecast()
	_ok("forecast has one entry per sealed candidate", fc.size() == 3)
	for i in range(3):
		var f: Dictionary = fc[i]
		_ok("forecast %d names no best spoof (no such key)" % i, not f.has("best_spoof") and not f.has("best_state"))
		_ok("forecast %d: the floor is never worse than holding" % i, L3Rules.score(m2.leg, f["floor_state"]) >= L3Rules.score(m2.leg, f["state"]))
		var line: Array = m2.raid_data()["cands"][i]
		var inside := true
		for c: Vector2i in f["save_cells"]:
			inside = inside and line.has(c)
		_ok("forecast %d: the nodes a spoof could save lie on the sealed line" % i, inside)
		_ok("forecast %d: 'saves' iff there is a node to save" % i, bool(f["saves"]) == (not (f["save_cells"] as Array).is_empty()))
	var m3 := L3Model.new(0)
	m3.state.kit["spoof"] = 0
	var any_save := false
	for f3: Dictionary in m3.forecast():
		any_save = any_save or not (f3["save_cells"] as Array).is_empty() or bool(f3["can_spoof"])
	_ok("with no spoof in the kit the forecast offers none", not any_save)


func _taken_refused() -> bool:
	var m := L3Model.new(0)
	var c: Vector2i = m.values().keys()[0]
	m.state.status[c] = "TAKEN"
	return m.why_not("dark", c) != "" and m.why_not("ghost", c) != ""


## The between step on a hand-made state: repairs are paid before the shop and income; one buy; intensity.
func _between_flow() -> void:
	L3Config.reset()
	var m := L3Model.new(0)
	var dn: Array = []
	for c: Vector2i in m.values():
		dn.append(c)
		if dn.size() == 2:
			break
	# Make a settled raid with two DOWN assets and a small bank.
	m.state.status[dn[0]] = "DOWN"
	m.state.status[dn[1]] = "DOWN"
	m.state.bank = 7
	m.history.append({"alloc": L3Rules.empty_alloc(), "tier": "HOLDS"})
	m.breached = false
	_ok("[between] the step is open after a settled raid", m.between_open())
	var c0: int = L3Rules.idiv(int(m.values()[dn[0]]), 2)
	_ok("[between] a repair within the bank is accepted", m.toggle_repair(dn[0]) == "")
	var left: int = 7 - c0
	# A buy the bank cannot pay after the repair is refused with a reason.
	var refused: String = m.set_buy("ghost") if left < 6 else "skip"
	_ok("[between] a buy the bank cannot cover after repairs is refused", left >= 6 or refused != "")
	m.set_intensity("HOT")
	var pv := m.between_preview()
	var ns: L3State = pv["state"]
	_ok("[between] HOT adds 18 Heat", ns.heat == 44 + 18 and int(pv["heat_add"]) == 18)
	_ok("[between] bank ledger: before - repairs - buy + income = after", 7 - int(pv["repair_cost"]) - int(pv["buy_cost"]) + int(pv["income"]) == ns.bank)
	m.set_intensity("LOW")
	var lo := m.between_preview()
	m.set_intensity("NORMAL")
	var no := m.between_preview()
	m.set_intensity("HOT")
	var hi := m.between_preview()
	_ok("[between] LOW income = NORMAL x 0.5, rounded down", int(lo["income"]) == L3Rules.idiv(int(no["income"]), 2))
	_ok("[between] HOT income = NORMAL x 1.5, rounded down", int(hi["income"]) == L3Rules.idiv(int(no["income"]) * 3, 2))
	_ok("[between] undoing the repair frees the bank", m.toggle_repair(dn[0]) == "" and m.pending_repairs.is_empty() and m.budget() == 7)
	m.state.bank = 12
	_ok("[between] spoof (5) bought with the bank", m.set_buy("spoof") == "" and m.pending_buy == "spoof" and m.budget() == 7)
	_ok("[between] only one buy: picking another replaces it", m.set_buy("ghost") == "" and m.pending_buy == "ghost")
	_ok("[between] the same pick again takes it back", m.set_buy("ghost") == "" and m.pending_buy == "")
	var kit0 := _kit_total(m.state)
	m.set_buy("decoy")
	m.finish_between()
	_ok("[between] finish: kit +1 item, bank paid, next raid", _kit_total(m.state) == kit0 + 1 and m.raid == 1 and m.pending_buy == "" and m.pending_intensity == "NORMAL")


func _scramble() -> void:
	var G = load("res://tools/raid_lab_m10/l3_glyphs.gd")
	G.scramble = true
	var a: String = G.scr("Heat 44 Heat")
	var parts: PackedStringArray = a.split(" ")
	_ok("[scramble] same length, digits stay", a.length() == "Heat 44 Heat".length() and parts[1] == "44")
	_ok("[scramble] the same word gives the same noise", parts[0] == parts[2])
	_ok("[scramble] case pattern stays", (parts[0] as String)[0] == (parts[0] as String)[0].to_upper() and (parts[0] as String).substr(1) == (parts[0] as String).substr(1).to_lower())
	var word: String = G.scr("aaaaaaaaaaaaaaaa")
	var distinct := {}
	for i in range(word.length()):
		distinct[word[i]] = true
	_ok("[scramble] not a letter substitution (one letter in, many out)", distinct.size() > 3)
	_ok("[scramble] different words get different noise", G.scr("ghost") != G.scr("decoy") and G.scr("Alpha") != G.scr("Alpha beta"))
	G.scramble = false
	_ok("[scramble] off by default text passes through", G.scr("Heat") == "Heat")


## Run one raid through the model + play with a plan and a spoof; returns the settled row.
func _run_raid(m: L3Model, alloc: Dictionary, spoof: Vector2i) -> Dictionary:
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
		if play.state == L3Play.S.DECIDE:
			if spoof == L3Rules.NONE:
				play.pass_spoof()
			else:
				play.choose_spoof(spoof)
		else:
			play.advance(0.05)
		guard += 1
	_ok("raid %d playout finished" % (m.raid + 1), play.is_done() and seen.has(L3Play.S.TURN) or play.cut)
	var row := m.settle(play)
	row["play"] = play
	row["forecast"] = fc
	row["extra_planned"] = extra
	row["seen"] = seen
	return row


func _planned_leg0() -> void:
	L3Config.reset()
	var m := L3Model.new(0)
	var steps: Array = m.leg["planned"]
	var tag := "[planned leg 0]"
	var kit_bought := 0
	_ok(tag + " the golden planned line has 3 raids", steps.size() == 3)
	for i in range(steps.size()):
		var s: Dictionary = steps[i]
		var alloc := L3Data.alloc_of(s["alloc"])
		var spoof := L3Data.spoof_of(s["spoof"])
		_ok("%s raid %d starts at the golden state" % [tag, i + 1], m.state.to_array() == L3State.from_golden(s["before"]).to_array())
		var row := _run_raid(m, alloc, spoof)
		_ok("%s raid %d levers accepted (kit and caps)" % [tag, i + 1], not row.is_empty())
		var fc: Array = row["forecast"]
		_ok("%s raid %d heat band at the sweep = extra beams in the trace" % [tag, i + 1],
			int(row["extra_planned"]) == int(row["ledger"]["extra"]) and (row["beams"] as Array).size() == 3 + int(row["extra_planned"]))
		var play: L3Play = row["play"]
		var want_touches := _touched_arr(s["touched"])
		_ok("%s raid %d touches = golden" % [tag, i + 1], _touched_arr_of(row["touches"]) == want_touches)
		_ok("%s raid %d touches logged beat by beat = result" % [tag, i + 1], play.logged_touches() == want_touches)
		_ok("%s raid %d tier = golden (%s)" % [tag, i + 1, s["tier"]], row["tier"] == s["tier"])
		_ok("%s raid %d after the raid = golden" % [tag, i + 1], (row["after_raid"] as L3State).to_array() == L3State.from_golden(s["after_raid"]).to_array())
		# Forecast = result for the chosen spoof (the forecast of the revealed line with the spoof the player picked).
		var f: Dictionary = fc[L3Config.REVEAL]
		if spoof == L3Rules.NONE:
			_ok("%s raid %d forecast (hold) = result" % [tag, i + 1], _touched_arr_of(f["touches"]) == want_touches and f["summary"] == row["summary"])
		else:
			var pv := L3Rules.resolve(m.leg, i, row["before"], play.b2, alloc, spoof)
			_ok("%s raid %d forecast with the chosen spoof = the real sweep" % [tag, i + 1], _touched_arr_of(pv["touches"]) == want_touches and L3Rules.summary(row["before"], pv["touches"]) == row["summary"])
			_ok("%s raid %d the forecast lists the chosen spoof's node among the nodes a spoof could save" % [tag, i + 1], (f["save_cells"] as Array).has(spoof))
		_ok("%s raid %d the spoof leaves the kit only if used" % [tag, i + 1], int(row["ledger"]["kit_used"]["spoof"]) == (0 if spoof == L3Rules.NONE else 1))
		_ok("%s raid %d ledger reconciles (heat, home, kit, bank)" % [tag, i + 1], L3Model.ledger_reconciles(row["ledger"], (row["after_raid"] as L3State).bank))
		_ok("%s raid %d ledger starts at the contact numbers" % [tag, i + 1], int(row["ledger"]["heat_before"]) == int(s["before"]["heat"]))
		if i < steps.size() - 1:
			_ok("%s raid %d the between step is open" % [tag, i + 1], m.between_open())
			var b: Dictionary = s["between"]
			var bank_raid := m.state.bank
			var heat_raid := m.state.heat
			for c: Vector2i in L3Data.cells(b["repairs"]):
				m.toggle_repair(c)
			if b["buy"] != null:
				m.set_buy(String(b["buy"]))
			m.set_intensity(String(b["intensity"]))
			var pv2 := m.between_preview()
			var ns: L3State = pv2["state"]
			_ok("%s raid %d between ledger reconciles (bank and Heat)" % [tag, i + 1],
				bank_raid - int(pv2["repair_cost"]) - int(pv2["buy_cost"]) + int(pv2["income"]) == ns.bank and heat_raid + int(L3Config.INTENSITY_HEAT[b["intensity"]]) == ns.heat)
			if String(pv2["bought"]) != "":
				kit_bought += 1
			_ok("%s raid %d finish_between" % [tag, i + 1], m.finish_between())
			_ok("%s raid %d next contact = golden after" % [tag, i + 1], m.state.to_array() == L3State.from_golden(s["after"]).to_array())
		else:
			_ok("%s the last raid has no between step" % tag, not m.between_open() and m.leg_over())
	_ok(tag + " leg score = golden (Heat carried charged)", m.final_score() == _score_of(steps.back()))
	_ok(tag + " the planned line does not breach", not m.breached and m.history.size() == 3)
	var used := 0
	for h: Dictionary in m.history:
		for k in L3Config.KITS:
			used += int(h["ledger"]["kit_used"][k])
	_ok(tag + " the kit is conserved: start + bought - used = left", 6 + kit_bought - used == _kit_total(m.state))


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


## The naive policy through the model on every golden leg; it breaches on legs 0, 5 and 8 and ends as the golden.
func _naive_legs() -> void:
	var breached_legs: Array = []
	for seed_id in L3Config.LEGS:
		L3Config.reset()
		var m := L3Model.new(seed_id)
		var steps: Array = m.leg["naive"]
		var guard := 0
		var used := 0
		var bought := 0
		while not m.leg_over() and guard < 5:
			var d := L3Rules.naive_decide(m.leg, m.raid, m.state)
			var row := _run_raid(m, d["alloc"], d["spoof"])
			_ok("[naive %d] raid %d ledger reconciles" % [seed_id, row["raid"] + 1], L3Model.ledger_reconciles(row["ledger"], (row["after_raid"] as L3State).bank))
			for k in L3Config.KITS:
				used += int(row["ledger"]["kit_used"][k])
			if row["cut"]:
				var cp: L3Play = row["play"]
				if cp.last_beam() < cp.order.find("b2"):
					_ok("[naive %d] HOME fell before beam 2: no spoof decision, the spoof stays in the kit" % seed_id, not (row["seen"] as Array).has(L3Play.S.DECIDE) and not cp.spoof_used)
			if m.breached:
				break
			if m.between_open():
				for c: Vector2i in L3Rules.naive_repairs(m.leg, m.state):
					m.toggle_repair(c)
				m.finish_between()
			guard += 1
		var last: Dictionary = steps.back()
		_ok("[naive %d] ends as the golden naive line (score %d)" % [seed_id, _score_of(last)], m.final_score() == _score_of(last))
		_ok("[naive %d] the kit is conserved (6 - used = left)" % seed_id, 6 + bought - used == _kit_total(m.state))
		_ok("[naive %d] tier of the last raid = golden (%s)" % [seed_id, last["tier"]], (m.history.back() as Dictionary)["tier"] == last["tier"])
		if m.breached:
			breached_legs.append(seed_id)
			_ok("[naive %d] BREACHED: score -100, the leg is over, no between step" % seed_id, m.final_score() == -100 and m.leg_over() and not m.between_open() and m.state.home_hp == 0)
	_ok("naive breaches on legs 0, 5 and 8", breached_legs == [0, 5, 8])


# ---------- the scene, through its own input path ----------
func _make_view(seed_id: int) -> Control:
	L3Config.reset()
	var view: Control = (load("res://tools/raid_lab_m10/raid_lab_m10.tscn") as PackedScene).instantiate()
	root.add_child(view)
	if view.get("model") == null:
		_ok("the lab scene loads with its script", false)
		view.queue_free()
		return null
	view.model.new_leg(seed_id)
	return view


## One raid through the view: levers by key and click, forecast, launch, the spoof by click or hold, to the end of the
## playout. Leaves the view on AFTER or BREACH.
func _view_raid(view: Control, alloc: Dictionary, spoof: Vector2i) -> void:
	_seen_states = []
	view._key(KEY_ENTER)
	_ok("Enter goes to the plan", view.phase == view.Phase.PLAN)
	for pair in [["ghost", KEY_1, "ghost"], ["decoy", KEY_2, "decoys"], ["dark", KEY_3, "dark"]]:
		for c: Vector2i in alloc[pair[2]]:
			if view.sel_lever != pair[0]:
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
		if not _seen_states.has(view.play.state):
			_seen_states.append(view.play.state)
		if view.play.state == L3Play.S.DECIDE and not clicked:
			for off in L3Rules.nodes():
				if not view.play.b2.has(off):
					view._act("cell:%d,%d" % [off.x, off.y])
					break
			_ok("a click off the lit line is refused", view.play.state == L3Play.S.DECIDE)
			if spoof == L3Rules.NONE:
				view._key(KEY_H)
			else:
				view._act("cell:%d,%d" % [spoof.x, spoof.y])
			clicked = true
		view._process(0.05)
		guard += 1
	_ok("the playout ends by itself", view.phase in [view.Phase.AFTER, view.Phase.BREACH] and not view.row.is_empty())


func _view_planned() -> void:
	var view := _make_view(0)
	if view == null:
		return
	var tag := "[view planned]"
	_ok(tag + " opens on the contact screen", view.phase == view.Phase.CONTACT)
	var steps: Array = view.model.leg["planned"]
	var s: Dictionary = steps[0]
	_view_raid(view, L3Data.alloc_of(s["alloc"]), L3Data.spoof_of(s["spoof"]))
	_ok(tag + " aftermath, not a breach", view.phase == view.Phase.AFTER)
	_ok(tag + " aftermath = golden", (view.row["after_raid"] as L3State).to_array() == L3State.from_golden(s["after_raid"]).to_array())
	_ok(tag + " the tier is shown as the golden's (" + String(s["tier"]) + ")", view.row["tier"] == s["tier"])
	_ok(tag + " aftermath ledger reconciles", L3Model.ledger_reconciles(view.row["ledger"], (view.row["after_raid"] as L3State).bank))
	view._key(KEY_ENTER)
	_ok(tag + " Enter opens the between screen", view.phase == view.Phase.REPAIR)
	var down: Array = []
	for c: Vector2i in view.model.state.status:
		if view.model.state.status[c] == "DOWN":
			down.append(c)
	_ok(tag + " the golden raid 1 left DOWN assets to repair", not down.is_empty())
	view._act("cell:%d,%d" % [down[0].x, down[0].y])
	_ok(tag + " clicking a DOWN asset picks its repair", view.model.pending_repairs.has(down[0]))
	view._act("cell:%d,%d" % [down[0].x, down[0].y])
	_ok(tag + " clicking again takes it back", view.model.pending_repairs.is_empty())
	view._key(KEY_H)
	_ok(tag + " key H picks HOT", view.model.pending_intensity == "HOT")
	view._key(KEY_L)
	_ok(tag + " key L picks LOW", view.model.pending_intensity == "LOW")
	view._act("buy:ghost")
	view._act("buy:none")
	_ok(tag + " the buy can be taken back", view.model.pending_buy == "")
	var b: Dictionary = s["between"]
	for c: Vector2i in L3Data.cells(b["repairs"]):
		view._act("cell:%d,%d" % [c.x, c.y])
	if b["buy"] != null:
		view._act("buy:" + String(b["buy"]))
	view._act("inten:" + String(b["intensity"]))
	view._key(KEY_ENTER)
	_ok(tag + " Enter goes to raid 2 contact with the golden state", view.phase == view.Phase.CONTACT and view.model.raid == 1 and view.model.state.to_array() == L3State.from_golden(s["after"]).to_array())
	view.queue_free()


func _view_breach() -> void:
	var view := _make_view(0)
	if view == null:
		return
	var tag := "[view breach]"
	var guard := 0
	while view.phase != view.Phase.BREACH and guard < 4:
		var d := L3Rules.naive_decide(view.model.leg, view.model.raid, view.model.state)
		_view_raid(view, d["alloc"], d["spoof"])
		if view.phase == view.Phase.AFTER:
			_ok(tag + " a raid that hit HOME is DAMAGED, not CELL HOLDS", view.row["tier"] == "DAMAGED" or int(view.row["summary"]["home"]) == 0)
			view._key(KEY_ENTER)
			for c: Vector2i in L3Rules.naive_repairs(view.model.leg, view.model.state):
				view._act("cell:%d,%d" % [c.x, c.y])
			view._key(KEY_ENTER)
		guard += 1
	_ok(tag + " the naive line ends in the full-screen BREACH", view.phase == view.Phase.BREACH)
	_ok(tag + " breach on raid 3 with HOME 0", view.model.raid == 2 and view.model.state.home_hp == 0 and view.model.breached)
	_ok(tag + " the breach raid's tier is BREACHED", view.row["tier"] == "BREACHED" and view.row["cut"])
	var b2_i: int = view.play.order.find("b2")
	if view.play.last_beam() < b2_i:
		_ok(tag + " HOME fell before beam 2: no spoof decision was offered", not _seen_states.has(L3Play.S.DECIDE))
	else:
		_ok(tag + " HOME fell on or after beam 2 (the decision came first)", true)
	_ok(tag + " the sweep stopped at the touch that emptied HOME", (view.row["touches"] as Array).size() <= (view.play.res["touches"] as Array).size())
	view._key(KEY_ENTER)
	_ok(tag + " Enter shows the leg record", view.phase == view.Phase.RECORD)
	_ok(tag + " the record scores -100", view.model.final_score() == -100)
	view._key(KEY_ENTER)
	_ok(tag + " Enter starts the leg again", view.phase == view.Phase.CONTACT and view.model.raid == 0 and view.model.state.home_hp == 3)
	view.queue_free()
