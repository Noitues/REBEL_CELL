extends GutTest
## Determinism (M1 acceptance): replaying a recorded fight from its seed gives an
## identical state hash.

const MAX_TURNS := 40

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


## Plays a fight with scripted-random choices until it ends (or MAX_TURNS).
func _play(enemy: StringName, seed: int, choice_seed: int) -> CombatSession:
	var choice := CombatFixture.rng(choice_seed)
	var s := CombatSession.start(_resolver, &"breaker", [enemy], seed, &"rank:1")
	var turns := 0
	while not s.state.is_over() and turns < MAX_TURNS:
		for i in choice.randi_range(0, 3):
			var enemies := s.state.living_enemies(true)
			var pick := choice.randi_range(0, 2)
			var a: CombatAction
			if pick == 0 and not s.state.hand.is_empty():
				a = CombatAction.play_card(choice.randi_range(0, s.state.hand.size() - 1), [&"player", s.state.target_id][choice.randi_range(0, 1)])
				a.direction = [1, -1][choice.randi_range(0, 1)]
			elif pick == 1:
				a = CombatAction.nudge([&"player", s.state.target_id][choice.randi_range(0, 1)], [1, -1][choice.randi_range(0, 1)])
			else:
				a = CombatAction.target(enemies[choice.randi_range(0, enemies.size() - 1)].id)
			s.apply(a)  # refused actions are simply not recorded
		s.apply(CombatAction.end_turn())
		turns += 1
	return s


func test_replaying_a_recorded_fight_gives_the_same_hash() -> void:
	for enemy in [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]:
		var original := _play(enemy, 2024, 7)
		assert_true(original.history.size() > 5, "%s: recorded %d actions" % [enemy, original.history.size()])
		var replayed := CombatSession.replay(_resolver, original.setup, original.combat_seed, original.history)
		assert_eq(replayed.state_hash(), original.state_hash(), "%s replay hash" % enemy)
		assert_eq(replayed.state.turn, original.state.turn)
		assert_eq(replayed.state.outcome, original.state.outcome)
		assert_eq(replayed.rng.state, original.rng.state, "RNG consumed identically")


func test_replay_from_a_saved_history_round_trips_through_json() -> void:
	var original := _play(&"collections_agent", 31337, 3)
	var json := JSON.stringify(original.to_dict())
	var data: Dictionary = JSON.parse_string(json)
	var actions: Array[CombatAction] = []
	for ad in data["history"]:
		actions.append(CombatAction.from_dict(ad))
	var replayed := CombatSession.replay(_resolver, data["setup"], int(String(data["seed"])), actions)
	assert_eq(replayed.state_hash(), original.state_hash())


func test_different_seeds_diverge() -> void:
	var a := _play(&"compliance_officer", 1, 7)
	var b := _play(&"compliance_officer", 2, 7)
	assert_ne(a.state_hash(), b.state_hash())


func test_fights_end_within_the_turn_cap() -> void:
	for enemy in [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]:
		var s := _play(enemy, 555, 9)
		assert_true(s.state.is_over(), "%s fight reached an outcome in %d turns" % [enemy, s.state.turn])
