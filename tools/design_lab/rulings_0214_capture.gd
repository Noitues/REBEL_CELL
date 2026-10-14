extends Node
## Designer rulings 2026-10-14 capture (dev tool, windowed only through tools/run_windowed.py): ruling 3's list for a
## SINGLE pick (left) and ruling 4's raid setup crew line "Crew: X (Stationed: Y)" with the warning (right), as one JPG
## at `--out=<abs file>`.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out.get_base_dir())
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	RunManager.new_campaign(1)
	var holder := Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await _frames(10)
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	await _frames(60)
	var list_img := get_viewport().get_texture().get_image()
	holder.queue_free()
	await _frames(2)
	# Raid setup: a few claimed nodes and a queued raid, nobody stationed.
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = 400
	for t: StringName in [&"firewall_relay", &"safehouse"]:
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var r := RunState.new()
		r.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), r)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, t)
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "capture")
	var holder2 := Control.new()
	holder2.size = Vector2(1280, 720)
	add_child(holder2)
	var hq: Control = load(HQ).instantiate()
	holder2.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(10)
	hq.show_raid()
	await _frames(60)
	var raid_img := get_viewport().get_texture().get_image()
	var sheet := Image.create(list_img.get_width() * 2, list_img.get_height(), false, list_img.get_format())
	sheet.blit_rect(list_img, Rect2i(Vector2i.ZERO, list_img.get_size()), Vector2i.ZERO)
	sheet.blit_rect(raid_img, Rect2i(Vector2i.ZERO, raid_img.get_size()), Vector2i(list_img.get_width(), 0))
	sheet.save_jpg(out, 0.88)
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame
