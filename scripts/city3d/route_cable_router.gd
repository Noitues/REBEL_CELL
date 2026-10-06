class_name RouteCableRouter
extends RefCounted
## ART-7 7w: the netrun transit's cable router (ART_BIBLE v2 §4.6 "Transit paths v3"): every
## link of the run's route is a network cable run laid on the real city's streets and blocks,
## found on a lattice of CELLS_PER_LOT points per lot (lot space, the ground):
## - straight segments with **45° or 90° turns only** (eight directions; a sharper turn is
##   never taken);
## - cables **cross streets rather than ride them**: a step along a street's own run costs
##   RIDE more than a step across it or between the blocks' buildings;
## - **crossings avoided**: a cable already laid makes its points and segments dear to the
##   ones routed after it (CROSS where one would cross it, SHARE where one would run along
##   it), except within END_FREE lots of the new cable's own ends (links fan out of one node);
## - **the rest bridged with a hop**: where two cables still cross, the one routed later
##   carries a hop there (`hops`), drawn by the view as a small bridge.
## Cables are routed in the order given (the view passes the route's graph order, so a
## cable never moves when the run's state changes). Pure and deterministic: ties go by the
## lattice's own order (f, then the state index), never by dictionary order. A view helper:
## it reads the city through `is_street` and changes nothing.

## Lattice points per lot (even, so a lot's centre is a lattice point).
const CELLS_PER_LOT := 2
## The search box round a cable's two ends (lots).
const BOX_MARGIN_LOTS := 4
## Costs are in lattice steps of cable (a straight step costs 1, a diagonal one sqrt 2).
## Extra cost per step of riding along a street's run (a diagonal step pays half).
const RIDE := 3.0
## Cost of a 45° and of a 90° turn.
const TURN_45 := 0.35
const TURN_90 := 1.2
## Cost of crossing a cable already laid, and of running along one (per step).
const CROSS := 10.0
const SHARE := 12.0
## Near its own ends a cable may touch others freely (lots): links fan out of one node.
const END_FREE := 1.0
## A crossing this near either cable's end is where they meet at a node: no hop (lots).
const HOP_END_SKIP := 0.75

## The eight directions, counter-clockwise from +x (lattice steps).
const DIRS: Array[Vector2i] = [Vector2i(1, 0), Vector2i(1, 1), Vector2i(0, 1), Vector2i(-1, 1), Vector2i(-1, 0),
	Vector2i(-1, -1), Vector2i(0, -1), Vector2i(1, -1)]
const NO_DIR := 8

var _is_street: Callable
var _street_memo: Dictionary = {}
var _used_points: Dictionary = {}
var _used_segs: Dictionary = {}
## The search's open set: a binary heap of (f, state).
var _hf := PackedFloat32Array()
var _hs := PackedInt32Array()


## Routes every pair in `pairs` ({"a": Vector2, "b": Vector2}, lot points) in order over the
## city whose street lots `is_street` (func(i: int, j: int) -> bool) answers. Returns one
## {"points": PackedVector2Array (lot points: the ends and every turn), "hops":
## Array[Dictionary] ({"seg": int, "at": Vector2}, along the cable)} per pair.
static func route_all(pairs: Array, is_street: Callable) -> Array[Dictionary]:
	var r := RouteCableRouter.new()
	r._is_street = is_street
	var out: Array[Dictionary] = []
	for p: Dictionary in pairs:
		var pts := r.route(Vector2(p["a"]), Vector2(p["b"]))
		r._lay(pts)
		out.append({"points": pts, "hops": []})
	# Crossings left: the later cable hops the earlier one.
	for i in out.size():
		var hops: Array[Dictionary] = []
		var pi: PackedVector2Array = out[i]["points"]
		for j in i:
			for h in crossings(pi, out[j]["points"]):
				hops.append(h)
		hops.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
			if int(x["seg"]) != int(y["seg"]):
				return int(x["seg"]) < int(y["seg"])
			return pi[int(x["seg"])].distance_squared_to(x["at"]) < pi[int(y["seg"])].distance_squared_to(y["at"]))
		out[i]["hops"] = hops
	return out


## The lattice point nearest lot point `p`.
static func lattice(p: Vector2) -> Vector2i:
	return Vector2i(roundi(p.x * CELLS_PER_LOT), roundi(p.y * CELLS_PER_LOT))


## The lot point of lattice point `v`.
static func lot_point(v: Vector2i) -> Vector2:
	return Vector2(v) / float(CELLS_PER_LOT)


## The turn between directions `d0` and `d1` (DIRS indices) in 45° steps (0..4).
static func turn_steps(d0: int, d1: int) -> int:
	var t := absi(d0 - d1) % 8
	return mini(t, 8 - t)


## One cable from lot point `a` to `b` (the ends and its turns, lot points), avoiding the
## cables laid so far.
func route(a: Vector2, b: Vector2) -> PackedVector2Array:
	var s := lattice(a)
	var t := lattice(b)
	var out := PackedVector2Array()
	if s == t:
		out.append(a)
		out.append(b)
		return out
	var m := BOX_MARGIN_LOTS * CELLS_PER_LOT
	var box := Rect2i(Vector2i(mini(s.x, t.x) - m, mini(s.y, t.y) - m), Vector2i(absi(s.x - t.x) + 2 * m + 1, absi(s.y - t.y) + 2 * m + 1))
	var w := box.size.x
	var states := box.size.x * box.size.y * 9
	var g := PackedFloat32Array()
	g.resize(states)
	g.fill(INF)
	var from := PackedInt32Array()
	from.resize(states)
	from.fill(-1)
	var closed := PackedByteArray()
	closed.resize(states)
	_hf = PackedFloat32Array()
	_hs = PackedInt32Array()
	var start := ((s.x - box.position.x) + (s.y - box.position.y) * w) * 9 + NO_DIR
	g[start] = 0.0
	_push(_octile(s, t), start)
	var goal := -1
	while not _hs.is_empty():
		var cur := _pop()
		if closed[cur] == 1:
			continue
		closed[cur] = 1
		var cell := cur / 9
		var dir := cur % 9
		var v := Vector2i(cell % w + box.position.x, cell / w + box.position.y)
		if v == t:
			goal = cur
			break
		for nd in 8:
			var turn := 0 if dir == NO_DIR else turn_steps(dir, nd)
			if turn > 2:
				continue
			var nv := v + DIRS[nd]
			if not box.has_point(nv):
				continue
			var ns := ((nv.x - box.position.x) + (nv.y - box.position.y) * w) * 9 + nd
			if closed[ns] == 1:
				continue
			var cost := _step_cost(v, nv, nd, s, t)
			if turn == 1:
				cost += TURN_45
			elif turn == 2:
				cost += TURN_90
			var ng := g[cur] + cost
			if ng < g[ns] - 0.00001:
				g[ns] = ng
				from[ns] = cur
				_push(ng + _octile(nv, t), ns)
	if goal < 0:
		out.append(a)
		out.append(b)
		return out
	var chain: Array[Vector2i] = []
	var at := goal
	while at >= 0:
		var c := at / 9
		chain.append(Vector2i(c % w + box.position.x, c / w + box.position.y))
		at = from[at]
	chain.reverse()
	# The ends exactly where asked (a lot point off the lattice keeps a short stub), then
	# only the turns.
	out.append(a)
	if not lot_point(chain[0]).is_equal_approx(a):
		out.append(lot_point(chain[0]))
	for k in range(1, chain.size() - 1):
		if chain[k] - chain[k - 1] != chain[k + 1] - chain[k]:
			out.append(lot_point(chain[k]))
	if not lot_point(chain[chain.size() - 1]).is_equal_approx(b):
		out.append(lot_point(chain[chain.size() - 1]))
	out.append(b)
	return out


## The cost of the step from lattice point `v` to `nv` (direction `nd`) for a cable from
## `s` to `t`: its length, riding a street, crossing or running along a cable laid.
func _step_cost(v: Vector2i, nv: Vector2i, nd: int, s: Vector2i, t: Vector2i) -> float:
	var diag := nd % 2 == 1
	var cost := sqrt(2.0) if diag else 1.0
	var mid := (lot_point(v) + lot_point(nv)) * 0.5
	var lot := Vector2i(floori(mid.x), floori(mid.y))
	var run := _street_run(lot)
	if run >= 0:
		if diag:
			cost += RIDE * 0.5
		elif (run == 0 and DIRS[nd].y == 0) or (run == 1 and DIRS[nd].x == 0):
			cost += RIDE
	var free_r := END_FREE * CELLS_PER_LOT
	var near_end := Vector2(nv - s).length() <= free_r or Vector2(nv - t).length() <= free_r \
		or Vector2(v - s).length() <= free_r or Vector2(v - t).length() <= free_r
	if near_end:
		return cost
	if _used_segs.has(_seg_key(v, nv)):
		cost += SHARE
	elif _used_points.has(nv):
		cost += CROSS
	elif diag and _used_segs.has(_seg_key(Vector2i(nv.x, v.y), Vector2i(v.x, nv.y))):
		cost += CROSS
	return cost


## The run of street lot `lot`: 0 along lot x, 1 along lot y, -1 when it is no street or
## a crossing of both (a step there rides nothing).
func _street_run(lot: Vector2i) -> int:
	if not _street(lot):
		return -1
	var along_x := _street(lot + Vector2i(1, 0)) or _street(lot - Vector2i(1, 0))
	var along_y := _street(lot + Vector2i(0, 1)) or _street(lot - Vector2i(0, 1))
	if along_x and not along_y:
		return 0
	if along_y and not along_x:
		return 1
	return -1


func _street(lot: Vector2i) -> bool:
	var known: Variant = _street_memo.get(lot)
	if known != null:
		return known
	var v: bool = bool(_is_street.call(lot.x, lot.y)) if _is_street.is_valid() else false
	_street_memo[lot] = v
	return v


## Marks cable `pts` (lot points) as laid: its lattice points and segments.
func _lay(pts: PackedVector2Array) -> void:
	for k in pts.size() - 1:
		var a := lattice(pts[k])
		var b := lattice(pts[k + 1])
		var d := b - a
		var n := maxi(absi(d.x), absi(d.y))
		if n == 0:
			continue
		var step := Vector2i(signi(d.x), signi(d.y))
		var p := a
		_used_points[p] = true
		for q in n:
			var nxt := p + step
			_used_segs[_seg_key(p, nxt)] = true
			_used_points[nxt] = true
			p = nxt


static func _seg_key(a: Vector2i, b: Vector2i) -> Vector4i:
	if a.x < b.x or (a.x == b.x and a.y < b.y):
		return Vector4i(a.x, a.y, b.x, b.y)
	return Vector4i(b.x, b.y, a.x, a.y)


static func _octile(a: Vector2i, b: Vector2i) -> float:
	var dx := absi(a.x - b.x)
	var dy := absi(a.y - b.y)
	return float(maxi(dx, dy) - mini(dx, dy)) + sqrt(2.0) * mini(dx, dy)


## Where polyline `p` (lot points) properly crosses polyline `q`, away from both ends
## (HOP_END_SKIP): [{"seg": index of p's segment, "at": the lot point}].
static func crossings(p: PackedVector2Array, q: PackedVector2Array) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if p.size() < 2 or q.size() < 2:
		return out
	var ends: Array[Vector2] = [p[0], p[p.size() - 1], q[0], q[q.size() - 1]]
	for i in p.size() - 1:
		for j in q.size() - 1:
			var hit: Variant = Geometry2D.segment_intersects_segment(p[i], p[i + 1], q[j], q[j + 1])
			if hit == null:
				continue
			var at: Vector2 = hit
			var near := false
			for e in ends:
				if at.distance_to(e) < HOP_END_SKIP:
					near = true
					break
			# Two cables along one line touch, they do not cross: no hop.
			var dp := (p[i + 1] - p[i]).normalized()
			var dq := (q[j + 1] - q[j]).normalized()
			if near or absf(dp.cross(dq)) < 0.01:
				continue
			out.append({"seg": i, "at": at})
	return out


# --- A binary heap of (f, state), ties by the state index --------------------------------------

static func _less(fa: float, sa: int, fb: float, sb: int) -> bool:
	if not is_equal_approx(fa, fb):
		return fa < fb
	return sa < sb


func _push(f: float, s: int) -> void:
	_hf.append(f)
	_hs.append(s)
	var i := _hs.size() - 1
	while i > 0:
		var p := (i - 1) / 2
		if not _less(_hf[i], _hs[i], _hf[p], _hs[p]):
			break
		var tf := _hf[i]
		_hf[i] = _hf[p]
		_hf[p] = tf
		var ts := _hs[i]
		_hs[i] = _hs[p]
		_hs[p] = ts
		i = p


func _pop() -> int:
	var top := _hs[0]
	var last := _hs.size() - 1
	_hf[0] = _hf[last]
	_hs[0] = _hs[last]
	_hf.resize(last)
	_hs.resize(last)
	var i := 0
	while true:
		var l := i * 2 + 1
		var r := l + 1
		var m := i
		if l < last and _less(_hf[l], _hs[l], _hf[m], _hs[m]):
			m = l
		if r < last and _less(_hf[r], _hs[r], _hf[m], _hs[m]):
			m = r
		if m == i:
			break
		var tf := _hf[i]
		_hf[i] = _hf[m]
		_hf[m] = tf
		var ts := _hs[i]
		_hs[i] = _hs[m]
		_hs[m] = ts
		i = m
	return top
