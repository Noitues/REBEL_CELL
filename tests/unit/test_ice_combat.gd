extends GutTest
## Combat-side ICE and Heat rule modifiers (GDD 11.9, 4.3): enemy resistance, boss
## strength, the extra boss pointer, the starting Bug card, no free nudge on turn 1,
## and Heat-gated enemy behaviour. Each has a resolver-level test and a NetrunSession
## test that reads the modifiers from the campaign's ICE level.

var _resolver: CombatResolver
var _cfg: CampaignConfigData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = _resolver.config


func _session(enemy: StringName, overrides: Dictionary = {}, seed: int = 3) -> CombatSession:
	return CombatSession.start(_resolver, &"breaker", [enemy], seed, &"rank:1", 0, overrides)


func test_enemy_resistance_adds_passive_resistance_that_refreshes_each_turn() -> void:
	var s := _session(&"collections_agent", {"enemy_resistance": 1})
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(e.wheel.passive_resistance, 1)
	assert_eq(e.resistance, 1)
	var sat := s.state.satellites_of(&"enemy_0")[0]
	assert_eq(sat.resistance, 0, "satellites are not affected")
	s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 0, "the nudge was absorbed")
	CombatFixture.land(s.state.player, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 1, "restored at the start of the next turn")


func test_boss_strength_scales_bosses_and_mini_bosses_only() -> void:
	var boss := _session(&"renewal_engine", {"boss_strength_pct": 25.0}).state.get_combatant(&"enemy_0")
	assert_eq(boss.max_hp, roundi(360 * 1.25))
	assert_almost_eq(boss.output_scale, 1.25, 0.001)
	var mini := _session(&"account_manager", {"boss_strength_pct": 25.0}).state.get_combatant(&"enemy_0")
	assert_eq(mini.max_hp, roundi(150 * 1.25))
	var normal := _session(&"triage_unit", {"boss_strength_pct": 25.0}).state.get_combatant(&"enemy_0")
	assert_eq(normal.max_hp, 45, "normal enemies are untouched")
	var both := _session(&"renewal_engine", {"boss_strength_pct": 25.0, "enemy_scale": 2.0}).state.get_combatant(&"enemy_0")
	assert_eq(both.max_hp, roundi(360 * 2.0 * 1.25), "tier scale and boss strength multiply")
	assert_almost_eq(both.output_scale, 2.5, 0.001)


func test_boss_extra_pointer_is_evenly_spaced_and_survives_phases() -> void:
	var s := _session(&"renewal_engine", {"boss_extra_pointer": 1})
	var b := s.state.get_combatant(&"enemy_0")
	assert_eq(b.wheel.pointer_ticks, PackedInt32Array([0, 15]))
	var normal := _session(&"triage_unit", {"boss_extra_pointer": 1}).state.get_combatant(&"enemy_0")
	assert_eq(normal.wheel.pointer_ticks, PackedInt32Array([0]), "only the final boss")
	# Two extra pointers land 15 and 10 ticks from pointer 0.
	var two := _session(&"renewal_engine", {"boss_extra_pointer": 2}).state.get_combatant(&"enemy_0")
	assert_eq(two.wheel.pointer_ticks, PackedInt32Array([0, 15, 10]))


func test_no_first_turn_free_nudge_only_affects_turn_1() -> void:
	var s := _session(&"triage_unit", {"no_first_turn_free_nudge": true})
	assert_eq(s.state.free_nudges, 0)
	assert_eq(s.state.ram, 6)
	var r := s.apply(CombatAction.nudge(&"player", 1))
	assert_true(r.ok(), "a nudge still works for RAM")
	assert_eq(s.state.ram, 5)
	CombatFixture.land(s.state.player, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.free_nudges, 1, "turn 2 has its free nudge")


func test_bug_card_drains_ram_and_exhausts_and_is_never_offered() -> void:
	var s := _session(&"triage_unit", {"deck": ["bug", "bug", "bug", "bug", "bug"]})
	assert_eq(s.state.hand.count(&"bug"), 5)
	var ram := s.state.ram
	var r := s.apply(CombatAction.play_card(0, &"player"))
	assert_true(r.ok(), r.error)
	assert_eq(s.state.ram, ram - 1)
	assert_eq(s.state.exhaust_pile, [&"bug"])
	var bug := ContentRegistry.get_content(&"bug") as CardData
	assert_false(bug.offered)
	assert_eq(bug.ram_cost, 0)


func test_heat_gated_enemy_behaviour_only_above_its_heat() -> void:
	# Compliance Officer at Heat 50+: every attack drains 1 RAM.
	for heat in [0, 50]:
		var s := _session(&"compliance_officer", {"heat": heat})
		var e := s.state.get_combatant(&"enemy_0")
		CombatFixture.land(e, 0)  # Atk 7
		CombatFixture.land(s.state.player, 5)
		var ram := s.state.ram
		s.apply(CombatAction.end_turn())
		var expected := ram + 4 - (1 if heat >= 50 else 0)
		assert_eq(s.state.ram, expected, "heat %d" % heat)


func _campaign(ice: int) -> CampaignState:
	var c := CampaignState.new()
	c.campaign_seed = 7
	c.ice_level = ice
	c.schematics = _cfg.starting_schematics
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	return c


func test_netrun_reads_the_ice_ladder_into_combat() -> void:
	# ICE 12 (cumulative): enemies +1 resistance (7), boss +25% (9), Bug card (11), no free
	# nudge on turn 1 (12).
	var c := _campaign(12)
	var s := NetrunSession.start(_resolver, c, &"op_1", 1, &"t1_a", 11)
	assert_eq(s.run.operative.deck.count(&"bug"), 1, "one Bug card in the working deck")
	assert_eq(c.get_operative(&"op_1").deck.count(&"bug"), 0, "the roster copy is untouched until completion")
	s.enter_node(s.available_nodes()[0])
	assert_true(s.in_combat())
	var cs := s.combat.state
	assert_eq(cs.free_nudges, 0, "ICE 12: no free nudge on turn 1")
	assert_eq(cs.get_combatant(&"enemy_0").wheel.passive_resistance,
		(ContentRegistry.get_content(cs.get_combatant(&"enemy_0").source_id) as EnemyData).wheel.passive_resistance + 1)
	assert_eq(cs.campaign_heat, 0)
	# ICE 18: the final boss gains a pointer.
	var c2 := _campaign(18)
	var boss := NetrunSession.start_special(_resolver, c2, &"op_1", "boss", &"renewal_engine_site", 4, 5, &"renewal_engine", {})
	boss.enter_node(boss.available_nodes()[0])
	assert_true(boss.in_combat())
	var b := boss.combat.state.get_combatant(&"enemy_0")
	assert_eq(b.wheel.pointer_ticks.size(), 2, "ICE 18: +1 boss pointer")
	assert_eq(b.max_hp, roundi(roundi(360 * pow(_cfg.enemy_scale_per_tier, 3)) * 1.25), "tier 4 scale x ICE 9 strength")


func test_heat_50_threshold_adds_enemy_resistance_through_the_netrun() -> void:
	var c := _campaign(0)
	c.heat = 50
	var s := NetrunSession.start(_resolver, c, &"op_1", 1, &"t1_a", 12)
	s.enter_node(s.available_nodes()[0])
	var e := s.combat.state.get_combatant(&"enemy_0")
	var base := (ContentRegistry.get_content(e.source_id) as EnemyData).wheel.passive_resistance
	assert_eq(e.wheel.passive_resistance, base + 1)
	assert_eq(s.combat.state.campaign_heat, 50)
	assert_true(s.combat.state.free_nudges == 1)
