class_name NetrunArtLayoutRules
extends RefCounted
## NA-11 twin of `layout.py` `apply_layout_rules`, `frontage_silhouette`, `horizon_break` and `apply_rules`: the layout rules
## on a `city.json` dict (frontage minimum floors, border street width, the street r2 height passes). Pure on its inputs
## (the city is copied), no engine RNG: draws are splitmix64 art streams (`ArtSeed`). Numbers come from the twin config
## (`NetrunArtConfigData.layout_rules`). Heights equal the Python oracle to 1e-4 BU (tests/netrun_art/test_na11_layout_rules.gd).

const RHYTHM: Array = ["low", "mid", "tall"]
## Cell size of the building index (BU); only a speed knob, results do not depend on it.
const INDEX_BU: float = 12.0


## Every link of `net` sorted by `(a, b)` ("all": the fixed city), else `NetrunArtLayout.border_links` ("state").
static func links_of(net: Dictionary, border_mode: String = "state") -> Array:
	if border_mode != "all":
		return NetrunArtLayout.border_links(net)
	var links: Array = (net["links"] as Array).duplicate()
	links.sort_custom(func(p: Dictionary, q: Dictionary) -> bool:
		if String(p["a"]) != String(q["a"]):
			return IdSort.less(String(p["a"]), String(q["a"]))
		return IdSort.less(String(p["b"]), String(q["b"])))
	return links


## The whole pipeline in spec order: frontage minimum + border width, silhouette, HQ zone cap, horizon. `route_tops` bid -> top room floor.
## `stats` (optional) receives frontage / raised / moved / silhouette_* / spikes counts.
static func apply_rules(city: Dictionary, net: Dictionary, route_tops: Dictionary = {}, border_mode: String = "state",
		stats: Dictionary = {}) -> Dictionary:
	var ctx: Dictionary = {}
	var c1: Dictionary = apply_layout_rules(city, net, border_mode, stats, ctx)
	var c2: Dictionary = frontage_silhouette(c1, net, route_tops, border_mode, stats, ctx)
	return horizon_break(hq_cap(c2, route_tops.keys(), stats), net, route_tops.keys(), border_mode, stats, ctx)


## `layout.rules` (spec 3.2): the street-front band raised to its minimum and border streets widened.
static func apply_layout_rules(city: Dictionary, net: Dictionary, border_mode: String = "state", stats: Dictionary = {},
		ctx: Dictionary = {}) -> Dictionary:
	var r: Dictionary = _rules()
	var cfg: NetrunArtConfigData = NetrunArtConfigData.shipped()
	var fb: Array = cfg.layout["front_band"]
	var reach: float = _reach()
	var fl: float = NetrunArtUnits.floor_bu()
	var out: Dictionary = _cow(city)
	var step: float = (float(r["border_street_width"]) - float(r["base_street_width"])) / 2.0
	var bases: Array = NetrunArtLayout.merged_buildings(city)
	var cow: Dictionary = _cow_index(out)
	var done: Dictionary = {}
	var raised: int = 0
	var moved: int = 0
	var index: Dictionary = _index(bases)
	for link: Dictionary in links_of(net, border_mode):
		var legs: Array = legs_of(city, link, ctx)
		for li in range(legs.size() - 1):
			var a: Array = legs[li]
			var c: Array = legs[li + 1]
			var ax: int = NetrunArtLayout.leg_axis(a, c)
			var lo: float = minf(float(a[ax]), float(c[ax])) - reach
			var hi: float = maxf(float(a[ax]), float(c[ax])) + reach
			for bi: Dictionary in _near(index, ax, a, lo, hi):
				if done.has(bi["bid"]):
					continue
				var m: Array = _metrics(bi, a, ax)
				if not (m[1] > lo and m[0] < hi and float(fb[0]) < m[2] and m[2] < float(fb[1])):
					continue
				done[bi["bid"]] = true
				var base: Dictionary = _own(out, cow, bi["bid"])["parts"][bi["base"]]
				var sgn: float = 1.0 if m[3] else -1.0
				var ref: float
				if ax == 0:
					ref = bi["y0"] if sgn > 0.0 else bi["y1"]
				else:
					ref = bi["x0"] if sgn > 0.0 else bi["x1"]
				var k: int = 1 if ax == 0 else 0
				for p: Array in base["poly"]:
					if absf(float(p[k]) - ref) < float(r["face_tol"]):
						p[k] = float(p[k]) + sgn * step
						moved += 1
				var want: float = (float(r["frontage_min_floors"]) + float(absi(int(bi["key"])) % 3)) * fl + 0.1
				if float(bi["h"]) < want:
					base["h"] = want - float(base["z0"])
					raised += 1
	stats["frontage"] = done.size()
	stats["raised"] = raised
	stats["moved"] = moved
	return out


## `frontage.silhouette` (see `layout.frontage_silhouette`).
static func frontage_silhouette(city: Dictionary, net: Dictionary, route_tops: Dictionary = {}, border_mode: String = "state",
		stats: Dictionary = {}, ctx: Dictionary = {}) -> Dictionary:
	var r: Dictionary = _rules()
	var p: Dictionary = r["silhouette"]
	var min_f: int = int(r["frontage_min_floors"])
	var fl: float = NetrunArtUnits.floor_bu()
	var out: Dictionary = _cow(city)
	var cow: Dictionary = _cow_index(out)
	var bases: Array = NetrunArtLayout.merged_buildings(city)
	var seed: int = ArtSeed.u64_from_str(str(city["layout_seed"]))
	var rp: Array = p["rhythm_p"]
	var rp_sum: float = 0.0
	for x: Variant in rp:
		rp_sum += float(x)
	var done: Dictionary = {}
	var assigned: Dictionary = {}
	var n_set: int = 0
	var index: Dictionary = _index(bases)
	for link: Dictionary in links_of(net, border_mode):
		var legs: Array = legs_of(city, link, ctx)
		for li in range(legs.size() - 1):
			var rows: Dictionary = frontage_rows(bases, legs[li], legs[li + 1], index)
			for side: int in [1, -1]:
				var prev_cls: String = ""
				var run: int = 0
				var prev_f: int = -1
				var have_prev: bool = false
				var hist: Array = []
				for bi: Dictionary in rows[side]:
					var bid: String = bi["bid"]
					if done.has(bid):
						prev_f = assigned[bid]
						have_prev = true
						hist.append(prev_f)
						continue
					done[bid] = true
					var b: Dictionary = (out["buildings"] as Array)[cow["pos"][bid]]
					var u: Array = _draws(seed, "frontage", [bid], 3)
					var top0: float = bi["h"]
					var f0: int = int(top0 / fl)
					var acc: float = 0.0
					var cls: String = RHYTHM[RHYTHM.size() - 1]
					for i in RHYTHM.size():
						acc += float(rp[i])
						if float(u[0]) * rp_sum < acc:
							cls = RHYTHM[i]
							break
					if cls == prev_cls and run >= int(p["rotate_run"]):
						cls = RHYTHM[(RHYTHM.find(cls) + 1 + int(float(u[1]) * 2.0)) % 3]
					var range_f: Array = p["floors_" + cls]
					var f: int = maxi(_randint(float(u[2]), int(range_f[0]), int(range_f[1])), min_f)
					if route_tops.has(bid):
						f = maxi(f, int(route_tops[bid]) + int(p["route_sign_floors"]))
					var stacked: bool = is_stacked(b, bi)
					var floor_min: int = maxi(min_f, f0 if stacked else 0)
					f = maxi(f, floor_min)
					var span: int = int(p["triple_span_min"])
					if hist.size() >= 2:
						var h1: int = hist[hist.size() - 2]
						var h2: int = hist[hist.size() - 1]
						var lo3: int = mini(mini(h1, h2), f)
						var hi3: int = maxi(maxi(h1, h2), f)
						if hi3 - lo3 < span:
							var mean2: float = float(h1 + h2) / 2.0
							var lift: int = mini(h1, h2) + span
							var drop: int = maxi(h1, h2) - span
							var ceil_f: int = int((p["floors_tall"] as Array)[1])
							if float(f) >= mean2 and lift <= ceil_f:
								f = lift
							elif drop >= floor_min:
								f = drop
							elif lift <= ceil_f:
								f = lift
					var step: int = int(p["height_step_min"])
					if have_prev and absi(f - prev_f) < step:
						var down: int = prev_f - step
						var go_down: bool = down >= floor_min and (f < prev_f or prev_f + step > int((p["floors_tall"] as Array)[1]))
						f = down if go_down else prev_f + step
					var want: float = float(f) * fl + 0.1
					var got: int = f0 if stacked else f
					if not stacked and absf(top0 - want) > float(p["base_h_eps"]):
						var base: Dictionary = _own(out, cow, bid)["parts"][bi["base"]]
						base["h"] = want - float(base["z0"])
						n_set += 1
					assigned[bid] = got
					prev_f = got
					have_prev = true
					hist.append(got)
					run = run + 1 if cls == prev_cls else 1
					prev_cls = cls
	stats["silhouette_buildings"] = done.size()
	stats["silhouette_set"] = n_set
	return out


## `[x0, x1, y0, y1, top]` of every HQ stand-in (plan bbox of all parts, top of the highest part), by bid.
static func hq_rects(city: Dictionary) -> Array:
	var hqs: Array = []
	for b: Dictionary in city["buildings"]:
		if bool(b["hq"]) and not (b["parts"] as Array).is_empty():
			hqs.append(b)
	hqs.sort_custom(func(x: Dictionary, y: Dictionary) -> bool: return IdSort.less(x["bid"], y["bid"]))
	var out: Array = []
	for b: Dictionary in hqs:
		var x0: float = INF
		var x1: float = -INF
		var y0: float = INF
		var y1: float = -INF
		var top: float = -INF
		for part: Dictionary in b["parts"]:
			var bb: Array = NetrunArtLayout.poly_bbox(part["poly"])
			x0 = minf(x0, bb[0])
			x1 = maxf(x1, bb[1])
			y0 = minf(y0, bb[2])
			y1 = maxf(y1, bb[3])
			top = maxf(top, float(part["z0"]) + float(part["h"]))
		out.append([x0, x1, y0, y1, top])
	return out


## The top (BU) of the tallest HQ within `reach` BU (plan gap) of building info `bi`, NAN when none is that near.
static func hq_zone_top(hq_list: Array, reach: float, bi: Dictionary) -> float:
	var best: float = NAN
	for r: Array in hq_list:
		var gap: float = maxf(maxf(float(r[0]) - float(bi["x1"]), float(bi["x0"]) - float(r[1])),
			maxf(float(r[2]) - float(bi["y1"]), float(bi["y0"]) - float(r[3])))
		gap = maxf(gap, 0.0)
		if gap <= reach and (is_nan(best) or float(r[4]) > best):
			best = float(r[4])
	return best


## `hq.cap` (see `layout.hq_cap`): no building within `zone_lots` lots of an HQ lot is taller than `cap_k` x the HQ top
## (route columns exempt).
static func hq_cap(city: Dictionary, route_bids: Array = [], stats: Dictionary = {}) -> Dictionary:
	var hp: Dictionary = _rules()["hq"]
	var out: Dictionary = _cow(city)
	var cow: Dictionary = _cow_index(out)
	var hq_list: Array = hq_rects(city)
	var n: int = 0
	if not hq_list.is_empty():
		var reach: float = float(hp["zone_lots"]) * float(city["lot_bu"])
		for bi: Dictionary in NetrunArtLayout.merged_buildings(city):
			var top: float = hq_zone_top(hq_list, reach, bi)
			if is_nan(top) or route_bids.has(bi["bid"]):
				continue
			var cap: float = float(hp["cap_k"]) * top
			if float(bi["h"]) <= cap + 1e-9:
				continue
			n += 1
			var parts: Array = _own(out, cow, bi["bid"])["parts"]
			for j: int in bi["parts"]:
				var part: Dictionary = parts[j]
				part["z0"] = minf(float(part["z0"]), cap - float(hp["clamp_eps"]))
				part["h"] = minf(float(part["h"]), cap - float(part["z0"]))
	stats["hq_capped"] = n
	return out


## `horizon.break` (see `layout.horizon_break`).
static func horizon_break(city: Dictionary, net: Dictionary, route_bids: Array = [], border_mode: String = "state",
		stats: Dictionary = {}, ctx: Dictionary = {}) -> Dictionary:
	var h: Dictionary = _rules()["horizon"]
	var out: Dictionary = _cow(city)
	var links: Array = links_of(net, border_mode)
	if links.is_empty():
		return out
	var legs: Array = legs_of(city, links[0], ctx)
	if legs.size() < 2:
		return out
	var a: Array = legs[0]
	var c: Array = legs[1]
	var ax: int = NetrunArtLayout.leg_axis(a, c)
	var reach: float = _reach()
	var lo: float = minf(float(a[ax]), float(c[ax])) - reach
	var hi: float = maxf(float(a[ax]), float(c[ax])) + reach
	var cow: Dictionary = _cow_index(out)
	var band: Array = h["backdrop_band"]
	var cand: Array = []
	var hq_list: Array = hq_rects(city)
	var reach_hq: float = float(_rules()["hq"]["zone_lots"]) * float(city["lot_bu"])
	for bi: Dictionary in NetrunArtLayout.merged_buildings(city):
		if route_bids.has(bi["bid"]) or is_stacked((out["buildings"] as Array)[cow["pos"][bi["bid"]]], bi) \
				or not is_nan(hq_zone_top(hq_list, reach_hq, bi)):
			continue
		var along: float
		var far: float
		if ax == 0:
			along = (float(bi["x0"]) + float(bi["x1"])) / 2.0
			far = absf((float(bi["y0"]) + float(bi["y1"])) / 2.0 - float(a[1]))
		else:
			along = (float(bi["y0"]) + float(bi["y1"])) / 2.0
			far = absf((float(bi["x0"]) + float(bi["x1"])) / 2.0 - float(a[0]))
		if not (lo <= along and along <= hi and float(band[0]) < far and far < float(band[1])):
			continue
		if minf(float(bi["x1"]) - float(bi["x0"]), float(bi["y1"]) - float(bi["y0"])) < float(h["spike_min_w"]):
			continue
		cand.append({"top": float(bi["h"]), "along": along, "bi": bi})
	var med: float = float(h["default_median"])
	if not cand.is_empty():
		var tops: Array = []
		for e: Dictionary in cand:
			tops.append(e["top"])
		tops.sort_custom(func(x: float, y: float) -> bool: return x < y)
		med = tops[floori(tops.size() / 2.0)]
	var seed: int = ArtSeed.u64_from_str(str(city["layout_seed"]))
	var l0: Dictionary = links[0]
	var n_sp: int = _randint(float(_draws(seed, "spikes", [l0["a"], l0["b"]], 1)[0]), int(h["spikes_min"]), int(h["spikes_max"]))
	for e: Dictionary in cand:
		var bid: String = (e["bi"] as Dictionary)["bid"]
		e["score"] = -(float(e["top"]) + float(_draws(seed, "spike_pick", [bid], 1)[0]) * float(h["pick_jitter"]))
	cand.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		if float(x["score"]) != float(y["score"]):
			return float(x["score"]) < float(y["score"])
		return IdSort.less((x["bi"] as Dictionary)["bid"], (y["bi"] as Dictionary)["bid"]))
	var picked: Array = []
	for e: Dictionary in cand:
		if picked.size() >= n_sp:
			break
		var spaced: bool = true
		for q: Variant in picked:
			if absf(float(e["along"]) - float(q)) < float(h["spike_spacing_bu"]):
				spaced = false
				break
		if spaced:
			picked.append(e["along"])
			var bi: Dictionary = e["bi"]
			var base: Dictionary = _own(out, cow, bi["bid"])["parts"][bi["base"]]
			base["h"] = float(h["spike_k"]) * med - float(base["z0"])
	stats["spikes"] = picked.size()
	return out


## The frontage rows of a leg per side (`1` / `-1`), in order along the leg (ties by bid).
static func frontage_rows(bases: Array, a: Array, c: Array, index: Dictionary = {}) -> Dictionary:
	var fb: Array = NetrunArtConfigData.shipped().layout["front_band"]
	var ax: int = NetrunArtLayout.leg_axis(a, c)
	var reach: float = _reach()
	var lo: float = minf(float(a[ax]), float(c[ax])) - reach
	var hi: float = maxf(float(a[ax]), float(c[ax])) + reach
	var rows: Dictionary = {1: [], -1: []}
	for bi: Dictionary in (bases if index.is_empty() else _near(index, ax, a, lo, hi)):
		var m: Array = _metrics(bi, a, ax)
		if m[1] > lo and m[0] < hi and float(fb[0]) < m[2] and m[2] < float(fb[1]):
			(rows[1 if m[3] else -1] as Array).append({"mid": (m[0] + m[1]) / 2.0, "bi": bi})
	for s: int in [1, -1]:
		var list: Array = rows[s]
		list.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
			if float(x["mid"]) != float(y["mid"]):
				return float(x["mid"]) < float(y["mid"])
			return IdSort.less((x["bi"] as Dictionary)["bid"], (y["bi"] as Dictionary)["bid"]))
		var bis: Array = []
		for e: Dictionary in list:
			bis.append(e["bi"])
		rows[s] = bis
	return rows


## The legs of `link` over street tiles (cached in `ctx` by link ends; `ctx` also holds the routing caches).
static func legs_of(city: Dictionary, link: Dictionary, ctx: Dictionary) -> Array:
	var cache: Dictionary = ctx.get_or_add("legs", {})
	var key: String = "%s|%s" % [link["a"], link["b"]]
	if not cache.has(key):
		cache[key] = NetrunArtLayout.link_legs(city, link["pts"], ctx)
	return cache[key]


## A grid index of building infos by footprint box (`INDEX_BU` cells), for `_near`.
static func _index(bases: Array) -> Dictionary:
	var map: Dictionary = {}
	for bi: Dictionary in bases:
		for i in range(floori(float(bi["x0"]) / INDEX_BU), floori(float(bi["x1"]) / INDEX_BU) + 1):
			for j in range(floori(float(bi["y0"]) / INDEX_BU), floori(float(bi["y1"]) / INDEX_BU) + 1):
				var k := Vector2i(i, j)
				if not map.has(k):
					map[k] = []
				(map[k] as Array).append(bi)
	return map if not map.is_empty() else {"_none": true}


## Buildings whose footprint box meets the strip of a leg on axis `ax` through `a`: along `[lo, hi]`, across the front band
## (a superset of the buildings the exact band test accepts; the callers keep that test). Each building once.
static func _near(index: Dictionary, ax: int, a: Array, lo: float, hi: float) -> Array:
	var fb: Array = NetrunArtConfigData.shipped().layout["front_band"]
	var line: float = float(a[1]) if ax == 0 else float(a[0])
	var p0: float = line - float(fb[1]) - 1.0
	var p1: float = line + float(fb[1]) + 1.0
	var i0: int = floori((lo if ax == 0 else p0) / INDEX_BU)
	var i1: int = floori((hi if ax == 0 else p1) / INDEX_BU)
	var j0: int = floori((p0 if ax == 0 else lo) / INDEX_BU)
	var j1: int = floori((p1 if ax == 0 else hi) / INDEX_BU)
	var seen: Dictionary = {}
	var out: Array = []
	for i in range(i0, i1 + 1):
		for j in range(j0, j1 + 1):
			for bi: Dictionary in index.get(Vector2i(i, j), []):
				if not seen.has(bi["bid"]):
					seen[bi["bid"]] = true
					out.append(bi)
	return out


## True when a part above the base reaches higher than the base.
static func is_stacked(b: Dictionary, bi: Dictionary) -> bool:
	var base: Dictionary = b["parts"][bi["base"]]
	return float(bi["h"]) > float(base["z0"]) + float(base["h"]) + 1e-6


## `[a0, a1, near, positive_side]` of building info `bi` against a leg through `a` on axis `ax`.
static func _metrics(bi: Dictionary, a: Array, ax: int) -> Array:
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
	return [a0, a1, d0 if d0 > 0.0 else d1, d0 > 0.0]


static func _rules() -> Dictionary:
	return NetrunArtConfigData.shipped().layout_rules


static func _reach() -> float:
	var ext: Array = NetrunArtConfigData.shipped().layout["extend"]
	return maxf(float(ext[0]), float(ext[1]))


## A copy of `city` that shares its buildings with it until one is written (`_own`): the passes touch about a quarter of them.
static func _cow(city: Dictionary) -> Dictionary:
	var out: Dictionary = city.duplicate(false)
	out["buildings"] = (city["buildings"] as Array).duplicate(false)
	return out


## The copy-on-write bookkeeping of `out`: bid -> position, and the set of buildings already copied.
static func _cow_index(out: Dictionary) -> Dictionary:
	var pos: Dictionary = {}
	var blds: Array = out["buildings"]
	for i in blds.size():
		pos[(blds[i] as Dictionary)["bid"]] = i
	return {"pos": pos, "owned": {}}


## The building `bid` of `out`, deep-copied the first time it is asked for (safe to write).
static func _own(out: Dictionary, cow: Dictionary, bid: String) -> Dictionary:
	var blds: Array = out["buildings"]
	var i: int = cow["pos"][bid]
	if not (cow["owned"] as Dictionary).has(bid):
		blds[i] = (blds[i] as Dictionary).duplicate(true)
		cow["owned"][bid] = true
	return blds[i]


## The first `n` uniform draws of the art stream (`stream`, `keys`) of `seed`.
static func _draws(seed: int, stream: String, keys: Array, n: int) -> Array:
	var state: int = ArtSeed.derive(seed, stream, keys)
	var out: Array = []
	for i in n:
		var r: Array[int] = ArtSeed.splitmix64(state)
		state = r[0]
		out.append(ArtSeed.uniform(r[1]))
	return out


## Integer in `[lo, hi]` from one uniform draw.
static func _randint(u: float, lo: int, hi: int) -> int:
	return lo + mini(int(floorf(u * float(hi - lo + 1))), hi - lo)
