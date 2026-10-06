extends GutTest
## B4 (M14 art-direction integration review; round 44 `hq_idle.png` / `hq_node_selected.png`,
## designer: "build the HQ to round 44"): the HQ idle is the City Grid look with the map dimmed
## outside the network (D7: x0.68, x0.86 inside, lit round the selection), only the Sites bible
## 4.5 pins and one name tag, the idle verb JACK IN with its one plan in yellow wax, the selected
## corporate Site's file as a holo, the Cell's nodes on terminal cards (CORE's with HEAT SCRUB as
## a terminal action), the corp news as a 2.4 s holo toast at the foot, the RAID SETUP title in
## the DEFENCE hand (Q10), the crew as polaroids with the RUNNER tag, the system word keylined,
## the off-screen TARGET's chip, and the JACK IN sticker breathing without vanishing.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_b4_hq_round44"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	Motion.force_live = false
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


## A network of claimed nodes (a Firewall Relay and a Safehouse) and Schematics to spend.
func _network() -> void:
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
	c.pending_raids.clear()


func test_the_jack_in_sticker_breathes_on_both_axes_and_never_vanishes() -> void:
	Motion.force_live = true
	var c: Control = add_child_autofree(Control.new())
	c.size = Vector2(100, 40)
	var tw := Motion.loop_pulse(c, ^"scale", &"jack_ring_breathe")
	assert_not_null(tw, "live: it breathes")
	await BoundedWait.until(get_tree(), func() -> bool: return c.scale.x > 1.0, Motion.seconds(&"jack_ring_breathe") + BoundedWait.SLACK)
	assert_gt(c.scale.x, 1.0, "it grows (a float set into a Vector2 zeroed it)")
	assert_almost_eq(c.scale.x, c.scale.y, 0.0001, "both axes")
	Motion.stop(c)
	assert_eq(c.scale, Vector2.ONE, "at rest at 1")


func test_the_hq_idle_pins_only_the_bible_4_5_sites_and_shows_one_tag() -> void:
	_network()
	var hq := await _hq()
	var c := RunManager.campaign
	var ov: CityMapOverlay = hq.city_overlay
	var unpinned := 0
	for n in ov.nodes:
		assert_false(n.has("socket"), "%s: no raid socket at the HQ idle" % n["id"])
		if not n.has("marker"):
			continue
		var spec: Dictionary = n["marker"]
		var pinned := bool(spec.get("pinned", true))
		assert_eq(pinned, HqScript().pinned_at_hq(spec), "%s: pinned by bible 4.5" % n["id"])
		if not pinned:
			unpinned += 1
			assert_eq(String(spec["kind"]), SiteMarker.KIND_SITE, "%s: only a plain Site hides" % n["id"])
			assert_eq(String(spec["status"]), SiteMarker.ST_CORPORATE, "%s: still the corp's" % n["id"])
		if c.grid.is_claimed(n["id"]):
			assert_true(pinned, "%s: the Cell's nodes always show" % n["id"])
		assert_eq(String(n.get("label", "")) != "", n["id"] == hq.selected_site, "%s: one name tag, the selection's" % n["id"])
	assert_gt(unpinned, 0, "the selectable plain Sites hide until hovered")
	# A hovered hidden Site shows with its tag; the pointer leaving takes it off.
	var hidden_id: StringName = &""
	for n in ov.nodes:
		if n.has("marker") and not bool(n["marker"].get("pinned", true)) and n["id"] != hq.selected_site:
			hidden_id = n["id"]
	hq._hq_hover_tag(hidden_id)
	for n in ov.nodes:
		if n["id"] == hidden_id:
			assert_true(ov.marker_shown(n), "hovered: it shows")
			assert_ne(String(n["label"]), "", "with its tag")
	hq._hq_hover_tag(&"")
	for n in ov.nodes:
		if n["id"] == hidden_id:
			assert_eq(String(n["label"]), "", "and goes")
	# No disc on the ground for a hidden Site; a link only where both its ends show.
	var shown := {}
	for n in ov.nodes:
		if n["id"] == hq.selected_site or not n.has("marker") or bool(n["marker"].get("pinned", true)):
			shown[n["id"]] = true
	assert_eq(ov.network_data().nodes.size(), shown.size(), "the decal draws the shown Sites only")
	for e in ov.edges:
		assert_true(e.get("arrows", false) or (shown.has(e["a"]) and shown.has(e["b"])), "%s-%s: a hidden Site's link hides" % [e["a"], e["b"]])
	assert_eq(hq.wireframe.city.band_lock, CityLod.Band.GRID, "the City Grid look (solid buildings)")


func test_the_idle_verb_is_jack_in_and_its_plan_is_one_yellow_wax_arrow() -> void:
	_network()
	var hq := await _hq()
	var site := CampaignRules.site_data(RunManager.corporation, hq.selected_site)
	assert_eq(RunManager.campaign.grid.status_of(site.id), GridState.SiteStatus.CORPORATE, "the idle pick is a corporate Site")
	assert_not_null(hq._panel.get_node("VerbSlot").get_node_or_null("Launch"), "JACK IN is the idle verb")
	var plan := hq._panel.get_node("PlanPencil") as HqPlanPencil
	assert_eq(plan.to_id, site.id, "the plan runs to the selected Site")
	assert_eq(plan.from_id, RouteLinkLayout.from_site(RunManager.corporation, RunManager.campaign, site.id), "from JACK IN's owned end")
	# Selecting a node of the Cell's: its verb, no plan.
	var node: StringName = &""
	for id in RunManager.campaign.grid.claimed_ids():
		if id != RunManager.campaign.grid.home_site_id:
			node = id
	hq.select_site(node)
	await _frames(3)
	assert_null(hq._panel.get_node("VerbSlot").get_node_or_null("Launch"), "no JACK IN on the Cell's node")
	assert_not_null(hq._panel.get_node("VerbSlot").get_node_or_null("Upgrade"), "UPGRADE once the node is selected")
	assert_eq((hq._panel.get_node("PlanPencil") as HqPlanPencil).to_id, &"", "no plan while a node is selected")


func test_the_map_dims_outside_the_network_and_lights_the_selection() -> void:
	_network()
	var hq := await _hq()
	await _frames(4)
	var dim: Dictionary = hq.hq_map_dim()
	assert_false(dim.is_empty(), "the HQ idle dims its map")
	var rect: Rect2 = dim["rect"]
	for id in RunManager.campaign.grid.claimed_ids():
		var r: Rect2 = hq._map_node_rect(id)
		if r.has_area():
			assert_true(rect.grow(1.0).encloses(r), "%s: inside the network's rect" % id)
	var sel: Rect2 = hq._map_node_rect(hq.selected_site)
	assert_almost_eq(dim["focus"], sel.get_center(), Vector2.ONE, "lit round the selected Site")
	var look := UiScrimPools.LOOK
	var d := {"rect": Rect2(0, 0, 200, 200), "focus": Vector2(1000, 1000), "feather": 10.0, "hold": 50.0, "end": 100.0}
	assert_almost_eq(UiScrimPools.dim_at(d, Vector2(100, 100)).x, 1.0 - look.map_dim_inside, 0.001, "x0.86 inside the network")
	assert_almost_eq(UiScrimPools.dim_at(d, Vector2(600, 100)).x, 1.0 - look.map_dim_outside, 0.001, "x0.68 outside (D7)")
	assert_almost_eq(UiScrimPools.dim_at(d, Vector2(600, 100)).y, 1.0, 0.001, "desaturated outside")
	assert_almost_eq(UiScrimPools.dim_at(d, Vector2(1000, 1000)).x, 0.0, 0.001, "fully lit at the selection")
	assert_almost_eq(look.map_dim_outside, 0.68, 0.0001, "D7's 0.68 map band darkening")
	# The raid setup is a raid view: no idle dim there.
	RunManager.campaign.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	hq.show_raid()
	await _frames(2)
	assert_true(hq.hq_map_dim().is_empty(), "the setup keeps its own map mode")


func test_a_corporate_site_is_a_holo_file_and_cores_card_is_a_terminal_with_heat_scrub() -> void:
	_network()
	var c := RunManager.campaign
	c.heat = 40
	var hq := await _hq()
	var card: Node = hq._panel.find_child("SelectedSite", true, false)
	assert_true(card is SiteHoloCard, "the corporate Site's file is a holo (hacked intel)")
	var rows: PackedStringArray = (card as SiteHoloCard).rows_text()
	assert_true(rows.size() >= 2 and rows[0].begins_with(tr("TYPE")), "TYPE first: %s" % [rows])
	assert_not_null(card.find_child("IfCleared", true, false), "IF CLEARED in it (the rules' preview)")
	hq.select_site(c.grid.home_site_id)
	await _frames(3)
	card = hq._panel.find_child("SelectedSite", true, false)
	assert_true(card is CrtWindow, "CORE's card is a terminal (the Cell's node)")
	for row in ["IntegrityRow", "DefencesRow", "LinksRow", "StationedRow"]:
		assert_not_null(card.find_child(row, true, false), "CORE's %s" % row)
	var readout := card.find_child("Integrity", true, false) as IntegrityReadout
	assert_eq(readout.value, c.grid.home_integrity)
	assert_eq(readout.most, c.grid.home_max_integrity)
	var scrub := card.find_child("CoreHeatScrub", true, false) as MenuChip
	assert_not_null(scrub, "HEAT SCRUB as CORE's terminal action (review section c)")
	var cfg := RunManager.config()
	var price := CampaignRules.heat_purchase_price(c, cfg)
	var amount := HeatRules.scaled_delta(c, -cfg.heat_purchase_amount, cfg)
	var sch := c.schematics
	var heat := c.heat
	scrub.pressed.emit()
	await _frames(2)
	assert_eq(c.schematics, sch - price, "preview == result: the shown price")
	assert_eq(c.heat, heat + amount, "and the shown Heat")


func test_the_corp_news_is_a_holo_toast_at_the_foot_not_a_band() -> void:
	_network()
	RunManager.campaign.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	var hq := await _hq()
	var toast := hq._panel.get_node(CorpNewsToast.NODE_NAME) as CorpNewsToast
	assert_true(toast.visible, "a pending raid's warning is intercepted news")
	assert_true(toast.text().begins_with(tr(HqScript().INTERCEPTED).split("%")[0].strip_edges()), "INTERCEPTED // ...: %s" % toast.text())
	assert_false(Dialogue.bar.visible, "not the subtitle band under the top bar")
	assert_false(Dialogue.history.is_empty(), "the line still reaches Dialogue's history")
	assert_gte(CorpNewsToast.hold_for("short"), 2.4 - 0.001, "it holds 2.4 s (bible 4.13)")
	var page: Rect2 = hq._panel.get_global_rect()
	var band := (hq._panel.get_node("OnAir") as Control).size.y
	assert_between(toast.get_global_rect().end.y, page.end.y - band - HqLayout.GAP - HqLayout.MARGIN - 1.0, page.end.y + 0.5, "at the foot (on the ON AIR line)")
	assert_false(toast.get_global_rect().intersects(hq._panel.get_node("VerbSlot").get_global_rect().grow(-1.0)), "clear of the verb")


func test_the_raid_setup_has_its_title_sticker_and_the_idle_has_none() -> void:
	_network()
	var hq := await _hq()
	assert_null(hq._panel.find_child("RaidSetupTitle", true, false), "no title on the HQ idle (Q10)")
	assert_null(hq._panel.find_child("TitleSticker", true, false))
	RunManager.campaign.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	hq.show_raid()
	await _frames(3)
	var title := hq._panel.find_child("RaidSetupTitle", true, false) as VerbSticker
	assert_not_null(title, "the DEFENCE hand's page is the raid setup: its title")
	assert_eq(title.fill, VerbSticker.Fill.YELLOW, "the yellow title sticker (round 40)")


func test_the_crew_are_polaroids_the_runner_tagged_and_the_system_word_keylined() -> void:
	_network()
	var c := RunManager.campaign
	var hq := await _hq()
	var cards: Node = hq._panel.get_node("Hand/HandCards")
	var i := 0
	for k in cards.get_children():
		if k is CrewHandCard:
			assert_almost_eq((k as CrewHandCard).rest_tilt, CrewHandCard.rest_tilt_for(i), 0.001, "a polaroid's rest tilt")
			assert_almost_eq((k as CrewHandCard).rotation_degrees, CrewHandCard.rest_tilt_for(i), 0.01, "kept after the hand's layout")
			i += 1
	var runner := hq._panel.find_child("Crew_%s" % hq.selected_operative, true, false) as CrewHandCard
	assert_true(runner.picked, "the runner's polaroid (its RUNNER tag)")
	var word := hq._panel.find_child("SystemWord", true, false) as Label
	var keyline := word.get_theme_constant("outline_size")
	assert_gte(keyline * 1080.0 / 720.0, 3.0, "the system word's ink keyline is >= 3 px at 1080p")
	assert_eq(word.get_theme_color("font_outline_color"), Palette.GLYPH_INK)
	# A flatlined operative's print is greyscale.
	c.roster[0].alive = false
	hq.show_hq()
	await _frames(3)
	var dead := hq._panel.find_child("Crew_%s" % c.roster[0].id, true, false) as CrewHandCard
	assert_true(dead.dead)
	await _frames(1)
	assert_not_null(dead.get_node("Photo").material, "drawn through greyscale")


func test_the_off_screen_target_carries_its_boss_chip() -> void:
	var hq := await _hq()
	if hq.grid_target == null:
		pending("no 3D city headless: no edge marker")
		return
	var c := RunManager.campaign
	assert_eq(hq.grid_target.chip_text, CityMapOverlay.tr_word(SiteMarker.BOSS_CHIP) % [c.exploits.size(), RunManager.config().min_exploits_for_breach])


func test_the_page_fits_with_the_toast_at_every_text_scale() -> void:
	_network()
	RunManager.campaign.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	for s in [1.0, 1.6, 2.0]:
		Settings.set_text_scale(s)
		var hq := await _hq()
		await _frames(3)
		var page: Rect2 = hq._panel.get_global_rect().grow(1.0)
		for name in ["HandTabs", "Hand", "CardColumn", "VerbSlot", "OnAir", CorpNewsToast.NODE_NAME, "WorkOrder"]:
			var n := hq._panel.get_node_or_null(name) as Control
			if n != null and n.visible:
				assert_true(page.encloses(n.get_global_rect()), "x%.1f: %s on the page" % [s, name])
		var toast := hq._panel.get_node(CorpNewsToast.NODE_NAME) as Control
		for name in ["HandTabs", "VerbSlot", "CardColumn"]:
			assert_false(toast.get_global_rect().grow(-1.0).intersects((hq._panel.get_node(name) as Control).get_global_rect().grow(-1.0)), "x%.1f: the toast clear of %s" % [s, name])
		hq.get_parent().free()


func HqScript() -> GDScript:
	return load("res://scripts/ui/hq_scene.gd") as GDScript
