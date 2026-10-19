extends GutTest
## N9: a mid-fight save keeps OUTPUT_DOWN / TIER_DOWN stacks, the config validates the new RAM
## numbers and rejects the retired CORRUPTED fields, the status text is US English.


func test_save_round_trip_keeps_the_new_statuses() -> void:
	var atk := CombatFixture.slice(&"n9s_atk", RC.SliceType.SHIM, 4)
	var cls := CombatFixture.operative_class(&"n9s_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, atk]), [])
	var enemy := CombatFixture.enemy(&"n9s_enemy", 100, CombatFixture.null_wheel())
	var res := CombatFixture.resolver([cls, enemy])
	var s := CombatSession.start(res, cls.id, [enemy.id], 8)
	s.state.player.wheel.set_status(2, RC.Status.OUTPUT_DOWN, 3)
	s.state.player.wheel.set_status(4, RC.Status.TIER_DOWN, 1)
	var back := CombatSession.from_dict(res, JSON.parse_string(JSON.stringify(s.to_dict())))
	assert_eq(back.state.player.wheel.stacks_of(2, RC.Status.OUTPUT_DOWN), 3)
	assert_eq(back.state.player.wheel.stacks_of(4, RC.Status.TIER_DOWN), 1)
	assert_eq(back.state_hash(), s.state_hash())


func test_config_has_the_ram_numbers_and_validates() -> void:
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	assert_eq(cfg.corrupted_ram_cost_multiplier, 2)
	assert_eq(cfg.corrupted_enemy_ram_divisor, 2)
	assert_eq(cfg.validate().size(), 0, str(cfg.validate()))


func test_config_rejects_a_multiplier_or_divisor_below_one() -> void:
	var cfg := CampaignConfigData.new()
	cfg.corrupted_ram_cost_multiplier = 0
	assert_true(" ".join(cfg.validate()).contains("corrupted_ram_cost_multiplier"))
	cfg = CampaignConfigData.new()
	cfg.corrupted_enemy_ram_divisor = 0
	assert_true(" ".join(cfg.validate()).contains("corrupted_enemy_ram_divisor"))


func test_retired_fields_are_rejected_by_name() -> void:
	for field in ["corrupted_self_damage", "corrupted_damage_per_major", "corrupted_ram_drain"]:
		var errors := CampaignConfigData.retired_field_errors("[resource]\n%s = 3\n" % field)
		assert_eq(errors.size(), 1, field)
		assert_true(errors[0].begins_with(field))
	assert_eq(CampaignConfigData.retired_field_errors("[resource]\ncorrupted_ram_cost_multiplier = 2\n").size(), 0)
	var f := FileAccess.open("res://content/config/campaign_config.tres", FileAccess.READ)
	assert_eq(CampaignConfigData.retired_field_errors(f.get_as_text()).size(), 0, "the shipped config is clean")


func test_retired_fields_are_gone_from_the_schema() -> void:
	var names: Array[String] = []
	for p in CampaignConfigData.new().get_property_list():
		names.append(String(p["name"]))
	for field in CampaignConfigData.RETIRED_FIELDS:
		assert_false(field in names, field)


func test_status_text_is_us_english_and_says_ram() -> void:
	var corrupted: String = Codex.STATUS_TEXT[RC.Status.CORRUPTED]
	assert_true(corrupted.contains("RAM") and corrupted.contains("double"))
	assert_false(corrupted.contains("self-damage"))
	assert_true(Codex.STATUS_TEXT.has(RC.Status.TIER_DOWN))
