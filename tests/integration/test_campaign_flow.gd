extends GutTest
## Whole-campaign flow through RunManager and the HQ scene (M3 acceptance): win with
## 3 Exploits, lose at home integrity 0, profile records, campaign save/load exactness.

const HQ := "res://scenes/hq/hq_scene.tscn"

var _hq: Control


func before_each() -> void:
	RunManager.save_slot = "gut_test"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	_hq = add_child_autofree(load(HQ).instantiate())


func after_each() -> void:
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


## Plays the active run to its end like an invincible, hurried player.
func _finish_run() -> void:
	var s := RunManager.netrun
	var steps := 0
	while not s.run.is_over() and steps < 400:
		steps += 1
		match s.run.phase:
			RunState.Phase.MAP:
				s.enter_node(s.available_nodes()[0])
			RunState.Phase.COMBAT:
				# Invincible test operative: tier-scaled bosses hit far harder than 60 HP.
				s.combat.state.player.max_hp = 9999
				s.combat.state.player.hp = 9999
				CombatFixture.land(s.combat.state.player, 0)
				s.combat_action(CombatAction.end_turn())
			RunState.Phase.REWARD:
				s.skip_reward()
			RunState.Phase.EVENT:
				s.choose_event_option(s.current_event().choices.size() - 1)
			RunState.Phase.SHOP:
				s.leave_shop()
			RunState.Phase.RAID:
				s.raid_fight()
	RunManager.after_step()
	RunManager.clear_run()


func _clear(site_id: StringName) -> void:
	var op := RunManager.campaign.living_operatives()[0]
	op.rank = 3  # rank gating is tested in test_campaign_rules; here we want the flow
	assert_true(_hq.launch(site_id, op.id), "launched %s" % site_id)
	_finish_run()
	# Retaliation and story raids now follow every objective run (GDD 4.4); this flow test
	# is about the breach gate, not defense, so the undefended home is patched up.
	RunManager.campaign.grid.home_integrity = RunManager.campaign.grid.home_max_integrity
	assert_true(RunManager.campaign.grid.is_cleared(site_id) or RunManager.campaign.is_over(), "%s cleared" % site_id)


func test_new_campaign_shows_hq_and_the_grid_lists_three_t1_sites() -> void:
	_hq.new_campaign(3)
	assert_eq(_hq.panel_name, "hq")
	_hq.show_grid()
	assert_eq(_hq.panel_name, "grid")
	assert_eq(RunManager.launchable_sites().size(), 3)
	assert_eq(RunManager.profile.campaigns_started, 1)


func test_winning_the_breach_with_three_exploits_wins_the_campaign_and_records_it() -> void:
	_hq.new_campaign(5)
	for id in [&"t1_a", &"t1_b", &"t1_c", &"t2_intel", &"t2_breach", &"t2_virus", &"t3_core"]:
		_clear(id)
	var c := RunManager.campaign
	assert_eq(c.exploits.size(), 3)
	assert_eq(c.story_beats_revealed, 3, "one beat per Exploit")
	assert_true(RunManager.launch_error(c.living_operatives()[0].id, &"renewal_engine_site") == "", "breach open")
	var op := c.living_operatives()[0]
	assert_true(_hq.launch(&"renewal_engine_site", op.id))
	assert_eq(RunManager.netrun.run.kind, "boss")
	assert_eq(RunManager.netrun.run.combat_overrides["remove_boss_pointers"], 1)
	RunManager.netrun.enter_node(RunManager.netrun.available_nodes()[0])
	assert_eq(RunManager.netrun.combat.state.get_combatant(&"enemy_0").source_id, &"renewal_engine")
	assert_eq(RunManager.netrun.combat.state.get_combatant(&"enemy_0").wheel.slice_statuses.count(RC.Status.CORRUPTED), 2, "Virus")
	_finish_run()
	assert_eq(c.outcome, CampaignState.Outcome.WON)
	assert_eq(RunManager.profile.campaigns_won, 1, "profile records the win")
	assert_eq(RunManager.profile.best_ice_for(&"solace"), 0)
	assert_true(RunManager.profile.runs_completed >= 8)
	_hq.show_end()
	assert_eq(_hq.panel_name, "end")


func test_home_integrity_zero_loses_the_campaign_and_records_it() -> void:
	_hq.new_campaign(6)
	var c := RunManager.campaign
	c.grid.home_integrity = 5
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	_hq.show_raid()
	assert_eq(_hq.panel_name, "raid")
	var projection := RunManager.project_raid()
	assert_true(projection.campaign_lost, "projection already shows the loss")
	_hq.fight_raid()
	assert_eq(c.outcome, CampaignState.Outcome.LOST)
	assert_eq(_hq.panel_name, "end")
	assert_eq(RunManager.profile.campaigns_lost, 1)
	assert_eq(RunManager.profile.raids_lost, 1)


func test_raid_setup_projection_matches_the_playout_and_assets_persist() -> void:
	_hq.new_campaign(8)
	var c := RunManager.campaign
	_clear(&"t1_a")
	c.schematics = 100
	c.armory = [&"turret", &"ice_lock"]  # after the run: runs bank their own drops
	_hq.claim(&"t1_a", &"firewall_relay")
	assert_true(c.grid.is_claimed(&"t1_a"))
	assert_eq(c.pending_raids.size(), 1, "claiming next to corporate Sites provoked a raid")
	_hq.deploy_asset(0, &"t1_a")
	_hq.deploy_asset(0, &"t1_a")
	assert_eq(c.grid.assets_on(&"t1_a"), [&"turret", &"ice_lock"])
	var projection := RunManager.project_raid()
	_hq.fight_raid()
	assert_eq(c.last_raid["home_after"], projection.home_after, "projection == playout")
	assert_eq(c.last_raid["won"], projection.won)
	assert_eq(c.grid.assets_on(&"t1_a"), [&"turret", &"ice_lock"], "assets persist after the raid")
	assert_eq(_hq.panel_name, "raid_summary")
	# Reposition to home and back to the Armory.
	_hq.move_asset(&"t1_a", 0, &"home")
	assert_eq(c.grid.assets_on(&"home"), [&"turret"])
	_hq.move_asset(&"home", 0, &"")
	assert_eq(c.armory, [&"turret"])


func test_campaign_save_and_resume_are_exact_through_the_manager() -> void:
	_hq.new_campaign(9)
	var c := RunManager.campaign
	_clear(&"t1_a")
	c.schematics = 100
	_hq.claim(&"t1_a", &"relay")
	HeatRules.add_heat(c, 30, RunManager.config(), "test")
	RunManager.autosave()
	var hash_before := c.state_hash()
	var profile_before := RunManager.profile.state_hash()
	RunManager.reset()
	assert_null(RunManager.campaign)
	assert_true(RunManager.resume())
	assert_eq(RunManager.campaign.state_hash(), hash_before, "campaign round-trips exactly")
	assert_eq(RunManager.profile.state_hash(), profile_before, "profile round-trips exactly")
	assert_eq(RunManager.campaign.pending_raids.size(), c.pending_raids.size())
	assert_eq(RunManager.corporation.id, &"solace")
