extends GutTest
## N2 (CONTENT_DESIGN_V2 R2): the band lint over every content/enemies/*.tres, plus the drift
## guard that pins the config's band numbers to the R2 table. Enemies not migrated yet
## (empty hp_by_tier / hp_bands) are warnings, not failures; a boss over its budget is a
## warning too (designer ruling 2026-10-18 Q29).

const ENEMY_DIR := "res://content/enemies/"
## The R2 table (CONTENT_DESIGN_V2 section 1), copied here on purpose: the drift guard.
const R2_BANDS := {
	&"normal": [28, 36, 34, 44, 44, 56, 56, 70],
	&"elite": [56, 72, 68, 88, 88, 112, 112, 144],
	&"mini_boss_2": [56, 72, 68, 88, 88, 112, 0, 0],
	&"mini_boss_3": [85, 105, 104, 128, 132, 162, 0, 0],
}

var _cfg: CampaignConfigData


func before_all() -> void:
	_cfg = CombatFixture.config()


func _content_enemies() -> Array[EnemyData]:
	var out: Array[EnemyData] = []
	var files := Array(DirAccess.get_files_at(ENEMY_DIR))
	files.sort()
	for f: String in files:
		var name := f.trim_suffix(".remap")
		if name.ends_with(".tres"):
			var e := load(ENEMY_DIR + name) as EnemyData
			if e != null:
				out.append(e)
	return out


func test_every_enemy_that_sets_a_table_is_in_band_at_all_tiers() -> void:
	var enemies := _content_enemies()
	assert_true(enemies.size() > 40, "found the enemy content (%d)" % enemies.size())
	var report := HpBandLint.lint(enemies, _cfg)
	assert_eq(report["errors"], PackedStringArray(), "band lint errors")
	if not report["warnings"].is_empty():
		gut.p("N2 band lint: %d warnings (not migrated / boss over budget):" % report["warnings"].size())
		for w in report["warnings"]:
			gut.p("  " + w)


func test_non_migrated_enemies_are_warnings_not_errors() -> void:
	var report := HpBandLint.lint(_content_enemies(), _cfg)
	var migrated := 0
	for e in _content_enemies():
		if e.uses_hp_table():
			migrated += 1
	assert_eq(Array(report["warnings"]).filter(func(w: String) -> bool: return w.contains("not migrated")).size(),
		_content_enemies().size() - migrated)


func test_drift_guard_config_bands_match_r2() -> void:
	for cls: StringName in R2_BANDS:
		assert_eq(Array(_cfg.hp_band_table(cls)), R2_BANDS[cls], "config hp_band_%s drifted from R2" % cls)
		assert_eq(Array(CampaignConfigData.new().hp_band_table(cls)), R2_BANDS[cls], "schema default hp_band_%s" % cls)


func test_phase_budget_matches_config() -> void:
	assert_eq(HpBandLint.phase_budget(_cfg, 4, 1, 3.0), 52, "Genome Core P1: (18 - 3) x 3.5")
	assert_eq(HpBandLint.phase_budget(_cfg, 4, 1, 6.0), 42, "P2: (18 - 6) x 3.5")
	assert_eq(HpBandLint.phase_budget(_cfg, 4, 2, 6.0), 105, "P3 / P4: (2 x 18 - 6) x 3.5")
	assert_eq(HpBandLint.phase_budget(_cfg, 1), 31, "T1 one needle: 9 x 3.5")


func test_lint_report_names_enemy_and_tier() -> void:
	var e := CombatFixture.enemy(&"n2l_bad", 30, CombatFixture.null_wheel())
	e.is_elite = true
	e.hp_by_tier = PackedInt32Array([60, 70, 200, 120])
	var report := HpBandLint.lint([e] as Array[EnemyData], _cfg)
	assert_eq(report["errors"].size(), 1)
	assert_string_contains(report["errors"][0], "n2l_bad")
	assert_string_contains(report["errors"][0], "T3")


func test_boss_over_budget_is_a_warning() -> void:
	var b := CombatFixture.enemy(&"n2l_boss", 1475, CombatFixture.null_wheel())
	b.is_boss = true
	b.hp_bands = [Vector2(1.0, 1475), Vector2(99.0, 1600)]
	var report := HpBandLint.lint([b] as Array[EnemyData], _cfg)
	assert_eq(report["errors"], PackedStringArray(), "a boss band overshoot never fails")
	assert_eq(report["warnings"].size(), 1)
	assert_string_contains(report["warnings"][0], "above boss budget")
	b.hp_bands = [Vector2(1.0, 300), Vector2(1.15, 330), Vector2(1.30, 360), Vector2(99.0, 400)]
	b.phases.clear()
	for i in 3:
		var p := BossPhaseData.new()
		p.hp_threshold_pct = 0.82 - 0.2 * i
		b.phases.append(p)
	assert_eq(HpBandLint.lint([b] as Array[EnemyData], _cfg)["warnings"], PackedStringArray(), "Genome Core 300 fits 4 phases")
