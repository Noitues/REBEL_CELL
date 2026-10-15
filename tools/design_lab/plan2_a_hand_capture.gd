extends Node
## Plan 2 A-HAND capture (dev tool, windowed only through tools/run_windowed.py).
## `--out=<abs jpg>`: the hand with its leftmost card raised, before (the old pictogram row and clearance, on
## top) and after (below), the bottom of the screen at 1280x720 in one JPG.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const CROP := Rect2(0, 400, 1280, 320)


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	RunManager.save_slot = "plan2_a_hand"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	RunManager.reset()
	RunManager.new_campaign(7)
	var holder := Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_fight(&"collections_agent", 5)
	await _frames(30)
	var before := await _raise(scene, true)
	var after := await _raise(scene, false)
	var sheet := Image.create(1280, int(CROP.size.y) * 2, false, Image.FORMAT_RGB8)
	sheet.blit_rect(before.get_region(Rect2i(CROP)), Rect2i(0, 0, 1280, int(CROP.size.y)), Vector2i(0, 0))
	sheet.blit_rect(after.get_region(Rect2i(CROP)), Rect2i(0, 0, 1280, int(CROP.size.y)), Vector2i(0, int(CROP.size.y)))
	DirAccess.make_dir_recursive_absolute(out.get_base_dir())
	sheet.save_jpg(out, 0.9)
	RunManager.delete_save()
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


## The hand with card 0 raised; `old` puts back the pictogram row and the HP-only clearance.
func _raise(scene: Control, old: bool) -> Image:
	scene._spread_hand(-1)
	await _frames(20)
	for c in scene._hand_box.get_children():
		if c is ZineCard:
			var z := c as ZineCard
			z.pictos_give_way = not old
			z.grown_clear_of = scene.player_hp_rect if old else scene._grown_clear_rect.bind(z)
			z.queue_redraw()
	var first := scene._hand_box.get_child(0) as ZineCard
	first.grow_hover(true)
	first._set_lift(true)
	scene._spread_hand(0)
	await _frames(60)
	var img := get_viewport().get_texture().get_image()
	first.grow_hover(false)
	first._set_lift(false)
	return img
