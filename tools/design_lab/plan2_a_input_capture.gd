extends Node
## Plan 2 A-INPUT review capture (dev tool, windowed only through tools/run_windowed.py).
## `--out=<abs dir>`: saves before.png (a card aimed, the sticker as it was: a greyed UNDO) and after.png (the same
## aim with CANCEL live).

const COMBAT := "res://scenes/combat/combat_scene.tscn"


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out)
	RunManager.save_slot = "plan2_a_input"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	RunManager.new_campaign(1)
	var holder := Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	var st: CombatState = scene.engine.state()
	st.hand[0] = &"fine_tune"
	scene._refresh(st)
	await _frames(10)
	scene.select_card(0)
	await _frames(40)
	var sticker: Button = scene._rewind_button
	var label := sticker.text
	# before: what the sticker was while aiming
	sticker.text = "UNDO"
	sticker.disabled = true
	await _frames(6)
	get_viewport().get_texture().get_image().save_png("%s/before.png" % out)
	sticker.text = label
	sticker.disabled = false
	await _frames(6)
	get_viewport().get_texture().get_image().save_png("%s/after.png" % out)
	print("sticker label: ", label, " rect: ", sticker.get_global_rect())
	RunManager.delete_save()
	get_tree().quit()
