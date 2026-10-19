class_name CityA2Raster
extends RefCounted
## CITY-A2 step 1: a CityPlanA2 laid on the game's lot grid (seed-independent, built once per config): which lots are
## sea / lake / river, which A2 district and game territory each lot lies in (with the runner-up territory and a border
## share, NeonCity's `_territory_pair` form), the A2 road class over each lot, the parks, and each lot's signed depth from
## the shore. Pure data; lots outside the raster read as their nearest edge lot.
##
## Mapping: lot = origin + (x_m, -y_m) / metres_per_lot (A2 +X east = +i, +Y north = -j).

var a2: CityPlanA2
## The rasterised lots (the city rect grown by the config's margin).
var rect: Rect2i = Rect2i()
var metres_per_lot: float = 1.0
## The lot point of A2's origin (0, 0).
var origin: Vector2 = Vector2.ZERO
## Territory ids by index (0 = &"", the neutral Sprawl).
var terr_ids: Array[StringName] = [&""]
## 0 land, SEA (the ocean and lakes) or RIVER (a river lot: local streets bridge it).
var water: PackedByteArray = PackedByteArray()
const SEA := 1
const RIVER := 2
## A2 district index + 1 (0 = outside every district).
var district: PackedByteArray = PackedByteArray()
var terr: PackedByteArray = PackedByteArray()
var second: PackedByteArray = PackedByteArray()
var border: PackedFloat32Array = PackedFloat32Array()
## Road class rank + 1 (CityPlanA2.ROAD_CLASSES order; 0 = no road; the widest road wins).
var road: PackedByteArray = PackedByteArray()
var park: PackedByteArray = PackedByteArray()
## Signed lots from the shore: positive on land, negative in the water.
var depth: PackedFloat32Array = PackedFloat32Array()
## The A2 neighbourhood kind over each lot (index into `nb_kinds`; 0 = none): the first neighbourhood (file order)
## whose radius holds the lot's centre.
var nb_kind: PackedByteArray = PackedByteArray()
var nb_kinds: Array[StringName] = [&""]
## Road id -> the lots it covers inside the raster (Array[Vector2i], in polyline order, no repeats).
var road_lots: Dictionary = {}


## The raster of `p_a2` over `p_rect` at `mpl` metres per lot, A2's origin at lot point `p_origin`. `territory_of` maps
## an A2 district id to a game territory id (unmapped ids are Sprawl); `river_kinds` are the river kinds that are water;
## `road_half_min` the least half width (lots) a road is drawn with; `blend` the lots a territory border mixes over.
static func make(p_a2: CityPlanA2, p_rect: Rect2i, mpl: float, p_origin: Vector2, territory_of: Dictionary,
		river_kinds: PackedStringArray, road_half_min: float, blend: float) -> CityA2Raster:
	var r := CityA2Raster.new()
	r.a2 = p_a2
	r.rect = p_rect
	r.metres_per_lot = mpl
	r.origin = p_origin
	var n := p_rect.size.x * p_rect.size.y
	r.water.resize(n)
	r.district.resize(n)
	r.terr.resize(n)
	r.second.resize(n)
	r.road.resize(n)
	r.park.resize(n)
	r.border.resize(n)
	r.nb_kind.resize(n)
	r.depth.resize(n)
	r._fill(r.water, r._to_lots(p_a2.ocean), 1)
	for l in p_a2.lakes:
		r._fill(r.water, r._to_lots(l), 1)
	for rv in p_a2.rivers:
		if String(rv["kind"]) in river_kinds:
			var w: Vector2 = rv["width"]
			r._stroke(rv["polyline"], maxf(maxf(w.x, w.y) * 0.5 / mpl, road_half_min), func(k: int) -> void:
				if r.water[k] == 0:
					r.water[k] = RIVER)
	var ids: Array = []
	for d in p_a2.districts:
		var t := StringName(String(territory_of.get(String(d["id"]), "")))
		if t != &"" and not t in r.terr_ids:
			ids.append(t)
	IdSort.sort_ids(ids)
	for t: StringName in ids:
		r.terr_ids.append(t)
	for k in p_a2.districts.size():
		var d := p_a2.districts[k]
		r._fill(r.district, r._to_lots(d["polygon"]), k + 1)
	for k in n:
		var di := int(r.district[k])
		if di > 0:
			var t := StringName(String(territory_of.get(String(p_a2.districts[di - 1]["id"]), "")))
			r.terr[k] = r.terr_ids.find(t)
	for pk in p_a2.parks:
		r._fill(r.park, r._to_lots(pk), 1)
	for rd in p_a2.roads:
		var rank := CityPlanA2.ROAD_CLASSES.find(rd["class"]) + 1
		var lots: Array[Vector2i] = []
		var seen := {}
		r._stroke(rd["polyline"], maxf(float(rd["width"]) * 0.5 / mpl, road_half_min), func(k: int) -> void:
			if r.road[k] == 0 or r.road[k] > rank:
				r.road[k] = rank
			if not seen.has(k):
				seen[k] = true
				lots.append(r.lot_at_index(k)))
		r.road_lots[rd["id"]] = lots
	for nb in p_a2.neighbourhoods:
		var kn := r.nb_kinds.find(nb["kind"])
		if kn < 0:
			kn = r.nb_kinds.size()
			r.nb_kinds.append(nb["kind"])
		var c := r.lot_of(nb["centre"])
		var rad := float(nb["radius"]) / mpl
		for j in range(floori(c.y - rad), ceili(c.y + rad) + 1):
			for i in range(floori(c.x - rad), ceili(c.x + rad) + 1):
				if p_rect.has_point(Vector2i(i, j)) and Vector2(i + 0.5, j + 0.5).distance_to(c) <= rad:
					var k := r.index(i, j)
					if r.nb_kind[k] == 0:
						r.nb_kind[k] = kn
	r._depths()
	r._borders(blend)
	return r


## The lot point (fractional) of A2 point `m` (metres).
func lot_of(m: Vector2) -> Vector2:
	return origin + Vector2(m.x, -m.y) / metres_per_lot


## The A2 point (metres) of lot point `l`.
func metres_of(l: Vector2) -> Vector2:
	var d := (l - origin) * metres_per_lot
	return Vector2(d.x, -d.y)


## The raster index of lot (i, j), clamped to the raster's edge.
func index(i: int, j: int) -> int:
	var x := clampi(i - rect.position.x, 0, rect.size.x - 1)
	var y := clampi(j - rect.position.y, 0, rect.size.y - 1)
	return y * rect.size.x + x


## The lot of raster index `k`.
func lot_at_index(k: int) -> Vector2i:
	return Vector2i(rect.position.x + k % rect.size.x, rect.position.y + k / rect.size.x)


func is_water(i: int, j: int) -> bool:
	return water[index(i, j)] != 0


func is_river(i: int, j: int) -> bool:
	return water[index(i, j)] == RIVER


## The game territory of lot (i, j) (&"" = Sprawl).
func territory(i: int, j: int) -> StringName:
	return terr_ids[terr[index(i, j)]]


## [owner, runner-up, border 0-1] of lot (i, j) (NeonCity's `_territory_pair` form).
func territory_pair(i: int, j: int) -> Array:
	var k := index(i, j)
	return [terr_ids[terr[k]], terr_ids[second[k]], border[k]]


## The A2 district id of lot (i, j) (&"" outside every district).
func district_id(i: int, j: int) -> StringName:
	var di := int(district[index(i, j)])
	return a2.districts[di - 1]["id"] if di > 0 else &""


## The A2 road class rank + 1 over lot (i, j) (0 = none).
func road_rank(i: int, j: int) -> int:
	return int(road[index(i, j)])


## The A2 neighbourhood kind over lot (i, j) (&"" = none).
func neighbourhood_kind(i: int, j: int) -> StringName:
	return nb_kinds[nb_kind[index(i, j)]]


func is_park(i: int, j: int) -> bool:
	return park[index(i, j)] != 0


## Signed lots from the shore at lot point (x, y): positive on land.
func depth_at(x: float, y: float) -> float:
	return depth[index(floori(x), floori(y))]


func _to_lots(poly: PackedVector2Array) -> PackedVector2Array:
	var out := PackedVector2Array()
	for p in poly:
		out.append(lot_of(p))
	return out


## Sets `grid` to `value` on every lot whose centre lies inside `poly` (lots; even-odd scanlines).
func _fill(grid: PackedByteArray, poly: PackedVector2Array, value: int) -> void:
	var n := poly.size()
	for y in rect.size.y:
		var cy := float(rect.position.y + y) + 0.5
		var xs: Array[float] = []
		for k in n:
			var a := poly[k]
			var b := poly[(k + 1) % n]
			if (a.y > cy) != (b.y > cy):
				xs.append(a.x + (cy - a.y) * (b.x - a.x) / (b.y - a.y))
		xs.sort()
		var q := 0
		while q + 1 < xs.size():
			var i0 := maxi(ceili(xs[q] - 0.5), rect.position.x)
			var i1 := mini(ceili(xs[q + 1] - 0.5), rect.end.x)
			for i in range(i0, i1):
				grid[y * rect.size.x + (i - rect.position.x)] = value
			q += 2


## Calls `mark` with the raster index of every lot within `half` lots of polyline `pl` (metres), along the line
## (4-connected: a diagonal step also marks its corner lot), each lot once per segment run.
func _stroke(pl: PackedVector2Array, half: float, mark: Callable) -> void:
	var reach := maxi(ceili(half - 0.5), 0)
	var last := Vector2i(1 << 30, 1 << 30)
	for s in range(pl.size() - 1):
		var a := lot_of(pl[s])
		var b := lot_of(pl[s + 1])
		var steps := maxi(ceili(a.distance_to(b) * 4.0), 1)
		for t in steps + 1:
			var p := a.lerp(b, float(t) / steps)
			var l := Vector2i(floori(p.x), floori(p.y))
			if l == last:
				continue
			if last.x != (1 << 30) and l.x != last.x and l.y != last.y:
				_mark_disc(Vector2i(l.x, last.y), Vector2(l.x, last.y) + Vector2(0.5, 0.5), half, reach, mark)
			_mark_disc(l, p, half, reach, mark)
			last = l


func _mark_disc(l: Vector2i, p: Vector2, half: float, reach: int, mark: Callable) -> void:
	for dj in range(-reach, reach + 1):
		for di in range(-reach, reach + 1):
			var q := l + Vector2i(di, dj)
			if not rect.has_point(q):
				continue
			if (di != 0 or dj != 0) and (Vector2(q) + Vector2(0.5, 0.5)).distance_to(p) > half + 0.5:
				continue
			mark.call((q.y - rect.position.y) * rect.size.x + (q.x - rect.position.x))


## `depth`: a 4-neighbour breadth-first distance from the other medium (land from water, water from land), the lot
## next to the shore at 0.5.
func _depths() -> void:
	var n := water.size()
	var dist := PackedInt32Array()
	dist.resize(n)
	dist.fill(-1)
	var queue := PackedInt32Array()
	var w := rect.size.x
	for k in n:
		var x := k % w
		var y := k / w
		for d: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var nx := x + d.x
			var ny := y + d.y
			if nx >= 0 and ny >= 0 and nx < w and ny < rect.size.y and (water[ny * w + nx] != 0) != (water[k] != 0):
				dist[k] = 1
				queue.append(k)
				break
	var head := 0
	while head < queue.size():
		var k := queue[head]
		head += 1
		var x := k % w
		var y := k / w
		for d: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var nx := x + d.x
			var ny := y + d.y
			if nx < 0 or ny < 0 or nx >= w or ny >= rect.size.y:
				continue
			var q := ny * w + nx
			if dist[q] < 0 and (water[q] != 0) == (water[k] != 0):
				dist[q] = dist[k] + 1
				queue.append(q)
	var far := float(w + rect.size.y)
	for k in n:
		var dd := float(dist[k]) - 0.5 if dist[k] > 0 else far
		depth[k] = -dd if water[k] != 0 else dd


## `second` and `border`: from every lot with a 4-neighbour of another territory (border 1, that territory second),
## a breadth-first spread `blend` lots inward (border falling to 0); deeper lots keep their own territory second.
func _borders(blend: float) -> void:
	var n := terr.size()
	var w := rect.size.x
	var dist := PackedInt32Array()
	dist.resize(n)
	dist.fill(-1)
	var queue := PackedInt32Array()
	for k in n:
		second[k] = terr[k]
		var x := k % w
		var y := k / w
		for d: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var nx := x + d.x
			var ny := y + d.y
			if nx >= 0 and ny >= 0 and nx < w and ny < rect.size.y and terr[ny * w + nx] != terr[k]:
				second[k] = terr[ny * w + nx]
				dist[k] = 0
				queue.append(k)
				break
	var head := 0
	var reach := ceili(blend)
	while head < queue.size():
		var k := queue[head]
		head += 1
		if dist[k] >= reach:
			continue
		var x := k % w
		var y := k / w
		for d: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var nx := x + d.x
			var ny := y + d.y
			if nx < 0 or ny < 0 or nx >= w or ny >= rect.size.y:
				continue
			var q := ny * w + nx
			if dist[q] < 0 and terr[q] == terr[k]:
				dist[q] = dist[k] + 1
				second[q] = second[k]
				queue.append(q)
	for k in n:
		border[k] = clampf(1.0 - float(dist[k]) / maxf(blend, 0.001), 0.0, 1.0) if dist[k] >= 0 else 0.0
