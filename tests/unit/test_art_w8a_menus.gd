extends GutTest
## Art pass W8a (ART_BIBLE §2, §3.3, §5.3, §6.4-§6.5, §10, §11 title family, §12): the shared
## GLASS / PAPER panels size to their content and scroll inside, page transitions keep one
## direction per material (fade under reduce motion), modals close before a page changes,
## the baked logo, case-file slots with a Danger Delete, Options on kit components in one
## size across tabs, the codex spread, stats badges, the pause menu sized to its content
## with the code behind a CodeField, and every title page at text scale 2.0.

const TITLE := "res://scenes/menu/title_scene.tscn"
const SLOT := "gut_test_w8a"

var _saved_settings: Dictionary


func before_each() -> void:
	AudioDirector.muted = true
	_saved_settings = Settings.to_dict()
	RunManager.scene_switching_enabled = false
	RunManager.save_slot = SLOT
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = false
	Settings.from_dict(_saved_settings)
	Settings.save_settings()
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _all(root: Node) -> Array[Node]:
	var out: Array[Node] = [root]
	for c in root.get_children():
		out.append_array(_all(c))
	return out


# --- 1. Shared panels ---------------------------------------------------------------------------

func test_glass_window_type_comes_from_the_scale_and_has_a_scrim() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var w := TerminalWindow.new("SYSTEM ONLINE")
		w.tag_label.text = "120"
		add_child_autofree(w)
		await _frames()
		var px := w.title_label.get_theme_font_size(&"font_size")
		assert_true(px == UiTheme.font_px(TerminalWindow.TITLE_STEP) or px == UiTheme.font_px(TerminalWindow.FIT_STEP),
			"the title is a step x the text scale (%d at %.1f)" % [px, scale])
		assert_eq(w.tag_label.get_theme_font_size(&"font_size"), UiTheme.font_px(TerminalWindow.TAG_STEP))
		assert_not_null(w.scrim, "a SCRIM behind the glass")
		assert_eq(w.scrim.get_rect(), Rect2(Vector2.ZERO, w.size), "the scrim covers the whole window")


func test_a_long_title_never_widens_its_window() -> void:
	var w := TerminalWindow.new("A VERY LONG WINDOW TITLE THAT WOULD PUSH THE GLASS WIDE // MORE WORDS HERE")
	var l := Label.new()
	l.text = "short"
	w.body.add_child(l)
	add_child_autofree(w)
	await _frames()
	assert_true(w.get_combined_minimum_size().x < 400.0, "the body sets the width (%.0f)" % w.get_combined_minimum_size().x)


func test_high_contrast_makes_the_scrim_opaque() -> void:
	Settings.set_high_contrast(true)
	var s := GlassScrim.new()
	add_child_autofree(s)
	assert_true(s.opaque(), "opaque under high contrast")
	Settings.set_high_contrast(false)
	s.sync()
	assert_false(s.opaque(), "a blur otherwise")
	assert_eq((s.material as ShaderMaterial).shader, GlassScrim.SHADER)


func test_panels_fit_their_content_and_scroll_past_the_cap() -> void:
	var host := VBoxContainer.new()
	add_child_autofree(host)
	var w := TerminalWindow.new("LIST")
	for i in 30:
		var l := Label.new()
		l.text = "row %d" % i
		w.body.add_child(l)
	host.add_child(w)
	await _frames()
	assert_true(w.empty_share() <= 0.25, "sized to its content (%.2f empty)" % w.empty_share())
	w.scroll_body(160.0)
	await _frames()
	assert_true(w.fit.overflowing(), "past the cap it scrolls")
	assert_true(w.fit.scroll.size.y <= 161.0, "the view keeps to the cap (%.0f)" % w.fit.scroll.size.y)
	assert_true(w.empty_share() <= 0.25, "still no empty band (%.2f)" % w.empty_share())
	var p := ZinePanel.new("NOTE")
	var big := Label.new()
	big.text = "words"
	big.custom_minimum_size = Vector2(200, 120)
	p.content.add_child(big)
	host.add_child(p)
	await _frames()
	assert_true(p.size.y >= 120.0, "a zine panel is as tall as its content")
	assert_true(p.empty_share() <= 0.25, "and no emptier (%.2f)" % p.empty_share())
	assert_eq(p.title_size, UiTheme.font_px(ZinePanel.TITLE_STEP), "the paper title is on the scale")


# --- 2. Page transitions and modals -------------------------------------------------------------

func test_glass_slides_from_the_right_and_paper_drops_whatever_the_caller_asks() -> void:
	Motion.force_live = true
	var holder := Control.new()
	add_child_autofree(holder)
	var glass := Control.new()
	holder.add_child(glass)
	var t := PageTransition.enter(glass, PageTransition.Look.GLASS, Callable(), -1)
	assert_not_null(t)
	assert_eq(t.direction, 1, "glass always comes from the right (§10)")
	assert_false(t.fade_only)
	assert_true(PageTransition.seconds_for(PageTransition.Look.GLASS) <= PageTransition.PAGE_BUDGET)
	assert_true(PageTransition.seconds_for(PageTransition.Look.PAPER) <= PageTransition.PAGE_BUDGET)
	for i in 4:
		await get_tree().process_frame
	await get_tree().process_frame
	assert_true(glass.position.x >= 0.0, "it moves in from the right, never from the left (%.1f)" % glass.position.x)
	t.finish()


func test_reduce_motion_cross_fades_in_place() -> void:
	Motion.force_live = true
	Settings.set_reduce_motion(true)
	var holder := Control.new()
	add_child_autofree(holder)
	var page := Control.new()
	holder.add_child(page)
	var t := PageTransition.enter(page, PageTransition.Look.GLASS)
	assert_true(t.fade_only, "reduce motion: a cross-fade")
	for i in 6:
		await get_tree().process_frame
		assert_eq(page.position, Vector2.ZERO, "the page never moves")
	t.finish()
	assert_eq(page.modulate.a, 1.0)


func test_modals_open_and_close_within_budget_never_a_cut() -> void:
	assert_true(Motion.seconds(&"modal_in") > 0.0 and Motion.seconds(&"modal_in") <= PageTransition.MODAL_BUDGET)
	assert_true(Motion.seconds(&"modal_out") > 0.0 and Motion.seconds(&"modal_out") <= PageTransition.MODAL_BUDGET)
	Motion.force_live = true
	var m := Control.new()
	add_child(m)
	PageTransition.open_modal(m)
	assert_true(PageTransition.modal_open(self))
	assert_true(m.modulate.a < 1.0, "it fades in, not a cut")
	var done := [false]
	PageTransition.close_modal(m, func() -> void: done[0] = true)
	assert_false(PageTransition.modal_open(self), "a closing modal no longer counts as open")
	await get_tree().process_frame
	assert_true(is_instance_valid(m), "it fades out first")
	var took := await BoundedWait.timed(get_tree(), func() -> bool: return done[0], PageTransition.MODAL_BUDGET * BoundedWait.SLACK)
	assert_true(done[0], "then it is gone and the caller goes on")
	assert_true(took <= PageTransition.MODAL_BUDGET + 0.05, "within the modal budget (%.3f s)" % took)
	assert_false(is_instance_valid(m))


func test_no_page_change_under_an_open_modal() -> void:
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	await _frames()
	title.confirm_quit()
	assert_true(title.confirm_visible())
	assert_true(PageTransition.modal_open(title), "the confirm is a modal")
	var seen: Array = []
	PageTransition.after_modals(title, func() -> void: seen.append(PageTransition.modal_open(title)))
	await _frames()
	assert_eq(seen, [false], "the page change runs once, with no modal open")
	title.confirm_quit()
	title.show_codex()
	await _frames()
	assert_false(title.confirm_visible(), "a page change closes the confirm first")
	assert_eq(title.panel_name, "codex")


# --- 3. Title ------------------------------------------------------------------------------------

func _count(root: Node, cls: String) -> int:
	var n := 0
	for c in _all(root):
		if c.is_class(cls) or (c.get_script() != null and (c.get_script() as Script).get_global_name() == cls):
			n += 1
	return n


func _primaries(root: Node) -> Array[Control]:
	var out: Array[Control] = []
	for c in _all(root):
		if c is Button and (c as Button).theme_type_variation == UiTheme.PRIMARY and (c as Control).is_visible_in_tree():
			out.append(c)
	return out


func test_the_logo_is_baked_art_with_a_drip_that_stops_under_reduce_effects() -> void:
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	await _frames()
	assert_true(title.logo is LogoArt, "the logo is LogoArt")
	assert_true(title.logo.texture is Texture2D, "drawn from the baked SVG as a texture")
	assert_eq(_count(title.margin, "GraffitiTag"), 0, "no live-text logo")
	assert_true(SvgArt.natural_size(SvgArt.LOGO).x > 0.0)
	for page in ["show_options", "show_codex", "show_stats"]:
		title.call(page)
		await _frames()
		assert_true(title.logo.is_visible_in_tree(), "%s keeps the logo" % page)
	# The drip swells then runs down; one drop at a time.
	var start: Array = title.logo.drop_at(0.1)
	var later: Array = title.logo.drop_at(Motion.seconds(LogoArt.MOTION) * 0.9)
	assert_true(float(later[0].y) > float(start[0].y), "the drop runs down")
	Settings.set_reduce_effects(true)
	await _frames()
	assert_false(Motion.live(LogoArt.MOTION), "static under reduce effects")
	assert_false(title.logo.is_processing(), "no drip then")


func test_the_title_has_one_primary_one_note_one_scrawl_taped_to_the_menu() -> void:
	RunManager.new_campaign(1)
	RunManager.campaign.heat = 14
	RunManager.autosave()
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	title.continue_slot = SLOT
	title.show_main()
	await _frames(4)
	var cont := title._panel.find_child("Continue", true, false) as Button
	assert_not_null(cont)
	var prim := _primaries(title._panel)
	assert_eq(prim.size(), 1, "one primary")
	assert_eq(prim[0], cont, "Continue is the one primary")
	assert_eq(_count(title._panel, "ZineNote"), 1, "one PAPER note")
	assert_eq(_count(title._panel, "ScrawlArt"), 1, "one scrawl")
	var menu := title._panel.find_child("Menu", true, false) as Control
	var note := title._panel.find_child("PlanNote", true, false) as Control
	var scrawl := title._panel.find_child("Scrawl", true, false) as Control
	assert_true(note.get_global_rect().position.x < menu.get_global_rect().end.x, "the note is taped over the menu's edge")
	assert_eq(scrawl.get_parent(), note.get_parent(), "the scrawl hangs with it from the menu's row")
	# Readable meta (critique 01): caption or larger, 4.5:1 on the glass and on the pink.
	var v := title._panel.find_child("Version", true, false) as Label
	assert_true(v.get_theme_font_size(&"font_size") >= UiTheme.CAPTION)
	assert_true(Palette.contrast(v.get_theme_color(&"font_color"), Palette.TERMINAL_BG) >= 4.5)
	var line := cont.find_child("SlotLine", true, false) as IconLine
	assert_true(line._fs() >= UiTheme.CAPTION, "the Continue glyph line is caption or larger (%d)" % line._fs())
	assert_true(Palette.contrast(line.color, Palette.CELL_PINK) >= 4.5, "ink on the pink primary")
	# The pad's prompt bar.
	Settings.set_pad_active(true)
	await _frames()
	assert_true(title.prompts.visible, "a prompt bar with a pad")
	Settings.set_pad_active(false)
	await _frames()
	assert_false(title.prompts.visible)
	assert_not_null(title._panel.find_child("Uplink", true, false) as TerminalWindow, "the profile uplink is glass")


func test_never_sleep_is_art_with_a_subtitle_in_other_languages() -> void:
	var s := ScrawlArt.new()
	add_child_autofree(s)
	assert_true(s.art.texture is Texture2D, "baked art")
	var locale := TranslationServer.get_locale()
	TranslationServer.set_locale("en")
	assert_false(ScrawlArt.needs_subtitle(), "English reads the art")
	TranslationServer.set_locale("de")
	assert_true(ScrawlArt.needs_subtitle(), "another language gets the subtitle")
	TranslationServer.set_locale(locale)


# --- 4. Campaign slots ---------------------------------------------------------------------------

func test_slots_are_case_files_and_delete_is_danger_with_a_confirm() -> void:
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	title.show_slots()
	await _frames()
	var cards: Array[Node] = title._panel.find_children("*", "CaseFileCard", true, false)
	assert_eq(cards.size(), title.SLOTS.size(), "one case file per slot")
	var summary := {"corporation": String(RunManager.DEFAULT_CORPORATION), "heat": 55, "ice": 2, "runs": 4, "state": "active",
		"in_run": false, "saved_at": 1790000000.0}
	var crew := [{"id": "op_1", "name": "Vex", "class_id": String(RunManager.DEFAULT_CLASS), "alive": true}]
	var card := CaseFileCard.new("2", summary, crew, true)
	add_child_autofree(card)
	await _frames()
	assert_eq(card.load_button.theme_type_variation, UiTheme.PRIMARY, "Load is the primary")
	assert_eq(card.delete_button.theme_type_variation, UiTheme.DANGER, "Delete is Danger")
	assert_eq(IconMark.kind_of(card.delete_button), StatIcon.TRASH, "with the trash glyph, never the power glyph")
	var bar := card.find_child("HeatBar", true, false)
	assert_not_null(bar, "a Heat bar")
	assert_eq(int(bar.get_meta(&"heat")), 55)
	assert_ne(SvgArt.landmark_path(RunManager.DEFAULT_CORPORATION), "", "a landmark glyph")
	assert_eq(card.find_child("Crew", true, false).get_child_count(), 1, "crew Polaroids")
	assert_not_null(card.find_child("LastPlayed", true, false), "the last-played date")
	for l in card.find_children("*", "Label", true, false):
		assert_true(card.folder.is_ancestor_of(l) or card.find_child("Actions", true, false).is_ancestor_of(l), "no plain text row: '%s'" % (l as Label).text)
	card.delete_pressed.connect(title.confirm_delete)
	card.delete_button.pressed.emit()
	assert_true(title.confirm_visible(), "Delete asks first")
	assert_true(PageTransition.modal_open(title), "on a modal")


# --- 5. Options ----------------------------------------------------------------------------------

func test_options_use_kit_components_one_size_and_aligned_toggles() -> void:
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	title.show_options()
	await _frames()
	var panel := title._panel.find_children("*", "SettingsPanel", true, false)[0] as SettingsPanel
	for cls in ["OptionButton", "CheckButton", "CheckBox", "HSlider"]:
		assert_eq(panel.find_children("*", cls, true, false).size(), 0, "no native %s" % cls)
	var sizes := []
	for s in SettingsPanel.SECTIONS:
		panel.show_section(s)
		await _frames()
		sizes.append(panel.size)
		var toggles: Array = (panel.sections[s] as Node).find_children("*", "ZineToggle", true, false)
		var longest := 0.0
		for t in toggles:
			longest = maxf(longest, (t as ZineToggle).own_label_width())
		for t in toggles:
			var gap := (t as ZineToggle).pill_rect().position.x - longest
			assert_almost_eq(gap, float(ZineToggle.GAP), 0.5, "%s: the switch sits 16 px right of the longest label" % t.name)
	for sz in sizes:
		assert_eq(sz, sizes[0], "one size across the tabs")
	assert_eq(panel.scale_slider.readout(1.6), "1.6×", "the slider reads 1.6×")
	panel.scale_slider.value = 1.4
	assert_eq(panel.text_preview.get_theme_font_size(&"font_size"), UiTheme.font_px_at(UiTheme.BODY, 1.4), "the preview follows the slider")
	for n in _all(panel):
		var words := ""
		if n is Label:
			words = (n as Label).text
		elif n is Button:
			words = (n as Button).text
		elif n is ZineToggle:
			words = (n as ZineToggle).text
		for w in ["click", "drag", "mouse"]:
			assert_false(words.to_lower().contains(w), "no mouse wording: '%s'" % words)
	Settings.set_pad_active(true)
	await _frames()
	assert_false(panel.close_button.text.contains("["), "the prompt bar, never Close [B]")
	assert_true(title.prompts.visible)
	Settings.set_pad_active(false)


# --- 6. Codex ------------------------------------------------------------------------------------

func test_codex_is_a_two_column_spread_of_short_lines_with_glyphs() -> void:
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	title.show_codex()
	await _frames()
	var spread := title._panel.find_child("CodexSpread", true, false) as CodexSpread
	assert_eq(spread.column_count(), 2, "two columns at 1.0")
	assert_eq(spread.tabs.get_child_count(), Codex.entries(RunManager.lookup(), RunManager.profile).size(), "a tab per section")
	assert_eq(spread.heading.get_theme_font_size(&"font_size"), UiTheme.font_px(UiTheme.HEADING), "a real heading")
	spread.show_section("Statuses & precision")
	await _frames()
	var px := UiTheme.font_px(UiTheme.BODY)
	for n in spread.find_children("Body", "Label", true, false):
		var l := n as Label
		assert_eq(l.theme_type_variation, UiTheme.BODY_TEXT, "Plex body")
		for k in CodexSpread.line_lengths(l.text, l.size.x, px):
			assert_true(k <= CodexSpread.MAX_LINE_CHARS, "%d characters on a line" % k)
	var glyphs := spread.find_children("Glyph", "Control", true, false)
	assert_true(glyphs.size() > 0)
	var statuses := 0
	for g in glyphs:
		assert_eq((g as Control).custom_minimum_size, Vector2.ONE * CodexSpread.GLYPH, "24 px glyphs")
		statuses += 1 if (g.get_meta(&"item") as Dictionary).has("status") else 0
	assert_true(statuses > 0, "statuses draw their StatIcon")


# --- 7. Stats ------------------------------------------------------------------------------------

func test_stats_show_earned_and_unearned_badges_a_grid_and_receipts() -> void:
	var first: StringName = Achievements.DEFS[0]["id"]
	var had := RunManager.profile.achievements.has(first)
	if not had:
		RunManager.profile.achievements.append(first)
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	title.show_stats()
	await _frames()
	var badges: Array[Node] = title._panel.find_children("*", "AchievementBadge", true, false)
	assert_eq(badges.size(), Achievements.DEFS.size())
	var earned := 0
	for b in badges:
		earned += 1 if (b as AchievementBadge).earned else 0
	assert_eq(earned, RunManager.profile.achievements.size(), "earned in colour, the rest outlined with a lock")
	assert_true(earned >= 1 and earned < badges.size(), "both kinds show")
	assert_eq((title._panel.find_child("StatGrid", true, false) as GridContainer).columns, 3, "a 3-column grid")
	var receipts: Node = title._panel.find_child("Receipts", true, false)
	assert_eq(receipts.get_child_count(), maxi(1, RunManager.profile.run_history.size()), "a receipt per run, or the empty slip")
	if not had:
		RunManager.profile.achievements.erase(first)


# --- 8. Pause ------------------------------------------------------------------------------------

func test_pause_fits_its_content_one_primary_and_the_code_in_a_field() -> void:
	RunManager.new_campaign(1)
	var menu := PauseMenu.new()
	menu.position = Vector2((1280 - PauseMenu.MENU_SIZE.x) / 2.0, 100)
	add_child_autofree(menu)
	await _frames(4)
	assert_true(menu.size.y < PauseMenu.MENU_SIZE.y, "no taller than its lines (%.0f)" % menu.size.y)
	assert_true(menu.size.x < PauseMenu.MENU_SIZE.x, "no wider than its lines (%.0f)" % menu.size.x)
	assert_almost_eq(menu.position.x + menu.size.x * 0.5, 640.0, 1.0, "centred where the host put it")
	assert_eq(_primaries(menu).size(), 1, "one primary: Resume")
	assert_not_null(menu.code_field, "the campaign code in a CodeField")
	assert_not_null(menu.code_field.copy_button, "with a copy button")
	assert_eq(menu.code_field.value, CampaignCode.of(RunManager.campaign, RunManager.campaign.start_class_id))
	for n in _all(menu):
		if n is Label:
			assert_false((n as Label).text.contains(menu.code_field.value), "the raw code is never body text")
	menu.show_options()
	await _frames()
	assert_eq(menu.size.x, PauseMenu.MENU_SIZE.x, "Options widen it to the menu's box")
	assert_true(menu.settings_panel.own_prompts)


# --- 9. Text scale 2.0 ---------------------------------------------------------------------------

func _check_page(title: Control, label: String) -> void:
	var view := Rect2(Vector2.ZERO, title.get_viewport_rect().size)
	var page := title._panel as Control
	assert_true(view.grow(1.0).encloses(page.get_global_rect()), "%s: the page %s stays on screen" % [label, page.get_global_rect()])
	for n in _all(page):
		if not (n is Label) or not (n as Control).is_visible_in_tree():
			continue
		var l := n as Label
		if l.text == "":
			continue
		assert_true(l.get_theme_font_size(&"font_size") >= UiTheme.CAPTION, "%s: '%s' at %d px" % [label, l.text, l.get_theme_font_size(&"font_size")])
		if l.autowrap_mode == TextServer.AUTOWRAP_OFF and not l.clip_text:
			assert_true(l.get_minimum_size().x <= l.size.x + 1.0, "%s: '%s' is whole" % [label, l.text])


func test_title_pages_fit_at_every_text_scale() -> void:
	RunManager.new_campaign(1)
	RunManager.autosave()
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var title: Control = add_child_autofree(load(TITLE).instantiate())
		title.continue_slot = SLOT
		for page in ["show_main", "show_slots", "show_options", "show_codex", "show_stats"]:
			title.call(page)
			await _frames(4)
			_check_page(title, "%s at %.1f" % [page, scale])
		title.queue_free()
		await _frames()
