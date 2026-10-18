extends GutTest
## Plan 2 N11: the save format is unchanged (pointer_ticks was already saved per wheel), so a
## save written before N11 loads with its legacy layout, and authored uneven or adjacent
## ticks survive a round trip.


func _round_trip(s: CombatSession) -> CombatSession:
	var d: Dictionary = JSON.parse_string(JSON.stringify(s.to_dict()))
	return CombatSession.from_dict(s.resolver, d)


func test_round_trip_keeps_authored_uneven_and_adjacent_ticks() -> void:
	var hit := CombatFixture.slice(&"ps_hit", RC.SliceType.SHIM, 1)
	var data := CombatFixture.enemy(&"ps_enemy", 400, CombatFixture.wheel([hit, hit, hit, hit, hit, hit], null, [0, 14, 15]))
	var s := PhaseFixture.session(data, 2, [0, 1], 1101, [hit])
	s.apply(CombatAction.end_turn())
	var back := _round_trip(s)
	assert_eq(back.state.get_combatant(&"enemy_0").wheel.pointer_ticks, PackedInt32Array([0, 14, 15]))
	assert_eq(back.state.player.wheel.pointer_ticks, PackedInt32Array([0, 1]))
	assert_eq(back.state_hash(), s.state_hash())


func test_a_pre_n11_wheel_save_loads_its_legacy_layout() -> void:
	# The shape a pre-N11 save wrote for a boss with one ICE extra pointer (offset 15) and a
	# pending MIGRATE: the same keys N11 reads.
	var legacy := {"rotation": 7, "pointer_ticks": [0, 15], "pending_pointer_ticks": [5, 20]}
	var w := WheelState.from_dict(legacy)
	assert_eq(w.pointer_ticks, PackedInt32Array([0, 15]))
	assert_eq(w.pending_pointer_ticks, PackedInt32Array([5, 20]))
	assert_eq(WheelState.from_dict(w.to_dict()).pointer_ticks, PackedInt32Array([0, 15]))


func test_a_boss_with_an_extra_pointer_saves_and_loads_the_same_ticks() -> void:
	var boss := PhaseFixture.enemy(&"ps_boss", 300, [0.66, 0.33])
	var cls := PhaseFixture.operative(&"ps_op", 1)
	var s := CombatSession.start(CombatFixture.resolver([boss, cls]), cls.id, [boss.id], 1101, &"", 0, {"boss_extra_pointer": 1})
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.pointer_ticks, PackedInt32Array([0, 15]), "legacy offset 15")
	var back := _round_trip(s)
	assert_eq(back.state.get_combatant(&"enemy_0").wheel.pointer_ticks, PackedInt32Array([0, 15]))
	assert_eq(back.state_hash(), s.state_hash())
