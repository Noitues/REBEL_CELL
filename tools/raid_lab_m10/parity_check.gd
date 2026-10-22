extends SceneTree
## Parity check: replays every case of data/m10_golden.json (12 networks x 4 plans x 3 candidates, each with no spoof
## and with every spoof) through the GDScript rules and compares the found lists and values. Also checks the rule
## constants against the golden "config" and that the REPAIR "half" toggle leaves the golden value untouched.
## Exits 0 only on full parity.
##   godot --headless --path . -s res://tools/raid_lab_m10/parity_check.gd

var _fails: int = 0
var _checks: int = 0
var _shown: int = 0


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


func _cells(arr: Array) -> Array:
	var out: Array = []
	for c in arr:
		out.append([c.x, c.y])
	return out


func _init() -> void:
	var gold := M10Data.load_json(M10Data.GOLDEN_PATH)
	if gold.is_empty():
		print("FAIL golden file missing: %s" % M10Data.GOLDEN_PATH)
		quit(1)
		return
	var cfg: Dictionary = gold["config"]
	_check("config ghost_heat", M10Config.GHOST_HEAT, cfg["ghost_heat"])
	_check("config heat_value", M10Config.HEAT_VALUE, cfg["heat_value"])
	_check("config decoy_cost", M10Config.DECOY_COST, cfg["decoy_cost"])
	_check("config evade", M10Config.EVADE, cfg["evade"])
	_check("config max_ghost", M10Config.MAX_GHOST, cfg["max_ghost"])
	_check("config max_decoy", M10Config.MAX_DECOY, cfg["max_decoy"])
	_check("config w", M10Config.W, cfg["w"])
	_check("config h", M10Config.H, cfg["h"])
	_check("config nodes", _cells(M10Rules.nodes()), cfg["nodes"])
	var n_sweeps := 0
	for raw in gold["cases"]:
		var cs := M10Data.make_case(raw)
		var assets: Dictionary = cs["assets"]
		for plan_name in raw["plans"]:
			var rp: Dictionary = raw["plans"][plan_name]
			var plan := M10Data.plan_of(rp)
			for ci in range(3):
				var want: Dictionary = rp["per_candidate"][ci]
				var tag := "seed %d %s cand %d" % [cs["seed"], plan_name, ci]
				var res := M10Rules.sweep(assets, cs["b1"], cs["cands"][ci], cs["own3"], plan)
				_check(tag + " found", _cells(res["found"]), want["found"])
				_check(tag + " value", M10Rules.value(assets, res["found"], plan), want["value"])
				_check(tag + " found_of equals sweep", M10Rules.found_of(assets, cs["b1"], cs["cands"][ci], cs["own3"], plan), res["found"])
				n_sweeps += 1
				for sp in want["spoofs"]:
					var spoof: Array = [int(sp["beam"]), M10Data.cell(sp["node"])]
					var r2 := M10Rules.sweep(assets, cs["b1"], cs["cands"][ci], cs["own3"], plan, spoof)
					var t2 := "%s spoof %d@%s" % [tag, sp["beam"], str(sp["node"])]
					_check(t2 + " found", _cells(r2["found"]), sp["found"])
					_check(t2 + " value", M10Rules.value(assets, r2["found"], plan), sp["value"])
					n_sweeps += 1
	# REPAIR toggle: the ledger changes, the rules' value does not.
	var c22 := M10Data.case_by_seed(M10Data.load_cases(), 22)
	var plan22 := M10Data.plan_of(c22["plans"]["none"])
	var f22: Array = M10Rules.found_of(c22["assets"], c22["b1"], c22["cands"][0], c22["own3"], plan22)
	_check("repair value mode = found values", M10Rules.repair(c22["assets"], f22, "value"), 26)
	_check("repair half mode = sum of v // 2", M10Rules.repair(c22["assets"], f22, "half"), 13)
	M10Config.toggles["REPAIR"] = "half"
	_check("value() ignores the REPAIR toggle", M10Rules.value(c22["assets"], f22, plan22), -26)
	M10Config.reset()
	print("%d sweeps, %d checks, %d failed" % [n_sweeps, _checks, _fails])
	print("PARITY %s" % ("PASS" if _fails == 0 else "FAIL"))
	quit(0 if _fails == 0 else 1)
