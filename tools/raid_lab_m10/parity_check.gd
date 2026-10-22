extends SceneTree
## Parity check of the L2 rules against data/l2_golden.json (tools/raid_concepts/l2_golden.py): every step of the
## planned and greedy line of each of the 6 legs, the naive line (data/l2_extra.json), and all 200 random single-raid
## resolutions. Compares touches, status, Heat, bank, home integrity and score. Also the config constants and that every
## golden allocation passes the lab's lever validation. Exits 0 only on full parity.
##   godot --headless --path . -s res://tools/raid_lab_m10/parity_check.gd

var _fails: int = 0
var _checks: int = 0
var _shown: int = 0
var _steps: int = 0


func _check(label: String, got: Variant, want: Variant) -> void:
	_checks += 1
	var ok: bool = JSON.stringify(_norm(got)) == JSON.stringify(_norm(want))
	if not ok:
		_fails += 1
		if _shown < 40:
			_shown += 1
			print("FAIL %s   got %s want %s" % [label, JSON.stringify(got), JSON.stringify(want)])


func _norm(v: Variant) -> Variant:
	if v is float and is_equal_approx(v, round(v)):
		return int(round(v))
	if v is Array:
		var a: Array = []
		for e in v:
			a.append(_norm(e))
		return a
	return v


func _touched(touches: Array) -> Array:
	var out: Array = []
	for t: Dictionary in touches:
		out.append([t["cell"].x, t["cell"].y, t["kind"]])
	return out


func _golden_state(d: Dictionary) -> Array:
	var st := L2State.from_golden(d)
	return st.to_array()


func _cells(arr: Array) -> Array:
	var out: Array = []
	for c: Vector2i in arr:
		out.append([c.x, c.y])
	return out


func _init() -> void:
	var gold := L2Data.load_json(L2Data.GOLDEN_PATH)
	var extra := L2Data.load_json(L2Data.EXTRA_PATH)
	if gold.is_empty() or extra.is_empty():
		print("FAIL golden or extra file missing")
		quit(1)
		return
	var cfg: Dictionary = gold["config"]
	var mine := {"W": L2Config.W, "H": L2Config.H, "ASSETS": L2Config.ASSETS, "CANDIDATES": L2Config.CANDIDATES,
		"HOME_HP": L2Config.HOME_HP, "STRONG_AT": L2Config.STRONG_AT, "START_HEAT": L2Config.START_HEAT,
		"RUN_HEAT": L2Config.RUN_HEAT, "GHOST_HEAT": L2Config.GHOST_HEAT, "DECOY_COST": L2Config.DECOY_COST,
		"EVADE_HEAT": L2Config.EVADE_HEAT, "START_BANK": L2Config.START_BANK, "HOME_LOSS_COST": L2Config.HOME_LOSS_COST,
		"BREACH": L2Config.BREACH, "RAIDS": L2Config.RAIDS}
	for k in cfg:
		_check("config " + k, mine[k], cfg[k])
	_check("config EXTRA_AT", L2Config.EXTRA_AT, extra["extra_at"])
	_check("config legs", L2Config.LEGS, gold["legs"].map(func(l: Dictionary) -> int: return int(l["seed"])))

	var n_lines := 0
	for raw in gold["legs"]:
		var seed_id: int = int(raw["seed"])
		var leg := L2Data.load_leg(seed_id)
		for line_name in ["planned", "greedy", "naive"]:
			_replay("leg %d %s" % [seed_id, line_name], leg, leg[line_name], line_name == "naive")
			n_lines += 1

	var n_random := 0
	for i in range(gold["random_raids"].size()):
		var r: Dictionary = gold["random_raids"][i]
		var leg := L2Data.load_leg(int(r["leg"]))
		var st := L2State.from_golden(r["before"])
		var alloc := L2Data.alloc_of(r["alloc"])
		var b2: Array = leg["raids"][int(r["raid"])]["cands"][int(r["candidate"])]
		var res := L2Rules.resolve(leg, int(r["raid"]), st, b2, alloc, L2Data.spoof_of(r["spoof"]))
		var tag := "random %d (leg %d raid %d cand %d)" % [i, r["leg"], r["raid"], r["candidate"]]
		_check(tag + " touches", _touched(res["touches"]), r["touched"])
		_check(tag + " after", (res["state"] as L2State).to_array(), _golden_state(r["after_raid"]))
		_check(tag + " score", L2Rules.score(leg, res["state"]), r["score"])
		_check_levers(tag, leg, st, alloc)
		n_random += 1
	print("%d lines, %d golden steps, %d random raids, %d checks, %d failed" % [n_lines, _steps, n_random, _checks, _fails])
	print("PARITY %s" % ("PASS" if _fails == 0 else "FAIL"))
	quit(0 if _fails == 0 else 1)


## The lab's lever validation accepts a golden allocation, lever by lever, in ghost, dark, decoy order.
func _check_levers(tag: String, leg: Dictionary, st: L2State, alloc: Dictionary) -> void:
	var acc := L2Rules.empty_alloc()
	var ok := true
	for lever in ["ghost", "dark", "decoys"]:
		for c in alloc[lever]:
			var lv: String = "decoy" if lever == "decoys" else String(lever)
			if L2Rules.why_not(leg, st, acc, lv, c) != "":
				ok = false
			(acc[lever] as Array).append(c)
	_check(tag + " golden allocation passes the lever validation", ok, true)


func _replay(tag: String, leg: Dictionary, steps: Array, is_naive: bool) -> void:
	var st := L2Rules.initial(leg)
	for s: Dictionary in steps:
		var i: int = int(s["raid"])
		var t := "%s raid %d" % [tag, i + 1]
		_steps += 1
		_check(t + " before", st.to_array(), _golden_state(s["before"]))
		var alloc := L2Data.alloc_of(s["alloc"])
		var spoof := L2Data.spoof_of(s["spoof"])
		if is_naive:
			var nd := L2Rules.naive_decide(leg, i, st)
			_check(t + " naive alloc", _cells(nd["alloc"]["ghost"]), s["alloc"]["ghost"])
			_check(t + " naive spoof", [nd["spoof"].x, nd["spoof"].y] if nd["spoof"] != L2Rules.NONE else null, s["spoof"])
		var res := L2Rules.resolve(leg, i, st, leg["raids"][i]["cands"][L2Config.REVEAL], alloc, spoof)
		var ns: L2State = res["state"]
		_check(t + " touches", _touched(res["touches"]), s["touched"])
		_check(t + " after raid", ns.to_array(), _golden_state(s["after_raid"]))
		var repairs := L2Data.cells(s["repairs"])
		if is_naive and ns.home_hp > 0 and i < L2Config.RAIDS - 1:
			_check(t + " naive repairs", _cells(L2Rules.naive_repairs(leg, ns)), s["repairs"])
		var after: L2State = ns
		if i < L2Config.RAIDS - 1 and ns.home_hp > 0:
			after = L2Rules.between(leg, ns, alloc["dark"], repairs)
			var parts := L2Rules.between_parts(leg, ns, alloc["dark"], repairs)
			_check(t + " between parts equal between", (parts["state"] as L2State).to_array(), after.to_array())
		_check(t + " after", after.to_array(), _golden_state(s["after"]))
		_check(t + " score", L2Rules.score(leg, after), s["score_after"])
		st = after
		if ns.home_hp <= 0:
			break
