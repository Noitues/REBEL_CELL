extends GutTest
## N2 flow: a seeded netrun fight at T1 and at T4 starts a table enemy at its hp_by_tier
## HP, the breach-style preview session equals the real fight start, and the shipped
## content still validates with the new fields.

var _cfg: CampaignConfigData
var _enemy: EnemyData
var _resolver: CombatResolver


func before_all() -> void:
	_cfg = CombatFixture.config()
	_enemy = CombatFixture.enemy(&"n2f_normal", 30, CombatFixture.null_wheel())
	_enemy.hp_by_tier = PackedInt32Array([32, 40, 50, 63])
	_resolver = CombatFixture.resolver([_enemy])


func _campaign() -> CampaignState:
	var c := CampaignState.new()
	c.campaign_seed = 9
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	return c


func _fight(tier: int, enemy: StringName) -> NetrunSession:
	var s := NetrunSession.start_special(_resolver, _campaign(), &"op_1", "reclaim", &"t1_a", tier, 21, enemy, {})
	s.enter_node(s.available_nodes()[0])
	return s


func test_netrun_t1_and_t4_fight_hp_matches_table() -> void:
	for t in [1, 4]:
		var s := _fight(t, &"n2f_normal")
		assert_true(s.in_combat())
		var e := s.combat.state.get_combatant(&"enemy_0")
		assert_eq(e.max_hp, _enemy.hp_by_tier[t - 1], "T%d starts at the table HP" % t)
		assert_almost_eq(e.output_scale, _cfg.enemy_damage_factor(t), 0.000001)


func test_netrun_legacy_enemy_unchanged_at_t4() -> void:
	var s := _fight(4, &"triage_unit")
	var data := ContentRegistry.get_content(&"triage_unit") as EnemyData
	assert_eq(s.combat.state.get_combatant(&"enemy_0").max_hp, roundi(data.hp * pow(1.6, 3)))


func test_same_seed_same_fight() -> void:
	var a := _fight(4, &"n2f_normal")
	var b := _fight(4, &"n2f_normal")
	assert_eq(a.combat.state_hash(), b.combat.state_hash())
	assert_eq(a.combat.setup, b.combat.setup)
	assert_eq(int(a.combat.setup["overrides"]["tier"]), 4, "the tier is recorded for replay")


func test_validate_content_passes() -> void:
	var errors := ContentRegistry.validate()
	assert_eq(errors, PackedStringArray(), "content validates with the N2 fields")
