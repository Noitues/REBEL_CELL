extends GutTest
## Horizontal pass 5 fixes (GAP_ANALYSIS H5), driven through the viewport like real input:
## keyboard actions keep the End Turn preview, focus navigation previews the focused card,
## focus stays in the hand (or falls back to SEND IT), dialogs give focus back, Esc leaves
## the share-code field.


func _frames(n: int = 2) -> void:
	for i in n:
		await get_tree().process_frame


func _key(keycode: Key, shift: bool = false) -> void:
	var down := InputEventKey.new()
	down.keycode = keycode
	down.physical_keycode = keycode
	down.shift_pressed = shift
	down.pressed = true
	get_viewport().push_input(down)
	var up := down.duplicate() as InputEventKey
	up.pressed = false
	get_viewport().push_input(up)


func _begin(slot: String) -> Control:
	RunManager.save_slot = slot
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	return add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())


func _end() -> void:
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


## The End Turn preview for the scene's current state (recomputed, then read back).
func _end_turn_text(scene: Control) -> String:
	scene._show_end_turn_preview()
	return scene.preview_note.label.get_parsed_text()


func test_keyboard_actions_keep_the_end_turn_preview() -> void:
	var scene := _begin("gut_test_kb_preview")
	scene.start_fight(&"triage_unit", 7)
	await _frames()
	_key(KEY_E)  # nudge right: refreshes the hand
	await _frames(3)
	var shown: String = scene.preview_note.label.get_parsed_text()
	assert_eq(shown, _end_turn_text(scene), "E keeps the End Turn preview")
	var owner := get_viewport().gui_get_focus_owner()
	assert_true(owner != null and scene.is_ancestor_of(owner), "focus stays in the combat UI")
	_end()


func test_focus_navigation_previews_the_focused_card() -> void:
	var scene := _begin("gut_test_nav_preview")
	scene.start_fight(&"triage_unit", 7)
	await _frames()
	_key(KEY_RIGHT)
	await _frames(2)
	var shown: String = scene.preview_note.label.get_parsed_text()
	assert_true(get_viewport().gui_get_focus_owner() is ZineCard, "focus moved to a card")
	assert_ne(shown, _end_turn_text(scene), "moving focus shows that card's play instead")
	_end()


func test_focus_falls_back_to_send_it_when_no_card_is_playable() -> void:
	var scene := _begin("gut_test_fallback")
	scene.start_fight(&"triage_unit", 7)
	await _frames()
	scene.engine.state().ram = 0
	scene.play_card(0)  # refused: triggers a refresh with every card unaffordable
	scene._refresh(scene.engine.state())
	await _frames(3)
	var owner := get_viewport().gui_get_focus_owner()
	assert_not_null(owner)
	assert_false(owner is ZineCard and (owner as ZineCard).disabled, "not a dead card")
	_end()


func test_a_closed_confirm_dialog_gives_focus_back() -> void:
	var opener := Button.new()
	opener.text = "Quit"
	add_child_autofree(opener)
	opener.grab_focus()
	await _frames()
	var d := ConfirmDialog.new("Really?")
	add_child(d)
	await _frames()
	d.no_button.pressed.emit()
	await _frames(2)
	assert_eq(get_viewport().gui_get_focus_owner(), opener)


func test_esc_leaves_the_share_code_field() -> void:
	RunManager.save_slot = "gut_test_code_esc"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
	hq.show_start()
	await _frames()
	var field := hq.find_child("CodeEdit", true, false) as LineEdit
	field.grab_focus()
	await _frames()
	_key(KEY_ESCAPE)
	await _frames(2)
	assert_ne(get_viewport().gui_get_focus_owner(), field, "Esc released the field")
	_end()
