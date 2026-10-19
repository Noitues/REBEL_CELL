extends GutTest
## Plan 2 N3 (R3): while a phase is active, HP cannot drop below ceil(max HP x the next
## threshold) on any loss path (hits, pierce, self-damage, parasites, CORRUPTED bites); the
## excess is parked (lost). Heal is never clamped. Normals and the last phase have no floor.

var _resolver: CombatResolver
var _fx: EffectInterpreter


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_fx = _resolver.fx


func _hit(victim: CombatantState, amount: int, pierce: bool = false) -> Dictionary:
	var events: Array[Dictionary] = []
	var attacker := PhaseFixture.combatant(60, 60, 0.0)
	attacker.id = &"pf_attacker"
	_fx.deal_hit(CombatState.new(), attacker, victim, amount, pierce, true, events)
	return events[events.size() - 1]


func test_floor_is_ceil_of_max_hp_times_threshold() -> void:
	assert_eq(PhaseFixture.combatant(99, 99, 0.68).hp_floor(), 68, "67.32 rounds up")
	assert_eq(PhaseFixture.combatant(100, 100, 0.68).hp_floor(), 68, "exactly 68, never 69 from float error")
	assert_eq(PhaseFixture.combatant(100, 100, 0.33).hp_floor(), 33)
	assert_eq(PhaseFixture.combatant(360, 360, 0.66).hp_floor(), 238, "237.6 rounds up")
	assert_eq(PhaseFixture.combatant(100, 100, 0.0).hp_floor(), 0, "no next phase: no floor")


func test_hit_crossing_floor_leaves_hp_at_floor() -> void:
	var c := PhaseFixture.combatant(80, 100, 0.68)
	var e := _hit(c, 30)
	assert_eq(c.hp, 68)
	assert_eq(int(e["hp_damage"]), 12)
	assert_eq(int(e["parked"]), 18)


func test_hit_landing_exactly_on_floor_not_parked() -> void:
	var c := PhaseFixture.combatant(80, 100, 0.68)
	var e := _hit(c, 12)
	assert_eq(c.hp, 68)
	assert_eq(int(e["parked"]), 0)


func test_hit_one_above_floor_unchanged() -> void:
	var c := PhaseFixture.combatant(70, 100, 0.68)
	_hit(c, 1)
	assert_eq(c.hp, 69)


func test_hp_already_at_floor_takes_zero() -> void:
	var c := PhaseFixture.combatant(68, 100, 0.68)
	var e := _hit(c, 20)
	assert_eq(c.hp, 68)
	assert_eq(int(e["hp_damage"]), 0)
	assert_eq(int(e["parked"]), 20, "all 20 lost")


func test_block_and_shield_soak_before_the_floor() -> void:
	var c := PhaseFixture.combatant(80, 100, 0.68)
	c.block = 10
	c.shield = 5
	var e := _hit(c, 30)
	assert_eq(int(e["blocked"]) + int(e["shielded"]), 15)
	assert_eq(c.hp, 68)
	assert_eq(int(e["parked"]), 3, "30 - 15 soaked = 15; 12 to the floor, 3 parked")


func test_pierce_parks() -> void:
	var c := PhaseFixture.combatant(80, 100, 0.68)
	c.block = 10
	c.shield = 5
	var e := _hit(c, 30, true)
	assert_eq(c.block, 10, "pierce skips block")
	assert_eq(c.shield, 5, "pierce skips shield")
	assert_eq(c.hp, 68, "but not the floor")
	assert_eq(int(e["parked"]), 18)


func test_self_damage_parks() -> void:
	var c := PhaseFixture.combatant(70, 100, 0.68)
	var events: Array[Dictionary] = []
	var st := CombatState.new()
	st.player = PhaseFixture.combatant(60, 60, 0.0)
	st.enemies.append(c)
	var dmg := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.SELF, 10)
	_fx.apply_effect(st, dmg, {"owner": c, "target": st.player}, CombatFixture.rng(1001), events)
	assert_eq(c.hp, 68)
	assert_eq(PhaseFixture.sum_of(events, "damage", "parked"), 8)


func test_parasite_damage_parks() -> void:
	# A parasite (a docked satellite) hits through deal_hit like any attacker.
	var c := PhaseFixture.combatant(75, 100, 0.68)
	var parasite := PhaseFixture.combatant(10, 10, 0.0)
	parasite.id = &"pf_parasite"
	parasite.is_satellite = true
	var events: Array[Dictionary] = []
	_fx.deal_hit(CombatState.new(), parasite, c, 9, false, true, events, &"parasite")
	assert_eq(c.hp, 68)
	assert_eq(int(events[0]["parked"]), 2)


func test_corrupted_bite_parks() -> void:
	var data := PhaseFixture.enemy(&"pk_bitten", 100, [0.68], RC.EnemyClass.ELITE)
	var s := PhaseFixture.session(data, 0)
	var e := PhaseFixture.aim(s)
	e.hp = 69
	e.wheel.set_status(0, RC.Status.CORRUPTED)
	var r := s.apply(CombatAction.end_turn())
	var bite := CombatFixture.events_of(r, "corrupted")
	assert_eq(bite.size(), 1)
	assert_eq(int(bite[0]["amount"]), 1, "69 -> 68")
	assert_eq(int(bite[0]["parked"]), CombatFixture.config().corrupted_self_damage - 1)


func test_multi_hit_slice_parks_once_rest_lost() -> void:
	var data := PhaseFixture.enemy(&"pk_multi", 100, [0.68, 0.33], RC.EnemyClass.MINI_BOSS)
	var s := PhaseFixture.session(data, 10, [0, 10, 20])
	var e := PhaseFixture.aim(s)
	e.hp = 75
	var r := s.apply(CombatAction.end_turn())
	var after := r.resolved_state.get_combatant(&"enemy_0")
	assert_eq(after.hp, 68)
	assert_eq(PhaseFixture.sum_of(r.events, "damage", "hp_damage"), 7)
	assert_eq(PhaseFixture.sum_of(r.events, "damage", "parked"), 23, "23 lost in total")


func test_last_phase_has_no_floor() -> void:
	var data := PhaseFixture.enemy(&"pk_last", 100, [0.5], RC.EnemyClass.ELITE)
	var s := PhaseFixture.session(data, 30)
	var e := PhaseFixture.aim(s)
	e.hp = 50
	s.apply(CombatAction.end_turn())  # at the floor: the last phase starts
	e = PhaseFixture.aim(s)
	assert_eq(e.phase_index, 1)
	assert_eq(e.hp_floor(), 0)
	e.hp = 20
	var r := s.apply(CombatAction.end_turn())
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").hp, 0, "HP reaches 0")
	assert_eq(r.state.outcome, CombatState.Outcome.VICTORY)


func test_normal_has_no_floor() -> void:
	var data := PhaseFixture.enemy(&"pk_normal", 20, [], RC.EnemyClass.NORMAL)
	var s := PhaseFixture.session(data, 30)
	PhaseFixture.aim(s)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").hp, 0)
	assert_eq(PhaseFixture.sum_of(r.events, "damage", "parked"), 0)


func test_floor_on_heal_not_clamped() -> void:
	var c := PhaseFixture.combatant(68, 100, 0.68)
	var events: Array[Dictionary] = []
	_fx.heal(c, 20, events)
	assert_eq(c.hp, 88, "healing above the floor is allowed")
	_fx.heal(c, 50, events)
	assert_eq(c.hp, 100, "max HP caps it")


func test_one_hp_max_edge() -> void:
	# max HP 1, threshold 0.5: the floor is ceil(0.5) = 1. HP 1 stands at the floor, so the
	# phase starts at the end of the first resolve: no softlock.
	var data := PhaseFixture.enemy(&"pk_tiny", 1, [0.5], RC.EnemyClass.ELITE)
	var s := PhaseFixture.session(data, 5)
	var e := PhaseFixture.aim(s)
	assert_eq(e.hp_floor(), 1)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").hp, 1, "parked on the first resolve")
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").phase_index, 1, "the phase starts anyway")
	PhaseFixture.aim(s)
	r = s.apply(CombatAction.end_turn())
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").hp, 0, "then it dies")
