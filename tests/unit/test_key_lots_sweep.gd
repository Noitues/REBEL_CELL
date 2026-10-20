extends GutTest
## Plan 2 EX-02, full tier: key placement on real A2 cities. Every corporation's three keys land on distinct building lots
## with no HQ lot, sound footprints and a start street lot, for SEEDS city seeds (a seed's plan and subdivision is ~0.4 s,
## so the real-city sweep is 200 seeds; test_key_lots.gd sweeps 1,000 synthetic cities).

const SEEDS := 200
const LOT_BU := 6.0


func test_two_hundred_real_cities() -> void:
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
		var p := KeyLots.for_seed(s, corps, LOT_BU)
		var plan := CityPlan.for_seed(s)
		var lots := CityA2Builder.lots_for(plan, CityPlan.plan_config(), NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
		for e in KeyLots.validate(p, lots, plan.hq_rects(NeonCity.HQ_LOTS), cfg, LOT_BU):
			bad.append("seed %d: %s" % [s, e])
		if (p["keys"] as Array).size() != corps.size() * 3:
			bad.append("seed %d: %d keys" % [s, (p["keys"] as Array).size()])
		CityPlan.forget_all()
		CityA2Builder.forget()
		if bad.size() > 8:
			break
	assert_eq(bad, PackedStringArray(), "%d real cities place every key" % SEEDS)
