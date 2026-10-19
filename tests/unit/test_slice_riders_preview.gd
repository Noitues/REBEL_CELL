extends GutTest
## Plan 2 N20: the End Turn preview runs the same resolver path as the result, so staged
## actions that change a rider (a nudge off a PERFECT, a cleanse of a counted CORRUPTED
## slice) change the preview the same way; undo restores the staged state; rewind never
## crosses a checkpoint.

const F := preload("res://tests/helpers/rider_fixture.gd")


func _cleanse_deck(tag: StringName) -> Array[CardData]:
	var c := CombatFixture.card(StringName("%s_cleanse" % tag), [CombatFixture.effect(RC.EffectType.CLEANSE, RC.EffectTarget.OWN_WHEEL)], 0, RC.WheelTarget.OWN)
	return [c, c, c, c, c, c]


## An IV-style foe against an operative whose deck is all Cleanse (under the needle).
func _iv_session(tag: StringName) -> CombatSession:
	var p := F.pad(StringName("%s_pad" % tag))
	var cls := CombatFixture.operative_class(StringName("%s_op" % tag), 200, CombatFixture.wheel([p, p, p, p, p, p]), _cleanse_deck(tag))
	var iv := F.rider(StringName("%s_iv" % tag), 2, 1, 1.0, false, RC.Status.CORRUPTED, 1)
	var foe := CombatFixture.enemy(StringName("%s_foe" % tag), 999, CombatFixture.wheel([iv, iv, iv, iv, iv, iv]))
	var s := CombatSession.start(CombatFixture.resolver([cls, foe]), cls.id, [foe.id], F.SEED)
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	F.corrupt(s, [0, 1, 2])
	s._set_checkpoint()  # the hand-staged landing and statuses are this turn's start
	return s


func _preview_lost(s: CombatSession) -> int:
	return s.state.player.hp - s.preview_end_turn().resolved_state.player.hp


func test_preview_drops_perfect_multiplier_after_nudge() -> void:
	var s := F.session(&"rp_nudge", F.rider(&"rp_nudge_shim", 10, 1, 4.0))
	assert_eq(_preview_lost(s), 40, "PERFECT: x4")
	var r := s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_true(r.ok(), r.error)
	assert_eq(_preview_lost(s), 10, "nudged to GOOD: x1")
	var out := F.end(s)
	assert_eq(out["lost"], 10)
	assert_eq(out["preview_lost"], out["lost"])


func test_preview_hit_count_follows_staged_cleanse_and_undo() -> void:
	var s := _iv_session(&"rp_cl")
	var start_hash := s.state_hash()
	assert_eq(_preview_lost(s), 6, "3 CORRUPTED slices: 3 hits of 2")
	var r := s.apply(CombatAction.play_card(0))
	assert_true(r.ok(), r.error)
	assert_eq(s.state.player.wheel.count_status(RC.Status.CORRUPTED), 2)
	assert_eq(_preview_lost(s), 4, "cleansed one: 2 hits")
	assert_true(s.can_rewind())
	assert_true(s.rewind().ok())
	assert_eq(s.state_hash(), start_hash, "undo restores the staged state")
	assert_eq(_preview_lost(s), 6)


func test_preview_equals_result_after_staging() -> void:
	var s := _iv_session(&"rp_eq")
	s.apply(CombatAction.play_card(0))
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	var pid := s.state.player.id
	assert_eq(F.amounts(pv.events, pid), F.amounts(r.events, pid))
	assert_eq(pv.resolved_state.state_hash(), r.resolved_state.state_hash())


func test_rewind_does_not_cross_the_respin_checkpoint() -> void:
	var s := F.session(&"rp_rw", F.rider(&"rp_rw_shim", 3, 3, 4.0, true))
	s.apply(CombatAction.end_turn())
	assert_false(s.can_rewind(), "End Turn respins: a checkpoint")
	assert_false(s.rewind().ok())
	var h := s.state_hash()
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_true(s.rewind().ok())
	assert_eq(s.state_hash(), h, "undo stops at the checkpoint, state restored")
	assert_false(s.rewind().ok())
