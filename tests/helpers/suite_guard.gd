extends GutHookScript
## The suite guard (ANIM-R6 D9 / D10; docs/TEST_SUITE.md "The suite guard"): GUT's pre-run
## and post-run hook (the same file for both: `-gpre_run_script` and `-gpost_run_script`,
## set in .gutconfig.json and by tools/run_tests.py).
##
## - **Settings as found.** Each test script must leave the Settings autoload as it found
##   it (`Settings.snapshot`: every saved value and the session's `pad_active`). The guard
##   takes a snapshot as each script starts and compares it as the script ends; a script
##   that leaves a change is named (`SETTINGS LEAK <script>: <keys>`), the snapshot is put
##   back (so no later script runs on it: no order-dependent failure) and the run fails.
## - **No orphans left.** When the run ends (after a few frames, so everything queued is
##   gone) no node may be left outside the tree: each is named (`ORPHAN LEFT <node>`) and
##   the run fails. GUT's per-test orphan lines also count nodes that were only queued for
##   deletion when the test ended; this counts only what never goes.
##
## The first run() call is the pre-run hook, the second the post-run hook (static state
## carries over between the two instances GUT makes of this script).

## Frames the post-run hook lets pass so queued frees happen before orphans are counted.
const SETTLE_FRAMES := 3

static var _started: bool = false
static var _snap: Dictionary = {}
static var _script: String = ""
static var leaks: Array[String] = []


func run() -> void:
	if not _started:
		_started = true
		gut.start_script.connect(_on_start_script)
		gut.end_script.connect(_on_end_script)
		return
	await _report()


func _settings() -> Node:
	return gut.get_tree().root.get_node_or_null(^"Settings")


func _on_start_script(coll_script: Variant) -> void:
	var s := _settings()
	_script = String(coll_script.get_full_name()) if coll_script != null and coll_script.has_method(&"get_full_name") else ""
	_snap = s.call(&"snapshot") if s != null else {}


func _on_end_script() -> void:
	var s := _settings()
	if s == null or _snap.is_empty():
		return
	var now: Dictionary = s.call(&"snapshot")
	var changed := changed_keys(_snap, now)
	if changed.is_empty():
		return
	var line := "SETTINGS LEAK %s: %s" % [_script, ", ".join(changed)]
	leaks.append(line)
	print(line)
	s.call(&"restore", _snap)


## The keys whose values differ between two snapshots, sorted.
static func changed_keys(before: Dictionary, after: Dictionary) -> PackedStringArray:
	var out := PackedStringArray()
	for k in before:
		if not after.has(k) or var_to_str(before[k]) != var_to_str(after[k]):
			out.append(String(k))
	for k in after:
		if not before.has(k):
			out.append(String(k))
	out.sort()
	return out


func _report() -> void:
	for i in SETTLE_FRAMES:
		await gut.get_tree().process_frame
	for id in Node.get_orphan_node_ids():
		var n := instance_from_id(id) as Node
		if n == null:
			continue
		var line := "ORPHAN LEFT %s (%s)" % [n, n.get_script().resource_path if n.get_script() != null else n.get_class()]
		leaks.append(line)
		print(line)
	if not leaks.is_empty():
		print("suite guard: %d problem(s): Settings left changed or nodes left outside the tree (lines above)" % leaks.size())
		set_exit_code(1)
