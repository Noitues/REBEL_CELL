extends GutTest
## ART-5 5c (ART_BIBLE §4.1 car LOD, §4.2 city motion, §4.3 Heat on maps, §5.3, §5.4, §6.1):
## the city's motion layers, headless. The sky lanes' 16 road shapes as baked paths (uniform
## by arc length, the shader's interpolation on the CPU), cars with whole gaps per loop and
## colours from the seeded `city_traffic` stream (same seed, same colours), the car tier by
## ortho with hysteresis, the Heat rig per band (PURGE = HUNTED's look, centred on the
## hardened nodes), the ambient props, the pause / reduce rules, and the layer node: pauses
## when covered or unfocused, end state under reduce effects, markers only under reduce
## motion, LOD swaps, the day / night crossfade, every motion in the table as T0.

const CITY_CONFIG := preload("res://content/config/city_config.tres")
## A part of the game's city (lots) for the model test: the Halcyon border round the raid frame.
const MODEL_RECT := Rect2i(10, 0, 48, 48)

var cfg: CityMotionConfigData
var site: CityMotionSite
var lanes: CitySkyLanes
var _reduce_effects: bool = false
var _reduce_motion: bool = false


func before_all() -> void:
	cfg = CityMotionConfigData.shipped()
	site = CityMotionSite.grid()
	lanes = CitySkyLanes.build(cfg, site)
	_reduce_effects = Settings.reduce_effects
	_reduce_motion = Settings.reduce_motion


func after_each() -> void:
	Settings.reduce_effects = _reduce_effects
	Settings.reduce_motion = _reduce_motion
	Motion.force_live = false


func test_the_config_validates_and_every_motion_is_a_t0_table_entry() -> void:
	assert_not_null(cfg, "the shipped city motion config loads")
	assert_eq(cfg.validate().size(), 0, "the shipped config validates: %s" % [cfg.validate()])
	var bad := CityMotionConfigData.new()
	bad.lane_colors = [Color.RED]
	bad.band_police = [1]
	assert_eq(bad.validate().size(), 2, "a short palette and a short band array are refused")
	for id in CityMotionLayers.MOTION_IDS:
		assert_true(Motion.has(id), "%s is in ui_motion.tres" % id)
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is a required id" % id)
		var e := Motion.entry(id)
		assert_eq(int(e.tier), VfxTier.T0, "%s is T0 ambient" % id)
		assert_true(VfxTier.fits(e), "%s fits its tier" % id)
	# Police strobes stay under 3 Hz (bible 5.4): two colours alternate within one period.
	assert_gte(Motion.entry(CityMotionLayers.STROBE).duration, 2.0 / 3.0, "strobe flashes stay under 3 Hz")


func test_the_sixteen_road_shapes_are_laid_on_the_avenues() -> void:
	var names: Array[String] = []
	for rd in lanes.roads:
		names.append(String(rd["name"]))
		var rows: PackedInt32Array = rd["rows"]
		assert_eq(rows.size(), 1 if bool(rd["oneway"]) else 2, "%s: one row a direction" % rd["name"])
	names.sort()
	var want := CitySkyLanes.ROAD_NAMES.duplicate()
	want.sort()
	assert_eq(names, want, "the grid city carries all 16 road shapes")
	var picks := CitySkyLanes.pick_avenues(cfg, site)
	var a: Dictionary = picks["h"][0]
	var f: Dictionary = picks["v"][0]
	var x := CitySkyLanes.crossing(a, f, 0.0)
	# A cloverleaf loop leaves A's lower deck on A's line and lands on F's deck on F's line.
	var clover := _road("clover_0")
	var row := int((clover["rows"] as PackedInt32Array)[0])
	var start := site.world_to_lot(lanes.sample(row, 0.0))
	var end := site.world_to_lot(lanes.sample(row, 1.0))
	assert_almost_eq(start.y, x.y, 0.01, "the loop starts on A")
	assert_almost_eq(end.x, x.x, 0.01, "and ends on F")
	assert_almost_eq(lanes.sample(row, 0.0).y, cfg.deck_a_low, 0.01, "at A's lower deck")
	assert_almost_eq(lanes.sample(row, 1.0).y, cfg.deck_f, 0.01, "rising to F's deck")
	# 270 degrees of a circle of clover_radius (three quarters of its circumference), climbing
	# from A's deck to F's on the way.
	var arc := 1.5 * PI * cfg.clover_radius * site.lot_bu
	var climb := cfg.deck_f - cfg.deck_a_low
	assert_between(float(lanes.rows[row]["length"]), sqrt(arc * arc + climb * climb) - 0.3, arc + climb, "a 270-degree loop")
	var spiral := int((_road("C_spiral")["rows"] as PackedInt32Array)[0])
	assert_almost_eq(lanes.sample(spiral, 1.0).y, cfg.spiral_floor, 0.01, "the spiral lands at street level")
	var stack := int((_road("stack_2")["rows"] as PackedInt32Array)[0])
	var top := 0.0
	for k in 21:
		top = maxf(top, lanes.sample(stack, k / 20.0).y)
	assert_gt(top, cfg.deck_e, "a wide stack flyover climbs over both decks")


func test_rows_are_uniform_by_arc_length_and_the_bake_matches_the_cpu() -> void:
	var img := lanes.bake()
	assert_eq(img.get_height(), lanes.rows.size(), "one texel row per lane row")
	assert_eq(img.get_width(), cfg.bake_samples)
	for r in [0, lanes.rows.size() / 2, lanes.rows.size() - 1]:
		var pts: PackedVector3Array = lanes.rows[r]["points"]
		var step := float(lanes.rows[r]["length"]) / float(pts.size() - 1)
		for k in range(1, pts.size(), 37):
			assert_almost_eq(pts[k].distance_to(pts[k - 1]), step, step * 0.35 + 0.01, "row %d sample %d evenly spaced" % [r, k])
		var px := img.get_pixel(100, r)
		assert_almost_eq(Vector3(px.r, px.g, px.b), pts[100], Vector3(0.01, 0.01, 0.01), "the texture holds the row")
		assert_almost_eq(px.a, float(lanes.rows[r]["length"]), 0.01, "and its length")
		# The shader's interpolation between two texels, on the CPU.
		var s := 100.5 / float(pts.size() - 1)
		assert_almost_eq(lanes.sample(r, s), pts[100].lerp(pts[101], 0.5), Vector3(0.001, 0.001, 0.001))
	# The two directions of a two-way road run opposite ways, either side of the centre.
	var rows: PackedInt32Array = _road("B")["rows"]
	var fw := lanes.sample(rows[0], 0.5)
	var bw := lanes.sample(rows[1], 0.5)
	assert_almost_eq(fw.distance_to(bw), cfg.lane_side * 2.0, 0.05, "the two directions sit lane_side either side")
	assert_almost_eq(lanes.sample(rows[0], 0.0).distance_to(lanes.sample(rows[1], 1.0)), cfg.lane_side * 2.0, 0.05, "reversed")


func test_the_lanes_on_the_city_model_are_deterministic() -> void:
	var m := CityModel.build(CITY_CONFIG, 7, MODEL_RECT)
	var s1 := CityMotionSite.from_model(m, CITY_CONFIG)
	var l1 := CitySkyLanes.build(cfg, s1)
	var l2 := CitySkyLanes.build(cfg, CityMotionSite.from_model(m, CITY_CONFIG))
	assert_gte(l1.roads.size(), 6, "the busiest avenues carry at least the six straight roads")
	assert_eq(l1.rows.size(), l2.rows.size())
	for r in l1.rows.size():
		assert_eq(l1.rows[r]["points"], l2.rows[r]["points"], "row %d the same each build" % r)
	assert_gt(l1.street_rows.size(), 0, "busy avenues carry street traffic")
	assert_gt(s1.roofs.size(), 500, "every building's roof reaches the layers")
	assert_true(s1.bounds.has_point(s1.home), "home inside the city's bounds")


func test_car_colours_are_seeded_and_every_loop_moves_whole_gaps() -> void:
	var loop := 3.84
	var a := CitySkyTraffic.build(cfg, lanes, 7, loop, 2.4, site.lot_bu)
	var b := CitySkyTraffic.build(cfg, lanes, 7, loop, 2.4, site.lot_bu)
	var c := CitySkyTraffic.build(cfg, lanes, 8, loop, 2.4, site.lot_bu)
	assert_gt(a.cars.size(), 50, "the lanes carry cars")
	assert_eq(a.cars, b.cars, "same seed, same cars and colours")
	assert_eq(a.street_cars, b.street_cars, "and the same street cars")
	var colours_a: Array = a.cars.map(func(x: Dictionary) -> int: return x["color"])
	var colours_c: Array = c.cars.map(func(x: Dictionary) -> int: return x["color"])
	assert_ne(colours_a, colours_c, "another seed, other colours")
	var used := {}
	for car in a.cars:
		used[car["color"]] = true
		assert_between(int(car["color"]), 0, 5, "one of the six lane colours")
		assert_between(float(car["streak"]), cfg.streak_length.x, cfg.streak_length.y)
	assert_eq(used.size(), 6, "every lane colour is in use")
	for r in lanes.rows.size():
		var n := maxi(1, roundi(float(lanes.rows[r]["length"]) / cfg.car_gap))
		for car in a.cars:
			if int(car["row"]) == r:
				var gaps := float(car["speed"]) * loop * n
				assert_almost_eq(gaps, roundf(gaps), 0.001, "row %d: a whole number of gaps per loop" % r)
				assert_between(roundi(gaps), cfg.gaps_per_loop.x, cfg.gaps_per_loop.y, "14-20 gaps a loop")
				break
	# position_at follows the row.
	var car0: Dictionary = a.cars[0]
	assert_almost_eq(a.position_at(lanes, 0, 1.0), lanes.sample(int(car0["row"]), CitySkyTraffic.share_at(car0, 1.0)),
		Vector3(0.0001, 0.0001, 0.0001))


func test_the_car_tier_follows_ortho_with_hysteresis() -> void:
	var F := CitySkyTraffic.CarTier.FAR
	var M := CitySkyTraffic.CarTier.MEDIUM
	var C := CitySkyTraffic.CarTier.CLOSE
	assert_eq(CitySkyTraffic.car_tier(cfg, 440.0), F, "City Grid (ortho 440): FAR")
	assert_eq(CitySkyTraffic.car_tier(cfg, 380.0), M, "raid (380): MEDIUM")
	assert_eq(CitySkyTraffic.car_tier(cfg, 60.0), C, "close (60): CLOSE")
	var h := cfg.lod_hysteresis
	assert_eq(CitySkyTraffic.car_tier(cfg, cfg.car_far_above * (1.0 - h * 0.5), F), F, "FAR holds inside the band")
	assert_eq(CitySkyTraffic.car_tier(cfg, cfg.car_far_above * (1.0 - h * 1.5), F), M, "and swaps past it")
	assert_eq(CitySkyTraffic.car_tier(cfg, cfg.car_far_above * (1.0 + h * 0.5), M), M, "MEDIUM holds above its edge")
	assert_eq(CitySkyTraffic.car_tier(cfg, cfg.car_far_above * (1.0 + h * 1.5), M), F)
	assert_eq(CitySkyTraffic.car_tier(cfg, cfg.car_close_below * (1.0 + h * 0.5), C), C, "CLOSE holds")
	assert_eq(CitySkyTraffic.car_tier(cfg, cfg.car_close_below * (1.0 + h * 1.5), C), M)
	assert_eq(CitySkyTraffic.car_tier(cfg, cfg.car_close_below * (1.0 - h * 0.5), M), M)


func test_the_heat_rig_per_band_is_centred_on_the_hardened_nodes() -> void:
	var nodes: Array[Vector3] = [site.lot_to_world(Vector2(12, 12)), site.lot_to_world(Vector2(18, 14))]
	var none: Array[Vector3] = []
	var cool := CityHeatRig.build(cfg, site, CityHeatRig.Band.COOL, none, false)
	assert_eq(cool.searchlights.size() + cool.alarms.size() + cool.police.size() + cool.choppers.size() + cool.drones.size(), 0,
		"COOL: no Heat lights")
	for band in [CityHeatRig.Band.NOTICED, CityHeatRig.Band.FLAGGED, CityHeatRig.Band.HUNTED]:
		var r := CityHeatRig.build(cfg, site, band, nodes, false)
		assert_eq(r.searchlights.size(), cfg.band_searchlights[band], "band %d searchlights" % band)
		assert_eq(r.alarms.size(), cfg.band_alarms[band], "band %d alarms" % band)
		assert_eq(r.police.size(), cfg.band_police[band], "band %d police" % band)
		assert_eq(r.choppers.size(), cfg.band_choppers[band])
		assert_eq(r.drones.size(), cfg.band_drones[band])
		assert_eq(r.node_lights.size(), 2, "one circling light per hardened node")
		var reach := cfg.rig_radius_lots * site.lot_bu
		for p: Vector3 in r.searchlights.map(func(x: Dictionary) -> Vector3: return x["pos"]) + r.alarms.map(func(x: Dictionary) -> Vector3: return x["pos"]):
			assert_lte(Vector2(p.x - r.centre.x, p.z - r.centre.z).length(), reach, "placed round the hardened nodes")
	var calm := CityHeatRig.build(cfg, site, CityHeatRig.Band.FLAGGED, nodes, false)
	assert_almost_eq(calm.centre, (nodes[0] + nodes[1]) * 0.5, Vector3(0.001, 0.001, 0.001), "centred on the hardened nodes")
	assert_false(bool(calm.node_lights[0]["blue"]), "red, then")
	assert_true(bool(calm.node_lights[1]["blue"]), "blue, alternating")
	var hunted := CityHeatRig.build(cfg, site, CityHeatRig.Band.HUNTED, nodes, false)
	var purge := CityHeatRig.build(cfg, site, CityHeatRig.Band.PURGE, nodes, false)
	assert_eq(purge.signature(), hunted.signature(), "PURGE uses HUNTED's look (designer ruling 2026-10-05)")
	assert_eq(CityHeatRig.build(cfg, site, CityHeatRig.Band.HUNTED, nodes, false).signature(), hunted.signature(), "deterministic")
	var sus := CityHeatRig.build(cfg, site, CityHeatRig.Band.COOL, none, true)
	assert_eq(sus.police.size(), cfg.suspicion_police, "suspicion: police round home")
	assert_eq(sus.choppers.size(), cfg.suspicion_choppers)
	assert_eq(sus.drones.size(), cfg.suspicion_drones)


func test_ambient_props_are_seeded() -> void:
	var a := CityAmbientProps.build(cfg, site, 7)
	var b := CityAmbientProps.build(cfg, site, 7)
	assert_eq(a.aviation, b.aviation, "same seed, same aviation lights")
	assert_eq(a.billboards, b.billboards, "and billboards")
	assert_eq(a.aviation.size(), mini(cfg.aviation_count, site.roofs.size()))
	var tallest := 0.0
	for rf in site.roofs:
		tallest = maxf(tallest, float(rf["h"]))
	assert_almost_eq((a.aviation[0]["pos"] as Vector3).y, tallest, 0.001, "aviation lights start on the tallest roof")
	assert_gt(a.billboards.size(), 0)
	for i in a.billboards.size():
		for j in range(i + 1, a.billboards.size()):
			var p: Vector3 = a.billboards[i]["pos"]
			var q: Vector3 = a.billboards[j]["pos"]
			assert_gte(Vector2(p.x - q.x, p.z - q.z).length(), CityAmbientProps.BILLBOARD_SPACING_LOTS * site.lot_bu - 0.001, "spaced")


func test_the_pause_and_reduce_rules() -> void:
	var L := CityMotionClock.Layer
	for layer in CityMotionClock.COUNT:
		assert_eq(CityMotionClock.rate(cfg, layer, true, false, true), 0.0, "paused: layer %d stops" % layer)
		assert_eq(CityMotionClock.rate(cfg, layer, false, false, false), 0.0, "not live: layer %d holds" % layer)
		assert_true(CityMotionClock.steady(layer, false, false), "not live: end state")
		assert_eq(CityMotionClock.rate(cfg, layer, false, false, true), 1.0, "live: full speed")
		assert_false(CityMotionClock.steady(layer, false, true))
	assert_almost_eq(CityMotionClock.rate(cfg, L.STREET_CARS, false, true, true), cfg.reduce_motion_street_rate, 0.0001,
		"reduce motion: street traffic at its share (bible 5.4: 40 %)")
	assert_almost_eq(cfg.reduce_motion_street_rate, 0.4, 0.0001, "the shipped share is the bible's 40 %")
	assert_eq(CityMotionClock.rate(cfg, L.STREET_CARS, true, true, true), 0.0, "covered under reduce motion: still paused")
	assert_eq(CityMotionClock.rate(cfg, L.SKY_CARS, false, true, true), 0.0, "reduce motion: no sky-lane cars run")
	assert_eq(CityMotionClock.rate(cfg, L.SEARCHLIGHTS, false, true, true), 0.0, "reduce motion: searchlights fixed")
	assert_true(CityMotionClock.steady(L.STROBES, true, true), "reduce motion: strobes steady")
	assert_false(CityMotionClock.street_streaks(true), "no streaks under reduce motion")
	assert_false(CityMotionClock.sky_cars_shown(true, false), "reduce motion: sky-lane markers without cars")
	assert_false(CityMotionClock.sky_cars_shown(false, true), "netrun transit: the sky-lane car layer is off")
	assert_true(CityMotionClock.sky_cars_shown(false, true, true), "ART-7 7w: a netrun close-up shows the CLOSE tier")
	assert_false(CityMotionClock.sky_cars_shown(true, true, true), "reduce motion: still no cars")
	var clock := CityMotionClock.new()
	var rates := PackedFloat64Array()
	var live: Array[bool] = []
	for k in CityMotionClock.COUNT:
		rates.append(1.0)
		live.append(true)
	clock.advance(0.5, rates, live)
	live[L.BILLBOARDS] = false
	clock.advance(0.5, rates, live)
	assert_almost_eq(clock.times[L.SKY_CARS], 1.0, 0.0001)
	assert_eq(clock.times[L.BILLBOARDS], 0.0, "a held layer goes back to its end state")


func _layers() -> CityMotionLayers:
	var layers := CityMotionLayers.new()
	add_child_autofree(layers)
	layers.setup(cfg, site, 7)
	layers.honour_focus = true
	return layers


func test_the_layers_pause_when_covered_or_unfocused() -> void:
	Settings.reduce_effects = false
	Settings.reduce_motion = false
	Motion.force_live = true
	var layers := _layers()
	var L := CityMotionClock.Layer
	layers._process(0.25)
	var t := layers.layer_time(L.SKY_CARS)
	assert_almost_eq(t, 0.25, 0.0001, "the sky lanes run")
	var scales: Array[float] = []
	layers.ambient_scale_changed.connect(func(s: float) -> void: scales.append(s))
	layers.set_covered(true)
	layers._process(0.25)
	assert_eq(layers.layer_time(L.SKY_CARS), t, "covered: paused")
	assert_eq(scales, [0.0] as Array[float], "the host's fog and rain pause too")
	layers.set_covered(false)
	layers._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	layers._process(0.25)
	assert_eq(layers.layer_time(L.AVIATION), t, "unfocused: paused")
	layers._notification(Node.NOTIFICATION_APPLICATION_FOCUS_IN)
	layers._process(0.25)
	assert_almost_eq(layers.layer_time(L.AVIATION), t + 0.25, 0.0001, "focused again: running")
	assert_eq(scales.back(), 1.0)
	# The host's ambient scale (CityView3D.ambient_changed) pauses them as well.
	layers.set_host_ambient(0.0)
	layers._process(0.25)
	assert_almost_eq(layers.layer_time(L.AVIATION), t + 0.25, 0.0001, "the host paused: paused")
	layers.set_host_ambient(1.0)
	layers._process(0.25)
	assert_almost_eq(layers.layer_time(L.AVIATION), t + 0.5, 0.0001, "the host live again: running")


func test_the_groups_go_to_the_hosts_layers_and_its_ground_pass() -> void:
	var layers := _layers()
	assert_eq(layers.groups.keys(), CityMotionLayers.GROUPS as Array, "traffic, sky, props and heat groups")
	assert_true(layers._street_mmi.get_parent() == layers.groups[&"traffic"], "street cars in traffic")
	assert_true(layers._car_mmis[0].get_parent() == layers.groups[&"sky"], "sky cars in sky")
	assert_true(layers._billboard_mmi.get_parent() == layers.groups[&"props"], "billboards in props")
	assert_true(layers._search_mmi.get_parent() == layers.groups[&"heat"], "the rig in heat")
	layers.set_ground_pass_layer(CityView3D.GROUND_LAYER)
	assert_true(layers._car_mmis[0].get_layer_mask_value(CityView3D.GROUND_LAYER), "sky cars draw under see-through buildings")
	assert_false(layers._billboard_mmi.get_layer_mask_value(CityView3D.GROUND_LAYER), "billboards do not")
	var nodes: Array[Vector3] = [site.lot_to_world(Vector2(30, 30))]
	layers.set_heat(CityHeatRig.Band.HUNTED, nodes)
	assert_true(layers._ring_mmi.get_layer_mask_value(CityView3D.GROUND_LAYER), "a rebuilt rig keeps the ground pass")


func test_reduce_effects_shows_the_end_state_and_reduce_motion_keeps_it_steady() -> void:
	Settings.reduce_motion = false
	Motion.force_live = true
	Settings.reduce_effects = true
	var layers := _layers()
	var L := CityMotionClock.Layer
	layers._process(0.5)
	for k in CityMotionClock.COUNT:
		assert_eq(layers.layer_time(k), 0.0, "reduce effects: layer %d at its end state" % k)
	var av: ShaderMaterial = layers._aviation_mat
	assert_true(bool(av.get_shader_parameter(&"steady")), "lights on and still")
	Settings.reduce_effects = false
	Settings.reduce_motion = true
	layers._process(0.5)
	assert_almost_eq(layers.layer_time(L.STREET_CARS), 0.5 * cfg.reduce_motion_street_rate, 0.0001,
		"street traffic keeps moving at 40 % (bible 5.4)")
	assert_eq(layers.layer_time(L.CHOPPERS), 0.0, "choppers parked")
	assert_false(layers.sky_cars_visible(), "sky lanes: markers without cars")
	for mi in layers._car_mmis:
		assert_false(mi.visible)
	assert_true(layers._guide_mmi.visible, "the lane markers stay")
	assert_false(bool(layers._street_mat.get_shader_parameter(&"streak_on")), "no streaks")


func test_headless_the_layers_never_move() -> void:
	Motion.force_live = false
	var layers := _layers()
	layers._process(1.0)
	for k in CityMotionClock.COUNT:
		assert_eq(layers.layer_time(k), 0.0, "headless: layer %d holds its end state, nothing waits" % k)


func test_the_car_lod_swaps_at_the_configured_zooms() -> void:
	Settings.reduce_motion = false
	var layers := _layers()
	layers.set_ortho(440.0)
	assert_eq(layers.car_tier, CitySkyTraffic.CarTier.FAR)
	assert_true(layers._car_mmis[CitySkyTraffic.CarTier.FAR].visible)
	assert_false(layers._car_mmis[CitySkyTraffic.CarTier.MEDIUM].visible)
	layers.set_ortho(cfg.car_far_above * (1.0 - cfg.lod_hysteresis * 0.5))
	assert_eq(layers.car_tier, CitySkyTraffic.CarTier.FAR, "inside the hysteresis band: still FAR")
	layers.set_ortho(cfg.car_far_above * (1.0 - cfg.lod_hysteresis * 1.5))
	assert_eq(layers.car_tier, CitySkyTraffic.CarTier.MEDIUM)
	layers.set_ortho(60.0)
	assert_eq(layers.car_tier, CitySkyTraffic.CarTier.CLOSE)
	assert_true(layers._car_mmis[CitySkyTraffic.CarTier.CLOSE].visible)
	layers.set_view(CityMotionLayers.View.NETRUN)
	# ART-7 7w: a netrun close-up shows the CLOSE tier (round 40 cars_lod); the transit's own
	# fit (MEDIUM) shows no sky-lane cars (bible 4.1).
	assert_true(layers.sky_cars_visible(), "a netrun close-up shows the CLOSE car tier")
	assert_true(layers._car_mmis[CitySkyTraffic.CarTier.CLOSE].visible)
	layers.set_ortho(cfg.car_close_below * (1.0 + cfg.lod_hysteresis * 1.5))
	assert_eq(layers.car_tier, CitySkyTraffic.CarTier.MEDIUM)
	assert_false(layers.sky_cars_visible(), "no sky-lane cars in the netrun transit at its fit")
	layers.set_ortho(60.0)
	# The layer carries the seeded traffic (the headless renderer keeps no instance colours).
	var mm := layers._car_mmis[0].multimesh
	assert_eq(mm.instance_count, layers.traffic.cars.size())
	assert_eq(layers.traffic.cars, CitySkyTraffic.build(cfg, layers.lanes, 7, Motion.seconds(CityMotionLayers.SKY_CARS), Motion.seconds(CityMotionLayers.STREET_CARS), site.lot_bu).cars, "same seed, same cars")


func test_day_and_night_crossfade_and_heat_rebuilds_the_rig() -> void:
	Settings.reduce_effects = false
	Motion.force_live = true
	var layers := _layers()
	var shares: Array[float] = []
	layers.night_share_changed.connect(func(s: float) -> void: shares.append(s))
	layers.set_light(CityMotionLayers.Daylight.DAY, false)
	layers._process(Motion.seconds(CityMotionLayers.LIGHT_FADE) * 0.5)
	assert_almost_eq(layers.night_share, 0.5, 0.01, "half way through the crossfade")
	layers._process(Motion.seconds(CityMotionLayers.LIGHT_FADE))
	assert_eq(layers.night_share, 0.0, "day")
	assert_eq(shares.back(), 0.0, "the host hears the day look")
	Motion.force_live = false
	layers.set_light(CityMotionLayers.Daylight.NIGHT, false)
	assert_eq(layers.night_share, 1.0, "no crossfade when it doesn't play: night at once")
	var nodes: Array[Vector3] = [site.lot_to_world(Vector2(30, 30))]
	layers.set_heat(CityHeatRig.Band.PURGE, nodes)
	assert_eq(layers.rig.look, CityHeatRig.Band.HUNTED, "PURGE shows HUNTED's rig")
	assert_eq(layers._choppers.size(), cfg.band_choppers[CityHeatRig.Band.HUNTED])
	assert_eq(int(layers.spill_uniforms()["spill_count"]), mini(LightSpill.MAX_3D, layers.props.billboards.size() + layers.rig.searchlights.size()),
		"the nearest billboards and searchlights spill on the toon materials")


func test_the_close_car_chopper_drone_and_billboards_are_the_art_pass_assets() -> void:
	# M14 asset parity: models exported from the concept round's own builders (Blender), the panels from cm.py.
	var car := CityMotionMeshes.car(cfg, CitySkyTraffic.CarTier.CLOSE)
	assert_eq(car.get_surface_count(), 1)
	assert_true(car.get_aabb().size.x >= cfg.close_length - 0.01, "the car runs close_length from tail to nose (plus its line)")
	assert_gt((CityMotionMeshes.CAR_TRIS.data as Dictionary)["tris"].size(), 20, "the exported flying car's triangles")
	var parts := {}
	for t: Array in (CityMotionMeshes.CAR_TRIS.data as Dictionary)["tris"]:
		parts[int(t[0][3])] = true
	for p in CityMotionMeshes.Part.values():
		assert_true(parts.has(p), "part %d is in the exported car" % p)
	var heli := CityMotionMeshes.chopper(cfg.chopper_length)
	assert_almost_eq((heli["body"] as Mesh).get_aabb().size.x * float(heli["scale"]), cfg.chopper_length, 0.01, "fitted to chopper_length")
	assert_not_null(heli["neon"], "the concept's lit parts")
	assert_gt(float(heli["rotor_r"]), 0.0, "the blur disc takes the model's blade radius")
	var drone := CityMotionMeshes.drone(cfg.drone_size)
	assert_almost_eq((drone["body"] as Mesh).get_aabb().size.x * float(drone["scale"]), cfg.drone_size, 0.01)
	var tex := load("res://assets/city/billboards/panels.png") as Texture2D
	assert_eq(tex.get_width() % cfg.billboard_panels, 0, "an atlas of billboard_panels cells")
	assert_eq(CityMotionLayers.BILLBOARD_PANELS, tex)


func _road(name: String) -> Dictionary:
	for rd in lanes.roads:
		if rd["name"] == name:
			return rd
	return {}
