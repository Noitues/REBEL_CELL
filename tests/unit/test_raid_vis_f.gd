extends GutTest
## RAID-VIS F (designer D26 / D28): the raid playout is a step-locked fight (one beat per step, the feed told when
## its beat has landed, the verdict hidden until the end, 20-40 s at 1x for a typical raid); each node shows its
## own outcome as grease pencil through one helper; the report lists the consequences (repair costs, TAKEN Sites,
## new entry points) with the rules' own numbers; the Site markers' orange rings mute under the raid lens.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Vector2(1280, 720)

var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _reduce: bool


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func before_each() -> void:
	_reduce = Settings.reduce_effects
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_raid_vis_f"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Motion.force_live = false
	Motion.set_speed(1.0)
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _fixture_raid(steps_chain: Array[StringName] = [&"c1", &"c2"]) -> RaidResolver.RaidResult:
	var grid := GridFixture.chain_grid(steps_chain)
	var claims := {}
	for id in steps_chain:
		claims[id] = &"relay"
	var c := GridFixture.campaign(grid, claims)
	var raid := GridFixture.raid(&"vis_f", [&"collector", &"enforcer"])
	return RaidResolver.resolve(c, grid, raid, _lookup, _cfg)


# --- F1: the step-locked playout --------------------------------------------------------------

func test_a_step_with_beats_takes_at_least_the_minimum_and_phases_rest_apart() -> void:
	var result := _fixture_raid()
	var least := RaidBeats.raw_seconds(RaidBeats.STEP_MIN_MOTION)
	assert_gt(least, 0.0, "the minimum step is in the motion table")
	var stepped := 0
	for g in RaidBeats.group(result.events):
		var tl := RaidBeats.timeline(g)
		if RaidBeats.is_step_group(g) and not (tl["beats"] as Array).is_empty():
			stepped += 1
			assert_gte(float(tl["seconds"]), least - 0.0001, "a step with beats takes its minimum")
		if RaidBeats.is_end_group(g):
			assert_false(RaidBeats.is_step_group(g), "the end is no step")
	assert_gt(stepped, 0, "the raid has steps")


func test_the_playout_length_counts_the_approach_and_the_settle() -> void:
	var result := _fixture_raid()
	var total := RaidBeats.playout_seconds(result.events)
	var steps := 0.0
	for g in RaidBeats.group(result.events):
		steps += float(RaidBeats.timeline(g)["seconds"])
	assert_almost_eq(total, steps + RaidBeats.raw_seconds(RaidBeats.APPROACH_MOTION) + RaidBeats.raw_seconds(RaidBeats.SETTLE_MOTION), 0.0001, "approach + every group + settle")
	assert_gt(total, 5.0, "even a short raid plays a few beats (approach, impact, settle)")


func test_a_long_raid_plays_between_20_and_40_seconds() -> void:
	var chain: Array[StringName] = [&"c1", &"c2", &"c3", &"c4", &"c5", &"c6", &"c7"]
	var result := _fixture_raid(chain)
	assert_gte(result.steps_run, 6, "a raid with several steps")
	var total := RaidBeats.playout_seconds(result.events)
	assert_gte(total, 20.0, "a typical raid plays at least 20 s at 1x (%.1f s)" % total)
	assert_lte(total, 40.0, "and at most 40 s (%.1f s)" % total)


func test_an_event_lands_when_its_beat_does() -> void:
	var result := _fixture_raid()
	for g in RaidBeats.group(result.events):
		var tl := RaidBeats.timeline(g)
		for b: Dictionary in tl["beats"]:
			var at := RaidBeats.landing_of(b["event"], tl)
			assert_gte(at, float(b["t0"]) - 0.0001, "%s lands no earlier than it starts" % b["type"])
			assert_lte(at, float(b["t0"]) + float(b["dur"]) + 0.0001, "and no later than it ends")
			if String(b["type"]) == "shot":
				assert_almost_eq(at, float(b["t0"]) + RaidBeats.raw_seconds(&"turret_trace"), 0.0001, "a shot lands as its trace arrives")
		for e: Dictionary in g:
			if not RaidBeats.is_beat(String(e.get("type", ""))):
				assert_gte(RaidBeats.landing_of(e, tl), 0.0, "a line without a beat comes at the group's end")


func _hq_raid() -> Control:
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 100
	var grid_data := RunManager.corporation.city_grid
	var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	c.armory = [&"turret"]
	CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
	return hq


func test_the_feed_is_told_as_beats_land_and_the_verdict_stays_hidden_until_the_end() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	var hq := _hq_raid()
	await _frames()
	var before := RunManager.campaign.duplicate_state()
	var events := RunManager.fight_raid()
	var resolved := RunManager.campaign.to_dict()
	hq.show_raid_playout(events, before)
	await _frames()
	var panel: RaidPlayoutPanel = hq.playout
	assert_not_null(panel)
	var forecast := hq.find_child("PlayoutForecast", true, false) as ForecastStamp
	assert_not_null(forecast)
	assert_false(forecast.resolved, "the stamp is not resolved while the raid plays")
	assert_eq(forecast.verdict, hq.PLAYING_WORD, "the verdict is hidden while it plays")
	assert_false(panel.is_done())
	# Told in the resolver's order, each only once its beat has landed (nothing is told ahead of the clock).
	var told: Array[Dictionary] = []
	panel.event_shown.connect(func(e: Dictionary) -> void: told.append(e))
	var guard := 0
	while not panel.is_done() and guard < 4000:
		guard += 1
		panel._process(0.1)
		assert_lte(told.size(), events.size(), "never more told than happened")
	assert_true(panel.is_done(), "the playout reaches its end")
	assert_eq(panel._pending.size(), 0, "every line was told")
	assert_eq(told.size(), events.size(), "every event was told once")
	assert_eq(RunManager.campaign.to_dict(), resolved, "playing the raid changed no game state")
	await _frames(2)
	assert_true(forecast.resolved, "the stamp resolves at the end")
	assert_eq(forecast.verdict, RaidVerdict.of_result(RunManager.campaign.last_raid), "into the raid's one verdict")


func test_a_node_keeps_its_integrity_until_the_hit_lands() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	var hq := _hq_raid()
	await _frames()
	var before := RunManager.campaign.duplicate_state()
	var events := RunManager.fight_raid()
	hq.show_raid_playout(events, before)
	await _frames()
	var fx: RaidFxLayer = hq.playout.fx
	assert_not_null(fx)
	var r := RunManager.campaign.last_raid
	var hit_nodes: Array[String] = []
	for id in r["nodes"]:
		if int(r["nodes"][id]["after"]) < int(r["nodes"][id]["before"]) and StringName(id) != RunManager.campaign.grid.home_site_id:
			hit_nodes.append(String(id))
	if hit_nodes.is_empty():
		pending("the demo raid hurts no node besides home")
		return
	var id: String = hit_nodes[0]
	# Run the panel until a hit on a node is scheduled: until its time the map shows the node whole.
	var guard := 0
	while fx._node_due.is_empty() and not hq.playout.is_done() and guard < 4000:
		guard += 1
		hq.playout._process(0.05)
	assert_false(fx._node_due.is_empty(), "a hit on a node was scheduled")
	var due: Dictionary = fx._node_due[0]
	var site: String = due["site"]
	if fx.clock < float(due["t0"]):
		assert_eq(int(fx._node_left[site]), int(r["nodes"][site]["before"]), "the node is whole before its hit lands")
	hq.playout.skip_to_end()
	assert_eq(int(fx._node_left[id]), int(r["nodes"][id]["after"]), "and ends on the resolved integrity")


# --- F2: per-node marks ------------------------------------------------------------------------

func test_the_one_helper_draws_a_mark_for_each_outcome() -> void:
	var c := Vector2(100, 100)
	var down := RaidNodeMarks.strokes(RaidNodeMarks.DOWN, c, 20.0)
	assert_eq(down.size(), 2, "DOWN: a cross-out is two strokes")
	var taken := RaidNodeMarks.strokes(RaidNodeMarks.TAKEN, c, 20.0)
	assert_eq(taken.size(), 3, "TAKEN: a ring, the flag's pole and its pennant")
	var holds := RaidNodeMarks.strokes(RaidNodeMarks.HOLDS, c, 20.0)
	assert_eq(holds.size(), 1, "HOLDS: one check")
	assert_eq(holds[0].size(), 3, "a check has three points")
	assert_true(RaidNodeMarks.strokes("passed", c, 20.0).is_empty(), "a passed node has no mark")
	assert_eq(RaidNodeMarks.ink_of(RaidNodeMarks.DOWN), GreasePencilMark.Ink.THREAT, "a loss is the threat's red")
	assert_eq(RaidNodeMarks.ink_of(RaidNodeMarks.HOLDS), GreasePencilMark.Ink.PLAN, "the check is the plan's yellow")
	var pool := PencilSet.new()
	add_child_autofree(pool)
	pool.begin()
	assert_not_null(RaidNodeMarks.draw(pool, "x", RaidNodeMarks.DOWN, c, 20.0))
	assert_null(RaidNodeMarks.draw(pool, "y", "passed", c, 20.0), "no mark, no stroke")
	pool.end()


func test_the_marks_come_from_the_outcomes_and_the_grid() -> void:
	var nodes := {"home": {"outcome": "holds"}, "a": {"outcome": "down"}, "b": {"outcome": "taken"}, "c": {"outcome": "holds"}, "d": {"outcome": "passed"}}
	var of_raid := RaidNodeMarks.of_raid(nodes, &"home")
	assert_eq(of_raid, {"a": "down", "b": "taken", "c": "holds"}, "home and a passed node have none")
	var grid := GridFixture.chain_grid([&"r1", &"t1"])
	var c := GridFixture.campaign(grid, {&"r1": &"relay"})
	c.grid.site(&"r1")["condition"] = GridState.Condition.DOWN
	c.grid.site(&"t1")["status"] = GridState.SiteStatus.TAKEN
	var of_grid := RaidNodeMarks.of_grid(c.grid)
	assert_eq(of_grid, {"r1": "down", "t1": "taken"}, "the HQ shows the standing losses")
	c.grid.site(&"r1")["condition"] = GridState.Condition.OK
	assert_false(RaidNodeMarks.of_grid(c.grid).has("r1"), "repaired, the mark is gone")


# --- F3: consequences --------------------------------------------------------------------------

func test_every_taken_site_next_to_the_territory_is_an_entry_point() -> void:
	var middle: Array[StringName] = [&"r1", &"t1", &"x", &"t2"]
	var grid := GridFixture.chain_grid(middle)
	var c := GridFixture.campaign(grid, {&"r1": &"relay"})
	c.grid.site(&"t1")["status"] = GridState.SiteStatus.TAKEN
	c.grid.site(&"t2")["status"] = GridState.SiteStatus.TAKEN
	assert_eq(RaidOutcome.entry_points(c.grid, grid), [&"t1"] as Array[StringName], "only the one beside the territory")
	assert_eq(RaidOutcome.entry_points(c.grid, grid, [&"t2"]), [] as Array[StringName], "limited to the ones named")


func test_the_report_lists_repair_costs_and_the_new_entry_point() -> void:
	var hq := _hq_raid()
	await _frames()
	var c := RunManager.campaign
	var grid_data := RunManager.corporation.city_grid
	var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
	c.grid.site(first)["condition"] = GridState.Condition.DOWN
	# A TAKEN Site beside the territory.
	var taken_id := &""
	for n in c.grid.neighbors(first, grid_data):
		if c.grid.is_corporate(n):
			taken_id = n
			break
	assert_ne(taken_id, &"", "the first Site has a corporate neighbour")
	c.grid.site(taken_id)["status"] = GridState.SiteStatus.TAKEN
	c.last_raid = {"raid_id": "test", "steps_run": 3, "won": false, "campaign_lost": false, "home_before": 50, "home_after": 50,
		"threats_destroyed": 0, "threats_reached_home": 0, "nodes": {String(first): {"before": 30, "after": 0, "outcome": "down"},
		String(taken_id): {"before": 10, "after": 0, "outcome": "taken"}}, "down": [String(first)], "taken": [String(taken_id)]}
	hq.show_raid_summary()
	await _frames(2)
	var cost := CampaignRules.repair_cost(c, RunManager.config(), RunManager.lookup(), first)
	assert_gt(cost, 0, "the repair costs something")
	var down := hq._panel.find_child("ReportDown", true, false) as Label
	assert_not_null(down, "the DOWN node is listed")
	assert_string_contains(down.text, str(cost), "with its repair cost")
	var taken := hq._panel.find_child("ReportReclaimed", true, false) as Label
	assert_not_null(taken, "the TAKEN Site is listed")
	var entries := hq._panel.find_child("ReportEntries", true, false) as Label
	assert_not_null(entries, "and the new raid entry point")
	assert_string_contains(entries.text, hq.site_name(taken_id).to_upper())
	assert_not_null(hq._node_marks, "the report's map carries the per-node marks")
	assert_eq(hq._node_marks.marks.get(String(first)), "down", "DOWN on the map")
	assert_eq(hq._node_marks.marks.get(String(taken_id)), "taken", "TAKEN on the map")
	assert_true(hq._node_marks.entries.has(taken_id), "and the entry point is written on it")


func test_the_hq_marks_a_standing_loss_until_it_is_repaired() -> void:
	var hq := _hq_raid()
	await _frames()
	var c := RunManager.campaign
	var grid_data := RunManager.corporation.city_grid
	var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
	c.grid.site(first)["condition"] = GridState.Condition.DOWN
	hq.show_hq()
	await _frames(3)
	assert_not_null(hq._node_marks, "the HQ map has the layer")
	assert_eq(hq._node_marks.marks.get(String(first)), "down", "the DOWN node is crossed out at the HQ")
	c.grid.site(first)["condition"] = GridState.Condition.OK
	hq.show_hq()
	await _frames(3)
	assert_false(hq._node_marks.marks.has(String(first)), "repaired: the mark is gone")


# --- F4: the lens rings ------------------------------------------------------------------------

func test_the_lens_mutes_the_availability_ring_to_a_thin_translucent_outline() -> void:
	assert_almost_eq(SiteMarker.LENS_RING_ALPHA, 0.3, 0.0001, "about 30 % alpha")
	assert_lt(SiteMarker.LENS_RING_W, 1.0, "thinner than the full ring")
	var view := SiteMarkerView.new({"avail": SiteMarker.AV_NEXT, "status": SiteMarker.ST_CORPORATE, "kind": ""})
	add_child_autofree(view)
	assert_false(view.lens, "off by default")
	view.lens = true
	assert_true(view.lens)
	view.lens = false
	assert_false(view.lens, "restored when the lens is off")
