extends GutTest
## B3 (M14 art-direction integration review: raid, map and route, the clutter rule). Review
## `INTEGRATION_REVIEW/REVIEW.md` D5, D6, D14, sections c / d / f and the designer's rulings (Q4,
## Q5, Q6, Q7, Q9, Q10, Q15); round 44 `A_map/route_page*.png`, `raid_setup.png`. Views never
## change state. Headless (the frames are checked windowed: DECISIONS "B3").

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
## The layout is 720p; the art's numbers are at 1080p.
const TO_1080 := 1.5
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const CORPORATIONS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]

var _scale: float
var _all_nodes: bool


func before_each() -> void:
	_scale = Settings.text_scale
	_all_nodes = Settings.always_show_all_nodes
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_b3_raid_map_route"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	Motion.force_live = false
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.always_show_all_nodes != _all_nodes:
		Settings.set_always_show_all_nodes(_all_nodes)
	Fx._set_jacking(false)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _unlock_all() -> void:
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10


func _netrun(corp: StringName = &"solace") -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_unlock_all()
	RunManager.new_campaign(1, corp)
	scene.start_run(1)
	return scene


## A campaign with two claimed nodes, three defence cards and a raid pending (as test_hq_b_defence).
func _raid_campaign() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = 400
	for t: StringName in [&"firewall_relay", &"safehouse"]:
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, t)
	c.armory = [&"turret", &"ice_lock", &"honeypot_node"]
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")


func _hq() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(4)
	return scene


# --- The clutter rule (D5, section d) --------------------------------------------------------------

func test_the_clutter_rule_tags_only_the_selected_lit_or_plan_node() -> void:
	var ov := CityMapOverlay.new()
	add_child_autofree(ov)
	var nodes: Array[Dictionary] = []
	for i in 4:
		nodes.append({"id": StringName("n%d" % i), "at": Vector2(10 + i * 4, 12), "label": "Node %d" % i, "result": "20 > 15 HOLDS"})
	nodes[3]["plan"] = true
	ov.set_graph(nodes, [] as Array[Dictionary])
	ov.selected_id = &"n1"
	# ALL (the old maps): every node with words, with its raid result.
	assert_eq(ov.label_lines(&"n0").size(), 2)
	# FOCUS (the HQ Grid): the selected node, the lit one and a plan node; never the result line.
	ov.tag_rule = CityMapOverlay.TagRule.FOCUS
	assert_true(ov.label_lines(&"n0").is_empty(), "an unselected, unlit node has no tag")
	assert_eq(Array(ov.label_lines(&"n1")), ["Node 1"], "the selected node's name, no HOLDS tag")
	assert_eq(Array(ov.label_lines(&"n3")), ["Node 3"], "a plan-relevant node")
	ov.hover_id = &"n2"
	assert_eq(Array(ov.label_lines(&"n2")), ["Node 2"], "the lit node (a list row, the pad)")
	# LIT (the raid maps): not even the selected node.
	ov.hover_id = &""
	ov.tag_rule = CityMapOverlay.TagRule.LIT
	assert_true(ov.label_lines(&"n1").is_empty(), "the raid map tags no node (status on the node)")
	assert_false(ov.label_lines(&"n3").is_empty(), "a plan node still")
	assert_string_contains(ov.tip_of(&"n0"), "Node 0", "the name is the hover tooltip")


func test_the_raid_setup_map_has_no_node_tags_and_no_resource_bar() -> void:
	_raid_campaign()
	var hq := await _hq()
	hq.show_raid()
	await _frames(6)
	var ov: CityMapOverlay = hq.city_overlay
	assert_eq(ov.tag_rule, CityMapOverlay.TagRule.LIT)
	for id in ov.tagged_ids():
		assert_true(id == ov.hover_id or bool(ov._node_dict(id).get("plan", false)), "%s: no tag on an unlit node" % id)
	for n in ov.nodes:
		assert_false(ov.label_lines(n["id"]).has(String(n.get("result", "#"))), "%s: no HOLDS tag" % n["id"])
	# Threat tags only on the lit node.
	var home := RunManager.campaign.grid.home_site_id
	ov.threat_markers = {home: ["Collector"]}
	await _frames(2)
	for key in ov.label_rects():
		assert_false(String(key).ends_with("#threats"), "no threat tag on an unlit node")
	ov.hover_id = home
	await _frames(2)
	assert_true(ov.label_rects().has("%s#threats" % home), "the lit node names its threats")
	ov.hover_id = &""
	# Q10: the yellow RAID SETUP title; round 44: no resource bar (YOUR NETWORK is the Cell's state).
	assert_eq(String(hq.hud._title), tr("RAID SETUP"))
	assert_true(hq.hud.stats.items.is_empty(), "no resource tags on the raid setup")
	assert_false(hq.hud.heat_gauge.visible, "no Heat gauge (Heat settles on the report)")
	# Back at the HQ the bar returns.
	hq.show_hq()
	await _frames(3)
	assert_false(hq.hud.stats.items.is_empty(), "the HQ keeps its bar")



# --- The route (D14, Q4, Q15, bible 4.6 round 44) ---------------------------------------------------

func test_route_links_are_only_the_ones_the_route_uses_until_the_strip_is_hovered() -> void:
	Settings.set_always_show_all_nodes(false)
	var scene := _netrun()
	await _frames(4)
	var ov := scene.city_overlay as RouteOverlay
	var used := 0
	var other := 0
	for e in ov.edges:
		if ov.route_uses(e):
			used += 1
			assert_gt(ov.edge_shown(e), 0.0, "a link the route uses is drawn")
		else:
			other += 1
			assert_eq(ov.edge_shown(e), 0.0, "a link the route does not use is not drawn")
			assert_eq(ov.link_hint(e), 0.0, "nor its hairline before the hover")
	assert_gt(other, 0, "the run has links the route does not use yet")
	scene.route_legend.show_links_hovered.emit(true)
	ov.links_t = 1.0
	for e in ov.edges:
		if not ov.route_uses(e):
			assert_eq(ov.link_hint(e), 1.0, "the hover shows every run link as a hairline")
	assert_almost_eq(RouteOverlay.LINK_HINT_ALPHA, 0.25, 0.001, "25 % white")
	scene.route_legend.show_links_hovered.emit(false)
	for e in ov.edges:
		assert_eq(ov.link_hint(e), 0.0, "and they go again")


## B3 b (art director, round 44 `route_page.png`): the route frames the walked path, the options
## and one layer ahead at ortho 130-190 (at a run's start and mid-run, 1.0 / 1.6 / 2.0); the
## TARGET need not be in frame: off frame it has the red pencil edge arrow.
func test_route_frames_the_options_at_the_round_44_zoom_with_the_target_arrow() -> void:
	var cfg: CityConfig = CityView3D.CONFIG
	assert_almost_eq(cfg.route_ortho_near, 130.0, 0.001)
	assert_almost_eq(cfg.route_ortho_far, 190.0, 0.001)
	for corp in CORPORATIONS:
		for mid in [false, true]:
			for scale in [1.0, 1.6, 2.0]:
				Settings.set_text_scale(scale)
				RunManager.reset()
				var scene := _netrun(corp)
				await _frames(8)
				if mid:
					var s := RunManager.netrun
					var first: StringName = s.available_nodes()[0]
					s.run.current_node_id = first
					s.run.visited.append(first)
					scene._show_map()
					await _frames(8)
				var tag := "%s %s x%.1f" % [corp, "mid-run" if mid else "start", scale]
				var ov := scene.city_overlay as RouteOverlay
				var ortho: float = scene.route_ortho()
				gut.p("%s: route ortho %.0f" % [tag, ortho])
				assert_gte(ortho, cfg.route_ortho_near - 1.0, "%s: never closer than 130 (%.0f)" % [tag, ortho])
				assert_lte(ortho, cfg.route_ortho_far + 1.0, "%s: never further than 190 (%.0f)" % [tag, ortho])
				var free: Rect2 = scene.route_free_area()
				assert_true(scene.route_frames(free), "%s: where the player is and the options are in frame" % tag)
				# The TARGET: in frame, or the edge arrow shows (with the TARGET word).
				var target: Dictionary = {}
				for n in ov.nodes:
					if bool(n.get("target", false)):
						target = n
				assert_false(target.is_empty(), "%s: the run has its TARGET" % tag)
				var arrow: TargetEdgeMarker = scene.route_target
				assert_not_null(arrow, "%s: the edge arrow is on the page" % tag)
				arrow.refresh()
				# B3 c: "in frame" is the whole TARGET (its circle) inside the area and clear of the top
				# bar; while the arrow shows the TARGET's own circle hides.
				var at := ov.get_global_transform_with_canvas() * ov.icon_pos(target)
				var reach: float = ov.target_reach(target) * ov.get_global_transform_with_canvas().get_scale().x
				var area := (arrow.get_parent() as Control).get_global_rect()
				var whole := Rect2(at - Vector2(reach, reach), Vector2(reach, reach) * 2.0)
				var in_frame: bool = area.encloses(whole) and not (scene.hud as Control).get_global_rect().intersects(whole)
				assert_eq(arrow.showing(), not in_frame, "%s: the arrow shows exactly when the TARGET is (partly) off frame" % tag)
				assert_eq(ov.target_off, arrow.showing(), "%s: the TARGET's circle hides while its arrow shows" % tag)
				if ov.target_off:
					assert_false(ov.target_drawn(), "%s: and its sticker" % tag)
				if arrow.showing():
					var tip: Vector2 = arrow.get_global_transform() * arrow.tip()
					assert_false(scene.hud.get_global_rect().has_point(tip), "%s: the arrow keeps off the top bar" % tag)
				# Node stickers at least 44 px at 1080p (their die-cut).
				var k := ov.get_global_transform_with_canvas().get_scale().x
				var r := ov.icon_radius(ov.nodes[0]) * k
				var die := (r - (RouteOverlay.RING_WIDTH + RouteOverlay.RING_GAP) * k) * 2.0
				assert_gte(die * TO_1080, 44.0, "%s: a node sticker is %.0f px at 1080p" % [tag, die * TO_1080])
				Settings.set_text_scale(1.0)
				scene.get_parent().queue_free()
				await _frames(1)


func test_the_edge_arrow_finds_the_route_target() -> void:
	var ov := CityMapOverlay.new()
	add_child_autofree(ov)
	var nodes: Array[Dictionary] = [{"id": &"a", "at": Vector2(1, 1)}, {"id": &"t", "at": Vector2(3, 3), "target": true}]
	ov.set_graph(nodes, [] as Array[Dictionary])
	var m := TargetEdgeMarker.make(ov)
	add_child_autofree(m)
	assert_true(TargetEdgeMarker.edge_point(Rect2(0, 0, 100, 100), Vector2(300, 50), 10.0)["inside"] == false)
	assert_false(m.showing(), "nothing before a frame")


func test_the_route_window_keeps_grid_view_and_save_and_quit_only() -> void:
	var scene := _netrun()
	await _frames(4)
	var row := scene._panel.find_child("RouteNodes", true, false) as Control
	var win := row.get_parent()
	while win != null and not (win is TerminalWindow):
		win = win.get_parent()
	assert_not_null(win)
	var shown: Array[String] = []
	for b in (win as Control).find_children("*", "Button", true, false):
		var btn := b as Button
		if btn.is_visible_in_tree() and not btn.top_level:
			shown.append(btn.name)
	shown.sort()
	assert_eq(shown, ["GridZoom", "SaveQuit"] as Array[String], "GRID VIEW and Save & quit only")
	# Round 44's top strip: Heat (the gauge), HP and Cycles.
	assert_true(scene.route_strip_only(RunManager.netrun))
	var marks: Array[String] = []
	for it: Array in scene.hud.stats.items:
		marks.append(String(it[0]))
	assert_eq(marks, [TextDb.mark("HP"), TextDb.mark("CYCLES")] as Array[String])
	assert_true(scene.hud.heat_gauge.visible, "Heat is the strip's gauge")


# --- The raid (D6, Q5, Q6, Q7, the legend, the interlude) -------------------------------------------

func test_the_raid_draws_no_influence_fill_and_no_verdict_over_the_map() -> void:
	assert_false(RaidFxLayer.FX_MOTION.has("tint"), "D6: no district tint")
	var fx := RaidFxLayer.new()
	assert_false(fx.has_method("_draw_tints"), "D6: no influence wash drawn")
	fx.free()
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/raid_fx_layer.gd")
	assert_false(src.contains("\"banner_%d\""), "Q7: home's verdict is no pencil banner over the map")


func test_cell_holds_is_a_sticker_on_the_after_action_paper_with_the_result_motion() -> void:
	_raid_campaign()
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	hq.fight_raid()
	await _frames(2)
	hq.show_raid_summary()
	await _frames(4)
	var holds := hq._panel.find_child("CellHolds", true, false) as RaidSticker
	if holds == null:
		pass_test("the raid was lost: no CELL HOLDS")
		return
	var paper := hq._panel.find_child("RaidReport", true, false) as Control
	assert_true(paper.get_global_rect().has_point(holds.get_global_rect().get_center()), "on the paper")
	assert_eq(holds.scale, Vector2.ONE, "at rest headless (the result motion's end state)")
	assert_eq(RaidSticker.RESULT_MOTION, &"raid_result_banner", "the banner's motion moved onto the sticker")
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/raid_sticker.gd")
	assert_string_contains(src, "Motion.run(RESULT_MOTION", "the sticker plays the result motion")
	# The report's map: no node tags; the key is the strip.
	assert_eq(hq.city_overlay.tag_rule, CityMapOverlay.TagRule.LIT)
	var legend := hq._panel.find_child("MapLegend", true, false) as MapLegend
	assert_true(legend.strip, "the key strip")


func test_the_raid_legend_is_the_folded_key_strip_at_every_text_size() -> void:
	_raid_campaign()
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var hq := await _hq()
		hq.show_raid()
		await _frames(2)
		hq.fight_raid()
		await _frames(2)
		hq.show_raid_summary()
		await _frames(3)
		var legend := hq._panel.find_child("MapLegend", true, false) as MapLegend
		assert_true(legend.strip, "x%.1f: a strip" % scale)
		assert_true(legend.is_folded(), "x%.1f: folded to its MAP KEY line" % scale)
		assert_eq(hq.raid_legend, legend, "x%.1f: [K] opens it" % scale)
		legend.set_opened(true, true)
		assert_false(legend.is_folded(), "x%.1f: opens on hover" % scale)
		legend.set_opened(false)
		hq.get_parent().queue_free()
		await _frames(1)


func test_defence_cards_are_the_concept_size_at_1080p_and_the_honeypot_is_the_decoy_violet() -> void:
	_raid_campaign()
	var hq := await _hq()
	hq.show_raid()
	await _frames(4)
	var cards := hq._panel.find_child("AssetCards", true, false) as Control
	var seen := 0
	for k in cards.get_children():
		if not k is AssetCard:
			continue
		var card := k as AssetCard
		var r := card.card_rect()
		var s := card.get_global_transform_with_canvas().get_scale()
		assert_gte(r.size.x * s.x * TO_1080, 156.0, "%s: about 158 px wide at 1080p" % card.asset_id)
		assert_gte(r.size.y * s.y * TO_1080, 177.0, "%s: about 180 px tall at 1080p" % card.asset_id)
		var lay: Dictionary = card._layout()
		for key in ["name", "num", "rule"]:
			assert_gte(int(lay[key]) * TO_1080, 12.0, "%s: %s text at the 12 px floor at 1080p" % [card.asset_id, key])
		seen += 1
	assert_eq(seen, 3)
	# Q5: the honeypot is the atlas's hook in the decoy violet #B08CFF (log: the glyph slice).
	var m: Dictionary = AssetCard.manifest()["cards"]["honeypot_node"]
	assert_eq(String(m["glyph"]), "placeholder_phishing")
	assert_eq(AssetCard.color_of(&"honeypot_node").to_html(false), "b08cff")
	assert_eq(AssetIcon.color_of(&"honeypot_node").to_html(false), "b08cff")


## B3 b (art director): no instruction panel over the work order; the paper takes the left
## column; YOUR NETWORK shows (collapsed to its header and CORE when short) and is never below the
## fold; the RAID SETUP title is a page title sticker (about 220 px wide, 48 px cap at 1080p).
func test_raid_setup_paper_whole_network_visible_and_a_page_title() -> void:
	_raid_campaign()
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var hq := await _hq()
		hq.show_raid()
		await _frames(8)
		var page: Control = hq._panel
		var tag := "x%.1f" % scale
		assert_null(page.find_child("RaidIntro", true, false), "%s: no instruction panel" % tag)
		var order := page.get_node("WorkOrder") as Control
		var paper := page.find_child("RaidCard", true, false) as Control
		assert_true(order.is_ancestor_of(paper), "%s: the work order holds the left column" % tag)
		for k in order.get_children():
			if k is Control and (k as Control).visible and not (k as Control).is_ancestor_of(paper) and k != paper:
				assert_true((k as Control).get_global_rect().position.y >= paper.get_global_rect().end.y - 1.0 or not (k as Control).get_global_rect().intersects(paper.get_global_rect()),
					"%s: nothing over the paper (%s)" % [tag, k.name])
		var column := page.get_node("CardColumn") as Control
		var network := page.find_child("NodeOrders", true, false) as Control
		var core := network.find_child("Order_%s" % RunManager.campaign.grid.home_site_id, true, false) as Control
		assert_not_null(core, "%s: the CORE row" % tag)
		var shown := column.get_global_rect().grow(1.0)
		assert_true(shown.encloses(core.get_global_rect()), "%s: YOUR NETWORK's CORE row is in view, not below the fold (%s in %s)" % [tag, core.get_global_rect(), shown])
		var run := page.find_child("RunRaid", true, false) as Control
		assert_lte(minf(core.get_global_rect().end.y, shown.end.y), run.get_global_rect().position.y + 0.5, "%s: the CORE row is clear of START DEFENSE" % tag)
		var head := network.get_global_rect().position.y
		assert_true(shown.has_point(Vector2(network.get_global_rect().get_center().x, head + 2.0)), "%s: its header is in view" % tag)
		assert_eq((network as RaidTerminal).tag_label.text, tr("%d NODES") % RunManager.campaign.grid.claimed_ids().size(), "%s: the header counts the nodes" % tag)
		gut.p("%s: YOUR NETWORK collapsed %s" % [tag, hq.network_collapsed()])
		if scale <= 1.6:
			var intel := page.find_child("ThreatIntel", true, false) as Control
			assert_true(shown.encloses(intel.get_global_rect()), "%s: THREAT INTEL whole too" % tag)
		# The title: the page title's baked sticker at the title pages' size.
		var st: VerbSticker = hq.hud.title_sticker
		assert_not_null(st, tag)
		assert_true(st.uses_art(), "%s: RAID SETUP is the baked title sticker" % tag)
		var w := st.get_combined_minimum_size().x * TO_1080
		assert_gte(w, 200.0, "%s: about 220 px wide at 1080p (%.0f)" % [tag, w])
		hq.get_parent().queue_free()
		await _frames(1)
	Settings.set_text_scale(1.0)


func test_your_network_and_threat_intel_fit_the_column_at_every_text_size() -> void:
	_raid_campaign()
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var hq := await _hq()
		hq.show_raid()
		await _frames(6)
		var page: Control = hq._panel
		var column := page.get_node("CardColumn") as Control
		var intel := page.find_child("ThreatIntel", true, false) as Control
		var network := page.find_child("NodeOrders", true, false) as Control
		assert_true(column.is_ancestor_of(network), "x%.1f: YOUR NETWORK in the right column" % scale)
		if scale <= 1.6:
			# The review: THREAT INTEL was cut at the column's scroll edge at 1.6 (B1c note).
			assert_true(column.get_global_rect().grow(1.0).encloses(intel.get_global_rect()), "x%.1f: THREAT INTEL whole in the column" % scale)
			assert_gt(network.get_global_rect().position.y, intel.get_global_rect().position.y, "x%.1f: under THREAT INTEL" % scale)
		else:
			# 2.0 (B3 b): THREAT INTEL alone is taller than the column (its big-text layout is a later
			# slice): the collapsed YOUR NETWORK leads the column, never below the fold.
			assert_true(hq.network_collapsed(), "x%.1f: YOUR NETWORK collapsed" % scale)
			assert_lte(absf(network.get_global_rect().position.y - column.get_global_rect().position.y), 1.0, "x%.1f: YOUR NETWORK at the column's top" % scale)
		assert_true(SCREEN.grow(1.0).encloses(column.get_global_rect()), "x%.1f: on screen" % scale)
		hq.get_parent().queue_free()
		await _frames(1)


func test_the_raid_interlude_plays_one_incoming_transition_from_the_route() -> void:
	var e := Motion.entry(RaidIncoming.MOTION)
	assert_not_null(e, "its motion entry")
	assert_almost_eq(e.duration, 0.6, 0.001, "about 0.6 s")
	assert_true(VfxTier.fits(e))
	assert_true(UiMotionData.REQUIRED_IDS.has(RaidIncoming.MOTION))
	# Headless (no motion): nothing plays, the raid page is the end state.
	var host: Control = add_child_autofree(Control.new())
	host.size = SCREEN.size
	assert_eq(RaidIncoming.play(host), 0.0)
	assert_null(host.get_node_or_null("RaidIncoming"))
	# With motion: the layer plays over the page and MotionSkip ends it.
	Motion.force_live = true
	var d := RaidIncoming.play(host)
	assert_gt(d, 0.0)
	var layer := host.get_node_or_null("RaidIncoming") as RaidIncoming
	assert_not_null(layer)
	assert_true(layer.motion_running())
	assert_eq(RaidIncoming.envelope(0.5), 1.0, "the word holds in the middle")
	assert_eq(RaidIncoming.envelope(0.0), 0.0)
	layer.complete_motion()
	await _frames(1)
	assert_null(host.get_node_or_null("RaidIncoming"), "skipped: gone")
	Motion.force_live = false
	# The interlude from the route page asks for it (the source calls it on the route's way in).
	var src := FileAccess.get_file_as_string("res://scripts/ui/netrun_scene.gd")
	assert_string_contains(src, "RaidIncoming.play(self)")
