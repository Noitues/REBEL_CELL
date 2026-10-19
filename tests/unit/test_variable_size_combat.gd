extends GutTest
## Plan 2 N12 (R10, R11): fights on uneven wheels. Preview == result for nudges and End Turn,
## a seeded replay matches, rewind never crosses a checkpoint, the status remap reads each old
## slice's centre tick, Mirror / Shunt read the actual neighbour, and the tier is the slot's
## sub-tick map (a 4-tick slice is never Perfect).

const OP_SIZES := [6, 4, 4, 6, 4, 6]
## The Genome Core P3 layout (CONTENT_DESIGN_V2 2): uneven, two needles 14 ticks apart.
const ENEMY_SIZES := [5, 4, 3, 4, 4, 3, 4, 3]


func _atk(id: StringName, out: int) -> SliceData:
	return CombatFixture.slice(id, RC.SliceType.SHIM, out)


func _mirror_fw() -> FirmwareData:
	var fw := FirmwareData.new()
	fw.id = &"vsc_mirror"
	fw.neighbor_rule = RC.NeighborRule.MIRROR
	return fw


func _class(firmware: Array = []) -> ClassData:
	var slices := [_atk(&"vsc_a", 6), _atk(&"vsc_b", 7), CombatFixture.slice(&"vsc_def", RC.SliceType.DEFRAG, 5, RC.TargetRule.SELF),
		_atk(&"vsc_c", 8), _atk(&"vsc_d", 9), _atk(&"vsc_e", 10)]
	var w := WheelFixtures.make_layout(OP_SIZES, slices, [], firmware)
	w.hub = CombatFixture.hub(&"vsc_hub")
	var deck: Array[CardData] = []
	for i in 6:
		deck.append(CombatFixture.card(StringName("vsc_card_%d" % i), [CombatFixture.effect(RC.EffectType.NUDGE, RC.EffectTarget.TARGET_WHEEL, 1)], 1))
	return CombatFixture.operative_class(&"vsc_class", 200, w, deck)


func _enemy() -> EnemyData:
	var slices := []
	for i in ENEMY_SIZES.size():
		slices.append(_atk(StringName("vsc_en_%d" % i), 3 + i))
	return CombatFixture.enemy(&"vsc_enemy", 400, WheelFixtures.make_layout(ENEMY_SIZES, slices, [], [], [0, 14]))


func _resolver(firmware: Array = []) -> CombatResolver:
	var cls := _class(firmware)
	var custom: Array = [cls, _enemy(), _mirror_fw()]
	custom.append_array(cls.starting_deck)
	return CombatFixture.resolver(custom)


func _start(seed: int, firmware: Array = []) -> CombatSession:
	return CombatSession.start(_resolver(firmware), &"vsc_class", [&"vsc_enemy"], seed)


func test_wheels_carry_their_sizes_into_the_fight() -> void:
	var s := _start(1)
	assert_eq(s.state.player.wheel.layout(), PackedInt32Array(OP_SIZES))
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.layout(), PackedInt32Array(ENEMY_SIZES))


func test_preview_equals_result_uneven_wheels() -> void:
	var pick := CombatFixture.rng(0x12)
	for seed in 50:
		var s := _start(500 + seed)
		for turn in 3:
			if s.state.is_over():
				break
			for k in 2:
				var a := CombatAction.nudge(&"enemy_0" if pick.randi() % 2 == 0 else &"player", 1 if pick.randi() % 2 == 0 else -1)
				var pv := s.preview(a)
				var real := s.apply(a)
				assert_eq(pv.error, real.error)
				assert_eq(pv.state.state_hash(), real.state.state_hash(), "seed %d nudge preview == result" % seed)
			var end_pv := s.preview_end_turn()
			var end_real := s.apply(CombatAction.end_turn())
			assert_eq(end_pv.state.state_hash(), end_real.resolved_state.state_hash(), "seed %d End Turn preview == result" % seed)


func test_seeded_replay_same_state_hash() -> void:
	var s := _start(77)
	for turn in 10:
		if s.state.is_over():
			break
		s.apply(CombatAction.nudge(&"enemy_0", 1 if turn % 3 == 0 else -1))
		s.apply(CombatAction.end_turn())
	var again := CombatSession.replay(s.resolver, s.setup, 77, s.history)
	assert_eq(again.state.state_hash(), s.state.state_hash())


func test_two_uneven_needles_read_their_own_slots() -> void:
	var s := _start(3)
	var e := s.state.get_combatant(&"enemy_0")
	e.wheel.rotation = 0
	# slots: 28-2 | 3-6 | 7-9 | 10-13 | 14-17 | 18-20 | 21-24 | 25-27
	assert_eq(e.wheel.slice_at(0), 0, "needle 0 on tick 0: slot 0")
	assert_eq(e.wheel.slice_at(1), 4, "needle 1 on tick 14: slot 4")
	var r0: Dictionary = s.resolver._readout(s.state, e, 0)
	var r1: Dictionary = s.resolver._readout(s.state, e, 1)
	assert_eq(r0["tier"], RC.PrecisionTier.PERFECT, "tick 0 is slot 0's centre")
	assert_eq(r1["tier"], RC.PrecisionTier.WEAK, "tick 14 is the first tick of a 4-tick slot: WEAK")
	e.wheel.rotation = 1
	assert_eq(s.resolver._readout(s.state, e, 1)["tier"], RC.PrecisionTier.GOOD, "tick 15: GOOD")


func test_perfect_never_on_a_four_tick_slice() -> void:
	var s := _start(4)
	var p := s.state.player
	for r in 30:
		p.wheel.rotation = r
		var read := s.resolver._readout(s.state, p, 0)
		if p.wheel.slot_size(int(read["slice_index"])) == 4:
			assert_ne(read["tier"], RC.PrecisionTier.PERFECT, "rotation %d" % r)


func test_mirror_firmware_reads_the_actual_neighbor() -> void:
	# Mirror on slot 1 (ticks 3-6, 4 ticks): landing on tick 6 (clockwise half) copies slot 2;
	# on tick 3 (counter-clockwise half) slot 0. A 4-tick slice has no Perfect tick, so never both.
	var s := _start(5, [null, _mirror_fw()])
	var p := s.state.player
	for tick in [3, 4, 5, 6]:
		p.wheel.rotation = tick
		var res: Array = s.resolver._collect_resolutions(s.state)
		var derived := []
		for r in res:
			if r["owner"] == p and r.get("derived", false):
				derived.append(int(r["slice_index"]))
		assert_eq(derived, [0] if tick < 5 else [2], "tick %d" % tick)


func test_mirror_skips_an_empty_arc() -> void:
	var sizes := PackedInt32Array([5, 0, 25])
	assert_eq(WheelMath.neighbor_slot(0, 1, sizes), 2)


func test_status_remap_after_layout_change() -> void:
	var cap := CombatFixture.config().status_stack_cap
	var old: Array[Dictionary] = [{}, {}, {RC.Status.CORRUPTED: 1}, {RC.Status.OVERCLOCKED: 1}, {}, {}]
	# old equal slot 2 is centred on tick 10, which new slot 2 (7-10) owns; slot 3 (15) -> new 3 (11-16)
	var out := WheelState.remap_stacks_sized(old, WheelMath.uniform_sizes(6), PackedInt32Array(OP_SIZES), cap)
	assert_eq(out[2], {RC.Status.CORRUPTED: 1})
	assert_eq(out[3], {RC.Status.OVERCLOCKED: 1})
	# into 3 x 10: old slots 0 (tick 0) and 5 (tick 25) both land on slot 0 (25-4) and merge
	var merge: Array[Dictionary] = [{RC.Status.CORRUPTED: 1}, {}, {}, {}, {}, {RC.Status.CORRUPTED: 1}]
	assert_eq(WheelState.remap_stacks_sized(merge, WheelMath.uniform_sizes(6), PackedInt32Array([10, 10, 10]), cap)[0], {RC.Status.CORRUPTED: 2})
	# an uneven old layout uses its own centre ticks: slot 3 of OP_SIZES (11-16) is centred on 13
	var back: Array[Dictionary] = [{}, {}, {}, {RC.Status.CORRUPTED: 1}, {}, {}]
	assert_eq(WheelState.remap_stacks_sized(back, PackedInt32Array(OP_SIZES), WheelMath.uniform_sizes(6), cap)[3], {RC.Status.CORRUPTED: 1}, "tick 13 is equal slot 3 (13-17)")


func test_rewind_does_not_cross_checkpoint_after_nudge() -> void:
	var s := _start(9)
	var before := s.state.state_hash()
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_true(s.can_rewind())
	s.rewind()
	assert_eq(s.state.state_hash(), before, "undo restores the uneven wheel exactly")
	assert_false(s.can_rewind(), "nothing before the checkpoint")
	s.apply(CombatAction.end_turn())
	assert_false(s.can_rewind(), "End Turn is a checkpoint (random respins)")


func test_geometry_uses_no_rng() -> void:
	var s := _start(11)
	var rng_before := s.rng.state
	var w := s.state.player.wheel
	for t in 30:
		w.slot_of_tick(t)
		WheelMath.snap_delta_in(t, w.layout(), WheelMath.default_quality(4, 1))
	w.flip()
	w.flip()
	assert_eq(s.rng.state, rng_before)
