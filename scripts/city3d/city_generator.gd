class_name CityGenerator
extends RefCounted
## Plan 2 NA-12 (D3): the per-seed city layout, a planner-style city (DIRECTION_REVIEW "Horseshoe
## Bay" A2: the Cell hidden in the old core, the corporations on a ring round it at comparable
## distances, one side of the city open sea). Pure: every draw comes from the `rng` passed in
## (a named stream of the city seed, CityPlan.generate), every number from CampaignConfigData's
## `city_gen_*`, ties by id. The output is a CityPlan (lots); NeonCity builds the streets, lots
## and buildings on it as for the fixed city, so the layout rules (NA-11) and the async build
## see a city like any other.
##
## One attempt, in draw order: the coast (side, depth, wave), the Cell's centre (near the land's
## centre), the corporations round it (a shuffled order, an even turn with play, a radius in the
## ring), their pulls, the neutral Sprawl centres (best of `city_gen_candidates`), then each
## corporation's Site heading (the first, by angle, whose whole layout box is on land, inside the
## city and off every other HQ, with most of it in its own territory). An attempt whose HQ rects
## overlap, leave the city or touch the water, or a corporation with no heading, is drawn again;
## after `city_gen_attempts` the plan comes back with `fallback` set.

## The Site layout box is checked at SAMPLES x SAMPLES points (u, v in [-1, 1]).
const SAMPLES := 5


## A plan for `rng` (consumed), config `cfg`, city rect `city_rect` (lots), territories
## `corp_ids` (the Cell `cell_id` among them; its territory has no plaza), `hq_lots` square HQ
## rects and the Site layout `frame` (CityPlan.site_frame).
static func generate(rng: RandomNumberGenerator, cfg: CampaignConfigData, city_rect: Rect2i, corp_ids: Array, cell_id: StringName,
		hq_lots: int, frame: Dictionary) -> CityPlan:
	var ids := corp_ids.duplicate()
	IdSort.sort_ids(ids)
	var plan: CityPlan = null
	for attempt in cfg.city_gen_attempts:
		plan = _attempt(rng, cfg, city_rect, ids, cell_id, hq_lots, frame)
		plan.attempts = attempt + 1
		if not plan.fallback:
			return plan
	return plan


static func _attempt(rng: RandomNumberGenerator, cfg: CampaignConfigData, city_rect: Rect2i, ids: Array, cell_id: StringName,
		hq_lots: int, frame: Dictionary) -> CityPlan:
	var p := CityPlan.new()
	p.rect = city_rect
	# The coast.
	var side := rng.randi_range(0, 3)
	p.coast = {"side": side, "depth": rng.randf_range(cfg.city_gen_coast_depth.x, cfg.city_gen_coast_depth.y),
		"amp": rng.randf_range(cfg.city_gen_coast_wave.x, cfg.city_gen_coast_wave.y),
		"wavelength": rng.randf_range(cfg.city_gen_coast_wavelength.x, cfg.city_gen_coast_wavelength.y),
		"phase": rng.randf_range(0.0, TAU)}
	var inland: Vector2 = [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)][side]
	var land_centre := Vector2(city_rect.position) + Vector2(city_rect.size) * 0.5 + inland * float(p.coast["depth"]) * 0.5
	# The Cell, then the corporations round it.
	var half := float(hq_lots) * 0.5
	var centres := {}
	var jit := cfg.city_gen_cell_jitter
	centres[cell_id] = land_centre + Vector2(rng.randf_range(-jit, jit), rng.randf_range(-jit, jit))
	var ring: Array = []
	for id: StringName in ids:
		if id != cell_id:
			ring.append(id)
	for k in range(ring.size() - 1, 0, -1):
		var m := rng.randi_range(0, k)
		var tmp: Variant = ring[k]
		ring[k] = ring[m]
		ring[m] = tmp
	var step := TAU / maxf(1.0, float(ring.size()))
	var theta0 := rng.randf() * TAU
	for k in ring.size():
		var ang := theta0 + k * step + rng.randf_range(-1.0, 1.0) * cfg.city_gen_angle_jitter * step
		var rad := rng.randf_range(cfg.city_gen_ring_lots.x, cfg.city_gen_ring_lots.y)
		centres[ring[k]] = centres[cell_id] + Vector2(cos(ang), sin(ang)) * rad
	var at := {}
	for id: StringName in ids:
		var c: Vector2 = centres[id]
		at[id] = Vector2(roundi(c.x - half), roundi(c.y - half))
	var pulls := {}
	for id: StringName in ids:
		pulls[id] = rng.randf_range(cfg.city_gen_pull_range.x, cfg.city_gen_pull_range.y)
	for id: StringName in ids:
		p.territories.append({"id": id, "at": at[id], "pull": pulls[id]})
	# The neutral Sprawl centres: the candidate farthest from every territory so far.
	var inner := Rect2(city_rect.grow(-cfg.city_gen_edge_lots))
	for n in cfg.city_gen_neutral_count:
		var best := Vector2.INF
		var best_d := -1.0
		for k in cfg.city_gen_candidates:
			var q := Vector2(rng.randf_range(inner.position.x, inner.end.x), rng.randf_range(inner.position.y, inner.end.y))
			if p.land_depth(q.x, q.y) < cfg.city_gen_coast_clear:
				continue
			var d := INF
			for t in p.territories:
				d = minf(d, q.distance_to(t["at"]))
			if d > best_d:
				best_d = d
				best = q
		var pull := rng.randf_range(cfg.city_gen_neutral_pull_range.x, cfg.city_gen_neutral_pull_range.y)
		if best_d >= 0.0:
			p.territories.append({"id": &"", "at": Vector2(roundi(best.x), roundi(best.y)), "pull": pull})
	if not _hqs_ok(p, cfg, ids, hq_lots):
		p.fallback = true
		return p
	# Each corporation's Site heading.
	var rects := p.hq_rects(hq_lots)
	var aims := int(ceilf(360.0 / cfg.city_gen_aim_step_deg - 0.0001))
	for id: StringName in ids:
		var best_aim := -1.0
		var best_own := -1
		for k in aims:
			var deg := k * cfg.city_gen_aim_step_deg
			var own := _site_box_score(p, cfg, id, cell_id, rects, (at[id] as Vector2) + Vector2(half, half), deg, frame)
			if own > best_own:
				best_own = own
				best_aim = deg
		if best_own < 0:
			p.fallback = true
			return p
		p.site_aim[id] = best_aim
		p.site_mirror[id] = false
	return p


## True when every HQ rect is inside the city by `city_gen_edge_lots`, `city_gen_coast_clear`
## lots from the water, and every two HQ centres are `city_gen_hq_gap` apart.
static func _hqs_ok(p: CityPlan, cfg: CampaignConfigData, ids: Array, hq_lots: int) -> bool:
	var inner := p.rect.grow(-cfg.city_gen_edge_lots)
	var rects := p.hq_rects(hq_lots)
	for id: StringName in ids:
		var r: Rect2i = rects[id]
		if not inner.encloses(r):
			return false
		for q in [Vector2(r.position), Vector2(r.end.x, r.position.y), Vector2(r.end), Vector2(r.position.x, r.end.y)]:
			if p.land_depth(q.x, q.y) < cfg.city_gen_coast_clear:
				return false
	for a in ids.size():
		for b in range(a + 1, ids.size()):
			var ra: Rect2i = rects[ids[a]]
			var rb: Rect2i = rects[ids[b]]
			if Vector2(ra.get_center()).distance_to(Vector2(rb.get_center())) < cfg.city_gen_hq_gap:
				return false
	return true


## The Site layout box of `id` turned `deg` round HQ centre `centre`: -1 when a sample point
## leaves the city (by `city_gen_edge_lots`), comes within `city_gen_coast_clear` of the water or
## falls on another corporation's HQ rect (grown by 1; the Cell has no plaza), else how many
## samples lie in `id`'s own territory (nearest centre by pull, no border warp).
static func _site_box_score(p: CityPlan, cfg: CampaignConfigData, id: StringName, cell_id: StringName, rects: Dictionary,
		centre: Vector2, deg: float, frame: Dictionary) -> int:
	var inner := Rect2(p.rect.grow(-cfg.city_gen_edge_lots))
	var box := site_box(centre, deg, false, frame)
	var outline := PackedVector2Array([box[0], box[SAMPLES - 1], box[SAMPLES * SAMPLES - 1], box[SAMPLES * (SAMPLES - 1)]])
	var others: Array = rects.keys()
	IdSort.sort_ids(others)
	for other: StringName in others:
		if other == id or other == cell_id:
			continue
		var r := Rect2((rects[other] as Rect2i).grow(1))
		var poly := PackedVector2Array([r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)])
		if not Geometry2D.intersect_polygons(outline, poly).is_empty():
			return -1
	var own := 0
	for q in box:
		if not inner.has_point(q) or p.land_depth(q.x, q.y) < cfg.city_gen_coast_clear:
			return -1
		var best: StringName = &""
		var best_d := INF
		for t in p.territories:
			var d: float = q.distance_to(t["at"]) / float(t["pull"])
			if d < best_d:
				best_d = d
				best = t["id"]
		if best == id:
			own += 1
	return own


## SAMPLES x SAMPLES points (lots) spanning the Site layout box round HQ centre `centre`, turned
## `deg`, mirrored when `mirror` (CityLayout.site_points_aimed's frame: every Site lies inside).
static func site_box(centre: Vector2, deg: float, mirror: bool, frame: Dictionary) -> PackedVector2Array:
	var a: Vector2 = (frame["right"] as Vector2).rotated(deg_to_rad(deg))
	var b: Vector2 = (frame["down"] as Vector2).rotated(deg_to_rad(deg)) * (-1.0 if mirror else 1.0)
	var spread: float = frame["spread"]
	var run: float = float(frame["run_half"]) * spread
	var cross: float = float(frame["cross_half"]) * spread
	var origin := centre - a * (float(frame["boss_gap"]) + run) + b * float(frame["cross_offset"])
	var out := PackedVector2Array()
	for su in SAMPLES:
		for sv in SAMPLES:
			var u := float(su) / (SAMPLES - 1) * 2.0 - 1.0
			var v := float(sv) / (SAMPLES - 1) * 2.0 - 1.0
			out.append(origin + a * u * run + b * v * cross)
	return out
