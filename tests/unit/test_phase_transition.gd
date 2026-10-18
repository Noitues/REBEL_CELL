extends GutTest
## Plan 2 N3 (R3): a phase starts at the end of the resolve whose damage reached its floor;
## later hits in that resolve are lost; one phase per resolve; the new floor is the next
## threshold. The preview (CombatOutcome, the result chips) shows the parked amount and
## equals the real resolve.


func _boss(thresholds: Array = [0.68, 0.33], dmg: int = 10, pointers: Array = [0]) -> CombatSession:
	return PhaseFixture.session(PhaseFixture.enemy(&"pt_boss", 100, thresholds, RC.EnemyClass.MINI_BOSS), dmg, pointers)


func test_phase_changes_when_hp_reaches_floor() -> void:
	var s := _boss([0.68, 0.33], 12)
	var e := PhaseFixture.aim(s)
	e.hp = 80
	var r := s.apply(CombatAction.end_turn())
	var resolved := r.resolved_state.get_combatant(&"enemy_0")
	assert_eq(resolved.hp, 68)
	assert_eq(resolved.phase_index, 1, "HP on the floor: the phase starts")
	# The phase event comes after every hit of the resolve, not mid-resolve.
	var last_hit := -1
	for i in r.events.size():
		if String(r.events[i].get("type", "")) == "damage":
			last_hit = i
	assert_gt(CombatFixture.index_of_event(r, "boss_phase"), last_hit)


func test_later_hits_in_same_resolve_lost() -> void:
	var s := _boss([0.68, 0.33], 20, [0, 10])
	var e := PhaseFixture.aim(s)
	e.hp = 80
	var r := s.apply(CombatAction.end_turn())
	var hits := CombatFixture.events_of(r, "damage")
	assert_eq(hits.size(), 2)
	assert_eq(int(hits[0]["hp_damage"]), 12)
	assert_eq(int(hits[0]["parked"]), 8)
	assert_eq(int(hits[1]["hp_damage"]), 0, "needle 2 deals 0: the new phase has not begun")
	assert_eq(int(hits[1]["parked"]), 20)
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").hp, 68)


func test_one_transition_per_resolve() -> void:
	var s := _boss([0.68, 0.33], 90)
	var e := PhaseFixture.aim(s)
	e.hp = 100
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "boss_phase").size(), 1)
	var after := r.resolved_state.get_combatant(&"enemy_0")
	assert_eq(after.phase_index, 1, "P1 -> P2 only")
	assert_eq(after.hp, 68)
	e = PhaseFixture.aim(s)
	r = s.apply(CombatAction.end_turn())
	after = r.resolved_state.get_combatant(&"enemy_0")
	assert_eq(after.hp, 33, "parks at the next floor")
	assert_eq(after.phase_index, 2, "P3 waits for the next resolve")


func test_hp_set_below_two_floors_still_one_phase_per_resolve() -> void:
	var s := _boss([0.68, 0.33], 0)
	var e := PhaseFixture.aim(s)
	e.hp = 20
	var r := s.apply(CombatAction.end_turn())
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").phase_index, 1)
	PhaseFixture.aim(s)
	r = s.apply(CombatAction.end_turn())
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").phase_index, 2)


func test_new_floor_set_after_change() -> void:
	var s := _boss([0.68, 0.33], 12)
	var e := PhaseFixture.aim(s)
	assert_eq(e.hp_floor(), 68)
	e.hp = 80
	s.apply(CombatAction.end_turn())
	e = s.state.get_combatant(&"enemy_0")
	assert_eq(e.hp_floor(), 33, "the next threshold")
	e.hp = 34
	PhaseFixture.aim(s)
	s.apply(CombatAction.end_turn())
	e = s.state.get_combatant(&"enemy_0")
	assert_eq(e.phase_index, 2)
	assert_eq(e.hp_floor(), 0, "the last phase has none")


func test_preview_parked_amount_equals_result() -> void:
	for pointers in [[0], [0, 10, 20]]:
		var s := _boss([0.68, 0.33], 10, pointers)
		var e := PhaseFixture.aim(s)
		e.hp = 75
		var before := s.state.duplicate_state()
		var pv := s.preview_end_turn()
		var r := s.apply(CombatAction.end_turn())
		var po := CombatOutcome.between(before, pv.resolved_state, pv.events).of(&"enemy_0")
		var ro := CombatOutcome.between(before, r.resolved_state, r.events).of(&"enemy_0")
		assert_eq(int(po["parked"]), int(ro["parked"]), "parked: preview == result (%d needles)" % pointers.size())
		assert_eq(int(po["hp_after"]), int(ro["hp_after"]), "post-clamp HP: preview == result")
		var raw := PhaseFixture.sum_of(r.events, "damage", "amount")
		assert_eq(int(ro["hp_before"]) - int(ro["hp_after"]) + int(ro["parked"]), raw, "loss + parked == raw damage")
		assert_eq(pv.resolved_state.state_hash(), r.resolved_state.state_hash())
	# Single needle: 10 from 75 -> 68, 3 parked; three needles: 7 lost, 23 parked.


func test_preview_flags_phase_change() -> void:
	var s := _boss([0.68, 0.33], 10)
	var e := PhaseFixture.aim(s)
	e.hp = 75
	var before := s.state.duplicate_state()
	var pv := s.preview_end_turn()
	var po := CombatOutcome.between(before, pv.resolved_state, pv.events).of(&"enemy_0")
	assert_eq(int(po["phase_before"]), 0)
	assert_eq(int(po["phase_after"]), 1, "the preview says the phase changes")
	var chips := RealChips.build(s.resolver, before, null, pv.resolved_state, pv.events, &"enemy_0", RC.Status.NONE, 0)
	assert_eq(ResultChipModel.value_of(chips, ResultChipModel.PARKED), 3)


func test_preview_with_block_and_shield() -> void:
	var s := _boss([0.68, 0.33], 30)
	var e := PhaseFixture.aim(s)
	e.hp = 78
	e.block = 10
	e.shield = 5
	var before := s.state.duplicate_state()
	var pv := s.preview_end_turn()
	var o := CombatOutcome.between(before, pv.resolved_state, pv.events).of(&"enemy_0")
	assert_eq(int(o["soaked"]), 15)
	assert_eq(int(o["hp_before"]) - int(o["hp_after"]), 10, "lost 10")
	assert_eq(int(o["parked"]), 5, "parked 5")
	var r := s.apply(CombatAction.end_turn())
	var ro := CombatOutcome.between(before, r.resolved_state, r.events).of(&"enemy_0")
	assert_eq(int(ro["parked"]), 5)


func test_phase_applies_wheel_and_hub_override() -> void:
	var atk := CombatFixture.slice(&"pt_atk", RC.SliceType.SHIM, 4)
	var nul := CombatFixture.slice(&"pt_nul", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var hub := CombatFixture.hub(&"pt_hub", 2)
	var over := CombatFixture.wheel([atk, nul, atk, nul, atk], hub)
	var data := PhaseFixture.enemy(&"pt_over", 100, [0.68], RC.EnemyClass.ELITE)
	data.phases[0].wheel_override = over
	data.phases[0].hub_override = hub
	var s := PhaseFixture.session(data, 40, [0], 1001, [atk, nul, hub])
	PhaseFixture.aim(s)
	s.apply(CombatAction.end_turn())
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(e.phase_index, 1)
	assert_eq(e.wheel.slice_count, 5)
	assert_eq(e.wheel.slice_count * e.wheel.ticks_per_slice(), RC.TICKS, "the layout sums to 30 ticks")
	assert_eq(e.wheel.hub_id, &"pt_hub")
	assert_eq(e.hub_resistance, 2)
