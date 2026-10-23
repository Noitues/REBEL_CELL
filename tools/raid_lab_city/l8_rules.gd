class_name L8Rules
extends RefCounted
## The round-8 (L8) city-raid rules, ported from tools/raid_concepts/sweep_l8.py (the oracle). Covers capture,
## placements, the launch (beam 1, extras, sealed, hunter), responses, between, tier, score and forecast. Pure and
## deterministic: no randomness, no nodes. Cells are Vector2i (x 0..3, y 0..2); HOME is the String "HOME".
## Every enumeration walks CELLS (y, then x), never dictionary order. Data shapes: docs/handoff/raid_lab_l8/GD_CONTRACT.md.

# Grid: cell order is y, then x.
const W := 4
const H := 3
const CELLS: Array = [
	Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0), Vector2i(3, 0),
	Vector2i(0, 1), Vector2i(1, 1), Vector2i(2, 1), Vector2i(3, 1),
	Vector2i(0, 2), Vector2i(1, 2), Vector2i(2, 2), Vector2i(3, 2),
]
const NEIGHBORS: Array = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]

# Beam types and display names.
const TYPES: Array = ["D", "N", "E"]
const TYPE_NAMES: Dictionary = {"D": "DRONE", "N": "NETRUNNER", "E": "ENFORCER"}
const ROUTE_NAMES: Array = ["NORTH", "MID", "SOUTH"]
const BEAMS: Array = ["beam1", "extra1", "extra2", "sealed", "hunter"]

# Leg shape.
const VALUES: Array = [4, 6, 8, 10, 12]
const EXPLOITS := 3
const START_CELLS := 2
const RAIDS := 3
const CANDIDATES := 3

# Cell statuses.
const HOME := "HOME"
const OK := "OK"
const DOWN := "DOWN"
const TAKEN := "TAKEN"

# Economy and Heat.
const START_BANK := 10
const START_HEAT := 44
const EXTRA_AT := 50
const STRONG_AT := 75
const HOME_HP := 3
const GHOST_HEAT := 5
const SPOOF_HEAT := 2
const EVADE_HEAT := 10
const SENTRY_PRICE := 4
const REPAIR_DIV := 2
const INCOME_DIV := 3
const POOL_START: Dictionary = {"D": 1, "N": 1, "E": 1}
const KIT_START: Dictionary = {"ghost": 2, "spoof": 2}
const INTENSITY_ORDER: Array = ["LOW", "NORMAL", "HOT"]
const INTENSITY: Dictionary = {"LOW": [6, 0.5], "NORMAL": [12, 1.0], "HOT": [18, 1.5]}

# Score.
const EXPLOIT_BONUS := 6
const HOME_LOSS_COST := 8
const HEAT_CARRY := 1.0
const BREACH := 100
const KIT_VALUE := 2.5	# planner heuristic only: an unspent kit item (ghost, spoof, pool sentry) mid-leg
const EPS := 1e-9		# float ties keep the earlier option


# ---------------------------------------------------------------- helpers

## Integer division (python //); values are never negative.
@warning_ignore("integer_division")
static func idiv(a: int, b: int) -> int:
	return a / b


## All 12 cells in python CELLS order (y, then x).
static func cells() -> Array:
	return CELLS.duplicate()


## sweep_l8.config(): the tuning constants as a JSON-compatible dictionary.
static func config() -> Dictionary:
	var inten := {}
	for k: String in INTENSITY_ORDER:
		inten[k] = (INTENSITY[k] as Array).duplicate()
	return {"W": W, "H": H, "TYPES": TYPES.duplicate(), "VALUES": VALUES.duplicate(), "EXPLOITS": EXPLOITS,
		"START_CELLS": START_CELLS, "RAIDS": RAIDS, "START_BANK": START_BANK, "START_HEAT": START_HEAT,
		"EXTRA_AT": EXTRA_AT, "STRONG_AT": STRONG_AT, "HOME_HP": HOME_HP, "GHOST_HEAT": GHOST_HEAT,
		"SPOOF_HEAT": SPOOF_HEAT, "EVADE_HEAT": EVADE_HEAT, "SENTRY_PRICE": SENTRY_PRICE,
		"POOL_START": POOL_START.duplicate(), "KIT_START": KIT_START.duplicate(), "INTENSITY": inten,
		"EXPLOIT_BONUS": EXPLOIT_BONUS, "HOME_LOSS_COST": HOME_LOSS_COST, "HEAT_CARRY": HEAT_CARRY,
		"BREACH": BREACH, "KIT_VALUE": KIT_VALUE}


static func _fail(msg: String) -> void:
	push_error("L8Rules: " + msg)


static func _is_none(v: Variant) -> bool:
	return typeof(v) == TYPE_NIL


## Type-safe equality (a Vector2i never equals "HOME", and neither raises).
static func _same(a: Variant, b: Variant) -> bool:
	if typeof(a) == TYPE_STRING_NAME:
		a = String(a)
	if typeof(b) == TYPE_STRING_NAME:
		b = String(b)
	return typeof(a) == typeof(b) and a == b


## Normalizes a cell from code or JSON: null, "HOME", Vector2i, [x, y], or a "x,y" string.
static func to_cell(v: Variant) -> Variant:
	match typeof(v):
		TYPE_NIL:
			return null
		TYPE_VECTOR2I:
			return v
		TYPE_VECTOR2:
			return Vector2i(int((v as Vector2).x), int((v as Vector2).y))
		TYPE_ARRAY, TYPE_PACKED_INT32_ARRAY, TYPE_PACKED_FLOAT64_ARRAY:
			return Vector2i(int(v[0]), int(v[1]))
		TYPE_STRING, TYPE_STRING_NAME:
			var s := String(v)
			if s == HOME:
				return HOME
			var p := s.replace("[", "").replace("]", "").replace("(", "").replace(")", "").split(",")
			if p.size() == 2:
				return Vector2i(p[0].strip_edges().to_int(), p[1].strip_edges().to_int())
			return s
	return v


## A cell (or HOME / null) in JSON form: [x, y], "HOME" or null.
static func cell_to_json(c: Variant) -> Variant:
	if typeof(c) == TYPE_VECTOR2I:
		return [(c as Vector2i).x, (c as Vector2i).y]
	return c


static func in_grid(c: Variant) -> bool:
	if typeof(c) != TYPE_VECTOR2I:
		return false
	var v: Vector2i = c
	return v.x >= 0 and v.x < W and v.y >= 0 and v.y < H


## A copy of d with its cell keys re-inserted in cell order (python _otup); non-grid keys are dropped.
static func _ordered(d: Dictionary) -> Dictionary:
	var out := {}
	for c: Vector2i in CELLS:
		if d.has(c):
			out[c] = d[c]
	return out


## The cells of arr in cell order (duplicates dropped).
static func _sort_cells(arr: Array) -> Array:
	var out: Array = []
	for c: Vector2i in CELLS:
		if arr.has(c):
			out.append(c)
	return out


## The keys of a cell-keyed dictionary in cell order.
static func sorted_cells(d: Dictionary) -> Array:
	var out: Array = []
	for c: Vector2i in CELLS:
		if d.has(c):
			out.append(c)
	return out


static func _pool_t(d: Dictionary) -> Dictionary:
	return {"D": int(d.get("D", 0)), "N": int(d.get("N", 0)), "E": int(d.get("E", 0))}


static func _kit_t(d: Dictionary) -> Dictionary:
	return {"ghost": int(d.get("ghost", 0)), "spoof": int(d.get("spoof", 0))}


static func _status(owned: Dictionary, c: Variant) -> String:
	return String(owned.get(c, ""))


static func _live_status(s: String) -> bool:
	return s == OK or s == DOWN


## True when the cell is owned and not TAKEN.
static func is_live(st: Dictionary, c: Variant) -> bool:
	return _live_status(_status(st["owned"], c))


## The owned non-TAKEN cells, in cell order (python _live).
static func live_cells(st: Dictionary) -> Array:
	var owned: Dictionary = st["owned"]
	var out: Array = []
	for c: Vector2i in CELLS:
		if _live_status(_status(owned, c)):
			out.append(c)
	return out


## A deep copy of a state.
static func copy_state(st: Dictionary) -> Dictionary:
	return {"heat": int(st["heat"]), "bank": int(st["bank"]), "home_hp": int(st["home_hp"]),
		"owned": _ordered(st["owned"]), "sentries": _ordered(st["sentries"]), "pool": _pool_t(st["pool"]),
		"kit": _kit_t(st["kit"])}


## The repair cost of a cell (v // 2).
static func repair_cost(leg: Dictionary, c: Vector2i) -> int:
	return idiv(int(leg["values"][c]), REPAIR_DIV)


## How many extra known beams fire at this launch Heat: 0, 1 (>= EXTRA_AT) or 2 (>= STRONG_AT).
static func extra_count(heat: int) -> int:
	if heat >= STRONG_AT:
		return 2
	if heat >= EXTRA_AT:
		return 1
	return 0


## The Heat a raid launches at: the state's Heat plus GHOST_HEAT when a ghost is placed.
static func launch_heat(st: Dictionary, place: Dictionary) -> int:
	return int(st["heat"]) + (0 if _is_none(to_cell(place.get("ghost"))) else GHOST_HEAT)


## Income for the owned map: int(sum(v // 3 over OK cells) * the intensity multiplier).
static func income(leg: Dictionary, owned: Dictionary, intensity: String) -> int:
	var vals: Dictionary = leg["values"]
	var sum := 0
	for c: Vector2i in CELLS:
		if _status(owned, c) == OK:
			sum += idiv(int(vals[c]), INCOME_DIV)
	return int(sum * float(INTENSITY[intensity][1]))


# ---------------------------------------------------------------- lines

## A ROUTE line along row y (x = 3 -> 0, then HOME).
static func route(y: int, t: String) -> Dictionary:
	var cs: Array = []
	for x in range(W - 1, -1, -1):
		cs.append(Vector2i(x, y))
	return {"kind": "ROUTE", "index": y, "cells": cs, "type": t, "home": true}


## A STREET line along column x (y 0 -> 2 when down, else 2 -> 0); it never reaches HOME.
static func street(x: int, down: bool, t: String) -> Dictionary:
	var cs: Array = []
	if down:
		for y in range(H):
			cs.append(Vector2i(x, y))
	else:
		for y in range(H - 1, -1, -1):
			cs.append(Vector2i(x, y))
	return {"kind": "STREET", "index": x, "cells": cs, "type": t, "home": false}


## A line from its JSON form {kind, index, cells: [[x, y]], type, home}.
static func line_from_json(d: Dictionary) -> Dictionary:
	var cs: Array = []
	for c: Variant in d["cells"]:
		cs.append(to_cell(c))
	var kind := String(d["kind"])
	return {"kind": kind, "index": int(d["index"]), "cells": cs, "type": String(d["type"]),
		"home": bool(d.get("home", kind == "ROUTE"))}


## A line in JSON form.
static func line_to_json(ln: Variant) -> Variant:
	if _is_none(ln):
		return null
	var d: Dictionary = ln
	var cs: Array = []
	for c: Variant in d["cells"]:
		cs.append(cell_to_json(c))
	return {"kind": d["kind"], "index": d["index"], "cells": cs, "type": d["type"], "home": d["home"]}


# ---------------------------------------------------------------- leg and state

## The golden's `leg` object as a leg Dictionary: {seed, values: {Vector2i: int}, exploits, start, raids}.
static func leg_from_json(d: Dictionary) -> Dictionary:
	var values := {}
	var vraw: Variant = d["values"]
	if typeof(vraw) == TYPE_DICTIONARY:
		for k: Variant in vraw:
			values[to_cell(k)] = int(vraw[k])
	else:
		for item: Variant in vraw:
			var e: Array = item
			if typeof(e[0]) == TYPE_ARRAY:
				values[to_cell(e[0])] = int(e[1])
			else:
				values[Vector2i(int(e[0]), int(e[1]))] = int(e[2])
	var ex: Array = []
	for c: Variant in d["exploits"]:
		ex.append(to_cell(c))
	var start: Array = []
	for c: Variant in d["start"]:
		start.append(to_cell(c))
	var raids: Array = []
	for rv: Variant in d["raids"]:
		var r: Dictionary = rv
		var perm: Array = []
		for t: Variant in r["perm"]:
			perm.append(String(t))
		var cands: Array = []
		if r.has("cands"):
			for lv: Variant in r["cands"]:
				cands.append(line_from_json(lv))
		else:
			for k in range(CANDIDATES):
				cands.append(route(k, String(perm[k])))
		raids.append({"b1": line_from_json(r["b1"]), "extra1": line_from_json(r["extra1"]),
			"extra2": line_from_json(r["extra2"]), "perm": perm, "cands": cands, "real": int(r["real"]),
			"hunter_type": String(r["hunter_type"]), "hunter_street": int(r["hunter_street"])})
	return {"seed": int(d.get("seed", 0)), "values": _ordered(values), "exploits": _sort_cells(ex),
		"start": _sort_cells(start), "raids": raids}


## sweep_l8.initial: the leg-start state (the seeded x = 0 cells owned OK).
static func initial(leg: Dictionary) -> Dictionary:
	var owned := {}
	for c: Vector2i in leg["start"]:
		owned[c] = OK
	return {"heat": START_HEAT, "bank": START_BANK, "home_hp": HOME_HP, "owned": _ordered(owned), "sentries": {},
		"pool": POOL_START.duplicate(), "kit": KIT_START.duplicate()}


## A state from the golden's state_json form (owned and sentries as [[x, y, s]]).
static func state_from_json(d: Dictionary) -> Dictionary:
	var owned := {}
	for e: Variant in d["owned"]:
		owned[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	var sent := {}
	for e: Variant in d["sentries"]:
		sent[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	return {"heat": int(d["heat"]), "bank": int(d["bank"]), "home_hp": int(d["home_hp"]), "owned": _ordered(owned),
		"sentries": _ordered(sent), "pool": _pool_t(d["pool"]), "kit": _kit_t(d["kit"])}


## A state in the golden's state_json form (lists in cell order, pool D/N/E, kit ghost/spoof).
static func state_to_json(st: Dictionary) -> Dictionary:
	var owned: Array = []
	var sent: Array = []
	var od: Dictionary = st["owned"]
	var sd: Dictionary = st["sentries"]
	for c: Vector2i in CELLS:
		if od.has(c):
			owned.append([c.x, c.y, String(od[c])])
	for c: Vector2i in CELLS:
		if sd.has(c):
			sent.append([c.x, c.y, String(sd[c])])
	return {"heat": int(st["heat"]), "bank": int(st["bank"]), "home_hp": int(st["home_hp"]), "owned": owned,
		"sentries": sent, "pool": _pool_t(st["pool"]), "kit": _kit_t(st["kit"])}


## A place from JSON {sentries: [[x, y, t]] or {cell: t}, ghost: null | "HOME" | [x, y]}.
static func place_from_json(d: Dictionary) -> Dictionary:
	var sent := {}
	var raw: Variant = d.get("sentries", [])
	if typeof(raw) == TYPE_DICTIONARY:
		for k: Variant in raw:
			sent[to_cell(k)] = String(raw[k])
	else:
		for e: Variant in raw:
			sent[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	return {"sentries": _ordered(sent), "ghost": to_cell(d.get("ghost"))}


## A place in JSON form (sentries as [[x, y, t]] in cell order).
static func place_to_json(place: Dictionary) -> Dictionary:
	var sd: Dictionary = place["sentries"]
	var sent: Array = []
	for c: Vector2i in CELLS:
		if sd.has(c):
			sent.append([c.x, c.y, String(sd[c])])
	return {"sentries": sent, "ghost": cell_to_json(to_cell(place.get("ghost")))}


static func _norm_place(place: Dictionary) -> Dictionary:
	var sent := {}
	var sd: Dictionary = place.get("sentries", {})
	for k: Variant in sd:
		sent[to_cell(k)] = String(sd[k])
	return {"sentries": _ordered(sent), "ghost": to_cell(place.get("ghost"))}


# ---------------------------------------------------------------- capture and placement

## sweep_l8.capture_options: NEUTRAL cells adjacent to an owned non-TAKEN cell, or at x = 0; in cell order.
static func capture_options(leg: Dictionary, st: Dictionary) -> Array:
	var owned: Dictionary = st["owned"]
	var out: Array = []
	for c: Vector2i in CELLS:
		if owned.has(c):
			continue
		var ok := c.x == 0
		if not ok:
			for n: Vector2i in NEIGHBORS:
				if _live_status(_status(owned, c + n)):
					ok = true
					break
		if ok:
			out.append(c)
	return out


## sweep_l8.capture: claim one legal NEUTRAL cell (it becomes OK). An illegal cell is reported and ignored.
static func capture(leg: Dictionary, st: Dictionary, cell: Variant) -> Dictionary:
	var c: Variant = to_cell(cell)
	var out := copy_state(st)
	if typeof(c) != TYPE_VECTOR2I or not capture_options(leg, st).has(c):
		_fail("illegal capture %s" % str(cell))
		return out
	var owned: Dictionary = out["owned"]
	owned[c] = OK
	out["owned"] = _ordered(owned)
	return out


static func _place_rec(live: Array, left: Dictionary, idx: int, cur: Dictionary, k: int, maps: Array) -> void:
	if k == 0:
		maps.append(cur.duplicate())
		return
	if live.size() - idx < k:
		return
	var c: Vector2i = live[idx]
	for t: String in TYPES:
		if int(left[t]) > 0:
			left[t] = int(left[t]) - 1
			cur[c] = t
			_place_rec(live, left, idx + 1, cur, k - 1, maps)
			cur.erase(c)
			left[t] = int(left[t]) + 1
	_place_rec(live, left, idx + 1, cur, k, maps)


## sweep_l8.placements: every {sentries, ghost} with all pool sentries placed (as many as live cells allow), distinct
## maps only. Ghost order: null, HOME, then live cells; maps in the python recursion order within each ghost.
static func placements(leg: Dictionary, st: Dictionary) -> Array:
	var live := live_cells(st)
	var left := _pool_t(st["pool"])
	var total := 0
	for t: String in TYPES:
		total += int(left[t])
	var need := mini(total, live.size())
	var maps: Array = []
	_place_rec(live, left, 0, {}, need, maps)
	var ghosts: Array = [null]
	if int(st["kit"]["ghost"]) > 0:
		ghosts.append(HOME)
		ghosts.append_array(live)
	var out: Array = []
	for g: Variant in ghosts:
		for m: Dictionary in maps:
			out.append({"sentries": m.duplicate(), "ghost": g})
	return out


## sweep_l8._check_place: "" when the place is legal for the state, else the reason.
static func check_place(st: Dictionary, place: Dictionary) -> String:
	var p := _norm_place(place)
	var sd: Dictionary = p["sentries"]
	if sd.size() != (place.get("sentries", {}) as Dictionary).size():
		return "illegal sentry cell"
	var counts := {"D": 0, "N": 0, "E": 0}
	for c: Vector2i in sd:
		var t := String(sd[c])
		if not is_live(st, c) or not TYPES.has(t):
			return "illegal sentry %s %s" % [str(c), t]
		counts[t] = int(counts[t]) + 1
	var pool: Dictionary = st["pool"]
	for t: String in TYPES:
		if int(counts[t]) > int(pool[t]):
			return "more sentries than the pool"
	var g: Variant = p["ghost"]
	if not _is_none(g):
		if int(st["kit"]["ghost"]) <= 0 or (not _same(g, HOME) and not is_live(st, g)):
			return "illegal ghost %s" % str(g)
	return ""


# ---------------------------------------------------------------- responses

## sweep_l8.norm_response: null / "HOLD" / "JAM" / ["REDEPLOY", s, c] (JSON cells accepted) -> the canonical array.
## Returns [] for an unknown response.
static func norm_response(r: Variant) -> Array:
	if _is_none(r):
		return ["HOLD"]
	var a: Array
	if typeof(r) == TYPE_STRING or typeof(r) == TYPE_STRING_NAME:
		a = [String(r)]
	elif typeof(r) == TYPE_ARRAY:
		a = r
	else:
		return []
	if a.is_empty():
		return []
	var head := String(a[0])
	if head == "REDEPLOY" and a.size() == 3:
		return ["REDEPLOY", to_cell(a[1]), to_cell(a[2])]
	if (head == "HOLD" or head == "JAM") and a.size() == 1:
		return [head]
	return []


## A response in JSON form: ["HOLD"], ["JAM"] or ["REDEPLOY", [x, y], [x, y]].
static func response_to_json(r: Variant) -> Array:
	var a := norm_response(r)
	if not a.is_empty() and a[0] == "REDEPLOY":
		return ["REDEPLOY", cell_to_json(a[1]), cell_to_json(a[2])]
	return a


# ---------------------------------------------------------------- the sweep

static func _new_sweep(st: Dictionary, place: Dictionary) -> Dictionary:
	return {"sent": (place["sentries"] as Dictionary).duplicate(), "ghost": place["ghost"],
		"owned": (st["owned"] as Dictionary).duplicate(), "hp": int(st["home_hp"]), "home_hit": false,
		"seen": {}, "trace": [], "first": null, "lost": []}


## sweep_l8._Sweep.scan: one line, cell by cell (ghost pass, typed BLOCK stops the line, HIT, else pass), then HOME.
static func _scan(sw: Dictionary, beam: String, ln: Dictionary) -> void:
	var sent: Dictionary = sw["sent"]
	var owned: Dictionary = sw["owned"]
	var seen: Dictionary = sw["seen"]
	var tr: Array = sw["trace"]
	var lost: Array = sw["lost"]
	var t := String(ln["type"])
	for c: Vector2i in ln["cells"]:
		if _same(c, sw["ghost"]):
			continue
		if sent.has(c) and String(sent[c]) == t:
			tr.append([beam, c, "block"])
			if _is_none(sw["first"]):
				sw["first"] = c
			return
		var s := _status(owned, c)
		if _live_status(s) and not seen.has(c):
			if s == OK:
				owned[c] = DOWN
			else:
				owned[c] = TAKEN
				if sent.has(c):
					lost.append(String(sent[c]))
					sent.erase(c)
			tr.append([beam, c, "hit"])
			seen[c] = true
			if _is_none(sw["first"]):
				sw["first"] = c
	if bool(ln["home"]) and not _same(sw["ghost"], HOME) and not bool(sw["home_hit"]):
		sw["hp"] = maxi(0, int(sw["hp"]) - 1)
		sw["home_hit"] = true
		tr.append([beam, HOME, "home"])


## sweep_l8._launch: beam 1 and the extras (before the reveal). {error, raid, heat (launch Heat), sw}.
static func _launch(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary) -> Dictionary:
	var err := check_place(st, place)
	if err != "":
		return {"error": err}
	var p := _norm_place(place)
	var rd: Dictionary = leg["raids"][raid_i]
	var heat: int = int(st["heat"]) + (0 if _is_none(p["ghost"]) else GHOST_HEAT)
	var sw := _new_sweep(st, p)
	_scan(sw, "beam1", rd["b1"])
	if heat >= EXTRA_AT:
		_scan(sw, "extra1", rd["extra1"])
	if heat >= STRONG_AT:
		_scan(sw, "extra2", rd["extra2"])
	return {"error": "", "raid": rd, "heat": heat, "sw": sw}


## sweep_l8._resolve: {error, state, trace, heat_launch}.
static func _resolve(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, place: Dictionary, response: Variant) -> Dictionary:
	var resp := norm_response(response)
	if resp.is_empty():
		return {"error": "unknown response %s" % str(response)}
	var kit := _kit_t(st["kit"])
	var spoof: bool = resp[0] != "HOLD"
	if spoof and int(kit["spoof"]) <= 0:
		return {"error": "no spoof charge"}
	var la := _launch(leg, raid_i, st, place)
	if la["error"] != "":
		return {"error": la["error"]}
	var rd: Dictionary = la["raid"]
	var heat: int = la["heat"]
	var sw: Dictionary = la["sw"]
	var sent: Dictionary = sw["sent"]
	if resp[0] == "REDEPLOY":
		var s: Variant = resp[1]
		var c: Variant = resp[2]
		if not sent.has(s) or _same(c, s) or sent.has(c) or not _live_status(_status(sw["owned"], c)):
			return {"error": "illegal redeploy %s -> %s" % [str(s), str(c)]}
		var t: Variant = sent[s]
		sent.erase(s)
		sent[c] = t
	_scan(sw, "sealed", rd["cands"][cand])
	if resp[0] != "JAM":
		var col: int = (sw["first"] as Vector2i).x if not _is_none(sw["first"]) else int(rd["hunter_street"])
		_scan(sw, "hunter", street(col, true, String(rd["hunter_type"])))
	var tr: Array = sw["trace"]
	var heat_launch := heat
	if tr.is_empty():
		heat -= EVADE_HEAT
	if spoof:
		heat += SPOOF_HEAT
		kit["spoof"] = int(kit["spoof"]) - 1
	if not _is_none(to_cell(place.get("ghost"))):
		kit["ghost"] = int(kit["ghost"]) - 1
	var pool := _pool_t(st["pool"])
	for t: String in sw["lost"]:
		pool[t] = int(pool[t]) - 1
	var ns := {"heat": heat, "bank": int(st["bank"]), "home_hp": int(sw["hp"]), "owned": _ordered(sw["owned"]),
		"sentries": _ordered(sent), "pool": pool, "kit": kit}
	return {"error": "", "state": ns, "trace": tr, "heat_launch": heat_launch}


## sweep_l8.resolve: one raid (raid = index into leg.raids) from the post-capture state, with any legal response.
## Returns {state (after the raid), touches: [[cell | "HOME", "hit" | "block" | "home"]], trace, heat_launch}.
## On illegal input: push_error and {error, state: {}, touches: [], trace: []}.
static func resolve(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, place: Dictionary, response: Variant = null) -> Dictionary:
	var r := _resolve(leg, raid_i, st, cand, place, response)
	if r["error"] != "":
		_fail(r["error"])
		return {"error": r["error"], "state": {}, "touches": [], "trace": []}
	var touches: Array = []
	for e: Array in r["trace"]:
		touches.append([e[1], e[2]])
	return {"state": r["state"], "touches": touches, "trace": r["trace"], "heat_launch": r["heat_launch"]}


## sweep_l8.trace: the touches with their beam, [[beam, cell | "HOME", kind]], beam in BEAMS (the lab's cues).
static func trace(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, place: Dictionary, response: Variant = null) -> Array:
	var r := _resolve(leg, raid_i, st, cand, place, response)
	if r["error"] != "":
		_fail(r["error"])
		return []
	return r["trace"]


## A trace (or touches) in JSON form: cells as [x, y].
static func trace_to_json(tr: Array) -> Array:
	var out: Array = []
	for e: Array in tr:
		var j: Array = []
		for v: Variant in e:
			j.append(cell_to_json(v))
		out.append(j)
	return out


## sweep_l8.hunter_line: the street the hunter runs (top to bottom), or null when JAMMED.
static func hunter_line(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, place: Dictionary, response: Variant = null) -> Variant:
	var resp := norm_response(response)
	if not resp.is_empty() and resp[0] == "JAM":
		return null
	var rd: Dictionary = leg["raids"][raid_i]
	var col := int(rd["hunter_street"])
	for e: Array in trace(leg, raid_i, st, cand, place, resp):
		if e[0] != "hunter" and not _same(e[1], HOME):
			col = (e[1] as Vector2i).x
			break
	return street(col, true, String(rd["hunter_type"]))


## sweep_l8.response_options: HOLD, then (with a spoof charge) every REDEPLOY (source in cell order, then target in cell
## order), then JAM. Legality is read after beam 1 and the extras.
static func response_options(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, place: Dictionary) -> Array:
	var out: Array = [["HOLD"]]
	if int(st["kit"]["spoof"]) <= 0:
		return out
	var la := _launch(leg, raid_i, st, place)
	if la["error"] != "":
		_fail(la["error"])
		return out
	var sw: Dictionary = la["sw"]
	var sent: Dictionary = sw["sent"]
	var owned: Dictionary = sw["owned"]
	var targets: Array = []
	for c: Vector2i in CELLS:
		if _live_status(_status(owned, c)) and not sent.has(c):
			targets.append(c)
	for s: Vector2i in sorted_cells(sent):
		for c: Vector2i in targets:
			if c != s:
				out.append(["REDEPLOY", s, c])
	out.append(["JAM"])
	return out


# ---------------------------------------------------------------- outcome

## sweep_l8.tier: BREACHED (HOME at 0), DAMAGED (HOME lost integrity), EVADED (no touches), BATTERED (2+ cells newly
## DOWN or any newly TAKEN), else HOLDS.
static func tier(before: Dictionary, after: Dictionary, touches: Array) -> String:
	if int(after["home_hp"]) <= 0:
		return "BREACHED"
	if int(after["home_hp"]) < int(before["home_hp"]):
		return "DAMAGED"
	if touches.is_empty():
		return "EVADED"
	var b: Dictionary = before["owned"]
	var a: Dictionary = after["owned"]
	var new_down := 0
	var new_taken := 0
	for c: Vector2i in CELLS:
		var s := _status(a, c)
		if s == DOWN and _status(b, c) == OK:
			new_down += 1
		if s == TAKEN and _status(b, c) != TAKEN:
			new_taken += 1
	return "BATTERED" if new_down >= 2 or new_taken >= 1 else "HOLDS"


## sweep_l8.score: bank + sum(v - (v // 2 if DOWN)) over owned non-TAKEN + EXPLOIT_BONUS per owned non-TAKEN exploit
## - HOME_LOSS_COST per HOME lost - HEAT_CARRY per Heat above START_HEAT; a breach is -BREACH. mid adds KIT_VALUE per
## unspent ghost, spoof and pool sentry (planner heuristic only).
static func score(leg: Dictionary, st: Dictionary, mid: bool = false) -> float:
	if int(st["home_hp"]) <= 0:
		return float(-BREACH)
	var vals: Dictionary = leg["values"]
	var ex: Array = leg["exploits"]
	var owned: Dictionary = st["owned"]
	var s := float(int(st["bank"]))
	for c: Vector2i in CELLS:
		var stat := _status(owned, c)
		if _live_status(stat):
			var v := int(vals[c])
			s += v - (idiv(v, REPAIR_DIV) if stat == DOWN else 0) + (EXPLOIT_BONUS if ex.has(c) else 0)
	s -= HOME_LOSS_COST * (HOME_HP - int(st["home_hp"]))
	s -= HEAT_CARRY * maxi(0, int(st["heat"]) - START_HEAT)
	if mid:
		var n := 0
		for k: String in ["ghost", "spoof"]:
			n += int(st["kit"][k])
		for t: String in TYPES:
			n += int(st["pool"][t])
		s += KIT_VALUE * n
	return s


## The score's terms for the RECORD screen: {bank, cells, exploits, home_loss, heat_carry, total, breach}.
static func score_parts(leg: Dictionary, st: Dictionary) -> Dictionary:
	var vals: Dictionary = leg["values"]
	var ex: Array = leg["exploits"]
	var owned: Dictionary = st["owned"]
	var cell_sum := 0
	var ex_sum := 0
	for c: Vector2i in CELLS:
		var stat := _status(owned, c)
		if _live_status(stat):
			var v := int(vals[c])
			cell_sum += v - (idiv(v, REPAIR_DIV) if stat == DOWN else 0)
			if ex.has(c):
				ex_sum += EXPLOIT_BONUS
	return {"bank": int(st["bank"]), "cells": cell_sum, "exploits": ex_sum,
		"home_loss": HOME_LOSS_COST * (HOME_HP - int(st["home_hp"])),
		"heat_carry": HEAT_CARRY * maxi(0, int(st["heat"]) - START_HEAT), "total": score(leg, st),
		"breach": int(st["home_hp"]) <= 0}


# ---------------------------------------------------------------- between raids

## The pieces of the between step, for the ledger: {repaired (cell or null), repair_cost, built (type or null),
## build_cost, income, heat_add, state}. An unaffordable or illegal repair or build is skipped.
static func between_parts(leg: Dictionary, st: Dictionary, repair: Variant, build: Variant, intensity: String = "NORMAL") -> Dictionary:
	var vals: Dictionary = leg["values"]
	var owned := _ordered(st["owned"])
	var bank := int(st["bank"])
	var rep: Variant = to_cell(repair)
	var repaired: Variant = null
	var rcost := 0
	if typeof(rep) == TYPE_VECTOR2I and _status(owned, rep) == DOWN and bank >= idiv(int(vals[rep]), REPAIR_DIV):
		rcost = idiv(int(vals[rep]), REPAIR_DIV)
		bank -= rcost
		owned[rep] = OK
		repaired = rep
	var pool := _pool_t(st["pool"])
	var built: Variant = null
	var bcost := 0
	if not _is_none(build) and TYPES.has(String(build)) and bank >= SENTRY_PRICE:
		bank -= SENTRY_PRICE
		bcost = SENTRY_PRICE
		pool[String(build)] = int(pool[String(build)]) + 1
		built = String(build)
	var inten := intensity
	if not INTENSITY.has(inten):
		_fail("unknown intensity %s" % intensity)
		inten = "NORMAL"
	var dh := int(INTENSITY[inten][0])
	var inc := income(leg, owned, inten)
	var ns := {"heat": int(st["heat"]) + dh, "bank": bank + inc, "home_hp": int(st["home_hp"]), "owned": owned,
		"sentries": _ordered(st["sentries"]), "pool": pool, "kit": _kit_t(st["kit"])}
	return {"repaired": repaired, "repair_cost": rcost, "built": built, "build_cost": bcost, "income": inc,
		"heat_add": dh, "state": ns}


## sweep_l8.between: repair (<= 1 DOWN cell, v // 2), then build (<= 1 sentry, SENTRY_PRICE), then income and Heat.
## repair is a Vector2i or null, build a type String or null.
static func between(leg: Dictionary, st: Dictionary, repair: Variant, build: Variant, intensity: String = "NORMAL") -> Dictionary:
	return between_parts(leg, st, repair, build, intensity)["state"]


## sweep_l8.between_options: every affordable [repair, build, intensity]; repair null then DOWN cells (cell order),
## build null then D, N, E, intensity LOW, NORMAL, HOT.
static func between_options(leg: Dictionary, st: Dictionary) -> Array:
	var vals: Dictionary = leg["values"]
	var owned: Dictionary = st["owned"]
	var bank := int(st["bank"])
	var reps: Array = [null]
	for c: Vector2i in CELLS:
		if _status(owned, c) == DOWN and bank >= idiv(int(vals[c]), REPAIR_DIV):
			reps.append(c)
	var out: Array = []
	for r: Variant in reps:
		var left := bank - (0 if _is_none(r) else idiv(int(vals[r]), REPAIR_DIV))
		var builds: Array = [null]
		if left >= SENTRY_PRICE:
			builds.append_array(TYPES)
		for b: Variant in builds:
			for inten: String in INTENSITY_ORDER:
				out.append([r, b, inten])
	return out


# ---------------------------------------------------------------- forecast

## sweep_l8._best_per_cand: per sealed candidate {value, response, state, touches}; ties keep the earliest response.
static func _best_per_cand(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary, mid: bool) -> Array:
	var opts := response_options(leg, raid_i, st, 0, place)
	var per: Array = []
	for k in range(CANDIDATES):
		var best: Dictionary = {}
		for r: Array in opts:
			var res := resolve(leg, raid_i, st, k, place, r)
			if res.has("error"):
				continue
			var v := score(leg, res["state"], mid)
			if best.is_empty() or v > float(best["value"]) + EPS:
				best = {"value": v, "response": r, "state": res["state"], "touches": res["touches"]}
		per.append(best)
	return per


## sweep_l8.forecast: per sealed candidate {cand, route, type, hold: {state, touches, tier, score},
## best: {response, state, touches, tier, score, value}}; the best response is ranked by the mid-leg value.
static func forecast(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary) -> Array:
	var mid := raid_i < RAIDS - 1
	var rd: Dictionary = leg["raids"][raid_i]
	var out: Array = []
	var per := _best_per_cand(leg, raid_i, st, place, mid)
	for k in range(CANDIDATES):
		var hold := resolve(leg, raid_i, st, k, place, ["HOLD"])
		if hold.has("error"):
			return []
		var best: Dictionary = per[k]
		var hs: Dictionary = hold["state"]
		var ns: Dictionary = best["state"]
		out.append({"cand": k, "route": ROUTE_NAMES[k], "type": String(rd["cands"][k]["type"]),
			"hold": {"state": hs, "touches": hold["touches"], "tier": tier(st, hs, hold["touches"]),
				"score": score(leg, hs)},
			"best": {"response": best["response"], "state": ns, "touches": best["touches"],
				"tier": tier(st, ns, best["touches"]), "score": score(leg, ns), "value": best["value"]}})
	return out
