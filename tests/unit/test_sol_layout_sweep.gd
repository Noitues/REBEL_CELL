extends GutTest
## Solace district layout (A-069 / A-070), full tier: over SEEDS city seeds the Solace layout holds its rules (blocks 2-3 lots,
## 3+ storeys, no interior street, a clear plinth circle, every stair on a path, every park path on lawn), every key finds a
## building, and over Solace campaigns 1..CAMPAIGNS every launchable Site derives a street (no fallback route page, L4).

const SEEDS := 40
const CAMPAIGNS := 20
const TERR := &"solace"


func after_each() -> void:
	RunManager.reset()


func test_rules_over_seeds() -> void:
	var cfg: CampaignConfigData = load(CityPlan.FIXED_CONFIG_PATH)
	var fl := NetrunArtUnits.floor_bu()
	var lot_bu := CityView3D.CONFIG.lot_bu
	var bad := PackedStringArray()
	for k in SEEDS:
		var s := CityGenFixture.seed_of(k)
		var plan := CityPlan.for_seed(s)
		if plan.fallback:
			continue
		var lots := CityA2Builder.lots_for(plan, cfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
		var park: Dictionary = lots.get("solace", {})
		if park.is_empty():
			bad.append("seed %d: no Solace park" % s)
			continue
		var hq: Rect2i = plan.hq_rects(NeonCity.HQ_LOTS)[TERR]
		var centre := Vector2(hq.position) + Vector2(hq.size) * 0.5
		var r_l := float(park["plinth"]["radius_bu"]) / lot_bu
		for c: Dictionary in lots["cells"]:
			var cell: Rect2i = c["cell"]
			if plan.a2.territory(cell.end.x - 1, cell.end.y - 1) != TERR:
				continue
			var top := 0.0
			for e: Dictionary in c["extrusions"]:
				top = maxf(top, float(e["z0"]) + float(e["h"]))
			if top < 3.0 * fl - 0.001:
				bad.append("seed %d: %s only %.1f BU" % [s, cell, top])
			if plan.a2_sites.has(cell.position):
				continue
			if cell.size.x < 2 or cell.size.x > 3 or cell.size.y < 2 or cell.size.y > 3:
				bad.append("seed %d: block %s is %s lots" % [s, cell, cell.size])
			if CitySolaceDistrict._in_circle_rect(cell, centre, r_l):
				bad.append("seed %d: block %s in the plinth circle" % [s, cell])
		bad.append_array(SolSiteCheck.problems(plan, lots, "seed %d" % s))
		var ids := {}
		for p: Dictionary in park["paths"]:
			ids[p["id"]] = true
		for st: Dictionary in park["plinth"]["stairs"]:
			if st["path"] == "" or not ids.has(st["path"]):
				bad.append("seed %d: stair %s has no path" % [s, st["dir"]])
		if bad.size() > 10:
			break
	assert_eq(bad, PackedStringArray(), "%d seeds" % SEEDS)


func test_keys_find_buildings() -> void:
	var corps: Array = []
	var ids: Array = ContentRegistry.all_ids()
	IdSort.sort_ids(ids)
	for cid: Variant in ids:
		var oc := ContentRegistry.get_content(cid) as CorporationData
		if oc != null and oc.city_grid != null:
			corps.append(oc)
	var cfg := CampaignConfigData.new()
	var bad := PackedStringArray()
	for k in SEEDS:
		var s := CityGenFixture.seed_of(k)
		var p := KeyLots.for_seed(s, corps, 6.0)
		var plan := CityPlan.for_seed(s)
		var lots := CityA2Builder.lots_for(plan, CityPlan.plan_config(), NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
		for e in KeyLots.validate(p, lots, plan.hq_rects(NeonCity.HQ_LOTS), cfg, 6.0):
			bad.append("seed %d: %s" % [s, e])
		if bad.size() > 8:
			break
	assert_eq(bad, PackedStringArray(), "every key placed")


func test_solace_street_netruns_derive() -> void:
	RunManager.save_slot = "gut_sol_layout_sweep"
	RunManager.scene_switching_enabled = false
	var fails: Array[String] = []
	var runs := 0
	for s in range(1, CAMPAIGNS + 1):
		RunManager.reset()
		RunManager.new_campaign(s, TERR)
		var cfg := CityView3D.CONFIG
		var city_seed := CityPlan.current_seed()
		var sids: Array[StringName] = []
		for site: SiteData in RunManager.launchable_sites():
			sids.append(site.id)
		for sid in sids:
			RunManager.netrun = null
			var session := RunManager.start_run(&"", sid)
			if session == null:
				fails.append("%d/%s no run" % [s, sid])
				continue
			var d := StreetRouteData.build(session, CityModel.shared(cfg, city_seed), cfg, CityLayout.site_points(RunManager.corporation))
			runs += 1
			if d.error != "":
				fails.append("%d/%s %s" % [s, sid, d.error])
	assert_gt(runs, 0)
	assert_eq(fails, [], "Solace street derive failures: %s" % str(fails))
