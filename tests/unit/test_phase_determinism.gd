extends GutTest
## Plan 2 N3: phases and parking are deterministic: seeded replays match, parking draws no
## RNG, rewind never crosses the checkpoint a phase-changing resolve made, a staged undo
## leaves HP / floor / phase untouched, and a save mid-phase round-trips.

const SEEDS: Array[int] = [1001, 1002]


func _data() -> EnemyData:
	return PhaseFixture.enemy(&"pd_boss", 120, [0.68, 0.33], RC.EnemyClass.MINI_BOSS)


func _play(seed: int) -> CombatSession:
	var s := PhaseFixture.session(_data(), 15, [0, 10], seed)
	for t in 8:
		if s.state.is_over():
			break
		PhaseFixture.aim(s)
		s.apply(CombatAction.end_turn())
	return s


func test_same_seed_same_inputs_same_hash() -> void:
	for seed in SEEDS:
		var a := _play(seed)
		var b := _play(seed)
		assert_eq(a.state_hash(), b.state_hash(), "seed %d" % seed)
		assert_eq(a.rng.state, b.rng.state, "seed %d: same draws" % seed)
	var c := _play(SEEDS[0])
	assert_gt(c.state.get_combatant(&"enemy_0").phase_index, 0, "the fight went through a phase")


func test_parking_uses_no_rng() -> void:
	var s := PhaseFixture.session(_data(), 60)
	var e := PhaseFixture.aim(s)
	e.hp = 90
	var rng_before := s.rng.state
	var resolved := s.state.duplicate_state()
	var events: Array[Dictionary] = []
	s.resolver.resolve_turn(resolved, s.rng, events)
	assert_eq(s.rng.state, rng_before, "a parked hit and a phase change draw nothing")
	assert_eq(resolved.get_combatant(&"enemy_0").phase_index, 1)
	assert_eq(resolved.get_combatant(&"enemy_0").hp, 82)


func test_no_global_randi() -> void:
	for path in ["res://scripts/state/wheel_state.gd", "res://scripts/data/boss_phase_data.gd", "res://scripts/state/combatant_state.gd"]:
		var text := FileAccess.get_file_as_string(path)
		for word in ["randi(", "randf(", "randomize("]:
			assert_false(text.contains(word), "%s uses %s" % [path, word])


func test_rewind_cannot_cross_checkpoint_after_phase_change() -> void:
	var s := PhaseFixture.session(_data(), 60)
	PhaseFixture.aim(s)
	s.apply(CombatAction.end_turn())
	var after := s.state.get_combatant(&"enemy_0")
	assert_eq(after.phase_index, 1)
	assert_false(s.can_rewind(), "the resolve (and its respins) is a checkpoint")
	var r := s.rewind()
	assert_false(r.ok())
	assert_eq(s.state.get_combatant(&"enemy_0").phase_index, 1, "undo does not undo the phase")
	assert_eq(s.state.get_combatant(&"enemy_0").hp, after.hp)


func test_undo_clean_staging() -> void:
	var s := PhaseFixture.session(_data(), 60)
	var e := PhaseFixture.aim(s)
	var hp := e.hp
	var floor := e.hp_floor()
	var pv := s.preview_end_turn()
	assert_gt(int(CombatOutcome.between(s.state, pv.resolved_state, pv.events).of(&"enemy_0")["parked"]), 0, "the staged turn parks")
	var nudge := CombatAction.nudge(s.state.player.id, 1)
	var applied := s.apply(nudge)
	assert_true(applied.ok(), applied.error)
	assert_true(s.can_rewind())
	s.rewind()
	e = s.state.get_combatant(&"enemy_0")
	assert_eq(e.hp, hp)
	assert_eq(e.hp_floor(), floor)
	assert_eq(e.phase_index, 0)


func test_save_round_trip_mid_phase() -> void:
	var s := PhaseFixture.session(_data(), 60)
	PhaseFixture.aim(s)
	s.apply(CombatAction.end_turn())
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(e.phase_index, 1)
	assert_eq(e.hp, 82, "parked at the old floor, ceil(120 x 0.68)")
	var saved := JSON.parse_string(JSON.stringify(s.to_dict())) as Dictionary
	var loaded := CombatSession.from_dict(s.resolver, saved)
	var le := loaded.state.get_combatant(&"enemy_0")
	assert_eq(le.phase_index, 1)
	assert_eq(le.next_threshold_bp, e.next_threshold_bp)
	assert_eq(le.hp_floor(), e.hp_floor())
	assert_eq(loaded.state_hash(), s.state_hash())
	PhaseFixture.aim(s)
	PhaseFixture.aim(loaded)
	var a := s.apply(CombatAction.end_turn())
	var b := loaded.apply(CombatAction.end_turn())
	assert_eq(b.resolved_state.state_hash(), a.resolved_state.state_hash(), "the next resolve matches a control run")


func test_fights_without_phases_save_as_before() -> void:
	var data := PhaseFixture.enemy(&"pd_normal", 40, [], RC.EnemyClass.NORMAL)
	var s := PhaseFixture.session(data, 5)
	assert_false(s.state.get_combatant(&"enemy_0").to_dict().has("next_threshold_bp"), "no new key: hashes unchanged")
	assert_false(s.state.player.to_dict().has("next_threshold_bp"))


func test_old_save_without_floor_loads() -> void:
	var c := CombatantState.from_dict({"id": "enemy_0", "hp": 50, "max_hp": 100})
	assert_eq(c.next_threshold_bp, 0)
	assert_eq(c.hp_floor(), 0, "a save without the field loads with no floor (save compatibility not required)")
