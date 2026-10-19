extends Node
## COMBAT-LOCK capture (dev tool, windowed only through tools/run_windowed.py, 1920x1080, text 1.0).
## `--out=<abs dir>`: crops round the player wheel, PNG each:
##   lock_1_write, lock_2_held, lock_3_scribble, lock_4_wipe   CAP_W1 panel 3 (the N7 lock slash)
##   chase_1..3                                                  Q19 panel 2 (the respin ghost's chevron chase)
## tools/design_lab/combat_lock_sheet.py stitches them into docs/art_review/PLAN2/COMBAT_LOCK.jpg.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const LK = preload("res://tests/helpers/lock_fixture.gd")
## Half the crop's side (px) round the player wheel's centre.
const HALF := 300
## Half the side (px) of a 2x zoom crop (shown at 600 px on the sheet).
const ZOOM_HALF := 150

var _out := ""
var _holder: Control = null


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _wait(sec: float) -> void:
	await get_tree().create_timer(sec).timeout


func _scene() -> Control:
	var s := LK.session()
	_holder = Control.new()
	_holder.size = get_viewport().get_visible_rect().size
	add_child(_holder)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	_holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.engine.resolver = s.resolver
	scene.engine.session = s
	scene.engine.state_changed.emit(s.state, s.last_events)
	scene.skip_motion()
	await _frames(12)
	return scene


func _shot(scene: Control, name: String) -> void:
	await get_tree().process_frame
	var c: Vector2 = scene._player_view.global_center()
	var img := get_viewport().get_texture().get_image()
	var r := Rect2i(Vector2i(c) - Vector2i(HALF - 40, HALF), Vector2i(HALF * 2, HALF * 2)).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
	img.get_region(r).save_png("%s/%s.png" % [_out, name])
	print("shot ", name, " ", r)


## A ZOOM_HALF square round global point `c`, saved as `name` (the sheet shows it at 2x).
func _zoom(name: String, c: Vector2) -> void:
	await get_tree().process_frame
	var img := get_viewport().get_texture().get_image()
	var r := Rect2i(Vector2i(c) - Vector2i(ZOOM_HALF, ZOOM_HALF), Vector2i(ZOOM_HALF * 2, ZOOM_HALF * 2)).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
	img.get_region(r).save_png("%s/%s.png" % [_out, name])
	print("zoom ", name, " ", r)


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(_out)
	DisplayServer.window_set_size(Vector2i(1920, 1080))
	await _frames(6)
	RunManager.save_slot = "combat_lock_cap"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	RunManager.new_campaign(1)
	var scene := await _scene()
	var wheel: WheelState = scene.engine.state().player.wheel
	print("MOTION_LIVE ", Motion.live(&"pencil_write_on"), " ", Motion.live(&"respin_ghost_chase"))
	wheel.add_lock(WheelState.LOCK_NUDGE, &"lk_enemy", 1)
	wheel.add_lock(WheelState.LOCK_RESPIN, &"lk_enemy", 1)
	await _wait(0.2)
	await _shot(scene, "lock_1_write")
	await _wait(1.0)
	await _shot(scene, "lock_2_held")
	var q: Dictionary = scene.hud_layer.buttons()[0]
	var qc: Vector2 = q["center"]
	await _zoom("zoom_held", qc + Vector2(0.0, 12.0))
	scene._on_action_refused(CombatResolver.NUDGE_LOCKED)
	await _wait(0.1)
	await _shot(scene, "lock_3_scribble")
	await _zoom("zoom_scribble", qc + Vector2(0.0, 12.0))
	await _wait(0.8)
	wheel.clear_locks()
	await _wait(0.2)
	await _shot(scene, "lock_4_wipe")
	await _wait(1.0)
	scene._show_respin_odds()
	for i in 3:
		await _wait(0.45)
		await _shot(scene, "chase_%d" % (i + 1))
	RunManager.delete_save()
	get_tree().quit()
