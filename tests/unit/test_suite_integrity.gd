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


## ANIM-R3 B11: the forms a frame signal is connected in: `<sig>.connect(`, `<sig> .connect (`
## and `connect("<sig>", ` / `connect(&"<sig>", ` (Object.connect by name). Group 1 is what is
## connected (up to the next comma or the line's end).
const FRAME_CONNECT_PATTERNS: Array[String] = [
	"\\b(?:%s)\\s*\\.\\s*connect\\s*\\(\\s*(.*)$",
	"\\bconnect\\s*\\(\\s*&?\"(?:%s)\"\\s*,\\s*(.*)$",
]


## The code of `line` without its comment ("" for a comment line). Strings are kept.
static func _frame_code(line: String) -> String:
	var code := line.strip_edges()
	if code.begins_with("#"):
		return ""
	return code


## What `line` connects to a frame signal ("" when it connects nothing to one).
static func _frame_target(line: String) -> String:
	var code := _frame_code(line)
	if code == "":
		return ""
	var sigs := "|".join(FRAME_SIGNALS)
	for pat in FRAME_CONNECT_PATTERNS:
		var re := RegEx.create_from_string(pat % sigs)
		var m := re.search(code)
		if m != null:
			return m.get_string(1).strip_edges()
	return ""


## True when `line` connects a lambda to a frame signal: `func` written in the call (any
## spacing), a `Callable(func` or a lambda held in a variable of `lambdas` (names assigned
## a `func` in the same script; see frame_lambda_lines).
static func frame_lambda(line: String, lambdas: Dictionary = {}) -> bool:
	var target := _frame_target(line)
	if target == "":
		return false
	var is_func := RegEx.create_from_string("^(?:Callable\\s*\\(\\s*)?func\\b")
	if is_func.search(target) != null:
		return true
	var ident := target
	for stop in [",", ")", " ", "."]:
		var at := ident.find(stop)
		if at >= 0:
			ident = ident.left(at)
	return lambdas.has(ident)


## The names `lines` assign a lambda to (`var name := func`, `var name = func`,
## `name = func`, typed `var name: Callable = func`), as a set.
static func lambda_names(lines: PackedStringArray) -> Dictionary:
	var out := {}
	var re := RegEx.create_from_string("^(?:var\\s+)?([A-Za-z_][A-Za-z0-9_]*)\\s*(?::\\s*[A-Za-z_][A-Za-z0-9_\\[\\]]*\\s*)?:?=\\s*func\\b")
	for line in lines:
		var code := _frame_code(line)
		var m := re.search(code)
		if m != null:
			out[m.get_string(1)] = true
	return out


## The 0-based numbers of `lines` (one script) that connect a lambda to a frame signal.
static func frame_lambda_lines(lines: PackedStringArray) -> Array[int]:
	var lambdas := lambda_names(lines)
	var out: Array[int] = []
	for n in lines.size():
		if frame_lambda(lines[n], lambdas):
			out.append(n)
	return out


func test_no_lambda_is_connected_to_a_frame_signal() -> void:
	assert_true(frame_lambda("\tget_tree().process_frame.connect(func() -> void:"), "a lambda on process_frame is caught")
	assert_true(frame_lambda("RenderingServer.frame_post_draw.connect(func() -> void: pass)"), "and on the renderer's")
	assert_false(frame_lambda("\tget_tree().process_frame.connect(_redraw_top_later, CONNECT_ONE_SHOT)"), "a method passes")
	var paths: Array[String] = []
	_game_scripts("res://scripts", paths)
	var found: Array[String] = []
	for p in paths:
		var lines := FileAccess.get_file_as_string(p).split("\n")
		for n in frame_lambda_lines(lines):
			found.append("%s:%d %s" % [p, n + 1, lines[n].strip_edges()])
	assert_eq(found, [] as Array[String], "no lambda on a frame signal in scripts/")


## ANIM-R3 B11: the rule's heuristics: the spacings and forms that slipped past it, lambdas
## held in a variable, and no false alarm on a method callable.
func test_the_frame_lambda_rule_catches_every_form() -> void:
	assert_true(frame_lambda("\tget_tree().process_frame.connect( func() -> void:"), "a space before func")
	assert_true(frame_lambda("\tget_tree().process_frame.connect(\tfunc(): pass)"), "a tab before func")
	assert_true(frame_lambda("\ttree.process_frame .connect (func(): pass)"), "spaces round the dot and paren")
	assert_true(frame_lambda("\tget_tree().connect(\"process_frame\", func() -> void: pass)"), "connect by the signal's name")
	assert_true(frame_lambda("\tget_tree().connect(&\"physics_frame\", func(): pass, CONNECT_ONE_SHOT)"), "by a StringName")
	assert_true(frame_lambda("\tRenderingServer.connect(\"frame_pre_draw\",func(): pass)"), "no space after the comma")
	assert_true(frame_lambda("\tget_tree().process_frame.connect(Callable(func(): pass))"), "a lambda wrapped in Callable")
	var held := PackedStringArray([
		"func _ready() -> void:",
		"\tvar redraw := func() -> void: queue_redraw()",
		"\tvar typed: Callable = func() -> void: pass",
		"\t_later = func(): pass",
		"\tget_tree().process_frame.connect(redraw, CONNECT_ONE_SHOT)",
		"\tget_tree().connect(\"process_frame\", typed)",
		"\tRenderingServer.frame_post_draw.connect(_later)",
		"\tget_tree().process_frame.connect(_method_callable)",
		"\tbutton.pressed.connect(redraw)",
	])
	assert_eq(frame_lambda_lines(held), [4, 5, 6] as Array[int], "lambdas held in variables are caught; a method and another signal pass")
	# No false alarms.
	assert_false(frame_lambda("\tget_tree().process_frame.connect(function_name)"), "a method whose name starts with func")
	assert_false(frame_lambda("\tget_tree().process_frame.connect(_on_frame.bind(3))"), "a bound method")
	assert_false(frame_lambda("\t# get_tree().process_frame.connect(func(): pass)"), "a comment")
	assert_false(frame_lambda("\tbutton.pressed.connect(func(): pass)"), "a lambda on another signal")
	assert_false(frame_lambda("\tawait get_tree().process_frame"), "an await")
	assert_false(frame_lambda("\tget_tree().process_frame.disconnect(_on_frame)"), "a disconnect")


## Test suite: bounded waits (DECISIONS): a test that starts a motion and then waits a fixed
## time (a timer, `wait_seconds`) or reads the wall clock before asserting flakes under
## load: a slow frame, a tween chain a frame late, a stalled process. Wait on the real
## condition with `BoundedWait.until` (bounded in game time and frames), measure with
## `BoundedWait.timed`, hold a mid-motion look with `BoundedWait.frozen_frames`. The rule flags,
## in the test scripts, a fixed wait or wall-clock read followed by an assertion in the same
## test, and any in a helper function (its caller asserts after it). A line (or the comment
## line right above it) carrying FIXED_WAIT_OK and a reason is let through: a wait that only
## lets motion run before a skip or settle, or a performance bound. Text in strings and
## comments is not code.
const FIXED_WAIT_CALLS: Array[String] = ["create_timer(", "wait_seconds(", "Time.get_ticks_msec(", "Time.get_ticks_usec("]
const FIXED_WAIT_OK := "# fixed-wait-ok:"
const ASSERT_CALLS: Array[String] = ["assert_", "pass_test(", "fail_test(", "pending("]


## `line` without its string literals and its comment.
static func _code_of(line: String) -> String:
	var out := ""
	var in_str := false
	var quote := ""
	var i := 0
	while i < line.length():
		var ch := line[i]
		if in_str:
			if ch == "\\":
				i += 1
			elif ch == quote:
				in_str = false
		elif ch == "\"" or ch == "'":
			in_str = true
			quote = ch
		elif ch == "#":
			break
		else:
			out += ch
		i += 1
	return out


## The fixed waits in a test script's source `src` that break the rule, as "line: code".
static func fixed_waits(src: String) -> Array[String]:
	var out: Array[String] = []
	var lines := src.split("\n")
	var fn_is_test := false
	var in_fn := false
	for n in lines.size():
		var raw := lines[n]
		if raw.begins_with("func ") or raw.begins_with("static func "):
			in_fn = true
			fn_is_test = raw.begins_with("func test_")
			continue
		if raw.begins_with("const ") or raw.begins_with("var ") or raw.begins_with("class ") or raw.begins_with("static var "):
			in_fn = false
			continue
		if not in_fn:
			continue
		var code := _code_of(raw)
		var waits := false
		for call in FIXED_WAIT_CALLS:
			if code.contains(call):
				waits = true
		if not waits:
			continue
		if raw.contains(FIXED_WAIT_OK) or (n > 0 and lines[n - 1].strip_edges().begins_with(FIXED_WAIT_OK)):
			continue
		var asserts := not fn_is_test
		var k := n  # the wait's own line may assert (a wall-clock read inside an assert)
		while not asserts and k < lines.size() and not (lines[k].begins_with("func ") or lines[k].begins_with("static func ")):
			var later := _code_of(lines[k])
			for a in ASSERT_CALLS:
				if later.contains(a):
					asserts = true
			k += 1
		if asserts:
			out.append("%d: %s" % [n + 1, raw.strip_edges()])
	return out


func test_no_fixed_wait_gates_an_assertion() -> void:
	var gated := "func test_x() -> void:\n\tstart()\n\tawait get_tree().create_timer(0.3).timeout\n\tassert_true(done())\n"
	assert_eq(fixed_waits(gated).size(), 1, "a timer before an assertion is caught")
	assert_eq(fixed_waits(gated.replace("create_timer(0.3).timeout", "create_timer(Motion.seconds(&\"x\") + 0.1).timeout")).size(), 1, "whatever its argument")
	assert_eq(fixed_waits(gated.replace("get_tree().create_timer(0.3).timeout", "wait_seconds(0.5)")).size(), 1, "wait_seconds too")
	assert_eq(fixed_waits("func test_x() -> void:\n\tvar t := Time.get_ticks_msec()\n\trun()\n\tassert_lt(Time.get_ticks_msec() - t, 500)\n").size(), 2, "a wall-clock assert")
	assert_eq(fixed_waits("func _wait(s: float) -> void:\n\tawait get_tree().create_timer(s).timeout\n").size(), 1, "a helper that waits a fixed time")
	assert_eq(fixed_waits("func test_x() -> void:\n\tassert_true(a)\n\tawait get_tree().create_timer(0.3).timeout\n\tskip()\n").size(), 0, "no assertion after it: passes")
	assert_eq(fixed_waits(gated.replace(".timeout\n", ".timeout  # fixed-wait-ok: lets it run before the skip\n")).size(), 0, "the marker lets it through")
	assert_eq(fixed_waits(gated.replace("\tawait get_tree()", "\t# fixed-wait-ok: why\n\tawait get_tree()")).size(), 0, "on the line above too")
	assert_eq(fixed_waits("func test_x() -> void:\n\tassert_true(has(\"create_timer(\"))\n\t# wait_seconds(1)\n\tassert_true(b)\n").size(), 0, "strings and comments are not code")
	assert_eq(fixed_waits("func test_x() -> void:\n\tawait BoundedWait.until(get_tree(), f, 1.0)\n\tassert_true(f.call())\n").size(), 0, "a bounded poll passes")
	var found: Array[String] = []
	for p in _test_scripts():
		for w in fixed_waits(FileAccess.get_file_as_string(p)):
			found.append("%s:%s" % [p, w])
	assert_eq(found, [] as Array[String], "no fixed wait or wall-clock read gates an assertion (use BoundedWait; see DECISIONS \"Test suite: bounded waits\")")
