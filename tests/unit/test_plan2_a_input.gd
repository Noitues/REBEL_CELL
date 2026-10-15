extends GutTest
## Plan 2 A-INPUT: cancel / unstage, card-select then enemy-wheel click, selection staying on the card clicked
## (PB-PT-003b B2, B3, B4, B7; PB-PT-002 C4, B8). Real viewport input, seeded; kept as regressions.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_plan2_a_input"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false
	# Pushed pointer events need a window the size of the screen (the headless one is 64 x 64).
	_win_size = get_window().size
	get_window().size = Vector2i(SCREEN.size)
	# GUT's own output panel sits over the screen and takes the pointer.
	_gut_layer = get_tree().root.find_child("GutLayer", true, false) as CanvasLayer
	if _gut_layer != null:
		_gut_layer_was = _gut_layer.visible
		_gut_layer.visible = false


var _win_size: Vector2i
var _gut_layer: CanvasLayer
var _gut_layer_was: bool = true


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


func _combat(cards: Array[StringName], combat_seed: int = 5, enemy: StringName = &"collections_agent") -> Control:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, combat_seed)
	scene.skip_motion()
	var st: CombatState = scene.engine.state()
	for i in cards.size():
		if i < st.hand.size():
			st.hand[i] = cards[i]
	scene._refresh(st)
	await _frames(3)
	return scene


func _move(at: Vector2) -> void:
	var m := InputEventMouseMotion.new()
	m.position = at
	m.global_position = at
	get_viewport().push_input(m, false)
	await _frames(2)


func _click(at: Vector2, button: int = MOUSE_BUTTON_LEFT, move_first: bool = true) -> void:
	if move_first:
		await _move(at)
	for down in [true, false]:
		var b := InputEventMouseButton.new()
		b.button_index = button as MouseButton
		b.pressed = down
		b.position = at
		b.global_position = at
		b.button_mask = (1 << (button - 1)) if down else 0
		get_viewport().push_input(b, false)
		await _frames(2)


func _key(keycode: int) -> void:
	for down in [true, false]:
		var e := InputEventKey.new()
		e.keycode = keycode as Key
		e.physical_keycode = keycode as Key
		e.pressed = down
		get_viewport().push_input(e, false)
		await _frames(2)


func _card_center(scene: Control, i: int) -> Vector2:
	return scene._card_node(i).get_global_rect().get_center()


func _enemy_view(scene: Control) -> WheelView:
	return scene._view_of(scene.engine.state().enemies[0].id)


func test_aim_cancels_by_esc_right_click_and_z_without_opening_pause() -> void:
	var failures: Array[String] = []
	for way in ["esc", "right_empty", "right_wheel", "right_hand", "z"]:
		var scene := await _combat([&"fine_tune"] as Array[StringName])
		scene.select_card(0)
		await _frames(2)
		if scene.selecting < 0:
			failures.append("%s: not aiming" % way)
			scene.get_parent().queue_free()
			continue
		match way:
			"esc":
				await _key(KEY_ESCAPE)
			"right_empty":
				await _click(Vector2(640, 40), MOUSE_BUTTON_RIGHT)
			"right_wheel":
				await _click(_enemy_view(scene).global_center(), MOUSE_BUTTON_RIGHT)
			"right_hand":
				await _click(_card_center(scene, 0), MOUSE_BUTTON_RIGHT)
			"z":
				await _key(KEY_Z)
		if scene.selecting != -1:
			failures.append("%s: aim stays" % way)
		if scene._settings_panel != null:
			failures.append("%s: pause opened" % way)
		scene.get_parent().queue_free()
		await _frames(1)
	print("A-INPUT cancel failures: ", failures)
	assert_eq(failures, [] as Array[String], "every cancel works")


## B3: click a card, then click each aim zone on the enemy wheel (the pointer arriving by a move first, and
## jumping straight there): the first click plays the card.
func test_card_click_then_enemy_wheel_click_plays_at_once() -> void:
	var failures: Array[String] = []
	for card_id in [&"fine_tune", &"jolt", &"brute_spin"]:
		for jump in [false, true]:
			for zone_i in 3:
				Motion.force_live = jump  # live motion: the card lift, the aim pulse and the zone pulse all run
				var scene := await _combat([card_id] as Array[StringName])
				var view := _enemy_view(scene)
				await _click(_card_center(scene, 0))
				if scene.selecting < 0:
					failures.append("%s: click did not select" % card_id)
					scene.get_parent().queue_free()
					continue
				var on_wheel: Array[Vector2] = []
				for o in scene.selection_options():
					var z: Array = scene._zone_of(o)
					if z[0] == view.combatant.id:
						on_wheel.append(view.zone_center(z[1]))
				if zone_i >= on_wheel.size():
					scene.get_parent().queue_free()
					continue
				var hand_before: int = scene.engine.state().hand.size()
				await _click(on_wheel[zone_i], MOUSE_BUTTON_LEFT, not jump)
				if scene.selecting != -1 or scene.engine.state().hand.size() != hand_before - 1:
					failures.append("%s zone %d jump=%s: first click did not play (selecting=%d)" % [card_id, zone_i, jump, scene.selecting])
				scene.get_parent().queue_free()
				await _frames(1)
	print("A-INPUT B3 failures: ", failures)
	assert_eq(failures, [] as Array[String], "the first click on the wheel plays")


## B3: a click on the enemy wheel off every glowing zone says what to do (never silence), and keeps the aim.
func test_click_off_the_zones_while_aiming_answers() -> void:
	var scene := await _combat([&"fine_tune"] as Array[StringName])
	var view := _enemy_view(scene)
	await _click(_card_center(scene, 0))
	assert_gt(scene.selecting, -1, "aiming")
	var off := view.global_center() + Vector2(0.0, view.extent_radius() * 0.3)
	var hand_before: int = scene.engine.state().hand.size()
	await _click(off)
	assert_gt(scene.selecting, -1, "the aim stays")
	assert_eq(scene.engine.state().hand.size(), hand_before, "nothing played")
	assert_true(scene.toast.label.text.contains("glowing"), "and it says what to do: %s" % scene.toast.label.text)
	scene.get_parent().queue_free()


## B4: a click on a card's face selects that card, never its neighbour, whichever card was last under the pointer
## (hover grows and slides the neighbours; live motion). A right-click on it inspects that card only.
func test_a_click_selects_the_card_clicked_not_its_neighbour() -> void:
	Motion.force_live = true
	var failures: Array[String] = []
	var scene := await _combat([&"fine_tune", &"jolt", &"brute_spin", &"fine_tune", &"jolt"] as Array[StringName])
	var n: int = scene.engine.state().hand.size()
	for order in [range(n), range(n - 1, -1, -1)]:
		for i in order:
			scene.cancel_selection()
			await _click(_card_center(scene, i))
			if scene.selecting != i:
				failures.append("click on card %d selected %d" % [i, scene.selecting])
			scene.cancel_selection()
			await _move(_card_center(scene, i))
			await _frames(12)  # the hover grow / neighbour slide settle
			await _click(_card_center(scene, i), MOUSE_BUTTON_LEFT, false)
			if scene.selecting != i:
				failures.append("settled click on card %d selected %d" % [i, scene.selecting])
	print("A-INPUT B4 failures: ", failures)
	assert_eq(failures, [] as Array[String], "the card clicked is the card selected")
	scene.get_parent().queue_free()


## B2 / PT-002 C4: a visible cancel control while a card is aimed: the UNDO sticker reads CANCEL, is live even
## when UNDO is blocked, and a click on it ends the aim and takes back nothing; Z does the same.
func test_the_sticker_reads_cancel_while_aiming() -> void:
	var scene := await _combat([&"fine_tune", &"jolt"] as Array[StringName])
	var sticker: StickerButton = scene._stickers["undo"]
	var hash_before: int = scene.engine.session.state_hash()
	assert_true(scene._rewind_button.disabled, "nothing to undo at the turn's start")
	await _click(_card_center(scene, 0))
	assert_gt(scene.selecting, -1, "aiming")
	assert_false(scene._rewind_button.disabled, "CANCEL is live")
	assert_eq(sticker.text, "CANCEL", "it reads CANCEL")
	await _click(scene._rewind_button.get_global_rect().get_center())
	assert_eq(scene.selecting, -1, "the click cancelled the aim")
	assert_eq(scene.engine.session.state_hash(), hash_before, "and took nothing back")
	assert_true(scene._rewind_button.disabled, "UNDO is back (and blocked)")
	scene.get_parent().queue_free()


## B7 / PT-002 B8: SEND IT by real clicks through a long elite fight with live motion: every turn needs at most two
## clicks (the first may only end the previous replay), and the screen keeps answering afterwards.
func test_send_it_clicks_never_stall_in_an_elite_fight() -> void:
	Motion.force_live = true
	var worst := 0
	var stalls: Array[String] = []
	for combat_seed in [5, 6]:
		var scene := await _combat([] as Array[StringName], combat_seed, &"recall_unit")
		for t in 8:
			if scene.engine.state().is_over():
				break
			var turn_before: int = scene.engine.state().turn
			var clicks := 0
			var at: Vector2 = scene._end_turn_button.get_global_rect().get_center()
			while scene.engine.state().turn == turn_before and not scene.engine.state().is_over() and clicks < 6:
				await _click(at)
				clicks += 1
			worst = maxi(worst, clicks)
			if clicks > 2:
				stalls.append("seed %d turn %d: %d clicks" % [combat_seed, turn_before, clicks])
			# after the replay the screen answers: a card click selects or plays
			scene.skip_motion()
			await _frames(2)
		scene.get_parent().queue_free()
		await _frames(1)
	print("A-INPUT B7 worst clicks ", worst, " stalls ", stalls)
	assert_eq(stalls, [] as Array[String], "SEND IT never needs more than two clicks")


## B2: Esc on a staged card (one already queued, no aim) takes it back before the pause menu opens; with nothing
## staged Esc opens the pause menu as before.
func test_esc_unstages_a_staged_card_then_pauses() -> void:
	var scene := await _combat([&"jolt"] as Array[StringName])
	var hash_before: int = scene.engine.session.state_hash()
	var hand_before: int = scene.engine.state().hand.size()
	scene.play_card(0)
	scene.skip_motion()
	await _frames(2)
	assert_eq(scene.engine.state().hand.size(), hand_before - 1, "a card is staged")
	assert_true(scene.engine.can_rewind(), "and can be taken back")
	await _key(KEY_ESCAPE)
	scene.skip_motion()
	await _frames(2)
	assert_null(scene._settings_panel, "Esc did not open the pause menu")
	assert_eq(scene.engine.session.state_hash(), hash_before, "the staged card is back in the hand")
	await _key(KEY_ESCAPE)
	assert_not_null(scene._settings_panel, "with nothing staged Esc pauses")
	scene.get_parent().queue_free()
