class_name CityMotionSite
extends RefCounted
## ART-5 5c: the one seam between the city's motion layers and the city model they sit on.
## Everything the layers need from the city, as plain world-space data: the lot frame
## (world = (lot - origin_lot) * lot_bu on X / Z, height on Y), the avenues busiest first,
## the roofs (for billboards, aviation lights, searchlights, alarms), the street lots (for
## police strobes and street traffic), the Cell's home point and the bounds. Built from
## 1D's spike district (`from_district`) until 5a's CityModel lands (then `from_model`
## fills the same fields); the lab and the tests build a small grid (`grid`). Pure data.

## World units per lot and the lot at the world origin.
var lot_bu: float = 6.0
var origin_lot: Vector2 = Vector2.ZERO
## Avenues busiest first (CityTraffic.avenue_lines' shape): {"axis": 0 (runs along lot y
## at x = line) / 1 (along lot x at y = line), "line": int, "a": Vector2, "b": Vector2
## (lot points on its centre line), "traffic": float, "n": int}.
var avenues: Array[Dictionary] = []
## Roofs by building key: {"pos": Vector3 (world, roof centre), "h": float, "key": int}.
var roofs: Array[Dictionary] = []
## Street lots: {"lot": Vector2i, "traffic": float, "corner": bool}.
var streets: Array[Dictionary] = []
## The Cell's home (world, street level) and the city's bounds.
var home: Vector3 = Vector3.ZERO
var bounds: AABB = AABB()


## World position of lot point `lot` at height `h`.
func lot_to_world(lot: Vector2, h: float = 0.0) -> Vector3:
	return Vector3((lot.x - origin_lot.x) * lot_bu, h, (lot.y - origin_lot.y) * lot_bu)


## Lot point under world position `w`.
func world_to_lot(w: Vector3) -> Vector2:
	return Vector2(w.x / lot_bu + origin_lot.x, w.z / lot_bu + origin_lot.y)


## The site of 1D's spike district `d` (its config gives the lot frame); `home_lot` is the
## Cell's district centre in lots (the district's centre when omitted).
static func from_district(d: CityDistrict, spike_cfg: CitySpikeConfig, home_lot: Vector2 = Vector2.INF) -> CityMotionSite:
	var s := CityMotionSite.new()
	s.lot_bu = spike_cfg.lot_bu
	s.origin_lot = spike_cfg.district_centre
	s.avenues = CityTraffic.avenue_lines(d)
	var tops := {}
	for pr in d.prisms:
		var b := int(pr["building"])
		var top := float(pr["y0"]) + float(pr["h"])
		if not tops.has(b) or top > float(tops[b]["h"]):
			var c: Vector2 = pr["centre"]
			tops[b] = {"pos": Vector3(c.x, top, c.y), "h": top, "key": b}
	var keys: Array = tops.keys()
	keys.sort()
	for k: int in keys:
		s.roofs.append(tops[k])
	for st in d.streets:
		s.streets.append({"lot": st["lot"], "traffic": float(st["traffic"]), "corner": bool(st["along_i"]) and bool(st["along_j"])})
	s.home = s.lot_to_world(spike_cfg.district_centre if home_lot == Vector2.INF else home_lot)
	s.bounds = d.bounds()
	return s


## A small regular city for the lab and the tests: `size` lots square with an avenue every
## `every` lots both ways (traffic falling off from the centre lines), a building in every
## other lot with a height from the lot's hash.
static func grid(size: int = 60, every: int = 6, lot_bu_: float = 6.0) -> CityMotionSite:
	var s := CityMotionSite.new()
	s.lot_bu = lot_bu_
	s.origin_lot = Vector2(size, size) * 0.5
	var mid := size / 2
	var lines: Array[Dictionary] = []
	for axis in 2:
		for line in range(every / 2, size, every):
			var c := float(line) + 0.5
			var a := Vector2(c, 0.0) if axis == 0 else Vector2(0.0, c)
			var b := Vector2(c, float(size)) if axis == 0 else Vector2(float(size), c)
			var t := 1.0 - absf(float(line - mid)) / float(size)
			lines.append({"axis": axis, "line": line, "a": a, "b": b, "traffic": t, "n": size})
	lines.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		if x["traffic"] != y["traffic"]:
			return x["traffic"] > y["traffic"]
		if x["axis"] != y["axis"]:
			return x["axis"] < y["axis"]
		return x["line"] < y["line"])
	s.avenues = lines
	var key := 0
	for i in size:
		for j in size:
			var on_x := (i - every / 2) % every == 0
			var on_y := (j - every / 2) % every == 0
			if on_x or on_y:
				s.streets.append({"lot": Vector2i(i, j), "traffic": 0.6, "corner": on_x and on_y})
			elif (i + j) % 2 == 0:
				var h := 6.0 + 50.0 * fposmod(sin(float(i * 127 + j * 311)) * 43758.5453, 1.0)
				s.roofs.append({"pos": s.lot_to_world(Vector2(i + 0.5, j + 0.5), h), "h": h, "key": key})
				key += 1
	s.home = s.lot_to_world(Vector2(mid, mid))
	var lo := s.lot_to_world(Vector2.ZERO)
	s.bounds = AABB(lo, Vector3(size * lot_bu_, 60.0, size * lot_bu_))
	return s
