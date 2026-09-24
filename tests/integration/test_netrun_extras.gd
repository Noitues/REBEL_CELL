extends GutTest
## Netrun rules added by the vertical-slice fixes: Routers drop common Firmware some of
## the time (GDD 6.3), Reclaim runs do not raise Rank (decision 2026-09-24), and
## RunManager starts campaigns at a chosen ICE on a chosen home server.

var _resolver: CombatResolver
var _cfg: CampaignConfigData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = _resolver.config


func before_each() -> void:
	RunManager.save_slot = "gut_test"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func _campaign() -> CampaignState:
	var c := CampaignState.new()
	c.campaign_seed = 4
	c.schematics = 20
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	return c


func _win_first_router(s: NetrunSession) -> void:
	s.enter_node(s.available_nodes()[0])
	var turns := 0
	while s.in_combat() and turns < 60:
		turns += 1
		s.combat.state.player.hp = s.combat.state.player.max_hp
		CombatFixture.land(s.combat.state.player, 0)
		s.combat_action(CombatAction.end_turn())


func test_routers_sometimes_drop_common_firmware() -> void:
	var offered := 0
	var runs := 0
	for seed in range(1, 25):
		var s := NetrunSession.start(_resolver, _campaign(), &"op_1", 1, &"t1_a", seed)
		_win_first_router(s)
		runs += 1
		for offer in s.run.pending_rewards:
			if offer["kind"] == "firmware":
				offered += 1
				assert_eq(offer["options"].size(), _cfg.router_firmware_choices)
				for id in offer["options"]:
					assert_eq((ContentRegistry.get_content(StringName(String(id))) as FirmwareData).rarity, RC.Rarity.COMMON, "%s is common" % id)
	assert_true(offered > 0, "some Routers dropped Firmware (%d of %d)" % [offered, runs])
	assert_true(offered < runs, "not every Router does (%d of %d)" % [offered, runs])


func test_reclaim_runs_do_not_raise_rank() -> void:
	var c := _campaign()
	var s := NetrunSession.start_special(_resolver, c, &"op_1", "reclaim", &"t1_a", 1, 9, &"triage_unit", {})
	_win_first_router(s)
	assert_eq(s.run.outcome, RunState.Outcome.COMPLETED)
	assert_eq(c.get_operative(&"op_1").rank, 0, "one fight is not a netrun")
	assert_eq(c.get_operative(&"op_1").runs_completed, 1)


func test_run_manager_starts_campaigns_at_a_chosen_ice_on_an_unlocked_home() -> void:
	assert_eq(RunManager.ice_cap(), 3)
	var c := RunManager.new_campaign(11, &"solace", 9)
	assert_eq(c.ice_level, 3, "clamped to the profile cap")
	assert_eq(RunManager.available_home_variants().size(), 1, "only the standard home without the unlock")
	RunManager.profile.add_unlock(&"unlock_home_bunker")
	assert_eq(RunManager.available_home_variants().size(), 2)
	c = RunManager.new_campaign(11, &"solace", 2, &"home_bunker")
	assert_eq(c.ice_level, 2)
	assert_eq(c.home_variant_id, &"home_bunker")
	assert_eq(c.grid.home_max_integrity, 70)
	assert_true(RunManager.resume(), "the campaign was autosaved")
	assert_eq(RunManager.campaign.home_variant_id, &"home_bunker")
	assert_eq(RunManager.campaign.ice_level, 2)
