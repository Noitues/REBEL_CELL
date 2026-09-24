extends GutTest
## A full fight against each of the three enemies is playable in the scene (M1
## acceptance). Drives the real scene through its public methods.

const SCENE := "res://scenes/combat/combat_scene.tscn"
const MAX_TURNS := 60

var _scene: Control


func before_each() -> void:
	_scene = add_child_autofree(load(SCENE).instantiate())


func _play_out(enemy_id: StringName, seed: int) -> CombatState:
	_scene.start_fight(enemy_id, seed)
	var engine: CombatEngine = _scene.engine
	var turns := 0
	while not engine.state().is_over() and turns < MAX_TURNS:
		# Spend the free nudge and play whatever is affordable, like a hurried player.
		_scene.nudge(1)
		for i in range(engine.state().hand.size() - 1, -1, -1):
			if i < engine.state().hand.size():
				_scene.play_card(i)
		_scene.end_turn()
		turns += 1
	return engine.state()


func test_scene_starts_a_fight_on_ready() -> void:
	var engine: CombatEngine = _scene.engine
	assert_true(engine.has_fight())
	assert_eq(engine.state().turn, 1)
	assert_eq(engine.state().hand.size(), 5)


func test_full_fight_against_each_enemy_reaches_an_outcome() -> void:
	for enemy_id in [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]:
		var state := _play_out(enemy_id, 12)
		assert_true(state.is_over(), "%s: fight ended (turn %d)" % [enemy_id, state.turn])
		assert_true(state.turn < MAX_TURNS, "%s: ended before the cap" % enemy_id)
		assert_eq(state.enemies[0].source_id, enemy_id)


func test_scene_controls_drive_the_engine() -> void:
	var engine: CombatEngine = _scene.engine
	var before := engine.state().state_hash()
	_scene.nudge(1)
	assert_ne(engine.state().state_hash(), before, "nudge changed the state")
	assert_true(engine.can_rewind())
	_scene.rewind()
	assert_eq(engine.state().state_hash(), before, "rewind restored it")
	_scene.cycle_target()
	assert_eq(engine.state().target_id, engine.state().living_enemies(true)[1 % engine.state().living_enemies(true).size()].id)
	var hand := engine.state().hand.size()
	_scene.play_card(0)
	assert_eq(engine.state().hand.size(), hand - 1, "card left the hand")
	var turn := engine.state().turn
	_scene.end_turn()
	assert_eq(engine.state().turn, turn + 1)
	assert_false(engine.can_rewind(), "start-of-turn respin is a checkpoint")


func test_refused_actions_are_reported_not_applied() -> void:
	var engine: CombatEngine = _scene.engine
	watch_signals(engine)
	var before := engine.state().state_hash()
	engine.submit(CombatAction.play_card(99))
	assert_signal_emitted(engine, "action_refused")
	assert_eq(engine.state().state_hash(), before)


func test_preview_readouts_are_available_for_every_wheel() -> void:
	var engine: CombatEngine = _scene.engine
	var state := engine.state()
	assert_eq(engine.readouts(state.player).size(), 1)
	for e in state.living_enemies(true):
		assert_true(engine.readouts(e).size() >= 1, "%s has a readout" % e.id)
	assert_not_null(engine.preview_end_turn())
