extends GutTest
## PB-SOL-1 I1 (B-01, B-13): the rewards screen takes real pointer clicks (move, press, release through the
## viewport) with live motion on: a row opens, a card pick lands, SKIP returns to the list, PROCEED asks and its
## answers work, each on the first click.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _win_size: Vector2i
var _gut_layer: CanvasLayer
var _gut_layer_was: bool = true


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_pt_p1_loot_clicks"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
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
	Motion.force_live = false
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _settle(seconds: float) -> void:
	# A dwell of game time (the clock live motion runs on), the way a person looks at a page before clicking:
	# not a wait that gates an assertion (every check below reads the click's end state).
	await BoundedWait.until(get_tree(), _never, seconds, 1)


func _never() -> bool:
	return false


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
	await _frames(2)


func _centre(c: Control) -> Vector2:
	return c.get_global_rect().get_center()


## A netrun scene on a reward screen with `picks` offers (a card offer each, more cards than one).
func _rewards(picks: int) -> Control:
	RunManager.new_campaign(9)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await _frames(2)
	var s := RunManager.netrun
	var rng := RandomNumberGenerator.new()
	rng.seed = 9
	for i in picks:
		s._offer(&"card", s._card_pool(), 3, rng)
	s.run.phase = RunState.Phase.REWARD
	scene._show_current()
	await _settle(1.6)  # the page's entrance, at live speed
	return scene


func test_the_rewards_list_row_pick_skip_and_proceed_take_the_first_click() -> void:
	var failures: Array[String] = []
	var scene := await _rewards(2)
	var s := RunManager.netrun
	assert_true(scene.rewards_list_on(), "the list shows")
	# 1. A row opens on one click.
	var row := scene._panel.find_child("Reward1", true, false) as Control
	assert_not_null(row, "row 1")
	await _click(_centre(row))
	await _settle(1.6)
	if scene.rewards_list_on():
		failures.append("row 1 click at %s did not open the pick page" % _centre(row))
	# 2. SKIP on the page returns to the list on one click.
	var skip := scene._panel.find_child("Skip", true, false) as Control
	assert_not_null(skip, "SKIP")
	if skip != null:
		var left: int = s.run.pending_rewards.size()
		await _click(_centre(skip))
		await _settle(1.6)
		if s.run.pending_rewards.size() != left - 1:
			failures.append("SKIP click at %s did not skip the pick (%d left)" % [_centre(skip), s.run.pending_rewards.size()])
	# 3. PROCEED asks; its BACK answers on one click, PROCEED on one click.
	var go := scene._panel.find_child("Proceed", true, false) as Control
	assert_not_null(go, "PROCEED")
	if go != null:
		await _click(_centre(go))
		await _settle(1.2)
		var d := scene.get_node_or_null("ProceedConfirm") as ConfirmDialog
		if d == null:
			failures.append("PROCEED click at %s did not ask" % _centre(go))
		else:
			await _click(_centre(d.no_button))
			await _settle(1.0)
			if scene.get_node_or_null("ProceedConfirm") != null and not scene.get_node("ProceedConfirm").is_queued_for_deletion():
				failures.append("BACK click did not close the dialog")
			go = scene._panel.find_child("Proceed", true, false) as Control
			await _click(_centre(go))
			await _settle(1.2)
			d = scene.get_node_or_null("ProceedConfirm") as ConfirmDialog
			if d == null:
				failures.append("second PROCEED click did not ask again")
			else:
				await _click(_centre(d.yes_button))
				await _settle(1.5)
				if s.run.phase == RunState.Phase.REWARD:
					failures.append("the dialog's PROCEED click did not leave the rewards")
	print("PT-P1 rewards failures: ", failures)
	assert_eq(failures, [] as Array[String], "every rewards control takes its first click")


func test_picking_a_card_by_click_lands_and_the_screen_goes_on() -> void:
	var failures: Array[String] = []
	var scene := await _rewards(1)
	var s := RunManager.netrun
	var row := scene._panel.find_child("Reward1", true, false) as Control
	await _click(_centre(row))
	await _settle(1.6)
	var sheet := scene._panel.find_child("LootSheet", true, false) as LootSheet
	assert_not_null(sheet, "the loot sheet")
	var deck: int = s.run.operative.deck.size()
	var stickers: Node = scene._panel.find_child("Stickers", true, false)
	var pick: Control = null
	if stickers != null:
		for k in stickers.get_children():
			if k is Control and (k as Control).visible:
				pick = k
				break
	assert_not_null(pick, "a card on the sheet")
	if pick != null:
		await _click(_centre(pick))
		# The pick flies to the deck and the page leaves: the hold is bounded.
		var left := await BoundedWait.until(get_tree(), _page_left.bind(scene), BoundedWait.motion_limit([&"loot_pick", &"loot_reject"], 4.0))
		assert_true(left, "the loot page's hold ends on its own")
		if s.run.operative.deck.size() != deck + 1:
			failures.append("the card click did not take the card (deck %d -> %d)" % [deck, s.run.operative.deck.size()])
		if s.run.phase == RunState.Phase.REWARD:
			failures.append("the screen stayed on the rewards after the only pick")
	print("PT-P1 pick failures: ", failures)
	assert_eq(failures, [] as Array[String], "a click takes the card")


func _page_left(scene: Control) -> bool:
	return not scene.loot_leaving()
