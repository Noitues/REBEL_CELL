class_name CityModel
extends RefCounted
## ART-5 5a: the production city model (bible §4.1 "one model, one camera", §6.1
## `CityModel`): the WHOLE city of the game's own layout (NeonCity's streets, lots,
## territories, buildings and HQ lots, read through CityLayoutRecorder) as world-space
## data, split into square chunks of `chunk_lots` lots so the renderer gives each chunk its
## own MultiMesh per building family (frustum culling) and picking only tests the chunks
## the ray crosses. Pure data after the recording (headless-testable: projection, picking,
## chunking); deterministic (chunks in row order, each chunk's lots in the layout's draw
## order). Successor of 1D's CityDistrict, which stays for the spike.
##
## Prisms: {"poly": PackedVector2Array (world X/Z), "y0", "h", "taper", "ink": Color,
## "terr": StringName, "key": int, "building": int, "cell": Rect2i (lots; HQ: its rect),
## "centre": Vector2 (world X/Z), "chunk": Vector2i, "hq": bool}.

var cfg: CityConfig
var city_seed: int = 0
var prisms: Array[Dictionary] = []
## Street lots: {"lot": Vector2i, "along_i", "along_j", "col": Color, "traffic": float}.
var streets: Array[Dictionary] = []
## Plaza (HQ) lots: {"lot": Vector2i, "terr": StringName}.
var plazas: Array[Dictionary] = []
## HQ rects (lots): corp id -> Rect2i.
var hqs: Dictionary = {}
## chunk (Vector2i) -> {"rect": Rect2i (lots), "prisms": PackedInt32Array,
## "streets": PackedInt32Array, "plazas": PackedInt32Array, "top": float (tallest top, BU)}.
var chunks: Dictionary = {}
var buildings: int = 0

## Built models, by config path and seed (a view cache: the layout is a pure function of
## the seed; the game's city is built once per process).
static var _shared: Dictionary = {}


## The chunk keys covering `rect` (lots), row by row.
static func chunk_keys(p_cfg: CityConfig, rect: Rect2i) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	var n := p_cfg.chunk_lots
	var lo := Vector2i(floori(float(rect.position.x) / n), floori(float(rect.position.y) / n))
	var hi := Vector2i(floori(float(rect.end.x - 1) / n), floori(float(rect.end.y - 1) / n))
	for cy in range(lo.y, hi.y + 1):
		for cx in range(lo.x, hi.x + 1):
			out.append(Vector2i(cx, cy))
	return out


## The lots of chunk `key`, clipped to the city rect.
static func chunk_rect(p_cfg: CityConfig, key: Vector2i) -> Rect2i:
	var n := p_cfg.chunk_lots
	return Rect2i(key * n, Vector2i(n, n)).intersection(p_cfg.city_rect)


## A recorder for one chunk (made on the main thread; `record` may run on a worker).
static func recorder(p_seed: int) -> CityLayoutRecorder:
	var rec := CityLayoutRecorder.new()
	rec.city_seed = p_seed
	return rec


## The whole city (or the chunks of `rect` when given), recorded on this thread.
static func build(p_cfg: CityConfig, p_seed: int, rect: Rect2i = Rect2i()) -> CityModel:
	var m := CityModel.new()
	m.cfg = p_cfg
	m.city_seed = p_seed
	var box := p_cfg.city_rect if rect.size == Vector2i.ZERO else rect.intersection(p_cfg.city_rect)
	for key in chunk_keys(p_cfg, box):
		var r := chunk_rect(p_cfg, key).intersection(box)
		if r.size.x <= 0 or r.size.y <= 0:
			continue
		var rec := recorder(p_seed)
		rec.record(r)
		m.add_recording(key, r, rec)
		rec.free()
	m.finish()
	return m


## The game's city for `p_seed`, built once and shared (every scene reads the same one).
static func shared(p_cfg: CityConfig, p_seed: int) -> CityModel:
	var k := "%s|%d" % [p_cfg.resource_path, p_seed]
	if not _shared.has(k):
		_shared[k] = build(p_cfg, p_seed)
	return _shared[k]


## The shared model when it is built already, else null.
static func shared_if_built(p_cfg: CityConfig, p_seed: int) -> CityModel:
	return _shared.get("%s|%d" % [p_cfg.resource_path, p_seed])


## Keeps `m` as the shared model of its config and seed (an async build landing).
static func keep_shared(m: CityModel) -> void:
	_shared["%s|%d" % [m.cfg.resource_path, m.city_seed]] = m


## Adds chunk `key` (lots `r`) from a finished recording. Call in chunk order.
func add_recording(key: Vector2i, r: Rect2i, rec: CityLayoutRecorder) -> void:
	var ch := {"rect": r, "prisms": PackedInt32Array(), "streets": PackedInt32Array(), "plazas": PackedInt32Array(),
		"top": 0.0}
	var ids := {}
	for e in rec.extrusions:
		var cell: Rect2i = e["cell"]
		if not ids.has(cell):
			ids[cell] = buildings + ids.size()
		var pr := prism_of(cfg, e)
		pr["building"] = ids[cell]
		pr["chunk"] = key
		ch["prisms"].append(prisms.size())
		ch["top"] = maxf(float(ch["top"]), float(pr["y0"]) + float(pr["h"]))
		prisms.append(pr)
	buildings += ids.size()
	for s in rec.streets:
		ch["streets"].append(streets.size())
		streets.append(s)
	for p in rec.plazas:
		ch["plazas"].append(plazas.size())
		plazas.append(p)
	for cid: StringName in rec.hqs:
		hqs[cid] = rec.hqs[cid]
	chunks[key] = ch


## After the last chunk: the HQ stand-ins (stepped towers until the landmarks land, 5b),
## each in the chunk holding its rect's centre.
func finish() -> void:
	var ids: Array = hqs.keys()
	ids.sort()
	for cid: StringName in ids:
		var r: Rect2i = hqs[cid]
		var c := Vector2(r.get_center())
		var key := Vector2i(floori(c.x / cfg.chunk_lots), floori(c.y / cfg.chunk_lots))
		if not chunks.has(key):
			continue
		var ch: Dictionary = chunks[key]
		var wc := CityIsoCamera.lot_to_world(cfg, c)
		for k in cfg.hq_tiers:
			var ins := cfg.hq_inset + k * cfg.hq_tier_inset
			var lo := Vector2(r.position) + Vector2(ins, ins)
			var hi := Vector2(r.end) - Vector2(ins, ins)
			var poly := PackedVector2Array()
			for q in [lo, Vector2(hi.x, lo.y), hi, Vector2(lo.x, hi.y)]:
				var w := CityIsoCamera.lot_to_world(cfg, q)
				poly.append(Vector2(w.x, w.z))
			ch["prisms"].append(prisms.size())
			ch["top"] = maxf(float(ch["top"]), (k + 1) * cfg.hq_tier_bu)
			prisms.append({"poly": poly, "y0": k * cfg.hq_tier_bu, "h": cfg.hq_tier_bu, "taper": 1.0,
				"ink": Palette.corp_color(cid), "terr": cid, "key": 7919 + k, "building": buildings, "cell": r,
				"centre": Vector2(wc.x, wc.z), "chunk": key, "hq": true})
		buildings += 1


## One recorded extrusion (lots, height px) as a world prism.
static func prism_of(p_cfg: CityConfig, e: Dictionary) -> Dictionary:
	var base: PackedVector2Array = e["base"]
	var c := Vector2.ZERO
	for p in base:
		c += p
	c /= base.size()
	var poly := PackedVector2Array()
	for p in base:
		var w := CityIsoCamera.lot_to_world(p_cfg, p)
		poly.append(Vector2(w.x, w.z))
	var wc := CityIsoCamera.lot_to_world(p_cfg, c)
	return {"poly": poly, "y0": float(e["z0"]) * p_cfg.height_px_bu, "h": float(e["h"]) * p_cfg.height_px_bu,
		"taper": float(e["taper"]), "ink": e["ink"], "terr": e["terr"], "key": int(e["key"]), "cell": e["cell"],
		"centre": Vector2(wc.x, wc.z), "hq": false}


## The world box of chunk `key`: its lots, grown to every prism it holds (a merged cell or an
## HQ reaches past its front lot's chunk), ground to its tallest top.
func chunk_aabb(key: Vector2i) -> AABB:
	var ch: Dictionary = chunks[key]
	if ch.has("box"):
		return ch["box"]
	var r: Rect2i = ch["rect"]
	var a := CityIsoCamera.lot_to_world(cfg, Vector2(r.position))
	var b := CityIsoCamera.lot_to_world(cfg, Vector2(r.end))
	var lo := Vector3(minf(a.x, b.x), 0.0, minf(a.z, b.z))
	var hi := Vector3(maxf(a.x, b.x), 0.0, maxf(a.z, b.z))
	for n: int in ch["prisms"]:
		var pr := prisms[n]
		for q: Vector2 in pr["poly"]:
			lo = Vector3(minf(lo.x, q.x), 0.0, minf(lo.z, q.y))
			hi = Vector3(maxf(hi.x, q.x), 0.0, maxf(hi.z, q.y))
		hi.y = maxf(hi.y, float(pr["y0"]) + float(pr["h"]))
	var box := AABB(lo, hi - lo)
	ch["box"] = box
	return box


## The chunk keys, sorted (row by row).
func keys() -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for k: Vector2i in chunks:
		out.append(k)
	out.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.y < b.y if a.y != b.y else a.x < b.x)
	return out


# --- Picking API (5c / 5d / the views; pure, by screen pixel) ---------------------------------

## The prism under screen pixel `p` for camera `cam` (nearest along the ray), or -1. Only
## the chunks the ray crosses are tested; ties by prism index.
func pick(cam: CityIsoCamera, p: Vector2) -> int:
	var o := cam.ray_origin(p)
	var f := cam.forward()
	var best := -1
	var best_t := INF
	for key in keys():
		if not _ray_hits(o, f, chunk_aabb(key)):
			continue
		for n: int in chunks[key]["prisms"]:
			var t := CityDistrict.ray_prism(o, f, prisms[n])
			if t < best_t:
				best_t = t
				best = n
	return best


## What is under screen pixel `p`: {"prism": int, "building": int, "cell": Rect2i,
## "lot": Vector2i (the ground lot when no building is hit), "terr": StringName,
## "world": Vector3 (the ground point under the pixel)}.
func pick_info(cam: CityIsoCamera, p: Vector2) -> Dictionary:
	var g := cam.unproject(p, 0.0)
	var lot := CityIsoCamera.world_to_lot(cfg, g)
	var out := {"prism": -1, "building": -1, "cell": Rect2i(), "lot": Vector2i(floori(lot.x), floori(lot.y)),
		"terr": &"", "world": g}
	var n := pick(cam, p)
	if n >= 0:
		var pr := prisms[n]
		out["prism"] = n
		out["building"] = pr["building"]
		out["cell"] = pr["cell"]
		out["terr"] = pr["terr"]
		var cell: Rect2i = pr["cell"]
		out["lot"] = cell.end - Vector2i.ONE
	return out


## The building id under screen pixel `p`, or -1.
func pick_building(cam: CityIsoCamera, p: Vector2) -> int:
	var n := pick(cam, p)
	return int(prisms[n]["building"]) if n >= 0 else -1


## The ground lot under screen pixel `p` (buildings ignored).
func lot_at(cam: CityIsoCamera, p: Vector2) -> Vector2i:
	var l := CityIsoCamera.world_to_lot(cfg, cam.unproject(p, 0.0))
	return Vector2i(floori(l.x), floori(l.y))


## The tallest top (BU) over lot `lot` (0 = no building), for markers floating over roofs.
func top_at(lot: Vector2i) -> float:
	var key := Vector2i(floori(float(lot.x) / cfg.chunk_lots), floori(float(lot.y) / cfg.chunk_lots))
	if not chunks.has(key):
		return 0.0
	var top := 0.0
	for n: int in chunks[key]["prisms"]:
		var pr := prisms[n]
		if (pr["cell"] as Rect2i).has_point(lot):
			top = maxf(top, float(pr["y0"]) + float(pr["h"]))
	return top


## The whole city's world box.
func bounds() -> AABB:
	var out := AABB()
	var first := true
	for key in keys():
		var b := chunk_aabb(key)
		out = b if first else out.merge(b)
		first = false
	return out


## Slab test: does the line o + f t cross box `b`?
static func _ray_hits(o: Vector3, f: Vector3, b: AABB) -> bool:
	var t0 := -INF
	var t1 := INF
	for axis in 3:
		var lo := b.position[axis]
		var hi := b.end[axis]
		if absf(f[axis]) < 1e-9:
			if o[axis] < lo or o[axis] > hi:
				return false
			continue
		var a := (lo - o[axis]) / f[axis]
		var c := (hi - o[axis]) / f[axis]
		t0 = maxf(t0, minf(a, c))
		t1 = minf(t1, maxf(a, c))
	return t0 <= t1
