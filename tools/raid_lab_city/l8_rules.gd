class_name L8Rules
extends RefCounted
## The round-8 (L8) city-raid rules with the L9, L10, L11 and L13 changes, ported from tools/raid_concepts/sweep_l8.py
## (the oracle). Covers decay, capture (with the HOT extra capture), placements, the launch (beam 1, extras, sealed,
## hunter on one of two sealed streets), responses (HOLD, REDEPLOY, DEPLOY, SACRIFICE, JAM), between (with intensity
## perks), tier, banded score, forecast and safe_next. Pure and deterministic: no randomness, no nodes. Cells are
## Vector2i (x 0..3, y 0..2); HOME is the String "HOME". Every enumeration walks CELLS (y, then x), never dictionary
## order. Data shapes: docs/handoff/raid_lab_l8/GD_CONTRACT.md. Changes: docs/handoff/raid_lab_l8/L9_CHANGES.md,
## L10_CHANGES.md, L11_CHANGES.md and L13_RULES.md (R2 hunter street sealed, R3 SACRIFICE, R4 Heat bands, R5 perks).

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
const HUNTER_CANDS := 2		# L13 R2: two sealed hunter streets per raid
const HUNTER_SEED := 9100	# L13 R2: random.Random(HUNTER_SEED + 13 * seed + raid) in the Python oracle

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
const SENTRY_PRICE := 3		# L9: was 4
const REPAIR_DIV := 2
const INCOME_DIV := 3
const POOL_START: Dictionary = {"D": 1, "N": 1, "E": 0}	# L10: was 1/1/1 (two sentries, three sealed routes)
const MAX_PLACED := 2		# L11: PLAN places at most 2 sentries; the rest of the pool is the reserve
const KIT_START: Dictionary = {"ghost": 2, "spoof": 2}
const INTENSITY_ORDER: Array = ["LOW", "NORMAL", "HOT"]
const INTENSITY: Dictionary = {"LOW": [6, 0.5], "NORMAL": [12, 1.0], "HOT": [18, 0.5]}	# L13b: HOT income x0.5 (x1.5 made HOT 38/40)
const FREE_REPAIR_AT := "NORMAL"	# L13 R5: this between step's repair is free
const EXTRA_CAPTURE_AT := "HOT"	# L13 R5: the next raid's CAPTURE takes two cells

# Score.
const EXPLOIT_BONUS := 6
const HOME_LOSS_COST := 15	# L13 R4: was 8
const HEAT_CARRY := 0.5		# L13 R4: was 1.0
const HEAT_BAND := 6		# L13 R4: per band crossed (heat >= EXTRA_AT, heat >= STRONG_AT)
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
		"SPOOF_HEAT": SPOOF_HEAT, "EVADE_HEAT": EVADE_HEAT, "SENTRY_PRICE": SENTRY_PRICE, "DECAY": true, "HUNTER_CANDS": HUNTER_CANDS, "HUNTER_SEED": HUNTER_SEED, "PERKS": {"HOT": "EXTRA_CAPTURE", "LOW": null, "NORMAL": "FREE_REPAIR"},
		"POOL_START": POOL_START.duplicate(), "KIT_START": KIT_START.duplicate(), "INTENSITY": inten,
		"EXPLOIT_BONUS": EXPLOIT_BONUS, "HOME_LOSS_COST": HOME_LOSS_COST, "HEAT_CARRY": HEAT_CARRY,
		"HEAT_BAND": HEAT_BAND, "BREACH": BREACH, "KIT_VALUE": KIT_VALUE, "MAX_PLACED": MAX_PLACED}


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


## A deep copy of a state (L13: carries extra_capture).
static func copy_state(st: Dictionary) -> Dictionary:
	return {"heat": int(st["heat"]), "bank": int(st["bank"]), "home_hp": int(st["home_hp"]),
		"owned": _ordered(st["owned"]), "sentries": _ordered(st["sentries"]), "pool": _pool_t(st["pool"]),
		"kit": _kit_t(st["kit"]), "extra_capture": int(st.get("extra_capture", 0))}


## The repair cost of a cell at a given intensity (v // 2; L13 R5: 0 under NORMAL).
static func repair_cost(leg: Dictionary, c: Vector2i, intensity: String = "") -> int:
	if intensity == FREE_REPAIR_AT:
		return 0
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


## L11: how many sentries of type t are in reserve (pool count minus the placed ones of that type).
static func _reserve_left(pool: Dictionary, sent: Dictionary, t: String) -> int:
	var n := 0
	for c: Variant in sent:
		if String(sent[c]) == t:
			n += 1
	return int(pool.get(t, 0)) - n


## L11: the reserve by type for a placement ({D, N, E}: pool minus placed), for the lab's reserve tray.
static func reserve_counts(st: Dictionary, sentries: Dictionary) -> Dictionary:
	var pool := _pool_t(st["pool"])
	var out := {}
	for t: String in TYPES:
		out[t] = maxi(0, _reserve_left(pool, sentries, t))
	return out


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
## L13 R2: each raid carries hunter_cands (2 distinct streets) and hunter_real (0 or 1); hunter_street is gone.
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
		var hc: Array = []
		for x: Variant in r["hunter_cands"]:
			hc.append(int(x))
		raids.append({"b1": line_from_json(r["b1"]), "extra1": line_from_json(r["extra1"]),
			"extra2": line_from_json(r["extra2"]), "perm": perm, "cands": cands, "real": int(r["real"]),
			"hunter_type": String(r["hunter_type"]), "hunter_cands": hc, "hunter_real": int(r["hunter_real"])})
	return {"seed": int(d.get("seed", 0)), "values": _ordered(values), "exploits": _sort_cells(ex),
		"start": _sort_cells(start), "raids": raids}


## sweep_l8.initial: the leg-start state (the seeded x = 0 cells owned OK, pool POOL_START, kit KIT_START,
## extra_capture 0).
static func initial(leg: Dictionary) -> Dictionary:
	var owned := {}
	for c: Vector2i in leg["start"]:
		owned[c] = OK
	return {"heat": START_HEAT, "bank": START_BANK, "home_hp": HOME_HP, "owned": _ordered(owned), "sentries": {},
		"pool": _pool_t(POOL_START), "kit": KIT_START.duplicate(), "extra_capture": 0}


## A state from the golden's state_json form (owned and sentries as [[x, y, s]], plus extra_capture).
static func state_from_json(d: Dictionary) -> Dictionary:
	var owned := {}
	for e: Variant in d["owned"]:
		owned[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	var sent := {}
	for e: Variant in d["sentries"]:
		sent[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	return {"heat": int(d["heat"]), "bank": int(d["bank"]), "home_hp": int(d["home_hp"]), "owned": _ordered(owned),
		"sentries": _ordered(sent), "pool": _pool_t(d["pool"]), "kit": _kit_t(d["kit"]),
		"extra_capture": int(d.get("extra_capture", 0))}


## A state in the golden's state_json form (lists in cell order, pool D/N/E, kit ghost/spoof, extra_capture).
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
		"sentries": sent, "pool": _pool_t(st["pool"]), "kit": _kit_t(st["kit"]),
		"extra_capture": int(st.get("extra_capture", 0))}


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


# ---------------------------------------------------------------- decay (L9, L11)

## The cells decay(leg, st) would turn TAKEN: every owned cell still DOWN, in cell order (for the lab's DECAY beat).
static func decaying_cells(st: Dictionary) -> Array:
	var owned: Dictionary = st["owned"]
	var out: Array = []
	for c: Vector2i in CELLS:
		if _status(owned, c) == DOWN:
			out.append(c)
	return out


## sweep_l8.decay_cells: the same list as decaying_cells.
static func decay_cells(leg: Dictionary, st: Dictionary) -> Array:
	return decaying_cells(st)


## sweep_l8.decay (L9, L11): every owned cell whose status is still DOWN becomes TAKEN; its sentry leaves the
## placement and goes back to the pool (L11: the pool count is unchanged). Heat, bank, HOME, kit and extra_capture
## are unchanged. The caller applies it at the start of every raid after the first, before CAPTURE. Idempotent.
static func decay(leg: Dictionary, st: Dictionary) -> Dictionary:
	var out := copy_state(st)
	var owned: Dictionary = out["owned"]
	var sent: Dictionary = out["sentries"]
	for c: Vector2i in CELLS:
		if _status(owned, c) == DOWN:
			owned[c] = TAKEN
			if sent.has(c):
				sent.erase(c)
	out["owned"] = _ordered(owned)
	out["sentries"] = _ordered(sent)
	return out


# ---------------------------------------------------------------- capture and placement

## sweep_l8.capture_options: NEUTRAL cells adjacent to an owned non-TAKEN cell, or at x = 0; in cell order.
## From raid 2 on, pass the decayed state.
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
## extra_capture is left as is; the CAPTURE phase clears it with end_capture (L13 R5).
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


## L13 R5: how many cells this CAPTURE phase claims (1, or 2 after a HOT between step).
static func capture_slots(st: Dictionary) -> int:
	return 1 + (1 if int(st.get("extra_capture", 0)) > 0 else 0)


## L13 R5: the end of the CAPTURE phase: extra_capture is cleared.
static func end_capture(st: Dictionary) -> Dictionary:
	var out := copy_state(st)
	out["extra_capture"] = 0
	return out


## L13 R5: the whole CAPTURE phase: capture cells[0], then cells[1] if extra_capture > 0 (each from the updated
## state's options), then clear extra_capture. cells holds 0 to 2 cells (0 only when there is no option).
static func capture_all(leg: Dictionary, st: Dictionary, cells_in: Array) -> Dictionary:
	var out := copy_state(st)
	var n := mini(cells_in.size(), capture_slots(st))
	for i in range(n):
		out = capture(leg, out, cells_in[i])
	return end_capture(out)


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


## sweep_l8.placements: every {sentries, ghost} with min(pool total, live cells, MAX_PLACED) sentries placed (L11
## cap), distinct maps only; unplaced pool sentries are the reserve. Ghost order: null, HOME, then live cells; maps in
## the python recursion order within each ghost.
static func placements(leg: Dictionary, st: Dictionary) -> Array:
	var live := live_cells(st)
	var left := _pool_t(st["pool"])
	var total := 0
	for t: String in TYPES:
		total += int(left[t])
	var need := mini(mini(total, live.size()), MAX_PLACED)
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


## sweep_l8._check_place: "" when the place is legal for the state, else the reason (L11: at most MAX_PLACED).
static func check_place(st: Dictionary, place: Dictionary) -> String:
	var p := _norm_place(place)
	var sd: Dictionary = p["sentries"]
	if sd.size() != (place.get("sentries", {}) as Dictionary).size():
		return "illegal sentry cell"
	if sd.size() > MAX_PLACED:
		return "more than %d sentries placed" % MAX_PLACED
	var counts := {"D": 0, "N": 0, "E": 0}
	for c: Vector2i in sd:
		var t := String(sd[c])
		if not is_live(st, c) or not TYPES.has(t):
			return "illegal sentry %s %s" % [str(c), t]
		counts[t] = int(counts[t]) + 1
	var pool: Dictionary = st["pool"]
	for t: String in TYPES:
		if int(counts[t]) > int(pool.get(t, 0)):
			return "more sentries than the pool"
	var g: Variant = p["ghost"]
	if not _is_none(g):
		if int(st["kit"]["ghost"]) <= 0 or (not _same(g, HOME) and not is_live(st, g)):
			return "illegal ghost %s" % str(g)
	return ""


# ---------------------------------------------------------------- responses

## sweep_l8.norm_response: null / "HOLD" / "JAM" / ["REDEPLOY", s, c] / ["DEPLOY", t, c] / ["SACRIFICE", c] (JSON
## cells accepted) -> the canonical array. Returns [] for an unknown response.
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
	if head == "DEPLOY" and a.size() == 3:
		return ["DEPLOY", String(a[1]), to_cell(a[2])]
	if head == "SACRIFICE" and a.size() == 2:
		return ["SACRIFICE", to_cell(a[1])]
	if (head == "HOLD" or head == "JAM") and a.size() == 1:
		return [head]
	return []


## A response in JSON form: ["HOLD"], ["JAM"], ["REDEPLOY", [x, y], [x, y]], ["DEPLOY", type, [x, y]] or
## ["SACRIFICE", [x, y]].
static func response_to_json(r: Variant) -> Array:
	var a := norm_response(r)
	if a.is_empty():
		return a
	if a[0] == "REDEPLOY":
		return ["REDEPLOY", cell_to_json(a[1]), cell_to_json(a[2])]
	if a[0] == "DEPLOY":
		return ["DEPLOY", String(a[1]), cell_to_json(a[2])]
	if a[0] == "SACRIFICE":
		return ["SACRIFICE", cell_to_json(a[1])]
	return a


## True when the response spends a spoof charge and SPOOF_HEAT (everything but HOLD and SACRIFICE).
static func response_spoofs(r: Variant) -> bool:
	var a := norm_response(r)
	return not a.is_empty() and a[0] != "HOLD" and a[0] != "SACRIFICE"


# ---------------------------------------------------------------- the sweep

static func _new_sweep(st: Dictionary, place: Dictionary) -> Dictionary:
	return {"sent": (place["sentries"] as Dictionary).duplicate(), "ghost": place["ghost"],
		"owned": (st["owned"] as Dictionary).duplicate(), "hp": int(st["home_hp"]), "home_hit": false,
		"shield": false, "seen": {}, "trace": []}


## sweep_l8._Sweep.scan: one line, cell by cell (ghost pass, typed BLOCK stops the line, HIT, else pass), then HOME.
## L11: a cell turned TAKEN drops its sentry from the placement; the sentry returns to the pool (count unchanged).
## L13 R3: after a SACRIFICE, a route reaching HOME records ("HOME", "shielded") and HOME is unharmed.
static func _scan(sw: Dictionary, beam: String, ln: Dictionary) -> void:
	var sent: Dictionary = sw["sent"]
	var owned: Dictionary = sw["owned"]
	var seen: Dictionary = sw["seen"]
	var tr: Array = sw["trace"]
	var t := String(ln["type"])
	for c: Vector2i in ln["cells"]:
		if _same(c, sw["ghost"]):
			continue
		if sent.has(c) and String(sent[c]) == t:
			tr.append([beam, c, "block"])
			return
		var s := _status(owned, c)
		if _live_status(s) and not seen.has(c):
			if s == OK:
				owned[c] = DOWN
			else:
				owned[c] = TAKEN
				if sent.has(c):
					sent.erase(c)
			tr.append([beam, c, "hit"])
			seen[c] = true
	if bool(ln["home"]) and not _same(sw["ghost"], HOME) and not bool(sw["home_hit"]):
		if bool(sw["shield"]):
			tr.append([beam, HOME, "shielded"])
		else:
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


## L13 R2: the street index the hunter runs for hunter street candidate hunt (0 or 1).
static func hunter_street_of(leg: Dictionary, raid_i: int, hunt: int) -> int:
	return int((leg["raids"][raid_i]["hunter_cands"] as Array)[hunt])


## sweep_l8._resolve: {error, state, trace, heat_launch}.
static func _resolve(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, hunt: int, place: Dictionary, response: Variant) -> Dictionary:
	var resp := norm_response(response)
	if resp.is_empty():
		return {"error": "unknown response %s" % str(response)}
	var kit := _kit_t(st["kit"])
	var spoof: bool = resp[0] != "HOLD" and resp[0] != "SACRIFICE"
	if spoof and int(kit["spoof"]) <= 0:
		return {"error": "no spoof charge"}
	var la := _launch(leg, raid_i, st, place)
	if la["error"] != "":
		return {"error": la["error"]}
	var rd: Dictionary = la["raid"]
	var hc: Array = rd["hunter_cands"]
	if hunt < 0 or hunt >= hc.size():
		return {"error": "illegal hunter street %d" % hunt}
	if cand < 0 or cand >= (rd["cands"] as Array).size():
		return {"error": "illegal candidate %d" % cand}
	var heat: int = la["heat"]
	var sw: Dictionary = la["sw"]
	var sent: Dictionary = sw["sent"]
	var owned: Dictionary = sw["owned"]
	var pool := _pool_t(st["pool"])
	if resp[0] == "REDEPLOY":
		var s: Variant = resp[1]
		var c: Variant = resp[2]
		if not sent.has(s) or _same(c, s) or sent.has(c) or not _live_status(_status(owned, c)):
			return {"error": "illegal redeploy %s -> %s" % [str(s), str(c)]}
		var t: Variant = sent[s]
		sent.erase(s)
		sent[c] = t
	elif resp[0] == "DEPLOY":
		var dt := String(resp[1])
		var dc: Variant = resp[2]
		if not TYPES.has(dt) or _reserve_left(pool, sent, dt) <= 0 or typeof(dc) != TYPE_VECTOR2I \
				or sent.has(dc) or not _live_status(_status(owned, dc)):
			return {"error": "illegal deploy %s -> %s" % [dt, str(dc)]}
		sent[dc] = dt
	elif resp[0] == "SACRIFICE":
		var sc: Variant = resp[1]
		if typeof(sc) != TYPE_VECTOR2I or not _live_status(_status(owned, sc)):
			return {"error": "illegal sacrifice %s" % str(sc)}
		owned[sc] = TAKEN
		if sent.has(sc):
			sent.erase(sc)
		sw["shield"] = true
	_scan(sw, "sealed", rd["cands"][cand])
	if resp[0] != "JAM":
		_scan(sw, "hunter", street(int(hc[hunt]), true, String(rd["hunter_type"])))
	var tr: Array = sw["trace"]
	var heat_launch := heat
	if tr.is_empty() and not bool(sw.get("shield", false)):
		heat -= EVADE_HEAT
	if spoof:
		heat += SPOOF_HEAT
		kit["spoof"] = int(kit["spoof"]) - 1
	if not _is_none(to_cell(place.get("ghost"))):
		kit["ghost"] = int(kit["ghost"]) - 1
	var ns := {"heat": heat, "bank": int(st["bank"]), "home_hp": int(sw["hp"]), "owned": _ordered(owned),
		"sentries": _ordered(sent), "pool": pool, "kit": kit, "extra_capture": int(st.get("extra_capture", 0))}
	return {"error": "", "state": ns, "trace": tr, "heat_launch": heat_launch}


static func _touches(tr: Array) -> Array:
	var touches: Array = []
	for e: Array in tr:
		touches.append([e[1], e[2]])
	return touches


## sweep_l8.resolve: one raid (raid = index into leg.raids) from the post-capture state, for sealed candidate cand
## and hunter street candidate hunt (L13 R2; callers pass raid.hunter_real for the real line), with any legal
## response. Returns {state (after the raid), touches: [[cell | "HOME", "hit" | "block" | "home" | "shielded"]],
## trace, heat_launch}. On illegal input: push_error and {error, state: {}, touches: [], trace: []}.
static func resolve(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, hunt: int, place: Dictionary, response: Variant = null) -> Dictionary:
	var r := _resolve(leg, raid_i, st, cand, hunt, place, response)
	if r["error"] != "":
		_fail(r["error"])
		return {"error": r["error"], "state": {}, "touches": [], "trace": []}
	return {"state": r["state"], "touches": _touches(r["trace"]), "trace": r["trace"], "heat_launch": r["heat_launch"]}


## sweep_l8.trace: the touches with their beam, [[beam, cell | "HOME", kind]], beam in BEAMS (the lab's cues).
static func trace(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, hunt: int, place: Dictionary, response: Variant = null) -> Array:
	var r := _resolve(leg, raid_i, st, cand, hunt, place, response)
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


## sweep_l8.hunter_line (L13 R2): street(hunter_cands[hunt], down, hunter_type), top to bottom, or null when JAMMED.
## The first-touch rule is gone, so cand, st and place do not change the line.
static func hunter_line(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, hunt: int, place: Dictionary, response: Variant = null) -> Variant:
	var resp := norm_response(response)
	if not resp.is_empty() and resp[0] == "JAM":
		return null
	var rd: Dictionary = leg["raids"][raid_i]
	return street(hunter_street_of(leg, raid_i, hunt), true, String(rd["hunter_type"]))


## sweep_l8.response_options: HOLD, then (with a spoof charge) every REDEPLOY (source in cell order, then target in
## cell order) and every DEPLOY (L11: reserve types in D, N, E order, then target in cell order), then every SACRIFICE
## (L13 R3: owned non-TAKEN cells in cell order; free, so offered without a spoof charge too), then JAM (with a spoof
## charge). Legality and the reserve are read after beam 1 and the extras.
static func response_options(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, place: Dictionary) -> Array:
	var out: Array = [["HOLD"]]
	var la := _launch(leg, raid_i, st, place)
	if la["error"] != "":
		_fail(la["error"])
		return out
	var has_spoof := int(st["kit"]["spoof"]) > 0
	var sw: Dictionary = la["sw"]
	var sent: Dictionary = sw["sent"]
	var owned: Dictionary = sw["owned"]
	var pool := _pool_t(st["pool"])
	var live: Array = []
	var targets: Array = []
	for c: Vector2i in CELLS:
		if _live_status(_status(owned, c)):
			live.append(c)
			if not sent.has(c):
				targets.append(c)
	if has_spoof:
		for s: Vector2i in sorted_cells(sent):
			for c: Vector2i in targets:
				if c != s:
					out.append(["REDEPLOY", s, c])
		for t: String in TYPES:
			if _reserve_left(pool, sent, t) > 0:
				for c: Vector2i in targets:
					out.append(["DEPLOY", t, c])
	for c: Vector2i in live:
		out.append(["SACRIFICE", c])
	if has_spoof:
		out.append(["JAM"])
	return out


# ---------------------------------------------------------------- outcome

## sweep_l8.tier: BREACHED (HOME at 0), DAMAGED (HOME lost integrity), EVADED (no touches and no newly TAKEN cell),
## BATTERED (2+ cells newly DOWN or any newly TAKEN, a SACRIFICE included), else HOLDS.
static func tier(before: Dictionary, after: Dictionary, touches: Array) -> String:
	if int(after["home_hp"]) <= 0:
		return "BREACHED"
	if int(after["home_hp"]) < int(before["home_hp"]):
		return "DAMAGED"
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
	if touches.is_empty() and new_taken == 0:
		return "EVADED"
	return "BATTERED" if new_down >= 2 or new_taken >= 1 else "HOLDS"


## L13 R4: the Heat term's cost: HEAT_CARRY per Heat above START_HEAT, plus HEAT_BAND at >= EXTRA_AT and again at
## >= STRONG_AT.
static func heat_cost(heat: int) -> float:
	var c := HEAT_CARRY * maxi(0, heat - START_HEAT)
	if heat >= EXTRA_AT:
		c += HEAT_BAND
	if heat >= STRONG_AT:
		c += HEAT_BAND
	return c


## sweep_l8.score: bank + sum(v - (v // 2 if DOWN)) over owned non-TAKEN + EXPLOIT_BONUS per owned non-TAKEN exploit
## - HOME_LOSS_COST per HOME lost - 0.5 per Heat above START_HEAT - HEAT_BAND per Heat band reached (L13 R4); a breach
## is -BREACH. mid adds KIT_VALUE per unspent ghost, spoof and pool sentry (planner heuristic only).
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
	var heat := int(st["heat"])
	s -= HEAT_CARRY * maxi(0, heat - START_HEAT)
	if heat >= EXTRA_AT:
		s -= HEAT_BAND
	if heat >= STRONG_AT:
		s -= HEAT_BAND
	if mid:
		var n := 0
		for k: String in ["ghost", "spoof"]:
			n += int(st["kit"][k])
		for t: String in TYPES:
			n += int(st["pool"].get(t, 0))
		s += KIT_VALUE * n
	return s


## The score's terms for the RECORD screen and the HUD breakdown: {bank, cells, exploits, home_loss, heat_carry
## (the whole Heat term), heat_bands (its band part), total, breach}.
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
	var heat := int(st["heat"])
	var bands := (HEAT_BAND if heat >= EXTRA_AT else 0) + (HEAT_BAND if heat >= STRONG_AT else 0)
	return {"bank": int(st["bank"]), "cells": cell_sum, "exploits": ex_sum,
		"home_loss": HOME_LOSS_COST * (HOME_HP - int(st["home_hp"])), "heat_carry": heat_cost(heat),
		"heat_bands": bands, "total": score(leg, st), "breach": int(st["home_hp"]) <= 0}


# ---------------------------------------------------------------- between raids

## The pieces of the between step, for the ledger: {repaired (cell or null), repair_cost, built (type or null),
## build_cost, income, heat_add, extra_capture, state}. Order: repair (free under NORMAL), build, income, Heat, perk
## flag (HOT sets extra_capture to 1). An unaffordable or illegal repair or build is skipped.
static func between_parts(leg: Dictionary, st: Dictionary, repair: Variant, build: Variant, intensity: String = "NORMAL") -> Dictionary:
	var inten := intensity
	if not INTENSITY.has(inten):
		_fail("unknown intensity %s" % intensity)
		inten = "NORMAL"
	var owned := _ordered(st["owned"])
	var bank := int(st["bank"])
	var rep: Variant = to_cell(repair)
	var repaired: Variant = null
	var rcost := 0
	if typeof(rep) == TYPE_VECTOR2I and _status(owned, rep) == DOWN and bank >= repair_cost(leg, rep, inten):
		rcost = repair_cost(leg, rep, inten)
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
	var dh := int(INTENSITY[inten][0])
	var inc := income(leg, owned, inten)
	var extra := 1 if inten == EXTRA_CAPTURE_AT else int(st.get("extra_capture", 0))
	var ns := {"heat": int(st["heat"]) + dh, "bank": bank + inc, "home_hp": int(st["home_hp"]), "owned": owned,
		"sentries": _ordered(st["sentries"]), "pool": pool, "kit": _kit_t(st["kit"]), "extra_capture": extra}
	return {"repaired": repaired, "repair_cost": rcost, "built": built, "build_cost": bcost, "income": inc,
		"heat_add": dh, "extra_capture": extra, "state": ns}


## sweep_l8.between: repair (<= 1 DOWN cell, v // 2, free under NORMAL), then build (<= 1 sentry, SENTRY_PRICE),
## then income, Heat and the HOT extra-capture flag. repair is a Vector2i or null, build a type String or null.
static func between(leg: Dictionary, st: Dictionary, repair: Variant, build: Variant, intensity: String = "NORMAL") -> Dictionary:
	return between_parts(leg, st, repair, build, intensity)["state"]


## sweep_l8.between_options: every affordable [repair, build, intensity]; repair null then DOWN cells (cell order),
## build null then D, N, E, intensity LOW, NORMAL, HOT; a combination is kept when its repair cost (0 under NORMAL)
## plus its build cost fits the bank.
static func between_options(leg: Dictionary, st: Dictionary) -> Array:
	var owned: Dictionary = st["owned"]
	var bank := int(st["bank"])
	var reps: Array = [null]
	for c: Vector2i in CELLS:
		if _status(owned, c) == DOWN:
			reps.append(c)
	var builds: Array = [null]
	builds.append_array(TYPES)
	var out: Array = []
	for r: Variant in reps:
		for b: Variant in builds:
			for inten: String in INTENSITY_ORDER:
				var cost := (0 if _is_none(r) else repair_cost(leg, r, inten)) + (0 if _is_none(b) else SENTRY_PRICE)
				if cost <= bank:
					out.append([r, b, inten])
	return out


# ---------------------------------------------------------------- forecast and planner

## The best response for one sealed candidate over opts, ranked by the mean mid-leg value over the HUNTER_CANDS
## hunter streets (L13 R2: chosen without knowing the street). {value, response, outcomes: [{state, touches}] per
## hunt}; ties keep the earliest response. Empty when no option resolves.
static func _best_for(leg: Dictionary, raid_i: int, st: Dictionary, k: int, place: Dictionary, opts: Array, mid: bool) -> Dictionary:
	var best: Dictionary = {}
	for r: Array in opts:
		var outs: Array = []
		var total := 0.0
		var ok := true
		for h in range(HUNTER_CANDS):
			var res := _resolve(leg, raid_i, st, k, h, place, r)
			if res["error"] != "":
				ok = false
				break
			total += score(leg, res["state"], mid)
			outs.append({"state": res["state"], "touches": _touches(res["trace"])})
		if not ok:
			continue
		var v := total / HUNTER_CANDS
		if best.is_empty() or v > float(best["value"]) + EPS:
			best = {"value": v, "response": r, "outcomes": outs}
	return best


## sweep_l8._best_per_cand: per sealed candidate, the greedy response (mean over the hunter streets); see _best_for.
static func _best_per_cand(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary, mid: bool) -> Array:
	var opts := response_options(leg, raid_i, st, 0, place)
	var per: Array = []
	for k in range(CANDIDATES):
		per.append(_best_for(leg, raid_i, st, k, place, opts, mid))
	return per


## sweep_l8.forecast (L13 R2): per sealed candidate {cand, outcomes: [HOLD for hunt 0, HOLD for hunt 1]}, each
## outcome {state, touches, tier}. Empty on an illegal placement.
static func forecast(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary) -> Array:
	var out: Array = []
	for k in range(CANDIDATES):
		var outs: Array = []
		for h in range(HUNTER_CANDS):
			var hold := resolve(leg, raid_i, st, k, h, place, ["HOLD"])
			if hold.has("error"):
				return []
			var hs: Dictionary = hold["state"]
			outs.append({"state": hs, "touches": hold["touches"], "tier": tier(st, hs, hold["touches"])})
		out.append({"cand": k, "outcomes": outs})
	return out


# ---------------------------------------------------------------- safe_next (L11)

## True when every sealed candidate's best response (as in _best_per_cand) keeps HOME above 0 on every hunter street
## for this placement.
static func _place_safe(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary, mid: bool) -> bool:
	var opts := response_options(leg, raid_i, st, 0, place)
	for k in range(CANDIDATES):
		var best := _best_for(leg, raid_i, st, k, place, opts, mid)
		if best.is_empty():
			return false
		for o: Dictionary in best["outcomes"]:
			if int((o["state"] as Dictionary)["home_hp"]) <= 0:
				return false
	return true


## sweep_l8.safe_next (L11): true if some capture option (none when there is no option), then some placement, with
## the best response per sealed candidate, keeps HOME above 0 on every sealed candidate of raid raid_i. It runs on
## the post-decay state; decay is idempotent, so it is applied here too when raid_i > 0. True when raid_i >= RAIDS.
static func safe_next(leg: Dictionary, raid_i: int, st: Dictionary) -> bool:
	if raid_i >= RAIDS:
		return true
	var s0: Dictionary = copy_state(st)
	if raid_i > 0:
		s0 = decay(leg, s0)
	if int(s0["home_hp"]) <= 0:
		return false
	var mid := raid_i < RAIDS - 1
	var caps: Array = capture_options(leg, s0)
	if caps.is_empty():
		caps = [null]
	for cap: Variant in caps:
		var s1: Dictionary = s0 if _is_none(cap) else capture(leg, s0, cap)
		for place: Dictionary in placements(leg, s1):
			if _place_safe(leg, raid_i, s1, place, mid):
				return true
	return false


## The lab's between-screen badge: safe_next on the next raid after between(repair, build, intensity) and decay.
static func safe_after_between(leg: Dictionary, st: Dictionary, next_raid: int, repair: Variant, build: Variant, intensity: String) -> bool:
	return safe_next(leg, next_raid, between(leg, st, repair, build, intensity))
