class_name StreetR2Rules
extends RefCounted
## Street r2 rules (twin of `tools/netrun_art/r2/rules.py`, the plate's `r2_rules.py`): the layout passes (frontage.silhouette,
## horizon.break) and the dressing plan (materials.mix, repetition.guard, crowns, trims, signs, props, lamps, plumes, stops, checks) as
## seeded passes over the one-city lots. `layout_pass` changes heights; `plan_pass` makes the plan. Every draw is keyed by content ids
## (`StreetR2Rng.stream`), so adding or removing one object never moves another. Ordering follows the Python line by line.

const GRID := 16.0
const NEAR_BASE := 0.05


static func _r(block: String) -> Dictionary:
	var c := StreetR2ConfigData.shipped()
	return c.get(block)


static func _axis_of(D: Dictionary) -> int:
	return 0 if absf(float(D["a"][1]) - float(D["c"][1])) < 1e-6 else 1


# ---------------------------------------------------------------- the one-city helpers
static func _border_legs(links: Array) -> Array:
	var sorted_links := StreetR2Util.sorted_by(links, func(x: Dictionary, y: Dictionary) -> bool:
		return StreetR2Util.tuple_less([x["a"], x["b"]], [y["a"], y["b"]]))
	var legs: Array = []
	for l: Dictionary in sorted_links:
		if l["state"] != "border":
			continue
		var pts: Array = []
		for p: Array in l["pts"]:
			pts.append(StreetR2OneCity.w_of(p))
		for k in pts.size() - 1:
			legs.append(["%s|%s|%d" % [l["a"], l["b"], k], pts[k], pts[k + 1]])
	return legs


static func _frontage_rows(bases: Array, a: Array, c: Array) -> Dictionary:
	var ax := 0 if absf(float(a[1]) - float(c[1])) < 1e-6 else 1
	var oc: Dictionary = StreetR2ConfigData.shipped().onecity
	var ext := maxf(float(oc["extend"][0]), float(oc["extend"][1]))
	var lo := minf(float(a[ax]), float(c[ax])) - ext
	var hi := maxf(float(a[ax]), float(c[ax])) + ext
	var fb: Array = oc["front_band"]
	var rows := {1: [], -1: []}
	for bi: Dictionary in bases:
		if float(bi["z0"]) > NEAR_BASE:
			continue
		var a0: float
		var a1: float
		var d0: float
		var d1: float
		if ax == 0:
			a0 = bi["x0"]
			a1 = bi["x1"]
			d0 = float(bi["y0"]) - float(a[1])
			d1 = float(a[1]) - float(bi["y1"])
		else:
			a0 = bi["y0"]
			a1 = bi["y1"]
			d0 = float(bi["x0"]) - float(a[0])
			d1 = float(a[0]) - float(bi["x1"])
		var near := d0 if d0 > 0 else d1
		if a1 > lo and a0 < hi and float(fb[0]) < near and near < float(fb[1]) and a1 - a0 >= float(oc["min_width"]):
			(rows[1 if d0 > 0 else -1] as Array).append([(a0 + a1) / 2, bi["uid"], bi])
	var out := {}
	for s: int in [1, -1]:
		var v: Array = StreetR2Util.sorted_by(rows[s], func(x: Array, y: Array) -> bool:
			return StreetR2Util.tuple_less([x[0], x[1]], [y[0], y[1]]))
		var lst: Array = []
		for e: Array in v:
			lst.append(e[2])
		out[s] = lst
	return out


## The top of the stack above each street-level building: uid -> highest z0 + h of the parts whose centre it contains.
static func _tops(bases: Array) -> Dictionary:
	var lows: Array = []
	var grid := {}
	for bi: Dictionary in bases:
		if float(bi["z0"]) <= NEAR_BASE:
			var i := lows.size()
			lows.append(bi)
			for ix in range(int(floorf(float(bi["x0"]) / GRID)), int(floorf(float(bi["x1"]) / GRID)) + 1):
				for iy in range(int(floorf(float(bi["y0"]) / GRID)), int(floorf(float(bi["y1"]) / GRID)) + 1):
					var key := Vector2i(ix, iy)
					if not grid.has(key):
						grid[key] = []
					(grid[key] as Array).append(i)
	var tops := {}
	for bi: Dictionary in bases:
		if float(bi["z0"]) > NEAR_BASE:
			var cx := (float(bi["x0"]) + float(bi["x1"])) / 2
			var cy := (float(bi["y0"]) + float(bi["y1"])) / 2
			for i: int in grid.get(Vector2i(int(floorf(cx / GRID)), int(floorf(cy / GRID))), []):
				var bb: Dictionary = lows[i]
				if float(bb["x0"]) <= cx and cx <= float(bb["x1"]) and float(bb["y0"]) <= cy and cy <= float(bb["y1"]):
					tops[bb["uid"]] = maxf(float(tops.get(bb["uid"], 0.0)), float(bi["z0"]) + float(bi["h"]))
					break
	return tops


## horizon.break selection: the backdrop towers that become spikes. Returns `{pick: [[top, sx, far, record]], med}`.
static func horizon_pick(seed: Variant, bs: Array, D: Dictionary, route: Dictionary) -> Dictionary:
	var H := _r("horizon_break")
	var ov: Dictionary = D["overview"]
	var nrm: Array = D["nrm"]
	var sa: Array = D["a"]
	var st_axis := _axis_of(D)
	var cand: Array = []
	var tops2 := _tops(bs)
	var band: Array = H["backdrop_band"]
	for bi: Dictionary in bs:
		if float(bi["z0"]) > NEAR_BASE or route.has(bi["uid"]):
			continue
		var cx := (float(bi["x0"]) + float(bi["x1"])) / 2
		var cy := (float(bi["y0"]) + float(bi["y1"])) / 2
		var far := (cy - float(sa[1])) * float(nrm[1]) if st_axis == 0 else (cx - float(sa[0])) * float(nrm[0])
		if not (float(band[0]) < far and far < float(band[1])):
			continue
		if minf(float(bi["x1"]) - float(bi["x0"]), float(bi["y1"]) - float(bi["y0"])) < float(H["spike_min_w"]):
			continue
		var sx := float(StreetR2OneCity.proj(ov, [cx, cy, 0.0])[0]) / StreetR2OneCity.frame_w()
		if not (0.04 < sx and sx < 0.96):
			continue
		cand.append([maxf(float(bi["h"]), float(tops2.get(bi["uid"], 0.0))), sx, far, bi])
	var med := 15.0
	if not cand.is_empty():
		var hs: Array = []
		for c: Array in cand:
			hs.append(c[0])
		hs = StreetR2Util.sorted_by(hs, func(x: float, y: float) -> bool: return x < y)
		med = hs[cand.size() / 2]
	var r_ := StreetR2Rng.stream(seed, "spikes", [D["route_uids"][0]])
	var n_sp := r_.randint(int(H["spikes_min"]), int(H["spikes_max"]))
	var keyed: Array = []
	for c: Array in cand:
		keyed.append([-(float(c[0]) + StreetR2Rng.stream(seed, "spike_pick", [c[3]["uid"]]).uniform(0.0, 25.0)), c[3]["uid"], c])
	keyed = StreetR2Util.sorted_by(keyed, func(x: Array, y: Array) -> bool: return StreetR2Util.tuple_less([x[0], x[1]], [y[0], y[1]]))
	var pick: Array = []
	for k: Array in keyed:
		var c: Array = k[2]
		var ok := true
		for p: Array in pick:
			if not (absf(float(c[1]) - float(p[1])) >= float(H["spike_spacing"])):
				ok = false
				break
		if ok:
			pick.append(c)
		if pick.size() >= n_sp:
			break
	return {"pick": pick, "med": med}


# ---------------------------------------------------------------- LAYOUT: frontage.silhouette + horizon.break
## The layout passes on the v3 city (raw lot records `{buildings, hqs}`), the network's links and the street derivation `D`. Returns
## `{city, log}`: a copy of the city with the new heights, and the pass log.
static func layout_pass(seed: Variant, city: Dictionary, links: Array, D: Dictionary) -> Dictionary:
	var ov: Dictionary = D["overview"]
	var LAY: Dictionary = city.duplicate(true)
	var bymap := {}
	var bases: Array = []
	for b: Dictionary in LAY["buildings"]:
		bymap["%d_%d" % [b["ci"], b["key"]]] = b
		bases.append(StreetR2OneCity.bld_info(b))
	var tops := _tops(bases)
	var fl := StreetR2OneCity.floor_bu()
	var KH := StreetR2OneCity.kh()
	var P := _r("frontage_silhouette")
	var route := {}
	for u: String in D["column_uids"]:
		route[u] = true
	var room_top := {}
	for r: Dictionary in D["rooms"].values():
		room_top[r["bld_uid"]] = maxi(int(room_top.get(r["bld_uid"], 0)), int(r["floor"]) + int(r["span"]))
	var hq := StreetR2OneCity.w_of(LAY["hqs"]["meridian"])
	var lx := float(StreetR2OneCity.proj(ov, [hq[0], hq[1], 20.0])[0]) / StreetR2OneCity.frame_w()
	var st_axis := _axis_of(D)
	var st_line := float(D["a"][1 - st_axis])
	var plog := {"raised": 0, "rows": 0, "sightline": [], "spikes": [], "crowns": []}
	var done := {}
	var assigned := {}
	var legs: Array = _border_legs(links)
	var keyed: Array = []
	for leg: Array in legs:
		var a: Array = leg[1]
		var c: Array = leg[2]
		var ax := 0 if absf(float(a[1]) - float(c[1])) < 1e-6 else 1
		var first := 0 if ax == st_axis and absf(float(a[1 - ax]) - st_line) < 1e-3 else 1
		keyed.append([first, leg[0], leg])
	keyed = StreetR2Util.sorted_by(keyed, func(x: Array, y: Array) -> bool: return StreetR2Util.tuple_less([x[0], x[1]], [y[0], y[1]]))
	var classes: Array = ["low", "mid", "tall"]
	for kl: Array in keyed:
		var leg: Array = kl[2]
		var lid: String = leg[0]
		var rows := _frontage_rows(bases, leg[1], leg[2])
		for side: int in [1, -1]:
			var row: Array = rows[side]
			if row.is_empty():
				continue
			var all_done := true
			for b: Dictionary in row:
				if not done.has(b["uid"]):
					all_done = false
					break
			if all_done:
				continue
			plog["rows"] = int(plog["rows"]) + 1
			var prev_cls: Variant = null
			var run := 0
			var prev_f: Variant = null
			var hist: Array = []
			for b: Dictionary in row:
				if done.has(b["uid"]):             # a corner building set by a crossing row: fixed, but still a neighbour
					prev_f = assigned[b["uid"]]
					hist.append(prev_f)
					continue
				done[b["uid"]] = true
				var r_ := StreetR2Rng.stream(seed, "frontage", [b["uid"]])
				var top0 := maxf(float(b["h"]), float(tops.get(b["uid"], 0.0)))
				var f0 := int(top0 / fl)
				var cls: String = r_.choices(classes, [P["rhythm_p"]["low"], P["rhythm_p"]["mid"], P["rhythm_p"]["tall"]])
				if prev_cls != null and cls == prev_cls and run >= 2:
					cls = classes[(classes.find(cls) + 1 + r_.randrange(2)) % 3]
				var lohi: Array = P["floors_" + cls]
				var f := r_.randint(int(lohi[0]), int(lohi[1]))
				f = maxi(f, int(P["frontage_min_floors"]))
				if route.has(b["uid"]):
					f = maxi(f, int(room_top.get(b["uid"], 6)) + int(P["route_sign_floors"]))
				# the netrun street's sightline to the landmark
				var mid_c := (float(b["y0"]) + float(b["y1"])) / 2 if st_axis == 0 else (float(b["x0"]) + float(b["x1"])) / 2
				var on_street := absf(mid_c - st_line) < 20
				if on_street and not route.has(b["uid"]):
					var xs: Array = []
					for x: float in [b["x0"], b["x1"]]:
						for y: float in [b["y0"], b["y1"]]:
							xs.append(float(StreetR2OneCity.proj(ov, [x, y, 0.0])[0]) / StreetR2OneCity.frame_w())
					if float(StreetR2Util.amin(xs)) - float(P["sightline_pad"]) < lx and lx < float(StreetR2Util.amax(xs)) + float(P["sightline_pad"]):
						f = mini(f, int(P["sightline_floors"]))
						(plog["sightline"] as Array).append(b["uid"])
				var stacked := float(tops.get(b["uid"], 0.0)) > float(b["h"]) + 1e-6
				var floor_min := maxi(int(P["frontage_min_floors"]), f0 if stacked else 0)       # stacked parts are never cut
				f = maxi(f, floor_min)
				# no flat stretch: any 3 neighbours span at least triple_span_min floors
				if hist.size() >= 2:
					var h2: Array = [hist[hist.size() - 2], hist[hist.size() - 1]]
					var lo3 := mini(mini(int(h2[0]), int(h2[1])), f)
					var hi3 := maxi(maxi(int(h2[0]), int(h2[1])), f)
					var span := int(P["triple_span_min"])
					if hi3 - lo3 < span:
						var mean2 := float(int(h2[0]) + int(h2[1])) / 2.0
						var mn2 := mini(int(h2[0]), int(h2[1]))
						var mx2 := maxi(int(h2[0]), int(h2[1]))
						if float(f) >= mean2 or mn2 + span <= int(P["floors_tall"][1]):
							f = maxi(f, mn2 + span)
						if float(f) < mean2 and mx2 - span >= floor_min:
							f = mx2 - span
				var st_ := int(P["height_step_min"])
				if prev_f != null and absi(f - int(prev_f)) < st_:
					var down := int(prev_f) - st_
					f = down if (f < int(prev_f) and down >= floor_min) else int(prev_f) + st_
				var want := f * fl + 0.1
				if absf(top0 - want) > 0.05 and not (stacked and top0 > want):
					bymap[b["uid"]]["h"] = want / KH
					var kname := "raised" if want > top0 else "lowered"
					plog[kname] = int(plog.get(kname, 0)) + 1
				prev_f = f if not (stacked and top0 > want) else f0
				assigned[b["uid"]] = prev_f
				if not plog.has("rhythm"):
					plog["rhythm"] = {}
				plog["rhythm"][b["uid"]] = [lid, side, f, StreetR2Util.py_round(top0, 1), stacked]
				hist.append(prev_f)
				run = run + 1 if (prev_cls != null and cls == prev_cls) else 1
				prev_cls = cls
	# horizon.break: spikes in the backdrop of the netrun street
	var H := _r("horizon_break")
	var bs2: Array = []
	for b: Dictionary in LAY["buildings"]:
		bs2.append(StreetR2OneCity.bld_info(b))
	var hp := horizon_pick(seed, bs2, D, route)
	var med: float = hp["med"]
	for c: Array in hp["pick"]:
		var top := float(c[0])
		var sx := float(c[1])
		var far := float(c[2])
		var bi: Dictionary = c[3]
		var cx := (float(bi["x0"]) + float(bi["x1"])) / 2
		var cy := (float(bi["y0"]) + float(bi["y1"])) / 2
		var st: Array = H["spike_top"]
		var ty := StreetR2Rng.stream(seed, "spike_top", [bi["uid"]]).uniform(float(st[0]), float(st[1])) * StreetR2OneCity.frame_h()
		var lo_ := 1.0
		var hi_ := 400.0
		for _i in 40:
			var mid := (lo_ + hi_) / 2
			if float(StreetR2OneCity.proj(ov, [cx, cy, mid])[1]) > ty:
				lo_ = mid
			else:
				hi_ = mid
		var z := maxf(maxf(hi_, float(H["spike_k"]) * med), top)
		bymap[bi["uid"]]["h"] = z / KH
		(plog["spikes"] as Array).append({"key": bi["uid"], "z": StreetR2Util.py_round(z, 1), "sx": StreetR2Util.py_round(sx, 3), "far": StreetR2Util.py_round(far, 1)})
	plog["backdrop_median"] = StreetR2Util.py_round(med, 1)
	return {"city": LAY, "log": plog}


# ---------------------------------------------------------------- PLAN
## (u0, u1, face, out) of a building's street face: out = the direction from the face toward the street.
static func _face_frame(b: Dictionary, nrm: Array, axis: int) -> Array:
	if axis == 0:
		return [b["x0"], b["x1"], b["y0"] if float(nrm[1]) > 0 else b["y1"], -1.0 if float(nrm[1]) > 0 else 1.0]
	return [b["y0"], b["y1"], b["x0"] if float(nrm[0]) > 0 else b["x1"], -1.0 if float(nrm[0]) > 0 else 1.0]


static func _pt(axis: int, u: float, d: float, z: float) -> Array:
	return [u, d, z] if axis == 0 else [d, u, z]


static func _dist_of(terr: Dictionary, key: String) -> String:
	var t: String = terr.get(key, "")
	return t if (_r("palette_districts")["sign_pal"] as Dictionary).has(t) else ""


static func _copy_col(c: Array) -> Array:
	return c.duplicate()


## The index of `x` in a set-like String Array, or -1.
static func _room_hit(rooms_by_b: Dictionary, axis: int, key: String, u0: float, u1: float, z0: float, z1: float) -> Variant:
	for ir: Array in rooms_by_b.get(key, []):
		var r: Dictionary = ir[1]
		var us: Array = []
		for p: Array in r["front"]:
			us.append(p[axis])
		if u0 < float(StreetR2Util.amax(us)) + 0.1 and u1 > float(StreetR2Util.amin(us)) - 0.1 and z0 < float(r["front"][2][2]) + 0.1 and z1 > float(r["front"][0][2]) - 0.1:
			return ir[0]
	return null


## `add` of the plate: one sign rectangle on a building's face, clipped to the face, with the sign's texture request. Returns the sign
## (also appended to `ctx.signs`) or null when it would be under 0.4 BU wide.
static func _add(ctx: Dictionary, kind: String, b: Dictionary, u0_in: float, u1_in: float, z0: float, z1: float, col: Array, tex: Dictionary,
		emit: Variant, text_frac: float, words: Array, extra: Dictionary = {}) -> Variant:
	var ff := _face_frame(b, ctx["nrm"], ctx["axis"])
	var bu0 := float(ff[0])
	var bu1 := float(ff[1])
	var face := float(ff[2])
	var out := float(ff[3])
	var u0 := maxf(u0_in, bu0 + 0.05)
	var u1 := minf(u1_in, bu1 - 0.05)
	if u1 - u0 < 0.4:
		return null
	var d := face + out * float(ctx["S"]["sign_off"])
	var c3 := _pt(ctx["axis"], (u0 + u1) / 2, d, (z0 + z1) / 2)
	var signs: Array = ctx["signs"]
	var sg := {"id": "%s_%s_%d" % [kind, b["uid"], signs.size()], "kind": kind, "key": b["uid"], "axis": ctx["axis"], "face": face, "out": out, "d": d,
		"u0": u0, "u1": u1, "z0": z0, "z1": z1, "col": col.duplicate(), "tex": tex, "emit": emit, "text_frac": text_frac, "centre": c3,
		"words": words, "wall": _room_hit(ctx["rooms_by_b"], ctx["axis"], b["uid"], u0, u1, z0, z1), "district": _dist_of(ctx["terr"], b["uid"])}
	for k: String in extra:
		sg[k] = extra[k]
	signs.append(sg)
	return sg


static func _roof_board(ctx: Dictionary, seed: Variant, b: Dictionary, kind: String, w_: float, h_: float, st: String, z_lift: float = 0.9) -> void:
	var PD := _r("palette_districts")
	var ads: Dictionary = StreetR2ConfigData.shipped().ads
	var words: Dictionary = StreetR2ConfigData.shipped().words
	var subs: Array = StreetR2ConfigData.shipped().subs
	var axis: int = ctx["axis"]
	var r_ := StreetR2Rng.stream(seed, "roof_board", [b["uid"]])
	var ff := _face_frame(b, ctx["nrm"], axis)
	var bu0 := float(ff[0])
	var bu1 := float(ff[1])
	var out := float(ff[3])
	var face := float(ff[2])
	var dis := _dist_of(ctx["terr"], b["uid"])
	var pal: Array = PD["sign_pal"][dis]
	var uc := (bu0 + bu1) / 2
	var d := face - out * 0.4
	var z0 := float(b["h"]) + z_lift
	var wl: Array = words[dis]
	var wd: String = wl[r_.randrange(wl.size())]
	var ad: Variant = null
	if st == "ad":
		ad = ads["board"][r_.randrange((ads["board"] as Array).size())]
	var signs: Array = ctx["signs"]
	var sid := "%s_%s_%d" % [kind, b["uid"], signs.size()]
	var col: Array = (pal[r_.randrange(pal.size())] as Array).duplicate()
	var sub: String = subs[r_.randrange(subs.size())]
	signs.append({"id": sid, "kind": kind, "key": b["uid"], "axis": axis, "face": d, "out": out, "d": d, "u0": uc - w_ / 2, "u1": uc + w_ / 2,
		"z0": z0, "z1": z0 + h_, "col": col,
		"tex": {"style": st, "ad": ad, "word": wd, "sub": sub, "seed": StreetR2Rng.art_seed(seed, "tex", [b["uid"], kind])},
		"emit": ctx["S"]["sec_emit"], "text_frac": 0.3 if st != "ad" else 0.25, "centre": _pt(axis, uc, d, z0 + h_ / 2),
		"words": [wd] if st != "ad" else [], "wall": null, "district": dis, "roof": true, "legs": z_lift})


## The dressing plan of art seed `seed` on the street derivation `D`. `merged` = BU building records (see `StreetR2OneCity.merged_buildings`)
## and `terr` = district per uid; `layout_log` = the layout pass log (its `spikes`).
static func plan_pass(seed: Variant, D: Dictionary, merged: Array, terr: Dictionary, layout_log: Dictionary) -> Dictionary:
	var cfg := StreetR2ConfigData.shipped()
	var ov: Dictionary = D["overview"]
	var dec: Dictionary = D["decision"]
	var B: Array = merged
	var bk := {}
	for b: Dictionary in B:
		bk[b["uid"]] = b
	var nrm: Array = D["nrm"]
	var axis := _axis_of(D)
	var sa: Array = D["a"]
	var sc: Array = D["c"]
	var line := float(sa[1 - axis])
	var route: Array = (D["column_uids"] as Array).duplicate()
	var rset := {}
	for u: String in route:
		rset[u] = true
	var spikes: Array = []
	for s: Dictionary in layout_log["spikes"]:
		spikes.append(s["key"])
	var spike_set := {}
	for u: String in spikes:
		spike_set[u] = true
	var mid: Array = [(float(sa[0]) + float(sc[0])) / 2, (float(sa[1]) + float(sc[1])) / 2]
	var u0_s := minf(float(sa[axis]), float(sc[axis]))
	var u1_s := maxf(float(sa[axis]), float(sc[axis]))
	var W_ := StreetR2OneCity.frame_w()
	var H_ := StreetR2OneCity.frame_h()
	var front: Array = StreetR2OneCity.frontage(B, sa, sc, int(D["side"]))
	var fkeys: Array = []
	for b: Dictionary in front:
		fkeys.append(b["uid"])
	var PD := _r("palette_districts")
	var sorted_b: Array = StreetR2Util.sorted_by(B, func(x: Dictionary, y: Dictionary) -> bool: return String(x["uid"]) < String(y["uid"]))
	# ------------------------------------------------ materials.mix + repetition.guard
	var M := _r("materials_mix")
	var kits := {}
	for b: Dictionary in sorted_b:
		var cx := (float(b["x0"]) + float(b["x1"])) / 2
		var cy := (float(b["y0"]) + float(b["y1"])) / 2
		var dx := cx - float(mid[0])
		var dy := cy - float(mid[1])
		if sqrt(dx * dx + dy * dy) > float(M["kit_radius"]):
			continue
		var dw: Dictionary = M["district_weights"]
		var dname := _dist_of(terr, b["uid"])
		var w: Array = dw.get(dname, dw[""])
		kits[b["uid"]] = StreetR2Rng.stream(seed, "kit", [b["uid"]]).choices(M["kits"], w)
	# the frontage (both sides) never repeats a kit between neighbours
	for side: int in [1, -1]:
		var row := StreetR2OneCity.frontage(B, sa, sc, side)
		var prev: Variant = null
		for b: Dictionary in row:
			var k: String = kits.get(b["uid"], "concrete_band")
			if prev != null and k == prev:
				var opts: Array = []
				for x: String in M["kits"]:
					if x != prev:
						opts.append(x)
				k = opts[StreetR2Rng.stream(seed, "kit_fix", [b["uid"]]).randrange(opts.size())]
			kits[b["uid"]] = k
			prev = k
	# stacked parts take their base's kit
	for b: Dictionary in B:
		for p: String in b.get("parts_uid", []):
			if kits.has(b["uid"]):
				kits[p] = kits[b["uid"]]
	# window module per building (repetition guard)
	var modules := {}
	var prevm: Variant = null
	var runm := 0
	var RG := _r("repetition_guard")
	for b: Dictionary in front:
		var m := StreetR2Rng.stream(seed, "module", [b["uid"]]).randrange(3)
		if prevm != null and m == prevm and runm >= int(RG["max_same_module_adjacent"]):
			m = (m + 1) % 3
		runm = runm + 1 if (prevm != null and m == prevm) else 1
		prevm = m
		modules[b["uid"]] = m
	# ------------------------------------------------ crowns (frontage.silhouette)
	var P := _r("frontage_silhouette")
	var crowns: Array = []
	for side: int in [1, -1]:
		var row := StreetR2OneCity.frontage(B, sa, sc, side)
		if row.is_empty():
			continue
		var need := int(ceilf(float(P["crown_share"]) * row.size()))
		var keyed: Array = []
		for b: Dictionary in row:
			keyed.append([StreetR2Rng.stream(seed, "crown_pick", [b["uid"]]).random(), b["uid"], b])
		keyed = StreetR2Util.sorted_by(keyed, func(x: Array, y: Array) -> bool: return StreetR2Util.tuple_less([x[0], x[1]], [y[0], y[1]]))
		var chosen := {}
		for i in mini(need, keyed.size()):
			chosen[keyed[i][1]] = true
		for b: Dictionary in row:
			var r_ := StreetR2Rng.stream(seed, "crown", [b["uid"]])
			if chosen.has(b["uid"]) or r_.random() < 0.15:
				var ck: Array = P["crown_kinds"]
				var kind: String = ck[r_.randrange(ck.size())]
				if float(b["x1"]) - float(b["x0"]) < 3.6 and float(b["y1"]) - float(b["y0"]) < 3.6 and kind == "setback":
					kind = "spire"
				var pal: Array = PD["sign_pal"][_dist_of(terr, b["uid"])]
				var q: Array = []
				for p: Array in b["q"]:
					q.append(p.duplicate())
				var col: Array = (pal[r_.randrange(pal.size())] as Array).duplicate()
				var floors := r_.randint(2, 4)
				var hh := r_.uniform(4.0, 9.0)
				crowns.append({"key": b["uid"], "kind": kind, "side": side, "top": b["h"], "q": q, "box": [b["x0"], b["y0"], b["x1"], b["y1"]], "col": col,
					"floors": floors, "h": hh})
	# ------------------------------------------------ lit silhouette trims
	var trims := {}
	for side: int in [1, -1]:
		for b: Dictionary in StreetR2OneCity.frontage(B, sa, sc, side):
			var r_ := StreetR2Rng.stream(seed, "trim", [b["uid"]])
			var pal: Array = PD["sign_pal"][_dist_of(terr, b["uid"])]
			var c1: Array = (pal[r_.randrange(pal.size())] as Array).duplicate()
			var c2: Array = (pal[r_.randrange(pal.size())] as Array).duplicate()
			var be: Array = P["band_every"]
			var every := r_.randint(int(be[0]), int(be[1]))
			var corner := r_.random() < float(P["p_corner"])
			trims[b["uid"]] = {"col": c1, "col2": c2, "band_every": every, "corner": corner, "roof": bool(P["roof_rim"]), "gap_p": P["band_gap_p"]}
	# ------------------------------------------------ dressing.signs
	var S := _r("dressing_signs")
	var words: Dictionary = cfg.words
	var subs: Array = cfg.subs
	var ads: Dictionary = cfg.ads
	var signs: Array = []
	var rooms_by_b := {}
	for i: String in D["rooms"]:
		var r: Dictionary = D["rooms"][i]
		if not rooms_by_b.has(r["bld_uid"]):
			rooms_by_b[r["bld_uid"]] = []
		(rooms_by_b[r["bld_uid"]] as Array).append([i, r])
	var ctx := {"signs": signs, "nrm": nrm, "axis": axis, "S": S, "terr": terr, "rooms_by_b": rooms_by_b}
	var fl := StreetR2OneCity.floor_bu()
	var room_top := {}
	for r: Dictionary in D["rooms"].values():
		room_top[r["bld_uid"]] = maxf(float(room_top.get(r["bld_uid"], 0.0)), float(r["front"][2][2]))
	var hero_i := 0
	for b: Dictionary in front:
		var key: String = b["uid"]
		var r_ := StreetR2Rng.stream(seed, "signs", [key])
		var dis := _dist_of(terr, key)
		var pal: Array = PD["sign_pal"][dis]
		var wl: Array = words[dis]
		var ff := _face_frame(b, nrm, axis)
		var bu0 := float(ff[0])
		var bu1 := float(ff[1])
		var wdt := bu1 - bu0
		# shopfront strip on every frontage base + a shop sign over it (p_shop_sign)
		var sc_col: Array = pal[r_.randrange(pal.size())]
		var shop_word: String = wl[r_.randrange(wl.size())]
		_add(ctx, "shopfront", b, bu0 + 0.35, bu1 - 0.35, 0.15, 1.45, sc_col,
			{"style": "shop", "word": shop_word, "seed": StreetR2Rng.art_seed(seed, "tex", [key, "shop"])}, S["shop_emit"], 0.0, [])
		if r_.random() < float(S["p_shop_sign"]):
			var sw := minf(wdt * 0.8, r_.uniform(2.6, 4.0))
			var u0 := bu0 + r_.uniform(0.3, maxf(0.31, wdt - sw - 0.3))
			var wd: String = wl[r_.randrange(wl.size())]
			var zt := 1.6 + sw / r_.uniform(2.0, 2.6)
			var scol: Array = pal[r_.randrange(pal.size())]
			var sub: String = subs[r_.randrange(subs.size())]
			_add(ctx, "shop_sign", b, u0, u0 + sw, 1.6, zt, scol, {"style": "box", "word": wd, "sub": sub, "seed": StreetR2Rng.art_seed(seed, "tex", [key, "shopsign"])},
				S["shop_emit"], 0.5, [wd])
		var top := float(b["h"])
		if rset.has(key):
			# hero sign over the rooms, in the district pair (hero_i alternates) - blade (vertical) or wall (board)
			var z0 := float(room_top.get(key, 6 * fl)) + 0.45
			var z1 := top - 0.7
			var hk: Array = S["hero_kinds"]
			var kind: String = hk[r_.randrange(2)] if (z1 - z0) > 3.2 and wdt > 4.2 else "blade"
			var hcol: Array
			if dis != "":
				hcol = pal[hero_i % 2]
			else:
				hcol = [[1.0, 0.16, 0.6], [0.16, 0.8, 1.0]][hero_i % 2]
			var wd: String = wl[r_.randrange(wl.size())]
			if kind == "blade":
				var bw := minf(2.6, maxf(1.6, wdt * 0.3))
				var bh := minf(z1 - z0, 0.46 * bw * (wd.replace(" ", "").length() + 1.5))
				var left := r_.random() < 0.5
				var u0 := bu0 + 0.2 if left else bu1 - 0.2 - bw
				var sub: String = subs[r_.randrange(subs.size())]
				_add(ctx, "hero_blade", b, u0, u0 + bw, z1 - bh, z1, hcol, {"style": "blade", "word": wd, "sub": sub, "seed": StreetR2Rng.art_seed(seed, "tex", [key, "hero"])},
					S["hero_emit"], 0.38, [wd], {"hero": true})
			else:
				var bw := minf(wdt - 0.8, r_.uniform(4.0, 6.5))
				var bh := minf(z1 - z0, bw / r_.uniform(1.7, 2.3))
				var u0 := bu0 + (wdt - bw) / 2
				var zc := z0 + r_.uniform(0.0, maxf(0.0, z1 - z0 - bh))
				var ad: Variant = null
				if r_.random() < 0.5:
					ad = ads["hero"][dis][r_.randrange(3)]
				var sub: String = subs[r_.randrange(subs.size())]
				_add(ctx, "hero_wall", b, u0, u0 + bw, zc, zc + bh, hcol, {"style": "ad" if ad != null else "wall", "ad": ad, "word": wd, "sub": sub,
					"seed": StreetR2Rng.art_seed(seed, "tex", [key, "hero"])}, S["hero_emit"], 0.30, [wd], {"hero": true})
			hero_i += 1
		# secondary sign (p_secondary): a small blade / box / holo, off the rooms
		if r_.random() < float(S["p_secondary"]):
			var kinds3: Array = ["sec_blade", "sec_box", "sec_holo"]
			var kind: String = kinds3[r_.randrange(3)]
			var zlo := float(room_top.get(key, 2.2)) + 0.3 if rset.has(key) else 2.4
			if top - 0.8 - zlo > 2.0:
				var wd: String = wl[r_.randrange(wl.size())]
				var bw: float
				var bh: float
				var u0: float
				var tx: Dictionary
				var tf: float
				if kind == "sec_blade":
					bw = 0.8
					bh = minf(top - 0.8 - zlo, r_.uniform(2.6, 4.4))
					u0 = bu0 + 0.15 if r_.random() < 0.5 else bu1 - 0.95
					tx = {"style": "blade", "word": wd.substr(0, 6), "sub": "", "seed": StreetR2Rng.art_seed(seed, "tex", [key, "sec"])}
					tf = 0.38
				else:
					bw = minf(wdt * 0.75, r_.uniform(2.6, 4.2))
					bh = bw / r_.uniform(1.5, 2.2)
					u0 = bu0 + r_.uniform(0.2, maxf(0.21, wdt - bw - 0.2))
					var sub: String = subs[r_.randrange(subs.size())]
					tx = {"style": "box" if kind == "sec_box" else "holo", "word": wd, "sub": sub, "seed": StreetR2Rng.art_seed(seed, "tex", [key, "sec"])}
					tf = 0.42 if kind == "sec_box" else 0.26
				var z0 := zlo + r_.uniform(0.0, maxf(0.0, top - 0.8 - zlo - bh))
				var scol: Array = pal[r_.randrange(pal.size())]
				var s_: Variant = _add(ctx, kind, b, u0, u0 + bw, z0, z0 + bh, scol, tx, S["sec_emit"], tf, [wd])
				if s_ != null and (s_ as Dictionary)["wall"] != null:
					signs.pop_back()
	# backdrop signs: a tall vertical sign high on visible backdrop towers (the spikes first)
	for key: String in spikes:
		if not bk.has(key):
			continue
		var b: Dictionary = bk[key]
		var r_ := StreetR2Rng.stream(seed, "backdrop_sign", [key])
		if r_.random() > float(S["backdrop_sign_p"]) and key != spikes[0]:
			continue
		var dis := _dist_of(terr, key)
		var pal: Array = PD["sign_pal"][dis]
		var wd: String = words[dis][r_.randrange(3)]
		var ff := _face_frame(b, nrm, axis)
		var bu0 := float(ff[0])
		var bu1 := float(ff[1])
		var bw := minf(4.5, (bu1 - bu0) * 0.5)
		var bh := minf(float(b["h"]) * 0.4, 0.46 * bw * (wd.replace(" ", "").length() + 1.5))
		var z1 := float(b["h"]) - r_.uniform(1.5, 4.0)
		var u0 := bu0 + 0.3 if r_.random() < 0.5 else bu1 - 0.3 - bw
		var scol: Array = pal[r_.randrange(pal.size())]
		_add(ctx, "backdrop_blade", b, u0, u0 + bw, z1 - bh, z1, scol, {"style": "blade", "word": wd, "sub": "", "seed": StreetR2Rng.art_seed(seed, "tex", [key, "bd"])},
			S["backdrop_emit"], 0.36, [wd])
	# megastructure: on the tallest spike inside the central 2/3 of the OVERVIEW, off the DECISION frame
	var mega: Variant = null
	var cands: Array = []
	var front_top := float(front[0]["h"])
	for b: Dictionary in front:
		front_top = maxf(front_top, float(b["h"]))
	var loc: Array = ov["persp"]["loc"]
	var lens := float(ov["persp"]["lens"])
	for b: Dictionary in sorted_b:
		if rset.has(b["uid"]) or float(b["z0"]) > NEAR_BASE:
			continue
		var far := _far_of(b, axis, line, nrm)
		if not (24.0 < far and far < 170.0) or float(b["h"]) < front_top * 0.8:
			continue
		var cx := (float(b["x0"]) + float(b["x1"])) / 2
		var cy := (float(b["y0"]) + float(b["y1"])) / 2
		var p1 := StreetR2OneCity.proj(ov, [cx, cy, b["h"]])
		var x := float(p1[0]) / W_
		var y := float(p1[1]) / H_
		var p2 := StreetR2OneCity.proj(dec, [cx, cy, b["h"]])
		var xd := float(p2[0]) / W_
		var yd := float(p2[1]) / H_
		var in_dec := 0.0 < xd and xd < 1.0 and 0.0 < yd and yd < 1.0
		var sz := _mega_size(loc, lens, W_, cx, cy, float(b["h"]))
		var p3 := StreetR2OneCity.proj(ov, [cx, cy, float(b["h"]) + 1.6 + sz * 0.75])
		var ytop := float(p3[1]) / H_          # the tallest kind (globe on its mast)
		if 1.0 / 6.0 < x and x < 5.0 / 6.0 and not in_dec and ytop > float(S["mega_headroom"]) and y < 0.45:
			cands.append([float(b["h"]) + (40.0 if spike_set.has(b["uid"]) else 0.0), b["uid"], b, x, y])
	if not cands.is_empty():
		cands = StreetR2Util.sorted_by(cands, func(x: Array, y: Array) -> bool: return StreetR2Util.tuple_less([-float(x[0]), x[1]], [-float(y[0]), y[1]]))
		var best: Array = cands[0]
		var key: String = best[1]
		var b: Dictionary = best[2]
		var r_ := StreetR2Rng.stream(seed, "mega", [key])
		var mk: Array = S["mega_kinds"]
		var kind: String = mk[r_.randrange(mk.size())]
		var cx := (float(b["x0"]) + float(b["x1"])) / 2
		var cy := (float(b["y0"]) + float(b["y1"])) / 2
		var dis := _dist_of(terr, key)
		var mcols: Array = [[0.35, 0.9, 1.0], [1.0, 0.25, 0.65], [1.0, 0.65, 0.2]]
		var col: Array = (mcols[r_.randrange(3)] as Array).duplicate()
		var h := float(b["h"])
		var size := _mega_size(loc, lens, W_, cx, cy, h)
		var ad: String = ads["mega"][r_.randrange((ads["mega"] as Array).size())]
		mega = {"kind": kind, "key": key, "pos": [cx, cy, h], "size": size, "col": col, "screen": [best[3], best[4]], "district": dis,
			"tex": {"style": "ad", "ad": ad, "word": "", "sub": "", "seed": StreetR2Rng.art_seed(seed, "tex", [key, "mega"])}, "emit": S["mega_emit"]}
	# roof boards: every sign_frame crown on the camera row carries a lit board, and backdrop roofs over 14 BU in the OVERVIEW carry one with
	# p_roof_board. Boards stand on legs at the roof's street edge, facing the street.
	var kinds_cb: Array = ["wall", "ad", "holo"]
	for c_: Dictionary in crowns:
		if c_["kind"] == "sign_frame" and int(c_["side"]) == int(D["side"]):
			var b: Dictionary = bk[c_["key"]]
			var span := (float(b["x1"]) - float(b["x0"]) if axis == 0 else float(b["y1"]) - float(b["y0"]))
			var w_ := minf(span, 7.0) * 0.85
			_roof_board(ctx, seed, b, "crown_board", w_, w_ * 0.42, kinds_cb[StreetR2Rng.stream(seed, "crown_board", [b["uid"]]).randrange(3)])
	var kinds_rb: Array = ["holo", "ad", "wall"]
	var mega_key: Variant = (mega as Dictionary)["key"] if mega != null else null
	for b: Dictionary in sorted_b:
		if rset.has(b["uid"]) or spike_set.has(b["uid"]) or (mega != null and b["uid"] == mega_key) or float(b["z0"]) > NEAR_BASE or float(b["h"]) < 14.0:
			continue
		var far := _far_of(b, axis, line, nrm)
		if not (12.0 < far and far < 170.0) or StreetR2Rng.stream(seed, "p_roof_board", [b["uid"]]).random() > float(S["p_roof_board"]):
			continue
		var pp := StreetR2OneCity.proj(ov, [(float(b["x0"]) + float(b["x1"])) / 2, (float(b["y0"]) + float(b["y1"])) / 2, b["h"]])
		var x := float(pp[0]) / W_
		var y := float(pp[1]) / H_
		if not (0.02 < x and x < 0.98 and 0.04 < y and y < 0.8):
			continue
		var span := (float(b["x1"]) - float(b["x0"]) if axis == 0 else float(b["y1"]) - float(b["y0"]))
		var wv := minf(span, 7.5) * 0.8
		if wv < 2.5:
			continue
		_roof_board(ctx, seed, b, "roof_board", wv, wv * 0.6, kinds_rb[StreetR2Rng.stream(seed, "roof_board_kind", [b["uid"]]).randrange(3)])
	# ------------------------------------------------ repetition.guard (rhythm) + props.facade
	var PF := _r("props_facade")
	var rhythm := {}
	for b: Dictionary in sorted_b:
		var uid: String = b["uid"]
		if not kits.has(uid):
			continue
		var ff := _face_frame(b, nrm, axis)
		rhythm[uid] = StreetR2Facade.make_rhythm(StreetR2Rng.stream(seed, "rhythm", [uid]), kits[uid], float(ff[1]) - float(ff[0]), float(b["h"]), RG,
			PD["sign_pal"][_dist_of(terr, uid)], room_top.get(uid))
	for b: Dictionary in B:
		for pu: String in b.get("parts_uid", []):
			if rhythm.has(b["uid"]) and pu != b["uid"]:
				rhythm[pu] = rhythm[b["uid"]]
	var props: Array = []
	var front_set := {}
	for u: String in fkeys:
		front_set[u] = true
	var prow: Array = front.duplicate()
	for b: Dictionary in sorted_b:
		if front_set.has(b["uid"]) or float(b["z0"]) > NEAR_BASE or not kits.has(b["uid"]):
			continue
		var far := _far_of(b, axis, line, nrm)
		var cu := (float(b["x0"]) + float(b["x1"])) / 2 if axis == 0 else (float(b["y0"]) + float(b["y1"])) / 2
		if 0.5 < far and far < 6.5 + float(PF["second_row_band"]) and u0_s - 20 < cu and cu < u1_s + 20:
			prow.append(b)
	for b: Dictionary in prow:
		var uid: String = b["uid"]
		if not rhythm.has(uid):
			continue
		var ff := _face_frame(b, nrm, axis)
		var rh: Dictionary = rhythm[uid]
		var fz := StreetR2Facade.floor_bounds(rh, 0.0, float(b["h"]))
		var rects: Array = []
		for s_: Dictionary in signs:
			if s_["key"] == uid:
				rects.append([s_["u0"], s_["z0"], s_["u1"], s_["z1"]])
		rects.append([ff[0], 0.0, ff[1], 1.9])                                   # the shopfront zone
		for r_: Dictionary in D["rooms"].values():
			if r_["bld_uid"] == uid:
				var us_: Array = []
				for q: Array in r_["front"]:
					us_.append(q[axis])
				rects.append([float(StreetR2Util.amin(us_)) - 0.15, r_["front"][0][2], float(StreetR2Util.amax(us_)) + 0.15, r_["front"][2][2]])
		props.append_array(StreetR2Facade.make_props(StreetR2Rng.stream(seed, "facade_props", [uid]), uid, b, ff, axis, line,
			PD["sign_pal"][_dist_of(terr, uid)], D["rooms"], rects, PF, fz))
	# ------------------------------------------------ streets.light: kerb lamp posts
	var L_ := _r("streets_light")
	var lamps: Array = []
	var lamps_dropped := 0
	var k := 0
	var u := u0_s - 30.0
	var shifts: Array = [0.0, 0.8, -0.8, 1.6, -1.6, PF["lamp_shift_max"], -float(PF["lamp_shift_max"])]
	while u <= u1_s + 30.0:
		for side: int in [-1, 1]:
			var r_ := StreetR2Rng.stream(seed, "lamp", [StreetR2Util.py_round(u, 1), side])
			var jit := float(L_["lamp_jit"])
			var uu0 := u + r_.uniform(-jit, jit)
			var nv := float(nrm[1]) if axis == 0 else float(nrm[0])
			var pos := _pt(axis, uu0, line + side * float(L_["kerb_off"]) * nv, 0.0)
			var warm := (k % 3) != 0
			var ok_: Variant = null
			for dsh: float in shifts:
				var uu_ := float(pos[axis]) + dsh
				if not StreetR2Facade.prop_hits_opening({"u0": uu_ - 0.15, "u1": uu_ + 0.15, "z0": 0.0, "z1": L_["lamp_post_h"], "face": pos[1 - axis], "out": 0.0, "depth": 0.0},
						D["rooms"], axis, line, float(PF["opening_margin"])):
					ok_ = uu_
					break
			if ok_ == null:
				lamps_dropped += 1
				k += 1
				continue
			pos = _pt(axis, float(ok_), float(pos[1 - axis]), 0.0)
			lamps.append({"pos": pos, "side": side, "col": [1.0, 0.72, 0.42] if warm else [0.55, 0.85, 1.0]})
			k += 1
		u += float(L_["lamp_step"])
	# ------------------------------------------------ atmosphere.layers: plumes + bank glow stops along the street
	var A := _r("atmosphere_layers")
	var plume_src: Array = []
	for c_: Dictionary in crowns:
		if (c_["kind"] == "roof_box" or c_["kind"] == "setback") and int(c_["side"]) == int(D["side"]):
			if bk.has(c_["key"]):
				var b: Dictionary = bk[c_["key"]]
				plume_src.append([(float(b["x0"]) + float(b["x1"])) / 2, (float(b["y0"]) + float(b["y1"])) / 2, b["h"], c_["key"]])
	for key: String in spikes:
		if bk.has(key) and (mega == null or key != mega_key):
			var b: Dictionary = bk[key]
			plume_src.append([(float(b["x0"]) + float(b["x1"])) / 2, (float(b["y0"]) + float(b["y1"])) / 2, b["h"], key])
	var keyed_p: Array = []
	for p: Array in plume_src:
		keyed_p.append([StreetR2Rng.stream(seed, "plume", [p[3]]).random(), p[3], p])
	keyed_p = StreetR2Util.sorted_by(keyed_p, func(x: Array, y: Array) -> bool: return StreetR2Util.tuple_less([x[0], x[1]], [y[0], y[1]]))
	var plumes: Array = []
	for i in mini(int(A["plumes"]), keyed_p.size()):
		var p: Array = keyed_p[i][2]
		var r_ := StreetR2Rng.stream(seed, "plume_size", [p[3]])
		var ph: Array = A["plume_h"]
		var pr: Array = A["plume_r"]
		var hv := r_.uniform(float(ph[0]), float(ph[1]))
		var rv := r_.uniform(float(pr[0]), float(pr[1]))
		plumes.append({"pos": [p[0], p[1], p[2]], "h": hv, "r": rv, "key": p[3]})
	var stops: Array = []
	for kk in 13:
		var uu := u0_s - 150 + kk * (u1_s - u0_s + 300) / 12.0
		var cnt := {}
		for b: Dictionary in B:
			var cu := (float(b["x0"]) + float(b["x1"])) / 2 if axis == 0 else (float(b["y0"]) + float(b["y1"])) / 2
			var far := _far_of(b, axis, line, nrm)
			if absf(cu - uu) < 18 and 10 < far and far < 140:
				var d_ := _dist_of(terr, b["uid"])
				cnt[d_] = int(cnt.get(d_, 0)) + 1
		var dsel := ""
		if not cnt.is_empty():
			var items: Array = []
			for dn: String in cnt:
				items.append([-int(cnt[dn]), dn])
			items = StreetR2Util.sorted_by(items, func(x: Array, y: Array) -> bool: return StreetR2Util.tuple_less(x, y))
			dsel = items[0][1]
		var col: Array
		if dsel != "":
			col = (PD["hues"][dsel] as Array).duplicate()
		else:
			col = [[1.0, 0.16, 0.6], [0.16, 0.8, 1.0]][kk % 2]
		stops.append({"u": uu, "district": dsel, "col": col})
	var near: Array = []                        # streets.light section_spill: the cut near-side frontage keeps its light
	for b: Dictionary in StreetR2OneCity.frontage(B, sa, sc, -int(D["side"])):
		var neg: Array = [-float(nrm[0]) if typeof(nrm[0]) == TYPE_FLOAT else -int(nrm[0]), -float(nrm[1]) if typeof(nrm[1]) == TYPE_FLOAT else -int(nrm[1])]
		var ff := _face_frame(b, neg, axis)
		near.append({"uid": b["uid"], "u0": ff[0], "u1": ff[1], "face": ff[2], "out": ff[3], "top": b["h"], "col": trims[b["uid"]]["col"]})
	var faces: Array = []
	for b: Dictionary in front:
		var ff := _face_frame(b, nrm, axis)
		faces.append({"uid": b["uid"], "u0": ff[0], "u1": ff[1], "face": ff[2], "out": ff[3], "top": b["h"], "col": trims[b["uid"]]["col"]})
	# the fog underlight ramp: the AAA pair and the districts in view whose hue is not the ambient violet
	var dset := {}
	for s_: Dictionary in stops:
		if s_["district"] != "":
			dset[s_["district"]] = true
	var dkeys: Array = dset.keys()
	IdSort.sort_ids(dkeys)
	var ul: Array = []
	for d_: String in dkeys:
		if d_ != "halcyon" and d_ != "orbital":
			ul.append((PD["hues"][d_] as Array).duplicate())
	ul.append([1.0, 0.16, 0.6])
	var kits_out := {}
	for kn: String in kits:
		kits_out[kn] = kits[kn]
	var views := {}
	for u2: String in fkeys:
		views[_dist_of(terr, u2)] = true
	var views_k: Array = views.keys()
	IdSort.sort_ids(views_k)
	var plan := {"seed": seed, "axis": axis, "nrm": nrm, "line": line, "route": route, "front": fkeys, "front_faces": faces, "near_faces": near, "trims": trims,
		"rhythm": rhythm, "props": props, "lamps_dropped": lamps_dropped, "underlight": ul, "kits": kits_out, "modules": modules, "crowns": crowns,
		"signs": signs, "mega": mega, "lamps": lamps, "plumes": plumes, "bank_stops": stops, "spikes": spikes,
		"fg_lanes": (_r("foreground_street")["fg_lanes"] as Array).duplicate(), "lod": _r("lod_signs"), "districts_in_view": views_k}
	plan["checks"] = checks(plan, D, B, bk)
	return plan


## `plan_pass` on raw lot records (the plate's input shape): merges the buildings and reads the district of each from its `terr`.
static func plan_pass_lots(seed: Variant, D: Dictionary, city: Dictionary, layout_log: Dictionary) -> Dictionary:
	var terr := {}
	for b: Dictionary in city["buildings"]:
		terr["%d_%d" % [b["ci"], b["key"]]] = b["terr"]
	return plan_pass(seed, D, StreetR2OneCity.merged_buildings(city["buildings"]), terr, layout_log)


static func _far_of(b: Dictionary, axis: int, line: float, nrm: Array) -> float:
	var cx := (float(b["x0"]) + float(b["x1"])) / 2
	var cy := (float(b["y0"]) + float(b["y1"])) / 2
	return (cy - line) * float(nrm[1]) if axis == 0 else (cx - line) * float(nrm[0])


static func _mega_size(loc: Array, lens: float, w: float, cx: float, cy: float, h: float) -> float:
	var dx := cx - float(loc[0])
	var dy := cy - float(loc[1])
	var dz := h - float(loc[2])
	return 150.0 / w * sqrt(dx * dx + dy * dy + dz * dz) * 36.0 / lens


# ---------------------------------------------------------------- plan-level rule checks
## The rule tests the plan carries (R-SIL, materials, R-REP-1, R-DET-2, props, horizon). Adds `cap_px_ov` to the legible signs.
static func checks(plan: Dictionary, D: Dictionary, B: Array, bk: Dictionary) -> Dictionary:
	var out := {}
	var ov: Dictionary = D["overview"]
	var fr: Array = []
	for k: String in plan["front"]:
		fr.append(bk[k])
	var fl := StreetR2OneCity.floor_bu()
	var P := _r("frontage_silhouette")
	var steps: Array = []
	for i in fr.size() - 1:
		steps.append(absi(int(float(fr[i]["h"]) / fl) - int(float(fr[i + 1]["h"]) / fl)))
	var eq := 0
	var run := 0
	for s: int in steps:
		run = run + 1 if s <= 1 else 0
		eq = maxi(eq, run + 1 if run != 0 else 0)
	var ncrown := 0
	for c: Dictionary in plan["crowns"]:
		if (plan["front"] as Array).has(c["key"]):
			ncrown += 1
	var floors: Array = []
	for b: Dictionary in fr:
		floors.append(int(float(b["h"]) / fl))
	var share := float(ncrown) / float(maxi(1, fr.size()))
	var min_step: Variant = StreetR2Util.amin(steps) if not steps.is_empty() else null
	var ok_sil: bool = ((int(min_step) >= int(P["height_step_min"])) if not steps.is_empty() else true) and share >= float(P["crown_share"]) - 1e-6
	out["frontage.silhouette"] = {"floors": floors, "min_step": min_step, "max_equal_tops": eq, "crown_share": StreetR2Util.py_round(share, 2), "ok": ok_sil}
	# materials.mix
	var M := _r("materials_mix")
	var ks: Array = []
	for k: String in plan["front"]:
		ks.append((plan["kits"] as Dictionary).get(k))
	var adj := 0
	for i in ks.size() - 1:
		if ks[i] == ks[i + 1]:
			adj += 1
	var kset := {}
	for v: String in (plan["kits"] as Dictionary).values():
		kset[v] = true
	var kinds: Array = kset.keys()
	IdSort.sort_ids(kinds)
	out["materials.mix"] = {"kits_in_radius": kinds.size(), "frontage_kits": ks, "adjacent_same": adj, "ok": kinds.size() >= int(M["material_kinds"]) and adj == 0}
	var km: Array = []
	for k: String in plan["front"]:
		km.append([(plan["kits"] as Dictionary).get(k), (plan["modules"] as Dictionary)[k]])
	var mx := 1
	var runm := 1
	for i in km.size() - 1:
		runm = runm + 1 if (km[i][0] == km[i + 1][0] and km[i][1] == km[i + 1][1]) else 1
		mx = maxi(mx, runm)
	out["repetition.guard"] = {"max_same_module_run": mx, "ok": mx <= int(_r("repetition_guard")["max_same_module_adjacent"])}
	# dressing.signs
	var S := _r("dressing_signs")
	var bad: Array = []
	var legible := 0
	var legible_ids: Array = []
	var heroes := {}
	var central := false
	var axis: int = plan["axis"]
	var wf := StreetR2OneCity.frame_w()
	for s: Dictionary in plan["signs"]:
		var has_b: bool = bk.has(s["key"])
		var b: Variant = bk.get(s["key"])
		var ok := has_b and absf(float(s["d"]) - float(s["face"])) <= 0.35 and float(s["u0"]) >= minf(float(b["x0"]), float(b["y0"])) - 1e3
		if has_b and s.has("roof") and s["roof"]:
			var ff := _face_frame(b, plan["nrm"], axis)
			ok = float(ff[0]) - 0.01 <= float(s["u0"]) and float(s["u1"]) <= float(ff[1]) + 0.01 and absf(float(s["z0"]) - float(s["legs"]) - float(b["h"])) < 0.05
		elif has_b:
			var ff := _face_frame(b, plan["nrm"], axis)
			ok = ok and float(ff[0]) - 0.01 <= float(s["u0"]) and float(s["u1"]) <= float(ff[1]) + 0.01 and float(s["z0"]) >= -0.01 and float(s["z1"]) <= float(b["h"]) + 0.01
		if not ok:
			bad.append(s["id"])
		if s.has("hero") and s["hero"]:
			heroes[s["key"]] = s["id"]
			var x := float(StreetR2OneCity.proj(ov, s["centre"])[0]) / wf
			var cf := float(S["hero_central_frac"])
			if (1 - cf) / 2 < x and x < 1 - (1 - cf) / 2:
				central = true
		if float(s["text_frac"]) > 0 and not (s["words"] as Array).is_empty():
			var um := (float(s["u0"]) + float(s["u1"])) / 2
			var hpx := absf(float(StreetR2OneCity.proj(ov, _pt(axis, um, float(s["d"]), float(s["z1"])))[1]) - float(StreetR2OneCity.proj(ov, _pt(axis, um, float(s["d"]), float(s["z0"])))[1]))
			var wpx := absf(float(StreetR2OneCity.proj(ov, _pt(axis, float(s["u1"]), float(s["d"]), float(s["z0"])))[0]) - float(StreetR2OneCity.proj(ov, _pt(axis, float(s["u0"]), float(s["d"]), float(s["z0"])))[0]))
			var cap := float(s["text_frac"]) * (wpx if s["tex"]["style"] == "blade" else hpx)
			s["cap_px_ov"] = StreetR2Util.py_round(cap, 1)
			if cap >= float(S["legible_px"]):
				legible += 1
				legible_ids.append(s["id"])
	var mega: Variant = plan["mega"]
	out["dressing.signs"] = {"signs": (plan["signs"] as Array).size(), "off_face": bad, "heroes": heroes.size(), "route_columns": (plan["route"] as Array).size(),
		"hero_central": central, "legible_ov": legible, "legible_ids": legible_ids, "megastructure": (mega as Dictionary)["kind"] if mega != null else null,
		"ok": bad.is_empty() and heroes.size() == (plan["route"] as Array).size() and central and legible >= int(S["signs_on_screen_min"]) and mega != null}
	# roof clutter kinds on the frontage
	var PF := _r("props_facade")
	var blocked: Array = []
	var kset2 := {}
	for p: Dictionary in plan["props"]:
		if StreetR2Facade.prop_hits_opening(p, D["rooms"], axis, float(plan["line"]), float(PF["opening_margin"])):
			blocked.append(p["id"])
		kset2[p["kind"]] = true
	var lamp_bad := 0
	var lph := float(_r("streets_light")["lamp_post_h"])
	for l: Dictionary in plan["lamps"]:
		var lp: Array = l["pos"]
		if StreetR2Facade.prop_hits_opening({"u0": float(lp[axis]) - 0.15, "u1": float(lp[axis]) + 0.15, "z0": 0.0, "z1": lph, "face": lp[1 - axis], "out": 0.0, "depth": 0.0},
				D["rooms"], axis, float(plan["line"]), float(PF["opening_margin"])):
			lamp_bad += 1
	var kinds_ := kset2.keys()
	IdSort.sort_ids(kinds_)
	out["props.facade"] = {"props": (plan["props"] as Array).size(), "kinds": kinds_, "blocked_by_opening": blocked, "lamps_in_front_of_openings": lamp_bad,
		"lamps_dropped": plan.get("lamps_dropped"), "rhythm_buildings": (plan["rhythm"] as Dictionary).size(),
		"ok": blocked.is_empty() and lamp_bad == 0 and kinds_.size() >= 4}
	out["horizon.break"] = {"spikes": (plan["spikes"] as Array).size(), "ok": (plan["spikes"] as Array).size() >= int(_r("horizon_break")["spikes_min"])}
	return out
