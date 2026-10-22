class_name M10Rules
extends RefCounted
## The M10 sweep rules, ported from tools/raid_concepts/ghost2.py (sweep, value, allocations) with the scarce levers
## (one ghost, one decoy). Pure and deterministic: no randomness, no nodes. Cells are Vector2i (x, y), x 0..3, y 0..2.
## `assets` maps cell -> value. A plan is {"ghost": Array, "dark": Array, "decoys": Array} of cells.
## A spoof is [beam_index 0..2, cell] or [] for none.


## All 12 cells in python NODES order (row by row).
static func nodes() -> Array:
	var out: Array = []
	for y in range(M10Config.H):
		for x in range(M10Config.W):
			out.append(Vector2i(x, y))
	return out


static func empty_plan() -> Dictionary:
	return {"ghost": [], "dark": [], "decoys": []}


## The column a hunter beam scans, top to bottom.
static func column(x: int) -> Array:
	var out: Array = []
	for y in range(M10Config.H):
		out.append(Vector2i(x, y))
	return out


static func hidden_of(plan: Dictionary) -> Array:
	return (plan["ghost"] as Array) + (plan["dark"] as Array)


## Full sweep with a per-beam trace. Returns {found, first, beams}. `first` is Vector2i(-1, -1) when nothing was
## found and no decoy was hit. Each beam entry: {line (the cells it scans), steps: [{cell, kind}], stopped: bool}.
## Step kinds: "spoofed" (skipped by the spoof), "decoy" (beam stops here), "found" (new find), "dup" (an asset
## already found, nothing new), "near" (a hidden asset: ghost or dark, passed), "empty".
## Beam 3 (the hunter) scans the column of the first thing found by beams 1 and 2 (a decoy counts), else `own3`.
static func sweep(assets: Dictionary, b1: Array, b2: Array, own3: Array, plan: Dictionary, spoof: Array = []) -> Dictionary:
	var hidden: Array = hidden_of(plan)
	var decoys: Array = plan["decoys"]
	var found: Array = []
	var first := Vector2i(-1, -1)
	var beams: Array = []
	var lines: Array = [b1, b2, own3]
	for k in range(3):
		var line: Array = lines[k]
		if k == 2 and first.x >= 0:
			line = column(first.x)
		var steps: Array = []
		var stopped := false
		for c in line:
			if not spoof.is_empty() and int(spoof[0]) == k and spoof[1] == c:
				steps.append({"cell": c, "kind": "spoofed"})
				continue
			if decoys.has(c):
				if first.x < 0:
					first = c
				steps.append({"cell": c, "kind": "decoy"})
				stopped = true
				break
			if assets.has(c):
				if hidden.has(c):
					steps.append({"cell": c, "kind": "near"})
				elif found.has(c):
					steps.append({"cell": c, "kind": "dup"})
				else:
					found.append(c)
					if first.x < 0:
						first = c
					steps.append({"cell": c, "kind": "found"})
			else:
				steps.append({"cell": c, "kind": "empty"})
		beams.append({"line": line, "steps": steps, "stopped": stopped})
	return {"found": found, "first": first, "beams": beams}


## Just the found list (ghost2.sweep).
static func found_of(assets: Dictionary, b1: Array, b2: Array, own3: Array, plan: Dictionary, spoof: Array = []) -> Array:
	return sweep(assets, b1, b2, own3, plan, spoof)["found"]


## The income a dark node forfeits: v // 2 + 1.
static func dark_cost(v: int) -> int:
	return floori(v / 2.0) + 1


## ghost2.value(): -found values - decoy cost - dark costs + EVADE if nothing found - Heat valued per ghost.
static func value(assets: Dictionary, found: Array, plan: Dictionary) -> float:
	var v: float = 0.0
	for c in found:
		v -= assets[c]
	v -= M10Config.DECOY_COST * (plan["decoys"] as Array).size()
	for c in plan["dark"]:
		v -= dark_cost(int(assets[c]))
	if found.is_empty():
		v += M10Config.EVADE
	v -= M10Config.HEAT_VALUE * M10Config.GHOST_HEAT * (plan["ghost"] as Array).size()
	return v


## Sum of the values of the found assets.
static func found_value(assets: Dictionary, found: Array) -> int:
	var s := 0
	for c in found:
		s += int(assets[c])
	return s


## Repair cost of the found assets: the value ("value") or half of it per asset, rounded down ("half").
static func repair(assets: Dictionary, found: Array, mode: String = "") -> int:
	var m: String = mode if mode != "" else M10Config.repair_mode()
	var s := 0
	for c in found:
		s += int(assets[c]) if m == "value" else floori(int(assets[c]) / 2.0)
	return s


## Forecast of one sealed candidate under a plan, with the held spoof unused: the found list and the repair.
static func forecast(assets: Dictionary, b1: Array, cand: Array, own3: Array, plan: Dictionary) -> Dictionary:
	var f: Array = found_of(assets, b1, cand, own3, plan)
	return {"found": f, "repair": repair(assets, f)}


## The key-bar loss range over the candidates: [min, max] repair.
static func loss_range(assets: Dictionary, b1: Array, cands: Array, own3: Array, plan: Dictionary) -> Array:
	var lo := 1 << 30
	var hi := -1
	for c in cands:
		var r: int = forecast(assets, b1, c, own3, plan)["repair"]
		lo = mini(lo, r)
		hi = maxi(hi, r)
	return [lo, hi]


## Heat the plan has already charged (ghosts, immediately).
static func plan_heat(plan: Dictionary) -> int:
	return M10Config.GHOST_HEAT * (plan["ghost"] as Array).size()


## Key the plan has already charged (decoys, immediately).
static func plan_key_cost(plan: Dictionary) -> int:
	return M10Config.DECOY_COST * (plan["decoys"] as Array).size()


## Income the dark nodes forfeit on the next run.
static func plan_dark_loss(assets: Dictionary, plan: Dictionary) -> int:
	var s := 0
	for c in plan["dark"]:
		s += dark_cost(int(assets[c]))
	return s


## The raid ledger in one currency (the key) plus Heat. `found` is the real result. The key cannot go below 0 or above
## KEY_MAX, so unpayable repair appears as a "short" row and overflow as a "cap" row; the rows always reconcile.
static func ledger(assets: Dictionary, plan: Dictionary, found: Array, key_before: int, heat_before: int) -> Dictionary:
	var decoy: int = plan_key_cost(plan)
	var rep: int = repair(assets, found)
	var evaded: bool = found.is_empty()
	var gain: int = M10Config.EVADE if evaded else 0
	var raw: int = key_before - decoy - rep + gain
	var key_after: int = clampi(raw, 0, M10Config.KEY_MAX)
	var heat_ghost: int = plan_heat(plan)
	var heat_evade: int = -M10Config.EVADE_HEAT if evaded else 0
	var heat_raw: int = heat_before + heat_ghost + heat_evade
	var heat_after: int = clampi(heat_raw, 0, M10Config.HEAT_MAX)
	return {"key_before": key_before, "decoy": decoy, "repair": rep, "evade_gain": gain,
		"short": key_after - raw if raw < 0 else 0, "cap": key_after - raw if raw > M10Config.KEY_MAX else 0,
		"key_after": key_after, "heat_before": heat_before, "heat_ghost": heat_ghost, "heat_evade": heat_evade,
		"heat_adjust": heat_after - heat_raw, "heat_after": heat_after,
		"dark_loss": plan_dark_loss(assets, plan), "evaded": evaded, "down": found.size()}


## Rows of the key ledger that sum from key_before to key_after: [[id, signed amount], ...].
static func ledger_rows(l: Dictionary) -> Array:
	var rows: Array = []
	rows.append(["decoy", -int(l["decoy"])])
	rows.append(["repair", -int(l["repair"])])
	if int(l["evade_gain"]) > 0:
		rows.append(["evade", int(l["evade_gain"])])
	if int(l["short"]) > 0:
		rows.append(["short", int(l["short"])])
	if int(l["cap"]) < 0:
		rows.append(["cap", int(l["cap"])])
	return rows


## True when key_before + the rows == key_after and Heat before + its rows == Heat after.
static func ledger_reconciles(l: Dictionary) -> bool:
	var s: int = int(l["key_before"])
	for r in ledger_rows(l):
		s += int(r[1])
	var h: int = int(l["heat_before"]) + int(l["heat_ghost"]) + int(l["heat_evade"]) + int(l["heat_adjust"])
	return s == int(l["key_after"]) and h == int(l["heat_after"])
