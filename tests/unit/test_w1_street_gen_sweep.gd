extends GutTest
## W1 close: the street derive on the generated city. For campaign seeds 1..20 (the corporation rotates with the seed, so each
## sees four cities) and every launchable Site, plus the three Orbital cities that once ran out of frontage (seeds 3, 6, 17; the
## 1000-run sweep of 5 corporations x 20 seeds found only those), the street netrun builds on the campaign's own city
## (CityPlan.current_seed) without a derive error.

const SEEDS := 20
const CORPS: Array[StringName] = [&"halcyon", &"meridian", &"orbital", &"rebel_cell", &"solace"]
const HARD_ORBITAL: Array[int] = [3, 6, 17]


func after_each() -> void:
	RunManager.reset()


func _combos() -> Array:
	var out: Array = []
	for s in range(1, SEEDS + 1):
		out.append([s, CORPS[s % CORPS.size()]])
	for s: int in HARD_ORBITAL:
		if CORPS[s % CORPS.size()] != &"orbital":
			out.append([s, &"orbital"])
	return out


func test_every_launchable_site_derives_on_generated_cities() -> void:
	RunManager.save_slot = "gut_w1_sweep"
	RunManager.scene_switching_enabled = false
	var fails: Array[String] = []
	var runs := 0
	for combo: Array in _combos():
		var s: int = combo[0]
		var corp: StringName = combo[1]
		RunManager.reset()
		RunManager.new_campaign(s, corp)
		var cfg := CityView3D.CONFIG
		var city_seed := CityPlan.current_seed()
		assert_eq(city_seed, RunManager.campaign.city_seed, "the street builds on the campaign's city")
		var ids: Array[StringName] = []
		for site: SiteData in RunManager.launchable_sites():
			ids.append(site.id)
		for sid in ids:
			RunManager.netrun = null
			var session := RunManager.start_run(&"", sid)
			if session == null:
				fails.append("%s/%d/%s no run" % [corp, s, sid])
				continue
			var d := StreetRouteData.build(session, CityModel.shared(cfg, city_seed), cfg, CityLayout.site_points(RunManager.corporation))
			runs += 1
			if d.error != "":
				fails.append("%s/%d/%s %s" % [corp, s, sid, d.error])
	assert_gt(runs, 0)
	assert_eq(fails, [], "street derive failures: %s" % str(fails))
