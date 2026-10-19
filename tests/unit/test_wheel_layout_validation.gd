extends GutTest
## Plan 2 N12 (R11, Q20): WheelData validation names its reason for every bad layout; the
## slice cap is config (operative 6, enemy 30; an empty arc does not count); every shipped
## enemy still validates.


func _slices(n: int) -> Array:
	var out := []
	for i in n:
		out.append(CombatFixture.slice(StringName("lv_%d" % i), RC.SliceType.SHIM, 5))
	return out


func _has(errors: PackedStringArray, reason: String) -> bool:
	for e in errors:
		if e.begins_with(reason + ":"):
			return true
	return false


func test_sizes_not_summing_30_rejected() -> void:
	assert_true(_has(WheelFixtures.make_layout([5, 5, 5, 5, 5, 4], _slices(6)).validate(), "size_sum"), "29")
	assert_true(_has(WheelFixtures.make_layout([5, 5, 5, 5, 5, 6], _slices(6)).validate(), "size_sum"), "31")
	assert_eq(WheelFixtures.make_layout([6, 4, 4, 6, 4, 6], _slices(6)).validate(), PackedStringArray(), "30 is sound")


func test_size_out_of_range_rejected() -> void:
	assert_true(_has(WheelFixtures.make_layout([32, -2], _slices(2)).validate(), "size_range"))


func test_size_below_config_minimum_rejected() -> void:
	var w := WheelFixtures.make_layout([1, 29], _slices(2))
	assert_eq(w.slice_cap_errors(30, 1), PackedStringArray(), "1 tick is the smallest slice")
	assert_true(_has(w.slice_cap_errors(30, 2), "size_range"), "under a raised minimum")


func test_tick_quality_wrong_length_rejected() -> void:
	var w := WheelFixtures.make_layout([4, 26], _slices(2), [[0, 1, 1]])
	assert_true(_has(w.validate(), "quality_length"))
	var bad := WheelFixtures.make_layout([4, 26], _slices(2), [[0, 1, 7, 0]])
	assert_true(_has(bad.validate(), "quality_tier"))


func test_mixed_auto_and_sized_rejected() -> void:
	var w := WheelFixtures.make_layout([5, 5, 5, 5, 5, 5], _slices(6))
	w.slots[3].size_ticks = RC.SIZE_AUTO
	assert_true(_has(w.validate(), "size_mixed"))


func test_slice_cap_from_config() -> void:
	var cfg := CombatFixture.config()
	assert_eq(cfg.operative_slice_cap, 6)
	assert_eq(cfg.enemy_slice_cap, 30)
	assert_eq(cfg.slice_size_min, 1)
	var ten := WheelFixtures.make_layout([3, 3, 3, 3, 3, 3, 3, 3, 3, 3], _slices(10))
	assert_eq(ten.validate(), PackedStringArray(), "10 slices of 3 are a sound layout")
	assert_eq(ten.slice_cap_errors(cfg.enemy_slice_cap, cfg.slice_size_min), PackedStringArray(), "enemies lift the cap")
	assert_true(_has(ten.slice_cap_errors(cfg.operative_slice_cap, cfg.slice_size_min), "slice_cap"), "operatives stay at 6")


func test_empty_arcs_do_not_count_toward_the_cap() -> void:
	var w := WheelFixtures.make_layout([5, 0, 5, 5, 0, 5, 5, 5], _slices(8))
	assert_eq(w.validate(), PackedStringArray())
	assert_eq(w.slice_cap_errors(6, 1), PackedStringArray(), "8 slots, 6 slices")


func test_missing_size_ticks_defaults_to_equal_share() -> void:
	var w := CombatFixture.wheel(_slices(6))
	assert_eq(w.slots[0].size_ticks, RC.SIZE_AUTO)
	assert_eq(w.slot_sizes(), PackedInt32Array([5, 5, 5, 5, 5, 5]), "6 slots read 5 ticks each")
	assert_eq(w.validate(), PackedStringArray())
	assert_eq(CombatFixture.wheel(_slices(3)).slot_sizes(), PackedInt32Array([10, 10, 10]), "a satellite's 3 slots")


func test_operative_class_over_the_cap_rejected() -> void:
	var cls := CombatFixture.operative_class(&"lv_cls", 50, WheelFixtures.make_layout([3, 3, 3, 3, 3, 3, 3, 3, 3, 3], _slices(10)), [])
	assert_true(_has(cls.validate(CombatFixture.config()), "slice_cap"))


func test_validate_content_all_enemies_pass() -> void:
	var cfg := CombatFixture.config()
	var n := 0
	for id in ContentRegistry.all_ids():
		var e := ContentRegistry.get_content(id) as EnemyData
		if e == null:
			continue
		for problem in e.validate(cfg):
			assert_false(problem.begins_with("size_") or problem.begins_with("slice_cap") or problem.begins_with("quality_"), "%s: %s" % [e.id, problem])
		n += 1
	assert_true(n > 10, "checked %d enemies" % n)
