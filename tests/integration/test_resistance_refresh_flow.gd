extends GutTest
## Plan 2 N21 flow (rulings Q16, Q31): the "+N" grease-pencil mark beside the enemy's RESIST
## chip. It shows the amount gained at each refresh (turn 1 included), once per refresh,
## stays static for the turn, and never appears in a fight whose enemy gains 0.


func _session(passive: int) -> CombatSession:
	var e := PhaseFixture.enemy(&"n21_flow", 999, [], RC.EnemyClass.NORMAL, CombatFixture.null_wheel(passive))
	e.phases.clear()
	return PhaseFixture.session(e, 0)


func _view(c: CombatantState) -> WheelView:
	var v: WheelView = autofree(WheelView.new())
	v.combatant = c
	return v


func _marks(v: WheelView) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for chip in v.standing_chips():
		if bool(chip.get("pencil", false)):
			out.append(chip)
	return out


func test_the_mark_shows_the_gain_once_per_refresh() -> void:
	var s := _session(2)
	var marks := _marks(_view(s.state.get_combatant(&"enemy_0")))
	assert_eq(marks.size(), 1, "one mark")
	assert_eq(String(marks[0]["text"]), "+2")
	assert_eq(marks[0]["color"], Palette.PENCIL_THREAT, "grease pencil, threat ink")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	marks = _marks(_view(s.state.get_combatant(&"enemy_0")))
	assert_eq(String(marks[0]["text"]), "+2", "static: spending resistance leaves the gained amount")
	s.apply(CombatAction.end_turn())
	marks = _marks(_view(s.state.get_combatant(&"enemy_0")))
	assert_eq(marks.size(), 1, "the next refresh: one mark again")
	assert_eq(String(marks[0]["text"]), "+2")


func test_no_mark_on_a_fight_with_zero_gain() -> void:
	var s := _session(0)
	assert_eq(_marks(_view(s.state.get_combatant(&"enemy_0"))).size(), 0)
	s.apply(CombatAction.end_turn())
	assert_eq(_marks(_view(s.state.get_combatant(&"enemy_0"))).size(), 0)
	assert_eq(_marks(_view(s.state.player)).size(), 0, "the operative never shows one")


func test_the_chip_row_lays_the_mark_out_after_resist() -> void:
	var s := _session(2)
	var row: HudResultChips = autofree(HudResultChips.new())
	row.set_standing(_view(s.state.get_combatant(&"enemy_0")).standing_chips())
	var rects := row.standing_rects()
	assert_eq(rects.size(), 2, "RESIST and +2")
	assert_eq(String(row.standing[0]["text"]), "RESIST 2")
	assert_gt(rects[1].position.x, rects[0].end.x - 0.01, "the mark follows the RESIST chip")
	assert_gt(rects[1].size.x, 0.0)
