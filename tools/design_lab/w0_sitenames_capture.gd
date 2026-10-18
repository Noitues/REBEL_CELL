extends Node
## W0 SITENAMES review capture (dev tool, windowed only through tools/run_windowed.py).
## `--out=<abs dir>`: 1920x1080 PNGs 1_grid, 2_raid, 3_netrun, 4_reward. The same script runs on the
## before and the after tree; tools/design_lab/w0_sitenames_sheet.py joins the two runs.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SIZE := Vector2(1920, 1080)

var out: String = ""


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(shot_name: String) -> void:
	await _frames(12)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, shot_name])


func _mount(path: String) -> Control:
	var holder := Control.new()
	holder.size = SIZE
	add_child(holder)
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out)
	RunManager.save_slot = "w0_sitenames"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	# 1 Grid view: a launchable Site selected.
	RunManager.reset()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var hq := _mount(HQ)
	await _frames(60)
	var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
	if not open.is_empty():
		hq.select_site(open[0].id)
	await _frames(60)
	await _shot("1_grid")
	hq.get_parent().queue_free()
	await _frames(3)
	# 2 Raid map: a few claimed nodes and a queued raid.
	RunManager.reset()
	RunManager.new_campaign(1)
	c = RunManager.campaign
	corp = RunManager.corporation
	c.schematics = 400
	for t: StringName in [&"firewall_relay", &"safehouse"]:
		var o := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if o.is_empty():
			break
		var r := RunState.new()
		r.site_id = o[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), r)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), o[0].id, t)
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "capture")
	hq = _mount(HQ)
	await _frames(10)
	hq.show_raid()
	await _frames(80)
	await _shot("2_raid")
	hq.get_parent().queue_free()
	await _frames(3)
	# 3 A netrun header, 4 the reward screen.
	RunManager.reset()
	RunManager.new_campaign(1)
	var nr := _mount(NETRUN)
	nr.start_run(1)
	await _frames(60)
	await _shot("3_netrun")
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	nr._show_current()
	await _frames(60)
	await _shot("4_reward")
	RunManager.delete_save()
	get_tree().quit()
