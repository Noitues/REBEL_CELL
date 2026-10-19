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


func test_disc_shader_spans_equal_wheelmath_boundaries() -> void:
	var uneven := PackedInt32Array([6, 0, 4, 4, 6, 10])
	var spans := WheelDisc.slot_spans(uneven, WheelView.DEG_PER_TICK)
	assert_eq(spans.size(), WheelDisc.MAX_SLICES)
	var starts := WheelMath.slot_starts(uneven)
	for i in uneven.size():
		var next := starts[i + 1] if i + 1 < uneven.size() else starts[0] + RC.TICKS
		assert_almost_eq(spans[i], float(posmod(next - starts[i], RC.TICKS)) * WheelView.DEG_PER_TICK, 0.001, "slot %d span = boundary gap" % i)
		assert_almost_eq(spans[i], float(uneven[i]) * WheelView.DEG_PER_TICK, 0.001, "slot %d span = its size" % i)
	assert_eq(spans[1], 0.0, "an empty arc draws no span")
	assert_eq(spans[6], 0.0, "unused shader slots are 0")
	for seed in 50:
		var sizes := WheelFixtures.random_sizes(seed)
		if sizes.size() > WheelDisc.MAX_SLICES:
			continue
		var total := 0.0
		for v in WheelDisc.slot_spans(sizes, WheelView.DEG_PER_TICK):
			total += v
		assert_almost_eq(total, 360.0, 0.01, "seed %d: the spans fill the disc" % seed)
