extends GutTest
## Renewal Engine (GDD A.3, 2.11, 11.7): phases, Auto-Renew, Exploit effects on the breach.

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


func _session(overrides: Dictionary = {}) -> CombatSession:
	var s := CombatSession.start(_resolver, &"breaker", [&"renewal_engine"], 5, &"rank:1", 0, overrides)
	CombatFixture.land(s.state.player, 5)  # Miss: the operative does no damage unless told to
	return s


func _boss(s: CombatSession) -> CombatantState:
	return s.state.get_combatant(&"enemy_0")


func test_stats_match_a3() -> void:
	var b := _boss(_session())
	assert_eq(b.max_hp, 360, "A.3 lists 300; raised by the M7 balance pass (DECISIONS)")
	assert_eq(b.wheel.slot_slice_ids, [&"atk_14", &"atk_14", &"def_12", &"dose", &"crit_24", &"miss"])
	assert_eq(b.wheel.hub_id, &"auto_renew")
	assert_eq(b.wheel.pointer_ticks, PackedInt32Array([0]))


func test_auto_renew_heals_10_per_turn_unless_breached() -> void:
	var s := _session()
	var b := _boss(s)
	b.hp = 250
	CombatFixture.land(b, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(_boss(s).hp, 260, "+10 at the start of the next turn")
	var events: Array[Dictionary] = []
	_resolver.fx.hub_breach(_boss(s), 1, events)
	CombatFixture.land(_boss(s), 5)
	CombatFixture.land(s.state.player, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(_boss(s).hp, 260, "breached: no heal this turn")


func test_phase_1_at_66_percent_multiplies_to_two_pointers() -> void:
	var s := _session()
	var b := _boss(s)
	b.hp = 240  # 66% of 360 is 237.6: not yet
	CombatFixture.land(b, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(_boss(s).phase_index, 0, "still above the threshold (healed to 250)")
	b = _boss(s)
	b.hp = 225
	CombatFixture.land(b, 5)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "boss_phase").size(), 1)
	assert_eq(_boss(s).phase_index, 1)
	assert_eq(_boss(s).wheel.pointer_ticks, PackedInt32Array([0, 15]))


func test_phase_2_at_33_percent_orbits_and_spawns_two_drones() -> void:
	var s := _session()
	var b := _boss(s)
	b.hp = 100  # below 33% of 360
	CombatFixture.land(b, 5)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "boss_phase").size(), 2, "both phases entered at once")
	assert_eq(_boss(s).phase_index, 2)
	assert_eq(_boss(s).wheel.pointer_orbit, 3)
	assert_eq(s.state.satellites_of(&"enemy_0").size(), 2)
	var ticks := _boss(s).wheel.pointer_ticks
	CombatFixture.land(_boss(s), 5)
	CombatFixture.land(s.state.player, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(_boss(s).wheel.pointer_ticks[0], posmod(ticks[0] + 3, 30), "orbit +3 per turn")


func test_breach_exploit_removes_a_pointer_in_every_phase() -> void:
	var s := _session({"remove_boss_pointers": 1})
	assert_eq(_boss(s).wheel.pointer_ticks.size(), 1, "never below one pointer")
	var b := _boss(s)
	b.hp = 190
	CombatFixture.land(b, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(_boss(s).wheel.pointer_ticks, PackedInt32Array([0]), "Multiply to 2 minus 1")


func test_virus_exploit_corrupts_two_boss_slices_at_the_start() -> void:
	var s := _session({"boss_corrupt_slices": 2})
	var statuses := _boss(s).wheel.slice_statuses
	assert_eq(statuses.count(RC.Status.CORRUPTED), 2)
	assert_eq(statuses[5], RC.Status.NONE, "never the Miss slice")
	var replayed := CombatSession.replay(_resolver, s.setup, s.combat_seed, s.history)
	assert_eq(replayed.state.get_combatant(&"enemy_0").wheel.slice_statuses, statuses, "deterministic")
