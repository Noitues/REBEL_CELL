extends GutTest
## N2 (CONTENT_DESIGN_V2 R2): NetrunSession.enemy_scale() / enemy_output_scale() read the
## config tables, and CombatResolver.create_combat starts table enemies at their authored
## HP (hp_by_tier by tier, boss hp_bands by ICE strength) while legacy enemies keep the old
## multiplier.

const DAMAGE := [1.0, 1.3, 1.69, 2.2]

var _cfg: CampaignConfigData
var _normal: EnemyData
var _mini: EnemyData
var _boss: EnemyData
var _sat: EnemyData
var _resolver: CombatResolver


func before_all() -> void:
	_cfg = CombatFixture.config()
	_sat = CombatFixture.enemy(&"n2s_sat", 4, CombatFixture.null_wheel())
	_normal = CombatFixture.enemy(&"n2s_normal", 30, CombatFixture.null_wheel(), [CombatFixture.spawn(_sat, 1)])
	_normal.hp_by_tier = PackedInt32Array([30, 40, 50, 60])
	_normal.spawns[0].trigger = RC.Trigger.ON_COMBAT_START
	_mini = CombatFixture.enemy(&"n2s_mini", 150, CombatFixture.null_wheel())
	_mini.is_elite = true
	_mini.is_mini_boss = true
	_mini.hp_by_tier = PackedInt32Array([63, 77, 98, 0])
	_boss = CombatFixture.enemy(&"n2s_boss", 360, CombatFixture.null_wheel())
	_boss.is_boss = true
	_boss.hp_bands = [Vector2(1.0, 300), Vector2(1.15, 330), Vector2(1.30, 360), Vector2(99.0, 400)]
	_resolver = CombatFixture.resolver([_sat, _normal, _mini, _boss])


func _campaign() -> CampaignState:
	var c := CampaignState.new()
	c.campaign_seed = 7
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	return c


func _start(enemy: StringName, overrides: Dictionary) -> CombatantState:
	return CombatSession.start(_resolver, &"breaker", [enemy], 11, &"rank:1", 0, overrides).state.get_combatant(&"enemy_0")


func test_session_scales_read_the_tables_per_tier() -> void:
	for t in range(1, 5):
		var s := NetrunSession.start_special(_resolver, _campaign(), &"op_1", "reclaim", &"t1_a", t, 5, &"n2s_normal", {})
		assert_eq(s.enemy_output_scale(), DAMAGE[t - 1], "T%d damage factor" % t)
		assert_almost_eq(s.enemy_output_scale(), pow(1.3, t - 1), 0.05, "within 0.05 of the old 1.3^(t-1)")
		assert_almost_eq(s.enemy_scale(), pow(1.6, t - 1), 0.000001, "legacy HP multiplier unchanged")


func test_create_combat_enemy_hp_from_hp_by_tier() -> void:
	for t in range(1, 5):
		var e := _start(&"n2s_normal", {"tier": t, "enemy_scale": _cfg.enemy_hp_scale(t), "enemy_output_scale": _cfg.enemy_damage_factor(t)})
		assert_eq(e.max_hp, [30, 40, 50, 60][t - 1], "T%d table HP" % t)
		assert_eq(e.hp, e.max_hp)
		assert_almost_eq(e.output_scale, _cfg.enemy_damage_factor(t), 0.000001)


func test_enemy_scale_no_longer_multiplies_table_hp() -> void:
	var a := _start(&"n2s_normal", {"tier": 3, "enemy_scale": 1.0})
	var b := _start(&"n2s_normal", {"tier": 3, "enemy_scale": 7.5})
	assert_eq(a.max_hp, 50)
	assert_eq(b.max_hp, 50, "the HP multiplier has no effect on a table enemy")


func test_satellites_of_table_enemy_keep_the_legacy_scale() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"n2s_normal"], 11, &"rank:1", 0, {"tier": 3, "enemy_scale": 2.56, "enemy_output_scale": 1.69})
	var sats := s.state.satellites_of(&"enemy_0")
	assert_eq(sats.size(), 1)
	assert_eq(sats[0].max_hp, roundi(4 * 2.56), "satellites keep the legacy HP multiplier")
	assert_almost_eq(sats[0].output_scale, 1.69, 0.000001)


func test_legacy_enemy_keeps_current_hp() -> void:
	var data := ContentRegistry.get_content(&"triage_unit") as EnemyData
	assert_false(data.uses_hp_table(), "no content is migrated by N2")
	var e := CombatSession.start(_resolver, &"breaker", [&"triage_unit"], 11, &"rank:1", 0, {"tier": 4, "enemy_scale": _cfg.enemy_hp_scale(4)}).state.get_combatant(&"enemy_0")
	assert_eq(e.max_hp, roundi(data.hp * pow(1.6, 3)), "legacy fallback = the old 1.6^(t-1)")


func test_create_combat_boss_hp_from_band_and_ice() -> void:
	assert_eq(_start(&"n2s_boss", {"tier": 4}).max_hp, 300, "ICE 0")
	assert_eq(_start(&"n2s_boss", {"tier": 4, "boss_strength_pct": 15.0}).max_hp, 330)
	assert_eq(_start(&"n2s_boss", {"tier": 4, "boss_strength_pct": 20.0}).max_hp, 360)
	assert_eq(_start(&"n2s_boss", {"tier": 4, "boss_strength_pct": 30.0}).max_hp, 360)
	var b := _start(&"n2s_boss", {"tier": 4, "boss_strength_pct": 31.0, "enemy_scale": 4.096, "enemy_output_scale": 2.2})
	assert_eq(b.max_hp, 400)
	assert_almost_eq(b.output_scale, 2.2 * 1.31, 0.0001, "output still takes tier x strength")


func test_mini_boss_table_hp_takes_strength() -> void:
	assert_eq(_start(&"n2s_mini", {"tier": 2}).max_hp, 77)
	assert_eq(_start(&"n2s_mini", {"tier": 2, "boss_strength_pct": 25.0}).max_hp, roundi(77 * 1.25))
	assert_eq(_start(&"n2s_mini", {"tier": 4}).max_hp, 98, "no T4 band: T3 HP")


func test_tier_out_of_range_clamps_no_crash() -> void:
	assert_eq(_start(&"n2s_normal", {"tier": 0}).max_hp, 30)
	assert_eq(_start(&"n2s_normal", {"tier": 9}).max_hp, 60)
	assert_eq(_start(&"n2s_normal", {}).max_hp, 30, "no tier override = T1")


func test_loaded_resources_untouched() -> void:
	var before := _normal.hp_by_tier.duplicate()
	_start(&"n2s_normal", {"tier": 4})
	assert_eq(_normal.hp_by_tier, before)
	assert_eq(_normal.hp, 30)
