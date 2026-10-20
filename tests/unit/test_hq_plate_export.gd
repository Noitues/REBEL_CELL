extends GutTest
## HQ-EXPORT: the HQ plate inputs (HqPlateExport): byte-identical across two runs, the schema keys, every part's transform
## round-trips (local through the placement = world, also through the canonical text), the rooms and the camera equal the page's.

const CORPS: Array[StringName] = [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]
const PX := Vector2i(1920, 1080)
const REACH := 8
const EPS := 0.001
const HQ_TIER := 4

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _model: CityModel


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_model = CityModel.shared(CityView3D.CONFIG, CityPlan.current_seed())


func _page(corp: StringName) -> HqRunView:
	var cd := ContentRegistry.get_content(corp) as CorporationData
	var c := CampaignRules.new_campaign(cd, _cfg, _lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	var s := NetrunSession.start_special(_resolver, c, c.roster[0].id, "boss", &"the_genome_core", HQ_TIER, 5, cd.final_boss.id,
		CampaignRules.boss_overrides(c, cd), cd)
	var v := HqRunView.new()
	v.size = Vector2(PX)
	add_child_autofree(v)
	v.show_run(corp, s.run.map, &"", [], s.available_nodes(), "")
	return v


func _files(corp: StringName, v: HqRunView) -> Dictionary:
	return HqPlateExport.files(corp, v, _model, CityView3D.CONFIG, PX, REACH, "overview", "t")


func test_two_runs_are_byte_identical_and_canonical() -> void:
	for corp in CORPS:
		var a := _files(corp, _page(corp))
		var b := _files(corp, _page(corp))
		assert_eq(a.keys().size(), 3, "%s: three files" % corp)
		for fn: String in a:
			assert_eq(a[fn], b[fn], "%s %s: same bytes" % [corp, fn])
			assert_false(String(a[fn]).contains("\r") or String(a[fn]).contains("\t"), "%s %s: LF, no tabs" % [corp, fn])
			assert_true(String(a[fn]).ends_with("}\n"), "%s %s: one closing LF" % [corp, fn])


func test_schema_keys_are_present() -> void:
	var corp := &"solace"
	var f := _files(corp, _page(corp))
	var comp: Dictionary = JSON.parse_string(f["hq_compound.json"])
	for k in ["version", "corp", "landmark", "units", "layout_seed", "lot_bu", "site", "compound", "parts", "ring"]:
		assert_true(comp.has(k), "hq_compound.json: %s" % k)
	for k in ["hq_rect", "place_lot", "origin_lot"]:
		assert_true(comp["site"].has(k), "site.%s" % k)
	for k in ["glb", "transform", "plan_origin", "footprint"]:
		assert_true(comp["compound"].has(k), "compound.%s" % k)
	for k in ["buildings", "streets", "plazas", "hqs", "window"]:
		assert_true(comp["ring"].has(k), "ring.%s" % k)
	assert_false((comp["ring"]["buildings"] as Array).is_empty(), "the ring holds buildings")
	for k in ["bid", "cell", "hq", "parts", "terr"]:
		assert_true(comp["ring"]["buildings"][0].has(k), "ring building %s" % k)
	assert_false((comp["parts"] as Array).is_empty(), "the compound has parts")
	var rg: Dictionary = JSON.parse_string(f["run_graph.json"])
	for k in ["version", "run", "corp", "layers", "rooms", "edges", "slots", "entry"]:
		assert_true(rg.has(k), "run_graph.json: %s" % k)
	for k in ["id", "layer", "kind", "state", "box", "point", "number", "server"]:
		assert_true(rg["rooms"][0].has(k), "room %s" % k)
	var cap: Dictionary = JSON.parse_string(f["hq_overview_capture.json"])
	for k in ["version", "kind", "view", "corp", "resolution", "camera", "layout_seed", "look"]:
		assert_true(cap.has(k), "capture: %s" % k)
	for k in ["loc", "tgt", "lens", "shift_x", "shift_y", "yaw", "pitch", "dist", "ortho_scale", "projection"]:
		assert_true(cap["camera"].has(k), "camera.%s" % k)
	assert_eq(cap["resolution"], [float(PX.x), float(PX.y)], "JSON parses numbers as floats")


func test_every_part_transform_round_trips() -> void:
	for corp in CORPS:
		var v := _page(corp)
		var at := v.compound_at()
		var parts := HqPlateExport.parts(HqCompoundStage.model_path(corp, HqCompoundStage.manifest(corp)), at)
		assert_false(parts.is_empty(), "%s: parts" % corp)
		var text: Dictionary = JSON.parse_string(NetrunArtExport.canonical({"parts": parts}))
		for i in parts.size():
			var local := HqPlateExport.from_xf(parts[i]["local"])
			var world := HqPlateExport.from_xf(parts[i]["world"])
			assert_true((at * local).is_equal_approx(world), "%s %s: at * local = world" % [corp, parts[i]["name"]])
			var tl := HqPlateExport.from_xf(text["parts"][i]["local"])
			var tw := HqPlateExport.from_xf(text["parts"][i]["world"])
			assert_lt((at * tl).origin.distance_to(tw.origin), EPS, "%s %s: through the text, origin" % [corp, parts[i]["name"]])
			assert_lt(((at * tl).basis.x - tw.basis.x).length() + ((at * tl).basis.y - tw.basis.y).length() + ((at * tl).basis.z - tw.basis.z).length(), EPS,
				"%s %s: through the text, basis" % [corp, parts[i]["name"]])


func test_rooms_and_camera_equal_the_page() -> void:
	var corp := &"halcyon"
	var v := _page(corp)
	var rg := HqPlateExport.rooms_json(v, "t")
	assert_eq((rg["rooms"] as Array).size(), v.graph.all_nodes().size(), "one room per node")
	for r: Dictionary in rg["rooms"]:
		var id := StringName(r["id"])
		assert_eq(r["kind"], v.kind_of(id))
		assert_eq(r["state"], v.state_of(id))
		var p := r["point"] as Array
		assert_eq(Vector3(p[0], p[1], p[2]), v.world_of(id), "room %s: the page's world point" % id)
	var cap := HqPlateExport.capture_json(corp, v, _model, PX, "overview", "t")["camera"] as Dictionary
	assert_eq(cap["tgt"], [v.iso.target.x, v.iso.target.y, v.iso.target.z])
	var eye := v.iso.eye()
	assert_eq(cap["loc"], [eye.x, eye.y, eye.z])
	assert_eq(cap["yaw"], v.iso.yaw_deg)
	assert_eq(cap["ortho_scale"], v.iso.ortho)
