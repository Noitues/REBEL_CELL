class_name CitySolaceDistrict
extends RefCounted
## Solace district layout (A-069 / A-070, designer 2026-10-21): after CityA2Builder has made a city's lots, the Solace
## territory is re-laid. Pure and deterministic from the city seed; reads no gameplay stream.
##  - The district's local street grid becomes one park (kind K_PARK). Streets on the district's border (a lot with a
##    4-neighbour of another territory) and A2 roads stay: they are the ordinary city streets at the park's edge.
##  - Its buildings stand in blocks of `city_sol_block_lots` lots a side, on a lattice of pitch (largest block + gap)
##    with a lawn gap of at least `city_sol_gap_lots` lots between two blocks. A Site lot keeps a one-lot building and a lawn
##    ring of one lot round it.
##  - Heights are `city_sol_height_k` of the A2 Solace heights, never under `city_sol_min_floors` storeys.
##  - The HQ plinth circle (`city_sol_plinth_r_bu` round the HQ centre) holds no block.
## Nothing outside the Solace territory changes: the A2 pass has drawn every random number first (this pass draws from
## its own seeded generator), and it only edits lots whose territory is Solace.
## The result gains `"solace"`: the park (CitySolacePark.build), or {} when the territory has none.

const TERR: StringName = &"solace"
const SALT_PHASE := 9110
const STREAM: StringName = &"city_solace"
const LOT_BLOCK_SEED := 9111


## Re-lays `lots` (CityA2Builder._subdivide's result) in place. `plan`: the city's plan; `px_per_bu` as for `_extrusions`.
static func apply(lots: Dictionary, plan: CityPlan, cfg: CampaignConfigData, hq_lots: int, cell_id: StringName, px_per_bu: float) -> void:
	if not cfg.city_sol_layout or plan.a2 == null or not plan.has_territory(TERR):
		return
	var ras: CityA2Raster = plan.a2
	var R: Rect2i = lots["rect"]
	var w := R.size.x
	var kind: PackedByteArray = lots["kind"]
	var streets: Dictionary = lots["streets"]
	var old_cells: Array = lots["cells"]
	var lot_bu := CityView3D.CONFIG.lot_bu
	var rects := plan.hq_rects(hq_lots)
	var hq: Rect2i = rects.get(TERR, Rect2i())
	var centre := Vector2(hq.position) + Vector2(hq.size) * 0.5
	var r_l := cfg.city_sol_plinth_r_bu / lot_bu
	var removed := {}  # lot -> true: the Solace street and building lots this pass re-lays
	var bare := {}
	for k in kind.size():
		var l := Vector2i(R.position.x + k % w, R.position.y + k / w)
		if ras.territory(l.x, l.y) != TERR:
			continue
		if kind[k] == CityA2Builder.K_STREET and ras.road_rank(l.x, l.y) == 0 and not _border(ras, R, l):
			removed[l] = true
		elif kind[k] == CityA2Builder.K_BARE:
			bare[l] = true
	var kept: Array = []
	for c: Dictionary in old_cells:
		var cell: Rect2i = c["cell"]
		var f := cell.end - Vector2i.ONE
		if ras.territory(f.x, f.y) != TERR:
			kept.append(c)
			continue
		for j in range(cell.position.y, cell.end.y):
			for i in range(cell.position.x, cell.end.x):
				removed[Vector2i(i, j)] = true
	if removed.is_empty() and bare.is_empty():
		lots["solace"] = {}
		return
	# Site lots keep a one-lot building and a lawn ring.
	var site_lots: Array[Vector2i] = []
	for s: Vector2i in plan.a2_sites:
		if removed.has(s):
			site_lots.append(s)
	site_lots.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.y < b.y if a.y != b.y else a.x < b.x)
	var blocked := {}
	for s in site_lots:
		for dj in range(-1, 2):
			for di in range(-1, 2):
				blocked[s + Vector2i(di, dj)] = true
	var avail := {}
	var bb := Rect2i()
	var first := true
	for l: Vector2i in removed:
		if blocked.has(l) or (hq.size != Vector2i.ZERO and _in_circle(l, centre, r_l)):
			continue
		avail[l] = true
		bb = Rect2i(l, Vector2i.ONE) if first else bb.expand(l).expand(l + Vector2i.ONE)
		first = false
	# Blocks on the lattice.
	var bl := cfg.city_sol_block_lots
	var pitch := bl.y + cfg.city_sol_gap_lots
	var ox := int(CityMeshKit.hash01(SALT_PHASE, plan.city_seed & 0xffff, 1) * float(pitch)) % pitch
	var oy := int(CityMeshKit.hash01(SALT_PHASE, plan.city_seed & 0xffff, 2) * float(pitch)) % pitch
	var new_cells: Array[Rect2i] = []
	for s in site_lots:
		new_cells.append(Rect2i(s, Vector2i.ONE))
	var taken := {}
	for c: Rect2i in new_cells:
		taken[c.position] = true
	if not first:
		for cj in range(floori(float(bb.position.y - oy) / pitch), floori(float(bb.end.y - oy) / pitch) + 1):
			for ci in range(floori(float(bb.position.x - ox) / pitch), floori(float(bb.end.x - ox) / pitch) + 1):
				var g := RandomNumberGenerator.new()
				g.seed = hash([plan.city_seed, LOT_BLOCK_SEED, ci, cj])
				var sx := g.randi_range(bl.x, bl.y)
				var sy := g.randi_range(bl.x, bl.y)
				var offx := g.randi_range(0, bl.y - sx)
				var offy := g.randi_range(0, bl.y - sy)
				var B := Rect2i(ox + ci * pitch + offx, oy + cj * pitch + offy, sx, sy)
				var best := _best_sub(B, avail, bl.x)
				if best.size != Vector2i.ZERO:
					new_cells.append(best)
					for j in range(best.position.y, best.end.y):
						for i in range(best.position.x, best.end.x):
							taken[Vector2i(i, j)] = true
	new_cells.sort_custom(func(a: Rect2i, b: Rect2i) -> bool: return a.position.y < b.position.y if a.position.y != b.position.y else a.position.x < b.position.x)
	# Kinds: the re-laid lots and the bare Solace land are lawn, except the blocks.
	for l: Vector2i in removed:
		kind[(l.y - R.position.y) * w + (l.x - R.position.x)] = CityA2Builder.K_PARK
	for l: Vector2i in bare:
		kind[(l.y - R.position.y) * w + (l.x - R.position.x)] = CityA2Builder.K_PARK
	for l: Vector2i in taken:
		kind[(l.y - R.position.y) * w + (l.x - R.position.x)] = CityA2Builder.K_BUILDING
	# Streets: the removed ones go; their neighbours re-read their axes.
	var cleared: Array[Vector2i] = []
	for l: Vector2i in removed:
		var k := (l.y - R.position.y) * w + (l.x - R.position.x)
		if streets.has(k):
			streets.erase(k)
			cleared.append(l)
	cleared.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.y < b.y if a.y != b.y else a.x < b.x)
	var touched := {}
	for l in cleared:
		for d: Vector2i in CityA2Builder.DIRS:
			var q := l + d
			if R.has_point(q) and streets.has((q.y - R.position.y) * w + (q.x - R.position.x)):
				touched[q] = true
	var tl: Array = touched.keys()
	tl.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.y < b.y if a.y != b.y else a.x < b.x)
	for q: Vector2i in tl:
		_reaxis(streets[(q.y - R.position.y) * w + (q.x - R.position.x)], kind, R, q, ras, cfg)
	# The buildings: their own generator, sorted by lot.
	var rng := RngStreams.make_stream(plan.city_seed, STREAM)
	var hq_centres: Array[Vector2] = []
	var ids: Array = rects.keys()
	IdSort.sort_ids(ids)
	for id: StringName in ids:
		if id != cell_id:
			hq_centres.append(Vector2(rects[id].position) + Vector2(hq_lots, hq_lots) * 0.5)
	var cells: Array = kept
	for c: Rect2i in new_cells:
		var on_street := false
		for j in range(c.position.y - 1, c.end.y + 1):
			for i in range(c.position.x - 1, c.end.x + 1):
				var edge := (i < c.position.x or i >= c.end.x) != (j < c.position.y or j >= c.end.y)
				if edge and R.has_point(Vector2i(i, j)) and kind[(j - R.position.y) * w + (i - R.position.x)] == CityA2Builder.K_STREET:
					on_street = true
		var near_hq := false
		for id: StringName in rects:
			if (rects[id] as Rect2i).grow(cfg.city_a2_spike_hq_clear).intersects(c):
				near_hq = true
				break
		cells.append({"cell": c, "extrusions": CityA2Builder._extrusions(ras, cfg, c, cell_id, hq_centres, px_per_bu, rng, plan.terrain,
			plan.a2_sites, on_street, near_hq, true)})
	var front := {}
	for ci in cells.size():
		var cell: Rect2i = cells[ci]["cell"]
		var f := cell.end - Vector2i.ONE
		front[(f.y - R.position.y) * w + (f.x - R.position.x)] = ci
	lots["kind"] = kind
	lots["cells"] = cells
	lots["front"] = front
	lots["solace"] = CitySolacePark.build(lots, ras, cfg, plan.city_seed, TERR, hq, r_l, lot_bu)


## Site points (lots) moved off the plinth circle (radius `r` lots round `centre`; r <= 0 = no change). A point whose lot
## square comes within 1 lot of the circle moves, in whole lots along the axis it lies furthest on (x on a tie, away from
## `centre`), by the smallest count that clears the circle by 1 lot and lands on no lot an earlier point holds; the fraction
## is kept. Points are taken in the layout's order, so the result is deterministic. Then no stair landing (on the circle) can
## lie in a Site lot.
static func shift_sites(points: PackedVector2Array, centre: Vector2, r: float) -> PackedVector2Array:
	if r <= 0.0:
		return points
	var out := PackedVector2Array()
	var held := {}
	for p in points:
		var l := Vector2i(p.floor())
		var v := Vector2(l) + Vector2(0.5, 0.5) - centre
		var d := Vector2i(1 if v.x >= 0.0 else -1, 0) if absf(v.x) >= absf(v.y) else Vector2i(0, 1 if v.y >= 0.0 else -1)
		var n := 0
		while n < 256 and (held.has(l + d * n) or _gap(l + d * n, centre) < r + 1.0):
			n += 1
		held[l + d * n] = true
		out.append(p + Vector2(d * n))
	return out


## Distance from the lot square of `l` to `c`.
static func _gap(l: Vector2i, c: Vector2) -> float:
	var dx := maxf(maxf(float(l.x) - c.x, c.x - float(l.x + 1)), 0.0)
	var dy := maxf(maxf(float(l.y) - c.y, c.y - float(l.y + 1)), 0.0)
	return sqrt(dx * dx + dy * dy)


## True when lot `l` lies on the Solace territory's border: a 4-neighbour outside the city or of another territory.
static func _border(ras: CityA2Raster, R: Rect2i, l: Vector2i) -> bool:
	for d: Vector2i in CityA2Builder.DIRS:
		var q := l + d
		if not R.has_point(q) or ras.territory(q.x, q.y) != TERR:
			return true
	return false


## True when the lot square of `l` reaches into the circle of radius `r` (lots) round `c`.
static func _in_circle(l: Vector2i, c: Vector2, r: float) -> bool:
	var dx := maxf(maxf(float(l.x) - c.x, c.x - float(l.x + 1)), 0.0)
	var dy := maxf(maxf(float(l.y) - c.y, c.y - float(l.y + 1)), 0.0)
	return dx * dx + dy * dy < r * r


## True when any lot of `r` reaches into the circle (see `_in_circle`).
static func _in_circle_rect(r: Rect2i, c: Vector2, rad: float) -> bool:
	for j in range(r.position.y, r.end.y):
		for i in range(r.position.x, r.end.x):
			if _in_circle(Vector2i(i, j), c, rad):
				return true
	return false


## The largest sub-rectangle of `b` whose lots are all in `avail`, each side at least `min_side` (the first by row, column on a tie);
## a Rect2i of size 0 when none.
static func _best_sub(b: Rect2i, avail: Dictionary, min_side: int) -> Rect2i:
	var best := Rect2i()
	var best_area := 0
	for y0 in range(b.position.y, b.end.y):
		for x0 in range(b.position.x, b.end.x):
			for y1 in range(y0 + min_side, b.end.y + 1):
				for x1 in range(x0 + min_side, b.end.x + 1):
					var area := (x1 - x0) * (y1 - y0)
					if area <= best_area:
						continue
					var ok := true
					for j in range(y0, y1):
						for i in range(x0, x1):
							if not avail.has(Vector2i(i, j)):
								ok = false
								break
						if not ok:
							break
					if ok:
						best = Rect2i(x0, y0, x1 - x0, y1 - y0)
						best_area = area
	return best


## Street record `rec` at lot `l` re-reads its axes from the street lots now round it (A2's rule); an intersection is
## black with no traffic, a lot that stopped being one takes a hashed ink and its class's traffic.
static func _reaxis(rec: Dictionary, kind: PackedByteArray, R: Rect2i, l: Vector2i, ras: CityA2Raster, cfg: CampaignConfigData) -> void:
	var ai := CityA2Builder._street(kind, R, l + Vector2i(0, 1)) or CityA2Builder._street(kind, R, l + Vector2i(0, -1))
	var aj := CityA2Builder._street(kind, R, l + Vector2i(1, 0)) or CityA2Builder._street(kind, R, l + Vector2i(-1, 0))
	if not ai and not aj:
		aj = true
	rec["along_i"] = ai
	rec["along_j"] = aj
	if ai and aj:
		rec["col"] = Color.BLACK
		rec["traffic"] = 0.0
	elif rec["col"] == Color.BLACK:
		rec["col"] = NeonCity.INKS[int(CityMeshKit.hash01(SALT_PHASE + 5, l.x, l.y) * NeonCity.INKS.size()) % NeonCity.INKS.size()]
		var rk := ras.road_rank(l.x, l.y)
		var cls: StringName = CityPlanA2.ROAD_CLASSES[rk - 1] if rk > 0 else &"local"
		rec["traffic"] = float(cfg.city_a2_traffic.get(cls, cfg.city_a2_traffic[&"local"]))
