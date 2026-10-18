extends GutTest
## NA-02 (spec §12.3.1), full tier: building ids are unique across 1,000 city seeds (0
## collisions); a FULL-city city.json validates against its schema at 3 seeds (signed seed
## included); and the exporter CLI run twice in fresh processes writes byte-identical files.

const SchemaCheck := preload("res://tools/netrun_art/schema_check.gd")
const CITY_CONFIG := "res://content/config/city_config.tres"
## The sweep's probe: one chunk-sized box round the district centre per seed (a full-city build
## is ~1 s, so the 1,000 seeds read this box; the full city is checked at FULL_SEEDS).
const SWEEP_SEEDS := 1000
const SWEEP_HALF := 12
const FULL_SEEDS: Array[int] = [7, -1, 424242]

var _cfg: CityConfig


func before_all() -> void:
	_cfg = load(CITY_CONFIG)


func test_building_ids_unique_across_1000_seeds() -> void:
	var c := Vector2i(_cfg.district_centre)
	var box := Rect2i(c - Vector2i(SWEEP_HALF, SWEEP_HALF), Vector2i(2 * SWEEP_HALF, 2 * SWEEP_HALF))
	var collisions := 0
	var buildings := 0
	for s in SWEEP_SEEDS:
		var m := CityModel.build(_cfg, s * 7919 - 500000, box)
		var conflicts := NetrunArtExport.bid_conflicts(m.prisms)
		collisions += conflicts.size()
		if not conflicts.is_empty():
			gut.p("seed %d: %s" % [s * 7919 - 500000, str(conflicts)])
		var city := NetrunArtExport.city_json(m.city_seed, _cfg.lot_bu, _cfg.district_centre, m.prisms, m.streets,
			m.plazas, m.hqs)
		var seen := {}
		for b: Dictionary in city["buildings"]:
			if seen.has(b["bid"]):
				collisions += 1
			seen[b["bid"]] = true
		buildings += seen.size()
	gut.p("NA-02 sweep: %d seeds, %d buildings, %d collisions" % [SWEEP_SEEDS, buildings, collisions])
	assert_eq(collisions, 0)
	assert_true(buildings > SWEEP_SEEDS, "the box holds buildings")


func test_full_city_validates_and_ids_are_unique() -> void:
	var sch := SchemaCheck.schema("city")
	for s in FULL_SEEDS:
		var m := CityModel.build(_cfg, s)
		assert_eq(NetrunArtExport.bid_conflicts(m.prisms), PackedStringArray(), "seed %d" % s)
		var city := NetrunArtExport.city_json(m.city_seed, _cfg.lot_bu, _cfg.district_centre, m.prisms, m.streets,
			m.plazas, m.hqs)
		assert_eq(city["layout_seed"], ArtSeed.u64_str(s))
		var doc: Dictionary = JSON.parse_string(NetrunArtExport.canonical(city))
		assert_eq(SchemaCheck.validate(doc, sch), PackedStringArray(), "full city.json, seed %d" % s)
		assert_eq(doc["hqs"].size(), (city["hqs"] as Dictionary).size())


func test_fresh_processes_write_identical_bytes() -> void:
	var root := OS.get_environment("TEMP").path_join("na02_fresh_%d" % OS.get_process_id())
	var texts := []
	for k in 2:
		var dir := root.path_join(str(k))
		var out := []
		var code := OS.execute(OS.get_executable_path(), ["--headless", "--audio-driver", "Dummy", "--path",
			ProjectSettings.globalize_path("res://"), "-s", "tools/netrun_art/export_contract.gd", "--", "--out=" + dir], out, true)
		assert_eq(code, 0, "export_contract exits 0 (run %d): %s" % [k, str(out).right(400)])
		var files := {}
		for name in DirAccess.get_files_at(dir):
			files[name] = FileAccess.get_file_as_bytes(dir.path_join(name))
			DirAccess.remove_absolute(dir.path_join(name))
		DirAccess.remove_absolute(dir)
		texts.append(files)
	DirAccess.remove_absolute(root)
	assert_eq(texts[0].size(), 5, "five files: %s" % str(texts[0].keys()))
	assert_eq(texts[1].keys(), texts[0].keys())
	for name: String in texts[0]:
		assert_true(texts[1].get(name, PackedByteArray()) == texts[0][name], "%s byte-identical across processes" % name)
