extends GutTest
## Plan 2 N12 (R11): the loadout's sub-tick map per slice and the wheel's wedge arcs both come
## from WheelMath's boundaries (one flow test for the view glue).


func _lookup(custom: Array = []) -> ContentLookup:
	var l := ContentLookup.new().add_registry(ContentRegistry)
	for r in custom:
		l.add(r)
	return l


func test_loadout_shows_map_string_per_slice() -> void:
	var cls := ContentRegistry.get_content(&"breaker") as ClassData
	var op := OperativeState.from_class(cls, &"op_1", "Vex")
	var maps := LoadoutView.subtick_maps(op, _lookup(), CombatFixture.config())
	assert_eq(maps.size(), 6)
	for m in maps:
		assert_eq(m, "W G P G W", "a 5-tick slice")


func test_loadout_map_for_an_uneven_class() -> void:
	var slices := []
	for i in 3:
		slices.append(CombatFixture.slice(StringName("lsm_%d" % i), RC.SliceType.SHIM, 5))
	var fw := FirmwareData.new()
	fw.id = &"lsm_calibrated"
	fw.tick_quality_step = 1
	var w := WheelFixtures.make_layout([4, 7, 19], slices, [], [fw])
	w.hub = CombatFixture.hub(&"lsm_hub")
	var cls := CombatFixture.operative_class(&"lsm_class", 50, w, [])
	var op := OperativeState.from_class(cls, &"op_1", "Ash")
	var maps := LoadoutView.subtick_maps(op, _lookup([cls, fw] + slices), CombatFixture.config())
	assert_eq(maps[0], "G P P G", "Calibrated on W G G W")
	assert_eq(maps[1], "W W G P G W W")


func test_wedge_angles_match_wheelmath_boundaries() -> void:
	for seed in 50:
		var sizes := WheelFixtures.random_sizes(seed)
		var w := WheelFixtures.state(sizes)
		var starts := WheelMath.slot_starts(sizes)
		var covered := 0.0
		for i in sizes.size():
			var arc := WheelView.slot_arc_ticks(w, i)
			assert_almost_eq(arc.y - arc.x, float(sizes[i]), 0.001, "seed %d slot %d span" % [seed, i])
			assert_almost_eq(fposmod(arc.x + 0.5, 30.0), float(starts[i]), 0.001, "seed %d slot %d starts on its boundary" % [seed, i])
			if i + 1 < sizes.size():
				assert_almost_eq(arc.y, WheelView.slot_arc_ticks(w, i + 1).x, 0.001, "seed %d: arcs %d and %d meet" % [seed, i, i + 1])
			covered += arc.y - arc.x
		assert_almost_eq(covered, 30.0, 0.001, "seed %d: the arcs cover the wheel once" % seed)
