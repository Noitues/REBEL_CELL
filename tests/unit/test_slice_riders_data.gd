extends GutTest
## Plan 2 N20: the four SliceData riders (hits, hits_per_target_status + hits_per_status_slice,
## perfect_multiplier, pierce). Defaults leave a slice as it was; validate() names each bad
## combination; a save keeps them; no shipped slice is refused. No hit cap (ruling Q40).


func _shim(id: StringName = &"rd_shim") -> SliceData:
	return CombatFixture.slice(id, RC.SliceType.SHIM, 5)


func _codes(s: SliceData) -> String:
	return ",".join(s.validate())


func test_defaults_leave_slice_unchanged() -> void:
	var s := SliceData.new()
	assert_eq([s.hits, s.hits_per_target_status, s.hits_per_status_slice, s.perfect_multiplier, s.pierce],
		[1, RC.Status.NONE, 0, 1.0, false])
	assert_false(s.has_riders())
	assert_eq(_shim().validate().size(), 0)


func test_validate_rejects_hits_below_1() -> void:
	var s := _shim()
	s.hits = 0
	assert_string_contains(_codes(s), "hits_lt_1")


func test_validate_has_no_hit_cap() -> void:
	var s := _shim()
	s.hits = 64
	assert_eq(s.validate().size(), 0, "Q40: no hit cap")


func test_validate_rejects_non_positive_perfect_multiplier() -> void:
	for m: float in [0.0, -1.0]:
		var s := _shim()
		s.perfect_multiplier = m
		assert_string_contains(_codes(s), "perfect_multiplier_not_positive")


func test_validate_rejects_count_without_status() -> void:
	var s := _shim()
	s.hits_per_status_slice = 2
	assert_string_contains(_codes(s), "hits_per_status_without_status")


func test_validate_rejects_status_without_count() -> void:
	var s := _shim()
	s.hits_per_target_status = RC.Status.CORRUPTED
	assert_string_contains(_codes(s), "hits_per_status_lt_1")
	s.hits_per_status_slice = 1
	assert_eq(s.validate().size(), 0)


func test_validate_rejects_riders_on_non_damage_slices() -> void:
	for t: int in [RC.SliceType.DEFRAG, RC.SliceType.SANDBOX, RC.SliceType.DETOUR, RC.SliceType.HOTFIX, RC.SliceType.TROJAN, RC.SliceType.NULL]:
		var s := CombatFixture.slice(&"rd_def", t, 3)
		s.hits = 3
		assert_string_contains(_codes(s), "riders_on_non_damage", RC.SliceType.keys()[t])
		var p := CombatFixture.slice(&"rd_def_p", t, 3)
		p.pierce = true
		assert_string_contains(_codes(p), "riders_on_non_damage", "pierce on %s" % RC.SliceType.keys()[t])


func test_overflow_takes_riders() -> void:
	var s := CombatFixture.slice(&"rd_crit", RC.SliceType.OVERFLOW, 10)
	s.perfect_multiplier = 4.0
	s.pierce = true
	s.hits = 2
	assert_eq(s.validate().size(), 0)


func test_tres_round_trip_keeps_riders() -> void:
	var s := _shim(&"rd_round")
	s.hits = 3
	s.hits_per_target_status = RC.Status.CORRUPTED
	s.hits_per_status_slice = 2
	s.perfect_multiplier = 4.0
	s.pierce = true
	var path := "user://test_slice_riders_round.tres"
	assert_eq(ResourceSaver.save(s, path), OK)
	var back := ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE) as SliceData
	assert_not_null(back)
	assert_eq([back.hits, back.hits_per_target_status, back.hits_per_status_slice, back.perfect_multiplier, back.pierce],
		[3, RC.Status.CORRUPTED, 2, 4.0, true])
	assert_eq(back.validate().size(), 0)
	DirAccess.remove_absolute(path)


func test_shipped_slices_have_no_rider_errors() -> void:
	var dir := DirAccess.open("res://content/slices")
	assert_not_null(dir)
	var checked := 0
	for f in dir.get_files():
		if not f.ends_with(".tres"):
			continue
		var s := load("res://content/slices/" + f) as SliceData
		if s == null:
			continue
		checked += 1
		assert_eq(s.rider_errors().size(), 0, f)
	assert_gt(checked, 0)
