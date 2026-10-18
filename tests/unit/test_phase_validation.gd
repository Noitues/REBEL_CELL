extends GutTest
## Plan 2 N3 (R1): phase counts per class (base phase included, from campaign_config),
## strictly descending thresholds inside (0, 1), and cleanse_on_enter. Each failure names its
## reason and carries the content id.

var _config: CampaignConfigData


func before_all() -> void:
	_config = CombatFixture.config()


## R1's table as the spec gives it (the shipped boss minimum is a placeholder: DECISIONS N3).
func _spec_config() -> CampaignConfigData:
	var c := CampaignConfigData.new()
	c.phase_count_min_by_class = PackedInt32Array([1, 1, 2, 4])
	c.phase_count_max_by_class = PackedInt32Array([1, 2, 3, 5])
	return c


func _errors(cls: int, thresholds: Array, config: CampaignConfigData = null) -> PackedStringArray:
	var e := PhaseFixture.enemy(&"pv_enemy", 100, thresholds, cls)
	# N21: in its class's resistance range, so only the phase rules speak here.
	e.wheel.passive_resistance = _config.resistance_min_by_class[cls]
	return e.validate(config if config != null else _config)


func _has(errors: PackedStringArray, reason: String) -> bool:
	for e in errors:
		if e.begins_with(reason + ":") and e.contains("pv_enemy"):
			return true
	return false


func test_normal_with_phase_entry_rejected() -> void:
	assert_true(_errors(RC.EnemyClass.NORMAL, []).is_empty())
	assert_true(_has(_errors(RC.EnemyClass.NORMAL, [0.5]), "normal_has_phases"))


func test_elite_with_one_phase_entry_accepted() -> void:
	assert_true(_errors(RC.EnemyClass.ELITE, [0.5]).is_empty(), "R1: an elite has 2 phases")
	assert_true(_errors(RC.EnemyClass.ELITE, []).is_empty(), "elite at most one entry")


func test_elite_with_two_phase_entries_rejected() -> void:
	assert_true(_has(_errors(RC.EnemyClass.ELITE, [0.6, 0.3]), "elite_too_many_phases"))


func test_miniboss_two_and_three_phases_accepted() -> void:
	assert_true(_errors(RC.EnemyClass.MINI_BOSS, [0.5]).is_empty())
	assert_true(_errors(RC.EnemyClass.MINI_BOSS, [0.66, 0.33]).is_empty())
	assert_true(_has(_errors(RC.EnemyClass.MINI_BOSS, []), "mini_boss_phase_count"))
	assert_true(_has(_errors(RC.EnemyClass.MINI_BOSS, [0.8, 0.6, 0.3]), "mini_boss_phase_count"))


func test_boss_four_and_five_accepted_three_rejected() -> void:
	var spec := _spec_config()
	assert_true(_errors(RC.EnemyClass.BOSS, [0.82, 0.68, 0.33], spec).is_empty(), "4 phases")
	assert_true(_errors(RC.EnemyClass.BOSS, [0.8, 0.6, 0.4, 0.2], spec).is_empty(), "5 phases")
	assert_true(_has(_errors(RC.EnemyClass.BOSS, [0.66, 0.33], spec), "boss_phase_count"), "3 phases under R1")
	assert_true(_has(_errors(RC.EnemyClass.BOSS, [0.9, 0.8, 0.6, 0.4, 0.2], spec), "boss_phase_count"), "6 phases")


func test_shipped_config_reads_the_class_table() -> void:
	assert_eq(_config.phase_count_max_by_class, PackedInt32Array([1, 2, 3, 5]))
	assert_eq(_config.phase_count_min_by_class.size(), RC.EnemyClass.size())
	assert_true(_config.validate().is_empty(), "config validates")


func test_thresholds_must_descend() -> void:
	assert_true(_has(_errors(RC.EnemyClass.MINI_BOSS, [0.5, 0.68]), "threshold_order"))


func test_threshold_edges_rejected() -> void:
	for t in [0.0, 1.0, 1.2]:
		var errs := _errors(RC.EnemyClass.ELITE, [t])
		assert_true(_has(errs, "threshold_range") or _has(errs, "threshold_order"), "threshold %s refused" % t)
		var found := false
		for e in errs:
			found = found or (e.begins_with("threshold_range:") and e.contains("pv_enemy"))
		assert_true(found, "threshold %s: range reason" % t)
	for t in [0.01, 0.99]:
		assert_true(_errors(RC.EnemyClass.ELITE, [t]).is_empty(), "threshold %s accepted" % t)


func test_duplicate_thresholds_rejected() -> void:
	assert_true(_has(_errors(RC.EnemyClass.MINI_BOSS, [0.5, 0.5]), "threshold_order"))


func test_cleanse_on_enter_unknown_value_rejected() -> void:
	var e := PhaseFixture.enemy(&"pv_enemy", 100, [0.5], RC.EnemyClass.ELITE)
	e.wheel.passive_resistance = _config.resistance_min_by_class[RC.EnemyClass.ELITE]  # N21
	e.phases[0].set("cleanse_on_enter", 9)
	var found := false
	for err in e.validate(_config):
		found = found or (err.begins_with("cleanse_mode:") and err.contains("pv_enemy"))
	assert_true(found, "cleanse_mode reason with the id")
	for scope in RC.CleanseScope.values():
		e.phases[0].cleanse_on_enter = scope
		assert_true(e.validate(_config).is_empty(), "scope %d accepted" % scope)


func test_all_shipped_enemies_validate() -> void:
	var problems := PackedStringArray()
	var checked := 0
	for id in ContentRegistry.all_ids():
		var data := ContentRegistry.get_content(id) as EnemyData
		if data == null:
			continue
		checked += 1
		for p in data.validate(_config):
			problems.append("%s: %s" % [id, p])
	assert_gt(checked, 10)
	assert_eq(problems, PackedStringArray(), "every shipped enemy passes the phase rules")
