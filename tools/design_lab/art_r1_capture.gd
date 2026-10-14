extends Node
## ART-R1 review sheet capture (dev tool, windowed only through tools/run_windowed.py).
## `--group=<name> --out=<abs dir>`: saves PNGs (<group>_<n>.png). Written to run on BOTH trees
## (before = main fb6ae75d, after = ART-R1): newer APIs are reached through has_method checks.
## Groups: tags (1a), report (3a), claimed (4a), toast (F7), loot (7), cover (9a).

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
	RunManager.save_slot = "art_r1"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	match group:
		"tags":
			await _tags()
		"report":
			await _report()
		"claimed":
			await _claimed()
		"toast":
			await _toast()
		"loot":
			await _loot()
		"rdbg":
			await _rdbg()
		"dbg":
			await _dbg()
		"cover":
			await _cover()
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


## 1a: the HQ Grid at rest (no tags), one node hovered (its tag), the map key's hover (all tags).
func _tags() -> void:
	await _fresh(1)
	var hq := _mount(HQ)
	await _frames(90)
	await _shot("tags_1_rest")
	var target: StringName = &""
	for n in hq.city_overlay.nodes:
		if n.has("marker") and String(n["marker"].get("avail", "")) == "next":
			target = n["id"]
			break
	if target == &"":
		target = hq.city_overlay.nodes[1]["id"]
	var r: Rect2 = hq._map_node_rect(target)
	_hover_at(r.get_center())
	await _frames(40)
	_hover_at(r.get_center() + Vector2(1, 1))
	await _frames(40)
	await _shot("tags_2_hover")
	var key := hq.find_child("MapLegend", true, false) as Control
	if key != null and hq.hq_legend != null and hq.hq_legend.fold_button != null:
		var kr: Rect2 = hq.hq_legend.fold_button.get_global_rect()
		_hover_at(kr.get_center())
		await _frames(40)
		_hover_at(kr.get_center() + Vector2(1, 1))
		await _frames(60)
	await _shot("tags_3_key")
	_hover_at(Vector2(5, 5))


## 3a: the raid report after a held raid.
func _report() -> void:
	await _fresh(3)
	var c := RunManager.campaign
	_advance(3)
	var n := 0
	for sid in c.grid.sites.keys():
		if sid != c.grid.home_site_id and c.grid.status_of(sid) == GridState.SiteStatus.CLEARED and n < 3:
			c.grid.sites[sid]["status"] = GridState.SiteStatus.CLAIMED
			n += 1
	c.heat = 30
	CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "capture")
	var hq := _mount(HQ)
	await _frames(40)
	hq.show_raid()
	await _frames(40)
	RunManager.fight_raid()
	hq.show_raid_summary()
	await _frames(30)
	await _shot("report_1_early")
	await _frames(200)
	await _shot("report_2")


## 4a: three claimed Sites, a raid queued (the HQ idle) and the raid setup.
func _claimed() -> void:
	await _fresh(7)
	var c := RunManager.campaign
	_advance(3)
	var n := 0
	for sid in c.grid.sites.keys():
		if sid != c.grid.home_site_id and c.grid.status_of(sid) == GridState.SiteStatus.CLEARED and n < 3:
			c.grid.sites[sid]["status"] = GridState.SiteStatus.CLAIMED
			n += 1
	c.heat = 30
	CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "capture")
	var hq := _mount(HQ)
	await _frames(100)
	await _frames(420)
	await _shot("claimed_1_idle")
	hq.show_raid()
	await _frames(200)
	await _shot("claimed_2_setup")


## F7: the nudge refusal with the tutorial box left open.
func _toast() -> void:
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
	await _shot("toast_1")


## 7: the loot sheet's row pick page (two picks, so BACK shows).
func _loot() -> void:
	await _fresh(1)
	var nr := _mount(NETRUN)
	nr.start_run(1)
	await _frames(10)
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.pending_rewards.append({"kind": "firmware", "options": ["leech", "overvolt"]})
	run.phase = RunState.Phase.REWARD
	nr._show_current()
	await _frames(60)
	nr.open_reward(0)
	await _frames(80)
	await _shot("loot_1")


## 9a: a reward pick, then the map arriving: a frame every 5 frames for 150 frames.
func _cover() -> void:
	await _fresh(1)
	var nr := _mount(NETRUN)
	nr.start_run(1)
	await _frames(40)
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	nr._show_current()
	await _frames(60)
	await _shot("cover_000")
	nr.choose_reward(0, -1)
	for i in 30:
		await _frames(5)
		get_viewport().get_texture().get_image().save_png("%s/cover_%03d.png" % [out, (i + 1) * 5])


func _dbg() -> void:
	await _fresh(7)
	var c := RunManager.campaign
	_advance(3)
	var n := 0
	for sid in c.grid.sites.keys():
		if sid != c.grid.home_site_id and c.grid.status_of(sid) == GridState.SiteStatus.CLEARED and n < 3:
			c.grid.sites[sid]["status"] = GridState.SiteStatus.CLAIMED
			n += 1
	var hq := _mount(HQ)
	await _frames(120)
	await _shot("dbg_0")
	var v3 = hq.wireframe.city.view3d
	print("MAPLOOK ", v3.map_look(), " mode ", v3.map_mode, " lock ", v3.band_lock)
	for m in [v3._net_mat, v3._net_xray_mat]:
		(m as ShaderMaterial).set_shader_parameter(&"halo", 0.0)
	await _frames(10)
	await _shot("dbg_1_nohalo")
	hq.wireframe.city.pin_influence({})
	await _frames(60)
	await _shot("dbg_2_noinfl")


func _rdbg() -> void:
	await _report()
	var v3 = holder.get_child(0).wireframe.city.view3d
	print("MAPLOOK ", v3.map_look(), " mode ", v3.map_mode, " lock ", v3.band_lock, " rh ", v3.ring_halos)
	holder.get_child(0).wireframe.city.pin_influence({})
	await _frames(60)
	await _shot("rdbg_noinfl")
