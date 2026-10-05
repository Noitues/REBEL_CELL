extends "res://tools/visual_qa/review_pack.gd"
## ART-5 5d capture lab: one windowed launch walks the corporations x text scales 1.0 / 1.6 /
## 2.0 x the Grid's zooms with the Site markers v4 in every state (cleared = a fight won,
## claimed, DOWN, TAKEN, Exploit Sites, the boss TARGET), an Exploit Site pointed at (its
## decrypted file) and SHOW ALL. Reuses the review pack's harness (settle, city bakes, error
## log). Dev tool, never exported. Run only through tools/run_windowed.py:
##   res://tools/art5/grid_marker_lab.tscn -- --out=<abs dir> [--save-size=800x450]
##       [--corps=a,b] [--scales=1.0,1.6]

const LAB_CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital"]
const LAB_SCALES: Array[float] = [1.0, 1.6, 2.0]
## Runs completed before the picture (Sites cleared along the real rules).
const LAB_RUNS := 4
## The close zoom over the Grid's (bible: x1.7 with labels).
const CLOSE_ZOOM := 1.7

var _corp: StringName = &"meridian"
var _variant: String = "grid"


func _ready() -> void:
	var corps := LAB_CORPS.duplicate()
	var scales := LAB_SCALES.duplicate()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		elif a.begins_with("--save-size="):
			var wh := a.trim_prefix("--save-size=").split("x")
			if wh.size() == 2:
				save_size = Vector2i(int(wh[0]), int(wh[1]))
		elif a.begins_with("--corps="):
			corps.clear()
			for c in a.trim_prefix("--corps=").split(",", false):
				corps.append(StringName(c))
		elif a.begins_with("--scales="):
			scales.clear()
			for s in a.trim_prefix("--scales=").split(",", false):
				scales.append(float(s))
	if out_dir == "":
		push_error("grid_marker_lab: --out=<dir> is required")
		get_tree().quit(2)
		return
	DirAccess.make_dir_recursive_absolute(out_dir)
	_log = ErrorLog.new()
	OS.add_logger(_log)
	_setup_settings()
	for n in get_tree().root.get_children():
		_keep.append(n)
	await get_tree().process_frame
	var count := 0
	for corp in corps:
		for scale in scales:
			for variant in ["grid", "close", "showall"]:
				if variant == "showall" and not is_equal_approx(scale, 1.0):
					continue
				_corp = corp
				_variant = variant
				Settings.text_scale = scale
				Settings.changed.emit()
				await _capture("%s_%s_%s" % [corp, variant, str(scale).replace(".", "")], "_s_lab", "%s %s x%.1f" % [corp, variant, scale])
				count += 1
	_teardown()
	print("GRID MARKER LAB DONE %d frames in %s" % [count, out_dir])
	get_tree().quit()


func _s_lab() -> void:
	_unlock_all_corps()
	var hq: Node = _open(HQ)
	await _frames(2)
	hq.new_campaign(1, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, _corp)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	# Fights won along the real rules, one claimed, then a DOWN node and a TAKEN Site.
	for i in LAB_RUNS:
		var open := RunManager.launchable_sites().filter(func(s: SiteData) -> bool: return s.objective != RC.SiteObjective.CENTRAL_SERVER)
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		run.kind = CampaignRules.run_kind_for(c, open[0])
		CampaignRules.on_run_completed(c, corp, cfg, run, RunManager.lookup())
	DemoSetup.set_schematics(c, DEMO_SCHEMATICS)
	var cleared: Array[StringName] = []
	for sd in corp.city_grid.sites:
		if sd != null and c.grid.is_cleared(sd.id):
			cleared.append(sd.id)
	if cleared.size() >= 2:
		CampaignRules.claim(c, corp, cfg, RunManager.lookup(), cleared[0], &"firewall_relay")
		c.grid.sites[cleared[0]]["condition"] = GridState.Condition.DOWN
		c.grid.sites[cleared[1]]["status"] = GridState.SiteStatus.TAKEN
	hq.selected_site = cleared[0] if not cleared.is_empty() else &""
	await _grid(hq)
	var overlay: CityMapOverlay = hq.city_overlay
	if _variant == "showall":
		hq.grid_legend.show_all_cell.mouse_entered.emit()
	elif _variant == "close":
		var city: NeonCity = hq.wireframe.city
		hq._frame_city(city.scale.x * CLOSE_ZOOM, city.focus_grid, city.focus_anchor)
		await _settle(hq)
	# An Exploit Site pointed at: its decrypted file.
	for n in overlay.nodes:
		if n.has("exploit_tag") and overlay.marker_shown(n):
			overlay._point_at(n["id"])
			break
	await _settle(hq)
