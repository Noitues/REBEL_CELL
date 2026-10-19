extends GutTest
## Street r2 twins (P2-P4 step 1) against the Python port, which equals the art-pass plate (tools/netrun_art/tests/gen_r2_fixtures.py):
## layout pass, dressing plan, facade kits and sign draw lists on the plate's input at art seed 1, byte for byte as canonical text, and the
## adapter on the game-shaped synthetic worlds. Floats of the inputs are hex strings (exact doubles).

const DIR := "res://tools/netrun_art/tests/fixtures/r2/"

static var _laid: Dictionary = {}


func _inputs(name: String) -> Dictionary:
	return NaFixture.decode(JSON.parse_string(FileAccess.get_file_as_string(DIR + "inputs/" + name)))


func _expected(name: String) -> String:
	return FileAccess.get_file_as_string(DIR + "expected/" + name)


func _layout() -> Dictionary:
	if _laid.is_empty():
		var inp := _inputs("s1_layout.json")
		var res := StreetR2Rules.layout_pass(int(inp["seed"]), inp["city"], inp["links"], inp["derive"])
		_laid = {"inp": inp, "city": res["city"], "log": res["log"]}
	return _laid


func test_layout_pass_reproduces_the_plate() -> void:
	var l := _layout()
	var heights := {}
	for b: Dictionary in l["city"]["buildings"]:
		heights["%d_%d" % [b["ci"], b["key"]]] = b["h"]
	var diff := NaFixture.first_diff(StreetR2Util.dumps({"heights": heights, "log": l["log"]}), _expected("s1_layout.json"))
	assert_eq(diff, "", "layout pass: " + diff)


func test_plan_pass_reproduces_the_plate() -> void:
	var l := _layout()
	var plan := StreetR2Rules.plan_pass_lots(int(l["inp"]["seed"]), l["inp"]["derive"], l["city"], l["log"])
	var diff := NaFixture.first_diff(StreetR2Util.dumps(plan), _expected("s1_plan.json"))
	assert_eq(diff, "", "plan: " + diff)
	for k: String in plan["checks"]:
		assert_true(plan["checks"][k]["ok"], "the plate passes its own check " + k)


func test_facade_kits_reproduce_the_plate() -> void:
	var cases: Array = _inputs("s1_kits.json")["cases"]
	var rows: Array = []
	for cs: Dictionary in cases:
		var r := StreetR2Rng.from_seed(StreetR2Util.u64(cs["seed"]))
		var counts := {}
		var res := {}
		if cs["op"] == "face":
			var accs := StreetR2Kits.new_accs()
			var fl: float = cs.get("fl", 1.9)
			StreetR2Kits.kit_face(cs["kit"], cs["a"], cs["c"], cs["z0"], cs["z1"], cs["nx"], cs["ny"], cs["col"], r, accs, int(cs["module"]), fl,
				cs.get("lit_low"), bool(cs.get("lite", false)), cs.get("rh"))
			for m: String in accs:
				res[m] = (accs[m] as StreetR2Faces).faces
				counts[m] = res[m].size()
		else:
			var solid := StreetR2Faces.new()
			var neon := StreetR2Faces.new()
			var kinds := {}
			var ants: Array = []
			StreetR2Kits.roof_clutter(cs["kit"], cs["top"], cs["zt"], r, solid, neon, kinds, ants)
			var kk: Array = kinds.keys()
			IdSort.sort_ids(kk)
			res = {"faces": solid.faces, "prims": solid.prims, "neon": neon.faces, "kinds": kk, "ants": ants}
			counts = {"faces": solid.faces.size(), "prims": solid.prims.size(), "neon": neon.faces.size(), "ants": ants.size()}
		rows.append({"name": "%s:%s:%s" % [cs["op"], cs["kit"], cs["uid"]], "counts": counts, "digest": StreetR2Util.digest(res)})
	var diff := NaFixture.first_diff(StreetR2Util.dumps(rows), _expected("s1_kits.json"))
	assert_eq(diff, "", "kits: " + diff)


func test_sign_draw_lists_reproduce_the_plate() -> void:
	var d := _inputs("s1_signs.json")
	var plan: Dictionary = d["plan"]
	for s: Dictionary in plan["signs"]:
		s["tex"]["seed"] = StreetR2Util.u64(s["tex"]["seed"])
	if plan["mega"] != null:
		plan["mega"]["tex"]["seed"] = StreetR2Util.u64(plan["mega"]["tex"]["seed"])
	var specs := StreetR2Signs.make(plan, StreetR2Signs.table_measure(d["measure"]))
	var diff := NaFixture.first_diff(StreetR2Util.dumps(specs), _expected("s1_signs.json"))
	assert_eq(diff, "", "signs: " + diff)


func test_adapter_plans_game_shaped_streets_like_python() -> void:
	var digs: Dictionary = JSON.parse_string(_expected("adapter_digests.json"))
	var first := true
	for seed_name in ["101", "105", "108"]:
		var w := NaFixture.load_inputs(seed_name)
		var d := NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"], w["partial_street"])
		assert_false(d.has("error"), "seed %s derive: %s" % [seed_name, d.get("error", "")])
		var plan := StreetR2Adapter.plan_street(w["city"], d, w["seed"])
		if first:
			first = false
			var diff := NaFixture.first_diff(StreetR2Util.dumps(plan), _expected("adapter_%s.json" % seed_name))
			assert_eq(diff, "", "adapter plan %s: %s" % [seed_name, diff])
		var want: Dictionary = digs[seed_name]
		for k: String in plan:
			assert_eq(StreetR2Util.digest(plan[k]), want[k], "seed %s section %s" % [seed_name, k])
		assert_eq(plan.size(), want.size(), "seed %s has the same sections" % seed_name)
