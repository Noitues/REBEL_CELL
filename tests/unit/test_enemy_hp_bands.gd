extends GutTest
## N2 (CONTENT_DESIGN_V2 R2): EnemyData.hp_by_tier / hp_bands and validate()'s named band
## rejections per class (normal, elite, mini-boss 2 / 3 phases, boss).

var _cfg: CampaignConfigData


func before_all() -> void:
	_cfg = CombatFixture.config()


func _enemy(hp_by_tier: Array, elite: bool = false, mini: bool = false, phase_entries: int = 0) -> EnemyData:
	var e := CombatFixture.enemy(&"n2_e", 30, CombatFixture.null_wheel())
	e.hp_by_tier = PackedInt32Array(hp_by_tier)
	e.is_elite = elite
	e.is_mini_boss = mini
	for i in phase_entries:
		var p := BossPhaseData.new()
		p.hp_threshold_pct = 0.66 - 0.33 * i
		e.phases.append(p)
	return e


func _boss(bands: Array[Vector2]) -> EnemyData:
	var e := CombatFixture.enemy(&"n2_boss", 300, CombatFixture.null_wheel())
	e.is_boss = true
	e.hp_bands = bands
	return e


## Only the HP-table problems (phase data on fixtures is not under test here).
func _hp_errors(e: EnemyData) -> PackedStringArray:
	var out := PackedStringArray()
	for p in e.validate(_cfg):
		if p.contains("hp_by_tier") or p.contains("hp_bands"):
			out.append(p)
	return out


func _genome_core_bands() -> Array[Vector2]:
	return [Vector2(1.0, 300), Vector2(1.15, 330), Vector2(1.30, 360), Vector2(99.0, 400)]


func test_normal_validate_accepts_in_band_and_edges() -> void:
	assert_eq(_hp_errors(_enemy([32, 40, 50, 63])), PackedStringArray())
	assert_eq(_hp_errors(_enemy([28, 34, 44, 56])), PackedStringArray(), "lower edges")
	assert_eq(_hp_errors(_enemy([36, 44, 56, 70])), PackedStringArray(), "upper edges")


func test_normal_validate_rejects_below_band_with_named_reason() -> void:
	var errors := _hp_errors(_enemy([32, 40, 43, 63]))
	assert_eq(errors.size(), 1)
	assert_string_contains(errors[0], "hp_by_tier[2] 43 outside normal band 44-56")
	assert_string_contains(errors[0], "n2_e")
	assert_string_contains(errors[0], "T3")


func test_normal_validate_rejects_above_band() -> void:
	assert_eq(_hp_errors(_enemy([32, 40, 57, 63])).size(), 1)


func test_elite_band_edges_t1_to_t4() -> void:
	var lo := [56, 68, 88, 112]
	var hi := [72, 88, 112, 144]
	assert_eq(_hp_errors(_enemy(lo, true)), PackedStringArray())
	assert_eq(_hp_errors(_enemy(hi, true)), PackedStringArray())
	for t in 4:
		var below: Array = lo.duplicate()
		below[t] -= 1
		assert_eq(_hp_errors(_enemy(below, true)).size(), 1, "T%d min - 1 rejected" % (t + 1))
		var above: Array = hi.duplicate()
		above[t] += 1
		assert_eq(_hp_errors(_enemy(above, true)).size(), 1, "T%d max + 1 rejected" % (t + 1))


func test_miniboss_2_and_3_phase_bands() -> void:
	var two := _enemy([63, 77, 98, 0], true, true, 1)
	assert_eq(two.band_class(), &"mini_boss_2")
	assert_eq(_hp_errors(two), PackedStringArray())
	var three := _enemy([95, 116, 147, 0], true, true, 2)
	assert_eq(three.band_class(), &"mini_boss_3")
	assert_eq(_hp_errors(three), PackedStringArray())
	var wrong := _enemy([95, 77, 147, 0], true, true, 2)
	var errors := _hp_errors(wrong)
	assert_eq(errors.size(), 1)
	assert_string_contains(errors[0], "outside mini-boss 3-phase band 104-128")


func test_miniboss_rejects_t4_entry() -> void:
	var errors := _hp_errors(_enemy([63, 77, 98, 120], true, true, 1))
	assert_eq(errors.size(), 1)
	assert_string_contains(errors[0], "mini-boss has no T4 band")


func test_miniboss_t4_reads_t3() -> void:
	assert_eq(_enemy([63, 77, 98, 0], true, true, 1).hp_at_tier(4), 98)


func test_hp_by_tier_wrong_length_rejected() -> void:
	var errors := _hp_errors(_enemy([30, 40, 50]))
	assert_eq(errors.size(), 1)
	assert_string_contains(errors[0], "hp_by_tier must have 4 entries")


func test_hp_at_tier_clamps() -> void:
	var e := _enemy([30, 40, 50, 60])
	assert_eq(e.hp_at_tier(0), 30)
	assert_eq(e.hp_at_tier(1), 30)
	assert_eq(e.hp_at_tier(3), 50)
	assert_eq(e.hp_at_tier(9), 60)


func test_boss_hp_bands_lookup_zones() -> void:
	var b := _boss(_genome_core_bands())
	assert_eq(_hp_errors(b), PackedStringArray())
	assert_eq(b.hp_for(1.0), 300)
	assert_eq(b.hp_for(1.01), 330)
	assert_eq(b.hp_for(1.15), 330)
	assert_eq(b.hp_for(1.0 + 15.0 / 100.0), 330, "ICE +15 % sits on the ceiling")
	assert_eq(b.hp_for(1.30), 360)
	assert_eq(b.hp_for(1.31), 400)
	assert_eq(b.hp_for(250.0), 400, "the last band is open-ended")


func test_boss_hp_bands_must_be_sorted() -> void:
	var errors := _hp_errors(_boss([Vector2(1.15, 330), Vector2(1.0, 300), Vector2(99.0, 400)]))
	assert_true(Array(errors).any(func(p: String) -> bool: return p.contains("hp_bands ceilings must ascend")))


func test_boss_hp_bands_last_ceiling_open() -> void:
	var errors := _hp_errors(_boss([Vector2(1.0, 300), Vector2(1.15, 330), Vector2(1.30, 360)]))
	assert_eq(errors.size(), 1)
	assert_string_contains(errors[0], "hp_bands must cover multiplier > last ceiling")


func test_boss_rejects_hp_by_tier_and_non_boss_rejects_hp_bands() -> void:
	var b := _boss(_genome_core_bands())
	b.hp_by_tier = PackedInt32Array([1, 2, 3, 4])
	assert_true(Array(_hp_errors(b)).any(func(p: String) -> bool: return p.contains("uses hp_bands, not hp_by_tier")))
	var n := _enemy([32, 40, 50, 63])
	n.hp_bands = _genome_core_bands()
	assert_true(Array(_hp_errors(n)).any(func(p: String) -> bool: return p.contains("has hp_bands but is not a boss")))


func test_legacy_enemy_has_no_table_and_validates() -> void:
	var e := _enemy([])
	assert_false(e.uses_hp_table())
	assert_eq(e.hp_at_tier(2), 0)
	assert_eq(_hp_errors(e), PackedStringArray(), "empty hp_by_tier is the documented legacy fallback")
	assert_eq(_boss([]).hp_for(1.0), 0)


func test_validate_without_config_uses_game_config() -> void:
	var errors := PackedStringArray()
	for p in _enemy([32, 40, 43, 63]).validate():
		if p.contains("hp_by_tier"):
			errors.append(p)
	assert_eq(errors.size(), 1, "validate() with no argument still checks the bands")
