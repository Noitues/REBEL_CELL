class_name NetrunStreetDeriver
extends RefCounted
## NA-21 twin of `tools/netrun_art/derive/street.py`: the netrun street derived from the city map.
## Python `DeriveError` becomes `{"error": message}` (callers test `has("error")`).

## Room kinds a node may carry.
const ROOM_KINDS: Array = ["router", "terminal", "mainframe", "server_rack", "rest", "workshop", "cache"]
## Link types (`hq` is reserved for landmark links).
const LINK_TYPES: Array = ["facade"]
## Local ground height under a room (city.json v1 has no terrain).
const GROUND_Z_DEFAULT := 0.0


## The street rules (Python `RULES`): config street_rules + floor_bu + front_band, extend from layout.
static func rules() -> Dictionary:
	var cfg: NetrunArtConfigData = NetrunArtConfigData.shipped()
	var out: Dictionary = {}
	out["front_band"] = (cfg.layout["front_band"] as Array).duplicate()
	out["floor_bu"] = NetrunArtUnits.floor_bu()
	for k: Variant in cfg.street_rules:
		out[k] = cfg.street_rules[k]
	out["extend"] = (cfg.layout["extend"] as Array).duplicate()
	return out


static func _rl(rules_over: Dictionary) -> Dictionary:
	if rules_over.is_empty():
		return rules()
	return rules_over


## Usable floors of a frontage building (on a tapered one only while the setback stays small).
static func floors(b: Dictionary, rules_over: Dictionary = {}) -> int:
	var r: Dictionary = _rl(rules_over)
	var fbu: float = float(r["floor_bu"])
	var h: float = float(b["h"])
	var ts: float = float(b["ts"])
	var n: int = int(h / fbu)
	if ts >= 0.99:
		return n
	var depth: float
	if int(b.get("axis", 0)) == 0:
		depth = float(b["y1"]) - float(b["y0"])
	else:
		depth = float(b["x1"]) - float(b["x0"])
	var k: int = 0
	var max_setback: float = float(r["max_setback"])
	while k < n:
		var z: float = (k + 1) * fbu
		if (1.0 - ts) * depth / 2.0 * z / h > max_setback:
			break
		k += 1
	return k


## Buildings fronting the leg a -> c on `side` (+1 = left), ordered by `(along, bid)`.
static func frontage(B: Array, a: Array, c: Array, side: int, rules_over: Dictionary = {}) -> Array:
	var r: Dictionary = _rl(rules_over)
	var ax: int = NetrunArtLayout.leg_axis(a, c)
	var d: int = 1 if float(c[ax]) > float(a[ax]) else -1
	var lo: float = minf(float(a[ax]), float(c[ax]))
	var hi: float = maxf(float(a[ax]), float(c[ax]))
	var nrm: Array
	if ax == 0:
		nrm = [0.0, float(side * d)]
	else:
		nrm = [float(-side * d), 0.0]
	var band: Array = r["front_band"]
	var min_width: float = float(r["min_width"])
	var out: Array = []
	for b: Dictionary in B:
		var a0: float
		var a1: float
		var near: float
		var dist: float
		if ax == 0:
			a0 = float(b["x0"])
			a1 = float(b["x1"])
			near = float(b["y0"]) if float(nrm[1]) > 0.0 else float(b["y1"])
			dist = (near - float(a[1])) * float(nrm[1])
		else:
			a0 = float(b["y0"])
			a1 = float(b["y1"])
			near = float(b["x0"]) if float(nrm[0]) > 0.0 else float(b["x1"])
			dist = (near - float(a[0])) * float(nrm[0])
		if a1 > lo and a0 < hi and float(band[0]) < dist and dist < float(band[1]) and a1 - a0 >= min_width:
			var q: Dictionary = b.duplicate()
			q["along"] = ((a0 + a1) / 2.0 - float(a[ax])) * d
			q["face"] = near
			q["nrm"] = nrm.duplicate()
			q["axis"] = ax
			q["dirn"] = d
			out.append(q)
	out.sort_custom(_front_less)
	return out


static func _front_less(p: Dictionary, q: Dictionary) -> bool:
	if float(p["along"]) != float(q["along"]):
		return float(p["along"]) < float(q["along"])
	return String(p["bid"]) < String(q["bid"])


static func _node_less(p: Dictionary, q: Dictionary) -> bool:
	if int(p["index"]) != int(q["index"]):
		return int(p["index"]) < int(q["index"])
	return String(p["id"]) < String(q["id"])


## `[[layer, nodes sorted by index]]` in layer order.
static func layer_nodes(run_graph: Dictionary) -> Array:
	var by: Dictionary = {}
	for n: Dictionary in run_graph["nodes"]:
		var l: int = int(n["layer"])
		if not by.has(l):
			by[l] = []
		(by[l] as Array).append(n)
	var keys: Array = by.keys()
	keys.sort()
	var out: Array = []
	for l: int in keys:
		var nodes: Array = (by[l] as Array).duplicate()
		nodes.sort_custom(_node_less)
		out.append([l, nodes])
	return out


## Layer -> frontage building in link order, skipping a building without the floors; `[out, ok]`.
static func assign(front: Array, layers: Array, span: int = 1, rules_over: Dictionary = {}) -> Array:
	var r: Dictionary = _rl(rules_over)
	var out: Array = []
	var k: int = 0
	var base_floor: int = int(r["base_floor"])
	for item: Array in layers:
		var rooms: Array = item[1]
		var need: int = base_floor + rooms.size() * span
		while k < front.size() and floors(front[k], r) < need:
			k += 1
		if k >= front.size():
			return [out, false]
		out.append([item[0], front[k]])
		k += 1
	return [out, true]


## The leg + side whose frontage fits best; empty Dictionary when none, else score/li/side/a/c/front/asg/ok/start_left.
static func choose_street(B: Array, legs: Array, layers: Array, rules_over: Dictionary = {}) -> Dictionary:
	var r: Dictionary = _rl(rules_over)
	var best: Dictionary = {}
	var e: Array = r["extend"]
	for li in range(legs.size() - 1):
		var a0: Array = legs[li]
		var c0: Array = legs[li + 1]
		var L: float = NetrunArtUnits.hypot(float(c0[0]) - float(a0[0]), float(c0[1]) - float(a0[1]))
		if L < 1e-9:
			continue
		var ux: float = (float(c0[0]) - float(a0[0])) / L
		var uy: float = (float(c0[1]) - float(a0[1])) / L
		var a: Array = [float(a0[0]) - ux * float(e[0]), float(a0[1]) - uy * float(e[0])]
		var c: Array = [float(c0[0]) + ux * float(e[1]), float(c0[1]) + uy * float(e[1])]
		for side: int in [1, -1]:
			var fr: Array = frontage(B, a, c, side, r)
			var res: Array = assign(fr, layers, 1, r)
			var asg: Array = res[0]
			var ok: bool = res[1]
			var nfl: int = 0
			for it: Array in asg:
				nfl += floors(it[1], r)
			var nrm: Array = fr[0]["nrm"] if not fr.is_empty() else [0.0, 1.0]
			var right: Array = [nrm[1], -float(nrm[0])]
			var start_left: bool = ((float(c[0]) - float(a[0])) * float(right[0]) + (float(c[1]) - float(a[1])) * float(right[1])) > 0.0
			var score: Array = [asg.size(), nfl, 1 if start_left else 0]
			if best.is_empty() or _score_gt(score, best["score"]):
				best = {"score": score, "li": li, "side": side, "a": a, "c": c, "front": fr, "asg": asg, "ok": ok,
					"start_left": start_left}
	return best


static func _score_gt(s: Array, t: Array) -> bool:
	for i in 3:
		if int(s[i]) != int(t[i]):
			return int(s[i]) > int(t[i])
	return false


## `legs` with every slanted leg replaced by an L (dominant axis first); axis-aligned legs are kept (Python `square_legs`).
static func square_legs(legs: Array) -> Array:
	var tol: float = float(NetrunArtConfigData.shipped().layout["axis_tol"])
	var out: Array = [(legs[0] as Array).duplicate()]
	for i in range(legs.size() - 1):
		var p: Array = legs[i]
		var q: Array = legs[i + 1]
		var dx: float = absf(float(q[0]) - float(p[0]))
		var dy: float = absf(float(q[1]) - float(p[1]))
		if dx >= tol and dy >= tol:
			if dx >= dy:
				out.append([q[0], p[1]])
			else:
				out.append([p[0], q[1]])
		out.append(q.duplicate())
	return out


static func _fits(best: Dictionary) -> bool:
	return not best.is_empty() and not (best["front"] as Array).is_empty() and bool(best["ok"])


## `[best, step]`: `choose_street`, then, only when it does not fit every layer, the same on the squared legs (step 1).
## A street that fits at step 0 is never changed. When neither fits the step 0 result is returned with step 0.
static func choose_street_fitting(B: Array, legs: Array, layers: Array, rules_over: Dictionary = {}) -> Array:
	var r: Dictionary = _rl(rules_over)
	var first: Dictionary = choose_street(B, legs, layers, r)
	if _fits(first):
		return [first, 0]
	var sq: Array = square_legs(legs)
	if sq != legs:
		var best: Dictionary = choose_street(B, sq, layers, r)
		if _fits(best):
			return [best, 1]
	return [first, 0]


static func _link_less(p: Dictionary, q: Dictionary) -> bool:
	if String(p["a"]) != String(q["a"]):
		return String(p["a"]) < String(q["a"])
	return String(p["b"]) < String(q["b"])


## The Site's border link (or any link at the Site) and its points from the relay end. Returns `{"error"}` without a link.
static func select_link(net: Dictionary, site: String) -> Dictionary:
	var links: Array = (net["links"] as Array).duplicate()
	links.sort_custom(_link_less)
	var mine: Array = []
	for l: Dictionary in links:
		if String(l["a"]) == site or String(l["b"]) == site:
			mine.append(l)
	if mine.is_empty():
		return {"error": "site %s has no link" % site}
	var border: Dictionary = {}
	for bl: Dictionary in NetrunArtLayout.border_links(net):
		border[String(bl["a"]) + "|" + String(bl["b"])] = true
	var link: Dictionary = mine[0]
	for l: Dictionary in mine:
		if border.has(String(l["a"]) + "|" + String(l["b"])):
			link = l
			break
	var pts: Array = []
	for p: Array in link["pts"]:
		pts.append(p.duplicate())
	if String(link["a"]) == site:
		pts.reverse()
	return {"link": link, "pts": pts}


## `{node id: room}` in the concept corner order; heights above `ground_z`.
static func room_boxes(asg: Array, layers: Array, span: int, rules_over: Dictionary = {}, ground_z: float = GROUND_Z_DEFAULT) -> Dictionary:
	var r: Dictionary = _rl(rules_over)
	var nodes: Dictionary = {}
	for item: Array in layers:
		nodes[int(item[0])] = item[1]
	var base_floor: int = int(r["base_floor"])
	var fbu: float = float(r["floor_bu"])
	var inset: float = float(r["room_inset"])
	var zin: float = float(r["room_z_inset"])
	var depth: float = float(r["room_depth"])
	var rooms: Dictionary = {}
	for item: Array in asg:
		var l: int = int(item[0])
		var b: Dictionary = item[1]
		var ax: int = int(b["axis"])
		var nrm: Array = b["nrm"]
		var layer_list: Array = nodes[l]
		var span_l: int = span if floors(b, r) >= base_floor + layer_list.size() * span else 1
		var lo: float
		var hi: float
		if ax == 0:
			lo = float(b["x0"])
			hi = float(b["x1"])
		else:
			lo = float(b["y0"])
			hi = float(b["y1"])
		var u0: float = lo + inset
		var u1: float = hi - inset
		for k in layer_list.size():
			var n: Dictionary = layer_list[k]
			var f: int = base_floor + k * span_l
			var z0: float = f * fbu + zin
			var z1: float = (f + span_l) * fbu - zin
			var face: float = float(b["face"])
			var back: float = face + depth * (float(nrm[1]) if ax == 0 else float(nrm[0]))
			var fr: Array
			var bk: Array
			if ax == 0:
				fr = [[u0, face, z0], [u1, face, z0], [u1, face, z1], [u0, face, z1]]
				bk = [[u0, back, z0], [u1, back, z0], [u1, back, z1], [u0, back, z1]]
			else:
				fr = [[face, u0, z0], [face, u1, z0], [face, u1, z1], [face, u0, z1]]
				bk = [[back, u0, z0], [back, u1, z0], [back, u1, z1], [back, u0, z1]]
			rooms[n["id"]] = {"front": fr, "back": bk, "floor": f, "span": span_l, "ground_z": ground_z,
				"bld": b["bid"], "parts": (b["parts"] as Array).duplicate(), "layer": l, "kind": n["type"]}
	return rooms


static func _p(ax: int, face: float, u: float, z: float) -> Array:
	if ax == 0:
		return [u, face, z]
	return [face, u, z]


## Facade links: out of room a, across at the mid point, into room b, on a plane in front of the faces.
static func link_paths(rooms: Dictionary, edges: Array, rules_over: Dictionary = {}) -> Array:
	var r: Dictionary = _rl(rules_over)
	var offset: float = float(r["link_offset"])
	var stub: float = float(r["link_stub"])
	var sorted_edges: Array = edges.duplicate()
	sorted_edges.sort_custom(_link_less)
	var out: Array = []
	for e: Dictionary in sorted_edges:
		var ra: Dictionary = rooms[e["a"]]
		var rb: Dictionary = rooms[e["b"]]
		var fa: Array = ra["front"]
		var fb: Array = rb["front"]
		var ax: int = 0 if absf(float(fa[0][1]) - float(fa[1][1])) < 1e-6 else 1
		var nrm_s: float = 1.0 if float(ra["back"][0][1 - ax]) > float(fa[0][1 - ax]) else -1.0
		var face: float
		if nrm_s > 0.0:
			face = minf(float(fa[0][1 - ax]), float(fb[0][1 - ax]))
		else:
			face = maxf(float(fa[0][1 - ax]), float(fb[0][1 - ax]))
		face = face - offset * nrm_s
		var ua: Array = []
		var ub: Array = []
		for p: Array in fa:
			ua.append(float(p[ax]))
		for p: Array in fb:
			ub.append(float(p[ax]))
		var dirn: float = 1.0 if NetrunArtUnits.sum_f(ub) > NetrunArtUnits.sum_f(ua) else -1.0
		var xa: float = float(ua.max()) if dirn > 0.0 else float(ua.min())
		var xb: float = float(ub.min()) if dirn > 0.0 else float(ub.max())
		var za: float = (float(fa[0][2]) + float(fa[2][2])) / 2.0
		var zb: float = (float(fb[0][2]) + float(fb[2][2])) / 2.0
		var xm: float = (xa + xb) / 2.0
		out.append({"a": e["a"], "b": e["b"], "type": "facade",
			"path": [_p(ax, face, xa - dirn * stub, za), _p(ax, face, xm, za), _p(ax, face, xm, zb),
				_p(ax, face, xb + dirn * stub, zb)]})
	return out


## Reorder a quad to BL, BR, TR, TL seen from the street (camera looks along `nrm`).
static func normalise_quad(q: Array, nrm: Array) -> Array:
	var right: Array = [nrm[1], -float(nrm[0])]
	var du: float = (float(q[1][0]) - float(q[0][0])) * float(right[0]) + (float(q[1][1]) - float(q[0][1])) * float(right[1])
	if du >= 0.0:
		var same: Array = []
		for p: Array in q:
			same.append(p.duplicate())
		return same
	return [(q[1] as Array).duplicate(), (q[0] as Array).duplicate(), (q[3] as Array).duplicate(), (q[2] as Array).duplicate()]


static func _span_poses(rooms: Dictionary, layers: Array, nrm: Array, start_left: bool, rig_over: Dictionary,
		entry: Array = []) -> Array:
	var ov: NetrunPose = NetrunCameraRig.street_overview(rooms, nrm, start_left, rig_over)
	var first: Array = []
	for n: Dictionary in layers[0][1]:
		first.append(n["id"])
	var dec: NetrunPose = NetrunCameraRig.street_decision(rooms, "", first, 0.0, nrm, start_left, rig_over, entry)
	return [ov, dec]


## Projected height in px (1920 x 1080 frame) of a room's front edge in pose `ov`; -1.0 when the edge is not visible.
static func room_px(ov: NetrunPose, room: Dictionary) -> float:
	var c: Array = NetrunCameraRig.room_corners(room)
	var p0: Array = ov.proj(c[0])
	var p3: Array = ov.proj(c[3])
	if p0.is_empty() or p3.is_empty():
		return -1.0
	var rg: Dictionary = NetrunArtConfigData.shipped().rig
	var ref_w: float = rg["ref_w"]
	var ref_h: float = rg["ref_h"]
	for p: Array in [p0, p3]:
		if float(p[0]) < 0.0 or float(p[0]) > ref_w or float(p[1]) < 0.0 or float(p[1]) > ref_h:
			return -1.0
	return absf(float(p0[1]) - float(p3[1]))


## One row per candidate span 1..span_max: `{span, min_px, fallback}` (Python `span_scan`). `min_px` is the smallest visible
## route-room height in the OVERVIEW pose over the rooms that hold the span (0.0 with none); `fallback` the layers whose
## building cannot fit the span (sorted).
static func span_scan(asg: Array, layers: Array, nrm: Array, start_left: bool, rules_over: Dictionary,
		rig_over: Dictionary = {}) -> Array:
	var rows: Array = []
	for span in range(1, int(rules_over["span_max"]) + 1):
		var rooms: Dictionary = room_boxes(asg, layers, span, rules_over)
		var ov: NetrunPose = NetrunCameraRig.street_overview(rooms, nrm, start_left, rig_over)
		var min_px := -1.0
		var fb: Array = []
		var ids: Array = rooms.keys()
		IdSort.sort_ids(ids)
		for rid: String in ids:
			var rm: Dictionary = rooms[rid]
			if int(rm["span"]) == span:
				var q: float = room_px(ov, rm)
				if q >= 0.0 and (min_px < 0.0 or q < min_px):
					min_px = q
			elif not fb.has(int(rm["layer"])):
				fb.append(int(rm["layer"]))
		fb.sort()
		rows.append({"span": span, "min_px": maxf(min_px, 0.0), "fallback": fb})
	return rows


## The smallest span whose smallest visible route room in the OVERVIEW pose reaches `room_px_target` (NA-23b); when none up to
## `span_max` does, the span with the largest smallest room (the lower span on a tie).
static func choose_span(asg: Array, layers: Array, nrm: Array, start_left: bool, rules_over: Dictionary = {},
		rig_over: Dictionary = {}) -> int:
	var r: Dictionary = _rl(rules_over)
	var rows: Array = span_scan(asg, layers, nrm, start_left, r, rig_over)
	for row: Dictionary in rows:
		if float(row["min_px"]) >= float(r["room_px_target"]):
			return int(row["span"])
	var best: Dictionary = rows[0]
	for row: Dictionary in rows:
		if float(row["min_px"]) > float(best["min_px"]):
			best = row
	return int(best["span"])


## The whole street derivation: a derive v2 dict (`kind: "street"`). Returns `{"error": msg}` when the frontage runs out.
static func derive_street(city: Dictionary, net: Dictionary, run_graph: Dictionary, site: String, partial: Dictionary = {},
		rules_over: Dictionary = {}, rig_over: Dictionary = {}) -> Dictionary:
	var r: Dictionary = NetrunArtUnits.merge(rules(), rules_over)
	var layers: Array = layer_nodes(run_graph)
	var sl: Dictionary = select_link(net, site)
	if sl.has("error"):
		return sl
	var legs: Array = NetrunArtLayout.link_legs(city, sl["pts"])
	var B: Array = NetrunArtLayout.merged_buildings(city)
	var best: Dictionary = (choose_street_fitting(B, legs, layers, r) as Array)[0]
	if best.is_empty() or (best["front"] as Array).is_empty():
		return {"error": "no frontage along the link of " + site}
	var li: int = best["li"]
	var side: int = best["side"]
	var a: Array = best["a"]
	var c: Array = best["c"]
	var fr: Array = best["front"]
	var asg: Array = best["asg"]
	var start_left: bool = best["start_left"]
	if not bool(best["ok"]):
		return {"error": "frontage runs out: %d of %d layers assigned on leg %d side %d" % [asg.size(), layers.size(), li, side]}
	var nrm: Array = fr[0]["nrm"]
	var span: int = choose_span(asg, layers, nrm, start_left, r, rig_over)
	var rooms: Dictionary = room_boxes(asg, layers, span, r)
	var poses: Array = _span_poses(rooms, layers, nrm, start_left, rig_over, [a[0], a[1], 0.0])
	var ov: NetrunPose = poses[0]
	var dec: NetrunPose = poses[1]
	var edges: Array = link_paths(rooms, run_graph["edges"], r)
	var ax: int = NetrunArtLayout.leg_axis(a, c)
	var sgn: float = 1.0 if float(c[ax]) > float(a[ax]) else -1.0
	var col_info: Array = []
	for item: Array in asg:
		var b: Dictionary = item[1]
		var lo: float
		var hi: float
		if int(b["axis"]) == 0:
			lo = float(b["x0"])
			hi = float(b["x1"])
		else:
			lo = float(b["y0"])
			hi = float(b["y1"])
		var ua: float = (lo - float(a[ax])) * sgn
		var ub: float = (hi - float(a[ax])) * sgn
		col_info.append({"layer": item[0], "bid": b["bid"], "top": b["h"], "u0": minf(ua, ub), "u1": maxf(ua, ub),
			"face": b["face"]})
	var out_rooms: Dictionary = {}
	var ids: Array = rooms.keys()
	IdSort.sort_ids(ids)
	for rid: String in ids:
		var rm: Dictionary = (rooms[rid] as Dictionary).duplicate()
		rm["front"] = normalise_quad(rm["front"], nrm)
		rm["back"] = normalise_quad(rm["back"], nrm)
		out_rooms[rid] = rm
	for e: Dictionary in edges:
		var np: Array = []
		for p: Array in e["path"]:
			np.append(p.duplicate())
		e["path"] = np
	var base: Dictionary
	if not partial.is_empty():
		base = partial.duplicate()
	else:
		base = NetrunArtDeriver.game_partial(str(city["layout_seed"]), str(run_graph.get("run", "run")), "street")
	base["version"] = NetrunArtDeriver.VERSION
	base["kind"] = "street"
	var columns: Array = []
	var route_keys: Array = []
	for item: Array in asg:
		columns.append([item[0], item[1]["bid"]])
		route_keys.append(item[1]["bid"])
	var front_rows: Array = []
	for b: Dictionary in fr:
		front_rows.append([b["bid"], roundf(float(b["h"]) * 10.0) / 10.0, floors(b, r), roundf(float(b["ts"]) * 100.0) / 100.0])
	base["street"] = {"a": a.duplicate(), "c": c.duplicate()}
	base["nrm"] = nrm.duplicate()
	base["start_left"] = start_left
	base["span"] = span
	base["columns"] = columns
	base["route_keys"] = route_keys
	base["col_info"] = col_info
	base["rooms"] = out_rooms
	base["edges"] = edges
	base["overview"] = ov.to_json()
	base["decision"] = dec.to_json()
	base["frontage"] = front_rows
	return base
