extends Node
## Plan 1 wave 3 review sheets capture (dev tool, windowed only through tools/run_windowed.py).
## `--group=grid|route|hq|w3b --out=<abs dir>`: saves numbered PNGs (<group>_<n>.png), one per panel.
## Written to run on BOTH trees (before = gate/PT-002, after = wave 3 + 3b): anything newer than the
## before tree is reached through has_method / property checks, so the before run shows what was there.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const COMBAT := "res://scenes/combat/combat_scene.tscn"

var out: String = ""
var holder: Control


func _ready() -> void:
	var group := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
		elif a.begins_with("--group="):
			group = a.substr(8)
	DirAccess.make_dir_recursive_absolute(out)
	RunManager.save_slot = "w3_sheets"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	match group:
		"grid":
			await _grid()
		"route":
			await _route()
		"hq":
			await _hq()
		"w3b":
			await _w3b()
		"w3b_tut":
			await _w3b_tut()
	RunManager.delete_save()
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(shot_name: String) -> void:
	await _frames(3)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, shot_name])


func _fresh(seed_value: int) -> void:
	if holder != null:
		holder.queue_free()
		holder = null
		await _frames(3)
	RunManager.reset()
	RunManager.new_campaign(seed_value)
	holder = Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)


func _mount(path: String) -> Control:
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _hover_at(p: Vector2) -> void:
	var m := InputEventMouseMotion.new()
	m.position = p
	m.global_position = p
	Input.warp_mouse(p)
	get_viewport().push_input(m)


func _advance(steps: int) -> void:
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	for i in steps:
		var open := CampaignRules.launchable_sites(c, corp, cfg)
		if open.is_empty():
			return
		var run := RunState.new()
		run.site_id = open[0].id
		run.kind = CampaignRules.run_kind_for(c, open[0])
		CampaignRules.on_run_completed(c, corp, cfg, run, RunManager.lookup())


func _grid() -> void:
	# 1: idle, reachable Sites tagged with the orange ring
	await _fresh(1)
	var hq := _mount(HQ)
	await _frames(90)
	await _shot("grid_1")
	# 2: a locked Site pointed at: tooltip and the prerequisite's double ring
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var locked: SiteData = null
	for s in corp.city_grid.sites:
		if s == null:
			continue
		if hq.has_method("lock_line") and hq.lock_line(s) != "":
			locked = s
			break
	if locked == null:
		var open_ids := {}
		for s in CampaignRules.launchable_sites(c, corp, cfg):
			open_ids[s.id] = true
		for s in corp.city_grid.sites:
			if s != null and s.id != c.grid.home_site_id and not open_ids.has(s.id):
				locked = s
				break
	print("locked site: ", locked.id)
	if hq.has_method("_hq_hover_tag"):
		hq._hq_hover_tag(locked.id)
	else:
		hq.city_overlay.hover_id = locked.id
	await _frames(30)
	var r: Rect2 = hq._map_node_rect(locked.id)
	print("locked rect: ", r)
	_hover_at(r.get_center() if r.has_area() else Vector2(640, 360))
	await _frames(100)
	_hover_at(r.get_center() + Vector2(1, 1))
	await _frames(60)
	await _shot("grid_2")
	# 2b: also selected (click) for the pan / ring
	hq.select_site(locked.id)
	await _frames(60)
	await _shot("grid_2b")
	_hover_at(Vector2(5, 5))
	# 3: FLATLINE row / RAID badge on a runnable Site (Heat just under a threshold)
	var open: SiteData = CampaignRules.launchable_sites(c, corp, cfg)[0]
	c.heat = 22
	hq.select_site(open.id)
	await _frames(60)
	await _shot("grid_3")
	# 3b: the RAID badge: a Site and a Heat at which clearing it crosses a raid line
	var found := false
	for h in range(15, 80):
		for s in CampaignRules.launchable_sites(c, corp, cfg):
			c.heat = h
			var pv := CampaignRules.clear_preview(c, corp, cfg, s, RunManager.lookup())
			if bool(pv.get("raid", false)):
				found = true
				print("raid badge at heat ", h, " site ", s.id)
				hq.select_site(s.id)
				await _frames(60)
				await _shot("grid_3b")
				break
		if found:
			break
	# 4: Heat Scrub disabled with its reason (CORE card, nothing to scrub)
	c.heat = 0
	c.schematics = 0
	hq.select_site(c.grid.home_site_id)
	await _frames(60)
	await _shot("grid_4")
	# 5: GRID VIEW during a run
	await _fresh(1)
	var nr := _mount(NETRUN)
	nr.start_run(1)
	await _frames(40)
	await _shot("grid_5a_route")
	nr._grid_zoomed = true
	nr._show_map()
	await _frames(300)
	await _shot("grid_5")


func _route() -> void:
	await _fresh(1)
	var nr := _mount(NETRUN)
	nr.start_run(1)
	await _frames(60)
	await _shot("route_1")
	var s := RunManager.netrun
	s.run.operative.hp = maxi(1, s.run.operative.max_hp - 7)
	nr._show_map()
	await _frames(40)
	if nr.has_method("route_selected"):
		var b := nr._panel.find_child("Node1", true, false) as Button
		if b != null:
			var click := InputEventMouseButton.new()
			click.button_index = MOUSE_BUTTON_LEFT
			click.pressed = true
			b.gui_input.emit(click)
			b.pressed.emit()
	await _frames(60)
	await _shot("route_2")
	var prompt := nr._panel.find_child("RoutePrompt", true, false) as Control
	if prompt != null:
		var pr := prompt.get_global_rect()
		_hover_at(pr.get_center())
		await _frames(100)
		_hover_at(pr.get_center() + Vector2(1, 1))
		await _frames(60)
		await _shot("route_3")
	_hover_at(Vector2(5, 5))


func _hq() -> void:
	await _fresh(7)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	for op in c.roster:
		op.alive = false
	c.schematics = 0
	var hq := _mount(HQ)
	await _frames(90)
	await _shot("hq_1")
	var jack := hq._panel.find_child("Launch", true, false) as Control
	if jack != null:
		var jr := jack.get_global_rect()
		_hover_at(jr.get_center())
		await _frames(100)
		_hover_at(jr.get_center() + Vector2(1, 1))
		await _frames(60)
		await _shot("hq_1b_jackin")
		_hover_at(Vector2(5, 5))
	for tab_name in ["Tab_CREW", "Tab_MARKET"]:
		var tab := hq._panel.find_child(tab_name, true, false) as BaseButton
		if tab != null:
			tab.pressed.emit()
			await _frames(40)
			await _shot("hq_2_" + tab_name.to_lower())
	# 3: CLAIMED stamps + raid-queued note
	await _fresh(7)
	c = RunManager.campaign
	corp = RunManager.corporation
	_advance(3)
	var n := 0
	for sid in c.grid.sites.keys():
		if sid != c.grid.home_site_id and c.grid.status_of(sid) == GridState.SiteStatus.CLEARED and n < 3:
			c.grid.sites[sid]["status"] = GridState.SiteStatus.CLAIMED
			n += 1
	c.heat = 30
	CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "capture")
	hq = _mount(HQ)
	await _frames(20)
	await _shot("hq_3_early")  # W3-POLISH F8: the stamps while they hold, before their wipe
	await _frames(70)
	await _shot("hq_3")
	await _frames(420)
	await _shot("hq_3_later")
	# 4: the raid-queued note with the foot band free (heat crosses 25 with nothing else on screen)
	await _fresh(7)
	c = RunManager.campaign
	c.heat = 10
	hq = _mount(HQ)
	await _frames(60)
	c.heat = 30
	var gauge: Variant = hq.hud.heat_gauge if "hud" in hq else null
	if gauge != null:
		gauge.set_heat(30, 100, HeatRules.band_levels(c, RunManager.config()))
	await _frames(40)
	await _shot("hq_4")


func _w3b() -> void:
	await _fresh(1)
	var scene := _mount(COMBAT)
	scene.auto_start = false
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	if scene.tutorial != null and is_instance_valid(scene.tutorial):
		scene.tutorial.queue_free()
		scene.tutorial = null
	var st: CombatState = scene.engine.state()
	st.hand[0] = &"malware_drop"
	scene._refresh(st)
	await _frames(30)
	scene.play_card(0)
	scene.skip_motion()
	await _frames(20)
	scene.rewind()
	await _frames(25)
	await _shot("w3b_1")
	await _frames(120)
	st = scene.engine.state()
	st.free_nudges = 0
	st.ram = 0
	scene._refresh(st)
	await _frames(10)
	scene.nudge(1)
	await _frames(25)
	await _shot("w3b_2")


## W3-POLISH F7: the nudge refusal with the tutorial box left open (the toast must stand over it).
func _w3b_tut() -> void:
	await _fresh(1)
	var scene := _mount(COMBAT)
	scene.auto_start = false
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	await _frames(30)
	var st: CombatState = scene.engine.state()
	st.free_nudges = 0
	st.ram = 0
	scene._refresh(st)
	await _frames(10)
	scene.nudge(1)
	await _frames(25)
	await _shot("w3b_3")
