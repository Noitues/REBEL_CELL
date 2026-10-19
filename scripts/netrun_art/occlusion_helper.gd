class_name OcclusionHelper
extends RefCounted
## NA-21 twin of `tools/netrun_art/occlusion.py`: the camera-rig occlusion rule (spec 7.1-7.4), pure and cheap.

## Depth knots of the cone.
const NK := 5
## Tolerance when selecting the points at or beyond a knot depth.
const KNOT_EPS := 1e-6


## The 28 `occ_*` key names (the shader's `KEYS`).
static func keys() -> Array:
	var out: Array = ["occ_on", "occ_cx", "occ_cy", "occ_cz", "occ_ux", "occ_uy", "occ_tsoft", "occ_a0", "occ_amax",
		"occ_vsoft", "occ_stub", "occ_ghost", "occ_edge"]
	for c: String in ["t", "T", "v"]:
		for k in NK:
			out.append("occ_%s%d" % [c, k])
	return out


## The per-frame cone of the target volume as the flat `occ_*` keys; `cfg["occ"]` may override the OCC numbers.
static func occlusion_params(cam: Array, pts: Array, cfg: Dictionary = {}) -> Dictionary:
	var oc: Dictionary = NetrunArtConfigData.shipped().occlusion
	var o: Dictionary = {}
	for k: String in ["cone_margin", "stub", "ghost", "edge", "tsoft", "vsoft"]:
		o[k] = oc[k]
	if cfg.has("occ") and cfg["occ"] is Dictionary:
		var ov: Dictionary = cfg["occ"]
		for k: Variant in ov:
			o[k] = ov[k]
	var min_span: float = oc["min_span"]
	var cx: float = cam[0]
	var cy: float = cam[1]
	var cz: float = cam[2]
	var sx := 0.0
	var sy := 0.0
	for p: Array in pts:
		sx += p[0]
	for p: Array in pts:
		sy += p[1]
	var ox: float = sx / float(pts.size())
	var oy: float = sy / float(pts.size())
	var ll: float = NetrunArtUnits.hypot(ox - cx, oy - cy)
	if ll == 0.0:
		ll = 1.0
	var ux: float = (ox - cx) / ll
	var uy: float = (oy - cy) / ll
	var tt: Array = []
	var vv: Array = []
	var al_list: Array = []
	for p: Array in pts:
		var al: float = maxf((p[0] - cx) * ux + (p[1] - cy) * uy, 1.0)
		var la: float = (p[1] - cy) * ux - (p[0] - cx) * uy
		tt.append(la / al)
		vv.append((p[2] - cz) / al)
		al_list.append(al)
	var cm: float = o["cone_margin"]
	var msp_t: float = cm * maxf(float(tt.max()) - float(tt.min()), min_span)
	var msp_v: float = cm * maxf(float(vv.max()) - float(vv.min()), min_span)
	var a0: float = al_list.min()
	var a1: float = al_list.max()
	var out: Dictionary = {"occ_on": true, "occ_cx": cx, "occ_cy": cy, "occ_cz": cz, "occ_ux": ux, "occ_uy": uy,
		"occ_tsoft": o["tsoft"], "occ_a0": a0, "occ_amax": a1, "occ_vsoft": o["vsoft"], "occ_stub": o["stub"],
		"occ_ghost": o["ghost"], "occ_edge": o["edge"]}
	for k in NK:
		var ak: float = a0 + (a1 - a0) * float(k) / float(NK - 1)
		var sub: Array = []
		for j in al_list.size():
			if float(al_list[j]) >= ak - KNOT_EPS:
				sub.append(j)
		if sub.is_empty():
			sub = [al_list.find(a1)]
		var tmin: float = tt[sub[0]]
		var tmax: float = tt[sub[0]]
		var vmin: float = vv[sub[0]]
		for j: int in sub:
			tmin = minf(tmin, tt[j])
			tmax = maxf(tmax, tt[j])
			vmin = minf(vmin, vv[j])
		out["occ_t%d" % k] = tmin - msp_t
		out["occ_T%d" % k] = tmax + msp_t
		out["occ_v%d" % k] = vmin - msp_v
	return out


static func _knot(p: Dictionary, key: String, a: float) -> float:
	var a0: float = p["occ_a0"]
	var f: float = (a - a0) / maxf(float(p["occ_amax"]) - a0, 1.0) * float(NK - 1)
	f = maxf(0.0, minf(float(NK - 1), f))
	var v: float = p["occ_%s0" % key]
	for k in range(1, NK):
		v += maxf(0.0, minf(1.0, f - float(k - 1))) * (float(p["occ_%s%d" % [key, k]]) - float(p["occ_%s%d" % [key, k - 1]]))
	return v


static func _sstep(x: float, w: float) -> float:
	return NetrunArtUnits.smoothstep01(x / maxf(w, 1e-4))


static func _blocks(p: Dictionary, z: float, al: float, r: float, vmin: float) -> float:
	return _sstep((z - float(p["occ_cz"])) / maxf(al + r, 1.0) - vmin, p["occ_vsoft"])


## `[cut_height, opacity]` of one building `b = [x, y, top, hx, hy]` under the frame params `p`.
static func occlusion_state(p: Dictionary, b: Array) -> Array:
	var oc: Dictionary = NetrunArtConfigData.shipped().occlusion
	var front_fade: float = NetrunArtUnits.kit(oc["front_fade_kit"])
	var clutter: float = NetrunArtUnits.kit(oc["clutter_kit"])
	var x: float = b[0]
	var y: float = b[1]
	var top: float = b[2]
	var hx: float = b[3]
	var hy: float = b[4]
	var r: float = maxf(NetrunArtUnits.hypot(hx, hy), 0.5)
	var dx: float = x - float(p["occ_cx"])
	var dy: float = y - float(p["occ_cy"])
	var al: float = dx * float(p["occ_ux"]) + dy * float(p["occ_uy"])
	var la: float = dy * float(p["occ_ux"]) - dx * float(p["occ_uy"])
	var alc: float = maxf(al, 1.0)
	var tmin: float = _knot(p, "t", al - r)
	var tmax: float = _knot(p, "T", al - r)
	var vmin: float = _knot(p, "v", al - r)
	var lat: float = _sstep((la + r) / alc - tmin, p["occ_tsoft"]) * _sstep(tmax - (la - r) / alc, p["occ_tsoft"])
	var front: float = (1.0 if al > 0.0 else 0.0) * _sstep(float(p["occ_amax"]) - (al - r), front_fade)
	var fc: float = (1.0 if p["occ_on"] else 0.0) * lat * front * _blocks(p, top, al, r, vmin)
	var stub: float = minf(p["occ_stub"], top)
	var zc: float = stub + (1.0 - fc) * (top + clutter - stub)
	var g: float = fc * _blocks(p, stub, al, r, vmin)
	return [minf(zc, top), 1.0 - g * (1.0 - float(p["occ_ghost"]))]


static func _bid_less(a: Dictionary, b: Dictionary) -> bool:
	return String(a["bid"]) < String(b["bid"])


## Rows `{bid, box: [x, y, top, hx, hy]}` of the city buildings (whole-building box over all parts), sorted by bid.
static func building_boxes(city: Dictionary, skip: Dictionary = {}) -> Array:
	var out: Array = []
	var bs: Array = (city["buildings"] as Array).duplicate()
	bs.sort_custom(_bid_less)
	for b: Dictionary in bs:
		if not skip.is_empty() and skip.has(b["bid"]):
			continue
		var xs: Array = []
		var ys: Array = []
		var top: float = -INF
		for pt: Dictionary in b["parts"]:
			for p: Array in pt["poly"]:
				xs.append(float(p[0]))
				ys.append(float(p[1]))
			top = maxf(top, float(pt["z0"]) + float(pt["h"]))
		var x0: float = xs.min()
		var x1: float = xs.max()
		var y0: float = ys.min()
		var y1: float = ys.max()
		out.append({"bid": b["bid"], "box": [(x0 + x1) / 2.0, (y0 + y1) / 2.0, top, (x1 - x0) / 2.0, (y1 - y0) / 2.0]})
	return out


## `{params, buildings, unaffected}`: only buildings with a cut or a ghost are listed.
static func occlusion_block(params: Dictionary, boxes: Array, eps: float = 1e-4) -> Dictionary:
	var rows: Array = []
	for bx: Dictionary in boxes:
		var st: Array = occlusion_state(params, bx["box"])
		var cut: float = st[0]
		var op: float = st[1]
		if cut < float(bx["box"][2]) - eps or op < 1.0 - eps:
			rows.append({"bid": bx["bid"], "cut_height": cut, "opacity": op})
	return {"params": params, "buildings": rows, "unaffected": boxes.size() - rows.size()}


## Corridor segments `[ax, ay, bx, by, half]` from consecutive `rail.pts`, `half = rail.half_clear`.
static func rail_segments(rail: Dictionary) -> Array:
	var pts: Array = rail["pts"]
	var out: Array = []
	for i in range(pts.size() - 1):
		var a: Array = pts[i]
		var b: Array = pts[i + 1]
		out.append([a[0], a[1], b[0], b[1], rail["half_clear"]])
	return out


static func _seg_point_dist(ax: float, ay: float, bx: float, by: float, x: float, y: float) -> float:
	var vx: float = bx - ax
	var vy: float = by - ay
	var l2: float = vx * vx + vy * vy
	if l2 == 0.0:
		l2 = 1.0
	var t: float = maxf(0.0, minf(1.0, ((x - ax) * vx + (y - ay) * vy) / l2))
	return NetrunArtUnits.hypot(x - ax - vx * t, y - ay - vy * t)


## Distance from `(x, y)` to the nearest corridor axis (INF without corridors).
static func corridor_dist(segs: Array, x: float, y: float) -> float:
	var best: float = INF
	for s: Array in segs:
		best = minf(best, _seg_point_dist(s[0], s[1], s[2], s[3], x, y))
	return best


## True when the box meets a corridor segment (0.5 BU samples along each segment).
static func in_corridor(segs: Array, x0: float, y0: float, x1: float, y1: float) -> bool:
	for s: Array in segs:
		var ax: float = s[0]
		var ay: float = s[1]
		var bx: float = s[2]
		var by: float = s[3]
		var hw: float = s[4]
		var n: int = maxi(1, int(NetrunArtUnits.hypot(bx - ax, by - ay) / 0.5) + 1)
		for k in range(n + 1):
			var px: float = ax + (bx - ax) * float(k) / float(n)
			var py: float = ay + (by - ay) * float(k) / float(n)
			var dx: float = maxf(maxf(x0 - px, 0.0), px - x1)
			var dy: float = maxf(maxf(y0 - py, 0.0), py - y1)
			if NetrunArtUnits.hypot(dx, dy) < hw:
				return true
	return false


## Height cap beside the rail: within `side_d` of the polyline a top is limited to `side_cap`; `[h, capped]`.
static func rail_cap(rail: Dictionary, x: float, y: float, h: float) -> Array:
	if corridor_dist(rail_segments(rail), x, y) > float(rail["side_d"]) or h <= float(rail["side_cap"]):
		return [h, false]
	return [rail["side_cap"], true]


## Ids (sorted) of the route rooms the DECISION cone must cover (art-pass 6d214ce9, NA-04c): every room whose front quad
## projects fully in front of the camera with its centre inside the `ref_w` x `ref_h` frame and, when `hq_visible` is set
## (HQ), facing the camera (`NetrunHqOrbit.visible_room`).
## A street netrun (`street_facing`) uses `room_faces_camera` instead.
static func rooms_in_frame(rooms: Dictionary, pose: NetrunPose, ref_w: float, ref_h: float, hq_visible: bool = false,
		street_facing: bool = false) -> Array:
	var ids: Array = rooms.keys()
	IdSort.sort_ids(ids)
	var out: Array = []
	for rid: String in ids:
		var r: Dictionary = rooms[rid]
		var gz: float = r.get("ground_z", 0.0)
		var sx := 0.0
		var sy := 0.0
		var ok := true
		for c: Array in r["front"]:
			var q: Array = pose.proj([c[0], c[1], c[2] + gz])
			if q.is_empty():
				ok = false
				break
			sx += q[0]
			sy += q[1]
		if not ok:
			continue
		var n: float = float((r["front"] as Array).size())
		var cx: float = sx / n
		var cy: float = sy / n
		if not (cx >= 0.0 and cx <= ref_w and cy >= 0.0 and cy <= ref_h):
			continue
		if hq_visible and not NetrunHqOrbit.visible_room(r, pose):
			continue
		if street_facing and not room_faces_camera(r, pose):
			continue
		out.append(rid)
	return out


## True when the room's outward normal points toward the camera (street netruns; an HQ uses `visible_room`).
static func room_faces_camera(room: Dictionary, pose: NetrunPose) -> bool:
	var loc: Array = pose.loc()
	var n: Array = NetrunHqOrbit.room_normal(room)
	var sx := 0.0
	var sy := 0.0
	for q: Array in room["front"]:
		sx += q[0]
		sy += q[1]
	var cnt: float = float((room["front"] as Array).size())
	return n[0] * (loc[0] - sx / cnt) + n[1] * (loc[1] - sy / cnt) > 0.0


static func _band_point_ok(p: Array, nrm: Array, pose: NetrunPose, ref_w: float, ref_h: float) -> bool:
	var loc: Array = pose.loc()
	if nrm[0] * (loc[0] - p[0]) + nrm[1] * (loc[1] - p[1]) <= 0.0:
		return false
	var q: Array = pose.proj(p)
	return not q.is_empty() and q[0] >= 0.0 and q[0] <= ref_w and q[1] >= 0.0 and q[1] <= ref_h


## One representative room (lowest id) per distinct level key, sorted by key (`street` keys are [bld, floor, span],
## HQ keys the tier `layer`).
static func _band_levels(rooms: Dictionary, ids: Array, street: bool) -> Array:
	var sorted_ids: Array = ids.duplicate()
	IdSort.sort_ids(sorted_ids)
	var seen: Dictionary = {}
	var keys: Array = []
	for i: String in sorted_ids:
		var r: Dictionary = rooms[i]
		var k: Array = [r["bld"], int(r["floor"]), int(r["span"])] if street else [int(r["layer"])]
		var ks: String = "|".join(k.map(func(v: Variant) -> String: return str(v)))
		if not seen.has(ks):
			seen[ks] = r
			keys.append(k)
	keys.sort_custom(_band_key_less)
	var out: Array = []
	for k: Array in keys:
		out.append(seen["|".join(k.map(func(v: Variant) -> String: return str(v)))])
	return out


static func _band_key_less(a: Array, b: Array) -> bool:
	for j in a.size():
		if a[j] != b[j]:
			return a[j] < b[j]
	return false


static func _front_z_range(r: Dictionary) -> Array:
	var z0 := INF
	var z1 := -INF
	for q: Array in r["front"]:
		z0 = minf(z0, float(q[2]))
		z1 = maxf(z1, float(q[2]))
	var gz: float = r.get("ground_z", 0.0)
	return [z0 + gz, z1 + gz]


## Where the ray from the origin at `angle_rad` leaves the closed CCW polyline `outline` (the farthest crossing; twin of
## `outline_hit`): `[x, y, nx, ny]` (unit outward normal of the hit segment), or `[]` when the ray misses.
static func outline_hit(outline: Array, angle_rad: float) -> Array:
	var dx: float = cos(angle_rad)
	var dy: float = sin(angle_rad)
	var best: Array = []
	var best_t := 0.0
	var n: int = outline.size()
	for i in n:
		var a: Array = outline[i]
		var b: Array = outline[(i + 1) % n]
		var ax: float = a[0]
		var ay: float = a[1]
		var ex: float = float(b[0]) - ax
		var ey: float = float(b[1]) - ay
		var den: float = dx * ey - dy * ex
		if absf(den) < 1e-12:
			continue
		var t: float = (ax * ey - ay * ex) / den
		var u: float = (ax * dy - ay * dx) / den
		if t > best_t + 1e-12 and u >= -1e-9 and u <= 1.0 + 1e-9:
			var ln: float = NetrunArtUnits.hypot(ex, ey)
			if ln == 0.0:
				ln = 1.0
			best_t = t
			best = [dx * t, dy * t, ey / ln, -ex / ln]
	return best


## Face band of the HQ's current level (spec 7.1 rule 1; twin of `hq_band_points`): per tier of the rooms `ids`, points
## every `hq_step_deg` around `centre`, at floor and room-top height, facing the camera and inside the frame. They lie on
## the landmark's face `outline` (relative to `centre`, closed CCW) when it is not empty, else on the tier's square face.
## `step_deg` <= 0 = config.
static func hq_band_points(rooms: Dictionary, ids: Array, centre: Array, pose: NetrunPose, ref_w: float, ref_h: float,
		step_deg: float = 0.0, outline: Array = []) -> Array:
	var st: float = step_deg if step_deg > 0.0 else float(NetrunArtConfigData.shipped().occlusion["hq_step_deg"])
	var out: Array = []
	for r: Dictionary in _band_levels(rooms, ids, false):
		var n: Array = NetrunHqOrbit.room_normal(r)
		var fx := 0.0
		var fy := 0.0
		for q: Array in r["front"]:
			fx += q[0]
			fy += q[1]
		var cnt: float = float((r["front"] as Array).size())
		var hs: float = (fx / cnt - centre[0]) * n[0] + (fy / cnt - centre[1]) * n[1]
		var zr: Array = _front_z_range(r)
		for k in int(360.0 / st):
			var a: float = deg_to_rad(float(k) * st)
			if not outline.is_empty():
				var hit: Array = outline_hit(outline, a)
				if hit.is_empty():
					continue
				for z: float in zr:
					var hp: Array = [centre[0] + hit[0], centre[1] + hit[1], z]
					if _band_point_ok(hp, [hit[2], hit[3]], pose, ref_w, ref_h):
						out.append(hp)
				continue
			var ca: float = cos(a)
			var sa: float = sin(a)
			var s: float = hs / maxf(absf(ca), absf(sa))
			var nrm: Array
			if absf(ca) >= absf(sa):
				nrm = [1.0 if ca > 0.0 else -1.0, 0.0]
			else:
				nrm = [0.0, 1.0 if sa > 0.0 else -1.0]
			for z: float in zr:
				var p: Array = [centre[0] + s * ca, centre[1] + s * sa, z]
				if _band_point_ok(p, nrm, pose, ref_w, ref_h):
					out.append(p)
	return out


## Face band of the route building(s) holding the rooms `ids` (twin of `street_band_points`): points along the face every
## `street_step_bu`, at floor and room-top height of each (building, floor, span) level. `extents[bid] = [x0, x1, y0, y1]`.
static func street_band_points(rooms: Dictionary, ids: Array, extents: Dictionary, pose: NetrunPose, ref_w: float,
		ref_h: float, step_bu: float = 0.0) -> Array:
	var st: float = step_bu if step_bu > 0.0 else float(NetrunArtConfigData.shipped().occlusion["street_step_bu"])
	var out: Array = []
	for r: Dictionary in _band_levels(rooms, ids, true):
		var n: Array = NetrunHqOrbit.room_normal(r)
		var f: Array = r["front"]
		var zr: Array = _front_z_range(r)
		var ex: Array = extents[r["bld"]]
		var along_x: bool = absf(float(f[0][1]) - float(f[1][1])) < 1e-9
		var lo: float = ex[0] if along_x else ex[2]
		var hi: float = ex[1] if along_x else ex[3]
		for k in int((hi - lo) / st) + 1:
			var u: float = lo + float(k) * st
			for z: float in zr:
				var p: Array = [u, f[0][1], z] if along_x else [f[0][0], u, z]
				if _band_point_ok(p, n, pose, ref_w, ref_h):
					out.append(p)
	return out


## `[x0, x1, y0, y1]` bounding box over all parts of the city building `bid`.
static func building_extent(city: Dictionary, bid: String) -> Array:
	for b: Dictionary in city["buildings"]:
		if b["bid"] == bid:
			var xs: Array = []
			var ys: Array = []
			for pt: Dictionary in b["parts"]:
				for p: Array in pt["poly"]:
					xs.append(float(p[0]))
					ys.append(float(p[1]))
			return [xs.min(), xs.max(), ys.min(), ys.max()]
	return []
