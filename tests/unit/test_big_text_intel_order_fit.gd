extends GutTest
## M14 BIG-TEXT: THREAT INTEL (the decrypted holo) and the raid setup's work order fit their rooms at
## text scales 1.0 / 1.6 / 2.0 (the layout is 1280x720 at 1080p too: the stretch keeps it). Every line
## of each is whole inside its panel and inside what the page shows of it; the MORE tab shows only
## when the order is folded and the two pages together carry every row. BIG-TEXT b (art director):
## no text on these panels is smaller than at 1.0 (`HqLayout.base_floor`), THREAT INTEL pages like
## the order, the order's tab is a paper tab out of the sheet's foot (inside the sticker safe
## margin), YOUR NETWORK is one row from 1.6 when short of room (whole on focus), and the
## letterhead's corp name keeps left of its seal. Views never change state.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
## A tilted sheet's corners leave its rect by a pixel or two.
const TILT_SLACK := 6.0
const ROWS: Array[String] = ["RaidTarget", "RaidUnits", "RaidStrength", "HomeForecast", "ThreatsStopped"]

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_big_text_fit"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	Motion.force_live = false
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


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


## 0: the review pack's raid (two entry routes, one node); 1: two nodes and a wider network.
func _campaign(kind: int) -> void:
	if kind == 1:
		_raid_campaign()
		return
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var grid := RunManager.corporation.city_grid
	var first: StringName = grid.get_site(grid.home_site_id).links[0]
	c.schematics = 400
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})


func _hq(scale: float) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(4)
	scene.show_raid()
	await _frames(8)
	return scene


## The smallest font size of the visible Labels under `root` (px).
func _min_font(root: Node) -> int:
	var texts: Array[Control] = []
	_texts(root, texts)
	var least := 1 << 20
	for t in texts:
		if t is Label and (t as Label).text != "":
			least = mini(least, t.get_theme_font_size(&"font_size"))
	return least


## Every visible text Control under `root` (Labels and RichTextLabels).
func _texts(root: Node, out: Array[Control]) -> void:
	for ch in root.get_children():
		if ch is Control and not (ch as Control).is_visible_in_tree():
			continue
		if ch is Label or ch is RichTextLabel:
			out.append(ch)
		_texts(ch, out)


## Asserts every line under `panel` is whole: inside `panel` and inside `shown`, and its box is as
## tall as its text needs.
func _assert_whole(panel: Control, shown: Rect2, tag: String, slack: float = 1.0) -> int:
	var texts: Array[Control] = []
	_texts(panel, texts)
	var inside := panel.get_global_rect().grow(slack)
	for t in texts:
		var r := t.get_global_rect()
		if r.size.x <= 0.0 or (t is Label and (t as Label).text == ""):
			continue
		assert_true(inside.encloses(r), "%s: '%s' inside its panel (%s in %s)" % [tag, (t as Label).text if t is Label else t.name, r, inside])
		assert_true(shown.grow(slack).encloses(r), "%s: '%s' inside what the page shows (%s in %s)" % [tag, (t as Label).text if t is Label else t.name, r, shown])
		assert_gte(r.size.y + 1.0, t.get_combined_minimum_size().y, "%s: '%s' is as tall as its text (%s)" % [tag, t.name, r.size.y])
	return texts.size()


func _intel_body(kind: int) -> void:
	_campaign(kind)
	var base_font := 0
	for scale in SCALES:
		var hq := await _hq(scale)
		var page: Control = hq._panel
		var tag := "x%.1f" % scale
		var column := page.get_node("CardColumn") as Control
		var fit := page.find_child("ThreatIntelFit", true, false) as FitBuildBox
		var intel := page.find_child("ThreatIntel", true, false) as Control
		var more := page.find_child("IntelMore", true, false) as MenuChip
		assert_not_null(intel, tag)
		assert_gte(fit.mul, fit.floor_for(fit.detail) - 0.001, "%s: THREAT INTEL's scale stays at its floor or above (%.2f)" % [tag, fit.mul])
		assert_false(fit.overflow, "%s: THREAT INTEL fits its room (mul %.2f detail %d min %s column %s)" % [tag, fit.mul, fit.detail, fit.get_combined_minimum_size(), column.size])
		# BIG-TEXT b: never smaller than at 1.0 (the holo's lettering and every line).
		assert_gte(fit.mul * scale, 1.0 - 0.001, "%s: THREAT INTEL at the 1.0 size or bigger (%.2f)" % [tag, fit.mul * scale])
		assert_gte((intel as RaidHolo)._k, 1.0 - 0.001, "%s: its header lettered at 1.0 or bigger" % tag)
		if scale <= 1.0:
			base_font = _min_font(intel)
		assert_gte(_min_font(intel), base_font, "%s: no line smaller than at 1.0 (%d px)" % [tag, base_font])
		var shown := column.get_global_rect()
		assert_true(shown.grow(1.0).encloses(intel.get_global_rect()), "%s: THREAT INTEL whole in the column (%s in %s)" % [tag, intel.get_global_rect(), shown])
		var lines := _assert_whole(intel, shown, tag)
		assert_gt(lines, 1, "%s: its lines were checked" % tag)
		assert_eq(more.visible, fit.level != 0, "%s: THREAT INTEL's MORE tab shows only when it pages" % tag)
		if scale <= 1.0:
			assert_almost_eq(fit.mul, 1.0, 0.001, "%s: no shrink at the base size" % tag)
		gut.p("%s: THREAT INTEL mul %.2f detail %d" % [tag, fit.mul, fit.detail])
		if fit.level != 0:
			assert_eq(FitBuildBox.page_of(fit.detail), 1, "%s: a paged THREAT INTEL opens on its first page" % tag)
			_assert_intel_page(intel, 1, tag)
			assert_true(shown.grow(1.0).encloses(more.get_global_rect()), "%s: the MORE tab in view (%s in %s)" % [tag, more.get_global_rect(), shown])
			assert_gte(more.get_global_rect().position.y, intel.get_global_rect().end.y - fit.tab_tuck - 1.0, "%s: the tab hangs under the holo" % tag)
			assert_eq(more.label_step, UiTheme.BODY, "%s: its word at body size" % tag)
			more.pressed.emit()
			await _frames(6)
			intel = page.find_child("ThreatIntel", true, false) as Control
			assert_eq(FitBuildBox.page_of(fit.detail), 2, "%s: MORE turns to the routes" % tag)
			assert_false(fit.overflow, "%s: page 2 fits" % tag)
			assert_gte(fit.mul * scale, 1.0 - 0.001, "%s: page 2 at the 1.0 size or bigger" % tag)
			_assert_intel_page(intel, 2, tag)
			shown = column.get_global_rect()
			_assert_whole(intel, shown, tag + " p2")
			assert_eq(more.text, hq.ORDER_BACK, "%s: the tab says BACK" % tag)
			more.pressed.emit()
			await _frames(6)
			assert_eq(FitBuildBox.page_of(fit.detail), 1, "%s: BACK returns to the threats" % tag)
		hq.get_parent().queue_free()
		await _frames(1)


## A paged THREAT INTEL shows the threats (page 1) or their routes (page 2), never both.
func _assert_intel_page(intel: Control, p: int, tag: String) -> void:
	var heads := 0
	var routes := 0
	for l in intel.find_children("Threats_*", "Label", true, false):
		heads += 1 if (l as Control).is_visible_in_tree() else 0
	for l in intel.find_children("Route_*", "Label", true, false):
		routes += 1 if (l as Control).is_visible_in_tree() else 0
	if p == 1:
		assert_gt(heads, 0, "%s: page 1 lists the threats" % tag)
		assert_eq(routes, 0, "%s: page 1 leaves the routes to page 2" % tag)
	else:
		assert_gt(routes, 0, "%s: page 2 lists the routes" % tag)
		assert_eq(heads, 0, "%s: page 2 leaves the threats to page 1" % tag)


func _order_body(kind: int) -> void:
	_campaign(kind)
	var base_font := 0
	for scale in SCALES:
		var hq := await _hq(scale)
		var page: Control = hq._panel
		var tag := "x%.1f" % scale
		var order := page.get_node("WorkOrder") as Control
		var scroll := page.find_child("WorkOrderPaper", true, false) as Control
		var fit := page.find_child("WorkOrderFit", true, false) as FitBuildBox
		var more := page.find_child("OrderMore", true, false) as Control
		assert_not_null(fit, tag)
		assert_gte(fit.mul, fit.floor_for(fit.detail) - 0.001, "%s: the order scale stays at its floor or above (%.2f)" % [tag, fit.mul])
		assert_gte(fit.mul * scale, 1.0 - 0.001, "%s: the order at the 1.0 size or bigger (%.2f)" % [tag, fit.mul * scale])
		if scale <= 1.0:
			base_font = _min_font(page.find_child("RaidCard", true, false))
		assert_gte(_min_font(page.find_child("RaidCard", true, false)), base_font, "%s: no order line smaller than at 1.0 (%d px)" % [tag, base_font])
		assert_eq(more.visible, fit.level != 0, "%s: the MORE tab shows only when the order is folded" % tag)
		gut.p("%s: work order mul %.2f detail %d rooms %s heights %s" % [tag, fit.mul, fit.detail, fit.last_rooms, fit.heights])
		var tab_top := (page.find_child("Tab_CREW", true, false) as Control).get_global_rect().position.y
		assert_lte(order.get_global_rect().end.y, tab_top + 1.0, "%s: the order ends above the tabs" % tag)
		var seen: Array[String] = []
		var shown := scroll.get_global_rect()
		var paper := page.find_child("RaidCard", true, false) as Control
		assert_true(shown.grow(TILT_SLACK).encloses(paper.get_global_rect()), "%s: the paper is whole in its room (%s in %s)" % [tag, paper.get_global_rect(), shown])
		_assert_whole(paper, shown, tag, TILT_SLACK)
		for n in ROWS:
			var l := paper.find_child(n, true, false) as Control
			if l != null and l.is_visible_in_tree():
				seen.append(n)
		if fit.detail == 0:
			assert_eq(seen.size(), ROWS.size(), "%s: every row shows on the whole order" % tag)
		else:
			var first: Array[String] = ["RaidTarget"]
			if FitBuildBox.pages_of(fit.level) == 2:
				first.append("RaidUnits")
			assert_eq(seen, first, "%s: the fold's first page keeps TARGET (and UNITS in two pages)" % tag)
			var title := paper.find_child("PaperTitle", true, false) as Control
			assert_true(title.is_visible_in_tree(), "%s: and the title" % tag)
			_assert_paper_tab(more as PaperIndexTab, paper, fit, shown, tag)
			assert_false(fit.overflow, "%s: the fold fits" % tag)
			# MORE: the rest on the next pages, every row whole; BACK on the last.
			var n_pages := FitBuildBox.pages_of(fit.level)
			assert_eq((more as MenuChip).text, hq.ORDER_MORE, "%s: page 1 says MORE" % tag)
			for i in range(1, n_pages):
				more.pressed.emit()
				await _frames(6)
				var pt := "%s p%d/%d" % [tag, i + 1, n_pages]
				assert_eq(FitBuildBox.page_of(fit.detail), i + 1, "%s: MORE turns the page" % pt)
				assert_eq((more as MenuChip).text, hq.ORDER_BACK if i == n_pages - 1 else hq.ORDER_MORE, "%s: BACK on the last page" % pt)
				paper = page.find_child("RaidCard", true, false) as Control
				shown = scroll.get_global_rect()
				assert_true(shown.grow(TILT_SLACK).encloses(paper.get_global_rect()), "%s: whole in its room (%s in %s)" % [pt, paper.get_global_rect(), shown])
				_assert_whole(paper, shown, pt, TILT_SLACK)
				_assert_paper_tab(more as PaperIndexTab, paper, fit, shown, pt)
				assert_gte(fit.mul * scale, 1.0 - 0.001, "%s: at the 1.0 size or bigger" % pt)
				for rn in ROWS:
					var l := paper.find_child(rn, true, false) as Control
					if l != null and l.is_visible_in_tree() and not seen.has(rn):
						seen.append(rn)
			assert_eq(seen.size(), ROWS.size(), "%s: the pages together carry every row (%s)" % [tag, seen])
			more.pressed.emit()
			await _frames(6)
			assert_eq(FitBuildBox.page_of((page.find_child("WorkOrderFit", true, false) as FitBuildBox).detail), 1, "%s: BACK returns to the first page" % tag)
		hq.get_parent().queue_free()
		await _frames(1)


## BIG-TEXT b: the order's MORE / BACK is a paper index tab out of the sheet's foot: under the
## footer (never over its redactions or meta line), turned with the sheet, its word at body size,
## in view and inside the sticker safe margin.
func _assert_paper_tab(tab: PaperIndexTab, paper: Control, fit: FitBuildBox, shown: Rect2, tag: String) -> void:
	assert_not_null(tab, "%s: the MORE tab is a paper index tab" % tag)
	if tab == null:
		return
	assert_true(tab.visible, "%s: the tab shows" % tag)
	assert_eq(tab.label_step, UiTheme.BODY, "%s: its word at body size" % tag)
	assert_almost_eq(tab.rotation, paper.rotation, 0.0001, "%s: it turns with the sheet" % tag)
	# In the sheet's own frame the tab starts at its foot (only its tucked top is under the sheet).
	var foot := paper.get_global_transform().affine_inverse() * tab.get_global_transform() * Vector2.ZERO
	assert_almost_eq(foot.y, paper.size.y - fit.tab_tuck, 0.5, "%s: the tab's top tucks under the sheet's foot (%s)" % [tag, foot])
	assert_gte(foot.y + 0.5, paper.size.y - HqLayout.PAGE_TAB_TUCK * Settings.text_scale, "%s: never over the footer" % tag)
	var r := tab.get_global_rect()
	assert_true(shown.grow(TILT_SLACK).encloses(r), "%s: the tab in view (%s in %s)" % [tag, r, shown])
	assert_true(Fx.sticker_safe_rect(SCREEN).grow(1.0).encloses(r), "%s: inside the sticker safe margin (%s)" % [tag, r])


func test_no_fit_floor_is_under_the_1_0_size() -> void:
	var box := FitBuildBox.new()
	add_child_autofree(box)
	var page1 := FitBuildBox.fold(2) + 1
	for scale in SCALES:
		Settings.set_text_scale(scale)
		for d in [0, page1]:
			assert_gte(box.floor_for(d) * scale, 1.0 - 0.001, "x%.1f detail %d: the floor is the 1.0 size or bigger" % [scale, d])
		assert_almost_eq(box.floor_for(page1), HqLayout.base_floor(scale), 0.001, "x%.1f: a page shrinks to the 1.0 size, no further" % scale)
	assert_almost_eq(HqLayout.base_floor(2.0), 0.5, 0.0001, "0.5 at 2.0")


func test_the_fit_box_shrinks_to_the_floor_then_folds() -> void:
	Settings.set_text_scale(2.0)  # BIG-TEXT b: at 1.0 nothing shrinks (the floor is the 1.0 size)
	var box := FitBuildBox.new()
	add_child_autofree(box)
	box.builder = func(m: float, d: int) -> Control:
		var l := Label.new()
		l.text = "line"
		l.custom_minimum_size.y = 100.0 * m * (1.0 if d == 0 else 0.2)
		return l
	box.details = [0, FitBuildBox.fold(2)]
	box.fit(100.0, 1000.0)
	assert_almost_eq(box.mul, 1.0, 0.001, "roomy: no shrink")
	box.fit(100.0, 90.0)
	assert_lte(box.mul, 0.91, "tight: smaller")
	assert_gte(box.mul, HqLayout.FIT_FLOOR - 0.001, "never below the floor")
	assert_eq(box.detail, 0, "it fit whole")
	box.fit(100.0, 50.0)
	assert_eq(box.level, FitBuildBox.fold(2), "folded when the floor is still too tall")
	assert_eq(box.detail, FitBuildBox.fold(2) + 1, "on its first page")
	assert_false(box.overflow, "and the fold fits")
	box.page = 1
	box.fit(100.0, 50.0)
	assert_eq(box.detail, FitBuildBox.fold(2) + 2, "its second page")
	box.fit(100.0, 5.0)
	assert_true(box.overflow, "nothing fits: flagged, at the floor")
	assert_almost_eq(box.mul, box.floor_for(box.detail), 0.001, "at the floor")


## BIG-TEXT b (art director, 2): from 1.6, short of room, YOUR NETWORK is one terminal row (CORE and
## its forecast, the node count at the right, never smaller than at 1.0); focus brings the whole
## block back (on CORE's name), and it folds again when the focus leaves.
func _network_body(kind: int) -> void:
	_campaign(kind)
	for scale in SCALES:
		var hq := await _hq(scale)
		var page: Control = hq._panel
		var tag := "x%.1f" % scale
		var column := page.get_node("CardColumn") as Control
		var network := page.find_child("NodeOrders", true, false) as RaidTerminal
		var row := network.find_child("NetworkRow", true, false) as Control
		gut.p("%s: YOUR NETWORK collapsed %s one row %s" % [tag, hq.network_collapsed(), hq.network_one_row()])
		if scale < HqLayout.NETWORK_ROW_SCALE - 0.001:
			assert_false(hq.network_one_row(), "%s: one row only from 1.6" % tag)
			assert_false(row.visible, "%s: no one row" % tag)
		if not hq.network_one_row():
			assert_true(network.header_shown(), "%s: the header shows" % tag)
			hq.get_parent().queue_free()
			await _frames(1)
			continue
		assert_true(row.is_visible_in_tree(), "%s: the one row shows" % tag)
		assert_false(network.header_shown(), "%s: no header over it" % tag)
		var core := row.find_child("NetworkRowCore", true, false) as Button
		var count := row.find_child("NetworkRowCount", true, false) as Label
		var home := RunManager.campaign.grid.home_site_id
		assert_true(core.text.begins_with(tr(hq.NETWORK_ROW) % [hq.site_name(home).to_upper(), ""]), "%s: CORE (%s)" % [tag, core.text])
		assert_true(core.text.contains("→"), "%s: and its forecast (%s)" % [tag, core.text])
		assert_eq(count.text, network.tag_label.text, "%s: the node count at the right" % tag)
		assert_gte(core.get_theme_font_size(&"font_size"), UiTheme.font_px_at(UiTheme.BODY, 1.0), "%s: never smaller than at 1.0" % tag)
		var font := core.get_theme_font(&"font")
		var words_w := font.get_string_size(core.text, HORIZONTAL_ALIGNMENT_LEFT, -1, core.get_theme_font_size(&"font_size")).x
		assert_lte(words_w, core.size.x + 1.0, "%s: the row's words whole on one line (%.0f in %.0f)" % [tag, words_w, core.size.x])
		assert_gt(count.get_global_rect().position.x, core.get_global_rect().position.x, "%s: the count at the right" % tag)
		var shown := column.get_global_rect().grow(1.0)
		assert_true(shown.encloses(row.get_global_rect()), "%s: the row in view" % tag)
		# Focus opens the whole block on CORE's name; leaving it folds it again.
		core.grab_focus()
		await _frames(4)
		assert_false(hq.network_collapsed(), "%s: focus brings the whole block back" % tag)
		var name_btn := network.find_child("Target_%s" % home, true, false) as Control
		assert_eq(page.get_viewport().gui_get_focus_owner(), name_btn, "%s: the focus on CORE's name" % tag)
		assert_true(shown.encloses(name_btn.get_global_rect()), "%s: CORE's name in view" % tag)
		(page.get_node("MapCursor") as Control).grab_focus()
		await _frames(4)
		assert_true(hq.network_one_row(), "%s: one row again when the focus leaves" % tag)
		hq.get_parent().queue_free()
		await _frames(1)


func test_your_network_is_one_row_from_1_6_review_raid() -> void:
	await _network_body(0)


func test_your_network_is_one_row_from_1_6_wide_network() -> void:
	await _network_body(1)


## BIG-TEXT b (art director, 4a): the letterhead's corp name keeps left of the seal at every size:
## it fits that width (never under the 1.0 size), wraps to two lines, then ends in an ellipsis.
func test_the_letterhead_name_keeps_left_of_the_seal() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		for corp: StringName in [&"solace", &"meridian", &"halcyon", &"orbital"]:
			var sheet := RaidPaper.new(corp, "COLLECTIONS: FIRST NOTICE", RaidPaper.STAMP_INTERCEPTED, "WO 25-SB-452")
			add_child_autofree(sheet)
			sheet.size = Vector2(HqLayout.ORDER_WIDTH * HqLayout.words_scale(scale), 400.0)
			await _frames(1)
			var lh := sheet.paper
			var fit := lh.letterhead_fit()
			var tag := "x%.1f %s" % [scale, corp]
			var font := Palette.body_medium()
			assert_gte(int(fit["px"]), UiTheme.font_px_at(UiTheme.LABEL, 1.0), "%s: never smaller than at 1.0" % tag)
			var right := UiTheme.SP_L + lh.name_width()
			assert_lte(right, sheet.size.x - sheet.seal_reserve() + 0.5, "%s: the name's room ends left of the seal" % tag)
			for line: String in fit["lines"]:
				assert_lte(font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, int(fit["px"])).x, lh.name_width() + 0.5, "%s: '%s' fits left of the seal" % [tag, line])
			assert_true(" ".join(fit["lines"]) == lh.letterhead_text() or String(fit["lines"][-1]).ends_with(CorpPaperPanel.ELLIPSIS), "%s: the whole name (M14 FOLLOW-UP: the letterhead name), or cut with an ellipsis" % tag)
			sheet.queue_free()
	# The pure fit: wider than the room -> two lines -> an ellipsis.
	var f := Palette.body_medium()
	var one := CorpPaperPanel.fit_name(f, "MERIDIAN FREIGHTS", 36, 18, 2000.0, 80.0)
	assert_eq(Array(one["lines"]), ["MERIDIAN FREIGHTS"], "room: one line")
	assert_eq(int(one["px"]), 36, "room: at its size")
	var w := f.get_string_size("MERIDIAN", HORIZONTAL_ALIGNMENT_LEFT, -1, 18).x + 4.0
	var two := CorpPaperPanel.fit_name(f, "MERIDIAN FREIGHTS", 36, 18, w + f.get_string_size("FREIGHTS", HORIZONTAL_ALIGNMENT_LEFT, -1, 18).x * 0.2, 80.0)
	assert_eq(PackedStringArray(two["lines"]).size(), 2, "narrow: two lines (%s)" % [two])
	var cut := CorpPaperPanel.fit_name(f, "SUPERCALIFRAGILISTIC", 36, 18, 60.0, 80.0)
	assert_true(String(cut["lines"][0]).ends_with(CorpPaperPanel.ELLIPSIS), "one long word: cut with an ellipsis (%s)" % [cut])
	assert_eq(int(cut["px"]), 18, "at the 1.0 size")
	Settings.set_text_scale(1.0)


func test_threat_intel_is_whole_at_every_text_size_review_raid() -> void:
	await _intel_body(0)


func test_threat_intel_is_whole_at_every_text_size_wide_network() -> void:
	await _intel_body(1)


func test_the_work_order_is_whole_or_folded_at_every_text_size_review_raid() -> void:
	await _order_body(0)


func test_the_work_order_is_whole_or_folded_at_every_text_size_wide_network() -> void:
	await _order_body(1)
