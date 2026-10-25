class_name L5Rules
extends RefCounted
## The round-5 (L5) sweep rules, ported from tools/raid_concepts/sweep_l5.py (and the sweep_l3.py / sweep_l2.py it builds on):
## sweep, resolve, between, score, tier, the lever caps of `allocations`, the naive policy. Pure and deterministic: no
## randomness, no nodes. Cells are Vector2i (x 0..3, y 0..2). A leg is the dictionary of L5Data.load_leg. An alloc is
## {"ghost": Array, "dark": Array, "decoys": Array} of cells. NONE means "no spoof" / "no cell".

const NONE := Vector2i(-1, -1)
## The spoof that stops the hunter for this raid (sweep_l5.JAM); any other non-NONE spoof is a SKIP of that cell on beam 2.
const JAM := Vector2i(-2, -2)
const BEAM_IDS: Array = ["b1", "extra", "extra2", "b2", "hunter"]


## Integer division (python //), values are never negative.
@warning_ignore("integer_division")
static func idiv(a: int, b: int) -> int:
	return a / b


## All 12 cells in python NODES order (row by row).
static func nodes() -> Array:
	var out: Array = []
	for y in range(L5Config.H):
		for x in range(L5Config.W):
			out.append(Vector2i(x, y))
	return out


## The column a hunter beam scans, top to bottom.
static func column(x: int) -> Array:
	var out: Array = []
	for y in range(L5Config.H):
		out.append(Vector2i(x, y))
	return out


static func empty_alloc() -> Dictionary:
	return {"ghost": [], "dark": [], "decoys": []}


static func copy_alloc(a: Dictionary) -> Dictionary:
	return {"ghost": (a["ghost"] as Array).duplicate(), "dark": (a["dark"] as Array).duplicate(),
		"decoys": (a["decoys"] as Array).duplicate()}


## How many extra known beams Heat brings: 0 below EXTRA_AT, 1 from EXTRA_AT, 2 from STRONG_AT.
static func extra_count(heat: int) -> int:
	if heat >= L5Config.STRONG_AT:
		return 2
	if heat >= L5Config.EXTRA_AT:
		return 1
	return 0


static func initial(leg: Dictionary) -> L5State:
	var s := L5State.new()
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
static func sweep(leg: Dictionary, raid_i: int, st: L5State, b2: Array, alloc: Dictionary, spoof: Vector2i, heat: int) -> Dictionary:
	var raid: Dictionary = leg["raids"][raid_i]
	var hidden: Array = (alloc["ghost"] as Array) + (alloc["dark"] as Array)
	var decoys: Array = alloc["decoys"]
	var touches: Array = []
	var first: Array = [NONE]
	var seen: Array = []
	var beams: Array = []
	beams.append(_scan(leg, st.status, "b1", raid["b1"], hidden, decoys, spoof, seen, touches, first))
	if heat >= L5Config.EXTRA_AT:
		beams.append(_scan(leg, st.status, "extra", raid["extra"], hidden, decoys, spoof, seen, touches, first))
	if heat >= L5Config.STRONG_AT:
		beams.append(_scan(leg, st.status, "extra2", raid["extra2"], hidden, decoys, spoof, seen, touches, first))
	beams.append(_scan(leg, st.status, "b2", b2, hidden, decoys, spoof, seen, touches, first))
	if spoof != JAM:
		var hl: Array = column((first[0] as Vector2i).x) if first[0] != NONE else raid["own3"]
		beams.append(_scan(leg, st.status, "hunter", hl, hidden, decoys, spoof, seen, touches, first))
	return {"touches": touches, "first": first[0], "beams": beams}


## sweep_l5.resolve: one raid. Decoys, the ghost, go dark and a used spoof leave the kit; decoys cost no Schematics. Returns
## {state (after the raid, before the between-raid step), touches, beams, first, run_heat (the Heat the sweep ran at)}.
static func resolve(leg: Dictionary, raid_i: int, st: L5State, b2: Array, alloc: Dictionary, spoof: Vector2i = NONE) -> Dictionary:
	var heat: int = st.heat + L5Config.GHOST_HEAT * (alloc["ghost"] as Array).size()
	var sw := sweep(leg, raid_i, st, b2, alloc, spoof, heat)
	var out := st.copy()
	for t: Dictionary in sw["touches"]:
		if t["kind"] == "asset":
			out.status[t["cell"]] = "DOWN" if out.status[t["cell"]] == "OK" else "TAKEN"
		elif t["kind"] == "home":
			out.home_hp -= 1
	var run_heat := heat
	if (sw["touches"] as Array).is_empty():
		heat -= L5Config.EVADE_HEAT
	if spoof != NONE:
		heat += L5Config.SPOOF_HEAT
	out.heat = heat
	out.home_hp = maxi(0, out.home_hp)
	out.kit["ghost"] = int(st.kit["ghost"]) - (alloc["ghost"] as Array).size()
	out.kit["decoy"] = int(st.kit["decoy"]) - (alloc["decoys"] as Array).size()
	out.kit["dark"] = int(st.kit["dark"]) - (alloc["dark"] as Array).size()
	out.kit["spoof"] = int(st.kit["spoof"]) - (1 if spoof != NONE else 0)
	return {"state": out, "touches": sw["touches"], "beams": sw["beams"], "first": sw["first"], "run_heat": run_heat}


## The outcome tier of a raid (sweep_l5.tier): BREACHED (HOME at 0), DAMAGED (HOME lost integrity), EVADED (nothing
## touched), BATTERED (HOME intact and 2+ assets newly DOWN, or any asset newly TAKEN), else HOLDS.
static func tier(before: L5State, after: L5State, touch_count: int) -> String:
	if after.home_hp <= 0:
		return "BREACHED"
	if after.home_hp < before.home_hp:
		return "DAMAGED"
	if touch_count == 0:
		return "EVADED"
	var new_down := 0
	var new_taken := 0
	for c: Vector2i in after.status:
		if after.status[c] == "DOWN" and before.status.get(c, "") == "OK":
			new_down += 1
		if after.status[c] == "TAKEN" and before.status.get(c, "") != "TAKEN":
			new_taken += 1
	return "BATTERED" if new_down >= 2 or new_taken >= 1 else "HOLDS"


## The corp's real sealed line (candidate index) of raid i: seeded per raid in the golden, never a tell.
static func real_cand(leg: Dictionary, raid_i: int) -> int:
	return int(leg["raids"][raid_i]["real"])


## The shape drawn for candidate k of raid i: 0 triangle, 1 square, 2 circle (shuffled per raid in the golden).
static func shape_of(leg: Dictionary, raid_i: int, k: int) -> int:
	return int(leg["raids"][raid_i]["shapes"][k])


## The candidate index that wears shape s in raid i.
static func cand_of_shape(leg: Dictionary, raid_i: int, s: int) -> int:
	return (leg["raids"][raid_i]["shapes"] as Array).find(s)


## Income of the interval: sum(v // 3) over OK, not-dark assets, times the intensity multiplier, rounded down.
static func income_of(leg: Dictionary, status: Dictionary, dark: Array, intensity: String) -> int:
	var vals: Dictionary = leg["values"]
	var sum := 0
	for c: Vector2i in status:
		if status[c] == "OK" and not dark.has(c):
			sum += idiv(int(vals[c]), L5Config.INCOME_DIV)
	return idiv(sum * int(L5Config.INTENSITY_NUM[intensity]), L5Config.INTENSITY_DEN)


## sweep_l5.between: repairs (in the given order, each DOWN asset the bank can pay v // 2), then one shop buy (`buy` is
## "" or "ghost" / "decoy" / "spoof" / "dark", bought if the bank can pay), then income and the run's Heat. `dark` assets earn
## nothing this interval.
static func between(leg: Dictionary, st: L5State, dark: Array, repairs: Array, intensity: String, buy: String) -> L5State:
	return between_parts(leg, st, dark, repairs, intensity, buy)["state"]


## The pieces of the between step, for the ledger: repairs actually paid, the buy, income, and the state.
## {repaired, repair_cost, bought (kit name or ""), buy_cost, income, heat_add, state}.
static func between_parts(leg: Dictionary, st: L5State, dark: Array, repairs: Array, intensity: String, buy: String) -> Dictionary:
	var out := st.copy()
	var vals: Dictionary = leg["values"]
	var paid := 0
	var done: Array = []
	for c: Vector2i in repairs.slice(0, L5Config.REPAIR_SLOTS):
		if out.status.get(c, "") == "DOWN" and out.bank >= idiv(int(vals[c]), L5Config.REPAIR_DIV):
			var cost := idiv(int(vals[c]), L5Config.REPAIR_DIV)
			out.bank -= cost
			paid += cost
			out.status[c] = "OK"
			done.append(c)
	var bought := ""
	var buy_cost := 0
	if buy != "" and out.bank >= int(L5Config.PRICES[buy]):
		buy_cost = int(L5Config.PRICES[buy])
		out.bank -= buy_cost
		out.kit[buy] = int(out.kit[buy]) + 1
		bought = buy
	var income := income_of(leg, out.status, dark, intensity)
	out.bank += income
	var dh: int = int(L5Config.INTENSITY_HEAT[intensity])
	out.heat = st.heat + dh
	return {"repaired": done, "repair_cost": paid, "bought": bought, "buy_cost": buy_cost, "income": income,
		"heat_add": dh, "state": out}


## sweep_l5.score: bank + the values of assets not TAKEN (a DOWN one less its repair) - HOME_LOSS_COST per integrity
## lost - HEAT_CARRY per Heat point above the start; a breach is -BREACH.
static func score(leg: Dictionary, st: L5State) -> int:
	if st.home_hp <= 0:
		return -L5Config.BREACH
	var vals: Dictionary = leg["values"]
	var s: int = st.bank
	for c: Vector2i in st.status:
		if st.status[c] != "TAKEN":
			s += int(vals[c])
			if st.status[c] == "DOWN":
				s -= idiv(int(vals[c]), L5Config.REPAIR_DIV)
	s -= L5Config.HOME_LOSS_COST * (L5Config.HOME_HP - st.home_hp)
	return s - L5Config.HEAT_CARRY * maxi(0, st.heat - L5Config.START_HEAT)


## Value of the assets still held (a DOWN one less its repair), for the score formula on the record.
static func assets_kept(leg: Dictionary, st: L5State) -> int:
	var vals: Dictionary = leg["values"]
	var s := 0
	for c: Vector2i in st.status:
		if st.status[c] != "TAKEN":
			s += int(vals[c])
			if st.status[c] == "DOWN":
				s -= idiv(int(vals[c]), L5Config.REPAIR_DIV)
	return s


## Heat points the leg score charges (Heat carried into the campaign's later raids).
static func heat_carried(st: L5State) -> int:
	return L5Config.HEAT_CARRY * maxi(0, st.heat - L5Config.START_HEAT)


## The spoof options for one sealed line (the held spoof is a choice after the reveal; skipping a node of the lit
## line). Returns {hold: resolve result, options: [{cell, res, saves}], floor: the best (score, fewest touches) result
## over hold and every skip, with ties keeping hold}. `saves` = that skip beats holding: it avoids the breach or
## scores strictly higher (a skip that only drops a decoy touch is no save). It never names a best spoof; callers show
## the set and the range, the player picks.
static func spoof_options(leg: Dictionary, raid_i: int, st: L5State, b2: Array, alloc: Dictionary) -> Dictionary:
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
	var jres := resolve(leg, raid_i, st, b2, alloc, JAM)
	var jk := _key(leg, jres)
	var jam := {"cell": JAM, "res": jres, "saves": _better(jk, hk, hold, jres)}
	if jk[0] > floor_key[0] or (jk[0] == floor_key[0] and jk[1] > floor_key[1]):
		floor_res = jres
	return {"hold": hold, "options": opts, "jam": jam, "floor": floor_res}


## sweep_l5.spoof_options: the responses after the reveal. NONE (hold) first; with a spoof in the kit also SKIP of each node of
## the revealed line, then JAM.
static func responses(st: L5State, b2: Array) -> Array:
	var out: Array = [NONE]
	if int(st.kit["spoof"]) > 0:
		out.append_array(b2)
		out.append(JAM)
	return out


## sweep_l5.allocations: every lever plan the kit and the per-raid caps allow, as alloc dictionaries (python order).
static func allocations(leg: Dictionary, st: L5State) -> Array:
	var home: Vector2i = leg["home"]
	var live: Array = []
	for c: Vector2i in nodes():
		if st.status.has(c) and st.status[c] != "TAKEN":
			live.append(c)
	var hideable: Array = live.duplicate()
	hideable.append(home)
	var empty: Array = []
	for c: Vector2i in nodes():
		if not st.status.has(c) and c != home:
			empty.append(c)
	var ghosts: Array = [[]]
	if int(st.kit["ghost"]) > 0:
		for c in hideable:
			ghosts.append([c])
	var max_nd: int = mini(L5Config.MAX_DECOY, int(st.kit["decoy"]))
	var decoy_sets: Array = [[]]
	if max_nd >= 1:
		for a in empty:
			decoy_sets.append([a])
	if max_nd >= 2:
		for i in range(empty.size()):
			for j in range(i + 1, empty.size()):
				decoy_sets.append([empty[i], empty[j]])
	var out: Array = []
	for g: Array in ghosts:
		var darks: Array = [[]]
		if int(st.kit["dark"]) > 0:
			for c in live:
				if not g.has(c):
					darks.append([c])
		for dk: Array in darks:
			for dc: Array in decoy_sets:
				out.append({"ghost": g, "dark": dk, "decoys": dc})
	return out


## True when the sweep touches HOME (a lean copy of `sweep`, enough for breach_risk).
static func _home_hit(leg: Dictionary, raid_i: int, st: L5State, b2: Array, alloc: Dictionary, spoof: Vector2i) -> bool:
	var raid: Dictionary = leg["raids"][raid_i]
	var home: Vector2i = leg["home"]
	var hidden: Array = (alloc["ghost"] as Array) + (alloc["dark"] as Array)
	var decoys: Array = alloc["decoys"]
	var heat: int = st.heat + L5Config.GHOST_HEAT * (alloc["ghost"] as Array).size()
	var lines: Array = [[raid["b1"], "b1"]]
	if heat >= L5Config.EXTRA_AT:
		lines.append([raid["extra"], "extra"])
	if heat >= L5Config.STRONG_AT:
		lines.append([raid["extra2"], "extra2"])
	lines.append([b2, "b2"])
	var first := NONE
	var seen: Array = []
	var li := 0
	while li <= lines.size():
		var line: Array
		var id := "hunter"
		if li < lines.size():
			line = lines[li][0]
			id = lines[li][1]
		elif spoof == JAM:
			break
		else:
			line = column(first.x) if first != NONE else raid["own3"]
		li += 1
		for c: Vector2i in line:
			if id == "b2" and spoof != NONE and c == spoof:
				continue
			if decoys.has(c):
				if first == NONE:
					first = c
				break
			if hidden.has(c) or seen.has(c):
				continue
			if c == home:
				return true
			elif st.status.has(c) and st.status[c] != "TAKEN":
				seen.append(c)
				if first == NONE:
					first = c
	return false


## sweep_l5.breach_risk for raid i from state st: over every allocation the kit allows, the fewest sealed lines on which every
## response (hold, each SKIP, JAM) still empties HOME. 0 = some plan avoids a breach on every line.
static func breach_risk(leg: Dictionary, raid_i: int, st: L5State) -> int:
	var raid: Dictionary = leg["raids"][raid_i]
	var best: int = L5Config.CANDIDATES
	if st.home_hp >= 2:
		return 0
	for alloc: Dictionary in allocations(leg, st):
		best = mini(best, breach_lines(leg, raid_i, st, alloc, best))
		if best == 0:
			return 0
	return best


## How many of the raid's sealed lines still breach under this one lever plan, with the best response on each (a line
## breaches when hold, every SKIP and JAM all empty HOME). `cap` stops the count early once it reaches that many.
static func breach_lines(leg: Dictionary, raid_i: int, st: L5State, alloc: Dictionary, cap: int = 3) -> int:
	var raid: Dictionary = leg["raids"][raid_i]
	var n := 0
	for b2: Array in raid["cands"]:
		var all_breach := true
		for sp: Vector2i in responses(st, b2):
			if st.home_hp >= 2 or (st.home_hp > 0 and not _home_hit(leg, raid_i, st, b2, alloc, sp)):
				all_breach = false
				break
		if all_breach:
			n += 1
			if n >= cap:
				break
	return n


static func _key(leg: Dictionary, res: Dictionary) -> Array:
	return [score(leg, res["state"]), -(res["touches"] as Array).size()]


static func _better(k: Array, hk: Array, hold: Dictionary, res: Dictionary) -> bool:
	var hb: bool = (hold["state"] as L5State).home_hp <= 0
	var rb: bool = (res["state"] as L5State).home_hp <= 0
	if hb and rb:
		return false
	return k[0] > hk[0]


## What each touch does to the network, in touch order: [{cell, kind, outcome}]; outcome is "DOWN", "TAKEN", "HOME"
## or "DECOY". `st` is the state the raid starts from (statuses before the sweep).
static func outcomes(st: L5State, touches: Array) -> Array:
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
static func summary(st: L5State, touches: Array) -> Dictionary:
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


## "" if the lever may go on the cell, else the reason (the kit and the per-raid caps of sweep_l5.allocations).
static func why_not(leg: Dictionary, st: L5State, alloc: Dictionary, lever: String, c: Vector2i) -> String:
	if not (c.x >= 0 and c.x < L5Config.W and c.y >= 0 and c.y < L5Config.H):
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
			if (alloc["ghost"] as Array).size() >= L5Config.MAX_GHOST:
				return "only %d ghost per raid" % L5Config.MAX_GHOST
		"decoy":
			if is_asset or c == leg["home"]:
				return "a decoy goes on an empty node"
			if (alloc["decoys"] as Array).size() >= int(st.kit["decoy"]):
				return "no decoy left in the kit"
			if (alloc["decoys"] as Array).size() >= L5Config.MAX_DECOY:
				return "only %d decoys per raid" % L5Config.MAX_DECOY
		"dark":
			if not live:
				return "go dark on a live asset"
			if int(st.kit["dark"]) <= 0:
				return "no go dark left in the kit"
			if (alloc["dark"] as Array).size() >= L5Config.MAX_DARK:
				return "at most %d dark per raid" % L5Config.MAX_DARK
	return ""


## The naive policy of sweep_l5.naive_leg for raid i: ghost the biggest live asset while the kit lasts, no decoy, no
## dark, spoof the first live, un-ghosted asset on the corp's real line while the kit lasts. Returns {alloc, spoof}.
static func naive_decide(leg: Dictionary, raid_i: int, st: L5State) -> Dictionary:
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
	var b2: Array = leg["raids"][raid_i]["cands"][real_cand(leg, raid_i)]
	var sp := NONE
	if int(st.kit["spoof"]) > 0:
		for c: Vector2i in b2:
			if vals.has(c) and st.status.get(c, "") != "TAKEN" and not ghost.has(c):
				sp = c
				break
	return {"alloc": alloc, "spoof": sp}


## The naive repairs after a raid: every DOWN asset, biggest first (the bank decides how many are paid).
static func naive_repairs(leg: Dictionary, st: L5State) -> Array:
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
