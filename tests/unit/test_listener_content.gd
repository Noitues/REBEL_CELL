extends GutTest
## Plan 2 N6: ListenerData.validate refuses what a listener may not be (a trigger it cannot
## hear, no effects, a cap below 1, an effect that draws RNG, PERCENT over 100), accepts
## PERCENT damage, EnemyData.validate reports its own and its Hubs' listeners by id, the
## config default validates, and every shipped listener validates.

const L = preload("res://tests/helpers/listener_fixture.gd")


func _codes(l: ListenerData) -> String:
	return ",".join(l.validate())


func test_valid_listener_has_no_errors() -> void:
	for t in ListenerData.TRIGGERS:
		assert_eq(L.listener(t, [L.block(1)]).validate().size(), 0, "trigger %d" % t)


func test_validate_rejects_unlistenable_trigger_by_name() -> void:
	var codes := _codes(L.listener(RC.Trigger.ON_TURN_START, [L.block(1)]))
	assert_string_contains(codes, "trigger_not_listenable")
	assert_string_contains(codes, "ON_TURN_START")
	assert_string_contains(_codes(L.listener(RC.Trigger.ON_NETRUN_COMPLETE, [L.block(1)])), "trigger_not_listenable")


func test_validate_rejects_empty_effects_and_empty_entries() -> void:
	assert_string_contains(_codes(L.listener(RC.Trigger.ON_NUDGE, [])), "no_effects")
	var l := L.listener(RC.Trigger.ON_NUDGE, [L.block(1)])
	l.effects.append(null)
	assert_string_contains(_codes(l), "empty_effect")


func test_validate_rejects_rng_effects() -> void:
	var random_pick := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.TARGET_WHEEL, 1, RC.RingScope.OUTER, 1.0, RC.Status.CORRUPTED, RC.SlicePick.RANDOM_NON_NULL)
	var respin := CombatFixture.effect(RC.EffectType.RESPIN, RC.EffectTarget.TARGET_WHEEL, 0, RC.RingScope.WHOLE_WHEEL)
	var draw := CombatFixture.effect(RC.EffectType.DRAW_CARDS, RC.EffectTarget.SELF, 1)
	var custom := CombatFixture.effect(RC.EffectType.CUSTOM, RC.EffectTarget.SELF, 0)
	for e in [random_pick, respin, draw, custom]:
		var l := L.listener(RC.Trigger.ON_PERFECT, [e])
		assert_string_contains(_codes(l), "rng_effect", RC.EffectType.keys()[e.type])


func test_validate_rejects_zero_or_negative_caps() -> void:
	for cap in [0, -2]:
		assert_string_contains(_codes(L.listener(RC.Trigger.ON_NUDGE, [L.block(1)], cap)), "cap_not_positive", "turn cap %d" % cap)
		assert_string_contains(_codes(L.listener(RC.Trigger.ON_NUDGE, [L.block(1)], 1, cap)), "cap_not_positive", "combat cap %d" % cap)
	assert_eq(L.listener(RC.Trigger.ON_NUDGE, [L.block(1)], 3, 7).validate().size(), 0, "authored caps")


func test_percent_damage_allowed_and_over_100_refused() -> void:
	assert_eq(L.listener(RC.Trigger.ON_PERFECT, [L.hit(10, true)]).validate().size(), 0, "PERCENT damage is a listener amount")
	assert_string_contains(_codes(L.listener(RC.Trigger.ON_PERFECT, [L.hit(150, true)])), "percent_out_of_range")
	var plain := L.hit(10, true)
	assert_string_contains(",".join(plain.validate()), "mode_unsupported_for_type", "outside a listener PERCENT damage stays refused")


func test_enemy_validate_reports_own_and_hub_listeners_with_id() -> void:
	var hub := CombatFixture.hub(&"lc_hub")
	var hub_listeners: Array[ListenerData] = [L.listener(RC.Trigger.ON_TURN_END, [L.block(1)])]
	hub.listeners = hub_listeners
	var e := CombatFixture.enemy(&"lc_enemy", 30, CombatFixture.null_wheel(1, hub))
	var own: Array[ListenerData] = [L.listener(RC.Trigger.ON_NUDGE, [L.block(1)], 0)]
	e.listeners = own
	var codes := ",".join(e.listener_errors())
	assert_string_contains(codes, "cap_not_positive")
	assert_string_contains(codes, "trigger_not_listenable")
	assert_string_contains(codes, "lc_enemy")
	assert_string_contains(",".join(e.validate()), "trigger_not_listenable", "validate includes listener errors")


func test_config_default_and_its_check() -> void:
	var shipped := CombatFixture.config()
	assert_eq(shipped.listener_max_per_turn_default, 1)
	var bad := CampaignConfigData.new()
	bad.listener_max_per_turn_default = 0
	assert_string_contains(",".join(bad.validate()), "listener_max_per_turn_default")


func test_all_shipped_enemies_with_listeners_validate() -> void:
	var checked := 0
	for id in ContentRegistry.all_ids():
		var e := ContentRegistry.get_content(id) as EnemyData
		if e == null:
			continue
		checked += 1
		assert_eq(e.listener_errors().size(), 0, "listeners of %s" % id)
	assert_gt(checked, 0, "enemies scanned")
