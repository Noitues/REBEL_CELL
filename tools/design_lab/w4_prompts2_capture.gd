extends Node
## Plan 1 W4-PROMPTS-2 capture (dev tool, windowed only through tools/run_windowed.py): the combat screen
## (SEND IT, RESPIN / UNDO, Legend, Settings with their key chips) and the HQ start page (the Options line's
## chip), side by side, as one JPG at `--out=<abs file>`.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"


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
	var scene: Control = load(COMBAT).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_fight(&"triage_unit", 7)
	await _frames(60)
	var a_img := get_viewport().get_texture().get_image()
	holder.remove_child(scene)
	scene.queue_free()
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(20)
	hq.show_start()
	await _frames(60)
	var b_img := get_viewport().get_texture().get_image()
	var sheet := Image.create(a_img.get_width() * 2, a_img.get_height(), false, a_img.get_format())
	sheet.blit_rect(a_img, Rect2i(Vector2i.ZERO, a_img.get_size()), Vector2i.ZERO)
	sheet.blit_rect(b_img, Rect2i(Vector2i.ZERO, b_img.get_size()), Vector2i(a_img.get_width(), 0))
	sheet.save_jpg(out, 0.88)
	get_tree().quit()


func _frames(n: int) -> void:
	for _i in n:
		await get_tree().process_frame
