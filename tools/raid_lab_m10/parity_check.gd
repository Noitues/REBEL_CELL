extends SceneTree
## Parity check of the L5 rules against data/l5_golden.json (tools/raid_concepts/l5_golden.py): every step of the
## planned, greedy and naive line of each of the 6 legs (state before incl. kit, touches, tier, state after the raid, the
## between step with repairs / intensity / buy, state after, score), all 200 random single-raid resolutions and all 200
## random between steps. Also the config constants, that the lab's lever validation accepts every golden allocation and
## that the lab's naive policy reproduces the naive line. Exits 0 only on full parity.
##   godot --headless --path . -s res://tools/raid_lab_m10/parity_check.gd

var _fails: int = 0
var _checks: int = 0
var _shown: int = 0
var _steps: int = 0
var _risks: int = 0
var _jams: int = 0
## The shape of the real line in every golden raid (it must not be one shape throughout: no tell).
var _real_shape_seen: Array = []


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
	if v is Dictionary:
		var keys: Array = (v as Dictionary).keys()
		keys.sort()
		var d: Dictionary = {}
		for k in keys:
			d[k] = _norm(v[k])
		return d
	return v


func _touched(touches: Array) -> Array:
	var out: Array = []
	for t: Dictionary in touches:
		out.append([t["cell"].x, t["cell"].y, t["kind"]])
	return out


func _golden_state(d: Dictionary) -> Array:
	return L5State.from_golden(d).to_array()


func _cells(arr: Array) -> Array:
	var out: Array = []
	for c: Vector2i in arr:
		out.append([c.x, c.y])
	return out


func _init() -> void:
	var gold := L5Data.load_json(L5Data.GOLDEN_PATH)
	if gold.is_empty():
		print("FAIL golden file missing")
		quit(1)
		return
	_config(gold["config"])
	_check("config legs", L5Config.LEGS, gold["legs"].map(func(l: Dictionary) -> int: return int(l["seed"])))

	var n_lines := 0
	for raw in gold["legs"]:
		var seed_id: int = int(raw["seed"])
		var leg := L5Data.load_leg(seed_id)
		_check_real_shapes(seed_id, leg, raw["leg"])
		for line_name in ["planned", "greedy", "naive"]:
			_replay("leg %d %s" % [seed_id, line_name], leg, leg[line_name], line_name == "naive")
			n_lines += 1

	var distinct_real_shapes: Array = []
	for s in _real_shape_seen:
		if not distinct_real_shapes.has(s):
			distinct_real_shapes.append(s)
	_check("the real line wears more than one shape across the golden raids", distinct_real_shapes.size() > 1, true)
	var n_random := 0
	for i in range(gold["random_raids"].size()):
		var r: Dictionary = gold["random_raids"][i]
		var leg := L5Data.load_leg(int(r["leg"]))
		var st := L5State.from_golden(r["before"])
		var alloc := L5Data.alloc_of(r["alloc"])
		var b2: Array = leg["raids"][int(r["raid"])]["cands"][int(r["candidate"])]
		if r["spoof"] is String:
			_jams += 1
		var res := L5Rules.resolve(leg, int(r["raid"]), st, b2, alloc, L5Data.spoof_of(r["spoof"]))
		var ns: L5State = res["state"]
		var tag := "random raid %d (leg %d raid %d cand %d)" % [i, r["leg"], r["raid"], r["candidate"]]
		_check(tag + " touches", _touched(res["touches"]), r["touched"])
		_check(tag + " tier", L5Rules.tier(st, ns, (res["touches"] as Array).size()), r["tier"])
		_check(tag + " after", ns.to_array(), _golden_state(r["after_raid"]))
		_check(tag + " score", L5Rules.score(leg, ns), r["score"])
		_check_levers(tag, leg, st, alloc)
		n_random += 1
	var n_between := 0
	for i in range(gold["random_betweens"].size()):
		var r: Dictionary = gold["random_betweens"][i]
		var leg := L5Data.load_leg(int(r["leg"]))
		var st := L5State.from_golden(r["before"])
		var dark := L5Data.cells(r["dark"])
		var repairs := L5Data.cells(r["repairs"])
		var buy: String = "" if r["buy"] == null else String(r["buy"])
		var tag := "random between %d (leg %d)" % [i, r["leg"]]
		var parts := L5Rules.between_parts(leg, st, dark, repairs, String(r["intensity"]), buy)
		_check(tag + " after", (parts["state"] as L5State).to_array(), _golden_state(r["after"]))
		_check(tag + " between() = parts", L5Rules.between(leg, st, dark, repairs, String(r["intensity"]), buy).to_array(), _golden_state(r["after"]))
		var ns: L5State = parts["state"]
		_check(tag + " ledger: bank before - repairs - buy + income = bank after",
			st.bank - int(parts["repair_cost"]) - int(parts["buy_cost"]) + int(parts["income"]), ns.bank)
		if r.has("risk"):
			_check(tag + " breach risk of raid %d" % int(r["risk_raid"]), L5Rules.breach_risk(leg, int(r["risk_raid"]), ns), r["risk"])
			_risks += 1
		n_between += 1
	print("real-line shapes seen across %d golden raids: %s" % [_real_shape_seen.size(), str(distinct_real_shapes)])
	print("%d lines, %d golden steps, %d random raids (%d with JAM), %d random betweens, %d breach_risk values, %d checks, %d failed" % [n_lines, _steps, n_random, _jams, n_between, _risks, _checks, _fails])
	print("PARITY %s" % ("PASS" if _fails == 0 else "FAIL"))
	quit(0 if _fails == 0 else 1)


## real and shapes: loaded as the golden has them; real is a candidate index, shapes a permutation of the three shapes;
## the lab's own helpers (real_cand, shape_of, cand_of_shape) read them back.
func _check_real_shapes(seed_id: int, leg: Dictionary, raw_leg: Dictionary) -> void:
	for i in range((raw_leg["raids"] as Array).size()):
		var g: Dictionary = raw_leg["raids"][i]
		var tag := "leg %d raid %d" % [seed_id, i + 1]
		_check(tag + " real", L5Rules.real_cand(leg, i), int(g["real"]))
		_check(tag + " real is a candidate", int(g["real"]) >= 0 and int(g["real"]) < L5Config.CANDIDATES, true)
		var shapes: Array = []
		for k in range(L5Config.CANDIDATES):
			shapes.append(L5Rules.shape_of(leg, i, k))
		_check(tag + " shapes", shapes, g["shapes"])
		var sorted_shapes := shapes.duplicate()
		sorted_shapes.sort()
		_check(tag + " shapes are a permutation", sorted_shapes, [0, 1, 2])
		for s in range(3):
			_check(tag + " cand_of_shape %d" % s, shapes[L5Rules.cand_of_shape(leg, i, s)], s)
		_real_shape_seen.append(shapes[int(g["real"])])
		# L5: the three sealed lines are distinct and each hits a different, non-empty set of asset / HOME cells.
		var hit_sets: Array = []
		for ln: Array in leg["raids"][i]["cands"]:
			var hs: Array = []
			for c: Vector2i in ln:
				if (leg["values"] as Dictionary).has(c) or c == leg["home"]:
					hs.append(c)
			hs.sort()
			hit_sets.append(JSON.stringify(hs))
		_check(tag + " sealed lines hit non-empty sets", hit_sets.has("[]"), false)
		_check(tag + " sealed lines hit different sets", hit_sets[0] != hit_sets[1] and hit_sets[0] != hit_sets[2] and hit_sets[1] != hit_sets[2], true)


func _config(cfg: Dictionary) -> void:
	var mine := {"W": L5Config.W, "H": L5Config.H, "ASSETS": L5Config.ASSETS, "CANDIDATES": L5Config.CANDIDATES,
		"HOME_HP": L5Config.HOME_HP, "EXTRA_AT": L5Config.EXTRA_AT, "STRONG_AT": L5Config.STRONG_AT,
		"MAX_DARK": L5Config.MAX_DARK, "START_HEAT": L5Config.START_HEAT, "GHOST_HEAT": L5Config.GHOST_HEAT,
		"EVADE_HEAT": L5Config.EVADE_HEAT, "START_BANK": L5Config.START_BANK, "HOME_LOSS_COST": L5Config.HOME_LOSS_COST,
		"BREACH": L5Config.BREACH, "RAIDS": L5Config.RAIDS, "KIT_START": L5Config.KIT_START, "PRICES": L5Config.PRICES,
		"MAX_DECOYS": L5Config.MAX_DECOY, "HEAT_CARRY": L5Config.HEAT_CARRY, "SPOOF_HEAT": L5Config.SPOOF_HEAT,
		"REPAIR_SLOTS": L5Config.REPAIR_SLOTS}
	_check("config JAM is read as the lab's JAM spoof", L5Data.spoof_of(cfg["JAM"]), L5Rules.JAM)
	for k in mine:
		_check("config " + k, mine[k], cfg[k])
	for k in cfg:
		if not (mine.has(k) or k in ["INTENSITY", "income", "tiers", "decoys", "dark", "tiers_l4", "JAM", "spoof", "breach_risk"]):
			_check("config " + k + " is covered by the lab", false, true)
	for name in L5Config.INTENSITIES:
		var g: Array = cfg["INTENSITY"][name]
		_check("config INTENSITY %s Heat" % name, L5Config.INTENSITY_HEAT[name], g[0])
		_check("config INTENSITY %s income multiplier" % name, float(L5Config.INTENSITY_NUM[name]) / float(L5Config.INTENSITY_DEN), float(g[1]))
	_check("config INTENSITY names", L5Config.INTENSITIES.size(), (cfg["INTENSITY"] as Dictionary).size())


## The lab's lever validation accepts a golden allocation, lever by lever, in ghost, dark, decoy order.
func _check_levers(tag: String, leg: Dictionary, st: L5State, alloc: Dictionary) -> void:
	var acc := L5Rules.empty_alloc()
	var ok := true
	for lever in ["ghost", "dark", "decoys"]:
		for c in alloc[lever]:
			var lv: String = "decoy" if lever == "decoys" else String(lever)
			if L5Rules.why_not(leg, st, acc, lv, c) != "":
				ok = false
			(acc[lever] as Array).append(c)
	_check(tag + " golden allocation passes the lever validation", ok, true)


func _replay(tag: String, leg: Dictionary, steps: Array, is_naive: bool) -> void:
	var st := L5Rules.initial(leg)
	for s: Dictionary in steps:
		var i: int = int(s["raid"])
		var t := "%s raid %d" % [tag, i + 1]
		_steps += 1
		_check(t + " before", st.to_array(), _golden_state(s["before"]))
		var alloc := L5Data.alloc_of(s["alloc"])
		var spoof := L5Data.spoof_of(s["spoof"])
		if is_naive:
			var nd := L5Rules.naive_decide(leg, i, st)
			_check(t + " naive ghost", _cells(nd["alloc"]["ghost"]), s["alloc"]["ghost"])
			_check(t + " naive spoof", [nd["spoof"].x, nd["spoof"].y] if nd["spoof"] != L5Rules.NONE else null, s["spoof"])
		_check_levers(t, leg, st, alloc)
		var res := L5Rules.resolve(leg, i, st, leg["raids"][i]["cands"][L5Rules.real_cand(leg, i)], alloc, spoof)
		var ns: L5State = res["state"]
		_check(t + " touches", _touched(res["touches"]), s["touched"])
		_check(t + " tier", L5Rules.tier(st, ns, (res["touches"] as Array).size()), s["tier"])
		_check(t + " after raid", ns.to_array(), _golden_state(s["after_raid"]))
		var after: L5State = ns
		if s["between"] == null:
			_check(t + " no between step after a breach or the last raid", ns.home_hp <= 0 or i == L5Config.RAIDS - 1, true)
		else:
			var b: Dictionary = s["between"]
			var repairs := L5Data.cells(b["repairs"])
			var buy: String = "" if b["buy"] == null else String(b["buy"])
			if is_naive:
				_check(t + " naive repairs", _cells(L5Rules.naive_repairs(leg, ns)), b["repairs"])
				_check(t + " naive intensity and buy", [b["intensity"], buy], ["NORMAL", ""])
			var parts := L5Rules.between_parts(leg, ns, alloc["dark"], repairs, String(b["intensity"]), buy)
			after = parts["state"]
			_check(t + " between = between_parts", L5Rules.between(leg, ns, alloc["dark"], repairs, String(b["intensity"]), buy).to_array(), after.to_array())
			for inten: String in L5Config.INTENSITIES:
				var nxt := L5Rules.between(leg, ns, alloc["dark"], repairs, inten, buy)
				_check(t + " risk " + inten, L5Rules.breach_risk(leg, i + 1, nxt), b["risk"][inten])
				_risks += 1
		_check(t + " after", after.to_array(), _golden_state(s["after"]))
		_check(t + " score", L5Rules.score(leg, after), s["score_after"])
		st = after
		if ns.home_hp <= 0:
			break
