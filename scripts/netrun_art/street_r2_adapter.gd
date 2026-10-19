class_name StreetR2Adapter
extends RefCounted
## Adapter (twin of `tools/netrun_art/r2/adapter.py`): the street derive (`NetrunStreetDeriver.derive_street`: rooms, columns, frontage bids,
## poses) and the game city -> the input of the street r2 rules, so a Godot street gets a plate-style facade / sign plan, deterministic per
## building bid and art seed (every stream is keyed by the bid, `StreetR2Rng`). The game applies its own layout rules (silhouette, horizon)
## before the derive, so only the dressing plan runs; the horizon spikes the plan needs are picked with the r2 selection over the heights
## the city already has.


## The u64 bits of a layout seed given as an int or its decimal string.
static func seed_of(layout_seed: Variant) -> int:
	if layout_seed is String:
		return ArtSeed.u64_from_str(layout_seed)
	return int(layout_seed)


## The r2 street derivation of a street derive `d`: leg ends, side, route column uids, room fronts, OVERVIEW / DECISION cameras.
static func street_derivation(d: Dictionary) -> Dictionary:
	var a: Array = (d["street"]["a"] as Array).duplicate()
	var c: Array = (d["street"]["c"] as Array).duplicate()
	var nrm: Array = (d["nrm"] as Array).duplicate()
	var ax := 0 if absf(float(a[1]) - float(c[1])) < 1e-6 else 1
	var dirn := 1 if float(c[ax]) > float(a[ax]) else -1
	var side := StreetR2Util.py_round0(float(nrm[1]) * dirn) if ax == 0 else StreetR2Util.py_round0(-float(nrm[0]) * dirn)
	var cols: Array = []
	for lb: Array in d["columns"]:
		cols.append(lb[1])
	var rooms := {}
	for rid: String in d["rooms"]:
		var r: Dictionary = d["rooms"][rid]
		var fr: Array = []
		for p: Array in r["front"]:
			fr.append(p.duplicate())
		rooms[rid] = {"front": fr, "bld_uid": r["bld"], "floor": r["floor"], "span": r["span"]}
	return {"a": a, "c": c, "nrm": nrm, "side": side, "column_uids": cols.duplicate(), "route_uids": cols.duplicate(), "rooms": rooms,
		"overview": camera(d["overview"]), "decision": camera(d["decision"])}


## The r2 camera dict of a v2 pose. The rig yaw is 0 = +y, clockwise; the r2 (layout36) yaw is 0 = +x, counter-clockwise: `90 - yaw`.
static func camera(pose: Dictionary) -> Dictionary:
	return {"yaw": 90.0 - float(pose["yaw"]), "pitch": pose["pitch"],
		"persp": {"loc": (pose["loc"] as Array).duplicate(), "lens": pose["lens"], "sx": pose["shift_x"], "sy": pose["shift_y"]}}


## BU records of the street-level buildings (merged with their stacked parts), in `bid` text order; `uid` is the bid.
static func buildings(city: Dictionary) -> Array:
	var byid := {}
	for b: Dictionary in city["buildings"]:
		byid[b["bid"]] = b
	var out: Array = []
	for bi: Dictionary in NetrunArtLayout.merged_buildings(city):
		var base: Dictionary = byid[bi["bid"]]["parts"][bi["base"]]
		var q: Array = []
		for p: Array in base["poly"]:
			q.append(p.duplicate())
		out.append({"key": bi["key"], "uid": bi["bid"], "q": q, "x0": bi["x0"], "x1": bi["x1"], "y0": bi["y0"], "y1": bi["y1"], "z0": bi["z0"],
			"h": bi["h"], "ts": bi["ts"], "top": bi["h"], "parts": [bi["key"]], "parts_uid": [bi["bid"]]})
	return out


## `{seed, D, merged, terr, layout_log}`: the arguments of `StreetR2Rules.plan_pass` for the street `d` of `city`.
static func r2_input(city: Dictionary, d: Dictionary, seed: Variant) -> Dictionary:
	var D := street_derivation(d)
	var merged := buildings(city)
	var terr := {}
	for b: Dictionary in city["buildings"]:
		terr[b["bid"]] = b.get("terr", "")
	var s := seed_of(seed)
	var route := {}
	for u: String in D["column_uids"]:
		route[u] = true
	var hp := StreetR2Rules.horizon_pick(s, merged, D, route)
	var spikes: Array = []
	for c: Array in hp["pick"]:
		spikes.append({"key": c[3]["uid"], "z": StreetR2Util.py_round(float(c[0]), 1), "sx": StreetR2Util.py_round(float(c[1]), 3), "far": StreetR2Util.py_round(float(c[2]), 1)})
	return {"seed": s, "D": D, "merged": merged, "terr": terr, "layout_log": {"spikes": spikes}}


## The r2 dressing plan of the derived street `d` on `city`, deterministic per bid and art seed.
static func plan_street(city: Dictionary, d: Dictionary, seed: Variant) -> Dictionary:
	var x := r2_input(city, d, seed)
	return StreetR2Rules.plan_pass(x["seed"], x["D"], x["merged"], x["terr"], x["layout_log"])
