extends GutTest
## Plan 2 N3 flow: a parked hit then a phase change, as the combat HUD shows it: the result
## chips (ResultChipModel, what the scene draws) read "PARKED −N" in the preview and after
## SEND IT, and the phase line is said once.


func _session() -> CombatSession:
	var data := PhaseFixture.enemy(&"pf_flow", 100, [0.68, 0.33], RC.EnemyClass.MINI_BOSS)
	data.phases[0].phase_line = "pf_flow phase line"
	return PhaseFixture.session(data, 30)


func test_parked_chip_shows_amount() -> void:
	var s := _session()
	var e := PhaseFixture.aim(s)
	e.hp = 80
	var before := s.state.duplicate_state()
	var pv := s.preview_end_turn()
	var shown := RealChips.build(s.resolver, before, null, pv.resolved_state, pv.events, &"enemy_0", RC.Status.NONE, 0)
	var r := s.apply(CombatAction.end_turn())
	var real := RealChips.build(s.resolver, before, null, r.resolved_state, r.events, &"enemy_0", RC.Status.NONE, 0)
	assert_eq(ResultChipModel.value_of(real, ResultChipModel.PARKED), 18, "30 - 12 to the floor")
	assert_eq(ResultChipModel.value_of(shown, ResultChipModel.PARKED), 18, "preview chip == result chip")
	var chip: Dictionary = {}
	for c in shown:
		if StringName(c["kind"]) == ResultChipModel.PARKED:
			chip = c
	assert_eq(ResultChipModel.label(chip), "PARKED −18")
	assert_eq(HudResultChips.parts(chip)["words"], "PARKED −18", "no HP tag in front")
	assert_eq(ResultChipModel.hp_change(real), -12, "the HP chips still say the real loss")


func test_phase_line_plays_once() -> void:
	var s := _session()
	var e := PhaseFixture.aim(s)
	e.hp = 80
	var r := s.apply(CombatAction.end_turn())
	var lines := 0
	for ev in r.events:
		if String(ev.get("text", "")).contains("pf_flow phase line"):
			lines += 1
	assert_eq(lines, 1, "entering the phase says its line once")
	PhaseFixture.aim(s)
	r = s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "boss_phase").size(), 0, "no second entry while above the next floor")
