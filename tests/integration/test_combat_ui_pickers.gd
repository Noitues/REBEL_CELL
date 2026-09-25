extends GutTest
## Combat UI completeness (gap analysis 2.1): the slice picker plays Cleanse/Encrypt, the
## direction picker steers nudge cards, the RAM respin works from the scene, random
## effects show odds instead of rolls, right-click inspect describes a slice, and the
## revealed boss phases reach the enemy wheel view.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _scene: Control


func before_each() -> void:
	_scene = add_child_autofree(load(SCENE).instantiate())


func _state() -> CombatState:
	return _scene.engine.state()


func test_slice_picker_is_needed_for_cleanse_and_encrypt() -> void:
	_scene.engine.session.state.hand[0] = &"cleanse"
	_scene.toggle_card_target()  # cards: own
	assert_eq(_scene.selected_slot(), -1)
	var hand := _state().hand.size()
	_scene.play_card(0)
	assert_eq(_state().hand.size(), hand, "refused without a chosen slice")
	_scene.set_slot(3)
	assert_eq(_scene.selected_slot(), 3)
	_scene.play_card(0)
	assert_eq(_state().hand.size(), hand - 1, "played with slot 3 chosen")
	_scene.engine.session.state.hand[0] = &"encrypt"
	_scene.cycle_slot()
	assert_eq(_scene.selected_slot(), 4)
	_scene.play_card(0)
	assert_eq(_state().player.wheel.slice_statuses[4], RC.Status.ENCRYPTED)


func test_direction_picker_steers_nudge_cards() -> void:
	_scene.engine.session.state.hand[0] = &"fine_tune"
	_scene.toggle_card_target()  # own wheel
	_scene.set_direction(-1)
	assert_eq(_scene.selected_direction(), -1)
	var before := _state().player.wheel.rotation
	_scene.play_card(0)
	assert_eq(_state().player.wheel.rotation, before - 2)
	_scene.engine.session.state.hand[0] = &"fine_tune"
	_scene.toggle_direction()
	assert_eq(_scene.selected_direction(), 1)
	before = _state().player.wheel.rotation
	_scene.play_card(0)
	assert_eq(_state().player.wheel.rotation, before + 2)


func test_respin_from_the_scene_costs_ram_and_sets_a_checkpoint() -> void:
	var ram := _state().ram
	var rotation := _state().player.wheel.rotation
	_scene.respin()
	assert_eq(_state().ram, ram - _scene.engine.resolver.config.respin_ram_cost)
	assert_ne(_state().player.wheel.rotation, rotation)
	assert_false(_scene.engine.can_rewind(), "a random event is a checkpoint")


func test_odds_text_gives_percentages_not_rolls() -> void:
	var odds: String = _scene.odds_text(_state().player)
	assert_true(odds.begins_with("odds:"))
	assert_true(odds.contains("%"))
	assert_true(odds.contains("ATK"))
	var non_miss: String = _scene.odds_text(_state().player, true)
	assert_false(non_miss.contains("MISS"))


func test_inspect_describes_the_slice_under_the_cursor() -> void:
	await get_tree().process_frame
	var view: WheelView = _scene._player_view
	var center: Vector2 = view.wheel_rect().get_center()
	var hub_text: String = _scene.inspect_at(center)
	assert_true(hub_text.contains("Breaker"), "centre: the operative and its hub")
	# A point on the outer band straight up is the slice under the pointer.
	var band := center + Vector2(0, -view._radius())
	var text: String = _scene.inspect_at(band)
	assert_true(text.contains("slot"), text)
	var slot: int = view.slot_at_global(band)
	assert_eq(slot, _state().player.wheel.slice_at(0))
	assert_eq(_scene.inspect_at(Vector2(-500, -500)), "", "nothing there")


func test_revealed_phases_and_drones_reach_the_views() -> void:
	_scene.engine.session = CombatSession.start(_scene.engine.resolver, &"breaker", [&"renewal_engine"], 3, &"rank:1", 0,
		{"reveal_phases": true, "daemon_ids": ["botnet_seed"]})
	var no_events: Array[Dictionary] = []
	_scene.engine.state_changed.emit(_scene.engine.state(), no_events)
	var enemy_view: WheelView = _scene._enemy_views[&"enemy_0"]
	assert_eq(enemy_view.extra_lines.size(), 2, "two phases revealed by Intel")
	assert_true(enemy_view.extra_lines[0].contains("MULTIPLY"))
	assert_true(_scene.daemon_note.label.get_parsed_text().contains("Botnet Seed"))
	CombatFixture.land(_state().player, 1, 0)
	var seeded := []  # an Array: lambdas capture ints by value
	_scene.engine.state_changed.connect(func(_st, evs) -> void:
		for e in evs:
			if e.get("type", "") == "botnet_seed":
				seeded.append(e))
	_scene.end_turn()
	assert_eq(seeded.size(), 1, "one Perfect, one seed drone (H15: Daemons fire once per landing)")
	assert_eq(_scene._player_view.satellites.size(), _state().living_drones().size(), "the player wheel shows its living drones")
