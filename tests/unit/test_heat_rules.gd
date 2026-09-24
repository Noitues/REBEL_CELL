extends GutTest
## Heat thresholds (GDD 4.3, M3 acceptance): events fire once only; modifiers switch
## off when Heat drops below the threshold.

var _cfg: CampaignConfigData


func before_all() -> void:
	_cfg = CombatFixture.config()


func _campaign() -> CampaignState:
	var c := CampaignState.new()
	c.schematics = 20
	return c


func _types(events: Array[Dictionary], type: String) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for e in events:
		if e.get("type", "") == type:
			out.append(e)
	return out


func test_crossing_thresholds_fires_each_once_in_order() -> void:
	var c := _campaign()
	var events := HeatRules.add_heat(c, 30, _cfg, "test")
	var fired := _types(events, "heat_threshold")
	assert_eq(fired.size(), 4, "10, 20, 25, 30 crossed")
	assert_eq(fired[2]["heat"], 25)
	assert_eq(c.thresholds_fired, [10, 20, 25, 30])
	assert_eq(c.pending_raids.size(), 1, "the MAJOR 25 raid is queued")
	assert_eq(c.pending_raids[0]["raid_id"], "raid_heat_25")
	assert_eq(c.pending_complications.size(), 3, "three MINOR complications (10, 20, 30)")


func test_a_threshold_never_fires_twice() -> void:
	var c := _campaign()
	HeatRules.add_heat(c, 30, _cfg, "up")
	var raids := c.pending_raids.size()
	HeatRules.add_heat(c, -15, _cfg, "down")
	assert_eq(c.heat, 15)
	var events := HeatRules.add_heat(c, 20, _cfg, "up again")
	assert_eq(_types(events, "heat_threshold").size(), 0, "10, 20, 25, 30 already fired")
	assert_eq(c.pending_raids.size(), raids, "no second raid at 25")
	events = HeatRules.add_heat(c, 20, _cfg, "to 55")
	var fired := _types(events, "heat_threshold")
	assert_eq(fired.size(), 2, "40 and 50 are new")
	assert_eq(c.pending_raids.size(), raids + 1, "the 50 raid queued once")


func test_reductions_never_fire_events() -> void:
	var c := _campaign()
	c.heat = 60
	var events := HeatRules.add_heat(c, -50, _cfg, "scrub")
	assert_eq(_types(events, "heat_threshold").size(), 0)
	assert_eq(c.thresholds_fired.size(), 0, "thresholds crossed downward do not count")
	events = HeatRules.add_heat(c, 20, _cfg, "back up")
	assert_eq(_types(events, "heat_threshold").size(), 3, "10, 20, 25 fire on the way back up (never fired before)")


func test_heat_is_clamped_and_the_purge_fires_at_100() -> void:
	var c := _campaign()
	var events := HeatRules.add_heat(c, 500, _cfg, "meltdown")
	assert_eq(c.heat, _cfg.heat_max)
	assert_eq(c.thresholds_fired.size(), _cfg.heat_thresholds.size(), "every threshold fired once")
	var raids := _types(events, "raid_pending")
	assert_eq(raids.size(), 4, "25, 50, 75, purge")
	assert_eq(raids[3]["raid_id"], &"raid_purge")


func test_ongoing_modifiers_apply_only_while_at_or_above() -> void:
	var c := _campaign()
	c.heat = 24
	assert_eq(c.rule_modifier(_cfg, RC.RuleModifierType.ELITE_FREQUENCY_PCT), 0.0)
	c.heat = 25
	assert_eq(c.rule_modifier(_cfg, RC.RuleModifierType.ELITE_FREQUENCY_PCT), 25.0)
	assert_eq(c.rule_modifier(_cfg, RC.RuleModifierType.ENEMY_RESISTANCE), 0.0)
	c.heat = 50
	assert_eq(c.rule_modifier(_cfg, RC.RuleModifierType.ENEMY_RESISTANCE), 1.0)
	c.heat = 75
	assert_eq(c.rule_modifier(_cfg, RC.RuleModifierType.RAID_STRENGTH_PCT), 25.0)
	assert_eq(HeatRules.active_modifiers(c, _cfg).size(), 3)
	c.heat = 49
	assert_eq(c.rule_modifier(_cfg, RC.RuleModifierType.ENEMY_RESISTANCE), 0.0, "switched off below 50")
	assert_eq(c.rule_modifier(_cfg, RC.RuleModifierType.ELITE_FREQUENCY_PCT), 25.0, "25 still active")
	assert_eq(HeatRules.active_modifiers(c, _cfg).size(), 1)


func test_ice_ladder_modifiers_stack_with_heat() -> void:
	var c := _campaign()
	c.ice_level = 3
	assert_eq(c.rule_modifier(_cfg, RC.RuleModifierType.ELITE_FREQUENCY_PCT), 25.0, "ICE 3: more elites")
	c.heat = 25
	assert_eq(c.rule_modifier(_cfg, RC.RuleModifierType.ELITE_FREQUENCY_PCT), 50.0, "ICE 3 + Heat 25")
	c.ice_level = 9
	assert_eq(c.rule_modifier(_cfg, RC.RuleModifierType.BOSS_STRENGTH_PCT), 25.0)
