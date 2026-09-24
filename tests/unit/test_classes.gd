extends GutTest
## M6 class roster (GDD 5.2): Ghost, Rigger and Botnet stats, hub hooks, drone
## persistence, the PARASITE status, raid station bonuses, and unlock / recruit gating.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func _class(id: StringName) -> ClassData:
	return ContentRegistry.get_content(id) as ClassData


func test_class_stats_follow_the_gdd() -> void:
	var expect := {&"ghost": [50, &"ghost_core"], &"rigger": [55, &"rig_core"], &"botnet": [45, &"swarm_core"]}
	for id in expect:
		var cls := _class(id)
		assert_not_null(cls, String(id))
		assert_eq(cls.base_hp, expect[id][0], "%s HP" % id)
		assert_eq(cls.starting_wheel.hub.id, expect[id][1], "%s hub" % id)
		assert_eq(cls.starting_wheel.slots.size(), 6, "%s wheel" % id)
		assert_eq(cls.starting_deck.size(), 10, "%s deck" % id)
		assert_true(cls.station_bonus.size() > 0, "%s station bonus" % id)


func test_ghost_first_enemy_nudge_ignores_resistance() -> void:
	var s := CombatSession.start(_resolver, &"ghost", [&"triage_unit"], 3, &"", 0, {"enemy_resistance": 2})
	var e := s.state.get_combatant(&"enemy_0")
	assert_true(e.resistance > 0)
	var before := e.wheel.rotation
	var r := s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_true(r.ok(), r.error)
	assert_eq(CombatFixture.events_of(r, "ghost_nudge").size(), 1)
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.rotation, before + 1, "the free nudge moves a full tick")
	r = s.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_eq(CombatFixture.events_of(r, "ghost_nudge").size(), 0, "only the first nudge each turn")


func test_rigger_core_raises_max_ram() -> void:
	var s := CombatSession.start(_resolver, &"rigger", [&"triage_unit"], 3)
	assert_eq(s.state.max_ram, _class(&"rigger").max_ram + 1)
	var mk2 := CombatSession.start(_resolver, &"rigger", [&"triage_unit"], 3, &"", 0, {"hub_id": "rig_core_mk2"})
	assert_eq(mk2.state.max_ram, _class(&"rigger").max_ram + 2)


func test_rigger_perfect_refunds_ram() -> void:
	var s := CombatSession.start(_resolver, &"rigger", [&"triage_unit"], 3)
	CombatFixture.land(s.state.player, 0, 0)
	var r := s.apply(CombatAction.end_turn())
	var gained := false
	for ev in CombatFixture.events_of(r, "ram"):
		if int(ev.get("amount", 0)) > 0:
			gained = true
	assert_true(gained, "a Perfect gives RAM back")


func test_botnet_deploy_slice_docks_a_drone() -> void:
	var s := CombatSession.start(_resolver, &"botnet", [&"triage_unit"], 3)
	CombatFixture.land(s.state.player, 1, 1)  # deploy_1, Good
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.living_drones().size(), 1)


func test_botnet_perfect_deploy_plants_a_parasite() -> void:
	var s := CombatSession.start(_resolver, &"botnet", [&"triage_unit"], 3)
	CombatFixture.land(s.state.player, 1, 0)  # deploy_1, Perfect
	var r := s.apply(CombatAction.end_turn())
	var ev := CombatFixture.events_of(r, "parasite")
	# The Swarm Core Perfect also resolves the slice again, and hook effects fire once per
	# resolution (the Breaker Mk2 rule), so the parasite lands once per resolution.
	assert_eq(ev.size(), 2)
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(e.wheel.slice_statuses[int(ev[0]["slot"])], RC.Status.PARASITE)


func test_parasite_halves_the_slice_output() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"triage_unit"], 4, &"", 0, {"ring_segment_ids": ["seg_blank", "seg_blank", "seg_blank"]})
	s.state.player.wheel.slice_statuses[1] = RC.Status.PARASITE
	CombatFixture.land(s.state.player, 1, 1)  # Atk 6, Good
	var r := s.apply(CombatAction.end_turn())
	var hits := CombatFixture.events_of(r, "damage")
	assert_true(hits.size() >= 1)
	assert_eq(int(hits[0]["amount"]), roundi(6 * _cfg.parasite_multiplier))


func test_drones_persist_between_fights_of_a_run() -> void:
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var c := CampaignRules.new_campaign(corp, _cfg, _lookup, 1, _class(&"botnet"), GridFixture.home_node())
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"t1_a", 5)
	s.enter_node(s.available_nodes()[0])
	assert_true(s.in_combat())
	var cs := s.combat.state
	var events: Array[Dictionary] = []
	var drone := _resolver.fx.deploy_drone(cs, cs.player, ContentRegistry.get_content(&"botnet_drone") as EnemyData, 1, events)
	assert_not_null(drone)
	drone.hp = drone.max_hp - 1
	for e in cs.living_enemies():
		e.hp = 1
	var turns := 0
	while s.in_combat() and turns < 10:
		turns += 1
		CombatFixture.land(s.combat.state.player, 0, 0)
		s.combat_action(CombatAction.end_turn())
	assert_false(s.in_combat())
	assert_eq(s.run.drones.size(), 1, "the drone rides along")
	var again := RunState.from_dict(s.run.to_dict())
	assert_eq(again.drones.size(), 1, "saved with the run")
	var next := CombatSession.start(_resolver, &"botnet", [&"triage_unit"], 9, &"", 0, {"drones": s.run.drones})
	assert_eq(next.state.living_drones().size(), 1, "and docks at the next fight")
	assert_eq(next.state.living_drones()[0].hp, int(s.run.drones[0]["hp"]))


func _stationed(class_id: StringName) -> Array:
	var grid := GridFixture.chain_grid([&"c1"])
	var c := GridFixture.campaign(grid, {&"c1": &"safehouse"})
	c.recruit(_class(class_id), "Op")
	CampaignRules.station(c, _lookup, c.roster[0].id, &"c1")
	assert_eq(c.grid.stationed_on(&"c1"), c.roster[0].id)
	return [c, grid]


func test_station_bonuses_per_class() -> void:
	var expect := {&"ghost": ["hold", 1], &"rigger": ["regen", 5], &"botnet": ["turrets", 1]}
	for id in expect:
		var pair := _stationed(id)
		var c: CampaignState = pair[0]
		var b := RaidResolver.station_bonuses(c, c.grid, pair[1], _lookup, &"c1")
		assert_eq(int(b[expect[id][0]]), expect[id][1], "%s %s" % [id, expect[id][0]])


func _event_types(result: RaidResolver.RaidResult) -> Array:
	var out := []
	for e in result.events:
		out.append(e.get("type", ""))
	return out


func test_ghost_station_holds_a_threat() -> void:
	var pair := _stationed(&"ghost")
	var raid := GridFixture.raid(&"probe", [&"enforcer"])
	var result := RaidResolver.resolve(pair[0], pair[1], raid, _lookup, _cfg)
	assert_true(_event_types(result).has("station_hold"))


func test_rigger_station_patches_the_node_after_a_wave() -> void:
	var pair := _stationed(&"rigger")
	var c: CampaignState = pair[0]
	# A sturdy node that survives the first wave, below its cap.
	c.grid.site(&"c1")["max_integrity"] = 100
	c.grid.site(&"c1")["integrity"] = 95
	var raid := GridFixture.raid(&"probe", [&"enforcer"], 8, 2)
	var result := RaidResolver.resolve(c, pair[1], raid, _lookup, _cfg)
	assert_true(_event_types(result).has("station_regen"))


func test_botnet_station_adds_turret_fire() -> void:
	var pair := _stationed(&"botnet")
	var raid := GridFixture.raid(&"probe", [&"enforcer"])
	var result := RaidResolver.resolve(pair[0], pair[1], raid, _lookup, _cfg)
	var turret_shots := 0
	for e in result.events:
		if e.get("type", "") == "shot" and e.get("asset", &"") == _cfg.station_deploy_asset.id:
			turret_shots += 1
	assert_true(turret_shots > 0, "the drone turret shoots")


func test_class_unlocks_gate_recruitment() -> void:
	var profile := ProfileState.new()
	var ids := []
	for cls in CampaignRules.available_classes(profile, _lookup):
		ids.append(cls.id)
	assert_eq(ids, [&"breaker"], "only the Breaker starts unlocked")
	assert_false(CampaignRules.class_available(profile, _lookup, _class(&"ghost")))
	profile.add_unlock(&"unlock_ghost")
	assert_true(CampaignRules.class_available(profile, _lookup, _class(&"ghost")))
	assert_false(CampaignRules.class_available(profile, _lookup, _class(&"rigger")))
	for id in [&"ghost", &"rigger", &"botnet"]:
		var u := CampaignRules.unlock_for(_lookup, _class(id))
		assert_not_null(u, String(id))
		assert_eq(u.schematic_cost, 80)


func test_new_campaign_with_a_class() -> void:
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var c := CampaignRules.new_campaign(corp, _cfg, _lookup, 1, _class(&"rigger"), GridFixture.home_node())
	assert_eq(c.roster[0].class_id, &"rigger")
	assert_eq(c.roster[0].max_hp, 55)


func test_alternatives_share_the_deck_and_swap_the_core() -> void:
	var pairs := {&"wrecker": &"breaker", &"phantom": &"ghost", &"overclocker": &"rigger", &"hivemind": &"botnet"}
	for alt_id in pairs:
		var alt := _class(alt_id)
		var base := _class(pairs[alt_id])
		assert_not_null(alt, String(alt_id))
		assert_eq(alt.alternative_of, base.id)
		assert_eq(alt.pool_class_id(), base.id, "draws the base class's exclusive cards")
		assert_eq(alt.base_hp, base.base_hp)
		var alt_deck := []
		var base_deck := []
		for c in alt.starting_deck:
			alt_deck.append(c.id)
		for c in base.starting_deck:
			base_deck.append(c.id)
		assert_eq(alt_deck, base_deck, "%s keeps the deck" % alt_id)
		assert_ne(alt.starting_wheel.hub.id, base.starting_wheel.hub.id, "%s changes the core" % alt_id)
		var u := CampaignRules.unlock_for(_lookup, alt)
		assert_not_null(u)
		assert_eq(u.schematic_cost, 60)
		assert_ne(Dialogue.bark(alt_id, "perfect", 1), "", "%s barks like its base class" % alt_id)


func test_phantom_core_grants_a_free_nudge_each_turn() -> void:
	var s := CombatSession.start(_resolver, &"phantom", [&"triage_unit"], 3)
	var start := s.state.free_nudges
	CombatFixture.land(s.state.player, 5)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.free_nudges, _class(&"phantom").free_nudges_per_turn + 1, "class nudge plus the Phantom Core nudge")
	assert_true(start >= 1)


func test_hive_core_drones_do_not_persist() -> void:
	var hub := ContentRegistry.get_content(&"hive_core") as HubCoreData
	assert_false(hub.drones_persist)
	assert_eq(hub.max_drones, 4)
	var s := CombatSession.start(_resolver, &"hivemind", [&"triage_unit"], 3)
	CombatFixture.land(s.state.player, 0, 0)  # Atk, Perfect: the hook docks a drone
	s.apply(CombatAction.end_turn())
	assert_true(s.state.living_drones().size() >= 1)


func test_wrecker_perfect_resolves_at_one_and_a_half() -> void:
	var s := CombatSession.start(_resolver, &"wrecker", [&"triage_unit"], 4)
	CombatFixture.land(s.state.player, 1, 0)  # Atk 6, Perfect
	var r := s.apply(CombatAction.end_turn())
	var amounts := []
	for h in CombatFixture.events_of(r, "damage"):
		amounts.append(int(h["amount"]))
	assert_true(amounts.has(9), "6 x 1.5 = 9 in %s" % [amounts])
