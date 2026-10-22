class_name L2Rules
extends RefCounted
## The round-2 (L2) sweep rules, ported from tools/raid_concepts/sweep_l2.py (sweep, resolve, between, score, the
## lever caps of `allocations`, the naive policy). Pure and deterministic: no randomness, no nodes.
## Cells are Vector2i (x 0..3, y 0..2). A leg is the dictionary of L2Data.load_leg. An alloc is
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
	for y in range(L2Config.H):
		for x in range(L2Config.W):
			out.append(Vector2i(x, y))
	return out


## The column a hunter beam scans, top to bottom.
static func column(x: int) -> Array:
	var out: Array = []
	for y in range(L2Config.H):
		out.append(Vector2i(x, y))
	return out


static func empty_alloc() -> Dictionary:
	return {"ghost": [], "dark": [], "decoys": []}


static func copy_alloc(a: Dictionary) -> Dictionary:
	return {"ghost": (a["ghost"] as Array).duplicate(), "dark": (a["dark"] as Array).duplicate(),
		"decoys": (a["decoys"] as Array).duplicate()}


## How many extra known beams Heat brings: 0 below EXTRA_AT, 1 from EXTRA_AT, 2 from STRONG_AT.
static func extra_count(heat: int) -> int:
	if heat >= L2Config.STRONG_AT:
		return 2
	if heat >= L2Config.EXTRA_AT:
		return 1
	return 0


static func initial(leg: Dictionary) -> L2State:
	var s := L2State.new()
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
static func sweep(leg: Dictionary, raid_i: int, st: L2State, b2: Array, alloc: Dictionary, spoof: Vector2i, heat: int) -> Dictionary:
	var raid: Dictionary = leg["raids"][raid_i]
	var hidden: Array = (alloc["ghost"] as Array) + (alloc["dark"] as Array)
	var decoys: Array = alloc["decoys"]
	var touches: Array = []
	var first: Array = [NONE]
	var seen: Array = []
	var beams: Array = []
	beams.append(_scan(leg, st.status, "b1", raid["b1"], hidden, decoys, spoof, seen, touches, first))
	if heat >= L2Config.EXTRA_AT:
		beams.append(_scan(leg, st.status, "extra", raid["extra"], hidden, decoys, spoof, seen, touches, first))
	if heat >= L2Config.STRONG_AT:
		beams.append(_scan(leg, st.status, "extra2", raid["extra2"], hidden, decoys, spoof, seen, touches, first))
	beams.append(_scan(leg, st.status, "b2", b2, hidden, decoys, spoof, seen, touches, first))
	var hl: Array = column((first[0] as Vector2i).x) if first[0] != NONE else raid["own3"]
	beams.append(_scan(leg, st.status, "hunter", hl, hidden, decoys, spoof, seen, touches, first))
	return {"touches": touches, "first": first[0], "beams": beams}


## sweep_l2.resolve: one raid. Returns {state (after the raid, before the between-raid step), touches, beams, first,
## run_heat (the Heat the sweep ran at)}.
static func resolve(leg: Dictionary, raid_i: int, st: L2State, b2: Array, alloc: Dictionary, spoof: Vector2i = NONE) -> Dictionary:
	var heat: int = st.heat + L2Config.GHOST_HEAT * (alloc["ghost"] as Array).size()
	var bank: int = st.bank - L2Config.DECOY_COST * (alloc["decoys"] as Array).size()
	var sw := sweep(leg, raid_i, st, b2, alloc, spoof, heat)
	var out := st.copy()
	out.bank = bank
	for t: Dictionary in sw["touches"]:
		if t["kind"] == "asset":
			out.status[t["cell"]] = "DOWN" if out.status[t["cell"]] == "OK" else "TAKEN"
		elif t["kind"] == "home":
			out.home_hp -= 1
	var run_heat := heat
	if (sw["touches"] as Array).is_empty():
		heat -= L2Config.EVADE_HEAT
	out.heat = heat
	out.home_hp = maxi(0, out.home_hp)
	return {"state": out, "touches": sw["touches"], "beams": sw["beams"], "first": sw["first"], "run_heat": run_heat}


## sweep_l2.between: repairs (in the given order, each DOWN asset the bank can pay v // 2), then income and the run's
## Heat. `dark` assets earn nothing this interval.
static func between(leg: Dictionary, st: L2State, dark: Array, repairs: Array) -> L2State:
	var out := st.copy()
	var vals: Dictionary = leg["values"]
	for c: Vector2i in repairs:
		if out.status.get(c, "") == "DOWN" and out.bank >= idiv(int(vals[c]), L2Config.REPAIR_DIV):
			out.bank -= idiv(int(vals[c]), L2Config.REPAIR_DIV)
			out.status[c] = "OK"
	var income := 0
	for c: Vector2i in out.status:
		if out.status[c] == "OK" and not dark.has(c):
			income += idiv(int(vals[c]), L2Config.INCOME_DIV)
	out.heat = st.heat + L2Config.RUN_HEAT
	out.bank += income
	return out


## The pieces of the between step, for the ledger: repairs actually paid, income, and the state.
static func between_parts(leg: Dictionary, st: L2State, dark: Array, repairs: Array) -> Dictionary:
	var vals: Dictionary = leg["values"]
	var paid := 0
	var done: Array = []
	var tmp := st.copy()
	for c: Vector2i in repairs:
		if tmp.status.get(c, "") == "DOWN" and tmp.bank >= idiv(int(vals[c]), L2Config.REPAIR_DIV):
			tmp.bank -= idiv(int(vals[c]), L2Config.REPAIR_DIV)
			paid += idiv(int(vals[c]), L2Config.REPAIR_DIV)
			tmp.status[c] = "OK"
			done.append(c)
	var after := between(leg, st, dark, repairs)
	return {"repaired": done, "repair_cost": paid, "income": after.bank - st.bank + paid, "state": after}


## sweep_l2.score: bank + the values of assets not TAKEN (a DOWN one less its repair) - HOME_LOSS_COST per integrity
## lost; a breach is -BREACH.
static func score(leg: Dictionary, st: L2State) -> int:
	if st.home_hp <= 0:
		return -L2Config.BREACH
	var vals: Dictionary = leg["values"]
	var s: int = st.bank
	for c: Vector2i in st.status:
		if st.status[c] != "TAKEN":
			s += int(vals[c])
			if st.status[c] == "DOWN":
				s -= idiv(int(vals[c]), L2Config.REPAIR_DIV)
	return s - L2Config.HOME_LOSS_COST * (L2Config.HOME_HP - st.home_hp)


## The player's best spoof for one sealed line (sweep_l2.raid_options): the cell on b2 (or NONE) with the highest
## (score, -touches). A strict improvement is needed to leave NONE. Returns {spoof, res, score}.
static func best_spoof(leg: Dictionary, raid_i: int, st: L2State, b2: Array, alloc: Dictionary) -> Dictionary:
	var best: Dictionary = {}
	var best_key: Array = []
	for sp: Vector2i in [NONE] + b2:
		var res := resolve(leg, raid_i, st, b2, alloc, sp)
		var key: Array = [score(leg, res["state"]), -(res["touches"] as Array).size()]
		if best.is_empty() or key[0] > best_key[0] or (key[0] == best_key[0] and key[1] > best_key[1]):
			best = {"spoof": sp, "res": res, "score": key[0]}
			best_key = key
	return best


## What each touch does to the network, in touch order: [{cell, kind, outcome}]; outcome is "DOWN", "TAKEN", "HOME"
## or "DECOY". `st` is the state the raid starts from (statuses before the sweep).
static func outcomes(st: L2State, touches: Array) -> Array:
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


## Counts of the distinct outcomes: {down, taken, home, decoy (bool), touched (any touch)}.
static func summary(st: L2State, touches: Array) -> Dictionary:
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
	return {"down": d, "taken": t, "home": h, "decoy": dc, "touched": not touches.is_empty()}


## "" if the lever may go on the cell, else the reason (the caps and targets of sweep_l2.allocations).
static func why_not(leg: Dictionary, st: L2State, alloc: Dictionary, lever: String, c: Vector2i) -> String:
	if not (c.x >= 0 and c.x < L2Config.W and c.y >= 0 and c.y < L2Config.H):
		return "off the grid"
	if (alloc["ghost"] as Array).has(c) or (alloc["dark"] as Array).has(c) or (alloc["decoys"] as Array).has(c):
		return "that node already has a lever"
	var is_asset: bool = st.status.has(c)
	var live: bool = is_asset and st.status[c] != "TAKEN"
	match lever:
		"ghost":
			if not (live or c == leg["home"]):
				return "a ghost hides a live asset or HOME"
			if (alloc["ghost"] as Array).size() >= L2Config.MAX_GHOST:
				return "only %d ghost" % L2Config.MAX_GHOST
		"decoy":
			if is_asset or c == leg["home"]:
				return "a decoy goes on an empty node"
			if (alloc["decoys"] as Array).size() >= L2Config.MAX_DECOY:
				return "only %d decoy" % L2Config.MAX_DECOY
			if L2Config.DECOY_COST * ((alloc["decoys"] as Array).size() + 1) > st.bank:
				return "not enough Schematics for a decoy"
		"dark":
			if not live:
				return "go dark on a live asset"
			if (alloc["dark"] as Array).size() >= L2Config.MAX_DARK:
				return "at most %d dark" % L2Config.MAX_DARK
	return ""


## The naive policy of sweep_l2.naive_leg for raid i: ghost the biggest live asset, no decoy, no dark, spoof the first
## live, un-ghosted asset on the revealed line. Returns {alloc, spoof}.
static func naive_decide(leg: Dictionary, raid_i: int, st: L2State) -> Dictionary:
	var vals: Dictionary = leg["values"]
	var live: Array = []
	for c: Vector2i in st.status:
		if st.status[c] != "TAKEN":
			live.append(c)
	live.sort_custom(func(a: Vector2i, b: Vector2i) -> bool:
		if vals[a] != vals[b]:
			return vals[a] > vals[b]
		return a.x < b.x or (a.x == b.x and a.y < b.y))
	var ghost: Array = [live[0]] if not live.is_empty() else []
	var alloc := {"ghost": ghost, "dark": [], "decoys": []}
	var b2: Array = leg["raids"][raid_i]["cands"][L2Config.REVEAL]
	var sp := NONE
	for c: Vector2i in b2:
		if vals.has(c) and st.status.get(c, "") != "TAKEN" and not ghost.has(c):
			sp = c
			break
	return {"alloc": alloc, "spoof": sp}


## The naive repairs after a raid: every DOWN asset, biggest first (the bank decides how many are paid).
static func naive_repairs(leg: Dictionary, st: L2State) -> Array:
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
