extends GutTest
## Plan 2 N4 (R4, rulings Q33 / Q16): the enrage in a fight. start_turn sets the step from the
## turn; enemy hits (only) scale by 1 + step x pct, rounded half up, before block, shield and
## the phase clamp; the preview equals the result at every step; resistance_step adds
## resistance; the buff state is hidden until step 1.


func _boss(hit: int = 10, authored: EnrageData = null, pointers: Array = [0]) -> EnemyData:
	return EnrageFixture.enemy(&"enr_boss", RC.EnemyClass.BOSS, hit, 999, authored, pointers)


func _at(data: EnemyData, turn: int, dmg: int = 0) -> CombatSession:
	var s := EnrageFixture.session(data, dmg)
	EnrageFixture.to_turn(s, turn)
	EnrageFixture.aim(s)
	return s


func test_enemy_hit_scaled_on_step_turn() -> void:
	var s := _at(_boss(), 10)
	assert_eq(s.state.get_combatant(&"enemy_0").enrage_step, 1)
	var lost := EnrageFixture.hp_lost_preview_and_actual(s)
	assert_eq(lost[1], 13, "10 x 1.25 = 12.5, rounded half up (EnrageData.scale_hit)")
	assert_eq(lost[0], lost[1])


func test_start_turn_sets_step_once() -> void:
	var s := _at(_boss(), 15)
	var e := s.state.get_combatant(&"enemy_0")
	var before := e.to_dict()
	var events: Array[Dictionary] = []
	s.resolver.refresh_enrage(s.state, e, events)
	s.resolver.refresh_enrage(s.state, e, events)
	assert_eq(e.enrage_step, 2)
	assert_eq(e.to_dict(), before, "recomputing on the same turn changes nothing")
	assert_eq(events.size(), 0, "no second enrage event")


func test_enrage_event_when_step_rises() -> void:
	var s := EnrageFixture.session(_boss())
	s.state.turn = 9
	var events: Array[Dictionary] = []
	s.resolver.start_turn(s.state, s.rng, events)
	var found := events.filter(func(ev: Dictionary) -> bool: return ev["type"] == "enrage")
	assert_eq(found.size(), 1)
	assert_eq(int(found[0]["step"]), 1)


func test_preview_equals_result_every_step() -> void:
	var want := {9: 10, 10: 13, 15: 15, 20: 18}
	for turn: int in want:
		var s := _at(_boss(), turn)
		var lost := EnrageFixture.hp_lost_preview_and_actual(s)
		assert_eq(lost[1], want[turn], "turn %d" % turn)
		assert_eq(lost[0], lost[1], "turn %d: preview == result" % turn)


func test_enrage_ignores_heal() -> void:
	var s := _at(_boss(), 15)
	var e := s.state.get_combatant(&"enemy_0")
	var heal := CombatFixture.effect(RC.EffectType.HEAL, RC.EffectTarget.SELF, 2)
	heal.amount_mode = RC.AmountMode.PERCENT
	var enraged := s.resolver.fx.effect_amount(heal, e)
	e.enrage_step = 0
	e.enrage_percent = RC.PERCENT_MAX
	assert_eq(enraged, s.resolver.fx.effect_amount(heal, e), "a 2 % heal is the same at step 2")


func test_enrage_ignores_block_and_shield() -> void:
	var defrag := CombatFixture.slice(&"enr_defrag", RC.SliceType.DEFRAG, 12)
	var w := CombatFixture.wheel([defrag, defrag, defrag, defrag, defrag, defrag])
	var data := PhaseFixture.enemy(&"enr_blocker", 999, [], RC.EnemyClass.BOSS, w)
	var s := _at(data, 15)
	assert_eq(s.state.get_combatant(&"enemy_0").enrage_step, 2)
	var pv := s.preview_end_turn()
	assert_eq(pv.resolved_state.get_combatant(&"enemy_0").block, 12, "block is not a hit")


func test_enrage_stacks_with_tier_factor() -> void:
	var s := _at(_boss(5), 10)
	s.state.get_combatant(&"enemy_0").output_scale = 1.69
	var lost := EnrageFixture.hp_lost_preview_and_actual(s)
	assert_eq(lost[1], 10, "T3: round(5 x 1.69) = 8, then x1.25 = 10")
	assert_eq(lost[0], lost[1])


func test_enrage_does_not_hit_player_damage() -> void:
	var s := _at(_boss(), 15, 10)
	var hp := s.state.get_combatant(&"enemy_0").hp
	var r := s.apply(CombatAction.end_turn())
	assert_eq(hp - r.resolved_state.get_combatant(&"enemy_0").hp, 10, "the operative's hit is unchanged")


func test_enrage_applies_to_every_pointer() -> void:
	var s := _at(_boss(10, null, [0, 15]), 10)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 3, 0, 1)
	var lost := EnrageFixture.hp_lost_preview_and_actual(s)
	assert_eq(lost[1], 26, "both needles hit 13")
	assert_eq(lost[0], lost[1])


func test_enrage_before_block() -> void:
	var s := _at(_boss(), 10)
	s.state.player.block = 5
	var lost := EnrageFixture.hp_lost_preview_and_actual(s)
	assert_eq(lost[1], 8, "13 enraged, 5 blocked")


func test_evade_still_negates_enraged_hit() -> void:
	var s := _at(_boss(), 15)
	s.state.player.evade_charges = 1
	var lost := EnrageFixture.hp_lost_preview_and_actual(s)
	assert_eq(lost[1], 0)
	assert_eq(lost[0], 0)


func test_enrage_persists_across_phase_change() -> void:
	var data := EnrageFixture.enemy(&"enr_phased", RC.EnemyClass.BOSS, 1, 100)
	data.phases = [PhaseFixture.phase(0.5)] as Array[BossPhaseData]
	var s := _at(data, 10, 80)
	var r := s.apply(CombatAction.end_turn())
	var e := r.resolved_state.get_combatant(&"enemy_0")
	assert_eq(e.phase_index, 1, "the phase changed this turn")
	assert_eq(e.enrage_step, 1, "and the enrage kept its step")
	assert_eq(s.state.get_combatant(&"enemy_0").enrage_step, 1, "turn 11 is still step 1")


func test_resistance_step_adds_resistance() -> void:
	var s := _at(_boss(10, EnrageFixture.enrage(10, 5, 0, 2)), 15)
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(e.enrage_resistance, 4, "2 steps x 2")
	assert_eq(e.resistance, 4, "added to the start-of-turn restore")
	assert_eq(e.full_resistance(), 4)
	var lost := EnrageFixture.hp_lost_preview_and_actual(s)
	assert_eq(lost[1], 10, "a 0 % step leaves the hits alone")


func test_satellites_never_enrage() -> void:
	var s := _at(_boss(), 15)
	var sat := s.state.get_combatant(&"enemy_0").duplicate_state()
	sat.is_satellite = true
	assert_null(s.resolver.enrage_of(sat))
	assert_null(s.resolver.enrage_of(s.state.player))


func test_buff_state_hidden_before_step_one() -> void:
	var s := _at(_boss(), 9)
	var st := s.resolver.enrage_buff_state(s.state, s.state.get_combatant(&"enemy_0"))
	assert_false(st["visible"], "no countdown before step 1 (Q33)")


func test_buff_state_at_step() -> void:
	var s := _at(_boss(), 12)
	var st := s.resolver.enrage_buff_state(s.state, s.state.get_combatant(&"enemy_0"))
	assert_true(st["visible"])
	assert_eq(st["step"], 1)
	assert_eq(st["percent"], 125)
	assert_eq(st["step_percent"], 25)
	assert_eq(st["next_turn"], 15)
	assert_eq(st["turns_to_next"], 3)


func test_buff_state_hidden_for_normal() -> void:
	var s := _at(EnrageFixture.enemy(&"enr_norm", RC.EnemyClass.NORMAL, 10), 30)
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(e.enrage_step, 0)
	assert_false(s.resolver.enrage_buff_state(s.state, e)["visible"])
	var lost := EnrageFixture.hp_lost_preview_and_actual(s)
	assert_eq(lost[1], 10, "normals never enrage")
