extends GutTest
## Plan 2 N6 sweep (full tier): every shipped enemy with listeners plus a fixture enemy that
## hears all five triggers, bot-played over 20 seeds. Each step: preview == result, no HP
## below 0, caps never exceeded; each fight replays to the same hash.

const L = preload("res://tests/helpers/listener_fixture.gd")
const SEED_FIRST := 1000
const SEED_COUNT := 20
const MAX_STEPS := 120


func _fixture_listeners() -> Array[ListenerData]:
	return [L.listener(RC.Trigger.ON_NUDGE, [L.hit(2), L.block(1)], 2, 6),
		L.listener(RC.Trigger.ON_CARD_PLAYED, [L.block(2)]),
		L.listener(RC.Trigger.ON_RAM_SPENT, [L.hit(1)], 3),
		L.listener(RC.Trigger.ON_PERFECT, [L.hit(5, true)]),
		L.listener(RC.Trigger.ON_HIT_DEALT, [L.hit(1)], 2, 10)]


## The bot's next action: a nudge, a card or End Turn, chosen by its own RNG (not the
## combat's), kept only when legal.
func _next(s: CombatSession, bot: RandomNumberGenerator) -> CombatAction:
	var roll := bot.randi_range(0, 3)
	var wheels: Array[StringName] = [&"player"]
	for e in s.state.living_enemies(false):
		wheels.append(e.id)
	var a: CombatAction = CombatAction.end_turn()
	if roll == 0:
		a = CombatAction.nudge(wheels[bot.randi_range(0, wheels.size() - 1)], 1 if bot.randi_range(0, 1) == 0 else -1)
	elif roll == 1 and not s.state.hand.is_empty():
		a = CombatAction.play_card(bot.randi_range(0, s.state.hand.size() - 1))
	if s.resolver.validate_action(s.state, a) != "":
		a = CombatAction.end_turn()
	return a


func _sweep(s: CombatSession, seed: int, label: String) -> void:
	var bot := RandomNumberGenerator.new()
	bot.seed = seed
	var fires := 0
	for step in MAX_STEPS:
		if s.state.is_over():
			break
		var a := _next(s, bot)
		var pv := s.preview(a) if a.type != CombatAction.Type.END_TURN else null
		var pe := s.preview_end_turn() if a.type == CombatAction.Type.END_TURN else null
		var r := s.apply(a)
		if not r.ok():
			fail_test("%s seed %d step %d refused: %s" % [label, seed, step, r.error])
			return
		if pv != null and pv.state.state_hash() != r.state.state_hash():
			fail_test("%s seed %d step %d: preview != result" % [label, seed, step])
			return
		if pe != null and pe.state.state_hash() != r.resolved_state.state_hash():
			fail_test("%s seed %d step %d: End Turn preview != resolved" % [label, seed, step])
			return
		fires += L.fires(r).size()
		for c in [s.state.player] + s.state.enemies:
			if c.hp < 0:
				fail_test("%s seed %d: %s HP %d" % [label, seed, c.id, c.hp])
				return
			for key in c.listener_fires_turn:
				if int(c.listener_fires_turn[key]) > int(c.listener_fires_combat.get(key, 0)):
					fail_test("%s: turn count above combat count" % label)
					return
	var again := CombatSession.replay(s.resolver, s.setup, seed, s.history)
	assert_eq(again.state.state_hash(), s.state.state_hash(), "%s seed %d replays" % [label, seed])
	gut.p("%s seed %d: %d listener fires" % [label, seed, fires])


func test_fixture_listener_enemy_fights_hold_invariants() -> void:
	for seed in range(SEED_FIRST, SEED_FIRST + SEED_COUNT):
		_sweep(L.session(_fixture_listeners(), {"seed": seed, "factor": 1.69}), seed, "fixture")


func test_every_shipped_listener_enemy_fight_holds_invariants() -> void:
	var resolver := CombatFixture.resolver()
	var ids: Array = []
	for id in ContentRegistry.all_ids():
		var e := ContentRegistry.get_content(id) as EnemyData
		if e != null and e.listener_errors().is_empty() and not resolver.enemy_listeners(_probe(e)).is_empty():
			ids.append(id)
	IdSort.sort_ids(ids)
	gut.p("shipped enemies with listeners: %s" % str(ids))
	for id in ids:
		for seed in range(SEED_FIRST, SEED_FIRST + SEED_COUNT):
			var enemies: Array[StringName] = [StringName(id)]
			_sweep(CombatSession.start(resolver, &"breaker", enemies, seed), seed, String(id))
	pass_test("swept %d shipped listener enemies" % ids.size())


## A bare combatant of `e` (for enemy_listeners): its id and Hub only.
func _probe(e: EnemyData) -> CombatantState:
	var c := CombatantState.new()
	c.source_id = e.id
	c.wheel = WheelState.new()
	if e.wheel != null and e.wheel.hub != null:
		c.wheel.hub_id = e.wheel.hub.id
	return c
