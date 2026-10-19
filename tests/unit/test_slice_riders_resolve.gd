extends GutTest
## Plan 2 N20: slice riders in a whole turn. One landing becomes a hit list (`hits`, or the
## target wheel's slices carrying a status), a PERFECT-only multiplier and a pierce flag.
## Each hit runs the damage path on its own: enrage -> SANDBOX charge -> bodyguard -> BLOCK
## -> SHIELD -> HP (phase floor). Pierce skips BLOCK and SHIELD only (ruling Q39). No hit cap
## (ruling Q40). Preview == result in every case.

const F := preload("res://tests/helpers/rider_fixture.gd")


func _check_preview(out: Dictionary) -> void:
	assert_eq(out["preview_lost"], out["lost"], "preview == result")
	var pv: CombatResult = out["preview"]
	var r: CombatResult = out["result"]
	var pid := r.resolved_state.player.id
	assert_eq(F.amounts(pv.events, pid), F.amounts(r.events, pid), "preview hit list == result hit list")


func test_default_slice_matches_legacy() -> void:
	var s := F.session(&"rr_legacy", F.rider(&"rr_legacy_shim", 5))
	var out := F.end(s)
	assert_eq(out["lost"], 5)
	var r: CombatResult = out["result"]
	assert_eq(F.amounts(r.events, s.state.player.id), [5], "one hit, as before N20")
	var atk := CombatFixture.events_of(r, "attack")
	assert_eq(int(atk[0]["hits"]), 1)
	assert_false(String(atk[0]["text"]).contains(" x "), "a 1-hit attack line reads as before")
	_check_preview(out)


func test_hits_3_deals_three_separate_hits() -> void:
	var s := F.session(&"rr_h3", F.rider(&"rr_h3_shim", 5, 3))
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id), [5, 5, 5])
	assert_eq(out["lost"], 15)
	_check_preview(out)


func test_each_hit_meets_block_separately() -> void:
	var s := F.session(&"rr_blk", F.rider(&"rr_blk_shim", 5, 3))
	s.state.player.block = 7
	var out := F.end(s)
	var dmg := ((out["result"] as CombatResult).events).filter(func(e: Dictionary) -> bool: return e["type"] == "damage")
	assert_eq(dmg.map(func(e: Dictionary) -> int: return int(e["blocked"])), [5, 2, 0])
	assert_eq(dmg.map(func(e: Dictionary) -> int: return int(e["hp_damage"])), [0, 3, 5])
	assert_eq(out["lost"], 8, "BLOCK 7 vs 3 x 5: 5 absorbed, then 2 absorbed + 3, then 5")
	_check_preview(out)


func test_each_hit_meets_shield_after_block() -> void:
	var s := F.session(&"rr_shd", F.rider(&"rr_shd_shim", 5, 3))
	s.state.player.block = 4
	s.state.player.shield = 4
	var out := F.end(s)
	assert_eq(out["lost"], 7, "15 - 4 block - 4 shield")
	assert_eq((out["result"] as CombatResult).resolved_state.player.shield, 0)
	_check_preview(out)


func test_no_hit_cap() -> void:
	var s := F.session(&"rr_ten", F.rider(&"rr_ten_shim", 1, 10))
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id).size(), 10, "Q40: 10 hits means 10 hits")
	assert_eq(out["lost"], 10)
	_check_preview(out)


func test_hits_per_status_counts_corrupted_slices() -> void:
	var s := F.session(&"rr_iv", F.rider(&"rr_iv_shim", 2, 1, 1.0, false, RC.Status.CORRUPTED, 1))
	F.corrupt(s, [1, 2, 3])
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id), [2, 2, 2], "IV: 3 CORRUPTED slices -> 3 hits of 2")
	_check_preview(out)


func test_hits_per_status_zero_slices_gives_minimum() -> void:
	var s := F.session(&"rr_iv0", F.rider(&"rr_iv0_shim", 2, 1, 1.0, false, RC.Status.CORRUPTED, 1))
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id), [2], "0 CORRUPTED -> 1 hit (min 1)")
	var s2 := F.session(&"rr_iv0b", F.rider(&"rr_iv0b_shim", 2, 2, 1.0, false, RC.Status.CORRUPTED, 1))
	F.corrupt(s2, [4])
	var out2 := F.end(s2)
	assert_eq(F.amounts((out2["result"] as CombatResult).events, s2.state.player.id).size(), 2, "`hits` is the minimum: max(2, 1)")


func test_hits_per_status_counts_slices_not_stacks() -> void:
	var s := F.session(&"rr_ivs", F.rider(&"rr_ivs_shim", 2, 1, 1.0, false, RC.Status.CORRUPTED, 1))
	F.corrupt(s, [1, 2], 3)
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id).size(), 2, "two slices at x3 count 2")
	_check_preview(out)


func test_hits_per_status_skips_null_slices() -> void:
	var null_slice := CombatFixture.slice(&"rr_ivn_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var p := F.pad(&"rr_ivn_pad")
	var s := F.session(&"rr_ivn", F.rider(&"rr_ivn_shim", 2, 1, 1.0, false, RC.Status.CORRUPTED, 1), [0], [0], [p, null_slice, null_slice, p, p, p])
	F.corrupt(s, [1, 2, 3, 4])
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id).size(), 2, "only the non-NULL slices 3 and 4 count")
	_check_preview(out)


func test_hits_per_status_slice_multiplier() -> void:
	var s := F.session(&"rr_ivx", F.rider(&"rr_ivx_shim", 2, 1, 1.0, false, RC.Status.CORRUPTED, 2))
	F.corrupt(s, [1, 2, 3])
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id).size(), 6)
	_check_preview(out)


func test_hits_per_status_counts_all_six_slices() -> void:
	var s := F.session(&"rr_iv6", F.rider(&"rr_iv6_shim", 1, 1, 1.0, false, RC.Status.CORRUPTED, 1))
	F.corrupt(s, [0, 1, 2, 3, 4, 5])
	var out := F.end(s)
	assert_eq(out["lost"], 6)
	_check_preview(out)


func test_perfect_multiplier_by_tier() -> void:
	var want := {0: 40, 1: 10, 2: 5}
	for offset: int in want:
		var s := F.session(StringName("rr_med%d" % offset), F.rider(StringName("rr_med%d_shim" % offset), 10, 1, 4.0))
		CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0, offset)
		var out := F.end(s)
		assert_eq(out["lost"], want[offset], "offset %d: PERFECT x4, GOOD x1, WEAK 0.5x only" % offset)
		_check_preview(out)


func test_perfect_multiplier_with_output_down() -> void:
	var s := F.session(&"rr_medod", F.rider(&"rr_medod_shim", 10, 1, 4.0))
	s.state.get_combatant(&"enemy_0").wheel.add_stacks(0, RC.Status.OUTPUT_DOWN, 1, 5)
	var out := F.end(s)
	assert_eq(out["lost"], 30, "40 x 0.75")
	_check_preview(out)


func test_rider_flat_damage_scales_with_tier_factor() -> void:
	var s := F.session(&"rr_t3", F.rider(&"rr_t3_shim", 10, 2, 4.0))
	s.state.get_combatant(&"enemy_0").output_scale = 1.69
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id), [68, 68], "R2: roundi(10 x 1.69 x 4) per hit")
	_check_preview(out)


func test_pierce_ignores_block_and_shield() -> void:
	var s := F.session(&"rr_prc", F.rider(&"rr_prc_shim", 10, 1, 1.0, true))
	s.state.player.block = 8
	s.state.player.shield = 5
	var out := F.end(s)
	assert_eq(out["lost"], 10)
	assert_eq((out["result"] as CombatResult).resolved_state.player.shield, 5, "SHIELD untouched")
	_check_preview(out)


func test_pierce_does_not_bypass_sandbox() -> void:
	var s := F.session(&"rr_psb", F.rider(&"rr_psb_shim", 5, 3, 1.0, true))
	s.state.player.evade_charges = 1
	var out := F.end(s)
	var hits := F.hits_of((out["result"] as CombatResult).events, s.state.player.id)
	assert_eq(hits.map(func(e: Dictionary) -> String: return String(e["type"])), ["evaded", "damage", "damage"], "Q39: one charge negates one hit")
	assert_eq(out["lost"], 10)
	_check_preview(out)


func test_each_charge_negates_one_hit() -> void:
	var s := F.session(&"rr_chg", F.rider(&"rr_chg_shim", 5, 3))
	s.state.player.evade_charges = 2
	var out := F.end(s)
	assert_eq(out["lost"], 5)
	_check_preview(out)


func test_pierce_does_not_bypass_bodyguard() -> void:
	var prc := F.rider(&"rr_bg_prc", 6, 2, 1.0, true)
	var null_slice := CombatFixture.slice(&"rr_bg_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var cls := CombatFixture.operative_class(&"rr_bg_op", 60, CombatFixture.wheel([prc, prc, prc, prc, prc, prc]), F._deck(&"rr_bg"))
	var drone := CombatFixture.enemy(&"rr_bg_drone", 50, CombatFixture.wheel([null_slice, null_slice]))
	var host := CombatFixture.enemy(&"rr_bg_host", 40, CombatFixture.wheel([null_slice, null_slice, null_slice, null_slice, null_slice, null_slice]), [CombatFixture.spawn(drone, 2)])
	var s := CombatSession.start(CombatFixture.resolver([cls, drone, host]), cls.id, [host.id], F.SEED)
	var sat := s.state.satellites_of(&"enemy_0")[0]
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 2)
	s.state.get_combatant(&"enemy_0").block = 10
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "bodyguard").size(), 2, "each pierce hit is redirected")
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").hp, 40)
	assert_eq(r.resolved_state.get_combatant(sat.id).hp, 38, "the drone takes 2 x 6")
	assert_eq(pv.resolved_state.state_hash(), r.resolved_state.state_hash(), "preview == result")


func test_hits_land_on_every_target_needle() -> void:
	var s := F.session(&"rr_two", F.rider(&"rr_two_shim", 3, 2), [0, 15])
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id), [3, 3, 3, 3], "2 hits x 2 operative needles")
	_check_preview(out)


func test_each_enemy_pointer_resolves_its_own_hits() -> void:
	var s := F.session(&"rr_mp", F.rider(&"rr_mp_shim", 4, 2), [0], [0, 15])
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id).size(), 4, "2 enemy needles x 2 hits")
	_check_preview(out)


func test_breaker_perfect_retrigger_repeats_the_hit_list() -> void:
	var again: Array[TriggeredEffectData] = [CombatFixture.triggered(RC.Trigger.ON_PERFECT, [CombatFixture.effect(RC.EffectType.RETRIGGER, RC.EffectTarget.SELF, 0)])]
	var s := F.session(&"rr_brk", F.rider(&"rr_brk_shim", 5, 3, 1.0, false, RC.Status.NONE, 0, RC.SliceType.SHIM, again))
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id).size(), 6, "resolves twice: 2 x 3 hits")
	assert_eq(out["lost"], 30)
	_check_preview(out)


func test_riders_combine_hits_pierce_perfect() -> void:
	var s := F.session(&"rr_adr", F.rider(&"rr_adr_shim", 10, 2, 4.0, true))
	s.state.player.block = 50
	var out := F.end(s)
	assert_eq(F.amounts((out["result"] as CombatResult).events, s.state.player.id), [40, 40])
	assert_eq(out["lost"], 80)
	_check_preview(out)


func test_overclocked_multiplies_rider_output() -> void:
	var s := F.session(&"rr_oc", F.rider(&"rr_oc_shim", 10, 1, 4.0))
	s.state.get_combatant(&"enemy_0").wheel.add_stacks(0, RC.Status.OVERCLOCKED, 1, 5)
	var out := F.end(s)
	assert_eq(out["lost"], 60, "10 x 4 x 1.5")
	_check_preview(out)


func test_phase_floor_parks_later_hits() -> void:
	var hit := F.rider(&"rr_pf_shim", 20, 4)
	var noop: Array[CardData] = F._deck(&"rr_pf")
	var cls := CombatFixture.operative_class(&"rr_pf_op", 60, CombatFixture.wheel([hit, hit, hit, hit, hit, hit]), noop)
	var boss := PhaseFixture.enemy(&"rr_pf_boss", 100, [0.5])
	var s := CombatSession.start(CombatFixture.resolver([cls, boss]), cls.id, [boss.id], F.SEED)
	var b := s.state.get_combatant(&"enemy_0")
	b.hp = b.hp_floor() + 10
	CombatFixture.land(s.state.player, 0)
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	var dmg := CombatFixture.events_of(r, "damage").filter(func(e: Dictionary) -> bool: return StringName(String(e["target"])) == &"enemy_0")
	assert_eq(dmg.map(func(e: Dictionary) -> int: return int(e["hp_damage"])), [10, 0, 0, 0], "the first hit stops at the floor")
	assert_eq(dmg.map(func(e: Dictionary) -> int: return int(e["parked"])), [10, 20, 20, 20], "later hits are lost")
	assert_eq(CombatFixture.events_of(r, "phase").size(), CombatFixture.events_of(pv, "phase").size())
	assert_eq(pv.resolved_state.state_hash(), r.resolved_state.state_hash(), "preview == result")
