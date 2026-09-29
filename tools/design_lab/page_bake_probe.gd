extends SceneTree
## Page bake probe (dev tool, ANIM-R5 P2): how long each page shows the city's silhouette
## (or a stand-in) before its own baked image covers the view. Drives the real scenes on a
## real display (never headless: nothing bakes there) and prints, per page, the time from
## the page's switch until every city on screen is covered by a finished bake of its current
## look: "probe <page>: covered in N ms (F frames), bakes landed K".
##
## The flows: a run's route, then an event, the loot page, the Modem and a fight, back to the
## route after each; the run's end page, then the HQ; the Grid and a claim; a run that opens
## on a raid interlude, its playout (the frames the fight camera showed uncovered are
## counted) and the route after it; ANIM-R6 C9: the start page, the HQ New campaign opens and
## that campaign's first Grid. `--leave=F` leaves each page F frames after it is covered
## (a quick player: its prebakes may still run) instead of waiting until no bake runs.
##
##   python tools/run_windowed.py --log <log> -- -s tools/design_lab/page_bake_probe.gd [-- --leave=20] [--why]
##
## (a quiet window: docs/TEST_SUITE.md "Windowed checks"). `--why` prints, at the playout's
## first uncovered frame, its view and look against every bake held or running.
##
## Autoload-touching classes load at run time (a -s script compiles before the autoloads).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const SLOT := "page_bake_probe"
## Frames a page may take to be covered, and to go idle (bounded).
const MAX_FRAMES := 1500
## RunState.Phase values (the enum lives in a class the -s script must not name).
const PHASE_MAP := 0
const PHASE_REWARD := 2
const PHASE_EVENT := 3

var _cache: GDScript
var _rm: Node
var _scene: Control
var _frames := 0
var _leave := -1
var _results: PackedStringArray = []
var _steps: Array = []
var _at := 0
var _mode := ""  # "act", "cover", "settle"
var _name := ""
var _t0 := 0
var _f0 := 0
var _bakes0 := 0
var _uncovered := 0


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--leave="):
			_leave = int(a.trim_prefix("--leave="))
	_cache = load("res://scripts/ui/kit/city_bake_cache.gd")
	_steps = [
		["route (first)", _open_run],
		["event", _page.bind("event")],
		["route (back)", _page.bind("map")],
		["loot", _page.bind("loot")],
		["route (back)", _page.bind("map")],
		["shop", _page.bind("shop")],
		["route (back)", _page.bind("map")],
		["fight", _page.bind("fight")],
		["route (back)", _page.bind("map")],
		["run end (flatline)", _flatline],
		["run end", _page.bind("end")],
		["hq (from the run)", _open_hq.bind("")],
		["grid", _open_hq.bind("grid")],
		["claim", _open_hq.bind("claim")],
		["raid interlude", _open_interlude],
		["interlude playout", _fight_interlude],
		["route (after the raid)", _after_interlude],
		# ANIM-R6 C9: the start page, New campaign's HQ and that campaign's first Grid.
		["start", _open_start],
		["hq (new campaign)", _new_from_start],
		["grid (first, new campaign)", _open_hq.bind("grid")],
	]
	_mode = "act"
	process_frame.connect(_tick)


func _cities() -> Array[Control]:
	var out: Array[Control] = []
	if _scene == null or not is_instance_valid(_scene):
		return out
	for n in _scene.find_children("*", "Control", true, false):
		var sc: Script = n.get_script()
		if sc != null and sc.get_global_name() == &"NeonCity" and (n as Control).is_visible_in_tree() and bool(n.call("is_baked")):
			out.append(n as Control)
	return out


func _covered() -> bool:
	var cities := _cities()
	if cities.is_empty():
		return false
	for c in cities:
		if not bool(c.call("view_covered")):
			return false
	return true


func _tick() -> void:
	_frames += 1
	match _mode:
		"act":
			if _at >= _steps.size():
				_finish()
				return
			_name = String(_steps[_at][0])
			_t0 = Time.get_ticks_msec()
			_f0 = _frames
			_bakes0 = int(_cache.get("bakes_done"))
			_uncovered = 0
			(_steps[_at][1] as Callable).call()
			_at += 1
			_mode = "wait_end" if _name == "run end (flatline)" else "cover"
		"wait_end":
			# ANIM-R6 B4: a fight lost for real (the scene's own combat end demo), its replay and
			# hold; the page's time starts when the run's end page shows.
			if String(_scene.get("_shown_screen")) == "run_end" or _frames - _f0 > MAX_FRAMES:
				var cities := _cities()
				if not cities.is_empty():
					_log("probe %s: the run end's look %s the route's (the flatline's Heat), prebaked %s" % [_name,
						"differs from" if String(cities[0].call("look_key")) != _look_before else "is", _scene.get("run_end_prebake") != ""])
				_t0 = Time.get_ticks_msec()
				_f0 = _frames
				_mode = "cover"
		"cover":
			if _name == "interlude playout":
				# The playout moves its camera: count the frames it showed uncovered until the end.
				if not _covered():
					_uncovered += 1
					if _uncovered == 1 and OS.get_cmdline_user_args().has("--why"):
						_why()
				if bool(_scene.get("playout").call("is_done")) or _frames - _f0 > MAX_FRAMES:
					_log("probe %s: %d frames of %d uncovered (%d ms), bakes landed %d" % [_name, _uncovered, _frames - _f0, Time.get_ticks_msec() - _t0, int(_cache.get("bakes_done")) - _bakes0])
					_settle()
			elif _covered():
				_log("probe %s: covered in %d ms (%d frames), bakes landed %d" % [_name, Time.get_ticks_msec() - _t0, _frames - _f0, int(_cache.get("bakes_done")) - _bakes0])
				_settle()
			elif _frames - _f0 > MAX_FRAMES:
				_log("probe %s: NOT covered in %d frames" % [_name, MAX_FRAMES])
				_settle()
		"settle":
			var done := (_leave >= 0 and _frames - _f0 >= _leave) or (_leave < 0 and int(_cache.call("busy")) == 0)
			if done or _frames - _f0 > MAX_FRAMES:
				_mode = "act"


## `--why`: what an uncovered city shows against what the cache holds (its view, and each
## finished or running bake's region and whether its look is the city's).
func _why() -> void:
	for c in _cities():
		var look := String(c.call("look_key"))
		print("  why: view %s look %s" % [c.call("view_rect"), look])
		var entries: Dictionary = _cache.get("_entries")
		for k: String in entries:
			var e: Dictionary = entries[k]
			print("  why: entry %s same look %s%s" % [e.get("region"), String(e.get("look", "")) == look, "" if String(e.get("look", "")) == look else " (" + String(e.get("look", "")) + ")"])
		var pending: Dictionary = _cache.get("_pending")
		for k: String in pending:
			print("  why: pending %s same look %s" % [pending[k].get("region"), String(pending[k].get("look", "")) == look])


func _settle() -> void:
	_mode = "settle"
	_f0 = _frames


func _log(line: String) -> void:
	print(line)
	_results.append(line)


func _swap(path: String) -> void:
	if _scene != null and is_instance_valid(_scene):
		_scene.free()
	_scene = (load(path) as PackedScene).instantiate()
	root.add_child(_scene)
	_scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _open_run() -> void:
	_rm = root.get_node("RunManager")
	_rm.set("save_slot", SLOT)
	_rm.set("scene_switching_enabled", false)
	_rm.call("delete_save")
	_swap(NETRUN)
	_scene.call("new_campaign", 1)
	_scene.call("start_run", 1)


func _page(page: String) -> void:
	var s: Object = _rm.get("netrun")
	var run: Object = s.get("run")
	match page:
		"map":
			(run.get("pending_rewards") as Array).clear()
			run.set("phase", PHASE_MAP)
			_scene.call("_show_current")
		"event":
			run.set("event_id", &"ev_leash_on_the_floor")
			run.set("phase", PHASE_EVENT)
			_scene.call("_show_current")
		"loot":
			(run.get("pending_rewards") as Array).append({"kind": "card", "options": ["twist", "jam", "cache"]})
			run.set("phase", PHASE_REWARD)
			_scene.call("_show_current")
		"shop":
			s.call("_open_shop")
			_scene.call("_show_current")
		"fight":
			_scene.call("enter_node", (s.call("available_nodes") as Array)[0])
		"end":
			_scene.call("_show_end")


## ANIM-R6 B4: the run ends in a flatline in a real fight: the next fight on the route, set
## one hit from the operative's end and sent (netrun_scene's `--demo-combat --demo-end=lose`
## path); the fight's replay, DEFEAT and its hold play, then the run's end page opens.
func _flatline() -> void:
	var s: Object = _rm.get("netrun")
	var cities := _cities()
	_look_before = String(cities[0].call("look_key")) if not cities.is_empty() else ""
	_scene.call("enter_node", (s.call("available_nodes") as Array)[0])
	_scene.call("_demo_combat_end", "lose")


## The route's look before the flatline (the run end's differs by the Heat it adds).
var _look_before := ""


func _open_hq(page: String) -> void:
	if page == "":
		_swap(HQ)
		_scene.call("show_hq")
	elif page == "grid":
		_scene.call("show_grid")
	else:
		var c: Object = _rm.get("campaign")
		var corp: Object = _rm.get("corporation")
		var grid_data: Object = corp.get("city_grid")
		var first: StringName = (grid_data.call("get_site", grid_data.get("home_site_id")) as Object).get("links")[0]
		var run: Object = (load("res://scripts/state/run_state.gd") as GDScript).new()
		run.set("site_id", first)
		(load("res://scripts/core/campaign_rules.gd") as GDScript).call("on_run_completed", c, corp, _rm.call("config"), run)
		_scene.call("claim", first, &"firewall_relay")


func _open_interlude() -> void:
	_swap(NETRUN)
	_rm.call("delete_save")
	_scene.call("new_campaign", 2)
	_scene.call("start_run", 1)
	var cfg: Object = _rm.call("config")
	(load("res://scripts/core/heat_rules.gd") as GDScript).call("add_heat", _rm.get("campaign"), int((cfg.call("major_heat_levels") as Array)[0]) + 1, cfg, "probe")
	_rm.get("netrun").call("_maybe_raid_interlude")
	_scene.call("_show_current")


## ANIM-R6 C9: the HQ with no campaign opens on its start page (it warms the new campaign's HQ).
func _open_start() -> void:
	_rm.call("delete_save")
	_rm.call("reset")
	_swap(HQ)


## ANIM-R6 C9: New campaign on the start page (the HQ it opens on).
func _new_from_start() -> void:
	_scene.call("new_campaign", 1)


func _fight_interlude() -> void:
	_scene.call("raid_fight")


func _after_interlude() -> void:
	_scene.call("_leave_raid_playout")


func _finish() -> void:
	process_frame.disconnect(_tick)
	print("page_bake_probe: " + " | ".join(_results))
	_cache.call("shutdown")
	_rm.call("delete_save")
	_rm.set("save_slot", _rm.get("DEFAULT_SLOT"))
	quit(0)
