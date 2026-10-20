extends GutTest
## Plan 2 EX-02 (REPLAN 2.3): key placement. Each corporation's three Exploit types stand in three distinct special-building
## lots: no lot shared, none on an HQ, footprints on land and clear of each other, a start street lot outside the footprint
## plus clearance; the same inputs give the same placement and bytes; no RNG stream is read or advanced. 1,000 synthetic
## cities here (cheap); the real A2 cities: test_key_lots_sweep.gd (full tier) and one seed below.

const CORPS: Array[StringName] = [&"alpha", &"beta", &"gamma", &"delta", &"epsilon"]
const SIDE := 110
const LOT_BU := 6.0

var _cfg: CampaignConfigData


func before_each() -> void:
	_cfg = CampaignConfigData.new()


## A synthetic city: streets on every 5th row / column, a water strip, 1 x 1 / 2 x 1 building cells elsewhere, HQ plazas.
func _city(seed_v: int) -> Dictionary:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_v
	var R := Rect2i(0, 0, SIDE, SIDE)
	var kind := PackedByteArray()
	kind.resize(SIDE * SIDE)
	var hq := {}
	for id in CORPS:
		hq[id] = Rect2i(rng.randi_range(2, SIDE - 14), rng.randi_range(2, SIDE - 14), 10, 10)
	var wet_x := rng.randi_range(10, SIDE - 20)
	var cells: Array = []
	for j in SIDE:
		for i in SIDE:
			var k := j * SIDE + i
			if i % 5 == 0 or j % 5 == 0:
				kind[k] = CityA2Builder.K_STREET
			elif i >= wet_x and i < wet_x + 3:
				kind[k] = CityA2Builder.K_WATER
	for id in hq:
		var r: Rect2i = hq[id]
		for j in range(r.position.y, r.end.y):
			for i in range(r.position.x, r.end.x):
				kind[j * SIDE + i] = CityA2Builder.K_PLAZA
	for j in SIDE:
		for i in SIDE:
			if kind[j * SIDE + i] == CityA2Builder.K_GROUND:
				kind[j * SIDE + i] = CityA2Builder.K_BUILDING
				var w := 1
				if i + 1 < SIDE and kind[j * SIDE + i + 1] == CityA2Builder.K_GROUND and rng.randf() < 0.3:
					w = 2
					kind[j * SIDE + i + 1] = CityA2Builder.K_BUILDING
				cells.append({"cell": Rect2i(i, j, w, 1), "extrusions": []})
	var corps: Array = []
	var points := {}
	for id in CORPS:
		var c := CorporationData.new()
		c.id = id
		c.city_grid = CityGridData.new()
		var sites: Array[SiteData] = []
		var pts := {}
		for e in [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]:
			var sid := StringName("%s_%d" % [id, e])
			sites.append(GridFixture.site(sid, 2, [], RC.SiteObjective.EXPLOIT, e))
			var hr: Rect2i = hq[id]
			pts[sid] = Vector2(hr.position.x + rng.randi_range(-8, 18), hr.position.y + rng.randi_range(-8, 18))
		c.city_grid.sites = sites
		corps.append(c)
		points[id] = pts
	return {"lots": {"rect": R, "kind": kind, "cells": cells}, "hq": hq, "corps": corps, "points": points}


func _place(c: Dictionary) -> Dictionary:
	return KeyLots.place(c["lots"], c["hq"], c["corps"], c["points"], _cfg, LOT_BU)


func test_a_thousand_synthetic_cities_place_every_key_on_its_own_lot() -> void:
	var bad := PackedStringArray()
	var keys := 0
	for s in 1000:
		var c := _city(s)
		var p := _place(c)
		keys += (p["keys"] as Array).size()
		for e in KeyLots.validate(p, c["lots"], c["hq"], _cfg, LOT_BU):
			if not e.contains("no building within"):  # a crowded synthetic city may leave a key unplaced: counted below
				bad.append("seed %d: %s" % [s, e])
		assert_eq((p["by_bid"] as Dictionary).size(), (p["keys"] as Array).size(), "one record per lot (seed %d)" % s)
		if bad.size() > 5:
			break
	assert_eq(bad, PackedStringArray(), "no shared lot, no HQ lot, footprints clear, starts outside")
	assert_true(keys >= 14250, "95 percent of the 15,000 keys are placed (%d)" % keys)


func test_three_distinct_lots_per_corporation_and_kinds() -> void:
	var c := _city(3)
	var p := _place(c)
	for id in CORPS:
		var by: Dictionary = p["by_corp"][String(id)]
		assert_eq(by.keys().size(), 3, "%s holds all three keys" % id)
		var bids := {}
		for name: String in by:
			bids[by[name]["bid"]] = true
		assert_eq(bids.size(), 3, "%s: three distinct lots" % id)
	_cfg.exploit_building_kinds = {"alpha/virus": "culture_garden"}
	var p2 := _place(c)
	assert_eq(p2["by_corp"]["alpha"]["virus"]["building"], &"culture_garden")
	assert_eq(p2["by_corp"]["alpha"]["intel"]["building"], &"key_intel", "an unbuilt key lot has the placeholder kind")
	var bid: String = p2["by_corp"]["alpha"]["virus"]["bid"]
	assert_eq(KeyLots.special_building_at(p2, bid), &"culture_garden", "the per-lot hook")
	assert_eq(KeyLots.special_building_at(p2, "no:such"), &"")


func test_a_taken_lot_moves_the_next_key_to_a_free_one() -> void:
	var c := _city(4)
	var spot := Vector2(30.5, 31.5)
	for sid: StringName in c["points"][&"alpha"]:
		c["points"][&"alpha"][sid] = spot
	var p := _place(c)
	var got: Dictionary = p["by_corp"]["alpha"]
	var bids := {}
	for name: String in ["intel", "breach", "virus"]:
		bids[got[name]["bid"]] = true
	assert_eq(bids.size(), 3, "three Sites on one spot still get three lots")
	assert_eq(KeyLots.validate(p, c["lots"], c["hq"], _cfg, LOT_BU), PackedStringArray())


func test_same_inputs_same_placement_and_no_stream_advanced() -> void:
	RngService.seed_campaign(99)
	var before := JSON.stringify(RngService.to_dict())
	var a := KeyLots.export_keys(_place(_city(11)), &"gamma")
	var b := KeyLots.export_keys(_place(_city(11)), &"gamma")
	assert_eq(NetrunArtExport.canonical(a), NetrunArtExport.canonical(b), "byte-identical")
	assert_eq(JSON.stringify(RngService.to_dict()), before, "no gameplay stream advanced")
	assert_ne(NetrunArtExport.canonical(a), NetrunArtExport.canonical(KeyLots.export_keys(_place(_city(12)), &"gamma")), "another city, another placement")


func test_occlusion_host_is_left_out_of_the_flatten_set() -> void:
	var c := _city(5)
	var p := _place(c)
	var all: Array = []
	for cell: Dictionary in c["lots"]["cells"]:
		var r: Rect2i = cell["cell"]
		all.append("%d:%d" % [r.position.x, r.position.y])
	var flat := KeyLots.flatten_set(all, p)
	var hosts := KeyLots.occlusion_exempt(p)
	assert_eq(hosts.size(), (p["keys"] as Array).size())
	assert_eq(flat.size(), all.size() - hosts.size(), "only the hosts are left out")
	for h in hosts:
		assert_false(flat.has(h))


func test_key_locations_json_carries_the_key_building() -> void:
	var c := _city(6)
	var p := _place(c)
	var corp: CorporationData = c["corps"][0]
	var doc := NetrunArtExport.key_locations_json(1, corp, c["points"][corp.id], {}, 4, KeyLots.export_keys(p, corp.id))
	assert_false(doc.has("error"), str(doc.get("error", "")))
	assert_eq((doc["locations"] as Array).size(), 3)
	for loc: Dictionary in doc["locations"]:
		assert_eq(loc["bid"], p["by_corp"][String(corp.id)][loc["exploit"]]["bid"])
		assert_true(loc.has("building") and loc.has("start"))


func test_real_city_seed_is_sound_and_byte_identical() -> void:
	var corps: Array = []
	var ids: Array = ContentRegistry.all_ids()
	IdSort.sort_ids(ids)
	for cid: Variant in ids:
		var oc := ContentRegistry.get_content(cid) as CorporationData
		if oc != null and oc.city_grid != null:
			corps.append(oc)
	var p := KeyLots.for_seed(7, corps, LOT_BU)
	var plan := CityPlan.for_seed(7)
	var lots := CityA2Builder.lots_for(plan, CityPlan.plan_config(), NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
	assert_eq(KeyLots.validate(p, lots, plan.hq_rects(NeonCity.HQ_LOTS), _cfg, LOT_BU), PackedStringArray())
	assert_eq((p["keys"] as Array).size(), corps.size() * 3, "every corporation's three keys")
	var a := NetrunArtExport.canonical(KeyLots.export_keys(p, &"solace"))
	CityPlan.forget_all()
	CityA2Builder.forget()
	var b := NetrunArtExport.canonical(KeyLots.export_keys(KeyLots.for_seed(7, corps, LOT_BU), &"solace"))
	assert_eq(a, b, "byte-identical after a rebuild from scratch")
