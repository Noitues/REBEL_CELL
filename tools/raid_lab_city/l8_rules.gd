class_name L8Rules
extends RefCounted
## The round-8 (L8) city-raid rules with the L9, L10, L11, L13 and L14 changes, ported from
## tools/raid_concepts/sweep_l8.py (the oracle). It covers:
## - decay (with wounds) and capture (with the HOT extra capture);
## - the DRAW of a hand from the run deck, and card-id placements;
## - the launch: beam 1, the extras, sealed A, sealed B, and the hunter on one of two sealed streets;
## - card-gated responses (HOLD, REDEPLOY, DEPLOY, SACRIFICE, JAM);
## - between (with intensity perks, built cards and CLEAN), tier, the banded score with wounds;
## - forecast over (B, hunt), best_response, buy_hint and safe_next.
## Pure and deterministic: no global randomness, no nodes. The hand shuffle uses PyRandom, a port of CPython's
## random.Random. Cells are Vector2i (x 0..3, y 0..2); HOME is the String "HOME". Every enumeration walks CELLS (y,
## then x), never dictionary order. A card is [id, type, verb]; the deck is sorted by id (string order).
## Data shapes: docs/handoff/raid_lab_l8/GD_CONTRACT.md. Changes: L9_CHANGES.md, L10_CHANGES.md, L11_CHANGES.md,
## L13_RULES.md and L14_RULES.md (R9 deck and wounds, R1 two sealed beams, R13 hand size, R14 hint).

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
const BEAMS: Array = ["beam1", "extra1", "extra2", "sealed", "sealed_b", "hunter"]	# L14 R1: sealed_b

# Leg shape.
const VALUES: Array = [4, 6, 8, 10, 12]
const EXPLOITS := 3
const START_CELLS := 2
const RAIDS := 3
const CANDIDATES := 3
const HUNTER_CANDS := 2		# L13 R2: two sealed hunter streets per raid
const HUNTER_SEED := 9100	# L13 R2: random.Random(HUNTER_SEED + 13 * seed + raid) in the Python oracle
const SEALB_SEED := 9200	# L14 R1: random.Random(SEALB_SEED + 13 * seed + raid) draws real_b (oracle only)
const HAND_SEED := 9300		# L14 R9: random.Random(HAND_SEED + 13 * seed + raid) shuffles the deck ids

# Cell statuses.
const HOME := "HOME"
const OK := "OK"
const DOWN := "DOWN"
const TAKEN := "TAKEN"

# Cards (L14 R9).
const V_GUARD := "GUARD"
const V_SHIFT := "SHIFT"
const V_JAM := "JAM"
const V_WOUND := "WOUND"
const WOUND_TYPE := "-"
const CLEAN := "CLEAN"
const START_DECK: Array = [
	["s0", "D", "GUARD"], ["s1", "D", "GUARD"], ["s2", "N", "GUARD"], ["s3", "N", "GUARD"],
	["s4", "E", "GUARD"], ["s5", "D", "SHIFT"], ["s6", "E", "SHIFT"], ["s7", "N", "JAM"],
]
const HAND_BASE := 4		# L14 R13: + 1 at Heat >= EXTRA_AT, + 1 at Heat >= STRONG_AT

# Economy and Heat.
const START_BANK := 10
const START_HEAT := 44
const EXTRA_AT := 50
const STRONG_AT := 75
const HOME_HP := 3
const GHOST_HEAT := 5
const SPOOF_HEAT := 2		# every response but HOLD and SACRIFICE
const EVADE_HEAT := 10
const HINT_HEAT := 3		# L14 R14: buy_hint
const SENTRY_PRICE := 3		# L9: was 4
const CLEAN_PRICE := 4		# L14 R9: remove the highest-id wound
const REPAIR_DIV := 2
const INCOME_DIV := 3
const MAX_PLACED := 2		# L11: PLAN places at most 2 sentries
const KIT_START: Dictionary = {"ghost": 2}	# L14 R9: spoof removed (responses are paid with cards)
const INTENSITY_ORDER: Array = ["LOW", "NORMAL", "HOT"]
const INTENSITY: Dictionary = {"LOW": [6, 0.5], "NORMAL": [12, 1.0], "HOT": [18, 0.5]}	# L13b: HOT income x0.5
const FREE_REPAIR_AT := "NORMAL"	# L13 R5: this between step's repair is free
const EXTRA_CAPTURE_AT := "HOT"	# L13 R5: the next raid's CAPTURE takes two cells

# Score.
const EXPLOIT_BONUS := 6
const HOME_LOSS_COST := 15	# L13 R4: was 8
const HEAT_CARRY := 0.5		# L13 R4: was 1.0
const HEAT_BAND := 6		# L13 R4: per band reached (heat >= EXTRA_AT, heat >= STRONG_AT)
const WOUND_COST := 5		# L14 R9: per wound in the deck
const BREACH := 100
const KIT_VALUE := 2.5	# planner heuristic only: per unspent ghost and per built card, mid-leg
const EPS := 1e-9		# float ties keep the earlier option

## Shuffled deck-id orders by "rng seed|ids" (the shuffle only depends on these).
static var _hand_cache: Dictionary = {}


# ---------------------------------------------------------------- PyRandom

## A port of CPython 3.11 random.Random for non-negative int seeds: MT19937 with init_by_array, getrandbits (k <= 32),
## _randbelow_with_getrandbits and shuffle. Used only for the L14 hand shuffle.
class PyRandom extends RefCounted:
	const MT_N := 624
	const MT_M := 397
	const MATRIX_A := 0x9908b0df
	const UPPER := 0x80000000
	const LOWER := 0x7fffffff
	const MASK := 0xffffffff
	var mt := PackedInt64Array()
	var mti := MT_N + 1

	func _init(seed_value: int) -> void:
		var key: Array = []
		var n := absi(seed_value)
		if n == 0:
			key.append(0)
		while n > 0:
			key.append(n & MASK)
			n = n >> 32
		_init_by_array(key)

	func _init_genrand(s: int) -> void:
		mt.resize(MT_N)
		mt[0] = s & MASK
		for i in range(1, MT_N):
			var prev: int = mt[i - 1]
			mt[i] = (1812433253 * (prev ^ (prev >> 30)) + i) & MASK
		mti = MT_N

	func _init_by_array(key: Array) -> void:
		_init_genrand(19650218)
		var i := 1
		var j := 0
		var kl := key.size()
		var k := maxi(MT_N, kl)
		while k > 0:
			var prev: int = mt[i - 1]
			mt[i] = ((mt[i] ^ ((prev ^ (prev >> 30)) * 1664525)) + int(key[j]) + j) & MASK
			i += 1
			j += 1
			if i >= MT_N:
				mt[0] = mt[MT_N - 1]
				i = 1
			if j >= kl:
				j = 0
			k -= 1
		k = MT_N - 1
		while k > 0:
			var prev: int = mt[i - 1]
			mt[i] = ((mt[i] ^ ((prev ^ (prev >> 30)) * 1566083941)) - i) & MASK
			i += 1
			if i >= MT_N:
				mt[0] = mt[MT_N - 1]
				i = 1
			k -= 1
		mt[0] = UPPER

	func _mag(y: int) -> int:
		return MATRIX_A if (y & 1) == 1 else 0

	## genrand_uint32.
	func next_u32() -> int:
		if mti >= MT_N:
			for kk in range(MT_N - MT_M):
				var y: int = (mt[kk] & UPPER) | (mt[kk + 1] & LOWER)
				mt[kk] = mt[kk + MT_M] ^ (y >> 1) ^ _mag(y)
			for kk in range(MT_N - MT_M, MT_N - 1):
				var y: int = (mt[kk] & UPPER) | (mt[kk + 1] & LOWER)
				mt[kk] = mt[kk + (MT_M - MT_N)] ^ (y >> 1) ^ _mag(y)
			var yl: int = (mt[MT_N - 1] & UPPER) | (mt[0] & LOWER)
			mt[MT_N - 1] = mt[MT_M - 1] ^ (yl >> 1) ^ _mag(yl)
			mti = 0
		var z: int = mt[mti]
		mti += 1
		z = z ^ (z >> 11)
		z = z ^ ((z << 7) & 0x9d2c5680)
		z = z ^ ((z << 15) & 0xefc60000)
		z = z ^ (z >> 18)
		return z & MASK

	## getrandbits(k) for 1 <= k <= 32.
	func getrandbits(k: int) -> int:
		return next_u32() >> (32 - k)

	## _randbelow_with_getrandbits(n), n >= 1.
	func randbelow(n: int) -> int:
		var k := 0
		var m := n
		while m > 0:
			k += 1
			m = m >> 1
		var r := getrandbits(k)
		while r >= n:
			r = getrandbits(k)
		return r

	## random.shuffle (3.11): for i in reversed(range(1, len(x))): j = randbelow(i + 1); swap.
	func shuffle(arr: Array) -> void:
		for i in range(arr.size() - 1, 0, -1):
			var j := randbelow(i + 1)
			var tmp: Variant = arr[i]
			arr[i] = arr[j]
			arr[j] = tmp


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
		"SPOOF_HEAT": SPOOF_HEAT, "EVADE_HEAT": EVADE_HEAT, "SENTRY_PRICE": SENTRY_PRICE, "DECAY": true,
		"HUNTER_CANDS": HUNTER_CANDS, "HUNTER_SEED": HUNTER_SEED,
		"PERKS": {"HOT": "EXTRA_CAPTURE", "LOW": null, "NORMAL": "FREE_REPAIR"},
		"KIT_START": KIT_START.duplicate(), "INTENSITY": inten, "EXPLOIT_BONUS": EXPLOIT_BONUS,
		"HOME_LOSS_COST": HOME_LOSS_COST, "HEAT_CARRY": HEAT_CARRY, "HEAT_BAND": HEAT_BAND, "BREACH": BREACH,
		"KIT_VALUE": KIT_VALUE, "MAX_PLACED": MAX_PLACED, "START_DECK": START_DECK.duplicate(true),
		"HAND_BASE": HAND_BASE, "HAND_SEED": HAND_SEED, "SEALB_SEED": SEALB_SEED, "WOUND_COST": WOUND_COST,
		"CLEAN_PRICE": CLEAN_PRICE, "HINT_HEAT": HINT_HEAT}


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


static func _kit_t(d: Dictionary) -> Dictionary:
	return {"ghost": int(d.get("ghost", 0))}


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


# ---------------------------------------------------------------- deck (L14 R9)

## Sorts a deck in place by card id (string order).
static func _sort_deck(deck: Array) -> void:
	deck.sort_custom(func(a: Variant, b: Variant) -> bool: return String(a[0]) < String(b[0]))


## A deck copy: cards [id, type, verb] (from arrays or {id, type, verb}), sorted by id.
static func _deck_t(raw: Variant) -> Array:
	var out: Array = []
	if typeof(raw) == TYPE_ARRAY:
		for e: Variant in raw:
			if typeof(e) == TYPE_DICTIONARY:
				out.append([String(e["id"]), String(e["type"]), String(e["verb"])])
			else:
				out.append([String(e[0]), String(e[1]), String(e[2])])
	_sort_deck(out)
	return out


static func _find_card(deck: Array, id: String) -> Array:
	for cd: Array in deck:
		if String(cd[0]) == id:
			return cd
	return []


## The card [id, type, verb] with this id in the state's deck, or [] when absent.
static func card_of(st: Dictionary, id: String) -> Array:
	var cd := _find_card(st["deck"], id)
	return cd.duplicate()


## The sentry type of a card id ("" when absent; "-" for a wound).
static func card_type(st: Dictionary, id: String) -> String:
	var cd := _find_card(st["deck"], id)
	return "" if cd.is_empty() else String(cd[1])


static func is_wound(cd: Array) -> bool:
	return not cd.is_empty() and String(cd[2]) == V_WOUND


## The deck ids in id order.
static func deck_ids(st: Dictionary) -> Array:
	var ids: Array = []
	for cd: Array in st["deck"]:
		ids.append(String(cd[0]))
	ids.sort()
	return ids


static func _wounds_in(deck: Array) -> int:
	var n := 0
	for cd: Array in deck:
		if String(cd[2]) == V_WOUND:
			n += 1
	return n


static func _built_in(deck: Array) -> int:
	var n := 0
	for cd: Array in deck:
		if String(cd[0]).begins_with("b"):
			n += 1
	return n


## The number of wound cards in the deck.
static func wound_count(st: Dictionary) -> int:
	return _wounds_in(st["deck"])


## The number of built cards (ids b<k>) in the deck.
static func built_count(st: Dictionary) -> int:
	return _built_in(st["deck"])


## Adds ("w<k>", "-", "WOUND") to the deck in place, k = the wounds already in it; keeps the deck sorted.
static func _add_wound(deck: Array) -> void:
	deck.append(["w%d" % _wounds_in(deck), WOUND_TYPE, V_WOUND])
	_sort_deck(deck)


## The highest wound id (string order), or "".
static func _highest_wound(deck: Array) -> String:
	var best := ""
	for cd: Array in deck:
		if String(cd[2]) == V_WOUND and (best == "" or String(cd[0]) > best):
			best = String(cd[0])
	return best


## A deep copy of a state (L14: deck replaces pool; kit is ghost only).
static func copy_state(st: Dictionary) -> Dictionary:
	return {"heat": int(st["heat"]), "bank": int(st["bank"]), "home_hp": int(st["home_hp"]),
		"owned": _ordered(st["owned"]), "sentries": _ordered(st["sentries"]), "deck": _deck_t(st["deck"]),
		"kit": _kit_t(st["kit"]), "extra_capture": int(st.get("extra_capture", 0))}


## L14 R9/R14: the state after buying the scan: Heat + HINT_HEAT.
static func buy_hint(st: Dictionary) -> Dictionary:
	var out := copy_state(st)
	out["heat"] = int(out["heat"]) + HINT_HEAT
	return out


# ---------------------------------------------------------------- hand (L14 R9, R13)

## L14 R13: HAND_BASE, plus 1 at Heat >= EXTRA_AT, plus 1 at Heat >= STRONG_AT.
static func hand_size(heat: int) -> int:
	return HAND_BASE + (1 if heat >= EXTRA_AT else 0) + (1 if heat >= STRONG_AT else 0)


## sweep_l8.hand: the deck ids in id order, shuffled with random.Random(HAND_SEED + 13 * seed + raid). It returns
## the first hand_size(st.heat) ids, using the draw-time Heat without the ghost. Pass the post-decay, post-capture
## state.
static func hand(leg: Dictionary, raid_i: int, st: Dictionary) -> Array:
	var ids := deck_ids(st)
	var rs: int = HAND_SEED + 13 * int(leg["seed"]) + raid_i
	var key := "%d|%s" % [rs, ",".join(PackedStringArray(ids))]
	var order: Array
	if _hand_cache.has(key):
		order = _hand_cache[key]
	else:
		order = ids.duplicate()
		var rng := PyRandom.new(rs)
		rng.shuffle(order)
		if _hand_cache.size() > 4096:
			_hand_cache.clear()
		_hand_cache[key] = order
	return order.slice(0, mini(hand_size(int(st["heat"])), order.size()))


## The hand as cards [id, type, verb], in hand order (for the view).
static func hand_cards(leg: Dictionary, raid_i: int, st: Dictionary) -> Array:
	var out: Array = []
	for id: String in hand(leg, raid_i, st):
		out.append(card_of(st, id))
	return out


## The response hand: the hand minus the placed cards (place.sentries), in hand order; wounds included (they are dead).
static func response_hand(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary) -> Array:
	var p := _norm_place(place)
	var placed := {}
	for c: Vector2i in p["sentries"]:
		placed[String(p["sentries"][c])] = true
	var out: Array = []
	for id: String in hand(leg, raid_i, st):
		if not placed.has(id):
			out.append(id)
	return out


## The usable response cards (non-wound, not placed) as [id, type, verb] in hand order.
static func _response_cards(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary) -> Array:
	var out: Array = []
	for id: String in response_hand(leg, raid_i, st, place):
		var cd := _find_card(st["deck"], id)
		if not cd.is_empty() and not is_wound(cd):
			out.append(cd.duplicate())
	return out


static func _has_verb(cards_in: Array, verb: String) -> bool:
	for cd: Array in cards_in:
		if String(cd[2]) == verb:
			return true
	return false


static func _first_verb(cards_in: Array, verb: String) -> String:
	for cd: Array in cards_in:
		if String(cd[2]) == verb:
			return String(cd[0])
	return ""


## The first card of type t in hand order ("" when none).
static func _first_of_type(cards_in: Array, t: String) -> String:
	var best := ""
	for cd: Array in cards_in:
		if String(cd[1]) == t and (best == "" or String(cd[0]) < best):
			best = String(cd[0])
	return best


## The unplaced non-wound hand cards by type ({D, N, E}), for the lab's reserve tray.
static func reserve_counts(leg: Dictionary, raid_i: int, st: Dictionary, sentries: Dictionary) -> Dictionary:
	var placed := {}
	for k: Variant in sentries:
		placed[String(sentries[k])] = true
	var out := {"D": 0, "N": 0, "E": 0}
	for id: String in hand(leg, raid_i, st):
		var cd := _find_card(st["deck"], id)
		if placed.has(id) or cd.is_empty() or is_wound(cd):
			continue
		out[String(cd[1])] = int(out[String(cd[1])]) + 1
	return out


# ---------------------------------------------------------------- small rules

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


## L14 R1: the B candidates for sealed route A: the two other routes, in route order.
static func other_cands(k: int) -> Array:
	var out: Array = []
	for j in range(CANDIDATES):
		if j != k:
			out.append(j)
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
## Each raid carries hunter_cands and hunter_real (L13 R2), and real_b, the second sealed route (L14 R1).
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
			"real_b": int(r["real_b"]), "hunter_type": String(r["hunter_type"]), "hunter_cands": hc,
			"hunter_real": int(r["hunter_real"])})
	return {"seed": int(d.get("seed", 0)), "values": _ordered(values), "exploits": _sort_cells(ex),
		"start": _sort_cells(start), "raids": raids}


## sweep_l8.initial: the leg-start state: the seeded x = 0 cells owned OK, deck START_DECK, kit KIT_START, and
## extra_capture 0.
static func initial(leg: Dictionary) -> Dictionary:
	var owned := {}
	for c: Vector2i in leg["start"]:
		owned[c] = OK
	return {"heat": START_HEAT, "bank": START_BANK, "home_hp": HOME_HP, "owned": _ordered(owned), "sentries": {},
		"deck": _deck_t(START_DECK.duplicate(true)), "kit": KIT_START.duplicate(), "extra_capture": 0}


## A state from the golden's state_json form (owned [[x, y, s]], sentries [[x, y, card_id]], deck [[id, type, verb]]).
static func state_from_json(d: Dictionary) -> Dictionary:
	var owned := {}
	for e: Variant in d["owned"]:
		owned[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	var sent := {}
	for e: Variant in d["sentries"]:
		sent[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	return {"heat": int(d["heat"]), "bank": int(d["bank"]), "home_hp": int(d["home_hp"]), "owned": _ordered(owned),
		"sentries": _ordered(sent), "deck": _deck_t(d.get("deck", [])), "kit": _kit_t(d["kit"]),
		"extra_capture": int(d.get("extra_capture", 0))}


## A state in the golden's state_json form (lists in cell order, deck by id, kit ghost, extra_capture).
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
	var deck: Array = []
	for cd: Array in _deck_t(st["deck"]):
		deck.append([String(cd[0]), String(cd[1]), String(cd[2])])
	return {"heat": int(st["heat"]), "bank": int(st["bank"]), "home_hp": int(st["home_hp"]), "owned": owned,
		"sentries": sent, "deck": deck, "kit": _kit_t(st["kit"]), "extra_capture": int(st.get("extra_capture", 0))}


## A place from JSON {sentries: [[x, y, card_id]] or {cell: card_id}, ghost: null | "HOME" | [x, y]}.
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


## A place in JSON form (sentries as [[x, y, card_id]] in cell order).
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


# ---------------------------------------------------------------- decay (L9, L11, L14)

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


## sweep_l8.decay: every owned cell whose status is still DOWN becomes TAKEN, in cell order.
## - Its card leaves the placement (the card stays in the deck).
## - L14 R9: each one adds a wound.
## The caller applies it at the start of every raid after the first, before CAPTURE. Idempotent.
static func decay(leg: Dictionary, st: Dictionary) -> Dictionary:
	var out := copy_state(st)
	var owned: Dictionary = out["owned"]
	var sent: Dictionary = out["sentries"]
	var deck: Array = out["deck"]
	for c: Vector2i in CELLS:
		if _status(owned, c) == DOWN:
			owned[c] = TAKEN
			if sent.has(c):
				sent.erase(c)
			_add_wound(deck)
	out["owned"] = _ordered(owned)
	out["sentries"] = _ordered(sent)
	out["deck"] = deck
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


## L13 R5: the whole CAPTURE phase.
## - Capture cells[0], then cells[1] if extra_capture > 0, each from the updated state's options.
## - Then clear extra_capture.
## cells holds 0 to 2 cells (0 only when there is no option).
static func capture_all(leg: Dictionary, st: Dictionary, cells_in: Array) -> Dictionary:
	var out := copy_state(st)
	var n := mini(cells_in.size(), capture_slots(st))
	for i in range(n):
		out = capture(leg, out, cells_in[i])
	return end_capture(out)


static func _sig(cd: Array) -> String:
	return String(cd[1]) + ":" + String(cd[2])


static func _place_rec(live: Array, sigs: Array, groups: Dictionary, used: Dictionary, idx: int, cur: Dictionary, k: int, maps: Array) -> void:
	if k == 0:
		maps.append(cur.duplicate())
		return
	if live.size() - idx < k:
		return
	var c: Vector2i = live[idx]
	for sg: String in sigs:
		var pick := ""
		for id: String in groups[sg]:
			if not used.has(id):
				pick = id
				break
		if pick == "":
			continue
		used[pick] = true
		cur[c] = pick
		_place_rec(live, sigs, groups, used, idx + 1, cur, k - 1, maps)
		cur.erase(c)
		used.erase(pick)
	_place_rec(live, sigs, groups, used, idx + 1, cur, k, maps)


## sweep_l8.placements (L14 R9): every {sentries: {cell: card_id}, ghost}.
## - Count: min(non-wound hand cards, live cells, MAX_PLACED) cards are placed, at most 1 per live cell.
## - Distinct by the (type, verb) signature on each cell; within a signature, the lowest unused id is placed.
## - Order: cells in cell order, then signatures by first appearance in hand order, then skip.
## - Ghost order: null, HOME, then live cells.
static func placements(leg: Dictionary, raid_i: int, st: Dictionary) -> Array:
	var live := live_cells(st)
	var sigs: Array = []
	var groups := {}
	var n_cards := 0
	for id: String in hand(leg, raid_i, st):
		var cd := _find_card(st["deck"], id)
		if cd.is_empty() or is_wound(cd):
			continue
		n_cards += 1
		var sg := _sig(cd)
		if not groups.has(sg):
			sigs.append(sg)
			groups[sg] = []
		(groups[sg] as Array).append(id)
	for sg: String in sigs:
		(groups[sg] as Array).sort()
	var need := mini(mini(n_cards, live.size()), MAX_PLACED)
	var maps: Array = []
	_place_rec(live, sigs, groups, {}, 0, {}, need, maps)
	var ghosts: Array = [null]
	if int(st["kit"]["ghost"]) > 0:
		ghosts.append(HOME)
		ghosts.append_array(live)
	var out: Array = []
	for g: Variant in ghosts:
		for m: Dictionary in maps:
			out.append({"sentries": m.duplicate(), "ghost": g})
	return out


## sweep_l8._check_place: "" when the place is legal for the state and this raid's hand, else the reason. The rules:
## - at most MAX_PLACED distinct non-wound hand cards;
## - each card on a live cell;
## - the ghost from the kit, on HOME or a live cell.
static func check_place(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary) -> String:
	var p := _norm_place(place)
	var sd: Dictionary = p["sentries"]
	if sd.size() != (place.get("sentries", {}) as Dictionary).size():
		return "illegal sentry cell"
	if sd.size() > MAX_PLACED:
		return "more than %d sentries placed" % MAX_PLACED
	var hids := hand(leg, raid_i, st)
	var used := {}
	for c: Vector2i in sd:
		var id := String(sd[c])
		if not is_live(st, c):
			return "illegal sentry cell %s" % str(c)
		if not hids.has(id):
			return "card %s not in hand" % id
		var cd := _find_card(st["deck"], id)
		if cd.is_empty() or is_wound(cd):
			return "card %s cannot be placed" % id
		if used.has(id):
			return "card %s placed twice" % id
		used[id] = true
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


## True when the response needs a card and costs SPOOF_HEAT (everything but HOLD and SACRIFICE).
static func response_spoofs(r: Variant) -> bool:
	var a := norm_response(r)
	return not a.is_empty() and a[0] != "HOLD" and a[0] != "SACRIFICE"


## L14 R9: the response-hand card that pays for or carries the response ("" for HOLD, SACRIFICE or no such card).
## - REDEPLOY: the first SHIFT card.
## - DEPLOY t: the first card of type t, which is the one deployed.
## - JAM: the first JAM card.
static func response_card(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary, r: Variant) -> String:
	var a := norm_response(r)
	if a.is_empty():
		return ""
	var rh := _response_cards(leg, raid_i, st, place)
	match String(a[0]):
		"REDEPLOY":
			return _first_verb(rh, V_SHIFT)
		"DEPLOY":
			return _first_of_type(rh, String(a[1]))
		"JAM":
			return _first_verb(rh, V_JAM)
	return ""


# ---------------------------------------------------------------- the sweep

static func _type_map(deck: Array) -> Dictionary:
	var out := {}
	for cd: Array in deck:
		out[String(cd[0])] = String(cd[1])
	return out


static func _new_sweep(st: Dictionary, place: Dictionary) -> Dictionary:
	var deck := _deck_t(st["deck"])
	return {"sent": (place["sentries"] as Dictionary).duplicate(), "ghost": place["ghost"],
		"owned": (st["owned"] as Dictionary).duplicate(), "hp": int(st["home_hp"]), "home_hit": false,
		"shield": false, "seen": {}, "trace": [], "deck": deck, "types": _type_map(deck)}


## A live cell turns TAKEN: its card leaves the placement (L11), and a wound joins the deck (L14 R9).
static func _take(sw: Dictionary, c: Vector2i) -> void:
	var owned: Dictionary = sw["owned"]
	var sent: Dictionary = sw["sent"]
	owned[c] = TAKEN
	if sent.has(c):
		sent.erase(c)
	_add_wound(sw["deck"])


## sweep_l8._Sweep.scan: one line, cell by cell (ghost pass, typed BLOCK stops the line, HIT, else pass), then HOME.
## A sentry's type is its card's type. L13 R3: after a SACRIFICE, a route reaching HOME records ("HOME",
## "shielded") and HOME is unharmed.
static func _scan(sw: Dictionary, beam: String, ln: Dictionary) -> void:
	var sent: Dictionary = sw["sent"]
	var owned: Dictionary = sw["owned"]
	var seen: Dictionary = sw["seen"]
	var types: Dictionary = sw["types"]
	var tr: Array = sw["trace"]
	var t := String(ln["type"])
	for c: Vector2i in ln["cells"]:
		if _same(c, sw["ghost"]):
			continue
		if sent.has(c) and String(types.get(String(sent[c]), "")) == t:
			tr.append([beam, c, "block"])
			return
		var s := _status(owned, c)
		if _live_status(s) and not seen.has(c):
			if s == OK:
				owned[c] = DOWN
			else:
				_take(sw, c)
			tr.append([beam, c, "hit"])
			seen[c] = true
	if bool(ln["home"]) and not _same(sw["ghost"], HOME) and not bool(sw["home_hit"]):
		if bool(sw["shield"]):
			tr.append([beam, HOME, "shielded"])
		else:
			sw["hp"] = maxi(0, int(sw["hp"]) - 1)
			sw["home_hit"] = true
			tr.append([beam, HOME, "home"])


## sweep_l8._launch: beam 1 and the extras (before the reveal). It returns {error, raid, heat (launch Heat), sw,
## resp}, where resp is the usable response cards.
static func _launch(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary) -> Dictionary:
	var err := check_place(leg, raid_i, st, place)
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
	return {"error": "", "raid": rd, "heat": heat, "sw": sw, "resp": _response_cards(leg, raid_i, st, p)}


## L13 R2: the street index the hunter runs for hunter street candidate hunt (0 or 1).
static func hunter_street_of(leg: Dictionary, raid_i: int, hunt: int) -> int:
	return int((leg["raids"][raid_i]["hunter_cands"] as Array)[hunt])


## sweep_l8._resolve: {error, state, trace, heat_launch}.
static func _resolve(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, cand_b: int, hunt: int, place: Dictionary, response: Variant) -> Dictionary:
	var resp := norm_response(response)
	if resp.is_empty():
		return {"error": "unknown response %s" % str(response)}
	if cand_b == cand:
		return {"error": "cand_b equals cand %d" % cand}
	var kit := _kit_t(st["kit"])
	var la := _launch(leg, raid_i, st, place)
	if la["error"] != "":
		return {"error": la["error"]}
	var rd: Dictionary = la["raid"]
	var hc: Array = rd["hunter_cands"]
	if hunt < 0 or hunt >= hc.size():
		return {"error": "illegal hunter street %d" % hunt}
	var nc := (rd["cands"] as Array).size()
	if cand < 0 or cand >= nc:
		return {"error": "illegal candidate %d" % cand}
	if cand_b < 0 or cand_b >= nc:
		return {"error": "illegal candidate b %d" % cand_b}
	var heat: int = la["heat"]
	var sw: Dictionary = la["sw"]
	var sent: Dictionary = sw["sent"]
	var owned: Dictionary = sw["owned"]
	var rh: Array = la["resp"]
	if resp[0] == "REDEPLOY":
		var s: Variant = resp[1]
		var c: Variant = resp[2]
		if not _has_verb(rh, V_SHIFT):
			return {"error": "no SHIFT card for redeploy"}
		if not sent.has(s) or _same(c, s) or sent.has(c) or not _live_status(_status(owned, c)):
			return {"error": "illegal redeploy %s -> %s" % [str(s), str(c)]}
		var id: Variant = sent[s]
		sent.erase(s)
		sent[c] = id
	elif resp[0] == "DEPLOY":
		var dt := String(resp[1])
		var dc: Variant = resp[2]
		var dcard := _first_of_type(rh, dt) if TYPES.has(dt) else ""
		if dcard == "" or typeof(dc) != TYPE_VECTOR2I or sent.has(dc) or not _live_status(_status(owned, dc)):
			return {"error": "illegal deploy %s -> %s" % [dt, str(dc)]}
		sent[dc] = dcard
	elif resp[0] == "SACRIFICE":
		var sc: Variant = resp[1]
		if typeof(sc) != TYPE_VECTOR2I or not _live_status(_status(owned, sc)):
			return {"error": "illegal sacrifice %s" % str(sc)}
		_take(sw, sc)
		sw["shield"] = true
	elif resp[0] == "JAM":
		if not _has_verb(rh, V_JAM):
			return {"error": "no JAM card"}
	_scan(sw, "sealed", rd["cands"][cand])
	_scan(sw, "sealed_b", rd["cands"][cand_b])
	if resp[0] != "JAM":
		_scan(sw, "hunter", street(int(hc[hunt]), true, String(rd["hunter_type"])))
	var tr: Array = sw["trace"]
	var heat_launch := heat
	if tr.is_empty() and not bool(sw.get("shield", false)):
		heat -= EVADE_HEAT
	if response_spoofs(resp):
		heat += SPOOF_HEAT
	if not _is_none(to_cell(place.get("ghost"))):
		kit["ghost"] = int(kit["ghost"]) - 1
	var ns := {"heat": heat, "bank": int(st["bank"]), "home_hp": int(sw["hp"]), "owned": _ordered(owned),
		"sentries": _ordered(sent), "deck": sw["deck"], "kit": kit, "extra_capture": int(st.get("extra_capture", 0))}
	return {"error": "", "state": ns, "trace": tr, "heat_launch": heat_launch}


static func _touches(tr: Array) -> Array:
	var touches: Array = []
	for e: Array in tr:
		touches.append([e[1], e[2]])
	return touches


## sweep_l8.resolve: one raid (raid = index into leg.raids) from the post-capture state, with any legal response.
## - Inputs: sealed A cand, sealed B cand_b (!= cand) and hunter street candidate hunt; callers pass raid.real,
##   raid.real_b and raid.hunter_real for the real line.
## - Returns {state (after the raid), touches: [[cell | "HOME", "hit" | "block" | "home" | "shielded"]], trace,
##   heat_launch}.
## - On illegal input: push_error and {error, state: {}, touches: [], trace: []}.
static func resolve(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, cand_b: int, hunt: int, place: Dictionary, response: Variant = null) -> Dictionary:
	var r := _resolve(leg, raid_i, st, cand, cand_b, hunt, place, response)
	if r["error"] != "":
		_fail(r["error"])
		return {"error": r["error"], "state": {}, "touches": [], "trace": []}
	return {"state": r["state"], "touches": _touches(r["trace"]), "trace": r["trace"], "heat_launch": r["heat_launch"]}


## sweep_l8.trace: the touches with their beam, [[beam, cell | "HOME", kind]], beam in BEAMS (the lab's cues).
static func trace(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, cand_b: int, hunt: int, place: Dictionary, response: Variant = null) -> Array:
	var r := _resolve(leg, raid_i, st, cand, cand_b, hunt, place, response)
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
## cand, cand_b, st and place do not change the line.
static func hunter_line(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, cand_b: int, hunt: int, place: Dictionary, response: Variant = null) -> Variant:
	var resp := norm_response(response)
	if not resp.is_empty() and resp[0] == "JAM":
		return null
	var rd: Dictionary = leg["raids"][raid_i]
	return street(hunter_street_of(leg, raid_i, hunt), true, String(rd["hunter_type"]))


## sweep_l8.response_options, in this order:
## 1. HOLD;
## 2. every REDEPLOY (with a SHIFT card in the response hand; source in cell order, then target in cell order);
## 3. every DEPLOY (types in D, N, E order with a response-hand card of that type, then target in cell order);
## 4. every SACRIFICE (live cells in cell order);
## 5. JAM (with a JAM card in the response hand).
## Legality is read after beam 1 and the extras.
static func response_options(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, place: Dictionary) -> Array:
	var out: Array = [["HOLD"]]
	var la := _launch(leg, raid_i, st, place)
	if la["error"] != "":
		_fail(la["error"])
		return out
	var sw: Dictionary = la["sw"]
	var sent: Dictionary = sw["sent"]
	var owned: Dictionary = sw["owned"]
	var rh: Array = la["resp"]
	var live: Array = []
	var targets: Array = []
	for c: Vector2i in CELLS:
		if _live_status(_status(owned, c)):
			live.append(c)
			if not sent.has(c):
				targets.append(c)
	if _has_verb(rh, V_SHIFT):
		for s: Vector2i in sorted_cells(sent):
			for c: Vector2i in targets:
				if c != s:
					out.append(["REDEPLOY", s, c])
	for t: String in TYPES:
		if _first_of_type(rh, t) != "":
			for c: Vector2i in targets:
				out.append(["DEPLOY", t, c])
	for c: Vector2i in live:
		out.append(["SACRIFICE", c])
	if _has_verb(rh, V_JAM):
		out.append(["JAM"])
	return out


# ---------------------------------------------------------------- outcome

## sweep_l8.tier, in order:
## - BREACHED: HOME at 0;
## - DAMAGED: HOME lost integrity;
## - EVADED: no touches and no newly TAKEN cell;
## - BATTERED: 2+ cells newly DOWN, or any newly TAKEN (a SACRIFICE included);
## - HOLDS: otherwise.
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


## sweep_l8.score. A breach is -BREACH. Otherwise:
## - plus bank;
## - plus sum(v - (v // 2 if DOWN)) over owned non-TAKEN cells;
## - plus EXPLOIT_BONUS per owned non-TAKEN exploit;
## - minus HOME_LOSS_COST per HOME lost;
## - minus the banded Heat term (L13 R4);
## - minus WOUND_COST per wound (L14 R9).
## mid adds KIT_VALUE per unspent ghost and per built card (planner heuristic only).
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
	s -= WOUND_COST * wound_count(st)
	if mid:
		s += KIT_VALUE * (int(st["kit"]["ghost"]) + built_count(st))
	return s


## The score's terms for the RECORD screen and the HUD breakdown: {bank, cells, exploits, home_loss, heat_carry
## (the whole Heat term), heat_bands (its band part), wounds (WOUND_COST per wound), total, breach}.
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
		"heat_bands": bands, "wounds": WOUND_COST * wound_count(st), "total": score(leg, st),
		"breach": int(st["home_hp"]) <= 0}


# ---------------------------------------------------------------- between raids

## The pieces of the between step, for the ledger: {repaired, repair_cost, built (the build string or null),
## build_cost, new_card (id or null), cleaned (wound id or null), income, heat_add, extra_capture, state}.
## Order: repair (free under NORMAL), build (a type adds ("b<k>", t, GUARD); CLEAN removes the highest-id wound),
## income, Heat, perk flag. An unaffordable or illegal repair or build is skipped.
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
	var deck := _deck_t(st["deck"])
	var built: Variant = null
	var bcost := 0
	var new_card: Variant = null
	var cleaned: Variant = null
	if not _is_none(build):
		var bs := String(build)
		if TYPES.has(bs) and bank >= SENTRY_PRICE:
			bank -= SENTRY_PRICE
			bcost = SENTRY_PRICE
			var id := "b%d" % _built_in(deck)
			deck.append([id, bs, V_GUARD])
			_sort_deck(deck)
			built = bs
			new_card = id
		elif bs == CLEAN and bank >= CLEAN_PRICE:
			var w := _highest_wound(deck)
			if w != "":
				bank -= CLEAN_PRICE
				bcost = CLEAN_PRICE
				for i in range(deck.size()):
					if String(deck[i][0]) == w:
						deck.remove_at(i)
						break
				built = CLEAN
				cleaned = w
	var dh := int(INTENSITY[inten][0])
	var inc := income(leg, owned, inten)
	var extra := 1 if inten == EXTRA_CAPTURE_AT else int(st.get("extra_capture", 0))
	var ns := {"heat": int(st["heat"]) + dh, "bank": bank + inc, "home_hp": int(st["home_hp"]), "owned": owned,
		"sentries": _ordered(st["sentries"]), "deck": deck, "kit": _kit_t(st["kit"]), "extra_capture": extra}
	return {"repaired": repaired, "repair_cost": rcost, "built": built, "build_cost": bcost, "new_card": new_card,
		"cleaned": cleaned, "income": inc, "heat_add": dh, "extra_capture": extra, "state": ns}


## sweep_l8.between, in order:
## 1. repair <= 1 DOWN cell (v // 2, free under NORMAL);
## 2. build null | D | N | E (SENTRY_PRICE) | CLEAN (CLEAN_PRICE);
## 3. income, Heat and the HOT extra-capture flag.
static func between(leg: Dictionary, st: Dictionary, repair: Variant, build: Variant, intensity: String = "NORMAL") -> Dictionary:
	return between_parts(leg, st, repair, build, intensity)["state"]


## sweep_l8.between_options: every affordable [repair, build, intensity].
## - repair: null, then the DOWN cells in cell order;
## - build: null, D, N, E, then CLEAN (only when a wound exists);
## - intensity: LOW, NORMAL, HOT.
## A combination is kept when its repair cost (0 under NORMAL) plus its build cost fits the bank.
static func between_options(leg: Dictionary, st: Dictionary) -> Array:
	var owned: Dictionary = st["owned"]
	var bank := int(st["bank"])
	var reps: Array = [null]
	for c: Vector2i in CELLS:
		if _status(owned, c) == DOWN:
			reps.append(c)
	var builds: Array = [null]
	builds.append_array(TYPES)
	if wound_count(st) > 0:
		builds.append(CLEAN)
	var out: Array = []
	for r: Variant in reps:
		for b: Variant in builds:
			var bcost := 0
			if not _is_none(b):
				bcost = CLEAN_PRICE if String(b) == CLEAN else SENTRY_PRICE
			for inten: String in INTENSITY_ORDER:
				var cost := (0 if _is_none(r) else repair_cost(leg, r, inten)) + bcost
				if cost <= bank:
					out.append([r, b, inten])
	return out


# ---------------------------------------------------------------- forecast and planner

## The best response for sealed route A = k over opts (L14 R1).
## - Ranking: the mean value over the 2 B routes (in route order) x HUNTER_CANDS hunter streets, chosen knowing A
##   only. Ties keep the earliest response.
## - Returns {value, response, outcomes: [[{state, touches}] per hunt] per B}.
## - Empty when no option resolves.
static func _best_for(leg: Dictionary, raid_i: int, st: Dictionary, k: int, place: Dictionary, opts: Array, mid: bool) -> Dictionary:
	var best: Dictionary = {}
	var bs := other_cands(k)
	var n := bs.size() * HUNTER_CANDS
	for r: Array in opts:
		var outs: Array = []
		var total := 0.0
		var ok := true
		for b: int in bs:
			var row: Array = []
			for h in range(HUNTER_CANDS):
				var res := _resolve(leg, raid_i, st, k, b, h, place, r)
				if res["error"] != "":
					ok = false
					break
				total += score(leg, res["state"], mid)
				row.append({"state": res["state"], "touches": _touches(res["trace"])})
			if not ok:
				break
			outs.append(row)
		if not ok:
			continue
		var v := total / n
		if best.is_empty() or v > float(best["value"]) + EPS:
			best = {"value": v, "response": r, "outcomes": outs}
	return best


## sweep_l8._best_per_cand: per sealed A, the greedy response (mean over (B, hunt)); see _best_for.
static func _best_per_cand(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary, mid: bool) -> Array:
	var opts := response_options(leg, raid_i, st, 0, place)
	var per: Array = []
	for k in range(CANDIDATES):
		per.append(_best_for(leg, raid_i, st, k, place, opts, mid))
	return per


## sweep_l8.best_response (L14 R14): the planner's response for sealed A = cand.
## - It maximizes the mean over the 4 (B, hunt) outcomes, with the earliest kept on ties.
## - mid=True before the final raid, mid=False in it.
## - ["HOLD"] when nothing resolves.
static func best_response(leg: Dictionary, raid_i: int, st: Dictionary, cand: int, place: Dictionary) -> Array:
	var opts := response_options(leg, raid_i, st, cand, place)
	var best := _best_for(leg, raid_i, st, cand, place, opts, raid_i < RAIDS - 1)
	if best.is_empty():
		return ["HOLD"]
	return (best["response"] as Array).duplicate()


## sweep_l8.forecast (L14 R1): per sealed A {cand, outcomes: [[HOLD for (b, hunt 0), (b, hunt 1)] for each b]}.
## b runs over the two other routes in route order; each outcome is {state, touches, tier}. Empty on an illegal
## placement.
static func forecast(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary) -> Array:
	var out: Array = []
	for k in range(CANDIDATES):
		var outs: Array = []
		for b: int in other_cands(k):
			var row: Array = []
			for h in range(HUNTER_CANDS):
				var hold := resolve(leg, raid_i, st, k, b, h, place, ["HOLD"])
				if hold.has("error"):
					return []
				var hs: Dictionary = hold["state"]
				row.append({"state": hs, "touches": hold["touches"], "tier": tier(st, hs, hold["touches"])})
			outs.append(row)
		out.append({"cand": k, "outcomes": outs})
	return out


# ---------------------------------------------------------------- safe_next (L11)

## True when every sealed A's best response (as in _best_per_cand) keeps HOME above 0 on every (B, hunt) for this
## placement.
static func _place_safe(leg: Dictionary, raid_i: int, st: Dictionary, place: Dictionary, mid: bool) -> bool:
	var opts := response_options(leg, raid_i, st, 0, place)
	for k in range(CANDIDATES):
		var best := _best_for(leg, raid_i, st, k, place, opts, mid)
		if best.is_empty():
			return false
		for row: Array in best["outcomes"]:
			for o: Dictionary in row:
				if int((o["state"] as Dictionary)["home_hp"]) <= 0:
					return false
	return true


## sweep_l8.safe_next (L11): true if some capture option, then some placement from this raid's hand, keeps HOME
## above 0 on every sealed A of raid raid_i, with the best response per A.
## - With no capture option, it tries the placements without a capture.
## - It runs on the post-decay state; decay is idempotent, so it is applied here too when raid_i > 0.
## - True when raid_i >= RAIDS.
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
		for place: Dictionary in placements(leg, raid_i, s1):
			if _place_safe(leg, raid_i, s1, place, mid):
				return true
	return false


## The lab's between-screen badge: safe_next on the next raid after between(repair, build, intensity) and decay.
static func safe_after_between(leg: Dictionary, st: Dictionary, next_raid: int, repair: Variant, build: Variant, intensity: String) -> bool:
	return safe_next(leg, next_raid, between(leg, st, repair, build, intensity))
