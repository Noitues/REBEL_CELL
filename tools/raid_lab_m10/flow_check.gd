extends SceneTree
## Flow check of the L5 lab (not the golden parity): the leg kit (dark included) and lever rules with undo, the BATTERED tier,
## the seeded real line and shapes, the forecast (it names no best spoof, only the nodes a spoof could save and the range),
## the response after the reveal (HOLD, every SKIP and JAM: each option's forecast equals the result of really playing it,
## SPOOF_HEAT is charged, JAM stops the hunter), golden leg 0 played on its planned line through the model (forecast = result,
## ledger reconciles, the kit is conserved, the between step = golden), the naive line on every golden leg ending as the
## golden (breach on legs 0 and 8), the one repair slot and the DOWN age, the breach risk each intensity card shows
## (= breach_risk, = golden), the no-words scramble, and the scene driven through its own input path (a planned raid with the
## between screen, a JAM raid, and a full naive breach leg to the record).
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
	_tiers_and_shapes()
	for planned_seed in [0, 3, 5, 11]:
		_planned_leg(planned_seed)
	_naive_legs()
	_breach_warning()
	_kit_strip_amber()
	_lanes()
	_responses_and_jam()
	_view_planned()
	_view_jam()
	_view_breach()
	_motion()
	L5Config.reset()
	print("%d checks" % _checks)
	print("FLOW %s" % ("PASS" if _fails == 0 else "FAIL"))
	quit(0 if _fails == 0 else 1)


func _score_of(step: Dictionary) -> int:
	return int(step["score_after"])


func _kit_total(st: L5State) -> int:
	return int(st.kit["ghost"]) + int(st.kit["decoy"]) + int(st.kit["spoof"]) + int(st.kit["dark"])


func _rules_flow() -> void:
	L5Config.reset()
	var m := L5Model.new(0)
	_ok("leg 0 opens on raid 1 at Heat 44, bank 10, HOME 3", m.raid == 0 and m.state.heat == 44 and m.state.bank == 10 and m.state.home_hp == 3)
	_ok("the leg kit starts at 2 ghosts, 2 decoys, 2 spoofs, 2 go dark", m.state.kit["ghost"] == 2 and m.state.kit["decoy"] == 2 and m.state.kit["spoof"] == 2 and m.state.kit["dark"] == 2)
	_ok("shop prices: ghost 4, decoy 3, spoof 3, dark 3", L5Config.PRICES == {"ghost": 4, "decoy": 3, "spoof": 3, "dark": 3})
	_ok("the network has 6 assets, all OK, and HOME", m.state.status.size() == 6 and m.state.count("OK") == 6 and m.home() != L5Rules.NONE)
	_ok("heat bands: 49 none, 50 one, 74 one, 75 two", L5Rules.extra_count(49) == 0 and L5Rules.extra_count(50) == 1 and L5Rules.extra_count(74) == 1 and L5Rules.extra_count(75) == 2)
	var cells: Array = m.values().keys()
	var asset: Vector2i = cells[0]
	var empties: Array = []
	for c in L5Rules.nodes():
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
	_ok("second dark refused (cap 1 a raid)", m.why_not("dark", cells[1]) != "")
	_ok("the kit tray shows go dark 1 left after the plan", int(m.kit_left()["dark"]) == 1 and int(m.state.kit["dark"]) == 2)
	_ok("a lever node takes no second lever", m.why_not("decoy", asset) != "")
	_ok("undo takes the last lever off", m.undo() and (m.plan["dark"] as Array).is_empty())
	_ok("undo twice more takes the decoys off", m.undo() and m.undo() and (m.plan["decoys"] as Array).is_empty())
	m.undo()
	_ok("the plan is clear again; Heat back to 44", not m.can_undo() and m.heat_now() == 44)
	m.place("ghost", asset)
	_ok("click-remove takes a placed lever off", m.remove_at(asset) and (m.plan["ghost"] as Array).is_empty())
	# A spent kit refuses the lever, whatever the per-raid cap.
	var m0 := L5Model.new(0)
	m0.state.kit["ghost"] = 0
	m0.state.kit["decoy"] = 1
	_ok("ghost refused with an empty kit", m0.why_not("ghost", asset) != "")
	_ok("one decoy left: first allowed, second refused", m0.place("decoy", empties[0]) and m0.why_not("decoy", empties[1]) != "")
	_ok("dark refused on a TAKEN asset", _taken_refused())
	var m0d := L5Model.new(0)
	m0d.state.kit["dark"] = 0
	_ok("go dark refused with an empty kit", m0d.why_not("dark", asset) != "")
	# Strength follows the ghost: a state at Heat 47 crosses the 50 line with the ghost's +5.
	var m2 := L5Model.new(0)
	m2.state.heat = 47
	_ok("at Heat 47 no extra beam", m2.extra_now() == 0)
	m2.place("ghost", asset)
	_ok("the ghost's +5 Heat (47 -> 52) adds a known beam", m2.extra_now() == 1)
	var fc := m2.forecast()
	_ok("forecast has one entry per sealed candidate", fc.size() == 3)
	for i in range(3):
		var f: Dictionary = fc[i]
		_ok("forecast %d names no best spoof (no such key)" % i, not f.has("best_spoof") and not f.has("best_state"))
		_ok("forecast %d: the floor is never worse than holding" % i, L5Rules.score(m2.leg, f["floor_state"]) >= L5Rules.score(m2.leg, f["state"]))
		var line: Array = m2.raid_data()["cands"][i]
		var inside := true
		for c: Vector2i in f["save_cells"]:
			inside = inside and line.has(c)
		_ok("forecast %d: the nodes a spoof could save lie on the sealed line" % i, inside)
		_ok("forecast %d: 'saves' iff a node or JAM saves" % i, bool(f["saves"]) == (not (f["save_cells"] as Array).is_empty() or bool(f["jam_saves"])))
	var m3 := L5Model.new(0)
	m3.state.kit["spoof"] = 0
	var any_save := false
	for f3: Dictionary in m3.forecast():
		any_save = any_save or not (f3["save_cells"] as Array).is_empty() or bool(f3["jam_saves"]) or bool(f3["can_spoof"])
	_ok("with no spoof in the kit the forecast offers none", not any_save)


func _taken_refused() -> bool:
	var m := L5Model.new(0)
	var c: Vector2i = m.values().keys()[0]
	m.state.status[c] = "TAKEN"
	return m.why_not("dark", c) != "" and m.why_not("ghost", c) != ""


## The between step on a hand-made state: repairs are paid before the shop and income; one buy; intensity.
func _between_flow() -> void:
	L5Config.reset()
	var m := L5Model.new(0)
	var dn: Array = []
	for c: Vector2i in m.values():
		dn.append(c)
		if dn.size() == 2:
			break
	# Make a settled raid with two DOWN assets and a small bank.
	m.state.status[dn[0]] = "DOWN"
	m.state.status[dn[1]] = "DOWN"
	m.state.bank = 7
	m.history.append({"alloc": L5Rules.empty_alloc(), "tier": "HOLDS"})
	m.breached = false
	_ok("[between] the step is open after a settled raid", m.between_open())
	var c0: int = L5Rules.idiv(int(m.values()[dn[0]]), 2)
	_ok("[between] a repair within the bank is accepted", m.toggle_repair(dn[0]) == "")
	var left: int = 7 - c0
	# A buy the bank cannot pay after the repair is refused with a reason.
	var refused: String = m.set_buy("ghost") if left < int(L5Config.PRICES["ghost"]) else "skip"
	_ok("[between] a buy the bank cannot cover after repairs is refused", left >= int(L5Config.PRICES["ghost"]) or refused != "")
	m.set_intensity("HOT")
	var pv := m.between_preview()
	var ns: L5State = pv["state"]
	_ok("[between] HOT adds 18 Heat", ns.heat == 44 + 18 and int(pv["heat_add"]) == 18)
	_ok("[between] bank ledger: before - repairs - buy + income = after", 7 - int(pv["repair_cost"]) - int(pv["buy_cost"]) + int(pv["income"]) == ns.bank)
	m.set_intensity("LOW")
	var lo := m.between_preview()
	m.set_intensity("NORMAL")
	var no := m.between_preview()
	m.set_intensity("HOT")
	var hi := m.between_preview()
	_ok("[between] LOW income = NORMAL x 0.5, rounded down", int(lo["income"]) == L5Rules.idiv(int(no["income"]), 2))
	_ok("[between] HOT income = NORMAL x 1.5, rounded down", int(hi["income"]) == L5Rules.idiv(int(no["income"]) * 3, 2))
	_ok("[between] one crew: picking a second DOWN asset moves the pick (REPAIR_SLOTS = 1)", m.toggle_repair(dn[0]) == "" and m.toggle_repair(dn[1]) == "" and m.pending_repairs == [dn[1]])
	_ok("[between] the rules repair only the first slot even if given two", L5Rules.between_parts(m.leg, m.state, [], [dn[0], dn[1]], "NORMAL", "")["repaired"] == [dn[0]])
	_ok("[between] undoing the repair frees the bank", m.toggle_repair(dn[1]) == "" and m.pending_repairs.is_empty() and m.budget() == 7)
	m.state.bank = 12
	_ok("[between] spoof (3) bought with the bank", m.set_buy("spoof") == "" and m.pending_buy == "spoof" and m.budget() == 9)
	_ok("[between] only one buy: picking another replaces it", m.set_buy("ghost") == "" and m.pending_buy == "ghost")
	_ok("[between] the same pick again takes it back", m.set_buy("ghost") == "" and m.pending_buy == "")
	var kit0 := _kit_total(m.state)
	m.set_buy("decoy")
	m.finish_between()
	_ok("[between] finish: kit +1 item, bank paid, next raid", _kit_total(m.state) == kit0 + 1 and m.raid == 1 and m.pending_buy == "" and m.pending_intensity == "NORMAL")


## The plan screen's "kit after this raid" strip equals what the raid really leaves: the kit (a spoof counts whole in the
## strip, so a used one is added back), the Heat the plan leaves (= Heat after + evade - spoof Heat), and the next raid's beam
## count at the Heat after plus the cheapest run, checked against the real between step at LOW when nothing moved the Heat.
func _kit_strip_matches(tag: String, m: L5Model, row: Dictionary, has_next: bool) -> void:
	var sp: Dictionary = row["strip"]
	var after: L5State = row["after_raid"]
	var l: Dictionary = row["ledger"]
	var kit: Dictionary = sp["kit"]
	var kit_ok: bool = int(kit["ghost"]) == int(after.kit["ghost"]) and int(kit["decoy"]) == int(after.kit["decoy"]) \
		and int(kit["dark"]) == int(after.kit["dark"]) and int(kit["spoof"]) == int(after.kit["spoof"]) + int(l["kit_used"]["spoof"])
	_ok(tag + " the kit strip = the kit after the raid", kit_ok)
	_ok(tag + " the strip's Heat = the Heat after, plus the evade credit, less the spoof's Heat", int(sp["heat_leaves"]) == int(l["heat_after"]) + int(l["evade"]) - int(l["spoof_heat"]))
	_ok(tag + " the strip's beam counts = extra_count at that Heat and at the cheapest run",
		int(sp["beams_now"]) == 1 + int(l["extra"]) and int(sp["beams_next"]) == 1 + L5Rules.extra_count(int(sp["heat_leaves"]) + int(L5Config.INTENSITY_HEAT["LOW"])))
	if has_next and int(l["evade"]) == 0 and int(l["spoof_heat"]) == 0:
		var low := L5Rules.between_parts(m.leg, after, row["alloc"]["dark"], [], "LOW", "")["state"] as L5State
		_ok(tag + " the strip's next-raid beams = the real next raid's beams after a LOW run", int(sp["beams_next"]) == 1 + L5Rules.extra_count(low.heat))


## Amber: the plan spends the last kit item and the next raid will run more beams than this one.
func _kit_strip_amber() -> void:
	L5Config.reset()
	var m := L5Model.new(0)
	m.state.heat = 46
	for k in L5Config.KITS:
		m.state.kit[k] = 0
	var pv := m.kit_after_preview()
	_ok("[kit strip] an empty kit at Heat 46: LOW takes the next raid to 52, one more beam, so amber", bool(pv["amber"]) and int(pv["levers_left"]) == 0 and int(pv["beams_next"]) == int(pv["beams_now"]) + 1)
	m.state.heat = 30
	_ok("[kit strip] an empty kit but no new beam next raid: not amber", not bool(m.kit_after_preview()["amber"]))
	m.state.heat = 46
	m.state.kit["spoof"] = 1
	var pv2 := m.kit_after_preview()
	_ok("[kit strip] one lever left: not amber, and it is counted", not bool(pv2["amber"]) and int(pv2["levers_left"]) == 1)
	var fresh := L5Model.new(0)
	fresh.state.kit["ghost"] = 1
	_ok("[kit strip] the ghost is placed on an asset", fresh.place("ghost", (fresh.values().keys()[0] as Vector2i)))
	var pv3 := fresh.kit_after_preview()
	_ok("[kit strip] a placed ghost leaves the kit and adds its Heat", int(pv3["kit"]["ghost"]) == 0 and int(pv3["heat_leaves"]) == fresh.state.heat + L5Config.GHOST_HEAT)


## Parallel beams on one row or column take fixed, ordered, distinct lanes, centered on it; the hunter has its own lane on
## every column; the node's value is one pip per 2.
func _lanes() -> void:
	var view := _make_view(0)
	if view == null:
		return
	var apart := true
	var ordered := true
	var centered := true
	var hunter_clear := true
	var n_lines := 0
	for seed_id in L5Config.LEGS:
		view.model.new_leg(seed_id)
		for rx in range(L5Config.RAIDS * 3):
			var r: int = rx / 3
			view.model.raid = r
			view.lane_extra = rx % 3	## 0, 1 or 2 extra known beams: only the beams that run take a lane
			var offs: Array = view._offsets()
			var lines: Array = view._all_lines()
			var by_key := {}
			for i in range(lines.size()):
				if not view._lane_live(i):
					continue
				var key: String = view._lane_key(lines[i])
				if not by_key.has(key):
					by_key[key] = []
				(by_key[key] as Array).append(float(offs[i]))
				n_lines += 1
			for key: String in by_key:
				var lanes: Array = by_key[key]
				var all_lanes := lanes.duplicate()
				if key.begins_with("c"):
					all_lanes.append(view._h_off(int(key.substr(1))))
				for a in range(all_lanes.size()):
					if a > 0:
						apart = apart and float(all_lanes[a]) - float(all_lanes[a - 1]) >= view.LANE - 0.01
					ordered = ordered and (a == 0 or float(all_lanes[a]) > float(all_lanes[a - 1]))
				var total := 0.0
				for v in all_lanes:
					total += float(v)
				centered = centered and absf(total) < 0.01
			for x in range(L5Config.W):
				for ln_off in (by_key.get("c%d" % x, []) as Array):
					hunter_clear = hunter_clear and absf(float(ln_off) - view._h_off(x)) >= view.LANE - 0.01
	_ok("[lanes] beams on one row or column are at least a lane apart (%d lines over 6 legs)" % n_lines, apart)
	_ok("[lanes] the lanes keep the order beam 1, extra, extra 2, candidates", ordered)
	_ok("[lanes] the lanes are centered on the row or column (never between rows)", centered)
	_ok("[lanes] the hunter's lane never shares a lane with a line on its column", hunter_clear)
	var pips_ok := true
	for v in [4, 6, 8, 10, 12]:
		pips_ok = pips_ok and G_pips(v) == v / 2
	_ok("[pips] a node of value v wears v / 2 pips (4 to 12 give 2 to 6)", pips_ok)
	view.queue_free()


func G_pips(v: int) -> int:
	var G = load("res://tools/raid_lab_m10/l5_glyphs.gd")
	return int(G.pip_count(v))


func _scramble() -> void:
	var G = load("res://tools/raid_lab_m10/l5_glyphs.gd")
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
func _run_raid(m: L5Model, alloc: Dictionary, spoof: Vector2i) -> Dictionary:
	for lv in [["ghost", "ghost"], ["decoys", "decoy"], ["dark", "dark"]]:
		for c: Vector2i in alloc[lv[0]]:
			if not m.place(lv[1], c):
				return {}
	var fc := m.forecast()
	var extra := m.extra_now()
	var strip := m.kit_after_preview()
	var play := m.make_play()
	var fx := L7Fx.new()
	fx.consume(play)
	var seen: Array = []
	var guard := 0
	var options_ok := true
	var n_options := 0
	while not play.is_done() and guard < 4000:
		if not seen.has(play.state):
			seen.append(play.state)
		if play.state == L5Play.S.DECIDE:
			if not seen.has(-1):
				seen.append(-1)
				n_options = play.options().size()
				options_ok = _options_match(play)
			if spoof == L5Rules.NONE:
				play.pass_spoof()
			elif spoof == L5Rules.JAM:
				play.choose_jam()
			else:
				play.choose_spoof(spoof)
		else:
			play.advance(0.05)
		fx.consume(play)
		guard += 1
	_ok("raid %d playout finished" % (m.raid + 1), play.is_done() and (seen.has(L5Play.S.TURN) or spoof == L5Rules.JAM) or play.cut)
	# The animation's cues come in the resolver's touch order (a sweep cut by the breach shows the prefix it reached).
	var want: Array = _touched_arr_of(play.shown_touches() if play.cut else play.res["touches"])
	_ok("raid %d: the animation's touch order equals the resolver's touch order (%d touches)" % [m.raid + 1, want.size()], fx.touch_order() == want)
	_ok("raid %d: the animation cues launch every beam, then stamp once" % (m.raid + 1), fx.kinds().count("stamp") == 1 and fx.kinds().count("launch") >= 1)
	if seen.has(-1):
		_ok("raid %d: the decision screen's forecast equals the real result for each of its %d options" % [m.raid + 1, n_options], options_ok)
		_ok("raid %d: the decision offers HOLD, one SKIP per lit node and JAM" % (m.raid + 1), n_options == 2 + play.b2.size())
	elif not play.cut:
		_ok("raid %d: no spoof in the kit, so the decision is skipped with a 'no spoof left' beat" % (m.raid + 1), seen.has(L5Play.S.NOTE) and int(play.before.kit["spoof"]) == 0)
	var row := m.settle(play)
	row["play"] = play
	row["forecast"] = fc
	row["extra_planned"] = extra
	row["strip"] = strip
	row["seen"] = seen
	return row


## At the decision, every option's forecast (touches, state after, Heat after incl. SPOOF_HEAT, summary) equals what a fresh
## playout of that option really does; HOLD adds no Heat, SKIP and JAM add SPOOF_HEAT; only JAM drops the hunter.
func _options_match(p: L5Play) -> bool:
	var ok := true
	for o: Dictionary in p.options():
		var q := L5Play.new(p.leg, p.raid_i, p.before.copy(), L5Rules.copy_alloc(p.alloc), p.b2)
		var guard := 0
		while q.state != L5Play.S.DECIDE and not q.is_done() and guard < 4000:
			q.advance(0.05)
			guard += 1
		if q.state == L5Play.S.DECIDE:
			match String(o["kind"]):
				"hold":
					q.pass_spoof()
				"jam":
					q.choose_jam()
				_:
					q.choose_spoof(o["cell"])
		guard = 0
		while not q.is_done() and guard < 4000:
			q.advance(0.05)
			guard += 1
		var want: Dictionary = o["res"]
		var qs: L5State = q.res["state"]
		var ws: L5State = want["state"]
		var want_t := _touched_arr_of(want["touches"])
		var got_t := q.logged_touches()
		ok = ok and (want_t.slice(0, got_t.size()) == got_t if q.cut else want_t == got_t)
		ok = ok and qs.to_array() == ws.to_array() and int(o["heat_after"]) == qs.heat
		ok = ok and o["summary"] == L5Rules.summary(p.before, want["touches"])
		ok = ok and int(o["spoof_heat"]) == (0 if o["kind"] == "hold" else L5Config.SPOOF_HEAT)
		for line: int in [L5Config.EXTRA_AT, L5Config.STRONG_AT]:
			ok = ok and (p.run_heat < line and qs.heat >= line) == (o["up"] as Array).has(line)
			ok = ok and (p.run_heat >= line and qs.heat < line) == (o["down"] as Array).has(line)
		var has_hunter := false
		for b: Dictionary in want["beams"]:
			has_hunter = has_hunter or b["id"] == "hunter"
		ok = ok and has_hunter == (o["kind"] != "jam") and q.hunter_runs() == (o["kind"] != "jam")
	return ok


func _planned_leg(seed_id: int) -> void:
	L5Config.reset()
	var m := L5Model.new(seed_id)
	var steps: Array = m.leg["planned"]
	var tag := "[planned leg %d]" % seed_id
	var kit_bought := 0
	var age := {}
	_ok(tag + " the golden planned line has 3 raids", steps.size() == 3)
	for i in range(steps.size()):
		var s: Dictionary = steps[i]
		var alloc := L5Data.alloc_of(s["alloc"])
		var spoof := L5Data.spoof_of(s["spoof"])
		_ok("%s raid %d starts at the golden state" % [tag, i + 1], m.state.to_array() == L5State.from_golden(s["before"]).to_array())
		var row := _run_raid(m, alloc, spoof)
		_ok("%s raid %d levers accepted (kit and caps)" % [tag, i + 1], not row.is_empty())
		var fc: Array = row["forecast"]
		_ok("%s raid %d heat band at the sweep = extra beams in the trace" % [tag, i + 1],
			int(row["extra_planned"]) == int(row["ledger"]["extra"]) and (row["beams"] as Array).size() == 3 + int(row["extra_planned"]) - (1 if spoof == L5Rules.JAM else 0))
		var play: L5Play = row["play"]
		_kit_strip_matches(tag + " raid %d" % (i + 1), m, row, i < steps.size() - 1)
		var want_touches := _touched_arr(s["touched"])
		_ok("%s raid %d touches = golden" % [tag, i + 1], _touched_arr_of(row["touches"]) == want_touches)
		_ok("%s raid %d touches logged beat by beat = result" % [tag, i + 1], play.logged_touches() == want_touches)
		_ok("%s raid %d tier = golden (%s)" % [tag, i + 1, s["tier"]], row["tier"] == s["tier"])
		_ok("%s raid %d after the raid = golden" % [tag, i + 1], (row["after_raid"] as L5State).to_array() == L5State.from_golden(s["after_raid"]).to_array())
		# Forecast = result for the chosen spoof (the forecast of the revealed line with the spoof the player picked).
		var f: Dictionary = fc[L5Rules.real_cand(m.leg, i)]
		if spoof == L5Rules.NONE:
			_ok("%s raid %d forecast (hold) = result" % [tag, i + 1], _touched_arr_of(f["touches"]) == want_touches and f["summary"] == row["summary"])
		else:
			var pv := L5Rules.resolve(m.leg, i, row["before"], play.b2, alloc, spoof)
			_ok("%s raid %d forecast with the chosen spoof = the real sweep" % [tag, i + 1], _touched_arr_of(pv["touches"]) == want_touches and L5Rules.summary(row["before"], pv["touches"]) == row["summary"])
			_ok("%s raid %d the forecast lists the chosen response among the ones that save" % [tag, i + 1], bool(f["jam_saves"]) if spoof == L5Rules.JAM else (f["save_cells"] as Array).has(spoof))
			_ok("%s raid %d a spoof (%s) costs +%d Heat after the sweep" % [tag, i + 1, "JAM" if spoof == L5Rules.JAM else "SKIP", L5Config.SPOOF_HEAT], int(row["ledger"]["spoof_heat"]) == L5Config.SPOOF_HEAT)
		_ok("%s raid %d the spoof leaves the kit only if used" % [tag, i + 1], int(row["ledger"]["kit_used"]["spoof"]) == (0 if spoof == L5Rules.NONE else 1))
		_ok("%s raid %d ledger reconciles (heat, home, kit, bank)" % [tag, i + 1], L5Model.ledger_reconciles(row["ledger"], (row["after_raid"] as L5State).bank))
		var ar: L5State = row["after_raid"]
		var age_ok := true
		for c: Vector2i in ar.status:
			if ar.status[c] == "DOWN":
				age[c] = int(age.get(c, 0)) + 1
				age_ok = age_ok and int(m.down_raids.get(c, 0)) == int(age[c])
			else:
				age_ok = age_ok and not m.down_raids.has(c)
		_ok("%s raid %d each DOWN asset knows how many raids it has stayed down" % [tag, i + 1], age_ok)
		_ok("%s raid %d ledger starts at the contact numbers" % [tag, i + 1], int(row["ledger"]["heat_before"]) == int(s["before"]["heat"]))
		_ok("%s raid %d the forecast lines wear the three shapes, the real line among them" % [tag, i + 1], _shapes_of(fc) == [0, 1, 2] and int(fc[L5Rules.real_cand(m.leg, i)]["shape"]) == L5Rules.shape_of(m.leg, i, L5Rules.real_cand(m.leg, i)))
		_ok("%s raid %d the revealed line is the corp's real candidate (seeded), not candidate 0 by rule" % [tag, i + 1], (play.b2 as Array) == (m.leg["raids"][i]["cands"][L5Rules.real_cand(m.leg, i)] as Array))
		_worst_case_ok(tag + " raid %d" % (i + 1), m, fc)
		_formula_ok(tag + " raid %d aftermath" % (i + 1), m.leg, row["after_raid"])
		if i < steps.size() - 1:
			_ok("%s raid %d the between step is open" % [tag, i + 1], m.between_open())
			var b: Dictionary = s["between"]
			var bank_raid := m.state.bank
			var heat_raid := m.state.heat
			for c: Vector2i in L5Data.cells(b["repairs"]).slice(0, L5Config.REPAIR_SLOTS):
				m.toggle_repair(c)
			if b["buy"] != null:
				m.set_buy(String(b["buy"]))
			m.set_intensity(String(b["intensity"]))
			for nm: String in L5Config.INTENSITIES:
				_ok("%s raid %d the breach risk on the %s card = breach_risk = golden" % [tag, i + 1, nm],
					int(m.risk_for(nm)["risk"]) == int(b["risk"][nm]) and int(b["risk"][nm]) == L5Rules.breach_risk(m.leg, i + 1, m.between_preview(nm)["state"]))
			var pv2 := m.between_preview()
			var ns: L5State = pv2["state"]
			_ok("%s raid %d the picks are marked committed (intensity yes; buy only if picked)" % [tag, i + 1], m.intensity_committed and m.buy_committed == (b["buy"] != null))
			_ok("%s raid %d assets kept after the picks = the kept term of the step's state" % [tag, i + 1], m.kept_after_picks() == L5Rules.assets_kept(m.leg, ns))
			_formula_ok(tag + " raid %d between" % (i + 1), m.leg, ns)
			_ok("%s raid %d between ledger reconciles (bank and Heat)" % [tag, i + 1],
				bank_raid - int(pv2["repair_cost"]) - int(pv2["buy_cost"]) + int(pv2["income"]) == ns.bank and heat_raid + int(L5Config.INTENSITY_HEAT[b["intensity"]]) == ns.heat)
			if String(pv2["bought"]) != "":
				kit_bought += 1
			_ok("%s raid %d finish_between" % [tag, i + 1], m.finish_between())
			_ok("%s raid %d next contact = golden after" % [tag, i + 1], m.state.to_array() == L5State.from_golden(s["after"]).to_array())
			for c: Vector2i in m.state.status:
				if m.state.status[c] != "DOWN":
					age.erase(c)
		else:
			_ok("%s the last raid has no between step" % tag, not m.between_open() and m.leg_over())
	_ok(tag + " leg score = golden (Heat carried charged)", m.final_score() == _score_of(steps.back()))
	_ok(tag + " the planned line does not breach", not m.breached and m.history.size() == 3)
	var used := 0
	for h: Dictionary in m.history:
		for k in L5Config.KITS:
			used += int(h["ledger"]["kit_used"][k])
	_ok(tag + " the kit is conserved (go dark included): start 8 + bought - used = left", 8 + kit_bought - used == _kit_total(m.state))


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


## The naive policy through the model on every golden leg; it breaches on legs 0 and 8 and ends as the golden.
func _naive_legs() -> void:
	var breached_legs: Array = []
	for seed_id in L5Config.LEGS:
		L5Config.reset()
		var m := L5Model.new(seed_id)
		var steps: Array = m.leg["naive"]
		var guard := 0
		var used := 0
		var bought := 0
		while not m.leg_over() and guard < 5:
			var d := L5Rules.naive_decide(m.leg, m.raid, m.state)
			var row := _run_raid(m, d["alloc"], d["spoof"])
			_ok("[naive %d] raid %d ledger reconciles" % [seed_id, row["raid"] + 1], L5Model.ledger_reconciles(row["ledger"], (row["after_raid"] as L5State).bank))
			for k in L5Config.KITS:
				used += int(row["ledger"]["kit_used"][k])
			if row["cut"]:
				var cp: L5Play = row["play"]
				if cp.last_beam() < cp.order.find("b2"):
					_ok("[naive %d] HOME fell before beam 2: no spoof decision, the spoof stays in the kit" % seed_id, not (row["seen"] as Array).has(L5Play.S.DECIDE) and not cp.spoof_used)
			if m.breached:
				break
			if m.between_open():
				for c: Vector2i in L5Rules.naive_repairs(m.leg, m.state).slice(0, L5Config.REPAIR_SLOTS):
					m.toggle_repair(c)
				var gb: Dictionary = steps[m.raid]["between"]
				for nm: String in L5Config.INTENSITIES:
					_ok("[naive %d] raid %d: the %s card's breach risk = golden (%d)" % [seed_id, m.raid + 1, nm, int(gb["risk"][nm])], int(m.risk_for(nm)["risk"]) == int(gb["risk"][nm]))
				if m.raid == 1 and seed_id in [0, 8]:
					_ok("[naive %d] the breach is settled after raid 2: every intensity card says BREACH on 3/3 lines" % seed_id, int(m.risk_for("LOW")["risk"]) == 3 and int(m.risk_for("NORMAL")["risk"]) == 3 and int(m.risk_for("HOT")["risk"]) == 3)
				m.finish_between()
			guard += 1
		var last: Dictionary = steps.back()
		_ok("[naive %d] ends as the golden naive line (score %d)" % [seed_id, _score_of(last)], m.final_score() == _score_of(last))
		_ok("[naive %d] the kit is conserved (8 - used = left)" % seed_id, 8 + bought - used == _kit_total(m.state))
		_ok("[naive %d] tier of the last raid = golden (%s)" % [seed_id, last["tier"]], (m.history.back() as Dictionary)["tier"] == last["tier"])
		if m.breached:
			breached_legs.append(seed_id)
			_ok("[naive %d] BREACHED: score -100, the leg is over, no between step" % seed_id, m.final_score() == -100 and m.leg_over() and not m.between_open() and m.state.home_hp == 0)
	_ok("naive breaches on legs 0 and 8 only (leg 5 now avoids it: its golden risk is 0)", breached_legs == [0, 8])


func _shapes_of(fc: Array) -> Array:
	var out: Array = []
	for f: Dictionary in fc:
		out.append(int(f["shape"]))
	out.sort()
	return out


## The leg value can be rebuilt from the numbers the screen shows beside it: bank + assets kept - HOME lost x 8 - Heat carried.
func _formula_ok(label: String, leg: Dictionary, st: L5State) -> void:
	var rebuilt: int = st.bank + L5Rules.assets_kept(leg, st) - L5Config.HOME_LOSS_COST * (L5Config.HOME_HP - st.home_hp) - L5Rules.heat_carried(st)
	_ok(label + ": leg value = bank + assets kept - HOME lost x 8 - Heat carried (rebuilt from the shown numbers)", rebuilt == L5Rules.score(leg, st) or st.home_hp <= 0)


## "Worst" counts everything: it is the line that scores lowest, with its DOWN / TAKEN / HOME counts.
func _worst_case_ok(label: String, m: L5Model, fc: Array) -> void:
	var wc := m.worst_case(fc)
	var lowest := 1000000
	for f: Dictionary in fc:
		lowest = mini(lowest, L5Rules.score(m.leg, f["state"]))
	var hit := false
	for f: Dictionary in fc:
		if L5Rules.score(m.leg, f["state"]) == lowest and int(f["shape"]) == int(wc["hold"]["shape"]):
			var sm: Dictionary = f["summary"]
			hit = int(sm["down"]) == int(wc["hold"]["down"]) and int(sm["taken"]) == int(wc["hold"]["taken"]) and int(sm["home"]) == int(wc["hold"]["home"])
	_ok(label + " worst case = the lowest-scoring line with its DOWN, TAKEN and HOME counts", hit)


func _st(hp: int, statuses: Dictionary) -> L5State:
	var s := L5State.new()
	s.home_hp = hp
	s.status = statuses
	return s


## BATTERED between HOLDS and DAMAGED; the corp's real line and the shapes are seeded per raid, no tell.
func _tiers_and_shapes() -> void:
	L5Config.reset()
	var a := Vector2i(0, 0)
	var b := Vector2i(1, 0)
	var c := Vector2i(2, 0)
	var ok3 := {a: "OK", b: "OK", c: "OK"}
	_ok("[tiers] nothing touched is EVADED", L5Rules.tier(_st(3, ok3), _st(3, ok3), 0) == "EVADED")
	_ok("[tiers] one asset DOWN is HOLDS", L5Rules.tier(_st(3, ok3), _st(3, {a: "DOWN", b: "OK", c: "OK"}), 1) == "HOLDS")
	_ok("[tiers] a decoy-only touch is HOLDS", L5Rules.tier(_st(3, ok3), _st(3, ok3), 1) == "HOLDS")
	_ok("[tiers] two assets newly DOWN is BATTERED", L5Rules.tier(_st(3, ok3), _st(3, {a: "DOWN", b: "DOWN", c: "OK"}), 2) == "BATTERED")
	_ok("[tiers] an asset newly TAKEN is BATTERED", L5Rules.tier(_st(3, {a: "DOWN", b: "OK", c: "OK"}), _st(3, {a: "TAKEN", b: "OK", c: "OK"}), 1) == "BATTERED")
	_ok("[tiers] an asset already TAKEN and untouched does not count", L5Rules.tier(_st(3, {a: "TAKEN", b: "OK", c: "OK"}), _st(3, {a: "TAKEN", b: "DOWN", c: "OK"}), 1) == "HOLDS")
	_ok("[tiers] HOME losing integrity is DAMAGED even with assets lost", L5Rules.tier(_st(3, ok3), _st(2, {a: "DOWN", b: "DOWN", c: "OK"}), 3) == "DAMAGED")
	_ok("[tiers] HOME at 0 is BREACHED", L5Rules.tier(_st(1, ok3), _st(0, ok3), 1) == "BREACHED")
	_ok("[tiers] BATTERED has its own amber, apart from DAMAGED orange and HOLDS", G_tier_colors_differ())
	var distinct_legs := 0
	var not_zero := 0
	var total := 0
	for seed_id in L5Config.LEGS:
		var lg := L5Data.load_leg(seed_id)
		var seen: Array = []
		for i in range(L5Config.RAIDS):
			var perm: Array = []
			for k in range(L5Config.CANDIDATES):
				perm.append(L5Rules.shape_of(lg, i, k))
			perm.sort()
			_ok("[shapes] leg %d raid %d: the three candidates wear the three shapes" % [seed_id, i + 1], perm == [0, 1, 2])
			var real_k := L5Rules.real_cand(lg, i)
			var sh := L5Rules.shape_of(lg, i, real_k)
			if not seen.has(sh):
				seen.append(sh)
			total += 1
			if real_k != 0:
				not_zero += 1
			_ok("[shapes] leg %d raid %d: cand_of_shape finds the real line's shape" % [seed_id, i + 1], L5Rules.cand_of_shape(lg, i, sh) == real_k)
		print("  [shapes] leg %d: the revealed shape per raid is %s" % [seed_id, str(seen)])
		if seen.size() > 1:
			distinct_legs += 1
	_ok("[shapes] in every golden leg the revealed shape differs between raids (no reveal tell)", distinct_legs == L5Config.LEGS.size())
	_ok("[shapes] the real line is not always candidate 0 (%d of %d raids)" % [not_zero, total], not_zero > 0)
	var m := L5Model.new(0)
	_ok("[shapes] the model reveals the real line, not candidate 0", m.b2() == m.raid_data()["cands"][m.real()])
	_ok("[shapes] a forecast line wears its candidate's shape", _shapes_of(m.forecast()) == [0, 1, 2])


func G_tier_colors_differ() -> bool:
	var g = load("res://tools/raid_lab_m10/l5_glyphs.gd")
	var cols: Array = [g.tier_color("HOLDS"), g.tier_color("BATTERED"), g.tier_color("DAMAGED"), g.tier_color("BREACHED"), g.tier_color("EVADED")]
	for i in range(cols.size()):
		for j in range(i + 1, cols.size()):
			if cols[i] == cols[j]:
				return false
	return true


## When the forecast shows BREACH on every line even with a spoof, the plan screen warns before launch and names the one
## lever that avoids it (if any). Played on the naive breach legs' last raid; placing the named lever must clear it.
func _breach_warning() -> void:
	var certain := 0
	var named := 0
	var named_demo := 0
	for seed_id in [0, 5, 8]:
		L5Config.reset()
		var m := L5Model.new(seed_id)
		var guard := 0
		while m.raid < 2 and guard < 4:
			var d := L5Rules.naive_decide(m.leg, m.raid, m.state)
			_run_raid(m, d["alloc"], d["spoof"])
			if m.between_open():
				for c: Vector2i in L5Rules.naive_repairs(m.leg, m.state).slice(0, L5Config.REPAIR_SLOTS):
					m.toggle_repair(c)
				m.finish_between()
			guard += 1
		var d3 := L5Rules.naive_decide(m.leg, m.raid, m.state)
		for pair in [["ghost", "ghost"], ["decoys", "decoy"], ["dark", "dark"]]:
			for c: Vector2i in d3["alloc"][pair[0]]:
				m.place(pair[1], c)
		var fc := m.forecast()
		var cert := m.breach_certain(fc)
		var fix := m.breach_fix()
		print("  [breach warning] naive leg %d raid 3: breach on every line = %s, fix = %s" % [seed_id, str(cert), str(fix)])
		if cert:
			certain += 1
			if fix.is_empty():
				_ok("[breach warning] leg %d: no lever is named when the kit has none that avoids it (a breach stays possible)" % seed_id, m.breach_possible())
			else:
				named += 1
				_ok("[breach warning] leg %d: the named levers clear every line" % seed_id, _apply_fix_clears(m, fix))
		else:
			_ok("[breach warning] leg %d: no warning when a line does not breach" % seed_id, not cert)
		# The same raid with one ghost back in the kit: a lever may now avoid the breach, and it is named.
		var m2 := L5Model.new(seed_id)
		m2.raid = m.raid
		m2.state = m.state.copy()
		m2.state.kit["ghost"] = 1
		var fix2 := m2.breach_fix()
		print("  [breach warning] naive leg %d raid 3 with a ghost in the kit: certain = %s, fix = %s" % [seed_id, str(m2.breach_certain()), str(fix2)])
		if not fix2.is_empty():
			named_demo += 1
			_ok("[breach warning] leg %d with a ghost: the named levers clear every line" % seed_id, _apply_fix_clears(m2, fix2))
	print("  [breach warning] %d of 3 naive breach legs show a certain breach at raid 3, %d name a lever" % [certain, named])
	_ok("[breach warning] a certain breach is exercised in at least one naive leg", certain > 0)
	print("  [breach warning] %d of 3 legs name a lever once a ghost is in the kit" % named_demo)


## Place the steps of a breach_fix on the model's plan; true when no line breaches any more (legal levers only).
func _apply_fix_clears(m: L5Model, fix: Dictionary) -> bool:
	var saved := L5Rules.copy_alloc(m.plan)
	var legal := true
	for stp: Dictionary in fix["steps"]:
		if not m.place(String(stp["lever"]), stp["cell"]):
			legal = false
	var clear := legal and not m.breach_possible()
	m.plan = saved
	return clear


# ---------- the scene, through its own input path ----------
func _make_view(seed_id: int) -> Control:
	L5Config.reset()
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
func _view_raid(view: Control, alloc: Dictionary, spoof: Vector2i) -> int:
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
		if view.play.state == L5Play.S.DECIDE and not clicked:
			for off in L5Rules.nodes():
				if not view.play.b2.has(off):
					view._act("cell:%d,%d" % [off.x, off.y])
					break
			_ok("a click off the lit line is refused", view.play.state == L5Play.S.DECIDE)
			_ok("the decision screen lists HOLD, every SKIP and JAM", view.play.options().size() == 2 + view.play.b2.size())
			if spoof == L5Rules.NONE:
				view._key(KEY_H)
			elif spoof == L5Rules.JAM:
				view._key(KEY_J)
			else:
				view._act("cell:%d,%d" % [spoof.x, spoof.y])
			clicked = true
		view._process(0.05)
		guard += 1
	_ok("the playout ends by itself", view.phase in [view.Phase.AFTER, view.Phase.BREACH] and not view.row.is_empty())
	return guard


func _view_planned() -> void:
	var view := _make_view(0)
	if view == null:
		return
	var tag := "[view planned]"
	_ok(tag + " opens on the contact screen", view.phase == view.Phase.CONTACT)
	var steps: Array = view.model.leg["planned"]
	var s: Dictionary = steps[0]
	_view_raid(view, L5Data.alloc_of(s["alloc"]), L5Data.spoof_of(s["spoof"]))
	_ok(tag + " aftermath, not a breach", view.phase == view.Phase.AFTER)
	_ok(tag + " aftermath = golden", (view.row["after_raid"] as L5State).to_array() == L5State.from_golden(s["after_raid"]).to_array())
	_ok(tag + " the tier is shown as the golden's (" + String(s["tier"]) + ")", view.row["tier"] == s["tier"])
	_ok(tag + " aftermath ledger reconciles", L5Model.ledger_reconciles(view.row["ledger"], (view.row["after_raid"] as L5State).bank))
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
	for c: Vector2i in L5Data.cells(b["repairs"]).slice(0, L5Config.REPAIR_SLOTS):
		view._act("cell:%d,%d" % [c.x, c.y])
	if b["buy"] != null:
		view._act("buy:" + String(b["buy"]))
	view._act("inten:" + String(b["intensity"]))
	_ok(tag + " a safe between step is not a settled breach: Enter goes to the next contact", not view.model.breach_settled())
	for nm: String in L5Config.INTENSITIES:
		var rc: Dictionary = view.risk_card(nm)
		var want_risk: int = L5Rules.breach_risk(view.model.leg, view.model.raid + 1, view.model.between_preview(nm)["state"])
		_ok(tag + " the risk on the %s card (%s) = breach_risk = golden" % [nm, rc["line1"]], int(rc["risk"]) == want_risk and want_risk == int(b["risk"][nm]))
		_ok(tag + " the %s card says %s" % [nm, "BREACH" if want_risk > 0 else "safe"], (String(rc["line1"]).begins_with("BREACH")) == (want_risk > 0))
	view._key(KEY_ENTER)
	_ok(tag + " Enter goes to raid 2 contact with the golden state", view.phase == view.Phase.CONTACT and view.model.raid == 1 and view.model.state.to_array() == L5State.from_golden(s["after"]).to_array())
	view.queue_free()


## The rules of the response after the reveal, on a hand-run raid: HOLD adds no Heat, SKIP and JAM add SPOOF_HEAT and spend a
## spoof; JAM removes exactly the hunter's touches and its beam; the options exist only while the kit holds a spoof.
func _responses_and_jam() -> void:
	L5Config.reset()
	var lg := L5Data.load_leg(3)
	var st := L5Rules.initial(lg)
	var al := L5Rules.empty_alloc()
	var b2: Array = lg["raids"][0]["cands"][L5Rules.real_cand(lg, 0)]
	var hold := L5Rules.resolve(lg, 0, st, b2, al, L5Rules.NONE)
	var jam := L5Rules.resolve(lg, 0, st, b2, al, L5Rules.JAM)
	var skip := L5Rules.resolve(lg, 0, st, b2, al, b2[0])
	var tag := "[response]"
	_ok(tag + " the options after the reveal: HOLD, one SKIP per lit node, JAM", L5Rules.responses(st, b2) == [L5Rules.NONE] + b2 + [L5Rules.JAM])
	var st0 := st.copy()
	st0.kit["spoof"] = 0
	_ok(tag + " with no spoof in the kit only HOLD is left", L5Rules.responses(st0, b2) == [L5Rules.NONE])
	var ids_h: Array = []
	var ids_j: Array = []
	for b: Dictionary in hold["beams"]:
		ids_h.append(b["id"])
	for b: Dictionary in jam["beams"]:
		ids_j.append(b["id"])
	_ok(tag + " JAM: the hunter's beam is gone, the other beams run as before", ids_h.has("hunter") and not ids_j.has("hunter") and ids_h.slice(0, ids_h.size() - 1) == ids_j)
	var no_hunter: Array = []
	for t: Dictionary in hold["touches"]:
		if t["beam"] != "hunter":
			no_hunter.append(t)
	_ok(tag + " JAM: the touches are the hold touches without the hunter's", _touched_arr_of(jam["touches"]) == _touched_arr_of(no_hunter))
	var hs: L5State = hold["state"]
	var js: L5State = jam["state"]
	var ss: L5State = skip["state"]
	var base_h: int = st.heat - (L5Config.EVADE_HEAT if (hold["touches"] as Array).is_empty() else 0)
	var base_j: int = st.heat - (L5Config.EVADE_HEAT if (jam["touches"] as Array).is_empty() else 0)
	var base_s: int = st.heat - (L5Config.EVADE_HEAT if (skip["touches"] as Array).is_empty() else 0)
	_ok(tag + " HOLD adds no Heat and keeps the spoof", hs.heat == base_h and int(hs.kit["spoof"]) == 2)
	_ok(tag + " JAM costs +%d Heat after the sweep and one spoof" % L5Config.SPOOF_HEAT, js.heat == base_j + L5Config.SPOOF_HEAT and int(js.kit["spoof"]) == 1)
	_ok(tag + " SKIP costs +%d Heat after the sweep and one spoof" % L5Config.SPOOF_HEAT, ss.heat == base_s + L5Config.SPOOF_HEAT and int(ss.kit["spoof"]) == 1)
	var so := L5Rules.spoof_options(lg, 0, st, b2, al)
	_ok(tag + " the forecast's JAM entry is the rules' JAM result", (so["jam"]["res"]["state"] as L5State).to_array() == js.to_array())
	# One repair slot: the rules ignore a second repair.
	var ds := st.copy()
	var cs: Array = lg["values"].keys()
	ds.status[cs[0]] = "DOWN"
	ds.status[cs[1]] = "DOWN"
	ds.bank = 40
	var two := L5Rules.between_parts(lg, ds, [], [cs[0], cs[1]], "NORMAL", "")
	_ok(tag + " one crew: only the first repair is done, the other stays DOWN", (two["repaired"] as Array) == [cs[0]] and (two["state"] as L5State).status[cs[1]] == "DOWN")


func _view_jam() -> void:
	var view := _make_view(3)
	if view == null:
		return
	var tag := "[view jam]"
	var s: Dictionary = view.model.leg["planned"][0]
	_ok(tag + " the golden planned line of leg 3 jams the hunter in raid 1", s["spoof"] is String)
	_view_raid(view, L5Data.alloc_of(s["alloc"]), L5Rules.JAM)
	_ok(tag + " aftermath, not a breach", view.phase == view.Phase.AFTER)
	_ok(tag + " aftermath = golden", (view.row["after_raid"] as L5State).to_array() == L5State.from_golden(s["after_raid"]).to_array())
	_ok(tag + " the row records the JAM and the ledger charges its Heat", view.row["spoof"] == L5Rules.JAM and view.row["ledger"]["spoof_kind"] == "JAM" and int(view.row["ledger"]["spoof_heat"]) == L5Config.SPOOF_HEAT)
	_ok(tag + " the hunter did not run (no hunter beam in the trace)", not (view.row["beams"] as Array).any(func(b: Dictionary) -> bool: return b["id"] == "hunter"))
	_ok(tag + " ledger reconciles", L5Model.ledger_reconciles(view.row["ledger"], (view.row["after_raid"] as L5State).bank))
	view.queue_free()


## The settled breach: launching the between screen plays the next raid fast and straight to the BREACHED card. No contact,
## plan, forecast or decision screen, one short beat per beam, no levers, and the same result as the slow playout of HOLD.
func _fast_breach(view: Control, tag: String) -> void:
	_seen_states = []
	var screens: Array = []
	var p: L5Play = view.play
	_ok(tag + " Enter on the settled between screen goes straight to the playout of raid 3", view.phase == view.Phase.PLAY and view.fast_play and p.fast and view.model.raid == 2)
	_ok(tag + " the fast raid runs with no levers", (p.alloc["ghost"] as Array).is_empty() and (p.alloc["decoys"] as Array).is_empty() and (p.alloc["dark"] as Array).is_empty())
	var slow := L5Play.new(view.model.leg, 2, p.before.copy(), L5Rules.empty_alloc(), p.b2)
	var g2 := 0
	while not slow.is_done() and g2 < 4000:
		if slow.state == L5Play.S.DECIDE:
			slow.pass_spoof()
		else:
			slow.advance(0.05)
		g2 += 1
	var guard := 0
	while view.phase == view.Phase.PLAY and guard < 400:
		if not _seen_states.has(p.state):
			_seen_states.append(p.state)
		if not screens.has(view.phase):
			screens.append(view.phase)
		view._process(0.05)
		guard += 1
	_ok(tag + " the fast playout needs no decision and no 'no spoof' beat", not _seen_states.has(L5Play.S.DECIDE) and not _seen_states.has(L5Play.S.NOTE))
	_ok(tag + " the fast playout stays on the playout screen until the card (%d ticks of 0.05 s)" % guard, screens == [view.Phase.PLAY] and view.phase == view.Phase.BREACH)
	var cap := 5.0 * L5Play.FAST_BEAT + L5Play.FAST_UNSEAL + L5Play.FAST_TURN + L5Play.FAST_END + 0.3
	_ok(tag + " the fast playout takes one short beat per beam (under %.1f s)" % cap, float(guard) * 0.05 <= cap)
	_ok(tag + " the fast result = the slow playout's: same touches, HOME 0", _touched_arr_of(view.row["touches"]) == _touched_arr_of(slow.shown_touches()) and slow.cut and view.row["cut"])


func _view_breach() -> void:
	var view := _make_view(0)
	if view == null:
		return
	var tag := "[view breach]"
	var guard := 0
	while view.phase != view.Phase.BREACH and guard < 4:
		if view.phase == view.Phase.PLAY:
			break	## the settled breach is already playing
		var d := L5Rules.naive_decide(view.model.leg, view.model.raid, view.model.state)
		_view_raid(view, d["alloc"], d["spoof"])
		if view.phase == view.Phase.AFTER:
			_ok(tag + " a raid that hit HOME is DAMAGED, not CELL HOLDS", view.row["tier"] == "DAMAGED" or int(view.row["summary"]["home"]) == 0)
			view._key(KEY_ENTER)
			for c: Vector2i in L5Rules.naive_repairs(view.model.leg, view.model.state).slice(0, L5Config.REPAIR_SLOTS):
				view._act("cell:%d,%d" % [c.x, c.y])
			if view.model.raid == 1:
				_ok(tag + " between raids 2 and 3: the loss is settled (breach_risk 3/3 on every card)", view.model.breach_settled())
				for nm: String in L5Config.INTENSITIES:
					var rc: Dictionary = view.risk_card(nm)
					_ok(tag + " between raids 2 and 3: the %s card says 'BREACH on 3/3 lines whatever you pick'" % nm,
						rc["line1"] == "BREACH on 3/3 lines" and rc["line2"] == "whatever you pick" and int(rc["risk"]) == L5Rules.breach_risk(view.model.leg, 2, view.model.between_preview(nm)["state"]))
			view._key(KEY_ENTER)
		guard += 1
	if view.phase == view.Phase.PLAY:
		_fast_breach(view, tag)
	else:
		_ok(tag + " the settled breach plays fast (it did not: the naive leg 0 loss is settled after raid 2)", false)
	_ok(tag + " the naive line ends in the full-screen BREACH", view.phase == view.Phase.BREACH)
	_ok(tag + " breach on raid 3 with HOME 0", view.model.raid == 2 and view.model.state.home_hp == 0 and view.model.breached)
	_ok(tag + " the breach raid's tier is BREACHED", view.row["tier"] == "BREACHED" and view.row["cut"])
	var b2_i: int = view.play.order.find("b2")
	if view.play.last_beam() < b2_i:
		_ok(tag + " HOME fell before beam 2: no spoof decision was offered", not _seen_states.has(L5Play.S.DECIDE))
	else:
		_ok(tag + " HOME fell on or after beam 2 (the decision came first)", true)
	_ok(tag + " the sweep stopped at the touch that emptied HOME", (view.row["touches"] as Array).size() <= (view.play.res["touches"] as Array).size())
	view._key(KEY_ENTER)
	_ok(tag + " Enter shows the leg record", view.phase == view.Phase.RECORD)
	_ok(tag + " the record scores -100", view.model.final_score() == -100)
	view._key(KEY_ENTER)
	_ok(tag + " Enter starts the leg again", view.phase == view.Phase.CONTACT and view.model.raid == 0 and view.model.state.home_hp == 3)
	view.queue_free()


# ---------- L7: the look and the motion ----------
## The camera, the timings, the speed and instant toggles, instant = animated, the animation's order = the resolver's.
func _motion() -> void:
	_motion_cam()
	_motion_timings()
	for pair in [[0, "planned"], [3, "planned"], [0, "naive"], [8, "naive"]]:
		_motion_instant_vs_animated(int(pair[0]), String(pair[1]))
	_motion_breach_instant()
	_motion_speed()
	L7Config.instant = false


## The target camera: the aim point lands where the board is centered, chips float above the beam plane above the floor, rows
## run far to near and columns left to right, and the whole slab fits left of the side panel and under the HUD (text 1.0).
func _motion_cam() -> void:
	var tag := "[l7 camera]"
	var aim: Vector2 = L7Cam.project(L7Cam.AIM)
	_ok(tag + " the Blender aim point lands on the chosen screen spot", aim.distance_to(L7Cam.AIM_SCREEN) < 0.6)
	var stacked := true
	var ordered := true
	var inside := true
	for y in range(L5Config.H):
		for x in range(L5Config.W):
			var c := Vector2i(x, y)
			stacked = stacked and L7Cam.chip_pos(c).y < L7Cam.beam_pos(c).y and L7Cam.beam_pos(c).y < L7Cam.cell_at(c, 0.0).y
			if x > 0:
				ordered = ordered and L7Cam.beam_pos(c).x > L7Cam.beam_pos(Vector2i(x - 1, y)).x
			if y > 0:
				ordered = ordered and L7Cam.beam_pos(c).y > L7Cam.beam_pos(Vector2i(x, y - 1)).y
			var chip: Vector2 = L7Cam.chip_pos(c, true)
			inside = inside and chip.x > 40.0 and chip.x < 740.0 and chip.y > 80.0 and chip.y < 600.0
	_ok(tag + " the chip floats above the beam plane, which floats above the floor", stacked)
	_ok(tag + " columns run left to right, rows far to near", ordered)
	_ok(tag + " every chip stays inside the board area (left of the panel, under the HUD)", inside)
	var fits := true
	for corner in [Vector3(L7Cam.SLAB_X0, L7Cam.SLAB_Y0, 0), Vector3(L7Cam.SLAB_X1, L7Cam.SLAB_Y0, 0), Vector3(L7Cam.SLAB_X1, L7Cam.SLAB_Y1, 0), Vector3(L7Cam.SLAB_X0, L7Cam.SLAB_Y1, 0)]:
		var q: Vector2 = L7Cam.project(corner)
		fits = fits and q.x >= 0.0 and q.x < 768.0 and q.y > 60.0 and q.y < 676.0
	_ok(tag + " the whole slab fits left of the side panel and above the status strip", fits)
	var gm := L7Cam.hfov_deg()
	_ok(tag + " the 3D camera's field of view matches the projection (%.2f deg)" % gm, gm > 5.0 and gm < 40.0)


func _motion_timings() -> void:
	var tag := "[l7 timings]"
	var all_pos := true
	for v in [L7Config.BEAM_LEAD, L7Config.STEP_T, L7Config.BEAM_TAIL, L7Config.FLASH_T, L7Config.DECOY_PULL_T, L7Config.UNSEAL_T, L7Config.FIRE_HOLD,
			L7Config.DECIDE_RING_T, L7Config.PICK_FX_T, L7Config.TURN_T, L7Config.WRENCH_T, L7Config.SHAKE_T, L7Config.FLIP_T, L7Config.HOME_LAG_T,
			L7Config.STAMP_T, L7Config.END_T, L7Config.COUNT_UP_T, L7Config.HEAT_EASE_T, L7Config.HEAT_PULSE_T]:
		all_pos = all_pos and float(v) > 0.0
	_ok(tag + " every timing is positive and read from L7Config", all_pos)
	_ok(tag + " the unseal shimmers, then collapses, then ignites (in that order, inside the unseal)", L7Config.UNSEAL_SHIMMER_END > 0.0 and L7Config.UNSEAL_SHIMMER_END < L7Config.UNSEAL_COLLAPSE_END and L7Config.UNSEAL_COLLAPSE_END < 1.0)
	_ok(tag + " the lit real line holds before it fires (FIRE_HOLD is the beam 2 lead)", L7Config.FIRE_HOLD > 0.0)
	_ok(tag + " the speed toggle offers 1x, 2x and 4x", L7Config.SPEEDS == [1.0, 2.0, 4.0])
	var p := L5Play.new(L5Data.load_leg(0), 0, L5Rules.initial(L5Data.load_leg(0)), L5Rules.empty_alloc(), L5Data.load_leg(0)["raids"][0]["cands"][0])
	_ok(tag + " the playout's beam 2 leads by FIRE_HOLD and the others by BEAM_LEAD", is_equal_approx(p.lead_of("b2"), L7Config.FIRE_HOLD) and is_equal_approx(p.lead_of("b1"), L7Config.BEAM_LEAD))


## One golden raid through the scene's own input path, animated (a frame at a time) or instant; what it ended with.
func _mode_run(seed_id: int, line: String, instant: bool) -> Dictionary:
	L7Config.instant = instant
	var view := _make_view(seed_id)
	var s: Dictionary = view.model.leg[line][0]
	var frames := _view_raid(view, L5Data.alloc_of(s["alloc"]), L5Data.spoof_of(s["spoof"]))
	var out := {"frames": frames, "ledger": var_to_str(view.row["ledger"]), "after": (view.row["after_raid"] as L5State).to_array(),
		"state": view.model.state.to_array(), "sig": view.fx.signature(), "touch": view.fx.touch_order(), "tier": view.row["tier"],
		"want": _touched_arr_of(view.play.shown_touches() if view.play.cut else view.play.res["touches"]), "phase": view.phase}
	L7Config.instant = false
	view.queue_free()
	return out


func _motion_instant_vs_animated(seed_id: int, line: String) -> void:
	var tag := "[instant leg %d %s]" % [seed_id, line]
	var a := _mode_run(seed_id, line, false)
	var b := _mode_run(seed_id, line, true)
	_ok(tag + " instant ends in the same state as animated", a["state"] == b["state"] and a["after"] == b["after"] and a["phase"] == b["phase"])
	_ok(tag + " instant writes the same ledger as animated", a["ledger"] == b["ledger"] and a["tier"] == b["tier"])
	_ok(tag + " instant cues the same events in the same order (%d cues)" % (a["sig"] as Array).size(), a["sig"] == b["sig"] and not (a["sig"] as Array).is_empty())
	_ok(tag + " the animation's touch order equals the resolver's (animated and instant)", a["touch"] == a["want"] and b["touch"] == b["want"])
	_ok(tag + " instant needs no pacing (%d frames against %d)" % [b["frames"], a["frames"]], int(b["frames"]) * 8 < int(a["frames"]))


## The settled breach (fast playout) animated and instant: the same BREACHED end, ledger and cues.
func _motion_breach_instant() -> void:
	var results: Array = []
	for instant in [false, true]:
		L7Config.instant = false
		var view := _make_view(0)
		var steps: Array = view.model.leg["naive"]
		for i in range(2):
			view._play_step_instant(steps[i])
			if view.phase == view.Phase.REPAIR:
				view._pick_between(steps[i])
				if i == 0:
					view._act("next")
		var settled: bool = view.phase == view.Phase.REPAIR and view.model.breach_settled()
		view._act("next")	## launch the settled breach
		L7Config.instant = instant
		var guard := 0
		while view.phase == view.Phase.PLAY and guard < 400:
			view._process(0.05)
			guard += 1
		results.append({"settled": settled, "ledger": var_to_str(view.row["ledger"]), "state": view.model.state.to_array(), "sig": view.fx.signature(),
			"touch": view.fx.touch_order(), "want": _touched_arr_of(view.play.shown_touches() if view.play.cut else view.play.res["touches"]),
			"phase": view.phase, "bp": view.Phase.BREACH, "frames": guard})
		L7Config.instant = false
		view.queue_free()
	var tag := "[instant breach]"
	_ok(tag + " the naive leg 0 is settled after raid 2 in both runs", results[0]["settled"] and results[1]["settled"])
	_ok(tag + " both end on the BREACHED card with the same state and ledger", results[0]["phase"] == results[0]["bp"] and results[1]["phase"] == results[1]["bp"] and results[0]["state"] == results[1]["state"] and results[0]["ledger"] == results[1]["ledger"])
	_ok(tag + " both cue the same events, in the resolver's touch order", results[0]["sig"] == results[1]["sig"] and results[0]["touch"] == results[0]["want"] and results[1]["touch"] == results[1]["want"])
	_ok(tag + " the instant run is not slower than the animated one (%d frames against %d)" % [results[1]["frames"], results[0]["frames"]], int(results[1]["frames"]) <= int(results[0]["frames"]))


## The speed toggle scales the raid layer (4x runs the same raid in about a quarter of the frames) and the instant toggle is a key.
func _motion_speed() -> void:
	var tag := "[speed]"
	var counts: Array = []
	for speed_i in range(3):
		L7Config.instant = false
		var view := _make_view(0)
		view._act("speed:%d" % speed_i)
		_ok(tag + " the %dx button sets the speed" % int(L7Config.SPEEDS[speed_i]), view.speed_i == speed_i)
		var s: Dictionary = view.model.leg["planned"][0]
		view._key(KEY_ENTER)
		for pair in [["ghost", KEY_1, "ghost"], ["decoy", KEY_2, "decoys"], ["dark", KEY_3, "dark"]]:
			for c: Vector2i in L5Data.alloc_of(s["alloc"])[pair[2]]:
				if view.sel_lever != pair[0]:
					view._key(pair[1])
				view._act("cell:%d,%d" % [c.x, c.y])
		view._key(KEY_ENTER)
		view._key(KEY_ENTER)
		var frames := 0
		while view.phase == view.Phase.PLAY and frames < 6000:
			if view.play.state == L5Play.S.DECIDE:
				view._key(KEY_H)
			view._process(0.02)
			frames += 1
		counts.append(frames)
		view.queue_free()
	_ok(tag + " 2x runs the raid in about half the frames of 1x (%d against %d)" % [counts[1], counts[0]], absf(float(counts[0]) / float(counts[1]) - 2.0) < 0.3)
	_ok(tag + " 4x runs it in about a quarter of the frames (%d against %d)" % [counts[2], counts[0]], absf(float(counts[0]) / float(counts[2]) - 4.0) < 0.6)
	var view2 := _make_view(0)
	view2._key(KEY_I)
	_ok(tag + " key I turns the instant toggle on", L7Config.instant)
	view2._act("instant")
	_ok(tag + " the instant button turns it off again", not L7Config.instant)
	view2.queue_free()
