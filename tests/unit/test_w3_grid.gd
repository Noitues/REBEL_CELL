extends GutTest
## Plan 1 wave 3, W3-GRID: the reachable flag is the launch rule's (C4), the Heat forecast is the
## Heat after the action (C3), Heat Scrub's reason is the rule's (C3), GRID VIEW draws the active
## run's path (R6 / C10).


func after_each() -> void:
	RunManager.reset()


## Plays `steps` runs in a row (the first launchable Site each time, completed as the rules do).
func _advance(steps: int) -> void:
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	for i in steps:
		var open := CampaignRules.launchable_sites(c, corp, cfg)
		if open.is_empty():
			return
		var run := RunState.new()
		run.site_id = open[0].id
		run.kind = CampaignRules.run_kind_for(c, open[0])
		CampaignRules.on_run_completed(c, corp, cfg, run, RunManager.lookup())


func test_reachable_flag_equals_the_launch_rule_for_seeded_campaigns() -> void:
	for seed_value in [1, 7, 42]:
		RunManager.new_campaign(seed_value)
		for step in 4:
			var c := RunManager.campaign
			var corp := RunManager.corporation
			var cfg := RunManager.config()
			var open := {}
			for s in CampaignRules.launchable_sites(c, corp, cfg):
				open[s.id] = true
			for s in corp.city_grid.sites:
				if s == null or s.id == c.grid.home_site_id:
					continue
				var a := GridAccess.site_access(c, corp, cfg, s)
				var want: bool = open.has(s.id) or CampaignRules.is_patrol(c, s)
				assert_eq(bool(a["reachable"]), want, "seed %d step %d %s" % [seed_value, step, s.id])
				if not want and a["why"] == GridAccess.WHY_FROM:
					assert_false((a["prereqs"] as Array).is_empty(), "%s names what to clear first" % s.id)
			_advance(1)


func test_a_locked_site_names_its_linked_sites() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var found := false
	for s in corp.city_grid.sites:
		if s == null:
			continue
		var a := GridAccess.site_access(c, corp, cfg, s)
		if String(a["why"]) == GridAccess.WHY_FROM:
			found = true
			for p in a["prereqs"]:
				var other := CampaignRules.site_data(corp, p)
				assert_true(other.links.has(s.id) or s.links.has(other.id) or other.locked_links.has(s.id), "%s is linked to %s" % [p, s.id])
	assert_true(found, "a fresh Grid has locked Sites")


func test_heat_forecast_equals_the_heat_after_the_action() -> void:
	RunManager.new_campaign(3)
	var c := RunManager.campaign
	var cfg := RunManager.config()
	for start in [0, 9, 22, 48, 73]:
		for delta in [5, 11, 12, -10]:
			var probe := c.duplicate_state()
			probe.heat = start
			var f := HeatRules.forecast(probe, delta, cfg)
			assert_eq(probe.heat, start, "the forecast does not change the campaign")
			var real := probe.duplicate_state()
			var events := HeatRules.add_heat(real, delta, cfg, "real")
			assert_eq(int(f["after"]), real.heat, "heat %d %+d: after" % [start, delta])
			assert_eq(int(f["delta"]), real.heat - start, "heat %d %+d: delta" % [start, delta])
			var raid := false
			for e in events:
				if String(e.get("type", "")) == "raid_pending":
					raid = true
			assert_eq(bool(f["raid"]), raid, "heat %d %+d: the raid warning is the real raid" % [start, delta])


func test_the_flatline_forecast_is_the_deaths_heat() -> void:
	RunManager.new_campaign(5)
	var c := RunManager.campaign
	var cfg := RunManager.config()
	for tier in [1, 2, 3]:
		var f := HeatRules.forecast(c, HeatRules.death_heat(c, cfg, tier), cfg)
		var real := c.duplicate_state()
		HeatRules.add_heat(real, HeatRules.death_heat(c, cfg, tier), cfg, "operative death")
		assert_eq(int(f["after"]), real.heat)
		assert_gt(HeatRules.death_heat(c, cfg, tier), 0)


func test_the_clear_preview_names_the_thresholds_it_crosses() -> void:
	RunManager.new_campaign(2)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var site: SiteData = CampaignRules.launchable_sites(c, corp, cfg)[0]
	c.heat = 0
	var calm := CampaignRules.clear_preview(c, corp, cfg, site, RunManager.lookup())
	assert_true((calm["crosses"] as Array).is_empty() or int(calm["heat"]) >= cfg.heat_thresholds[0].heat)
	c.heat = 99
	var hot := CampaignRules.clear_preview(c, corp, cfg, site, RunManager.lookup())
	var copy := c.duplicate_state()
	var run := RunState.new()
	run.site_id = site.id
	run.kind = CampaignRules.run_kind_for(c, site)
	CampaignRules.on_run_completed(copy, corp, cfg, run, RunManager.lookup())
	assert_eq(int(hot["heat"]), copy.heat - c.heat, "the previewed Heat is the real Heat change")
	for t in hot["crosses"]:
		assert_true(copy.thresholds_fired.has(t))


func test_heat_scrub_says_why_it_is_unavailable() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var cfg := RunManager.config()
	c.heat = 0
	c.schematics = 1000
	assert_ne(CampaignRules.scrub_error(c, cfg), "", "no Heat, nothing to scrub")
	c.heat = 30
	c.schematics = 0
	assert_true(CampaignRules.scrub_error(c, cfg).begins_with("Not enough Schematics"))
	c.schematics = CampaignRules.heat_purchase_price(c, cfg)
	assert_eq(CampaignRules.scrub_error(c, cfg), "", "available exactly when the purchase would go through")
	var before := c.heat
	CampaignRules.buy_heat_reduction(c, cfg)
	assert_lt(c.heat, before)


func test_grid_view_draws_the_active_run_path() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var site: SiteData = CampaignRules.launchable_sites(c, corp, cfg)[0]
	var from_id := RouteLinkLayout.from_site(corp, c, site.id)
	var g := CityLayout.grid_graph(c, corp, [] as Array[Array], site.id, true, cfg)
	var edges_before: int = (g["edges"] as Array).size()
	g = CityLayout.with_run_path(g, from_id, site.id)
	var targets := 0
	for n: Dictionary in g["nodes"]:
		if bool(n.get("run_target", false)):
			targets += 1
			assert_eq(n["id"], site.id)
	assert_eq(targets, 1, "the target is flagged once")
	var paths := 0
	for e: Dictionary in g["edges"]:
		if bool(e.get("run_path", false)):
			paths += 1
			assert_eq(e["b"], site.id)
	assert_eq(paths, 1 if from_id != &"" else 0)
	assert_eq((g["edges"] as Array).size(), edges_before + paths)
	# no next-node choices on the drawn Grid
	for n: Dictionary in g["nodes"]:
		assert_false(n.has("next"), "GRID VIEW marks no next node")


# --- The HQ page (one flow test) ----------------------------------------------------------------

const HQ := "res://scenes/hq/hq_scene.tscn"


func test_hq_locked_site_says_why_rings_its_prerequisite_and_drops_the_stamp() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await get_tree().process_frame
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var locked: SiteData = null
	for s in corp.city_grid.sites:
		if s != null and String(GridAccess.site_access(c, corp, cfg, s)["why"]) == GridAccess.WHY_FROM:
			locked = s
			break
	assert_not_null(locked, "a fresh Grid has a locked Site")
	assert_ne(hq.lock_line(locked), "", "it carries a lock reason")
	assert_false(hq.prereqs_of(locked.id).is_empty(), "and names what to clear first")
	hq.select_site(locked.id)
	await get_tree().process_frame
	await get_tree().process_frame
	assert_eq(hq.city_overlay.prereq_ids, hq.prereqs_of(locked.id), "the prerequisites are ringed on the map")
	var card := hq.find_child("SelectedSite", true, false) as SiteHoloCard
	assert_not_null(card)
	if card != null:
		assert_false(card.holo.stamp_slot.visible, "no DECRYPTED on a Site that is not reachable yet")
	var open: SiteData = CampaignRules.launchable_sites(c, corp, cfg)[0]
	hq.select_site(open.id)
	await get_tree().process_frame
	await get_tree().process_frame
	card = hq.find_child("SelectedSite", true, false) as SiteHoloCard
	if card != null:
		assert_true(card.holo.stamp_slot.visible, "a reachable Site keeps its stamp")
		assert_not_null(card.find_child("FlatlineRow", true, false), "and shows the flatline Heat before acting")
	assert_true(hq.city_overlay.prereq_ids.is_empty())
