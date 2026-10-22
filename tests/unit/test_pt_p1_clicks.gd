extends GutTest
## PB-SOL-1 I1 (B-04): real pointer clicks on the player's own wheel play Jolt / Fine Tune at once.
## Posted through the viewport like a real mouse (move, press, release at the zone's centre).

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _win_size: Vector2i
var _gut_layer: CanvasLayer
var _gut_layer_was: bool = true


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_pt_p1_clicks"
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


func _click(at: Vector2, move_first: bool = true) -> void:
	if move_first:
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


func _card_center(scene: Control, i: int) -> Vector2:
	var card := scene._card_node(i) as ZineCard
	return card.get_global_transform() * card.hit_rect().get_center()


func test_clicking_a_glowing_zone_on_the_players_own_wheel_plays() -> void:
	var failures: Array[String] = []
	var tried := 0
	for card_id in [&"fine_tune", &"jolt"]:
		for live in [false, true]:
			for zone_i in 4:
				Motion.force_live = live
				var scene := await _combat([card_id] as Array[StringName])
				var view: WheelView = scene._player_view
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
				tried += 1
				var hand_before: int = scene.engine.state().hand.size()
				await _click(on_wheel[zone_i], not live)
				if scene.selecting != -1 or scene.engine.state().hand.size() != hand_before - 1:
					failures.append("%s zone %d live=%s at %s: click did not play (selecting=%d)" % [card_id, zone_i, live, on_wheel[zone_i], scene.selecting])
				scene.get_parent().queue_free()
				await _frames(1)
	print("PT-P1 own-wheel tried %d failures: %s" % [tried, failures])
	assert_gt(tried, 0, "some own-wheel zone was offered")
	assert_eq(failures, [] as Array[String], "the first click on the player's own wheel plays")


## A sticker whose gloss sweep runs (no state tween) and is then disabled with motion off must still take the
## disabled look: set_state used to call kill() on its null state tween and stop before applying it.
func test_a_vinyl_sticker_mid_sweep_still_takes_the_disabled_state() -> void:
	var v := VinylSticker.new()
	add_child_autofree(v)
	v.size = Vector2(240, 80)
	await _frames(2)
	Motion.force_live = true
	v.sweep()
	assert_true(v.sweep_running(), "the sweep runs")
	Motion.force_live = false
	v.set_state(VinylSticker.State.DISABLED)
	assert_eq(v.state, VinylSticker.State.DISABLED)
	assert_false(v.motion_running() and v._tween != null, "no state tween left")
