extends SceneTree
## Parity check: replays both leg-0 lines of tools/raid_concepts/h7_golden.json through the GDScript port
## and compares every field. Prints PASS/FAIL per field; exits 0 only on full parity.
##   godot --headless --path . -s res://tools/raid_lab_h7/parity_check.gd

var _fails: int = 0
var _checks: int = 0


func _check(label: String, got: Variant, want: Variant) -> void:
	_checks += 1
	got = _norm(got)
	want = _norm(want)
	var ok: bool = JSON.stringify(got) == JSON.stringify(want)
	if not ok:
		_fails += 1
	print("%s %s%s" % ["PASS" if ok else "FAIL", label, "" if ok else "   got %s want %s" % [JSON.stringify(got), JSON.stringify(want)]])


## JSON numbers load as floats; whole floats compare as ints, dictionaries by sorted keys.
func _norm(v: Variant) -> Variant:
	if v is float and is_equal_approx(v, round(v)):
		return int(round(v))
	if v is Array:
		var a: Array = []
		for e in v:
			a.append(_norm(e))
		return a
	if v is Dictionary:
		var d := {}
		var keys: Array = v.keys()
		keys.sort()
		for k in keys:
			d[k] = _norm(v[k])
		return d
	return v


func _init() -> void:
	var gold: Dictionary = H7Data.load_json(H7Data.GOLDEN_PATH)
	if gold.is_empty():
		print("FAIL golden file missing: %s" % H7Data.GOLDEN_PATH)
		quit(1)
		return
	var legs: Array = gold["legs"]
	_check("lab legs data equals golden legs", H7Data.load_legs(), legs)
	var leg0: Array = legs[0]
	for line_name in ["planned", "greedy"]:
		_replay(leg0, line_name, gold["leg0"][line_name])
	var extra: Dictionary = H7Data.load_json("res://tools/raid_lab_h7/data/h7_extra_golden.json")
	_check("extra golden present (python replays of lost nodes, survivors, Lockdown)", extra.size() > 0, true)
	for case_name in extra:
		_replay(legs[int(extra[case_name]["leg"])], case_name, extra[case_name]["rows"])
	_playable(legs)
	print("%d checks, %d failed" % [_checks, _fails])
	print("PARITY %s" % ("PASS" if _fails == 0 else "FAIL"))
	quit(0 if _fails == 0 else 1)


func _replay(leg: Array, line_name: String, line: Array) -> void:
	var st := H7State.new()
	for x in line:
		var i: int = int(x["raid"])
		var tag := "%s raid %d" % [line_name, i]
		var roster := H7Campaign.roster_for(leg, i, st)
		var buy: Array = x["buy"]
		var place: Array = x["place"]
		var rr := H7Campaign.raid_result(st, buy, place, x["crew"], roster)
		var r: H7Result = rr["r"]
		var s := H7Campaign.settle(st, rr["fort"], r, roster, i, buy, leg.size())
		_check(tag + " roster", roster, x["roster"])
		_check(tag + " frozen", r.frozen, x["frozen"])
		_check(tag + " steps", r.steps.size(), int(x["steps"]))
		var nodes := {}
		for k in r.nodes:
			nodes[k] = [r.nodes[k]["outcome"], r.nodes[k]["after"]]
		_check(tag + " nodes", nodes, x["nodes"])
		_check(tag + " kills", r.kill_ids(), x["kills"])
		_check(tag + " clean", r.clean, x["clean"])
		_check(tag + " breached", r.breached, x["breached"])
		_check(tag + " net", s.net, int(x["net"]))
		_check(tag + " bank", s.state.bank, int(x["bank"]))
		_check(tag + " lost", s.state.lost, x["lost"])
		_check(tag + " survivors", s.state.surv, x["survivors"])
		st = s.state


## Every seeded leg's rosters must be playable: all three raids resolve with a default fortress.
func _playable(legs: Array) -> void:
	for li in range(legs.size()):
		var st := H7State.new()
		var ok := true
		for i in range(legs[li].size()):
			var roster := H7Campaign.roster_for(legs[li], i, st)
			var rr := H7Campaign.raid_result(st, [], [], "SAFE", roster)
			var s := H7Campaign.settle(st, rr["fort"], rr["r"], roster, i, [], legs[li].size())
			ok = ok and not rr["r"].steps.is_empty()
			st = s.state
			if rr["r"].breached:
				break
		_check("seeded leg %d playable (resolves, no script error)" % li, ok, true)
