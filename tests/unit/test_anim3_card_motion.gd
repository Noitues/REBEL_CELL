extends GutTest
## Animation pass ANIM-3 (ANIMATION_HANDOFF 4.5; GDD 9.2): card targeting and execution.
## Headless and reduce effects show the end state at once; a cancelled drag returns the
## card to its slot; a played card flies to the zone the action used; the hand keeps a
## gap while a card flies (no card moves under the cursor); hover lifts, drag ghosts
## trail, zones pulse, the RAM cost blinks; the layout holds at the end state; motion
## never changes game state.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _text_scale_before: float = 1.0
var _reduce_before: bool = false


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_reduce_before = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_anim3"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	if Settings.reduce_effects != _reduce_before:
		Settings.set_reduce_effects(_reduce_before)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


func _combat(enemy: StringName = &"collections_agent", scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, 5)
	await _frames()
	return scene


func _live() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Motion.force_live = true


func _signature(scene: Control) -> Array:
	var s: CombatState = scene.engine.state()
	return [s.state_hash(), scene.engine.session.rng.state, s.hand.duplicate(), s.ram, s.turn]


## A playable card with several legal targets (-1 when the hand has none).
func _multi(scene: Control) -> int:
	var s: CombatState = scene.engine.state()
	for i in s.hand.size():
		var card := scene.engine.content(s.hand[i]) as CardData
		if card.ram_cost <= s.ram and CardTargeting.options(scene.engine.resolver, s, i).size() > 1:
			return i
	return -1


func _playable(scene: Control) -> int:
	var s: CombatState = scene.engine.state()
	for i in s.hand.size():
		var card := scene.engine.content(s.hand[i]) as CardData
		if card.ram_cost <= s.ram and not CardTargeting.options(scene.engine.resolver, s, i).is_empty():
			return i
	return -1


func test_headless_plays_cards_with_no_motion() -> void:
	var scene := await _combat()
	var i := _playable(scene)
	assert_true(i >= 0, "a playable card")
	scene.play_card(i)
	assert_false(scene.fx_layer.busy(), "no flight")
	assert_null(scene._gap, "no gap")
	for c in scene._hand_box.get_children():
		assert_true(c is ZineCard, "the hand is cards only")
		assert_eq((c as ZineCard).draw_offset, Vector2.ZERO, "dealt in place")
		assert_eq((c as ZineCard).modulate.a, 1.0, "shown")
	assert_eq(scene.ram_note.shown_ram, scene.engine.state().ram, "RAM chips show the state at once")


func test_reduce_effects_plays_cards_with_no_motion() -> void:
	var scene := await _combat()
	Motion.force_live = true
	Settings.set_reduce_effects(true)
	scene.play_card(_playable(scene))
	assert_false(scene.fx_layer.busy(), "no flight under reduce effects")
	assert_eq(scene.ram_note.shown_ram, scene.engine.state().ram, "RAM at once")


func test_a_cancelled_drag_returns_the_card_to_its_slot() -> void:
	var scene := await _combat()
	_live()
	var i := _multi(scene)
	if i < 0:
		i = _playable(scene)
	var node: ZineCard = scene._card_node(i)
	var slot := node.get_global_rect()
	var index := node.get_index()
	scene._dragging = true
	scene._begin_targeting(i, CardTargeting.options(scene.engine.resolver, scene.engine.state(), i))
	scene._dragging = false
	scene._cancel_drag(i, Vector2(700, 300))
	assert_eq(scene.selecting, -1, "the aim ends")
	var f: Dictionary = scene.fx_layer.last_flight("return")
	assert_false(f.is_empty(), "a copy glides home")
	assert_eq(f["to"], slot.get_center(), "to the card's own slot")
	assert_eq(node.modulate.a, 0.0, "the slot waits for it")
	await get_tree().create_timer(Motion.seconds(&"drag_cancel_return") + 0.15).timeout
	assert_true(scene.fx_layer.last_flight("return").is_empty(), "it has landed")
	assert_eq(node.modulate.a, 1.0, "the card shows in its slot again")
	assert_eq(node.get_index(), index, "at the same place in the hand")
	assert_eq(node.get_global_rect(), slot, "nothing moved")


func test_a_drop_snaps_to_the_zone_the_action_used() -> void:
	var scene := await _combat()
	_live()
	var i := _multi(scene)
	assert_true(i >= 0, "a card with several targets")
	scene.select_card(i)
	scene.step_selection(1)
	var action: CombatAction = scene.aimed_action()
	var z: Array = scene._zone_of(action)
	var v: WheelView = scene._view_of(z[0])
	var expected := v.zone_center(z[1])
	scene.confirm_selection()
	var f: Dictionary = scene.fx_layer.last_flight("exhaust")
	if f.is_empty():
		f = scene.fx_layer.last_flight("play")
	assert_false(f.is_empty(), "the card flies")
	assert_eq(f["to"], expected, "onto the zone the action used")
	scene.skip_motion()
	assert_false(scene.fx_layer.busy(), "the skip lands it")


func test_the_hand_keeps_a_gap_while_a_card_flies() -> void:
	var scene := await _combat()
	_live()
	var s: CombatState = scene.engine.state()
	var i := _playable(scene)
	if i + 1 >= s.hand.size():
		pass_test("no card right of the played one")
		return
	var right: ZineCard = scene._card_node(i + 1)
	var x_before := right.get_global_rect().position.x
	var s_before: float = scene._hand_scale
	scene.select_card(i)
	if scene.selecting >= 0:
		scene.confirm_selection()
	await _frames(2)
	assert_not_null(scene._gap, "the played card's slot stays open")
	var moved: ZineCard = scene._card_node(i)  # the old i + 1 took index i
	assert_not_null(moved, "the next card")
	assert_almost_eq(moved.get_global_rect().position.x, x_before, 0.5, "the card right of it didn't move under the cursor")
	assert_almost_eq(scene._hand_scale, s_before, 0.001, "the hand keeps its scale")
	scene.skip_motion()
	await _frames(2)
	assert_null(scene._gap, "the gap is gone at the end state")


func test_hover_lifts_and_tilts_the_card_to_zero() -> void:
	var scene := await _combat()
	var card: ZineCard = scene._card_node(0)
	card.focus_entered.emit()
	assert_eq(card.lift, Motion.amplitude(&"card_hover"), "hover lifts it (end state at once headless)")
	assert_eq(card.rotation_degrees, 0.0, "tilted to 0")
	card.focus_exited.emit()
	assert_eq(card.lift, 0.0, "it settles back")
	assert_eq(card.rotation_degrees, card.rest_tilt, "to its resting tilt")


func test_the_drag_ghost_trails_the_cursor_and_catches_up() -> void:
	var card := ZineCard.new("TEST", 1, "x", 0)
	card.size = card.custom_minimum_size
	var ghost := DragGhost.new(card)
	add_child_autofree(ghost)
	ghost.position = Vector2(100, 100)
	ghost.step(1.0 / 30.0)
	assert_eq(card.position, -card.size * 0.5, "not live: it sits on the cursor")
	_live()
	ghost.position = Vector2(400, 100)
	ghost.step(1.0 / 30.0)
	assert_true(card.position.x < -card.size.x * 0.5 - 1.0, "live: it lags behind the cursor")
	assert_true(card.rotation != 0.0, "and tilts with the move")
	for k in 60:
		ghost.step(1.0 / 30.0)
	assert_almost_eq(card.position.x, -card.size.x * 0.5, 0.5, "it catches up")
	assert_almost_eq(card.rotation, 0.0, 0.01, "and straightens")
	assert_almost_eq(card.modulate.a, Motion.amplitude(&"drag_ghost_follow"), 0.001, "ghost alpha from the table")


func test_aiming_pulses_the_zones_and_blinks_the_ram_cost() -> void:
	var scene := await _combat()
	_live()
	var i := _multi(scene)
	assert_true(i >= 0, "a card with several targets")
	scene.select_card(i)
	var pulsing := false
	for v in scene._views():
		if not (v as WheelView).valid_zones.is_empty():
			pulsing = pulsing or (v as WheelView)._tweens.has(&"zones")
	assert_true(pulsing, "the valid zones pulse")
	assert_true(scene.ram_note.aiming, "the RAM cost blinks")
	assert_true(scene.fx_layer.reticle_visible, "a target reticle shows")
	var before: Vector2 = scene._aim_target
	scene.step_selection(1)
	assert_ne(scene._aim_target, before, "keys move the reticle to the next zone")
	scene.cancel_selection()
	for v in scene._views():
		assert_eq((v as WheelView).zone_pulse, 1.0, "the pulse stops")
	assert_false(scene.ram_note.aiming, "the blink stops")
	assert_false(scene.fx_layer.reticle_visible, "the reticle goes")


func test_ram_chips_drain_with_a_tick_and_settle_on_the_state() -> void:
	var scene := await _combat()
	_live()
	var bar: RamBar = scene.ram_note
	bar.set_ram(bar.ram, bar.max_ram)
	var before := bar.ram
	scene.play_card(_playable(scene))
	var after: int = scene.engine.state().ram
	assert_eq(bar.ram, after, "the number is the state at once")
	if after != before:
		assert_eq(bar.shown_ram, before, "the chips tick from where they were")
	await get_tree().create_timer(Motion.seconds(&"ram_tick") * (absi(before - after) + 2)).timeout
	assert_eq(bar.shown_ram, after, "and settle on the state")


func test_new_cards_deal_in_from_the_deck_pile() -> void:
	var scene := await _combat()
	_live()
	scene._deal_hand(0)
	var any := false
	for c in scene._hand_box.get_children():
		if c is ZineCard and (c as ZineCard).draw_offset != Vector2.ZERO:
			any = true
	assert_true(any, "cards start at the pile")
	scene.skip_motion()
	for c in scene._hand_box.get_children():
		assert_eq((c as ZineCard).draw_offset, Vector2.ZERO, "the skip deals them home")
		assert_eq((c as ZineCard).modulate.a, 1.0, "shown")


func test_no_layout_violation_at_the_end_state_after_card_motion() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"collections_agent", scale)
		_live()
		scene.play_card(_playable(scene))
		scene.skip_motion()
		await _frames(3)
		assert_eq(scene.layout_violations(), [] as Array[String], "scale %.1f" % scale)
		Motion.force_live = false


func test_card_motion_never_changes_game_state() -> void:
	var scene := await _combat()
	_live()
	var i := _multi(scene)
	scene.select_card(i)
	scene.step_selection(1)
	var sig := _signature(scene)
	scene._cancel_drag(i, Vector2(600, 300))
	scene._deal_hand(0)
	scene.ram_note.hold(0)
	scene.ram_note.play_refill()
	await get_tree().create_timer(0.3).timeout
	scene.skip_motion()
	assert_eq(_signature(scene), sig, "targeting and card motion left the state as it was")
