extends GutTest
## Plan 2 N4 sweep (full tier): every shipped enemy resolves its enrage by class (normal off,
## elite 8, mini-boss / boss 10, an authored one wins), no normal carries one, and every
## enemy still validates.


func _enemies() -> Array[EnemyData]:
	var out: Array[EnemyData] = []
	var ids := ContentRegistry.all_ids()
	ids.sort()
	for id in ids:
		var data := ContentRegistry.get_content(id) as EnemyData
		if data != null:
			out.append(data)
	return out


func test_all_enemies_resolve_enrage_by_class() -> void:
	var cfg := CombatFixture.config()
	var list := _enemies()
	assert_gt(list.size(), 50)
	for data in list:
		var en := cfg.enrage_for(data)
		match data.enemy_class():
			RC.EnemyClass.NORMAL:
				assert_null(en, "%s is a normal: no enrage" % data.id)
				assert_null(data.enrage, "%s: no authored enrage on a normal" % data.id)
			RC.EnemyClass.ELITE:
				assert_eq(en.start_turn, data.enrage.start_turn if data.enrage != null else 8, String(data.id))
			_:
				assert_eq(en.start_turn, data.enrage.start_turn if data.enrage != null else 10, String(data.id))


func test_all_authored_enrage_validate() -> void:
	for data in _enemies():
		if data.enrage != null:
			assert_eq(data.enrage.validate(), PackedStringArray(), String(data.id))
		var errors := data.validate()
		for e in errors:
			assert_false(e.contains("enrage"), "%s: %s" % [data.id, e])
