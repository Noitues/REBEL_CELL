class_name CityA2Builder
extends RefCounted
## CITY-A2 step 1 (D3): a city seed's city inside the art-pass planner city A2 (CityPlanA2 on the lot grid,
## CityA2Raster). A2's districts, coast, terrain and roads are fixed; the seed varies (1) the plan: each corporation's
## HQ spot near its A2 HQ inside its own district, the Cell's near the Old City centre, every Site layout's heading and
## mirror (`make_plan`, stream `CITY_LAYOUT_STREAM`), and (2) the lots: each district's local street spacing and
## phase, which lots merge into one building, building heights, tapers, setbacks and inks (`lots_for`, stream
## `CITY_BLOCKS_STREAM`). Pure: RNG streams of the city seed only, every number from CampaignConfigData `city_a2_*`,
## ties by id then lot (row order). Results are cached per seed (thread-safe; the async build records on workers).
##
## `lots_for` result: {"rect": Rect2i (the city rect), "kind": PackedByteArray (K_* per lot, row order), "streets":
## Dictionary index -> street record, "plazas": Dictionary index -> corp id, "cells": Array of {"cell": Rect2i,
## "extrusions": Array (CityLayoutRecorder's extrusion form)}, "front": Dictionary index -> cells index (the cell's
## front lot, `cell.end - 1`), "sites": Dictionary Vector2i -> true}.

const K_GROUND := 0
const K_STREET := 1
const K_PLAZA := 2
const K_BUILDING := 3
const K_WATER := 4
const K_PARK := 5
## CITY-A2 r2: open land, no building and no local street (steep or high ground, or the sprawl thinning past the ring).
const K_BARE := 6
## Lots round a Site's lot kept built whatever the open-land and corridor rules say (its marker needs a roof).
const SITE_KEEP := 2
## LOOK L5: the hash salt of the height spikes and the drowned quarter's sunk blocks.
const SPIKE_SALT := 7310

const DIRS: Array[Vector2i] = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]
## A Site heading score below any real one (a rejected heading).
const INF_SCORE := 1 << 20

static var _rasters: Dictionary = {}
static var _terrains: Dictionary = {}
static var _lots: Dictionary = {}
static var _mutex: Mutex = Mutex.new()


## The raster of `cfg`'s A2 plan over `city_rect` (grown by the margin), built once per config and rect.
static func raster(cfg: CampaignConfigData, city_rect: Rect2i, blend: float) -> CityA2Raster:
	var k := "%s|%s|%s" % [cfg.city_a2_path, city_rect, cfg.resource_path]
	_mutex.lock()
	var r: CityA2Raster = _rasters.get(k)
	if r == null:
		var a2 := CityPlanA2.shared(cfg.city_a2_path)
		if a2.errors.is_empty():
			r = CityA2Raster.make(a2, city_rect.grow(cfg.city_a2_raster_margin), cfg.city_a2_metres_per_lot,
				Vector2(city_rect.get_center()), cfg.city_a2_territories, cfg.city_a2_river_kinds, cfg.city_a2_road_half_min, blend)
			_rasters[k] = r
	_mutex.unlock()
	return r


## CITY-A2 step 2: the terrain of `cfg`'s A2 plan (CityA2Terrain, heights in BU of `lot_bu`), built once per config and
## rect; null when the A2 file does not load.
static func terrain(cfg: CampaignConfigData, city_rect: Rect2i, blend: float, lot_bu: float) -> CityA2Terrain:
	var ras := raster(cfg, city_rect, blend)
	if ras == null:
		return null
	var k := "%s|%s|%s|%s" % [cfg.city_a2_path, city_rect, cfg.resource_path, lot_bu]
	_mutex.lock()
	var t: CityA2Terrain = _terrains.get(k)
	if t == null:
		t = CityA2Terrain.make(ras, cfg, city_rect, lot_bu)
		_terrains[k] = t
	_mutex.unlock()
	return t


## Forgets the cached lots (tests: a rebuild from scratch).
static func forget() -> void:
	_mutex.lock()
	_lots.clear()
	_mutex.unlock()


## The plan of `p_seed`: A2's territories (the corporations of `corp_ids` with an A2 district, sorted by id, then the
## Sprawl neighbourhood centres), each HQ rect (`hq_lots` square) and Site heading, A2's coast and hills. `fallback` is
## set (with `failure`) when the A2 file does not load or a corporation finds no HQ spot or Site heading.
static func make_plan(p_seed: int, cfg: CampaignConfigData, city_rect: Rect2i, corp_ids: Array, cell_id: StringName,
		hq_lots: int, frame: Dictionary, blend: float, lot_bu: float) -> CityPlan:
	var p := CityPlan.new()
	p.city_seed = p_seed
	p.rect = city_rect
	var ras := raster(cfg, city_rect, blend)
	if ras == null:
		p.fallback = true
		p.failure = ",".join(CityPlanA2.shared(cfg.city_a2_path).errors)
		return p
	p.a2 = ras
	p.terrain = terrain(cfg, city_rect, blend, lot_bu)
	var rng := RngStreams.make_stream(p_seed, RngStreams.CITY_LAYOUT_STREAM)
	var ids: Array = corp_ids.duplicate()
	IdSort.sort_ids(ids)
	var rects := {}
	for id: StringName in ids:
		var d := _district_of(ras, cfg, id)
		if d.is_empty():
			continue
		var m: Vector2 = ras.a2.old_city_centre if id == cell_id else d["hq"]
		var at := _place_hq(ras, cfg, city_rect, id, ras.lot_of(m), hq_lots, rects, rng)
		if at == Vector2i(1 << 30, 1 << 30):
			p.fallback = true
			p.failure = "%s: no HQ spot" % id
			return p
		rects[id] = Rect2i(at, Vector2i(hq_lots, hq_lots))
		p.territories.append({"id": id, "at": Vector2(at), "pull": 1.0})
	for nb in ras.a2.neighbourhoods:
		var l := ras.lot_of(nb["centre"]).floor()
		if city_rect.has_point(Vector2i(l)) and ras.territory(int(l.x), int(l.y)) == &"" and not ras.is_water(int(l.x), int(l.y)):
			p.territories.append({"id": &"", "at": l, "pull": 1.0})
	p.coast = {"side": _sea_side(ras, city_rect), "a2": true}
	var scale := lot_bu / cfg.city_a2_metres_per_lot
	for h in ras.a2.hills:
		var s: Vector2 = h["sigma"]
		p.hills.append({"centre": ras.lot_of(h["centre"]), "sigma_x": s.x / cfg.city_a2_metres_per_lot,
			"sigma_y": s.y / cfg.city_a2_metres_per_lot, "height": float(h["height"]) * scale, "rotation": -float(h["rotation"])})
	var uvs: Dictionary = frame.get("uvs", {})
	for id: StringName in ids:
		if not rects.has(id) or not uvs.has(id):
			continue
		var aim := _aim(ras, cfg, city_rect, id, rects, frame, uvs[id], hq_lots, rng)
		if aim.is_empty():
			p.fallback = true
			p.failure = "%s: no Site heading" % id
			return p
		p.site_aim[id] = aim[0]
		p.site_mirror[id] = aim[1]
		for q: Vector2 in site_points_at(_centre(rects[id], hq_lots), aim[0], aim[1], frame, uvs[id]):
			p.a2_sites[Vector2i(q.floor())] = true
	return p


## The lots of `plan`'s city (cached per seed): `px_per_bu` turns BU heights into the recorder's height px.
static func lots_for(plan: CityPlan, cfg: CampaignConfigData, hq_lots: int, cell_id: StringName, px_per_bu: float) -> Dictionary:
	var key := "%d|%s|%s" % [plan.city_seed, cfg.resource_path, plan.rect]
	_mutex.lock()
	var out: Dictionary = _lots.get(key, {})
	if out.is_empty():
		out = _subdivide(plan, cfg, hq_lots, cell_id, px_per_bu)
		_lots[key] = out
	_mutex.unlock()
	return out


static func _district_of(ras: CityA2Raster, cfg: CampaignConfigData, id: StringName) -> Dictionary:
	var ds: Array = cfg.city_a2_territories.keys()
	IdSort.sort_ids(ds)
	for k: Variant in ds:
		if StringName(String(cfg.city_a2_territories[k])) == id:
			return ras.a2.district(StringName(String(k)))
	return {}


static func _centre(r: Rect2i, hq_lots: int) -> Vector2:
	return Vector2(r.position) + Vector2(hq_lots, hq_lots) * 0.5


## An HQ rect's top-left near `base` (lots, the wanted centre): `city_a2_hq_tries` jittered draws, then the spot itself,
## then the nearest fit within `city_a2_hq_search` lots (by distance, then row); Vector2i(1 << 30, 1 << 30) when none.
static func _place_hq(ras: CityA2Raster, cfg: CampaignConfigData, city_rect: Rect2i, id: StringName, base: Vector2, hq_lots: int,
		rects: Dictionary, rng: RandomNumberGenerator) -> Vector2i:
	var half := Vector2(hq_lots, hq_lots) * 0.5
	for k in cfg.city_a2_hq_tries:
		var off := Vector2(rng.randf_range(-1.0, 1.0), rng.randf_range(-1.0, 1.0)) * cfg.city_a2_hq_jitter
		var at := Vector2i((base + off - half).round())
		if _hq_ok(ras, cfg, city_rect, id, Rect2i(at, Vector2i(hq_lots, hq_lots)), rects):
			return at
	var at0 := Vector2i((base - half).round())
	var offs: Array[Vector2i] = []
	var s := cfg.city_a2_hq_search
	for dy in range(-s, s + 1):
		for dx in range(-s, s + 1):
			offs.append(Vector2i(dx, dy))
	offs.sort_custom(func(a: Vector2i, b: Vector2i) -> bool:
		var la := a.length_squared()
		var lb := b.length_squared()
		if la != lb:
			return la < lb
		return a.y < b.y if a.y != b.y else a.x < b.x)
	for o in offs:
		if _hq_ok(ras, cfg, city_rect, id, Rect2i(at0 + o, Vector2i(hq_lots, hq_lots)), rects):
			return at0 + o
	return Vector2i(1 << 30, 1 << 30)


## True when HQ rect `r` lies `city_gen_edge_lots` inside the city, every lot on land in `id`'s own territory, and
## `city_a2_hq_gap` lots off every rect in `rects`.
static func _hq_ok(ras: CityA2Raster, cfg: CampaignConfigData, city_rect: Rect2i, id: StringName, r: Rect2i, rects: Dictionary) -> bool:
	if not city_rect.grow(-cfg.city_gen_edge_lots).encloses(r):
		return false
	for o: Rect2i in rects.values():
		if o.grow(cfg.city_a2_hq_gap).intersects(r):
			return false
	for j in range(r.position.y, r.end.y):
		for i in range(r.position.x, r.end.x):
			if ras.is_water(i, j) or ras.territory(i, j) != id:
				return false
	return true


## [heading deg, mirrored] for `id`'s Site layout: every heading (`city_gen_aim_step_deg` apart) both ways, in a seeded
## order; a candidate whose every Site lot is in the city (by `city_gen_edge_lots`), `city_gen_coast_clear` from the
## water and off every HQ rect but the Cell's (grown by 1); the best score wins (+1 per Site in its own territory, -1 per
## Site on an A2 road or park lot, whose building then stands next to it; ties: the earlier in the seeded order).
## [] when none fits.
static func _aim(ras: CityA2Raster, cfg: CampaignConfigData, city_rect: Rect2i, id: StringName, rects: Dictionary, frame: Dictionary,
		uv: PackedVector2Array, hq_lots: int, rng: RandomNumberGenerator) -> Array:
	var cands: Array = []
	var steps := maxi(roundi(360.0 / cfg.city_gen_aim_step_deg), 1)
	for m in [false, true]:
		for s in steps:
			cands.append([float(s) * cfg.city_gen_aim_step_deg, m])
	for k in range(cands.size() - 1, 0, -1):
		var q := rng.randi_range(0, k)
		var t: Variant = cands[k]
		cands[k] = cands[q]
		cands[q] = t
	var inner := city_rect.grow(-cfg.city_gen_edge_lots)
	var centre := _centre(rects[id], hq_lots)
	var best: Array = []
	var best_score := -INF_SCORE
	for c: Array in cands:
		var score := 0
		for q: Vector2 in site_points_at(centre, c[0], c[1], frame, uv):
			var l := Vector2i(q.floor())
			if not inner.has_point(l) or ras.depth_at(q.x, q.y) < float(cfg.city_gen_coast_clear) or _on_hq(l, rects, id):
				score = -INF_SCORE
				break
			if ras.territory(l.x, l.y) == id:
				score += 1
			if ras.road_rank(l.x, l.y) > 0 or ras.is_park(l.x, l.y):
				score -= 1
		if score > best_score and score > -INF_SCORE:
			best_score = score
			best = c
	return best


## The Site points (lots) of a layout `uvs` (each in [-1, 1]^2, CityLayout.site_uvs) round HQ centre `centre`,
## turned `deg`, mirrored when `mirror` (CityLayout.site_points_aimed's formula; `frame`: CityPlan.site_frame).
static func site_points_at(centre: Vector2, deg: float, mirror: bool, frame: Dictionary, uvs: PackedVector2Array) -> PackedVector2Array:
	var a: Vector2 = (frame["right"] as Vector2).rotated(deg_to_rad(deg))
	var b: Vector2 = (frame["down"] as Vector2).rotated(deg_to_rad(deg)) * (-1.0 if mirror else 1.0)
	var spread: float = frame["spread"]
	var run: float = float(frame["run_half"]) * spread
	var cross: float = float(frame["cross_half"]) * spread
	var origin := centre - a * (float(frame["boss_gap"]) + run) + b * float(frame["cross_offset"])
	var out := PackedVector2Array()
	for uv in uvs:
		out.append(origin + a * uv.x * run + b * uv.y * cross)
	return out


## True when lot `l` is on `own`'s HQ rect or on another corporation's grown by 1 (the Cell's rect holds buildings,
## not a plaza, so it never counts).
static func _on_hq(l: Vector2i, rects: Dictionary, own: StringName) -> bool:
	for id: StringName in rects:
		if id == NeonCity.FIST_TERRITORY:
			continue
		var r: Rect2i = rects[id]
		if (r.grow(1) if id != own else r).has_point(l):
			return true
	return false


## The city rect's side holding the most sea lots (CityPlan.coast "side": 0 west, 1 east, 2 north, 3 south; ties by
## that order), for the water mesh's run axis.
static func _sea_side(ras: CityA2Raster, r: Rect2i) -> int:
	var counts := [0, 0, 0, 0]
	for j in range(r.position.y, r.end.y):
		for i in range(r.position.x, r.end.x):
			if not ras.is_water(i, j):
				continue
			var d := [i - r.position.x, r.end.x - 1 - i, j - r.position.y, r.end.y - 1 - j]
			var best := 0
			for k in range(1, 4):
				if d[k] < d[best]:
					best = k
			counts[best] += 1
	var side := 0
	for k in range(1, 4):
		if counts[k] > counts[side]:
			side = k
	return side


static func _subdivide(plan: CityPlan, cfg: CampaignConfigData, hq_lots: int, cell_id: StringName, px_per_bu: float) -> Dictionary:
	var ras: CityA2Raster = plan.a2
	var R := plan.rect
	var w := R.size.x
	var n := w * R.size.y
	var kind := PackedByteArray()
	kind.resize(n)
	var rank := PackedByteArray()
	rank.resize(n)
	var plazas := {}
	var rects := plan.hq_rects(hq_lots)
	var hq_ids: Array = rects.keys()
	IdSort.sort_ids(hq_ids)
	for id: StringName in hq_ids:
		if id == cell_id:
			continue
		var r: Rect2i = (rects[id] as Rect2i).intersection(R)
		for j in range(r.position.y, r.end.y):
			for i in range(r.position.x, r.end.x):
				var k := (j - R.position.y) * w + (i - R.position.x)
				kind[k] = K_PLAZA
				plazas[k] = id
	var zone := _site_zone(plan, cfg.city_a2_sprawl_site_keep)
	for k in n:
		if kind[k] != K_GROUND:
			continue
		var l := Vector2i(R.position.x + k % w, R.position.y + k / w)
		var rr := ras.road_rank(l.x, l.y)
		if rr > 0:
			kind[k] = K_STREET
			rank[k] = rr
		elif ras.is_water(l.x, l.y):
			kind[k] = K_WATER
		elif ras.is_park(l.x, l.y):
			kind[k] = K_PARK
		elif plan.terrain != null and ras.territory(l.x, l.y) == &"" and _bare(plan.terrain, cfg, l, zone) and not _near_site(plan, l) \
				and plan.terrain.outside_ring(l.x + 0.5, l.y + 0.5) > cfg.city_a2_sprawl_streets:
			# CITY-A2 r2: open Sprawl land past the suburbs gets no local streets either (no street grid to the rect's edge;
			# within `city_a2_sprawl_streets` lots of the ring the streets stay, the Sites' routes run on them).
			kind[k] = K_BARE
	var rng := RngStreams.make_stream(plan.city_seed, RngStreams.CITY_BLOCKS_STREAM)
	# Local streets: a seeded spacing and phase per A2 district (index 0 = outside every district).
	var grid: Array[Vector4i] = []
	for d in ras.a2.districts.size() + 1:
		var sx := rng.randi_range(cfg.city_a2_block_lots.x, cfg.city_a2_block_lots.y)
		var sy := rng.randi_range(cfg.city_a2_block_lots.x, cfg.city_a2_block_lots.y)
		grid.append(Vector4i(sx, sy, rng.randi_range(0, sx - 1), rng.randi_range(0, sy - 1)))
	# They run through parks and bridge rivers; every A2 district border is a street on both sides (the grids of two
	# districts meet on it, so the streets stay one network).
	for k in n:
		var l := Vector2i(R.position.x + k % w, R.position.y + k / w)
		if not (kind[k] == K_GROUND or kind[k] == K_PARK or (kind[k] == K_WATER and ras.is_river(l.x, l.y))):
			continue
		var di :=int(ras.district[ras.index(l.x, l.y)])
		var g := grid[di]
		var line := posmod(l.x - g.z, g.x) == 0 or posmod(l.y - g.w, g.y) == 0
		if not line and kind[k] != K_WATER:
			for d: Vector2i in DIRS:
				if int(ras.district[ras.index(l.x + d.x, l.y + d.y)]) != di:
					line = true
					break
		if line:
			kind[k] = K_STREET
	# A Site in a park gets its building: the park lots round it (3 x 3) are built on.
	for l: Vector2i in plan.a2_sites:
		for dj in range(-1, 2):
			for di in range(-1, 2):
				var q := l + Vector2i(di, dj)
				if R.has_point(q) and kind[(q.y - R.position.y) * w + (q.x - R.position.x)] == K_PARK:
					kind[(q.y - R.position.y) * w + (q.x - R.position.x)] = K_GROUND
	# Streets: their axis from their street neighbours, ink and traffic.
	var streets := {}
	var traffic_of := {}
	for c: StringName in CityPlanA2.ROAD_CLASSES:
		traffic_of[CityPlanA2.ROAD_CLASSES.find(c) + 1] = float(cfg.city_a2_traffic.get(c, cfg.city_a2_traffic[&"local"]))
	traffic_of[0] = float(cfg.city_a2_traffic[&"local"])
	for k in n:
		if kind[k] != K_STREET:
			continue
		var l := Vector2i(R.position.x + k % w, R.position.y + k / w)
		var ai := _street(kind, R, l + Vector2i(0, 1)) or _street(kind, R, l + Vector2i(0, -1))
		var aj := _street(kind, R, l + Vector2i(1, 0)) or _street(kind, R, l + Vector2i(-1, 0))
		if not ai and not aj:
			aj = true
		var rec := {"lot": l, "along_i": ai, "along_j": aj, "col": Color.BLACK, "traffic": 0.0}
		var t := ras.territory(l.x, l.y)
		var corp := t != &"" and t != cell_id and rng.randf() < cfg.city_a2_corp_ink_share
		var ink := Palette.corp_color(t) if corp else NeonCity.INKS[rng.randi() % NeonCity.INKS.size()]
		if not (ai and aj):
			rec["col"] = ink
			rec["traffic"] = traffic_of[int(rank[k])]
		streets[k] = rec
	# CITY-A2 r2: open land (no building; the streets stay, the Sites' routes need them): high or steep ground, the sprawl
	# thinning past the outer ring.
	if plan.terrain != null:
		for k in n:
			if kind[k] == K_GROUND:
				var l := Vector2i(R.position.x + k % w, R.position.y + k / w)
				if _bare(plan.terrain, cfg, l, zone) and not _near_site(plan, l):
					kind[k] = K_BARE
	# CITY-A2 r2: the elevated roads' corridors (art-pass zoning `clear`): no building within `city_a2_corridor` lots of a
	# ring / motorway / truck road's lots (streets still cross under the decks).
	for rd: Dictionary in ras.a2.roads:
		var reach: int = int(cfg.city_a2_corridor.get(rd["class"], 0))
		if reach <= 0 or not ras.road_lots.has(rd["id"]):
			continue
		for l: Vector2i in ras.road_lots[rd["id"]]:
			for dj in range(-reach, reach + 1):
				for di in range(-reach, reach + 1):
					var q := l + Vector2i(di, dj)
					if R.has_point(q):
						var kq := (q.y - R.position.y) * w + (q.x - R.position.x)
						if kind[kq] == K_GROUND and not _near_site(plan, q):
							kind[kq] = K_BARE
	# Buildings: row order; a lot may merge with its east or south neighbour.
	var cells: Array = []
	var front := {}
	var owner := PackedInt32Array()
	owner.resize(n)
	owner.fill(-1)
	var hq_centres: Array[Vector2] = []
	for id: StringName in hq_ids:
		if id != cell_id:
			hq_centres.append(_centre(rects[id], hq_lots))
	for k in n:
		if kind[k] != K_GROUND or owner[k] >= 0:
			continue
		var l := Vector2i(R.position.x + k % w, R.position.y + k / w)
		var cell := Rect2i(l, Vector2i.ONE)
		if rng.randf() < cfg.city_a2_merge_share:
			var d := Vector2i(1, 0) if rng.randi() % 2 == 0 else Vector2i(0, 1)
			var q := l + d
			if R.has_point(q):
				var kq := (q.y - R.position.y) * w + (q.x - R.position.x)
				if kind[kq] == K_GROUND and owner[kq] < 0 and ras.territory(q.x, q.y) == ras.territory(l.x, l.y) \
						and not plan.a2_sites.has(q) and not plan.a2_sites.has(l):
					cell = Rect2i(l, Vector2i.ONE + d)
		var ci := cells.size()
		for j in range(cell.position.y, cell.end.y):
			for i in range(cell.position.x, cell.end.x):
				var kk := (j - R.position.y) * w + (i - R.position.x)
				owner[kk] = ci
				kind[kk] = K_BUILDING
		var f := cell.end - Vector2i.ONE
		front[(f.y - R.position.y) * w + (f.x - R.position.x)] = ci
		cells.append({"cell": cell, "extrusions": _extrusions(ras, cfg, cell, cell_id, hq_centres, px_per_bu, rng, plan.terrain, plan.a2_sites)})
	return {"rect": R, "kind": kind, "streets": streets, "plazas": plazas, "cells": cells, "front": front, "sites": plan.a2_sites}


## CITY-A2 r2 (art-pass zoning_a2.py): lot `l` stays open land: its ground is over `city_a2_max_build_h` or steeper than
## `city_a2_max_build_slope`, or past the outer ring (by the terrain's broad noise x `city_a2_edge_noise`) its jitter is
## over the chance of a building there (1 at the ring, 0 past `city_a2_sprawl_fade`).
## `zone`: the lots within `city_a2_sprawl_site_keep` of a Site, where the sprawl does not thin (their run streets keep
## their frontage).
static func _bare(t: CityA2Terrain, cfg: CampaignConfigData, l: Vector2i, zone: Dictionary) -> bool:
	var c := Vector2(l) + Vector2(0.5, 0.5)
	if t.height_at(c.x, c.y) > cfg.city_a2_max_build_h or t.slope_at(c.x, c.y) > cfg.city_a2_max_build_slope:
		return true
	var d := t.outside_ring(c.x, c.y)
	if d <= 0.0 or zone.has(l):
		return false
	return t.jitter(l.x, l.y) >= _keep(t, cfg, l)


## LOOK L5: the chance (0..1) lot `l` past the outer ring keeps its building: the sprawl's fade past the ring (moved by the
## broad noise), x the dwindle toward the highest / steepest buildable ground and the plan rect's edge (1 inside the ring).
static func _keep(t: CityA2Terrain, cfg: CampaignConfigData, l: Vector2i) -> float:
	var c := Vector2(l) + Vector2(0.5, 0.5)
	var d := t.outside_ring(c.x, c.y)
	if d <= 0.0:
		return 1.0
	d = maxf(d + (t.noise_at(c.x, c.y) * 2.0 - 1.0) * cfg.city_a2_edge_noise, 0.0)
	var p := 1.0 - _smooth01(d, cfg.city_a2_sprawl_fade)
	var dw := cfg.city_a2_dwindle
	if dw.x < 1.0:
		p *= 1.0 - _smooth01(t.height_at(c.x, c.y), Vector2(cfg.city_a2_max_build_h * dw.x, cfg.city_a2_max_build_h))
	if dw.y < 1.0:
		p *= 1.0 - _smooth01(t.slope_at(c.x, c.y), Vector2(cfg.city_a2_max_build_slope * dw.y, cfg.city_a2_max_build_slope))
	if dw.z > 0.0:
		var fr := t.fine_rect
		var e := minf(minf(c.x - fr.position.x, fr.end.x - c.x), minf(c.y - fr.position.y, fr.end.y - c.y))
		p *= _smooth01(e, Vector2(0.0, dw.z))
	return p


## A height in `hr` at curve point `u` (0..1) bent by exponent `p` (1 = even).
static func _curve(u: float, hr: Vector2, p: float) -> float:
	return lerpf(hr.x, hr.y, pow(u, p))


static func _smooth01(x: float, r: Vector2) -> float:
	var t := clampf((x - r.x) / (r.y - r.x), 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)


## The lots within `reach` of any Site's lot (a set).
static func _site_zone(plan: CityPlan, reach: int) -> Dictionary:
	var out := {}
	for s: Vector2i in plan.a2_sites:
		for dj in range(-reach, reach + 1):
			for di in range(-reach, reach + 1):
				out[s + Vector2i(di, dj)] = true
	return out


## True when lot `l` is within SITE_KEEP lots of a Site's lot (its buildings stay).
static func _near_site(plan: CityPlan, l: Vector2i) -> bool:
	for dj in range(-SITE_KEEP, SITE_KEEP + 1):
		for di in range(-SITE_KEEP, SITE_KEEP + 1):
			if plan.a2_sites.has(l + Vector2i(di, dj)):
				return true
	return false


static func _street(kind: PackedByteArray, R: Rect2i, l: Vector2i) -> bool:
	return R.has_point(l) and kind[(l.y - R.position.y) * R.size.x + (l.x - R.position.x)] == K_STREET


## The height kind of a building at lot `l`: its A2 neighbourhood's kind (CityA2Raster.neighbourhood_kind) when that
## kind has heights, else corp / old_core (the Cell's territory) / sprawl.
static func _height_kind(ras: CityA2Raster, cfg: CampaignConfigData, l: Vector2i, terr: StringName, cell_id: StringName) -> StringName:
	# LOOK L5 (whole-city plate parity): a corporation's own height range (`corp_<id>`) wins over the A2 neighbourhood kind,
	# so each corp district keeps the plate's massing (Orbital's glass spires, Meridian's low port blocks).
	var ck := StringName("corp_%s" % terr)
	if terr != &"" and terr != cell_id and cfg.city_a2_heights.has(ck):
		return ck
	# ... then an A2 district's own (`a2_<id>`: Tethys, which is no game territory, has its drowned spires).
	var di := int(ras.district[ras.index(l.x, l.y)])
	if di > 0:
		var dk := StringName("a2_%s" % String(ras.a2.districts[di - 1]["id"]))
		if cfg.city_a2_heights.has(dk):
			return dk
	var nk := ras.neighbourhood_kind(l.x, l.y)
	if nk != &"" and cfg.city_a2_heights.has(nk):
		return nk
	if terr == cell_id:
		return &"old_core"
	return &"corp" if terr != &"" else &"sprawl"


## A building cell's extrusions (lots, height px): one prism, or a base and a setback tower over `city_a2_setback_from`.
static func _extrusions(ras: CityA2Raster, cfg: CampaignConfigData, cell: Rect2i, cell_id: StringName, hq_centres: Array[Vector2],
		px_per_bu: float, rng: RandomNumberGenerator, t: CityA2Terrain = null, sites: Dictionary = {}) -> Array:
	var f := cell.end - Vector2i.ONE
	var terr := ras.territory(f.x, f.y)
	var hk := _height_kind(ras, cfg, f, terr, cell_id)
	var hr: Vector2 = cfg.city_a2_heights[hk]
	var hp := float(cfg.city_a2_height_pow.get(hk, 1.0))
	var h := _curve(rng.randf(), hr, hp)
	# LOOK L5: a few lots stand out of the roofline (a hash of the lot: no extra draw from the layout stream).
	var spike := 1.0
	if CityMeshKit.hash01(SPIKE_SALT, cell.position.x, cell.position.y) < cfg.city_a2_height_spike.x:
		spike = cfg.city_a2_height_spike.y
	h *= spike
	if t != null:
		h *= lerpf(cfg.city_a2_dwindle_h_min, 1.0, _keep(t, cfg, f))
	# LOOK L5: the drowned quarter's sunk blocks: base under the ground, top under the water (Sites' buildings stand).
	var z_sink := 0.0
	if cfg.city_a2_sink_share > 0.0 and not sites.has(f) and not ras.a2.drowned.is_empty() 			and CityMeshKit.hash01(SPIKE_SALT + 1, cell.position.x, cell.position.y) < cfg.city_a2_sink_share 			and Geometry2D.is_point_in_polygon(ras.metres_of(Vector2(cell.get_center())), ras.a2.drowned):
		var sk := lerpf(cfg.city_a2_sink_bu.x, cfg.city_a2_sink_bu.y, CityMeshKit.hash01(SPIKE_SALT + 2, cell.position.x, cell.position.y))
		z_sink = sk
		h = minf(h, sk * 0.9)
	var c := Vector2(cell.get_center())
	var near := INF
	for q in hq_centres:
		near = minf(near, c.distance_to(q))
	var rise := 1.0 + cfg.city_a2_hq_rise * maxf(0.0, 1.0 - near / cfg.city_a2_hq_rise_lots)
	h *= rise
	var taper := rng.randf_range(cfg.city_a2_taper.x, cfg.city_a2_taper.y)
	var corp := terr != &"" and terr != cell_id and rng.randf() < cfg.city_a2_corp_ink_share
	var ink := Palette.corp_color(terr) if corp else NeonCity.INKS[rng.randi() % NeonCity.INKS.size()]
	var key := rng.randi() & 0x7fffffff
	var ins := cfg.city_a2_inset
	var out: Array = []
	# LOOK L5: the plate's finer grain: four quarter-lot buildings on one lot.
	if cfg.city_a2_sub_share > 0.0 and cell.size == Vector2i.ONE and h < cfg.city_a2_setback_from 			and cfg.city_a2_sub_kinds.has(hk) and rng.randf() < cfg.city_a2_sub_share:
		var si := cfg.city_a2_sub_inset
		for q in 4:
			var lo := Vector2(cell.position) + Vector2(0.5 * (q % 2), 0.5 * (q / 2)) + Vector2(si, si)
			var hi := lo + Vector2(0.5 - 2.0 * si, 0.5 - 2.0 * si)
			var hq := _curve(rng.randf(), hr, hp) * cfg.city_a2_sub_h_k * rise * spike
			if t != null:
				hq *= lerpf(cfg.city_a2_dwindle_h_min, 1.0, _keep(t, cfg, f))
			if z_sink > 0.0:
				hq = minf(hq, z_sink * 0.9)
			out.append(_extrusion_q(cell, lo, hi, -z_sink * px_per_bu, hq * px_per_bu, taper, ink, terr, key + 2 + q))
		return out
	if z_sink > 0.0:
		out.append(_extrusion(cell, ins, -z_sink * px_per_bu, h * px_per_bu, taper, ink, terr, key))
	elif h >= cfg.city_a2_setback_from:
		var h0 := h * cfg.city_a2_setback.y
		out.append(_extrusion(cell, ins, 0.0, h0 * px_per_bu, 1.0, ink, terr, key))
		var ins2 := minf(ins + cfg.city_a2_setback.x, 0.45)
		out.append(_extrusion(cell, ins2, h0 * px_per_bu, (h - h0) * px_per_bu, taper, ink, terr, key + 1))
	else:
		out.append(_extrusion(cell, ins, 0.0, h * px_per_bu, taper, ink, terr, key))
	return out


static func _extrusion(cell: Rect2i, ins: float, z0: float, h: float, taper: float, ink: Color, terr: StringName, key: int) -> Dictionary:
	return _extrusion_q(cell, Vector2(cell.position) + Vector2(ins, ins), Vector2(cell.end) - Vector2(ins, ins), z0, h, taper, ink, terr, key)


## An extrusion over the lot rect lo..hi (lots) of building cell `cell`.
static func _extrusion_q(cell: Rect2i, lo: Vector2, hi: Vector2, z0: float, h: float, taper: float, ink: Color, terr: StringName,
		key: int) -> Dictionary:
	return {"base": PackedVector2Array([lo, Vector2(hi.x, lo.y), hi, Vector2(lo.x, hi.y)]), "z0": z0, "h": h, "taper": taper,
		"ink": ink, "terr": terr, "key": key, "cell": cell}
