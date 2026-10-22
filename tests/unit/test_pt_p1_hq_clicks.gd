extends GutTest
## PB-SOL-1 I1 (B-02, B-03): real pointer clicks (move, press, release through the viewport) land on the
## HQ's JACK IN and on the pause menu's Quit stickers and its Quit dialog, at the centre and near every edge
## of the control's drawn rect, with live motion (hover growth, press squash) on.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
## How far inside the rect's edge the edge probes click (px).
const EDGE_INSET := 6.0

var _win_size: Vector2i
var _gut_layer: CanvasLayer
var _gut_layer_was: bool = true
var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_pt_p1_hq_clicks"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	Motion.force_live = true
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
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Motion.force_live = false
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


## Real seconds of frames (bounded): live motion needs time, not frames.
func _settle(seconds: float) -> void:
	# A dwell of game time (the clock live motion runs on), the way a person looks at a page before clicking:
	# not a wait that gates an assertion (every check below reads the click's end state).
	await BoundedWait.until(get_tree(), _never, seconds, 1)


func _never() -> bool:
	return false


func _hq() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _settle(1.5)
	return scene


func _move(at: Vector2) -> void:
	var m := InputEventMouseMotion.new()
	m.position = at
	m.global_position = at
	get_viewport().push_input(m, false)
	await _frames(2)


func _click(at: Vector2) -> void:
	await _move(at)
	for down in [true, false]:
		var b := InputEventMouseButton.new()
		b.button_index = MOUSE_BUTTON_LEFT
		b.pressed = down
		b.position = at
		b.global_position = at
		b.button_mask = 1 if down else 0
		get_viewport().push_input(b, false)
		await _frames(2)
	await _frames(4)


## The probe points: the centre, and a point EDGE_INSET inside each side of the control's drawn rect.
func _probes(c: Control) -> Array[Vector2]:
	var r := c.get_global_rect()
	var ctr := r.get_center()
	return [ctr, Vector2(r.position.x + EDGE_INSET, ctr.y), Vector2(r.end.x - EDGE_INSET, ctr.y),
		Vector2(ctr.x, r.position.y + EDGE_INSET), Vector2(ctr.x, r.end.y - EDGE_INSET)]


## Clicks `c` at every probe point and returns the failures (a probe whose click did not press it).
func _press_failures(c: Button, label: String) -> Array[String]:
	var presses := [0]
	c.pressed.connect(func() -> void: presses[0] += 1)
	var out: Array[String] = []
	var i := 0
	for p in _probes(c):
		var before: int = presses[0]
		await _click(p)
		if presses[0] != before + 1:
			out.append("%s probe %d at %s: %d presses" % [label, i, p, presses[0] - before])
		i += 1
	return out


func test_jack_in_takes_the_first_click_anywhere_on_it() -> void:
	var hq := await _hq()
	var jack := hq._panel.find_child("Launch", true, false) as Button
	assert_not_null(jack, "JACK IN is on the HQ")
	if jack == null:
		return
	assert_false(jack.disabled, "JACK IN is enabled")
	# One press at a time: a fresh run each probe would leave the HQ, so the probes only count presses.
	var failures := await _press_failures(jack, "JACK IN")
	print("PT-P1 JACK IN failures: ", failures)
	assert_eq(failures, [] as Array[String], "every probe click presses JACK IN")


func test_the_pause_menu_quit_stickers_take_the_first_click() -> void:
	var hq := await _hq()
	hq.open_settings()
	await _settle(1.0)
	var failures: Array[String] = []
	for nm in ["QuitMain", "Quit"]:
		for i in 5:
			# Each press changes the screen (QuitMain closes the menu, Quit opens a dialog): a fresh menu per probe.
			if hq._settings_panel != null:
				hq.open_settings()
				await _frames(3)
			hq.open_settings()
			await _settle(0.8)
			var menu: Control = hq._settings_panel
			var b := menu.find_child(nm, true, false) as Button
			assert_not_null(b, nm)
			if b == null:
				return
			var pressed := [0]
			b.pressed.connect(func() -> void: pressed[0] += 1)
			var p: Vector2 = _probes(b)[i]
			await _click(p)
			if pressed[0] != 1:
				failures.append("%s probe %d at %s: %d presses" % [nm, i, p, pressed[0]])
			if is_instance_valid(menu) and menu.exit_dialog != null and is_instance_valid(menu.exit_dialog):
				menu.exit_dialog.queue_free()
				menu.exit_dialog = null
				await _frames(3)
	print("PT-P1 pause failures: ", failures)
	assert_eq(failures, [] as Array[String], "every probe click presses the Quit stickers")


func test_the_quit_dialog_answers_take_the_first_click() -> void:
	var hq := await _hq()
	hq.open_settings()
	await _settle(1.0)
	var menu: Control = hq._settings_panel
	var failures: Array[String] = []
	for answer in ["Yes", "No"]:
		var done := [0]
		# (Not confirm_quit(): its YES would quit the test run.)
		menu._open_exit(ExitDialogs.quit(false), func() -> void: done[0] += 1)
		await _settle(1.2)  # the modal's drop-in
		var d: ConfirmDialog = menu.exit_dialog
		assert_not_null(d)
		var b: Button = d.yes_button if answer == "Yes" else d.no_button
		if answer != "Yes":
			d.cancelled.connect(func() -> void: done[0] += 1)
		var p := b.get_global_rect().get_center()
		await _click(p)
		if done[0] != 1:
			failures.append("%s at %s: %d answers" % [answer, p, done[0]])
		await _settle(0.8)
	print("PT-P1 quit dialog failures: ", failures)
	assert_eq(failures, [] as Array[String], "the first click answers the dialog")
