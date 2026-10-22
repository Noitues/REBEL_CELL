class_name L3Rules
extends RefCounted
## The round-3 (L3) sweep rules, ported from tools/raid_concepts/sweep_l3.py (and the sweep_l2.py it builds on):
## sweep, resolve, between, score, tier, the lever caps of `allocations`, the naive policy. Pure and deterministic: no
## randomness, no nodes. Cells are Vector2i (x 0..3, y 0..2). A leg is the dictionary of L3Data.load_leg. An alloc is
## {"ghost": Array, "dark": Array, "decoys": Array} of cells. NONE means "no spoof" / "no cell".

const NONE := Vector2i(-1, -1)
const BEAM_IDS: Array = ["b1", "extra", "extra2", "b2", "hunter"]


## Integer division (python //), values are never negative.
@warning_ignore("integer_division")
static func idiv(a: int, b: int) -> int:
	return a / b


## All 12 cells in python NODES order (row by row).
static func nodes() -> Array:
	var out: Array = []
	for y in range(L3Config.H):
		for x in range(L3Config.W):
			out.append(Vector2i(x, y))
	return out


## The column a hunter beam scans, top to bottom.
static func column(x: int) -> Array:
	var out: Array = []
	for y in range(L3Config.H):
		out.append(Vector2i(x, y))
	return out


static func empty_alloc() -> Dictionary:
	return {"ghost": [], "dark": [], "decoys": []}


static func copy_alloc(a: Dictionary) -> Dictionary:
	return {"ghost": (a["ghost"] as Array).duplicate(), "dark": (a["dark"] as Array).duplicate(),
		"decoys": (a["decoys"] as Array).duplicate()}


## How many extra known beams Heat brings: 0 below EXTRA_AT, 1 from EXTRA_AT, 2 from STRONG_AT.
static func extra_count(heat: int) -> int:
	if heat >= L3Config.STRONG_AT:
		return 2
	if heat >= L3Config.EXTRA_AT:
		return 1
	return 0


static func initial(leg: Dictionary) -> L3State:
	var s := L3State.new()
	for c in leg["values"]:
		s.status[c] = "OK"
	return s


static func _scan(leg: Dictionary, status: Dictionary, id: String, line: Array, hidden: Array, decoys: Array,
		spoof: Vector2i, seen: Array, touches: Array, first: Array) -> Dictionary:
	var steps: Array = []
	var stopped := false
	for c: Vector2i in line:
		if id == "b2" and spoof != NONE and c == spoof:
			steps.append({"cell": c, "kind": "spoofed"})
			continue
		if decoys.has(c):
			touches.append({"cell": c, "kind": "decoy", "beam": id})
			if first[0] == NONE:
				first[0] = c
			steps.append({"cell": c, "kind": "decoy"})
			stopped = true
			break
		if hidden.has(c):
			steps.append({"cell": c, "kind": "hidden"})
			continue
		if seen.has(c):
			steps.append({"cell": c, "kind": "seen"})
			continue
		if c == leg["home"]:
			touches.append({"cell": c, "kind": "home", "beam": id})
			seen.append(c)
			if first[0] == NONE:
				first[0] = c
			steps.append({"cell": c, "kind": "home"})
		elif status.has(c):
			if status[c] != "TAKEN":
				touches.append({"cell": c, "kind": "asset", "beam": id})
				seen.append(c)
				if first[0] == NONE:
					first[0] = c
				steps.append({"cell": c, "kind": "asset"})
			else:
				steps.append({"cell": c, "kind": "taken"})
		else:
			steps.append({"cell": c, "kind": "empty"})
	return {"id": id, "line": line, "steps": steps, "stopped": stopped}


## sweep_l2.sweep with a per-beam trace. `heat` is the Heat the raid runs at (after the ghost's +5).
## Returns {touches: [{cell, kind, beam}], first: Vector2i, beams: [{id, line, steps: [{cell, kind}], stopped}]}.
## Touch kinds: "asset" | "home" | "decoy". Step kinds add "spoofed", "hidden" (ghost or dark), "seen" (already
## touched), "taken" (corp ground, the beam passes) and "empty".
static func sweep(leg: Dictionary, raid_i: int, st: L3State, b2: Array, alloc: Dictionary, spoof: Vector2i, heat: int) -> Dictionary:
	var raid: Dictionary = leg["raids"][raid_i]
	var hidden: Array = (alloc["ghost"] as Array) + (alloc["dark"] as Array)
	var decoys: Array = alloc["decoys"]
	var touches: Array = []
	var first: Array = [NONE]
	var seen: Array = []
	var beams: Array = []
	beams.append(_scan(leg, st.status, "b1", raid["b1"], hidden, decoys, spoof, seen, touches, first))
	if heat >= L3Config.EXTRA_AT:
		beams.append(_scan(leg, st.status, "extra", raid["extra"], hidden, decoys, spoof, seen, touches, first))
	if heat >= L3Config.STRONG_AT:
		beams.append(_scan(leg, st.status, "extra2", raid["extra2"], hidden, decoys, spoof, seen, touches, first))
	beams.append(_scan(leg, st.status, "b2", b2, hidden, decoys, spoof, seen, touches, first))
	var hl: Array = column((first[0] as Vector2i).x) if first[0] != NONE else raid["own3"]
	beams.append(_scan(leg, st.status, "hunter", hl, hidden, decoys, spoof, seen, touches, first))
	return {"touches": touches, "first": first[0], "beams": beams}


## sweep_l3.resolve: one raid. Decoys, the ghost and a used spoof leave the kit; decoys cost no Schematics. Returns
## {state (after the raid, before the between-raid step), touches, beams, first, run_heat (the Heat the sweep ran at)}.
static func resolve(leg: Dictionary, raid_i: int, st: L3State, b2: Array, alloc: Dictionary, spoof: Vector2i = NONE) -> Dictionary:
	var heat: int = st.heat + L3Config.GHOST_HEAT * (alloc["ghost"] as Array).size()
	var sw := sweep(leg, raid_i, st, b2, alloc, spoof, heat)
	var out := st.copy()
	for t: Dictionary in sw["touches"]:
		if t["kind"] == "asset":
			out.status[t["cell"]] = "DOWN" if out.status[t["cell"]] == "OK" else "TAKEN"
		elif t["kind"] == "home":
			out.home_hp -= 1
	var run_heat := heat
	if (sw["touches"] as Array).is_empty():
		heat -= L3Config.EVADE_HEAT
	out.heat = heat
	out.home_hp = maxi(0, out.home_hp)
	out.kit["ghost"] = int(st.kit["ghost"]) - (alloc["ghost"] as Array).size()
	out.kit["decoy"] = int(st.kit["decoy"]) - (alloc["decoys"] as Array).size()
	out.kit["spoof"] = int(st.kit["spoof"]) - (1 if spoof != NONE else 0)
	return {"state": out, "touches": sw["touches"], "beams": sw["beams"], "first": sw["first"], "run_heat": run_heat}


## The outcome tier of a raid: BREACHED (HOME at 0), DAMAGED (HOME lost integrity), EVADED (nothing touched), else HOLDS.
static func tier(before_hp: int, after_hp: int, touch_count: int) -> String:
	if after_hp <= 0:
		return "BREACHED"
	if after_hp < before_hp:
		return "DAMAGED"
	return "HOLDS" if touch_count > 0 else "EVADED"


## Income of the interval: sum(v // 3) over OK, not-dark assets, times the intensity multiplier, rounded down.
static func income_of(leg: Dictionary, status: Dictionary, dark: Array, intensity: String) -> int:
	var vals: Dictionary = leg["values"]
	var sum := 0
	for c: Vector2i in status:
		if status[c] == "OK" and not dark.has(c):
			sum += idiv(int(vals[c]), L3Config.INCOME_DIV)
	return idiv(sum * int(L3Config.INTENSITY_NUM[intensity]), L3Config.INTENSITY_DEN)


## sweep_l3.between: repairs (in the given order, each DOWN asset the bank can pay v // 2), then one shop buy (`buy` is
## "" or "ghost" / "decoy" / "spoof", bought if the bank can pay), then income and the run's Heat. `dark` assets earn
## nothing this interval.
static func between(leg: Dictionary, st: L3State, dark: Array, repairs: Array, intensity: String, buy: String) -> L3State:
	return between_parts(leg, st, dark, repairs, intensity, buy)["state"]


## The pieces of the between step, for the ledger: repairs actually paid, the buy, income, and the state.
## {repaired, repair_cost, bought (kit name or ""), buy_cost, income, heat_add, state}.
static func between_parts(leg: Dictionary, st: L3State, dark: Array, repairs: Array, intensity: String, buy: String) -> Dictionary:
	var out := st.copy()
	var vals: Dictionary = leg["values"]
	var paid := 0
	var done: Array = []
	for c: Vector2i in repairs:
		if out.status.get(c, "") == "DOWN" and out.bank >= idiv(int(vals[c]), L3Config.REPAIR_DIV):
			var cost := idiv(int(vals[c]), L3Config.REPAIR_DIV)
			out.bank -= cost
			paid += cost
			out.status[c] = "OK"
			done.append(c)
	var bought := ""
	var buy_cost := 0
	if buy != "" and out.bank >= int(L3Config.PRICES[buy]):
		buy_cost = int(L3Config.PRICES[buy])
		out.bank -= buy_cost
		out.kit[buy] = int(out.kit[buy]) + 1
		bought = buy
	var income := income_of(leg, out.status, dark, intensity)
	out.bank += income
	var dh: int = int(L3Config.INTENSITY_HEAT[intensity])
	out.heat = st.heat + dh
	return {"repaired": done, "repair_cost": paid, "bought": bought, "buy_cost": buy_cost, "income": income,
		"heat_add": dh, "state": out}


## sweep_l3.score: bank + the values of assets not TAKEN (a DOWN one less its repair) - HOME_LOSS_COST per integrity
## lost - HEAT_CARRY per Heat point above the start; a breach is -BREACH.
static func score(leg: Dictionary, st: L3State) -> int:
	if st.home_hp <= 0:
		return -L3Config.BREACH
	var vals: Dictionary = leg["values"]
	var s: int = st.bank
	for c: Vector2i in st.status:
		if st.status[c] != "TAKEN":
			s += int(vals[c])
			if st.status[c] == "DOWN":
				s -= idiv(int(vals[c]), L3Config.REPAIR_DIV)
	s -= L3Config.HOME_LOSS_COST * (L3Config.HOME_HP - st.home_hp)
	return s - L3Config.HEAT_CARRY * maxi(0, st.heat - L3Config.START_HEAT)


## Value of the assets still held (a DOWN one less its repair), for the score formula on the record.
static func assets_kept(leg: Dictionary, st: L3State) -> int:
	var vals: Dictionary = leg["values"]
	var s := 0
	for c: Vector2i in st.status:
		if st.status[c] != "TAKEN":
			s += int(vals[c])
			if st.status[c] == "DOWN":
				s -= idiv(int(vals[c]), L3Config.REPAIR_DIV)
	return s


## Heat points the leg score charges (Heat carried into the campaign's later raids).
static func heat_carried(st: L3State) -> int:
	return L3Config.HEAT_CARRY * maxi(0, st.heat - L3Config.START_HEAT)


## The spoof options for one sealed line (the held spoof is a choice after the reveal; skipping a node of the lit
## line). Returns {hold: resolve result, options: [{cell, res, saves}], floor: the best (score, fewest touches) result
## over hold and every skip, with ties keeping hold}. `saves` = that skip beats holding: it avoids the breach or
## scores strictly higher (a skip that only drops a decoy touch is no save). It never names a best spoof; callers show
## the set and the range, the player picks.
static func spoof_options(leg: Dictionary, raid_i: int, st: L3State, b2: Array, alloc: Dictionary) -> Dictionary:
	var hold := resolve(leg, raid_i, st, b2, alloc, NONE)
	var hk := _key(leg, hold)
	var opts: Array = []
	var floor_res: Dictionary = hold
	var floor_key: Array = hk
	for c: Vector2i in b2:
		var res := resolve(leg, raid_i, st, b2, alloc, c)
		var k := _key(leg, res)
		var saves := _better(k, hk, hold, res)
		opts.append({"cell": c, "res": res, "saves": saves})
		if k[0] > floor_key[0] or (k[0] == floor_key[0] and k[1] > floor_key[1]):
			floor_res = res
			floor_key = k
	return {"hold": hold, "options": opts, "floor": floor_res}


static func _key(leg: Dictionary, res: Dictionary) -> Array:
	return [score(leg, res["state"]), -(res["touches"] as Array).size()]


static func _better(k: Array, hk: Array, hold: Dictionary, res: Dictionary) -> bool:
	var hb: bool = (hold["state"] as L3State).home_hp <= 0
	var rb: bool = (res["state"] as L3State).home_hp <= 0
	if hb and rb:
		return false
	return k[0] > hk[0]


## What each touch does to the network, in touch order: [{cell, kind, outcome}]; outcome is "DOWN", "TAKEN", "HOME"
## or "DECOY". `st` is the state the raid starts from (statuses before the sweep).
static func outcomes(st: L3State, touches: Array) -> Array:
	var out: Array = []
	for t: Dictionary in touches:
		var o := ""
		match t["kind"]:
			"asset":
				o = "DOWN" if st.status[t["cell"]] == "OK" else "TAKEN"
			"home":
				o = "HOME"
			_:
				o = "DECOY"
		out.append({"cell": t["cell"], "kind": t["kind"], "outcome": o})
	return out


## Counts of the distinct outcomes: {down, taken, home, decoy (bool), touched (any touch), breach (HOME reaches 0)}.
static func summary(st: L3State, touches: Array) -> Dictionary:
	var d := 0
	var t := 0
	var h := 0
	var dc := false
	for o: Dictionary in outcomes(st, touches):
		match o["outcome"]:
			"DOWN":
				d += 1
			"TAKEN":
				t += 1
			"HOME":
				h += 1
			_:
				dc = true
	return {"down": d, "taken": t, "home": h, "decoy": dc, "touched": not touches.is_empty(),
		"breach": h > 0 and st.home_hp - h <= 0}


## "" if the lever may go on the cell, else the reason (the kit and the per-raid caps of sweep_l3.allocations).
static func why_not(leg: Dictionary, st: L3State, alloc: Dictionary, lever: String, c: Vector2i) -> String:
	if not (c.x >= 0 and c.x < L3Config.W and c.y >= 0 and c.y < L3Config.H):
		return "off the grid"
	if (alloc["ghost"] as Array).has(c) or (alloc["dark"] as Array).has(c) or (alloc["decoys"] as Array).has(c):
		return "that node already has a lever"
	var is_asset: bool = st.status.has(c)
	var live: bool = is_asset and st.status[c] != "TAKEN"
	match lever:
		"ghost":
			if not (live or c == leg["home"]):
				return "a ghost hides a live asset or HOME"
			if int(st.kit["ghost"]) <= 0:
				return "no ghost left in the kit"
			if (alloc["ghost"] as Array).size() >= L3Config.MAX_GHOST:
				return "only %d ghost per raid" % L3Config.MAX_GHOST
		"decoy":
			if is_asset or c == leg["home"]:
				return "a decoy goes on an empty node"
			if (alloc["decoys"] as Array).size() >= int(st.kit["decoy"]):
				return "no decoy left in the kit"
			if (alloc["decoys"] as Array).size() >= L3Config.MAX_DECOY:
				return "only %d decoys per raid" % L3Config.MAX_DECOY
		"dark":
			if not live:
				return "go dark on a live asset"
			if (alloc["dark"] as Array).size() >= L3Config.MAX_DARK:
				return "at most %d dark per raid" % L3Config.MAX_DARK
	return ""


## The naive policy of sweep_l3.naive_leg for raid i: ghost the biggest live asset while the kit lasts, no decoy, no
## dark, spoof the first live, un-ghosted asset on the revealed line while the kit lasts. Returns {alloc, spoof}.
static func naive_decide(leg: Dictionary, raid_i: int, st: L3State) -> Dictionary:
	var vals: Dictionary = leg["values"]
	var live: Array = []
	for c: Vector2i in st.status:
		if st.status[c] != "TAKEN":
			live.append(c)
	live.sort_custom(func(a: Vector2i, b: Vector2i) -> bool:
		if vals[a] != vals[b]:
			return vals[a] > vals[b]
		return a.x < b.x or (a.x == b.x and a.y < b.y))
	var ghost: Array = [live[0]] if (not live.is_empty() and int(st.kit["ghost"]) > 0) else []
	var alloc := {"ghost": ghost, "dark": [], "decoys": []}
	var b2: Array = leg["raids"][raid_i]["cands"][L3Config.REVEAL]
	var sp := NONE
	if int(st.kit["spoof"]) > 0:
		for c: Vector2i in b2:
			if vals.has(c) and st.status.get(c, "") != "TAKEN" and not ghost.has(c):
				sp = c
				break
	return {"alloc": alloc, "spoof": sp}


## The naive repairs after a raid: every DOWN asset, biggest first (the bank decides how many are paid).
static func naive_repairs(leg: Dictionary, st: L3State) -> Array:
	var vals: Dictionary = leg["values"]
	var down: Array = []
	for c: Vector2i in st.status:
		if st.status[c] == "DOWN":
			down.append(c)
	down.sort_custom(func(a: Vector2i, b: Vector2i) -> bool:
		if vals[a] != vals[b]:
			return vals[a] > vals[b]
		return a.x < b.x or (a.x == b.x and a.y < b.y))
	return down
