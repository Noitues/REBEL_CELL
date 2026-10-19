class_name CityGenerator
extends RefCounted
## Plan 2 NA-12 (D3): the per-seed city layout, a planner-style city (DIRECTION_REVIEW "Horseshoe
## Bay" A2: one side of the city open sea with a concave bay, the Cell hidden in the old core at
## the bay's head, the corporations on an arc round it at comparable distances facing inland, the
## shore corporations (Tethys) on a bay flank touching the water; plus terrain hills as data).
## Pure: every draw comes from the `rng` passed in
## (a named stream of the city seed, CityPlan.generate), every number from CampaignConfigData's
## `city_gen_*`, ties by id. The output is a CityPlan (lots); NeonCity builds the streets, lots
## and buildings on it as for the fixed city, so the layout rules (NA-11) and the async build
## see a city like any other.
##
## One attempt, in draw order: the coast (side, depth, two waves, the bay), the Cell (its HQ at the
## bay head), the corporations round it (a shuffled order on the inland arc, play, a radius in the
## ring; shore ones on a bay flank), their pulls, the Sprawl centres, the hills, then each
## corporation's Site heading (the first, by angle, whose whole layout box is on land, inside the
## city and off every other HQ, with most of it in its own territory). An attempt whose HQ rects
## overlap, leave the city or touch the water, or a corporation with no heading, is drawn again;
## after `city_gen_attempts` the plan comes back with `fallback` set.

## The Site layout box is checked at SAMPLES x SAMPLES points (u, v in [-1, 1]).
const SAMPLES := 5
## The most single-lot moves that settle a shore HQ on the water's edge.
const SHORE_STEPS := 12


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
	# The coast: a sea side, its waves and the A2 bay (a Gaussian bump of the shore into the land).
	var side := rng.randi_range(0, 3)
	var span := float(city_rect.size.y if side < 2 else city_rect.size.x)
	var lo := float(city_rect.position.y if side < 2 else city_rect.position.x)
	p.coast = {"side": side, "depth": rng.randf_range(cfg.city_gen_coast_depth.x, cfg.city_gen_coast_depth.y),
		"amp": rng.randf_range(cfg.city_gen_coast_wave.x, cfg.city_gen_coast_wave.y),
		"wavelength": rng.randf_range(cfg.city_gen_coast_wavelength.x, cfg.city_gen_coast_wavelength.y),
		"phase": rng.randf_range(0.0, TAU),
		"amp2": rng.randf_range(cfg.city_gen_coast_wave2.x, cfg.city_gen_coast_wave2.y),
		"wavelength2": rng.randf_range(cfg.city_gen_coast_wavelength2.x, cfg.city_gen_coast_wavelength2.y),
		"phase2": rng.randf_range(0.0, TAU),
		"bay_at": lo + span * (0.5 + rng.randf_range(-cfg.city_gen_bay_shift, cfg.city_gen_bay_shift)),
		"bay_depth": rng.randf_range(cfg.city_gen_bay_depth.x, cfg.city_gen_bay_depth.y),
		"bay_width": rng.randf_range(cfg.city_gen_bay_width.x, cfg.city_gen_bay_width.y)}
	var inland := p.inland()
	# The Cell at the bay's head, then the corporations: shore ones on a bay flank, the rest on an arc round the Cell
	# facing inland.
	var half := float(hq_lots) * 0.5
	var centres := {}
	var bay_at := float(p.coast["bay_at"])
	var jit := cfg.city_gen_cell_jitter
	var along_jit := rng.randf_range(-jit, jit)
	var cell_t := bay_at + along_jit
	centres[cell_id] = p.edge_point(cell_t, maxf(p.shore_at(cell_t) + cfg.city_gen_cell_inland,
		_shore_max(p, cell_t - half - 1.0, cell_t + half + 1.0) + cfg.city_gen_coast_clear + half + 1.0))
	var ring: Array = []
	var shore: Array = []
	for id: StringName in ids:
		if id == cell_id:
			continue
		if cfg.city_gen_shore_corps.has(id):
			shore.append(id)
		else:
			ring.append(id)
	for k in range(ring.size() - 1, 0, -1):
		var m := rng.randi_range(0, k)
		var tmp: Variant = ring[k]
		ring[k] = ring[m]
		ring[m] = tmp
	# The Cell's Site heading first (the one nearest inland whose layout box is on land), so the ring leaves its
	# Sites a way out: no corporation's HQ may stand on one.
	var cell_aim := _cell_heading(p, cfg, centres[cell_id], inland, frame)
	if cell_aim < 0.0:
		p.failure = "no Site heading for %s" % cell_id
		p.fallback = true
		return p
	var uvs: Dictionary = frame.get("uvs", {})
	var cell_pts := site_points_at(centres[cell_id], cell_aim, false, frame, uvs[cell_id]) if uvs.has(cell_id) \
		else site_box(centres[cell_id], cell_aim, false, frame)
	# The shore corporations on a bay flank (before the ring, which keeps its gap from them).
	var bay_w := float(p.coast["bay_width"])
	for id: StringName in shore:
		var t := bay_at + (1.0 if rng.randf() < 0.5 else -1.0) * bay_w * rng.randf_range(cfg.city_gen_shore_flank.x, cfg.city_gen_shore_flank.y)
		# The rect's seaward edge on the shore's land side, `city_gen_shore_touch` lots up.
		centres[id] = p.edge_point(t, p.shore_at(t) + half + cfg.city_gen_shore_touch * 0.5)
	var arc := deg_to_rad(cfg.city_gen_ring_arc_deg)
	var step := arc / maxf(1.0, float(ring.size()))
	var theta0 := inland.angle() - arc * 0.5
	var tries := maxi(1, cfg.city_gen_candidates)
	for k in ring.size():
		# Its even turn with play first, then wider swings, until one is clear of the HQs, the water and the Cell's Sites.
		var c := Vector2.INF
		for n in tries:
			var play := cfg.city_gen_angle_jitter + (1.0 - cfg.city_gen_angle_jitter) * float(n) / float(maxi(1, tries - 1))
			var ang := theta0 + (k + 0.5) * step + rng.randf_range(-1.0, 1.0) * play * step
			var rad := rng.randf_range(cfg.city_gen_ring_lots.x, cfg.city_gen_ring_lots.y)
			c = centres[cell_id] + Vector2(cos(ang), sin(ang)) * rad
			if _ring_spot_ok(p, cfg, c, centres, hq_lots, cell_pts):
				break
		centres[ring[k]] = c
	var at := {}
	for id: StringName in ids:
		var c: Vector2 = centres[id]
		at[id] = Vector2(roundi(c.x - half), roundi(c.y - half))
		if shore.has(id):
			at[id] = _snap_to_shore(p, at[id], hq_lots)
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
	# Terrain hills (data only until NA-12c): centres on land, city_A2.json's Gaussian form.
	var inner_h := Rect2(city_rect.grow(-cfg.city_gen_edge_lots))
	for n in rng.randi_range(cfg.city_gen_hill_count.x, cfg.city_gen_hill_count.y):
		var hc := Vector2(rng.randf_range(inner_h.position.x, inner_h.end.x), rng.randf_range(inner_h.position.y, inner_h.end.y))
		var hill := {"centre": hc, "sigma_x": rng.randf_range(cfg.city_gen_hill_sigma.x, cfg.city_gen_hill_sigma.y),
			"sigma_y": rng.randf_range(cfg.city_gen_hill_sigma.x, cfg.city_gen_hill_sigma.y),
			"height": rng.randf_range(cfg.city_gen_hill_height.x, cfg.city_gen_hill_height.y), "rotation": rng.randf_range(0.0, PI)}
		if p.land_depth(hc.x, hc.y) >= cfg.city_gen_coast_clear:
			p.hills.append(hill)
	p.failure = _hq_problem(p, cfg, ids, hq_lots, shore, cell_id, cell_pts)
	if p.failure != "":
		p.fallback = true
		return p
	# Each corporation's Site heading.
	var rects := p.hq_rects(hq_lots)
	var aims := int(ceilf(360.0 / cfg.city_gen_aim_step_deg - 0.0001))
	p.site_aim[cell_id] = cell_aim
	p.site_mirror[cell_id] = false
	for id: StringName in ids:
		if id == cell_id:
			continue
		var best_aim := -1.0
		var best_own := -1
		for k in aims:
			var deg := k * cfg.city_gen_aim_step_deg
			var own := _site_box_score(p, cfg, id, cell_id, rects, (at[id] as Vector2) + Vector2(half, half), deg, frame)
			if own > best_own:
				best_own = own
				best_aim = deg
		if best_own < 0:
			p.failure = "no Site heading for %s" % id
			p.fallback = true
			return p
		p.site_aim[id] = best_aim
		p.site_mirror[id] = false
	return p


## The Cell's Site heading: of the headings whose layout box (CityGenerator.site_box) stays inside the city and off the
## water, the one whose Sites run nearest `inland` (ties: the lower angle); -1 when none.
static func _cell_heading(p: CityPlan, cfg: CampaignConfigData, centre: Vector2, inland: Vector2, frame: Dictionary) -> float:
	var inner := Rect2(p.rect.grow(-cfg.city_gen_edge_lots))
	var aims := int(ceilf(360.0 / cfg.city_gen_aim_step_deg - 0.0001))
	var best := -1.0
	var best_d := INF
	for k in aims:
		var deg := k * cfg.city_gen_aim_step_deg
		var ok := true
		for q in site_box(centre, deg, false, frame):
			if not inner.has_point(q) or p.land_depth(q.x, q.y) < cfg.city_gen_coast_clear:
				ok = false
				break
		if not ok:
			continue
		var run := -(frame["right"] as Vector2).rotated(deg_to_rad(deg)).normalized()
		var d := absf(run.angle_to(inland))
		if d < best_d - 0.0001:
			best_d = d
			best = deg
	return best


## True when an HQ centred on `c` stands inside the city, off the water, `city_gen_hq_gap` from every HQ centre in
## `centres` and off every point of `cell_pts` (grown by 1).
static func _ring_spot_ok(p: CityPlan, cfg: CampaignConfigData, c: Vector2, centres: Dictionary, hq_lots: int,
		cell_pts: PackedVector2Array) -> bool:
	var half := float(hq_lots) * 0.5
	var r := Rect2i(Vector2i(roundi(c.x - half), roundi(c.y - half)), Vector2i(hq_lots, hq_lots))
	if not p.rect.grow(-cfg.city_gen_edge_lots).encloses(r):
		return false
	for q in [Vector2(r.position), Vector2(r.end.x, r.position.y), Vector2(r.end), Vector2(r.position.x, r.end.y)]:
		if p.land_depth(q.x, q.y) < cfg.city_gen_coast_clear:
			return false
	var keys: Array = centres.keys()
	IdSort.sort_ids(keys)
	for k: StringName in keys:
		if (centres[k] as Vector2).distance_to(Vector2(r.get_center())) < cfg.city_gen_hq_gap:
			return false
	for q in cell_pts:
		if r.grow(1).has_point(Vector2i(q.floor())):
			return false
	return true


## "" when every HQ rect is inside the city by `city_gen_edge_lots`, `city_gen_coast_clear`
## lots from the water (a `shore` corporation's: on land and touching the water, `touches_water`),
## and every two HQ centres are `city_gen_hq_gap` apart; else what failed.
static func _hq_problem(p: CityPlan, cfg: CampaignConfigData, ids: Array, hq_lots: int, shore: Array = [], cell_id: StringName = &"",
		cell_pts: PackedVector2Array = PackedVector2Array()) -> String:
	var inner := p.rect.grow(-cfg.city_gen_edge_lots)
	var rects := p.hq_rects(hq_lots)
	for id: StringName in ids:
		var r: Rect2i = rects[id]
		if not inner.encloses(r):
			return "%s HQ off the city" % id
		if id != cell_id:
			for q in cell_pts:
				if r.grow(1).has_point(Vector2i(q.floor())):
					return "%s HQ on a Site of %s" % [id, cell_id]
		if shore.has(id):
			if not touches_water(p, r):
				return "%s HQ off the shore" % id
			continue
		for q in [Vector2(r.position), Vector2(r.end.x, r.position.y), Vector2(r.end), Vector2(r.position.x, r.end.y)]:
			if p.land_depth(q.x, q.y) < cfg.city_gen_coast_clear:
				return "%s HQ by the water" % id
	for a in ids.size():
		for b in range(a + 1, ids.size()):
			var ra: Rect2i = rects[ids[a]]
			var rb: Rect2i = rects[ids[b]]
			if Vector2(ra.get_center()).distance_to(Vector2(rb.get_center())) < cfg.city_gen_hq_gap:
				return "%s and %s HQs too close" % [ids[a], ids[b]]
	return ""


## Moves the HQ rect at `at` (top-left, lots) along the inland axis, a lot at a time, until it touches the water
## (`touches_water`): inland while a lot of it is sea, seaward while none of its neighbours is. Unchanged when it
## does not settle within SHORE_STEPS.
static func _snap_to_shore(p: CityPlan, at: Vector2, hq_lots: int) -> Vector2:
	var inl := p.inland()
	var cur := at
	for k in SHORE_STEPS:
		var r := Rect2i(Vector2i(cur), Vector2i(hq_lots, hq_lots))
		if touches_water(p, r):
			return cur
		var wet := false
		for i in range(r.position.x, r.end.x):
			for j in range(r.position.y, r.end.y):
				wet = wet or p.is_water(i, j)
		cur += inl if wet else -inl
	return at


## The shore's greatest distance from the sea edge over `[a, b]` (along the edge, sampled every half lot).
static func _shore_max(p: CityPlan, a: float, b: float) -> float:
	var m := -INF
	var t := a
	while t <= b:
		m = maxf(m, p.shore_at(t))
		t += 0.5
	return m


## True when HQ rect `r` holds no sea lot and a sea lot is a 4-neighbour of one of its lots (it touches the water).
static func touches_water(p: CityPlan, r: Rect2i) -> bool:
	var touch := false
	for i in range(r.position.x - 1, r.end.x + 1):
		for j in range(r.position.y - 1, r.end.y + 1):
			var inside := r.has_point(Vector2i(i, j))
			var ring := not inside and (i >= r.position.x and i < r.end.x or j >= r.position.y and j < r.end.y)
			if inside and p.is_water(i, j):
				return false
			if ring and p.is_water(i, j):
				touch = true
	return touch


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
	# The real Sites when the frame carries the layout (`uvs`: CityLayout.site_uvs), else the whole box, keep off other HQs.
	var uvs: Dictionary = frame.get("uvs", {})
	var pts := site_points_at(centre, deg, false, frame, uvs[id]) if uvs.has(id) else PackedVector2Array()
	for other: StringName in others:
		if other == id or other == cell_id:
			continue
		var r := Rect2((rects[other] as Rect2i).grow(1))
		if uvs.has(id):
			for q in pts:
				if r.has_point(q.floor()):
					return -1
			continue
		var poly := PackedVector2Array([r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)])
		if not Geometry2D.intersect_polygons(outline, poly).is_empty():
			return -1
	var own := 0
	for q in (pts if uvs.has(id) else box):  # the real Sites when known, else the whole box
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


## The Site points (lots) of a layout `uvs` (each in [-1, 1]^2, CityLayout.site_uvs) round HQ centre `centre`,
## turned `deg`, mirrored when `mirror` (CityLayout.site_points_aimed's formula).
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
