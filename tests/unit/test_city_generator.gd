extends GutTest
## Plan 2 NA-12 (D3), fast tier: the per-seed city on 50 seeds, CITY-A2 step 2: every seed is the planner city A2
## (CityPlan.generate; the grid generator is gone). Same seed, same plan (and a byte-identical full-city `city.json`);
## every corporation's HQ rect is exclusive (no other HQ, inside the city, off the water); every Site of every
## corporation lies on land inside the city and off another HQ; on full cities every Site has a building and every Grid
## link a street route; no global RNG; the default seed is an A2 city; the plan advances no campaign stream. The seed
## sweep and the time budget: test_city_a2_sweep.gd.

const CITY_CONFIG := preload("res://content/config/city_config.tres")
const SEEDS := 50
## The full-city seed (one build kept for the full-city checks; the sweep builds more).
const FULL_SEED := -987654321

var _cfg: CampaignConfigData
var _model: CityModel


func before_all() -> void:
	_cfg = load(CityPlan.FIXED_CONFIG_PATH)
	_model = CityModel.build(CITY_CONFIG, FULL_SEED)


func test_same_seed_gives_the_same_plan() -> void:
	for k in SEEDS:
		var s := CityGenFixture.seed_of(k)
		var a := JSON.stringify(CityPlan.generate(s, _cfg).to_dict(), "", true)
		var b := JSON.stringify(CityPlan.generate(s, _cfg).to_dict(), "", true)
		assert_eq(a, b, "seed %d" % s)
	assert_ne(JSON.stringify(CityPlan.generate(CityGenFixture.seed_of(0), _cfg).to_dict(), "", true),
		JSON.stringify(CityPlan.generate(CityGenFixture.seed_of(1), _cfg).to_dict(), "", true), "two seeds, two cities")


func test_same_seed_gives_a_byte_identical_city_json() -> void:
	var cfg: CityConfig = CITY_CONFIG
	var s := FULL_SEED
	var texts := []
	for m: CityModel in [_model, CityModel.build(cfg, s)]:
		texts.append(NetrunArtExport.canonical(NetrunArtExport.city_json(m.city_seed, cfg.lot_bu, cfg.district_centre, m.prisms,
			m.streets, m.plazas, m.hqs)))
	assert_eq(texts[0], texts[1], "two builds of seed %d" % s)
	assert_true(String(texts[0]).contains("\"layout_seed\": \"%s\"" % ArtSeed.u64_str(s)), "layout_seed as a u64 decimal string")


func test_every_hq_is_exclusive_and_every_site_on_land_over_50_seeds() -> void:
	var list := CityGenFixture.corps()
	assert_true(list.size() >= 5, "the corporations")
	var bad := 0
	for k in SEEDS:
		var plan := CityPlan.generate(CityGenFixture.seed_of(k), _cfg)
		assert_false(plan.fallback, "seed %d: a generated layout (%s)" % [CityGenFixture.seed_of(k), plan.failure])
		assert_false(plan.coast.is_empty(), "seed %d: a coast" % CityGenFixture.seed_of(k))
		var probs := CityGenFixture.plan_problems(plan, list)
		if not probs.is_empty():
			bad += 1
			gut.p("seed %d: %s" % [CityGenFixture.seed_of(k), ", ".join(probs)])
	assert_eq(bad, 0)


func test_full_cities_have_sites_on_buildings_links_on_streets_and_no_hq_overlap() -> void:
	var list := CityGenFixture.corps()
	assert_eq(CityGenFixture.full_city_problems(_model, list), PackedStringArray(), "seed %d" % FULL_SEED)


func test_the_sea_holds_no_street_and_no_building() -> void:
	var cfg: CityConfig = CITY_CONFIG
	var plan := CityPlan.for_seed(FULL_SEED)
	var m := _model
	var wet := 0
	for st: Dictionary in m.streets:
		var l: Vector2i = st["lot"]
		# CITY-A2: A2 roads cross the water on bridges and local streets bridge rivers.
		if plan.is_water(l.x, l.y) and not (plan.a2 != null and (plan.a2.road_rank(l.x, l.y) > 0 or plan.a2.is_river(l.x, l.y))):
			wet += 1
	for pr: Dictionary in m.prisms:
		var c: Rect2i = pr["cell"]
		for di in c.size.x:
			for dj in c.size.y:
				if plan.is_water(c.position.x + di, c.position.y + dj):
					wet += 1
	assert_eq(wet, 0, "no street or building lot is sea")
	var sea := 0
	for i in range(cfg.city_rect.position.x, cfg.city_rect.end.x):
		for j in range(cfg.city_rect.position.y, cfg.city_rect.end.y):
			if plan.is_water(i, j):
				sea += 1
	assert_gt(sea, 0, "A2's bay and coast are sea")


## The Cell's HQ is the HQ nearest A2's Old City (the bay head).
func test_the_cell_holds_the_bay_head() -> void:
	for k in SEEDS:
		var plan := CityPlan.generate(CityGenFixture.seed_of(k), _cfg)
		var head := plan.a2.lot_of(plan.a2.a2.old_city_centre)
		var nearest: StringName = &""
		var best := INF
		var rects := plan.hq_rects(NeonCity.HQ_LOTS)
		var ids: Array = rects.keys()
		IdSort.sort_ids(ids)
		for id: StringName in ids:
			var d := Vector2((rects[id] as Rect2i).get_center()).distance_to(head)
			if d < best:
				best = d
				nearest = id
		assert_eq(nearest, NeonCity.FIST_TERRITORY, "seed %d: the Cell holds the bay head" % CityGenFixture.seed_of(k))


## NA-12 r2: city.json's optional `coast` / `terrain` sections: present and valid (every shoreline lot land beside a sea
## cell, every sea cell sea); CITY-A2 step 2: the terrain's corner heights match the plan's ground.
func test_city_json_carries_the_coast_hills_and_heights() -> void:
	var cfg: CityConfig = CITY_CONFIG
	var sch := preload("res://tools/netrun_art/schema_check.gd")
	var city := NetrunArtExport.city_json(_model.city_seed, cfg.lot_bu, cfg.district_centre, _model.prisms, _model.streets,
		_model.plazas, _model.hqs, _model.city_sections())
	var doc: Dictionary = JSON.parse_string(NetrunArtExport.canonical(city))
	assert_eq(sch.validate(doc, sch.schema("city")), PackedStringArray(), "the schema takes the sections")
	var plan := CityPlan.for_seed(FULL_SEED)
	assert_eq(doc["coast"]["sea_side"], plan.sea_side())
	assert_gt((doc["coast"]["sea_cells"] as Array).size(), 0)
	for c: Array in doc["coast"]["sea_cells"]:
		assert_true(plan.is_water(int(c[0]), int(c[1])))
	var wet := 0
	for c: Array in doc["coast"]["shoreline"]:
		var l := Vector2i(int(c[0]), int(c[1]))
		assert_false(plan.is_water(l.x, l.y), "a shoreline lot is land")
		for d: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			if plan.is_water(l.x + d.x, l.y + d.y):
				wet += 1
				break
	assert_eq(wet, (doc["coast"]["shoreline"] as Array).size(), "every shoreline lot meets the sea")
	assert_eq((doc["terrain"]["hills"] as Array).size(), plan.hills.size())
	var hs: Dictionary = doc["terrain"]["heights"]
	assert_eq([int(hs["size"][0]), int(hs["size"][1])], [plan.rect.size.x + 1, plan.rect.size.y + 1])
	for c: Vector2i in [Vector2i(0, 0), Vector2i(40, 90), Vector2i(plan.rect.size.x, plan.rect.size.y)]:
		var want := plan.ground_at(plan.rect.position.x + c.x, plan.rect.position.y + c.y)
		assert_almost_eq(float(hs["rows"][c.y][c.x]), want, 0.001, "corner %s" % c)


## NA-12 r2: the sea's meshes come from the plan alone: a sea wall face on every shoreline edge, piers where streets
## meet the water, the sea and the void.
func test_the_sea_builds_its_wall_piers_and_void_from_the_plan() -> void:
	var plan := CityPlan.for_seed(FULL_SEED)
	var w: CityWater = autofree(CityWater.make(CITY_CONFIG, plan, _model, CityView3D.OUTER_GROUND_BU))
	var edges := 0
	for l in plan.shoreline():
		for d in CityWater.DIRS:
			if plan.is_water(l.x + d.x, l.y + d.y):
				edges += 1
	assert_eq(w.wall_edges, edges, "one wall face per shore edge")
	assert_gt(w.piers, 0, "streets that reach the water end in piers")
	for n in ["Void", "Sea", "SeaWall", "SeaWallLight", "Piers", "PierLamps"]:
		assert_not_null(w.get_node_or_null(n), n)


func test_the_default_seed_is_an_a2_city() -> void:
	var plan := CityPlan.for_seed(CityPlan.default_seed())
	assert_eq(CityPlan.default_seed(), CITY_CONFIG.city_seed)
	assert_eq(plan.source(), "a2", "CITY-A2 step 2: the default seed is the planner city")
	assert_false(plan.coast.is_empty(), "A2's sea")
	assert_not_null(plan.terrain, "A2's ground")
	assert_eq(CityPlan.current_seed(), CityPlan.default_seed(), "no campaign: the default city")


func test_the_generator_draws_no_global_rng_and_no_campaign_stream() -> void:
	var re := RegEx.create_from_string("(?<![\\w.])(randi|randf|randomize|randf_range|randi_range|randfn|rand_from_seed)\\s*\\(")
	for path in ["res://scripts/city3d/city_a2_builder.gd", "res://scripts/city3d/city_a2_terrain.gd", "res://scripts/city3d/city_plan.gd"]:
		var src := FileAccess.get_file_as_string(path)
		assert_ne(src, "", path)
		var hits := PackedStringArray()
		for m in re.search_all(src):
			hits.append(m.get_string())
		assert_eq(hits, PackedStringArray(), "%s: global RNG calls" % path)
		assert_false(src.contains("RngService"), "%s: no campaign stream" % path)
	RngService.seed_campaign(77)
	var before := JSON.stringify(RngService.to_dict(), "", true)
	CityPlan.generate(CityGenFixture.seed_of(3), _cfg)
	CampaignRules.city_seed_for(77)
	assert_eq(JSON.stringify(RngService.to_dict(), "", true), before, "no campaign stream advanced")
