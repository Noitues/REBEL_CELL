extends SceneTree
## Parity check of the L8–L13 rules (L8Rules, tools/raid_lab_city/l8_rules.gd) against data/l8_golden.json
## (tools/raid_concepts/l8_golden.py; oracle tools/raid_concepts/sweep_l8.py).
## It checks:
## - the config;
## - the leg data of every golden leg (leg_from_json), including the L13 `hunter_cands` (2 distinct streets in 0..3)
##   and `hunter_real` (0 or 1). The removed `hunter_street` field must be absent;
## - every step of the greedy and naive line of each leg. Per step:
##   - the state before the capture (state JSON carries `extra_capture`, an int);
##   - DECAY: for raid > 0, decay(before_capture) gives `after_decay`. For raid 0, `after_decay` equals
##     `before_capture` and no decay runs. A decayed cell's sentry leaves the placement but stays in the pool (L11);
##   - CAPTURE (L13 R5): `capture` is a list of 0 to 2 cells. Each capture is checked against capture_options of the
##     current state (the second capture uses the state after the first). A second capture only when extra_capture > 0.
##     A missing capture only when there is no option. The phase then clears extra_capture, and the result is `before`;
##   - `cand` is the real sealed candidate and `hunt` the real hunter street (hunter_real);
##   - placements() holds the place (at most MAX_PLACED sentries), and response_options() holds the response (HOLD,
##     REDEPLOY, DEPLOY, SACRIFICE or JAM), in the kind order HOLD, REDEPLOY…, DEPLOY…, SACRIFICE…, JAM;
##   - resolve / trace / hunter_line with hunt (L13 R2), tier and score. The hunter runs
##     street(hunter_cands[hunt]) top to bottom unless JAM. A SACRIFICE cell ends TAKEN with no sentry and the sealed
##     beam never harms HOME; a "shielded" touch only appears under SACRIFICE. A raid keeps the pool counts;
##   - the forecast: per candidate, the HOLD outcome for each of the 2 hunter streets;
##   - between_options() holds the between step, between() gives `after`, and score(after);
##   - SAFE_NEXT (L11): per intensity in the golden `safe_next`,
##     safe_next(leg, raid + 1, decay(leg, between(leg, after_raid, repair, build, intensity))) equals the golden bool;
##   - safe_next(leg, RAIDS, st) is true at the end of each line;
## - every random raid (with its `hunt`), random between step and random capture check (no decay there).
## States are compared as L8Rules.state_to_json against the golden JSON, by deep compare (ints stay ints; floats to
## 1e-6). The first 20 mismatches are printed with their path. Exits 0 only on full parity.
##   godot --headless --path . -s res://tools/raid_lab_city/parity_check.gd

const GOLDEN_PATH := "res://tools/raid_lab_city/data/l8_golden.json"
const MAX_SHOWN := 20
const EPS := 1e-6
const CANDIDATES := 3
const HUNTERS := 2
const STREETS := 4
const KNOWN_BEAMS := ["b1", "extra1", "extra2"]
const RESPONSE_RANK := {"HOLD": 0, "REDEPLOY": 1, "DEPLOY": 2, "SACRIFICE": 3, "JAM": 4}
const TYPE_RANK := {"D": 0, "N": 1, "E": 2}

var _fails: int = 0
var _checks: int = 0
var _shown: int = 0
var _steps: int = 0
var _blocks: int = 0
var _shielded: int = 0
var _decayed: int = 0
var _double_captures: int = 0
var _raids: int = 3
var _rows: int = 3
var _kit_value: float = 2.5
var _max_placed: int = -1
var _legs: Dictionary = {}
var _resp_use: Dictionary = {"HOLD": 0, "REDEPLOY": 0, "DEPLOY": 0, "SACRIFICE": 0, "JAM": 0}
var _rand_resp_use: Dictionary = {"HOLD": 0, "REDEPLOY": 0, "DEPLOY": 0, "SACRIFICE": 0, "JAM": 0}
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
	if cfg.has("H"):
		_rows = int(cfg["H"])

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
		var tag := "random raid %d (leg %d raid %d cand %d hunt %s)" % [idx, int(r["leg"]), int(r["raid"]) + 1,
			int(r["cand"]), str(r.get("hunt"))]
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

	print("%d lines, %d golden steps (responses %s, %d blocks, %d shielded, %d decayed cells, %d double captures, safe_next %d checked / %d safe), %d random raids (responses %s), %d random betweens (%d off the between_options list), %d random captures"
		% [n_lines, _steps, JSON.stringify(_resp_use), _blocks, _shielded, _decayed, _double_captures, _safe_checked,
			_safe_true, rr.size(), JSON.stringify(_rand_resp_use), rb.size(), _off_option_betweens, rc.size()])
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


## "" when heat, bank, home_hp, extra_capture and the pool and kit counts are ints, else what is not.
func _state_types(sj: Dictionary) -> String:
	for k: String in ["heat", "bank", "home_hp", "extra_capture"]:
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


## leg_from_json kept every value, exploit, start cell and line of the golden leg, and the L13 hunter fields.
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
		_check_true(t + " golden raid has hunter_cands and hunter_real", g.has("hunter_cands") and g.has("hunter_real"),
			str(g.keys()))
		_check(t + " hunter_cands", rd.get("hunter_cands"), g.get("hunter_cands"))
		_check(t + " hunter_real", rd.get("hunter_real"), g.get("hunter_real"))
		var hc := _ints(rd.get("hunter_cands", []))
		var hc_ok := hc.size() == HUNTERS and int(hc[0]) != int(hc[1])
		for x: Variant in hc:
			hc_ok = hc_ok and int(x) >= 0 and int(x) < STREETS
		_check_true(t + " hunter_cands are 2 distinct streets in 0..3", hc_ok, _s(hc))
		var hr := int(rd.get("hunter_real", -1))
		_check_true(t + " hunter_real is 0 or 1", hr == 0 or hr == 1, str(rd.get("hunter_real")))
		_check_true(t + " hunter_street is gone (L13)", not rd.has("hunter_street") and not g.has("hunter_street"))


## Replays one golden line from initial(leg), chaining our own states: decay (raid > 0), capture(s), raid, between.
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
		st = _capture_phase(t, leg, st, s)
		_check_state(t + " before (after the capture)", st, s["before"])
		var rd: Dictionary = leg["raids"][i]
		_check(t + " cand is the real candidate", int(s["cand"]), rd.get("real"))
		_check_true(t + " golden step has hunt", s.has("hunt"))
		if s.has("hunt"):
			_check(t + " hunt is the real hunter street", int(s["hunt"]), rd.get("hunter_real"))
		var place := _place(s["place"])
		var resp := _resp(s["response"])
		var rk := String(resp[0])
		_resp_use[rk] = int(_resp_use.get(rk, 0)) + 1
		if not greedy:
			_check(t + " naive never responds", _resp_json(resp), ["HOLD"])
			_check(t + " naive never ghosts", _cj(place["ghost"]), null)
		var ns := _raid(t, leg, i, st, s)
		_check_forecast(t, leg, i, st, place, int(s["cand"]), int(s.get("hunt", 0)), s)
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
			if not greedy:
				_check(t + " naive builds nothing", build, null)
				_check(t + " naive plays NORMAL", inten, "NORMAL")
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


## The CAPTURE phase of a golden step (L13 R5). The golden `capture` is a list of 0 to 2 cells. Capture 1 always
## runs; capture 2 runs when extra_capture > 0, on the updated state's options. A capture may be missing only when
## there is no option. The phase then clears extra_capture. Returns the state after the phase.
func _capture_phase(t: String, leg: Dictionary, st: Dictionary, s: Dictionary) -> Dictionary:
	var raw: Variant = s.get("capture")
	var caps: Array = []
	if typeof(raw) == TYPE_ARRAY:
		caps = raw
	else:
		_fail(t + " capture", "is a %s (%s), want a list of 0 to 2 cells" % [type_string(typeof(raw)), _s(raw)])
	var extra := int(st.get("extra_capture", 0))
	var allowed := 2 if extra > 0 else 1
	_check_true(t + " captures at most 1 + (extra_capture > 0)", caps.size() <= allowed,
		"%d captures with extra_capture %d" % [caps.size(), extra])
	var cur: Dictionary = st
	for n in range(maxi(allowed, caps.size())):
		var tc := "%s capture %d" % [t, n + 1]
		var opts_j := _cells_json(L8Rules.capture_options(leg, cur))
		if n >= caps.size():
			_check(tc + " is skipped only when there is no option", opts_j, [])
			continue
		var cap: Variant = _cell(caps[n])
		if typeof(cap) != TYPE_VECTOR2I:
			_fail(tc, "is %s, want a cell [x, y]" % _s(caps[n]))
			continue
		_check_true(tc + " is a capture option", _has(opts_j, _cj(cap)), "%s not in %s" % [_s(_cj(cap)), _s(opts_j)])
		var snap := JSON.stringify(L8Rules.state_to_json(cur))
		var nxt: Dictionary = L8Rules.capture(leg, cur, cap)
		_check_true(tc + " capture() leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(cur)) == snap)
		cur = nxt
	if caps.size() >= 2:
		_double_captures += 1
	if cur.has("extra_capture") and int(cur["extra_capture"]) != 0:
		cur = cur.duplicate(true)
		cur["extra_capture"] = 0
	return cur


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
	_check(t + " decay keeps extra_capture", sj_after.get("extra_capture"), sj_before.get("extra_capture"))
	if has_ad:
		_check_state(t + " after decay", dec, s["after_decay"])
	return dec


## One raid from st against a golden raid record (place, cand, hunt, response, trace, hunter, tier, after_raid,
## score_raid). Returns our state after the raid.
func _raid(t: String, leg: Dictionary, i: int, st: Dictionary, g: Dictionary) -> Dictionary:
	var place := _place(g["place"])
	var cand := int(g["cand"])
	var hunt_ok := g.has("hunt")
	_check_true(t + " golden raid has hunt", hunt_ok)
	var hunt := int(g["hunt"]) if hunt_ok else 0
	var resp := _resp(g["response"])
	_check_true(t + " cand is a candidate", cand >= 0 and cand < CANDIDATES, str(cand))
	_check_true(t + " hunt is 0 or 1", hunt >= 0 and hunt < HUNTERS, str(hunt))
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
	_check_response_order(t, st, r_opts)
	var res: Dictionary = L8Rules.resolve(leg, i, st, cand, hunt, place, resp)
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
		elif String(e[2]) == "shielded":
			_shielded += 1
	_check(t + " touches", _touches_json(touches), want_touches)
	var tr_j := _trace_json(L8Rules.trace(leg, i, st, cand, hunt, place, resp))
	_check(t + " trace", tr_j, g["trace"])
	var hl_j: Variant = _line_json(L8Rules.hunter_line(leg, i, st, cand, hunt, place, resp))
	_check(t + " hunter line", hl_j, g["hunter"])
	_check_hunter_shape(t, leg, i, hunt, resp, hl_j)
	var is_sac := String(resp[0]) == "SACRIFICE"
	for e: Variant in tr_j:
		if String(e[2]) == "shielded":
			_check_true(t + " a shielded touch only under SACRIFICE", is_sac, _s(e))
	if is_sac:
		_check_sacrifice(t, resp[1], ns, tr_j)
	_check(t + " tier", L8Rules.tier(st, ns, touches), g["tier"])
	_check_state(t + " after raid", ns, g["after_raid"])
	_check(t + " the raid keeps the pool counts", L8Rules.state_to_json(ns).get("pool"), L8Rules.state_to_json(st).get("pool"))
	_check_score(t + " score after raid", L8Rules.score(leg, ns), g["score_raid"])
	_check_true(t + " the raid leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap_st)
	_check_true(t + " the raid leaves the place untouched", JSON.stringify(_place_json(place)) == pkey)
	return ns


## L13 R2: unless JAM, the hunter runs street(hunter_cands[hunt]) top to bottom (y = 0→2) in hunter_type and does not
## reach HOME. Under JAM there is no hunter line.
func _check_hunter_shape(t: String, leg: Dictionary, i: int, hunt: int, resp: Array, hl_j: Variant) -> void:
	if String(resp[0]) == "JAM":
		_check(t + " JAM: no hunter line", hl_j, null)
		return
	var rd: Dictionary = leg["raids"][i]
	var hc := _ints(rd.get("hunter_cands", []))
	if hunt < 0 or hunt >= hc.size():
		_fail(t + " hunter street", "hunt %d out of hunter_cands %s" % [hunt, _s(hc)])
		return
	var x := int(hc[hunt])
	var cells: Array = []
	for y in range(_rows):
		cells.append([x, y])
	var want := {"kind": "STREET", "index": x, "cells": cells, "type": _str(rd.get("hunter_type")), "home": false}
	_check(t + " hunter runs hunter_cands[hunt] top to bottom", hl_j, want)


## L13 R3: the sacrificed cell ends TAKEN without a sentry, and the sealed beam never records a HOME loss.
func _check_sacrifice(t: String, cell: Variant, ns: Dictionary, tr_j: Array) -> void:
	if typeof(cell) != TYPE_VECTOR2I:
		_fail(t + " SACRIFICE", "target is %s, want a cell" % _s(_cj(cell)))
		return
	var owned: Dictionary = ns.get("owned", {})
	var sent: Dictionary = ns.get("sentries", {})
	_check_true(t + " SACRIFICE cell is TAKEN after the raid", String(owned.get(cell, "")) == "TAKEN",
		"%s is %s" % [str(cell), str(owned.get(cell))])
	_check_true(t + " SACRIFICE cell keeps no sentry", not sent.has(cell))
	for e: Variant in tr_j:
		_check_true(t + " SACRIFICE: the sealed beam does not harm HOME",
			not (String(e[0]) == "sealed" and String(e[2]) == "home"), _s(e))


## response_options order (L13): HOLD first, then REDEPLOY…, DEPLOY… (types D, N, E, then cells in cell order),
## SACRIFICE… (every owned non-TAKEN cell in cell order), JAM. Options are in JSON form.
func _check_response_order(t: String, st: Dictionary, r_opts: Array) -> void:
	var why := ""
	var prev := -1
	var holds := 0
	var jams := 0
	var last_dep := -1
	var sac: Array = []
	for o: Variant in r_opts:
		var a: Array = o
		var k := String(a[0])
		if not RESPONSE_RANK.has(k):
			why = "unknown response kind %s" % _s(a)
			break
		var rk := int(RESPONSE_RANK[k])
		if rk < prev:
			why = "%s comes after a later kind" % _s(a)
			break
		prev = rk
		if k == "HOLD":
			holds += 1
		elif k == "JAM":
			jams += 1
		elif k == "DEPLOY":
			var ty := String(a[1])
			var c: Array = a[2]
			var key := int(TYPE_RANK.get(ty, 9)) * 10000 + int(c[1]) * 100 + int(c[0])
			if key <= last_dep:
				why = "DEPLOY %s is out of type / cell order" % _s(a)
				break
			last_dep = key
		elif k == "SACRIFICE":
			sac.append(a[1])
	if why == "" and (r_opts.is_empty() or String((r_opts[0] as Array)[0]) != "HOLD"):
		why = "HOLD is not first"
	if why == "" and (holds != 1 or jams > 1):
		why = "%d HOLD and %d JAM rows" % [holds, jams]
	_check_true(t + " response_options order", why == "", why + "   " + _s(r_opts))
	var owned: Dictionary = st.get("owned", {})
	var cells: Array = owned.keys()
	cells.sort_custom(_cell_less)
	var want_sac: Array = []
	for c: Variant in cells:
		if String(owned[c]) != "TAKEN":
			want_sac.append(_cj(c))
	_check(t + " SACRIFICE rows = every owned non-TAKEN cell in cell order", sac, want_sac)


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


## forecast() (L13): per candidate {cand, outcomes: [HOLD for hunt 0, HOLD for hunt 1]}, each equal to
## resolve(HOLD) with that hunt. When the golden response is HOLD, the played candidate's real-hunt outcome is the
## golden tier and after-raid state.
func _check_forecast(t: String, leg: Dictionary, i: int, st: Dictionary, place: Dictionary, cand: int, hunt: int, g: Dictionary) -> void:
	var fc: Array = L8Rules.forecast(leg, i, st, place)
	_check(t + " forecast size", fc.size(), CANDIDATES)
	var played_hold := JSON.stringify(g["response"]) == JSON.stringify(["HOLD"])
	for k in range(mini(fc.size(), CANDIDATES)):
		var tk := "%s forecast cand %d" % [t, k]
		if typeof(fc[k]) != TYPE_DICTIONARY:
			_fail(tk, "entry is not a Dictionary")
			continue
		var e: Dictionary = fc[k]
		var outs_v: Variant = e.get("outcomes")
		var shape_ok: bool = typeof(outs_v) == TYPE_ARRAY and (outs_v as Array).size() == HUNTERS
		if shape_ok:
			for o: Variant in outs_v:
				shape_ok = shape_ok and typeof(o) == TYPE_DICTIONARY and typeof((o as Dictionary).get("state")) == TYPE_DICTIONARY
		_check_true(tk + " has 2 outcomes with states", shape_ok, str(e.keys()))
		if not shape_ok:
			continue
		_check(tk + " cand", e.get("cand"), k)
		var outs: Array = outs_v
		for h in range(HUNTERS):
			var th := "%s hunt %d" % [tk, h]
			var o: Dictionary = outs[h]
			var hres: Dictionary = L8Rules.resolve(leg, i, st, k, h, place, ["HOLD"])
			_check(th + " hold touches", _touches_json(o.get("touches", [])), _touches_json(hres["touches"]))
			_check(th + " hold state", L8Rules.state_to_json(o["state"]), L8Rules.state_to_json(hres["state"]))
			_check(th + " hold tier", o.get("tier"), L8Rules.tier(st, hres["state"], hres["touches"]))
		if k != cand or not played_hold or hunt < 0 or hunt >= HUNTERS:
			continue
		var real: Dictionary = outs[hunt]
		_check(tk + " real hunt hold tier = the golden tier", real.get("tier"), g["tier"])
		_check(tk + " real hunt hold state = the golden after raid", L8Rules.state_to_json(real["state"]), g["after_raid"])


## The options from capture_options (in cell order), and capture() of each = the state with that cell owned OK.
## extra_capture may be kept or consumed by capture() itself (the CAPTURE phase clears it anyway).
func _check_captures(tag: String, leg: Dictionary, r: Dictionary) -> void:
	var st: Dictionary = L8Rules.state_from_json(r["state"])
	_check_state(tag + " state (state_from_json round trip)", st, r["state"])
	_check(tag + " options", _cells_json(L8Rules.capture_options(leg, st)), r["options"])
	var snap := JSON.stringify(L8Rules.state_to_json(st))
	var e_in := int((r["state"] as Dictionary).get("extra_capture", 0))
	for oj: Variant in r["options"]:
		var c := Vector2i(int(oj[0]), int(oj[1]))
		var tc := "%s capture %s" % [tag, str(c)]
		var want: Dictionary = (r["state"] as Dictionary).duplicate(true)
		var owned: Array = (want["owned"] as Array).duplicate(true)
		owned.append([c.x, c.y, "OK"])
		owned.sort_custom(func(a: Variant, b: Variant) -> bool:
			return int(a[1]) < int(b[1]) or (int(a[1]) == int(b[1]) and int(a[0]) < int(b[0])))
		want["owned"] = owned
		var got: Dictionary = L8Rules.capture(leg, st, c)
		var e_out: Variant = L8Rules.state_to_json(got).get("extra_capture")
		_check_true(tc + " extra_capture is kept or consumed",
			typeof(e_out) == TYPE_INT and (int(e_out) == e_in or int(e_out) == 0), "%s from %d" % [str(e_out), e_in])
		if want.has("extra_capture"):
			want["extra_capture"] = e_out
		_check_state(tc, got, want)
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


## Every entry as an int ([] when arr is not an Array).
func _ints(arr: Variant) -> Array:
	var out: Array = []
	if typeof(arr) != TYPE_ARRAY:
		return out
	for e: Variant in arr:
		out.append(int(e))
	return out


## A golden cell ([x, y], "HOME" or null) to the lab form (Vector2i, "HOME" or null).
func _cell(j: Variant) -> Variant:
	match typeof(j):
		TYPE_NIL:
			return null
		TYPE_STRING, TYPE_STRING_NAME:
			return String(j)
		TYPE_ARRAY:
			var a: Array = j
			if a.size() == 2 and _is_num(typeof(a[0])) and _is_num(typeof(a[1])):
				return Vector2i(int(a[0]), int(a[1]))
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


## A golden response to the lab form: ["HOLD"], ["JAM"], ["REDEPLOY", Vector2i, Vector2i],
## ["DEPLOY", type, Vector2i] or ["SACRIFICE", Vector2i].
func _resp(j: Array) -> Array:
	var kind := String(j[0])
	if kind == "REDEPLOY":
		return [kind, _cell(j[1]), _cell(j[2])]
	if kind == "DEPLOY":
		return [kind, String(j[1]), _cell(j[2])]
	if kind == "SACRIFICE":
		return [kind, _cell(j[1])]
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
