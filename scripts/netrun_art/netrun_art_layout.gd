class_name NetrunArtLayout
extends RefCounted
## NA-21 twin of `tools/netrun_art/layout.py`: city.json / net.json helpers (lots, base parts, border links, street routing).
## `apply_layout_rules` and the r2 height passes live in `NetrunArtLayoutRules` (NA-11). Plan coordinates are BU `[x, y]`.

## Link states that count as open.
const OPEN_STATES: Array = ["open", "opened"]
## Node states that count as owned.
const OWN_STATES: Array = ["core", "owned"]
## Node states that count as corporate.
const CORP_STATES: Array = ["corporate", "taken"]
## 4-connected BFS steps `(di, dj)`.
const BFS_STEPS: Array = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]


## Plan BU `[x, y]` of a lot point (`layout36.W`).
static func lot_to_plan(lot: Array, origin_lot: Array, lot_bu: float) -> Array:
	return [(float(lot[0]) - float(origin_lot[0])) * lot_bu, -(float(lot[1]) - float(origin_lot[1])) * lot_bu]


## Lot point of a plan BU point (`layout36.lots`).
static func plan_to_lot(p: Array, origin_lot: Array, lot_bu: float) -> Array:
	return [float(p[0]) / lot_bu + float(origin_lot[0]), float(origin_lot[1]) - float(p[1]) / lot_bu]


## `[x0, x1, y0, y1]` of a polygon.
static func poly_bbox(poly: Array) -> Array:
	var x0: float = float(poly[0][0])
	var x1: float = x0
	var y0: float = float(poly[0][1])
	var y1: float = y0
	for p: Array in poly:
		x0 = minf(x0, float(p[0]))
		x1 = maxf(x1, float(p[0]))
		y0 = minf(y0, float(p[1]))
		y1 = maxf(y1, float(p[1]))
	return [x0, x1, y0, y1]


## Index of the street-level base part (z0 <= base_tol, largest footprint box, lowest index), or -1 for None.
static func base_part_index(b: Dictionary) -> int:
	var base_tol: float = float(NetrunArtConfigData.shipped().layout["base_tol"])
	var best_i: int = -1
	var best_k: float = 0.0
	var parts: Array = b["parts"]
	for i in parts.size():
		var p: Dictionary = parts[i]
		if float(p["z0"]) > base_tol:
			continue
		var bb: Array = poly_bbox(p["poly"])
		var k: float = -(bb[1] - bb[0]) * (bb[3] - bb[2])
		if best_i == -1 or k < best_k:
			best_k = k
			best_i = i
	return best_i


## The building as the game reads it (base box, top of highest part, tier indices); empty Dictionary when no part is on street level.
static func building_info(b: Dictionary) -> Dictionary:
	var base_tol: float = float(NetrunArtConfigData.shipped().layout["base_tol"])
	var bi: int = base_part_index(b)
	if bi == -1:
		return {}
	var parts: Array = b["parts"]
	var base: Dictionary = parts[bi]
	var bb: Array = poly_bbox(base["poly"])
	var x0: float = bb[0]
	var x1: float = bb[1]
	var y0: float = bb[2]
	var y1: float = bb[3]
	var members: Array = [bi]
	for j in parts.size():
		var p: Dictionary = parts[j]
		if j == bi or float(p["z0"]) <= base_tol:
			continue
		var pb: Array = poly_bbox(p["poly"])
		var cx: float = (pb[0] + pb[1]) / 2.0
		var cy: float = (pb[2] + pb[3]) / 2.0
		if x0 <= cx and cx <= x1 and y0 <= cy and cy <= y1:
			members.append(j)
	var top: float = 0.0
	var first: bool = true
	for j: int in members:
		var t: float = float(parts[j]["z0"]) + float(parts[j]["h"])
		if first or t > top:
			top = t
			first = false
	members.sort()
	return {"bid": b["bid"], "key": b["key"], "hq": bool(b["hq"]), "base": bi, "x0": x0, "x1": x1, "y0": y0, "y1": y1,
		"z0": base["z0"], "h": top, "ts": base["taper"], "parts": members}


## `building_info` of every street-level building, sorted by `bid`; HQ stand-ins only when `include_hq`.
static func merged_buildings(city: Dictionary, include_hq: bool = false) -> Array:
	var blds: Array = (city["buildings"] as Array).duplicate()
	blds.sort_custom(func(p: Dictionary, q: Dictionary) -> bool: return String(p["bid"]) < String(q["bid"]))
	var out: Array = []
	for b: Dictionary in blds:
		if bool(b["hq"]) and not include_hq:
			continue
		var bi: Dictionary = building_info(b)
		if not bi.is_empty():
			out.append(bi)
	return out


## Border links (O-D): open or opened, one end core/owned, the other corporate/taken. Sorted by `(a, b)`.
static func border_links(net: Dictionary) -> Array:
	var st: Dictionary = {}
	for n: Dictionary in net["nodes"]:
		st[n["id"]] = n["state"]
	var links: Array = (net["links"] as Array).duplicate()
	links.sort_custom(func(p: Dictionary, q: Dictionary) -> bool:
		if String(p["a"]) != String(q["a"]):
			return String(p["a"]) < String(q["a"])
		return String(p["b"]) < String(q["b"]))
	var out: Array = []
	for l: Dictionary in links:
		if not OPEN_STATES.has(l["state"]):
			continue
		var sa: Variant = st.get(l["a"], null)
		var sb: Variant = st.get(l["b"], null)
		if (OWN_STATES.has(sa) and CORP_STATES.has(sb)) or (OWN_STATES.has(sb) and CORP_STATES.has(sa)):
			out.append(l)
	return out


## Set (Dictionary cell -> true) of `Vector2i` street lot cells.
static func street_cells(city: Dictionary) -> Dictionary:
	var out: Dictionary = {}
	for s: Dictionary in city["streets"]:
		out[Vector2i(int(s["lot"][0]), int(s["lot"][1]))] = true
	return out


## `[turns still to make, next tile]` from tile `c` having arrived with step `d` (null at start); memoised.
static func _best(c: Vector2i, d: Variant, goal: Vector2i, dist: Dictionary, memo: Dictionary) -> Array:
	if c == goal:
		return [0, null]
	var key: String = "%d,%d," % [c.x, c.y]
	if d == null:
		key += "n"
	else:
		key += "%d,%d" % [(d as Vector2i).x, (d as Vector2i).y]
	if not memo.has(key):
		var best_t: int = 0
		var best_n: Vector2i = Vector2i.ZERO
		var have: bool = false
		for step: Vector2i in BFS_STEPS:
			var n: Vector2i = c + step
			if dist.has(n) and int(dist[n]) == int(dist[c]) - 1:
				var t: int = int(_best(n, step, goal, dist, memo)[0])
				if d != null and (d as Vector2i) != step:
					t += 1
				if not have or t < best_t or (t == best_t and (n.x < best_n.x or (n.x == best_n.x and n.y < best_n.y))):
					best_t = t
					best_n = n
					have = true
		memo[key] = [best_t, best_n]
	return memo[key]


## Shortest 4-connected cell path `a -> b` (fewest turns, then lowest tile); empty Array when unreachable. `ctx` (optional,
## shared between calls on one city) caches the distance field and the DP memo per goal `b`: same result, far fewer BFS runs.
static func _bfs(a: Vector2i, b: Vector2i, cells: Dictionary, ctx: Dictionary = {}) -> Array:
	var dists: Dictionary = ctx.get_or_add("dist", {})
	var memos: Dictionary = ctx.get_or_add("memo", {})
	if not dists.has(b):
		var field: Dictionary = {b: 0}
		var q: Array = [b]
		var head: int = 0
		while head < q.size():
			var c: Vector2i = q[head]
			head += 1
			for step: Vector2i in BFS_STEPS:
				var n: Vector2i = c + step
				if cells.has(n) and not field.has(n):
					field[n] = int(field[c]) + 1
					q.append(n)
		dists[b] = field
		memos[b] = {}
	var dist: Dictionary = dists[b]
	if not dist.has(a):
		return []
	var memo: Dictionary = memos[b]
	var out: Array = [a]
	var d: Variant = null
	while (out[out.size() - 1] as Vector2i) != b:
		var c: Vector2i = out[out.size() - 1]
		var n: Vector2i = _best(c, d, b, dist, memo)[1]
		d = n - c
		out.append(n)
	return out


## Cell path -> polyline of the corner cell centres (lots).
static func _simplify(path: Array) -> Array:
	var pts: Array = []
	for c: Vector2i in path:
		pts.append([float(c.x) + 0.5, float(c.y) + 0.5])
	var out: Array = [pts[0]]
	for i in range(1, pts.size() - 1):
		var a: Array = out[out.size() - 1]
		var b: Array = pts[i]
		var c: Array = pts[i + 1]
		if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) != 0.0:
			out.append(b)
	out.append(pts[pts.size() - 1])
	return out


## The cell whose centre is nearest `p` (ties: lexicographically smaller cell).
static func _nearest_cell(p: Array, cells: Array) -> Vector2i:
	var best: Vector2i = Vector2i.ZERO
	var best_d: float = 0.0
	var have: bool = false
	for c: Vector2i in cells:
		var ex: float = float(c.x) + 0.5 - float(p[0])
		var ey: float = float(c.y) + 0.5 - float(p[1])
		var dd: float = sqrt(ex * ex + ey * ey)
		if not have or dd < best_d or (dd == best_d and (c.x < best.x or (c.x == best.x and c.y < best.y))):
			best = c
			best_d = dd
			have = true
	return best


## Axis-aligned plan polyline (BU) from `a` to `b` along street tiles; L-shaped fallback when no street path exists.
static func route_on_streets(city: Dictionary, a: Array, b: Array, ctx: Dictionary = {}) -> Array:
	var ol: Array = city["origin_lot"]
	var lot_bu: float = float(city["lot_bu"])
	if not ctx.has("cell_set"):
		var cs: Dictionary = street_cells(city)
		var sorted_cells: Array = cs.keys()
		sorted_cells.sort_custom(func(p: Vector2i, q: Vector2i) -> bool: return p.x < q.x or (p.x == q.x and p.y < q.y))
		ctx["cell_set"] = cs
		ctx["cells"] = sorted_cells
	var cell_set: Dictionary = ctx["cell_set"]
	var cells: Array = ctx["cells"]
	var la: Array = plan_to_lot(a, ol, lot_bu)
	var lb_pt: Array = plan_to_lot(b, ol, lot_bu)
	if not cells.is_empty():
		var ca: Vector2i = _nearest_cell(la, cells)
		var cb: Vector2i = _nearest_cell(lb_pt, cells)
		var path: Array = []
		if ca != cb:
			path = _bfs(ca, cb, cell_set, ctx)
		if path.size() >= 2:
			var out: Array = []
			for p: Array in _simplify(path):
				out.append(lot_to_plan(p, ol, lot_bu))
			return out
	return [a.duplicate(), [b[0], a[1]], b.duplicate()]


## The link polyline made of axis-aligned legs: a diagonal segment is replaced by a street route.
static func link_legs(city: Dictionary, pts: Array, ctx: Dictionary = {}) -> Array:
	var axis_tol: float = float(NetrunArtConfigData.shipped().layout["axis_tol"])
	var out: Array = [(pts[0] as Array).duplicate()]
	for i in range(pts.size() - 1):
		var p: Array = pts[i]
		var q: Array = pts[i + 1]
		if absf(float(p[0]) - float(q[0])) < axis_tol or absf(float(p[1]) - float(q[1])) < axis_tol:
			out.append(q.duplicate())
		else:
			var r: Array = route_on_streets(city, p, q, ctx)
			for j in range(1, r.size()):
				out.append(r[j])
	return out


## 0 when the leg runs along x, else 1.
static func leg_axis(a: Array, c: Array) -> int:
	var axis_tol: float = float(NetrunArtConfigData.shipped().layout["axis_tol"])
	return 0 if absf(float(a[1]) - float(c[1])) < axis_tol else 1
