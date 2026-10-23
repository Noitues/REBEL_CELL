class_name L5Model
extends RefCounted
## Lab state of one leg of 3 raids on ONE network: the leg kit, the player's plan, undo, the campaign numbers, the
## settled raids and the between-raids step (repairs, one shop buy, run intensity). The rules are all in L5Rules.

const LEVERS: Array = ["ghost", "decoy", "dark"]
const ALLOC_KEY := {"ghost": "ghost", "decoy": "decoys", "dark": "dark"}

var leg: Dictionary = {}
var seed_id: int = 0
var raid: int = 0
## The network, kit and campaign numbers at contact (before the plan charges anything).
var state: L5State
var plan: Dictionary = L5Rules.empty_alloc()
var _undo: Array = []
## Settled raids: {raid, before, alloc, spoof, touches, outcomes, summary, after_raid, evaded, tier, cut, ledger,
## beams, between (set when the between step is done)}.
var history: Array = []
var breached: bool = false
## The between step's picks: repairs in click order, one shop buy ("" = none), the run intensity.
var pending_repairs: Array = []
var pending_buy: String = ""
var pending_intensity: String = "NORMAL"
## True once the player has clicked a buy / an intensity (the defaults are NO BUY and NORMAL until then): the between
## screen marks only committed choices.
var buy_committed: bool = false
var intensity_committed: bool = false
## The last between step: {repaired, repair_cost, bought, buy_cost, income, heat_add, intensity, before, after};
## empty on raid 1.
var run_note: Dictionary = {}
## Raids each DOWN asset has now stayed down (cell -> n; the raid that took it down counts as 1).
var down_raids: Dictionary = {}
## breach_risk of the next raid per between-step state, cached (the search is the heavy part): key -> {risk, empty}.
var _risk_cache: Dictionary = {}


func _init(p_seed: int = 0) -> void:
	new_leg(p_seed)


func new_leg(p_seed: int) -> void:
	seed_id = p_seed
	leg = L5Data.load_leg(p_seed)
	raid = 0
	state = L5Rules.initial(leg)
	history = []
	down_raids = {}
	breached = false
	_reset_between()
	run_note = {}
	_reset_plan()


func _reset_plan() -> void:
	plan = L5Rules.empty_alloc()
	_undo = []


func _reset_between() -> void:
	pending_repairs = []
	pending_buy = ""
	pending_intensity = "NORMAL"
	buy_committed = false
	intensity_committed = false


func raid_data() -> Dictionary:
	return leg["raids"][raid]


## The corp's real sealed line (the candidate the playout reveals).
func real() -> int:
	return L5Rules.real_cand(leg, raid)


## The shape drawn for candidate k of this raid (0 triangle, 1 square, 2 circle).
func shape(k: int) -> int:
	return L5Rules.shape_of(leg, raid, k)


func b2() -> Array:
	return raid_data()["cands"][real()]


func home() -> Vector2i:
	return leg["home"]


func values() -> Dictionary:
	return leg["values"]


func leg_over() -> bool:
	return breached or history.size() >= L5Config.RAIDS


## Heat shown on the meter: the ghost already raised it.
func heat_now() -> int:
	return state.heat + L5Config.GHOST_HEAT * (plan["ghost"] as Array).size()


## Extra known beams the raid will run with at the current plan.
func extra_now() -> int:
	return L5Rules.extra_count(heat_now())


## The kit left if the plan goes ahead (a spoof is spent only if used after the reveal, so it stays whole here).
func kit_left() -> Dictionary:
	return {"ghost": int(state.kit["ghost"]) - (plan["ghost"] as Array).size(),
		"decoy": int(state.kit["decoy"]) - (plan["decoys"] as Array).size(), "spoof": int(state.kit["spoof"]),
		"dark": int(state.kit["dark"]) - (plan["dark"] as Array).size()}


func why_not(lever: String, c: Vector2i) -> String:
	return L5Rules.why_not(leg, state, plan, lever, c)


func place(lever: String, c: Vector2i) -> bool:
	if why_not(lever, c) != "":
		return false
	(plan[ALLOC_KEY[lever]] as Array).append(c)
	_undo.append([lever, c])
	return true


## The lever on a cell, or "".
func lever_at(c: Vector2i) -> String:
	for lv in LEVERS:
		if (plan[ALLOC_KEY[lv]] as Array).has(c):
			return lv
	return ""


## Take the lever off a cell (any time before the sweep).
func remove_at(c: Vector2i) -> bool:
	var lv := lever_at(c)
	if lv == "":
		return false
	(plan[ALLOC_KEY[lv]] as Array).erase(c)
	for i in range(_undo.size()):
		if _undo[i][1] == c:
			_undo.remove_at(i)
			break
	return true


func can_undo() -> bool:
	return not _undo.is_empty()


func undo() -> bool:
	if _undo.is_empty():
		return false
	var last: Array = _undo.back()
	return remove_at(last[1])


## Forecast of every sealed candidate under the current plan. One entry per candidate:
## {touches, outcomes, summary (holding the spoof), state, tier, first, beams, save_cells (the nodes of the line whose
## skip would beat holding), floor_summary / floor_state (the best result any single skip reaches, no node named),
## can_spoof (the kit holds a spoof), saves (the spoof can change the result)}.
func forecast() -> Array:
	var out: Array = []
	var rd := raid_data()
	var can := int(state.kit["spoof"]) > 0
	for k in range((rd["cands"] as Array).size()):
		var cand: Array = rd["cands"][k]
		var so := L5Rules.spoof_options(leg, raid, state, cand, plan)
		var hold: Dictionary = so["hold"]
		var fl: Dictionary = so["floor"]
		var save_cells: Array = []
		if can:
			for o: Dictionary in so["options"]:
				if o["saves"]:
					save_cells.append(o["cell"])
		var hs: L5State = hold["state"]
		var jam_saves: bool = can and bool(so["jam"]["saves"])
		out.append({"cand": k, "shape": shape(k), "touches": hold["touches"], "outcomes": L5Rules.outcomes(state, hold["touches"]),
			"summary": L5Rules.summary(state, hold["touches"]), "state": hs,
			"tier": L5Rules.tier(state, hs, (hold["touches"] as Array).size()),
			"save_cells": save_cells, "jam_saves": jam_saves, "floor_summary": L5Rules.summary(state, fl["touches"]),
			"floor_state": fl["state"], "floor_touches": fl["touches"], "can_spoof": can,
			"saves": not save_cells.is_empty() or jam_saves,
			"first": hold["first"], "beams": hold["beams"]})
	return out


## The worst home loss over the candidates, holding and with the best case a spoof can reach: [hold, with_spoof].
func worst_home_loss() -> Array:
	var a := 0
	var b := 0
	for f: Dictionary in forecast():
		a = maxi(a, int(f["summary"]["home"]))
		b = maxi(b, int(f["floor_summary"]["home"]) if f["can_spoof"] else int(f["summary"]["home"]))
	return [a, b]


## The worst candidate by leg score, counting everything: {down, taken, home, breach, shape} for the line that scores
## lowest, once holding every spoof and once with the best single skip (`with_spoof`). A breach is the worst.
func worst_case(fc: Array = []) -> Dictionary:
	var lines: Array = fc if not fc.is_empty() else forecast()
	var hold: Dictionary = {}
	var hold_s := 1000000
	var best: Dictionary = {}
	var best_s := 1000000
	for f: Dictionary in lines:
		var s: int = L5Rules.score(leg, f["state"])
		if s < hold_s:
			hold_s = s
			hold = (f["summary"] as Dictionary).duplicate()
			hold["shape"] = f["shape"]
		var fs: L5State = f["floor_state"] if f["can_spoof"] else f["state"]
		var s2: int = L5Rules.score(leg, fs)
		if s2 < best_s:
			best_s = s2
			best = (f["floor_summary"] if f["can_spoof"] else f["summary"]).duplicate()
			best["shape"] = f["shape"]
	return {"hold": hold, "with_spoof": best}


## True when every sealed line ends in a breach if the player holds (the forecast already shows BREACH on each line).
func breach_certain(fc: Array = []) -> bool:
	var lines: Array = fc if not fc.is_empty() else forecast()
	for f: Dictionary in lines:
		if not bool(_best_summary(f)["breach"]):
			return false
	return not lines.is_empty()


## True when some sealed line still ends in a breach under the current plan, even with the best spoof.
func breach_possible(fc: Array = []) -> bool:
	var lines: Array = fc if not fc.is_empty() else forecast()
	for f: Dictionary in lines:
		if bool(_best_summary(f)["breach"]):
			return true
	return false


## When every line breaches: the fewest extra levers (kit and per-raid caps respected, at most 4) that leave no line
## breaching, searched in the order ghost, dark, decoy over the cells; [] when the kit has none. Returns
## {steps: [{lever, cell}]} or {}. It never changes the plan (a bounded search: 1200 forecasts).
func breach_fix() -> Dictionary:
	var saved := L5Rules.copy_alloc(plan)
	var found: Array = []
	for max_depth in range(1, 5):
		found = _fix_search(0, -1, 1, max_depth, [1200])
		if not found.is_empty():
			break
	plan = saved
	return {"steps": found} if not found.is_empty() else {}


const FIX_ORDER: Array = ["ghost", "dark", "decoy"]


func _fix_search(lever_i: int, cell_from: int, depth: int, max_depth: int, budget: Array) -> Array:
	var cells := L5Rules.nodes()
	for li in range(lever_i, FIX_ORDER.size()):
		var lever: String = FIX_ORDER[li]
		var start: int = cell_from + 1 if li == lever_i else 0
		for ci in range(start, cells.size()):
			var c: Vector2i = cells[ci]
			if why_not(lever, c) != "":
				continue
			if int(budget[0]) <= 0:
				return []
			budget[0] = int(budget[0]) - 1
			(plan[ALLOC_KEY[lever]] as Array).append(c)
			var res: Array = []
			if not breach_possible():
				res = [{"lever": lever, "cell": c}]
			elif depth < max_depth:
				var deeper := _fix_search(li, ci, depth + 1, max_depth, budget)
				if not deeper.is_empty():
					res = [{"lever": lever, "cell": c}] + deeper
			(plan[ALLOC_KEY[lever]] as Array).erase(c)
			if not res.is_empty():
				return res
	return []


## Assets kept now (sweep_l5.score term): live assets' value, a DOWN one less its repair.
func kept_now() -> int:
	return L5Rules.assets_kept(leg, state)


## Assets kept after the between picks so far (a repaired asset counts whole).
func kept_after_picks() -> int:
	var st := state.copy()
	for c: Vector2i in pending_repairs:
		st.status[c] = "OK"
	return L5Rules.assets_kept(leg, st)


## A fresh playout for the current plan.
func make_play() -> L5Play:
	return L5Play.new(leg, raid, state.copy(), L5Rules.copy_alloc(plan), b2())


## Settle the raid from a finished playout: ledger and campaign numbers. A sweep cut by the breach keeps only the
## touches it showed. Returns the history row.
func settle(play: L5Play) -> Dictionary:
	var res: Dictionary = play.res
	var after: L5State = (res["state"] as L5State).copy()
	var touches: Array = res["touches"]
	if play.cut:
		touches = play.shown_touches()
		after.status = (play.status_now()["status"] as Dictionary).duplicate()
	var beams: Array = res["beams"]
	if play.cut:
		# Only the beams the sweep reached; the last one stops at the touch that emptied HOME.
		var lb := play.last_beam()
		beams = []
		for k in range(lb + 1):
			beams.append((res["beams"] as Array)[k])
		var tail: Dictionary = (beams[lb] as Dictionary).duplicate()
		var n_shown := 0
		for e: Dictionary in play.events:
			if e["beam"] == tail["id"]:
				n_shown += 1
		tail["steps"] = (tail["steps"] as Array).slice(0, n_shown)
		tail["stopped"] = true
		beams[lb] = tail
	var alloc := L5Rules.copy_alloc(plan)
	var used := {"ghost": (alloc["ghost"] as Array).size(), "decoy": (alloc["decoys"] as Array).size(),
		"spoof": 1 if play.spoof_used else 0, "dark": (alloc["dark"] as Array).size()}
	var ledger := {
		"heat_before": state.heat, "ghost": L5Config.GHOST_HEAT * used["ghost"],
		"evade": L5Config.EVADE_HEAT if touches.is_empty() else 0,
		"spoof_heat": L5Config.SPOOF_HEAT if play.spoof_used else 0,
		"spoof_kind": "" if not play.spoof_used else ("JAM" if play.spoof == L5Rules.JAM else "SKIP"), "heat_after": after.heat,
		"home_before": state.home_hp, "home_lost": state.home_hp - after.home_hp, "home_after": after.home_hp,
		"kit_before": state.kit.duplicate(), "kit_used": used, "kit_after": after.kit.duplicate(),
		"bank": state.bank, "run_heat": play.run_heat, "extra": L5Rules.extra_count(play.run_heat),
		"carried": L5Rules.heat_carried(after)}
	var row := {"raid": raid, "before": state.copy(), "alloc": alloc, "spoof": play.spoof, "touches": touches,
		"outcomes": L5Rules.outcomes(state, touches), "summary": L5Rules.summary(state, touches), "after_raid": after,
		"evaded": touches.is_empty(), "tier": L5Rules.tier(state, after, touches.size()),
		"cut": play.cut, "ledger": ledger, "beams": beams, "between": {}, "real": real(), "real_shape": shape(real()), "first": play.hunter_from()}
	history.append(row)
	var nd := {}
	for c: Vector2i in after.status:
		if after.status[c] == "DOWN":
			nd[c] = (int(down_raids.get(c, 0)) + 1) if state.status.get(c, "") == "DOWN" else 1
	down_raids = nd
	state = after
	breached = after.home_hp <= 0
	return row


## True when the ledger's rows add up: Heat before + ghost - evade + spoof = Heat after; home before - lost = home after; kit
## before - used = kit after for ghost, decoy, spoof and dark; the bank does not move in a raid.
static func ledger_reconciles(l: Dictionary, bank_after: int) -> bool:
	for k in L5Config.KITS:
		if int(l["kit_before"][k]) - int(l["kit_used"][k]) != int(l["kit_after"][k]):
			return false
	return int(l["heat_before"]) + int(l["ghost"]) - int(l["evade"]) + int(l["spoof_heat"]) == int(l["heat_after"]) \
		and int(l["home_before"]) - int(l["home_lost"]) == int(l["home_after"]) and int(l["bank"]) == bank_after


## True while the between step is open (a raid settled, the leg goes on).
func between_open() -> bool:
	return not history.is_empty() and history.size() == raid + 1 and not breached and raid < L5Config.RAIDS - 1


## Schematics left after the picks so far (repairs, then the shop buy), before the interval's income.
func budget() -> int:
	var b := state.bank
	for c: Vector2i in pending_repairs:
		b -= L5Rules.idiv(int(values()[c]), L5Config.REPAIR_DIV)
	if pending_buy != "":
		b -= int(L5Config.PRICES[pending_buy])
	return b


## Click a DOWN asset in the between step: pick it for repair or take the pick back. There is one crew
## (L5Config.REPAIR_SLOTS): picking another asset moves the pick. "" or the reason.
func toggle_repair(c: Vector2i) -> String:
	if pending_repairs.has(c):
		pending_repairs.erase(c)
		return ""
	if state.status.get(c, "") != "DOWN":
		return "only a DOWN asset can be repaired"
	var cost := L5Rules.idiv(int(values()[c]), L5Config.REPAIR_DIV)
	var held := 0
	for p: Vector2i in pending_repairs:
		held += L5Rules.idiv(int(values()[p]), L5Config.REPAIR_DIV)
	if cost > budget() + held:
		return "not enough %s now: repair costs %d (repairs are paid before income)" % [L5Config.key_label(), cost]
	while pending_repairs.size() >= L5Config.REPAIR_SLOTS:
		pending_repairs.remove_at(0)
	pending_repairs.append(c)
	return ""


## The next raid's breach risk if the run goes at this intensity with the picks so far: {risk (the fewest sealed lines that
## still breach with the best plan and response, sweep_l5.breach_risk), empty (lines that breach with no lever at all),
## state (the next raid's starting state)}. Cached per state: the search is the heavy part.
func risk_for(intensity: String) -> Dictionary:
	var ns: L5State = between_preview(intensity)["state"]
	var key := "%d|%d|%s|%d|%d|%s" % [seed_id, raid, str(ns.status_list()), ns.heat, ns.home_hp, str(ns.kit)]
	if not _risk_cache.has(key):
		_risk_cache[key] = {"risk": L5Rules.breach_risk(leg, raid + 1, ns),
			"empty": L5Rules.breach_lines(leg, raid + 1, ns, L5Rules.empty_alloc()), "state": ns}
	return _risk_cache[key]


## Pick the one shop buy ("ghost" / "decoy" / "spoof" / "dark") or take it back (same pick again, or "" for none). "" or the reason.
func set_buy(what: String) -> String:
	if what == "":
		pending_buy = ""
		buy_committed = true
		return ""
	if what == pending_buy:
		pending_buy = ""
		buy_committed = false
		return ""
	var price: int = int(L5Config.PRICES[what])
	var spent := budget() + (int(L5Config.PRICES[pending_buy]) if pending_buy != "" else 0)
	if price > spent:
		return "not enough %s now: a %s costs %d (repairs are paid first)" % [L5Config.key_label(), what, price]
	pending_buy = what
	buy_committed = true
	return ""


func set_intensity(what: String) -> void:
	if L5Config.INTENSITIES.has(what):
		pending_intensity = what
		intensity_committed = true


## The between step with the picks so far: {repaired, repair_cost, bought, buy_cost, income, heat_add, state}.
func between_preview(intensity: String = "") -> Dictionary:
	var dark: Array = history.back()["alloc"]["dark"]
	return L5Rules.between_parts(leg, state, dark, pending_repairs, pending_intensity if intensity == "" else intensity, pending_buy)


## Close the between step and go on to the next raid's contact.
func finish_between() -> bool:
	if not between_open():
		return false
	var parts := between_preview()
	var row: Dictionary = history.back()
	row["between"] = {"repaired": parts["repaired"], "repair_cost": parts["repair_cost"], "bought": parts["bought"],
		"buy_cost": parts["buy_cost"], "income": parts["income"], "heat_add": parts["heat_add"],
		"intensity": pending_intensity, "before": state.copy(), "after": parts["state"]}
	run_note = row["between"]
	for rc: Vector2i in parts["repaired"]:
		down_raids.erase(rc)
	state = parts["state"]
	raid += 1
	_reset_between()
	_reset_plan()
	return true


## Leg score (sweep_l5.score) of the network as it stands.
func final_score() -> int:
	return L5Rules.score(leg, state)


## The best case of a forecast line: with a spoof when the kit holds one, else the hold result.
static func _best_summary(f: Dictionary) -> Dictionary:
	return f["floor_summary"] if f["can_spoof"] else f["summary"]
