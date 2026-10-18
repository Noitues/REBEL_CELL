extends GutTest
## Plan 2 N21 (rulings Q16, Q31): resistance goes to 0 at the end of every turn and is regained
## at the start of the next (+ enrage resistance_step x step, + a change carried from RESOLVE).
## After the refresh a nudge on the enemy wheel is absorbed (GDD 2.5), Flip / Respin stay
## blocked while it lasts, and ICE / Heat "+1 resistance", Ghost's free nudge, Strip, Jam and
## Hub Breach behave as before.

var _flip: CardData
var _respin: CardData
var _strip: CardData
var _jam: CardData
var _breach: CardData


func before_each() -> void:
	_flip = CombatFixture.card(&"n21_flip", [CombatFixture.effect(RC.EffectType.FLIP, RC.EffectTarget.TARGET_WHEEL, 0, RC.RingScope.WHOLE_WHEEL)])
	_respin = CombatFixture.card(&"n21_respin", [CombatFixture.effect(RC.EffectType.RESPIN, RC.EffectTarget.TARGET_WHEEL, 0, RC.RingScope.WHOLE_WHEEL)])
	_strip = CombatFixture.card(&"n21_strip", [CombatFixture.effect(RC.EffectType.MODIFY_RESISTANCE, RC.EffectTarget.TARGET_WHEEL, -2)])
	_jam = CombatFixture.card(&"n21_jam", [CombatFixture.effect(RC.EffectType.NUDGE, RC.EffectTarget.TARGET_WHEEL, 1, RC.RingScope.OUTER, 0.0)])
	_breach = CombatFixture.card(&"n21_breach", [CombatFixture.effect(RC.EffectType.HUB_BREACH, RC.EffectTarget.TARGET_WHEEL, 1)])


func _session(enemy: EnemyData, player_hub: HubCoreData = null, overrides: Dictionary = {}) -> CombatSession:
	var deck: Array[CardData] = [_flip, _respin, _strip, _jam, _breach]
	var cls := CombatFixture.operative_class(&"n21_op", 60, CombatFixture.null_wheel(0, player_hub), deck)
	var resolver := CombatFixture.resolver([cls, enemy])
	return CombatSession.start(resolver, cls.id, [enemy.id], 21, &"", 0, overrides)


func _normal(passive: int, hub: HubCoreData = null) -> EnemyData:
	var e := PhaseFixture.enemy(&"n21_normal", 999, [], RC.EnemyClass.NORMAL, CombatFixture.null_wheel(passive, hub))
	e.phases.clear()
	return e


func _enemy(s: CombatSession) -> CombatantState:
	return s.state.get_combatant(&"enemy_0")


func _card(s: CombatSession, id: StringName) -> int:
	return s.state.hand.find(id)


func test_end_of_turn_zeroes_and_start_of_turn_regains() -> void:
	var s := _session(_normal(2))
	assert_eq(_enemy(s).resistance, 2)
	assert_eq(_enemy(s).resistance_gain, 2, "the first turn's refresh is marked too")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(_enemy(s).resistance, 1)
	var rng_state := s.rng.state
	var events: Array[Dictionary] = []
	var copy := s.state.duplicate_state()
	s.resolver.end_turn(copy, events)
	assert_eq(copy.get_combatant(&"enemy_0").resistance, 0, "end of turn: 0")
	assert_eq(copy.get_combatant(&"enemy_0").resistance_gain, 0, "the mark goes with it")
	assert_eq(s.rng.state, rng_state, "no RNG read")
	var r := s.apply(CombatAction.end_turn())
	assert_eq(_enemy(s).resistance, 2, "start of turn: full value again")
	assert_eq(_enemy(s).resistance_gain, 2)
	var refresh := CombatFixture.events_of(r, "resistance_refresh")
	assert_eq(refresh.size(), 1)
	assert_eq(int(refresh[0]["amount"]), 2)


func test_unspent_resistance_does_not_stack_across_turns() -> void:
	var s := _session(_normal(2))
	s.apply(CombatAction.end_turn())
	s.apply(CombatAction.end_turn())
	assert_eq(_enemy(s).resistance, 2, "zeroed, then refilled: never 4")


func test_enrage_resistance_step_adds_at_the_refresh() -> void:
	var data := EnrageFixture.enemy(&"n21_boss", RC.EnemyClass.BOSS, 1, 999, EnrageFixture.enrage(2, 1, 0, 1))
	data.wheel.passive_resistance = 5
	var s := EnrageFixture.session(data)
	assert_eq(_enemy(s).resistance, 5, "turn 1: step 0")
	s.apply(CombatAction.end_turn())
	assert_eq(_enemy(s).enrage_step, 1)
	assert_eq(_enemy(s).resistance, 6, "turn 2: 5 + 1 x step 1")
	assert_eq(_enemy(s).resistance_gain, 6)
	s.apply(CombatAction.end_turn())
	assert_eq(_enemy(s).resistance, 7, "turn 3: 5 + 1 x step 2 (enrage may exceed the class range)")


func test_a_nudge_after_the_refresh_is_absorbed() -> void:
	var s := _session(_normal(1))
	s.apply(CombatAction.end_turn())
	var rot := _enemy(s).wheel.rotation
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(_enemy(s).wheel.rotation, rot, "absorbed by the refreshed resistance")
	assert_eq(_enemy(s).resistance, 0)
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(_enemy(s).wheel.rotation, rot + 1)


func test_flip_and_respin_stay_blocked_while_resistance_lasts() -> void:
	var s := _session(_normal(1))
	s.apply(CombatAction.end_turn())
	var r := s.apply(CombatAction.play_card(_card(s, &"n21_flip"), &"enemy_0"))
	assert_false(r.ok(), "flip refused after the refresh")
	r = s.apply(CombatAction.play_card(_card(s, &"n21_respin"), &"enemy_0"))
	assert_false(r.ok(), "respin refused after the refresh")


func test_ice_extra_resistance_stacks_above_the_range() -> void:
	var s := _session(_normal(2), null, {"enemy_resistance": 1})
	assert_eq(_enemy(s).resistance, 3, "2 + ICE 1")
	s.apply(CombatAction.end_turn())
	assert_eq(_enemy(s).resistance, 3, "regained each turn with the ICE bonus")


func test_ghost_free_nudge_ignores_the_refreshed_resistance() -> void:
	var ghost := CombatFixture.hub(&"n21_ghostlike")
	ghost.free_resistance_nudges = 1
	var s := _session(_normal(2), ghost)
	s.apply(CombatAction.end_turn())
	var rot := _enemy(s).wheel.rotation
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(_enemy(s).wheel.rotation, rot + 1, "first nudge slips past")
	assert_eq(_enemy(s).resistance, 2, "and leaves resistance alone")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(_enemy(s).resistance, 1, "the second is absorbed")


func test_strip_lasts_for_the_turn_only() -> void:
	var s := _session(_normal(2))
	s.apply(CombatAction.end_turn())
	s.apply(CombatAction.play_card(_card(s, &"n21_strip"), &"enemy_0"))
	assert_eq(_enemy(s).resistance, 0)
	s.apply(CombatAction.end_turn())
	assert_eq(_enemy(s).resistance, 2, "full again next turn")


func test_jam_ignores_resistance() -> void:
	var s := _session(_normal(2))
	s.apply(CombatAction.end_turn())
	var rot := _enemy(s).wheel.rotation
	var r := s.apply(CombatAction.play_card(_card(s, &"n21_jam"), &"enemy_0"))
	assert_true(r.ok(), r.error)
	assert_eq(_enemy(s).resistance, 2, "Jam spends none")
	assert_ne(_enemy(s).wheel.rotation, rot, "and moves the wheel")


func test_hub_breach_removes_hub_resistance_until_the_hub_is_back() -> void:
	var s := _session(_normal(0, CombatFixture.hub(&"n21_lock", 2)))
	assert_eq(_enemy(s).resistance, 2)
	s.apply(CombatAction.play_card(_card(s, &"n21_breach"), &"enemy_0"))
	assert_eq(_enemy(s).resistance, 0, "breach takes the hub's 2 at once")
	s.apply(CombatAction.end_turn())
	assert_eq(_enemy(s).resistance, 2, "the breach expired at this start of turn: the hub's 2 is regained")


func test_a_resolve_change_still_carries_into_the_refresh() -> void:
	var s := _session(_normal(2))
	# What a RESOLVE-time change leaves behind (Ghost Core strip on a Perfect: H13); the full
	# path is test_horizontal_pass13's strip test.
	_enemy(s).resistance_carry = -1
	s.apply(CombatAction.end_turn())
	assert_eq(_enemy(s).resistance, 1, "full 2 + carried -1, from 0")
	assert_eq(_enemy(s).resistance_gain, 1)
	assert_eq(_enemy(s).resistance_carry, 0, "the carry is spent")
	s.apply(CombatAction.end_turn())
	assert_eq(_enemy(s).resistance, 2, "full a turn later")


func test_zero_gain_writes_no_mark_and_no_event() -> void:
	var s := _session(_normal(0))
	assert_eq(_enemy(s).resistance_gain, 0)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "resistance_refresh").size(), 0)
