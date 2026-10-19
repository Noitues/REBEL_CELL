extends GutTest
## N9 (rulings Q36, Q37): CORRUPTED is a RAM cost. Doubled while a needle of the operative's
## wheel touches a CORRUPTED slice (0 stays 0, once per action); halved (rounded up) to
## manipulate an enemy wheel whose needle touches one; no damage, no drain. The forecast is
## the resolver's own function.

var _cfg: CampaignConfigData
var _atk: SliceData
var _null: SliceData
var _cls: ClassData
var _enemy: EnemyData
var _cost1: CardData
var _cost0: CardData
var _cost3: CardData
var _push1: CardData


func before_each() -> void:
	_cfg = CombatFixture.config()
	_atk = CombatFixture.slice(&"n9c_atk", RC.SliceType.SHIM, 4)
	_null = CombatFixture.slice(&"n9c_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var block := CombatFixture.effect(RC.EffectType.GAIN_BLOCK, RC.EffectTarget.SELF, 1)
	var effects: Array[EffectData] = [block]
	_cost1 = CombatFixture.card(&"n9c_c1", effects, 1, RC.WheelTarget.OWN)
	_cost0 = CombatFixture.card(&"n9c_c0", effects, 0, RC.WheelTarget.OWN)
	_cost3 = CombatFixture.card(&"n9c_c3", effects, 3, RC.WheelTarget.OWN)
	var push: Array[EffectData] = [CombatFixture.effect(RC.EffectType.NUDGE, RC.EffectTarget.TARGET_WHEEL, 1)]
	_push1 = CombatFixture.card(&"n9c_push", push, 1, RC.WheelTarget.ENEMY)
	var deck: Array[CardData] = [_cost1, _cost0, _cost3, _push1]
	_cls = CombatFixture.operative_class(&"n9c_class", 60, CombatFixture.wheel([_atk, _atk, _atk, _atk, _atk, _null]), deck)
	_enemy = CombatFixture.enemy(&"n9c_enemy", 500, CombatFixture.wheel([_atk, _atk, _atk, _atk, _atk, _null]))


func _session(majors: int = 0) -> CombatSession:
	var s := CombatSession.start(CombatFixture.resolver([_cls, _enemy]), _cls.id, [_enemy.id], 5, &"", majors)
	CombatFixture.land(s.state.player, 1)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 1)
	return s


func _hand(s: CombatSession, id: StringName) -> int:
	return s.state.hand.find(id)


func _spent(s: CombatSession, action: CombatAction) -> int:
	var before := s.state.ram
	var r := s.apply(action)
	assert_true(r.ok(), r.error)
	return before - s.state.ram


func _corrupt_player(s: CombatSession, slot: int = 1) -> void:
	s.state.player.wheel.set_status(slot, RC.Status.CORRUPTED, 1)


func test_card_costs_double_under_a_corrupted_needle() -> void:
	var clean := _session()
	assert_eq(_spent(clean, CombatAction.play_card(_hand(clean, &"n9c_c1"))), 1)
	var s := _session()
	_corrupt_player(s)
	s.state.ram = 12
	assert_eq(_spent(s, CombatAction.play_card(_hand(s, &"n9c_c1"))), 2)
	assert_eq(_spent(s, CombatAction.play_card(_hand(s, &"n9c_c3"))), 6)


func test_zero_cost_stays_zero_and_free_nudge_stays_free() -> void:
	var s := _session()
	_corrupt_player(s)
	assert_eq(_spent(s, CombatAction.play_card(_hand(s, &"n9c_c0"))), 0)
	assert_eq(_spent(s, CombatAction.nudge(&"enemy_0", 1)), 0, "the free nudge (ruling Q36: 2 x 0)")


func test_paid_nudge_doubles_and_is_judged_before_the_move() -> void:
	var s := _session()
	_corrupt_player(s)
	s.apply(CombatAction.nudge(&"enemy_0", 1))  # the free one
	var action := CombatAction.nudge(&"player", 1)  # moves the needle off the corrupted slice
	assert_eq(RamCost.of_action(s.state, action, s.resolver), 2)
	assert_eq(_spent(s, action), 2, "judged where the needle read before it moved")


func test_doubling_is_once_per_action_with_two_needles() -> void:
	var w := CombatFixture.wheel([_atk, _atk, _atk, _atk, _atk, _null], null, [0, 10])
	var deck: Array[CardData] = [_cost1]
	var cls := CombatFixture.operative_class(&"n9c_twin", 60, w, deck)
	var s := CombatSession.start(CombatFixture.resolver([cls, _enemy]), cls.id, [_enemy.id], 5)
	for slot in 6:
		s.state.player.wheel.set_status(slot, RC.Status.CORRUPTED, 2)
	assert_true(RamCost.touches_corrupted(s.state.player))
	assert_eq(RamCost.of_action(s.state, CombatAction.play_card(0), s.resolver), 2, "x2, not x4")


func test_multiplier_comes_from_config() -> void:
	var s := _session()
	_corrupt_player(s)
	var cfg := s.resolver.config.duplicate() as CampaignConfigData
	cfg.corrupted_ram_cost_multiplier = 3
	assert_eq(RamCost.adjusted(1, s.state, null, cfg), 3)
	cfg.corrupted_ram_cost_multiplier = 1
	assert_eq(RamCost.adjusted(1, s.state, null, cfg), 1)


func test_respin_doubles() -> void:
	var s := _session()
	_corrupt_player(s)
	assert_eq(RamCost.of_action(s.state, CombatAction.respin(), s.resolver), _cfg.respin_ram_cost * 2)


func test_enemy_wheel_manipulation_halves_rounding_up() -> void:
	var s := _session()
	var e := s.state.get_combatant(&"enemy_0")
	e.wheel.set_status(1, RC.Status.CORRUPTED, 1)
	var push := CombatAction.play_card(_hand(s, &"n9c_push"), &"enemy_0")
	assert_eq(RamCost.of_action(s.state, push, s.resolver), 1, "ceil(1 / 2) = 1, never 0")
	assert_eq(RamCost.adjusted(3, s.state, e, _cfg), 2, "odd 3 rounds up")
	assert_eq(RamCost.adjusted(4, s.state, e, _cfg), 2)
	assert_eq(RamCost.adjusted(0, s.state, e, _cfg), 0)


func test_doubling_then_halving_applies_x2_then_ceil_half() -> void:
	var s := _session()
	_corrupt_player(s)
	var e := s.state.get_combatant(&"enemy_0")
	e.wheel.set_status(1, RC.Status.CORRUPTED, 1)
	assert_eq(RamCost.adjusted(3, s.state, e, _cfg), 3, "3 -> 6 -> 3")
	assert_eq(RamCost.adjusted(1, s.state, e, _cfg), 1, "1 -> 2 -> 1")


func test_halving_does_not_touch_a_card_on_your_own_wheel() -> void:
	var s := _session()
	s.state.get_combatant(&"enemy_0").wheel.set_status(1, RC.Status.CORRUPTED, 1)
	assert_eq(RamCost.of_action(s.state, CombatAction.play_card(_hand(s, &"n9c_c3")), s.resolver), 3)


func test_resolving_a_corrupted_slice_does_no_damage_and_no_drain() -> void:
	for majors in 4:
		var control := _session(majors)
		var s := _session(majors)
		_corrupt_player(s)
		var ram := s.state.ram
		control.apply(CombatAction.end_turn())
		var r := s.apply(CombatAction.end_turn())
		assert_eq(CombatFixture.events_of(r, "corrupted").size(), 0)
		assert_eq(s.state.player.hp, control.state.player.hp, "heat %d: only the enemy's own hits" % majors)
		assert_eq(s.state.ram, mini(_cls.max_ram, ram + _cls.ram_regen), "no drain (heat %d)" % majors)


func test_refusal_names_the_doubled_cost_and_changes_nothing() -> void:
	var s := _session()
	_corrupt_player(s)
	s.state.ram = 1
	var before := s.state_hash()
	var r := s.apply(CombatAction.play_card(_hand(s, &"n9c_c1")))
	assert_false(r.ok())
	assert_string_contains(r.error, "2 needed")
	assert_eq(s.state_hash(), before)


func test_forecast_function_matches_the_spend_on_24_combinations() -> void:
	var n := 0
	for corrupt in [false, true]:
		for card_id in [&"n9c_c0", &"n9c_c1", &"n9c_c3"]:
			for enemy_corrupt in [false, true]:
				for paid_nudge in [false, true]:
					var s := _session()
					s.state.ram = 12
					if corrupt:
						_corrupt_player(s)
					if enemy_corrupt:
						s.state.get_combatant(&"enemy_0").wheel.set_status(1, RC.Status.CORRUPTED, 1)
					if paid_nudge:
						s.state.free_nudges = 0
					var a := CombatAction.play_card(_hand(s, card_id))
					var forecast := RamCost.of_action(s.state, a, s.resolver)
					assert_eq(_spent(s, a), forecast)
					var nudge := CombatAction.nudge(&"enemy_0", 1)
					forecast = RamCost.of_action(s.state, nudge, s.resolver)
					assert_eq(_spent(s, nudge), forecast)
					n += 1
	assert_eq(n, 24)
