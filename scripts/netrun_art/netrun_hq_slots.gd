class_name NetrunHqSlots
extends RefCounted
## HQ slot generator for any run graph: a stepped square landmark, one tier per layer, rooms on its faces (spiral).
## Functions that can fail return `{"error": "<message>"}` (the Python `SlotError`).

## Outward face normals N, E, S, W.
const FACES: Array = [[0, 1], [1, 0], [0, -1], [-1, 0]]
## Camera-direction dot products closer than this tie (a corner overview ties two faces exactly).
const ENTRANCE_EPS := 1e-9


## The slot parameters (copy of config `slot_params`).
static func slot_params() -> Dictionary:
	return NetrunArtConfigData.shipped().slot_params.duplicate(true)


## `[x0, x1, y0, y1]` plan BU of `city.hqs[corp]` (`[i, j, w, h]` in lots).
static func hq_lot_rect(city: Dictionary, corp: String) -> Array:
	var h: Array = city["hqs"][corp]
	var i: float = float(h[0])
	var j: float = float(h[1])
	var w: float = float(h[2])
	var hh: float = float(h[3])
	var ol: Array = city["origin_lot"]
	var lb: float = float(city["lot_bu"])
	var o0: float = float(ol[0])
	var o1: float = float(ol[1])
	return [(i - o0) * lb, (i + w - o0) * lb, -(j + hh - o1) * lb, -(j - o1) * lb]


## The stepped landmark: centre, tier half sizes and base heights. Returns `{"error"}` when the lot is too small.
static func plan_compound(rect: Array, n_tiers: int, params_over: Dictionary = {}) -> Dictionary:
	var p: Dictionary = NetrunArtUnits.merge(slot_params(), params_over)
	var cx: float = (float(rect[0]) + float(rect[1])) / 2
	var cy: float = (float(rect[2]) + float(rect[3])) / 2
	var base: float = minf(float(rect[1]) - float(rect[0]), float(rect[3]) - float(rect[2])) / 2 - float(p["lot_margin"])
	var top: float = maxf(float(p["min_half"]), base * float(p["top_share"]))
	if base < top:
		return {"error": "lot too small for the landmark"}
	var hs: Array = []
	var denom: float = float(maxi(1, n_tiers - 1))
	for t in n_tiers:
		hs.append(base - (base - top) * float(t) / denom)
	var tier_h: float = float(p["tier_floors"]) * NetrunArtUnits.floor_bu()
	var z0: Array = []
	for t in n_tiers:
		z0.append(float(t) * tier_h)
	return {"centre": [cx, cy], "half": hs, "tier_h": tier_h, "z0": z0, "rect": rect.duplicate()}


## Adds `entrance` ([x, y, z]) and `entry_nrm` ([nx, ny]) to `comp` (mutates and returns it); placeholder face pick, config landmark entry overrides.
static func set_entrance(comp: Dictionary, overview: NetrunPose, corp: String = "") -> Dictionary:
	var cx: float = comp["centre"][0]
	var cy: float = comp["centre"][1]
	var ov: Array = overview.dir()
	var cam: Array = [-ov[0], -ov[1]]
	var best_d: float = 0.0
	var best_k: int = -1
	for k in FACES.size():
		var n0: Array = FACES[k]
		var d: float = n0[0] * cam[0] + n0[1] * cam[1]
		if best_k < 0 or d > best_d + ENTRANCE_EPS:
			best_d = d
			best_k = k
	var n: Array = FACES[best_k]
	var h: float = comp["half"][0]
	comp["entrance"] = [cx + n[0] * h, cy + n[1] * h, 0.0]
	comp["entry_nrm"] = [float(n[0]), float(n[1])]
	var entries: Dictionary = NetrunArtConfigData.shipped().landmark_entries
	if corp != "" and entries.has(corp):
		var hook: Dictionary = entries[corp]
		if not hook.is_empty():
			var e: Array = hook["entry"]
			comp["entrance"] = [cx + float(e[0]), cy + float(e[1]), float(e[2])]
			var nn: Array = []
			for v: Variant in hook["entry_nrm"]:
				nn.append(float(v))
			comp["entry_nrm"] = nn
	return comp


static func _quad(c: Array, n: Array, s0: float, s1: float, z0: float, z1: float, off: float) -> Array:
	var t: Array = [-n[1], n[0]]
	var px: float = c[0] + n[0] * off
	var py: float = c[1] + n[1] * off
	return [[px + t[0] * s0, py + t[1] * s0, z0], [px + t[0] * s1, py + t[1] * s1, z0],
		[px + t[0] * s1, py + t[1] * s1, z1], [px + t[0] * s0, py + t[1] * s0, z1]]


## `{node id: room}` for every node of the graph (derive v2 room shape, `bld` = the HQ bid); `{"error"}` when it cannot be placed.
static func place_slots(run_graph: Dictionary, rect: Array, hq_bid: String, n_parts: int = 1, params_over: Dictionary = {}) -> Dictionary:
	var p: Dictionary = NetrunArtUnits.merge(slot_params(), params_over)
	var layers: Array = NetrunStreetDeriver.layer_nodes(run_graph)
	var comp: Dictionary = plan_compound(rect, layers.size(), p)
	if comp.has("error"):
		return comp
	var cx: float = comp["centre"][0]
	var cy: float = comp["centre"][1]
	var inset: float = NetrunStreetDeriver.rules()["room_z_inset"]
	var fbu: float = NetrunArtUnits.floor_bu()
	var tier_floors: int = int(p["tier_floors"])
	var rooms: Dictionary = {}
	for t in layers.size():
		var layer: int = layers[t][0]
		var nodes: Array = layers[t][1]
		var hs: float = comp["half"][t]
		var length: float = 2 * hs - 2 * float(p["corner_pad"])
		if length <= 0.0:
			return {"error": "tier too small"}
		var face_of: Array = []
		var count: Dictionary = {0: 0, 1: 0, 2: 0, 3: 0}
		var seen: Dictionary = {0: 0, 1: 0, 2: 0, 3: 0}
		for k in nodes.size():
			var fk: int = (t + k) % 4
			face_of.append(fk)
			count[fk] += 1
		var flr: int = t * tier_floors
		var z0: float = float(flr) * fbu + inset
		var z1: float = float(flr + 1) * fbu - inset
		for k in nodes.size():
			var nd: Dictionary = nodes[k]
			var f: int = face_of[k]
			var c: int = count[f]
			var seg: float = length / float(c)
			var w: float = minf(float(p["room_w_max"]), float(p["room_fill"]) * seg)
			var mid: float = -length / 2 + (float(seen[f]) + 0.5) * seg
			seen[f] += 1
			var n: Array = FACES[f]
			rooms[nd["id"]] = {
				"front": _quad([cx, cy], n, mid - w / 2, mid + w / 2, z0, z1, hs),
				"back": _quad([cx, cy], n, mid - w / 2, mid + w / 2, z0, z1, hs - float(p["room_depth"])),
				"floor": flr, "span": 1, "ground_z": 0.0, "bld": hq_bid,
				"parts": [mini(t, maxi(0, n_parts - 1))], "layer": layer, "kind": nd["type"]}
	return rooms


## Axis-aligned box `[x0, x1, y0, y1, z0, z1]` of a room (front and back corners).
static func room_slot_box(room: Dictionary) -> Array:
	var pts: Array = []
	pts.append_array(room["front"])
	pts.append_array(room["back"])
	var q0: Array = pts[0]
	var mnx: float = q0[0]
	var mxx: float = q0[0]
	var mny: float = q0[1]
	var mxy: float = q0[1]
	var mnz: float = q0[2]
	var mxz: float = q0[2]
	for q: Array in pts:
		mnx = minf(mnx, q[0])
		mxx = maxf(mxx, q[0])
		mny = minf(mny, q[1])
		mxy = maxf(mxy, q[1])
		mnz = minf(mnz, q[2])
		mxz = maxf(mxz, q[2])
	return [mnx, mxx, mny, mxy, mnz, mxz]


## Pairs `[id_a, id_b]` of rooms whose boxes intersect (open interiors), sorted by id.
static func overlaps(rooms: Dictionary) -> Array:
	var ids: Array = rooms.keys()
	IdSort.sort_ids(ids)
	var boxes: Dictionary = {}
	for i: String in ids:
		boxes[i] = room_slot_box(rooms[i])
	var bad: Array = []
	for x in ids.size():
		for y in range(x + 1, ids.size()):
			var a: Array = boxes[ids[x]]
			var b: Array = boxes[ids[y]]
			var all_ok: bool = true
			for k in 3:
				if not (a[2 * k] < b[2 * k + 1] - 1e-9 and b[2 * k] < a[2 * k + 1] - 1e-9):
					all_ok = false
					break
			if all_ok:
				bad.append([ids[x], ids[y]])
	return bad


## True when every room corner lies inside the lot rectangle.
static func inside_rect(room: Dictionary, rect: Array) -> bool:
	var pts: Array = []
	pts.append_array(room["front"])
	pts.append_array(room["back"])
	for q: Array in pts:
		if not (rect[0] <= q[0] and q[0] <= rect[1] and rect[2] <= q[1] and q[1] <= rect[3]):
			return false
	return true


static func _out(r: Dictionary, link_out: float) -> Array:
	var f: Array = r["front"]
	var bk: Array = r["back"]
	var c: Array = []
	var b: Array = []
	for k in 3:
		var sf: float = 0.0
		var sb: float = 0.0
		for q: Array in f:
			sf += q[k]
		for q: Array in bk:
			sb += q[k]
		c.append(sf / 4)
		b.append(sb / 4)
	var n: Array = [c[0] - b[0], c[1] - b[1]]
	var ln: float = NetrunArtUnits.hypot(n[0], n[1])
	if ln == 0.0:
		ln = 1.0
	n = [n[0] / ln, n[1] / ln]
	return [c, [c[0] + n[0] * link_out, c[1] + n[1] * link_out, c[2]], n]


static func _edge_less(p: Dictionary, q: Dictionary) -> bool:
	var pa: String = String(p["a"])
	var qa: String = String(q["a"])
	if pa != qa:
		return pa < qa
	return String(p["b"]) < String(q["b"])


## `"hq"` links: from the front centre of room a out `link_out` along its face normal, across, into room b.
static func link_paths(rooms: Dictionary, edges: Array, params_over: Dictionary = {}) -> Array:
	var p: Dictionary = NetrunArtUnits.merge(slot_params(), params_over)
	var lo: float = float(p["link_out"])
	var es: Array = edges.duplicate()
	es.sort_custom(_edge_less)
	var res: Array = []
	for e: Dictionary in es:
		var oa: Array = _out(rooms[e["a"]], lo)
		var ob: Array = _out(rooms[e["b"]], lo)
		res.append({"a": e["a"], "b": e["b"], "type": "hq", "path": [oa[0], oa[1], ob[1], ob[0]]})
	return res


## A derive v2 dict with `kind: "hq"` for the corp's HQ lot; `{"error"}` when the graph cannot be placed.
static func derive_hq(city: Dictionary, run_graph: Dictionary, corp: String, partial: Dictionary = {}, params_over: Dictionary = {}, rig_over: Dictionary = {}) -> Dictionary:
	var rect: Array = hq_lot_rect(city, corp)
	var bid: String = "hq:" + corp
	var n_parts: int = 1
	for b: Dictionary in city["buildings"]:
		if b["bid"] == bid:
			n_parts = (b["parts"] as Array).size()
			break
	var rooms: Dictionary = place_slots(run_graph, rect, bid, n_parts, params_over)
	if rooms.has("error"):
		return rooms
	var layers: Array = NetrunStreetDeriver.layer_nodes(run_graph)
	var comp: Dictionary = plan_compound(rect, layers.size(), params_over)
	if comp.has("error"):
		return comp
	var first: Array = []
	for nd: Dictionary in layers[0][1]:
		first.append(nd["id"])
	var ov: NetrunPose = NetrunHqOrbit.hq_overview(rooms, comp, first, "", rig_over)
	set_entrance(comp, ov, corp)
	var dec: NetrunPose = NetrunHqOrbit.hq_decision(rooms, "", first, 0, layers.size(), rig_over, comp["entrance"])
	var base: Dictionary
	if not partial.is_empty():
		base = partial.duplicate(true)
	else:
		base = NetrunArtDeriver.game_partial(city["layout_seed"], run_graph.get("run", "run"), "hq", [corp])
	base["version"] = NetrunArtDeriver.VERSION
	base["kind"] = "hq"
	for k: String in ["street", "nrm", "start_left"]:
		base.erase(k)
	base["span"] = 1
	base["route_keys"] = [bid]
	base["rooms"] = rooms
	base["edges"] = link_paths(rooms, run_graph["edges"], params_over)
	base["overview"] = ov.to_json()
	base["decision"] = dec.to_json()
	return base
