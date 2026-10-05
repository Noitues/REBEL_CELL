extends GutTest
## Horizontal pass 22, combat (GAP_ANALYSIS H22 1-6, 8, 13): the HP number is the HP now and
## the forecast a separate NEXT plate; satellites dock outside the slice values, are aimed
## before the arrows and show their own landing; the wheel keeps most of its size at big
## text; the tutorial teaches the nudge switches; odds in words; aim order follows the
## screen; the ring switch skips wheels without an inner ring.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_pass22"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(false)
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


func test_satellites_dock_outside_the_values_and_are_aimed_before_the_arrows() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"collections_agent", scale)
		var host: WheelView = scene._enemy_views.values()[0]
		assert_false(host.satellites.is_empty(), "the drone is docked")
		for rot in 30:
			host.combatant.wheel.rotation = rot
			for sat in host.satellites:
				var sp := host._satellite_pos(sat)
				var dist := sp.distance_to(host.global_center())
				assert_true(dist >= host._radius() + WheelView.VALUE_OUT + WheelView._fs(WheelView.VALUE_FONT_SIZE) * 0.5, "past the values at %.1f" % scale)
				assert_eq(String(host.zone_at(sp).get("kind", "")), "satellite", "the drone wins its spot over any arrow (rot %d, %.1f)" % [rot, scale])


func test_a_satellite_shows_where_its_own_needle_lands() -> void:
	var scene := await _combat()
	var host: WheelView = scene._enemy_views.values()[0]
	for sat in host.satellites:
		assert_true(host.satellite_landings.has(sat.id), "its landing is known")
		var tip := host._get_tooltip(host._satellite_pos(sat) - host.global_position)
		assert_string_contains(tip, "lands on", "and told on hover")


func test_the_hp_number_is_now_and_the_forecast_is_separate() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	# The number drawn is the current HP; a forecast lives in outcome["hp_after"] only.
	assert_eq(int(v.outcome.get("hp_after", v.combatant.hp)) <= v.combatant.max_hp, true)
	scene.end_turn()
	await _frames(1)
	assert_string_contains(v.last_turn, "LAST TURN")


func test_the_wheel_keeps_most_of_its_size_at_big_text() -> void:
	var small := await _combat(&"compliance_officer", 1.0)
	var r1: float = small._player_view._radius()
	var big := await _combat(&"compliance_officer", Settings.TEXT_SCALE_MAX)
	var r16: float = big._player_view._radius()
	assert_true(r16 >= r1 * WheelView.BIG_TEXT_RADIUS_KEEP - 1.0, "radius %.0f at TEXT_SCALE_MAX vs %.0f at 1.0" % [r16, r1])
	assert_eq(big.layout_violations(), [], "still nothing over a wheel")


func test_the_tutorial_teaches_the_nudge_switches_and_the_turn_lines() -> void:
	var nudge := TutorialOverlay.step_text(1)
	assert_string_contains(nudge, Settings.key_text(&"toggle_nudge_wheel"))
	assert_string_contains(nudge, Settings.key_text(&"toggle_ring"))
	var wheel := TutorialOverlay.step_text(0)
	assert_string_contains(wheel, "LAST TURN")
	assert_string_contains(wheel, "NEXT")
	assert_false(wheel.contains("BLK"))


func test_odds_are_in_words() -> void:
	var scene := await _combat()
	var s: CombatState = scene.engine.state()
	var text: String = scene.odds_text(s.player)
	for w in Palette.SLICE_NAMES.values():
		if not Palette.SLICE_WORDS.values().has(w):
			assert_false((" " + w + " ") in (" " + text.replace("%", " ") + " "), "no %s abbreviation in %s" % [w, text])


func test_aim_order_follows_the_screen() -> void:
	var scene := await _combat()
	var s: CombatState = scene.engine.state()
	s.hand = [&"jolt"]
	s.ram = s.max_ram
	var none: Array[Dictionary] = []
	scene.engine.state_changed.emit(s, none)
	scene.select_card(0)
	var xs: Array[float] = []
	for a in scene.selection_options():
		var z: Array = scene._zone_of(a)
		xs.append((scene._view_of(z[0]) as WheelView).zone_center(z[1]).x)
	for i in range(1, xs.size()):
		assert_true(xs[i] >= xs[i - 1] - 0.5, "left to right: %s" % [xs])
	scene.cancel_selection()


func test_the_ring_switch_skips_wheels_without_an_inner_ring() -> void:
	var scene := await _combat()
	var target: CombatantState = scene.engine.state().get_combatant(scene.engine.state().target_id)
	scene.toggle_nudge_wheel()
	if not target.wheel.has_inner_ring():
		scene.toggle_ring()
		assert_eq(scene._nudge_ring_option.selected, 0, "no inner ring to switch to")
		assert_string_contains(scene.toast.text(), "inner ring", "and a toast says why")
