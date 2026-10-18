extends GutTest
## Plan 2 N4 (R4, ruling Q33): the enrage step function, the additive multiplier, the class
## defaults in campaign_config.tres, the lookup order and validation.


func _boss() -> EnrageData:
	return EnrageFixture.enrage(10, 5, 25)


func test_step_before_start_is_zero() -> void:
	var e := _boss()
	for t in [1, 9]:
		assert_eq(e.enrage_step(t), 0, "turn %d" % t)
		assert_eq(e.enrage_multiplier(t), 1.0)


func test_step_at_start_turn_is_one() -> void:
	assert_eq(_boss().enrage_step(10), 1)
	assert_eq(_boss().enrage_multiplier(10), 1.25)


func test_step_every_n_turns() -> void:
	var e := _boss()
	var want := {14: 1, 15: 2, 19: 2, 20: 3}
	for t: int in want:
		assert_eq(e.enrage_step(t), want[t], "turn %d" % t)


func test_multiplier_is_additive() -> void:
	assert_eq(_boss().enrage_multiplier(20), 1.75, "3 steps of 25 % add up (Q33), never 1.25^3")
	assert_eq(_boss().damage_percent_at_step(3), 175)


func test_zero_step_pct_is_flat() -> void:
	var e := EnrageFixture.enrage(10, 5, 0)
	for t in [10, 50, 500]:
		assert_eq(e.enrage_multiplier(t), 1.0)


func test_every_n_one_steps_each_turn() -> void:
	var e := EnrageFixture.enrage(3, 1, 10)
	assert_eq(e.enrage_step(3), 1)
	assert_eq(e.enrage_step(4), 2)
	assert_eq(e.enrage_step(10), 8)


func test_huge_turn_no_overflow() -> void:
	var e := _boss()
	var m := e.enrage_multiplier(10000)
	assert_true(is_finite(m))
	assert_eq(e.enrage_step(10000), 1999)
	assert_eq(EnrageData.scale_hit(10, e.damage_percent_at_step(1999)), 5008, "integer math stays finite")


func test_scale_hit_rounds_half_up() -> void:
	assert_eq(EnrageData.scale_hit(10, 125), 13, "12.5 rounds up")
	assert_eq(EnrageData.scale_hit(10, 150), 15)
	assert_eq(EnrageData.scale_hit(7, 125), 9, "8.75 -> 9")
	assert_eq(EnrageData.scale_hit(0, 175), 0)


func test_next_step_turn() -> void:
	var e := _boss()
	assert_eq(e.next_step_turn(1), 15)
	assert_eq(e.next_step_turn(2), 20)


func test_resistance_step_adds_per_step() -> void:
	var e := EnrageFixture.enrage(10, 5, 0, 2)
	assert_eq(e.resistance_at_step(0), 0)
	assert_eq(e.resistance_at_step(3), 6, "additive, like the damage")


func _cfg() -> CampaignConfigData:
	return load("res://content/config/campaign_config.tres") as CampaignConfigData


func test_defaults_boss_miniboss_10_5_25() -> void:
	for cls in [RC.EnemyClass.BOSS, RC.EnemyClass.MINI_BOSS]:
		var d := _cfg().enrage_default(cls)
		assert_not_null(d)
		assert_eq([d.start_turn, d.every_n_turns, d.damage_pct_step, d.resistance_step], [10, 5, 25, 0], "class %d" % cls)


func test_defaults_elite_8_5_25() -> void:
	var d := _cfg().enrage_default(RC.EnemyClass.ELITE)
	assert_eq([d.start_turn, d.every_n_turns, d.damage_pct_step, d.resistance_step], [8, 5, 25, 0])


func test_defaults_normal_is_off() -> void:
	assert_null(_cfg().enrage_default(RC.EnemyClass.NORMAL))
	assert_null(_cfg().enrage_for(EnrageFixture.enemy(&"en_n", RC.EnemyClass.NORMAL, 5)))


func test_config_validates() -> void:
	assert_eq(_cfg().validate(), PackedStringArray())
	var bad := CampaignConfigData.new()
	bad.enrage_start_turn_by_class = PackedInt32Array([3, 8, 10, 10])
	assert_true(",".join(bad.validate()).contains("normals have no enrage"))


func test_lookup_authored_then_class_then_off() -> void:
	var cfg := _cfg()
	var authored := EnrageFixture.enrage(4, 2, 50)
	assert_eq(cfg.enrage_for(EnrageFixture.enemy(&"en_a", RC.EnemyClass.BOSS, 5, 999, authored)), authored)
	assert_eq(cfg.enrage_for(EnrageFixture.enemy(&"en_b", RC.EnemyClass.BOSS, 5)).start_turn, 10)
	assert_null(cfg.enrage_for(EnrageFixture.enemy(&"en_c", RC.EnemyClass.NORMAL, 5)))


func test_authored_overrides_class_default() -> void:
	var handler := load("res://content/enemies/the_handler.tres") as EnemyData
	assert_eq(handler.enemy_class(), RC.EnemyClass.MINI_BOSS)
	assert_eq(_cfg().enrage_for(handler).start_turn, 8, "the Handler's start 8 wins over the mini-boss 10")


func test_validate_rejects_start_turn_below_1() -> void:
	assert_true(",".join(EnrageFixture.enrage(0, 5, 25).validate()).begins_with("start_turn"))


func test_validate_rejects_every_n_below_1() -> void:
	assert_true(",".join(EnrageFixture.enrage(10, 0, 25).validate()).begins_with("every_n_turns"))


func test_validate_rejects_negative_step() -> void:
	assert_true(",".join(EnrageFixture.enrage(10, 5, -1).validate()).begins_with("damage_pct_step"))
	assert_true(",".join(EnrageFixture.enrage(10, 5, 0, -1).validate()).begins_with("resistance_step"))
	assert_eq(_boss().validate(), PackedStringArray())


func test_validate_rejects_enrage_on_normal() -> void:
	var e := EnrageFixture.enemy(&"en_norm", RC.EnemyClass.NORMAL, 5, 999, _boss())
	assert_true(",".join(e.validate(CampaignConfigData.new())).contains("normal_has_enrage"))
	var elite := EnrageFixture.enemy(&"en_el", RC.EnemyClass.ELITE, 5, 999, _boss())
	assert_false(",".join(elite.validate(CampaignConfigData.new())).contains("enrage"))
