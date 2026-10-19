extends GutTest
## NA-11: the layout rules on the game's FULL city (CityModel.finish -> CityLayoutRuler) at 3 seeds: no street-front building
## under 6 floors, ids unique and HQ rects exclusive, HQ stand-ins untouched, same seed same heights, rules switch off.

const CITY_CONFIG := "res://content/config/city_config.tres"
const SEEDS: Array[int] = [7, -1, 424242]

var _cfg: CityConfig
var _plain: CityConfig


func before_all() -> void:
	_cfg = load(CITY_CONFIG)
	_plain = _cfg.duplicate() as CityConfig
	_plain.layout_rules_on = false


func _corps() -> Array:
	var out: Array = []
	for cid: StringName in ContentRegistry.all_ids():
		var c := ContentRegistry.get_content(cid) as CorporationData
		if c != null and c.city_grid != null:
			out.append(c)
	return out


func _heights(m: CityModel) -> Array:
	var out: Array = []
	for pr: Dictionary in m.prisms:
		out.append([float(pr["y0"]), float(pr["h"])])
	return out


func test_frontage_ids_hq_and_determinism_at_three_seeds() -> void:
	var fl := NetrunArtUnits.floor_bu()
	for s in SEEDS:
		var ruled := CityModel.build(_cfg, s)
		var plain := CityModel.build(_plain, s)
		assert_gt(ruled.ruled_parts, 0, "seed %d: the rules changed prisms" % s)
		assert_eq(plain.ruled_parts, 0, "seed %d: switched off, nothing changed" % s)
		assert_eq(ruled.prisms.size(), plain.prisms.size(), "seed %d: no prism added or dropped" % s)
		# the frontage set on the plain geometry
		var city := NetrunArtExport.city_json(plain.city_seed, _cfg.lot_bu, _cfg.district_centre, plain.prisms, plain.streets,
			plain.plazas, plain.hqs)
		var plan_s := CityPlan.for_seed(s)  # NA-12: the seed's own city (the rules use it), not the running campaign's
		var net := CityLayoutRuler.fixed_net(s, _cfg, _corps(), func(c: CorporationData) -> Dictionary: return CityLayout.site_points_in(c, plan_s))
		var bases := NetrunArtLayout.merged_buildings(city)
		var front := {}
		for link: Dictionary in NetrunArtLayoutRules.links_of(net, "all"):
			var legs: Array = NetrunArtLayout.link_legs(city, link["pts"])
			for i in range(legs.size() - 1):
				var rows := NetrunArtLayoutRules.frontage_rows(bases, legs[i], legs[i + 1])
				for side: int in [1, -1]:
					for bi: Dictionary in rows[side]:
						front[bi["bid"]] = true
		assert_gt(front.size(), 0, "seed %d has a frontage" % s)
		var after := NetrunArtExport.city_json(ruled.city_seed, _cfg.lot_bu, _cfg.district_centre, ruled.prisms, ruled.streets,
			ruled.plazas, ruled.hqs)
		var tops := {}
		for bi: Dictionary in NetrunArtLayout.merged_buildings(after):
			tops[bi["bid"]] = bi["h"]
		var low: Array = []
		for bid: String in front:
			if int(float(tops[bid]) / fl + 1.0e-9) < 6:
				low.append(bid)
		assert_eq(low, [], "seed %d: frontage buildings under 6 floors" % s)
		# ids unique, HQ rects exclusive
		assert_eq(NetrunArtExport.bid_conflicts(ruled.prisms).size(), 0, "seed %d: ids unique" % s)
		assert_eq((after["hq_overlaps"] as Array).size(), 0, "seed %d: HQ rects hold no city building" % s)
		var ids := {}
		for b: Dictionary in after["buildings"]:
			assert_false(ids.has(b["bid"]), "seed %d: %s once" % [s, b["bid"]])
			ids[b["bid"]] = true
		# HQ stand-ins are exempt (untouched)
		for i in ruled.prisms.size():
			if bool(ruled.prisms[i].get("hq", false)):
				assert_eq(float(ruled.prisms[i]["h"]), float(plain.prisms[i]["h"]), "seed %d: HQ stand-in height" % s)
		# deterministic
		assert_eq(_heights(CityModel.build(_cfg, s)), _heights(ruled), "seed %d: same seed, same heights" % s)


## NA-11c: within 2 lots of an HQ lot no building is taller than 0.6x the HQ top, and nothing there is a spike (the live
## full city at 3 seeds); the spikes elsewhere are at most `spikes_max`.
func test_hq_zone_cap_and_spike_exemption_at_three_seeds() -> void:
	var hp: Dictionary = NetrunArtConfigData.shipped().layout_rules["hq"]
	var spikes_max: int = int(NetrunArtConfigData.shipped().layout_rules["horizon"]["spikes_max"])
	for s in SEEDS:
		var ruled := CityModel.build(_cfg, s)
		var plain := CityModel.build(_plain, s)
		var before := NetrunArtExport.city_json(plain.city_seed, _cfg.lot_bu, _cfg.district_centre, plain.prisms, plain.streets,
			plain.plazas, plain.hqs)
		var after := NetrunArtExport.city_json(ruled.city_seed, _cfg.lot_bu, _cfg.district_centre, ruled.prisms, ruled.streets,
			ruled.plazas, ruled.hqs)
		var hq_list := NetrunArtLayoutRules.hq_rects(after)
		assert_gt(hq_list.size(), 0, "seed %d has HQs" % s)
		var reach: float = float(hp["zone_lots"]) * _cfg.lot_bu
		var over: Array = []
		var in_zone := 0
		for bi: Dictionary in NetrunArtLayout.merged_buildings(after):
			var top := NetrunArtLayoutRules.hq_zone_top(hq_list, reach, bi)
			if is_nan(top):
				continue
			in_zone += 1
			if float(bi["h"]) > float(hp["cap_k"]) * top + 1.0e-6:
				over.append(bi["bid"])
		assert_gt(in_zone, 0, "seed %d: buildings stand in the HQ zone" % s)
		assert_eq(over, [], "seed %d: zone buildings above the cap" % s)
		# spikes: the stats of the pass on the plain city
		var plan_s := CityPlan.for_seed(s)  # NA-12: the seed's own city (the rules use it), not the running campaign's
		var net := CityLayoutRuler.fixed_net(s, _cfg, _corps(), func(c: CorporationData) -> Dictionary: return CityLayout.site_points_in(c, plan_s))
		var st := {}
		NetrunArtLayoutRules.apply_rules(before, net, {}, "all", st)
		assert_between(int(st.get("spikes", 0)), 0, spikes_max, "seed %d: spikes" % s)

## The async path (rules deferred, run on a worker thread, landed on the main thread) gives the synchronous heights.
func test_worker_thread_rules_match_synchronous_heights() -> void:
	var s := SEEDS[0]
	var sync := CityModel.build(_cfg, s)
	var m := CityModel.build(_plain, s)
	m.cfg = _cfg
	var job := m.layout_rules_job()
	assert_false(job.is_empty(), "the rules job exists for the full city")
	var task := WorkerThreadPool.add_task(func() -> void: CityLayoutRuler.run_job(job), true, "test layout rules")
	WorkerThreadPool.wait_for_task_completion(task)
	m.ruled_parts = CityLayoutRuler.land_job(m, job)
	assert_eq(m.ruled_parts, sync.ruled_parts, "same count of prisms changed")
	assert_eq(_heights(m), _heights(sync), "worker rules == synchronous rules")
