extends GutTest
## Boss phase details (GDD 2.11): MIGRATE is telegraphed one turn ahead, wheel_override
## swaps the layout, ON_TURN_START satellite spawns respect every_n and max_active, and
## Intel reveals the phases ahead.

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


func test_account_manager_migrate_is_telegraphed_then_applied_next_turn() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"account_manager"], 5, &"rank:1")
	var b := s.state.get_combatant(&"enemy_0")
	b.hp = 20  # below 25% of 120: both phases fire
	CombatFixture.land(b, 5)
	CombatFixture.land(s.state.player, 5)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "boss_phase").size(), 2)
	assert_eq(CombatFixture.events_of(r, "boss_migrate_telegraph").size(), 1)
	# The telegraph fires in RESOLVE; the next START_TURN in the same apply() moves them.
	b = s.state.get_combatant(&"enemy_0")
	assert_eq(b.wheel.pointer_ticks, PackedInt32Array([5, 20]))
	assert_eq(CombatFixture.events_of(r, "boss_migrate").size(), 1)
	# Preview of the turn that triggers the phase still shows the old pointers.
	var s2 := CombatSession.start(_resolver, &"breaker", [&"account_manager"], 5, &"rank:1")
	var b2 := s2.state.get_combatant(&"enemy_0")
	b2.hp = 20
	CombatFixture.land(b2, 5)
	CombatFixture.land(s2.state.player, 5)
	var p := s2.preview_end_turn()
	assert_eq(p.resolved_state.get_combatant(&"enemy_0").wheel.pointer_ticks, PackedInt32Array([0, 15]), "resolved state: MULTIPLY applied, MIGRATE pending")
	assert_eq(p.resolved_state.get_combatant(&"enemy_0").wheel.pending_pointer_ticks, PackedInt32Array([5, 20]))


func test_renewal_engine_orbit_phase_reconfigures_the_wheel() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"renewal_engine"], 5, &"rank:1")
	var b := s.state.get_combatant(&"enemy_0")
	b.hp = 90
	CombatFixture.land(b, 5)
	CombatFixture.land(s.state.player, 5)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "boss_wheel_override").size(), 1)
	b = s.state.get_combatant(&"enemy_0")
	assert_eq(b.wheel.slot_slice_ids, [&"atk_14", &"crit_24", &"def_12", &"dose", &"crit_24", &"miss"])
	assert_eq(b.wheel.hub_id, &"auto_renew")
	assert_eq(b.wheel.pointer_ticks.size(), 2, "pointers from the MULTIPLY phase are kept")


func test_turn_start_spawns_follow_every_n_and_max_active() -> void:
	var atk := CombatFixture.slice(&"bt_atk", RC.SliceType.ATTACK, 3)
	var def := CombatFixture.slice(&"bt_def", RC.SliceType.DEFEND, 2, RC.TargetRule.SELF)
	var drone := CombatFixture.enemy(&"bt_drone", 4, CombatFixture.wheel([atk, def]))
	var spawn := SatelliteSpawnData.new()
	spawn.satellite = drone
	spawn.trigger = RC.Trigger.ON_TURN_START
	spawn.every_n = 2
	spawn.dock_slot = 1
	spawn.max_active = 1
	var host := CombatFixture.enemy(&"bt_host", 100, CombatFixture.miss_wheel(), [spawn])
	var noop: Array[CardData] = [CombatFixture.card(&"bt_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"bt_class", 60, CombatFixture.miss_wheel(), noop)
	var s := CombatSession.start(CombatFixture.resolver([cls, host, drone]), cls.id, [host.id], 2)
	assert_eq(s.state.satellites_of(&"enemy_0").size(), 0, "turn 1: count 1 of 2")
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "satellite_spawn").size(), 1, "turn 2 spawns")
	assert_eq(s.state.satellites_of(&"enemy_0").size(), 1)
	assert_eq(s.state.satellites_of(&"enemy_0")[0].dock_slot, 1)
	s.apply(CombatAction.end_turn())
	r = s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "satellite_spawn").size(), 0, "turn 4: max_active reached")
	s.state.satellites_of(&"enemy_0")[0].hp = 0
	s.apply(CombatAction.end_turn())
	r = s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "satellite_spawn").size(), 1, "turn 6: replaced after the drone died")


func test_intel_reveals_upcoming_phases() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"renewal_engine"], 5, &"rank:1", 0, {"reveal_phases": true})
	assert_eq(int(s.state.flags.get("reveal_phases", 0)), 1)
	var phases := _resolver.upcoming_phases(s.state, s.state.get_combatant(&"enemy_0"))
	assert_eq(phases.size(), 2)
	assert_eq(phases[0].pointer_behavior, RC.PointerBehavior.MULTIPLY)
