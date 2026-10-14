extends Node
## Plan 1 W4-REWARDS capture (dev tool, windowed only through tools/run_windowed.py): the one rewards screen's list
## (a card pick and a Firmware pick) beside a row's pick page, as one JPG at `--out=<abs file>`.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out.get_base_dir())
	RunManager.new_campaign(1)
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
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
	run.pending_rewards.append({"kind": "firmware", "options": ["leech", "overvolt"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	await _frames(60)
	var list_img := get_viewport().get_texture().get_image()
	scene.open_reward(0)
	await _frames(60)
	var page_img := get_viewport().get_texture().get_image()
	var sheet := Image.create(list_img.get_width() * 2, list_img.get_height(), false, list_img.get_format())
	sheet.blit_rect(list_img, Rect2i(Vector2i.ZERO, list_img.get_size()), Vector2i.ZERO)
	sheet.blit_rect(page_img, Rect2i(Vector2i.ZERO, page_img.get_size()), Vector2i(list_img.get_width(), 0))
	sheet.save_jpg(out, 0.88)
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame
