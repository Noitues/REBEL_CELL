extends GutTest
## Plan 2 N11: phase pointer changes (MULTIPLY / MIGRATE / ORBIT, GDD 2.11) take any tick
## 0-29; the ICE extra pointer keeps the legacy 15 / 10 / 20 / 5 / 25 placement (now config);
## validate refuses out-of-range ticks, duplicates (Q27) and more pointers than the config cap.

## The removed EXTRA_POINTER_OFFSETS, kept here only as the golden reference.
const LEGACY_OFFSETS := [15, 10, 20, 5, 25]


## A mini-boss whose one phase (at 50 %) has `behavior` with `ticks`, and a session on it.
func _session(behavior: int, ticks: Array, orbit: int = 0) -> CombatSession:
	var data := PhaseFixture.enemy(&"pp_boss", 100, [0.5], RC.EnemyClass.MINI_BOSS)
	data.phases[0].pointer_behavior = behavior
	data.phases[0].pointer_ticks = PackedInt32Array(ticks)
	data.phases[0].orbit_ticks_per_turn = orbit
	var s := PhaseFixture.session(data, 0)
	s.state.get_combatant(&"enemy_0").hp = 50  # at the floor: the phase is entered this resolve
	return s


func test_multiply_takes_uneven_layouts() -> void:
	for ticks in [[0, 14], [0, 11], [0, 13], [0, 1]]:
		var s := _session(RC.PointerBehavior.MULTIPLY, ticks)
		s.apply(CombatAction.end_turn())
		assert_eq(s.state.get_combatant(&"enemy_0").wheel.pointer_ticks, PackedInt32Array(ticks), "MULTIPLY to %s" % [ticks])


func test_migrate_to_tick_13_is_telegraphed_then_applied_next_turn() -> void:
	var s := _session(RC.PointerBehavior.MIGRATE, [13])
	var p := s.preview_end_turn()
	var pe := p.resolved_state.get_combatant(&"enemy_0")
	assert_eq(pe.wheel.pending_pointer_ticks, PackedInt32Array([13]), "turn N: telegraphed")
	assert_eq(pe.wheel.pointer_ticks, PackedInt32Array([0]), "turn N: still on the old tick")
	var r := s.apply(CombatAction.end_turn())
	var tele := CombatFixture.index_of_event(r, "boss_migrate_telegraph")
	var moved := CombatFixture.index_of_event(r, "boss_migrate")
	assert_true(tele >= 0 and moved > tele, "the move comes at the next start of turn, after the telegraph")
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.pointer_ticks, PackedInt32Array([13]))


func test_orbit_3_from_tick_28_reads_1_and_the_trail_matches_the_turns() -> void:
	var w := WheelState.from_wheel_data(CombatFixture.null_wheel(0, null, [28]))
	w.pointer_orbit = 3
	assert_eq(w.orbit_ticks_after(1), PackedInt32Array([1]), "28 + 3 wraps to 1")
	var s := _session(RC.PointerBehavior.ORBIT, [28, 29], 3)
	s.apply(CombatAction.end_turn())
	var e := s.state.get_combatant(&"enemy_0")
	var trail: Array = []
	for k in range(1, 4):
		trail.append(e.wheel.orbit_ticks_after(k))
	var actual: Array = []
	for k in 3:
		s.apply(CombatAction.end_turn())
		actual.append(s.state.get_combatant(&"enemy_0").wheel.pointer_ticks)
	assert_eq(actual, trail, "the trail shows the ticks the next 3 turns read")


## The pre-N11 placement: `count` extra pointers at the first free legacy offset.
func _legacy_extra(ticks: PackedInt32Array, count: int) -> PackedInt32Array:
	var out := ticks.duplicate()
	if out.is_empty():
		return out
	for i in count:
		for offset in LEGACY_OFFSETS:
			var tick := posmod(out[0] + int(offset), RC.TICKS)
			if not out.has(tick):
				out.append(tick)
				break
	return out


func test_default_extra_pointers_keep_the_legacy_15_and_10_spacing() -> void:
	var cfg := CombatFixture.config()
	assert_eq(cfg.boss_extra_pointer_offsets, PackedInt32Array(LEGACY_OFFSETS))
	assert_eq(CampaignConfigData.new().boss_extra_pointer_offsets, PackedInt32Array(LEGACY_OFFSETS), "schema default too")
	assert_eq(CombatResolver.with_extra_pointers(PackedInt32Array([0]), 2, cfg.boss_extra_pointer_offsets), PackedInt32Array([0, 15, 10]))


func test_golden_every_shipped_enemy_layout_is_unchanged() -> void:
	var resolver := CombatFixture.resolver()
	var diffs: Array = []
	var checked := 0
	for id in ContentRegistry.all_ids():
		var data := ContentRegistry.get_content(id) as EnemyData
		if data == null or data.wheel == null:
			continue
		var layouts: Array[PackedInt32Array] = [data.wheel.pointer_ticks]
		for p in data.phases:
			if p != null:
				layouts.append(p.pointer_ticks)
		for ticks in layouts:
			for extra in 3:
				for removal in 2:
					var s := CombatState.new()
					s.flags["boss_extra_pointer"] = extra
					s.flags["boss_pointer_removal"] = removal
					var legacy := _legacy_extra(ticks, extra if data.is_boss else 0)
					legacy = legacy.duplicate() if removal <= 0 else legacy.slice(0, maxi(1, legacy.size() - removal))
					checked += 1
					if resolver.phase_layout(s, data, ticks) != legacy:
						diffs.append("%s %s +%d -%d" % [id, ticks, extra, removal])
	assert_gt(checked, 0)
	assert_eq(diffs, [], "0 diffs against the legacy constants")


func test_validate_names_range_duplicate_and_cap() -> void:
	var data := PhaseFixture.enemy(&"pp_cap", 100, [0.5], RC.EnemyClass.MINI_BOSS)
	data.phases[0].pointer_behavior = RC.PointerBehavior.MULTIPLY
	data.phases[0].pointer_ticks = PackedInt32Array([0, 14])
	var cfg := CampaignConfigData.new()
	assert_false("pointer" in " ".join(data.validate(cfg)), "an uneven layout is valid")
	data.phases[0].pointer_ticks = PackedInt32Array([0, 1, 2, 3, 4])
	assert_true("too_many_pointers" in " ".join(data.validate(cfg)), "5 pointers over the cap of %d" % cfg.max_pointers)
	cfg.max_pointers = 5
	assert_false("too_many_pointers" in " ".join(data.validate(cfg)), "the cap is read from the config")
	data.phases[0].pointer_ticks = PackedInt32Array([0, 30])
	assert_true("pointer_tick_out_of_range" in " ".join(data.validate(cfg)))
	data.phases[0].pointer_ticks = PackedInt32Array([4, 4])
	assert_true("pointer_ticks_duplicate" in " ".join(data.validate(cfg)))
	data.wheel.pointer_ticks = PackedInt32Array([9, 9])
	assert_true("pointer_ticks_duplicate" in " ".join(data.wheel.validate()), "the base wheel too")


func test_every_shipped_enemy_pointer_layout_validates() -> void:
	var cfg := CombatFixture.config()
	var ids := ContentRegistry.all_ids()
	ids.sort()
	for id in ids:
		var data := ContentRegistry.get_content(id) as EnemyData
		if data == null:
			continue
		for problem in data.validate(cfg):
			assert_false(problem.begins_with("pointer_") or problem.begins_with("too_many_pointers"), "%s: %s" % [id, problem])
