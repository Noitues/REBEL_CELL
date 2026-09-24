extends GutTest
## Every Daemon in the slice has a unit test (M2 acceptance, GDD 6.2). Combat-side
## Daemons here; Cold Exit and Scrubber (run-level) are covered in test_netrun.

var _atk6: SliceData
var _crit12: SliceData
var _miss: SliceData


func before_each() -> void:
	_atk6 = CombatFixture.slice(&"dm_atk6", RC.SliceType.ATTACK, 6)
	_crit12 = CombatFixture.slice(&"dm_crit12", RC.SliceType.CRIT, 12)
	_miss = CombatFixture.slice(&"dm_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)


func _session(daemon_ids: Array) -> CombatSession:
	var deck: Array[CardData] = [CombatFixture.card(&"dm_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"dm_class", 60, CombatFixture.wheel([_crit12, _atk6, _atk6, _atk6, _atk6, _miss]), deck)
	var dummy := CombatFixture.enemy(&"dm_dummy", 300, CombatFixture.miss_wheel())
	var ids := []
	for d in daemon_ids:
		ids.append(String(d))
	var s := CombatSession.start(CombatFixture.resolver([cls, dummy]), cls.id, [dummy.id], 6, &"", 0, {"daemon_ids": ids})
	assert_eq(s.state.daemon_ids.size(), daemon_ids.size())
	return s


func _enemy(s: CombatSession) -> CombatantState:
	return s.state.get_combatant(&"enemy_0")


func test_clean_signal_fires_on_the_third_consecutive_perfect() -> void:
	var s := _session([&"clean_signal"])
	for turn in 3:
		CombatFixture.land(s.state.player, 1, 0)
		var r := s.apply(CombatAction.end_turn())
		var heat := CombatFixture.events_of(r, "campaign_effect")
		if turn < 2:
			assert_eq(heat.size(), 0, "turn %d: not yet" % (turn + 1))
		else:
			assert_eq(heat.size(), 1, "third Perfect")
			assert_eq(heat[0]["amount"], -2)
			assert_eq(heat[0]["source_id"], &"clean_signal")
	assert_eq(s.state.consecutive_perfects, 3)
	CombatFixture.land(s.state.player, 1, 1)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.consecutive_perfects, 0, "a Good landing resets the streak")


func test_fault_tolerance_makes_the_miss_slice_hit_for_3() -> void:
	var s := _session([&"fault_tolerance"])
	CombatFixture.land(s.state.player, 5)
	var r := s.apply(CombatAction.end_turn())
	var hits := CombatFixture.events_of(r, "damage")
	assert_eq(hits.size(), 1)
	assert_eq(hits[0]["amount"], 3)
	assert_eq(hits[0]["source_id"], &"fault_tolerance")
	assert_eq(_enemy(s).hp, 297)


func test_kernel_sync_adds_1_damage_per_perfect() -> void:
	var s := _session([&"kernel_sync"])
	CombatFixture.land(s.state.player, 1, 0)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(s.state.damage_bonus, 1)
	assert_eq(CombatFixture.events_of(r, "damage")[0]["amount"], 6, "the bonus applies from the next attack on")
	CombatFixture.land(s.state.player, 2, 1)
	r = s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "damage")[0]["amount"], 7, "Good landing gets the +1")
	CombatFixture.land(s.state.player, 0, 0)
	r = s.apply(CombatAction.end_turn())
	assert_eq(s.state.damage_bonus, 2)
	assert_eq(CombatFixture.events_of(r, "damage")[0]["amount"], 13, "Crit 12 + 1 (the second Perfect grants after it hits)")


func test_zero_day_turns_a_perfect_miss_into_a_3x_crit() -> void:
	var s := _session([&"zero_day"])
	CombatFixture.land(s.state.player, 5, 0)
	var r := s.apply(CombatAction.end_turn())
	var hits := CombatFixture.events_of(r, "damage")
	assert_eq(hits.size(), 1)
	assert_eq(hits[0]["amount"], 36, "3 x Crit 12")
	assert_eq(_enemy(s).hp, 264)
	s = _session([&"zero_day"])
	CombatFixture.land(s.state.player, 5, 1)
	r = s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "damage").size(), 0, "only on a Perfect")


func test_daemons_survive_save_and_load_and_replay() -> void:
	var s := _session([&"kernel_sync", &"fault_tolerance"])
	CombatFixture.land(s.state.player, 1, 0)
	s.apply(CombatAction.end_turn())
	var loaded := CombatSession.from_dict(s.resolver, JSON.parse_string(JSON.stringify(s.to_dict())))
	assert_eq(loaded.state.daemon_ids, [&"kernel_sync", &"fault_tolerance"])
	assert_eq(loaded.state.damage_bonus, 1)
	var replayed := CombatSession.replay(s.resolver, s.setup, s.combat_seed, s.history)
	assert_eq(replayed.state.daemon_ids.size(), 2)


func test_all_six_daemons_exist() -> void:
	for id in [&"clean_signal", &"cold_exit", &"scrubber", &"fault_tolerance", &"kernel_sync", &"zero_day"]:
		assert_not_null(ContentRegistry.get_content(id) as DaemonData, String(id))
	assert_not_null((ContentRegistry.get_content(&"cold_exit") as DaemonData).custom_handler)
	assert_not_null((ContentRegistry.get_content(&"scrubber") as DaemonData).custom_handler)
