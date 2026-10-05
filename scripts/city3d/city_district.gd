class_name CityDistrict
extends RefCounted
## ART-1 1D: one district of the game's own city layout as world-space data for the
## unified-city renderers (3D and baked): every building extrusion as a prism (footprint,
## base, height, taper), the street lots with their lane colours and traffic, the plazas
## and HQ lots. Built from CityLayoutRecorder (seeded by the layout's look seed); pure
## data afterwards (the tests pick and project on it headless).

## Prisms: {"poly": PackedVector2Array (world X/Z), "y0", "h", "taper", "ink": Color,
## "terr": StringName, "key": int, "building": int, "centre": Vector2}.
var prisms: Array[Dictionary] = []
## Street lots: {"lot": Vector2i, "along_i", "along_j", "col": Color, "traffic": float}.
var streets: Array[Dictionary] = []
var plazas: Array[Dictionary] = []
var hqs: Dictionary = {}
var buildings: int = 0
var cfg: CitySpikeConfig


## Records the district of `cfg` from the game's layout (NeonCity, seed cfg.city_seed).
static func from_layout(p_cfg: CitySpikeConfig) -> CityDistrict:
	var rec := CityLayoutRecorder.new()
	rec.city_seed = p_cfg.city_seed
	var r := int(ceil(p_cfg.district_radius))
	var c := Vector2i(roundi(p_cfg.district_centre.x), roundi(p_cfg.district_centre.y))
	rec.record(Rect2i(c - Vector2i(r, r), Vector2i(r * 2 + 1, r * 2 + 1)))
	var d := from_recording(p_cfg, rec.extrusions, rec.streets, rec.plazas, rec.hqs)
	rec.free()
	return d


## Builds the district from recorded layout data (lots, height px), keeping what lies
## within the district radius.
static func from_recording(p_cfg: CitySpikeConfig, extrusions: Array[Dictionary], p_streets: Array[Dictionary],
		p_plazas: Array[Dictionary], p_hqs: Dictionary) -> CityDistrict:
	var d := CityDistrict.new()
	d.cfg = p_cfg
	var ids := {}
	for e in extrusions:
		var base: PackedVector2Array = e["base"]
		var c := Vector2.ZERO
		for p in base:
			c += p
		c /= base.size()
		if c.distance_to(p_cfg.district_centre) > p_cfg.district_radius:
			continue
		var poly := PackedVector2Array()
		for p in base:
			var w := CityIsoCamera.lot_to_world(p_cfg, p)
			poly.append(Vector2(w.x, w.z))
		var cell: Rect2i = e["cell"]
		if not ids.has(cell):
			ids[cell] = ids.size()
		var wc := CityIsoCamera.lot_to_world(p_cfg, c)
		d.prisms.append({"poly": poly, "y0": float(e["z0"]) * p_cfg.height_px_bu, "h": float(e["h"]) * p_cfg.height_px_bu,
			"taper": float(e["taper"]), "ink": e["ink"], "terr": e["terr"], "key": int(e["key"]), "building": ids[cell],
			"centre": Vector2(wc.x, wc.z)})
	d.buildings = ids.size()
	for s in p_streets:
		if Vector2(s["lot"]).distance_to(p_cfg.district_centre) <= p_cfg.district_radius:
			d.streets.append(s)
	for p in p_plazas:
		if Vector2(p["lot"]).distance_to(p_cfg.district_centre) <= p_cfg.district_radius + 10.0:
			d.plazas.append(p)
	d.hqs = p_hqs.duplicate()
	d._add_hq_stand_ins()
	return d


## The HQs within the district as stepped stand-in towers (the locked heroes are ART-5).
func _add_hq_stand_ins() -> void:
	var ids: Array = hqs.keys()
	ids.sort()
	for cid: StringName in ids:
		var r: Rect2i = hqs[cid]
		var c := Vector2(r.get_center())
		if c.distance_to(cfg.district_centre) > cfg.district_radius:
			continue
		buildings += 1
		for k in cfg.hq_tiers:
			var ins := cfg.hq_inset + k * cfg.hq_tier_inset
			var lo := Vector2(r.position) + Vector2(ins, ins)
			var hi := Vector2(r.end) - Vector2(ins, ins)
			var poly := PackedVector2Array()
			for q in [lo, Vector2(hi.x, lo.y), hi, Vector2(lo.x, hi.y)]:
				var w := CityIsoCamera.lot_to_world(cfg, q)
				poly.append(Vector2(w.x, w.z))
			var wc := CityIsoCamera.lot_to_world(cfg, c)
			prisms.append({"poly": poly, "y0": k * cfg.hq_tier_bu, "h": cfg.hq_tier_bu, "taper": 1.0,
				"ink": Palette.corp_color(cid), "terr": cid, "key": 7919 + k, "building": buildings - 1,
				"centre": Vector2(wc.x, wc.z), "hq": true})


## Index of the prism under screen pixel `p` for camera `cam` (nearest along the ray),
## or -1. Tapered prisms are tested at their mean width.
func pick(cam: CityIsoCamera, p: Vector2) -> int:
	var o := cam.ray_origin(p)
	var f := cam.forward()
	var best := -1
	var best_t := INF
	for n in prisms.size():
		var t := ray_prism(o, f, prisms[n])
		if t < best_t:
			best_t = t
			best = n
	return best


## The building (cell group) under screen pixel `p`, or -1.
func pick_building(cam: CityIsoCamera, p: Vector2) -> int:
	var n := pick(cam, p)
	return int(prisms[n]["building"]) if n >= 0 else -1


## Ray parameter where o + f t enters prism `pr` (convex footprint, y0..y0+h), or INF.
static func ray_prism(o: Vector3, f: Vector3, pr: Dictionary) -> float:
	var poly: PackedVector2Array = pr["poly"]
	var k := (1.0 + float(pr["taper"])) * 0.5
	var c: Vector2 = pr["centre"]
	var t0 := -INF
	var t1 := INF
	# Height slab.
	var y0: float = pr["y0"]
	var y1: float = y0 + float(pr["h"])
	if absf(f.y) < 1e-9:
		if o.y < y0 or o.y > y1:
			return INF
	else:
		var a := (y0 - o.y) / f.y
		var b := (y1 - o.y) / f.y
		t0 = maxf(t0, minf(a, b))
		t1 = minf(t1, maxf(a, b))
	# Side slabs: each footprint edge is a half-plane (outward normal away from the centre).
	var n := poly.size()
	for q in n:
		var pa := c + (poly[q] - c) * k
		var pb := c + (poly[(q + 1) % n] - c) * k
		var e := pb - pa
		var nrm := Vector2(e.y, -e.x)
		if nrm.dot(c - pa) > 0.0:
			nrm = -nrm
		var o2 := Vector2(o.x, o.z)
		var f2 := Vector2(f.x, f.z)
		var den := nrm.dot(f2)
		var num := nrm.dot(pa - o2)
		if absf(den) < 1e-9:
			if num < 0.0:
				return INF
			continue
		var t := num / den
		if den < 0.0:
			t0 = maxf(t0, t)
		else:
			t1 = minf(t1, t)
	if t0 > t1:
		return INF
	return t0


## World-space bounds of the district's prisms (X/Z) and the tallest top.
func bounds() -> AABB:
	var lo := Vector3(INF, 0.0, INF)
	var hi := Vector3(-INF, 0.0, -INF)
	for pr in prisms:
		for q: Vector2 in pr["poly"]:
			lo.x = minf(lo.x, q.x)
			lo.z = minf(lo.z, q.y)
			hi.x = maxf(hi.x, q.x)
			hi.z = maxf(hi.z, q.y)
		hi.y = maxf(hi.y, float(pr["y0"]) + float(pr["h"]))
	return AABB(lo, hi - lo)
