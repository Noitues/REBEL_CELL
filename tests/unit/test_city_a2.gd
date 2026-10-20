extends GutTest
## CITY-A2 step 1 (D3), fast tier: the planner city A2 is every generated seed's city. The vendored city_A2.json
## validates (and a broken one does not); same seed -> byte-identical plan and full-city `city.json`; two seeds differ
## inside the same A2 plan; every corporation's HQ rect lies on land inside its own A2 district and is the model's HQ;
## every A2 road inside the city is on the model's streets (or an HQ plaza); every Site has a building; the plan has no
## plan-level problem; the default seed is an A2 city too (step 2). Step 2: the terrain (heights, rails, landmarks) is
## the same after a rebuild from scratch; buildings stand on the ground. The 200-seed sweep and the time budget:
## test_city_a2_sweep.gd.

const CITY_CONFIG := preload("res://content/config/city_config.tres")
const SEED := 1
const SEED_B := 2

var _cfg: CampaignConfigData
var _model: CityModel


func before_all() -> void:
	_cfg = load(CityPlan.FIXED_CONFIG_PATH)
	_model = CityModel.build(CITY_CONFIG, SEED)


func test_a2_file_validates() -> void:
	var a2 := CityPlanA2.shared(_cfg.city_a2_path)
	assert_eq(a2.errors, PackedStringArray(), "city_A2.json validates")
	assert_eq(a2.districts.size(), 7, "seven districts")
	assert_eq(a2.roads.size(), 53, "53 roads")
	var bad := CityPlanA2.validate({"meta": {"version": 2}, "districts": [], "terrain": {}, "roads": [{"id": "r", "class": "lane"}]})
	assert_true(bad.size() >= 4, "a broken plan reports its problems: %s" % ", ".join(bad))


func test_generated_seed_is_the_a2_city() -> void:
	var p := CityPlan.for_seed(SEED)
	assert_eq(p.source(), "a2", "a generated seed is the planner city")
	assert_false(p.fallback, "no fallback: %s" % p.failure)
	assert_eq(CityPlan.for_seed(CityPlan.default_seed()).source(), "a2", "CITY-A2 step 2: the default seed is an A2 city too")


func test_same_seed_gives_a_byte_identical_city() -> void:
	var a := JSON.stringify(CityPlan.generate(SEED, _cfg).to_dict(), "", true)
	var b := JSON.stringify(CityPlan.generate(SEED, _cfg).to_dict(), "", true)
	assert_eq(a, b, "same plan")
	var ja := _export(_model)
	CityPlan.forget_all()
	var again := CityModel.build(CITY_CONFIG, SEED)
	assert_eq(_export(again), ja, "same seed, byte-identical city.json after a rebuild from scratch")
	assert_eq(again.prisms.size(), _model.prisms.size(), "same prisms")


func test_two_seeds_two_cities_in_one_plan() -> void:
	var a := CityPlan.for_seed(SEED)
	var b := CityPlan.for_seed(SEED_B)
	assert_ne(JSON.stringify(a.to_dict()), JSON.stringify(b.to_dict()), "HQ spots or Site headings differ")
	var ra := CityA2Builder.lots_for(a, _cfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
	var rb := CityA2Builder.lots_for(b, _cfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
	assert_ne(ra["kind"], rb["kind"], "the blocks differ")
	for i in range(a.rect.position.x, a.rect.end.x, 7):
		for j in range(a.rect.position.y, a.rect.end.y, 7):
			assert_eq(a.is_water(i, j), b.is_water(i, j), "same coast at %d, %d" % [i, j])
			assert_eq(a.territory_pair(i, j)[0], b.territory_pair(i, j)[0], "same districts at %d, %d" % [i, j])


func test_each_corp_hq_is_inside_its_a2_district() -> void:
	for s in [SEED, SEED_B, 77]:
		var p := CityPlan.for_seed(s)
		var rects := p.hq_rects(NeonCity.HQ_LOTS)
		for id: StringName in [&"halcyon", &"meridian", &"orbital", &"solace", &"rebel_cell"]:
			assert_true(rects.has(id), "seed %d: %s has an HQ" % [s, id])
			var r: Rect2i = rects.get(id, Rect2i())
			var a2_id := &"centre" if id == &"rebel_cell" else id
			var bad := 0
			for j in range(r.position.y, r.end.y):
				for i in range(r.position.x, r.end.x):
					if p.is_water(i, j) or p.a2.district_id(i, j) != a2_id:
						bad += 1
			assert_eq(bad, 0, "seed %d: %s HQ rect %s inside A2 district %s" % [s, id, r, a2_id])
	for id: StringName in _model.hqs:
		assert_eq(_model.hqs[id], CityPlan.for_seed(SEED).hq_rects(NeonCity.HQ_LOTS)[id], "%s: the model's HQ is the plan's" % id)
	assert_false(_model.hqs.has(NeonCity.FIST_TERRITORY), "the Cell has no plaza")


func test_every_a2_road_is_on_the_streets() -> void:
	var have := {}
	for s in _model.streets:
		have[s["lot"]] = true
	for pz in _model.plazas:
		have[pz["lot"]] = true
	var ras := CityPlan.for_seed(SEED).a2
	var roads := 0
	for id: StringName in ras.road_lots:
		var missing := 0
		var inside := 0
		for l: Vector2i in ras.road_lots[id]:
			if CITY_CONFIG.city_rect.has_point(l):
				inside += 1
				if not have.has(l):
					missing += 1
		if inside > 0:
			roads += 1
		assert_eq(missing, 0, "road %s: every lot inside the city is a street" % id)
	assert_eq(roads, ras.a2.roads.size(), "every A2 road crosses the city")


func test_sites_stand_on_buildings_and_the_plan_is_clean() -> void:
	var corps := CityGenFixture.corps()
	assert_eq(CityGenFixture.plan_problems(CityPlan.for_seed(SEED), corps), PackedStringArray(), "plan problems")
	assert_eq(CityGenFixture.full_city_problems(_model, corps), PackedStringArray(), "full-city problems")


func test_layout_draws_no_global_rng() -> void:
	seed(12345)
	var before := randi()
	seed(12345)
	CityA2Builder.forget()
	CityA2Builder.make_plan(SEED_B, _cfg, CITY_CONFIG.city_rect, [&"halcyon", &"rebel_cell"], NeonCity.FIST_TERRITORY,
		NeonCity.HQ_LOTS, CityPlan.site_frame(), NeonCity.BORDER_BLEND, CITY_CONFIG.lot_bu)
	CityA2Builder.lots_for(CityPlan.for_seed(SEED_B), _cfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
	assert_eq(randi(), before, "the global RNG did not advance")


## CITY-A2 step 2: the terrain is a pure function of the A2 file and the config (two fresh builds agree to the bit), A2's
## hills rise where the file puts them (the Panopticon's hill, 247 m -> about 12 BU), the water stays at sea level, and the
## mountains rise past the outer ring.
func test_terrain_is_deterministic_and_follows_a2() -> void:
	var cc: CityConfig = CITY_CONFIG
	var ras := CityA2Builder.raster(_cfg, cc.city_rect, NeonCity.BORDER_BLEND)
	var a := CityA2Terrain.make(ras, _cfg, cc.city_rect, cc.lot_bu)
	var b := CityA2Terrain.make(ras, _cfg, cc.city_rect, cc.lot_bu)
	assert_eq(a.fine, b.fine, "same fine grid")
	assert_eq(a.coarse, b.coarse, "same coarse grid")
	var hill := ras.lot_of(Vector2(700.0, 5900.0))
	var want := 247.0 * cc.lot_bu / _cfg.city_a2_metres_per_lot * _cfg.city_a2_hill_exag
	assert_between(a.height_at(hill.x, hill.y), want, want * 1.5, "the Panopticon's hill")
	var wet := 0
	for j in range(cc.city_rect.position.y, cc.city_rect.end.y, 3):
		for i in range(cc.city_rect.position.x, cc.city_rect.end.x, 3):
			if ras.is_water(i, j) and ras.water[ras.index(i, j)] == CityA2Raster.SEA and a.lot_height(i, j) > 0.0:
				wet += 1
	assert_eq(wet, 0, "the sea lots are at sea level")
	var top := 0.0
	for k in a.coarse.size():
		top = maxf(top, a.coarse[k])
	assert_gt(top, _cfg.city_a2_foot_h, "mountains past the outer ring")
	assert_almost_eq(CityPlan.for_seed(SEED).ground_at(hill.x, hill.y), a.height_at(hill.x, hill.y), 0.0001, "the plan's ground")


## CITY-A2 step 2: every building stands on the ground (its "ground" is its cell's lowest corner, its base on it); city.json
## keeps parts relative to that ground and carries it; a screen pick lands on the terrain.
func test_buildings_and_picks_follow_the_ground() -> void:
	var t := CityPlan.for_seed(SEED).terrain
	var off := 0
	var raised := 0
	for pr: Dictionary in _model.prisms:
		var g := t.cell_ground(pr["cell"])
		if absf(float(pr["ground"]) - g) > 0.0001 or float(pr["y0"]) < g - 0.0001:
			off += 1
		if g > 1.0:
			raised += 1
	assert_eq(off, 0, "every prism on its cell's ground")
	assert_gt(raised, 100, "the hills lift buildings")
	var doc: Dictionary = JSON.parse_string(_export(_model))
	var by_bid := {}
	for b: Dictionary in doc["buildings"]:
		by_bid[b["bid"]] = b
	for pr: Dictionary in _model.prisms.slice(0, 200):
		var cell: Rect2i = pr["cell"]
		var bid := "hq:%s" % pr["terr"] if bool(pr["hq"]) else "%d:%d" % [cell.position.x, cell.position.y]
		assert_almost_eq(float(by_bid[bid]["ground"]), float(pr["ground"]), 0.0001, bid)
		assert_true(float(by_bid[bid]["parts"][0]["z0"]) < float(pr["y0"]) + 0.0001, "%s: z0 relative" % bid)
	var cam := CityIsoCamera.for_view(CITY_CONFIG, "grid", Vector2(1920, 1080))
	var hill := CityPlan.for_seed(SEED).a2.lot_of(Vector2(700.0, 5900.0))
	cam.target = CityIsoCamera.lot_to_world(CITY_CONFIG, hill, t.height_at(hill.x, hill.y))
	var g := _model.ground_point(cam, Vector2(960, 540))
	var l := CityIsoCamera.world_to_lot(CITY_CONFIG, g)
	assert_almost_eq(g.y, t.height_at(l.x, l.y), 0.05, "the pick lands on the hill")


## CITY-A2 step 2: the features (roads by class, rails and stations, walls and checkpoints, port, drowned quarter,
## undercity entrances) come from the plan alone: two builds give the same vertices; every part is there; tunnels stay
## under ground and the walls open at their gates; every deck vertex stands at or over the ground.
func test_features_are_deterministic_and_complete() -> void:
	var plan := CityPlan.for_seed(SEED)
	var a := CityA2Features.build(CITY_CONFIG, plan)
	var b := CityA2Features.build(CITY_CONFIG, plan)
	for k: String in CityA2Features.ORDER:
		var pa: Dictionary = a["parts"][k]
		assert_gt(int(pa["quads"]), 0, "%s drawn" % k)
		assert_eq(int(pa["quads"]), int(b["parts"][k]["quads"]), "%s: same count" % k)
		if pa["mesh"] != null:
			assert_eq((pa["mesh"] as ArrayMesh).surface_get_arrays(0)[Mesh.ARRAY_VERTEX],
				(b["parts"][k]["mesh"] as ArrayMesh).surface_get_arrays(0)[Mesh.ARRAY_VERTEX], "%s: same vertices" % k)
	assert_gt(int(a["hidden"]), 0, "tunnel stretches are not drawn")
	assert_gt(int(a["gates"]), 0, "the walls open at their gates")
	var below := 0
	var verts: PackedVector3Array = (a["parts"]["roads"]["mesh"] as ArrayMesh).surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	for k in range(0, verts.size(), 7):
		var l := CityIsoCamera.world_to_lot(CITY_CONFIG, verts[k])
		if verts[k].y < plan.ground_at(l.x, l.y) - 0.001:
			below += 1
	assert_eq(below, 0, "road decks stand on the ground")


func _export(m: CityModel) -> String:
	return JSON.stringify(NetrunArtExport.city_json(m.city_seed, CITY_CONFIG.lot_bu, CITY_CONFIG.district_centre, m.prisms, m.streets,
		m.plazas, m.hqs, m.city_sections()), "", true)
