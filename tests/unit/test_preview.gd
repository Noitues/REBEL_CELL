extends GutTest
## Preview equals actual for 500 random seeded turns (M1 acceptance). Every player
## action is previewed then applied; the End Turn preview is compared with the real
## resolved state. Real Breaker content against the three Solace enemies.

const TURNS := 500
const ENEMIES: Array[StringName] = [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


## A random legal action for this state, or null to end the turn.
func _random_action(session: CombatSession, choice: RandomNumberGenerator) -> CombatAction:
	var s := session.state
	var candidates: Array[CombatAction] = []
	var enemies := s.living_enemies(true)
	for i in s.hand.size():
		for wheel_id in [&"player", s.target_id]:
			var a := CombatAction.play_card(i, wheel_id)
			a.direction = 1 if choice.randi_range(0, 1) == 0 else -1
			if session.resolver.validate_action(s, a) == "":
				candidates.append(a)
	for c in [s.player] + enemies:
		for dir in [1, -1]:
			var n := CombatAction.nudge(c.id, dir, RC.RingScope.OUTER)
			if session.resolver.validate_action(s, n) == "":
				candidates.append(n)
	if s.player.wheel.has_inner_ring():
		candidates.append(CombatAction.nudge(&"player", 1, RC.RingScope.INNER))
	for e in enemies:
		candidates.append(CombatAction.target(e.id))
	if candidates.is_empty() or choice.randi_range(0, 3) == 0:
		return null
	return candidates[choice.randi_range(0, candidates.size() - 1)]


func test_preview_equals_actual_for_500_random_turns() -> void:
	var choice := CombatFixture.rng(0xC0FFEE)
	var turns := 0
	var actions := 0
	var fights := 0
	while turns < TURNS:
		var enemy: StringName = ENEMIES[fights % ENEMIES.size()]
		var session := CombatSession.start(_resolver, &"breaker", [enemy], 1000 + fights, &"rank:1")
		fights += 1
		while not session.state.is_over() and turns < TURNS:
			var action := _random_action(session, choice)
			var guard := 0
			while action != null and guard < 6:
				var predicted := session.preview(action)
				var actual := session.apply(action)
				assert_eq(predicted.error, actual.error, "same verdict for %s" % action.describe())
				assert_eq(predicted.state.state_hash(), actual.state.state_hash(),
					"preview == actual for %s (fight %d turn %d)" % [action.describe(), fights, session.state.turn])
				assert_eq(predicted.events.size(), actual.events.size(), "same events")
				actions += 1
				guard += 1
				action = _random_action(session, choice)
			var end_preview := session.preview_end_turn()
			var end_actual := session.apply(CombatAction.end_turn())
			assert_eq(end_preview.state.state_hash(), end_actual.resolved_state.state_hash(),
				"End Turn preview == resolved state (fight %d turn %d)" % [fights, turns + 1])
			turns += 1
	assert_eq(turns, TURNS)
	assert_true(actions > TURNS, "previewed %d card/nudge/target actions on top of %d end turns" % [actions, turns])
	assert_true(fights > 3, "several complete fights (%d)" % fights)


func test_preview_never_mutates_the_session() -> void:
	var session := CombatSession.start(_resolver, &"breaker", [&"compliance_officer"], 42, &"rank:1")
	var before := session.state.state_hash()
	var rng_before := session.rng.state
	session.preview(CombatAction.nudge(&"enemy_0", 1))
	session.preview(CombatAction.play_card(0, &"enemy_0"))
	session.preview_end_turn()
	session.preview(CombatAction.end_turn())
	assert_eq(session.state.state_hash(), before)
	assert_eq(session.rng.state, rng_before, "RNG untouched by previews")


func test_random_dose_target_is_previewed_exactly() -> void:
	var session := CombatSession.start(_resolver, &"breaker", [&"dosage_dispenser"], 77, &"rank:1")
	CombatFixture.land(session.state.get_combatant(&"enemy_0"), 0)
	var predicted := session.preview_end_turn()
	var actual := session.apply(CombatAction.end_turn())
	assert_eq(predicted.state.player.wheel.slice_statuses, actual.resolved_state.player.wheel.slice_statuses)
