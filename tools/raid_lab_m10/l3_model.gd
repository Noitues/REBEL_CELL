class_name L3Model
extends RefCounted
## Lab state of one leg of 3 raids on ONE network: the leg kit, the player's plan, undo, the campaign numbers, the
## settled raids and the between-raids step (repairs, one shop buy, run intensity). The rules are all in L3Rules.

const LEVERS: Array = ["ghost", "decoy", "dark"]
const ALLOC_KEY := {"ghost": "ghost", "decoy": "decoys", "dark": "dark"}

var leg: Dictionary = {}
var seed_id: int = 0
var raid: int = 0
## The network, kit and campaign numbers at contact (before the plan charges anything).
var state: L3State
var plan: Dictionary = L3Rules.empty_alloc()
var _undo: Array = []
## Settled raids: {raid, before, alloc, spoof, touches, outcomes, summary, after_raid, evaded, tier, cut, ledger,
## beams, between (set when the between step is done)}.
var history: Array = []
var breached: bool = false
## The between step's picks: repairs in click order, one shop buy ("" = none), the run intensity.
var pending_repairs: Array = []
var pending_buy: String = ""
var pending_intensity: String = "NORMAL"
## The last between step: {repaired, repair_cost, bought, buy_cost, income, heat_add, intensity, before, after};
## empty on raid 1.
var run_note: Dictionary = {}


func _init(p_seed: int = 0) -> void:
	new_leg(p_seed)


func new_leg(p_seed: int) -> void:
	seed_id = p_seed
	leg = L3Data.load_leg(p_seed)
	raid = 0
	state = L3Rules.initial(leg)
	history = []
	breached = false
	_reset_between()
	run_note = {}
	_reset_plan()


func _reset_plan() -> void:
	plan = L3Rules.empty_alloc()
	_undo = []


func _reset_between() -> void:
	pending_repairs = []
	pending_buy = ""
	pending_intensity = "NORMAL"


func raid_data() -> Dictionary:
	return leg["raids"][raid]


func b2() -> Array:
	return raid_data()["cands"][L3Config.REVEAL]


func home() -> Vector2i:
	return leg["home"]


func values() -> Dictionary:
	return leg["values"]


func leg_over() -> bool:
	return breached or history.size() >= L3Config.RAIDS


## Heat shown on the meter: the ghost already raised it.
func heat_now() -> int:
	return state.heat + L3Config.GHOST_HEAT * (plan["ghost"] as Array).size()


## Extra known beams the raid will run with at the current plan.
func extra_now() -> int:
	return L3Rules.extra_count(heat_now())


## The kit left if the plan goes ahead (a spoof is spent only if used after the reveal, so it stays whole here).
func kit_left() -> Dictionary:
	return {"ghost": int(state.kit["ghost"]) - (plan["ghost"] as Array).size(),
		"decoy": int(state.kit["decoy"]) - (plan["decoys"] as Array).size(), "spoof": int(state.kit["spoof"])}


func why_not(lever: String, c: Vector2i) -> String:
	return L3Rules.why_not(leg, state, plan, lever, c)


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
	for cand: Array in rd["cands"]:
		var so := L3Rules.spoof_options(leg, raid, state, cand, plan)
		var hold: Dictionary = so["hold"]
		var fl: Dictionary = so["floor"]
		var save_cells: Array = []
		if can:
			for o: Dictionary in so["options"]:
				if o["saves"]:
					save_cells.append(o["cell"])
		var hs: L3State = hold["state"]
		out.append({"touches": hold["touches"], "outcomes": L3Rules.outcomes(state, hold["touches"]),
			"summary": L3Rules.summary(state, hold["touches"]), "state": hs,
			"tier": L3Rules.tier(state.home_hp, hs.home_hp, (hold["touches"] as Array).size()),
			"save_cells": save_cells, "floor_summary": L3Rules.summary(state, fl["touches"]),
			"floor_state": fl["state"], "can_spoof": can, "saves": not save_cells.is_empty(),
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


## A fresh playout for the current plan.
func make_play() -> L3Play:
	return L3Play.new(leg, raid, state.copy(), L3Rules.copy_alloc(plan), b2())


## Settle the raid from a finished playout: ledger and campaign numbers. A sweep cut by the breach keeps only the
## touches it showed. Returns the history row.
func settle(play: L3Play) -> Dictionary:
	var res: Dictionary = play.res
	var after: L3State = (res["state"] as L3State).copy()
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
	var alloc := L3Rules.copy_alloc(plan)
	var used := {"ghost": (alloc["ghost"] as Array).size(), "decoy": (alloc["decoys"] as Array).size(),
		"spoof": 1 if play.spoof_used else 0}
	var ledger := {
		"heat_before": state.heat, "ghost": L3Config.GHOST_HEAT * used["ghost"],
		"evade": L3Config.EVADE_HEAT if touches.is_empty() else 0, "heat_after": after.heat,
		"home_before": state.home_hp, "home_lost": state.home_hp - after.home_hp, "home_after": after.home_hp,
		"kit_before": state.kit.duplicate(), "kit_used": used, "kit_after": after.kit.duplicate(),
		"bank": state.bank, "run_heat": play.run_heat, "extra": L3Rules.extra_count(play.run_heat),
		"carried": L3Rules.heat_carried(after)}
	var row := {"raid": raid, "before": state.copy(), "alloc": alloc, "spoof": play.spoof, "touches": touches,
		"outcomes": L3Rules.outcomes(state, touches), "summary": L3Rules.summary(state, touches), "after_raid": after,
		"evaded": touches.is_empty(), "tier": L3Rules.tier(state.home_hp, after.home_hp, touches.size()),
		"cut": play.cut, "ledger": ledger, "beams": beams, "between": {}}
	history.append(row)
	state = after
	breached = after.home_hp <= 0
	return row


## True when the ledger's rows add up: Heat before + ghost - evade = Heat after; home before - lost = home after; kit
## before - used = kit after for ghost, decoy and spoof; the bank does not move in a raid.
static func ledger_reconciles(l: Dictionary, bank_after: int) -> bool:
	for k in L3Config.KITS:
		if int(l["kit_before"][k]) - int(l["kit_used"][k]) != int(l["kit_after"][k]):
			return false
	return int(l["heat_before"]) + int(l["ghost"]) - int(l["evade"]) == int(l["heat_after"]) \
		and int(l["home_before"]) - int(l["home_lost"]) == int(l["home_after"]) and int(l["bank"]) == bank_after


## True while the between step is open (a raid settled, the leg goes on).
func between_open() -> bool:
	return not history.is_empty() and history.size() == raid + 1 and not breached and raid < L3Config.RAIDS - 1


## Schematics left after the picks so far (repairs, then the shop buy), before the interval's income.
func budget() -> int:
	var b := state.bank
	for c: Vector2i in pending_repairs:
		b -= L3Rules.idiv(int(values()[c]), L3Config.REPAIR_DIV)
	if pending_buy != "":
		b -= int(L3Config.PRICES[pending_buy])
	return b


## Click a DOWN asset in the between step: pick it for repair or take the pick back. "" or the reason.
func toggle_repair(c: Vector2i) -> String:
	if pending_repairs.has(c):
		pending_repairs.erase(c)
		return ""
	if state.status.get(c, "") != "DOWN":
		return "only a DOWN asset can be repaired"
	var cost := L3Rules.idiv(int(values()[c]), L3Config.REPAIR_DIV)
	if cost > budget():
		return "not enough %s now: repair costs %d (repairs are paid before income)" % [L3Config.key_label(), cost]
	pending_repairs.append(c)
	return ""


## Pick the one shop buy ("ghost" / "decoy" / "spoof") or take it back (same pick again, or "" for none). "" or the reason.
func set_buy(what: String) -> String:
	if what == "" or what == pending_buy:
		pending_buy = ""
		return ""
	var price: int = int(L3Config.PRICES[what])
	var spent := budget() + (int(L3Config.PRICES[pending_buy]) if pending_buy != "" else 0)
	if price > spent:
		return "not enough %s now: a %s costs %d (repairs are paid first)" % [L3Config.key_label(), what, price]
	pending_buy = what
	return ""


func set_intensity(what: String) -> void:
	if L3Config.INTENSITIES.has(what):
		pending_intensity = what


## The between step with the picks so far: {repaired, repair_cost, bought, buy_cost, income, heat_add, state}.
func between_preview(intensity: String = "") -> Dictionary:
	var dark: Array = history.back()["alloc"]["dark"]
	return L3Rules.between_parts(leg, state, dark, pending_repairs, pending_intensity if intensity == "" else intensity, pending_buy)


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
	state = parts["state"]
	raid += 1
	_reset_between()
	_reset_plan()
	return true


## Leg score (sweep_l3.score) of the network as it stands.
func final_score() -> int:
	return L3Rules.score(leg, state)
