extends GutTest
## Plan 2 NA-12 (D3), fast tier: the per-seed city generator on 50 seeds. Same seed, same plan
## (and a byte-identical full-city `city.json`); every corporation's HQ rect is exclusive
## (no other HQ, inside the city, off the water); every Site of every corporation lies on land
## inside the city and off another HQ; on full cities every Site has a building and every Grid
## link a street route; no global RNG; the fixed seed is today's city; the generator advances
## no campaign stream. The 1,000-seed sweep and the time budget: test_city_generator_sweep.gd.

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
		assert_false(plan.fallback, "seed %d: a generated layout" % CityGenFixture.seed_of(k))
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
		if plan.is_water((st["lot"] as Vector2i).x, (st["lot"] as Vector2i).y):
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
	assert_gt(sea, cfg.city_rect.size.x * int(_cfg.city_gen_coast_depth.x - _cfg.city_gen_coast_wave.y) - 1, "a coast strip of sea")


func test_the_fixed_seed_is_todays_city() -> void:
	var plan := CityPlan.for_seed(CityPlan.fixed_seed())
	assert_eq(CityPlan.fixed_seed(), CITY_CONFIG.city_seed)
	assert_true(plan.fixed)
	assert_true(plan.coast.is_empty(), "no sea")
	assert_eq(plan.territories.size(), NeonCity.TERRITORIES.size())
	for k in NeonCity.TERRITORIES.size():
		assert_eq(plan.territories[k]["id"], NeonCity.TERRITORIES[k]["id"])
		assert_eq(plan.territories[k]["at"], NeonCity.TERRITORIES[k]["at"])
		assert_eq(plan.territories[k]["pull"], NeonCity.TERRITORIES[k]["pull"])
	for cid: StringName in CITY_CONFIG.site_aim_deg:
		assert_eq(plan.site_aim[cid], float(CITY_CONFIG.site_aim_deg[cid]))
	assert_eq(CityPlan.current_seed(), CityPlan.fixed_seed(), "no campaign: the fixed city")


func test_the_generator_draws_no_global_rng_and_no_campaign_stream() -> void:
	var re := RegEx.create_from_string("(?<![\\w.])(randi|randf|randomize|randf_range|randi_range|randfn|rand_from_seed)\\s*\\(")
	for path in ["res://scripts/city3d/city_generator.gd", "res://scripts/city3d/city_plan.gd"]:
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
