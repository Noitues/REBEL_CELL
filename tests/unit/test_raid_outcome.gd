extends GutTest
## RAID-RULES E (D27/D28): the verdict is CELL HOLDS or BREACHED; a clean defense gains Heat and Schematics,
## damage gains no Heat; the outcome projection equals
## what RaidResolver.apply does (preview == result), the severity tiers come from config, and
## IF PLACED speaks in words of effect.

var _cfg: CampaignConfigData
var _lookup: ContentLookup


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func _resolve(c: CampaignState, grid: CityGridData, raid: RaidData, cfg: CampaignConfigData = null) -> RaidResolver.RaidResult:
	return RaidResolver.resolve(c, grid, raid, _lookup, cfg if cfg != null else _cfg, [&"entry"])


## Layouts from test_raid_resolver: [name, middle sites, claims, assets {site: [ids]}, threats, reward].
func _layouts() -> Array:
	return [
		["undefended relay", [&"r1"], {&"r1": &"relay"}, {}, [&"collector"], 8],
		["ice lock and turret", [&"r1"], {&"r1": &"firewall_relay"}, {&"r1": [&"ice_lock", &"turret"]}, [&"collector"], 12],
		["enforcer on a relay", [&"r1"], {&"r1": &"relay"}, {}, [&"enforcer"], 8],
		["six enforcers", [], {}, {}, [&"enforcer", &"enforcer", &"enforcer", &"enforcer", &"enforcer", &"enforcer"], 8],
		["mixed", [&"r1", &"r2"], {&"r1": &"firewall_relay", &"r2": &"relay"}, {&"r1": [&"turret"]}, [&"collector", &"auditor", &"enforcer"], 12],
	]


func _build(layout: Array) -> Dictionary:
	var middle: Array[StringName] = []
	middle.assign(layout[1])
	var grid := GridFixture.chain_grid(middle)
	var c := GridFixture.campaign(grid, layout[2])
	for site in layout[3]:
		for a in layout[3][site]:
			GridFixture.deploy(c, site, a)
	return {"grid": grid, "campaign": c, "raid": GridFixture.raid(&"g_outcome", layout[4], int(layout[5]))}


func test_verdict_is_cell_holds_or_breached() -> void:
	assert_eq(RaidOutcome.verdict_of(false), RaidOutcome.Verdict.CELL_HOLDS)
	assert_eq(RaidOutcome.verdict_of(true), RaidOutcome.Verdict.BREACHED)
	assert_eq(RaidOutcome.Verdict.keys(), ["CELL_HOLDS", "BREACHED", "CITY_LOST"], "the verdicts: holds, breached, and CITY_LOST (R-E, 2026-10-25)")


func test_the_projection_equals_what_apply_does_for_every_layout() -> void:
	for layout in _layouts():
		var b := _build(layout)
		var c: CampaignState = b["campaign"]
		var r := _resolve(c, b["grid"], b["raid"])
		var p := RaidOutcome.project(r, _cfg)
		var heat_before := c.heat
		var sch_before := c.schematics
		var lost_before := c.raids_lost
		var won_before := c.raids_won
		RaidResolver.apply(c, r, b["raid"], _cfg)
		var tag := String(layout[0])
		assert_eq(c.heat - heat_before, p["heat_delta"], "%s: Heat delta" % tag)
		assert_eq(c.schematics - sch_before, p["schematics_delta"], "%s: Schematics delta" % tag)
		assert_eq(c.grid.home_integrity, p["home_after"], "%s: Home after" % tag)
		assert_eq(p["home_delta"], p["home_after"] - p["home_before"])
		assert_eq(p["threats_killed"], r.threats_destroyed)
		assert_eq(p["threats_total"], (layout[4] as Array).size(), "%s: every threat counted" % tag)
		match p["verdict"]:
			RaidOutcome.Verdict.CELL_HOLDS:
				assert_ne(c.outcome, CampaignState.Outcome.LOST)
				if p["clean"]:
					assert_eq(c.raids_won - won_before, 1, "%s: a clean defense is a raid won" % tag)
					assert_eq(p["schematics_delta"], int(layout[5]))
					assert_eq(p["heat_delta"], _cfg.clean_defense_heat, "%s: a clean defense gains Heat" % tag)
					assert_eq(p["home_delta"], 0)
					assert_eq(int(p["down"]) + int(p["taken"]), 0)
					assert_eq(p["tier"], RaidOutcome.Tier.CLEAN)
				else:
					assert_eq(c.raids_lost - lost_before, 1, "%s: damage is a raid lost" % tag)
					assert_eq(p["heat_delta"], 0, "%s: damage gains no Heat" % tag)
					assert_eq(p["schematics_delta"], 0)
					assert_ne(p["tier"], RaidOutcome.Tier.CLEAN, "%s: a damaged hold is never green" % tag)
			RaidOutcome.Verdict.BREACHED:
				assert_eq(c.outcome, CampaignState.Outcome.LOST, "%s: BREACHED loses the campaign" % tag)
		# The played raid's own dictionary tells the same outcome.
		var d := RaidOutcome.of_dict(c.last_raid, _cfg)
		assert_eq(d, p, "%s: the report reads the forecast" % tag)


func test_a_seeded_sweep_of_raids_projects_exactly() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 20261021
	var pool: Array[StringName] = [&"collector", &"auditor", &"enforcer"]
	var assets: Array[StringName] = [&"turret", &"ice_lock"]
	var checked := 0
	for i in 40:
		var threats: Array = []
		for k in rng.randi_range(1, 4):
			threats.append(pool[rng.randi() % pool.size()])
		var layout := ["sweep %d" % i, [&"r1", &"r2"], {&"r1": &"firewall_relay", &"r2": &"relay"}, {&"r1": [assets[rng.randi() % 2]], &"r2": [assets[rng.randi() % 2]]}, threats, rng.randi_range(1, 20)]
		var b := _build(layout)
		var c: CampaignState = b["campaign"]
		c.heat = rng.randi_range(0, 90)
		var r1 := _resolve(c, b["grid"], b["raid"])
		var r2 := _resolve(c, b["grid"], b["raid"])
		assert_eq(RaidOutcome.project(r1, _cfg), RaidOutcome.project(r2, _cfg), "sweep %d: seeded replay matches" % i)
		var p := RaidOutcome.project(r1, _cfg)
		var heat_before := c.heat
		var sch_before := c.schematics
		RaidResolver.apply(c, r1, b["raid"], _cfg)
		assert_eq(c.heat - heat_before, p["heat_delta"], "sweep %d: Heat" % i)
		assert_eq(c.schematics - sch_before, p["schematics_delta"], "sweep %d: Schematics" % i)
		checked += 1
	assert_eq(checked, 40)


func _clean_layout() -> Array:
	return ["clean", [&"r1"], {&"r1": &"relay"}, {&"r1": [&"ice_lock", &"turret", &"turret", &"turret"]}, [&"collector"], 8]


func test_clean_defense_gains_heat_and_schematics_damage_gains_no_heat() -> void:
	var clean := _build(_clean_layout())
	var c: CampaignState = clean["campaign"]
	var r := _resolve(c, clean["grid"], clean["raid"])
	var p := RaidOutcome.project(r, _cfg)
	assert_true(p["clean"], "turrets and a lock stop the collector without a scratch")
	assert_eq(p["heat_delta"], _cfg.clean_defense_heat)
	assert_eq(p["schematics_delta"], 8)
	assert_eq(p["verdict"], RaidOutcome.Verdict.CELL_HOLDS)
	assert_eq(p["tier"], RaidOutcome.Tier.CLEAN)
	var heat := c.heat
	RaidResolver.apply(c, r, clean["raid"], _cfg)
	assert_eq(c.heat - heat, _cfg.clean_defense_heat, "apply gains what the projection promised")
	assert_eq(c.raids_won, 1)
	# Damage: the undefended relay is hit; the Cell still holds, with no Heat and no Schematics.
	var hit := _build(_layouts()[0])
	var c2: CampaignState = hit["campaign"]
	var r2 := _resolve(c2, hit["grid"], hit["raid"])
	var p2 := RaidOutcome.project(r2, _cfg)
	assert_false(p2["clean"])
	assert_eq(p2["verdict"], RaidOutcome.Verdict.CELL_HOLDS)
	assert_eq(p2["heat_delta"], 0)
	assert_eq(p2["schematics_delta"], 0)
	var heat2 := c2.heat
	RaidResolver.apply(c2, r2, hit["raid"], _cfg)
	assert_eq(c2.heat, heat2, "damage gains no Heat")
	assert_eq(c2.raids_lost, 1)
	# BREACHED: Home at 0 loses the campaign, no Heat.
	var br := _build(_layouts()[3])
	var r3 := _resolve(br["campaign"], br["grid"], br["raid"])
	var p3 := RaidOutcome.project(r3, _cfg)
	assert_eq(p3["verdict"], RaidOutcome.Verdict.BREACHED)
	assert_eq(p3["heat_delta"], 0)
	assert_false(p3["clean"])


func test_per_node_outcome_data_is_exposed_sorted() -> void:
	var b := _build(_layouts()[2])
	var r := _resolve(b["campaign"], b["grid"], b["raid"])
	var nodes: Array = RaidOutcome.project(r, _cfg)["nodes"]
	assert_false(nodes.is_empty())
	var ids: Array = []
	for n in nodes:
		assert_true(["holds", "down", "taken", "passed"].has(n["outcome"]))
		assert_true(n.has("before") and n.has("after"))
		ids.append(String(n["id"]))
	var sorted := ids.duplicate()
	sorted.sort()
	assert_eq(ids, sorted, "ties by node id")
	assert_eq(RaidOutcome.of_dict(r.to_dict(), _cfg)["nodes"], nodes, "the report reads the forecast")


func test_heat_delta_is_clamped_at_the_ceiling() -> void:
	var b := _build(_clean_layout())
	var c: CampaignState = b["campaign"]
	c.heat = _cfg.heat_max - 2
	var r := _resolve(c, b["grid"], b["raid"])
	var p := RaidOutcome.project(r, _cfg)
	assert_eq(p["heat_delta"], 2, "only the Heat that fits is promised")
	var before := c.heat
	RaidResolver.apply(c, r, b["raid"], _cfg)
	assert_eq(c.heat - before, 2)


func test_severity_tiers_come_from_the_rules_and_the_config() -> void:
	var relay := _build(_layouts()[0])
	var r := _resolve(relay["campaign"], relay["grid"], relay["raid"])
	assert_eq(RaidOutcome.project(r, _cfg)["tier"], RaidOutcome.Tier.AMBER, "any Home loss is amber, never green")
	var down := _build(_layouts()[2])
	assert_eq(RaidOutcome.project(_resolve(down["campaign"], down["grid"], down["raid"]), _cfg)["tier"], RaidOutcome.Tier.DOWN)
	var breach := _build(_layouts()[3])
	assert_eq(RaidOutcome.project(_resolve(breach["campaign"], breach["grid"], breach["raid"]), _cfg)["tier"], RaidOutcome.Tier.TAKEN, "BREACHED is the red tier")
	var grid := GridFixture.chain_grid([&"s1"])
	var c := GridFixture.campaign(grid, {&"s1": &"safehouse"})
	var capped := RaidResolver.resolve(c, grid, GridFixture.raid(&"g4", [&"enforcer"]), _lookup, GridFixture.config_with_cap(2), [&"entry"])
	assert_eq(RaidOutcome.project(capped, _cfg)["tier"], RaidOutcome.Tier.TAKEN, "a TAKEN node is red")


func test_the_verdict_words_match_the_projection() -> void:
	for layout in _layouts():
		var b := _build(layout)
		var r := _resolve(b["campaign"], b["grid"], b["raid"])
		var p := RaidOutcome.project(r, _cfg)
		var words := RaidVerdict.of_projection(r)
		assert_eq(words, RaidVerdict.words(p["verdict"], p["heat_delta"], p["schematics_delta"], RaidVerdict.losses(r.to_dict())))
		RaidResolver.apply(b["campaign"], r, b["raid"], _cfg)
		assert_eq(RaidVerdict.of_result(b["campaign"].last_raid), words, "%s: the report says the forecast's words" % layout[0])
		match p["verdict"]:
			RaidOutcome.Verdict.CELL_HOLDS:
				assert_true(words.begins_with("CELL HOLDS"))
				if p["clean"]:
					assert_string_contains(words, "+%d HEAT" % p["heat_delta"])
				else:
					assert_string_contains(words, "NO HEAT")
					assert_false(words.contains("+"), "no gain on a damaged hold")
			RaidOutcome.Verdict.BREACHED:
				assert_eq(words, "BREACHED")


func test_if_placed_says_what_a_turret_kills() -> void:
	var base := ["x", [&"r1"], {&"r1": &"relay"}, {&"r1": [&"ice_lock"]}, [&"collector"], 8]
	var with := ["x", [&"r1"], {&"r1": &"relay"}, {&"r1": [&"ice_lock", &"turret", &"turret", &"turret"]}, [&"collector"], 8]
	var bn := _build(base)
	var bw := _build(with)
	var now := _resolve(bn["campaign"], bn["grid"], bn["raid"])
	var then := _resolve(bw["campaign"], bw["grid"], bw["raid"])
	var d := RaidOutcome.if_placed(now, then, &"r1", &"turret")
	if then.threats_destroyed > now.threats_destroyed:
		assert_true(d["changed"])
		assert_eq(d["kills"], then.threats_destroyed - now.threats_destroyed)
		assert_eq(d["total"], 1)
		var words := RaidVerdict.if_placed_words(d, func(o: String) -> String: return o.to_upper())
		assert_string_contains(words, "kills 1 of 1")
	else:
		fail_test("three turrets and an ICE lock must kill the collector the bare lock does not")


func test_if_placed_with_no_change_names_the_reason() -> void:
	var same := _build(_layouts()[0])
	var r := _resolve(same["campaign"], same["grid"], same["raid"])
	var word := func(o: String) -> String: return o.to_upper()
	# No shot and no threat passing the node: the wrong lane.
	var d := RaidOutcome.if_placed(r, r, &"far", &"turret")
	assert_false(d["changed"])
	assert_eq(d["reason"], RaidOutcome.REASON_WRONG_LANE)
	assert_eq(RaidVerdict.if_placed_words(d, word), "no change: no threat comes this way")
	# A threat passes the node but the asset never fires: out of reach.
	var passing := _resolve(same["campaign"], same["grid"], same["raid"])
	passing.events.append({"type": "move", "step": 1, "from": &"entry", "to": &"far"})
	d = RaidOutcome.if_placed(r, passing, &"far", &"turret")
	assert_eq(d["reason"], RaidOutcome.REASON_OUT_OF_REACH)
	assert_eq(RaidVerdict.if_placed_words(d, word), "no change: the threat is out of reach")
	# The asset fires and the threat survives: too strong.
	var firing := _resolve(same["campaign"], same["grid"], same["raid"])
	firing.events.append({"type": "shot", "step": 1, "site": &"far", "asset": &"turret"})
	d = RaidOutcome.if_placed(r, firing, &"far", &"turret")
	assert_eq(d["reason"], RaidOutcome.REASON_TOO_STRONG)
	assert_eq(RaidVerdict.if_placed_words(d, word), "no change: the threat is too strong")


func test_if_placed_names_the_node_and_home_change() -> void:
	var a := _resolve(_build(_layouts()[2])["campaign"], _build(_layouts()[2])["grid"], _build(_layouts()[2])["raid"])
	var b := _build(_layouts()[2])
	var after := _resolve(b["campaign"], b["grid"], b["raid"])
	after.nodes["r1"]["outcome"] = "holds"
	after.home_after = a.home_after + 9
	var d := RaidOutcome.if_placed(a, after, &"r1", &"turret")
	assert_true(d["changed"])
	var words := RaidVerdict.if_placed_words(d, func(o: String) -> String: return o.to_upper())
	assert_string_contains(words, "DOWN > HOLDS")
	assert_string_contains(words, "Home +9")


## RAID-VIS F3: the report's consequences: DOWN nodes with their repair cost (the node's share of its install
## cost, from content), TAKEN Sites, and the TAKEN Sites next to the territory (the new entry points).
func test_aftermath_lists_down_taken_and_new_entry_points() -> void:
	var middle: Array[StringName] = [&"r1", &"t1", &"x", &"t2"]
	var grid := GridFixture.chain_grid(middle)
	var c := GridFixture.campaign(grid, {&"r1": &"relay"})
	c.grid.site(&"r1")["condition"] = GridState.Condition.DOWN
	c.grid.site(&"t1")["status"] = GridState.SiteStatus.TAKEN
	c.grid.site(&"t2")["status"] = GridState.SiteStatus.TAKEN
	c.last_raid = {"nodes": {"home": {"before": 10, "after": 10, "outcome": "holds"}, "r1": {"before": 5, "after": 0, "outcome": "down"},
		"t1": {"before": 5, "after": 0, "outcome": "taken"}, "t2": {"before": 5, "after": 0, "outcome": "taken"}}}
	var a := RaidOutcome.aftermath(c, grid, _cfg, _lookup)
	var relay := ContentRegistry.get_content(&"relay") as NetworkNodeData
	assert_eq(a["down"].size(), 1, "one node DOWN")
	assert_eq(a["down"][0]["id"], &"r1")
	assert_eq(a["down"][0]["cost"], CampaignRules.repair_cost(c, _cfg, _lookup, &"r1"), "the repair cost is the rules' own")
	assert_eq(a["down"][0]["cost"], roundi(relay.install_cost * relay.repair_cost_ratio), "the node's share of its install cost")
	assert_eq(a["taken"], [&"t1", &"t2"] as Array[StringName], "both TAKEN Sites")
	assert_eq(a["entries"], [&"t1"] as Array[StringName], "only the TAKEN Site next to the territory is a new entry point")
	assert_true(RaidResolver.default_entry_sites(c, grid).has(&"t1"), "and the resolver enters from it next raid")
