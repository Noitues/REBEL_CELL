extends GutTest
## Plan 2 N6 (ruling Q19, designer answer 2): the preview of an action shows its listeners'
## results exactly (no "?"), the preview never fires them for real, and preview == result
## for every trigger.

const L = preload("res://tests/helpers/listener_fixture.gd")


func _check_action(s: CombatSession, action: CombatAction) -> CombatResult:
	var before := s.state.state_hash()
	var pv := s.preview(action)
	assert_eq(s.state.state_hash(), before, "preview leaves the session state alone")
	var r := s.apply(action)
	assert_true(r.ok(), "action accepted")
	assert_eq(pv.state.state_hash(), r.state.state_hash(), "preview == result (whole state)")
	assert_eq(L.fires(pv).size(), L.fires(r).size(), "same listener fires")
	return r


func _check_end_turn(s: CombatSession) -> CombatResult:
	var before := s.state.state_hash()
	var pv := s.preview_end_turn()
	assert_eq(s.state.state_hash(), before, "End Turn preview leaves the state alone")
	var r := s.apply(CombatAction.end_turn())
	assert_eq(pv.state.state_hash(), r.resolved_state.state_hash(), "End Turn preview == resolved state")
	assert_eq(pv.state.player.hp, r.resolved_state.player.hp)
	assert_eq(L.fires(pv).size(), L.fires(r).size())
	return r


func test_preview_equals_result_nudge_listener() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.hit(3), L.block(2)], 5)], {"factor": 1.3})
	L.stage(s, [], 6)
	var hp := s.state.player.hp
	for i in 3:
		_check_action(s, CombatAction.nudge(&"player", 1))
	assert_eq(hp - s.state.player.hp, 3 * 4, "round(3 x 1.3) per nudge")


func test_preview_equals_result_perfect_clawback() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_PERFECT, [L.hit(4)])])
	L.aim(s)
	var hp := s.state.player.hp
	var r := _check_end_turn(s)
	assert_eq(hp - r.resolved_state.player.hp, 4)


func test_preview_equals_result_hit_dealt() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_HIT_DEALT, [L.hit(2)], 3)])
	s.state.get_combatant(&"enemy_0").block = 2
	L.aim(s)
	_check_end_turn(s)


func test_preview_equals_result_card_and_ram_listeners_with_capped_fires() -> void:
	var listeners: Array[ListenerData] = [L.listener(RC.Trigger.ON_CARD_PLAYED, [L.hit(1)], 2),
		L.listener(RC.Trigger.ON_RAM_SPENT, [L.block(1)], 5)]
	var s := L.session(listeners)
	L.stage(s, [L.ZAP, L.ZAP, L.ZAP], 12)
	_check_action(s, CombatAction.play_card(0))
	_check_action(s, CombatAction.play_card(0))
	var third := s.preview(CombatAction.play_card(0))
	var card_fires := 0
	for f in L.fires(third):
		if int(f["trigger"]) == RC.Trigger.ON_CARD_PLAYED:
			card_fires += 1
	assert_eq(card_fires, 0, "the third card shows no capped fire")
	_check_action(s, CombatAction.play_card(0))


func test_preview_does_not_mutate_counters() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.block(1)], 2)])
	L.stage(s)
	for i in 3:
		s.preview(CombatAction.nudge(&"player", 1))
	assert_true(s.state.get_combatant(&"enemy_0").listener_fires_turn.is_empty(), "hovering alone fires nothing")


func test_preview_lists_one_entry_per_fire_with_key_and_amount() -> void:
	var listeners: Array[ListenerData] = [L.listener(RC.Trigger.ON_RAM_SPENT, [L.block(1)]),
		L.listener(RC.Trigger.ON_CARD_PLAYED, [L.block(1)])]
	var s := L.session(listeners)
	L.stage(s, [L.ZAP], 6)
	var pv := s.preview(CombatAction.play_card(0))
	var got := []
	for f in L.fires(pv):
		got.append([f["listener"], int(f["amount"])])
	assert_eq(got, [["lf_enemy:L0", 2], ["lf_enemy:L1", 0]])


func test_preview_includes_listener_damage_in_lethal_check() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.hit(20)])])
	s.state.player.hp = 5
	L.stage(s)
	var pv := s.preview(CombatAction.nudge(&"player", 1))
	assert_true(pv.state.is_over(), "the preview shows the loss")
	assert_eq(pv.state.player.hp, 0)
	var r := _check_action(s, CombatAction.nudge(&"player", 1))
	assert_true(r.state.is_over())
