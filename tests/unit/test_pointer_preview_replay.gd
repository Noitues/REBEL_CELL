extends GutTest
## Plan 2 N11: uneven and adjacent pointers (Q27: every needle resolves and shows on the
## preview) go through one placement path, so the preview's pointer ticks, slices and tiers
## equal the resolve's; seeded replays match, rewind never crosses the turn checkpoint and
## pointer placement draws no RNG.

const SEED := 1101


## An operative with needles on `player_ptrs` (SHIM 2 each) against a 5000 HP enemy whose
## SHIM 1 wheel has needles on `enemy_ptrs`.
func _session(seed: int, player_ptrs: Array = [0, 1], enemy_ptrs: Array = [0, 14]) -> CombatSession:
	var hit := CombatFixture.slice(&"ppr_hit", RC.SliceType.SHIM, 1)
	var wheel := CombatFixture.wheel([hit, hit, hit, hit, hit, hit], null, enemy_ptrs)
	var data := CombatFixture.enemy(&"ppr_enemy", 5000, wheel)
	return PhaseFixture.session(data, 2, player_ptrs, seed, [hit])


## The pointer events of `r` as [owner, index, tick, slice, tier] rows.
func _pointer_rows(r: CombatResult) -> Array:
	var rows: Array = []
	for ev in CombatFixture.events_of(r, "pointer"):
		rows.append([ev["owner"], ev["pointer_index"], ev["tick"], ev["slice_index"], ev["tier"]])
	return rows


func test_preview_equals_result_over_200_seeded_turns() -> void:
	var turns := 0
	for k in 40:
		var s := _session(SEED + k)
		for t in 20:
			if s.state.outcome != CombatState.Outcome.NONE or turns >= 200:
				break
			var p := s.preview_end_turn()
			var hp_preview := p.resolved_state.get_combatant(&"enemy_0").hp
			var r := s.apply(CombatAction.end_turn())
			var rows := _pointer_rows(r)
			assert_eq(_pointer_rows(p), rows, "seed %d turn %d: previewed ticks, slices and tiers" % [SEED + k, t])
			assert_eq(rows.size(), 4, "every needle resolves: 2 + 2")
			assert_eq(hp_preview, s.state.get_combatant(&"enemy_0").hp, "seed %d turn %d: previewed damage" % [SEED + k, t])
			turns += 1
	assert_eq(turns, 200)


func test_preview_equals_result_after_a_nudge_puts_a_needle_on_a_boundary() -> void:
	var s := _session(SEED)
	CombatFixture.land(s.state.player, 0, 1)  # needles on ticks 1 and 2
	var r := s.apply(CombatAction.nudge(s.state.player.id, 1))
	assert_eq(r.error, "")
	var p := s.preview_end_turn()
	var rows := _pointer_rows(s.apply(CombatAction.end_turn()))
	assert_eq(_pointer_rows(p), rows)
	var mine := rows.filter(func(row: Array) -> bool: return row[0] == s.state.player.id)
	assert_eq([mine[0][2], mine[1][2]], [2, 3], "tick 3 sits on the next slice's edge")
	assert_eq([mine[0][3], mine[1][3]], [0, 1])


func test_seeded_replay_matches_with_uneven_pointers() -> void:
	var s := _session(SEED)
	for t in 5:
		s.apply(CombatAction.end_turn())
	var again := CombatSession.replay(s.resolver, s.setup, SEED, s.history)
	assert_eq(again.state_hash(), s.state_hash())
	assert_eq(again.state.get_combatant(&"enemy_0").wheel.pointer_ticks, PackedInt32Array([0, 14]))


func test_rewind_restores_pointers_and_never_crosses_the_turn_checkpoint() -> void:
	var s := _session(SEED)
	var before := s.state.player.wheel.rotation
	s.apply(CombatAction.nudge(s.state.player.id, 1))
	assert_true(s.can_rewind())
	s.rewind()
	assert_eq(s.state.player.wheel.rotation, before)
	assert_eq(s.state.player.wheel.pointer_ticks, PackedInt32Array([0, 1]))
	s.apply(CombatAction.end_turn())
	assert_false(s.can_rewind(), "the respin checkpoint is not crossed")


func test_extra_pointer_placement_draws_no_rng() -> void:
	var boss := PhaseFixture.enemy(&"ppr_boss", 300, [0.66, 0.33])
	var cls := PhaseFixture.operative(&"ppr_op", 1)
	var resolver := CombatFixture.resolver([boss, cls])
	var states: Array = []
	for extra in [0, 2]:
		var s := CombatSession.start(resolver, cls.id, [boss.id], SEED, &"", 0, {"boss_extra_pointer": extra})
		states.append(s.rng.state)
		if extra == 2:
			assert_eq(s.state.get_combatant(&"enemy_0").wheel.pointer_ticks, PackedInt32Array([0, 15, 10]))
	assert_eq(states[0], states[1], "the same draws with or without extra pointers")
