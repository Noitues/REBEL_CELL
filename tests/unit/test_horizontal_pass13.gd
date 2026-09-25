extends GutTest
## Horizontal pass 13 fixes (GAP_ANALYSIS H13), with actions built the way the combat UI
## builds them: cards move the ring they name, resistance changed while the turn resolves
## lasts into the next turn, a kill from a card ends the fight, Terminal choices show and
## check their real costs, Rack Heat labels include Scrubber, the tutorial stays off the
## wheels, Momentum's spins come from the card.

var _atk6: SliceData
var _miss: SliceData
var _ring: InnerRingData


func before_each() -> void:
	_atk6 = CombatFixture.slice(&"h13_atk6", RC.SliceType.ATTACK, 6)
	_miss = CombatFixture.slice(&"h13_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)
	_ring = CombatFixture.ring([CombatFixture.segment(&"h13_s0"), CombatFixture.segment(&"h13_s1"), CombatFixture.segment(&"h13_s2")])


func _session(cards: Array, enemy: EnemyData = null, hub: HubCoreData = null) -> CombatSession:
	var deck: Array[CardData] = []
	for c in cards:
		deck.append(c if c is CardData else ContentRegistry.get_content(c) as CardData)
	var cls := CombatFixture.operative_class(&"h13_class", 60, CombatFixture.wheel([_atk6, _atk6, _atk6, _atk6, _atk6, _miss], hub, [0], 0, _ring), deck)
	if enemy == null:
		enemy = CombatFixture.enemy(&"h13_dummy", 200, CombatFixture.miss_wheel())
	var s := CombatSession.start(CombatFixture.resolver([cls, enemy]), cls.id, [enemy.id], 3)
	CombatFixture.land(s.state.player, 1)
	CombatFixture.land_inner(s.state.player, 0)
	return s


## A PLAY_CARD action as combat_scene._card_action builds it (ring from the toggle).
func _ui_action(wheel_id: StringName, ring: int) -> CombatAction:
	var a := CombatAction.play_card(0, wheel_id)
	a.ring = ring
	a.direction = 1
	return a


func test_a_card_that_names_the_inner_ring_moves_it_whatever_the_toggle() -> void:
	var s := _session([&"ring_tap"])
	var outer := s.state.player.wheel.rotation
	var inner := s.state.player.wheel.inner_rotation
	var r := s.apply(_ui_action(&"player", RC.RingScope.OUTER))
	assert_true(r.ok(), r.error)
	assert_eq(s.state.player.wheel.rotation, outer, "outer ring untouched")
	assert_ne(s.state.player.wheel.inner_rotation, inner, "the inner ring moved")


func test_an_outer_card_on_a_wheel_without_an_inner_ring_still_works() -> void:
	var s := _session([&"jam"])
	var before := s.state.get_combatant(&"enemy_0").wheel.rotation
	var r := s.apply(_ui_action(&"enemy_0", RC.RingScope.INNER))
	assert_true(r.ok(), r.error)
	assert_ne(s.state.get_combatant(&"enemy_0").wheel.rotation, before, "falls back to the outer ring instead of fizzling")


func test_fine_tune_still_follows_the_ring_toggle() -> void:
	var s := _session([&"fine_tune"])
	var inner := s.state.player.wheel.inner_rotation
	assert_true(s.apply(_ui_action(&"player", RC.RingScope.INNER)).ok())
	assert_eq(s.state.player.wheel.inner_rotation, inner + 2)


func test_a_strip_during_resolution_lasts_into_the_next_turn() -> void:
	var strip := CombatFixture.effect(RC.EffectType.MODIFY_RESISTANCE, RC.EffectTarget.POINTER_TARGET, -2)
	var hub := CombatFixture.hub(&"h13_ghostlike", 0, [], CombatFixture.triggered(RC.Trigger.ON_PERFECT, [strip], RC.PrecisionTier.PERFECT))
	var enemy := CombatFixture.enemy(&"h13_resist", 200, CombatFixture.miss_wheel(3))
	var s := _session([&"jam"], enemy, hub)
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 3)
	CombatFixture.land(s.state.player, 1)  # dead centre: Perfect
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 1, "3 - 2 after the next turn's restore")
	CombatFixture.land(s.state.player, 1, 2)  # Partial: no Perfect this time
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, 3, "back to full a turn later")


func test_a_card_that_kills_the_last_enemy_ends_the_fight() -> void:
	var kill := CombatFixture.card(&"h13_kill", [CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.TARGET_WHEEL, 999)], 0, RC.WheelTarget.ENEMY)
	var s := _session([kill])
	var r := s.apply(CombatAction.play_card(0, &"enemy_0"))
	assert_true(r.ok(), r.error)
	assert_true(s.state.is_over(), "the fight is over")
	assert_eq(s.state.outcome, CombatState.Outcome.VICTORY)


func _netrun() -> NetrunSession:
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var cfg := CombatFixture.config()
	var c := CampaignRules.new_campaign(corp, cfg, GridFixture.lookup(), 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node(), 6)
	return NetrunSession.start(CombatFixture.resolver(), c, c.roster[0].id, 1, &"t1_a", 5, corp)


func test_terminal_choices_show_and_check_their_real_costs() -> void:
	var s := _netrun()
	var hurt := EventChoiceData.new()
	hurt.label = "Strip the tracker"
	hurt.hp_cost = 3
	var heat := EffectData.new()
	heat.type = RC.EffectType.MODIFY_HEAT
	heat.amount = -4
	hurt.effects = [heat]
	var costs := s.choice_costs(hurt)
	assert_string_contains(costs, "-3 HP")
	assert_string_contains(costs, "%+d Heat" % HeatRules.scaled_delta(s.campaign, -4, s.config), "Heat as it will apply at ICE 6")
	s.run.operative.hp = 3
	assert_string_contains(s.choice_error(hurt), "flatline")
	s.run.operative.hp = 10
	assert_eq(s.choice_error(hurt), "")
	var broker := EventChoiceData.new()
	broker.cycle_cost = 0
	broker.reward = ContentRegistry.get_content(&"kernel_sync")
	s.run.operative.daemon_ids.append(&"kernel_sync")
	assert_string_contains(s.choice_error(broker), "already installed")
	assert_eq(load("res://scripts/ui/netrun_scene.gd")._choice_text("Tap it (+1 Heat)", "+2 Heat"), "Tap it (+2 Heat)", "the data replaces the hand-written summary")


func test_rack_heat_labels_include_scrubber() -> void:
	var s := _netrun()
	s.run.operative.daemon_ids.append(&"scrubber")
	for node in s.run.map.all_nodes():
		if int(node["type"]) == RC.InfilNodeType.SERVER_RACK:
			assert_eq(s.node_heat(node["id"]), HeatRules.scaled_delta(s.campaign, -1, s.config))


func test_the_tutorial_stays_off_the_wheels_and_names_the_bound_keys() -> void:
	RunManager.save_slot = "gut_test_tutorial_h13"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var scene: Control = add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())
	scene.start_fight(&"triage_unit", 7)
	scene.start_tutorial()
	for i in 3:
		await get_tree().process_frame
	assert_eq(scene.layout_violations(), [], "the tutorial covers no wheel")
	for i in TutorialOverlay.STEPS.size():
		assert_false(TutorialOverlay.step_text(i).contains("{"), "step %d has its keys filled in" % i)
	assert_string_contains(TutorialOverlay.step_text(1), Settings.key_text(&"nudge_left"))
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_momentum_spins_come_from_the_card() -> void:
	var e: EffectData = (ContentRegistry.get_content(&"momentum") as CardData).effects[0]
	assert_eq(e.amount, 2)
	assert_eq(roundi(e.amount * e.multiplier), 5)
