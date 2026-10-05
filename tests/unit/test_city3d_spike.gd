extends GutTest
## ART-1 1D (bible §4.1, §6.1; plan §5.1-5.2): the unified-city spike's logic, headless.
## Projection round-trips, ground and building picking, LOD and quality tiers from the
## config (car tiers with hysteresis, see-through band: the Grid solid, the raid at the
## locked v3 opacity), the district from the game's own layout (seeded, deterministic,
## tie-free), the unit-prism instance mapping and the seeded traffic.

const CONFIG := preload("res://tools/spike/city/city_spike_config.tres")

var cfg: CitySpikeConfig = CONFIG
var district: CityDistrict


func before_all() -> void:
	district = CityDistrict.from_layout(cfg)


func test_the_district_is_the_games_layout_and_deterministic() -> void:
	assert_gt(district.prisms.size(), 1000, "a real district of building extrusions")
	assert_gt(district.streets.size(), 500, "with its street lots")
	var again := CityDistrict.from_layout(cfg)
	assert_eq(again.prisms.size(), district.prisms.size())
	for n in [0, district.prisms.size() / 2, district.prisms.size() - 1]:
		assert_eq(again.prisms[n]["poly"], district.prisms[n]["poly"], "same seed, same footprint %d" % n)
		assert_eq(again.prisms[n]["h"], district.prisms[n]["h"])
	for pr in district.prisms:
		assert_lte((pr["centre"] as Vector2).length(), (cfg.district_radius + 12.0) * cfg.lot_bu, "inside the district")


func test_projection_round_trips_through_the_ground() -> void:
	for v: String in cfg.views:
		var cam := CityIsoCamera.for_view(cfg, v, Vector2(1920, 1080))
		assert_almost_eq(cam.project(cam.target), Vector2(960, 540), Vector2(0.01, 0.01), "%s target centred" % v)
		for p in [Vector2(10, 20), Vector2(1900, 1000), Vector2(700, 300)]:
			var w := cam.unproject(p, 0.0)
			assert_almost_eq(w.y, 0.0, 0.001)
			assert_almost_eq(cam.project(w), p, Vector2(0.01, 0.01), "%s pixel %s" % [v, p])
		assert_almost_eq(cam.bu_per_px(), cam.ortho / 1920.0, 0.0001)


func test_the_camera_is_the_locked_iso() -> void:
	var cam := CityIsoCamera.for_view(cfg, "grid", Vector2(1920, 1080))
	var f := cam.forward()
	assert_almost_eq(rad_to_deg(asin(-f.y)), cfg.pitch_deg, 0.001, "pitch 40")
	# Lot +x goes screen right and down, lot +y screen left and down (the game's map).
	var o := cam.project(CityIsoCamera.lot_to_world(cfg, Vector2(30, 30)))
	var px := cam.project(CityIsoCamera.lot_to_world(cfg, Vector2(31, 30)))
	var py := cam.project(CityIsoCamera.lot_to_world(cfg, Vector2(30, 31)))
	assert_gt(px.x, o.x)
	assert_gt(px.y, o.y)
	assert_lt(py.x, o.x)
	assert_gt(py.y, o.y)
	var t := cam.transform()
	assert_almost_eq(-t.basis.z, f, Vector3(0.0001, 0.0001, 0.0001), "Camera3D looks along forward()")


func test_picking_finds_the_building_under_the_cursor() -> void:
	var cam := CityIsoCamera.for_view(cfg, "raid", Vector2(1920, 1080))
	var hits := 0
	for n in range(0, district.prisms.size(), 97):
		var pr: Dictionary = district.prisms[n]
		var c: Vector2 = pr["centre"]
		var top := Vector3(c.x, float(pr["y0"]) + float(pr["h"]) * 0.999, c.y)
		var p := cam.project(top)
		if not Rect2(0, 0, 1920, 1080).has_point(p):
			continue
		var got := district.pick(cam, p)
		assert_ne(got, -1, "something under prism %d" % n)
		if got < 0:
			continue
		# The hit is this prism or one standing in front of it (nearer the camera).
		var t_self := CityDistrict.ray_prism(cam.ray_origin(p), cam.forward(), pr)
		var t_hit := CityDistrict.ray_prism(cam.ray_origin(p), cam.forward(), district.prisms[got])
		assert_lte(t_hit, t_self + 0.001)
		hits += 1
	assert_gt(hits, 5, "picked a sample of buildings")
	# Far outside the district nothing is picked.
	var away := CityIsoCamera.for_view(cfg, "raid", Vector2(1920, 1080))
	away.target = Vector3(20000, 0, 20000)
	assert_eq(district.pick(away, Vector2(960, 540)), -1, "outside the district: nothing")
	assert_eq(district.pick_building(away, Vector2(960, 540)), -1)


func test_lod_and_see_through_come_from_the_config() -> void:
	var grid: float = cfg.views["grid"][2]
	var raid: float = cfg.views["raid"][2]
	assert_eq(CityLod.opacity(cfg, CityIsoCamera.lod_of(cfg, grid)), 1.0, "the City Grid is solid (bible §4.1)")
	assert_almost_eq(CityLod.opacity(cfg, CityIsoCamera.lod_of(cfg, raid)), cfg.see_through_opacity, 0.01,
		"the raid at the locked v3 opacity")
	assert_almost_eq(CityIsoCamera.lod_of(cfg, cfg.lod_ortho_city), 2.0, 0.0001)
	assert_almost_eq(CityIsoCamera.lod_of(cfg, cfg.lod_ortho_raid), 1.0, 0.0001)
	assert_almost_eq(CityIsoCamera.lod_of(cfg, cfg.lod_ortho_transit), 0.0, 0.0001)
	assert_eq(CityLod.detail(cfg, grid), CityLod.Detail.CITY)
	assert_eq(CityLod.detail(cfg, raid), CityLod.Detail.RAID)
	assert_eq(CityLod.detail(cfg, cfg.views["netrun"][2]), CityLod.Detail.TRANSIT)


func test_car_tiers_swap_with_hysteresis() -> void:
	assert_eq(CityLod.car_tier(cfg, cfg.car_far_above + 1.0), CityLod.CarTier.FAR)
	assert_eq(CityLod.car_tier(cfg, (cfg.car_far_above + cfg.car_close_below) * 0.5), CityLod.CarTier.MEDIUM)
	assert_eq(CityLod.car_tier(cfg, cfg.car_close_below - 1.0), CityLod.CarTier.CLOSE)
	var just_in := cfg.car_far_above * (1.0 - cfg.lod_hysteresis * 0.5)
	assert_eq(CityLod.car_tier(cfg, just_in, CityLod.CarTier.FAR), CityLod.CarTier.FAR, "FAR holds inside the band")
	assert_eq(CityLod.car_tier(cfg, just_in, CityLod.CarTier.MEDIUM), CityLod.CarTier.MEDIUM)
	var past := cfg.car_far_above * (1.0 - cfg.lod_hysteresis * 2.0)
	assert_eq(CityLod.car_tier(cfg, past, CityLod.CarTier.FAR), CityLod.CarTier.MEDIUM, "past the band it swaps")
	var close_in := cfg.car_close_below * (1.0 + cfg.lod_hysteresis * 0.5)
	assert_eq(CityLod.car_tier(cfg, close_in, CityLod.CarTier.CLOSE), CityLod.CarTier.CLOSE)


func test_quality_tiers_and_the_deck() -> void:
	var deck := CityLod.quality(cfg, Settings.CITY_QUALITY_STEAM_DECK)
	assert_eq(deck["tier"], 1, "the Deck is tier 1")
	assert_eq(CityLod.quality(cfg, -1)["tier"], cfg.quality_default, "-1 = the renderer default")
	assert_eq(CityLod.quality(cfg, 99)["tier"], cfg.quality_render_scale.size() - 1, "clamped")
	for k in [cfg.quality_shadows, cfg.quality_shadow_size, cfg.quality_msaa, cfg.quality_ink, cfg.quality_fog, cfg.quality_rain]:
		assert_eq((k as Array).size(), cfg.quality_render_scale.size(), "every tier array has every tier")
	assert_eq(cfg.quality_render_scale.size(), Settings.CITY_QUALITY_MAX + 1, "one tier per Settings.city_quality")


func test_instances_map_the_unit_footprint_onto_the_layout() -> void:
	var checked := 0
	for n in range(0, district.prisms.size(), 41):
		var pr: Dictionary = district.prisms[n]
		var poly: PackedVector2Array = pr["poly"]
		var xf := CityMeshKit.instance_transform(poly, pr["y0"], pr["h"])
		var unit := CityMeshKit.unit_footprint(poly.size())
		for k in poly.size():
			var w := xf * Vector3(unit[k].x, 0.0, unit[k].y)
			# The mapped unit corner is one of the footprint's corners.
			var best := INF
			for q in poly:
				best = minf(best, Vector2(w.x, w.z).distance_to(q))
			assert_lt(best, 0.02, "prism %d corner %d" % [n, k])
		assert_almost_eq((xf * Vector3(0, 1, 0)).y, float(pr["y0"]) + float(pr["h"]), 0.001)
		assert_gt(xf.basis.determinant(), 0.0, "never mirrored (culling)")
		checked += 1
	assert_gt(checked, 50)


func test_traffic_is_seeded_on_the_busiest_avenues() -> void:
	var a := CityTraffic.build(cfg, district, 7)
	var b := CityTraffic.build(cfg, district, 7)
	assert_eq(a.cars.size(), b.cars.size())
	assert_gt(a.cars.size(), 50)
	for k in a.cars.size():
		assert_eq(a.cars[k]["color"], b.cars[k]["color"], "same seed, same lane colours")
		assert_true(cfg.lane_colors.has(a.cars[k]["color"]))
	var lines := CityTraffic.avenue_lines(district)
	for k in lines.size() - 1:
		var tk: float = float(lines[k]["traffic"]) * int(lines[k]["n"])
		var tn: float = float(lines[k + 1]["traffic"]) * int(lines[k + 1]["n"])
		assert_gte(tk, tn, "busiest first")
	assert_eq(a.lanes.size(), mini(cfg.sky_lane_heights.size(), lines.size()))
	# A car's loop: back where it started after 1 / speed seconds, on its lane's height.
	var p0 := a.position_at(0, 0.0)
	var period := 1.0 / float(a.cars[0]["speed"])
	assert_almost_eq(a.position_at(0, period), p0, Vector3(0.01, 0.01, 0.01))
	assert_almost_eq(p0.y, cfg.sky_lane_heights[a.cars[0]["lane"]], 0.001)
