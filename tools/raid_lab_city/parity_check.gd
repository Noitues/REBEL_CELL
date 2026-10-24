extends SceneTree
## Parity check of the L8–L14 rules (L8Rules, tools/raid_lab_city/l8_rules.gd) against data/l8_golden.json
## (tools/raid_concepts/l8_golden.py; oracle tools/raid_concepts/sweep_l8.py).
## It checks:
## - the config, and hand_size(heat) = HAND_BASE + (heat >= EXTRA_AT) + (heat >= STRONG_AT) for heat 0..120 (L14 R13);
## - the leg data of every golden leg (leg_from_json), including the L13 `hunter_cands` (2 distinct streets in 0..3)
##   and `hunter_real` (0 or 1), and the L14 `real_b` (a sealed route other than `real`). `hunter_street` must be absent;
## - initial(leg) holds the L14 START_DECK;
## - every step of the greedy and naive line of each leg. Per step:
##   - the state before the capture. The state JSON carries `extra_capture` (an int) and `deck` (cards [id, type, verb]
##     sorted by id), sentries as [x, y, card_id] on non-wound deck cards, a kit with `ghost` only, and no `pool`;
##   - DECAY: for raid > 0, decay(before_capture) gives `after_decay`, keeps every non-wound card and adds one wound per
##     decayed cell. For raid 0, `after_decay` equals `before_capture` and no decay runs;
##   - CAPTURE (L13 R5): `capture` is a list of 0 to 2 cells, checked against capture_options of the current state;
##   - DRAW (L14 R9): hand(leg, raid, before) equals the golden `hand`, has min(hand_size(heat), deck size) distinct
##     deck ids;
##   - `cand` is the real sealed A, `cand_b` the real sealed B (real_b), `hunt` the real hunter street (hunter_real);
##   - the place uses distinct non-wound hand cards on live cells (at most MAX_PLACED). It is among placements() by
##     card signature (type, verb per cell), and placements() are distinct by signature;
##   - response_options() holds the response, in the kind order HOLD, REDEPLOY…, DEPLOY…, SACRIFICE…, JAM. Every row is
##     paid by the response hand (hand minus placed cards): REDEPLOY needs SHIFT, DEPLOY t a non-wound t card, JAM a JAM
##     card (JAM is listed exactly when the response hand holds one);
##   - resolve / trace / hunter_line with (cand, cand_b, hunt), tier and score. Trace beams come in raid order (beam1,
##     extra1, extra2, sealed, sealed_b, hunter), with HOME lost at most once. A raid keeps every non-wound card and adds
##     one wound per newly TAKEN cell (hit, SACRIFICE);
##   - buy_hint(st) = st with Heat + HINT_HEAT; greedy steps: best_response(leg, raid, st, cand, place);
##   - naive: HOLD, no ghost, and the naive placement rule;
##   - the forecast: per A, the HOLD outcome for each (B in route order, hunt) pair, 2 × 2;
##   - between_options() holds the between step (CLEAN only with a wound), between() gives `after` (a build adds
##     [b<k>, t, GUARD], CLEAN drops one wound), and score(after);
##   - SAFE_NEXT (L11) per intensity in the golden `safe_next`, and safe_next(leg, RAIDS, st) at the end of each line;
## - every random raid (with its cand_b and hunt), random between step, random capture check, and the optional
##   random_hands records.
## States are compared as L8Rules.state_to_json against the golden JSON, by deep compare (ints stay ints; floats to
## 1e-6). The first 20 mismatches are printed with their path. Exits 0 only on full parity.
##   godot --headless --path . -s res://tools/raid_lab_city/parity_check.gd

const GOLDEN_PATH := "res://tools/raid_lab_city/data/l8_golden.json"
const RULES_PATH := "res://tools/raid_lab_city/l8_rules.gd"
const MAX_SHOWN := 20
const EPS := 1e-6
const CANDIDATES := 3
const B_CANDS := 2
const HUNTERS := 2
const STREETS := 4
const KNOWN_BEAMS := ["b1", "extra1", "extra2"]
const RESPONSE_RANK := {"HOLD": 0, "REDEPLOY": 1, "DEPLOY": 2, "SACRIFICE": 3, "JAM": 4}
const TYPE_RANK := {"D": 0, "N": 1, "E": 2}
const TRACE_RANK := {"beam1": 0, "extra1": 1, "extra2": 2, "sealed": 3, "sealed_b": 4, "hunter": 5}
const CARD_TYPES := ["D", "N", "E"]
const CARD_VERBS := ["GUARD", "SHIFT", "JAM"]
const START_DECK := [["s0", "D", "GUARD"], ["s1", "D", "GUARD"], ["s2", "N", "GUARD"], ["s3", "N", "GUARD"],
	["s4", "E", "GUARD"], ["s5", "D", "SHIFT"], ["s6", "E", "SHIFT"], ["s7", "N", "JAM"]]

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
var _hand_base: int = 4
var _extra_at: int = 50
var _strong_at: int = 75
var _hint_heat: int = 3
var _legs: Dictionary = {}
var _resp_use: Dictionary = {"HOLD": 0, "REDEPLOY": 0, "DEPLOY": 0, "SACRIFICE": 0, "JAM": 0}
var _rand_resp_use: Dictionary = {"HOLD": 0, "REDEPLOY": 0, "DEPLOY": 0, "SACRIFICE": 0, "JAM": 0}
var _off_option_betweens: int = 0
var _safe_checked: int = 0
var _safe_true: int = 0
var _hands_checked: int = 0
var _best_checked: int = 0
var _hints_checked: int = 0
var _wounds_added: int = 0
var _sealed_b_touches: int = 0
var _random_hands: int = 0
var _rules_script: Script = null
var _placement_params: Array = []
var _placement_probed: bool = false


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
	_hand_base = int(cfg.get("HAND_BASE", 4))
	_extra_at = int(cfg.get("EXTRA_AT", 50))
	_strong_at = int(cfg.get("STRONG_AT", 75))
	_hint_heat = int(cfg.get("HINT_HEAT", 3))
	_check_hand_size()

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
		var tag := "random raid %d (leg %d raid %d cand %d cand_b %s hunt %s)" % [idx, int(r["leg"]), int(r["raid"]) + 1,
			int(r["cand"]), str(r.get("cand_b")), str(r.get("hunt"))]
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
		_check_clean_options(tag, leg, st)
		var rep: Variant = _cell(r["repair"])
		var build: Variant = _str(r["build"])
		var inten := String(r["intensity"])
		var listed := _option_listed(leg, st, rep, build, inten)
		if not listed:
			_off_option_betweens += 1
		var snap := JSON.stringify(L8Rules.state_to_json(st))
		var after: Dictionary = L8Rules.between(leg, st, rep, build, inten)
		_check_state(tag + " after", after, r["after"])
		if listed:
			_check_between_deck(tag, st, after, build)
		_check_true(tag + " between() leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap)

	var rc: Array = gold["random_captures"]
	for idx in range(rc.size()):
		var r: Dictionary = rc[idx]
		var tag := "random capture %d (leg %d)" % [idx, int(r["leg"])]
		var leg := _leg_of(tag, r["leg"])
		if leg.is_empty():
			continue
		_check_captures(tag, leg, r)

	var rh: Array = gold.get("random_hands", [])
	for idx in range(rh.size()):
		var r: Dictionary = rh[idx]
		var tag := "random hand %d (leg %d raid %d)" % [idx, int(r["leg"]), int(r["raid"]) + 1]
		var leg := _leg_of(tag, r["leg"])
		if leg.is_empty():
			continue
		var sj_raw: Variant = r.get("state", r.get("before"))
		if typeof(sj_raw) != TYPE_DICTIONARY:
			_fail(tag, "has no state / before")
			continue
		var st: Dictionary = L8Rules.state_from_json(sj_raw)
		_check_state(tag + " state (state_from_json round trip)", st, sj_raw)
		_check_hand(tag, leg, int(r["raid"]), st, r.get("hand"))
		if r.has("hand_size"):
			_check(tag + " hand_size", L8Rules.hand_size(int(st.get("heat", 0))), r["hand_size"])
		_random_hands += 1
	if not gold.has("random_hands"):
		print("NOTE golden has no random_hands; hands are checked on every golden step and random raid only")

	print("%d lines, %d golden steps (responses %s, %d blocks, %d shielded, %d sealed_b touches, %d decayed cells, %d double captures, %d wounds added, safe_next %d checked / %d safe, %d best_response, %d hints), %d random raids (responses %s), %d random betweens (%d off the between_options list), %d random captures, %d hands checked (%d random hands)"
		% [n_lines, _steps, JSON.stringify(_resp_use), _blocks, _shielded, _sealed_b_touches, _decayed, _double_captures,
			_wounds_added, _safe_checked, _safe_true, _best_checked, _hints_checked, rr.size(),
			JSON.stringify(_rand_resp_use), rb.size(), _off_option_betweens, rc.size(), _hands_checked, _random_hands])
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


## A state against its golden state_json, and checks the L14 state shape.
func _check_state(label: String, st: Dictionary, want: Variant) -> void:
	var sj: Dictionary = L8Rules.state_to_json(st)
	_check(label, sj, want)
	var why := _state_shape(sj)
	_check_true(label + " state shape (ints, deck, card sentries)", why == "", why)


## "" when the state JSON has the L14 shape, else what is wrong: heat, bank, home_hp and extra_capture are ints; no
## `pool`; the kit holds an int `ghost` and no `spoof`; the deck is [id, type, verb] cards, ids strictly increasing
## as strings, a wound being ["w<k>", "-", "WOUND"]; every sentry is [x, y, card_id] on a non-wound deck card.
func _state_shape(sj: Dictionary) -> String:
	for k: String in ["heat", "bank", "home_hp", "extra_capture"]:
		if typeof(sj.get(k)) != TYPE_INT:
			return "%s is a %s" % [k, type_string(typeof(sj.get(k)))]
	if sj.has("pool"):
		return "pool is still in the state (L14: the deck replaces it)"
	var kv: Variant = sj.get("kit")
	if typeof(kv) != TYPE_DICTIONARY:
		return "kit is not a Dictionary"
	var kit: Dictionary = kv
	if kit.has("spoof"):
		return "kit still has spoof (L14: responses are paid with cards)"
	if not kit.has("ghost"):
		return "kit has no ghost"
	for k: Variant in kit:
		if typeof(kit[k]) != TYPE_INT:
			return "kit.%s is a %s" % [str(k), type_string(typeof(kit[k]))]
	var dv: Variant = sj.get("deck")
	if typeof(dv) != TYPE_ARRAY:
		return "deck is not an Array"
	var verbs: Dictionary = {}
	var prev := ""
	var first := true
	for c: Variant in dv:
		if typeof(c) != TYPE_ARRAY or (c as Array).size() != 3:
			return "deck card %s is not [id, type, verb]" % _s(c)
		var a: Array = c
		for e: Variant in a:
			if not _is_str(typeof(e)):
				return "deck card %s has a non-string field" % _s(a)
		var id := String(a[0])
		var ty := String(a[1])
		var vb := String(a[2])
		if not first and not (prev < id):
			return "deck ids are not strictly increasing as strings at %s" % id
		first = false
		prev = id
		if vb == "WOUND":
			if ty != "-" or not id.begins_with("w") or not id.substr(1).is_valid_int():
				return "wound card %s is not [w<k>, -, WOUND]" % _s(a)
		elif not (ty in CARD_TYPES and vb in CARD_VERBS):
			return "deck card %s has an unknown type or verb" % _s(a)
		verbs[id] = vb
	var sv: Variant = sj.get("sentries")
	if typeof(sv) != TYPE_ARRAY:
		return "sentries is not an Array"
	for e: Variant in sv:
		if typeof(e) != TYPE_ARRAY or (e as Array).size() != 3 or not _is_str(typeof((e as Array)[2])):
			return "sentry %s is not [x, y, card_id]" % _s(e)
		var cid := String((e as Array)[2])
		if not verbs.has(cid):
			return "sentry %s holds a card that is not in the deck" % _s(e)
		if String(verbs[cid]) == "WOUND":
			return "sentry %s holds a wound" % _s(e)
	return ""


## The leg's Dictionary by golden seed, or {} (and a failure) when that seed is not a golden leg.
func _leg_of(tag: String, seed_v: Variant) -> Dictionary:
	var s := int(seed_v)
	if not _legs.has(s):
		_fail(tag, "leg seed %d is not among the golden legs %s" % [s, str(_legs.keys())])
		return {}
	return _legs[s]


## hand_size(heat) = HAND_BASE + (heat >= EXTRA_AT) + (heat >= STRONG_AT) for heat 0..120 (L14 R9/R13).
func _check_hand_size() -> void:
	for heat in range(0, 121):
		var want := _hand_base + (1 if heat >= _extra_at else 0) + (1 if heat >= _strong_at else 0)
		_check("hand_size(%d)" % heat, L8Rules.hand_size(heat), want)


## leg_from_json kept every value, exploit, start cell and line of the golden leg, the L13 hunter fields and the
## L14 real_b.
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
		_check_true(t + " golden raid has real_b (L14 R1)", g.has("real_b"), str(g.keys()))
		_check(t + " real_b", rd.get("real_b"), g.get("real_b"))
		var rbv := int(rd.get("real_b", -1))
		_check_true(t + " real_b is a sealed route other than real",
			rbv >= 0 and rbv < CANDIDATES and rbv != int(rd.get("real", -1)), str(rd.get("real_b")))


## Replays one golden line from initial(leg), chaining our own states: decay (raid > 0), capture(s), draw, raid,
## between.
func _replay(tag: String, leg: Dictionary, steps: Array, greedy: bool) -> void:
	_check_true(tag + " has steps", steps.size() > 0)
	var st: Dictionary = L8Rules.initial(leg)
	var init_j: Dictionary = L8Rules.state_to_json(st)
	_check(tag + " initial deck is START_DECK", init_j.get("deck"), START_DECK)
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
		_check_true(t + " golden step has cand_b", s.has("cand_b"))
		if s.has("cand_b"):
			_check(t + " cand_b is the real B (real_b)", int(s["cand_b"]), rd.get("real_b"))
		_check_true(t + " golden step has hunt", s.has("hunt"))
		if s.has("hunt"):
			_check(t + " hunt is the real hunter street", int(s["hunt"]), rd.get("hunter_real"))
		_check_true(t + " golden step has hand", s.has("hand"))
		var place := _place(s["place"])
		var resp := _resp(s["response"])
		var rk := String(resp[0])
		_resp_use[rk] = int(_resp_use.get(rk, 0)) + 1
		if not greedy:
			_check(t + " naive never responds", _resp_json(resp), ["HOLD"])
			_check(t + " naive never ghosts", _cj(place["ghost"]), null)
			_check_naive_place(t, leg, st, _strs(L8Rules.hand(leg, i, st)), place)
		var ns := _raid(t, leg, i, st, s)
		_check_forecast(t, leg, i, st, place, int(s["cand"]), int(s.get("cand_b", -1)), int(s.get("hunt", 0)), s)
		if greedy:
			var snap_b := JSON.stringify(L8Rules.state_to_json(st))
			var br: Array = _resp_json(L8Rules.best_response(leg, i, st, int(s["cand"]), place))
			var want_br: Variant = s["best_response"] if s.has("best_response") else s["response"]
			_check(t + " best_response (planner rule)", br, want_br)
			_check_true(t + " best_response() leaves the state untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap_b)
			_best_checked += 1
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
			_check_clean_options(t, leg, ns)
			_check_true(t + " between step is one of between_options()", _option_listed(leg, ns, rep, build, inten),
				_s([_cj(rep), build, inten]))
			var snap := JSON.stringify(L8Rules.state_to_json(ns))
			after = L8Rules.between(leg, ns, rep, build, inten)
			_check_true(t + " between() leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(ns)) == snap)
			_check_between_deck(t, ns, after, build)
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
## raid 0 no decay runs, and the golden `after_decay` must equal `before_capture`. A decayed cell loses its sentry,
## its card stays in the deck, and each decayed cell adds one wound (L14 R9). Returns the state for capture.
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
	_check_wounds(t + " decay", st, dec)
	var sj_before: Dictionary = L8Rules.state_to_json(st)
	var sj_after: Dictionary = L8Rules.state_to_json(dec)
	_check(t + " decay keeps extra_capture", sj_after.get("extra_capture"), sj_before.get("extra_capture"))
	if has_ad:
		_check_state(t + " after decay", dec, s["after_decay"])
	return dec


## One raid from st against a golden raid record (place, cand, cand_b, hunt, response, hand, trace, hunter, tier,
## after_raid, score_raid). Returns our state after the raid.
func _raid(t: String, leg: Dictionary, i: int, st: Dictionary, g: Dictionary) -> Dictionary:
	var place := _place(g["place"])
	var cand := int(g["cand"])
	var hunt_ok := g.has("hunt")
	_check_true(t + " golden raid has hunt", hunt_ok)
	var hunt := int(g["hunt"]) if hunt_ok else 0
	var cb_ok := g.has("cand_b")
	_check_true(t + " golden raid has cand_b", cb_ok)
	var cand_b := int(g["cand_b"]) if cb_ok else int(_other_routes(cand)[0])
	var resp := _resp(g["response"])
	_check_true(t + " cand is a candidate", cand >= 0 and cand < CANDIDATES, str(cand))
	_check_true(t + " cand_b is another candidate", cand_b >= 0 and cand_b < CANDIDATES and cand_b != cand,
		"cand %d cand_b %d" % [cand, cand_b])
	_check_true(t + " hunt is 0 or 1", hunt >= 0 and hunt < HUNTERS, str(hunt))
	var snap_st := JSON.stringify(L8Rules.state_to_json(st))

	# DRAW and PLAN (L14 R9).
	var hand_raw: Variant = _check_hand(t, leg, i, st, g.get("hand"))
	var hand: Array = _strs(hand_raw)
	var hand_set: Dictionary = {}
	for h: Variant in hand:
		hand_set[String(h)] = true
	var cards := _cards(st)
	var owned: Dictionary = st.get("owned", {})
	var ghosts := int((st.get("kit", {}) as Dictionary).get("ghost", 0))
	var pp := _place_problem(place, hand_set, cards, owned, ghosts)
	_check_true(t + " place uses distinct non-wound hand cards on live cells (at most MAX_PLACED)", pp == "", pp)
	var pkey := JSON.stringify(_place_json(place))
	var psig := _place_sig(place, cards)
	var found := false
	var sigs: Dictionary = {}
	var dup := ""
	var bad := ""
	for p: Variant in _placements(leg, i, st, hand_raw):
		var sg := _place_sig(p, cards)
		if sigs.has(sg) and dup == "":
			dup = sg
		sigs[sg] = true
		if sg == psig:
			found = true
		if bad == "":
			var pr := _place_problem(p, hand_set, cards, owned, ghosts)
			if pr != "":
				bad = pr + "   " + _s(_place_json(p))
	_check_true(t + " place is one of placements() (by card signature)", found, psig)
	_check_true(t + " placements() are distinct by card signature", dup == "", dup)
	_check_true(t + " every placements() entry is legal", bad == "", bad)

	# RESPONSE: options, order, cards.
	var rkey := JSON.stringify(_resp_json(resp))
	var r_opts: Array = []
	for r: Variant in L8Rules.response_options(leg, i, st, cand, place):
		r_opts.append(_resp_json(r))
	_check_true(t + " response is one of response_options()", _has(r_opts, _resp_json(resp)), "%s not in %s" % [rkey, _s(r_opts)])
	_check_response_order(t, st, r_opts)
	var placed_ids: Dictionary = {}
	for c: Variant in (place["sentries"] as Dictionary):
		placed_ids[String(place["sentries"][c])] = true
	var rhand: Array = []
	for h: Variant in hand:
		if not placed_ids.has(String(h)):
			rhand.append(String(h))
	_check_response_cards(t, r_opts, rhand, cards)
	_check_hint(t, st)

	# RESOLVE.
	var res: Dictionary = L8Rules.resolve(leg, i, st, cand, cand_b, hunt, place, resp)
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
	var tr_j := _trace_json(L8Rules.trace(leg, i, st, cand, cand_b, hunt, place, resp))
	_check(t + " trace", tr_j, g["trace"])
	_check_trace_shape(t, tr_j)
	var hl_j: Variant = _line_json(L8Rules.hunter_line(leg, i, st, cand, cand_b, hunt, place, resp))
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
	_check_wounds(t + " the raid", st, ns)
	var ns_owned: Dictionary = ns.get("owned", {})
	var ns_sent: Dictionary = ns.get("sentries", {})
	for c: Variant in ns_sent:
		_check_true("%s after raid no sentry on TAKEN %s" % [t, str(c)], String(ns_owned.get(c, "")) != "TAKEN")
	_check_score(t + " score after raid", L8Rules.score(leg, ns), g["score_raid"])
	_check_true(t + " the raid leaves the state before untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap_st)
	_check_true(t + " the raid leaves the place untouched", JSON.stringify(_place_json(place)) == pkey)
	return ns


## hand(leg, raid, st) (L14 R9 DRAW): equals want when given; holds min(hand_size(heat), deck size) distinct deck ids;
## the Heat is the draw-time Heat, without the ghost. Returns the raw hand as L8Rules gave it ([] when not an Array).
func _check_hand(t: String, leg: Dictionary, i: int, st: Dictionary, want: Variant) -> Variant:
	var sj: Dictionary = L8Rules.state_to_json(st)
	var snap := JSON.stringify(sj)
	var raw: Variant = L8Rules.hand(leg, i, st)
	_check_true(t + " hand() leaves the state untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap)
	_hands_checked += 1
	if typeof(raw) != TYPE_ARRAY:
		_fail(t + " hand", "is a %s, want an Array of card ids" % type_string(typeof(raw)))
		return []
	var got := _strs(raw)
	if typeof(want) != TYPE_NIL:
		_check(t + " hand", got, want)
	var deck: Array = sj.get("deck", [])
	var ids: Dictionary = {}
	for c: Variant in deck:
		ids[String(c[0])] = true
	var size := mini(int(L8Rules.hand_size(int(sj.get("heat", 0)))), deck.size())
	_check(t + " hand size = min(hand_size(heat at draw), deck size)", got.size(), size)
	var seen: Dictionary = {}
	var why := ""
	for h: Variant in got:
		var id := String(h)
		if not ids.has(id):
			why = "%s is not in the deck" % id
			break
		if seen.has(id):
			why = "%s is drawn twice" % id
			break
		seen[id] = true
	_check_true(t + " hand ids are distinct deck cards", why == "", why + "   " + _s(got))
	return raw


## buy_hint(st) (L14 R14) = st with Heat + HINT_HEAT, nothing else changed, the input untouched.
func _check_hint(t: String, st: Dictionary) -> void:
	var sj: Dictionary = L8Rules.state_to_json(st)
	var snap := JSON.stringify(sj)
	var h: Dictionary = L8Rules.buy_hint(st)
	var want: Dictionary = sj.duplicate(true)
	want["heat"] = int(want["heat"]) + _hint_heat
	_check_state(t + " buy_hint", h, want)
	_check_true(t + " buy_hint() leaves the state untouched", JSON.stringify(L8Rules.state_to_json(st)) == snap)
	_hints_checked += 1


## The naive placement (L14 R9): the first min(MAX_PLACED, live) non-wound hand cards in hand order, on live cells by
## descending value then cell order; no ghost.
func _check_naive_place(t: String, leg: Dictionary, st: Dictionary, hand: Array, place: Dictionary) -> void:
	var cards := _cards(st)
	var owned: Dictionary = st.get("owned", {})
	var values: Dictionary = leg.get("values", {})
	var live: Array = []
	for c: Variant in owned:
		if String(owned[c]) != "TAKEN":
			live.append(c)
	live.sort_custom(func(a: Variant, b: Variant) -> bool:
		var va := int(values.get(a, 0))
		var vb := int(values.get(b, 0))
		return va > vb or (va == vb and _cell_less(a, b)))
	var cap := _max_placed if _max_placed >= 0 else 2
	var n := mini(cap, live.size())
	var picks: Array = []
	for h: Variant in hand:
		if picks.size() >= n:
			break
		var cv: Array = cards.get(String(h), ["", "WOUND"])
		if String(cv[1]) != "WOUND":
			picks.append(String(h))
	var want_sent: Dictionary = {}
	for j in range(picks.size()):
		want_sent[live[j]] = picks[j]
	_check(t + " naive placement rule", _place_json(place), _place_json({"sentries": want_sent, "ghost": null}))


## Every response row is paid by the response hand (L14 R9): REDEPLOY needs a SHIFT card, DEPLOY t a non-wound card
## of type t, JAM a JAM card; JAM is listed exactly when the response hand holds a JAM card.
func _check_response_cards(t: String, r_opts: Array, rhand: Array, cards: Dictionary) -> void:
	var has_shift := false
	var has_jam := false
	var types: Dictionary = {}
	for h: Variant in rhand:
		var cv: Array = cards.get(String(h), ["", "WOUND"])
		var vb := String(cv[1])
		if vb == "SHIFT":
			has_shift = true
		elif vb == "JAM":
			has_jam = true
		if vb != "WOUND":
			types[String(cv[0])] = true
	var why := ""
	var jam_listed := false
	for o: Variant in r_opts:
		var a: Array = o
		var k := String(a[0])
		if k == "REDEPLOY" and not has_shift:
			why = "%s without a SHIFT card" % _s(a)
		elif k == "DEPLOY" and not types.has(String(a[1])):
			why = "%s without a %s card" % [_s(a), String(a[1])]
		elif k == "JAM":
			jam_listed = true
			if not has_jam:
				why = "JAM without a JAM card"
		if why != "":
			break
	if why == "" and has_jam and not jam_listed:
		why = "a JAM card is in the response hand but there is no JAM row"
	_check_true(t + " responses are paid by the response hand", why == "", why + "   hand " + _s(rhand))


## Trace beams come in raid order (beam1, extra1, extra2, sealed, sealed_b, hunter), and HOME is lost at most once.
func _check_trace_shape(t: String, tr_j: Array) -> void:
	var why := ""
	var prev := -1
	var homes := 0
	for e: Variant in tr_j:
		var b := String(e[0])
		if not TRACE_RANK.has(b):
			why = "unknown beam %s" % b
			break
		var r := int(TRACE_RANK[b])
		if r < prev:
			why = "%s comes after a later beam" % _s(e)
			break
		prev = r
		if String(e[2]) == "home":
			homes += 1
		if b == "sealed_b":
			_sealed_b_touches += 1
	if why == "" and homes > 1:
		why = "HOME lost %d times in one raid" % homes
	_check_true(t + " trace beams in raid order, HOME lost at most once", why == "", why + "   " + _s(tr_j))


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


## L13 R3: the sacrificed cell ends TAKEN without a sentry, and neither sealed beam (A, B) records a HOME loss.
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
		_check_true(t + " SACRIFICE: the sealed beams do not harm HOME",
			not ((String(e[0]) == "sealed" or String(e[0]) == "sealed_b") and String(e[2]) == "home"), _s(e))


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


## A step that may turn cells TAKEN (decay, raid) keeps every non-wound card and adds one ["w<k>", "-", "WOUND"]
## per newly TAKEN cell, with distinct ids (L14 R9).
func _check_wounds(t: String, before: Dictionary, after: Dictionary) -> void:
	var bj: Dictionary = L8Rules.state_to_json(before)
	var aj: Dictionary = L8Rules.state_to_json(after)
	var bd: Array = bj.get("deck", [])
	var ad: Array = aj.get("deck", [])
	_check(t + " keeps every non-wound card", _non_wounds(ad), _non_wounds(bd))
	var newly := _newly_taken(before, after)
	var wb := _wounds(bd)
	var wa := _wounds(ad)
	_wounds_added += maxi(0, wa - wb)
	_check(t + " adds one wound per newly TAKEN cell", wa, wb + newly)
	var ids: Dictionary = {}
	var why := ""
	for c: Variant in ad:
		if String(c[2]) != "WOUND":
			continue
		var id := String(c[0])
		if ids.has(id):
			why = "wound %s twice" % id
			break
		ids[id] = true
	_check_true(t + " wound ids are distinct", why == "", why)


## The between step's deck change (L14 R9): a type build adds ["b<k>", t, "GUARD"] (k = built cards so far), CLEAN
## drops one wound, anything else keeps the deck.
func _check_between_deck(t: String, before: Dictionary, after: Dictionary, build: Variant) -> void:
	var bj: Dictionary = L8Rules.state_to_json(before)
	var aj: Dictionary = L8Rules.state_to_json(after)
	var bd: Array = bj.get("deck", [])
	var ad: Array = aj.get("deck", [])
	var want_nw := _non_wounds(bd)
	var wounds_want := _wounds(bd)
	var b := "" if typeof(build) == TYPE_NIL else String(build)
	if b in CARD_TYPES:
		want_nw.append(["b%d" % _built(bd), b, "GUARD"])
		want_nw.sort_custom(_card_less)
	elif b == "CLEAN":
		wounds_want -= 1
	_check(t + " between deck: non-wound cards", _non_wounds(ad), want_nw)
	_check(t + " between deck: wounds", _wounds(ad), wounds_want)


## between_options() offers CLEAN only when the deck holds a wound, and builds only D, N, E or CLEAN.
func _check_clean_options(t: String, leg: Dictionary, st: Dictionary) -> void:
	var sj: Dictionary = L8Rules.state_to_json(st)
	var w := _wounds(sj.get("deck", []))
	var why := ""
	for o: Variant in L8Rules.between_options(leg, st):
		var bv: Variant = _str(o[1])
		if typeof(bv) == TYPE_NIL:
			continue
		var b := String(bv)
		if b == "CLEAN" and w == 0:
			why = "CLEAN offered with no wound"
			break
		if not (b in CARD_TYPES or b == "CLEAN"):
			why = "unknown build %s" % b
			break
	_check_true(t + " between_options builds (CLEAN only with a wound)", why == "", why)


## score(mid = true) adds KIT_VALUE per unspent ghost and per built card (a breach stays -BREACH).
func _check_mid_score(t: String, leg: Dictionary, ns: Dictionary, after_j: Dictionary) -> void:
	var base := L8Rules.score(leg, ns)
	var want := float(base)
	if int(after_j["home_hp"]) > 0:
		var n := int((after_j["kit"] as Dictionary).get("ghost", 0))
		n += _built(after_j.get("deck", []))
		want += _kit_value * n
	_check_score(t + " mid-leg score", L8Rules.score(leg, ns, true), want)


## forecast() (L14 R1): per A {cand, outcomes}, outcomes[b][hunt] for b over the two other routes in route order and
## hunt 0, 1, each equal to resolve(HOLD) with that (A, B, hunt). When the golden response is HOLD, the played
## (cand_b, hunt) outcome is the golden tier and after-raid state.
func _check_forecast(t: String, leg: Dictionary, i: int, st: Dictionary, place: Dictionary, cand: int, cand_b: int, hunt: int, g: Dictionary) -> void:
	var fc: Array = L8Rules.forecast(leg, i, st, place)
	_check(t + " forecast size", fc.size(), CANDIDATES)
	var played_hold := JSON.stringify(g["response"]) == JSON.stringify(["HOLD"])
	for k in range(mini(fc.size(), CANDIDATES)):
		var tk := "%s forecast A %d" % [t, k]
		if typeof(fc[k]) != TYPE_DICTIONARY:
			_fail(tk, "entry is not a Dictionary")
			continue
		var e: Dictionary = fc[k]
		var outs_v: Variant = e.get("outcomes")
		var shape_ok: bool = typeof(outs_v) == TYPE_ARRAY and (outs_v as Array).size() == B_CANDS
		if shape_ok:
			for row: Variant in outs_v:
				shape_ok = shape_ok and typeof(row) == TYPE_ARRAY and (row as Array).size() == HUNTERS
				if shape_ok:
					for o: Variant in row:
						shape_ok = shape_ok and typeof(o) == TYPE_DICTIONARY and typeof((o as Dictionary).get("state")) == TYPE_DICTIONARY
		_check_true(tk + " has 2 × 2 (B, hunt) outcomes with states", shape_ok, str(e.keys()))
		if not shape_ok:
			continue
		_check(tk + " cand", e.get("cand"), k)
		var outs: Array = outs_v
		var bs := _other_routes(k)
		for bi in range(B_CANDS):
			var row: Array = outs[bi]
			for h in range(HUNTERS):
				var th := "%s B %d hunt %d" % [tk, int(bs[bi]), h]
				var o: Dictionary = row[h]
				var hres: Dictionary = L8Rules.resolve(leg, i, st, k, int(bs[bi]), h, place, ["HOLD"])
				_check(th + " hold touches", _touches_json(o.get("touches", [])), _touches_json(hres["touches"]))
				_check(th + " hold state", L8Rules.state_to_json(o["state"]), L8Rules.state_to_json(hres["state"]))
				_check(th + " hold tier", o.get("tier"), L8Rules.tier(st, hres["state"], hres["touches"]))
		var bi_real := bs.find(cand_b)
		if k != cand or not played_hold or bi_real < 0 or hunt < 0 or hunt >= HUNTERS:
			continue
		var real: Dictionary = (outs[bi_real] as Array)[hunt]
		_check(tk + " real (B, hunt) hold tier = the golden tier", real.get("tier"), g["tier"])
		_check(tk + " real (B, hunt) hold state = the golden after raid", L8Rules.state_to_json(real["state"]), g["after_raid"])


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


# --- placements (signature not fixed by L14: called by parameter name) ----------------------------------------------

## L8Rules.placements, called with arguments matched to its parameter names (leg, raid, st, hand). Unknown names fall
## back to position by count: 2 = (leg, st), 3 = (leg, raid, st), 4 = (leg, raid, st, hand).
func _placements(leg: Dictionary, i: int, st: Dictionary, hand_raw: Variant) -> Array:
	if not _placement_probed:
		_placement_probed = true
		_placement_params = _arg_names("placements")
		if _placement_params.is_empty():
			_fail("placements", "L8Rules.placements was not found in " + RULES_PATH)
	if _placement_params.is_empty():
		return []
	var args: Array = []
	var known := true
	for n: Variant in _placement_params:
		match String(n):
			"leg":
				args.append(leg)
			"raid", "r", "i", "ri", "raid_i":
				args.append(i)
			"st", "state", "s":
				args.append(st)
			"hand", "h", "hand_ids":
				args.append(hand_raw)
			_:
				known = false
	if not known:
		match _placement_params.size():
			2:
				args = [leg, st]
			3:
				args = [leg, i, st]
			_:
				args = [leg, i, st, hand_raw]
	var res: Variant = _rules_script.callv("placements", args)
	if typeof(res) != TYPE_ARRAY:
		_fail("placements", "returned a %s, want an Array" % type_string(typeof(res)))
		return []
	return res


## The parameter names of a static L8Rules function ([] when it is missing).
func _arg_names(fname: String) -> Array:
	var out: Array = []
	if _rules_script == null:
		_rules_script = load(RULES_PATH)
	if _rules_script == null:
		return out
	for m: Dictionary in _rules_script.get_script_method_list():
		if String(m.get("name", "")) == fname:
			for a: Variant in m.get("args", []):
				out.append(String((a as Dictionary).get("name", "")))
			break
	return out


## "" when a place is legal for the hand (L14 R9): at most MAX_PLACED sentries on distinct live cells, each a distinct
## non-wound hand card; the ghost is null, HOME or a live cell, and only with a ghost in the kit.
func _place_problem(p: Variant, hand_set: Dictionary, cards: Dictionary, owned: Dictionary, ghosts: int) -> String:
	if typeof(p) != TYPE_DICTIONARY:
		return "place is not a Dictionary"
	var d: Dictionary = p
	var sent: Dictionary = d.get("sentries", {})
	var cap := _max_placed if _max_placed >= 0 else 2
	if sent.size() > cap:
		return "%d sentries > MAX_PLACED %d" % [sent.size(), cap]
	var used: Dictionary = {}
	for c: Variant in sent:
		if typeof(c) != TYPE_VECTOR2I:
			return "sentry key %s is not a cell" % str(c)
		var id := String(sent[c])
		if String(owned.get(c, "")) in ["", "TAKEN"]:
			return "sentry on a dead cell %s" % str(c)
		if not hand_set.has(id):
			return "card %s is not in the hand" % id
		var cv: Array = cards.get(id, ["", "WOUND"])
		if String(cv[1]) == "WOUND":
			return "card %s is a wound" % id
		if used.has(id):
			return "card %s placed twice" % id
		used[id] = true
	var gh: Variant = d.get("ghost")
	if typeof(gh) != TYPE_NIL:
		if ghosts <= 0:
			return "ghost placed with no ghost in the kit"
		if typeof(gh) == TYPE_VECTOR2I:
			if String(owned.get(gh, "")) in ["", "TAKEN"]:
				return "ghost on a dead cell %s" % str(gh)
		elif not (_is_str(typeof(gh)) and String(gh) == "HOME"):
			return "ghost %s is not a cell or HOME" % str(gh)
	return ""


## A place's card signature: per cell (in cell order) the placed card's (type, verb), and the ghost.
func _place_sig(p: Variant, cards: Dictionary) -> String:
	if typeof(p) != TYPE_DICTIONARY:
		return "?"
	var d: Dictionary = p
	var sent: Dictionary = d.get("sentries", {})
	var keys: Array = sent.keys()
	keys.sort_custom(_cell_less)
	var out: Array = []
	for c: Variant in keys:
		var v: Vector2i = c
		var cv: Array = cards.get(String(sent[c]), ["?", "?"])
		out.append([v.x, v.y, String(cv[0]), String(cv[1])])
	return JSON.stringify([out, _cj(d.get("ghost"))])


# --- deck helpers -------------------------------------------------------------------------------------------------

## The state's deck as {card_id: [type, verb]}.
func _cards(st: Dictionary) -> Dictionary:
	var out: Dictionary = {}
	var sj: Dictionary = L8Rules.state_to_json(st)
	for c: Variant in sj.get("deck", []):
		var a: Array = c
		out[String(a[0])] = [String(a[1]), String(a[2])]
	return out


## The non-wound cards of a JSON deck as [id, type, verb] Strings, sorted by id.
func _non_wounds(deck: Array) -> Array:
	var out: Array = []
	for c: Variant in deck:
		if String(c[2]) != "WOUND":
			out.append([String(c[0]), String(c[1]), String(c[2])])
	out.sort_custom(_card_less)
	return out


## The number of wound cards in a JSON deck.
func _wounds(deck: Array) -> int:
	var n := 0
	for c: Variant in deck:
		if String(c[2]) == "WOUND":
			n += 1
	return n


## The number of built cards (ids b<k>) in a JSON deck.
func _built(deck: Array) -> int:
	var n := 0
	for c: Variant in deck:
		if String(c[0]).begins_with("b"):
			n += 1
	return n


## The number of cells TAKEN in after that were not TAKEN in before.
func _newly_taken(before: Dictionary, after: Dictionary) -> int:
	var bo: Dictionary = before.get("owned", {})
	var ao: Dictionary = after.get("owned", {})
	var n := 0
	for c: Variant in ao:
		if String(ao[c]) == "TAKEN" and String(bo.get(c, "")) != "TAKEN":
			n += 1
	return n


func _card_less(a: Variant, b: Variant) -> bool:
	return String(a[0]) < String(b[0])


## The two sealed routes other than k, in route order.
func _other_routes(k: int) -> Array:
	var out: Array = []
	for j in range(CANDIDATES):
		if j != k:
			out.append(j)
	return out


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
	if typeof(arr) != TYPE_ARRAY:
		return out
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


## A golden place ({sentries: [[x, y, card_id]], ghost}) to the lab form ({sentries: {Vector2i: card_id}, ghost}).
func _place(j: Dictionary) -> Dictionary:
	var sent: Dictionary = {}
	for e: Variant in j["sentries"]:
		sent[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	return {"sentries": sent, "ghost": _cell(j["ghost"])}


## A lab place to its canonical JSON form: sentries [x, y, card_id] in cell order (y, then x), whatever the dict order.
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
