extends GutTest
## CITY-A2 step 1 (D3), full tier: 200 seeds of the planner city. A seed's plan and subdivision (fresh, uncached, best
## of two runs) stays under `city_a2_budget_s` at the 95th percentile; no seed falls back; each plan is clean (CityGenFixture.plan_problems); each
## corporation's HQ rect lies on land in its own A2 district; every Site has a building lot within
## `art_site_bid_reach_lots`; and a few full cities pass the full-city checks (Site buildings, Grid street routes).

const CITY_CONFIG := preload("res://content/config/city_config.tres")
const SEEDS := 200
const FULL_SEEDS: Array[int] = [7919, -424242, 31337]

var _cfg: CampaignConfigData


func before_all() -> void:
	_cfg = load(CityPlan.FIXED_CONFIG_PATH)


func test_two_hundred_seeds() -> void:
	var corps := CityGenFixture.corps()
	var frame := CityPlan.site_frame()
	CityA2Builder.raster(_cfg, CITY_CONFIG.city_rect, NeonCity.BORDER_BLEND)  # seed-independent, built once
	var ids: Array = []
	for t in NeonCity.TERRITORIES:
		if t["id"] != &"":
			ids.append(t["id"])
	var times := PackedFloat64Array()
	var problems := PackedStringArray()
	for k in SEEDS:
		var s := CityGenFixture.seed_of(k)
		# Best of two runs per seed (the machine runs other agents' Godot processes; one spike is not the seed's cost).
		var took := INF
		var p: CityPlan
		var lots: Dictionary
		for run in 2:
			var t0 := Time.get_ticks_usec()  # fixed-wait-ok: the A2 time budget (CITY-A2 item 3), a performance bound
			p = CityA2Builder.make_plan(s, _cfg, CITY_CONFIG.city_rect, ids, NeonCity.FIST_TERRITORY, NeonCity.HQ_LOTS, frame,
				NeonCity.BORDER_BLEND, CITY_CONFIG.lot_bu)
			lots = CityA2Builder._subdivide(p, _cfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
			took = minf(took, (Time.get_ticks_usec() - t0) / 1e6)  # fixed-wait-ok: as above
		times.append(took)
		if p.fallback:
			problems.append("seed %d fell back: %s" % [s, p.failure])
			continue
		for e in CityGenFixture.plan_problems(p, corps):
			problems.append("seed %d: %s" % [s, e])
		var rects := p.hq_rects(NeonCity.HQ_LOTS)
		for id: StringName in rects:
			var r: Rect2i = rects[id]
			var a2_id := &"centre" if id == NeonCity.FIST_TERRITORY else id
			for j in range(r.position.y, r.end.y):
				for i in range(r.position.x, r.end.x):
					if p.is_water(i, j) or p.a2.district_id(i, j) != a2_id:
						problems.append("seed %d: %s HQ lot %d,%d off its district" % [s, id, i, j])
		for l: Vector2i in p.a2_sites:
			if not _building_near(lots, l, CITY_CONFIG.art_site_bid_reach_lots):
				problems.append("seed %d: Site lot %s has no building" % [s, l])
	assert_eq(problems, PackedStringArray(), "%d seeds clean" % SEEDS)
	# The budget holds for the 95th percentile seed: the gate runs four shards beside other agents' Godot processes, so the
	# single slowest best-of-two still carries load spikes (typical seed ~0.3 s here, quiet).
	times.sort()
	var p95 := times[int(times.size() * 0.95)]
	gut.p("CITY-A2 sweep: median %.3f s, p95 %.3f s, slowest %.3f s (budget %.1f s)" % [times[times.size() / 2], p95,
		times[times.size() - 1], _cfg.city_a2_budget_s])
	assert_lt(p95, _cfg.city_a2_budget_s, "95th percentile seed %.3f s under the budget" % p95)


func test_full_cities() -> void:
	var corps := CityGenFixture.corps()
	for s in FULL_SEEDS:
		var m := CityModel.build(CITY_CONFIG, s)
		assert_eq(CityPlan.for_seed(s).source(), "a2", "seed %d is A2" % s)
		assert_eq(CityGenFixture.full_city_problems(m, corps), PackedStringArray(), "seed %d full city" % s)


func _building_near(lots: Dictionary, l: Vector2i, reach: int) -> bool:
	var R: Rect2i = lots["rect"]
	var kind: PackedByteArray = lots["kind"]
	for dj in range(-reach, reach + 1):
		for di in range(-reach, reach + 1):
			var q := l + Vector2i(di, dj)
			if R.has_point(q) and kind[(q.y - R.position.y) * R.size.x + (q.x - R.position.x)] == CityA2Builder.K_BUILDING:
				return true
	return false
