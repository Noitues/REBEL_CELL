class_name L2Model
extends RefCounted
## Lab state of one leg of 3 raids on ONE network: the player's plan, undo, the campaign numbers, the settled raids and
## the between-raids repair step. The rules are all in L2Rules.

const LEVERS: Array = ["ghost", "decoy", "dark"]
const ALLOC_KEY := {"ghost": "ghost", "decoy": "decoys", "dark": "dark"}

var leg: Dictionary = {}
var seed_id: int = 0
var raid: int = 0
## The network and campaign numbers at contact (before the plan charges anything).
var state: L2State
var plan: Dictionary = L2Rules.empty_alloc()
var _undo: Array = []
## Settled raids: {raid, before, alloc, spoof, touches, outcomes, summary, after_raid, evaded, forecast_summary,
## ledger, between (set when the repair step is done)}.
var history: Array = []
var breached: bool = false
## Repairs picked in the between step, in click order.
var pending_repairs: Array = []
## The last between step: {repaired, repair_cost, income, heat, state}; empty on raid 1.
var run_note: Dictionary = {}


func _init(p_seed: int = 0) -> void:
	new_leg(p_seed)


func new_leg(p_seed: int) -> void:
	seed_id = p_seed
	leg = L2Data.load_leg(p_seed)
	raid = 0
	state = L2Rules.initial(leg)
	history = []
	breached = false
	pending_repairs = []
	run_note = {}
	_reset_plan()


func _reset_plan() -> void:
	plan = L2Rules.empty_alloc()
	_undo = []


func raid_data() -> Dictionary:
	return leg["raids"][raid]


func b2() -> Array:
	return raid_data()["cands"][L2Config.REVEAL]


func home() -> Vector2i:
	return leg["home"]


func values() -> Dictionary:
	return leg["values"]


func leg_over() -> bool:
	return breached or history.size() >= L2Config.RAIDS


## Heat shown on the meter: the ghost already raised it.
func heat_now() -> int:
	return state.heat + L2Config.GHOST_HEAT * (plan["ghost"] as Array).size()


## Bank shown: the decoy already cost it.
func bank_now() -> int:
	return state.bank - L2Config.DECOY_COST * (plan["decoys"] as Array).size()


## Extra known beams the raid will run with at the current plan.
func extra_now() -> int:
	return L2Rules.extra_count(heat_now())


func why_not(lever: String, c: Vector2i) -> String:
	return L2Rules.why_not(leg, state, plan, lever, c)


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


## Forecast of every sealed candidate under the current plan, including the held spoof. One entry per candidate:
## {touches, outcomes, summary (no spoof), best_spoof (cell or NONE), best_touches, best_summary (with that spoof),
## saves (the spoof changes the result)}.
func forecast() -> Array:
	var out: Array = []
	var rd := raid_data()
	for cand: Array in rd["cands"]:
		var plain := L2Rules.resolve(leg, raid, state, cand, plan, L2Rules.NONE)
		var best := L2Rules.best_spoof(leg, raid, state, cand, plan)
		var bres: Dictionary = best["res"]
		out.append({"touches": plain["touches"], "outcomes": L2Rules.outcomes(state, plain["touches"]),
			"summary": L2Rules.summary(state, plain["touches"]), "state": plain["state"],
			"best_spoof": best["spoof"], "best_touches": bres["touches"],
			"best_summary": L2Rules.summary(state, bres["touches"]), "best_state": bres["state"],
			"saves": best["spoof"] != L2Rules.NONE,
			"first": plain["first"], "beams": plain["beams"]})
	return out


## The worst home loss over the candidates, without and with the best spoof: [no_spoof, with_spoof].
func worst_home_loss() -> Array:
	var a := 0
	var b := 0
	for f: Dictionary in forecast():
		a = maxi(a, int(f["summary"]["home"]))
		b = maxi(b, int(f["best_summary"]["home"]))
	return [a, b]


## A fresh playout for the current plan.
func make_play() -> L2Play:
	return L2Play.new(leg, raid, state.copy(), L2Rules.copy_alloc(plan), b2())


## Settle the raid from a finished playout: ledger and campaign numbers. Returns the history row.
func settle(play: L2Play) -> Dictionary:
	var res: Dictionary = play.res
	var after: L2State = res["state"]
	var touches: Array = res["touches"]
	var alloc := L2Rules.copy_alloc(plan)
	var ledger := {
		"bank_before": state.bank, "decoy": L2Config.DECOY_COST * (alloc["decoys"] as Array).size(), "bank_after": after.bank,
		"heat_before": state.heat, "ghost": L2Config.GHOST_HEAT * (alloc["ghost"] as Array).size(),
		"evade": L2Config.EVADE_HEAT if touches.is_empty() else 0, "heat_after": after.heat,
		"home_before": state.home_hp, "home_lost": state.home_hp - after.home_hp, "home_after": after.home_hp,
		"run_heat": play.run_heat, "extra": L2Rules.extra_count(play.run_heat)}
	var row := {"raid": raid, "before": state.copy(), "alloc": alloc, "spoof": play.spoof, "touches": touches,
		"outcomes": L2Rules.outcomes(state, touches), "summary": L2Rules.summary(state, touches), "after_raid": after,
		"evaded": touches.is_empty(), "ledger": ledger, "beams": res["beams"], "between": {}}
	history.append(row)
	state = after
	breached = after.home_hp <= 0
	return row


## True when the ledger's rows add up: bank before - decoy = bank after; Heat before + ghost - evade = Heat after;
## home before - lost = home after.
static func ledger_reconciles(l: Dictionary) -> bool:
	return int(l["bank_before"]) - int(l["decoy"]) == int(l["bank_after"]) \
		and int(l["heat_before"]) + int(l["ghost"]) - int(l["evade"]) == int(l["heat_after"]) \
		and int(l["home_before"]) - int(l["home_lost"]) == int(l["home_after"])


## True while the between step is open (a raid settled, the leg goes on).
func between_open() -> bool:
	return not history.is_empty() and history.size() == raid + 1 and not breached and raid < L2Config.RAIDS - 1


## Click a DOWN asset in the between step: pick it for repair or take the pick back. "" or the reason.
func toggle_repair(c: Vector2i) -> String:
	if pending_repairs.has(c):
		pending_repairs.erase(c)
		return ""
	if state.status.get(c, "") != "DOWN":
		return "only a DOWN asset can be repaired"
	var cost := L2Rules.idiv(int(values()[c]), L2Config.REPAIR_DIV)
	if cost > repair_budget():
		return "not enough Schematics: repair costs %d" % cost
	pending_repairs.append(c)
	return ""


## Bank left after the picks so far.
func repair_budget() -> int:
	var b := state.bank
	for c: Vector2i in pending_repairs:
		b -= L2Rules.idiv(int(values()[c]), L2Config.REPAIR_DIV)
	return b


## The between step with the picks so far: {repaired, repair_cost, income, state}.
func between_preview() -> Dictionary:
	var dark: Array = history.back()["alloc"]["dark"]
	return L2Rules.between_parts(leg, state, dark, pending_repairs)


## Close the between step and go on to the next raid's contact.
func finish_between() -> bool:
	if not between_open():
		return false
	var parts := between_preview()
	var row: Dictionary = history.back()
	row["between"] = {"repaired": parts["repaired"], "repair_cost": parts["repair_cost"], "income": parts["income"],
		"before": state.copy(), "after": parts["state"]}
	run_note = row["between"]
	state = parts["state"]
	raid += 1
	pending_repairs = []
	_reset_plan()
	return true


## Leg score (sweep_l2.score) of the network as it stands.
func final_score() -> int:
	return L2Rules.score(leg, state)
