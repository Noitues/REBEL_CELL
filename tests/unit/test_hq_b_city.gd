extends GutTest
## HQ-B (b) (M14, HQ redesign direction B "THE HAND"; designer rulings 2026-10-05): the HQ is
## the live 3D city at the RAID band with the Grid folded in: every Site on the map, the
## Cell's nodes as their raid sockets, the camera fitted to the network and the runnable
## Sites (Q5), zoom out into the GRID band (Q4); the hand (CREW / MARKET / DEFENCE) along the
## foot, the selected Site's card at the right over the verb slot (JACK IN with the picked
## runner); the pirate radio as one ON AIR line (Q7), the story in the Codex (Q8), no Save /
## Codex / Settings on the page (Q9: the pause menu). Every function by mouse and by pad, and
## the page fits at text 1.0 / 1.6 / 2.0.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var cfg: CityConfig = CityView3D.CONFIG
var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_hq_b_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


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


## A campaign with two claimed nodes (one a Safehouse) and Schematics to spend.
func _network() -> void:
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = 400
	for t: StringName in [&"safehouse", &"firewall_relay"]:
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, t)


func _page(hq: Control) -> Control:
	return hq._panel


func test_the_hq_is_the_raid_band_city_with_every_site_on_it() -> void:
	_network()
	var hq := await _hq()
	assert_eq(hq.panel_name, "hq")
	assert_true(hq.wireframe.visible and hq.wireframe.city3d, "the HQ is the unified 3D city")
	assert_false(hq.background.visible, "no cyberdeck room behind it")
	assert_eq(hq.wireframe.city.band_lock, CityLod.Band.RAID, "at the RAID band")
	var c := RunManager.campaign
	for s in RunManager.corporation.city_grid.sites:
		if s != null:
			assert_true(hq.city_overlay.has_site(s.id), "%s on the map" % s.id)
	for n in hq.city_overlay.nodes:
		assert_eq(n.has("socket"), c.grid.is_claimed(n["id"]), "%s: the Cell's nodes are raid sockets, the rest markers" % n["id"])
	for name in ["MapCursor", "HandTabs", "Hand", "CardColumn", "VerbSlot", "OnAir", "MapLegend"]:
		assert_not_null(_page(hq).get_node_or_null(name), "%s on the page" % name)
	for gone in ["CityGrid", "SaveButton", "SettingsButton", "PirateRadio", "BlackMarket", "RunsOpen", "BackToHq"]:
		assert_null(_page(hq).find_child(gone, true, false), "%s left the HQ" % gone)
	assert_true(hq.hud.heat_gauge.is_visible_in_tree(), "the HEAT gauge (a)")


func test_the_camera_fits_the_network_and_the_runnable_sites_and_zooms_out_to_the_grid_band() -> void:
	_network()
	var hq := await _hq()
	await _frames(20)
	var ortho := RaidZoomFit.ortho_of(hq.wireframe.city.scale.x, hq.size.x)
	assert_between(ortho, cfg.raid_fit_min - 0.5, cfg.raid_fit_max + 0.5, "fitted in the raid range (Q5: up to the clamp)")
	if ortho < cfg.raid_fit_max - 0.5:
		var free: Rect2 = hq.hq_free_rect().grow(2.0)
		for s in RunManager.launchable_sites():
			var p: Vector2 = hq.city_overlay.get_global_transform() * hq.city_overlay.icon_at(s.id)
			assert_true(free.has_point(p), "%s: a runnable Site in the map's free part (%s in %s)" % [s.id, p, free])
	# Q4: the wheel zooms out past the raid range into the GRID band, and back.
	for i in 12:
		hq.grid_controls.zoom_at(hq.size * 0.5, 1.0)
	assert_gt(RaidZoomFit.ortho_of(hq.wireframe.city.scale.x, hq.size.x), cfg.raid_fit_max, "out past raid_fit_max")
	assert_eq(hq.wireframe.city.band_lock, CityLod.Band.GRID, "the whole city: the GRID band")
	for i in 12:
		hq.grid_controls.zoom_at(hq.size * 0.5, -1.0)
	assert_eq(hq.wireframe.city.band_lock, CityLod.Band.RAID, "back in: the RAID band")


func test_selecting_a_site_keeps_the_camera_and_shows_its_card_and_verb() -> void:
	_network()
	var hq := await _hq()
	await _frames(10)
	var open := RunManager.launchable_sites()
	assert_false(open.is_empty())
	var before: Dictionary = hq._city_frame()
	hq.city_overlay.node_clicked.emit(open[open.size() - 1].id)
	await _frames(3)
	assert_eq(hq.selected_site, open[open.size() - 1].id, "a map click selects the Site")
	assert_almost_eq(float(hq._city_frame()["scale"]), float(before["scale"]), 0.0001, "the camera stays where it was")
	var card := _page(hq).find_child("SelectedSite", true, false)
	assert_not_null(card, "the Site's card at the right")
	assert_true(_page(hq).get_node("CardColumn").is_ancestor_of(card))
	var jack := _page(hq).find_child("Launch", true, false) as VerbSticker
	assert_not_null(jack, "JACK IN is the verb slot's pink sticker")
	assert_eq(jack.fill, VerbSticker.Fill.PINK)
	assert_string_contains((_page(hq).find_child("SystemWord", true, false) as Label).text, "> jack --from", "its system word under it (bible 1.3)")
	assert_gt((_page(hq).find_child("SystemWord", true, false) as Label).size.y, 4.0, "the system word has its line")
	# show_grid is the HQ now (the Grid page folded in).
	hq.show_grid()
	await _frames(2)
	assert_eq(hq.panel_name, "hq")


func test_jack_in_starts_the_run_with_the_picked_runner() -> void:
	var c := RunManager.campaign
	var recruit_cls := RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData
	c.schematics = 200
	CampaignRules.recruit(c, RunManager.config(), recruit_cls)
	var hq := await _hq()
	var second := c.roster[1].id
	(_page(hq).find_child("Crew_%s" % second, true, false) as CrewHandCard).pressed.emit()
	await _frames(2)
	assert_eq(hq.selected_operative, second, "a card's press picks the runner")
	assert_true((_page(hq).find_child("Crew_%s" % second, true, false) as CrewHandCard).picked, "its card lifts")
	var site: StringName = hq.selected_site
	(_page(hq).find_child("Launch", true, false) as VerbSticker).pressed.emit()
	await _frames(2)
	assert_not_null(RunManager.netrun, "JACK IN started the run")
	assert_eq(RunManager.netrun.run.operative.id, second, "with the picked runner")
	assert_eq(RunManager.netrun.run.site_id, site, "on the selected Site")


func test_the_crew_hand_is_in_roster_order_flatlined_last_and_greys_with_the_rules_reason() -> void:
	var c := RunManager.campaign
	var cls := RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData
	c.schematics = 200
	CampaignRules.recruit(c, RunManager.config(), cls)
	CampaignRules.recruit(c, RunManager.config(), cls)
	c.roster[0].alive = false
	var hq := await _hq()
	var order: Array = []
	for k in _page(hq).get_node("Hand/HandCards").get_children():
		if k is CrewHandCard:
			order.append((k as CrewHandCard).operative_id)
	var want: Array = []
	for i in range(1, c.roster.size()):
		want.append(c.roster[i].id)
	want.append(c.roster[0].id)
	assert_eq(order, want, "roster order, the flatlined last (Q12)")
	var dead := _page(hq).find_child("Crew_%s" % c.roster[0].id, true, false) as CrewHandCard
	assert_true(dead.dead and dead.disabled, "a flatlined card can't be picked")
	# A Site the runner's rank can't take: the card greys with the rules' own words.
	var hard: SiteData = null
	for s in RunManager.corporation.city_grid.sites:
		if s != null and s.tier >= 2:
			hard = s
	if hard != null:
		var why := CampaignRules.launch_error(c, RunManager.corporation, RunManager.config(), c.roster[1], cls, hard)
		hq.selected_site = hard.id
		hq.show_hq()
		await _frames(2)
		var card := _page(hq).find_child("Crew_%s" % c.roster[1].id, true, false) as CrewHandCard
		if RunManager.launchable_sites().has(hard):
			assert_eq(card.refusal, why, "greyed with the rule's reason")


func test_the_market_hand_buys_at_the_shown_price() -> void:
	var c := RunManager.campaign
	c.schematics = 300
	var hq := await _hq()
	hq.open_hand(hq.HandTab.MARKET)
	await _frames(2)
	assert_true((_page(hq).find_child("Tab_MARKET", true, false) as MenuChip).selected, "the MARKET tab is open")
	var cls := RunManager.available_classes()[0]
	var hire := _page(hq).find_child("Recruit_%s" % cls.id, true, false) as CrewHandCard
	assert_not_null(hire)
	assert_true(hire.hire, "a HIRE card")
	var price := CampaignRules.rookie_price(c, RunManager.config())
	assert_string_contains(hire.status, str(price), "its price on its chip")
	var n := c.roster.size()
	var sch := c.schematics
	hire.pressed.emit()
	await _frames(2)
	assert_eq(c.roster.size(), n + 1, "hired")
	assert_eq(c.schematics, sch - price, "preview == result")
	var boost: NetrunBoostData = null
	for b in RunManager.config().netrun_boosts:
		if b != null:
			boost = b
			break
	var sticker := _page(hq).find_child("Boost_%s" % boost.id, true, false) as VerbSticker
	assert_not_null(sticker, "the boosts are stickers")
	sch = c.schematics
	sticker.pressed.emit()
	await _frames(2)
	assert_has(c.pending_boosts, boost.id)
	assert_eq(c.schematics, sch - boost.cost, "at its gold tag's price")
	assert_not_null(_page(hq).find_child("Unlocks", true, false), "Profile unlocks in the hand")


func test_station_recall_and_patch_from_the_node_card() -> void:
	_network()
	var c := RunManager.campaign
	var safehouse: StringName = &""
	for id in c.grid.claimed_ids():
		if c.grid.node_type_of(id) == &"safehouse":
			safehouse = id
	var hq := await _hq()
	hq.select_site(safehouse)
	await _frames(2)
	var station := _page(hq).find_child("StationHere", true, false) as Button
	assert_not_null(station, "the runner can be stationed from the node's card")
	station.pressed.emit()
	await _frames(2)
	var op: OperativeState = hq.selected_op()
	assert_eq(CampaignRules.stationed_site(c, op.id), safehouse, "stationed")
	var recall := _page(hq).find_child("Recall_%s" % op.id, true, false) as Button
	assert_not_null(recall, "RECALL beside the posted runner's card")
	recall.pressed.emit()
	await _frames(2)
	assert_eq(CampaignRules.stationed_site(c, op.id), &"", "back at HQ")
	c.grid.home_integrity = c.grid.home_max_integrity - 5
	hq.select_site(c.grid.home_site_id)
	await _frames(2)
	var patch := _page(hq).get_node("VerbSlot").find_child("Patch", true, false) as Button  # HQ-B (d): PATCH is the verb sticker
	assert_not_null(patch, "CORE's verb is PATCH")
	patch.pressed.emit()
	await _frames(2)
	assert_eq(c.grid.home_integrity, c.grid.home_max_integrity)


func test_the_defence_tab_shows_the_armory_and_a_pending_raid_opens_the_setup() -> void:
	var c := RunManager.campaign
	c.armory = [&"turret", &"ice_lock"]
	var hq := await _hq()
	hq.open_hand(hq.HandTab.DEFENCE)
	await _frames(2)
	assert_not_null(_page(hq).find_child("Armory_turret", true, false), "the Armory's cards")
	_network()
	CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")
	hq.open_hand(hq.HandTab.CREW)
	await _frames(2)
	assert_not_null(_page(hq).find_child("RaidCard", true, false), "the work order while a raid is pending")
	assert_not_null(_page(hq).find_child("RaidSetup", true, false), "RAID SETUP under it")
	assert_false(hq.raid_routes.what_if.is_empty(), "the routes as dashed what-if pencil")
	hq.open_hand(hq.HandTab.DEFENCE)
	await _frames(2)
	assert_eq(hq.panel_name, "raid", "DEFENCE with a raid pending is the raid setup")


func test_the_radio_is_one_on_air_line_and_the_story_is_in_the_codex() -> void:
	var hq := await _hq()
	var ticker := _page(hq).get_node("OnAir") as OnAirTicker
	assert_false(ticker.words.is_empty(), "the DJ on air (Q7)")
	assert_string_contains(ticker.tooltip_text, PauseMenu.code_line().left(8), "the share code in its tooltip")
	var c := RunManager.campaign
	if not CampaignRules.revealed_beats(c, RunManager.corporation).is_empty():
		assert_true(Codex.entries(RunManager.lookup(), RunManager.profile).has(Codex.STORY), "the story so far in the Codex (Q8)")
	RunManager.reset()
	assert_false(Codex.entries(RunManager.lookup(), RunManager.profile).has(Codex.STORY), "no campaign, no STORY")


func test_the_pad_reaches_the_map_the_hand_the_tabs_the_card_and_the_verb() -> void:
	_network()
	var hq := await _hq()
	var page := _page(hq)
	var cursor := page.get_node("MapCursor") as Control
	cursor.grab_focus()
	var before: StringName = hq.selected_site
	var ev := InputEventAction.new()
	ev.action = &"ui_right"
	ev.pressed = true
	cursor._gui_input(ev)
	await _frames(3)
	assert_ne(hq.selected_site, before, "right on the map steps to the next Site")
	page = _page(hq)
	assert_eq(get_viewport().gui_get_focus_owner(), page.get_node("MapCursor"), "the cursor keeps the focus")
	var seen := {}
	var queue: Array[Control] = [page.get_node("MapCursor")]
	while not queue.is_empty():
		var n: Control = queue.pop_front()
		if seen.has(n):
			continue
		seen[n] = true
		for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
			var nb := n.find_valid_focus_neighbor(side)
			if nb != null and not seen.has(nb):
				queue.append(nb)
	for name in ["Tab_CREW", "Tab_MARKET", "Tab_DEFENCE", "Launch"]:
		var want := page.find_child(name, true, false) as Control
		assert_true(want != null and seen.has(want), "%s reachable by pad" % name)
	for k in page.get_node("Hand/HandCards").get_children():
		if k is CrewHandCard and not (k as CrewHandCard).disabled:
			assert_true(seen.has(k), "%s reachable by pad" % k.name)


func test_the_page_fits_at_every_text_scale() -> void:
	_network()
	CampaignRules.queue_raid(RunManager.campaign, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")
	for s in SCALES:
		Settings.set_text_scale(s)
		var hq := await _hq()
		await _frames(3)
		var page := _page(hq)
		var screen: Rect2 = page.get_global_rect().grow(1.0)
		var parts: Array[Control] = []
		for name in ["WorkOrder", "HandTabs", "Hand", "CardColumn", "VerbSlot"]:
			var n := page.get_node_or_null(name) as Control
			assert_not_null(n, "x%.1f: %s" % [s, name])
			if n != null:
				parts.append(n)
				assert_true(screen.encloses(n.get_global_rect()), "x%.1f: %s on the page (%s in %s)" % [s, name, n.get_global_rect(), screen])
		for i in parts.size():
			for j in range(i + 1, parts.size()):
				var a := parts[i].get_global_rect().grow(-1.0)
				var b := parts[j].get_global_rect().grow(-1.0)
				assert_false(a.intersects(b), "x%.1f: %s clear of %s" % [s, parts[i].name, parts[j].name])
		assert_true(hq.hq_free_rect().has_area(), "x%.1f: the map keeps a free part" % s)
		hq.get_parent().free()
