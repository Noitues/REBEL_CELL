extends Control
## HQ-B lab (M14, HQ redesign direction B; dev tool, never exported): one windowed launch walks
## the HQ's states and writes a frame per state, for reading next to the design's images in
## docs/art_review/HQ_REDESIGN/ (direction_B*.png/jpg, q11_*.png, heat_indicator.jpg). Run only
## through tools/run_windowed.py (never a bare windowed Godot), with APPDATA pointed at a
## scratch folder (the HQ autosaves its lab campaign there):
##
##   python tools/run_windowed.py --log <file> -- res://tools/design_lab/hq_b_lab.tscn -- --out=<abs dir>
##       [--states=idle,site,...] [--scales=1.0,2.0]
##
## States: `idle` (the CREW hand, a raid pending), `site` (another runnable Site picked),
## `claim` (a cleared Site of the Cell's to build on), `repair` (a DOWN node), `upgrade` (an
## active node), `patch` (CORE, damaged), `defence` (the DEFENCE hand with the raid pending),
## `market`, `zoomed_out` (the wheel past the raid range: the GRID band), `heat` (the Heat
## terminal dropped). Writes `s<scale>_<state>.png` (1280x720).

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const ALL := ["idle", "site", "claim", "repair", "upgrade", "patch", "defence", "market", "zoomed_out", "heat"]
const SETTLE := 40
const WAIT := 900
## The lab campaign: the design's moment (Meridian, Heat 58, a raid pending, four crew).
const CORP := &"meridian"
const SEED := 7
const HEAT := 58
const NODES: Array[StringName] = [&"safehouse", &"firewall_relay"]
## Wheel notches out for `zoomed_out`.
const ZOOM_OUT_NOTCHES := 9

var out_dir := ""
var states: Array = ALL
var scales: Array = [1.0]
var _hq: Node = null
## The lab campaign's Sites: a cleared one to claim, the node to bring DOWN, the last runnable.
var _cleared: StringName = &""
var _down: StringName = &""
var _active: StringName = &""


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		elif a.begins_with("--states="):
			states = Array(a.trim_prefix("--states=").split(","))
		elif a.begins_with("--scales="):
			scales = []
			for s in a.trim_prefix("--scales=").split(","):
				scales.append(float(s))
	DirAccess.make_dir_recursive_absolute(out_dir)
	_run.call_deferred()


func _run() -> void:
	for sc: float in scales:
		Settings.text_scale = sc
		Settings.changed.emit()
		for s: String in states:
			print("hq_b_lab: x%.1f state %s" % [sc, s])
			await _screen(s)
			await _shot("s%.1f_%s" % [sc, s])
			_clear()
			await _frames(2)
	print("hq_b_lab: done")
	get_tree().quit(0)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _until(cond: Callable, limit: int = WAIT) -> bool:
	for i in limit:
		if cond.call():
			return true
		await get_tree().process_frame
	print("hq_b_lab: waited %d frames" % limit)
	return false


func _shot(state: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	if img.get_width() != 1280:
		img.resize(1280, 720, Image.INTERPOLATE_LANCZOS)
	img.save_png(out_dir.path_join(state + ".png"))


func _clear() -> void:
	if _hq != null and is_instance_valid(_hq):
		_hq.queue_free()
	_hq = null


## The design's moment: Meridian, two nodes of the Cell's (a Safehouse with an operative on it),
## a cleared Site still to claim, four crew (one flatlined), Heat 58, a raid pending, an Armory.
func _campaign() -> void:
	var p := RunManager.profile
	if not p.unlocks.has(&"unlock_meridian"):
		p.unlocks.append(&"unlock_meridian")
	RunManager.new_campaign(SEED, CORP)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	c.schematics = 300
	for t in NODES:
		# The first runnable Site that can be claimed once cleared (next to home or a Relay).
		for s in CampaignRules.launchable_sites(c, corp, cfg):
			var dry := c.duplicate_state()
			var probe := RunState.new()
			probe.site_id = s.id
			CampaignRules.on_run_completed(dry, corp, cfg, probe)
			if CampaignRules.claim_error(dry, corp, cfg, RunManager.lookup(), s.id, t, RunManager.profile) != "":
				continue
			var run := RunState.new()
			run.site_id = s.id
			CampaignRules.on_run_completed(c, corp, cfg, run)
			CampaignRules.claim(c, corp, cfg, RunManager.lookup(), s.id, t)
			break
	for s in CampaignRules.launchable_sites(c, corp, cfg):
		var dry := c.duplicate_state()
		var probe := RunState.new()
		probe.site_id = s.id
		CampaignRules.on_run_completed(dry, corp, cfg, probe)
		dry.schematics = 999
		if CampaignRules.claim_error(dry, corp, cfg, RunManager.lookup(), s.id, &"firewall_relay", RunManager.profile) != "":
			continue
		var run := RunState.new()
		run.site_id = s.id
		CampaignRules.on_run_completed(c, corp, cfg, run)
		_cleared = s.id
		break
	c.schematics = 300
	for cls in [&"ghost", &"rigger", &"botnet"]:
		var data := RunManager.lookup().get_content(cls) as ClassData
		if data != null:
			CampaignRules.recruit(c, cfg, data)
	c.schematics = 142
	if c.roster.size() > 3:
		c.roster[3].alive = false
	for id in c.grid.claimed_ids():
		if c.grid.node_type_of(id) == &"safehouse" and c.roster.size() > 1:
			CampaignRules.station(c, RunManager.lookup(), c.roster[1].id, id)
		elif id != c.grid.home_site_id:
			_down = id
			_active = id
	print("hq_b_lab: claimed %s cleared %s down %s" % [c.grid.claimed_ids(), _cleared, _down])
	c.grid.home_integrity = c.grid.home_max_integrity - 6
	c.heat = HEAT
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "hq lab")


func _open() -> Node:
	_hq = HQ.instantiate()
	add_child(_hq)
	await _frames(2)
	_campaign()
	_hq.show_hq()
	await _settle()
	return _hq


func _settle() -> void:
	await _until(func() -> bool: return _hq.arrival_ready())
	await _until(func() -> bool:
		var v: CityView3D = _hq.wireframe.city.view3d
		return v == null or (v.model != null and not v.is_processing()))
	await _frames(SETTLE)


func _screen(state: String) -> void:
	var hq: Node = await _open()
	var c := RunManager.campaign
	match state:
		"site":
			var open := RunManager.launchable_sites()
			if not open.is_empty():
				hq.select_site(open[open.size() - 1].id)
		"claim":
			if _cleared != &"":
				hq.select_site(_cleared)
		"repair":
			if _down != &"":
				c.grid.sites[_down]["condition"] = GridState.Condition.DOWN
				hq.select_site(_down)
		"upgrade":
			if _active != &"":
				hq.select_site(_active)
		"patch":
			hq.select_site(c.grid.home_site_id)
		"defence":
			hq.open_hand(hq.HandTab.DEFENCE)
		"market":
			hq.open_hand(hq.HandTab.MARKET)
		"zoomed_out":
			if hq.grid_controls != null:
				for i in ZOOM_OUT_NOTCHES:
					hq.grid_controls.zoom_at(hq.size * 0.5, 1.0)
				print("hq_b_lab: ortho %.0f band %d" % [RaidZoomFit.ortho_of(hq.wireframe.city.scale.x, hq.size.x), hq.wireframe.city.band_lock])
		"heat":
			hq.toggle_heat_terminal()
	await _settle()
