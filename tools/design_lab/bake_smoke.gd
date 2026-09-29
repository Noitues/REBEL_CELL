extends SceneTree
## Bake smoke test (ANIM-R5 P1; docs/TEST_SUITE.md "What bakes or threads run headless"):
## the city bake on a real renderer, which the headless suite never reaches (no
## RenderingDevice there). Opens the HQ's City Grid, waits (bounded) until its city is
## drawn from a finished bake, then checks every baked entry: its texture is usable (valid
## RID, non-empty size, its viewport or copy alive), its picture read back is not empty and
## not one flat colour, and the map view shows it. Runs once with the kept viewports (the
## game's path) and once with the GPU copy (`CityBakeCache.keep_viewports` off). A Logger
## counts every engine or script error meanwhile; any error fails the run. Needs a display:
##
##   godot --path . -s tools/design_lab/bake_smoke.gd > <log> 2>&1
##
## Prints "bake_smoke: PASS ..." and exits 0, else "bake_smoke: FAIL ..." and exits 1. Then
## grep the log for ERROR (errors printed at exit, after the script, land only in the log).
## Autoload-touching classes load at run time (a -s script compiles before the autoloads).

const HQ := "res://scenes/hq/hq_scene.tscn"
const SLOT := "bake_smoke"
## Frames the Grid may take to show its baked city (bounded; a bake lands in ~1-3 s).
const MAX_WAIT_FRAMES := 1800
## Pixels sampled per side of a picture, and the distinct colours a city must show at least.
const SAMPLES := 24
const MIN_COLOURS := 12
## Frames after the tear-down for queued frees (the kept viewports) to run.
const TEARDOWN_FRAMES := 4


class ErrorCounter extends Logger:
	var errors: PackedStringArray = []
	var _lock := Mutex.new()

	func _log_error(function: String, file: String, line: int, code: String, rationale: String, _editor_notify: bool, error_type: int, _backtraces: Array[ScriptBacktrace]) -> void:
		if error_type == ERROR_TYPE_WARNING:
			return
		_lock.lock()
		errors.append("%s %s (%s:%d %s)" % [code, rationale, file, line, function])
		_lock.unlock()

	func _log_message(_message: String, _error: bool) -> void:
		pass

	func count() -> int:
		_lock.lock()
		var n := errors.size()
		_lock.unlock()
		return n


var _cache: GDScript
var _rm: Node
var _hq: Control
var _log := ErrorCounter.new()
var _phase := 0
var _frames := 0
var _fails: PackedStringArray = []
var _notes: PackedStringArray = []
var _landed_at := 0


func _initialize() -> void:
	OS.add_logger(_log)
	if DisplayServer.get_name() == "headless":
		print("bake_smoke: SKIP (headless: no renderer to bake with)")
		quit(0)
		return
	_cache = load("res://scripts/ui/kit/city_bake_cache.gd")
	process_frame.connect(_tick)


func _tick() -> void:
	_frames += 1
	match _phase:
		0:
			_rm = root.get_node("RunManager")
			_rm.set("save_slot", SLOT)
			_rm.set("scene_switching_enabled", false)
			_rm.call("delete_save")
			_hq = (load(HQ) as PackedScene).instantiate()
			root.add_child(_hq)
			_hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			_hq.call("new_campaign", 1)
			_hq.call("show_grid")
			_phase = 1
			_frames = 0
		1, 3:
			var city := _map_city()
			if city != null and bool(city.call("view_covered")):
				_check("kept viewport" if _phase == 1 else "gpu copy", city)
				if _phase == 1:
					# The copy path: every bake dropped, the same view bakes again.
					_cache.call("shutdown")
					_cache.set("keep_viewports", false)
					city.call("refresh")
					_phase = 3
					_frames = 0
				else:
					_teardown()
			elif _frames > MAX_WAIT_FRAMES:
				_fails.append("%s: the Grid's city never showed a finished bake in %d frames" % ["kept viewport" if _phase == 1 else "gpu copy", MAX_WAIT_FRAMES])
				_teardown()
		5:
			if _frames >= TEARDOWN_FRAMES:
				_finish()


## The Grid map's NeonCity (the one drawing the baked view).
func _map_city() -> Control:
	for n in _hq.find_children("*", "Control", true, false):
		var sc: Script = n.get_script()
		if sc != null and sc.get_global_name() == &"NeonCity" and (n as Control).is_visible_in_tree() and bool(n.call("is_baked")):
			return n as Control
	return null


func _check(path: String, city: Control) -> void:
	var entries: Dictionary = _cache.get("_entries")
	var checked := 0
	for key: String in entries:
		var e: Dictionary = entries[key]
		if e.has("failed"):
			_fails.append("%s: a bake failed" % path)
			continue
		var tex: Texture2D = e.get("texture")
		if not bool(_cache.call("usable", tex)):
			_fails.append("%s: a baked texture is not usable" % path)
			continue
		var kind := String((tex.get_script() as Script).get_global_name()) if tex.get_script() != null else tex.get_class()
		if path == "kept viewport" and (tex.get("held") == null):
			_fails.append("%s: the bake was not kept (%s)" % [path, kind])
		if path == "gpu copy" and (tex.get("rd_copy") == null):
			_fails.append("%s: the bake was not copied (%s)" % [path, kind])
		var img: Image = tex.call("picture") if tex.has_method("picture") else tex.get_image()
		if img == null or img.is_empty():
			_fails.append("%s: the baked picture is empty" % path)
			continue
		var colours := {}
		for i in SAMPLES:
			for j in SAMPLES:
				colours[img.get_pixel(int((i + 0.5) * img.get_width() / SAMPLES), int((j + 0.5) * img.get_height() / SAMPLES)).to_rgba32()] = true
		if colours.size() < MIN_COLOURS:
			_fails.append("%s: the baked picture is flat (%d colours in %d samples)" % [path, colours.size(), SAMPLES * SAMPLES])
		checked += 1
		_notes.append("%s: %dx%d, %d colours" % [path, tex.get_width(), tex.get_height(), colours.size()])
	if checked == 0:
		_fails.append("%s: no bake to check" % path)
	_notes.append("%s: covered after %d frames" % [path, _frames])


func _teardown() -> void:
	_hq.queue_free()
	_cache.call("shutdown")
	_phase = 5
	_frames = 0


func _finish() -> void:
	process_frame.disconnect(_tick)
	var holder := root.get_node_or_null(String(_cache.get("HOLDER_NAME")))
	var left := holder.get_child_count() if holder != null else 0
	if left > 0:
		_fails.append("%d bake viewports left after shutdown" % left)
	_cache.set("keep_viewports", true)
	_rm.call("delete_save")
	_rm.set("save_slot", _rm.get("DEFAULT_SLOT"))
	for e in _log.errors:
		_fails.append("error logged: " + e)
	var ok := _fails.is_empty()
	print("bake_smoke: %s; %s%s" % ["PASS" if ok else "FAIL", "; ".join(_notes), "" if ok else "\n  " + "\n  ".join(_fails)])
	OS.remove_logger(_log)
	quit(0 if ok else 1)
