extends GutTest
## NA-21: the GDScript twins against the Python oracle (PIPELINE_SPEC 12.6, 12.8). For the 12 fixture seeds (101-112), street
## and HQ: the derive v2 text, the poses v1 text (camera poses, framing, dive, occlusion, LOD, section) and the dress reader
## round trip are byte-identical to `tools/netrun_art/tests/fixtures/`. A failure prints the first differing path. Inputs are
## the exact doubles of the Python run (hex floats), so a mismatch is a port bug, not a rounding artefact.

var _cache: Dictionary = {}


func _inputs(seed_name: String) -> Dictionary:
	if not _cache.has(seed_name):
		_cache[seed_name] = NaFixture.load_inputs(seed_name)
	return _cache[seed_name]


func _street(seed_name: String) -> Dictionary:
	var w := _inputs(seed_name)
	return NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"], w["partial_street"])


func _hq(seed_name: String) -> Dictionary:
	var w := _inputs(seed_name)
	return NetrunArtDeriver.derive_hq(w["city"], w["run_graph"], w["corp"], w["partial_hq"])


func test_fixture_decoder_rebuilds_exact_doubles() -> void:
	assert_eq(NaFixture.hex_float("~0x1.8p+3"), 12.0)
	assert_eq(NaFixture.hex_float("~-0x1p-3"), -0.125)
	assert_eq(NaFixture.hex_float("~0x0p+0"), 0.0)
	assert_eq(NaFixture.hex_float("~0x1.999999999999ap-4"), 0.1, "the double nearest 0.1")
	assert_eq(NaFixture.SEEDS.size(), 12)


func test_street_derive_is_byte_identical_to_python() -> void:
	for s in NaFixture.SEEDS:
		var d := _street(s)
		assert_false(d.has("error"), "seed %s street derive: %s" % [s, d.get("error", "")])
		var diff := NaFixture.first_diff(NetrunArtDeriver.derive_text(d), NaFixture.expected_text(s, "street_derive"))
		assert_eq(diff, "", "seed %s street derive: %s" % [s, diff])


func test_hq_derive_is_byte_identical_to_python() -> void:
	for s in NaFixture.SEEDS:
		var d := _hq(s)
		assert_false(d.has("error"), "seed %s hq derive: %s" % [s, d.get("error", "")])
		var diff := NaFixture.first_diff(NetrunArtDeriver.derive_text(d), NaFixture.expected_text(s, "hq_derive"))
		assert_eq(diff, "", "seed %s hq derive: %s" % [s, diff])


func test_street_poses_match_python() -> void:
	for s in NaFixture.SEEDS:
		var w := _inputs(s)
		var p := NetrunArtDeriver.poses(_street(s), w["city"], w["run_graph"], w["net"])
		var diff := NaFixture.first_diff(NetrunArtExport.canonical(p), NaFixture.expected_text(s, "street_poses"))
		assert_eq(diff, "", "seed %s street poses: %s" % [s, diff])


func test_hq_poses_match_python() -> void:
	for s in NaFixture.SEEDS:
		var w := _inputs(s)
		var p := NetrunArtDeriver.poses(_hq(s), w["city"], w["run_graph"])
		var diff := NaFixture.first_diff(NetrunArtExport.canonical(p), NaFixture.expected_text(s, "hq_poses"))
		assert_eq(diff, "", "seed %s hq poses: %s" % [s, diff])


func test_occlusion_runs_on_every_view_and_matches() -> void:
	# The poses files carry the occlusion block of OVERVIEW, DECISION and every fixture pose; it must be present and
	# non-trivial for street and HQ alike (ruling 2026-10-18: OcclusionHelper runs on every netrun view).
	var listed := 0
	for s in NaFixture.SEEDS:
		var w := _inputs(s)
		for kind in ["street", "hq"]:
			var d := _street(s) if kind == "street" else _hq(s)
			var p := NetrunArtDeriver.poses(d, w["city"], w["run_graph"], w["net"] if kind == "street" else {})
			var views: Array = [p["overview"], p["decision"]]
			for f: Dictionary in p["fixtures"]:
				views.append(f["decision"])
			for v: Dictionary in views:
				var occ: Dictionary = v["occlusion"]
				assert_true(occ["params"].has("occ_on") and occ["params"]["occ_on"], "%s %s occ_on" % [s, kind])
				assert_eq(occ["params"].size(), 28, "28 occ_* keys")
				listed += (occ["buildings"] as Array).size()
	assert_gt(listed, 0, "some building is cut or ghosted in the fixtures")


func test_deriving_twice_gives_identical_bytes() -> void:
	for s in ["101", "107", "112"]:
		assert_eq(NetrunArtDeriver.derive_text(_street(s)), NetrunArtDeriver.derive_text(_street(s)), "street %s" % s)
		assert_eq(NetrunArtDeriver.derive_text(_hq(s)), NetrunArtDeriver.derive_text(_hq(s)), "hq %s" % s)


func test_text_hash_matches_the_python_hashes_file() -> void:
	var hashes: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(NaFixture.DIR + "hashes.json"))["hashes"]
	for s in NaFixture.SEEDS:
		assert_eq(NetrunArtDeriver.derive_text(_street(s)).sha256_text(), hashes[s]["derive_street"], "seed %s derive_street sha256" % s)
		assert_eq(NetrunArtDeriver.derive_text(_hq(s)).sha256_text(), hashes[s]["derive_hq"], "seed %s derive_hq sha256" % s)


func test_rig_timings_come_from_config() -> void:
	var rig := NetrunCameraRig.street_rig_json()
	assert_eq(rig["t_zoom"], 1.0, "Z is 1.0 s")
	assert_eq(rig["t_step"], 0.9, "a step is 0.9 s")
	assert_eq(rig["look_bias_sign"], 1.0, "look-bias sign is +1 (art-pass confirmed)")
	assert_eq(rig["t_zoom"], NetrunArtConfigData.shipped().rig["t_zoom"])
	assert_eq(NetrunCameraRig.dive_constants()["duration_s"], 3.0)


func test_yaw_zero_is_north_and_turns_clockwise() -> void:
	var p := NetrunPose.make([0.0, 0.0, 0.0], 0.0, 0.0, 10.0, 30.0)
	assert_almost_eq(p.dir()[1], 1.0, 1e-12, "yaw 0 looks along +y")
	var q := NetrunPose.make([0.0, 0.0, 0.0], 90.0, 0.0, 10.0, 30.0)
	assert_almost_eq(q.dir()[0], 1.0, 1e-12, "yaw 90 looks east (clockwise from above)")


func test_reveal_tiers_cross_fade_with_distance() -> void:
	assert_eq(RevealTiers.visible_tier("street_sign", 2000.0), 0, "hidden at city zoom")
	assert_eq(RevealTiers.visible_tier("street_sign", 600.0), 1, "neon shape")
	assert_eq(RevealTiers.visible_tier("street_sign", 300.0), 2, "full sign")
	assert_eq(RevealTiers.visible_tier("street_sign", 100.0), 3, "flicker")
	assert_eq(RevealTiers.tier_weight("street_sign", 1, 790.0), 0.0)
	assert_eq(RevealTiers.tier_weight("street_sign", 1, 466.0), 1.0)
	var mid := RevealTiers.tier_weight("street_sign", 1, 600.0)
	assert_true(mid > 0.0 and mid < 1.0, "tier 1 fades between its edges")
	assert_eq(RevealTiers.tier_weight("unknown_asset", 1, 50.0), 1.0, "an unlisted asset is always drawn")


func test_dress_reader_round_trips_every_fixture() -> void:
	for s in NaFixture.SEEDS:
		var text := NaFixture.expected_text(s, "street_dress")
		var d := DressReader.read_text(text)
		assert_false(d.has("error"), "seed %s dress: %s" % [s, d.get("error", "")])
		var diff := NaFixture.first_diff(NetrunArtExport.canonical(d), text)
		assert_eq(diff, "", "seed %s dress round trip: %s" % [s, diff])
		assert_gt((d["lamps"] as Array).size(), 0)
		assert_true(d["signs"][0]["layer"] is int, "integer fields are ints")


func test_dress_reader_rejects_unknown_version_kind_and_palette() -> void:
	var text := NaFixture.expected_text("101", "street_dress")
	var d: Dictionary = JSON.parse_string(text)
	d["version"] = 2.0
	assert_true(String(DressReader.read_text(JSON.stringify(d))["error"]).begins_with("dress.version"), "unknown dress version")
	d["version"] = 1.0
	d["kind"] = "hq"
	assert_true(String(DressReader.read_text(JSON.stringify(d))["error"]).begins_with("dress.kind"), "unknown dress kind")
	d["kind"] = "street"
	d["lamps"][0]["pal"] = "neon_pink"
	assert_true(String(DressReader.read_text(JSON.stringify(d))["error"]).begins_with("dress.palette"), "unknown palette id")
	assert_true(String(DressReader.read_text("[1, 2]")["error"]).begins_with("dress.type"), "not an object")


func test_derive_gate_accepts_new_room_kinds_and_rejects_unknown() -> void:
	var d := _street("101")
	assert_eq(DressReader.check_derive(d), "", "the twin's own derive passes")
	for kind in ["router", "terminal", "mainframe", "server_rack", "rest", "workshop", "cache"]:
		assert_true(DressReader.is_room_kind(kind), kind)
	var first: String = (d["rooms"] as Dictionary).keys()[0]
	for ok_kind in ["rest", "workshop", "cache"]:
		d["rooms"][first]["kind"] = ok_kind
		assert_eq(DressReader.check_derive(d), "", "%s is accepted" % ok_kind)
	d["rooms"][first]["kind"] = "casino"
	assert_true(DressReader.check_derive(d).begins_with("derive.room_kind"), "unknown room kind")
	d["rooms"][first]["kind"] = "router"
	d["version"] = 3
	assert_true(DressReader.check_derive(d).begins_with("derive.version"), "unknown derive version")
