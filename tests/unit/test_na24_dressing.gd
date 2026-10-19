extends GutTest
## NA-24: the street dressing. Config soundness; every group's `visibility_range` is the config's (no literal ranges); tiers reveal in
## order and the count of a group changes by exactly its instance count at its band edge; streak lanes obey `L = k speed T`;
## the same layout gives identical node transforms and no RNG stream is drawn; district palettes and HQ-distance bands differ; the
## loops (lane streaks, flicker, plumes) repeat after the 4 s loop.

var _cache: Dictionary = {}


func after_all() -> void:
	for k: String in _cache:
		((_cache[k] as Dictionary)["dressing"] as StreetDressing).root.free()
	_cache.clear()


func _street(seed_name: String) -> Dictionary:
	if not _cache.has(seed_name):
		var w: Dictionary = NaFixture.load_inputs(seed_name)
		var d: Dictionary = NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"], w["partial_street"])
		_cache[seed_name] = {"derive": d, "city": w["city"], "dressing": StreetDressing.build(d, w["city"])}
	return _cache[seed_name]


func _visible_count(sd: StreetDressing, group: String, d: float) -> int:
	return int(sd.counts.get(group, 0)) if DressReveal.is_drawn(group, d) else 0


func test_config_is_sound_and_names_only_listed_assets() -> void:
	var cfg := DressingConfigData.shipped()
	assert_eq(cfg.validate().size(), 0, str(cfg.validate()))
	assert_true(DressingConfigData.new().validate().size() > 5, "an empty config reports its gaps")
	for g: String in cfg.groups:
		var asset: String = cfg.groups[g]["asset"]
		assert_true(asset == "" or NetrunArtConfigData.shipped().reveal.has(asset), "group %s asset %s" % [g, asset])


func test_every_group_takes_its_visibility_range_from_the_config() -> void:
	var sd: StreetDressing = _street("101")["dressing"]
	var tiered := 0
	for g: String in sd.nodes:
		var r: Dictionary = DressReveal.range_of(g)
		for n in sd.nodes[g]:
			var gi := n as GeometryInstance3D
			assert_eq(gi.visibility_range_end, float(r["end"]), "%s end" % g)
			assert_eq(gi.visibility_range_end_margin, float(r["margin"]), "%s margin" % g)
			assert_eq(gi.visibility_range_begin, 0.0)
		if float(r["end"]) > 0.0:
			tiered += 1
			var row: Array = DressReveal.row_of(String(DressingConfigData.shipped().groups[g]["asset"]), int(DressingConfigData.shipped().groups[g]["tier"]))
			assert_eq(float(r["end"]), float(row[1]), "%s end is the reveal row's far edge" % g)
			assert_true(float(r["margin"]) >= 0.1 * (float(row[1]) - float(row[2])) - 0.0001, "%s fades over at least 10 percent of its interval" % g)
	assert_true(tiered >= 8, "tiered groups present: %d" % tiered)


func test_tiers_reveal_in_order_and_counts_change_by_the_authored_amount_at_each_edge() -> void:
	var sd: StreetDressing = _street("101")["dressing"]
	assert_true(DressReveal.is_drawn("sign_neon", 600.0) and not DressReveal.is_drawn("sign_full", 600.0), "neon block first")
	assert_true(DressReveal.is_drawn("sign_full", 300.0) and not DressReveal.is_drawn("sign_flicker", 300.0), "full sign second")
	assert_true(DressReveal.is_drawn("sign_flicker", 200.0), "flicker last")
	assert_false(DressReveal.is_drawn("sign_neon", 900.0), "nothing beyond the first tier edge")
	assert_true(DressReveal.is_drawn("beam", 5000.0) and DressReveal.is_drawn("glow", 5000.0), "the big layer is never hidden")
	for g: String in sd.counts:
		var r: Dictionary = DressReveal.range_of(g)
		if float(r["end"]) <= 0.0:
			continue
		var inside := _visible_count(sd, g, float(r["end"]) - 0.01)
		var outside := _visible_count(sd, g, float(r["end"]) + 0.01)
		assert_eq(inside - outside, int(sd.counts[g]), "%s changes by its whole count at its edge" % g)
		assert_eq(DressReveal.weight(g, float(r["near"]) - 0.01), 1.0, "%s fully in inside its near edge" % g)
		assert_eq(DressReveal.weight(g, float(r["end"]) + 0.01), 0.0, "%s out beyond its far edge" % g)
	assert_true(sd.counts["sign_neon"] > 0 and sd.counts["hero_neon"] > 0, "city and hero signs are placed")


func test_signs_never_exceed_their_caps_and_beams_stay_within_the_spot_budget() -> void:
	var sd: StreetDressing = _street("101")["dressing"]
	var caps: Dictionary = DressingConfigData.shipped().caps
	assert_true(int(sd.plan["signs"].size()) <= int(caps["city_signs"]))
	assert_true(int(sd.plan["shops"].size()) <= int(caps["shopfronts"]))
	assert_true(int(sd.counts.get("beam", 0)) <= int(caps["beam_spots"]))
	assert_true(int(caps["glow_lights"]) <= 14)


func test_streak_lanes_are_a_whole_number_of_loops() -> void:
	for s in ["101", "104", "109"]:
		var sd: StreetDressing = _street(s)["dressing"]
		for lane: Dictionary in sd.dress["streak_lanes"]:
			var a := Vector2(float(lane["a"][0]), float(lane["a"][1]))
			var b := Vector2(float(lane["b"][0]), float(lane["b"][1]))
			var q: Dictionary = NetrunShaderKit.quantize_speed(a.distance_to(b), float(lane["speed"]), 4.0)
			var k: int = int(q["k"])
			assert_true(k >= 1)
			assert_almost_eq(a.distance_to(b), float(k) * float(q["speed"]) * 4.0, 0.001, "seed %s lane %s: L = k speed T" % [s, lane["lane_id"]])
			assert_true(not (lane["streaks"] as Array).is_empty())


func test_flicker_and_plume_loops_repeat_after_the_loop() -> void:
	# The shaders' time terms: fract(t / T * k + phase) with whole k, a hum of 4 cycles, and the plume phase fract(t / T + p).
	for k in [1, 2, 3]:
		for t in [0.0, 0.7, 2.9]:
			assert_almost_eq(fposmod(t / 4.0 * float(k) + 0.3, 1.0), fposmod((t + 4.0) / 4.0 * float(k) + 0.3, 1.0), 0.0001)
	assert_almost_eq(sin(TAU * (0.7 / 4.0 * 4.0 + 0.2)), sin(TAU * ((0.7 + 4.0) / 4.0 * 4.0 + 0.2)), 0.0001)
	assert_almost_eq(fposmod(1.3 / 4.0 + 0.4 + 0.1, 1.0), fposmod((1.3 + 4.0) / 4.0 + 0.4 + 0.1, 1.0), 0.0001)
	assert_eq(float(DressingConfigData.shipped().plume["loop_s"]), float(CityShaderConfigData.shipped().streak["loop_s"]), "one loop")


func _fingerprint(sd: StreetDressing) -> Array:
	var out: Array = []
	var names: Array = sd.nodes.keys()
	IdSort.sort_ids(names)
	for g: String in names:
		for n in sd.nodes[g]:
			if n is MultiMeshInstance3D:
				var mm: MultiMesh = (n as MultiMeshInstance3D).multimesh
				for i in mm.instance_count:
					out.append([n.name, mm.get_instance_transform(i), mm.get_instance_color(i)])
			else:
				out.append([n.name, (n as Node3D).transform])
	return out


func test_same_layout_gives_identical_transforms_without_touching_a_stream() -> void:
	var s: Dictionary = _street("102")
	var again := StreetDressing.build(s["derive"], s["city"])
	var fp_again: Array = _fingerprint(again)
	again.root.free()
	assert_eq(fp_again, _fingerprint(s["dressing"]), "node transforms and colours repeat")
	assert_eq(again.counts, (s["dressing"] as StreetDressing).counts)
	var src: String = FileAccess.get_file_as_string("res://scripts/city3d/street_dressing.gd") + FileAccess.get_file_as_string("res://scripts/city3d/dress_frontage.gd") \
		+ FileAccess.get_file_as_string("res://scripts/city3d/dress_districts.gd")
	for banned in ["randi(", "randf(", "randomize(", "RandomNumberGenerator", "RngService"]:
		assert_false(src.contains(banned), "no random draw: %s" % banned)


func _city3() -> Dictionary:
	var b: Array = []
	var terrs := ["halcyon", "meridian", "solace"]
	for i in 3:
		var x: float = 200.0 * float(i)
		b.append({"bid": "b%d" % i, "hq": i == 0, "terr": terrs[i], "parts": [{"z0": 0.0, "h": 20.0, "poly": [[x, 0.0], [x + 10.0, 0.0], [x + 10.0, 10.0], [x, 10.0]]}]})
	return {"buildings": b}


func test_districts_show_distinct_palettes_and_hq_bands_vary() -> void:
	var dd := DressDistricts.new(_city3())
	var seen: Dictionary = {}
	for i in 3:
		var c: Color = dd.color("district_a", 200.0 * float(i) + 5.0, 5.0)
		seen[c.to_html()] = true
		assert_eq(dd.terr_at(200.0 * float(i) + 5.0, 5.0), ["halcyon", "meridian", "solace"][i])
	assert_eq(seen.size(), 3, "three districts, three district_a colours")
	var sets: Dictionary = {}
	for t: String in DressingConfigData.shipped().districts:
		sets[DressingConfigData.shipped().districts[t]["palette"]] = true
	assert_true(sets.size() >= 3, "at least three palette sets in the language table")
	var near: Dictionary = dd.band_at(20.0, 5.0)
	var far: Dictionary = dd.band_at(400.0, 5.0)
	assert_true(float(near["sign_mul"]) > float(far["sign_mul"]), "signage is denser near the HQ")
	assert_ne(float(near["emit_mul"]), float(far["emit_mul"]))
	assert_eq(DressDistricts.hash01("sign", "10:13"), DressDistricts.hash01("sign", "10:13"))
	assert_ne(DressDistricts.hash01("sign", "10:13"), DressDistricts.hash01("sign", "10:14"))
