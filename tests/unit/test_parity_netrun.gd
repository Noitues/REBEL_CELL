extends GutTest
## Parity fix: the netrun pages (designer group ruling 2026-10-05: netrun pages and endings match
## the concepts; where the M13 build is richer and predates v2, the build's layout and content in
## the v2 language). Ids RAID-13, RAID-14, ROUTE-03, ROUTE-06, SHOP-03, SHOP-05, SHOP-06, SHOP-08,
## EVT-01, EVT-02, EVT-03, LOOT-02, LOOT-03, END-01, END-02 (docs/art_review/PARITY/GAPS.md).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const NetrunScript := preload("res://scripts/ui/netrun_scene.gd")
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_parity_netrun"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
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


func _netrun(scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	scene.start_run(1)
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(1)


func _show(scene: Control) -> void:
	await _frames(2)  # the page before it laid out (its bar), as in a run
	scene._show_current()
	PageTransition.settle(scene)
	await _frames(4)


# --- RAID-13 / RAID-14 ----------------------------------------------------------------------------

func test_the_raid_interlude_is_the_raid_view_on_the_3d_city_with_a_start_sticker() -> void:
	var scene := _netrun()
	DemoSetup.queue_raid_interlude(RunManager.netrun, RunManager.config())
	RunManager.campaign.armory.clear()
	await _show(scene)
	var s := RunManager.netrun
	var c := s.campaign
	assert_eq(s.run.phase, RunState.Phase.RAID, "the interlude is up")
	# RAID-13: the unified 3D city at the RAID band (map mode), the raid view's map.
	assert_true(scene.background.city3d, "the 3D city")
	assert_eq(scene.background.city.band_lock, CityLod.Band.RAID, "at the RAID band")
	var projection := s.raid_projection()
	var want := RaidMapNodes.major_ids(c, RaidMapNodes.route_paths(projection.events), projection.nodes)
	var shown := {}
	for n: Dictionary in scene.city_overlay.nodes:
		shown[n["id"]] = true
		assert_true(want.has(n["id"]), "%s is a major raid node (S-MAPVIEW)" % n["id"])
		if c.grid.is_claimed(n["id"]):
			assert_true(n.has("socket"), "%s: a claimed node is a raid socket" % n["id"])
	for id in want:
		assert_true(shown.has(id), "%s shows" % id)
	# Preview == result: the pencil routes are the projection's own.
	var routes: Array[Node] = scene.city_overlay.find_children("*", "RaidRouteLayer", true, false)
	assert_eq(routes.size(), 1, "the threat routes in pencil")
	assert_eq((routes[0] as RaidRouteLayer).routes, RaidMapNodes.route_paths(projection.events), "the routes the raid takes")
	# RAID-14: START DEFENSE is the raid's pink sticker; nothing to deploy says why.
	var start: Node = scene._panel.find_child("StartDefense", true, false)
	assert_true(start is VinylButton, "START DEFENSE is a vinyl sticker")
	assert_eq((start as VinylButton).sticker.fill, VinylSticker.Fill.PINK, "pink, the screen's one verb")
	assert_eq((start as VinylButton).text, TextDb.mark("START DEFENSE"))
	if s.run_assets().is_empty():
		assert_not_null(scene._panel.find_child("NoAssets", true, false), "the empty state in words")
		assert_null(scene._panel.find_child("RunAssetChips", true, false), "no bare RUN ASSETS: caption")
		var words := scene._panel.find_child("NoAssetsWords", true, false) as Label
		assert_eq(words.text, tr(NetrunScript.NO_ASSETS_WORDS))
	# The playout is the same raid view.
	(start as VinylButton).pressed.emit()
	await _frames(3)
	assert_true(scene.background.city3d and scene.background.city.band_lock == CityLod.Band.RAID or s.run.phase != RunState.Phase.RAID,
		"the playout (or the route after an instant one) never falls back to the 2D city mid-raid")
	await _close(scene)


# --- ROUTE-03 / ROUTE-06 --------------------------------------------------------------------------

func test_the_node_panel_keeps_every_word_whole_and_its_stamp_off_the_text() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var panel := RouteNodePanel.new()
		add_child_autofree(panel)
		panel.show_node(&"L1N0", {"title": "FIGHT // L1", "tier": 1, "type": "Fight: win it for Cycles and loot",
			"rewards": ["15-25 Cycles, a card", "maybe a Firmware chip"], "heat": "+2 Heat on entry", "corp_color": Palette.CORP_SOLACE})
		panel.size = panel.get_combined_minimum_size()
		await _frames(1)
		assert_false(panel.plate.stamp_slot.visible, "x%.1f: the plate's big stamp is off (it covered the title)" % scale)
		var fs := roundi(RouteNodePanel.FIELD_FONT * scale)
		for row in panel.row_lines(panel.size.x):
			for line: String in row[1]:
				var w := Palette.body().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
				assert_true(w <= panel.value_room(panel.size.x) + 0.5, "x%.1f: '%s' fits its column (never cut)" % [scale, line])
		var chip := panel.chip_rect()
		assert_true(Rect2(Vector2.ZERO, panel.size).encloses(chip), "x%.1f: DECRYPTED on the panel" % scale)
		assert_true(chip.position.y >= panel.fields_end() - 0.5, "x%.1f: DECRYPTED under the fields" % scale)
		assert_false(panel.plate.seal, "x%.1f: no seal on the fields (the concept's holo has none)" % scale)


func test_a_boss_runs_map_has_no_bar_title() -> void:
	# S-HQRUN relay: an HQ run's page has its own title sticker; the band shows the Heat gauge.
	var scene := _netrun()
	await _frames()
	assert_eq(scene.hud._title, tr(NetrunScript.ROUTE_TITLE), "a transit route keeps its title sticker")
	RunManager.netrun.run.kind = "boss"
	scene._title_screen(RunManager.netrun, "route")
	assert_eq(String(scene.hud._title), "", "a boss run's map: no bar title")
	assert_null(scene.hud.title_sticker)
	await _close(scene)


# --- SHOP-03 / SHOP-05 / SHOP-06 / SHOP-08 --------------------------------------------------------

func test_the_mainframe_tags_leave_arrow_and_wallet() -> void:
	assert_eq(BuyButton.BUY_FONT, 16, "SHOP-03: the price lettered at the concept's 16 px")
	for scale in SCALES:
		var scene := _netrun(scale)
		DemoSetup.open_shop(RunManager.netrun)
		await _show(scene)
		var leave := scene._panel.find_child("LeaveIcon", true, false) as Button
		assert_not_null(leave, "x%.1f: SHOP-05: LEAVE's chevron" % scale)
		assert_eq(leave.icon, MainframeArt.tex(NetrunScript.LEAVE_ARROW), "the concept's own export")
		assert_true(SCREEN.encloses(leave.get_global_rect()), "x%.1f: on screen" % scale)
		assert_false(leave.get_global_rect().intersects((scene._panel.find_child("LeaveMainframe", true, false) as Control).get_global_rect()), "x%.1f: beside LEAVE" % scale)
		# SHOP-03: no price tag covers the wallet (the bin's widened with the bigger price).
		var wallet := scene._panel.find_child("Wallet", true, false) as Control
		if wallet != null and wallet.is_visible_in_tree():
			for b in scene._panel.find_children("*", "BuyButton", true, false):
				var tag := b as Control
				if tag.is_visible_in_tree():
					assert_false(tag.get_global_rect().intersects(wallet.get_global_rect()), "x%.1f: a tag covers the wallet" % scale)
		leave.pressed.emit()
		await _frames(2)
		assert_ne(RunManager.netrun.run.phase, RunState.Phase.SHOP, "x%.1f: the chevron leaves too" % scale)
		await _close(scene)


func test_the_socket_choice_is_the_spinner_and_greys_the_slots_a_chip_cannot_take() -> void:
	var scene := _netrun()
	var s := RunManager.netrun
	var op := s.run.operative
	DemoSetup.offer_loot(s, ["barbed_wire"], "firmware")
	await _show(scene)
	var mini := scene._panel.find_child("SpinnerMini", true, false) as SpinnerMini
	assert_true(mini.pickable, "the spinner is the socket choice")
	assert_null(scene._panel.find_child("SlotPick", true, false), "no dropdown")
	# The marks are the rules' own answer.
	var fits := NetrunScript.socket_fits(&"barbed_wire")
	assert_eq(fits.size(), op.slot_slice_ids.size())
	var fit := -1
	var unfit := -1
	for k in fits.size():
		assert_eq(fits[k], s.firmware_slot_error(&"barbed_wire", k) == "", "slot %d" % k)
		if fits[k] and fit < 0:
			fit = k
		if not fits[k] and unfit < 0:
			unfit = k
	var sticker := (scene._panel.find_child("Stickers", true, false) as Node).get_child(0) as Control
	sticker.mouse_entered.emit()
	for k in fits.size():
		assert_eq(mini.slot_fits(k), fits[k], "pointing at the chip greys slot %d as the rule says" % k)
	if unfit >= 0:
		var before := mini.selected()
		mini.choose(unfit)
		assert_eq(mini.selected(), before, "an unfit slot is refused")
	assert_gte(fit, 0, "barbed wire fits some slot")
	mini.choose(fit)
	assert_eq(mini.selected(), fit)
	var line := scene._panel.find_child("SocketChoice", true, false) as Label
	assert_eq(line.text, NetrunScript.slot_name(op, fit), "the line names the chosen slot")
	sticker.mouse_exited.emit()
	assert_true(mini.slot_fits(unfit if unfit >= 0 else 0), "off the chip the marks clear")
	(sticker as ZineCard).pressed.emit()
	await _frames(2)
	assert_eq(op.slot_firmware_ids[fit], &"barbed_wire", "taken into the chosen slot (preview == result)")
	await _close(scene)


func test_upgrade_reads_its_price_on_one_tag() -> void:
	var scene := _netrun()
	var s := RunManager.netrun
	DemoSetup.open_shop(s)
	await _show(scene)
	if (s.run.shop.get("slices", []) as Array).is_empty():
		pass_test("no slice in stock")
		await _close(scene)
		return
	scene.open_overwrite(0)
	await _frames(3)
	var sv := scene.get_node("SpinnerView") as SpinnerView
	sv.select(1)
	var tag := sv.find_child("ActionButton", true, false) as DripButton
	assert_eq(tag.tag_text, SpinnerView.action_words(tr("UPGRADE"), s.slice_overwrite_price(1)), "SHOP-08: UPGRADE · price on one line")
	assert_string_contains(tag.tag_text, str(s.slice_overwrite_price(1)), "the slot's own price")
	assert_false(sv.price_label.visible, "the price is not shown twice")
	sv.close()
	await _close(scene)


# --- EVT-01 / EVT-02 / EVT-03 ---------------------------------------------------------------------

func test_the_event_terminal_has_its_place_the_run_panel_and_chips_beside_the_choices() -> void:
	for scale in SCALES:
		var scene := _netrun(scale)
		var s := RunManager.netrun
		DemoSetup.open_event(s, &"ev_leash_on_the_floor")
		await _show(scene)
		var panel := scene._panel.find_child("EventPanel", true, false) as CrtWindow
		assert_eq(panel.title, scene.event_header(s, TextDb.t(s.lookup.get_content(s.campaign.corporation_id), "display_name").to_upper()), "x%.1f: EVT-01 header" % scale)
		var run: Node = scene._panel.find_child("EventRun", true, false)
		if scale < NetrunScript.EVENT_FEED_BELOW:
			assert_not_null(run, "x%.1f: the RUN terminal" % scale)
			var words := PackedStringArray()
			for l in (run as Node).find_children("*", "Label", true, false):
				words.append((l as Label).text)
			var op := s.run.operative
			assert_true(words.has("%d/%d" % [op.hp, op.max_hp]), "x%.1f: HP" % scale)
			assert_true(words.has(str(s.run.cycles)), "x%.1f: CYCLES" % scale)
			assert_true(words.has(str(s.campaign.living_operatives().size())), "x%.1f: CREW" % scale)
		var ev := s.current_event()
		for i in ev.choices.size():
			var b := scene._panel.find_child("Choice%d" % (i + 1), true, false) as Button
			var row := b.find_child("OutcomeRow", false, false) as OutcomeRow
			assert_not_null(row, "x%.1f: choice %d has its chips" % [scale, i])
			assert_true(row.beside, "EVT-02: beside the sticker")
			var br := b.get_global_rect()
			var rr := row.get_global_rect()
			assert_true(rr.position.x >= br.end.x - 0.5, "x%.1f: choice %d's chips right of its sticker" % [scale, i])
			assert_true(SCREEN.encloses(rr.grow(-0.5)), "x%.1f: choice %d's chips on screen: %s" % [scale, i, rr])
			assert_true(panel.get_global_rect().grow(0.5).encloses(rr), "x%.1f: choice %d's chips in the terminal" % [scale, i])
		await _close(scene)


func test_dispatch_is_a_transcript_on_paper_not_a_waveform() -> void:
	var scene := _netrun()
	DemoSetup.open_event(RunManager.netrun, &"ev_dispatch_early_reply")
	await _show(scene)
	var memo := scene._panel.find_child("CorpMemo", true, false) as CorpMemo
	assert_not_null(memo, "EVT-03: DISPATCH's story is on paper")
	assert_eq(memo.head_word, CorpMemo.TRANSCRIPT_HEAD)
	assert_eq(memo.sheet.stamp, tr(CorpMemo.TRANSCRIPT_STAMP), "the concept's DO NOT FORWARD stamp")
	assert_null(scene._panel.find_child("CamFeed", true, false), "no voice-only feed")
	assert_true(memo.is_ancestor_of(scene._panel.find_child("EventText", true, false)), "the story is on the paper")
	await _close(scene)


# --- LOOT-02 / LOOT-03 ----------------------------------------------------------------------------

func test_the_loot_page_says_where_it_came_from_and_what_it_paid() -> void:
	for scale in SCALES:
		var scene := _netrun(scale)
		var s := RunManager.netrun
		var node: Dictionary = s.run.map.nodes_in_layer(1)[0]
		s.run.current_node_id = node["id"]
		s.last_events.clear()
		s.last_events.append({"type": "cycles", "amount": 18, "text": "test"})
		s.run.cycles += 18
		DemoSetup.offer_loot(s, ["twist", "jam", "cache"])
		await _show(scene)
		var win := scene._panel.find_child("LootWindow", true, false) as CrtWindow
		assert_eq(win.title, scene.loot_strip(s, scale >= NetrunScript.LOOT_SIDE_FROM, tr(NetrunScript.loot_source(s))), "x%.1f: LOOT-02 strip" % scale)
		assert_string_contains(win.title, "%d OF %d" % [int(node["layer"]), s.run.map.layer_count()])
		var pay := NetrunScript.payout_of(s)
		assert_eq(int(pay["cycles"]), 18, "the payout is the session's own events")
		var cyc := scene._panel.find_child("PayoutCycles", true, false) as Control
		var labels := cyc.find_children("*", "Label", true, false)
		assert_eq((labels[labels.size() - 1] as Label).text, "+18", "x%.1f: CYCLES +18" % scale)
		if scale < NetrunScript.LOOT_SIDE_FROM:
			var wallet := scene._panel.find_child("PayoutWallet", true, false) as Label
			assert_eq(wallet.text, tr(NetrunScript.PAYOUT_WALLET) % [s.run.cycles - 18, s.run.cycles])
			assert_true((scene._panel.find_child("PayoutHeat", true, false) as Control).visible, "x%.1f: the Heat line" % scale)
		# LOOT-03: the DECK counter bottom left, SKIP under the sheet, all on screen.
		var sheet := (scene._panel.find_child("LootSheet", true, false) as Control).get_global_rect()
		var deck := (scene._panel.find_child("LootDeck", true, false) as Control).get_global_rect()
		var skip := (scene._panel.find_child("Skip", true, false) as Control).get_global_rect()
		if scale < NetrunScript.LOOT_SIDE_FROM:
			assert_true(skip.position.y >= sheet.end.y - 0.5, "x%.1f: SKIP under the sheet" % scale)
			assert_true(deck.position.y >= sheet.end.y - 0.5 and deck.get_center().x < sheet.get_center().x, "x%.1f: DECK bottom left" % scale)
		else:
			assert_true(skip.position.x >= sheet.end.x - 0.5 and deck.position.x >= sheet.end.x - 0.5, "x%.1f: big words: beside the sheet" % scale)
		for r in [sheet, deck, skip, (scene._panel.find_child("Payout", true, false) as Control).get_global_rect()]:
			assert_true(SCREEN.grow(0.5).encloses(r), "x%.1f: on screen: %s" % [scale, r])
		await _close(scene)


# --- END-01 / END-02 ------------------------------------------------------------------------------

func test_a_flatline_greys_the_city_and_prints_the_operative_struck_out() -> void:
	for kind in ["died", "completed"]:
		for scale in SCALES:
			var scene := _netrun(scale)
			var s := RunManager.netrun
			DemoSetup.end_run(s, kind)
			await _show(scene)
			var lost: bool = kind != "completed"
			var grey := scene._panel.find_child("GreyCity", true, false) as ColorRect
			if lost:
				assert_not_null(grey, "x%.1f: END-01: the city greys" % scale)
				assert_eq((grey.material as ShaderMaterial).shader, NetrunScript.END_GREY_SHADER)
			else:
				assert_null(grey, "x%.1f: END-02: a clean exit keeps the city's colour" % scale)
			var photo := scene._panel.find_child("RunEndPolaroid", true, false) as Polaroid
			assert_not_null(photo, "x%.1f: the operative's Polaroid" % scale)
			assert_eq(photo.kia, lost, "x%.1f: struck out only when flatlined" % scale)
			assert_eq(photo.caption, s.run.operative.name)
			var stamp := scene._panel.find_child("ResultStamp", true, false) as Control
			var pr := photo.get_global_rect()
			assert_true(stamp.get_global_rect().intersects(pr), "x%.1f: the verdict slapped over the print" % scale)
			var row := (scene._panel.find_child("RunEndRow", true, false) as Control).get_global_rect()
			assert_true(SCREEN.encloses(row), "x%.1f: on screen: %s" % [scale, row])
			assert_almost_eq(row.get_center().x, SCREEN.get_center().x, 2.0, "x%.1f: in the middle" % scale)
			var back := scene._panel.find_child("BackToHq", true, false) as Control
			assert_true(SCREEN.encloses(back.get_global_rect()), "x%.1f: BACK TO HQ on screen" % scale)
			await _close(scene)
