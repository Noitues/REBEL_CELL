class_name M10Model
extends RefCounted
## Lab state of one leg of 3 raids on golden networks (M10Config.LEG_SEEDS). The player's plan, undo, the campaign
## numbers (key, Heat) and the settled raids live here; the rules are all in M10Rules.

const LEVERS: Array = ["ghost", "decoy", "dark"]

var cases: Array = []
var raid: int = 0
var case_: Dictionary = {}
var assets: Dictionary = {}
var b1: Array = []
var cands: Array = []
var own3: Array = []
var reveal: int = 0
## Campaign numbers at contact (before the plan charges anything).
var key: int = M10Config.KEY_START
var heat: int = M10Config.HEAT_START
var plan: Dictionary = M10Rules.empty_plan()
var _undo: Array = []
## Settled raids: {seed, plan, spoof, found, ledger, forecast, run}.
var history: Array = []
## What the run before this contact did: {heat, key, dark_loss}; empty on raid 1.
var run_note: Dictionary = {}


func _init() -> void:
	cases = M10Data.load_cases()
	new_leg()


func new_leg() -> void:
	raid = 0
	key = M10Config.KEY_START
	heat = M10Config.HEAT_START
	history = []
	run_note = {}
	_load_raid()


func _load_raid() -> void:
	case_ = M10Data.case_by_seed(cases, int(M10Config.LEG_SEEDS[raid]))
	assets = case_["assets"]
	b1 = case_["b1"]
	cands = case_["cands"]
	own3 = case_["own3"]
	reveal = M10Config.LEG_REVEAL
	plan = M10Rules.empty_plan()
	_undo = []


func seed_id() -> int:
	return int(case_["seed"])


func leg_over() -> bool:
	return history.size() >= M10Config.LEG_SEEDS.size()


## Key shown on the bar: the decoys already cost it.
func key_now() -> int:
	return key - M10Rules.plan_key_cost(plan)


## Heat shown on the meter: the ghosts already raised it.
func heat_now() -> int:
	return mini(heat + M10Rules.plan_heat(plan), M10Config.HEAT_MAX)


## "" if the lever may go on the cell, else the reason.
func why_not(lever: String, c: Vector2i) -> String:
	if not (c.x >= 0 and c.x < M10Config.W and c.y >= 0 and c.y < M10Config.H):
		return "off the grid"
	var taken: bool = plan["ghost"].has(c) or plan["dark"].has(c) or plan["decoys"].has(c)
	if taken:
		return "that node already has a lever"
	match lever:
		"ghost":
			if not assets.has(c):
				return "a ghost hides an asset node"
			if (plan["ghost"] as Array).size() >= M10Config.MAX_GHOST:
				return "only %d ghost" % M10Config.MAX_GHOST
		"decoy":
			if assets.has(c):
				return "a decoy goes on an empty node"
			if (plan["decoys"] as Array).size() >= M10Config.MAX_DECOY:
				return "only %d decoy" % M10Config.MAX_DECOY
			if key_now() < M10Config.DECOY_COST:
				return "not enough key for a decoy"
		"dark":
			if not assets.has(c):
				return "go dark on an asset node"
			if (plan["dark"] as Array).size() >= M10Config.MAX_DARK:
				return "at most %d dark" % M10Config.MAX_DARK
	return ""


func place(lever: String, c: Vector2i) -> bool:
	if why_not(lever, c) != "":
		return false
	var key_name: String = {"ghost": "ghost", "decoy": "decoys", "dark": "dark"}[lever]
	(plan[key_name] as Array).append(c)
	_undo.append([lever, c])
	return true


## The lever on a cell, or "".
func lever_at(c: Vector2i) -> String:
	if plan["ghost"].has(c):
		return "ghost"
	if plan["decoys"].has(c):
		return "decoy"
	if plan["dark"].has(c):
		return "dark"
	return ""


## Take the lever off a cell (any time before the sweep).
func remove_at(c: Vector2i) -> bool:
	var lv := lever_at(c)
	if lv == "":
		return false
	var key_name: String = {"ghost": "ghost", "decoy": "decoys", "dark": "dark"}[lv]
	(plan[key_name] as Array).erase(c)
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


## Forecast of every candidate under the current plan: [{found, repair}] in candidate order.
func forecast_all() -> Array:
	var out: Array = []
	for cd in cands:
		out.append(M10Rules.forecast(assets, b1, cd, own3, plan))
	return out


func loss_range() -> Array:
	return M10Rules.loss_range(assets, b1, cands, own3, plan)


## A fresh playout for the current plan.
func make_play() -> M10Play:
	return M10Play.new(assets, b1, cands, reveal, own3, plan)


## Settle the raid from a finished playout: ledger, campaign numbers. Returns the history row.
func settle(play: M10Play) -> Dictionary:
	var found: Array = play.final["found"]
	var l := M10Rules.ledger(assets, plan, found, key, heat)
	var fc := M10Rules.forecast(assets, b1, cands[reveal], own3, plan)
	var row := {"seed": seed_id(), "plan": plan.duplicate(true), "spoof": spoof_of(play), "found": found, "ledger": l,
		"forecast_found": fc["found"], "forecast_repair": fc["repair"], "evaded": found.is_empty()}
	history.append(row)
	key = int(l["key_after"])
	heat = int(l["heat_after"])
	return row


func spoof_of(play: M10Play) -> Array:
	if play.spoof_used and play.press_hit:
		return [1, play.spoof_cell]
	return []


## Go on to the next raid: the run between them adds Heat and key (less the dark nodes' lost income).
func next_raid() -> bool:
	if leg_over():
		return false
	var dark_loss: int = int(history.back()["ledger"]["dark_loss"])
	var new_heat: int = mini(heat + M10Config.RUN_HEAT, M10Config.HEAT_MAX)
	var new_key: int = clampi(key + M10Config.RUN_KEY - dark_loss, 0, M10Config.KEY_MAX)
	run_note = {"heat": new_heat - heat, "key": new_key - key, "dark_loss": dark_loss, "gain": M10Config.RUN_KEY}
	heat = new_heat
	key = new_key
	raid += 1
	_load_raid()
	return true
