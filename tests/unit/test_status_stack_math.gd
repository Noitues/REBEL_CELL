extends GutTest
## Plan 2 N8 (R8): OUTPUT_DOWN takes output_down_per_stack off a slice per stack, the shares
## adding up (ruling Q35 b: one signed sum, never below 0); today's PARASITE is OUTPUT_DOWN
## x2 (half output). One rounding, as every slice multiplier: roundi(base x product). The
## preview equals the result with stacks on the wheel.

var _cfg: CampaignConfigData
var _cleanse: CardData


func before_each() -> void:
	_cfg = CombatFixture.config()
	var e := CombatFixture.effect(RC.EffectType.CLEANSE, RC.EffectTarget.OWN_WHEEL)
	_cleanse = CombatFixture.card(&"sm_cleanse", [e], 0, RC.WheelTarget.OWN)


## An operative whose six slices all attack for `output`, against a punching bag (or `enemy`).
func _session(output: int, enemy: EnemyData = null, cards: Array[CardData] = []) -> CombatSession:
	var atk := CombatFixture.slice(StringName("sm_atk%d" % output), RC.SliceType.SHIM, output)
	var deck: Array[CardData] = [_cleanse]
	if not cards.is_empty():
		deck = cards
	var cls := CombatFixture.operative_class(&"sm_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, atk]), deck)
	if enemy == null:
		enemy = CombatFixture.enemy(&"sm_dummy", 500, CombatFixture.null_wheel())
	var custom: Array = [cls, enemy]
	custom.append_array(deck)
	var s := CombatSession.start(CombatFixture.resolver(custom), cls.id, [enemy.id], 52)
	CombatFixture.land(s.state.player, 1)
	return s


func _hit(s: CombatSession) -> int:
	var r := s.apply(CombatAction.end_turn())
	var hits := CombatFixture.events_of(r, "damage")
	return int(hits[0]["amount"]) if not hits.is_empty() else 0


func test_parasite_legacy_equals_output_down_two() -> void:
	assert_eq(CombatResolver.output_down_factor(_cfg.parasite_output_down_stacks, _cfg), 0.5, "x2 is the old PARASITE's half")
	var s := _session(10)
	s.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 2)
	assert_eq(_hit(s), 5, "10 -> 5")


func test_output_down_per_stack_table() -> void:
	# 1 - 0.25 n, summed (Q35 b), one rounding: 20 x {1, 0.75, 0.5, 0.25, 0}.
	var want := [20, 15, 10, 5, 0]
	for n in want.size():
		var s := _session(20)
		if n > 0:
			s.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, n)
		assert_eq(_hit(s), want[n], "x%d" % n)
		assert_eq(roundi(20 * CombatResolver.output_down_factor(n, _cfg)), want[n])


func test_output_down_floors_at_zero_never_negative() -> void:
	for n in [4, 5, 9]:
		assert_eq(CombatResolver.output_down_factor(n, _cfg), 0.0, "x%d" % n)
	var s := _session(1)
	s.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, _cfg.status_stack_cap)
	assert_eq(_hit(s), 0)


func test_preview_equals_result_with_stacks() -> void:
	var s := _session(12)
	s.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 3)
	var preview := s.preview_end_turn()
	var real := s.apply(CombatAction.end_turn())
	assert_eq(preview.state.state_hash(), real.resolved_state.state_hash(), "preview == result")
	assert_eq(CombatFixture.events_of(preview, "damage")[0]["amount"], CombatFixture.events_of(real, "damage")[0]["amount"])
	assert_eq(int(CombatFixture.events_of(real, "damage")[0]["amount"]), 3, "12 x 0.25")


func test_preview_equals_result_stacks_plus_weak_tier() -> void:
	var s := _session(14)
	CombatFixture.land(s.state.player, 1, 2)  # offset 2: WEAK
	s.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 2)
	var preview := s.preview_end_turn()
	var real := s.apply(CombatAction.end_turn())
	assert_eq(preview.state.state_hash(), real.resolved_state.state_hash())
	assert_eq(int(CombatFixture.events_of(real, "damage")[0]["amount"]), roundi(14 * _cfg.weak_multiplier * 0.5), "WEAK x0.5, then x2 stacks x0.5")


func test_preview_updates_after_cleanse_card() -> void:
	var s := _session(8)
	s.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 2)
	s._set_checkpoint()
	var before := s.preview_end_turn()
	assert_eq(int(CombatFixture.events_of(before, "damage")[0]["amount"]), 4)
	var r := s.apply(CombatAction.play_card(s.state.hand.find(&"sm_cleanse")))
	assert_true(r.ok(), r.error)
	var after := s.preview_end_turn()
	assert_eq(int(CombatFixture.events_of(after, "damage")[0]["amount"]), 8, "cleansed: full output")
	s.rewind()
	assert_eq(int(CombatFixture.events_of(s.preview_end_turn(), "damage")[0]["amount"]), 4, "undo restores the stacks")


func test_hardened_encrypted_firmware_absorbs_stack_apply() -> void:
	var hardened := FirmwareData.new()
	hardened.id = &"sm_hardened"
	hardened.permanent_status = RC.Status.ENCRYPTED
	var atk := CombatFixture.slice(&"sm_atk5", RC.SliceType.SHIM, 5)
	var cls := CombatFixture.operative_class(&"sm_hard", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, atk], null, [0], 0, null, [null, hardened]), [_cleanse])
	var dummy := CombatFixture.enemy(&"sm_dummy2", 100, CombatFixture.null_wheel())
	var s := CombatSession.start(CombatFixture.resolver([cls, dummy, hardened, _cleanse]), cls.id, [dummy.id], 3)
	for i in 3:
		var events: Array[Dictionary] = []
		assert_false(s.resolver.fx.apply_status(s.state.player, 1, RC.Status.OUTPUT_DOWN, events, 3))
	assert_eq(s.state.player.wheel.slice_stacks[1], {}, "Hardened re-arms: every apply absorbed")


func test_stacks_on_enemy_wheel_reduce_enemy_output() -> void:
	var atk := CombatFixture.slice(&"sm_eatk", RC.SliceType.SHIM, 12)
	var foe := CombatFixture.enemy(&"sm_foe", 200, CombatFixture.wheel([atk, atk, atk, atk, atk, atk]))
	var nul := CombatFixture.slice(&"sm_nul", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var cls := CombatFixture.operative_class(&"sm_bag", 90, CombatFixture.wheel([nul, nul, nul, nul, nul, nul]), [_cleanse])
	var s := CombatSession.start(CombatFixture.resolver([cls, foe, _cleanse]), cls.id, [foe.id], 8)
	var e := s.state.get_combatant(&"enemy_0")
	CombatFixture.land(e, 0)
	e.wheel.set_status(0, RC.Status.OUTPUT_DOWN, 1)
	var preview := s.preview_end_turn()
	var real := s.apply(CombatAction.end_turn())
	assert_eq(preview.state.state_hash(), real.resolved_state.state_hash())
	assert_eq(s.state.player.hp, 90 - roundi(12 * s.state.get_combatant(&"enemy_0").output_scale * 0.75), "the enemy hits at x0.75")
