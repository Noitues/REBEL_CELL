extends GutTest
## Plan 2 N6: enemy listeners. Trigger dispatch (ON_NUDGE, ON_CARD_PLAYED, ON_RAM_SPENT,
## ON_PERFECT, ON_HIT_DEALT), effect arithmetic (tier factor, PERCENT of max HP), caps per
## turn (config default 1) and per combat, the no-recursion guard, order by enemy id then
## listener index, Hub breach, dead enemies, SANDBOX (Q39) and the Trigger enum pin.

const L = preload("res://tests/helpers/listener_fixture.gd")


func _nudge(s: CombatSession) -> CombatResult:
	return s.apply(CombatAction.nudge(&"player", 1))


func _all_fires(results: Array) -> int:
	var n := 0
	for r in results:
		n += L.fires(r).size()
	return n


## The tier of the operative's pointer 0 under `offset` ticks from slot 0's centre.
func _tier_at(s: CombatSession, offset: int, pointer_index: int = 0) -> int:
	CombatFixture.land(s.state.player, 0, offset, pointer_index)
	return int(s.resolver.pointer_readouts(s.state, s.state.player)[pointer_index]["tier"])


func test_trigger_enum_ints_are_pinned() -> void:
	assert_eq(RC.Trigger.ON_CARD_PLAYED, 3)
	assert_eq(RC.Trigger.ON_NUDGE, 4)
	assert_eq(RC.Trigger.ON_PERFECT, 6)
	assert_eq(RC.Trigger.ON_RESOLVE, 13)
	assert_eq(RC.Trigger.ON_SATELLITE_DESTROYED, 14)
	assert_eq(RC.Trigger.ON_RAM_SPENT, 15, "appended after ON_SATELLITE_DESTROYED")
	assert_eq(RC.Trigger.ON_HIT_DEALT, 16)
	assert_eq(RC.Trigger.size(), 17)


func test_on_nudge_fires_on_free_and_paid_nudges_and_costs_stay() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.block(2)], 5)])
	L.stage(s, [], 6)
	var rs := [_nudge(s), _nudge(s), _nudge(s)]
	assert_eq(_all_fires(rs), 3, "one fire per accepted nudge, the free one too")
	assert_eq(s.state.get_combatant(&"enemy_0").block, 6, "+2 BLOCK each")
	assert_eq(s.state.ram, 6 - 2 * s.resolver.config.extra_nudge_ram_cost, "nudge costs unchanged")


func test_on_card_played_fires_per_card_and_not_on_rejected_play() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_CARD_PLAYED, [L.block(1)], 5)])
	L.stage(s, [L.ZAP, L.ZAP, L.PRICEY], 6)
	s.apply(CombatAction.play_card(0))
	s.apply(CombatAction.play_card(0))
	var refused := s.apply(CombatAction.play_card(0))
	assert_false(refused.ok(), "the 99 RAM card is refused")
	assert_eq(L.combat_fires(s.state), 2, "two accepted plays, two fires")


func test_on_ram_spent_carries_the_amount_and_skips_free_actions() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_RAM_SPENT, [L.block(1)], 5)])
	L.stage(s, [L.ZAP, L.FREE], 6)
	var free := _nudge(s)
	assert_eq(L.fires(free).size(), 0, "the free nudge spends no RAM")
	var paid := _nudge(s)
	var card := s.apply(CombatAction.play_card(0))
	var free_card := s.apply(CombatAction.play_card(0))
	assert_eq(L.fires(free_card).size(), 0, "a 0-cost card spends no RAM")
	var amounts := []
	for f in L.fires(paid) + L.fires(card):
		amounts.append(int(f["amount"]))
	assert_eq(amounts, [1, 2], "paid nudge 1, card 2")


func test_on_perfect_fires_only_on_perfect() -> void:
	for offset in [0, 1, 2]:
		var s := L.session([L.listener(RC.Trigger.ON_PERFECT, [L.block(1)])])
		var tier := _tier_at(s, offset)
		L.aim(s, offset)
		var r := s.apply(CombatAction.end_turn())
		var want := 1 if tier == RC.PrecisionTier.PERFECT else 0
		assert_eq(L.fires(r).size(), want, "offset %d (tier %d)" % [offset, tier])


func test_on_perfect_counts_each_needle_and_the_turn_cap_holds() -> void:
	var two: Array[ListenerData] = [L.listener(RC.Trigger.ON_PERFECT, [L.block(1)], 5)]
	# Needles on ticks 0 and 15 read the centres of slots 0 and 3, both SHIMs.
	var s := L.session(two, {"pointers": [0, 15], "shims": [0, 3]})
	CombatFixture.land(s.state.player, 0, 0, 0)
	var readouts := s.resolver.pointer_readouts(s.state, s.state.player)
	var perfects := 0
	for rd in readouts:
		if int(rd["tier"]) == RC.PrecisionTier.PERFECT:
			perfects += 1
	s._set_checkpoint()
	var r := s.apply(CombatAction.end_turn())
	assert_eq(L.fires(r).size(), perfects, "one fire per Perfect needle (%d)" % perfects)
	assert_eq(perfects, 2, "both needles centred")
	var capped := L.session([L.listener(RC.Trigger.ON_PERFECT, [L.block(1)])], {"pointers": [0, 15], "shims": [0, 3]})
	CombatFixture.land(capped.state.player, 0, 0, 0)
	capped._set_checkpoint()
	assert_eq(L.fires(capped.apply(CombatAction.end_turn())).size(), 1, "unauthored cap: once per turn (Q8 a)")


func test_on_perfect_once_per_needle_whatever_the_retriggers() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_PERFECT, [L.block(1)], 5)])
	L.aim(s)
	var r := s.apply(CombatAction.end_turn())
	var f := L.fires(r)
	assert_eq(f.size(), 1)
	assert_eq(int(f[0]["amount"]), 7, "carries the landed slice output")


func test_on_hit_dealt_fires_after_block_with_final_damage() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_HIT_DEALT, [L.block(1)])], {"shim": 7})
	var enemy := s.state.get_combatant(&"enemy_0")
	enemy.block = 3
	L.aim(s)
	var r := s.apply(CombatAction.end_turn())
	var f := L.fires(r)
	assert_eq(f.size(), 1, "one landed hit")
	assert_eq(int(f[0]["amount"]), 4, "7 - 3 BLOCK")
	assert_lt(CombatFixture.index_of_event(r, "damage"), CombatFixture.index_of_event(r, "listener"), "heard after the hit")
	assert_gt(CombatFixture.index_of_event(r, "listener"), CombatFixture.index_of_event(r, "pass", "pass", "statuses"), "after the slice passes")


func test_on_hit_dealt_min_tier() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_HIT_DEALT, [L.block(1)], -1, -1, RC.PrecisionTier.PERFECT)])
	var offset := 1
	while offset < 3 and _tier_at(s, offset) == RC.PrecisionTier.PERFECT:
		offset += 1
	L.aim(s, offset)
	var r := s.apply(CombatAction.end_turn())
	assert_gt(CombatFixture.events_of(r, "damage").size(), 0, "the hit lands")
	assert_eq(L.fires(r).size(), 0, "below the listener's min tier")


func test_listener_damage_uses_tier_factor() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.hit(4)])], {"factor": 1.69})
	L.stage(s)
	var hp := s.state.player.hp
	var r := _nudge(s)
	assert_eq(hp - s.state.player.hp, 7, "round(4 x 1.69)")
	assert_eq(int(CombatFixture.events_of(r, "damage")[0]["amount"]), 7)


func test_listener_percent_damage_reads_max_hp_unscaled() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.hit(10, true)])], {"factor": 2.2})
	L.stage(s)
	var hp := s.state.player.hp
	_nudge(s)
	assert_eq(s.state.get_combatant(&"enemy_0").max_hp, 300)
	assert_eq(hp - s.state.player.hp, 30, "10 % of 300, no tier factor")


func test_listener_fire_cap_per_turn() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.block(1)], 2)])
	L.stage(s, [], 12)
	var rs := []
	for i in 4:
		rs.append(_nudge(s))
	assert_eq(_all_fires(rs), 2)


func test_unauthored_cap_reads_config_default() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.block(1)])])
	L.stage(s, [], 12)
	var rs := []
	for i in 3:
		rs.append(_nudge(s))
	assert_eq(_all_fires(rs), s.resolver.config.listener_max_per_turn_default)
	assert_eq(s.resolver.config.listener_max_per_turn_default, 1)


func test_listener_cap_resets_at_turn_start_and_combat_cap_persists() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.block(1)], 2, 3)])
	L.stage(s, [], 12)
	for i in 4:
		_nudge(s)
	assert_eq(L.combat_fires(s.state), 2)
	s.apply(CombatAction.end_turn())
	assert_true(s.state.get_combatant(&"enemy_0").listener_fires_turn.is_empty(), "turn counts reset in start_turn")
	s.state.ram = 12
	var rs := []
	for i in 4:
		rs.append(_nudge(s))
	assert_eq(_all_fires(rs), 1, "the combat cap of 3 leaves one fire")
	assert_eq(L.combat_fires(s.state), 3)


func test_listener_does_not_trigger_listeners() -> void:
	# Each player hit is heard once; the listener's own hit on the operative is not a
	# player-side hit and is never heard.
	var s := L.session([L.listener(RC.Trigger.ON_HIT_DEALT, [L.hit(2)], 5)])
	L.aim(s)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(L.fires(r).size(), 1)
	# The guard itself: nothing nests inside a running listener.
	s.resolver._in_listener = true
	var events: Array[Dictionary] = []
	assert_eq(s.resolver.fire_listeners(s.state, RC.Trigger.ON_NUDGE, {}, s.rng, events), 0)
	s.resolver._in_listener = false


func test_order_is_enemy_id_then_listener_index_then_hub() -> void:
	var own: Array[ListenerData] = [L.listener(RC.Trigger.ON_NUDGE, [L.block(1)]), L.listener(RC.Trigger.ON_NUDGE, [L.block(2)])]
	var hub: Array[ListenerData] = [L.listener(RC.Trigger.ON_NUDGE, [L.block(3)])]
	var second: Array[ListenerData] = [L.listener(RC.Trigger.ON_NUDGE, [L.block(4)])]
	var s := L.session(own, {"hub": hub, "second": second})
	L.stage(s)
	var keys := []
	for f in L.fires(_nudge(s)):
		keys.append("%s/%s" % [f["owner"], f["listener"]])
	assert_eq(keys, ["enemy_0/lf_enemy:L0", "enemy_0/lf_enemy:L1", "enemy_0/lf_hub:L0", "enemy_1/lf_enemy_b:L0"])


func test_dead_enemy_does_not_listen_and_parked_low_hp_does() -> void:
	var second: Array[ListenerData] = [L.listener(RC.Trigger.ON_NUDGE, [L.block(4)])]
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.block(1)])], {"second": second})
	s.state.get_combatant(&"enemy_0").hp = 1
	s.state.get_combatant(&"enemy_1").hp = 0
	L.stage(s)
	var f := L.fires(_nudge(s))
	assert_eq(f.size(), 1)
	assert_eq(f[0]["owner"], &"enemy_0")


func test_hub_breach_silences_hub_listeners_only() -> void:
	var hub: Array[ListenerData] = [L.listener(RC.Trigger.ON_NUDGE, [L.block(3)])]
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.block(1)])], {"hub": hub})
	s.state.get_combatant(&"enemy_0").hub_breached_turns = 1
	L.stage(s)
	var f := L.fires(_nudge(s))
	assert_eq(f.size(), 1)
	assert_eq(f[0]["listener"], "lf_enemy:L0")


func test_hub_swap_swaps_hub_listeners() -> void:
	var hub: Array[ListenerData] = [L.listener(RC.Trigger.ON_NUDGE, [L.block(3)])]
	var s := L.session([], {"hub": hub})
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(s.resolver.enemy_listeners(e).size(), 1)
	e.wheel.hub_id = &""  # what a phase hub_override without listeners leaves
	assert_eq(s.resolver.enemy_listeners(e).size(), 0)


func test_sandboxed_hit_is_not_heard() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_HIT_DEALT, [L.block(1)])])
	s.state.get_combatant(&"enemy_0").evade_charges = 1
	L.aim(s)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "evaded").size(), 1)
	assert_eq(L.fires(r).size(), 0)


func test_listener_damage_spends_a_sandbox_charge() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.hit(5)])])
	s.state.player.evade_charges = 1
	L.stage(s)
	var hp := s.state.player.hp
	var r := _nudge(s)
	assert_eq(s.state.player.hp, hp, "Q39: negated")
	assert_eq(s.state.player.evade_charges, 0)
	assert_eq(CombatFixture.events_of(r, "evaded").size(), 1)


func test_listener_hit_can_end_the_fight_on_an_action() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.hit(50)])])
	s.state.player.hp = 10
	L.stage(s)
	_nudge(s)
	assert_true(s.state.is_over(), "an operative at 0 HP is lost (Q24.1)")


func test_no_listeners_leave_no_trace() -> void:
	var s := L.session([])
	L.stage(s, [L.ZAP], 6)
	var rs := [_nudge(s), _nudge(s), s.apply(CombatAction.play_card(0))]
	L.aim(s)
	rs.append(s.apply(CombatAction.end_turn()))
	assert_eq(_all_fires(rs), 0)
	var d := s.state.get_combatant(&"enemy_0").to_dict()
	assert_false(d.has("listener_fires_turn") or d.has("listener_fires_combat"), "save and hash unchanged without fires")
