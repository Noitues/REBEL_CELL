extends GutTest
## Change plan 1, wave 1b, slice 1B-MENU (PT-002a F6, F7, C-2, D-UX5, F16). Headless Godot drops pushed mouse
## clicks to a plain Button, so the F7 guard asks the engine's own hit test (`gui_get_hovered_control` after a pushed
## motion) which control is under the QUIT button, and presses the handler/keys directly.

const TITLE := "res://scenes/menu/title_scene.tscn"
const SCREEN := Vector2(1280, 720)

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_plan1_1b_menu"
	RunManager.scene_switching_enabled = false
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _title() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var title: Control = load(TITLE).instantiate()
	holder.add_child(title)
	title.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(6)
	return title


## F7 (cause): a top-level scrim with a STOP filter is hit-tested before the dialog's own panel whatever the z_index
## (windowed probe: the hovered control over QUIT was `ModalScrim`). So the scrim must not take the mouse, and the
## dialog swallows mouse events outside its panel itself. The hit test is windowed-only (headless has no hover), so
## this guards the structure; the windowed probe's result is in the DECISIONS entry.
func test_f7_the_scrim_takes_no_mouse_and_the_dialog_blocks_the_page_itself() -> void:
	var title := await _title()
	title.confirm_quit()
	await _frames(14)
	var d: ConfirmDialog = title._confirm
	var scrim := d.get_node("ModalScrim") as Control
	assert_true(scrim.top_level)
	assert_eq(scrim.mouse_filter, Control.MOUSE_FILTER_IGNORE, "a top-level scrim never takes the buttons' clicks")
	var outside := InputEventMouseButton.new()
	outside.button_index = MOUSE_BUTTON_LEFT
	outside.pressed = true
	outside.global_position = Vector2(4, 4)
	outside.position = outside.global_position
	d._input(outside)
	assert_true(get_viewport().is_input_handled(), "outside the panel the page does not get the click")


## F7: Enter and the pad's A press the focused answer (the safe one first), Left / Right reach the other answer.
func test_f7_every_quit_answer_has_its_key() -> void:
	var title := await _title()
	title.confirm_quit()
	await _frames(14)
	var d: ConfirmDialog = title._confirm
	var out := {"yes": 0, "no": 0}
	d.confirmed.connect(func() -> void: out["yes"] += 1)
	d.cancelled.connect(func() -> void: out["no"] += 1)
	assert_eq(get_viewport().gui_get_focus_owner(), d.no_button, "the safe answer has the focus")
	var right := InputEventAction.new()
	right.action = &"ui_right"
	right.pressed = true
	Input.parse_input_event(right)
	await _frames(3)
	assert_eq(get_viewport().gui_get_focus_owner(), d.yes_button, "Right reaches QUIT")
	for down in [true, false]:
		var k := InputEventKey.new()
		k.keycode = KEY_ENTER
		k.physical_keycode = KEY_ENTER
		k.pressed = down
		Input.parse_input_event(k)
		await _frames(2)
	assert_eq(out["yes"], 1, "Enter / pad A on QUIT quits")


## F6: Esc in the options panel marks the event handled, then emits `closed` (which frees the panel).
func test_f6_esc_in_options_handles_the_event_before_closing() -> void:
	var panel := SettingsPanel.new()
	add_child_autofree(panel)
	await _frames(2)
	var closed := [0]
	var handled_when_closed := [false]
	var vp := panel.get_viewport()
	panel.closed.connect(func() -> void:
		closed[0] += 1
		handled_when_closed[0] = vp.is_input_handled())
	var esc := InputEventAction.new()
	esc.action = &"ui_cancel"
	esc.pressed = true
	panel._unhandled_input(esc)
	assert_eq(closed[0], 1)
	assert_true(handled_when_closed[0], "handled before `closed` can free the panel")


## C-2: on the last tutorial page the line under the words names the button (FINISH), never NEXT.
func test_c2_the_last_tutorial_page_says_finish() -> void:
	var o := TutorialOverlay.new()
	add_child_autofree(o)
	await _frames(2)
	o.step = TutorialOverlay.STEPS.size() - 1
	o.page = 99
	o._render()
	assert_eq(o.next_button.text, tr("Finish"))
	var tip: String = o.next_button.tooltip_text
	assert_false(tip.contains("NEXT"), "the last page's reason does not say NEXT: %s" % tip)


## D-UX5: OVERTHROW acknowledges at once: the loading overlay is up before the (slow) scene change starts.
func test_dux5_new_campaign_shows_the_loading_overlay_first() -> void:
	var title := await _title()
	title.new_in_slot("gut_1b_menu")
	var ov := title.get_node_or_null("LoadingOverlay") as Control
	assert_not_null(ov, "the overlay is shown in the same frame as the press")
	if ov != null:
		assert_eq(ov.mouse_filter, Control.MOUSE_FILTER_STOP)


# --- F16: the event's lit choice follows focus and hover --------------------------------------------------------

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const EVENT := &"ev_leash_on_the_floor"


func _event_scene() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames()
	DemoSetup.open_event(RunManager.netrun, EVENT)
	scene._show_current()
	await _frames(3)
	Typing.finish_all(get_tree())
	await _frames(3)
	return scene


func _lit(scene: Control) -> Array[String]:
	var out: Array[String] = []
	for b in scene._panel.find_child("Choices", true, false).get_children():
		if b is Button and (b as Button).get_node(^"ChoiceNumber") is ChoiceSticker and ((b as Button).get_node(^"ChoiceNumber") as ChoiceSticker).is_lit():
			out.append(String(b.name))
	return out


func test_f16_the_lit_choice_follows_arrow_focus() -> void:
	var scene := await _event_scene()
	var choices: Node = scene._panel.find_child("Choices", true, false)
	var first := choices.get_child(0) as Button
	var second := choices.get_child(1) as Button
	assert_eq(get_viewport().gui_get_focus_owner(), first, "the page starts on choice 1")
	assert_eq(_lit(scene), [String(first.name)])
	var down := InputEventKey.new()
	down.keycode = KEY_DOWN
	down.physical_keycode = KEY_DOWN
	down.pressed = true
	Input.parse_input_event(down)
	await _frames(3)
	assert_eq(get_viewport().gui_get_focus_owner(), second, "Down moves the focus")
	assert_eq(_lit(scene), [String(second.name)], "and the lit plate moves with it")


func test_f16_hovering_a_choice_lights_it_and_takes_the_focus() -> void:
	var scene := await _event_scene()
	var choices: Node = scene._panel.find_child("Choices", true, false)
	var second := choices.get_child(1) as Button
	second.mouse_entered.emit()
	await _frames(2)
	assert_eq(get_viewport().gui_get_focus_owner(), second)
	assert_eq(_lit(scene), [String(second.name)], "one lit plate, on the hovered choice")
