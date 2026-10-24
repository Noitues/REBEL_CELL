extends SceneTree
## Parity check of the L8–L11 rules (L8Rules, tools/raid_lab_city/l8_rules.gd) against data/l8_golden.json
## (tools/raid_concepts/l8_golden.py; oracle tools/raid_concepts/sweep_l8.py).
## It checks:
## - the config;
## - the leg data of every golden leg (leg_from_json);
## - every step of the greedy and naive line of each leg. Per step:
##   - the state before the capture;
##   - DECAY: for raid > 0, decay(before_capture) gives `after_decay`. For raid 0, `after_decay` equals
##     `before_capture` and no decay runs. A decayed cell's sentry leaves the placement and goes back to the pool,
##     so the pool counts stay the same (L11);
##   - capture_options of the decayed state holds the capture, and capture() of the decayed state gives `before`;
##   - placements() holds the place (at most MAX_PLACED sentries), and response_options() holds the response
##     (HOLD, REDEPLOY, DEPLOY or JAM);
##   - resolve / trace / hunter_line / tier / score, then the forecast;
##   - between_options() holds the between step, between() gives `after`, and score(after);
##   - SAFE_NEXT (L11): per intensity in the golden `safe_next`,
##     safe_next(leg, raid + 1, decay(leg, between(leg, after_raid, repair, build, intensity))) equals the golden bool;
##   - safe_next(leg, RAIDS, st) is true at the end of each line;
## - every random raid, random between step and random capture check (no decay there).
## States are compared as L8Rules.state_to_json against the golden JSON, by deep compare (ints stay ints; floats to
## 1e-6). The first 20 mismatches are printed with their path. Exits 0 only on full parity.
##   godot --headless --path . -s res://tools/raid_lab_city/parity_check.gd

const GOLDEN_PATH := "res://tools/raid_lab_city/data/l8_golden.json"
const MAX_SHOWN := 20
const EPS := 1e-6
const CANDIDATES := 3
const KNOWN_BEAMS := ["b1", "extra1", "extra2"]

var _fails: int = 0
var _checks: int = 0
var _shown: int = 0
var _steps: int = 0
var _blocks: int = 0
var _decayed: int = 0
var _raids: int = 3
var _kit_value: float = 2.5
var _max_placed: int = -1
var _legs: Dictionary = {}
var _resp_use: Dictionary = {"HOLD": 0, "REDEPLOY": 0, "DEPLOY": 0, "JAM": 0}
var _rand_resp_use: Dictionary = {"HOLD": 0, "REDEPLOY": 0, "DEPLOY": 0, "JAM": 0}
var _off_option_betweens: int = 0
var _safe_checked: int = 0
var _safe_true: int = 0


func _init() -> void:
	if not FileAccess.file_exists(GOLDEN_PATH):
		print("FAIL golden file missing: " + GOLDEN_PATH)
		quit(1)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(GOLDEN_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		print("FAIL golden file is not a JSON object")
		quit(1)
		return
	var gold: Dictionary = parsed
	for key: String in ["config", "legs", "random_raids", "random_betweens", "random_captures"]:
		if not gold.has(key):
			print("FAIL golden file has no '%s'" % key)
			quit(1)
			return
	var cfg: Dictionary = gold["config"]
	_check("config", L8Rules.config(), cfg)
	_raids = int(cfg["RAIDS"])
	_kit_value = float(cfg["KIT_VALUE"])
	if cfg.has("MAX_PLACED"):
		_max_placed = int(cfg["MAX_PLACED"])

	var n_lines := 0
	for raw: Variant in gold["legs"]:
		var rl: Dictionary = raw
		var seed_id := int(rl["seed"])
		var leg: Dictionary = L8Rules.leg_from_json(rl["leg"])
		_legs[seed_id] = leg
		_check_leg(seed_id, leg, rl["leg"])
		_replay("leg %d greedy" % seed_id, leg, rl["greedy"], true)
		_replay("leg %d naive" % seed_id, leg, rl["naive"], false)
		n_lines += 2

	var rr: Array = gold["random_raids"]
	for idx in range(rr.size()):
		var r: Dictionary = rr[idx]
		var tag := "random raid %d (leg %d raid %d cand %d)" % [idx, int(r["leg"]), int(r["raid"]) + 1, int(r["cand"])]
		var leg := _leg_of(tag, r["leg"])
		if leg.is_empty():
			continue
		var st: Dictionary = L8Rules.state_from_json(r["before"])
		_check_state(tag + " before (state_from_json round trip)", st, r["before"])
		var rk := String((r["response"] as Array)[0])
		_rand_resp_use[rk] = int(_rand_resp_use.get(rk, 0)) + 1
		var ns := _raid(tag, leg, int(r["raid"]), st, r)
		_check_mid_score(tag, leg, ns, r["after_raid"])

	var rb: Array = gold["random_betweens"]
	for idx in range(rb.size()):
		var r: Dictionary = rb[idx]
		var tag := "random between %d (leg %d)" % [idx, int(r["leg"])]
		var leg := _leg_of(tag, r["leg"])
		if leg.is_empty():
			continue
		var st: Dictionary = L8Rules.state_from_json(r["before"])
		_check_state(tag + " before (state_from_json round trip)", st, r["before"])
		var rep: Variant = _cell(r["repair"])
		var build: Variant = _str(r["build"])
		var inten := String(r["intensity"])
		if not _option_listed(leg, st, rep, build, inten):
			_off_option_betweens += 1
		var snap := JSON.stringify(L8Rules.state_to_json(st))
		var after: Dictionary = L8Rules.between(leg, st, rep, build, inten)
		_check_state(tag + " after", after, r["after"])
		_check_true(tag + " between() leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap)

	var rc: Array = gold["random_captures"]
	for idx in range(rc.size()):
		var r: Dictionary = rc[idx]
		var tag := "random capture %d (leg %d)" % [idx, int(r["leg"])]
		var leg := _leg_of(tag, r["leg"])
		if leg.is_empty():
			continue
		_check_captures(tag, leg, r)

	print("%d lines, %d golden steps (responses %s, %d blocks, %d decayed cells, safe_next %d checked / %d safe), %d random raids (responses %s), %d random betweens (%d off the between_options list), %d random captures"
		% [n_lines, _steps, JSON.stringify(_resp_use), _blocks, _decayed, _safe_checked, _safe_true, rr.size(),
			JSON.stringify(_rand_resp_use), rb.size(), _off_option_betweens, rc.size()])
	if _fails == 0:
		print("PARITY PASS %d checks" % _checks)
	else:
		print("PARITY FAIL %d of %d" % [_fails, _checks])
	quit(0 if _fails == 0 else 1)


# --- checks -------------------------------------------------------------------------------------------------------

## Records a failure; only the first MAX_SHOWN are printed.
func _fail(label: String, msg: String) -> void:
	_fails += 1
	if _shown < MAX_SHOWN:
		_shown += 1
		print("FAIL %s   %s" % [label, msg])


## Deep compare of got (already in JSON form) against want (golden JSON).
func _check(label: String, got: Variant, want: Variant) -> void:
	_checks += 1
	var d := _diff(got, want, "$")
	if d != "":
		_fail(label, d)


## Checks a condition; why is printed on failure.
func _check_true(label: String, ok: bool, why: String = "") -> void:
	_checks += 1
	if not ok:
		_fail(label, why if why != "" else "is false")


## A float score against the golden, to 1e-6.
func _check_score(label: String, got: Variant, want: Variant) -> void:
	_checks += 1
	if typeof(got) != TYPE_FLOAT and typeof(got) != TYPE_INT:
		_fail(label, "got a %s, want a number %s" % [type_string(typeof(got)), str(want)])
	elif absf(float(got) - float(want)) > EPS:
		_fail(label, "got %.6f want %.6f" % [float(got), float(want)])


## A state against its golden state_json, and checks that its counters are ints.
func _check_state(label: String, st: Dictionary, want: Variant) -> void:
	var sj: Dictionary = L8Rules.state_to_json(st)
	_check(label, sj, want)
	var why := _state_types(sj)
	_check_true(label + " ints stay ints", why == "", why)


## "" when heat, bank, home_hp and the pool and kit counts are ints, else what is not.
func _state_types(sj: Dictionary) -> String:
	for k: String in ["heat", "bank", "home_hp"]:
		if typeof(sj.get(k)) != TYPE_INT:
			return "%s is a %s" % [k, type_string(typeof(sj.get(k)))]
	for group: String in ["pool", "kit"]:
		var g: Variant = sj.get(group)
		if typeof(g) != TYPE_DICTIONARY:
			return group + " is not a Dictionary"
		var gd: Dictionary = g
		for k: Variant in gd:
			if typeof(gd[k]) != TYPE_INT:
				return "%s.%s is a %s" % [group, str(k), type_string(typeof(gd[k]))]
	return ""


## The leg's Dictionary by golden seed, or {} (and a failure) when that seed is not a golden leg.
func _leg_of(tag: String, seed_v: Variant) -> Dictionary:
	var s := int(seed_v)
	if not _legs.has(s):
		_fail(tag, "leg seed %d is not among the golden legs %s" % [s, str(_legs.keys())])
		return {}
	return _legs[s]


## leg_from_json kept every value, exploit, start cell and line of the golden leg.
func _check_leg(seed_id: int, leg: Dictionary, raw: Dictionary) -> void:
	var tag := "leg %d data" % seed_id
	_check(tag + " seed", leg.get("seed"), raw["seed"])
	var values: Dictionary = leg.get("values", {})
	for e: Variant in raw["values"]:
		var c := Vector2i(int(e[0]), int(e[1]))
		_check("%s value %s" % [tag, str(c)], values.get(c), e[2])
	_check(tag + " value count", values.size(), (raw["values"] as Array).size())
	_check(tag + " exploits", _cells_json(leg.get("exploits", [])), raw["exploits"])
	_check(tag + " start", _cells_json(leg.get("start", [])), raw["start"])
	var raids: Array = leg.get("raids", [])
	var graids: Array = raw["raids"]
	_check(tag + " raid count", raids.size(), graids.size())
	for i in range(mini(raids.size(), graids.size())):
		var rd: Dictionary = raids[i]
		var g: Dictionary = graids[i]
		var t := "%s raid %d" % [tag, i + 1]
		for key: String in KNOWN_BEAMS:
			_check(t + " " + key, _line_json(rd.get(key)), g[key])
		var cj: Array = []
		for ln: Variant in rd.get("cands", []):
			cj.append(_line_json(ln))
		_check(t + " cands", cj, g["cands"])
		_check(t + " perm", _strs(rd.get("perm", [])), g["perm"])
		_check(t + " real", rd.get("real"), g["real"])
		_check(t + " hunter_type", _str(rd.get("hunter_type")), g["hunter_type"])
		_check(t + " hunter_street", rd.get("hunter_street"), g["hunter_street"])


## Replays one golden line from initial(leg), chaining our own states: decay (raid > 0), capture, raid, between.
func _replay(tag: String, leg: Dictionary, steps: Array, greedy: bool) -> void:
	_check_true(tag + " has steps", steps.size() > 0)
	var st: Dictionary = L8Rules.initial(leg)
	var ended_ok := false
	for n in range(steps.size()):
		var s: Dictionary = steps[n]
		var i := int(s["raid"])
		var t := "%s raid %d" % [tag, i + 1]
		_steps += 1
		_check(t + " raid index", i, n)
		_check_state(t + " before capture", st, s["before_capture"])
		st = _decay_step(t, leg, i, st, s)
		var opts_j := _cells_json(L8Rules.capture_options(leg, st))
		var cap: Variant = _cell(s["capture"])
		if typeof(cap) == TYPE_NIL:
			_check(t + " no capture only when there is no option (after decay)", opts_j, [])
		else:
			_check_true(t + " capture is a capture option (after decay)", _has(opts_j, _cj(cap)),
				"%s not in %s" % [_s(_cj(cap)), _s(opts_j)])
			var snap := JSON.stringify(L8Rules.state_to_json(st))
			var nxt: Dictionary = L8Rules.capture(leg, st, cap)
			_check_true(t + " capture() leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap)
			st = nxt
		_check_state(t + " before (after the capture)", st, s["before"])
		_check(t + " cand is the real candidate", int(s["cand"]), (leg["raids"][i] as Dictionary).get("real"))
		var place := _place(s["place"])
		var resp := _resp(s["response"])
		_resp_use[resp[0]] = int(_resp_use.get(resp[0], 0)) + 1
		var ns := _raid(t, leg, i, st, s)
		_check_forecast(t, leg, i, st, place, int(s["cand"]), s, greedy)
		var breached := int(ns.get("home_hp", 0)) <= 0
		var last := i == _raids - 1
		var after: Dictionary = ns
		if typeof(s["between"]) == TYPE_NIL:
			_check_true(t + " no between step only after a breach or the last raid", breached or last)
		else:
			_check_true(t + " a between step only before a later raid", not breached and not last)
			var b: Dictionary = s["between"]
			var rep: Variant = _cell(b["repair"])
			var build: Variant = _str(b["build"])
			var inten := String(b["intensity"])
			_check_true(t + " between step is one of between_options()", _option_listed(leg, ns, rep, build, inten),
				_s([_cj(rep), build, inten]))
			var snap := JSON.stringify(L8Rules.state_to_json(ns))
			after = L8Rules.between(leg, ns, rep, build, inten)
			_check_true(t + " between() leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(ns)) == snap)
			_check_safe_next(t, leg, i, ns, rep, build, inten, s)
		if s.has("after"):
			_check_state(t + " after", after, s["after"])
		_check_score(t + " score after", L8Rules.score(leg, after), s["score_after"])
		st = after
		if breached or last:
			ended_ok = true
			_check_true(t + " the line ends at a breach or the last raid", n == steps.size() - 1,
				"%d more steps follow" % (steps.size() - 1 - n))
			break
	_check_true(tag + " the line runs to the last raid or a breach", ended_ok)
	var past: Variant = L8Rules.safe_next(leg, _raids, st)
	_check(tag + " safe_next(raid = RAIDS) is true", past, true)


## The SAFE_NEXT record of a golden step with a between step (L11). For every intensity in the golden
## `safe_next` dict: safe_next(leg, raid + 1, decay(leg, between(leg, after_raid, repair, build, intensity)))
## equals the golden bool. The chosen intensity must be among the keys.
func _check_safe_next(t: String, leg: Dictionary, i: int, ns: Dictionary, rep: Variant, build: Variant, chosen: String, s: Dictionary) -> void:
	var has_sn := s.has("safe_next")
	_check_true(t + " golden step with a between step has safe_next", has_sn)
	if not has_sn:
		return
	var sn_v: Variant = s["safe_next"]
	if typeof(sn_v) != TYPE_DICTIONARY:
		_fail(t + " safe_next", "is a %s, want a Dictionary {intensity: bool}" % type_string(typeof(sn_v)))
		return
	var sn: Dictionary = sn_v
	_check_true(t + " safe_next lists the chosen intensity", sn.has(chosen), "%s not in %s" % [chosen, _s(sn.keys())])
	var keys: Array = sn.keys()
	keys.sort()
	var snap := JSON.stringify(L8Rules.state_to_json(ns))
	for k: Variant in keys:
		var inten := String(k)
		var tk := "%s safe_next %s" % [t, inten]
		var nb: Dictionary = L8Rules.between(leg, ns, rep, build, inten)
		var nd: Dictionary = L8Rules.decay(leg, nb)
		var got: Variant = L8Rules.safe_next(leg, i + 1, nd)
		_safe_checked += 1
		if typeof(sn[k]) == TYPE_BOOL and bool(sn[k]):
			_safe_true += 1
		_check(tk, got, sn[k])
	_check_true(t + " safe_next leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(ns)) == snap)


## The DECAY step of a golden step. For raid > 0 it runs decay(leg, st) and checks it against `after_decay`. For
## raid 0 no decay runs, and the golden `after_decay` must equal `before_capture`. A decayed cell's sentry leaves
## the placement but stays in the pool (L11). Returns the state for capture.
func _decay_step(t: String, leg: Dictionary, i: int, st: Dictionary, s: Dictionary) -> Dictionary:
	var has_ad := s.has("after_decay")
	_check_true(t + " golden step has after_decay", has_ad)
	if i == 0:
		if has_ad:
			_check(t + " after_decay = before_capture on the first raid", s["after_decay"], s["before_capture"])
		return st
	var snap := JSON.stringify(L8Rules.state_to_json(st))
	var dec: Dictionary = L8Rules.decay(leg, st)
	_check_true(t + " decay() leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap)
	var before_owned: Dictionary = st.get("owned", {})
	var after_owned: Dictionary = dec.get("owned", {})
	for c: Variant in before_owned:
		if String(before_owned[c]) == "DOWN" and String(after_owned.get(c, "")) == "TAKEN":
			_decayed += 1
	for c: Variant in after_owned:
		_check_true("%s after decay %s is not DOWN" % [t, str(c)], String(after_owned[c]) != "DOWN")
	var dec_sent: Dictionary = dec.get("sentries", {})
	for c: Variant in dec_sent:
		_check_true("%s after decay no sentry on TAKEN %s" % [t, str(c)], String(after_owned.get(c, "")) != "TAKEN")
	var sj_before: Dictionary = L8Rules.state_to_json(st)
	var sj_after: Dictionary = L8Rules.state_to_json(dec)
	_check(t + " decay keeps the pool (a lost sentry goes back to the pool)", sj_after.get("pool"), sj_before.get("pool"))
	if has_ad:
		_check_state(t + " after decay", dec, s["after_decay"])
	return dec


## One raid from st against a golden raid record (place, cand, response, trace, hunter, tier, after_raid, score_raid).
## Returns our state after the raid.
func _raid(t: String, leg: Dictionary, i: int, st: Dictionary, g: Dictionary) -> Dictionary:
	var place := _place(g["place"])
	var cand := int(g["cand"])
	var resp := _resp(g["response"])
	_check_true(t + " cand is a candidate", cand >= 0 and cand < CANDIDATES, str(cand))
	if _max_placed >= 0:
		var n_placed := (place["sentries"] as Dictionary).size()
		_check_true(t + " place holds at most MAX_PLACED sentries", n_placed <= _max_placed,
			"%d > %d" % [n_placed, _max_placed])
	var snap_st := JSON.stringify(L8Rules.state_to_json(st))
	var pkey := JSON.stringify(_place_json(place))
	var found := false
	for p: Variant in L8Rules.placements(leg, st):
		if JSON.stringify(_place_json(p)) == pkey:
			found = true
			break
	_check_true(t + " place is one of placements()", found, pkey)
	var rkey := JSON.stringify(_resp_json(resp))
	var r_opts: Array = []
	for r: Variant in L8Rules.response_options(leg, i, st, cand, place):
		r_opts.append(_resp_json(r))
	_check_true(t + " response is one of response_options()", _has(r_opts, _resp_json(resp)), "%s not in %s" % [rkey, _s(r_opts)])
	var res: Dictionary = L8Rules.resolve(leg, i, st, cand, place, resp)
	if not (res.has("state") and res.has("touches")):
		_fail(t + " resolve", "result lacks state / touches: %s" % str(res.keys()))
		return st
	var ns: Dictionary = res["state"]
	var touches: Array = res["touches"]
	var want_touches: Array = []
	for e: Variant in g["trace"]:
		want_touches.append([e[1], e[2]])
		if String(e[2]) == "block":
			_blocks += 1
	_check(t + " touches", _touches_json(touches), want_touches)
	_check(t + " trace", _trace_json(L8Rules.trace(leg, i, st, cand, place, resp)), g["trace"])
	_check(t + " hunter line", _line_json(L8Rules.hunter_line(leg, i, st, cand, place, resp)), g["hunter"])
	_check(t + " tier", L8Rules.tier(st, ns, touches), g["tier"])
	_check_state(t + " after raid", ns, g["after_raid"])
	_check_score(t + " score after raid", L8Rules.score(leg, ns), g["score_raid"])
	_check_true(t + " the raid leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap_st)
	_check_true(t + " the raid leaves the place untouched", JSON.stringify(_place_json(place)) == pkey)
	return ns


## score(mid = true) adds KIT_VALUE per unspent ghost, spoof and pool sentry (a breach stays -BREACH).
func _check_mid_score(t: String, leg: Dictionary, ns: Dictionary, after_j: Dictionary) -> void:
	var base := L8Rules.score(leg, ns)
	var want := float(base)
	if int(after_j["home_hp"]) > 0:
		var n := 0
		for k: Variant in (after_j["kit"] as Dictionary):
			n += int(after_j["kit"][k])
		for k: Variant in (after_j["pool"] as Dictionary):
			n += int(after_j["pool"][k])
		want += _kit_value * n
	_check_score(t + " mid-leg score", L8Rules.score(leg, ns, true), want)


## forecast(): HOLD per candidate equals resolve(HOLD), every best response replays to its own result, and the played
## candidate matches the golden step (the best response on the greedy line, HOLD on the naive line).
func _check_forecast(t: String, leg: Dictionary, i: int, st: Dictionary, place: Dictionary, cand: int, g: Dictionary, greedy: bool) -> void:
	var fc: Array = L8Rules.forecast(leg, i, st, place)
	_check(t + " forecast size", fc.size(), CANDIDATES)
	for k in range(mini(fc.size(), CANDIDATES)):
		var tk := "%s forecast cand %d" % [t, k]
		if typeof(fc[k]) != TYPE_DICTIONARY:
			_fail(tk, "entry is not a Dictionary")
			continue
		var e: Dictionary = fc[k]
		var shape_ok: bool = typeof(e.get("hold")) == TYPE_DICTIONARY and typeof(e.get("best")) == TYPE_DICTIONARY \
			and typeof(e["hold"].get("state")) == TYPE_DICTIONARY and typeof(e["best"].get("state")) == TYPE_DICTIONARY
		_check_true(tk + " has hold and best with states", shape_ok, str(e.keys()))
		if not shape_ok:
			continue
		_check(tk + " cand", e.get("cand"), k)
		var hold: Dictionary = e["hold"]
		var best: Dictionary = e["best"]
		var hres: Dictionary = L8Rules.resolve(leg, i, st, k, place, ["HOLD"])
		_check(tk + " hold touches", _touches_json(hold.get("touches", [])), _touches_json(hres["touches"]))
		_check(tk + " hold state", L8Rules.state_to_json(hold["state"]), L8Rules.state_to_json(hres["state"]))
		_check(tk + " hold tier", hold.get("tier"), L8Rules.tier(st, hres["state"], hres["touches"]))
		var bres: Dictionary = L8Rules.resolve(leg, i, st, k, place, best.get("response", ["HOLD"]))
		_check(tk + " best touches replay", _touches_json(best.get("touches", [])), _touches_json(bres["touches"]))
		_check(tk + " best state replay", L8Rules.state_to_json(best["state"]), L8Rules.state_to_json(bres["state"]))
		_check(tk + " best tier replay", best.get("tier"), L8Rules.tier(st, bres["state"], bres["touches"]))
		if k != cand:
			continue
		var side: Dictionary = best if greedy else hold
		var side_name := "best" if greedy else "hold"
		if greedy:
			_check(tk + " best response = the golden response", _resp_json(best.get("response", [])), g["response"])
		_check(tk + " %s tier = the golden tier" % side_name, side.get("tier"), g["tier"])
		_check(tk + " %s state = the golden after raid" % side_name, L8Rules.state_to_json(side["state"]), g["after_raid"])


## The options from capture_options (in cell order), and capture() of each = the state with that cell owned OK.
func _check_captures(tag: String, leg: Dictionary, r: Dictionary) -> void:
	var st: Dictionary = L8Rules.state_from_json(r["state"])
	_check_state(tag + " state (state_from_json round trip)", st, r["state"])
	_check(tag + " options", _cells_json(L8Rules.capture_options(leg, st)), r["options"])
	var snap := JSON.stringify(L8Rules.state_to_json(st))
	for oj: Variant in r["options"]:
		var c := Vector2i(int(oj[0]), int(oj[1]))
		var want: Dictionary = (r["state"] as Dictionary).duplicate(true)
		var owned: Array = (want["owned"] as Array).duplicate(true)
		owned.append([c.x, c.y, "OK"])
		owned.sort_custom(func(a: Variant, b: Variant) -> bool:
			return int(a[1]) < int(b[1]) or (int(a[1]) == int(b[1]) and int(a[0]) < int(b[0])))
		want["owned"] = owned
		_check_state("%s capture %s" % [tag, str(c)], L8Rules.capture(leg, st, c), want)
	_check_true(tag + " capture() leaves the state untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap)


## True when (repair, build, intensity) is one of between_options(leg, st).
func _option_listed(leg: Dictionary, st: Dictionary, rep: Variant, build: Variant, inten: String) -> bool:
	var key := JSON.stringify([_cj(rep), build, inten])
	for o: Variant in L8Rules.between_options(leg, st):
		if JSON.stringify(_opt_json(o)) == key:
			return true
	return false


# --- deep compare -------------------------------------------------------------------------------------------------

## "" when got equals want, else the first difference with its path. Numbers: int == int exactly, else to 1e-6.
## String and StringName are equal by text. Dictionaries compare by key set, not order.
func _diff(got: Variant, want: Variant, path: String) -> String:
	var tg := typeof(got)
	var tw := typeof(want)
	if _is_num(tg) and _is_num(tw):
		var same: bool = (int(got) == int(want)) if (tg == TYPE_INT and tw == TYPE_INT) else absf(float(got) - float(want)) <= EPS
		return "" if same else "%s: got %s want %s" % [path, str(got), str(want)]
	if _is_str(tg) and _is_str(tw):
		return "" if String(got) == String(want) else "%s: got \"%s\" want \"%s\"" % [path, String(got), String(want)]
	if tg != tw:
		return "%s: got %s (%s) want %s (%s)" % [path, _s(got), type_string(tg), _s(want), type_string(tw)]
	match tg:
		TYPE_NIL:
			return ""
		TYPE_ARRAY:
			var a: Array = got
			var b: Array = want
			for k in range(mini(a.size(), b.size())):
				var d := _diff(a[k], b[k], "%s[%d]" % [path, k])
				if d != "":
					return d
			if a.size() != b.size():
				return "%s: size got %d want %d   got %s want %s" % [path, a.size(), b.size(), _s(a), _s(b)]
			return ""
		TYPE_DICTIONARY:
			var a: Dictionary = got
			var b: Dictionary = want
			var keys: Array = b.keys()
			keys.sort()
			for k: Variant in keys:
				if not a.has(k):
					return "%s: missing key %s (want %s)" % [path, str(k), _s(b[k])]
				var d := _diff(a[k], b[k], "%s.%s" % [path, str(k)])
				if d != "":
					return d
			for k: Variant in a.keys():
				if not b.has(k):
					return "%s: extra key %s (got %s)" % [path, str(k), _s(a[k])]
			return ""
	return "" if got == want else "%s: got %s want %s" % [path, _s(got), _s(want)]


func _is_num(t: int) -> bool:
	return t == TYPE_INT or t == TYPE_FLOAT


func _is_str(t: int) -> bool:
	return t == TYPE_STRING or t == TYPE_STRING_NAME


func _s(v: Variant) -> String:
	var s := JSON.stringify(v)
	return s if s.length() <= 160 else s.substr(0, 157) + "..."


func _has(list: Array, item: Variant) -> bool:
	var key := JSON.stringify(item)
	for e: Variant in list:
		if JSON.stringify(e) == key:
			return true
	return false


# --- JSON <-> lab forms ---------------------------------------------------------------------------------------------

func _cell_less(a: Variant, b: Variant) -> bool:
	var va: Vector2i = a
	var vb: Vector2i = b
	return va.y < vb.y or (va.y == vb.y and va.x < vb.x)


func _str(v: Variant) -> Variant:
	return null if typeof(v) == TYPE_NIL else String(v)


func _strs(arr: Variant) -> Array:
	var out: Array = []
	for e: Variant in arr:
		out.append(_str(e))
	return out


## A golden cell ([x, y], "HOME" or null) to the lab form (Vector2i, "HOME" or null).
func _cell(j: Variant) -> Variant:
	match typeof(j):
		TYPE_NIL:
			return null
		TYPE_STRING, TYPE_STRING_NAME:
			return String(j)
		TYPE_ARRAY:
			return Vector2i(int(j[0]), int(j[1]))
	return j


## A lab cell to its JSON form; anything unexpected passes through so the compare shows it.
func _cj(c: Variant) -> Variant:
	match typeof(c):
		TYPE_NIL:
			return null
		TYPE_VECTOR2I:
			var v: Vector2i = c
			return [v.x, v.y]
		TYPE_STRING, TYPE_STRING_NAME:
			return String(c)
	return c


func _cells_json(arr: Variant) -> Array:
	var out: Array = []
	for c: Variant in arr:
		out.append(_cj(c))
	return out


## A golden place ({sentries: [[x, y, t]], ghost}) to the lab form ({sentries: {Vector2i: type}, ghost}).
func _place(j: Dictionary) -> Dictionary:
	var sent: Dictionary = {}
	for e: Variant in j["sentries"]:
		sent[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	return {"sentries": sent, "ghost": _cell(j["ghost"])}


## A lab place to its canonical JSON form: sentries in cell order (y, then x), whatever the dict order.
func _place_json(p: Variant) -> Dictionary:
	var d: Dictionary = p
	var sent: Dictionary = d.get("sentries", {})
	var keys: Array = sent.keys()
	keys.sort_custom(_cell_less)
	var out: Array = []
	for c: Variant in keys:
		var v: Vector2i = c
		out.append([v.x, v.y, String(sent[c])])
	return {"sentries": out, "ghost": _cj(d.get("ghost"))}


## A golden response to the lab form: ["HOLD"], ["JAM"], ["REDEPLOY", Vector2i, Vector2i] or
## ["DEPLOY", type, Vector2i].
func _resp(j: Array) -> Array:
	var kind := String(j[0])
	if kind == "REDEPLOY":
		return [kind, _cell(j[1]), _cell(j[2])]
	if kind == "DEPLOY":
		return [kind, String(j[1]), _cell(j[2])]
	return [kind]


## A lab response to its JSON form (cells as [x, y], the DEPLOY type as a String).
func _resp_json(r: Variant) -> Array:
	var a: Array = r
	var out: Array = [String(a[0])]
	for k in range(1, a.size()):
		out.append(_cj(a[k]))
	return out


func _line_json(v: Variant) -> Variant:
	if typeof(v) != TYPE_DICTIONARY:
		return v
	var d: Dictionary = v
	return {"kind": _str(d.get("kind")), "index": d.get("index"), "cells": _cells_json(d.get("cells", [])),
		"type": _str(d.get("type")), "home": d.get("home")}


func _trace_json(tr: Variant) -> Array:
	var out: Array = []
	for e: Variant in tr:
		out.append([String(e[0]), _cj(e[1]), String(e[2])])
	return out


func _touches_json(touches: Variant) -> Array:
	var out: Array = []
	for e: Variant in touches:
		out.append([_cj(e[0]), String(e[1])])
	return out


func _opt_json(o: Variant) -> Array:
	return [_cj(o[0]), _str(o[1]), _str(o[2])]
