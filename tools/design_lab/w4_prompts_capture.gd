extends Node
## Plan 1 W4-PROMPTS capture (dev tool, windowed only through tools/run_windowed.py): the netrun top bar and the
## pause menu with its Resume prompt, side by side, as one JPG at `--out=<abs file>`.

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
	await _frames(40)
	var bar_img := get_viewport().get_texture().get_image()
	scene.open_settings()
	await _frames(60)
	var menu_img := get_viewport().get_texture().get_image()
	var sheet := Image.create(bar_img.get_width() * 2, bar_img.get_height(), false, bar_img.get_format())
	sheet.blit_rect(bar_img, Rect2i(Vector2i.ZERO, bar_img.get_size()), Vector2i.ZERO)
	sheet.blit_rect(menu_img, Rect2i(Vector2i.ZERO, menu_img.get_size()), Vector2i(bar_img.get_width(), 0))
	sheet.save_jpg(out, 0.88)
	get_tree().quit()


func _frames(n: int) -> void:
	for _i in n:
		await get_tree().process_frame
