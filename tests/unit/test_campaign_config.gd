extends GutTest
## content/config/campaign_config.tres carries every GDD §11 value and validates.

const CONFIG_PATH := "res://content/config/campaign_config.tres"

var _cfg: CampaignConfigData


func before_all() -> void:
	_cfg = load(CONFIG_PATH)


func test_config_loads_and_validates() -> void:
	assert_not_null(_cfg)
	assert_eq(_cfg.validate().size(), 0, str(_cfg.validate()))


func test_default_schema_values_validate() -> void:
	assert_eq(CampaignConfigData.new().validate().size(), 0)


func test_heat_values_match_gdd_11_5() -> void:
	assert_eq(_cfg.heat_max, 100)
	assert_eq(_cfg.rack_heat_by_tier, PackedInt32Array([2, 3, 5, 8]))
	assert_eq(_cfg.exploit_heat, 10)
	assert_eq(_cfg.elite_heat, 1)
	assert_eq(_cfg.death_heat_base, 10)
	assert_eq(_cfg.lost_raid_heat, 5)
	assert_eq(_cfg.heat_purchase_amount, 5)
	assert_eq(_cfg.heat_purchase_cost, 25)
	assert_eq(_cfg.heat_purchase_increment, 10)


func test_heat_thresholds_match_gdd_4_3() -> void:
	var heats: Array[int] = []
	for t in _cfg.heat_thresholds:
		heats.append(t.heat)
	assert_eq(heats, [10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 100])
	for t in _cfg.heat_thresholds:
		var expected_kind: RC.ThresholdKind
		if t.heat == 100:
			expected_kind = RC.ThresholdKind.PURGE
		elif t.heat % 25 == 0:
			expected_kind = RC.ThresholdKind.MAJOR
		else:
			expected_kind = RC.ThresholdKind.MINOR
		assert_eq(t.kind, expected_kind, "kind at heat %d" % t.heat)
		if t.kind == RC.ThresholdKind.MINOR:
			assert_eq(t.event_complications.size(), 1, "minor %d has one complication" % t.heat)
			assert_eq(t.ongoing_modifiers.size(), 0, "minor %d has no ongoing modifier" % t.heat)


func test_major_threshold_modifiers_match_gdd_4_3() -> void:
	var by_heat := {}
	for t in _cfg.heat_thresholds:
		by_heat[t.heat] = t
	assert_eq(by_heat[25].ongoing_modifiers[0].type, RC.RuleModifierType.ELITE_FREQUENCY_PCT)
	assert_eq(by_heat[50].ongoing_modifiers[0].type, RC.RuleModifierType.ENEMY_RESISTANCE)
	assert_eq(by_heat[50].ongoing_modifiers[0].value, 1.0)
	assert_eq(by_heat[75].ongoing_modifiers[0].type, RC.RuleModifierType.RAID_STRENGTH_PCT)
	assert_eq(by_heat[75].ongoing_modifiers[0].value, 25.0)
	assert_eq(by_heat[100].ongoing_modifiers.size(), 0)


func test_economy_matches_gdd_11_1_and_11_4() -> void:
	assert_eq(_cfg.cycles_per_schematic, 10)
	assert_eq(_cfg.rack_schematics_by_tier, PackedInt32Array([10, 17, 29, 50]))
	assert_eq(_cfg.raid_schematics_by_tier, PackedInt32Array([8, 12, 18, 25]))
	assert_eq(_cfg.cycles_combat_range, Vector2i(10, 20))
	assert_eq(_cfg.cycles_elite_range, Vector2i(30, 40))
	assert_eq(_cfg.cycles_router_range, Vector2i(15, 25))
	assert_eq(_cfg.rookie_cost, 15)
	assert_eq(_cfg.node_base_cost, 20)
	assert_eq(_cfg.node_upgrade_costs, PackedInt32Array([30, 60]))
	assert_eq(_cfg.node_repair_ratio, 0.5)
	assert_eq(_cfg.netrun_boost_cost_range, Vector2i(10, 20))
	assert_eq(_cfg.class_unlock_cost, 80)


func test_shop_and_ram_match_gdd_11_2_and_11_3() -> void:
	assert_eq(_cfg.card_price_range, Vector2i(50, 75))
	assert_eq(_cfg.firmware_price_range, Vector2i(75, 150))
	assert_eq(_cfg.daemon_price_range, Vector2i(150, 250))
	assert_eq(_cfg.card_removal_price, 50)
	assert_eq(_cfg.card_removal_increment, 25)
	assert_eq(_cfg.slice_overwrite_price, 100)
	assert_eq(_cfg.miss_slice_overwrite_price, 150)
	assert_eq(_cfg.extra_nudge_ram_cost, 1)
	assert_eq(_cfg.respin_ram_cost, 4)


func test_scaling_and_breach_match_gdd_11_6_and_11_7() -> void:
	assert_eq(_cfg.enemy_scale_per_tier, 1.6)
	assert_eq(_cfg.reward_scale_per_tier, 1.7)
	assert_eq(_cfg.min_exploits_for_breach, 3)


func test_ice_ladder_has_20_ascending_unique_levels() -> void:
	assert_eq(_cfg.ice_ladder.size(), 20)
	for i in _cfg.ice_ladder.size():
		assert_eq(_cfg.ice_ladder[i].level, i + 1, "ladder index %d" % i)


func test_ice_ladder_matches_gdd_11_9() -> void:
	var expected := {
		1: [RC.RuleModifierType.HEAT_GAIN_PCT, 10.0],
		2: [RC.RuleModifierType.HEAT_OBJECTIVE_SITES, -1.0],
		4: [RC.RuleModifierType.CYCLE_PRICE_PCT, 10.0],
		5: [RC.RuleModifierType.RAID_STRENGTH_PCT, 15.0],
		6: [RC.RuleModifierType.HEAT_SINK_PCT, -15.0],
		7: [RC.RuleModifierType.ENEMY_RESISTANCE, 1.0],
		8: [RC.RuleModifierType.DEATH_HEAT, 5.0],
		9: [RC.RuleModifierType.BOSS_STRENGTH_PCT, 25.0],
		11: [RC.RuleModifierType.STARTING_BUG_CARD, 1.0],
		12: [RC.RuleModifierType.NO_FIRST_TURN_FREE_NUDGE, 1.0],
		16: [RC.RuleModifierType.EXPLOIT_HEAT, 5.0],
		17: [RC.RuleModifierType.PURGE_THRESHOLD, 90.0],
		18: [RC.RuleModifierType.BOSS_EXTRA_POINTER, 1.0],
		19: [RC.RuleModifierType.RAID_EXTRA_WAVE, 1.0],
	}
	for level in expected:
		var ice: IceLevelData = _cfg.ice_ladder[level - 1]
		assert_eq(ice.modifiers.size(), 1, "ICE %d has one modifier" % level)
		assert_eq(ice.modifiers[0].type, expected[level][0], "ICE %d type" % level)
		assert_eq(ice.modifiers[0].value, expected[level][1], "ICE %d value" % level)
