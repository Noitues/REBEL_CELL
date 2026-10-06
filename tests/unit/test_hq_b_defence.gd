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
	# B4 (art director): Q3's words are in the system word's tooltip (the pink line repeated the
	# INTERCEPTED corp news toast).
	var word := hq._panel.find_child("SystemWord", true, false) as Label
	assert_string_contains(word.tooltip_text, tr(hq.RAID_MID_RUN), "JACK IN's system word says the raid comes mid-run (Q3)")
	assert_null(hq._panel.find_child("RaidMidRun", true, false), "no pink line on the map")
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


# --- S-RAID's page items (designer group ruling: round 40) -----------------------------------------

## B3 (review Q9 / Q10, round 44 `raid_setup.png`; supersedes RAID-06's YOUR NETWORK top left and
## RAID-05's no title): YOUR NETWORK under THREAT INTEL on the right, the yellow RAID SETUP title,
## IF PLACED only while a card is pointed at; its preview is the result.
func test_round_44_your_network_under_threat_intel_if_placed_on_hover_and_its_preview_is_the_result() -> void:
	var c := RunManager.campaign
	var hq := await _hq()
	hq.show_raid()
	await _frames(4)
	var page: Control = hq._panel
	assert_eq(String(hq.hud._title), tr("RAID SETUP"), "Q10: the RAID SETUP title sticker while the DEFENCE hand is open")
	var network := page.find_child("NodeOrders", true, false) as Control
	var column := page.get_node("CardColumn") as Control
	var intel := page.find_child("ThreatIntel", true, false) as Control
	assert_true(column.is_ancestor_of(network), "Q9: YOUR NETWORK in the right column")
	assert_gt(network.get_global_rect().position.y, intel.get_global_rect().position.y, "under THREAT INTEL")
	assert_false(page.get_node("WorkOrder").is_ancestor_of(network), "not over the work order")
	var if_placed := page.find_child("IfPlaced", true, false) as Control
	assert_not_null(if_placed, "the IF PLACED terminal")
	assert_true(column.is_ancestor_of(if_placed), "on the right, in the card column")
	assert_false(if_placed.visible, "the clutter rule: no IF PLACED until a card is pointed at")
	assert_null(page.find_child("DeploySteps", true, false), "RAID-01: no steps panel")
	# Its lines are the rules' own preview: what the first defence would change on the target.
	var target: StringName = hq.selected_site
	var said: Array = []
	for l in page.find_child("IfPlacedLines", true, false).get_children():
		said.append((l as Label).text)
	var expect: Array = hq.if_placed_lines({"kind": "asset", "index": 0, "asset": c.armory[0]}, target)
	assert_eq(said, expect, "IF PLACED shows the first defence's change")
	# Hovering another card shows its change; placing it gives the forecast it showed.
	var card := page.find_child("Asset_%s" % c.armory[1], true, false) as AssetCard
	card.mouse_entered.emit()
	await _frames(1)
	assert_eq(hq.if_placed_index, 1, "the hovered card's change")
	assert_true(if_placed.visible, "IF PLACED shows while the card is pointed at")
	var copy := c.duplicate_state()
	CampaignRules.deploy_asset(copy, RunManager.config(), RunManager.lookup(), 1, target)
	var then := CampaignRules.project_raid(copy, RunManager.corporation, RunManager.config(), RunManager.lookup(), RunManager.pending_raid())
	card.pressed.emit()
	await _frames(2)
	assert_eq(RunManager.project_raid().home_after, then.home_after, "the preview is the result")


func test_round_40_continue_waits_unseen_and_the_report_has_no_disc() -> void:
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	Settings.set_reduce_effects(false)
	hq.fight_raid()
	await _frames(4)
	if hq.panel_name == "raid_playout":
		var cont: Button = null
		for b in hq._panel.find_children("*", "Button", true, false):
			if (b as Button).text == tr("Continue"):
				cont = b
		assert_not_null(cont, "Continue on the playout")
		if cont != null and cont.disabled:
			assert_eq(cont.modulate.a, 0.0, "RAID-09: no grey waiting sticker while the raid plays")
		hq.show_raid_summary()
	else:
		hq.show_raid_summary()
	await _frames(3)
	assert_null(hq._panel.find_child("RaidVerdict", true, false), "RAID-12: no result disc on the report")
	var holds := hq._panel.find_child("CellHolds", true, false) as Control
	if holds != null:
		# B3 (review Q7; supersedes RAID-12's centre left on the table): CELL HOLDS is on the
		# after-action paper.
		var paper := hq._panel.find_child("RaidReport", true, false) as Control
		assert_true(paper.get_global_rect().has_point(holds.get_global_rect().get_center()), "CELL HOLDS on the after-action paper")
