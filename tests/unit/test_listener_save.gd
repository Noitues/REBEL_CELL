extends GutTest
## Plan 2 N6: listener fire counters survive a mid-turn save round trip (and the cap still
## holds after the resume); a save without the fields loads empty counters.

const L = preload("res://tests/helpers/listener_fixture.gd")


func _session() -> CombatSession:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.block(1)], 2, 5)])
	L.stage(s, [], 12)
	return s


func test_round_trip_preserves_fire_counters() -> void:
	var s := _session()
	s.apply(CombatAction.nudge(&"player", 1))
	var back := CombatSession.from_dict(s.resolver, JSON.parse_string(JSON.stringify(s.to_dict())))
	var e := back.state.get_combatant(&"enemy_0")
	assert_eq(int(e.listener_fires_turn.get("lf_enemy:L0", -1)), 1)
	assert_eq(int(e.listener_fires_combat.get("lf_enemy:L0", -1)), 1)
	assert_eq(back.state.state_hash(), s.state.state_hash())


func test_mid_turn_resume_then_nudge_respects_cap() -> void:
	var s := _session()
	s.apply(CombatAction.nudge(&"player", 1))
	var back := CombatSession.from_dict(s.resolver, JSON.parse_string(JSON.stringify(s.to_dict())))
	var second := back.apply(CombatAction.nudge(&"player", 1))
	var third := back.apply(CombatAction.nudge(&"player", 1))
	assert_eq(L.fires(second).size(), 1)
	assert_eq(L.fires(third).size(), 0, "the per-turn cap of 2 counts the fire made before the save")


func test_old_save_without_listener_fields_loads_defaults() -> void:
	var s := _session()
	var d := s.state.get_combatant(&"enemy_0").to_dict()
	assert_false(d.has("listener_fires_turn"))
	var c := CombatantState.from_dict(d)
	assert_true(c.listener_fires_turn.is_empty() and c.listener_fires_combat.is_empty())


func test_counter_keys_save_in_text_order() -> void:
	var c := CombatantState.from_dict(_session().state.get_combatant(&"enemy_0").to_dict())
	c.listener_fires_combat = {"z:L0": 1, "a:L1": 2, "m:L0": 3}
	assert_eq((c.to_dict()["listener_fires_combat"] as Dictionary).keys(), ["a:L1", "m:L0", "z:L0"])
