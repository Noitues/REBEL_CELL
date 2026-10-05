class_name CityMotionSite
extends RefCounted
## ART-5 5c: the one seam between the city's motion layers and the city model they sit on.
## Everything the layers need from the city, as plain world-space data: the lot frame
## (world = (lot - origin_lot) * lot_bu on X / Z, height on Y), the avenues busiest first,
## the roofs (for billboards, aviation lights, searchlights, alarms), the street lots (for
## police strobes and street traffic), the Cell's home point and the bounds. Built from
## 5a's whole-city CityModel (`from_model`, the game's city) or 1D's spike district
## (`from_district`); the lab and the tests build a small grid (`grid`). Pure data.

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


## The site of 5a's city model `m` (CityModel: the whole city; `cfg` gives the lot frame);
## `home_lot` is the Cell's district centre in lots (the config's centre when omitted).
static func from_model(m: CityModel, cfg: CityConfig, home_lot: Vector2 = Vector2.INF) -> CityMotionSite:
	var s := _from(m.prisms, m.streets, cfg, home_lot)
	var r := cfg.city_rect
	var lo := s.lot_to_world(Vector2(r.position))
	var hi := s.lot_to_world(Vector2(r.end))
	var top := 0.0
	for rf in s.roofs:
		top = maxf(top, float(rf["h"]))
	s.bounds = AABB(lo, Vector3(hi.x - lo.x, top, hi.z - lo.z))
	return s


## The site of 1D's spike district `d` (its config gives the lot frame).
static func from_district(d: CityDistrict, cfg: CityConfig, home_lot: Vector2 = Vector2.INF) -> CityMotionSite:
	var s := _from(d.prisms, d.streets, cfg, home_lot)
	s.bounds = d.bounds()
	return s


static func _from(prisms: Array[Dictionary], streets_: Array[Dictionary], cfg: CityConfig, home_lot: Vector2) -> CityMotionSite:
	var s := CityMotionSite.new()
	s.lot_bu = cfg.lot_bu
	s.origin_lot = cfg.district_centre
	s.avenues = avenue_lines(streets_)
	var tops := {}
	for pr in prisms:
		var b := int(pr["building"])
		var top := float(pr["y0"]) + float(pr["h"])
		if not tops.has(b) or top > float(tops[b]["h"]):
			var c: Vector2 = pr["centre"]
			tops[b] = {"pos": Vector3(c.x, top, c.y), "h": top, "key": b}
	var keys: Array = tops.keys()
	keys.sort()
	for k: int in keys:
		s.roofs.append(tops[k])
	for st in streets_:
		s.streets.append({"lot": st["lot"], "traffic": float(st["traffic"]), "corner": bool(st["along_i"]) and bool(st["along_j"])})
	s.home = s.lot_to_world(cfg.district_centre if home_lot == Vector2.INF else home_lot)
	return s


## The avenue lines of street lots `streets_` ({"lot", "along_i", "along_j", "traffic"}),
## busiest first (mean traffic x lots; ties by axis, then line): the lot runs along one axis
## grouped by their line, each from its first to its last lot (1D's CityTraffic rule).
static func avenue_lines(streets_: Array[Dictionary]) -> Array[Dictionary]:
	var acc := {}
	for st in streets_:
		if st["along_i"] == st["along_j"]:
			continue
		var l: Vector2i = st["lot"]
		var axis := 0 if st["along_i"] else 1
		var line := l.x if axis == 0 else l.y
		var along := l.y if axis == 0 else l.x
		var key := Vector2i(axis, line)
		if not acc.has(key):
			acc[key] = {"axis": axis, "line": line, "lo": along, "hi": along, "sum": 0.0, "n": 0}
		var e: Dictionary = acc[key]
		e["lo"] = mini(e["lo"], along)
		e["hi"] = maxi(e["hi"], along)
		e["sum"] = float(e["sum"]) + float(st["traffic"])
		e["n"] = int(e["n"]) + 1
	var out: Array[Dictionary] = []
	for key: Vector2i in acc:
		var e: Dictionary = acc[key]
		var c := float(e["line"]) + 0.5
		var a := Vector2(c, e["lo"]) if e["axis"] == 0 else Vector2(e["lo"], c)
		var b := Vector2(c, int(e["hi"]) + 1) if e["axis"] == 0 else Vector2(int(e["hi"]) + 1, c)
		out.append({"axis": e["axis"], "line": e["line"], "a": a, "b": b, "traffic": float(e["sum"]) / int(e["n"]), "n": e["n"]})
	out.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		var tx: float = float(x["traffic"]) * int(x["n"])
		var ty: float = float(y["traffic"]) * int(y["n"])
		if tx != ty:
			return tx > ty
		if x["axis"] != y["axis"]:
			return x["axis"] < y["axis"]
		return x["line"] < y["line"])
	return out


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
