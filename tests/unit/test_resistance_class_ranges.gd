extends GutTest
## Plan 2 N21 (rulings Q16, Q31): the per-class resistance ranges live in the config, and
## EnemyData.validate holds each enemy's per-turn resistance (passive + hub at fight start,
## and after each phase's overrides) inside its class range, by reason name with the id.


func _cfg() -> CampaignConfigData:
	return load("res://content/config/campaign_config.tres") as CampaignConfigData


func _enemy(id: StringName, cls: int, passive: int, hub_res: int = 0) -> EnemyData:
	var hub: HubCoreData = CombatFixture.hub(StringName("%s_hub" % id), hub_res) if hub_res > 0 else null
	var e := PhaseFixture.enemy(id, 50, [], cls, CombatFixture.null_wheel(passive, hub))
	e.phases.clear()
	return e


func _range_errors(e: EnemyData) -> PackedStringArray:
	var out := PackedStringArray()
	for problem in e.validate(_cfg()):
		if problem.begins_with("resistance_out_of_range"):
			out.append(problem)
	return out


func test_config_holds_the_four_class_ranges() -> void:
	var cfg := _cfg()
	assert_eq(cfg.resistance_min_by_class, PackedInt32Array([1, 3, 3, 5]))
	assert_eq(cfg.resistance_max_by_class, PackedInt32Array([2, 4, 4, 6]))
	assert_eq(cfg.validate().size(), 0, str(cfg.validate()))


func test_config_refuses_a_bad_range() -> void:
	var cfg := CampaignConfigData.new()
	cfg.resistance_min_by_class = PackedInt32Array([3, 3, 3, 5])
	cfg.resistance_max_by_class = PackedInt32Array([2, 4, 4, 6])
	assert_true(",".join(cfg.validate()).contains("Resistance range for class 0"))
	cfg.resistance_max_by_class = PackedInt32Array([2, 4])
	assert_true(",".join(cfg.validate()).contains("Resistance ranges need one entry per enemy class"))


func test_a_normal_at_3_is_refused_by_name() -> void:
	var errors := _range_errors(_enemy(&"n21_normal3", RC.EnemyClass.NORMAL, 3))
	assert_eq(errors.size(), 1)
	assert_string_contains(errors[0], "n21_normal3")
	assert_string_contains(errors[0], "normal")


func test_a_boss_at_4_is_refused_by_name() -> void:
	var errors := _range_errors(_enemy(&"n21_boss4", RC.EnemyClass.BOSS, 4))
	assert_eq(errors.size(), 1)
	assert_string_contains(errors[0], "n21_boss4")
	assert_string_contains(errors[0], "boss")


func test_each_class_accepts_its_ends_and_refuses_outside() -> void:
	var cases := [[RC.EnemyClass.NORMAL, 1, 2], [RC.EnemyClass.ELITE, 3, 4], [RC.EnemyClass.MINI_BOSS, 3, 4], [RC.EnemyClass.BOSS, 5, 6]]
	for c: Array in cases:
		var cls: int = c[0]
		assert_eq(_range_errors(_enemy(&"n21_lo", cls, c[1])).size(), 0, "class %d at %d" % [cls, c[1]])
		assert_eq(_range_errors(_enemy(&"n21_hi", cls, c[2])).size(), 0, "class %d at %d" % [cls, c[2]])
		assert_eq(_range_errors(_enemy(&"n21_under", cls, c[1] - 1)).size(), 1, "class %d under" % cls)
		assert_eq(_range_errors(_enemy(&"n21_over", cls, c[2] + 1)).size(), 1, "class %d over" % cls)


func test_hub_resistance_counts_toward_the_total() -> void:
	assert_eq(_range_errors(_enemy(&"n21_hub2", RC.EnemyClass.NORMAL, 0, 2)).size(), 0, "hub 2 alone is a normal's 2")
	assert_eq(_range_errors(_enemy(&"n21_hub3", RC.EnemyClass.NORMAL, 1, 2)).size(), 1, "passive 1 + hub 2 = 3")


func test_a_phase_override_is_held_to_the_range() -> void:
	var e := _enemy(&"n21_phased", RC.EnemyClass.BOSS, 5)
	var low := CombatFixture.null_wheel(0)
	e.phases = [PhaseFixture.phase(0.66, RC.CleanseScope.NONE, low), PhaseFixture.phase(0.33)]
	var errors := _range_errors(e)
	assert_eq(errors.size(), 2, "phase 2 drops to 0 and phase 3 keeps the override: %s" % str(errors))
	assert_string_contains(errors[0], "phase 2")
	low.passive_resistance = 6
	assert_eq(_range_errors(e).size(), 0)


func test_satellite_wheels_are_not_held_to_the_range() -> void:
	var shim := CombatFixture.slice(&"n21_sat_shim", RC.SliceType.SHIM, 2)
	var sat := CombatFixture.enemy(&"n21_sat", 10, CombatFixture.wheel([shim, shim]))
	assert_eq(_range_errors(sat).size(), 0)
