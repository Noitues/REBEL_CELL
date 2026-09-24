extends GutTest
## Raid resolution (GDD 7, M3 acceptance): golden results for five layouts, projection
## equals the real result, Disabled/Seized rules, cascade (50%), step cap and
## home-server loss. Expected numbers are worked by hand from the A.5 stats
## (Collector 12/5/1, Auditor 8/3/2, Enforcer 25/9/1; Turret 4 dmg range 1; ICE Lock
## holds 2; Firewall turret 3 dmg own node; Relay 15, Safehouse 20, Firewall 30, home 50).

var _cfg: CampaignConfigData
var _lookup: ContentLookup


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func _resolve(c: CampaignState, grid: CityGridData, raid: RaidData, cfg: CampaignConfigData = null) -> RaidResolver.RaidResult:
	return RaidResolver.resolve(c, grid, raid, _lookup, cfg if cfg != null else _cfg, [&"entry"])


func test_layout_1_undefended_relay_is_passed_and_home_takes_the_hit() -> void:
	var grid := GridFixture.chain_grid([&"r1"])
	var c := GridFixture.campaign(grid, {&"r1": &"relay"})
	var r := _resolve(c, grid, GridFixture.raid(&"g1", [&"collector"]))
	assert_eq(r.steps_run, 2)
	assert_eq(r.nodes["r1"]["after"], 10, "Relay 15 - 5")
	assert_eq(r.nodes["r1"]["outcome"], "holds")
	assert_eq(r.home_after, 45, "home 50 - 5")
	assert_eq(r.threats_reached_home, 1)
	assert_false(r.won)
	assert_false(r.campaign_lost)
	assert_eq(c.grid.home_integrity, 50, "resolve() never touches the campaign")


func test_layout_2_ice_lock_and_turret_stop_a_collector() -> void:
	var grid := GridFixture.chain_grid([&"r1"])
	var c := GridFixture.campaign(grid, {&"r1": &"firewall_relay"})
	GridFixture.deploy(c, &"r1", &"ice_lock")
	GridFixture.deploy(c, &"r1", &"turret")
	var r := _resolve(c, grid, GridFixture.raid(&"g2", [&"collector"]))
	# Step 1: enter, advance to r1, locked (2), turret 3 + 4 -> 5 left, node 30-5 = 25.
	# Step 2: held, 7 damage -> destroyed before it can hit again.
	assert_eq(r.steps_run, 2)
	assert_true(r.won)
	assert_eq(r.threats_destroyed, 1)
	assert_eq(r.nodes["r1"]["after"], 25)
	assert_eq(r.home_after, 50)


func test_layout_3_enforcer_disables_a_relay_and_cascades_half_the_excess() -> void:
	var grid := GridFixture.chain_grid([&"r1"])
	var c := GridFixture.campaign(grid, {&"r1": &"relay"})
	var r := _resolve(c, grid, GridFixture.raid(&"g3", [&"enforcer"]))
	# Step 1: r1 15-9 = 6. Step 2: 6-9 = -3 -> Disabled, excess 3 x 0.5 = 1 cascades to home.
	# Step 3: moves on to home: 49 - 9 = 40.
	assert_eq(r.nodes["r1"]["outcome"], "disabled")
	assert_eq(r.nodes["r1"]["after"], 0)
	assert_eq(r.disabled, ["r1"])
	assert_eq(r.home_after, 40)
	assert_eq(r.steps_run, 3)
	var cascades := 0
	for e in r.events:
		if e.get("type", "") == "cascade":
			cascades += 1
			assert_eq(e["damage"], 1)
	assert_eq(cascades, 1)


func test_layout_4_step_cap_seizes_the_node_a_threat_still_stands_on() -> void:
	var grid := GridFixture.chain_grid([&"s1"])
	var c := GridFixture.campaign(grid, {&"s1": &"safehouse"})
	var cfg := GridFixture.config_with_cap(2)
	var r := _resolve(c, grid, GridFixture.raid(&"g4", [&"enforcer"]), cfg)
	# Weakest-node routing camps on the Safehouse: 20-9 = 11 (step 1), 2 (step 2); cap.
	assert_eq(r.steps_run, 2)
	assert_eq(r.nodes["s1"]["outcome"], "seized")
	assert_eq(r.seized, ["s1"])
	assert_true(r.grid_after.is_seized(&"s1"))
	assert_eq(r.grid_after.node_type_of(&"s1"), &"", "the node is lost with the Site")
	assert_false(r.won)


func test_layout_5_six_enforcers_take_the_home_server_down() -> void:
	var grid := GridFixture.chain_grid([])
	var c := GridFixture.campaign(grid)
	var r := _resolve(c, grid, GridFixture.raid(&"g5", [&"enforcer", &"enforcer", &"enforcer", &"enforcer", &"enforcer", &"enforcer"]))
	assert_true(r.campaign_lost)
	assert_eq(r.home_after, 0)
	assert_eq(r.steps_run, 1, "all six reach home on step 1: 54 damage")


func test_disabled_node_hit_again_is_seized() -> void:
	var grid := GridFixture.chain_grid([&"r1"])
	var c := GridFixture.campaign(grid, {&"r1": &"relay"})
	c.grid.site(&"r1")["condition"] = GridState.Condition.DISABLED
	c.grid.site(&"r1")["integrity"] = 0
	var cfg := GridFixture.config_with_cap(1)
	var r := _resolve(c, grid, GridFixture.raid(&"g6", [&"auditor"]), cfg)
	# Auditor moves 2 edges: entry -> r1 (Disabled, no stop) -> home (stop). It never
	# ends a step on r1, so the Disabled node is not hit; a slower threat is.
	assert_eq(r.threats_reached_home, 1)
	var slow := _resolve(c, grid, GridFixture.raid(&"g7", [&"collector"]), cfg)
	assert_eq(slow.nodes["r1"]["outcome"], "seized", "a Collector ends step 1 on the Disabled Relay -> Seized")


func test_decoy_pulls_routing_toward_its_node() -> void:
	var grid := CityGridData.new()
	var sites: Array[SiteData] = [
		GridFixture.site(&"home", 1, [&"a", &"b"]),
		GridFixture.site(&"a", 1, [&"entry"]),
		GridFixture.site(&"b", 1, [&"entry"]),
		GridFixture.site(&"entry", 1, []),
	]
	grid.sites = sites
	grid.home_site_id = &"home"
	grid.boss_site_id = &"entry"
	var c := GridFixture.campaign(grid, {&"a": &"relay", &"b": &"relay"})
	GridFixture.deploy(c, &"b", &"decoy")
	var r := _resolve(c, grid, GridFixture.raid(&"g8", [&"collector"]))
	# The Collector camps on the Decoy node until it falls (15 -> 10 -> 5 -> Disabled),
	# then carries on to home. The other Relay is never touched.
	assert_eq(r.nodes["a"]["after"], 15, "a untouched")
	assert_eq(r.nodes["b"]["outcome"], "disabled", "the Collector went for the Decoy on b")
	assert_eq(r.home_after, 45)
	var first_move := {}
	for e in r.events:
		if e.get("type", "") == "move":
			first_move = e
			break
	assert_eq(first_move["to"], &"b")


func test_projection_equals_the_real_result_and_apply_writes_it() -> void:
	var grid := GridFixture.chain_grid([&"r1", &"r2"])
	var c := GridFixture.campaign(grid, {&"r1": &"firewall_relay", &"r2": &"relay"})
	GridFixture.deploy(c, &"r1", &"turret")
	var raid := GridFixture.raid(&"g9", [&"collector", &"auditor", &"enforcer"], 12)
	var projected := _resolve(c, grid, raid)
	var real := _resolve(c, grid, raid)
	assert_eq(projected.summary_hash(), real.summary_hash(), "same inputs, same outcome")
	assert_eq(projected.events.size(), real.events.size())
	var before_hash := c.state_hash()
	assert_eq(c.state_hash(), before_hash, "projection left the campaign untouched")
	var events := RaidResolver.apply(c, real, raid, _cfg)
	assert_eq(c.grid.home_integrity, real.home_after)
	for id in real.nodes:
		if id == "home":
			continue
		assert_eq(int(c.grid.site(StringName(id))["integrity"]), real.nodes[id]["after"], "%s integrity applied" % id)
	assert_eq(c.last_raid["raid_id"], "g9")
	if real.won:
		assert_eq(c.schematics, 112)
	else:
		assert_true(c.heat >= _cfg.lost_raid_heat, "lost raid adds Heat")


func test_raid_strength_scales_threats() -> void:
	var grid := GridFixture.chain_grid([&"r1"])
	var c := GridFixture.campaign(grid, {&"r1": &"relay"})
	var raid := GridFixture.raid(&"g10", [&"collector"])
	var strong := RaidResolver.resolve(c, grid, raid, _lookup, _cfg, [&"entry"], 100.0)
	assert_eq(strong.nodes["r1"]["after"], 5, "Collector damage doubled: 15 - 10")
