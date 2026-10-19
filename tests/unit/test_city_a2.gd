extends GutTest
## CITY-A2 step 1 (D3), fast tier: the planner city A2 is every generated seed's city. The vendored city_A2.json
## validates (and a broken one does not); same seed -> byte-identical plan and full-city `city.json`; two seeds differ
## inside the same A2 plan; every corporation's HQ rect lies on land inside its own A2 district and is the model's HQ;
## every A2 road inside the city is on the model's streets (or an HQ plaza); every Site has a building; the plan has no
## plan-level problem; the &"grid" config still gives NA-12's generator. The 200-seed sweep and the time budget:
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
	assert_eq(CityPlan.for_seed(CityPlan.fixed_seed()).source(), "fixed", "the fixed seed stays today's city")
	var grid := _cfg.duplicate() as CampaignConfigData
	grid.city_layout_source = &"grid"
	assert_eq(CityPlan.generate(SEED, grid).source(), "grid", "the grid config keeps NA-12's generator")


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


func _export(m: CityModel) -> String:
	return JSON.stringify(NetrunArtExport.city_json(m.city_seed, CITY_CONFIG.lot_bu, CITY_CONFIG.district_centre, m.prisms, m.streets,
		m.plazas, m.hqs, m.city_sections()), "", true)
