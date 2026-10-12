extends GutTest
## M14 12Q-MENUS (QA matrix audit 12q, docs/handoff/m14_12q/qa_matrix_audit.md): the menu screens' layout
## defects, at text 1.0 / 1.6 / 2.0: the codex's tabs all reachable (L28), the campaign slots' name and LOAD
## whole with a cue for the slots out of view (L42), every line of every tutorial page shown (L39), SAVED clear
## of the hints and the ticker (L47), the pause menu's header on one line (L55), the options' focus brackets
## inside their row (L56), the pad's focus peeling a sticker back as hover does (L57), the share-code placeholder
## whole (L62).

const TITLE := "res://scenes/menu/title_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
## The title's campaign slots (title_scene.gd SLOTS).
const SLOTS: Array[String] = ["1", "2", "3"]

var _saved: Dictionary
var _profile: ProfileState


func before_each() -> void:
	_saved = Settings.snapshot()
	Settings.set_text_scale(1.0)
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	RunManager.save_slot = "gut_12q_menus"
	RunManager.reset()
	_profile = RunManager.profile


func after_each() -> void:
	Fx.saved_screen = Rect2()
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


# --- L28 codex tabs ---------------------------------------------------------------------------------

## Every tab of `book` comes whole into the row's view by the cue chips alone (a mouse player's reach).
func _assert_every_tab_reached(book: CodexBook, where: String) -> void:
	var n := book.tabs.get_child_count()
	if book.tab_scroll == null:
		var frame := book.frame.get_global_rect().grow(0.5)
		for b in book.tabs.get_children():
			assert_true(frame.encloses((b as Control).get_global_rect()), "%s: tab %s inside the window (rows)" % [where, b.name])
		return
	assert_true(book.tab_next.visible and book.tab_prev.visible, "%s: the cue chips show" % where)
	assert_gt(book.hidden_tabs(1), 0, "%s: tabs run past the view" % where)
	assert_eq(book.tab_next.text, tr(CodexBook.CUE_NEXT) % book.hidden_tabs(1), "%s: the right cue counts them" % where)
	assert_false(book.cue_live(-1), "%s: nothing hidden on the left yet (the left cue idle)" % where)
	assert_eq(book.tab_prev.modulate.a, 0.0, "%s: G2R-4 the left arrow hidden with nothing to page to" % where)
	assert_eq(book.tab_next.modulate.a, 1.0, "%s: G2R-4 the right arrow shows with tabs to page to" % where)
	var seen := {}
	for step in n + 1:
		var left := float(book.tab_scroll.scroll_horizontal)
		for b in book.tabs.get_children():
			var c := b as Control
			if c.position.x >= left - 0.5 and c.position.x + c.size.x <= left + book.tab_scroll.size.x + 0.5:
				seen[c.name] = true
		if book.hidden_tabs(1) == 0:
			break
		book.scroll_tabs(1)
		assert_gt(float(book.tab_scroll.scroll_horizontal), left, "%s: the right cue moves the row on" % where)
	assert_eq(seen.size(), n, "%s: every tab came whole into view (%s)" % [where, seen.keys()])
	assert_eq(book.hidden_tabs(1), 0, "%s: the row's end reached" % where)
	assert_false(book.cue_live(1), "%s: the right cue idles at the end" % where)
	assert_eq(book.tab_next.modulate.a, 0.0, "%s: G2R-4 the right arrow hidden at the end" % where)
	assert_gt(book.hidden_tabs(-1), 0, "%s: the left cue counts the tabs passed" % where)
	for step in n + 1:
		if book.hidden_tabs(-1) == 0:
			break
		book.scroll_tabs(-1)
	assert_eq(book.tab_scroll.scroll_horizontal, 0, "%s: the left cue scrolls back to the start" % where)
	await _frames(1)
	var row := book.tab_row.get_global_rect().grow(0.5)
	assert_true(book.frame.get_global_rect().grow(0.5).encloses(row), "%s: the row and its cues inside the window" % where)


func test_l28_every_codex_tab_is_reachable_on_the_title_and_in_the_pause_menu() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var t := _title()
		await _frames(2)
		t.show_codex()
		await _frames(4)
		var book := t._panel.find_child("Codex", true, false) as CodexBook
		await _assert_every_tab_reached(book, "title %.1f" % scale)
		t.queue_free()
		var menu: PauseMenu = add_child_autofree(PauseMenu.new())
		await _frames(2)
		menu.show_codex()
		await _frames(4)
		await _assert_every_tab_reached(menu.codex_note, "pause %.1f" % scale)
		menu.queue_free()
		await _frames(1)


func test_l28_the_pad_focus_brings_its_tab_into_view() -> void:
	Settings.set_text_scale(2.0)
	var t := _title()
	await _frames(2)
	t.show_codex()
	await _frames(4)
	var book := t._panel.find_child("Codex", true, false) as CodexBook
	var keys := book.entries.keys()
	book.step_section(-1)  # LB from the first tab: the last one
	await _frames(3)
	assert_eq(book.section, String(keys[keys.size() - 1]), "LB wraps to the last tab")
	var tab := book.current_tab()
	var view := book.tab_scroll.get_global_rect().grow(0.5)
	assert_true(view.encloses(tab.get_global_rect()), "the focused last tab is whole in the row's view")
	assert_eq(book.hidden_tabs(1), 0, "nothing hidden past it")


# --- L39 tutorial -----------------------------------------------------------------------------------

func test_l39_every_line_of_every_tutorial_page_shows() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		# The fight's own box (the notes column's room at this text size), then a few others.
		RunManager.new_campaign(1)
		var holder: Control = add_child_autofree(Control.new())
		holder.size = SCREEN.size
		var scene: Control = load("res://scenes/combat/combat_scene.tscn").instantiate()
		scene.auto_start = false
		holder.add_child(scene)
		scene.start_fight(&"collections_agent", 5)
		await _frames(3)
		scene.start_tutorial()
		await _frames(4)
		var tut: TutorialOverlay = scene.tutorial
		var boxes: Array = [tut.size, Vector2(380, tut.size.y)]  # the fight's box, and a wider one
		assert_gt(float(tut.note.label.get_theme_font_size(&"normal_font_size")), 15.0 * scale - 2.0, "%.1f: the note's words at the player's text size" % scale)
		for box in boxes:
			tut.fit(box)
			for i in TutorialOverlay.STEPS.size():
				tut.step = i
				tut.page = 0
				tut._show()
				var words := PackedStringArray()
				var count := tut.pages().size()
				for p in count:
					tut.page = p
					tut._show()
					assert_true(tut.page_fits(), "%.1f %s step %d page %d/%d: the whole page shows (%d px of %d)" % [scale, box, i + 1, p + 1, count,
						tut.note.label.get_content_height(), tut.note.label.size.y])
					words.append(tut.pages()[p])
				assert_eq(" ".join(words).split(" ", false).size(), TutorialOverlay.step_text(i).split(" ", false).size(),
					"%.1f %s step %d: every word on some page" % [scale, box, i + 1])
		tut.skip()
		scene.skip_motion()
		holder.queue_free()
		await _frames(1)


# --- L47 SAVED -------------------------------------------------------------------------------------

## The prompt pairs and the ticker shown under `root` (global rects).
func _hint_rects(root: Node) -> Array[Rect2]:
	var out: Array[Rect2] = []
	for n in root.find_children("*", "Control", true, false):
		var c := n as Control
		if c.is_visible_in_tree() and (c.has_meta(Fx.META_SAVED_AVOID) or c is OnAirTicker):
			out.append(c.get_global_rect())
	return out


func test_l47_saved_keeps_clear_of_the_ticker_and_the_prompts() -> void:
	Fx.saved_screen = SCREEN
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var t := _title()
		await _frames(3)
		for page in ["main", "codex", "slots"]:
			match page:
				"codex":
					t.show_codex()
				"slots":
					t.show_slots()
			await _frames(4)
			var hints := _hint_rects(t)
			assert_gt(hints.size(), 0, "%.1f %s: hints on the page" % [scale, page])
			var r := Fx.place_saved(SCREEN)
			for h in hints:
				assert_false(r.intersects(h), "%.1f %s: SAVED %s clear of the hint %s" % [scale, page, r, h])
		t.queue_free()
		await _frames(1)


# --- L57 the pad focus on a sticker -------------------------------------------------------------------------

## Designer ruling 2026-10-06 (3): focus and hover on a sticker show the peel-back (the corner curl) only, never
## brackets. The pad's focus on the title's verbs and on the slots' LOAD peels the sticker as the mouse's hover does
## (the QA matrix's pad and mouse frames matched because the page's default focus peels BREACH / LOAD in both).
func test_l57_pad_focus_peels_the_sticker_as_hover_does_and_draws_no_brackets() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		Settings.set_pad_active(true)
		var t := _title()
		await _frames(3)
		for i in t.verbs.size():
			var v := t.verbs[i] as VerbSticker
			if v.vinyl == null:
				continue
			v.grab_focus()
			await _frames(1)
			assert_true(v.has_focus(), "%.1f %s: the pad's focus" % [scale, v.name])
			assert_eq(v.vinyl.state, VinylSticker.State.DISABLED if v.disabled else VinylSticker.State.HOVER,
				"%.1f %s: focus peels the sticker back (the hover state)" % [scale, v.name])
			assert_eq(v.find_children("PadFocus", "", true, false).size(), 0,
				"%.1f %s: no focus brackets on a sticker" % [scale, v.name])
		var breach := t.verbs[0] as VerbSticker
		if breach.uses_art():
			# The concept image's rounded die-cut sits inside its opaque rect: the fold reaches past that corner, so
			# the flap the pad's focus peels shows as on a drawn sticker (it barely showed: the matrix's pad frame).
			assert_gt(breach.vinyl._fold_inset, 0.0, "%.1f: BREACH's fold starts at its die-cut, not its rect's corner" % scale)
			assert_almost_eq(breach.vinyl.peel_px() - breach.vinyl._fold_inset,
				VinylSticker.peel_leg(breach.vinyl.body_rect.size.x, breach.vinyl.get_viewport_rect().size.y), 0.01,
				"%.1f: the flap itself is the kit's leg" % scale)
		var other := t.verbs[0] as VerbSticker
		var live: VerbSticker = null
		for v in t.verbs:
			if not (v as VerbSticker).disabled and v != other:
				live = v
		if live != null:
			other.grab_focus()
			await _frames(1)
			assert_eq(live.vinyl.state, VinylSticker.State.REST, "%.1f: a sticker the focus left lies flat" % scale)
			Settings.set_pad_active(false)
			live.mouse_entered.emit()
			await _frames(1)
			assert_eq(live.vinyl.state, VinylSticker.State.HOVER, "%.1f: the mouse's hover is the same peel-back" % scale)
			live.mouse_exited.emit()
		t.queue_free()
		await _frames(1)


# --- L42 campaign slots -----------------------------------------------------------------------------

## Fills slots 1..`used` (false when a slot already holds a campaign: a player's save is never touched).
func _fill_slots(used: int) -> bool:
	for s in SLOTS:
		if not RunManager.slot_summary(s).is_empty():
			return false
	for i in used:
		RunManager.save_slot = str(i + 1)
		RunManager.new_campaign(4 + i)
		RunManager.autosave()
	RunManager.save_slot = "gut_12q_menus"
	return true


func _clear_slots() -> void:
	for s in SLOTS:
		RunManager.delete_slot(s)


func test_l42_the_focused_slot_shows_its_name_and_load_whole_with_a_cue_for_the_rest() -> void:
	if not _fill_slots(3):
		pending("a campaign already sits in slots 1-3")
		return
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var t := _title()
		await _frames(2)
		t.show_slots()
		await _frames(8)
		var win := t._panel.find_child("Slots", true, false) as CrtWindow
		var view := win.fit.scroll.get_global_rect().grow(1.0)
		var cards: Array[Node] = t._panel.find_children("Slot*", "CaseFileCard", true, false)
		assert_eq(cards.size(), 3, "three case files")
		for k in [cards.size() - 1, 0]:
			var card := cards[k] as CaseFileCard
			card.load_button.grab_focus()
			await _frames(6)
			view = win.fit.scroll.get_global_rect().grow(1.0)
			assert_true(card.held(), "%.1f slot %s: the focused slot lies straight" % [scale, card.slot])
			# G2R-3: at 2.0 a case file (folder + LOAD, DELETE and the pencil under it) is taller than the view
			# on a 720p screen: one folder per page, so the view holds the actions and the folder pages with MORE ABOVE / BELOW.
			assert_true(view.encloses(card.get_global_rect()), "%.1f slot %s: the whole case file %s (folder, LOAD, DELETE, pencil) in the view %s" % [scale, card.slot, card.get_global_rect(), view])
			assert_true(view.encloses(card.folder.get_global_rect()), "%.1f slot %s: the whole folder %s in the view %s (its tab and name)" % [scale, card.slot, card.folder.get_global_rect(), view])
			var name_l := card.folder.find_child("CorpName", true, false) as Control
			assert_true(view.encloses(name_l.get_global_rect()), "%.1f slot %s: the corporation's name shows" % [scale, card.slot])
			assert_eq(card.folder.find_child("Facts", true, false) == null, scale >= 1.6, "%.1f slot %s: ICE / RUNS / FILED move to the tooltip from 1.6" % [scale, card.slot])
			assert_gte(float(name_l.get_theme_font_size(&"font_size")), UiTheme.font_px(UiTheme.LABEL), "text never under 1.0 size")
			assert_true(view.encloses(card.load_button.get_global_rect()), "%.1f slot %s: LOAD whole in the view" % [scale, card.slot])
			assert_true(view.encloses(card.delete_button.get_global_rect()), "%.1f slot %s: DELETE whole in the view" % [scale, card.slot])
			var hidden_above := false
			var hidden_below := false
			for c in cards:
				var r := (c as CaseFileCard).get_global_rect()
				hidden_above = hidden_above or r.position.y < view.position.y - 0.5
				hidden_below = hidden_below or r.end.y > view.end.y + 0.5
			var hint := win.fit.hint
			if hidden_below:
				assert_true(hint.visible and not hint.says_above(), "%.1f slot %s: MORE BELOW for the slots under the view" % [scale, card.slot])
			elif hidden_above:
				assert_true(hint.visible and hint.says_above(), "%.1f slot %s: MORE ABOVE for the slots over the view" % [scale, card.slot])
			else:
				assert_false(hint.visible, "%.1f slot %s: no cue when every slot shows" % [scale, card.slot])
		var foot: Rect2 = (t.sub_foot as Control).get_global_rect()
		assert_true(SCREEN.grow(0.5).encloses(foot), "%.1f: the foot line and its prompts on screen (%s)" % [scale, foot])
		var back := t._panel.find_child("Back", true, false) as Control
		assert_lte(back.get_global_rect().end.y, foot.position.y + 0.5, "%.1f: Back above the foot" % scale)
		t.queue_free()
		await _frames(1)
	_clear_slots()


func test_l42_the_pad_walks_the_actions_under_each_folder_at_2_0() -> void:
	if not _fill_slots(2):
		pending("a campaign already sits in slots 1-3")
		return
	Settings.set_text_scale(2.0)
	var t := _title()
	await _frames(2)
	t.show_slots()
	await _frames(6)
	var one := t._panel.find_child("Slot1", true, false) as CaseFileCard
	var two := t._panel.find_child("Slot2", true, false) as CaseFileCard
	var nb := func(c: Control, p: NodePath) -> Control: return c.get_node_or_null(p) as Control
	assert_not_null(one.cant_undo, "G2R-3: the CAN'T UNDO pencil stays at 2.0")
	assert_eq(nb.call(one.load_button, one.load_button.focus_neighbor_right), one.delete_button, "LOAD right: its DELETE (beside it, under the folder)")
	assert_eq(nb.call(one.load_button, one.load_button.focus_neighbor_bottom), two.load_button, "LOAD down: the next slot's LOAD")
	assert_eq(nb.call(two.delete_button, two.delete_button.focus_neighbor_top), one.delete_button, "up walks back")
	t.queue_free()
	await _frames(1)
	_clear_slots()


# --- L55 the pause menu's header ------------------------------------------------------------------------

func test_l55_the_pause_header_stands_on_one_line_and_the_menu_on_screen() -> void:
	RunManager.new_campaign(4)
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var menu := PauseMenu.new()
		menu.position = Vector2((SCREEN.size.x - PauseMenu.MENU_SIZE.x) / 2.0, 60.0)  # as the hosts place it, before it enters
		add_child_autofree(menu)
		await _frames(4)
		var head := menu._panel.find_child("TerminalTitle", true, false) as Label
		assert_string_contains(head.text, "//", "%.1f: PAUSED // HQ // the corporation" % scale)
		assert_eq(head.get_line_count(), 1, "%.1f: the header on one line (%s)" % [scale, head.text])
		var r := menu.get_global_rect()
		assert_true(SCREEN.grow(0.5).encloses(r), "%.1f: the menu %s on screen" % [scale, r])
		assert_almost_eq(r.get_center().x, SCREEN.get_center().x, 1.0, "%.1f: still centred" % scale)
		for n in menu._notes:
			if n.is_visible_in_tree():
				assert_true(r.grow(0.5).encloses(n.get_global_rect()), "%.1f: the note %s whole in the menu" % [scale, n.name])
		menu.queue_free()
		await _frames(1)


# --- L56 the options' focus brackets ---------------------------------------------------------------

func test_l56_a_focused_rows_brackets_keep_off_the_heading_over_it() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
		await _frames(3)
		panel.show_section("Accessibility")
		await _frames(3)
		var row := panel.reduce_check
		row.grab_focus()
		await _frames(1)
		var heading: Label = null
		for c in row.get_parent().get_children():
			if c is Label and (c as Label).text == tr("EFFECTS & MOTION").to_upper():
				heading = c
		assert_not_null(heading, "%.1f: the EFFECTS & MOTION heading over the first row" % scale)
		var reach := StyleBoxBrackets.OFFSET + StyleBoxBrackets.current_thickness()
		var words_bottom := heading.get_global_rect().end.y - heading.get_theme_stylebox(&"normal").content_margin_bottom
		assert_lte(words_bottom, row.get_global_rect().position.y - reach + 0.5, "%.1f: the brackets' top arms below the heading's words" % scale)
		panel.queue_free()
		await _frames(1)


# --- L62 the share-code placeholder -------------------------------------------------------------------

func test_l62_the_share_code_field_shows_its_whole_placeholder() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
		hq.show_start()
		await _frames(3)
		(hq._panel.find_child("CodesToggle", true, false) as Button).pressed.emit()
		await _frames(3)
		var edit := hq._panel.find_child("CodeEdit", true, false) as LineEdit
		var words := edit.get_theme_font(&"font").get_string_size(edit.placeholder_text, HORIZONTAL_ALIGNMENT_LEFT, -1, edit.get_theme_font_size(&"font_size")).x
		var inner := edit.size.x - edit.get_theme_stylebox(&"normal").get_minimum_size().x
		assert_gte(inner, words, "%.1f: the placeholder (%.0f px) fits the field (%.0f px)" % [scale, words, inner])
		assert_true(SCREEN.grow(0.5).encloses(Rect2(edit.get_global_rect().position.x, 0, edit.size.x, 1)), "%.1f: the field inside the screen's width" % scale)
		hq.queue_free()
		await _frames(1)


func test_l42_a_sticker_held_at_its_size_keeps_its_fold() -> void:
	Settings.set_text_scale(1.0)
	var small_1 := VinylSticker.peel_leg(90.0, 720.0)
	var big_1 := VinylSticker.peel_leg(900.0, 720.0)
	for scale in [1.6, 2.0]:
		Settings.set_text_scale(scale)
		assert_lte(VinylSticker.peel_leg(90.0, 720.0), maxf(small_1, 90.0 * VinylSticker.PEEL_MAX_SHARE) + 0.01,
			"%.1f: LOAD's fold (a 90 px body) never grows past its share of the body (it read LOA)" % scale)
		assert_almost_eq(VinylSticker.peel_leg(900.0, 720.0), big_1 * scale, 0.01, "%.1f: a sticker that grows keeps the growing fold" % scale)


func test_l57_the_fold_inset_finds_a_rounded_die_cuts_corner() -> void:
	var img := Image.create(40, 30, false, Image.FORMAT_RGBA8)
	img.fill(Color(1, 1, 1, 1))
	var body := Rect2(0, 0, 40, 30)
	assert_eq(VinylSticker.fold_inset(img, body, VinylSticker.Lift.TOP_RIGHT), 0.0, "a square corner: no inset")
	for y in 6:
		for x in range(34 + y, 40):
			img.set_pixel(x, y, Color(0, 0, 0, 0))  # the top-right corner cut away (a rounded die-cut's empty corner)
	var inset := VinylSticker.fold_inset(img, body, VinylSticker.Lift.TOP_RIGHT)
	assert_gt(inset, 0.0, "the empty corner is walked past")
	assert_eq(VinylSticker.fold_inset(img, body, VinylSticker.Lift.TOP_LEFT), 0.0, "only the lifted corner counts")
