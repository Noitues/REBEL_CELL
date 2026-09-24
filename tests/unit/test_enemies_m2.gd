extends GutTest
## A.3 normal + elite enemies added in M2 match the GDD and their specials work.


func _enemy(id: StringName) -> EnemyData:
	return ContentRegistry.get_content(id) as EnemyData


func _slice_ids(w: WheelData) -> Array[StringName]:
	var out: Array[StringName] = []
	for slot in w.slots:
		out.append(slot.slice.id)
	return out


func test_stats_match_a3() -> void:
	assert_eq(_enemy(&"triage_unit").hp, 45)
	assert_eq(_slice_ids(_enemy(&"triage_unit").wheel), [&"def_8", &"heal_6", &"atk_6", &"heal_6", &"def_8", &"miss"])
	assert_eq(_enemy(&"billing_daemon").hp, 42)
	assert_eq(_slice_ids(_enemy(&"billing_daemon").wheel), [&"atk_7_drain", &"atk_7_drain", &"def_6", &"crit_12_drain", &"atk_7_drain", &"miss"])
	assert_eq(_enemy(&"care_swarm").hp, 25)
	assert_eq(_slice_ids(_enemy(&"care_swarm").wheel), [&"def_4", &"heal_4", &"def_4", &"heal_4", &"atk_4", &"miss"])
	assert_eq(_enemy(&"care_swarm").spawns[0].max_active, 3)
	assert_eq(_enemy(&"care_drone").hp, 4)
	assert_eq(_slice_ids(_enemy(&"care_drone").wheel), [&"atk_3", &"atk_3", &"def_2"])
	var adjuster := _enemy(&"claims_adjuster")
	assert_eq(adjuster.hp, 90)
	assert_true(adjuster.is_elite)
	assert_eq(adjuster.wheel.pointer_ticks, PackedInt32Array([0, 15]))
	assert_eq(_slice_ids(adjuster.wheel), [&"atk_10", &"def_8", &"crit_16", &"atk_10", &"dose", &"miss"])
	var recall := _enemy(&"recall_unit")
	assert_eq(recall.hp, 85)
	assert_true(recall.is_elite)
	assert_eq(recall.wheel.passive_resistance, 1)
	assert_eq(recall.wheel.pointer_orbit_per_turn, 2)
	assert_eq(_slice_ids(recall.wheel), [&"atk_9", &"atk_9", &"def_8", &"crit_15", &"shield_5", &"miss"])


func test_billing_daemon_attacks_drain_ram() -> void:
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"billing_daemon"], 4)
	var e := s.state.get_combatant(&"enemy_0")
	CombatFixture.land(e, 3)  # Crit 12, drains 2
	CombatFixture.land(s.state.player, 5)
	var ram := s.state.ram
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "ram").size() >= 1, true)
	assert_eq(s.state.ram, ram - 2 + 4, "drained 2, then +4 regen")


func test_recall_unit_pointer_orbits_2_per_turn() -> void:
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"recall_unit"], 4)
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(e.wheel.pointer_ticks[0], 0)
	assert_eq(e.resistance, 1)
	CombatFixture.land(s.state.player, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.pointer_ticks[0], 2)
	CombatFixture.land(s.state.player, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.pointer_ticks[0], 4)


func test_care_swarm_spawns_three_drones_on_distinct_slots() -> void:
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"care_swarm"], 4)
	var sats := s.state.satellites_of(&"enemy_0")
	assert_eq(sats.size(), 3)
	var slots := {}
	for sat in sats:
		slots[sat.dock_slot] = true
		assert_eq(sat.hp, 4)
	assert_eq(slots.size(), 3, "no two drones share a slot")


func test_triage_unit_heals_itself() -> void:
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"triage_unit"], 4)
	var e := s.state.get_combatant(&"enemy_0")
	e.hp = 30
	CombatFixture.land(e, 1)  # Heal 6
	CombatFixture.land(s.state.player, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 36)


func test_tier_scaling_applies_to_enemy_hp_and_output() -> void:
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"compliance_officer"], 4, &"", 0, {"enemy_scale": 1.6})
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(e.max_hp, 80, "50 x 1.6")
	CombatFixture.land(e, 0)  # Atk 7
	CombatFixture.land(s.state.player, 5)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "damage")[0]["amount"], 11, "7 x 1.6 = 11.2 -> 11")
