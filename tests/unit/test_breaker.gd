extends GutTest
## Breaker (GDD 5.2 / A.1, M1 acceptance): Perfect hook resolves the slice twice;
## Inner Ring x2 / Pierce apply; +1 spin on all cards. Uses the real Breaker content.

var _resolver: CombatResolver
var _dummy: EnemyData


func before_each() -> void:
	var def10 := CombatFixture.slice(&"b_def10", RC.SliceType.DEFEND, 10, RC.TargetRule.SELF)
	_dummy = CombatFixture.enemy(&"b_dummy", 200, CombatFixture.wheel([def10, def10, def10, def10, def10, def10]))
	_resolver = CombatFixture.resolver([_dummy])


func _session(ring: StringName = &"rank:1") -> CombatSession:
	var s := CombatSession.start(_resolver, &"breaker", [&"b_dummy"], 11, ring)
	s.state.player.block = 0
	return s


func _enemy(s: CombatSession) -> CombatantState:
	return s.state.get_combatant(&"enemy_0")


func test_breaker_wheel_is_crit_atk_atk_atk_def_miss() -> void:
	var s := _session()
	var ids := s.state.player.wheel.slot_slice_ids
	assert_eq(ids, [&"crit_12", &"atk_6", &"atk_6", &"atk_6", &"def_5", &"miss"])
	assert_eq(s.state.player.hp, 60)
	assert_eq(s.state.ram, 6)
	assert_eq(s.state.player.wheel.hub_id, &"breaker_core")


func test_perfect_resolves_the_slice_twice() -> void:
	var s := _session()
	CombatFixture.land(s.state.player, 1, 0)
	CombatFixture.land_inner(s.state.player, 2)  # blank segment
	CombatFixture.land(_enemy(s), 5)               # enemy blocks 10
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "retrigger").size(), 1)
	var hits := CombatFixture.events_of(r, "damage")
	assert_eq(hits.size(), 2, "attack 6 landed twice")
	assert_eq(_enemy(s).hp, 198, "12 total, 10 blocked -> 2")


func test_good_and_partial_do_not_retrigger() -> void:
	var s := _session()
	CombatFixture.land(s.state.player, 1, 1)
	CombatFixture.land_inner(s.state.player, 2)
	CombatFixture.land(_enemy(s), 5)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "damage").size(), 1)
	assert_eq(CombatFixture.events_of(r, "damage")[0]["amount"], 6, "Good = full output")
	s = _session()
	CombatFixture.land(s.state.player, 1, -2)
	CombatFixture.land_inner(s.state.player, 2)
	CombatFixture.land(_enemy(s), 5)
	r = s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "damage")[0]["amount"], 3, "Partial = 0.5x")


func test_ring_x2_doubles_output_and_stacks_with_the_perfect_hook() -> void:
	var s := _session()
	CombatFixture.land(s.state.player, 1, 0)
	CombatFixture.land_inner(s.state.player, 0)  # x2
	CombatFixture.land(_enemy(s), 5)
	var r := s.apply(CombatAction.end_turn())
	var hits := CombatFixture.events_of(r, "damage")
	assert_eq(hits.size(), 2)
	assert_eq(hits[0]["amount"], 12)
	assert_eq(hits[1]["amount"], 12)
	assert_eq(_enemy(s).hp, 186, "24 total, 10 blocked")


func test_ring_pierce_ignores_block() -> void:
	var s := _session()
	CombatFixture.land(s.state.player, 2, 1)
	CombatFixture.land_inner(s.state.player, 1)  # Pierce
	CombatFixture.land(_enemy(s), 5)
	var r := s.apply(CombatAction.end_turn())
	var hit := CombatFixture.events_of(r, "damage")[0]
	assert_true(hit["pierce"])
	assert_eq(hit["blocked"], 0)
	assert_eq(_enemy(s).hp, 194)


func test_rank_0_breaker_has_no_ring() -> void:
	var s := _session(&"")
	assert_false(s.state.player.wheel.has_inner_ring())
	CombatFixture.land(s.state.player, 1, 0)
	CombatFixture.land(_enemy(s), 5)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "damage").size(), 2, "Perfect hook still doubles without a ring")
	assert_eq(_enemy(s).hp, 198)


func test_hub_adds_one_spin_to_every_card() -> void:
	var s := _session()
	var jolt := s.state.hand.find(&"jolt")
	if jolt < 0:
		jolt = s.state.hand.find(&"brute_spin")
	assert_true(jolt >= 0, "a spin card in the opening hand (seed 11)")
	var card := _resolver.lookup.get_content(s.state.hand[jolt]) as CardData
	var before := _enemy(s).wheel.rotation
	var r := s.apply(CombatAction.play_card(jolt, &"enemy_0"))
	assert_true(r.ok(), r.error)
	assert_eq(_enemy(s).wheel.rotation, before + card.effects[0].amount + 1, "%s spins +1 for the Breaker" % card.id)


func test_spin_on_own_wheel_moves_both_rings() -> void:
	var s := _session()
	var idx := s.state.hand.find(&"jolt")
	if idx < 0:
		idx = s.state.hand.find(&"brute_spin")
	var outer := s.state.player.wheel.rotation
	var inner := s.state.player.wheel.inner_rotation
	var card := _resolver.lookup.get_content(s.state.hand[idx]) as CardData
	s.apply(CombatAction.play_card(idx, &"player"))
	assert_eq(s.state.player.wheel.rotation, outer + card.effects[0].amount + 1)
	assert_eq(s.state.player.wheel.inner_rotation, inner + card.effects[0].amount + 1)
