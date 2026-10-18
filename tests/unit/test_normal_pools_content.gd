extends GutTest
## Plan 2 N22 (ruling Q12), shipped content: every enemy validates with its normal_pool (only
## normals EASY), and the classification table in docs/handoff/N22_POOLS.md (one row per
## normal: corp, id, pool) matches the .tres both ways.

const TABLE_PATH := "res://docs/handoff/N22_POOLS.md"


func _cfg() -> CampaignConfigData:
	return load("res://content/config/campaign_config.tres") as CampaignConfigData


## The fight-class normals of the shipped content: {id: EnemyData}.
func _normals() -> Dictionary:
	var out := {}
	for id in CombatFixture.resolver().lookup.ids_of_class(&"EnemyData"):
		var e := ContentRegistry.get_content(id) as EnemyData
		if e.wheel != null and e.wheel.slice_count == RC.SLICES and e.enemy_class() == RC.EnemyClass.NORMAL:
			out[id] = e
	return out


## {id: [corp, pool]} from the table rows `| corp | `id` | EASY/HARD | ...` (the id in backticks).
func _table() -> Dictionary:
	var out := {}
	var f := FileAccess.open(TABLE_PATH, FileAccess.READ)
	assert_not_null(f, "the classification table exists")
	if f == null:
		return out
	for line in f.get_as_text().split("\n"):
		var cells := line.split("|")
		if cells.size() < 5:
			continue
		var pool := cells[3].strip_edges()
		if (pool != "EASY" and pool != "HARD") or not cells[2].strip_edges().begins_with("`"):
			continue
		out[StringName(cells[2].strip_edges().trim_prefix("`").trim_suffix("`"))] = [cells[1].strip_edges(), pool]
	return out


func test_every_enemy_validates_its_pool() -> void:
	var cfg := _cfg()
	for id in CombatFixture.resolver().lookup.ids_of_class(&"EnemyData"):
		var e := ContentRegistry.get_content(id) as EnemyData
		assert_eq(e.validate(cfg), PackedStringArray(), "%s validates (no EASY on a non-normal)" % id)


func test_classification_table_matches_the_tres() -> void:
	var table := _table()
	var normals := _normals()
	assert_eq(table.size(), normals.size(), "one row per normal")
	for id in table:
		assert_true(normals.has(id), "row %s is a shipped normal" % id)
	for id in normals:
		var e: EnemyData = normals[id]
		assert_true(table.has(id), "%s has a row" % id)
		if table.has(id):
			assert_eq(table[id][0], String(e.corporation_id), "%s corp" % id)
			assert_eq(table[id][1], RC.NormalPool.keys()[e.normal_pool], "%s pool" % id)


func test_every_corp_has_at_least_two_easy_normals() -> void:
	var easy := {}
	for id in _normals():
		var e: EnemyData = _normals()[id]
		easy[e.corporation_id] = int(easy.get(e.corporation_id, 0)) + (1 if e.normal_pool == RC.NormalPool.EASY else 0)
	assert_false(easy.is_empty())
	for corp in easy:
		assert_true(easy[corp] >= _cfg().easy_normal_fights, "%s has %d EASY normals" % [corp, easy[corp]])
