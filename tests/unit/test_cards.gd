extends GutTest
## Every card in the slice has a unit test (M2 acceptance): A.1 starting deck and the
## A.2 shared pool of 20, using the real card content on a controlled wheel.

var _atk6: SliceData
var _def5: SliceData
var _crit12: SliceData
var _miss: SliceData
var _ring: InnerRingData


func before_each() -> void:
	_atk6 = CombatFixture.slice(&"cd_atk6", RC.SliceType.ATTACK, 6)
	_def5 = CombatFixture.slice(&"cd_def5", RC.SliceType.DEFEND, 5, RC.TargetRule.SELF)
	_crit12 = CombatFixture.slice(&"cd_crit12", RC.SliceType.CRIT, 12)
	_miss = CombatFixture.slice(&"cd_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)
	_ring = CombatFixture.ring([CombatFixture.segment(&"cd_s0"), CombatFixture.segment(&"cd_s1"), CombatFixture.segment(&"cd_s2")])


func _card(id: StringName) -> CardData:
	return ContentRegistry.get_content(id) as CardData


## A session whose hand holds exactly `card_ids` (deck = those cards), on a wheel
## Crit, Atk, Atk, Atk, Def, Miss with an inner ring, against `enemy`.
func _session(card_ids: Array, enemy: EnemyData = null, hp: int = 60) -> CombatSession:
	var deck: Array[CardData] = []
	for id in card_ids:
		deck.append(_card(id))
	var cls := CombatFixture.operative_class(&"cd_class", hp, CombatFixture.wheel([_crit12, _atk6, _atk6, _atk6, _def5, _miss], null, [0], 0, _ring), deck)
	if enemy == null:
		enemy = CombatFixture.enemy(&"cd_dummy", 200, CombatFixture.miss_wheel())
	var s := CombatSession.start(CombatFixture.resolver([cls, enemy]), cls.id, [enemy.id], 3)
	CombatFixture.land(s.state.player, 1)
	CombatFixture.land_inner(s.state.player, 0)
	return s


func _enemy(s: CombatSession) -> CombatantState:
	return s.state.get_combatant(&"enemy_0")


func _play(s: CombatSession, id: StringName, wheel: StringName = &"", slot: int = -1, direction: int = 1) -> CombatResult:
	var a := CombatAction.play_card(s.state.hand.find(id), wheel, slot)
	a.direction = direction
	var r := s.apply(a)
	assert_true(r.ok(), "%s: %s" % [id, r.error])
	return r


# --- A.1 starting deck -----------------------------------------------------------------

func test_jolt_spins_3() -> void:
	var s := _session([&"jolt"])
	var before := _enemy(s).wheel.rotation
	_play(s, &"jolt", &"enemy_0")
	assert_eq(_enemy(s).wheel.rotation, before + 3)
	assert_eq(_card(&"jolt").ram_cost, 1)


func test_brute_spin_spins_6() -> void:
	var s := _session([&"brute_spin"])
	var before := _enemy(s).wheel.rotation
	_play(s, &"brute_spin", &"enemy_0")
	assert_eq(_enemy(s).wheel.rotation, before + 6)
	assert_eq(s.state.ram, 4)


func test_fine_tune_is_two_nudges_on_one_ring() -> void:
	var s := _session([&"fine_tune"])
	var outer := s.state.player.wheel.rotation
	var inner := s.state.player.wheel.inner_rotation
	var a := CombatAction.play_card(0, &"player")
	a.direction = -1
	a.ring = RC.RingScope.INNER
	assert_true(s.apply(a).ok())
	assert_eq(s.state.player.wheel.inner_rotation, inner - 2, "two nudges counter-clockwise on the inner ring")
	assert_eq(s.state.player.wheel.rotation, outer, "outer ring untouched")


func test_mirror_flip_mirrors_the_target() -> void:
	var s := _session([&"mirror_flip"])
	var tick := _enemy(s).wheel.tick_at(0)
	_play(s, &"mirror_flip", &"enemy_0")
	assert_eq(_enemy(s).wheel.tick_at(0), WheelMath.mirror_tick(tick))
	assert_eq(s.state.ram, 3)


func test_overdrive_overclocks_the_slice_under_the_pointer() -> void:
	var s := _session([&"overdrive"])
	_play(s, &"overdrive")
	assert_eq(s.state.player.wheel.slice_statuses[1], RC.Status.OVERCLOCKED)
	assert_eq(_card(&"overdrive").class_id, &"breaker")


# --- A.2 shared pool -----------------------------------------------------------------------

func test_twist_spins_4() -> void:
	var s := _session([&"twist"])
	var before := _enemy(s).wheel.rotation
	_play(s, &"twist", &"enemy_0")
	assert_eq(_enemy(s).wheel.rotation, before + 4)


func test_heavy_spin_spins_9_for_2_ram() -> void:
	var s := _session([&"heavy_spin"])
	var before := _enemy(s).wheel.rotation
	_play(s, &"heavy_spin", &"enemy_0")
	assert_eq(_enemy(s).wheel.rotation, before + 9)
	assert_eq(s.state.ram, 4)


func test_counter_spin_spins_minus_5() -> void:
	var s := _session([&"counter_spin"])
	var before := _enemy(s).wheel.rotation
	_play(s, &"counter_spin", &"enemy_0")
	assert_eq(_enemy(s).wheel.rotation, before - 5)


func test_ring_lock_keeps_the_inner_ring_still_this_turn() -> void:
	var s := _session([&"ring_lock", &"jolt"])
	var inner := s.state.player.wheel.inner_rotation
	var outer := s.state.player.wheel.rotation
	_play(s, &"ring_lock")
	assert_true(s.state.ring_locked)
	assert_eq(s.state.ram, 6, "Ring Lock costs 0")
	_play(s, &"jolt", &"player")
	assert_eq(s.state.player.wheel.rotation, outer + 3)
	assert_eq(s.state.player.wheel.inner_rotation, inner, "inner ring locked")
	s.apply(CombatAction.end_turn())
	assert_false(s.state.ring_locked, "lock ends with the turn")


func test_momentum_spins_2_then_5() -> void:
	var s := _session([&"momentum", &"momentum"])
	var before := _enemy(s).wheel.rotation
	_play(s, &"momentum", &"enemy_0")
	assert_eq(_enemy(s).wheel.rotation, before + 2, "first spin of the turn: 2")
	_play(s, &"momentum", &"enemy_0")
	assert_eq(_enemy(s).wheel.rotation, before + 7, "already spun: 5")


func test_gear_shift_moves_the_inner_ring_5() -> void:
	var s := _session([&"gear_shift"])
	var inner := s.state.player.wheel.inner_rotation
	var outer := s.state.player.wheel.rotation
	_play(s, &"gear_shift")
	assert_eq(s.state.player.wheel.inner_rotation, inner + 5)
	assert_eq(s.state.player.wheel.rotation, outer)


func test_snap_moves_a_ring_to_the_nearest_centre() -> void:
	var s := _session([&"snap"])
	CombatFixture.land(s.state.player, 2, 2)
	assert_eq(WheelMath.offset_at(s.state.player.wheel.tick_at(0)), 2)
	_play(s, &"snap")
	assert_eq(WheelMath.offset_at(s.state.player.wheel.tick_at(0)), 0)
	assert_eq(s.state.player.wheel.slice_at(0), 2, "same slice, now Perfect")


func test_micro_adjust_is_two_free_nudges_that_exhaust() -> void:
	var s := _session([&"micro_adjust"])
	var before := _enemy(s).wheel.rotation
	_play(s, &"micro_adjust", &"enemy_0")
	assert_eq(_enemy(s).wheel.rotation, before + 2)
	assert_eq(s.state.ram, 6, "costs 0")
	assert_eq(s.state.exhaust_pile, [&"micro_adjust"])


func test_calibrate_grants_two_free_nudges() -> void:
	var s := _session([&"calibrate"])
	assert_eq(s.state.free_nudges, 1)
	_play(s, &"calibrate")
	assert_eq(s.state.free_nudges, 3)
	var ram := s.state.ram
	for i in 3:
		s.apply(CombatAction.nudge(&"player", 1))
	assert_eq(s.state.ram, ram, "three nudges, no RAM spent")


func test_ring_tap_nudges_the_inner_ring_twice() -> void:
	var s := _session([&"ring_tap"])
	var inner := s.state.player.wheel.inner_rotation
	_play(s, &"ring_tap")
	assert_eq(s.state.player.wheel.inner_rotation, inner + 2)


func test_steady_hand_pays_2_ram_next_turn_on_a_perfect() -> void:
	var s := _session([&"steady_hand"])
	_play(s, &"steady_hand")
	CombatFixture.land(s.state.player, 1, 0)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.ram, 6 - 1 + 4 + 2, "cost 1, regen 4, Steady Hand +2")
	s = _session([&"steady_hand"])
	_play(s, &"steady_hand")
	CombatFixture.land(s.state.player, 1, 1)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.ram, 6 - 1 + 4, "Good landing: no bonus")


func test_strip_removes_2_resistance() -> void:
	var s := _session([&"strip"], CombatFixture.enemy(&"cd_resist", 200, CombatFixture.miss_wheel(3)))
	_play(s, &"strip", &"enemy_0")
	assert_eq(_enemy(s).resistance, 1)


func test_hub_breach_disables_the_hub_for_a_turn() -> void:
	var s := _session([&"hub_breach"], CombatFixture.enemy(&"cd_hubbed", 200, CombatFixture.miss_wheel(0, CombatFixture.hub(&"cd_lock", 3))))
	assert_eq(_enemy(s).resistance, 3)
	_play(s, &"hub_breach", &"enemy_0")
	assert_true(_enemy(s).is_hub_breached())
	assert_eq(_enemy(s).resistance, 0)
	assert_eq(s.state.ram, 4)


func test_undock_moves_a_satellite_to_an_adjacent_slice() -> void:
	var drone := CombatFixture.enemy(&"cd_drone", 5, CombatFixture.wheel([_miss, _miss]))
	var host := CombatFixture.enemy(&"cd_host", 200, CombatFixture.miss_wheel(), [CombatFixture.spawn(drone, 2)])
	var deck: Array[CardData] = [_card(&"undock")]
	var cls := CombatFixture.operative_class(&"cd_class", 60, CombatFixture.wheel([_crit12, _atk6, _atk6, _atk6, _def5, _miss]), deck)
	var s := CombatSession.start(CombatFixture.resolver([cls, drone, host]), cls.id, [host.id], 3)
	var sat := s.state.satellites_of(&"enemy_0")[0]
	var r := s.apply(CombatAction.play_card(0, sat.id))
	assert_true(r.ok(), r.error)
	assert_eq(s.state.satellites_of(&"enemy_0")[0].dock_slot, 3)
	s = CombatSession.start(CombatFixture.resolver([cls, drone, host]), cls.id, [host.id], 3)
	r = s.apply(CombatAction.play_card(0, &"enemy_0"))
	assert_false(r.ok(), "must target a satellite")


func test_freeze_skips_the_next_respin_and_exhausts() -> void:
	var s := _session([&"freeze"])
	_play(s, &"freeze", &"enemy_0")
	assert_true(_enemy(s).wheel.frozen)
	assert_eq(s.state.exhaust_pile, [&"freeze"])
	CombatFixture.land(_enemy(s), 4)
	var tick := _enemy(s).wheel.tick_at(0)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(_enemy(s).wheel.tick_at(0), tick, "frozen wheel did not respin")
	assert_false(_enemy(s).wheel.frozen, "one respin only")
	assert_eq(CombatFixture.events_of(r, "frozen_skip").size(), 1)


func test_jam_nudges_through_resistance() -> void:
	var s := _session([&"jam"], CombatFixture.enemy(&"cd_resist", 200, CombatFixture.miss_wheel(3)))
	var before := _enemy(s).wheel.rotation
	_play(s, &"jam", &"enemy_0")
	assert_eq(_enemy(s).wheel.rotation, before + 1)
	assert_eq(_enemy(s).resistance, 3, "resistance untouched")


func test_cache_gains_3_ram_and_exhausts() -> void:
	var s := _session([&"cache"])
	_play(s, &"cache")
	assert_eq(s.state.ram, 9)
	assert_eq(s.state.exhaust_pile, [&"cache"])


func test_pull_draws_2() -> void:
	var s := _session([&"pull", &"twist", &"twist", &"twist", &"twist", &"twist", &"twist", &"twist"])
	assert_eq(s.state.hand.size(), 5)
	assert_eq(s.state.draw_pile.size(), 3)
	if s.state.hand.find(&"pull") < 0:
		s = _session([&"pull"])
		assert_eq(s.state.hand, [&"pull"])
		_play(s, &"pull")
		assert_eq(s.state.hand.size(), 0, "nothing left to draw")
		return
	_play(s, &"pull")
	assert_eq(s.state.hand.size(), 6, "4 left after playing, +2 drawn")


func test_cleanse_removes_corrupted_from_a_chosen_slice() -> void:
	var s := _session([&"cleanse"])
	s.state.player.wheel.slice_statuses[3] = RC.Status.CORRUPTED
	assert_false(s.apply(CombatAction.play_card(0, &"player")).ok(), "needs a chosen slice")
	_play(s, &"cleanse", &"player", 3)
	assert_eq(s.state.player.wheel.slice_statuses[3], RC.Status.NONE)


func test_encrypt_protects_a_chosen_slice() -> void:
	var s := _session([&"encrypt", &"overdrive"])
	_play(s, &"encrypt", &"player", 1)
	assert_eq(s.state.player.wheel.slice_statuses[1], RC.Status.ENCRYPTED)
	_play(s, &"overdrive")
	assert_eq(s.state.player.wheel.slice_statuses[1], RC.Status.NONE, "encryption absorbed the overclock")


func test_all_25_slice_cards_exist_with_their_a1_a2_costs() -> void:
	var costs := {&"jolt": 1, &"brute_spin": 2, &"fine_tune": 1, &"mirror_flip": 3, &"overdrive": 1,
		&"twist": 1, &"heavy_spin": 2, &"counter_spin": 1, &"ring_lock": 0, &"momentum": 1, &"gear_shift": 1,
		&"snap": 2, &"micro_adjust": 0, &"calibrate": 1, &"ring_tap": 1, &"steady_hand": 1, &"strip": 1,
		&"hub_breach": 2, &"undock": 1, &"freeze": 3, &"jam": 2, &"cache": 0, &"pull": 1, &"cleanse": 1, &"encrypt": 1}
	for id in costs:
		var c := _card(id)
		assert_not_null(c, String(id))
		assert_eq(c.ram_cost, costs[id], "%s RAM" % id)
		assert_eq(c.validate().size(), 0, "%s validates" % id)
	assert_true(_card(&"micro_adjust").exhaust and _card(&"freeze").exhaust and _card(&"cache").exhaust)
