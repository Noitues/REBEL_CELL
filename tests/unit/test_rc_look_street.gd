extends GutTest
## LOOK-TOOLBOX module 10 (fast tier): street layers. RcLookRamp equals the ramps the street code repeats (RevealTiers band /
## tier weight / zoom converters, NetrunSection.zcut's log interpolation); RcLookStreet reads the street's look numbers from
## their configs, and the r2 plan's copy of the sign emission tiers equals the emission hierarchy; RouteRig's room window
## count fits city_building's room arrays.


func test_log_ramp_is_reveal_tiers() -> void:
	for d: float in [0.0, 5.0, 40.0, 152.0, 216.0, 466.0, 790.0, 3000.0]:
		assert_eq(RcLookRamp.log01(d, 790.0, 152.0), RevealTiers.zoom_detail(d, 790.0, 152.0), "log01 at %s" % d)
		assert_eq(RcLookRamp.log01(d, 3000.0, 114.6), RevealTiers.zoom_dive(d, 3000.0, 114.6), "zoom_dive at %s" % d)
		var t := RcLookRamp.log01(d, 466.0, 216.0)
		assert_eq(RcLookRamp.log_smooth(d, 466.0, 216.0), NetrunArtUnits.smoothstep01(t), "log_smooth at %s" % d)
	var rv: Dictionary = NetrunArtConfigData.shipped().reveal
	var assets: Array = rv.keys()
	assets.sort()
	for asset: String in assets:
		for row: Array in rv[asset]:
			for d: float in [10.0, 150.0, 400.0, 1200.0]:
				assert_eq(RcLookRamp.log_smooth(d, float(row[1]), float(row[2])), RevealTiers.tier_weight(asset, int(row[0]), d),
						"%s tier %s at %s" % [asset, row[0], d])


func test_log_lerp_ends_and_middle() -> void:
	assert_almost_eq(RcLookRamp.log_lerp(0.4, 40.0, 0.0), 0.4, 1e-6)
	assert_almost_eq(RcLookRamp.log_lerp(0.4, 40.0, 1.0), 40.0, 1e-4)
	assert_almost_eq(RcLookRamp.log_lerp(0.4, 40.0, 0.5), 4.0, 1e-5, "the geometric mean halfway")


func test_street_numbers_come_from_their_configs() -> void:
	var cfg := StreetRouteConfigData.shipped()
	assert_eq(RcLookStreet.lane()["gain"], float(cfg.look["lane"]["gain"]))
	assert_eq(RcLookStreet.room_energy(), Vector2(float(cfg.rooms["energy_idle"]), float(cfg.rooms["energy_lit"])))
	assert_almost_eq(RcLookStreet.hover_cut().x, float(cfg.hover["cut_level"]), 1e-6, "Vector3 holds 32-bit floats")
	assert_eq(RcLookStreet.look_at("exposure", 0.0), float(cfg.look["exposure"][0]))
	assert_eq(RcLookStreet.look_at("frame", 1.0), float(cfg.look["frame"][1]))
	assert_eq(RcLookStreet.fog_density(), float(cfg.atmosphere["density"]))


func test_r2_sign_tiers_equal_the_emission_hierarchy() -> void:
	var pairs := RcLookStreet.emit_pairs()
	assert_eq(pairs.size(), RcLookStreet.EMIT_PAIRS.size(), "every pair listed")
	for p: Array in pairs:
		assert_eq(p[1], p[2], "street_r2 %s equals city_shaders aaa.emit (the r2 plan keeps its own copy as the Python twin)" % p[0])


func test_route_rooms_fit_city_buildings_arrays() -> void:
	var code := FileAccess.get_file_as_string("res://shaders/city/city_building.gdshader")
	assert_string_contains(code, "uniform vec4 room_box[%d];" % RouteRig.ROOM_MAX, "RouteRig.ROOM_MAX = city_building's room arrays")


## Slab fix (designer 2026-10-22): wet_street's structure lift is off by default (every other view keeps the wet ground) and its
## numbers equal the street view's look.ground; the street camera hides the A2 features (a view flag, not a layout rule).
func test_the_street_lifts_structure_and_hides_the_a2_deck() -> void:
	var lk: Dictionary = StreetRouteConfigData.shipped().look
	var gd: Dictionary = lk["ground"]
	assert_eq(float(gd["struct_k"]), 1.0, "on in the street view")
	assert_true(bool(lk["hide_a2_features"]), "the street camera hides the A2 decks and pillars")
	var code := FileAccess.get_file_as_string("res://shaders/city/wet_street.gdshader")
	var re := RegEx.create_from_string("uniform (float|vec3) (struct_\\w+) = (vec3\\(([^)]*)\\)|[-0-9.]+);")
	var seen := {}
	for m: RegExMatch in re.search_all(code):
		var key := m.get_string(2)
		seen[key] = true
		if key == "struct_k":
			assert_eq(float(m.get_string(3)), 0.0, "off unless a view sets it")
			continue
		assert_true(gd.has(key), "%s in look.ground" % key)
		if m.get_string(1) == "vec3":
			var parts := m.get_string(4).split(",")
			for i in 3:
				assert_almost_eq(float(parts[i]), float((gd[key] as Array)[i]), 1e-6, "%s[%d]" % [key, i])
		else:
			assert_almost_eq(float(m.get_string(3)), float(gd[key]), 1e-6, key)
	assert_eq(seen.size(), gd.size(), "every look.ground key is a wet_street uniform")
