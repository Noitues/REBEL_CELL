extends GutTest
## M7 pools and Solace depth (GAP_ANALYSIS P1 6-7): pool sizes, every card plays with
## preview == result, new Firmware and Daemon hooks, new assets, shop slices and events.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func _ids(class_name_: StringName) -> Array[StringName]:
	return _lookup.ids_of_class(class_name_)


func _shared_cards() -> Array[StringName]:
	var out: Array[StringName] = []
	for id in _ids(&"CardData"):
		var c := _lookup.get_content(id) as CardData
		if c.class_id == &"" and c.offered:
			out.append(id)
	return out


func test_pool_sizes_reach_the_hundred_hour_targets() -> void:
	assert_true(_shared_cards().size() >= 60, "shared cards: %d" % _shared_cards().size())
	assert_true(_ids(&"FirmwareData").size() >= 18, "Firmware: %d" % _ids(&"FirmwareData").size())
	assert_true(_ids(&"DaemonData").size() >= 24, "Daemons: %d" % _ids(&"DaemonData").size())
	assert_true(_ids(&"DefenseAssetData").size() >= 8, "assets: %d" % _ids(&"DefenseAssetData").size())
	assert_true(_cfg.shop_slices.size() >= 12, "shop slices: %d" % _cfg.shop_slices.size())
	var solace_events := 0
	for id in _ids(&"TerminalEventData"):
		var ev := _lookup.get_content(id) as TerminalEventData
		if ev.corporation_id == &"" or ev.corporation_id == &"solace":
			solace_events += 1
	assert_true(solace_events >= 40, "events a Solace netrun can roll: %d" % solace_events)


## Plays `card_id` from a fresh Breaker hand and returns the result.
func _play(card_id: StringName, seed: int = 5) -> Array:
	var s := CombatSession.start(_resolver, &"breaker", [&"triage_unit"], seed, &"rank:1")
	s.state.hand[0] = card_id
	s.state.ram = s.state.max_ram
	var card := _lookup.get_content(card_id) as CardData
	var wheel: StringName = &"enemy_0" if card.wheel_target == RC.WheelTarget.ENEMY else &"player"
	var a := CombatAction.play_card(0, wheel, 1)
	a.direction = 1
	var predicted := s.preview(a)
	var actual := s.apply(a)
	return [s, predicted, actual]


func test_every_shared_card_plays_and_previews_exactly() -> void:
	for id in _shared_cards():
		if (_lookup.get_content(id) as CardData).wheel_target == RC.WheelTarget.SATELLITE:
			continue  # Undock needs a satellite (covered in test_cards)
		var out := _play(id)
		var predicted: CombatResult = out[1]
		var actual: CombatResult = out[2]
		assert_eq(actual.error, "", "%s plays" % id)
		assert_eq(predicted.state.state_hash(), actual.state.state_hash(), "%s preview == result" % id)
		assert_eq(CombatFixture.events_of(actual, "unsupported_effect").size(), 0, "%s uses only implemented effects" % id)


func test_damage_and_defence_cards_do_what_they_say() -> void:
	var out := _play(&"static_shock")
	var hits := CombatFixture.events_of(out[2], "damage")
	assert_true(hits.size() >= 1 and int(hits[0]["amount"]) <= 4)
	out = _play(&"bulwark")
	assert_eq(int(CombatFixture.events_of(out[2], "block")[0]["amount"]), 12)
	out = _play(&"arc_flash")
	assert_eq(CombatFixture.events_of(out[2], "damage").size(), (out[0] as CombatSession).state.living_enemies(true).size() + 0, "every enemy is hit")


func _fw_session(slot: int, firmware_id: String) -> CombatSession:
	var fw := ["", "", "", "", "", ""]
	fw[slot] = firmware_id
	return CombatSession.start(_resolver, &"breaker", [&"triage_unit"], 4, &"", 0, {"slot_firmware_ids": fw})


func test_new_firmware_hooks() -> void:
	# Breaker wheel: 0 Crit 12, 1-3 Atk 6, 4 Def 5, 5 Miss.
	var s := _fw_session(1, "siphon")
	s.state.player.hp = 30
	CombatFixture.land(s.state.player, 1, 1)
	var r := s.apply(CombatAction.end_turn())
	assert_true(CombatFixture.events_of(r, "heal").size() >= 1, "Siphon heals on Good")
	s = _fw_session(5, "recycler")
	CombatFixture.land(s.state.player, 5, 1)
	r = s.apply(CombatAction.end_turn())
	var ram_up := false
	for ev in CombatFixture.events_of(r, "ram"):
		if int(ev["amount"]) == 2:
			ram_up = true
	assert_true(ram_up, "Recycler: the Miss slice restores 2 RAM")
	s = _fw_session(4, "bulkhead")
	CombatFixture.land(s.state.player, 4, 1)
	r = s.apply(CombatAction.end_turn())
	assert_eq(int(CombatFixture.events_of(r, "block")[0]["amount"]), roundi(5 * 1.5), "Bulkhead: Def +50%")


func test_new_combat_daemons() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"triage_unit"], 4, &"", 0, {"daemon_ids": ["warm_boot", "shield_cache"]})
	assert_eq(s.state.player.shield, 5, "Shield Cache")
	var plain := CombatSession.start(_resolver, &"breaker", [&"triage_unit"], 4)
	assert_eq(s.state.ram, plain.state.ram + 2, "Warm Boot")


## A netrun whose first fight is won at once; returns the session after the fight.
func _win_first_fight(daemons: Array) -> NetrunSession:
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var c := CampaignRules.new_campaign(corp, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	for d in daemons:
		c.roster[0].daemon_ids.append(StringName(d))
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"t1_a", 5)
	s.enter_node(s.available_nodes()[0])
	for e in s.combat.state.living_enemies():
		e.hp = 1
	s.combat.state.player.hp = 20
	var turns := 0
	while s.in_combat() and turns < 10:
		turns += 1
		CombatFixture.land(s.combat.state.player, 0, 0)
		s.combat_action(CombatAction.end_turn())
	assert_false(s.in_combat())
	return s


func test_combat_end_daemons_pay_out_after_a_won_fight() -> void:
	var plain := _win_first_fight([])
	var with := _win_first_fight(["salvager", "bounty_code"])
	assert_eq(with.run.cycles, plain.run.cycles + 5, "Salvager +5 Cycles")
	assert_eq(with.run.banked_schematics, plain.run.banked_schematics + 1, "Bounty Code +1 Schematic")
	var medic := _win_first_fight(["field_medic"])
	assert_eq(medic.run.operative.hp, plain.run.operative.hp + 4, "Field Medic heals 4")


func test_rack_and_netrun_daemons() -> void:
	var plain := _win_first_fight([])
	var skim := _win_first_fight(["rack_skimmer", "log_wiper"])
	var before_plain := plain.run.banked_schematics
	var before_skim := skim.run.banked_schematics
	plain._capture_rack()
	skim._capture_rack()
	assert_eq(skim.run.banked_schematics - before_skim, plain.run.banked_schematics - before_plain + 3, "Rack Skimmer +3")
	var hooks := skim._run_daemon_hooks(RC.Trigger.ON_NETRUN_COMPLETE)
	var heat := 0
	for e in hooks:
		if int(e.get("effect", -1)) == RC.EffectType.MODIFY_HEAT:
			heat += int(e["amount"])
	assert_eq(heat, -1, "Log Wiper")


func test_new_assets_fire_in_raids() -> void:
	var grid := GridFixture.chain_grid([&"c1"])
	var c := GridFixture.campaign(grid, {&"c1": &"safehouse"})
	GridFixture.deploy(c, &"c1", &"railgun")
	GridFixture.deploy(c, &"c1", &"flak_array")
	var raid := GridFixture.raid(&"probe", [&"collector", &"auditor"])
	var result := RaidResolver.resolve(c, grid, raid, _lookup, _cfg)
	var shooters := {}
	for e in result.events:
		if e.get("type", "") == "shot":
			shooters[e["asset"]] = true
	assert_true(shooters.has(&"railgun") and shooters.has(&"flak_array"), "both new turrets shoot: %s" % [shooters.keys()])


func test_every_event_choice_resolves() -> void:
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	for id in _ids(&"TerminalEventData"):
		var ev := _lookup.get_content(id) as TerminalEventData
		for i in ev.choices.size():
			var c := CampaignRules.new_campaign(corp, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
			var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"t1_a", 5)
			s.run.cycles = 500
			s.run.phase = RunState.Phase.EVENT
			s.run.event_id = id
			var events := s.choose_event_option(i)
			for e in events:
				assert_ne(e.get("type", ""), "unsupported_effect", "%s choice %d" % [id, i])
				if not String(e.get("text", "")).contains("fits no slice"):  # H14: a Firmware that fits no slot is refused on purpose
					assert_ne(e.get("type", ""), "refused", "%s choice %d is affordable with 500 Cycles" % [id, i])
