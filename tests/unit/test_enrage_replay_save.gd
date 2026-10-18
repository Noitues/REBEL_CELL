extends GutTest
## Plan 2 N4: the enrage is deterministic. It is a function of the turn counter: seeded
## replays match, no RNG is drawn, a save round-trips mid-enrage, rewind never crosses a
## checkpoint, and a staged undo leaves the step untouched.

const SEEDS: Array[int] = [4242, 4243]


func _data() -> EnemyData:
	return EnrageFixture.enemy(&"enr_rp", RC.EnemyClass.BOSS, 1, 999)


func _play(seed: int, turns: int = 16) -> CombatSession:
	var s := EnrageFixture.session(_data(), 1, seed)
	for t in turns:
		if s.state.is_over():
			break
		EnrageFixture.aim(s)
		s.apply(CombatAction.end_turn())
	return s


func test_seeded_replay_same_hash_through_step_2() -> void:
	for seed in SEEDS:
		var a := _play(seed)
		var b := _play(seed)
		assert_eq(a.state.get_combatant(&"enemy_0").enrage_step, 2, "seed %d reached step 2" % seed)
		assert_eq(a.state_hash(), b.state_hash(), "seed %d" % seed)
		assert_eq(a.rng.state, b.rng.state, "seed %d: same draws" % seed)


func test_hash_includes_enrage_step() -> void:
	var s := EnrageFixture.session(_data())
	var other := s.state.duplicate_state()
	other.get_combatant(&"enemy_0").enrage_step = 1
	assert_ne(other.state_hash(), s.state.state_hash())


func test_enrage_draws_no_rng() -> void:
	var s := EnrageFixture.session(_data())
	s.state.turn = 15
	var e := s.state.get_combatant(&"enemy_0")
	var before := s.rng.state
	var events: Array[Dictionary] = []
	s.resolver.refresh_enrage(s.state, e, events)
	assert_eq(e.enrage_step, 2)
	assert_eq(s.rng.state, before)
	for path in ["res://scripts/data/enrage_data.gd"]:
		var text := FileAccess.get_file_as_string(path)
		for word in ["randi(", "randf(", "randomize("]:
			assert_false(text.contains(word), "%s uses %s" % [path, word])


func test_rewind_within_turn_keeps_step() -> void:
	var s := _play(4242, 9)  # real turns: the checkpoint is turn 10's start
	assert_eq(s.state.turn, 10)
	var applied := s.apply(CombatAction.nudge(s.state.player.id, 1))
	assert_true(applied.ok(), applied.error)
	assert_true(s.can_rewind())
	s.rewind()
	assert_eq(s.state.get_combatant(&"enemy_0").enrage_step, 1)


func test_rewind_cannot_cross_checkpoint() -> void:
	var s := EnrageFixture.session(_data())
	EnrageFixture.to_turn(s, 9)
	EnrageFixture.aim(s)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").enrage_step, 1, "turn 10 began enraged")
	assert_false(s.can_rewind(), "the resolve is a checkpoint")
	assert_false(s.rewind().ok())
	assert_eq(s.state.get_combatant(&"enemy_0").enrage_step, 1)


func test_undo_clean_after_enraged_preview() -> void:
	var s := _play(4242, 14)
	assert_eq(s.state.get_combatant(&"enemy_0").enrage_step, 2)
	var base := s.state_hash()
	s.preview_end_turn()
	assert_eq(s.state_hash(), base, "a preview changes nothing")
	s.apply(CombatAction.nudge(s.state.player.id, 1))
	s.rewind()
	assert_eq(s.state_hash(), base)


func test_save_round_trip_mid_fight_turn_12() -> void:
	var s := _play(4242, 11)
	assert_eq(s.state.turn, 12)
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(e.enrage_step, 1)
	var saved := JSON.parse_string(JSON.stringify(s.to_dict())) as Dictionary
	var loaded := CombatSession.from_dict(s.resolver, saved)
	var le := loaded.state.get_combatant(&"enemy_0")
	assert_eq(le.enrage_step, 1)
	assert_eq(le.enrage_percent, 125)
	assert_eq(loaded.state_hash(), s.state_hash())
	EnrageFixture.aim(s)
	EnrageFixture.aim(loaded)
	var a := s.apply(CombatAction.end_turn())
	var b := loaded.apply(CombatAction.end_turn())
	assert_eq(b.resolved_state.state_hash(), a.resolved_state.state_hash(), "the next resolve matches a control run")


func test_unenraged_fights_save_as_before() -> void:
	var s := EnrageFixture.session(_data())
	assert_false(s.state.get_combatant(&"enemy_0").to_dict().has("enrage_step"), "no new key before step 1: hashes unchanged")


func test_old_save_without_enrage_loads() -> void:
	var c := CombatantState.from_dict({"id": "enemy_0", "hp": 50, "max_hp": 100})
	assert_eq(c.enrage_step, 0)
	assert_eq(c.enrage_percent, RC.PERCENT_MAX)
	assert_eq(c.enrage_resistance, 0)


func test_two_enemies_enrage_independently() -> void:
	var boss := _data()
	var normal := EnrageFixture.enemy(&"enr_rp_n", RC.EnemyClass.NORMAL, 1, 999)
	var cls := PhaseFixture.operative(&"enr_rp_op", 0)
	var s := CombatSession.start(CombatFixture.resolver([cls, boss, normal]), cls.id, [boss.id, normal.id], 4242)
	EnrageFixture.to_turn(s, 10)
	assert_eq(s.state.get_combatant(&"enemy_0").enrage_step, 1)
	assert_eq(s.state.get_combatant(&"enemy_1").enrage_step, 0)
