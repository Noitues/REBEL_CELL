extends GutTest
## Plan 2 N4 flow (ruling Q33): the enrage as the combat HUD shows it. No buff before step 1;
## from step 1 a badge on the enemy wheel reads the step, its tooltip says the hit factor and
## the next step (from enrage_buff_state, TextDb words); the operative's HP chip in the
## preview equals the one after SEND IT on an enraged turn.


func _session(turn: int, cls: int = RC.EnemyClass.BOSS) -> CombatSession:
	var s := EnrageFixture.session(EnrageFixture.enemy(&"enr_hud", cls, 10))
	EnrageFixture.to_turn(s, turn)
	EnrageFixture.aim(s)
	return s


func _view() -> Control:
	var v := Control.new()
	v.size = Vector2(400, 400)
	add_child_autofree(v)
	return v


func test_buff_shows_and_steps_in_boss_fight() -> void:
	var v := _view()
	var s := _session(9)
	EnrageBuff.sync(v, s.resolver.enrage_buff_state(s.state, s.state.get_combatant(&"enemy_0")))
	assert_null(v.get_node_or_null(EnrageBuff.NODE_NAME), "no countdown before step 1")
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.turn, 10)
	var st := s.resolver.enrage_buff_state(s.state, s.state.get_combatant(&"enemy_0"))
	EnrageBuff.sync(v, st)
	var badge := v.get_node_or_null(EnrageBuff.NODE_NAME) as Badge
	assert_not_null(badge)
	assert_eq(badge.text, "ENRAGE 1")
	assert_true(badge.tooltip_text.contains("125%"), badge.tooltip_text)
	assert_true(badge.tooltip_text.contains("turn 15"), badge.tooltip_text)
	assert_true(Rect2(Vector2.ZERO, v.size).encloses(Rect2(badge.position, badge.size)), "the badge sits on the wheel")


func test_buff_absent_on_normal() -> void:
	var v := _view()
	var s := _session(20, RC.EnemyClass.NORMAL)
	EnrageBuff.sync(v, s.resolver.enrage_buff_state(s.state, s.state.get_combatant(&"enemy_0")))
	assert_null(v.get_node_or_null(EnrageBuff.NODE_NAME))


func test_buff_matches_buff_state() -> void:
	var s := _session(16)
	var st := s.resolver.enrage_buff_state(s.state, s.state.get_combatant(&"enemy_0"))
	assert_eq(EnrageBuff.label(st), "ENRAGE %d" % int(st["step"]))
	var tip := EnrageBuff.tooltip(st)
	assert_true(tip.contains("%d%%" % int(st["percent"])), tip)
	assert_true(tip.contains("in %d turns" % int(st["turns_to_next"])), tip)


func test_preview_hp_chip_equals_result_when_enraged() -> void:
	var s := _session(15)
	var before := s.state.duplicate_state()
	var pv := s.preview_end_turn()
	var shown := RealChips.build(s.resolver, before, null, pv.resolved_state, pv.events, &"player", RC.Status.NONE, 0)
	var r := s.apply(CombatAction.end_turn())
	var real := RealChips.build(s.resolver, before, null, r.resolved_state, r.events, &"player", RC.Status.NONE, 0)
	assert_eq(ResultChipModel.hp_change(real), -15, "10 x 1.5 at step 2")
	assert_eq(ResultChipModel.hp_change(shown), ResultChipModel.hp_change(real), "preview chip == result chip")
