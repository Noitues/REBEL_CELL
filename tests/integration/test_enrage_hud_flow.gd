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


func test_tooltip_plate_stands_outside_the_disc_clear_of_the_rim() -> void:
	var bounds := Rect2(0, 0, 1920, 1080)
	var center := Vector2(1450, 300)
	var radius := 150.0
	var gap := EnrageBadge.PLATE_GAP
	# the badge on the upper right rim (-45 degrees), as EnrageBuff hangs it
	var corner := center + Vector2.from_angle(-PI * 0.25) * (radius + 6.0)
	var badge := Rect2(corner - Vector2(0, 20), Vector2(90, 20))
	var sz := Vector2(300, 60)
	var r := EnrageBadge.plate_rect(badge, sz, center, radius, bounds, gap, EnrageBadge.BADGE_GAP)
	var nearest := Vector2(clampf(center.x, r.position.x, r.end.x), clampf(center.y, r.position.y, r.end.y))
	assert_gte(nearest.distance_to(center), radius + gap - 0.01, "12 px clear of the rim ring")
	assert_true(bounds.encloses(r), "clamped to the view")
	assert_gte(r.position.y, badge.end.y, "below the badge")
	# no room on the right: the plate is held inside the view and still clear of the rim
	var edge := EnrageBadge.plate_rect(Rect2(Vector2(1800, 100), Vector2(90, 20)), sz, Vector2(1700, 300), 150.0, bounds, gap, EnrageBadge.BADGE_GAP)
	assert_true(bounds.encloses(edge), "clamped at the screen's edge")
	var near := Vector2(clampf(1700.0, edge.position.x, edge.end.x), clampf(300.0, edge.position.y, edge.end.y))
	assert_gte(near.distance_to(Vector2(1700, 300)), 150.0 + gap - 0.01, "clear of the rim at the edge too")


func test_badge_keeps_its_words_but_not_the_native_popup() -> void:
	var v := _view()
	var s := _session(9)
	s.apply(CombatAction.end_turn())
	EnrageBuff.sync(v, s.resolver.enrage_buff_state(s.state, s.state.get_combatant(&"enemy_0")))
	var badge := v.get_node_or_null(EnrageBuff.NODE_NAME) as EnrageBadge
	assert_not_null(badge)
	assert_ne(badge.tooltip_text, "")
	assert_eq(badge._get_tooltip(Vector2.ZERO), "", "the plate is the tooltip, not the native popup")


func test_refusal_toast_stands_beside_the_aim_ring() -> void:
	var bounds := Rect2(0, 0, 1920, 1080)
	var sz := Vector2(240, 50)
	var p := Toast.beside_position(sz, Vector2(1500, 400), 40.0, bounds, Toast.BESIDE_GAP)
	assert_eq(p.x, 1500.0 + 40.0 + Toast.BESIDE_GAP, "right of the ring")
	var left := Toast.beside_position(sz, Vector2(1800, 400), 40.0, bounds, Toast.BESIDE_GAP)
	assert_eq(left.x + sz.x, 1800.0 - 40.0 - Toast.BESIDE_GAP, "left of it when the right has no room")
	assert_false(Rect2(left, sz).intersects(Rect2(Vector2(1760, 360), Vector2(80, 80))), "never over the ring")


func test_satellite_refusal_is_timed_in_the_table_and_ends_at_rest() -> void:
	assert_true(Motion.has(&"satellite_refusal") and UiMotionData.REQUIRED_IDS.has(&"satellite_refusal"))
	assert_almost_eq(Motion.seconds(&"satellite_refusal"), 0.25, 0.001)
	assert_lte(Motion.shake_px(&"satellite_refusal"), 3.0, "within 3 px")
	var w := WheelView.new()
	add_child_autofree(w)
	w.sat_refusal = 0.2
	assert_ne(w.sat_refusal_flash(), 0.0)
	w.play_satellite_refusal()  # headless / reduce effects: the end state at once
	assert_eq(w.sat_refusal, 0.0)
	assert_eq(w.sat_refusal_offset(), Vector2.ZERO)
	assert_eq(w.sat_refusal_flash(), 0.0)
