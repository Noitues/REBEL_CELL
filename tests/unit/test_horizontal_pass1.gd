extends GutTest
## Horizontal pass 1 fixes (GAP_ANALYSIS H1): corporation-aware text, speaker, music, DJ,
## corporation order, codex spoilers, rescue classes, cores and home servers in raids,
## Mirror threats, REBEL_CELL resume mid-netrun, every corporation's events.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
const CORPS := [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func _corp(id: StringName) -> CorporationData:
	var c := ContentRegistry.get_content(id) as CorporationData
	return RebelCellBuilder.build(c, RebelCellBuilder.snapshot(null, &"breaker"), _lookup) if c.generated_from_profile else c


func _campaign(corp: CorporationData, class_id: StringName = &"breaker") -> CampaignState:
	return CampaignRules.new_campaign(corp, _cfg, _lookup, 3, ContentRegistry.get_content(class_id) as ClassData, GridFixture.home_node())


func test_the_win_names_the_corporations_own_boss() -> void:
	var corp := _corp(&"meridian")
	var c := _campaign(corp)
	var r := RunState.new()
	r.site_id = corp.city_grid.boss_site_id
	r.kind = "boss"
	var events := CampaignRules.on_run_completed(c, corp, _cfg, r)
	var won := ""
	for e in events:
		if e.get("type", "") == "campaign_won":
			won = e["text"]
	assert_true(won.begins_with("The Manifest"), won)


func test_corporate_lines_carry_their_corporation() -> void:
	assert_eq(Dialogue.speaker_name(RC.Voice.CORPO, &"meridian"), "MERIDIAN")
	assert_eq(Dialogue.speaker_name(RC.Voice.CORPO, &"solace"), "SOLACE")
	assert_eq(Dialogue.speaker_name(RC.Voice.CORPO), "CORPORATE")
	assert_eq(Dialogue.speaker_name(RC.Voice.DISPATCH, &"meridian"), "DISPATCH")


func test_music_follows_the_corporation() -> void:
	assert_eq(AudioDirector.context_for("raid", &"solace"), "solace_raid")
	assert_eq(AudioDirector.context_for("raid", &"halcyon"), "halcyon_raid")
	assert_eq(AudioDirector.context_for("hq", &"rebel_cell"), "rebel_cell")
	assert_eq(AudioDirector.context_for("combat", &"orbital"), "combat")
	for ctx in ["meridian_raid", "halcyon_raid", "orbital_raid"]:
		assert_true(AudioDirector.CONTEXTS.has(ctx))


func test_pirate_radio_never_talks_about_another_corporation() -> void:
	for salt in 40:
		var l := Dialogue.line("dj", RC.Voice.NARRATOR, &"meridian", &"", salt)
		assert_not_null(l)
		assert_false(l.text.contains("Solace"), l.text)


func test_corporations_are_listed_open_first_then_by_price() -> void:
	var p := ProfileState.new()
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		p.add_unlock(u)
	for id in [&"solace", &"meridian", &"halcyon", &"orbital"]:
		p.best_ice_by_corp[String(id)] = 10
	var ids := []
	for c in CampaignRules.available_corporations(p, _lookup):
		ids.append(c.id)
	assert_eq(ids, [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"])


func test_the_codex_hides_unmet_enemies_and_lists_classes_and_homes() -> void:
	var p := ProfileState.new()
	var entries := Codex.entries(_lookup, p)
	var titles := []
	for e in entries["Enemies"]:
		titles.append(e["title"])
	assert_false(titles.has("DISPATCH"), "no spoiler before the fight")
	assert_eq(entries["Classes"].size(), 8)
	assert_eq(entries["Home servers"].size(), 5)
	var corp_titles := []
	for e in entries["Corporations"]:
		corp_titles.append(e["title"])
	assert_true(corp_titles.has("???"), "REBEL_CELL stays a secret")
	p.record_usage("seen", &"dispatch_core")
	titles.clear()
	for e in Codex.entries(_lookup, p)["Enemies"]:
		titles.append(e["title"])
	assert_true(titles.has("DISPATCH"))
	var all := Codex.entries(_lookup)
	assert_true(all["Enemies"].size() > 40, "without a profile (tools) everything shows")


func test_rescued_operatives_are_classes_already_on_the_roster() -> void:
	var corp := _corp(&"meridian")
	var c := _campaign(corp, &"ghost")
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 2, &"m1_a", 5, corp)
	var before := c.roster.size()
	s._grant_resource(ContentRegistry.get_content(&"breaker"))
	assert_eq(c.roster.size(), before + 1)
	assert_eq(c.roster[c.roster.size() - 1].class_id, &"ghost", "a Ghost-only Cell rescues a Ghost")
	for id in CORPS:
		var has_rescue := false
		for eid in _lookup.ids_of_class(&"TerminalEventData"):
			var ev := _lookup.get_content(eid) as TerminalEventData
			for ch in ev.choices:
				if ch.reward is ClassData and (ev.corporation_id == id or ev.corporation_id == &""):
					has_rescue = true
		assert_true(has_rescue, "%s has a rescue event" % id)


func test_breaker_has_two_exclusives_shared_with_the_wrecker() -> void:
	var b := ContentRegistry.get_content(&"breaker") as ClassData
	var w := ContentRegistry.get_content(&"wrecker") as ClassData
	assert_eq(b.exclusive_cards.size(), 2)
	assert_eq(w.exclusive_cards.size(), 2)


func _hub_session(class_id: StringName, hub_id: String) -> CombatSession:
	return CombatSession.start(_resolver, class_id, [&"triage_unit"], 3, &"", 0, {"hub_id": hub_id})


func test_alternative_and_mk2_cores() -> void:
	var cls := ContentRegistry.get_content(&"rigger") as ClassData
	assert_eq(_hub_session(&"overclocker", "overclock_core").state.max_ram, cls.max_ram + 2)
	assert_eq(_hub_session(&"overclocker", "overclock_core_mk2").state.max_ram, cls.max_ram + 3)
	var s := _hub_session(&"overclocker", "overclock_core")
	CombatFixture.land(s.state.player, 0, 0)
	var r := s.apply(CombatAction.end_turn())
	var gains := 0
	for e in CombatFixture.events_of(r, "ram"):
		if int(e["amount"]) == 2:
			gains += 1
	assert_true(gains >= 1, "an Overclock Perfect gains 2 RAM")
	assert_eq((ContentRegistry.get_content(&"ghost_core_mk2") as HubCoreData).free_resistance_nudges, 2)
	assert_eq((ContentRegistry.get_content(&"swarm_core_mk2") as HubCoreData).max_drones, 4)
	assert_eq((ContentRegistry.get_content(&"hive_core_mk2") as HubCoreData).max_drones, 5)
	var phantom := _hub_session(&"phantom", "phantom_core_mk2")
	CombatFixture.land(phantom.state.player, 5)
	phantom.apply(CombatAction.end_turn())
	var ghost := ContentRegistry.get_content(&"phantom") as ClassData
	assert_eq(phantom.state.free_nudges, ghost.free_nudges_per_turn + 2, "Phantom Mk2: two turn-start nudges")
	var wrecker := _hub_session(&"wrecker", "wrecker_core_mk2")
	assert_eq(_resolver.fx.spin_bonus_of(wrecker.state.player), 1, "Wrecker Mk2 regains the spin bonus")
	assert_eq(_resolver.fx.spin_bonus_of(_hub_session(&"wrecker", "wrecker_core").state.player), 0)


func _home_campaign(variant_id: StringName) -> Array:
	var grid := GridFixture.chain_grid([&"c1"])
	var v := ContentRegistry.get_content(variant_id) as HomeServerVariantData
	var c := GridFixture.campaign(grid)
	c.grid = GridState.from_grid(grid, v.core)
	c.grid.sites[c.grid.home_site_id]["node_type"] = String(v.core.id)
	for n in v.internal_nodes:
		c.grid.home_max_integrity += n.integrity
		c.grid.home_asset_slots += n.asset_slots
		if n.built_in_asset != null:
			c.grid.home_built_in.append(String(n.built_in_asset.id))
	c.grid.home_integrity = c.grid.home_max_integrity
	return [c, grid]


func test_the_ghost_home_holds_the_first_threat_at_the_door() -> void:
	var pair := _home_campaign(&"home_ghost")
	var c: CampaignState = pair[0]
	var raid := GridFixture.raid(&"probe", [&"collector"])
	var result := RaidResolver.resolve(c, pair[1], raid, _lookup, _cfg)
	var held_at_home := false
	for e in result.events:
		if e.get("type", "") == "ice_lock" and e.get("site", &"") == c.grid.home_site_id:
			held_at_home = true
	assert_true(held_at_home, "the built-in Ghost Lock holds at home")
	var plain := _home_campaign(&"home_fortress")
	var r2 := RaidResolver.resolve(plain[0], plain[1], raid, _lookup, _cfg)
	for e in r2.events:
		assert_ne(e.get("type", ""), "shot", "the Fortress has no gun")
	assert_eq((plain[0] as CampaignState).grid.home_max_integrity, 100)


func test_mirror_threats_route_like_the_asset_they_copy() -> void:
	var turret := RebelCellBuilder._mirror_threat(ContentRegistry.get_content(&"turret") as DefenseAssetData)
	var lock := RebelCellBuilder._mirror_threat(ContentRegistry.get_content(&"ice_lock") as DefenseAssetData)
	var decoy := RebelCellBuilder._mirror_threat(ContentRegistry.get_content(&"decoy") as DefenseAssetData)
	assert_eq(turret.routing, RC.ThreatRouting.WEAKEST_NODE)
	assert_true(lock.freezes_edges)
	assert_eq(decoy.edges_per_step, 2)
	assert_eq(decoy.routing, RC.ThreatRouting.HIGHEST_VALUE)


func test_a_rebel_cell_save_resumes_mid_netrun() -> void:
	RunManager.save_slot = "gut_test_rc_mid"
	RunManager.scene_switching_enabled = false
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10
	RunManager.new_campaign(2, &"rebel_cell")
	var s := RunManager.start_run()
	assert_not_null(s)
	s.enter_node(s.available_nodes()[0])
	RunManager.autosave()
	RunManager.reset()
	assert_true(RunManager.resume())
	assert_not_null(RunManager.netrun, "the netrun comes back")
	assert_true(RunManager.corporation.generated_from_profile)
	assert_true(RunManager.netrun.pools()["elites"].size() >= 1, "with its Mirrors")
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_every_corporations_events_resolve_in_its_own_campaign() -> void:
	for cid in CORPS:
		var corp := _corp(cid)
		for id in _lookup.ids_of_class(&"TerminalEventData"):
			var ev := _lookup.get_content(id) as TerminalEventData
			if ev.corporation_id != cid:
				continue
			for i in ev.choices.size():
				var c := _campaign(corp)
				var s := NetrunSession.start(_resolver, c, c.roster[0].id, 2, corp.city_grid.get_site(corp.city_grid.home_site_id).links[0], 5, corp)
				s.run.cycles = 500
				s.run.phase = RunState.Phase.EVENT
				s.run.event_id = id
				for e in s.choose_event_option(i):
					assert_ne(e.get("type", ""), "unsupported_effect", "%s choice %d" % [id, i])
					if not String(e.get("text", "")).contains("fits no slice"):  # H14: a Firmware that fits no slot is refused on purpose
						assert_ne(e.get("type", ""), "refused", "%s choice %d" % [id, i])
