extends GutTest
## Gap analysis pass 2 (V1-V3): Rank gating uses the operative's own class, clicking a
## Site on the Grid map selects it and lists its actions first, and the netrun reward,
## event, shop and end panels are zine-styled.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func _descendants(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_descendants(c))
	return out


func test_rank_gating_uses_the_operatives_own_class() -> void:
	var cfg := CombatFixture.config()
	var lookup := GridFixture.lookup()
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var breaker := ContentRegistry.get_content(&"breaker") as ClassData
	var c := CampaignRules.new_campaign(corp, cfg, lookup, 1, breaker, GridFixture.home_node())
	var op := c.roster[0]
	var site := CampaignRules.site_data(corp, &"t1_a")
	assert_eq(CampaignRules.launch_error(c, corp, cfg, op, breaker, site), "")
	var other := ClassData.new()
	other.id = &"other_class"
	assert_string_contains(CampaignRules.launch_error(c, corp, cfg, op, other, site), "does not match", "a mismatched class is refused, not silently used")
	RunManager.new_campaign(3)
	var first := RunManager.campaign.living_operatives()[0]
	assert_eq(RunManager.launch_error(first.id, &"t1_a"), "", "RunManager passes the operative's class")


func test_clicking_a_site_on_the_map_selects_it_and_lists_its_actions_first() -> void:
	var hq: Control = add_child_autofree(load(HQ).instantiate())
	hq.new_campaign(4)
	hq.show_grid()
	watch_signals(hq.grid_view)
	hq.grid_view.site_clicked.emit(&"t1_b")
	assert_eq(hq.selected_site, &"t1_b")
	assert_eq(hq.grid_view.selected_id, &"t1_b", "highlighted on the new map")
	var picked: Node = hq._panel.find_child("SelectedSite", true, false)
	assert_not_null(picked, "the selected row is shown")
	var launch := false
	for n in _descendants(picked):
		if n is Button and String(n.text).begins_with("Launch"):
			launch = true
	assert_true(launch, "its launch action is right there")


func test_netrun_panels_are_zine_styled() -> void:
	var scene: Control = add_child_autofree(load(NETRUN).instantiate())
	scene.new_campaign(7)
	scene.start_run(1)
	var s := RunManager.netrun
	# Reward: stickers.
	s.run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	s.run.phase = RunState.Phase.REWARD
	scene._show_current()
	var stickers: Node = scene._panel.find_child("Stickers", true, false)
	assert_not_null(stickers)
	assert_eq(stickers.get_child_count(), 3)
	assert_true(stickers.get_child(0) is ZineCard)
	(stickers.get_child(0) as ZineCard).pressed.emit()
	assert_true(s.run.operative.deck.has(&"twist"), "clicking the sticker takes the card")
	# Event: paper for a street voice, a dark strip for DISPATCH.
	s.run.event_id = &"ev_leash_on_the_floor"
	s.run.phase = RunState.Phase.EVENT
	scene._show_current()
	assert_true(scene._panel.find_child("EventPanel", true, false) is ZinePanel)
	s.run.event_id = &"ev_dispatch_early_reply"
	scene._show_current()
	var strip: Node = scene._panel.find_child("EventPanel", true, false)
	assert_true(strip is PanelContainer and not (strip is ZinePanel), "DISPATCH is never zined")
	# Shop: stickers with prices.
	s.run.event_id = &""
	s._open_shop()
	scene._show_current()
	var shop_stickers: Node = scene._panel.find_child("Stickers", true, false)
	assert_true(shop_stickers.get_child_count() >= 3)
	var first: ZineCard = shop_stickers.get_child(0)
	assert_eq(first.cost, int(s.run.shop["card_prices"][0]), "the cost circle shows the price")
	# End: a stamp.
	s.run.outcome = RunState.Outcome.COMPLETED
	s.run.phase = RunState.Phase.ENDED
	scene._show_current()
	var stamp := false
	for n in _descendants(scene._panel):
		stamp = stamp or (n is ZineStamp and n.stamp_text == "CLEAN EXIT")
	assert_true(stamp)


func test_patrols_rank_operatives_up_without_touching_the_grid() -> void:
	var cfg := CombatFixture.config()
	var lookup := GridFixture.lookup()
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var breaker := ContentRegistry.get_content(&"breaker") as ClassData
	var c := CampaignRules.new_campaign(corp, cfg, lookup, 1, breaker, GridFixture.home_node())
	assert_eq(CampaignRules.patrol_sites(c, corp).size(), 0, "nothing cleared yet")
	var r := RunState.new()
	r.site_id = &"t2_intel"
	c.grid.site(&"t1_a")["status"] = GridState.SiteStatus.CLEARED
	CampaignRules.on_run_completed(c, corp, cfg, r)
	assert_eq(c.exploits.size(), 1)
	var intel := CampaignRules.site_data(corp, &"t2_intel")
	assert_eq(CampaignRules.run_kind_for(c, intel), "patrol")
	assert_true(CampaignRules.patrol_sites(c, corp).has(intel))
	var op := c.roster[0]
	op.rank = 1
	assert_eq(CampaignRules.launch_error(c, corp, cfg, op, breaker, intel), "", "a patrol is launchable")
	var events := CampaignRules.on_run_completed(c, corp, cfg, r)
	assert_eq(events[0]["type"], "patrol_complete")
	assert_eq(c.exploits.size(), 1, "no second Exploit from a patrol")
	assert_eq(c.story_beats_revealed, 1)
	# A claimed Site stays claimed after a patrol.
	CampaignRules.claim(c, corp, cfg, lookup, &"t1_a", &"relay")
	var p := RunState.new()
	p.site_id = &"t1_a"
	CampaignRules.on_run_completed(c, corp, cfg, p)
	assert_true(c.grid.is_claimed(&"t1_a"))
	assert_false(CampaignRules.is_patrol(c, CampaignRules.site_data(corp, &"renewal_engine_site")), "never the boss")


func test_enemy_damage_scales_separately_from_hp() -> void:
	var cfg := CombatFixture.config()
	var c := CampaignState.new()
	c.campaign_seed = 3
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	var s := NetrunSession.start(CombatFixture.resolver(), c, &"op_1", 3, &"t3_core", 5)
	assert_almost_eq(s.enemy_scale(), pow(cfg.enemy_scale_per_tier, 2), 0.0001)
	assert_almost_eq(s.enemy_output_scale(), pow(cfg.enemy_damage_scale_per_tier, 2), 0.0001)
	s.enter_node(s.available_nodes()[0])
	var e := s.combat.state.get_combatant(&"enemy_0")
	var data := ContentRegistry.get_content(e.source_id) as EnemyData
	assert_eq(e.max_hp, roundi(data.hp * s.enemy_scale()))
	assert_almost_eq(e.output_scale, s.enemy_output_scale(), 0.0001)
	for sat in s.combat.state.satellites_of(e.id):
		assert_almost_eq(sat.output_scale, s.enemy_output_scale(), 0.0001, "satellites inherit the damage scale")
		assert_almost_eq(sat.hp_scale, s.enemy_scale(), 0.0001, "and the HP scale")
