extends GutTest
## PB-SOL-1 I2 (B-06 / C-05, designer default D-04 (a)): the RESPIN lock stays; the player is warned first.
## RESPIN with plays staged since the last random event asks (a dialog, keyboard-reachable, KEEP PLANNING the
## default); with nothing staged it respins at once. Answering changes the state exactly as the plain respin does.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _win_size: Vector2i
var _gut_layer: CanvasLayer
var _gut_layer_was: bool = true


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_pt_p1_respin"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false
	_win_size = get_window().size
	get_window().size = Vector2i(SCREEN.size)
	_gut_layer = get_tree().root.find_child("GutLayer", true, false) as CanvasLayer
	if _gut_layer != null:
		_gut_layer_was = _gut_layer.visible
		_gut_layer.visible = false


func after_each() -> void:
	get_window().size = _win_size
	if _gut_layer != null and is_instance_valid(_gut_layer):
		_gut_layer.visible = _gut_layer_was
	Motion.force_live = false
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _combat() -> Control:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	await _frames(3)
	return scene


func _key_action(scene: Control, action: StringName) -> void:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	scene._unhandled_input(e)
	await _frames(2)


func test_respin_with_nothing_staged_respins_at_once() -> void:
	var scene := await _combat()
	assert_eq(scene.respin_commits(), 0, "nothing staged")
	var ram: int = scene.engine.state().ram
	scene.request_respin()
	await _frames(2)
	assert_false(scene.respin_warning_open(), "no warning")
	assert_lt(scene.engine.state().ram, ram, "it respun and paid")
	assert_eq(String(scene.engine.session.checkpoint_cause["kind"]), "respin")


func test_respin_with_a_staged_play_asks_first_and_keep_planning_changes_nothing() -> void:
	var scene := await _combat()
	scene.nudge(1)
	scene.skip_motion()
	await _frames(2)
	assert_eq(scene.respin_commits(), 1, "one staged nudge")
	var hash_before: int = scene.engine.session.state_hash()
	scene.request_respin()
	await _frames(3)
	assert_true(scene.respin_warning_open(), "the warning shows")
	var d := scene.get_node("RespinConfirm") as ConfirmDialog
	var q := d.find_child("Question", true, false) as Label
	assert_not_null(q)
	assert_string_contains(q.text, "1 play")
	assert_eq(scene.engine.session.state_hash(), hash_before, "asking changes nothing")
	assert_true(scene.engine.can_rewind(), "UNDO still works while it asks")
	# Keyboard: the safe answer holds focus; Esc answers it.
	assert_true(d.no_button.has_focus(), "KEEP PLANNING is the default focus")
	d.no_button.pressed.emit()
	await _frames(20)
	assert_false(scene.respin_warning_open(), "closed")
	assert_eq(scene.engine.session.state_hash(), hash_before, "KEEP PLANNING changes nothing")
	assert_true(scene.engine.can_rewind(), "the staged play is still undoable")


func test_confirming_the_warning_respins_like_the_plain_respin_and_locks_the_stage() -> void:
	var scene := await _combat()
	scene.nudge(1)
	scene.skip_motion()
	await _frames(2)
	scene.request_respin()
	await _frames(3)
	var d := scene.get_node("RespinConfirm") as ConfirmDialog
	d.yes_button.pressed.emit()
	await _frames(3)
	assert_eq(String(scene.engine.session.checkpoint_cause["kind"]), "respin", "the respin happened")
	assert_false(scene.engine.can_rewind(), "UNDO stops at it, as the rule says")
	assert_eq(scene.respin_commits(), 0)


func test_the_respin_key_and_the_sticker_click_go_through_the_warning() -> void:
	var scene := await _combat()
	scene.nudge(1)
	scene.skip_motion()
	await _frames(2)
	await _key_action(scene, &"respin")
	assert_true(scene.respin_warning_open(), "the R key asks")
	scene.get_node("RespinConfirm").no_button.pressed.emit()
	await _frames(20)
	scene._respin_button.pressed.emit()
	await _frames(3)
	assert_true(scene.respin_warning_open(), "the RESPIN sticker asks")
	# A second request while it is open does not stack a second dialog.
	scene.request_respin()
	await _frames(2)
	var n := 0
	for k in scene.get_children():
		if k is ConfirmDialog and not k.is_queued_for_deletion():
			n += 1
	assert_eq(n, 1, "one dialog")


func test_the_ram_tip_says_there_is_no_debt() -> void:
	var scene := await _combat()
	assert_string_contains(scene.ram_note.tooltip_text, "no debt")
	assert_string_contains(scene.ram_note.tooltip_text, "RESPIN")
