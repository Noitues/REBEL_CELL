extends GutTest
## ART-10 4C (ART_BIBLE v2 §4.13, §1.2, §2.9-2.10, §5.6; round 31 / 33 ui_chrome): the
## menus, title, settings, pause and HQ on the v2 kit. Title option A (D10): the three
## numbered verbs and what each does, BREACH the default focus, the MORE list and its keys;
## the abandon-dialog confirm (yellow CANCEL default, pink verb, CANNOT UNDO); the vinyl
## sticker's states and its motions' end states; the neon sign's loop; the Options rows (the
## switches, the tiles, the LIMITED chip, no pad focus scale on full-width rows, fits at 2.0);
## the pause menu; the HQ's terminals and corp-paper dossier. Views never change state:
## every press goes through the scene's existing actions.

const TITLE := "res://scenes/menu/title_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
## The title's three numbered campaign slots.
const SLOT_IDS: Array[String] = ["1", "2", "3"]

var _saved: Dictionary
var _force_live: bool


func before_each() -> void:
	_saved = Settings.snapshot()
	_force_live = Motion.force_live
	Motion.force_live = false
	Settings.set_text_scale(1.0)
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	for slot in ["1", "2", "3", "gut_art10"]:
		RunManager.delete_slot(slot)
	RunManager.save_slot = "gut_art10"
	RunManager.reset()


func after_each() -> void:
	Motion.force_live = _force_live
	for slot in ["1", "2", "3", "gut_art10"]:
		RunManager.delete_slot(slot)
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true
	RunManager.pending_tutorial = false
	AudioDirector.muted = false
	Settings.restore(_saved)


func _frames(n: int = 1) -> void:
	for i in n:
		await get_tree().process_frame


func _title() -> Control:
	var t: Control = add_child_autofree(load(TITLE).instantiate())
	return t


func _saved_campaign() -> void:
	RunManager.save_slot = "gut_art10"
	RunManager.new_campaign(3)
	RunManager.autosave()


# --- Title option A (D10) ---------------------------------------------------------------------

func test_the_title_shows_breach_simulate_overthrow_with_their_chips() -> void:
	_saved_campaign()
	var t := _title()
	t.continue_slot = "gut_art10"
	t.show_main()
	await _frames(2)
	var words: Array[String] = []
	for v in t.verbs:
		words.append(v.shown_text())
	assert_eq(words, ["BREACH", "SIMULATE", "OVERTHROW"], "D10: the three verbs in order")
	assert_eq(t.verbs[0].fill, VerbSticker.Fill.PINK, "BREACH is the pink verb")
	assert_eq(t.verbs[1].fill, VerbSticker.Fill.GLITCH, "SIMULATE carries the CORRUPTED glitch")
	assert_eq(t.verbs[2].fill, VerbSticker.Fill.BLUE, "OVERTHROW is blue")
	assert_eq(t.verbs[2].fist_at, "OVERTHROW".length() - 2, "its last O is the rebel fist")
	var cont := t._panel.find_child("Continue", true, false) as MenuChip
	assert_not_null(cont, "BREACH's chip reads CONTINUE")
	assert_string_contains(cont.line, "Heat", "the chip carries the slot summary")
	assert_not_null(t._panel.find_child("Tutorial", true, false) as MenuChip)
	assert_not_null(t._panel.find_child("Newcampaign", true, false) as MenuChip)


func test_breach_is_the_default_focus_and_continues_the_saved_campaign() -> void:
	_saved_campaign()
	RunManager.reset()
	var t := _title()
	t.continue_slot = "gut_art10"
	t.show_main()
	await _frames(3)
	assert_eq(t._default_focus(t._panel), t.verbs[0], "BREACH takes the focus first")
	t.verbs[0].pressed.emit()
	assert_not_null(RunManager.campaign, "BREACH loads the campaign (RunManager.resume)")
	assert_eq(RunManager.save_slot, "gut_art10")


func test_simulate_starts_the_tutorial_and_overthrow_a_new_campaign() -> void:
	var t := _title()
	await _frames(2)
	assert_true(t.verbs[0].disabled, "no campaign saved: BREACH is the grey disabled sticker")
	assert_eq(t._default_focus(t._panel), t.verbs[1], "the first live verb takes the focus")
	t.verbs[1].pressed.emit()
	assert_true(RunManager.pending_tutorial, "SIMULATE = the tutorial")
	RunManager.pending_tutorial = false
	t.verbs[2].pressed.emit()
	assert_eq(RunManager.save_slot, "1", "OVERTHROW starts a campaign in the first empty slot")


func test_the_more_list_has_its_five_lines_and_key_hints() -> void:
	var t := _title()
	await _frames(2)
	var list := t._panel.find_child("MoreList", true, false) as Control
	assert_not_null(list)
	var lines: Array[String] = []
	for b in list.get_children():
		if b is Button:
			lines.append((b as Button).text)
			assert_not_null(b.find_child("KeyHint", false, false), "'%s' shows its key" % (b as Button).text)
			assert_ne((b as Button).tooltip_text, "", "'%s' says what it does" % (b as Button).text)
	assert_eq(lines, ["CAMPAIGN SLOTS", "CODEX", "STATS & ACHIEVEMENTS", "OPTIONS", "QUIT"])


func test_the_keys_open_the_pages_and_back_returns() -> void:
	var t := _title()
	await _frames(2)
	for pair in [[KEY_C, "slots"], [KEY_X, "codex"], [KEY_S, "stats"]]:
		var ev := InputEventKey.new()
		ev.keycode = pair[0]
		ev.pressed = true
		t._unhandled_input(ev)
		assert_eq(t.panel_name, pair[1], "key opens %s" % pair[1])
		var back := InputEventAction.new()
		back.action = &"ui_cancel"
		back.pressed = true
		t._unhandled_input(back)
		assert_eq(t.panel_name, "main", "back from %s" % pair[1])
		await _frames(1)


func test_the_title_fits_at_every_text_scale() -> void:
	_saved_campaign()
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var t := _title()
		t.continue_slot = "gut_art10"
		t.show_main()
		await _frames(3)
		var page := t._panel as Control
		for n in ["LeftColumn", "More", "ProfileTags"]:
			var c := page.find_child(n, true, false) as Control
			if not c.visible:
				continue  # big text: the profile waits on the Stats page
			var r := c.get_global_rect()
			assert_true(SCREEN.encloses(r.grow(-1.0)), "%s on the screen at %.1f: %s" % [n, scale, r])
		var more := (page.find_child("More", true, false) as Control).get_global_rect()
		var verbs := (page.find_child("Verbs", true, false) as Control).get_global_rect()
		assert_false(more.intersects(verbs.grow(-1.0)), "MORE %s clear of the verbs %s at %.1f" % [more, verbs, scale])
		# The bottom panels sit above the foot row (the pad prompts), never under it.
		var foot := (page.find_child("Foot", true, false) as Control).get_global_rect()
		for n in ["More", "ProfileTags"]:
			var c := page.find_child(n, true, false) as Control
			if c.visible:
				assert_false(c.get_global_rect().intersects(foot.grow(-1.0)), "%s clear of the foot row at %.1f" % [n, scale])
		# Each MORE line's words end before its key hint starts.
		for b in page.find_child("MoreList", true, false).get_children():
			var hint := (b as Node).find_child("KeyHint", false, false) as Control
			if hint == null:
				continue
			var bt := b as Button
			var words := bt.get_theme_font(&"font").get_string_size(bt.text, HORIZONTAL_ALIGNMENT_LEFT, -1, bt.get_theme_font_size(&"font_size")).x
			var words_end := bt.global_position.x + bt.get_theme_stylebox(&"normal").get_margin(SIDE_LEFT) + words
			assert_lt(words_end, hint.global_position.x, "%s clear of its key hint at %.1f" % [bt.text, scale])
		t.queue_free()
		await _frames(1)


func test_the_more_panel_keeps_a_clear_gap_under_overthrow() -> void:
	# Parity TITLE-02 (designer 2026-10-05: concept 33): a clear gap from the OVERTHROW sticker
	# down to the MORE panel, at every text scale MORE sits under the verbs.
	_saved_campaign()
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var t := _title()
		t.continue_slot = "gut_art10"
		t.show_main()
		await _frames(3)
		var page := t._panel as Control
		var more := (page.find_child("More", true, false) as Control).get_global_rect()
		var verbs := (page.find_child("Verbs", true, false) as Control).get_global_rect()
		var overthrow: Rect2 = (t.verbs[2] as Control).get_global_rect()
		if more.position.x < verbs.end.x:  # MORE under the verbs (not beside them, big text)
			assert_gte(more.position.y - maxf(verbs.end.y, overthrow.end.y), t.MORE_GAP - 0.5,
				"MORE %s a clear gap under OVERTHROW %s at %.1f" % [more, overthrow, scale])
		t.queue_free()
		await _frames(1)


# --- Campaign slots (parity SLOTS-01..04) -------------------------------------------------------

func _save_slots(count: int) -> void:
	for i in count:
		RunManager.save_slot = SLOT_IDS[i]
		RunManager.new_campaign(3 + i)
		RunManager.campaign.heat = 20 * (i + 1)
		RunManager.autosave()
	RunManager.save_slot = "gut_art10"
	RunManager.campaign = null


func _cards(t: Control) -> Array[CaseFileCard]:
	var out: Array[CaseFileCard] = []
	for c in (t._panel.find_child("Cards", true, false) as Node).get_children():
		out.append(c as CaseFileCard)
	return out


func test_the_slots_page_is_three_case_files_in_one_panel() -> void:
	_save_slots(1)
	var t := _title()
	await _frames(2)
	t.show_slots()
	await _frames(3)
	var page := t._panel as Control
	# SLOTS-03: the page title stays the yellow CAMPAIGN SLOTS sticker (v2 page-title rule).
	var sticker := page.find_child("TitleSticker", true, false) as VerbSticker
	assert_eq(sticker.shown_text(), "CAMPAIGN SLOTS")
	assert_eq(sticker.fill, VerbSticker.Fill.YELLOW)
	# SLOTS-01: one terminal panel, three case files in a row.
	assert_true(page.find_child("Slots", true, false) is CrtWindow, "one v2 terminal panel")
	var cards := _cards(t)
	assert_eq(cards.size(), 3)
	assert_eq((page.find_child("Cards", true, false) as GridContainer).columns, 3, "in a row at 1.0")
	assert_eq(cards[0].get_global_rect().position.y, cards[2].get_global_rect().position.y, "side by side")
	# A used slot: the dossier's fields.
	var used := cards[0]
	var summary := RunManager.slot_summary("1")
	var name_l := used.find_child("CorpName", true, false) as Label
	assert_eq(name_l.text, t.corporation_name(String(summary["corporation"])).to_upper(), "the corporation's name")
	assert_eq(name_l.get_theme_font(&"font"), Palette.paper_bold(), "typed in Courier Prime Bold (corp paper, no stencil)")
	assert_eq(int(used.find_child("HeatBar", true, false).get_meta(&"heat")), int(summary["heat"]), "the Heat bar")
	assert_eq((used.find_child("HeatValue", true, false) as Label).text, str(int(summary["heat"])), "and its number")
	assert_not_null(used.find_child("Emblem", true, false), "the corporation's emblem disc")
	assert_not_null(CorpSeal.emblem(StringName(String(summary["corporation"]))), "the art pass's emblem asset")
	for n in ["Ice", "Runs", "LastPlayed"]:
		assert_not_null(used.find_child(n, true, false), "the %s field" % n)
	var chips := used.find_children("Crew_*", "CrewChip", true, false)
	assert_eq(chips.size(), mini(t.slot_crew("1").size(), CaseFileCard.CREW_MAX), "the crew's portrait chips")
	for c in chips:
		assert_eq((c as Control).focus_mode, Control.FOCUS_NONE, "a portrait is not a focus stop")
	# Empty slots: dashed, EMPTY SLOT / No campaign filed here yet., and NEW CAMPAIGN.
	for k in [1, 2]:
		assert_eq((cards[k].find_child("Empty", true, false) as Label).text, "EMPTY SLOT")
		assert_eq((cards[k].find_child("EmptyHint", true, false) as Label).text, "No campaign filed here yet.")
		assert_not_null(cards[k].new_button, "an empty slot starts a campaign")
		assert_null(cards[k].load_button)
	cards[1].new_button.pressed.emit()
	assert_eq(RunManager.save_slot, "2", "NEW CAMPAIGN starts in its own slot")


func test_load_and_delete_are_stickers_and_delete_says_cant_undo_in_pencil() -> void:
	# Designer rulings 2026-10-05 (SLOTS b, c): every used slot carries two sticker verbs, the
	# pink LOAD and DELETE (4C's baked dialog_delete), with a red grease-pencil "Can't Undo"
	# arrow pointing at DELETE; the newest campaign's LOAD takes the first focus.
	_save_slots(3)
	var t := _title()
	await _frames(2)
	t.show_slots()
	await _frames(3)
	var cards := _cards(t)
	for c in cards:
		assert_true(c.load_button is VerbSticker and (c.load_button as VerbSticker).fill == VerbSticker.Fill.PINK, "slot %s: LOAD is the pink sticker" % c.slot)
		assert_true(c.delete_button is VerbSticker, "slot %s: DELETE is a sticker" % c.slot)
	var primaries := cards.filter(func(c: CaseFileCard) -> bool: return c.primary)
	assert_eq(primaries.size(), 1, "one newest campaign")
	var newest: CaseFileCard = primaries[0]
	assert_eq(RunManager.latest_slot(), newest.slot, "the newest campaign")
	assert_eq(t._default_focus(t._panel), newest.load_button, "the newest campaign's LOAD takes the focus first")
	var other := cards[0] if newest != cards[0] else cards[1]
	for c: CaseFileCard in cards:
		var del := c.delete_button as VerbSticker
		assert_not_null(del, "DELETE is a sticker")
		assert_true(del.uses_art() and del.art_key == CaseFileCard.DELETE_ART, "4C's baked DELETE sticker")
		assert_lte(del.size.y, CaseFileCard.DELETE_ART_SCALE * 100.0, "at about LOAD's size, not the dialog's (93 px)")
		var note := c.cant_undo
		assert_not_null(note, "Can't Undo in grease pencil at 1.0")
		assert_eq(note.text.replace("
", " "), "Can't Undo")
		assert_eq(note.colour, Palette.PENCIL_THREAT, "red pencil: a loss")
		var arrow := note.get_node("Arrow") as GreasePencilMark
		assert_gt(arrow.strokes().size(), 0, "with its arrow")
		var head: Vector2 = note.get_global_transform() * note.arrow_to
		assert_lt(head.x, del.get_global_rect().position.x, "the arrow stops short of DELETE (no UI over pencil)")
		assert_gt(head.x, del.get_global_rect().position.x - 45.0, "pointing at it")
		assert_eq(PencilLint.violations(c).size(), 0, "nothing in the card covers the pencil: %s; load %s del %s row %s" % [PencilLint.violations(c), c.load_button.size, c.delete_button.size, c.delete_button.get_parent().size])
	# The paper sliver is the art pass's print stock.
	assert_not_null(CaseFileCard.print_stock(), "the art pass's paper stock")
	other.delete_button.pressed.emit()
	await _frames(2)
	assert_true(t._confirm is AbandonDialog, "DELETE asks first (the abandon dialog)")
	(t._confirm as ConfirmDialog).no_button.pressed.emit()
	await _frames(2)
	other.load_button.pressed.emit()
	assert_eq(RunManager.save_slot, other.slot, "LOAD loads its slot")


func test_slots_fit_and_focus_reaches_every_action_at_every_text_scale() -> void:
	for used in [1, 2, 3]:
		for slot in SLOT_IDS:
			RunManager.delete_slot(slot)
		_save_slots(used)
		for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
			Settings.set_text_scale(scale)
			var t := _title()
			await _frames(2)
			t.show_slots()
			await _frames(5)
			var floor_y: float = (t.ticker as Control).get_global_rect().position.y
			var cards := _cards(t)
			var win := t._panel.find_child("Slots", true, false) as CrtWindow
			var back := t._panel.find_child("Back", true, false) as Control
			assert_true(SCREEN.encloses(win.get_global_rect()), "%d used, %.1f: the panel %s on the screen" % [used, scale, win.get_global_rect()])
			assert_lte(back.get_global_rect().end.y, floor_y + 1.0, "%d used, %.1f: Back above the ticker" % [used, scale])
			# Up to 1.6 a whole case file (tab to actions) shows in the panel's view; at 2.0 a
			# card is taller than the room left under the sticker, and the view follows the focus:
			# the focused card's actions are in sight.
			var view := win.fit.scroll.get_global_rect()
			var focused := get_viewport().gui_get_focus_owner()
			for c in cards:
				if scale < Settings.TEXT_SCALE_MAX and focused != null and c.is_ancestor_of(focused):
					assert_true(view.grow(1.0).encloses(c.get_global_rect()), "%d used, %.1f: the focused case file %s whole in the view %s" % [used, scale, c.get_global_rect(), view])
			assert_not_null(focused, "%d used, %.1f: an action holds the focus" % [used, scale])
			if focused != null:
				assert_true(view.grow(1.0).encloses(focused.get_global_rect()), "%d used, %.1f: the focused %s %s in the view %s" % [used, scale, focused.name, focused.get_global_rect(), view])
			for c in cards:
				var f := c.folder.get_global_rect()
				assert_lte(f.size.x, SCREEN.size.x, "a card fits the width at %.1f" % scale)
				for l in c.folder.find_children("*", "Label", true, false):
					var r := (l as Control).get_global_rect()
					assert_true(f.grow(1.0).encloses(r), "%d used, %.1f slot %s: '%s' %s inside its folder %s" % [used, scale, c.slot, (l as Label).text, r, f])
				for a in c.actions():
					assert_lte(a.get_global_rect().end.x, f.end.x + 1.0, "%.1f slot %s: %s under its folder" % [scale, c.slot, a.name])
				if c.delete_button == null:
					continue
				# The pencil up to 1.6; at 2.0 its words move into DELETE's tooltip.
				if scale <= CaseFileCard.PENCIL_UP_TO:
					assert_not_null(c.cant_undo, "%.1f slot %s: Can't Undo in pencil" % [scale, c.slot])
					if c.cant_undo != null:
						var nr := Rect2(c.cant_undo.global_position, c.cant_undo.text_size())
						assert_lte(nr.end.x, c.delete_button.get_global_rect().position.x, "%.1f slot %s: the words clear of DELETE" % [scale, c.slot])
						assert_gte(nr.position.x, c.load_button.get_global_rect().end.x, "%.1f slot %s: and of LOAD" % [scale, c.slot])
				else:
					assert_null(c.cant_undo, "2.0: no pencil")
					assert_string_contains(c.delete_button.tooltip_text, "Can't Undo", "2.0: DELETE's tooltip says it")
			# Pad / keyboard: every LOAD, DELETE and NEW CAMPAIGN and Back reachable from the first.
			var want: Array[Control] = [back]
			for c in cards:
				want.append_array(c.actions())
			var seen: Array[Control] = [cards[0].actions()[0]]
			var i := 0
			while i < seen.size():
				var c: Control = seen[i]
				for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
					var path := c.get_focus_neighbor(side)
					if path.is_empty():
						continue
					var n := c.get_node_or_null(path) as Control
					if n != null and not seen.has(n):
						seen.append(n)
				i += 1
			for w in want:
				assert_true(seen.has(w), "%d used, %.1f: focus reaches %s/%s" % [used, scale, w.get_parent().get_parent().name, w.name])
			t.queue_free()
			await _frames(1)


func test_the_slots_panel_wraps_its_cards_then_scrolls_past_its_room() -> void:
	_save_slots(1)
	var t := _title()
	await _frames(2)
	t.show_slots()
	await _frames(5)
	var win := t._panel.find_child("Slots", true, false) as CrtWindow
	var floor_y: float = (t.ticker as Control).get_global_rect().position.y
	assert_false(win.fit.overflowing(), "1.0: the cards fit")
	assert_lt(win.get_global_rect().end.y, floor_y - 100.0, "SLOTS-04: the panel wraps its cards (the city shows below)")
	t.queue_free()
	await _frames(1)
	for slot in SLOT_IDS:
		RunManager.delete_slot(slot)
	_save_slots(3)
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	t = _title()
	await _frames(2)
	t.show_slots()
	await _frames(5)
	win = t._panel.find_child("Slots", true, false) as CrtWindow
	floor_y = (t.ticker as Control).get_global_rect().position.y
	assert_true(win.fit.overflowing(), "2.0, three case files stacked: past the room, the cards scroll")
	assert_true(win.fit.hint.overflows(), "with the kit's ScrollHint")
	var back := t._panel.find_child("Back", true, false) as Control
	assert_lte(back.get_global_rect().end.y, floor_y + 1.0, "and the page stays over the ticker")
	assert_gt(back.get_global_rect().end.y, floor_y - 40.0, "using the room it has")


# --- The abandon dialog look ------------------------------------------------------------------

func test_the_confirm_is_yellow_cancel_by_default_and_a_pink_verb() -> void:
	var t := _title()
	await _frames(2)
	_saved_campaign()
	t.confirm_delete("1")
	await _frames(2)
	var d: ConfirmDialog = t._confirm
	# The round 33 abandon dialog on 2D's ConfirmDialog: abandon.py's own stickers (yellow
	# CANCEL, the pink verb, baked with their focus halo), the delete is destructive (CANNOT
	# UNDO) and names its verb; CANCEL keeps the focus.
	assert_true(d.no_button is VerbSticker and d.yes_button is VerbSticker, "two vinyl stickers")
	assert_true((d.no_button as VerbSticker).uses_art() and (d.yes_button as VerbSticker).uses_art(), "the concept's baked stickers")
	assert_eq((d.no_button as VerbSticker).fill, VerbSticker.Fill.YELLOW, "the safe answer is yellow")
	assert_eq((d.yes_button as VerbSticker).fill, VerbSticker.Fill.PINK, "the verb is pink")
	assert_eq(d.yes_button.text, "DELETE", "the committing verb")
	assert_true(d.panel.destructive, "a delete says it cannot be undone")
	assert_eq(get_viewport().gui_get_focus_owner(), d.no_button, "CANCEL holds the default focus")
	var esc := InputEventAction.new()
	esc.action = &"ui_cancel"
	esc.pressed = true
	d._unhandled_input(esc)
	await _frames(2)
	assert_false(t.confirm_visible(), "B / Esc cancels at once")


func test_the_codex_and_stats_pages_fit_over_the_ticker_at_every_text_scale() -> void:
	_saved_campaign()
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var t := _title()
		await _frames(2)
		var floor_y: float = (t.ticker as Control).get_global_rect().position.y
		for page in ["codex", "stats"]:
			t.call("show_" + page)
			await _frames(3)
			var p := t._panel as Control
			for n in ["Codex", "Stats", "History"]:
				var c := p.find_child(n, true, false) as Control
				if c != null:
					assert_lte(c.get_global_rect().end.y, floor_y + 1.0, "%s above the ticker at %.1f" % [n, scale])
			var back: Control = null
			for b in p.find_children("*", "Button", true, false):
				if (b as Button).text == tr("Back"):
					back = b
			assert_not_null(back, "%s has its Back" % page)
			if back != null:
				assert_lte(back.get_global_rect().end.y, floor_y + 1.0, "%s Back above the ticker at %.1f" % [page, scale])
		t.queue_free()
		await _frames(1)


func test_a_page_entering_late_leaves_the_focus_on_the_open_confirm() -> void:
	_saved_campaign()
	var t := _title()
	await _frames(2)
	t.confirm_delete("gut_art10")
	await _frames(2)
	var d: ConfirmDialog = t._confirm
	assert_eq(get_viewport().gui_get_focus_owner(), d.no_button, "CANCEL holds the focus")
	# The main page's enter finishing after the confirm opened (windowed, its motion runs).
	t._page_focus(t._panel, t.verbs[0])
	await _frames(1)
	assert_eq(get_viewport().gui_get_focus_owner(), d.no_button, "the page behind never takes the focus")
	# The header's words are not under the CRT material (it samples the MSDF atlas raw).
	var internal := d.panel.get_children(true).filter(func(c: Node) -> bool: return c.name == "HeaderWords")
	assert_eq(internal.size(), 1, "the header's words have their own canvas item")
	assert_null((internal[0] as CanvasItem).material, "with no CRT material")


func test_the_delete_confirm_is_the_abandon_dialog_with_the_slots_costs() -> void:
	_saved_campaign()
	var summary := RunManager.slot_summary("gut_art10")
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var t := _title()
		await _frames(2)
		t.confirm_delete("gut_art10")
		await _frames(3)
		var d := t._confirm as AbandonDialog
		assert_not_null(d, "the delete confirm is the round 33 abandon dialog")
		if d == null:
			return
		# The costs read from the slot (round 33: names in terminal CAPS, values beside them).
		var words := d.cost_words()
		assert_eq(words.size(), 8, "four costs, name and value")
		assert_true(words.has(t.corporation_name(String(summary["corporation"]))), "the target corporation")
		assert_true(words.has(str(int(summary["heat"]))), "the slot's Heat")
		assert_true(d.kept_label != null and d.kept_label.text != "", "what stays is said")
		assert_eq(d.kept_label.get_theme_color(&"font_color"), Palette.GAIN, "what stays reads in GAIN")
		assert_true(d.panel.destructive, "CANNOT UNDO")
		# Centred on the screen and on it whole, at every text size.
		var r := d.panel.get_global_rect()
		assert_true(SCREEN.encloses(r), "the dialog %s on the screen at %.1f" % [r, scale])
		assert_almost_eq(r.get_center().x, SCREEN.get_center().x, 2.0, "centred across at %.1f" % scale)
		t.queue_free()
		await _frames(1)


# --- Vinyl sticker, neon sign, ticker -----------------------------------------------------------

func test_sticker_motions_show_their_end_state_headless() -> void:
	var h: Control = add_child_autofree(Control.new())
	# BLUE (drawn here) and PINK (Group 1B's VinylSticker inside) grow and squash alike.
	var blue := VerbSticker.new("OVERTHROW", VerbSticker.Fill.BLUE, 40.0)
	var pink := VerbSticker.new("BURN IT", VerbSticker.Fill.PINK, 40.0)
	h.add_child(blue)
	h.add_child(pink)
	await _frames(1)
	assert_null(blue.vinyl, "BLUE has no kit fill: drawn here")
	assert_not_null(pink.vinyl, "PINK is the kit's vinyl sticker")
	for pair in [[blue, blue], [pink, pink.vinyl]]:
		var s: VerbSticker = pair[0]
		var shown: Control = pair[1]
		s._hot(true)
		assert_almost_eq(shown.scale.x, Motion.amplitude(VerbSticker.HOVER_MOTION), 0.001, "hover: the grown size at once")
		s._press(true)
		assert_almost_eq(shown.scale.y, Motion.amplitude(VerbSticker.PRESS_MOTION), 0.001, "press: squashed at once")
		s._press(false)
		s._hot(false)
		assert_almost_eq(shown.scale.x, 1.0, 0.001, "rest")
		assert_true(UiFocus.META_NO_SCALE in s.get_meta_list(), "a sticker grows itself: no pad focus scale")
	pink.disabled = true
	assert_eq(pink.state(), KitState.DISABLED)
	assert_gt(pink.get_combined_minimum_size().x, 0.0, "it takes the kit sticker's size")


func test_the_glitch_sign_and_ticker_hold_still_headless() -> void:
	var h: Control = add_child_autofree(Control.new())
	var sim := VerbSticker.new("SIMULATE", VerbSticker.Fill.GLITCH, 40.0)
	var sign := NeonSign.new()
	var ticker := OnAirTicker.new(PackedStringArray(["PIRATE RADIO 88.1"]))
	for c in [sim, sign, ticker]:
		h.add_child(c)
	await _frames(5)
	assert_false(sim.bursting(), "no glitch burst headless (its end state: the light split)")
	assert_eq(sign.frame(), -1, "the sign holds fully lit")
	assert_eq(ticker._offset, 0.0, "the ticker holds still")


func test_the_sign_is_the_concept_art_and_loops_its_lit_states() -> void:
	# The baked round 33 title.py sign: one image per lit state of its 48-frame loop.
	var m := NeonSign.meta()
	var frames: Array = m.get("frames", [])
	assert_eq(frames.size(), 48, "the concept's 48-frame loop")
	assert_eq(NeonSign.state_at(-1), 0, "held: fully lit")
	var states := {}
	for f in frames:
		states[int(f)] = true
	assert_gte(states.size(), 4, "lit, cursor off, the E stutter, the drop to CELL")
	for i in states:
		assert_true(ResourceLoader.exists(NeonSign.DIR + "sign_%d.png" % i), "state %d baked" % i)
	assert_true(VerbSticker.title_art("OPTIONS") != "", "the OPTIONS title sticker is baked")
	assert_eq(VerbSticker.title_art("NOT A BAKED WORD"), "", "no art: the kit's sticker draws it")
	var h: Control = add_child_autofree(Control.new())
	var b := VerbSticker.new("BREACH", VerbSticker.Fill.PINK, 36.0, 0.0, "breach")
	h.add_child(b)
	await _frames(1)
	assert_true(b.uses_art() and b.vinyl == null, "BREACH is the concept's sticker art")
	assert_true(UiMotionData.REQUIRED_IDS.has(NeonSign.MOTION))
	for id in [VerbSticker.HOVER_MOTION, VerbSticker.PRESS_MOTION, VerbSticker.GLITCH_MOTION, OnAirTicker.MOTION]:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(Motion.has(id), "%s is in ui_motion.tres" % id)


# --- Options ------------------------------------------------------------------------------------

func test_options_rows_are_switches_tiles_and_drive_settings() -> void:
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	await _frames(1)
	assert_true(panel.reduce_check is CrtSwitch, "a switch row")
	assert_eq((panel.reduce_check as CrtSwitch).parts()[0], "REDUCE EFFECTS", "the name in CAPS")
	assert_true(UiFocus.META_NO_SCALE in panel.reduce_check.get_meta_list(), "full-width rows never scale on pad focus (ART-0 carry-over)")
	var was := Settings.reduce_motion
	panel.reduce_motion_check.button_pressed = not was
	assert_eq(Settings.reduce_motion, not was, "the switch drives Settings")
	var tiles := panel.colorblind_tiles
	assert_eq(tiles.tiles.size(), Settings.COLORBLIND_MODES.size(), "one tile per mode")
	tiles.pick(Settings.COLORBLIND_MODES.find(&"deutan"))
	assert_eq(Settings.colorblind_mode, &"deutan", "a tile picks the mode")
	assert_true(tiles.tiles[Settings.COLORBLIND_MODES.find(&"deutan")].selected, "the picked tile is selected (cyan)")
	panel.resolve_tiles.pick(Settings.RESOLVE_SPEEDS.find(&"instant"))
	assert_eq(Settings.resolve_speed, &"instant")


func test_heat_glitch_says_limited_under_the_flash_limiter() -> void:
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	await _frames(1)
	Settings.set_heat_glitch(true)
	Settings.set_reduce_effects(false)
	Settings.set_flash_limiter(true)
	assert_string_contains(panel._glitch_note(), "LIMITED", "flash limiter on: LIMITED")
	Settings.set_flash_limiter(false)
	assert_eq(panel._glitch_note(), "", "nothing limits it")
	Settings.set_heat_glitch(false)
	assert_eq(panel._glitch_note(), "", "off: no chip")


func test_options_stack_and_fit_at_text_scale_two() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	await _frames(1)
	assert_false(panel.two_columns(), "big text: one column")
	for section in SettingsPanel.SECTIONS:
		panel.show_section(section)
		assert_lte(panel.get_combined_minimum_size().x, SCREEN.size.x, "%s fits the width at 2.0" % section)


func test_the_pause_menu_is_a_terminal_with_no_sticker_and_one_column_options() -> void:
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames(2)
	assert_true(menu._panel is CrtWindow, "terminal glass")
	assert_null(menu.find_child("TitleSticker", true, false), "PAUSE-01: no PAUSED sticker")
	menu.show_options()
	assert_false(menu.settings_panel.two_columns(), "one column inside the menu")
	assert_lte(menu.settings_panel.get_combined_minimum_size().x, PauseMenu.MENU_SIZE.x)
	menu.show_codex()
	assert_true(menu.codex_note is CrtText, "the codex is terminal text")


# --- HQ ------------------------------------------------------------------------------------------

func test_the_hq_is_v2_terminals_with_a_corp_paper_dossier() -> void:
	# HQ-B (b) (designer, direction B): the HQ's windows are the v2 kit: the selected Site's card
	# is a CRT terminal, the DJ is the ON AIR ticker (Q7), the crew are hand cards with their
	# photo prints, JACK IN is the pink vinyl sticker. (The corp-paper dossier went with the
	# crew window; the work order keeps corp paper.)
	var hq: Control = add_child_autofree(load(HQ).instantiate())
	hq.new_campaign(2)
	await _frames(2)
	assert_true(hq._panel.find_child("SelectedSite", true, false) is CrtWindow, "the Site's card is a v2 terminal")
	assert_true(hq._panel.find_child("OnAir", true, false) is OnAirTicker, "the DJ on the Cell's feed (ON AIR)")
	var card := hq._panel.find_child("Crew_%s" % RunManager.campaign.roster[0].id, true, false) as CrewHandCard
	assert_not_null(card, "the crew as hand cards")
	assert_eq(card.display_name, RunManager.campaign.roster[0].name)
	var jack := hq._panel.find_child("Launch", true, false) as VerbSticker
	assert_true(jack != null and jack.fill == VerbSticker.Fill.PINK, "JACK IN is the pink vinyl sticker")
