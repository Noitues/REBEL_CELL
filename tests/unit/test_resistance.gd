extends GutTest
## Spin resistance (GDD 2.5, M1 acceptance): nudges and spins are absorbed tick for
## tick; Flip and Respin are blocked while resistance > 0; passive resistance restores
## each player turn; Hub Breach disables Hub resistance for one turn.

var _resolver: CombatResolver
var _cls: ClassData
var _spin4: CardData
var _flip: CardData
var _respin: CardData
var _breach: CardData
var _strip: CardData


func before_each() -> void:
	_spin4 = CombatFixture.card(&"t_spin4", [CombatFixture.effect(RC.EffectType.SPIN, RC.EffectTarget.TARGET_WHEEL, 4, RC.RingScope.WHOLE_WHEEL)])
	_flip = CombatFixture.card(&"t_flip", [CombatFixture.effect(RC.EffectType.FLIP, RC.EffectTarget.TARGET_WHEEL, 0, RC.RingScope.WHOLE_WHEEL)])
	_respin = CombatFixture.card(&"t_respin", [CombatFixture.effect(RC.EffectType.RESPIN, RC.EffectTarget.TARGET_WHEEL, 0, RC.RingScope.WHOLE_WHEEL)])
	_breach = CombatFixture.card(&"t_breach", [CombatFixture.effect(RC.EffectType.HUB_BREACH, RC.EffectTarget.TARGET_WHEEL, 1)])
	_strip = CombatFixture.card(&"t_strip", [CombatFixture.effect(RC.EffectType.MODIFY_RESISTANCE, RC.EffectTarget.TARGET_WHEEL, -2)])
	var deck: Array[CardData] = [_spin4, _flip, _respin, _breach, _strip]
	_cls = CombatFixture.operative_class(&"t_class", 60, CombatFixture.miss_wheel(), deck)


func _session(enemy: EnemyData) -> CombatSession:
	_resolver = CombatFixture.resolver([_cls, enemy])
	return CombatSession.start(_resolver, _cls.id, [enemy.id], 7)


func _hand_index(session: CombatSession, card_id: StringName) -> int:
	return session.state.hand.find(card_id)


func test_nudges_are_absorbed_tick_for_tick() -> void:
	var s := _session(CombatFixture.enemy(&"t_resist3", 50, CombatFixture.miss_wheel(3)))
	var enemy := s.state.get_combatant(&"enemy_0")
	assert_eq(enemy.resistance, 3)
	var rotation_before := enemy.wheel.rotation
	for i in 3:
		assert_true(s.apply(CombatAction.nudge(&"enemy_0", 1)).ok(), "nudge %d accepted" % i)
	enemy = s.state.get_combatant(&"enemy_0")
	assert_eq(enemy.resistance, 0, "three nudges eat three resistance")
	assert_eq(enemy.wheel.rotation, rotation_before, "wheel did not move while resisting")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.rotation, rotation_before + 1, "fourth nudge moves the wheel")


func test_extra_nudges_cost_ram() -> void:
	var s := _session(CombatFixture.enemy(&"t_resist0", 50, CombatFixture.miss_wheel()))
	var ram := s.state.ram
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(s.state.ram, ram, "first nudge is free")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(s.state.ram, ram - CombatFixture.config().extra_nudge_ram_cost, "second nudge costs RAM")


func test_spin_loses_its_first_r_ticks_to_resistance() -> void:
	var s := _session(CombatFixture.enemy(&"t_resist3", 50, CombatFixture.miss_wheel(3)))
	var before := s.state.get_combatant(&"enemy_0").wheel.rotation
	var r := s.apply(CombatAction.play_card(_hand_index(s, &"t_spin4"), &"enemy_0"))
	assert_true(r.ok(), r.error)
	var enemy := s.state.get_combatant(&"enemy_0")
	assert_eq(enemy.resistance, 0)
	assert_eq(enemy.wheel.rotation, before + 1, "spin 4 minus 3 absorbed = 1 tick")


func test_flip_is_blocked_entirely_while_resistance_remains() -> void:
	var s := _session(CombatFixture.enemy(&"t_resist1", 50, CombatFixture.miss_wheel(1)))
	var r := s.apply(CombatAction.play_card(_hand_index(s, &"t_flip"), &"enemy_0"))
	assert_false(r.ok(), "flip refused")
	assert_string_contains(r.error, "FLIP blocked")
	var tick_before := s.state.get_combatant(&"enemy_0").wheel.tick_at(0)
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 0)
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.tick_at(0), tick_before, "absorbed nudge left the tick alone")
	r = s.apply(CombatAction.play_card(_hand_index(s, &"t_flip"), &"enemy_0"))
	assert_true(r.ok(), r.error)
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.tick_at(0), WheelMath.mirror_tick(tick_before), "flip works once resistance is gone")


func test_respin_is_blocked_while_resistance_remains() -> void:
	var s := _session(CombatFixture.enemy(&"t_resist2", 50, CombatFixture.miss_wheel(2)))
	var r := s.apply(CombatAction.play_card(_hand_index(s, &"t_respin"), &"enemy_0"))
	assert_false(r.ok())
	assert_string_contains(r.error, "RESPIN blocked")
	s.apply(CombatAction.play_card(_hand_index(s, &"t_strip"), &"enemy_0"))
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 0, "Strip removes 2")
	r = s.apply(CombatAction.play_card(_hand_index(s, &"t_respin"), &"enemy_0"))
	assert_true(r.ok(), r.error)
	assert_eq(CombatFixture.events_of(r, "respin").size(), 1)


func test_passive_resistance_restores_each_player_turn() -> void:
	var s := _session(CombatFixture.enemy(&"t_resist3", 50, CombatFixture.miss_wheel(3)))
	for i in 3:
		s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 0)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.turn, 2)
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 3, "back to full at the next player turn")


func test_hub_breach_disables_hub_resistance_for_one_turn() -> void:
	var lock := CombatFixture.hub(&"t_lock", 3)
	var s := _session(CombatFixture.enemy(&"t_hubbed", 50, CombatFixture.miss_wheel(1, lock)))
	var enemy := s.state.get_combatant(&"enemy_0")
	assert_eq(enemy.resistance, 4, "passive 1 + hub 3")
	var r := s.apply(CombatAction.play_card(_hand_index(s, &"t_breach"), &"enemy_0"))
	assert_true(r.ok(), r.error)
	enemy = s.state.get_combatant(&"enemy_0")
	assert_true(enemy.is_hub_breached())
	assert_eq(enemy.resistance, 1, "only the passive point remains")
	assert_false(s.apply(CombatAction.play_card(_hand_index(s, &"t_flip"), &"enemy_0")).ok(), "still 1 resistance: flip blocked")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_true(s.apply(CombatAction.play_card(_hand_index(s, &"t_flip"), &"enemy_0")).ok(), "flip goes through after the passive point is spent")
	s.apply(CombatAction.end_turn())
	enemy = s.state.get_combatant(&"enemy_0")
	assert_false(enemy.is_hub_breached(), "breach lasted one turn")
	assert_eq(enemy.resistance, 4, "hub resistance is back next turn")


func test_compliance_officer_content_starts_with_hub_resistance_3() -> void:
	var resolver := CombatFixture.resolver()
	var s := CombatSession.start(resolver, &"breaker", [&"compliance_officer"], 1)
	var officer := s.state.get_combatant(&"enemy_0")
	assert_eq(officer.hub_resistance, 3)
	assert_eq(officer.resistance, 3)
