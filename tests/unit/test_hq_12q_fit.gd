extends GutTest
## M14 12Q-HQ (QA matrix audit L30-L34, L43, L49, L53; ART-5 acceptance): at text 1.0 / 1.6 / 2.0
## the HQ page holds every offer, row and action whole, paging (MORE) where it is short of room,
## never clipping or scaling: the MARKET and CREW hands page in their box (HandPager); the
## selected card (a Site's file, CORE's and a node's terminal, the CLAIM terminal) pages its rows
## in the card column (CardPager), which ends above the verb sticker as drawn; the Heat terminal
## pages above the hand and its tabs; the corp news toast stands clear of the polaroids; the raid
## pencil lies in the page's own marks layer, under its panels and the Heat terminal.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const CORPS: Array[StringName] = [&"halcyon", &"meridian", &"orbital", &"solace"]
## A polaroid at rest is tilted a little (CrewHandCard.rest_tilt_for): its box may lean this far (px).
const TILT_SLACK := 4.0

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_hq_12q_fit"
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


## The B4 mid-campaign HQ (review pack `_b4_hq`): four crew, a network, a raid pending.
func _b4(corp: StringName = &"solace") -> void:
	RunManager.new_campaign(7, corp)
	var c := RunManager.campaign
	var classes: Array[ClassData] = []
	for id in [&"ghost", &"rigger", &"botnet", &"wrecker"]:
		classes.append(RunManager.lookup().get_content(id) as ClassData)
	DemoSetup.roster_of(c, classes)
	DemoSetup.set_schematics(c, 900)
	for i in 5:
		var open := CampaignRules.launchable_sites(c, RunManager.corporation, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), run)
		CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), open[0].id, &"firewall_relay" if i % 2 == 0 else &"safehouse")
	for id in c.grid.claimed_ids():
		if id != c.grid.home_site_id and c.grid.node_type_of(id) == &"safehouse":
			CampaignRules.station(c, RunManager.lookup(), c.roster[1].id, id)
			break
	c.roster[3].alive = false
	DemoSetup.set_heat(c, 58)
	DemoSetup.set_schematics(c, 142)
	c.pending_raids.clear()
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})


## Every control under `root` (a Recruit_, Boost_ ... name prefix in `prefixes`).
func _named(root: Node, prefixes: Array[String]) -> Array[Control]:
	var out: Array[Control] = []
	for n in root.find_children("*", "Control", true, false):
		for p in prefixes:
			if String(n.name).begins_with(p):
				out.append(n as Control)
	return out


## The names of `items` shown whole inside `box` now.
func _shown_whole(items: Array[Control], box: Rect2) -> Dictionary:
	var out := {}
	for k in items:
		if k.is_visible_in_tree() and box.grow(TILT_SLACK).encloses(k.get_global_rect()):
			out[String(k.name)] = true
	return out


## Turns the hand through its pages; returns the names of `items` shown whole on some page.
func _every_hand_page(hq: Control, items: Array[Control], s: float) -> Dictionary:
	var seen := {}
	var hand := hq._panel.get_node("Hand") as Control
	var tab := hq._panel.find_child(HandPager.TAB_NAME, true, false) as MenuChip
	var pages: int = hq._hand_pages
	for p in pages:
		await _frames(2)
		seen.merge(_shown_whole(items, hand.get_global_rect()))
		if pages > 1:
			assert_true(tab.is_visible_in_tree() and hq._panel.get_global_rect().grow(1.0).encloses(tab.get_global_rect()), "x%.1f: the MORE tab shows whole on the page" % s)
			for k in items:
				if k.is_visible_in_tree():
					assert_false(tab.get_global_rect().grow(-1.0).intersects(k.get_global_rect()), "x%.1f: the MORE tab clear of %s" % [s, k.name])
			assert_eq(tab.text, tr(hq.ORDER_BACK) if p == pages - 1 else tr(hq.ORDER_MORE), "x%.1f: MORE, BACK on the last page" % s)
			hq.turn_hand_page()
	if pages > 1:
		await _frames(2)
		assert_eq(hq.hand_page, 0, "x%.1f: BACK returns to the first page" % s)
	else:
		assert_false(tab.visible, "x%.1f: no tab when the hand fits" % s)
	return seen


func test_every_market_offer_is_reachable_whole_at_every_scale() -> void:
	for s in TestScope.scales(SCALES):
		Settings.set_text_scale(s)
		RunManager.new_campaign(1)
		DemoSetup.set_schematics(RunManager.campaign, 500)
		var hq := await _hq()
		hq.open_hand(hq.HandTab.MARKET)
		await _frames(3)
		var items := _named(hq._panel.get_node("Hand"), ["Recruit_", "Boost_", "Unlock_", "QueuedBoosts"])
		assert_gt(items.size(), 4, "x%.1f: recruits, boosts and unlocks" % s)
		var seen := await _every_hand_page(hq, items, s)
		for k in items:
			assert_true(seen.has(String(k.name)), "x%.1f: %s whole on a page of the hand" % [s, k.name])
		if s > 1.0:
			assert_gt(hq._hand_pages, 1, "x%.1f: the market pages" % s)
		hq.get_parent().free()


func test_every_operative_is_reachable_whole_and_clear_of_the_card() -> void:
	for s in TestScope.scales(SCALES):
		Settings.set_text_scale(s)
		_b4()
		var hq := await _hq()
		hq.open_hand(hq.HandTab.CREW)
		await _frames(3)
		var items := _named(hq._panel.get_node("Hand"), ["Crew_"])
		assert_eq(items.size(), 4, "x%.1f: four crew" % s)
		var column := (hq._panel.get_node("CardColumn") as Control).get_global_rect()
		var seen := await _every_hand_page(hq, items, s)
		for k in items:
			assert_true(seen.has(String(k.name)), "x%.1f: %s whole on a page of the hand" % [s, k.name])
		for k in items:
			if k.is_visible_in_tree():
				assert_false(k.get_global_rect().grow(-1.0).intersects(column), "x%.1f: %s clear of the card column" % [s, k.name])
		hq.get_parent().free()


## Turns the selected card through its pages; returns the body rows shown whole on some page
## and checks the column ends above the verb sticker as drawn and holds its tab.
func _every_card_page(hq: Control, s: float, what: String) -> Dictionary:
	var seen := {}
	var column := hq._panel.get_node("CardColumn") as Control
	var tab := hq._panel.find_child(hq.CARD_TAB_NAME, true, false) as MenuChip
	var pages: int = hq._card_pages
	for p in pages:
		await _frames(2)
		var card := hq._panel.find_child("SelectedSite", true, false) as Control
		var box := column.get_global_rect()
		assert_true(Rect2(hq._panel.get_global_rect()).grow(1.0).encloses(box), "x%.1f %s: the column on the page" % [s, what])
		var verb := hq._panel.get_node("VerbSlot") as Control
		for k in verb.get_children():
			if k is VerbSticker:
				var sticker := (k as Control).get_global_rect()
				var turn := (k as Control).rotation
				var lift := 0.5 * (absf(sticker.size.x * sin(turn)) + sticker.size.y * cos(turn)) - 0.5 * sticker.size.y
				assert_lt(box.end.y, sticker.position.y - lift + 0.5, "x%.1f %s: the card ends above the verb sticker as drawn" % [s, what])
		var body := card.get("body") as Control
		for row in body.get_children():
			var r := row as Control
			if r.is_visible_in_tree() and box.grow(1.0).encloses(r.get_global_rect()):
				for part in _parts(r, true):
					seen[part] = true
		if pages > 1:
			var t := tab.get_global_rect()
			assert_true(tab.is_visible_in_tree() and Rect2(hq._panel.get_global_rect()).grow(1.0).encloses(t), "x%.1f %s: MORE on the page" % [s, what])
			for v in verb.get_children():
				assert_false(t.grow(-1.0).intersects((v as Control).get_global_rect()), "x%.1f %s: MORE clear of the verb's %s" % [s, what, v.name])
			for row in body.get_children():
				if (row as Control).is_visible_in_tree() and (row as Control).get_global_rect().size.y > 0.5:
					assert_false(t.grow(-1.0).intersects((row as Control).get_global_rect()), "x%.1f %s: MORE clear of %s" % [s, what, row.name])
			hq.turn_card_page()
	if pages <= 1:
		assert_false(tab.visible, "x%.1f %s: no tab when the card fits" % [s, what])
	return seen


## Every body row the builder showed with a height, by name.
func _card_rows(hq: Control) -> Array[String]:
	var out: Array[String] = []
	var card := hq._panel.find_child("SelectedSite", true, false) as Control
	var heights: Array = card.get_meta(CardPager.META_HEIGHTS, [])
	var hidden: Array = card.get_meta(CardPager.META_HIDDEN, [])
	var body := card.get("body") as Control
	var i := 0
	for row in body.get_children():
		if i < heights.size() and float(heights[i]) > 0.5 and not hidden.has(row):
			out.append_array(_parts(row as Control, false))
		i += 1
	return out


## A row's parts as the pager deals them: a wrapped Label's lines ("name#line"), a grid's cells
## by name, else the row; `shown`: only what shows now.
func _parts(r: Control, shown: bool) -> Array[String]:
	var out: Array[String] = []
	if r is Label and (r as Label).get_line_count() > 1:
		var l := r as Label
		var first := l.lines_skipped if shown else 0
		var n := (l.max_lines_visible if l.max_lines_visible >= 0 else l.get_line_count() - first) if shown else l.get_line_count()
		for k in range(first, mini(first + n, l.get_line_count())):
			out.append("%s#%d" % [r.name, k])
	elif r is GridContainer or r is FlowContainer:
		for c in r.get_children():
			if not shown or (c as Control).visible:
				out.append(String(c.name))
	else:
		out.append(String(r.name))
	return out


func _check_card(hq: Control, s: float, what: String) -> void:
	await _frames(3)
	var rows := _card_rows(hq)
	assert_false(rows.is_empty(), "x%.1f %s: the card has rows" % [s, what])
	var seen := await _every_card_page(hq, s, what)
	for r in rows:
		assert_true(seen.has(r), "x%.1f %s: %s whole on a page of the card" % [s, what, r])


func test_the_claim_terminal_pages_its_build_choices_whole() -> void:
	for s in TestScope.scales(SCALES):
		Settings.set_text_scale(s)
		_b4()
		var c := RunManager.campaign
		var hq := await _hq()
		for site in CampaignRules.launchable_sites(c, RunManager.corporation, RunManager.config()):
			if not c.grid.is_claimed(site.id) and site.claimable:
				var run := RunState.new()
				run.site_id = site.id
				CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), run)
				hq.select_site(site.id)
				break
		await _check_card(hq, s, "CLAIM")
		var tiles := hq._panel.find_child("NodeTiles", true, false) as Control
		assert_not_null(tiles, "x%.1f: the build tiles" % s)
		hq.get_parent().free()


func test_core_and_node_terminals_page_every_row_and_action() -> void:
	for s in TestScope.scales(SCALES):
		Settings.set_text_scale(s)
		_b4()
		var c := RunManager.campaign
		var hq := await _hq()
		hq.select_site(c.grid.home_site_id)
		await _check_card(hq, s, "CORE")
		for id in c.grid.claimed_ids():
			if id != c.grid.home_site_id and c.grid.is_active_node(id):
				hq.select_site(id)
				break
		await _check_card(hq, s, "node")
		for id in c.grid.claimed_ids():
			if id != c.grid.home_site_id:
				c.grid.site(id)["condition"] = GridState.Condition.DOWN
				hq.select_site(id)
				break
		await _check_card(hq, s, "DOWN node")
		hq.get_parent().free()


func test_the_site_file_keeps_its_rows_for_every_corporation() -> void:
	for corp in CORPS:
		for s in TestScope.scales(SCALES):
			Settings.set_text_scale(s)
			_b4(corp)
			var hq := await _hq()
			await _check_card(hq, s, "%s Site" % corp)
			hq.get_parent().free()


func test_the_exploit_explanation_is_whole() -> void:
	for s in TestScope.scales(SCALES):
		Settings.set_text_scale(s)
		RunManager.new_campaign(1)
		var hq := await _hq()
		for sd in RunManager.corporation.city_grid.sites:
			if sd.objective == RC.SiteObjective.EXPLOIT:
				hq.select_site(sd.id)
				break
		await _check_card(hq, s, "Exploit")
		var why := hq._panel.find_child("WhyNot", true, false) as Label
		assert_not_null(why, "x%.1f: the explanation" % s)
		hq.get_parent().free()


func test_the_heat_terminal_pages_above_the_hand_and_its_tabs() -> void:
	for s in TestScope.scales(SCALES):
		Settings.set_text_scale(s)
		_b4()
		var hq := await _hq()
		hq.toggle_heat_terminal()
		await _frames(3)
		var term: HeatTerminal = hq.heat_terminal
		var hand := hq._panel.get_node("Hand") as Control
		var tabs := hq._panel.get_node("HandTabs") as Control
		var rows := term.body.get_node("HeatRows") as Control
		var seen := {}
		for p in hq._heat_pages:
			await _frames(2)
			var t := term.get_global_rect()
			assert_lt(t.end.y, minf(hand.get_global_rect().position.y, tabs.get_global_rect().position.y) + 0.5, "x%.1f: the terminal ends over the hand and its tabs" % s)
			for r in rows.get_children():
				if (r as Control).is_visible_in_tree() and t.grow(1.0).encloses((r as Control).get_global_rect()):
					seen[String(r.name)] = true
			assert_true(term.scrub.is_visible_in_tree(), "x%.1f: SCRUB HEAT on every page" % s)
			if hq._heat_pages > 1:
				hq.turn_heat_page()
		for r in rows.get_children():
			assert_true(seen.has(String(r.name)), "x%.1f: %s whole on a page of the Heat terminal" % [s, r.name])
		hq.close_heat_terminal(false)
		hq.get_parent().free()


func test_the_raid_pencil_lies_under_the_hq_panels() -> void:
	_b4()
	var hq := await _hq()
	await _frames(3)
	var routes: RaidRouteLayer = hq.raid_routes
	assert_not_null(routes, "the raid's routes on the HQ map")
	var marks := hq._panel.get_node_or_null(hq.HQ_MARKS) as Control
	assert_not_null(marks, "the page's marks layer")
	assert_eq(routes.pool_host, marks, "the pencil is laid in it")
	for name in ["WorkOrder", "HandTabs", "Hand", "CardColumn", "VerbSlot"]:
		var n := hq._panel.get_node_or_null(name) as Control
		if n != null:
			assert_gt(n.get_index(), marks.get_index(), "%s draws over the marks" % name)
	hq.toggle_heat_terminal()
	await _frames(2)
	assert_true(hq.heat_terminal.top_level and hq.heat_terminal.z_index > 0, "the Heat terminal over the page (marks included)")
	hq.close_heat_terminal(false)


func test_the_corp_news_toast_stands_clear_of_the_crew() -> void:
	for s in TestScope.scales(SCALES):
		Settings.set_text_scale(s)
		_b4()
		var hq := await _hq()
		hq.intercept_raid_warning(&"raid_heat_25")
		await _frames(3)
		var toast := hq._panel.get_node(CorpNewsToast.NODE_NAME) as Control
		if toast.visible:
			for k in _named(hq._panel.get_node("Hand"), ["Crew_"]):
				if k.is_visible_in_tree():
					assert_false(toast.get_global_rect().grow(-1.0).intersects(k.get_global_rect()), "x%.1f: the toast clear of %s" % [s, k.name])
		hq.get_parent().free()


func test_hand_split_deals_units_in_order_and_keeps_glue() -> void:
	var w: Array[float] = [100.0, 100.0, 100.0, 40.0, 100.0]
	var g: Array[int] = [-1, 0, 0, 0, 1]
	var glue: Array[bool] = [false, false, false, true, false]
	var pages := HandPager.split(w, g, {0: 50.0, 1: 300.0}, 5.0, 10.0, glue, 260.0)
	assert_eq(pages, [0, 0, 1, 1, 2] as Array[int], "a unit that overflows starts a page; the glued one follows its neighbour; a wide caption counts")
	assert_eq(HandPager.page_width([1, 2], w, g, {0: 50.0}, 5.0, 10.0), 205.0, "a group is its units and their gaps")


func test_card_split_keeps_captions_with_their_row_and_empty_rows_free() -> void:
	var h: Array[float] = [40.0, 0.0, 40.0, 20.0, 60.0]
	var nxt: Array[bool] = [false, false, false, true, false]
	var pages := CardPager.split(h, nxt, 4.0, 90.0)
	assert_eq(pages, [0, 0, 0, 1, 1] as Array[int], "an empty row costs nothing; a caption goes with the row after it")
	assert_eq(CardPager.split([200.0] as Array[float], [false] as Array[bool], 4.0, 90.0), [0] as Array[int], "a row taller than the room takes its own page")


## G2R2-2: the raid setup's INTERCEPTED toast takes the ON AIR line's place in the foot band for its
## hold (never over the map, the pencil or the paper), then the line returns; it never stands.
func test_the_raid_setup_toast_takes_the_on_air_lines_place_and_gives_it_back() -> void:
	for s in TestScope.scales(SCALES):
		Settings.set_text_scale(s)
		_b4()
		var hq := await _hq()
		hq.show_raid()
		await _frames(4)
		hq.intercept_raid_warning(&"raid_heat_25")
		await _frames(4)
		var toast := hq._panel.get_node(CorpNewsToast.NODE_NAME) as CorpNewsToast
		var ticker := hq._panel.get_node("OnAir") as Control
		assert_true(toast.visible, "x%.1f: the toast is up" % s)
		var tr_ := toast.get_global_rect()
		var kr := ticker.get_global_rect()
		assert_almost_eq(tr_.end.y, kr.end.y, 1.5, "x%.1f: the toast stands on the foot band" % s)
		assert_true(tr_.position.x >= kr.position.x - 1.0 and tr_.end.x <= kr.end.x + 1.0, "x%.1f: within the band's width" % s)
		assert_eq(ticker.modulate.a, 0.0, "x%.1f: the ticker waits under it" % s)
		assert_lt(CorpNewsToast.hold_for(toast.text()), 10.0, "x%.1f: the toast is transient (hold then fade)" % s)
		toast.hide()
		await _frames(2)
		assert_eq(ticker.modulate.a, 1.0, "x%.1f: the ON AIR line returns" % s)
		hq.get_parent().free()


## G2R2-4: the raid result's CONTINUE (built as the playout page builds it; headless the page
## goes straight on to the summary) keeps the focus fold's room after its last letter.
func test_the_raid_result_continue_keeps_room_for_its_focus_fold() -> void:
	var hq_script := load("res://scripts/ui/hq_scene.gd")
	for s in TestScope.scales(SCALES):
		Settings.set_text_scale(s)
		var cont := HoloSticker.word(tr("CONTINUE"), VinylSticker.Fill.PINK, minf(Settings.text_scale, ShopItem.OBJECT_MAX_SCALE), hq_script.RAID_CONTINUE_PX)
		cont.add_fold_room()
		add_child_autofree(cont)
		await _frames(2)
		var v := cont.sticker
		var last_end := 0.0
		for g in v.get(&"_glyphs"):
			if g[0] != "\u00a0":
				last_end = maxf(last_end, (g[1] as Vector2).x + Palette.display().get_string_size(g[0], HORIZONTAL_ALIGNMENT_LEFT, -1, v.get(&"_px")).x)
		assert_gt(last_end, 0.0, "x%.1f: the word is laid out" % s)
		assert_gte(v.body_rect.end.x - last_end, v.peel_px(), "x%.1f: the fold lies past the last letter" % s)
		# G2 polish P1: every glyph rect is clear of the fold's square, as BACK TO HQ is held
		var fold := Rect2(Vector2(v.body_rect.end.x - v.peel_px(), v.body_rect.position.y), Vector2(v.peel_px(), v.peel_px()))
		var font: Font = v.get(&"_font")
		for g in v.get(&"_glyphs"):
			var gp: Vector2 = g[1]
			var gr := Rect2(Vector2(gp.x, gp.y - float(g[4])), Vector2(font.get_string_size(g[0], HORIZONTAL_ALIGNMENT_LEFT, -1, v.get(&"_px")).x, float(g[4])))
			assert_false(gr.intersects(fold), "x%.1f: glyph %s clear of the fold" % [s, g[0]])
