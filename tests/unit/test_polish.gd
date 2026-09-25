extends GutTest
## M12 polish and reach (GAP_ANALYSIS P1 10, P2 11-13): controller bindings, share codes and
## the daily seed, assist mode, three more home-server variants.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func test_every_combat_action_has_a_controller_button() -> void:
	for action in Settings.CONTROLLER_BINDS:
		var found := false
		for ev in InputMap.action_get_events(action):
			if ev is InputEventJoypadButton and ev.button_index == Settings.CONTROLLER_BINDS[action]:
				found = true
		assert_true(found, "%s has its pad button" % action)
	var seen := {}
	for action in Settings.CONTROLLER_BINDS:
		var b: int = Settings.CONTROLLER_BINDS[action]
		assert_false(seen.has(b), "%s shares a button with %s" % [action, seen.get(b, "")])
		seen[b] = action


func test_rebinding_a_key_keeps_the_pad_button() -> void:
	var before := Settings.key_for(&"end_turn")
	Settings.rebind(&"end_turn", KEY_ENTER)
	var pad := false
	for ev in InputMap.action_get_events(&"end_turn"):
		pad = pad or ev is InputEventJoypadButton
	assert_true(pad)
	Settings.rebind(&"end_turn", before)


func test_campaign_codes_round_trip_and_reject_garbage() -> void:
	var code := CampaignCode.encode(4242, &"meridian", 5, &"home_bunker", &"ghost")
	assert_eq(code, "RC1-meridian-5-4242-home_bunker-ghost")
	var d := CampaignCode.decode(code)
	assert_eq(d["seed"], 4242)
	assert_eq(d["corporation"], &"meridian")
	assert_eq(d["ice"], 5)
	assert_eq(d["home"], &"home_bunker")
	assert_eq(d["class"], &"ghost")
	for bad in ["", "RC1", "RC2-solace-0-1-home_standard-breaker", "RC1-solace-x-1-home_standard-breaker", "RC1--0-1-home_standard-breaker"]:
		assert_eq(CampaignCode.decode(bad), {}, "rejects '%s'" % bad)
	assert_eq(CampaignCode.daily_seed(2026, 9, 24), 20260924)


func test_the_same_code_gives_the_same_campaign() -> void:
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var cls := ContentRegistry.get_content(&"breaker") as ClassData
	var a := CampaignRules.new_campaign(corp, _cfg, _lookup, 777, cls, GridFixture.home_node())
	var b := CampaignRules.new_campaign(corp, _cfg, _lookup, 777, cls, GridFixture.home_node())
	assert_eq(a.state_hash(), b.state_hash())
	assert_eq(CampaignCode.of(a, &"breaker"), "RC1-solace-0-777-home_standard-breaker")


func test_assist_mode_raises_hp_and_free_nudges() -> void:
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var cls := ContentRegistry.get_content(&"breaker") as ClassData
	var c := CampaignRules.new_campaign(corp, _cfg, _lookup, 3, cls, GridFixture.home_node())
	assert_false(c.is_assisted())
	c.enable_assist(_cfg.assist_free_nudges, _cfg.assist_hp_multiplier)
	assert_eq(c.roster[0].max_hp, roundi(cls.base_hp * _cfg.assist_hp_multiplier))
	var later := c.recruit(cls)
	assert_eq(later.max_hp, roundi(cls.base_hp * _cfg.assist_hp_multiplier), "recruits get it too")
	var back := CampaignState.from_dict(c.to_dict())
	assert_true(back.is_assisted(), "saved with the campaign")
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"t1_a", 5, corp)
	s.enter_node(s.available_nodes()[0])
	assert_eq(s.combat.state.free_nudges, cls.free_nudges_per_turn + _cfg.assist_free_nudges)


func test_assisted_wins_set_no_ice_record() -> void:
	RunManager.save_slot = "gut_test_assist"
	RunManager.scene_switching_enabled = false
	RunManager.new_campaign(1)
	RunManager.campaign.enable_assist(1, 1.25)
	var best := RunManager.profile.best_ice_for(&"solace")
	var won := RunManager.profile.campaigns_won
	RunManager.campaign.outcome = CampaignState.Outcome.WON
	RunManager.campaign.ice_level = 7
	RunManager.sync_profile_with_campaign()
	assert_eq(RunManager.profile.campaigns_won, won, "assisted wins are counted apart (no Breach achievement)")
	assert_eq(int(RunManager.profile.stats.get("assisted_wins", 0)), 1)
	assert_eq(RunManager.profile.best_ice_for(&"solace"), best, "no ICE record from an assisted win")
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_three_more_home_servers() -> void:
	var expect := {&"home_relay_nest": [50, 5], &"home_ghost": [50, 2], &"home_fortress": [100, 2]}
	for id in expect:
		var v := ContentRegistry.get_content(id) as HomeServerVariantData
		assert_not_null(v, String(id))
		var integ := v.core.integrity
		var slots := v.core.asset_slots
		for n in v.internal_nodes:
			integ += n.integrity
			slots += n.asset_slots
		assert_eq([integ, slots], expect[id], String(id))
		var u := CampaignRules.unlock_for(_lookup, v)
		assert_not_null(u)
		assert_eq(u.kind, RC.UnlockKind.HOME_SERVER)
	var ghost := ContentRegistry.get_content(&"home_ghost") as HomeServerVariantData
	assert_eq(ghost.internal_nodes[0].built_in_asset.asset_type, RC.AssetType.ICE_LOCK)


func test_hq_starts_a_campaign_from_a_code() -> void:
	RunManager.save_slot = "gut_test_code"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
	hq.show_start()
	assert_not_null(hq.find_child("CodeEdit", true, false))
	assert_false(hq.start_from_code("not a code"))
	assert_true(hq.start_from_code("RC1-solace-0-9090-home_standard-breaker"))
	assert_eq(RunManager.campaign.campaign_seed, 9090)
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
