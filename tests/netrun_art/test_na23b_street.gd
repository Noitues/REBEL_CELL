extends GutTest
## NA-23b: the street span rule and the street capacity ladder, GDScript twin against the Python oracle.
## g1 = Meridian, campaign seed 1, game city, Site m1_a; g2 = Solace t1_i (the routed link starts off the street axis, so the
## raw leg finds no frontage and the squared-legs step rescues it); g3 = Meridian on city seed 1. The inputs are the exact
## doubles of the Python run (`tools/netrun_art/tests/gen_game_fixtures.py`), trimmed around the Site's link.

const GAME_WORLDS: Array[String] = ["g1", "g2", "g3"]


func _street(name: String) -> Dictionary:
	var w := NaFixture.load_inputs(name)
	return NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"])


func test_game_world_street_derive_is_byte_identical_to_python() -> void:
	for name in GAME_WORLDS:
		var d := _street(name)
		assert_false(d.has("error"), "%s street derive: %s" % [name, d.get("error", "")])
		var diff := NaFixture.first_diff(NetrunArtDeriver.derive_text(d), NaFixture.expected_text(name, "street_derive"))
		assert_eq(diff, "", "%s street derive: %s" % [name, diff])


func test_meridian_seed_1_derives_on_the_first_step() -> void:
	for name in ["g1", "g3"]:
		var w := NaFixture.load_inputs(name)
		assert_eq(w["corp"], "meridian")
		var layers := NetrunStreetDeriver.layer_nodes(w["run_graph"])
		var sl := NetrunStreetDeriver.select_link(w["net"], w["site"])
		var legs := NetrunArtLayout.link_legs(w["city"], sl["pts"])
		var res := NetrunStreetDeriver.choose_street_fitting(NetrunArtLayout.merged_buildings(w["city"]), legs, layers)
		assert_eq(res[1], 0, "%s needs no ladder step" % name)


func test_a_slanted_leg_is_squared_and_found() -> void:
	var w := NaFixture.load_inputs("g2")
	var layers := NetrunStreetDeriver.layer_nodes(w["run_graph"])
	var sl := NetrunStreetDeriver.select_link(w["net"], w["site"])
	var legs := NetrunArtLayout.link_legs(w["city"], sl["pts"])
	var B := NetrunArtLayout.merged_buildings(w["city"])
	var raw := NetrunStreetDeriver.choose_street(B, legs, layers)
	assert_true(raw.is_empty() or (raw["front"] as Array).is_empty() or not bool(raw["ok"]), "the raw leg finds no street")
	assert_eq(NetrunStreetDeriver.choose_street_fitting(B, legs, layers)[1], 1)
	assert_eq(NetrunStreetDeriver.square_legs([[0.0, 0.0], [10.0, 2.0], [10.0, 9.0]]),
		[[0.0, 0.0], [10.0, 0.0], [10.0, 2.0], [10.0, 9.0]])


func test_span_scan_and_choice_match_python_on_a_fixture() -> void:
	# seed 105 (python test_na23b_street): span 2 reaches the target and layers 1 and 3 fall back to span 1 there
	var w := NaFixture.load_inputs("105")
	var layers := NetrunStreetDeriver.layer_nodes(w["run_graph"])
	var sl := NetrunStreetDeriver.select_link(w["net"], w["site"])
	var legs := NetrunArtLayout.link_legs(w["city"], sl["pts"])
	var best := NetrunStreetDeriver.choose_street(NetrunArtLayout.merged_buildings(w["city"]), legs, layers)
	var rules := NetrunStreetDeriver.rules()
	var rows := NetrunStreetDeriver.span_scan(best["asg"], layers, best["front"][0]["nrm"], best["start_left"], rules)
	assert_eq(rows.size(), int(rules["span_max"]))
	assert_eq(rows[1]["fallback"], [1, 3], "span 2: layers 1 and 3 sit in buildings without the floors")
	assert_eq(rows[0]["fallback"], [])
	assert_true(float(rows[1]["min_px"]) >= float(rules["room_px_target"]))
	assert_eq(NetrunStreetDeriver.choose_span(best["asg"], layers, best["front"][0]["nrm"], best["start_left"], rules), 2)


func _sparse_world(xs: Array) -> Array:
	var b: Array = []
	for i in xs.size():
		b.append({"bid": "b%02d" % i, "x0": float(xs[i]), "x1": float(xs[i]) + 5.0, "y0": 2.0, "y1": 9.0, "h": 40.0, "ts": 1.0, "axis": 0})
	var nodes: Array = []
	for l in range(1, 8):
		nodes.append({"id": "n%d" % l, "index": 0, "layer": l})
	return [b, NetrunStreetDeriver.layer_nodes({"nodes": nodes})]


func test_a_sparse_street_retries_with_a_longer_extension_like_python() -> void:
	# python test_w1_street_retry: 3 buildings inside the 12 / 60 BU extension, 4 more past it
	var legs: Array = [[0.0, 0.0], [10.0, 0.0]]
	var fit := _sparse_world([0, 8, 16, 24, 32, 40, 48])
	assert_eq(NetrunStreetDeriver.choose_street_fitting(fit[0], legs, fit[1])[1], 0, "a street that fits is never changed")
	var sparse := _sparse_world([0, 8, 16, 90, 98, 106, 114])
	var res := NetrunStreetDeriver.choose_street_fitting(sparse[0], legs, sparse[1])
	assert_true(int(res[1]) >= 2 and bool((res[0] as Dictionary)["ok"]), "the retry fits every layer")
	var few := _sparse_world([0, 8])
	var none := NetrunStreetDeriver.choose_street_fitting(few[0], legs, few[1])
	assert_eq(none[1], 0)
	assert_false(bool((none[0] as Dictionary)["ok"]))
