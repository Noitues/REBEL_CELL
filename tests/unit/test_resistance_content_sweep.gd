extends GutTest
## Plan 2 N21 sweep (rulings Q16, Q31): every shipped enemy's per-turn resistance lies in its
## class range (satellite wheels excepted), and a fight against it starts with exactly that
## much (enrage step 0 on turn 1), regained after the first end of turn.


func _fight_enemies() -> Array[EnemyData]:
	var out: Array[EnemyData] = []
	var ids := ContentRegistry.all_ids()
	ids.sort()
	for id in ids:
		var e := ContentRegistry.get_content(id) as EnemyData
		if e != null and e.wheel != null and e.wheel.slice_count == RC.SLICES:
			out.append(e)
	return out


func test_every_shipped_enemy_is_in_its_class_range() -> void:
	var cfg := ContentRegistry.config
	var enemies := _fight_enemies()
	assert_gt(enemies.size(), 40, "the sweep sees the shipped roster")
	for e in enemies:
		var cls := e.enemy_class()
		var r := e.turn_resistance()
		assert_between(r, cfg.resistance_min_by_class[cls], cfg.resistance_max_by_class[cls], String(e.id))
		for problem in e.validate(cfg):
			assert_false(problem.begins_with("resistance_out_of_range"), problem)


func test_every_fight_starts_and_refreshes_at_the_authored_value() -> void:
	var resolver := CombatFixture.resolver()
	for e in _fight_enemies():
		var s := CombatSession.start(resolver, &"breaker", [e.id], 3)
		var c := s.state.get_combatant(&"enemy_0")
		assert_eq(c.resistance, e.turn_resistance(), "%s turn 1" % e.id)
		assert_eq(c.resistance_gain, e.turn_resistance(), "%s +N" % e.id)
		if not s.state.is_over():
			s.apply(CombatAction.end_turn())
			if not s.state.is_over():
				c = s.state.get_combatant(&"enemy_0")
				assert_eq(c.resistance, c.resistance_gain, "%s turn 2: regained (from 0) at the refresh" % e.id)
				assert_gt(c.resistance_gain, 0, "%s turn 2" % e.id)
