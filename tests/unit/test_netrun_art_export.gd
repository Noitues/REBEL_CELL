extends GutTest
## NA-02 (spec §12.3.1; NA02_FIELDS.md, rulings O1-O13): the netrun-art contract exporter.
## Canonical text is byte-identical to tools/netrun_art/io.py and to itself; every file
## validates against its schema and mutated files are rejected; building ids are unique;
## run_graph.json is 1:1 with the MapGraph; every Exploit Site has an existing building;
## Site -> bid follows ruling O7; the run export takes <= 50 ms for a 40-Site city.
## (The 1,000-seed id sweep and the fresh-process check: test_netrun_art_export_sweep.gd.)

const SchemaCheck := preload("res://tools/netrun_art/schema_check.gd")
const CITY_CONFIG := "res://content/config/city_config.tres"
## io.canonical_dumps of the fixture in test_canonical_matches_python_io (UTF-8 bytes, hex),
## recorded from tools/netrun_art/io.py at main 6de1a521.
const PY_FIXTURE_HEX := "7b0a2022657363223a2022715c22625c5c6e5c6e5c745c7530303031222c0a202266223a205b0a2020302e352c0a2020312e302c0a2020302e302c0a202031322e333435372c0a2020302e303030312c0a2020302e303030312c0a2020302e302c0a20202d332e313431362c0a2020313030303030302e300a205d2c0a202269223a205b0a2020302c0a20202d372c0a2020393030373139393235343734303939320a205d2c0a20226e616d65223a2022c3a974c3a920cea920e697a5e69cac222c0a20226e6573746564223a207b0a20202261223a207b7d2c0a20202262223a205b5d2c0a20202279223a206e756c6c2c0a2020227a223a20747275650a207d2c0a2022753634223a20223138343436373434303733373039353531363135220a7d0a"

var _cfg: CityConfig
var _meridian: CorporationData
var _points: Dictionary
var _city: Dictionary
var _index: Dictionary
var _prisms: Array
var _resolver: CombatResolver


func before_all() -> void:
	_cfg = load(CITY_CONFIG)
	_meridian = ContentRegistry.get_content(&"meridian") as CorporationData
	_points = CityLayout.site_points(_meridian)
	var model := CityModel.build(_cfg, _cfg.city_seed, _sites_rect(_points, _cfg.art_site_bid_reach_lots + 2))
	_prisms = model.prisms
	_city = NetrunArtExport.city_json(model.city_seed, _cfg.lot_bu, _cfg.district_centre, model.prisms, model.streets,
		model.plazas, model.hqs)
	_index = NetrunArtExport.lot_index(_city["buildings"])
	_resolver = CombatFixture.resolver()


func after_each() -> void:
	NetrunArtExport.sink = Callable()


## The lots round every Site point of `points`, grown by `margin`.
static func _sites_rect(points: Dictionary, margin: int) -> Rect2i:
	var lo := Vector2i(1 << 30, 1 << 30)
	var hi := -lo
	for id: Variant in points:
		var p := Vector2i((points[id] as Vector2).floor())
		lo = lo.min(p)
		hi = hi.max(p)
	return Rect2i(lo - Vector2i(margin, margin), hi - lo + Vector2i(2 * margin + 1, 2 * margin + 1))


func _session(run_seed: int) -> NetrunSession:
	var c := CampaignRules.new_campaign(_meridian, CombatFixture.config(), GridFixture.lookup(), 3,
		ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	return NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"m1_a", run_seed, _meridian)


func _export(s: NetrunSession) -> Dictionary:
	var r := NetrunArtExport.export_run(s, _city, _index, _points, _cfg.art_site_bid_reach_lots)
	assert_eq(r["error"], "", "the run exports")
	return r["files"]


func test_canonical_matches_python_io() -> void:
	var fx := {"name": "été Ω 日本", "esc": "q\"b\\n\n\t" + String.chr(1),
		"f": [0.5, 1.0, -0.0, 12.34567, 0.00005, 0.00015, 2.5e-5, -3.14159265, 1e6],
		"i": [0, -7, 9007199254740992], "nested": {"b": [], "a": {}, "z": true, "y": null}, "u64": "18446744073709551615"}
	assert_eq(NetrunArtExport.canonical(fx).to_utf8_buffer().hex_encode(), PY_FIXTURE_HEX,
		"byte-identical to io.canonical_dumps (UTF-8 unescaped, 1e-4 floats, sorted keys, indent 1, LF)")


func test_same_inputs_export_byte_identical() -> void:
	var model := CityModel.build(_cfg, _cfg.city_seed, _sites_rect(_points, _cfg.art_site_bid_reach_lots + 2))
	var again := NetrunArtExport.city_json(model.city_seed, _cfg.lot_bu, _cfg.district_centre, model.prisms,
		model.streets, model.plazas, model.hqs)
	assert_eq(NetrunArtExport.canonical(again), NetrunArtExport.canonical(_city), "city.json")
	var a := _export(_session(11))
	var b := _export(_session(11))
	assert_eq(a.keys().size(), 4)
	for name: String in a:
		assert_eq(b[name], a[name], name)
		assert_true(a[name].ends_with("}\n") and not a[name].contains("\r"), "%s: LF, one trailing LF" % name)


func _all_docs() -> Dictionary:
	var files := _export(_session(11))
	var docs := {"city": JSON.parse_string(NetrunArtExport.canonical(_city))}
	for name: String in files:
		docs["derive" if name.begins_with("derive_") else name.get_basename()] = JSON.parse_string(files[name])
	return docs


func test_every_file_validates_against_its_schema() -> void:
	var docs := _all_docs()
	for name in ["city", "net", "run_graph", "key_locations", "derive"]:
		var sch := SchemaCheck.schema(name)
		assert_false(sch.is_empty(), "%s schema loads" % name)
		assert_eq(int(sch.get("version", 0)), 1, "%s schema carries version 1" % name)
		assert_eq(SchemaCheck.validate(docs[name], sch), PackedStringArray(), name)


func test_mutated_files_are_rejected() -> void:
	var docs := _all_docs()
	var city: Dictionary = docs["city"].duplicate(true)
	city.erase("lot_bu")
	assert_false(SchemaCheck.validate(city, SchemaCheck.schema("city")).is_empty(), "missing key")
	city = docs["city"].duplicate(true)
	city["buildings"][0]["hq"] = "no"
	assert_false(SchemaCheck.validate(city, SchemaCheck.schema("city")).is_empty(), "wrong type")
	city = docs["city"].duplicate(true)
	city["buildings"].append(city["buildings"][0].duplicate(true))
	assert_false(SchemaCheck.validate(city, SchemaCheck.schema("city")).is_empty(), "duplicate bid")
	var net: Dictionary = docs["net"].duplicate(true)
	net["nodes"][1]["id"] = net["nodes"][0]["id"]
	assert_false(SchemaCheck.validate(net, SchemaCheck.schema("net")).is_empty(), "duplicate Site id")
	var rg: Dictionary = docs["run_graph"].duplicate(true)
	rg["nodes"][0]["type"] = "rest"
	assert_false(SchemaCheck.validate(rg, SchemaCheck.schema("run_graph")).is_empty(), "unknown node type")
	rg = docs["run_graph"].duplicate(true)
	rg["version"] = 2
	assert_false(SchemaCheck.validate(rg, SchemaCheck.schema("run_graph")).is_empty(), "wrong version")
	var kl: Dictionary = docs["key_locations"].duplicate(true)
	kl["locations"][0].erase("bid")
	assert_false(SchemaCheck.validate(kl, SchemaCheck.schema("key_locations")).is_empty(), "missing bid")
	var dv: Dictionary = docs["derive"].duplicate(true)
	dv["art_seeds"]["scene"] = 12
	assert_false(SchemaCheck.validate(dv, SchemaCheck.schema("derive")).is_empty(), "u64 seed as a number")


func test_no_city_cell_intersects_an_hq_rect() -> void:
	assert_eq(_city["hq_overlaps"], [], "hq_overlaps is empty")
	for b: Dictionary in _city["buildings"]:
		if b["hq"]:
			continue
		var c: Array = b["cell"]
		var cell := Rect2i(c[0], c[1], c[2], c[3])
		for cid: Variant in _city["hqs"]:
			var r: Array = _city["hqs"][cid]
			assert_false(Rect2i(r[0], r[1], r[2], r[3]).intersects(cell), "%s clear of %s" % [b["bid"], cid])


func test_hq_overlaps_diagnostic_reports_a_planted_overlap() -> void:
	var b := [{"bid": "13:-36", "hq": false, "cell": [13, -36, 2, 2]}, {"bid": "hq:x", "hq": true, "cell": [4, -36, 10, 10]}]
	var got := NetrunArtExport.hq_overlaps(b, {&"x": Rect2i(4, -36, 10, 10)})
	assert_eq(got, [{"bid": "13:-36", "corp": "x"}])


func test_building_ids_unique_and_cells_disjoint() -> void:
	assert_eq(NetrunArtExport.bid_conflicts(_prisms), PackedStringArray(), "no two cells share a bid")
	# City cells never overlap (an HQ stand-in's rect may reach over an edge lot: lot_index
	# gives that lot to the city building).
	var owner := {}
	var overlaps := 0
	for b: Dictionary in _city["buildings"]:
		if b["hq"]:
			continue
		var c: Array = b["cell"]
		for i in range(c[0], c[0] + c[2]):
			for j in range(c[1], c[1] + c[3]):
				if owner.has(Vector2i(i, j)):
					overlaps += 1
				owner[Vector2i(i, j)] = b["bid"]
	assert_eq(overlaps, 0, "city cells do not overlap")
	var idx := NetrunArtExport.lot_index(_city["buildings"])
	var wrong := 0
	for lot: Vector2i in owner:
		wrong += 0 if idx[lot][0] == owner[lot] else 1
	assert_eq(wrong, 0, "every city lot indexes its own building")
	var seen := {}
	for b: Dictionary in _city["buildings"]:
		assert_false(seen.has(b["bid"]), b["bid"])
		seen[b["bid"]] = true
		if not b["hq"]:
			assert_eq(b["bid"], "%d:%d" % [b["cell"][0], b["cell"][1]], "bid = the cell's origin lot")
	assert_true(seen.size() > 50, "the probe rect holds buildings (%d)" % seen.size())


func test_run_graph_matches_the_map_one_to_one() -> void:
	for run_seed in [3, 11, 404]:
		var s := _session(run_seed)
		var rg: Dictionary = JSON.parse_string(_export(s)["run_graph.json"])
		var map := s.run.map
		assert_eq(rg["layers"], float(map.layer_count()))
		assert_eq(rg["nodes"].size(), map.node_count(), "node count")
		assert_eq(rg["run"], NetrunArtExport.run_id(s.run))
		var ids := []
		var edges := {}
		var n_next := 0
		for n: Dictionary in map.all_nodes():
			ids.append(String(n["id"]))
			for nx: Variant in n["next"]:
				edges["%s>%s" % [n["id"], nx]] = true
				n_next += 1
		var got_ids := []
		for n: Dictionary in rg["nodes"]:
			got_ids.append(n["id"])
			var src := map.get_node(StringName(n["id"]))
			assert_eq(int(n["layer"]), int(src["layer"]))
			assert_eq(int(n["index"]), int(src["index"]))
			assert_eq(n["elite"], bool(src["elite"]))
		ids.sort()
		got_ids.sort()
		assert_eq(got_ids, ids, "node ids 1:1")
		assert_eq(rg["edges"].size(), n_next, "one edge per next entry")
		for e: Dictionary in rg["edges"]:
			assert_true(edges.has("%s>%s" % [e["a"], e["b"]]), "edge %s>%s is in the map" % [e["a"], e["b"]])


func test_key_locations_list_every_exploit_site_on_a_building() -> void:
	var kl: Dictionary = JSON.parse_string(_export(_session(11))["key_locations.json"])
	var bids := {}
	for b: Dictionary in _city["buildings"]:
		bids[b["bid"]] = true
	var want := []
	for sd in _meridian.city_grid.sites:
		if sd.exploit_type != RC.ExploitType.NONE:
			want.append(String(sd.id))
	want.sort()
	var got := []
	for loc: Dictionary in kl["locations"]:
		got.append(loc["site"])
		assert_true(bids.has(loc["bid"]), "%s stands on building %s of city.json" % [loc["site"], loc["bid"]])
		assert_eq(loc["corp"], "meridian")
	assert_eq(got, want, "every Exploit Site, sorted by id")
	assert_true(want.size() >= 1)


func test_site_bid_rule_o7() -> void:
	var blds := [
		{"bid": "0:0", "cell": [0, 0, 2, 2], "hq": false},
		{"bid": "5:0", "cell": [5, 0, 1, 1], "hq": false},
		{"bid": "3:4", "cell": [3, 4, 1, 1], "hq": false},
		{"bid": "hq:x", "cell": [20, 20, 4, 4], "hq": true},
		{"bid": "23:23", "cell": [23, 23, 1, 1], "hq": false},
	]
	var idx := NetrunArtExport.lot_index(blds)
	assert_eq(NetrunArtExport.site_bid(Vector2(1.7, 1.2), idx, 4), "0:0", "the cell holding the lot")
	assert_eq(NetrunArtExport.site_bid(Vector2(21.5, 22.5), idx, 4), "hq:x", "an HQ plaza Site takes the HQ")
	assert_eq(NetrunArtExport.site_bid(Vector2(23.5, 23.5), idx, 4), "23:23", "a city cell under an HQ rect's edge keeps its lot")
	assert_eq(NetrunArtExport.site_bid(Vector2(6.5, 0.5), idx, 4), "5:0", "nearest at Chebyshev 1")
	# (4, 2): "0:0" is at distance 3, "5:0" at 2, "3:4" at 2: tie by (i, j) -> "3:4".
	assert_eq(NetrunArtExport.site_bid(Vector2(4.2, 2.9), idx, 4), "3:4", "ties by (i, j) ascending")
	assert_eq(NetrunArtExport.site_bid(Vector2(12.0, 12.0), idx, 4), "", "nothing within reach")
	assert_eq(NetrunArtExport.site_bid(Vector2(12.0, 12.0), idx, 8), "hq:x", "reach is a parameter")
	assert_eq(NetrunArtExport.site_bid(Vector2.INF, idx, 4), "", "no layout point")
	var corp := CorporationData.new()
	corp.id = &"t"
	corp.city_grid = CityGridData.new()
	var far: Array[SiteData] = [GridFixture.site(&"lost", 1, [], RC.SiteObjective.NONE, RC.ExploitType.INTEL)]
	corp.city_grid.sites = far
	var r := NetrunArtExport.key_locations_json(7, corp, {&"lost": Vector2(12, 12)}, idx, 4)
	assert_true(String(r.get("error", "")).contains("lost"), "the export fails naming the Site")


func test_hook_runs_once_and_observes_only() -> void:
	var calls := []
	NetrunArtExport.sink = func(s: NetrunSession) -> void:
		calls.append(_export(s).size())
	var with_hook := _session(21)
	NetrunArtExport.sink = Callable()
	var without := _session(21)
	assert_eq(calls, [4], "NetrunSession.start calls the hook once")
	assert_eq(with_hook.state_hash(), without.state_hash(), "the hook changes no session state")
	assert_eq(with_hook.campaign.state_hash(), without.campaign.state_hash(), "nor the campaign")


func test_run_export_time_for_a_40_site_city() -> void:
	var corp := CorporationData.new()
	corp.id = &"meridian"
	corp.city_grid = CityGridData.new()
	var sites: Array[SiteData] = []
	var pts := {}
	var keys: Array = _points.keys()
	keys.sort()
	for k in 40:
		var id := StringName("s%02d" % k)
		var links: Array = [StringName("s%02d" % (k + 1))] if k < 39 else []
		sites.append(GridFixture.site(id, 1 + k % 4, links, RC.SiteObjective.NONE, [RC.ExploitType.NONE, RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS][k % 4]))
		pts[id] = _points[keys[k % keys.size()]]
	corp.city_grid.sites = sites
	corp.city_grid.home_site_id = &"s00"
	var grid := GridState.from_grid(corp.city_grid, GridFixture.home_node())
	var s := _session(5)
	var seed := ArtSeed.u64_from_str(_city["layout_seed"])
	var t0 := Time.get_ticks_usec()  # fixed-wait-ok: acceptance 10 budget (measured ~5 ms, 10x headroom)
	var out := PackedStringArray()
	out.append(NetrunArtExport.canonical(NetrunArtExport.net_json(seed, _cfg.lot_bu, _cfg.district_centre, corp, grid, pts)))
	var kl := NetrunArtExport.key_locations_json(seed, corp, pts, _index, _cfg.art_site_bid_reach_lots)
	out.append(NetrunArtExport.canonical(kl))
	out.append(NetrunArtExport.canonical(NetrunArtExport.run_graph_json(s.run.map, "r")))
	out.append(NetrunArtExport.canonical(NetrunArtExport.derive_json("street", seed, "r", ["meridian", "solace"])))
	var ms := (Time.get_ticks_usec() - t0) / 1000.0  # fixed-wait-ok: acceptance 10 budget
	gut.p("NA-02 run export, 40-Site city: %.2f ms" % ms)
	assert_false(kl.has("error"), str(kl.get("error", "")))
	assert_eq(JSON.parse_string(out[0])["nodes"].size(), 40)
	assert_true(ms <= 50.0, "run export %.2f ms <= 50 ms" % ms)
