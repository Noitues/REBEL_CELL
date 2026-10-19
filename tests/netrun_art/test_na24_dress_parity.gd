extends GutTest
## NA-24: `NetrunArtDress` against the Python oracle (`tools/netrun_art/dress.py`). For the 12 fixture seeds the dress v1 text
## (signs, lamps, washes, glows, beams, streak lanes, fog fields) is byte-identical to `<seed>_street_dress.json`.


func test_street_dress_is_byte_identical_to_python() -> void:
	for s in NaFixture.SEEDS:
		var w: Dictionary = NaFixture.load_inputs(s)
		var d: Dictionary = NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"], w["partial_street"])
		assert_false(d.has("error"), "seed %s derive: %s" % [s, d.get("error", "")])
		var dress: Dictionary = NetrunArtDress.dress_street(d, w["city"])
		var diff: String = NaFixture.first_diff(NetrunArtExport.canonical(dress), NaFixture.expected_text(s, "street_dress"))
		assert_eq(diff, "", "seed %s dress: %s" % [s, diff])


func test_dress_round_trips_through_the_reader() -> void:
	var w: Dictionary = NaFixture.load_inputs("101")
	var d: Dictionary = NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"], w["partial_street"])
	var dress: Dictionary = NetrunArtDress.dress_street(d, w["city"])
	var back: Dictionary = DressReader.read_text(NetrunArtExport.canonical(dress))
	assert_false(back.has("error"), String(back.get("error", "")))
	assert_eq(back["signs"].size(), dress["signs"].size())
