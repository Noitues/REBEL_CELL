extends GutTest
## N2 (CONTENT_DESIGN_V2 R2): the tier base-value tables in CampaignConfigData. One damage
## table replaces the three old scales; accessors clamp the tier; validate() names bad tables.

var _cfg: CampaignConfigData


func before_all() -> void:
	_cfg = CombatFixture.config()


func test_damage_table_default_values_exact() -> void:
	assert_eq(_cfg.enemy_damage_by_tier, PackedFloat64Array([1.0, 1.3, 1.69, 2.2]))


func test_reference_dpt_and_turns_per_phase() -> void:
	assert_eq(_cfg.reference_dpt_by_tier, PackedInt32Array([9, 11, 14, 18]))
	assert_eq(_cfg.target_turns_per_phase, 3.5)


func test_damage_table_matches_old_formula() -> void:
	for t in 4:
		assert_almost_eq(_cfg.enemy_damage_by_tier[t], pow(1.3, t), 0.05, "T%d within 0.05 of 1.3^(t-1)" % (t + 1))


func test_legacy_hp_table_is_old_multiplier() -> void:
	for t in 4:
		assert_almost_eq(_cfg.enemy_hp_scale(t + 1), pow(1.6, t), 0.000001, "legacy HP keeps 1.6^(t-1)")


func test_fresh_config_has_the_same_tables() -> void:
	var fresh := CampaignConfigData.new()
	assert_eq(fresh.enemy_damage_by_tier, _cfg.enemy_damage_by_tier, "no stray 1.6 default")
	assert_eq(fresh.enemy_hp_scale_by_tier, _cfg.enemy_hp_scale_by_tier)
	assert_eq(fresh.reference_dpt_by_tier, _cfg.reference_dpt_by_tier)
	assert_eq(fresh.target_turns_per_phase, _cfg.target_turns_per_phase)
	for cls: StringName in [&"normal", &"elite", &"mini_boss_2", &"mini_boss_3"]:
		assert_eq(fresh.hp_band_table(cls), _cfg.hp_band_table(cls), "band %s" % cls)
	assert_eq(_cfg.validate(), PackedStringArray(), "the shipped config validates")


func test_tier_accessors_clamp() -> void:
	assert_eq(_cfg.enemy_damage_factor(0), 1.0)
	assert_eq(_cfg.enemy_damage_factor(-1), 1.0)
	assert_eq(_cfg.enemy_damage_factor(5), 2.2)
	assert_eq(_cfg.enemy_damage_factor(9), 2.2)
	assert_eq(_cfg.reference_dpt(0), 9)
	assert_eq(_cfg.reference_dpt(7), 18)
	assert_eq(_cfg.enemy_hp_scale(0), 1.0)
	assert_eq(_cfg.hp_band(&"normal", 0), Vector2i(28, 36))
	assert_eq(_cfg.hp_band(&"normal", 6), Vector2i(56, 70))
	assert_eq(_cfg.hp_band(&"mini_boss_3", 4), Vector2i.ZERO, "no mini-boss band at T4")
	assert_eq(_cfg.hp_band(&"unknown", 2), Vector2i.ZERO)


func test_config_validate_rejects_wrong_length() -> void:
	var c := CampaignConfigData.new()
	c.enemy_damage_by_tier = PackedFloat64Array([1.0, 1.3, 1.69])
	assert_true(c.validate().has("enemy_damage_by_tier must have 4 entries."))


func test_config_validate_rejects_non_monotonic() -> void:
	var c := CampaignConfigData.new()
	c.enemy_damage_by_tier = PackedFloat64Array([1.0, 0.9, 1.69, 2.2])
	assert_true(c.validate().has("enemy_damage_by_tier must be non-decreasing."))


func test_config_validate_rejects_zero_or_negative() -> void:
	var c := CampaignConfigData.new()
	c.reference_dpt_by_tier = PackedInt32Array([9, 0, 14, 18])
	assert_true(c.validate().has("reference_dpt_by_tier must be > 0."))
	c = CampaignConfigData.new()
	c.target_turns_per_phase = 0.0
	assert_true(c.validate().has("target_turns_per_phase must be > 0."))


func test_config_validate_rejects_bad_band() -> void:
	var c := CampaignConfigData.new()
	c.hp_band_elite = PackedInt32Array([72, 56, 68, 88, 88, 112, 112, 144])
	assert_true(c.validate().has("hp_band_elite T1 has min above max."))
	c.hp_band_elite = PackedInt32Array([56, 72])
	assert_true(c.validate().has("hp_band_elite must have 8 entries (min, max per tier)."))


func test_reading_tables_never_mutates_the_config() -> void:
	var before := _cfg.enemy_damage_by_tier.duplicate()
	for t in range(-1, 7):
		_cfg.enemy_damage_factor(t)
		_cfg.hp_band(&"elite", t)
	assert_eq(_cfg.enemy_damage_by_tier, before)
