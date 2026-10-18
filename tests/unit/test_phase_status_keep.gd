extends GutTest
## Plan 2 N3 (R6): a phase's wheel override keeps statuses, each moved to the new slice that
## covers the old slice's centre tick (same statuses merge); cleanse_on_enter clears exactly
## the stated side, after the remap.


func _remap(old: Array, old_count: int, new_count: int) -> Array[int]:
	var typed: Array[int] = []
	for v in old:
		typed.append(int(v))
	return WheelState.remap_statuses(typed, old_count, new_count)


## An elite whose phase swaps in a `new_count`-slice wheel, with `cleanse`.
func _session(new_count: int, cleanse: int = RC.CleanseScope.NONE) -> CombatSession:
	var nul := CombatFixture.slice(&"ps_nul", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var slices: Array = []
	for k in new_count:
		slices.append(nul)
	var data := PhaseFixture.enemy(&"ps_elite", 100, [0.68], RC.EnemyClass.ELITE)
	data.phases[0].wheel_override = CombatFixture.wheel(slices)
	data.phases[0].cleanse_on_enter = cleanse
	return PhaseFixture.session(data, 40, [0], 1001, [nul])


func test_status_kept_across_override() -> void:
	var s := _session(6)
	var e := PhaseFixture.aim(s)
	e.wheel.slice_statuses[2] = RC.Status.CORRUPTED
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "boss_wheel_override").size(), 1)
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").wheel.slice_statuses[2], RC.Status.CORRUPTED, "CORRUPTED on slice 2 stays")


func test_remap_to_slice_covering_old_centre_tick() -> void:
	# Old 6-slice slot 2 is centred on tick 10; on a 5-slice wheel (centres 0, 6, 12, 18, 24)
	# tick 10 is nearest 12: slot 2. Old slot 4 (tick 20) -> 18: slot 3.
	var out := _remap([0, 0, RC.Status.CORRUPTED, 0, RC.Status.OVERCLOCKED, 0], 6, 5)
	assert_eq(out, [0, 0, RC.Status.CORRUPTED, RC.Status.OVERCLOCKED, 0] as Array[int])
	var s := _session(5)
	var e := PhaseFixture.aim(s)
	e.wheel.slice_statuses[2] = RC.Status.CORRUPTED
	var r := s.apply(CombatAction.end_turn())
	var w := r.resolved_state.get_combatant(&"enemy_0").wheel
	assert_eq(w.slice_statuses.size(), 5)
	assert_eq(w.slice_statuses[WheelState.covering_slot(10, 5)], RC.Status.CORRUPTED)


func test_two_old_slices_land_on_one_new_merge_stacks() -> void:
	# Old 6-slice slots 0 and 1 (ticks 0, 5) both land on a 3-slice wheel's slot 0 (0, 10, 20):
	# tick 5 is a boundary between 0 and 10 -> the lower index. Before N8 statuses carry no
	# stacks, so the same status merges into one.
	var out := _remap([RC.Status.CORRUPTED, RC.Status.CORRUPTED, 0, 0, 0, 0], 6, 3)
	assert_eq(out, [RC.Status.CORRUPTED, 0, 0] as Array[int])
	var mixed := _remap([RC.Status.OVERCLOCKED, RC.Status.CORRUPTED, 0, 0, 0, 0], 6, 3)
	assert_eq(mixed[0], RC.Status.OVERCLOCKED, "different statuses: the first in old slot order stays")


func test_centre_on_boundary_tiebreak() -> void:
	assert_eq(WheelState.covering_slot(5, 3), 0, "tick 5 between centres 0 and 10: lower index")
	assert_eq(WheelState.covering_slot(15, 3), 1, "tick 15 between 10 and 20: lower index")
	assert_eq(WheelState.covering_slot(25, 3), 0, "tick 25 between 20 and 0 (30): index 0 is lower")
	assert_eq(WheelState.covering_slot(10, 6), 2, "on a centre: that slot")


func test_status_on_null_slice_kept() -> void:
	# The new wheel is all NULL: the status still moves onto it.
	var s := _session(6)
	var e := PhaseFixture.aim(s)
	e.wheel.slice_statuses[4] = RC.Status.OVERCLOCKED
	var r := s.apply(CombatAction.end_turn())
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").wheel.slice_statuses[4], RC.Status.OVERCLOCKED)


func test_cleanse_none_own_player_both() -> void:
	var cases := {
		RC.CleanseScope.NONE: [true, true],
		RC.CleanseScope.OWN: [false, true],
		RC.CleanseScope.PLAYER: [true, false],
		RC.CleanseScope.BOTH: [false, false],
	}
	for scope in cases:
		var s := _session(6, scope)
		var e := PhaseFixture.aim(s)
		e.wheel.slice_statuses[3] = RC.Status.CORRUPTED
		s.state.player.wheel.slice_statuses[3] = RC.Status.CORRUPTED
		var r := s.apply(CombatAction.end_turn())
		var rs := r.resolved_state
		var keep: Array = cases[scope]
		assert_eq(rs.get_combatant(&"enemy_0").wheel.slice_statuses[3] == RC.Status.CORRUPTED, keep[0], "scope %d: enemy side" % scope)
		assert_eq(rs.player.wheel.slice_statuses[3] == RC.Status.CORRUPTED, keep[1], "scope %d: operative side" % scope)


func test_cleanse_on_enter_runs_after_remap() -> void:
	# Remapped onto a 5-slice wheel, then OWN clears it: nothing survives anywhere.
	var s := _session(5, RC.CleanseScope.OWN)
	var e := PhaseFixture.aim(s)
	e.wheel.slice_statuses[2] = RC.Status.CORRUPTED
	var r := s.apply(CombatAction.end_turn())
	var w := r.resolved_state.get_combatant(&"enemy_0").wheel
	assert_eq(w.slice_statuses.size(), 5)
	for st in w.slice_statuses:
		assert_eq(st, RC.Status.NONE)
	var override_at := CombatFixture.index_of_event(r, "boss_wheel_override")
	var cleanse_at := CombatFixture.index_of_event(r, "cleanse", "target", &"enemy_0")
	assert_gt(cleanse_at, override_at, "cleanse after the remap")


func test_override_with_variable_sizes() -> void:
	pending("needs N12 (slice sizes 0-30)")


func test_encrypted_survives_and_still_absorbs() -> void:
	var s := _session(6)
	var e := PhaseFixture.aim(s)
	e.wheel.slice_statuses[1] = RC.Status.ENCRYPTED
	var r := s.apply(CombatAction.end_turn())
	e = r.resolved_state.get_combatant(&"enemy_0")
	assert_eq(e.phase_index, 1)
	assert_eq(e.wheel.slice_statuses[1], RC.Status.ENCRYPTED, "kept")
	var events: Array[Dictionary] = []
	var applied := s.resolver.fx.apply_status(e, 1, RC.Status.CORRUPTED, events)
	assert_false(applied, "ENCRYPTED still absorbs a status")
	assert_eq(e.wheel.slice_statuses[1], RC.Status.NONE, "and is spent doing so")
