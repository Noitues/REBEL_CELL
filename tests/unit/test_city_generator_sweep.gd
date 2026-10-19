extends GutTest
## Plan 2 NA-12 (D3), full tier: the city generator over 1,000 seeds. Every seed generates (no
## fallback) within the config's time budget (`city_gen_budget_s`, this machine); every
## corporation's HQ rect is exclusive and every Site on land inside the city, off another HQ;
## and on FULL_SEEDS whole cities, `hq_overlaps` is empty, every Site has a building and every
## Grid link a street route (CityGenFixture.full_city_problems).

const CITY_CONFIG := preload("res://content/config/city_config.tres")
const SWEEP_SEEDS := 1000
const FULL_SEEDS: Array[int] = [1, 2, 3, -5, 99991, 123456789, -42, 2026101900]


func test_1000_seeds_generate_within_the_budget_with_exclusive_hqs_and_sites_on_land() -> void:
	var cfg: CampaignConfigData = load(CityPlan.FIXED_CONFIG_PATH)
	var list := CityGenFixture.corps()
	var bad := 0
	var fallbacks := 0
	var worst_us := 0
	var retried := 0
	for k in SWEEP_SEEDS:
		var s := CityGenFixture.seed_of(k) * 31 + k
		var t0 := Time.get_ticks_usec()  # fixed-wait-ok: the generator time budget (NA-12 acceptance 5), a performance bound
		var plan := CityPlan.generate(s, cfg)
		worst_us = maxi(worst_us, Time.get_ticks_usec() - t0)  # fixed-wait-ok: as above
		if plan.fallback:
			fallbacks += 1
		if plan.attempts > 1:
			retried += 1
		var probs := CityGenFixture.plan_problems(plan, list)
		if not probs.is_empty():
			bad += 1
			gut.p("seed %d: %s" % [s, ", ".join(probs)])
	gut.p("NA-12 sweep: %d seeds, %d retried, %d fallbacks, slowest %.1f ms (budget %.0f ms)" % [SWEEP_SEEDS, retried, fallbacks,
		worst_us / 1000.0, cfg.city_gen_budget_s * 1000.0])
	assert_eq(fallbacks, 0, "every seed generates")
	assert_eq(bad, 0, "every plan holds")
	assert_lt(worst_us / 1.0e6, cfg.city_gen_budget_s, "every seed inside the time budget")


func test_whole_cities_hold_their_hqs_sites_and_streets() -> void:
	var list := CityGenFixture.corps()
	for s in FULL_SEEDS:
		var m := CityModel.build(CITY_CONFIG, s)
		assert_eq(CityGenFixture.full_city_problems(m, list), PackedStringArray(), "seed %d" % s)
