extends GutTest
## Designer answers to M3 (2026-09-24): tier scaling hits mini-bosses and the boss, the
## final Rack holds a mini-boss, raids interrupt a run between map nodes, station bonuses
## scale with Rank, and the Breaker Rank 2 Hub Core exists.

var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _corp: CorporationData
var _breaker: ClassData


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"solace") as CorporationData
	_breaker = ContentRegistry.get_content(&"breaker") as ClassData


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


func _path_to_final(s: NetrunSession) -> Array[StringName]:
	var prev := {}
	var queue: Array[StringName] = s.available_nodes().duplicate()
	for id in queue:
		prev[id] = &""
	while not queue.is_empty():
		var id: StringName = queue.pop_front()
		if id == s.run.map.final_node_id():
			var path: Array[StringName] = []
			var cur := id
			while cur != &"":
				path.push_front(cur)
				cur = prev[cur]
			return path
		for n in s.run.map.get_node(id)["next"]:
			if not prev.has(n):
				prev[n] = id
				queue.append(n)
	return []


func _settle(s: NetrunSession) -> void:
	var guard := 0
	while not s.run.is_over() and s.run.phase != RunState.Phase.MAP and guard < 200:
		guard += 1
		match s.run.phase:
			RunState.Phase.COMBAT:
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


func test_final_rack_is_a_mini_boss_scaled_by_tier() -> void:
	RunManager.new_campaign(31)
	var s := RunManager.start_run()
	assert_true(s.pools()["mini_bosses"].has(&"account_manager"))
	assert_false(s.pools()["elites"].has(&"account_manager"), "mini-bosses are not ordinary elites")
	var path := _path_to_final(s)
	for id in path:
		s.enter_node(id)
		if id == path[path.size() - 1]:
			break
		_settle(s)
	assert_true(s.in_combat())
	var enemy := s.combat.state.get_combatant(&"enemy_0")
	assert_eq(enemy.source_id, &"account_manager")
	assert_eq(enemy.max_hp, 120, "tier 1: unscaled")
	assert_eq(enemy.resistance, 1)
	# Tier 2 run: the mini-boss (and everything else) scales x1.6.
	var c := RunManager.campaign
	c.living_operatives()[0].rank = 3
	CampaignRules.on_run_completed(c, _corp, _cfg, _demo_run(&"t1_a"))
	var op := c.living_operatives()[0]
	RunManager.clear_run()
	var t2 := RunManager.start_run(op.id, &"t2_intel")
	assert_eq(t2.enemy_scale(), 1.6)


func test_the_final_boss_is_tier_scaled_too() -> void:
	RunManager.new_campaign(32)
	var c := RunManager.campaign
	c.exploits = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
	for id in [&"t1_a", &"t2_intel", &"t3_core"]:
		c.grid.sites[id]["status"] = GridState.SiteStatus.CLEARED
	var op := c.living_operatives()[0]
	op.rank = 3
	var s := RunManager.start_run(op.id, &"renewal_engine_site")
	assert_eq(s.run.kind, "boss")
	assert_eq(s.enemy_scale(), pow(1.6, 3))
	s.enter_node(s.available_nodes()[0])
	var boss := s.combat.state.get_combatant(&"enemy_0")
	assert_eq(boss.max_hp, roundi(300 * pow(1.6, 3)), "1229 HP at T4")
	assert_almost_eq(boss.output_scale, pow(_cfg.enemy_damage_scale_per_tier, 3), 0.0001, "damage scales with its own factor")


func test_a_threshold_raid_during_a_run_is_fought_as_an_interlude() -> void:
	RunManager.new_campaign(33)
	var c := RunManager.campaign
	c.heat = 24
	var s := RunManager.start_run()
	assert_eq(s.run.phase, RunState.Phase.MAP, "no raid pending at launch")
	# Find an elite Router (+1 Heat on entry crosses 25 -> raid queued).
	var target: StringName = &""
	var path: Array[StringName] = []
	var prev := {}
	var queue: Array[StringName] = s.available_nodes().duplicate()
	for id in queue:
		prev[id] = &""
	while not queue.is_empty() and target == &"":
		var id: StringName = queue.pop_front()
		var node := s.run.map.get_node(id)
		if node["elite"] and node["type"] == RC.InfilNodeType.ROUTER:
			target = id
			var cur := id
			while cur != &"":
				path.push_front(cur)
				cur = prev[cur]
			break
		for n in node["next"]:
			if not prev.has(n):
				prev[n] = id
				queue.append(n)
	assert_ne(target, &"", "an elite Router exists")
	for id in path:
		s.enter_node(id)
		if id == target:
			break
		_settle(s)
	assert_eq(c.heat, 25)
	assert_eq(c.pending_raids.size(), 1, "the Heat 25 raid is queued")
	assert_true(s.in_combat(), "the node's fight comes first")
	# Finish the fight and its rewards: the raid interrupts before the map.
	var guard := 0
	while (s.in_combat() or s.run.phase == RunState.Phase.REWARD) and guard < 100:
		guard += 1
		if s.in_combat():
			s.combat.state.player.max_hp = 9999
			s.combat.state.player.hp = 9999
			CombatFixture.land(s.combat.state.player, 0)
			s.combat_action(CombatAction.end_turn())
		else:
			s.skip_reward()
	assert_eq(s.run.phase, RunState.Phase.RAID, "raid interlude between map nodes")
	assert_true(s.in_raid())
	assert_eq(s.available_nodes().size(), 0, "no moving during the raid")
	s.run.unbanked_assets.append(&"turret")
	c.grid.sites[&"t1_a"]["status"] = GridState.SiteStatus.CLEARED
	c.schematics = 100
	CampaignRules.claim(c, _corp, _cfg, _lookup, &"t1_a", &"firewall_relay")
	assert_true(c.grid.is_claimed(&"t1_a"))
	assert_eq(c.pending_raids.size(), 2, "the claim provoked a second raid")
	var events := s.raid_deploy_run_asset(s.run_assets().find(&"turret"), &"t1_a")
	assert_eq(events[0]["type"], "deployed", "the run's own asset can be deployed mid-run")
	assert_eq(c.grid.assets_on(&"t1_a"), [&"turret"])
	assert_false(s.run_assets().has(&"turret"), "it left the run's inventory")
	var projection := s.raid_projection()
	assert_not_null(projection)
	# Save mid-interlude and resume identically.
	RunManager.after_step()
	var hash_before := s.state_hash()
	RunManager.reset()
	assert_true(RunManager.resume())
	s = RunManager.netrun
	c = RunManager.campaign
	assert_eq(s.state_hash(), hash_before)
	assert_true(s.in_raid())
	s.raid_fight()
	assert_eq(c.last_raid["home_after"], projection.home_after, "projection == playout mid-run")
	assert_eq(c.pending_raids.size(), 1, "the claim raid is still queued")
	assert_true(s.in_raid(), "back-to-back interludes")
	s.raid_fight()
	assert_eq(c.pending_raids.size(), 0)
	assert_eq(s.run.phase, RunState.Phase.MAP, "back to the map after the raids")
	RunManager.after_step()
	assert_eq(RunManager.profile.raids_won + RunManager.profile.raids_lost, 2, "profile counted both mid-run raids once")
	assert_eq(c.grid.assets_on(&"t1_a"), [&"turret"], "the deployed asset persists on the node")


func test_home_server_loss_during_an_interlude_aborts_the_run() -> void:
	RunManager.new_campaign(34)
	var c := RunManager.campaign
	var s := RunManager.start_run()
	c.grid.home_integrity = 1
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	s.enter_node(s.available_nodes()[0])
	_settle(s)
	assert_true(s.run.is_over())
	assert_eq(s.run.outcome, RunState.Outcome.ABORTED)
	assert_eq(c.outcome, CampaignState.Outcome.LOST)
	RunManager.after_step()
	assert_eq(RunManager.profile.campaigns_lost, 1)


func test_station_bonus_scales_asset_damage_with_rank() -> void:
	var grid := GridFixture.chain_grid([&"r1"])
	var c := GridFixture.campaign(grid, {&"r1": &"firewall_relay"})
	c.recruit(_breaker, "Vex")
	GridFixture.deploy(c, &"r1", &"turret")
	var raid := GridFixture.raid(&"sb", [&"enforcer"])
	var plain := RaidResolver.resolve(c, grid, raid, _lookup, _cfg, [&"entry"])
	c.grid.site(&"r1")["stationed"] = "op_1"
	assert_eq(RaidResolver.station_damage_multiplier(c, c.grid, grid, _lookup, &"r1"), 1.5, "Rank 0: +50%")
	c.roster[0].rank = 3
	assert_eq(RaidResolver.station_damage_multiplier(c, c.grid, grid, _lookup, &"r1"), 2.0, "Rank 3: bonus x2 -> +100%")
	var boosted := RaidResolver.resolve(c, grid, raid, _lookup, _cfg, [&"entry"])
	var first_shot := {}
	for e in boosted.events:
		if e.get("type", "") == "shot" and e["asset"] == &"turret":
			first_shot = e
			break
	assert_eq(first_shot["damage"], 8, "turret 4 x 2.0")
	assert_true(boosted.threats_destroyed >= plain.threats_destroyed)
	# Adjacent Firewall Relay shares a Safehouse operative's bonus; a plain Relay does not.
	var grid2 := GridFixture.chain_grid([&"f1", &"s1"])
	var c2 := GridFixture.campaign(grid2, {&"f1": &"firewall_relay", &"s1": &"safehouse"})
	c2.recruit(_breaker, "Vex")
	c2.grid.site(&"s1")["stationed"] = "op_1"
	assert_eq(RaidResolver.station_damage_multiplier(c2, c2.grid, grid2, _lookup, &"f1"), 1.5, "Firewall Relay next to the Safehouse")
	assert_eq(RaidResolver.station_damage_multiplier(c2, c2.grid, grid2, _lookup, &"home"), 1.0, "home is not a Firewall Relay")


func test_rank_2_breaker_fights_with_the_mk2_core() -> void:
	var op := OperativeState.from_class(_breaker, &"op_x", "Vex")
	assert_eq(op.hub_id(_breaker), &"")
	op.rank = 2
	assert_eq(op.hub_id(_breaker), &"breaker_core_mk2")
	assert_eq(op.station_multiplier(_breaker), 1.5)
	var resolver := CombatFixture.resolver()
	var s := CombatSession.start(resolver, &"breaker", [&"compliance_officer"], 3, &"rank:1", 0, {"hub_id": "breaker_core_mk2"})
	assert_eq(s.state.player.wheel.hub_id, &"breaker_core_mk2")
	assert_eq(resolver.fx.spin_bonus_of(s.state.player), 2, "+2 spin")
	var dummy := CombatFixture.enemy(&"mk_dummy", 200, CombatFixture.miss_wheel())
	var s2 := CombatSession.start(CombatFixture.resolver([dummy]), &"breaker", [&"mk_dummy"], 3, &"rank:1", 0, {"hub_id": "breaker_core_mk2"})
	CombatFixture.land(s2.state.player, 1, 0)
	CombatFixture.land_inner(s2.state.player, 2)
	var ram := s2.state.ram
	var r := s2.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "damage").size(), 2, "Perfect still resolves twice")
	assert_eq(s2.state.ram, mini(ram + 2 + 4, 12), "+1 RAM per resolution, then regen")


func _demo_run(site_id: StringName) -> RunState:
	var r := RunState.new()
	r.site_id = site_id
	return r
