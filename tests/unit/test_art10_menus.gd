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
		assert_false(more.intersects(verbs.grow(-1.0)), "MORE clear of the verbs at %.1f" % scale)
		t.queue_free()
		await _frames(1)


# --- The abandon dialog look ------------------------------------------------------------------

func test_the_confirm_is_yellow_cancel_by_default_and_a_pink_verb() -> void:
	var t := _title()
	await _frames(2)
	_saved_campaign()
	t.confirm_delete("1")
	await _frames(2)
	var d: ConfirmDialog = t._confirm
	# 2D's ConfirmDialog (the round 33 abandon dialog look): two vinyl stickers, the delete is
	# destructive (CANNOT UNDO) and names its verb; CANCEL keeps the focus.
	assert_true(d.no_button is SendItSticker and d.yes_button is SendItSticker, "two vinyl stickers")
	assert_eq((d.yes_button as SendItSticker).tag_text, "DELETE", "the committing verb")
	assert_true(d.panel.destructive, "a delete says it cannot be undone")
	assert_eq(get_viewport().gui_get_focus_owner(), d.no_button, "CANCEL holds the default focus")
	var esc := InputEventAction.new()
	esc.action = &"ui_cancel"
	esc.pressed = true
	d._unhandled_input(esc)
	await _frames(2)
	assert_false(t.confirm_visible(), "B / Esc cancels at once")


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


func test_the_pause_menu_is_a_terminal_with_its_sticker_and_one_column_options() -> void:
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames(2)
	assert_true(menu._panel is CrtWindow, "terminal glass")
	assert_eq(menu.title_sticker.shown_text(), "PAUSED")
	menu.show_options()
	assert_false(menu.settings_panel.two_columns(), "one column inside the menu")
	assert_lte(menu.settings_panel.get_combined_minimum_size().x, PauseMenu.MENU_SIZE.x)
	menu.show_codex()
	assert_true(menu.codex_note is CrtText, "the codex is terminal text")


# --- HQ ------------------------------------------------------------------------------------------

func test_the_hq_is_v2_terminals_with_a_corp_paper_dossier() -> void:
	var hq: Control = add_child_autofree(load(HQ).instantiate())
	hq.new_campaign(2)
	await _frames(2)
	var crt := 0
	for w in hq._panel.find_children("*", "TerminalWindow", true, false):
		if w is CrtWindow:
			crt += 1
	assert_gte(crt, 4, "CYBERDECK, CELL STATUS, CITY GRID, CREW ... are v2 terminals")
	assert_true(hq._panel.find_child("PirateRadio", true, false) is CrtText, "the DJ on the Cell's feed")
	var card := hq._panel.find_child("Crew_%s" % RunManager.campaign.roster[0].id, true, false) as CrewCard
	var name_label: Label = null
	for l in card.find_children("*", "Label", true, false):
		if (l as Label).text == RunManager.campaign.roster[0].name.to_upper():
			name_label = l
	assert_not_null(name_label)
	assert_eq(name_label.get_theme_font(&"font"), Palette.paper_bold(), "the dossier's name in Courier Prime (corp paper)")
	# Every current HQ action stays reachable (G13 not ruled: nothing removed).
	for n in ["JackIn", "PirateRadio"]:
		assert_not_null(hq._panel.find_child(n, true, false), "%s still on the HQ" % n)
