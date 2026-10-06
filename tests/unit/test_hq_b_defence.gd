extends GutTest
## HQ-B (c) (M14, HQ redesign direction B, `direction_B_defence.jpg`): the DEFENCE hand with a
## raid pending IS the raid setup, in place: the same page (no entrance), the same camera, the
## same card row and sticker slot. The routes go solid and the sockets carry the forecast; the
## hand holds the Armory's defence cards (press deploys to the target, drag onto any node); the
## card column holds THREAT INTEL and YOUR NETWORK; the slot holds START DEFENSE over Speed /
## Skip. The forecast equals the result. B / the CREW tab go back. JACK IN with a raid pending
## still plays the raid as an interlude (Q3).

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_hq_b_defence"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
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
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
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


func _hq() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(4)
	return scene


func test_the_defence_tab_is_the_raid_setup_in_place() -> void:
	var hq := await _hq()
	await _frames(10)
	var before: Dictionary = hq._city_frame()
	assert_false(hq.raid_routes.what_if.is_empty(), "at the HQ the routes are a dashed what-if")
	hq.open_hand(hq.HandTab.DEFENCE)
	await _frames(2)
	assert_eq(hq.panel_name, "raid", "DEFENCE with a raid pending is the raid setup")
	assert_false(hq.entering, "the same page: no entrance")
	assert_almost_eq(float(hq._city_frame()["scale"]), float(before["scale"]), 0.0001, "the same camera")
	var page: Control = hq._panel
	for name in ["MapCursor", "HandTabs", "Hand", "CardColumn", "VerbSlot", "WorkOrder", "OnAir"]:
		assert_not_null(page.get_node_or_null(name), "%s on the page" % name)
	assert_true((page.find_child("Tab_DEFENCE", true, false) as MenuChip).selected, "the DEFENCE tab is open")
	assert_true(hq.raid_routes.what_if.is_empty() and not hq.raid_routes.routes.is_empty(), "the routes go solid")
	for n in hq.city_overlay.nodes:
		if RunManager.campaign.grid.is_claimed(n["id"]):
			assert_true((n["socket"] as Dictionary).has("forecast"), "%s carries its forecast" % n["id"])
	for name in ["AssetCards", "ThreatIntel", "NodeOrders", "RaidCard", "HomeForecast", "RunRaid", "SpeedStrip"]:
		assert_not_null(page.find_child(name, true, false), "%s in the setup" % name)
	assert_true(page.get_node("VerbSlot").is_ancestor_of(page.find_child("RunRaid", true, false)), "START DEFENSE in the sticker slot")
	assert_false((page.find_child("RaidSetup", true, false) as Control).visible, "no RAID SETUP chip in the setup itself")
	hq.open_hand(hq.HandTab.CREW)
	await _frames(2)
	assert_eq(hq.panel_name, "hq", "the CREW tab goes back")
	assert_false(hq.entering)


func test_a_defence_card_deploys_to_the_target_and_the_forecast_equals_the_result() -> void:
	var c := RunManager.campaign
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	var target: StringName = hq.selected_site
	assert_true(c.grid.is_claimed(target), "the target is a node of the Cell's")
	var card := hq._panel.find_child("Asset_turret", true, false) as AssetCard
	assert_not_null(card)
	card.pressed.emit()
	await _frames(2)
	assert_has(c.grid.assets_on(target), &"turret", "deployed on the target")
	assert_eq(hq.panel_name, "raid", "the setup stays")
	var projection := RunManager.project_raid()
	var said := (hq._panel.find_child("HomeForecast", true, false) as Label).text
	assert_string_contains(said, "%d > %d" % [projection.home_before, projection.home_after], "the order prints the forecast")
	hq.fight_raid()
	await _frames(4)
	assert_eq(c.grid.home_integrity, projection.home_after, "preview == result")


func test_targets_by_map_click_by_pad_and_by_your_network() -> void:
	var c := RunManager.campaign
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	var claimed := c.grid.claimed_ids()
	var other: StringName = claimed[0] if claimed[0] != hq.selected_site else claimed[1]
	hq.city_overlay.node_clicked.emit(other)
	await _frames(2)
	assert_eq(hq.selected_site, other, "a click on a node of the Cell's makes it the target")
	var corp_site: StringName = RunManager.launchable_sites()[0].id
	hq.city_overlay.node_clicked.emit(corp_site)
	await _frames(2)
	assert_eq(hq.selected_site, other, "a corporate Site is no target")
	hq._panel.get_node("MapCursor").grab_focus()
	var ev := InputEventAction.new()
	ev.action = &"ui_right"
	ev.pressed = true
	hq._panel.get_node("MapCursor")._gui_input(ev)
	await _frames(3)
	assert_ne(hq.selected_site, other, "the pad steps the targets")
	assert_true(c.grid.is_claimed(hq.selected_site))
	var button := hq._panel.find_child("Target_%s" % other, true, false) as Button
	assert_not_null(button, "YOUR NETWORK lists the node")
	button.pressed.emit()
	await _frames(2)
	assert_eq(hq.selected_site, other, "its target button picks it")


func test_b_from_the_setup_goes_back_to_the_crew() -> void:
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	var b := InputEventJoypadButton.new()
	b.button_index = JOY_BUTTON_B
	b.pressed = true
	hq._unhandled_input(b)
	await _frames(4)
	assert_eq(hq.panel_name, "hq")
	assert_eq(hq.hand_tab, hq.HandTab.CREW)


func test_jack_in_with_a_raid_pending_plays_it_mid_run_and_says_so() -> void:
	var hq := await _hq()
	var word := hq._panel.find_child("RaidMidRun", true, false) as Label
	assert_not_null(word, "JACK IN's system word says the raid comes mid-run (Q3)")
	(hq._panel.find_child("Launch", true, false) as VerbSticker).pressed.emit()
	await _frames(2)
	assert_not_null(RunManager.netrun, "the rule kept: you may jack in with a raid pending")
	assert_true(RunManager.netrun.in_raid(), "the raid is the run's interlude")


func test_the_setup_fits_at_every_text_scale() -> void:
	for s in SCALES:
		Settings.set_text_scale(s)
		var hq := await _hq()
		hq.show_raid()
		await _frames(3)
		var page: Control = hq._panel
		var screen: Rect2 = page.get_global_rect().grow(1.0)
		var parts: Array[Control] = []
		for name in ["WorkOrder", "HandTabs", "Hand", "CardColumn", "VerbSlot"]:
			var n := page.get_node(name) as Control
			parts.append(n)
			assert_true(screen.encloses(n.get_global_rect()), "x%.1f: %s on the page" % [s, name])
		for i in parts.size():
			for j in range(i + 1, parts.size()):
				assert_false(parts[i].get_global_rect().grow(-1.0).intersects(parts[j].get_global_rect().grow(-1.0)), "x%.1f: %s clear of %s" % [s, parts[i].name, parts[j].name])
		hq.get_parent().free()
