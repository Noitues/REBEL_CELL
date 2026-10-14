extends Node
## Plan 1 wave 2 review R2 polish capture (dev tool, windowed only through tools/run_windowed.py): the player's wheel
## in four states, each saved as a PNG of the wheel's region under `--out=<abs dir>`:
## a_anchor_accel (twin pointer on ANCHOR and ACCEL), b_echo, c_bottom (twin pointer, one needle at the bottom
## near the HP gauge) and d_cover70 (DOUBLE covering 70 % of the slice).

const COMBAT := "res://scenes/combat/combat_scene.tscn"


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out)
	var rm: Node = RunManager
	rm.new_campaign(1)
	rm.scene_switching_enabled = false
	AudioDirector.muted = true
	var holder := Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	await _frames(30)
	var view: WheelView = scene._player_view
	var w := view.combatant.wheel
	var p0 := int(w.pointer_ticks[0])
	w.rotation = -p0
	view.hover_zone = {"kind": "hub"}
	# a: twin pointer on ANCHOR and ACCEL
	w.ring_segment_ids = [&"seg_anchor", &"seg_accelerator", &"seg_echo"]
	w.pointer_ticks = PackedInt32Array([p0, p0 + 15])
	w.inner_rotation = 0
	await _shot(view, out + "/a_anchor_accel.png")
	# b: ECHO under the needle
	w.pointer_ticks = PackedInt32Array([p0])
	w.inner_rotation = -20
	await _shot(view, out + "/b_echo.png")
	# c: the twin pointer with a needle at the bottom
	var bottom := int(roundf(-180.0 / WheelView.DEG_PER_TICK))
	w.ring_segment_ids = [&"seg_anchor", &"seg_accelerator", &"seg_echo"]
	w.pointer_ticks = PackedInt32Array([bottom, bottom + 15])
	w.inner_rotation = 0
	await _shot(view, out + "/c_bottom.png")
	# d: DOUBLE covering 70 % of the slice
	w.pointer_ticks = PackedInt32Array([p0])
	w.ring_segment_ids = [&"seg_x2", &"seg_pierce", &"seg_corrupt"]
	w.inner_rotation = -4 - p0
	await _shot(view, out + "/d_cover70.png")
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(view: WheelView, path: String) -> void:
	view.queue_redraw()
	await _frames(20)
	var img := get_viewport().get_texture().get_image()
	var r := Rect2i(Vector2i(view.global_position), Vector2i(view.size))
	img.get_region(r.intersection(Rect2i(Vector2i.ZERO, img.get_size()))).save_png(path)
