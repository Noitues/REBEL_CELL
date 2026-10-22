class_name CitySolacePark
extends RefCounted
## Solace district layout (A-069 / A-070): the park that replaces the district's street grid. Pure, deterministic from the
## city seed and the lots (no RNG stream advanced, hashes only). `build` reads the finished lots (CityA2Builder kinds) and
## returns the park's data in lot space:
## {"lots": Array[Vector2i] (K_PARK lots of the Solace territory, row order), "outline": Array of {"points": PackedVector2Array,
## "hole": bool} (the organic boundary of the park region: park, block, Site and HQ lots), "paths": Array of {"id", "kind"
## ("stair" / "path" / "lane"), "width_bu", "points": PackedVector2Array}, "ponds": Array of {"centre": Vector2, "points":
## PackedVector2Array}, "plinth": {"centre": Vector2, "radius_bu": float, "stairs": Array of {"dir": String, "landing":
## Vector2, "path": String}}} -- or {} when the territory has no HQ or no park.
## `section` turns it into the `city.json` optional section `solace_park` (plan BU).

const SALT_NOISE := 9120
const SALT_WOBBLE := 9121
const SALT_POND := 9122
const SALT_GATE := 9123
## N / E / S / W in lot space (plan north is -j).
const DIRS: Array[Vector2i] = [Vector2i(0, -1), Vector2i(1, 0), Vector2i(0, 1), Vector2i(-1, 0)]
const DIR_NAMES: Array[String] = ["N", "E", "S", "W"]
const D8: Array[Vector2i] = [Vector2i(0, -1), Vector2i(1, 0), Vector2i(0, 1), Vector2i(-1, 0), Vector2i(1, -1), Vector2i(1, 1),
	Vector2i(-1, 1), Vector2i(-1, -1)]
const ROUTE_LIMIT := 100000
const NONE := Vector2(INF, INF)


## The park of `lots` (CityA2Builder.lots_for result, Solace pass applied) for the Solace territory `terr`; `hq` is the
## Solace HQ rect (Rect2i; size 0 = none). `plinth_r_lots`: the plinth circle radius (lots).
static func build(lots: Dictionary, ras: CityA2Raster, cfg: CampaignConfigData, city_seed: int, terr: StringName, hq: Rect2i,
		plinth_r_lots: float, lot_bu: float) -> Dictionary:
	var R: Rect2i = lots["rect"]
	var kind: PackedByteArray = lots["kind"]
	var park: Dictionary = {}
	var inside: Dictionary = {}
	var park_list: Array[Vector2i] = []
	for j in range(R.position.y, R.end.y):
		for i in range(R.position.x, R.end.x):
			if ras.territory(i, j) != terr:
				continue
			var kd := int(kind[(j - R.position.y) * R.size.x + (i - R.position.x)])
			var l := Vector2i(i, j)
			if kd == CityA2Builder.K_PARK:
				park[l] = true
				inside[l] = true
				park_list.append(l)
			elif kd == CityA2Builder.K_BUILDING or kd == CityA2Builder.K_PLAZA:
				inside[l] = true
	if park_list.is_empty() or hq.size == Vector2i.ZERO:
		return {}
	var centre := Vector2(hq.position) + Vector2(hq.size) * 0.5
	var out := {"lots": park_list, "outline": _outline(inside, city_seed, cfg), "paths": [], "ponds": [], "plinth": {}}
	# Gates: park lots touching a street lot, spaced along the edge (by angle round the park's middle).
	var gates := _gates(park_list, kind, R, centre, cfg.city_sol_gate_spacing)
	var avoid := {}
	var paths: Array = []
	var net := {}  # lot -> true, the lots a path already runs over
	var stairs: Array = []
	var used_gates := {}
	var r_l := plinth_r_lots
	for d in 4:
		var dir := Vector2(DIRS[d])
		var landing := centre + dir * r_l
		var rec := {"dir": DIR_NAMES[d], "landing": landing, "path": ""}
		stairs.append(rec)
		var start := _nearest_park(park, Vector2i(landing.floor()))
		if start == Vector2i(1 << 30, 1 << 30):
			continue
		# gates by how well they lie in this direction, best first
		var ranked: Array = []
		for g: Dictionary in gates:
			var gv: Vector2 = Vector2(g["lot"]) + Vector2(0.5, 0.5) - centre
			ranked.append([-(gv.normalized().dot(dir)), gv.length(), g])
		ranked.sort_custom(func(a: Array, b: Array) -> bool:
			if a[0] != b[0]:
				return a[0] < b[0]
			return a[1] < b[1])
		for t in mini(ranked.size(), 4):
			var g: Dictionary = ranked[t][2]
			var route := _route(park, start, {g["lot"]: true}, city_seed, cfg.city_sol_path_wobble, {})
			if route.is_empty():
				continue
			used_gates[g["lot"]] = true
			var id := "path_%d" % paths.size()
			paths.append(_path(id, "stair", cfg.city_sol_path_width_bu, route, landing, Vector2(g["street"]) + Vector2(0.5, 0.5)))
			rec["path"] = id
			for l: Vector2i in route:
				net[l] = true
			break
	# Other gates: a winding path from the gate to the network (the stairs' paths and the paths laid before).
	for g: Dictionary in gates:
		if used_gates.has(g["lot"]):
			continue
		if net.is_empty():
			break
		var route2 := _route(park, g["lot"], net, city_seed, cfg.city_sol_path_wobble, {})
		if route2.size() < 2:
			continue
		var id2 := "path_%d" % paths.size()
		paths.append(_path(id2, "path", cfg.city_sol_path_width_bu, route2, Vector2(g["street"]) + Vector2(0.5, 0.5), NONE))
		for l: Vector2i in route2:
			net[l] = true
	# Curved service lanes between far-apart gates; they keep off the plinth circle.
	var circle := {}
	for l: Vector2i in park_list:
		if Vector2(l) + Vector2(0.5, 0.5) != centre and (Vector2(l) + Vector2(0.5, 0.5)).distance_to(centre) < r_l + 1.0:
			circle[l] = 12.0
	var n := gates.size()
	if n >= 2:
		for i in cfg.city_sol_lanes:
			var a: Dictionary = gates[(i * n / maxi(cfg.city_sol_lanes, 1)) % n]
			var b: Dictionary = gates[(i * n / maxi(cfg.city_sol_lanes, 1) + n / 2 + i) % n]
			if a["lot"] == b["lot"]:
				continue
			var route3 := _route(park, a["lot"], {b["lot"]: true}, city_seed + 7, cfg.city_sol_path_wobble * 2.0, circle)
			if route3.size() < 2:
				continue
			paths.append(_path("lane_%d" % i, "lane", cfg.city_sol_lane_width_bu, route3, Vector2(a["street"]) + Vector2(0.5, 0.5),
					Vector2(b["street"]) + Vector2(0.5, 0.5)))
	out["paths"] = paths
	out["ponds"] = _ponds(park, paths, centre, r_l, city_seed, cfg)
	out["plinth"] = {"centre": centre, "radius_bu": r_l * lot_bu, "stairs": stairs}
	return out


## The park lots next to a street lot of `kind`, chosen at least `spacing` lots apart (Chebyshev), in order of their angle
## round `centre` (then lot row, column): [{"lot": Vector2i, "street": Vector2i (the street lot beside it)}].
static func _gates(park_list: Array[Vector2i], kind: PackedByteArray, R: Rect2i, centre: Vector2, spacing: int) -> Array:
	var cand: Array = []
	for l in park_list:
		for d: Vector2i in DIRS:
			var q := l + d
			if R.has_point(q) and int(kind[(q.y - R.position.y) * R.size.x + (q.x - R.position.x)]) == CityA2Builder.K_STREET:
				var v := Vector2(l) + Vector2(0.5, 0.5) - centre
				cand.append([atan2(v.y, v.x), l.y, l.x, l, q])
				break
	cand.sort_custom(func(a: Array, b: Array) -> bool:
		for k in 3:
			if a[k] != b[k]:
				return a[k] < b[k]
		return false)
	var out: Array = []
	for c: Array in cand:
		var ok := true
		for g: Dictionary in out:
			var o: Vector2i = g["lot"]
			if maxi(absi(o.x - (c[3] as Vector2i).x), absi(o.y - (c[3] as Vector2i).y)) < spacing:
				ok = false
				break
		if ok:
			out.append({"lot": c[3], "street": c[4]})
	return out


## The park lot nearest `from` (ring search, then lot row, column); (1<<30, 1<<30) when the park is empty.
static func _nearest_park(park: Dictionary, from: Vector2i) -> Vector2i:
	if park.has(from):
		return from
	var best := Vector2i(1 << 30, 1 << 30)
	var best_d := INF
	for l: Vector2i in park:
		var d := Vector2(l - from).length_squared()
		if d < best_d or (d == best_d and (l.y < best.y or (l.y == best.y and l.x < best.x))):
			best_d = d
			best = l
	return best


## The cheapest route over `park` lots from `from` to the first lot of `targets` (a Dijkstra with a seeded noise cost per
## lot: `wobble` x noise, plus `extra` per lot); the lots from..target, or [] when none. Ties by cost, then lot row, column.
static func _route(park: Dictionary, from: Vector2i, targets: Dictionary, city_seed: int, wobble: float, extra: Dictionary) -> Array[Vector2i]:
	var dist := {from: 0.0}
	var prev := {}
	var heap: Array = [[0.0, from.y, from.x]]
	var done := {}
	var steps := 0
	while not heap.is_empty() and steps < ROUTE_LIMIT:
		steps += 1
		var top: Array = _pop(heap)
		var cur := Vector2i(top[2], top[1])
		if done.has(cur):
			continue
		done[cur] = true
		if targets.has(cur):
			var out: Array[Vector2i] = []
			var at := cur
			while true:
				out.append(at)
				if not prev.has(at):
					break
				at = prev[at]
			out.reverse()
			return out
		for k in D8.size():
			var d := D8[k]
			var q := cur + d
			if not park.has(q) or done.has(q):
				continue
			if k >= 4 and not (park.has(cur + Vector2i(d.x, 0)) and park.has(cur + Vector2i(0, d.y))):
				continue
			var step := 1.0 if k < 4 else 1.4142
			var c: float = float(top[0]) + step * (1.0 + wobble * CityMeshKit.hash01(SALT_NOISE ^ (city_seed * 31), q.x, q.y)) + float(extra.get(q, 0.0))
			if not dist.has(q) or c < float(dist[q]):
				dist[q] = c
				prev[q] = cur
				_push(heap, [c, q.y, q.x])
	var none: Array[Vector2i] = []
	return none


static func _less(a: Array, b: Array) -> bool:
	if a[0] != b[0]:
		return a[0] < b[0]
	if a[1] != b[1]:
		return a[1] < b[1]
	return a[2] < b[2]


static func _push(heap: Array, e: Array) -> void:
	heap.append(e)
	var i := heap.size() - 1
	while i > 0:
		var p := (i - 1) / 2
		if _less(heap[i], heap[p]):
			var t: Array = heap[i]
			heap[i] = heap[p]
			heap[p] = t
			i = p
		else:
			break


static func _pop(heap: Array) -> Array:
	var top: Array = heap[0]
	var last: Array = heap.pop_back()
	if not heap.is_empty():
		heap[0] = last
		var i := 0
		var n := heap.size()
		while true:
			var l := 2 * i + 1
			var r := l + 1
			var m := i
			if l < n and _less(heap[l], heap[m]):
				m = l
			if r < n and _less(heap[r], heap[m]):
				m = r
			if m == i:
				break
			var t: Array = heap[i]
			heap[i] = heap[m]
			heap[m] = t
			i = m
	return top


## A path record: `head` (a landing, or the street centre beside a gate; NONE = no head), the route's lot centres, `tail`
## (NONE = none), corner-cut twice.
static func _path(id: String, kind_name: String, width_bu: float, route: Array[Vector2i], head: Vector2, tail: Vector2) -> Dictionary:
	var pts := PackedVector2Array()
	if head != NONE:
		pts.append(head)
	for l in route:
		pts.append(Vector2(l) + Vector2(0.5, 0.5))
	if tail != NONE:
		pts.append(tail)
	return {"id": id, "kind": kind_name, "width_bu": width_bu, "points": _chaikin(pts, 2, false)}


## Corner cutting (`passes` times), keeping both ends; `closed` loops wrap round.
static func _chaikin(pts: PackedVector2Array, passes: int, closed: bool) -> PackedVector2Array:
	var cur := pts
	for _p in passes:
		if cur.size() < 3:
			break
		var nx := PackedVector2Array()
		var n := cur.size()
		if not closed:
			nx.append(cur[0])
		for i in (n if closed else n - 1):
			var a := cur[i]
			var b := cur[(i + 1) % n]
			nx.append(a.lerp(b, 0.25))
			nx.append(a.lerp(b, 0.75))
		if not closed:
			nx.append(cur[n - 1])
		cur = nx
	return cur


## The loops round the lots of `inside` (a set of lot Vector2i): grid edges chained (a left turn at a pinch), collinear
## points dropped, corner-cut `city_sol_outline_passes` times and wobbled by a hash; the largest loop is the outer one.
static func _outline(inside: Dictionary, city_seed: int, cfg: CampaignConfigData) -> Array:
	var edges := {}  # start vertex -> Array of end vertices
	var starts: Array[Vector2i] = []
	for l: Vector2i in inside:
		var x := l.x
		var y := l.y
		var sides := [[Vector2i(0, -1), Vector2i(x, y), Vector2i(x + 1, y)], [Vector2i(1, 0), Vector2i(x + 1, y), Vector2i(x + 1, y + 1)],
			[Vector2i(0, 1), Vector2i(x + 1, y + 1), Vector2i(x, y + 1)], [Vector2i(-1, 0), Vector2i(x, y + 1), Vector2i(x, y)]]
		for s: Array in sides:
			if not inside.has(l + (s[0] as Vector2i)):
				var a: Vector2i = s[1]
				if not edges.has(a):
					edges[a] = []
					starts.append(a)
				(edges[a] as Array).append(s[2])
	starts.sort_custom(func(p: Vector2i, q: Vector2i) -> bool: return p.y < q.y if p.y != q.y else p.x < q.x)
	var loops: Array = []
	for s0: Vector2i in starts:
		while not (edges[s0] as Array).is_empty():
			var loop: Array[Vector2i] = [s0]
			var cur: Vector2i = s0
			var dir := Vector2i.ZERO
			var guard := 0
			while guard < 100000:
				guard += 1
				var outs: Array = edges[cur]
				if outs.is_empty():
					break
				var pick := 0
				if outs.size() > 1:
					# the left turn (screen y down: cross of incoming x outgoing is negative)
					var best := 99
					for k in outs.size():
						var o: Vector2i = (outs[k] as Vector2i) - cur
						var cr := dir.x * o.y - dir.y * o.x
						var rank := 0 if cr < 0 else (1 if cr == 0 else 2)
						if rank < best:
							best = rank
							pick = k
				var nxt: Vector2i = outs[pick]
				outs.remove_at(pick)
				dir = nxt - cur
				cur = nxt
				if cur == s0:
					break
				loop.append(cur)
			loops.append(loop)
	var res: Array = []
	for loop: Array in loops:
		var pts := PackedVector2Array()
		var n := loop.size()
		for i in n:
			var a: Vector2i = loop[(i + n - 1) % n]
			var b: Vector2i = loop[i]
			var c: Vector2i = loop[(i + 1) % n]
			if (b - a) != (c - b):
				pts.append(Vector2(b))
		if pts.size() < 3:
			continue
		var area := 0.0
		for i in pts.size():
			var p := pts[i]
			var q := pts[(i + 1) % pts.size()]
			area += p.x * q.y - q.x * p.y
		var sm := _chaikin(pts, cfg.city_sol_outline_passes, true)
		var wob := PackedVector2Array()
		for p in sm:
			var h1 := CityMeshKit.hash01(SALT_WOBBLE ^ (city_seed * 31), int(floorf(p.x * 8.0)), int(floorf(p.y * 8.0)))
			var h2 := CityMeshKit.hash01(SALT_WOBBLE + 1 ^ (city_seed * 31), int(floorf(p.x * 8.0)), int(floorf(p.y * 8.0)))
			wob.append(p + Vector2(h1 - 0.5, h2 - 0.5) * 2.0 * cfg.city_sol_outline_wobble)
		res.append({"points": wob, "area": absf(area) * 0.5, "hole": area < 0.0})
	res.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a["area"] > b["area"])
	# the outer loops are those of the sign of the largest; the others (opposite sign) are holes
	if not res.is_empty():
		var outer_hole: bool = res[0]["hole"]
		for r: Dictionary in res:
			r["hole"] = (bool(r["hole"]) != outer_hole)
			r.erase("area")
	return res


## Up to `city_sol_ponds` ponds on open lawn: a park lot whose 8 neighbours are park too, off the paths and the plinth
## circle, spaced 6 lots apart, taken by a hash order; a 14-gon with a hashed radius wobble.
static func _ponds(park: Dictionary, paths: Array, centre: Vector2, r_l: float, city_seed: int, cfg: CampaignConfigData) -> Array:
	var out: Array = []
	if cfg.city_sol_ponds <= 0:
		return out
	# the lots within 2 of any path point (a pond is at most 1.4 lots across and keeps a lot off the paths)
	var on_path := {}
	for p: Dictionary in paths:
		for q: Vector2 in p["points"]:
			var ql := Vector2i(q.floor())
			for dj in range(-2, 3):
				for di in range(-2, 3):
					on_path[ql + Vector2i(di, dj)] = true
	var cand: Array = []
	for l: Vector2i in park:
		var open := true
		for d: Vector2i in D8:
			if not park.has(l + d):
				open = false
				break
		if not open:
			continue
		var c := Vector2(l) + Vector2(0.5, 0.5)
		if c.distance_to(centre) < r_l + 2.0:
			continue
		if on_path.has(l):
			continue
		cand.append([CityMeshKit.hash01(SALT_POND ^ (city_seed * 31), l.x, l.y), l.y, l.x, c])
	cand.sort_custom(func(a: Array, b: Array) -> bool:
		for k in 3:
			if a[k] != b[k]:
				return a[k] > b[k] if k == 0 else a[k] < b[k]
		return false)
	for c: Array in cand:
		if out.size() >= cfg.city_sol_ponds:
			break
		var at: Vector2 = c[3]
		var far := true
		for o: Dictionary in out:
			if (o["centre"] as Vector2).distance_to(at) < 6.0:
				far = false
				break
		if not far:
			continue
		var r0 := lerpf(cfg.city_sol_pond_r.x, cfg.city_sol_pond_r.y, CityMeshKit.hash01(SALT_POND + 1, int(c[2]), int(c[1])))
		var poly := PackedVector2Array()
		for k in 14:
			var a := TAU * float(k) / 14.0
			var rr := r0 * (0.85 + 0.3 * CityMeshKit.hash01(SALT_POND + 2, int(c[2]) * 31 + k, int(c[1])))
			poly.append(at + Vector2(cos(a), sin(a)) * rr)
		out.append({"centre": at, "points": poly})
	return out


## The `city.json` optional section `solace_park` (plan BU: x east, y north = -j; widths and radii in BU) from `park` (build).
static func section(park: Dictionary, lot_bu: float, origin: Vector2) -> Dictionary:
	if park.is_empty():
		return {}
	var loops := []
	for lp: Dictionary in park["outline"]:
		loops.append({"hole": bool(lp["hole"]), "points": _pts(lp["points"], lot_bu, origin)})
	var paths := []
	for p: Dictionary in park["paths"]:
		paths.append({"id": p["id"], "kind": p["kind"], "width": _r3(float(p["width_bu"])), "points": _pts(p["points"], lot_bu, origin)})
	var ponds := []
	for p: Dictionary in park["ponds"]:
		ponds.append({"centre": _pt(p["centre"], lot_bu, origin), "points": _pts(p["points"], lot_bu, origin)})
	var lots := []
	for l: Vector2i in park["lots"]:
		lots.append([l.x, l.y])
	var pl: Dictionary = park["plinth"]
	var stairs := []
	for s: Dictionary in pl["stairs"]:
		stairs.append({"dir": s["dir"], "landing": _pt(s["landing"], lot_bu, origin), "path": s["path"]})
	return {"outline": loops, "paths": paths, "ponds": ponds, "lots": lots,
		"plinth": {"centre": _pt(pl["centre"], lot_bu, origin), "radius": _r3(float(pl["radius_bu"])), "stairs": stairs}}


static func _r3(v: float) -> float:
	return roundf(v * 1000.0) / 1000.0


static func _pt(p: Vector2, lot_bu: float, origin: Vector2) -> Array:
	var a := NetrunArtExport.plan_point(p, lot_bu, origin)
	return [_r3(float(a[0])), _r3(float(a[1]))]


static func _pts(pts: PackedVector2Array, lot_bu: float, origin: Vector2) -> Array:
	var out := []
	for p in pts:
		out.append(_pt(p, lot_bu, origin))
	return out
