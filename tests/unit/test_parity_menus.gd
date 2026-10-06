extends GutTest
## M14 parity, designer group ruling 2026-10-05 for the menus: the codex and the stats take the
## build's structure reworked in v2 (CODEX-01: tabs in rows over one paper page with glyphs;
## STATS-01: stat tiles with icons, achievement badges, paper run cards); the options match
## round 31's concept (OPT-01: a centred terminal with its OPTIONS sticker, RESET TO DEFAULTS;
## OPT-02: the rows' words; OPT-03: the right column). Every setting keeps its behaviour, the
## pad reaches every tab and tile, and the pages fit at text 1.0 / 1.6 / 2.0.

const TITLE := "res://scenes/menu/title_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _saved: Dictionary
var _profile: ProfileState


func before_each() -> void:
	_saved = Settings.snapshot()
	Settings.set_text_scale(1.0)
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	RunManager.save_slot = "gut_parity_menus"
	RunManager.reset()
	_profile = RunManager.profile


func after_each() -> void:
	RunManager.profile = _profile
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true
	AudioDirector.muted = false
	Settings.restore(_saved)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _title() -> Control:
	return add_child_autofree(load(TITLE).instantiate())


func _focus_down(c: Control) -> Control:
	return c.get_node_or_null(c.focus_neighbor_bottom) as Control if not c.focus_neighbor_bottom.is_empty() else null


## The node `n` under `root` that is shown now (a section swap leaves the old one queued).
func _live(root: Node, n: String) -> Node:
	for c in root.find_children(n, "", true, false):
		if not c.is_queued_for_deletion() and (c as CanvasItem).visible:
			return c
	return null


func _pad(button: JoyButton) -> InputEventJoypadButton:
	var e := InputEventJoypadButton.new()
	e.button_index = button
	e.pressed = true
	return e


# --- CODEX-01 -------------------------------------------------------------------------------------

func test_the_codex_is_tabs_over_one_paper_page_with_glyphs() -> void:
	var t := _title()
	await _frames(2)
	t.show_codex()
	await _frames()
	var book := t._panel.find_child("Codex", true, false) as CodexBook
	assert_not_null(book, "the codex is a CodexBook")
	if book == null:
		return
	var keys := Codex.entries(RunManager.lookup(), RunManager.profile).keys()
	assert_eq(book.tabs.get_child_count(), keys.size(), "a tab per section")
	for k in keys:
		var tab := book.tabs.find_child(CodexBook.tab_name(String(k)), false, false) as MenuChip
		assert_not_null(tab, "%s has its tab" % k)
		if tab != null:
			assert_eq(tab.plate, &"tab", "%s wears round 31's tab plate" % k)
	assert_true(book.tabs is HFlowContainer, "at 1.0 the tabs wrap in rows")
	var rows := {}
	for tab in book.tabs.get_children():
		rows[roundi((tab as Control).position.y)] = true
	assert_eq(rows.size(), 2, "two rows of tabs at 1280 (the build's)")
	assert_eq(book.section, String(keys[0]), "the first section opens")
	assert_true(book.current_tab().selected, "its tab is filled")
	assert_eq(book.column_count(), 2, "two columns of entries on the title page")
	assert_eq(book.heading.text, tr(String(keys[0])).to_upper(), "the page's heading names the section")
	assert_not_null(book._paper.material, "the page is the art pass's paper stock")
	assert_eq((book._paper.material as ShaderMaterial).shader, CodexBook.PAPER_SHADER)


func test_every_entry_has_its_glyph_from_the_atlas_or_the_icon_set() -> void:
	var entries := Codex.entries(RunManager.lookup())
	var book: CodexBook = add_child_autofree(CodexBook.new(entries, 0.0, SCREEN.size.x))
	await _frames(1)
	for section in ["Slices", "Statuses & precision", "Firmware", "Daemons", "Ring segments", "Classes", "Cards"]:
		book.show_section(section)
		var glyphs := book.columns.find_children("Glyph", "", true, false)
		assert_eq(glyphs.size(), (entries[section] as Array).size(), "%s: a glyph per entry" % section)
	book.show_section("Slices")
	for g in book.columns.find_children("Glyph", "GlyphIcon", true, false):
		assert_ne((g as GlyphIcon).glyph, &"", "a slice draws its 1C atlas glyph")
	var slice_glyphs := book.columns.find_children("Glyph", "GlyphIcon", true, false)
	assert_eq(slice_glyphs.size(), (entries["Slices"] as Array).size(), "every slice is an atlas glyph")
	if not slice_glyphs.is_empty():
		var first: Dictionary = entries["Slices"][0]
		assert_eq((slice_glyphs[0] as GlyphIcon).fill, Palette.slice_color(int(first["slice"])), "in its slice colour")
	book.show_section("Statuses & precision")
	assert_gte(book.columns.find_children("Glyph", "GlyphIcon", true, false).size(), 4, "the four statuses are atlas glyphs")
	book.show_section("Firmware")
	var fw := book.columns.find_children("Glyph", "GlyphIcon", true, false)
	assert_gt(fw.size(), 0, "Firmware draws its atlas glyphs")
	for item in entries["Corporations"]:
		if (item as Dictionary).has("corporation"):
			assert_eq(CodexBook.atlas_glyph("Corporations", item), &"", "a corporation draws its crest (no atlas glyph)")
	assert_eq(CodexBook.atlas_glyph("Lexicon", entries["Lexicon"][0]), &"", "the lexicon draws the icon set's mark")


func test_an_entry_never_says_its_title_twice() -> void:
	assert_eq(CodexBook.body_text("SHIM", "SHIM: deals damage."), "deals damage.", "the audit's SHIM SHIM:")
	assert_eq(CodexBook.body_text("Patch+", "Firmware Patch+\nHeals."), "Heals.", "the kind and the title go")
	assert_eq(CodexBook.body_text("Jab", "Jab (RAM 1)\nDeals 3."), "(RAM 1)\nDeals 3.", "the numbers stay")
	assert_eq(CodexBook.body_text("leash", "A subscription implant."), "A subscription implant.", "other text as it is")
	var entries := Codex.entries(RunManager.lookup())
	var book: CodexBook = add_child_autofree(CodexBook.new(entries, 0.0, SCREEN.size.x))
	await _frames(1)
	for body in book.columns.find_children("Body", "Label", true, false):
		var title := ((body as Label).get_parent().get_node("Title") as Label).text
		assert_false((body as Label).text.begins_with(title + ":"), "%s says its name once" % title)


func test_the_story_heads_the_tabs_when_a_campaign_has_one() -> void:
	var entries := {Codex.STORY: [{"title": "Beat one", "text": "Something happened."}], "Slices": Codex.entries(RunManager.lookup())["Slices"]}
	var book: CodexBook = add_child_autofree(CodexBook.new(entries, 0.0, SCREEN.size.x))
	await _frames(1)
	assert_eq(book.section, Codex.STORY, "STORY first (HQ-B Q8)")
	assert_eq(book.tabs.get_child(0).name, CodexBook.tab_name(Codex.STORY))
	assert_true(CodexBook.SECTION_ICONS.has(Codex.STORY), "STORY's entries have their icon")
	assert_string_contains(book.all_text(), "Beat one")


func test_the_pad_switches_tabs_and_scrolls_the_page() -> void:
	var t := _title()
	await _frames(2)
	t.show_codex()
	await _frames()
	var book := t._panel.find_child("Codex", true, false) as CodexBook
	var keys := book.entries.keys()
	book._unhandled_input(_pad(JOY_BUTTON_RIGHT_SHOULDER))
	assert_eq(book.section, String(keys[1]), "RB: the next tab")
	assert_eq(get_viewport().gui_get_focus_owner(), book.current_tab(), "focus on the tab opened")
	book._unhandled_input(_pad(JOY_BUTTON_LEFT_SHOULDER))
	book._unhandled_input(_pad(JOY_BUTTON_LEFT_SHOULDER))
	assert_eq(book.section, String(keys[keys.size() - 1]), "LB wraps to the last tab")
	await _frames()
	# The tabs go down to the page (one focus stop), the page down to Back.
	var down := _focus_down(book.current_tab())
	assert_eq(down, book.page, "a tab's down is the page")
	var back := t._panel.find_child("Back", true, false) as Control
	assert_eq(_focus_down(book.page), back, "the page's down is Back")
	book.show_section("Cards")  # a long section: it scrolls
	await _frames()
	book.page.grab_focus()
	var e := InputEventAction.new()
	e.action = &"ui_down"
	e.pressed = true
	assert_true(book.fit.overflowing(), "the cards run past the view")
	book._on_page_input(e)
	assert_gt(book.fit.scroll.scroll_vertical, 0, "down scrolls the page")
	assert_eq(get_viewport().gui_get_focus_owner(), book.page, "and keeps the focus there")


func test_the_codex_fits_on_the_title_and_in_the_pause_menu_at_every_text_scale() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var t := _title()
		await _frames(2)
		t.show_codex()
		await _frames(4)
		var book := t._panel.find_child("Codex", true, false) as CodexBook
		assert_true(SCREEN.encloses(book.get_global_rect()), "title codex on screen at %.1f" % scale)
		assert_eq(book.tabs is HBoxContainer, scale >= CodexBook.ONE_ROW_FROM, "one scrolling row of tabs from %.1f (%.1f)" % [CodexBook.ONE_ROW_FROM, scale])
		t.queue_free()
		var menu: PauseMenu = add_child_autofree(PauseMenu.new())
		await _frames(2)
		menu.show_codex()
		await _frames(4)
		assert_false(menu._panel.visible, "the sticker menu gives the codex its place")
		var r := menu.codex_note.get_parent().get_global_rect() as Rect2
		assert_true(SCREEN.encloses(r), "pause codex %s on screen at %.1f" % [r, scale])
		assert_almost_eq(r.get_center().x, SCREEN.get_center().x, 2.0, "centred at %.1f" % scale)
		menu._close_sub()
		await _frames(1)
		assert_true(menu._panel.visible, "Back shows the menu again")
		menu.queue_free()
		await _frames(1)


# --- STATS-01 -------------------------------------------------------------------------------------

func _stats_profile() -> ProfileState:
	var p := ProfileState.new()
	p.campaigns_started = 3
	p.campaigns_won = 1
	p.runs_completed = 14
	p.raids_won = 2
	p.stats["perfects"] = 9
	p.stats["cycles"] = 640
	p.achievements.append(StringName(str(Achievements.DEFS[0]["id"])))
	p.run_history.append({"corporation": "solace", "tier": 1, "site": "t1_a", "outcome": "completed", "cycles": 40, "banked": 12})
	p.run_history.append({"corporation": "solace", "tier": 2, "site": "t2_intel", "outcome": "died", "cycles": 18, "banked": 0})
	return p


func test_stats_are_tiles_badges_and_run_cards() -> void:
	RunManager.profile = _stats_profile()
	var t := _title()
	await _frames(2)
	t.show_stats()
	await _frames()
	var tiles := t._panel.find_child("StatGrid", true, false) as GridContainer
	assert_not_null(tiles)
	if tiles == null:
		return
	assert_eq(tiles.get_child_count(), 12, "the build's twelve stats")
	var by_kind := {}
	for c in tiles.get_children():
		by_kind[(c as StatTile).kind] = (c as StatTile).value
	assert_eq(by_kind.get(StatIcon.CAMPAIGNS), "3", "campaigns started")
	assert_eq(by_kind.get(StatIcon.RUNS), "14")
	assert_eq(by_kind.get(StatIcon.RAIDS), "2/0", "raids won / lost")
	assert_eq(by_kind.get(StatIcon.CYCLES), "640")
	assert_eq(by_kind.get(StatIcon.BADGES), "1/%d" % Achievements.DEFS.size())
	assert_eq(tiles.columns, 6, "two rows of six at 1280")
	var ach := t._panel.find_child("Achievements", true, false) as CrtWindow
	assert_eq(ach.tag_label.text, "1/%d" % Achievements.DEFS.size(), "the count on the window's tag")
	var badges: Array[Node] = t._panel.find_children("Badge_*", "AchievementBadge", true, false)
	assert_eq(badges.size(), Achievements.DEFS.size(), "a badge per achievement")
	var earned: Array = badges.filter(func(b: Node) -> bool: return (b as AchievementBadge).earned)
	assert_eq(earned.size(), 1, "one earned")
	assert_true(String((badges[1] as AchievementBadge).tooltip_text).contains(tr("Not earned yet.")), "a locked badge says so")
	var cards := t._panel.find_child("Receipts", true, false) as GridContainer
	assert_eq(cards.get_child_count(), 2, "a paper card per run")
	var died := cards.get_child(1) as RunReceipt
	assert_true(died.words().has(tr("Died").to_upper()), "the outcome stamped")
	assert_not_null(t._panel.find_child("BestIceByCorp", true, false), "best ICE per corporation kept")


func test_no_runs_is_the_designed_empty_card() -> void:
	RunManager.profile = ProfileState.new()
	var t := _title()
	await _frames(2)
	t.show_stats()
	await _frames()
	var cards := t._panel.find_child("Receipts", true, false) as GridContainer
	assert_eq(cards.get_child_count(), 1)
	assert_eq(cards.get_child(0).name, "NoRuns")


func test_the_pad_walks_the_tiles_badges_and_cards() -> void:
	RunManager.profile = _stats_profile()
	var t := _title()
	await _frames(2)
	t.show_stats()
	await _frames()
	var tiles := t._panel.find_child("StatGrid", true, false) as GridContainer
	var cols := tiles.columns
	var first := tiles.get_child(0) as Control
	assert_eq(first.get_node(first.focus_neighbor_right), tiles.get_child(1), "right: the next tile")
	assert_eq(_focus_down(first), tiles.get_child(cols), "down: the tile under it")
	var last_row := tiles.get_child(tiles.get_child_count() - 1) as Control
	var badges := t._panel.find_child("Badges", true, false) as GridContainer
	assert_eq(_focus_down(last_row), badges.get_child(0), "the last row goes down to the badges")
	var cards := t._panel.find_child("Receipts", true, false) as GridContainer
	var back: Node = t._panel.find_child("Back", true, false)
	assert_eq(_focus_down(cards.get_child(cards.get_child_count() - 1) as Control), back, "the cards go down to Back")
	for c in tiles.get_children() + badges.get_children() + cards.get_children():
		assert_ne((c as Control).focus_mode, Control.FOCUS_NONE, "%s is a focus stop" % c.name)


func test_the_stats_fit_at_every_text_scale() -> void:
	RunManager.profile = _stats_profile()
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var t := _title()
		await _frames(2)
		t.show_stats()
		await _frames(4)
		var fit := t._panel.find_child("StatsScroll", true, false) as FitScroll
		var floor_y: float = (t.ticker as Control).get_global_rect().position.y
		assert_lte(fit.get_global_rect().end.y, floor_y + 1.0, "the sheet's view over the ticker at %.1f" % scale)
		var back := t._panel.find_child("Back", true, false) as Control
		assert_lte(back.get_global_rect().end.y, floor_y + 1.0, "Back over the ticker at %.1f" % scale)
		for c in (t._panel.find_child("StatGrid", true, false) as Node).get_children():
			assert_lte((c as Control).get_global_rect().end.x, SCREEN.end.x, "%s inside the screen at %.1f" % [c.name, scale])
		t.queue_free()
		await _frames(1)


# --- OPT-01 / OPT-02 / OPT-03 -----------------------------------------------------------------------

func test_title_options_are_a_centred_terminal_with_its_sticker() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var t := _title()
		await _frames(2)
		t.show_options()
		await _frames(4)
		var panel := t._panel.find_children("*", "SettingsPanel", true, false)[0] as Control
		var r := panel.get_global_rect()
		assert_true(SCREEN.encloses(r), "options %s on screen at %.1f" % [r, scale])
		assert_almost_eq(r.get_center().x, SCREEN.get_center().x, 2.0, "centred at %.1f" % scale)
		if scale == 1.0:
			assert_true((panel as SettingsPanel).two_columns(), "two columns at 1.0")
			assert_almost_eq(r.size.x, SettingsPanel.WIDTH_TWO, 1.0, "round 31: a centred terminal, not the page's width")
			var tiles := (panel as SettingsPanel).colorblind_tiles.tiles
			assert_almost_eq(tiles[0].get_global_rect().position.y, tiles[tiles.size() - 1].get_global_rect().position.y, 1.0, "the colour-blind tiles keep one row")
		var sticker := (panel as SettingsPanel).title_sticker
		assert_true(sticker.visible, "the OPTIONS sticker")
		assert_gte(sticker.get_global_rect().position.y, 0.0, "the sticker on screen at %.1f" % scale)
		t.queue_free()
		await _frames(1)


func test_pause_options_open_centred_in_the_menus_place() -> void:
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames(2)
	menu.show_options()
	await _frames(3)
	var panel := menu.settings_panel
	assert_false(menu._panel.visible, "the sticker menu hides behind")
	assert_false(panel.compact, "the full terminal (round 31: > PAUSED // OPTIONS)")
	assert_true(panel.title_sticker.visible, "with its OPTIONS sticker")
	assert_eq(panel.window.title, "%s // %s" % [tr("PAUSED"), tr("OPTIONS")])
	var r := panel.get_global_rect()
	assert_almost_eq(r.get_center().x, SCREEN.get_center().x, 2.0, "centred")
	assert_true(SCREEN.encloses(r))
	panel.closed.emit()
	await _frames(1)
	assert_true(menu._panel.visible, "closing shows the menu again")
	assert_null(menu.settings_panel)


func test_reset_to_defaults_resets_the_open_tab_only() -> void:
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	await _frames(1)
	assert_not_null(panel.reset_button, "RESET TO DEFAULTS in the foot")
	Settings.set_reduce_motion(true)
	Settings.set_heat_glitch(true)
	Settings.set_colorblind_mode(&"deutan")
	Settings.set_master_volume(0.3)
	panel.sync_widgets()
	panel.show_section("Accessibility")
	panel.reset_button.pressed.emit()
	assert_false(Settings.reduce_motion, "reduce motion back to off")
	assert_false(Settings.heat_glitch, "Heat glitch back to off")
	assert_eq(Settings.colorblind_mode, &"off", "colour-blind back to off")
	assert_almost_eq(Settings.master_volume, 0.3, 0.001, "another tab's setting is left alone")
	assert_false(panel.reduce_motion_check.button_pressed, "the row shows it")
	assert_true(panel.colorblind_tiles.tiles[0].selected, "the OFF tile shows it")
	panel.show_section("Audio")
	panel._unhandled_input(_pad(JOY_BUTTON_Y))
	assert_almost_eq(Settings.master_volume, 1.0, 0.001, "pad Y resets the open tab (Audio)")
	assert_almost_eq(panel.master_slider.value, 1.0, 0.001, "the slider shows it")


func test_the_rows_say_what_round_31_says() -> void:
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	await _frames(1)
	var expect := {panel.reduce_check: ["REDUCE EFFECTS", "No scanlines, flicker, chromatic or distortion"],
		panel.flash_check: ["FLASH LIMITER", "At most 3 flashes a second. On by default."],
		panel.high_contrast_check: ["HIGH CONTRAST", "Opaque panels, 7:1 text and thick edges"],
		panel.subtitles_check: ["SUBTITLES", "Every spoken line, with the speaker's name"]}
	for row in expect:
		assert_eq(Array((row as CrtSwitch).parts()), expect[row], "the concept's words")
	assert_eq((panel.assist_check as CrtSwitch).parts()[0], "ASSIST MODE")
	assert_string_contains((panel.assist_check as CrtSwitch).parts()[1], "New campaigns:")
	assert_eq((panel.heat_glitch_check as CrtSwitch).parts()[0], "HEAT GLITCH")
	# The rows' order is the concept's.
	var left := _live(panel, "Left")
	var names: Array[String] = []
	for c in left.get_children():
		if c is CrtSwitch:
			names.append((c as CrtSwitch).parts()[0])
	assert_eq(names, ["REDUCE EFFECTS", "REDUCE MOTION", "FLASH LIMITER", "HEAT GLITCH", "HIGH CONTRAST", "SUBTITLES", "SUBTITLES TYPE IN", "ASSIST MODE"] as Array[String])


func test_the_right_column_keeps_scale_tiles_and_previews() -> void:
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	await _frames(1)
	var right := _live(panel, "Right")
	for w in [panel._scale_block, panel.colorblind_tiles, panel.resolve_tiles, panel.glitch_preview]:
		assert_true(right.is_ancestor_of(w), "%s in the right column" % w.name)
	assert_false(panel.skin_option.is_inside_tree(), "the skin picker waits for Display")
	panel.show_section("Display")
	assert_true(panel.skin_option.is_inside_tree(), "the skin picker is on Display (ART-12)")
