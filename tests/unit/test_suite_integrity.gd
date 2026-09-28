extends GutTest
## Every test script compiles (Animation pass review: GUT skipped a test file that failed
## to parse, silently, for two batches). Test suite optimization (docs/TEST_SUITE.md):
## every test script is listed once in tests/test_manifest.json (its measured time for the
## parallel runner's shards and its tier), holds at least one test, and the fast tier keeps
## the rule guards CLAUDE.md names.

const MANIFEST := "res://tests/test_manifest.json"
const TEST_DIRS: Array[String] = ["res://tests/unit", "res://tests/integration"]
const TIERS: Array[String] = ["fast", "full"]
## The guards the fast tier must always run (CLAUDE.md rule 6 and TECH_SPEC 9): preview ==
## result, rewind never crosses a checkpoint, seeded replay, determinism, save round trip.
const FAST_GUARDS: Array[String] = [
	"res://tests/unit/test_preview.gd",
	"res://tests/unit/test_rewind.gd",
	"res://tests/unit/test_replay.gd",
	"res://tests/unit/test_rng_service.gd",
	"res://tests/unit/test_wheel_math.gd",
	"res://tests/unit/test_raid_resolver.gd",
	"res://tests/unit/test_map_generator.gd",
	"res://tests/integration/test_save_service.gd",
	"res://tests/unit/test_suite_integrity.gd",
]


func _scripts(dir: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_scripts(dir.path_join(d), out)


## The test scripts GUT runs (prefix test_, in the unit and integration folders).
func _test_scripts() -> Array[String]:
	var out: Array[String] = []
	for dir in TEST_DIRS:
		for f in DirAccess.get_files_at(dir):
			if f.begins_with("test_") and f.ends_with(".gd"):
				out.append(dir.path_join(f))
	return out


func _manifest() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
	assert_true(parsed is Dictionary and (parsed as Dictionary).has("scripts"), "%s parses" % MANIFEST)
	return (parsed as Dictionary).get("scripts", {}) if parsed is Dictionary else {}


func test_every_test_script_compiles() -> void:
	var paths: Array[String] = []
	_scripts("res://tests", paths)
	assert_gt(paths.size(), 50, "the suite's scripts were found")
	for p in paths:
		var s := load(p) as GDScript
		assert_not_null(s, "%s loads" % p)
		if s != null:
			assert_true(s.can_instantiate(), "%s compiles" % p)


func test_every_test_script_is_in_the_manifest_once_with_a_tier() -> void:
	var entries := _manifest()
	var scripts := _test_scripts()
	for p in scripts:
		assert_true(entries.has(p), "%s is listed in %s (add it with its tier; see docs/TEST_SUITE.md)" % [p, MANIFEST])
	for p in entries:
		assert_true(scripts.has(p), "the manifest's %s exists" % p)
		var e: Variant = entries[p]
		assert_true(e is Dictionary, "%s: an entry" % p)
		if e is Dictionary:
			assert_true(TIERS.has(String((e as Dictionary).get("tier", ""))), "%s: tier fast or full" % p)
			assert_true(float((e as Dictionary).get("seconds", -1.0)) >= 0.0, "%s: a measured time" % p)
	# Keys of a JSON object are unique, so each script sits in exactly one tier.
	var text := FileAccess.get_file_as_string(MANIFEST)
	for p in scripts:
		assert_eq(text.count("\"%s\"" % p), 1, "%s appears once in the manifest" % p)


func test_no_test_script_is_empty() -> void:
	for p in _test_scripts():
		var src := FileAccess.get_file_as_string(p)
		var tests := 0
		for line in src.split("\n"):
			if line.begins_with("func test_"):
				tests += 1
		assert_gt(tests, 0, "%s holds at least one test" % p)


func test_the_fast_tier_keeps_the_rule_guards() -> void:
	var entries := _manifest()
	for p in FAST_GUARDS:
		assert_true(entries.has(p), "%s is listed" % p)
		if entries.has(p):
			assert_eq(String((entries[p] as Dictionary).get("tier", "")), "fast", "%s runs in the fast tier" % p)


## ANIM-R2 R4: the game's scripts print nothing but the frame-capture markers the strip
## tooling reads (ANIMATION_HANDOFF 6: "anim5: <id> starts on frame N" and the like). A
## debug print left in a script (the city printed on every bake request) fails here.
## Allowed: `print("<tag>` with a tag of CAPTURE_PRINT_TAGS; everything else (other
## prints, prints/printt/print_raw/print_rich/print_debug) is not. tools/ and tests/ may
## print.
const CAPTURE_PRINT_TAGS: Array[String] = ["anim4: ", "anim4b: ", "anim5: ", "MotionDemo: "]
const PRINT_CALLS: Array[String] = ["print(", "prints(", "printt(", "print_raw(", "print_rich(", "print_debug("]


func _game_scripts(dir: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_game_scripts(dir.path_join(d), out)


## The print calls on `line` that break the rule (empty when none).
static func bad_prints(line: String) -> Array[String]:
	var out: Array[String] = []
	var code := line.strip_edges()
	if code.begins_with("#"):
		return out
	for call in PRINT_CALLS:
		var at := code.find(call)
		while at >= 0:
			# A word boundary before the call (not `_print(` or `fingerprint(`).
			var starts := at == 0 or not (code[at - 1].is_valid_identifier() or code[at - 1] == "_" or code[at - 1] == ".")
			if starts:
				var ok := false
				if call == "print(":
					for tag in CAPTURE_PRINT_TAGS:
						if code.substr(at + call.length()).begins_with("\"" + tag):
							ok = true
				if not ok:
					out.append(code)
			at = code.find(call, at + call.length())
	return out


func test_game_scripts_print_only_capture_markers() -> void:
	assert_eq(bad_prints("\tprint(\"SBDBG \", 1)").size(), 1, "a debug print is caught")
	assert_eq(bad_prints("\tprints(\"x\")").size(), 1, "prints is caught")
	assert_eq(bad_prints("\tprint(\"anim5: %s starts\" % id)").size(), 0, "a capture marker passes")
	assert_eq(bad_prints("\t# print(\"x\")").size(), 0, "a comment passes")
	assert_eq(bad_prints("\tvar fp := fingerprint(x)").size(), 0, "a longer name passes")
	var paths: Array[String] = []
	_game_scripts("res://scripts", paths)
	assert_gt(paths.size(), 100, "the game's scripts were found")
	var found: Array[String] = []
	for p in paths:
		var lines := FileAccess.get_file_as_string(p).split("\n")
		for n in lines.size():
			for b in bad_prints(lines[n]):
				found.append("%s:%d %s" % [p, n + 1, b])
	assert_eq(found, [] as Array[String], "no debug prints in scripts/")


## Bake crash (DECISIONS "Animation pass - bake crash"): a lambda connected to one of the
## tree's or the renderer's frame signals outlives the view that made it (a lambda using self
## holds a raw pointer; a one-shot slot is called after its view was freed earlier in the same
## emission). Those signals take a method callable (it holds the object's id).
const FRAME_SIGNALS: Array[String] = ["process_frame", "physics_frame", "frame_pre_draw", "frame_post_draw"]


## True when `line` connects a lambda to a frame signal.
static func frame_lambda(line: String) -> bool:
	var code := line.strip_edges()
	if code.begins_with("#"):
		return false
	for s in FRAME_SIGNALS:
		if code.contains("." + s + ".connect(func"):
			return true
	return false


func test_no_lambda_is_connected_to_a_frame_signal() -> void:
	assert_true(frame_lambda("\tget_tree().process_frame.connect(func() -> void:"), "a lambda on process_frame is caught")
	assert_true(frame_lambda("RenderingServer.frame_post_draw.connect(func() -> void: pass)"), "and on the renderer's")
	assert_false(frame_lambda("\tget_tree().process_frame.connect(_redraw_top_later, CONNECT_ONE_SHOT)"), "a method passes")
	var paths: Array[String] = []
	_game_scripts("res://scripts", paths)
	var found: Array[String] = []
	for p in paths:
		var lines := FileAccess.get_file_as_string(p).split("\n")
		for n in lines.size():
			if frame_lambda(lines[n]):
				found.append("%s:%d %s" % [p, n + 1, lines[n].strip_edges()])
	assert_eq(found, [] as Array[String], "no lambda on a frame signal in scripts/")
