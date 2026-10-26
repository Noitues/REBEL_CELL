extends GutTest
## Plan 1 wave 3 polish (W3-POLISH F1-F9): layout rules the review sheets found broken: a locked
## Site's hover file has no DECRYPTED stamp (F1), the prerequisite's words stand clear of its rings
## (F2), "HEAT +N -> T" never splits and the raid line stands alone (F3), CORP's card names its
## node once and ends above the ON AIR line (F4), GRID VIEW frames the run path (F5), the route
## node file's chip clears its last row (F6), a combat toast stands over the tutorial (F7), the
## raid note covers neither the ON AIR line nor the work order (F8 / F9).

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Vector2(1280, 720)


func before_each() -> void:
	RaidModelFixture.use_resolver()  # Phase 2b: Solace is the resolver's carrier here (raid views of the tide are Phase 3)


func after_each() -> void:
	RaidModelFixture.restore()
	RunManager.reset()


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _hq(seed_value: int) -> Control:
	RunManager.new_campaign(seed_value)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(4)
	return hq


func test_locked_site_hover_file_has_no_stamp() -> void:
	var hq := await _hq(1)
	var overlay: CityMapOverlay = hq.city_overlay
	var locked_exploit: StringName = &""
	for n: Dictionary in overlay.nodes:
		if bool(n.get("locked", false)) and not (n.get("exploit_tag", {}) as Dictionary).is_empty():
			locked_exploit = n["id"]
			break
	assert_ne(locked_exploit, &"", "a fresh Grid has a locked Exploit Site")
	if locked_exploit == &"":
		return
	overlay.hover_id = locked_exploit
	await _frames(4)
	var file := overlay.exploit_file
	assert_not_null(file, "pointing at it opens its hover file")
	if file != null:
		assert_false(file.stamp_slot.visible, "no DECRYPTED on a Site that is not reachable yet")


func test_prerequisite_words_stand_under_the_double_ring() -> void:
	var hq := await _hq(1)
	var overlay: CityMapOverlay = hq.city_overlay
	var at := Vector2(300, 200)
	var outer := 24.0
	var r := overlay.prereq_words_rect(at, outer)
	assert_true(r.has_area())
	assert_true(r.end.y <= at.y - outer + 0.5 or r.position.y >= at.y + outer - 0.5, "the words stand clear of the outer ring (%s)" % r)
	assert_almost_eq(r.get_center().x, at.x, 0.5, "and are centered on it")
	assert_eq(CityMapOverlay.PREREQ_WORDS, "CLEAR FIRST")


func test_flatline_value_keeps_its_total_whole_and_the_raid_line_alone() -> void:
	var hq := await _hq(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var saw_raid := false
	for site in CampaignRules.launchable_sites(c, corp, cfg):
		for h in range(0, 60):
			c.heat = h
			var lines := String(hq.flatline_words(site)).split("\n")
			assert_false(lines[0].contains(" "), "heat %d: 'HEAT +N -> T' has no breakable space (%s)" % [h, lines[0]])
			assert_true(lines[0].contains("->"), "the arrow and its total share the line")
			if lines.size() > 1:
				saw_raid = true
				assert_eq(lines.size(), 2)
				assert_true(lines[1].begins_with("RAID AT HEAT"), "the raid line stands on its own")
		break
	assert_true(saw_raid, "some Heat crosses a raid line")


func test_core_card_names_its_node_once_and_ends_above_the_ticker() -> void:
	var hq := await _hq(1)
	hq.select_site(RunManager.campaign.grid.home_site_id)
	await _frames(6)
	var card := hq.find_child("SelectedSite", true, false) as TerminalWindow
	assert_not_null(card)
	if card == null:
		return
	assert_eq(card.title.count("HOME SERVER"), 1, "CORE says HOME SERVER once (%s)" % card.title)
	var ticker := hq.find_child("OnAir", true, false) as Control
	assert_not_null(ticker)
	if ticker != null:
		assert_lte(card.get_global_rect().end.y, ticker.get_global_rect().position.y + 0.5, "the card ends above the ON AIR line")
	for l in card.find_children("*", "Label", true, false):
		var label := l as Label
		if label.visible and label.text != "":
			assert_lte(label.get_global_rect().end.y, card.get_global_rect().end.y + 0.5, "'%s' is inside the card" % label.text)


func test_grid_view_frames_the_run_path() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await _frames(4)
	scene._grid_zoomed = true
	scene._show_map()
	await _frames(12)
	var s := RunManager.netrun
	var from_id := CampaignRules.jack_from_site(RunManager.corporation, RunManager.campaign, s.run.site_id)
	var overlay: CityMapOverlay = scene.city_overlay
	var screen := Rect2(Vector2.ZERO, SCREEN)
	var window := scene._panel.find_child("RouteWindow", true, false) as Control
	var icons := overlay._icon_positions()
	for id in [from_id, s.run.site_id]:
		if id == &"":
			continue
		assert_true(icons.has(id), "%s has an icon" % id)
		if not icons.has(id):
			continue
		var p: Vector2 = overlay.get_global_transform_with_canvas() * (icons[id] as Vector2)
		assert_true(screen.grow(-8.0).has_point(p), "%s is on screen at %s" % [id, p])
		if window != null:
			assert_false(window.get_global_rect().has_point(p), "%s is not under the ROUTE window" % id)


## PT-003 fix 1 (ruling 1a on the netrun maps): GRID VIEW has no name tag at rest, a tag while its node is lit, and every
## tag on the map key's hover.
func test_grid_view_has_no_tags_at_rest_and_the_map_key_lights_them_all() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await _frames(4)
	scene._grid_zoomed = true
	scene._show_map()
	await _frames(8)
	var overlay: CityMapOverlay = scene.city_overlay
	assert_eq(overlay.tag_rule, CityMapOverlay.TagRule.FOCUS, "GRID VIEW follows the HQ Grid's rule")
	assert_true(overlay.tagged_ids().is_empty(), "no tag at rest")
	var legend: MapLegend = scene._grid_legend
	assert_not_null(legend, "GRID VIEW has its map key")
	legend.show_all_changed.emit(true)
	assert_false(overlay.tagged_ids().is_empty(), "the map key's hover shows tags")
	legend.show_all_changed.emit(false)
	assert_true(overlay.tagged_ids().is_empty(), "and they go with the hover")
	var named: StringName = &""
	for n: Dictionary in overlay.nodes:
		if String(n.get("label", n.get("name", ""))) != "":
			named = n["id"]
			break
	if named != &"":
		overlay.hover_id = named
		assert_true(overlay.tagged_ids().has(named), "a lit node carries its tag")
		overlay.hover_id = &""


func test_route_node_chip_clears_the_last_row() -> void:
	var panel: RouteNodePanel = add_child_autofree(RouteNodePanel.new())
	panel.show_node(&"n1", {"title": "Fight // L1", "tier": 1, "type": "Fight: win it for Cycles and loot", "rewards": ["15-25 Cycles, a card", "maybe a Firmware chip"],
		"hp": "53 / 60 on arrival", "heals": "not here; the run's end heals fully", "heat": "", "corp_color": Palette.CORP_MERIDIAN})
	await _frames(2)
	panel.size = panel.custom_minimum_size
	var gap := panel.chip_rect().position.y - panel.fields_end()
	assert_gte(gap, 4.0, "the DECRYPTED chip leaves a gap under the last row (%.1f)" % gap)
	assert_gte(panel.fields_end(), 0.0)


func test_combat_toast_stands_over_the_tutorial() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(COMBAT).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(3)
	assert_not_null(scene.toast)
	assert_gt(scene.toast.z_index, scene.OVER_HAND_Z, "a toast is above the tutorial box's layer")


func test_art_r1_f7_a_toast_never_covers_a_visible_button() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(COMBAT).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.auto_start = false
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	scene.start_tutorial()
	await _frames(10)
	var st: CombatState = scene.engine.state()
	st.free_nudges = 0
	st.ram = 0
	scene._refresh(st)
	await _frames(3)
	scene.nudge(1)
	await _frames(6)
	assert_true(scene.toast.visible, "the refusal toast is up")
	assert_not_null(scene.tutorial, "with the tutorial box open")
	var tr_rect: Rect2 = scene.toast.get_global_rect()
	for b in Toast.button_rects(scene):
		assert_false(tr_rect.intersects(b), "the toast %s covers no button (%s)" % [tr_rect, b])


func test_raid_note_covers_neither_the_ticker_nor_the_work_order() -> void:
	var hq := await _hq(7)
	var c := RunManager.campaign
	c.heat = 30
	CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")
	hq.show_hq()
	await _frames(6)
	var gauge: HeatPoster = hq.hud.heat_gauge
	gauge.set_heat(30, 100, HeatRules.band_levels(c, RunManager.config()))
	await _frames(4)
	if gauge.note_text() == "":
		pending("no note text at this Heat")
		return
	var note := gauge.note_rect()
	assert_true(note.has_area())
	for node_name in ["OnAir", "WorkOrder"]:
		var other := hq.find_child(node_name, true, false) as Control
		if other != null and other.is_visible_in_tree():
			assert_false(note.intersects(other.get_global_rect()), "the raid note keeps off %s (%s vs %s)" % [node_name, note, other.get_global_rect()])
