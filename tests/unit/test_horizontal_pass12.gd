extends GutTest
## Horizontal pass 12 fixes (GAP_ANALYSIS H12): one profile for every campaign slot, a
## patrol stays a patrol when its Site is Seized mid-run, an Exploit is never held twice,
## Daemon tuning and raid pacing come from content and config, Twin Pointer's Miss spoils
## Cold Exit, and long HQ / title panels wrap. (The final Rack's rewards: test_netrun.gd.)

var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _corp: CorporationData


var _text_scale_before: float = 1.0


## A failed width test must not leave the player's text scale changed.
func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)

func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"solace") as CorporationData


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func test_every_campaign_slot_shares_one_profile() -> void:
	var before := RunManager.save_slot
	var paths := {}
	for slot in ["1", "2", "3", RunManager.DEFAULT_SLOT]:
		RunManager.save_slot = slot
		paths[RunManager.profile_path()] = true
	assert_eq(paths.size(), 1, "slots 1-3 and the default slot use one profile file")
	RunManager.save_slot = "gut_test_profile_private"
	assert_false(paths.has(RunManager.profile_path()), "test slots keep a private profile")
	RunManager.save_slot = before


func _exploit_site() -> SiteData:
	for s in _corp.city_grid.sites:
		if s != null and s.objective == RC.SiteObjective.EXPLOIT:
			return s
	return null


func _campaign() -> CampaignState:
	return CampaignRules.new_campaign(_corp, _cfg, _lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())


func test_a_patrol_seized_mid_run_stays_a_patrol() -> void:
	var c := _campaign()
	var site := _exploit_site()
	assert_not_null(site)
	c.grid.sites[site.id]["status"] = GridState.SiteStatus.CLEARED
	c.exploits = [site.exploit_type]
	var s := NetrunSession.start(CombatFixture.resolver(), c, c.roster[0].id, site.tier, site.id, 5, _corp)
	assert_true(s.run.patrol, "launched as a patrol")
	var back := RunState.from_dict(s.run.to_dict())
	assert_true(back.patrol, "saved with the run")
	c.grid.sites[site.id]["status"] = GridState.SiteStatus.SEIZED  # a mid-run raid takes it
	var heat := c.heat
	CampaignRules.on_run_completed(c, _corp, _cfg, s.run, _lookup)
	assert_eq(c.exploits, [site.exploit_type], "no second Exploit")
	assert_eq(c.heat, heat, "no Exploit Heat")
	assert_eq(int(c.grid.sites[site.id]["status"]), GridState.SiteStatus.SEIZED, "the Site stays Seized")


func test_an_exploit_is_never_held_twice() -> void:
	var c := _campaign()
	var site := _exploit_site()
	c.exploits = [site.exploit_type]
	var run := RunState.new()
	run.site_id = site.id
	CampaignRules.on_run_completed(c, _corp, _cfg, run, _lookup)
	assert_eq(c.exploits, [site.exploit_type])


func test_daemon_tuning_comes_from_the_daemon() -> void:
	var expect := {&"cold_exit": 3, &"scrubber": 1, &"kernel_sync": 1, &"zero_day": 3, &"botnet_seed": 2}
	for id in expect:
		var d := ContentRegistry.get_content(id) as DaemonData
		assert_eq(d.amount, expect[id], String(id))
	var d: DaemonData = (ContentRegistry.get_content(&"cold_exit") as DaemonData).duplicate()
	d.amount = 7
	var run := RunState.new()
	var out: Array = d.custom_handler.new().handle({"trigger": RC.Trigger.ON_NETRUN_COMPLETE, "daemon": d}, run, null)
	assert_eq(int(out[0]["amount"]), -7)


func test_raid_pacing_comes_from_the_config() -> void:
	var grid := GridFixture.chain_grid([&"c1"])
	var c := GridFixture.campaign(grid)
	var raid := GridFixture.raid(&"probe", [&"enforcer"], 8, 2)
	var cfg: CampaignConfigData = _cfg.duplicate()
	cfg.raid_wave_interval = 9
	var entries: Array[StringName] = [&"entry"]
	var waves: Dictionary = RaidResolver._waves(raid, entries, c, cfg, 0.0)
	var steps := waves.keys()
	steps.sort()
	assert_eq(steps, [1, 1 + cfg.raid_wave_interval], "waves start every raid_wave_interval steps")


func test_twin_pointers_miss_spoils_cold_exit() -> void:
	var atk := CombatFixture.slice(&"h12_atk", RC.SliceType.ATTACK, 6)
	var miss := CombatFixture.slice(&"h12_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)
	var hub := CombatFixture.hub(&"h12_hub")
	var deck: Array[CardData] = [CombatFixture.card(&"h12_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"h12_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, miss], hub), deck)
	var enemy := CombatFixture.enemy(&"h12_dummy", 300, CombatFixture.miss_wheel())
	var s := CombatSession.start(CombatFixture.resolver([cls, enemy]), cls.id, [enemy.id], 9, &"", 0, {"daemon_ids": ["twin_pointer"]})
	CombatFixture.land(s.state.player, 2)  # pointer 0 on Atk (slot 2), pointer 1 on the Miss (slot 5)
	s.apply(CombatAction.end_turn())
	assert_true(s.state.miss_resolved, "the second read head resolved the Miss")


func _width(panel: Control) -> float:
	return panel.get_combined_minimum_size().x


func test_raid_setup_end_and_title_panels_fit_at_every_text_scale() -> void:
	var before := Settings.text_scale
	RunManager.save_slot = "gut_test_widths_h12"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var c := RunManager.campaign
		HeatRules.add_heat(c, 26, RunManager.config(), "test")
		var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
		if not c.pending_raids.is_empty():
			hq.show_raid()
			await _frames()
			assert_true(_width(hq._panel) <= 1280.0, "raid setup %d px at %.1f" % [_width(hq._panel), scale])
		c.story_beats_revealed = 99
		c.outcome = CampaignState.Outcome.WON
		hq.show_end()
		await _frames()
		assert_true(_width(hq._panel) <= 1280.0, "end screen %d px at %.1f" % [_width(hq._panel), scale])
		hq.queue_free()
		var title: Control = add_child_autofree(load("res://scenes/menu/title_scene.tscn").instantiate())
		for show in ["show_main", "show_slots", "show_stats", "show_codex"]:
			title.call(show)
			await _frames()
			assert_true(_width(title._panel) <= 1280.0, "title %s %d px at %.1f" % [show, _width(title._panel), scale])
		title.queue_free()
		RunManager.campaign = null
	Settings.set_text_scale(before)
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
