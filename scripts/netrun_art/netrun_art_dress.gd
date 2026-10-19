class_name NetrunArtDress
extends RefCounted
## NA-24: the GDScript twin of `tools/netrun_art/dress.py` (placement lists of the street dressing, spec 9, 4.1, 13.1). A pure
## function of the street derive v2 and the exporter's city: no Nodes, no global RNG; the per-object streams are the
## splitmix64 draws of `ArtSeed.derive(layout_seed, name, keys)` exactly as the Python (`netrun_art.checks` parity in
## tests/netrun_art/test_na24_dress_parity.gd). The result is the typed lists of `dress_<run>.json` v1 (`DressReader`).

const VERSION := 1
const SIGN_PAL: Array[String] = ["district_a", "district_b"]
const BEAM_PAL: Array[String] = ["district_a", "district_b", "accent_warm", "district_b", "district_a", "accent_cool"]
const GLOW_PAL: Array[String] = ["accent_warm", "district_a", "district_b", "accent_warm", "accent_cool"]
const LAMP_PAL: Array[String] = ["lamp_cool", "lamp_warm"]
## `(cross fraction, direction, palette id)` of the four traffic lanes.
const LANES: Array = [[0.28, 1, "lane_head_a"], [0.62, 1, "lane_head_b"], [-0.3, -1, "lane_tail_a"], [-0.64, -1, "lane_tail_b"]]

## The preset (Python `PRESET`): placement numbers of the dressing, one copy.
const PRESET: Dictionary = {
	"street_width": 8.0,
	"lamp_step": 6.0, "lamp_inset": 0.3, "lamp_z": 1.6, "lamp_skip_margin": 0.15, "lamp_shift_steps": [0.8, 1.6, 2.4],
	"wash_back": 3.5, "wash_z": 0.4, "wash_rise": 0.55,
	"ground_glow_step": 9.0, "ground_glow_depth": 60.0, "ground_glow_p": 0.55, "ground_glow_z": 0.9, "glow_pad": 30.0,
	"glow_jitter_u": 0.8, "glow_jitter_d": 0.6, "plinth_extra": 0.2, "glow_drift": 0.12, "glow_depth_step": 0.8, "glow_depth_from": 2.0,
	"sign_z0": 2.2, "sign_min_top": 4.5, "sign_top_gap": 1.6, "sign_panel": 1.4, "sign_min_panels": 3, "sign_w": 0.8, "sign_in": 0.25,
	"band_inset": 0.4, "band_drop": 0.75, "band_h": 0.32,
	"beams": 6, "beam_rise": 1.35, "beam_min_d": 25.0, "beam_max_d": 170.0, "beam_behind": 12.0, "beam_spacing": 45.0, "beam_up": 0.5,
	"beam_lx": [0.12, 0.30], "beam_ly": [0.18, 0.12], "beam_sweep": [4.5, 1.5], "beam_sweep_on": false,
	"front_far": 18.0, "front_pad": 10.0, "sky_lo": 18.0, "sky_hi": 160.0, "sky_r": 180.0, "sky_q": 0.9, "h_front_default": 14.0,
	"lane_period": 80.0, "lane_pad": 120.0, "lane_z": 0.12, "lane_len": [3.0, 16.0], "lane_bright": [0.5, 1.3], "lane_gap": [4.0, 22.0],
	"t_loop": 4.0, "fog_pad": 10.0, "fog_top_min": 80.0, "fog_sky_k": 2.5,
}


## The typed placement lists of `dress_<run>.json` v1 for a street derive (a new dict). `preset` overrides `PRESET` keys.
static func dress_street(derive: Dictionary, city: Dictionary, preset: Dictionary = {}) -> Dictionary:
	var p: Dictionary = PRESET.duplicate()
	p.merge(preset, true)
	var built: Array = building_tops(city)
	var h: Dictionary = heights(derive, built, p)
	return {"version": VERSION, "run": derive["run"], "layout_seed": derive["layout_seed"], "kind": "street",
		"signs": signs(derive, p), "lamps": lamps(derive, p), "washes": washes(derive, p), "glows": glows(derive, p),
		"beams": beams(derive, built, float(h["h_front"]), p), "streak_lanes": streak_lanes(derive, p),
		"fog_fields": fog_fields(city, float(h["h_sky"]), p)}


static func _stream_seed(layout_seed: String, name: String, keys: Array) -> int:
	return ArtSeed.derive(ArtSeed.u64_from_str(layout_seed), name, keys)


## The next draw of a splitmix64 stream held in `st` (`st[0]` is the state): returns the uniform in [0, 1).
static func _next(st: Array) -> float:
	var r: Array[int] = ArtSeed.splitmix64(int(st[0]))
	st[0] = r[0]
	return ArtSeed.uniform(r[1])


static func _frame(derive: Dictionary) -> Dictionary:
	var a: Array = derive["street"]["a"]
	var c: Array = derive["street"]["c"]
	var ax: int = NetrunArtLayout.leg_axis(a, c)
	var nrm: Array = derive["nrm"]
	var sgn: float = 1.0 if float(c[ax]) > float(a[ax]) else -1.0
	return {"a": a, "c": c, "ax": ax, "sgn": sgn, "nrm": nrm, "length": absf(float(c[ax]) - float(a[ax])), "cline": float(a[1 - ax]),
		"ncross": float(nrm[1]) if ax == 0 else float(nrm[0])}


## World xyz of street coordinate `u` and cross-axis coordinate `cross`.
static func _world(f: Dictionary, u: float, cross: float, z: float) -> Array:
	var along: float = float(f["a"][f["ax"]]) + float(f["sgn"]) * u
	return [along, cross, z] if int(f["ax"]) == 0 else [cross, along, z]


static func _col_less(p: Dictionary, q: Dictionary) -> bool:
	if int(p["layer"]) != int(q["layer"]):
		return int(p["layer"]) < int(q["layer"])
	return IdSort.less(p["bid"], q["bid"])


## Hero blade signs, one per route column, sorted by bid. The `(hero_sign, bid)` stream is reserved (no draws).
static func signs(derive: Dictionary, p: Dictionary) -> Array:
	var f: Dictionary = _frame(derive)
	var cols: Array = (derive["col_info"] as Array).duplicate()
	cols.sort_custom(_col_less)
	var out: Array = []
	for k in cols.size():
		var ci: Dictionary = cols[k]
		var z0: float = float(p["sign_z0"])
		var h: float = maxf(float(p["sign_min_top"]), float(ci["top"]) - float(p["sign_top_gap"])) - z0
		var u: float = float(ci["u0"]) + float(p["sign_in"])
		var cross: float = float(ci["face"]) - float(p["sign_in"]) * float(f["ncross"])
		out.append({"bid": ci["bid"], "layer": int(ci["layer"]), "pos": _world(f, u, cross, z0), "nrm": (f["nrm"] as Array).duplicate(),
			"w": float(p["sign_w"]), "h": h, "panels": maxi(int(p["sign_min_panels"]), int(h / float(p["sign_panel"]))),
			"pal": SIGN_PAL[k % 2], "band_pal": SIGN_PAL[(k + 1) % 2]})
	out.sort_custom(func(x: Dictionary, y: Dictionary) -> bool: return IdSort.less(x["bid"], y["bid"]))
	return out


## Kerb lamps every `lamp_step` BU, both kerbs; cool when the running index `k % 3 == 0`. A lamp in front of a route opening is shifted
## along the street to the nearest clear `u` (candidates +/- `lamp_shift_steps`, + first), dropped when none is clear.
static func lamps(derive: Dictionary, p: Dictionary) -> Array:
	var f: Dictionary = _frame(derive)
	var off: float = float(p["street_width"]) / 2.0 - float(p["lamp_inset"])
	var spans: Dictionary = {-1: [], 1: []}
	var rooms: Dictionary = derive["rooms"]
	var rids: Array = rooms.keys()
	for rid: String in rids:
		var r: Dictionary = rooms[rid]
		var us: Array = []
		for q: Array in r["front"]:
			us.append((float(q[f["ax"]]) - float(f["a"][f["ax"]])) * float(f["sgn"]))
		IdSort.sort_ids(us)
		var bside: int = 1 if float(r["front"][0][1 - int(f["ax"])]) > float(f["cline"]) else -1
		var m: float = float(p["lamp_skip_margin"])
		(spans[bside] as Array).append([float(us[0]) - m, float(us[us.size() - 1]) + m])
	var out: Array = []
	var k := 0
	var u := 0.0
	var steps: Array = [0.0]
	for x: float in p["lamp_shift_steps"]:
		steps.append(x)
		steps.append(-x)
	while u < float(f["length"]):
		for side: int in [-1, 1]:
			var uu: Variant = null
			for d_: float in steps:
				var clear := true
				for sp: Array in spans[side]:
					if float(sp[0]) <= u + d_ and u + d_ <= float(sp[1]):
						clear = false
						break
				if clear:
					uu = u + d_
					break
			if uu != null:
				out.append({"u": float(uu), "side": side, "pos": _world(f, float(uu), float(f["cline"]) + float(side) * off, float(p["lamp_z"])),
					"pal": LAMP_PAL[0] if k % 3 == 0 else LAMP_PAL[1]})
			k += 1
		u += float(p["lamp_step"])
	return out


static func _pos_less(a: Array, b: Array) -> bool:
	for i in a.size():
		if float(a[i]) != float(b[i]):
			return float(a[i]) < float(b[i])
	return false


## One wash spot per route column, palette by the index over the bid order (odd -> district_a).
static func washes(derive: Dictionary, p: Dictionary) -> Array:
	var f: Dictionary = _frame(derive)
	var cols: Dictionary = {}
	var rooms: Dictionary = derive["rooms"]
	var rids: Array = rooms.keys()
	IdSort.sort_ids(rids)
	for rid: String in rids:
		var r: Dictionary = rooms[rid]
		if not cols.has(r["bld"]):
			cols[r["bld"]] = []
		(cols[r["bld"]] as Array).append(r)
	var bids: Array = cols.keys()
	IdSort.sort_ids(bids)
	var out: Array = []
	var nrm: Array = f["nrm"]
	for k in bids.size():
		var bid: String = bids[k]
		var us: Array = []
		for r: Dictionary in cols[bid]:
			for q: Array in r["front"]:
				us.append((float(q[f["ax"]]) - float(f["a"][f["ax"]])) * float(f["sgn"]))
		var lo: float = us[0]
		var hi: float = us[0]
		for v: float in us:
			lo = minf(lo, v)
			hi = maxf(hi, v)
		var face: float = float(cols[bid][0]["front"][0][1 - int(f["ax"])])
		var umid: float = (lo + hi) / 2.0
		var cross: float = face - float(p["wash_back"]) * float(f["ncross"])
		var n: float = sqrt(float(nrm[0]) ** 2 + float(nrm[1]) ** 2 + float(p["wash_rise"]) ** 2)
		out.append({"u": umid, "pos": _world(f, umid, cross, float(p["wash_z"])),
			"dir": [float(nrm[0]) / n, float(nrm[1]) / n, float(p["wash_rise"]) / n], "power": 1.0,
			"pal": "district_a" if k % 2 == 1 else "district_b"})
	out.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		if float(x["u"]) != float(y["u"]):
			return float(x["u"]) < float(y["u"])
		return _pos_less(x["pos"], y["pos"]))
	return out


## Ground glows on a jittered grid; one stream per cell `(ground_glow, i, j)`. Draw order: keep, jitter_u, jitter_d, power,
## colour, drift r, g, b.
static func glows(derive: Dictionary, p: Dictionary) -> Array:
	var f: Dictionary = _frame(derive)
	var step: float = float(p["ground_glow_step"])
	var plinth: float = float(p["street_width"]) / 2.0 + float(p["plinth_extra"])
	var out: Array = []
	var i := 0
	while -float(p["glow_pad"]) + step * i < float(f["length"]) + float(p["glow_pad"]):
		var u: float = -float(p["glow_pad"]) + step * i
		var j := 0
		while plinth + float(p["glow_depth_from"]) + step * float(p["glow_depth_step"]) * j < float(p["ground_glow_depth"]):
			var d: float = plinth + float(p["glow_depth_from"]) + step * float(p["glow_depth_step"]) * j
			var g: Array = [_stream_seed(String(derive["layout_seed"]), "ground_glow", [i, j])]
			if _next(g) <= float(p["ground_glow_p"]):
				var ju: float = (_next(g) - 0.5) * float(p["glow_jitter_u"]) * step
				var jd: float = (_next(g) - 0.5) * float(p["glow_jitter_d"]) * step
				var power: float = 0.5 + 0.5 * _next(g)
				var pal: String = GLOW_PAL[int(_next(g) * GLOW_PAL.size())]
				var drift: Array = []
				for _n in 3:
					drift.append((_next(g) - 0.5) * 2.0 * float(p["glow_drift"]))
				out.append({"cell": [i, j], "pos": _world(f, u + ju, float(f["cline"]) - float(f["ncross"]) * (d + jd), float(p["ground_glow_z"])),
					"power": power, "pal": pal, "drift": drift})
			j += 1
		i += 1
	return out


## `[{bid, c: [x, y], top}]` of every building (whole-building box centre, top of the highest part), sorted by bid.
static func building_tops(city: Dictionary) -> Array:
	var bs: Array = (city["buildings"] as Array).duplicate()
	bs.sort_custom(func(x: Dictionary, y: Dictionary) -> bool: return IdSort.less(x["bid"], y["bid"]))
	var out: Array = []
	for b: Dictionary in bs:
		var x0 := INF
		var x1 := -INF
		var y0 := INF
		var y1 := -INF
		var top := -INF
		for pt: Dictionary in b["parts"]:
			for q: Array in pt["poly"]:
				x0 = minf(x0, float(q[0]))
				x1 = maxf(x1, float(q[0]))
				y0 = minf(y0, float(q[1]))
				y1 = maxf(y1, float(q[1]))
			top = maxf(top, float(pt["z0"]) + float(pt["h"]))
		out.append({"bid": b["bid"], "c": [(x0 + x1) / 2.0, (y0 + y1) / 2.0], "top": top})
	return out


static func _top_less(x: Dictionary, y: Dictionary) -> bool:
	return float(x["top"]) < float(y["top"])


## `h_front` (median roof of the frontage across the street) and `h_sky` (90th percentile roof behind it).
static func heights(derive: Dictionary, built: Array, p: Dictionary) -> Dictionary:
	var f: Dictionary = _frame(derive)
	var a: Array = f["a"]
	var mid: Array = _world(f, float(f["length"]) / 2.0, float(f["cline"]), 0.0)
	var lo: float = minf(float(a[f["ax"]]), float(f["c"][f["ax"]]))
	var hi: float = maxf(float(a[f["ax"]]), float(f["c"][f["ax"]]))
	var fr: Array = []
	var sk: Array = []
	for b: Dictionary in built:
		var c: Array = b["c"]
		var fa: float = (float(c[1]) - float(a[1])) * float(f["nrm"][1]) if int(f["ax"]) == 0 else (float(c[0]) - float(a[0])) * float(f["nrm"][0])
		if fa > 0.0 and fa < float(p["front_far"]) and lo - float(p["front_pad"]) < float(c[f["ax"]]) and float(c[f["ax"]]) < hi + float(p["front_pad"]):
			fr.append(float(b["top"]))
		if fa > float(p["sky_lo"]) and fa < float(p["sky_hi"]) and Vector2(float(c[0]) - float(mid[0]), float(c[1]) - float(mid[1])).length() < float(p["sky_r"]):
			sk.append(float(b["top"]))
	IdSort.sort_ids(fr)
	IdSort.sort_ids(sk)
	var h_front: float = float(fr[fr.size() / 2]) if not fr.is_empty() else float(p["h_front_default"])
	var h_sky: float = float(sk[int(float(sk.size()) * float(p["sky_q"]))]) if not sk.is_empty() else 2.2 * h_front
	return {"h_front": h_front, "h_sky": h_sky}


## The K tallest non-route roofs that clear the frontage by `beam_rise` x H_FRONT; stream `(beams, bid)`.
static func beams(derive: Dictionary, built: Array, h_front: float, p: Dictionary) -> Array:
	var f: Dictionary = _frame(derive)
	var mid: Array = _world(f, float(f["length"]) / 2.0, float(f["cline"]), 0.0)
	var a: Array = f["a"]
	var route: Array = derive["route_keys"]
	var cands: Array = []
	for b: Dictionary in built:
		if route.has(b["bid"]) or float(b["top"]) < float(p["beam_rise"]) * h_front:
			continue
		var c: Array = b["c"]
		var d: float = Vector2(float(c[0]) - float(mid[0]), float(c[1]) - float(mid[1])).length()
		var fa: float = (float(c[1]) - float(mid[1])) * float(f["nrm"][1]) if int(f["ax"]) == 0 else (float(c[0]) - float(a[0])) * float(f["nrm"][0])
		if float(p["beam_min_d"]) < d and d < float(p["beam_max_d"]) and fa > float(p["beam_behind"]):
			cands.append(b)
	cands.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		if float(x["top"]) != float(y["top"]):
			return float(x["top"]) > float(y["top"])
		return IdSort.less(x["bid"], y["bid"]))
	var pick: Array = []
	for b: Dictionary in cands:
		var ok := true
		for q: Dictionary in pick:
			if Vector2(float(b["c"][0]) - float(q["c"][0]), float(b["c"][1]) - float(q["c"][1])).length() <= float(p["beam_spacing"]):
				ok = false
				break
		if ok:
			pick.append(b)
		if pick.size() >= int(p["beams"]):
			break
	var out: Array = []
	for k in pick.size():
		var b: Dictionary = pick[k]
		var g: Array = [_stream_seed(String(derive["layout_seed"]), "beams", [b["bid"]])]
		var lx: float = float(p["beam_lx"][0]) + float(p["beam_lx"][1]) * _next(g)
		var ly: float = float(p["beam_ly"][0]) + float(p["beam_ly"][1]) * _next(g)
		var sweep: float = float(p["beam_sweep"][0]) + float(p["beam_sweep"][1]) * _next(g)
		var phase: float = _next(g)
		lx = lx if float(b["c"][0]) > float(mid[0]) else -lx
		ly = ly if int(f["ax"]) == 0 else 0.0
		out.append({"bid": b["bid"], "pos": [b["c"][0], b["c"][1], float(b["top"]) + float(p["beam_up"])],
			"lean": [rad_to_deg(atan(lx)), rad_to_deg(atan(ly))], "sweep_deg": sweep if bool(p["beam_sweep_on"]) else 0.0,
			"phase": phase, "pal": BEAM_PAL[k % BEAM_PAL.size()]})
	out.sort_custom(func(x: Dictionary, y: Dictionary) -> bool: return IdSort.less(x["bid"], y["bid"]))
	return out


## Four traffic lanes; stream `(street_lanes, lane_id)`; per streak draws: length, brightness, gap. The lane length is
## `L = k * speed * T` (T the 4 s loop).
static func streak_lanes(derive: Dictionary, p: Dictionary) -> Array:
	var f: Dictionary = _frame(derive)
	var half: float = float(p["street_width"]) / 2.0
	var cycle: float = float(p["lane_period"])
	var k: int = maxi(1, int(ceilf((float(f["length"]) + 2.0 * float(p["lane_pad"])) / cycle)))
	var L: float = float(k) * cycle
	var u_lo: float = -(L - float(f["length"])) / 2.0
	var out: Array = []
	for lane_id in LANES.size():
		var spec: Array = LANES[lane_id]
		var g: Array = [_stream_seed(String(derive["layout_seed"]), "street_lanes", [lane_id])]
		var cross: float = float(f["cline"]) + float(spec[0]) * half
		var streaks: Array = []
		var x := 0.0
		while x < L:
			var ln: float = float(p["lane_len"][0]) + (float(p["lane_len"][1]) - float(p["lane_len"][0])) * _next(g)
			var br: float = float(p["lane_bright"][0]) + (float(p["lane_bright"][1]) - float(p["lane_bright"][0])) * _next(g)
			var gap: float = float(p["lane_gap"][0]) + (float(p["lane_gap"][1]) - float(p["lane_gap"][0])) * _next(g)
			streaks.append({"u0": x, "len": ln, "gap": gap, "bright": br})
			x += ln + gap
		var a_pt: Array = _world(f, u_lo, cross, float(p["lane_z"])).slice(0, 2)
		var b_pt: Array = _world(f, u_lo + L, cross, float(p["lane_z"])).slice(0, 2)
		if int(spec[1]) < 0:
			var t: Array = a_pt
			a_pt = b_pt
			b_pt = t
		out.append({"lane_id": lane_id, "a": a_pt, "b": b_pt, "z": float(p["lane_z"]), "speed": cycle / float(p["t_loop"]),
			"pal": spec[2], "streaks": streaks})
	return out


## One fog box over the city extent (padded), from ground to `max(fog_top_min, 2.5 * H_SKY)`.
static func fog_fields(city: Dictionary, h_sky: float, p: Dictionary) -> Array:
	var x0 := INF
	var x1 := -INF
	var y0 := INF
	var y1 := -INF
	for b: Dictionary in city["buildings"]:
		for pt: Dictionary in b["parts"]:
			for q: Array in pt["poly"]:
				x0 = minf(x0, float(q[0]))
				x1 = maxf(x1, float(q[0]))
				y0 = minf(y0, float(q[1]))
				y1 = maxf(y1, float(q[1]))
	var top: float = maxf(float(p["fog_top_min"]), float(p["fog_sky_k"]) * h_sky)
	var pad: float = float(p["fog_pad"])
	return [{"id": "city", "min": [x0 - pad, y0 - pad, 0.0], "max": [x1 + pad, y1 + pad, top], "density": 1.0}]
