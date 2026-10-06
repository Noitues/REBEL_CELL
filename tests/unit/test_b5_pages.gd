extends GutTest
## B5 (M14 art-direction integration review; DECISIONS "B5 — pages and review follow-ups (integration review)"):
## the pages the concepts never designed (round 44 `B_menus`, review sections c / d / f) and the B1 review
## follow-ups:
## - follow-up 1: a baked VerbSticker is shown by a kit VinylSticker (the focus fold cuts its corner away and the
##   adhesive back lies over the face, as on the kit stickers);
## - follow-up 2: no view uses the shared `crt_panel` material; every terminal is the kit's CRT glass, whose hex dump
##   fades under its words;
## - the menus: slots, new campaign, options, codex, stats, pause, the confirms, the deck viewer and loadout.

const BoundedWait := preload("res://tests/helpers/bounded_wait.gd")

var _scale := 1.0
var _reduce := false


func before_each() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	if Settings.text_scale != _scale:
		Settings.text_scale = _scale
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _scripts(dir: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_scripts(dir.path_join(d), out)


## The kit glass an owner carries (CrtTerminalPanel.behind), or null.
func _glass_of(owner: Control) -> CrtTerminalPanel:
	for c in owner.get_children(true):
		if c is CrtTerminalPanel and (c as CrtTerminalPanel).text_scope == owner:
			return c
	return null


# --- Follow-up 1: baked stickers are kit stickers ---------------------------------------------

func test_a_baked_verb_sticker_is_a_kit_sticker_whose_fold_cuts_its_corner_away() -> void:
	var h: Control = add_child_autofree(Control.new())
	var s := VerbSticker.new("CANCEL", VerbSticker.Fill.YELLOW, 28.0, 0.0, "dialog_cancel")
	h.add_child(s)
	await _frames(2)
	assert_true(s.uses_art(), "the concept's baked CANCEL")
	assert_not_null(s.vinyl, "shown by the kit's VinylSticker")
	assert_true(s.vinyl.is_baked(), "the kit sticker shows the baked image")
	var k := VerbSticker.ART_TO_GAME
	assert_eq(s.custom_minimum_size, (s._art_rest.get_size() * k).ceil(), "the button keeps the art's size")
	# the image lands on the button's own frame; the fold's corner is the opaque die-cut body's, not the image's
	var art := s.vinyl.art_rect()
	assert_almost_eq(s.vinyl.position + art.position, Vector2.ZERO, Vector2(0.01, 0.01))
	var body := s.vinyl.body_rect
	assert_almost_eq(body.size, s._art_body.size * k, Vector2(0.01, 0.01), "the fold's body is the die-cut")
	assert_gt(body.position.x, art.position.x, "inside the image's shadow margin")
	s.grab_focus()
	s.vinyl.complete_motion()
	await _frames(1)
	assert_eq(s.vinyl.state, VinylSticker.State.HOVER, "focus: the kit's peel-back")
	var mat := s.vinyl.material as ShaderMaterial
	assert_gt(float(mat.get_shader_parameter(&"peel_back")), 0.0, "the fold runs in the kit shader: the corner is cut away")
	assert_eq(float(mat.get_shader_parameter(&"rim")), 0.0, "the image keeps its own rim")
	assert_eq(float(mat.get_shader_parameter(&"shadow_k")), 0.0, "and its own shadow")
	assert_eq(float(mat.get_shader_parameter(&"gloss_k")), 0.0, "and its own gloss")


func test_the_glitch_sticker_swaps_its_burst_frames_on_the_kit_sticker() -> void:
	var h: Control = add_child_autofree(Control.new())
	var s := VerbSticker.new("SIMULATE", VerbSticker.Fill.GLITCH, 36.0, 0.0, "simulate")
	h.add_child(s)
	await _frames(1)
	assert_not_null(s.vinyl)
	assert_gt(s._art_bursts.size(), 0, "the concept's burst frames")
	Motion.force_live = true
	s._clock = Motion.seconds(VerbSticker.GLITCH_MOTION) * 9.5 / VerbSticker.LOOP_FRAMES
	assert_gte(s.burst_phase(), 0, "in a burst")
	s._show_burst()
	assert_eq(s.vinyl._baked["tex"], s._art_bursts[s.burst_phase()], "the burst frame shows")
	Motion.force_live = false
	s._clock = 0.0
	s._show_burst()
	assert_eq(s.vinyl._baked["tex"], s._art_rest, "at rest: the rest art")


func test_the_white_fill_is_the_kit_white_vinyl() -> void:
	var h: Control = add_child_autofree(Control.new())
	var s := VerbSticker.new("DELETE", VerbSticker.Fill.WHITE, 28.0)
	h.add_child(s)
	await _frames(1)
	assert_true(s.uses_kit())
	assert_eq(s.vinyl.fill, VinylSticker.Fill.WHITE, "round 44 FILL_WHITE: white vinyl lettering, ink keyline")
	assert_eq(s.sweep_rank(), 2, "never the page's primary by colour")


# --- Follow-up 2: every terminal is the kit's CRT glass ----------------------------------------

func test_no_view_uses_the_shared_crt_panel_material() -> void:
	var files: Array[String] = []
	_scripts("res://scripts", files)
	_scripts("res://tools/design_lab", files)
	var allowed := ["res://scripts/ui/kit/ui_theme.gd", "res://scripts/ui/kit/hud_skin.gd"]
	for path in files:
		if path in allowed:
			continue
		var src := FileAccess.get_file_as_string(path)
		assert_false(src.contains("crt_material()"), "%s still uses the shared crt_panel material" % path)


func test_every_terminal_kind_has_the_kit_glass_with_its_word_mask() -> void:
	var tw := TerminalWindow.new("NODE STATUS")
	var lbl := Label.new()
	lbl.text = "SOME WORDS ON THE GLASS"
	tw.body.add_child(lbl)
	var bar := HudBar.new()
	var dlg := ConfirmDialog.new("Quit?", "QUIT", "CANCEL", "QUIT", "Your campaign is autosaved.", false, "", "keep going [B]")
	var note := TerminalNote.new("TUTORIAL")
	var host: Control = add_child_autofree(Control.new())
	host.size = Vector2(1280, 720)
	for c: Control in [tw, bar, dlg, note]:
		host.add_child(c)
	tw.size = Vector2(400, 200)
	note.size = Vector2(300, 160)
	await _frames(3)
	for owner: Control in [tw, bar, dlg.panel, note]:
		var g := _glass_of(owner)
		assert_not_null(g, "%s: the kit's CRT glass" % owner.get_class())
		if g == null:
			continue
		assert_null(owner.material, "%s: no shared crt_panel material" % owner.get_class())
		assert_true(g.show_behind_parent, "under the owner's own edge and words")
		assert_almost_eq(g.hex_alpha(), CrtTerminalPanel.HEX_ALPHA, 0.0001, "the 6 % hex dump")
	var g_tw := _glass_of(tw)
	g_tw.refresh_text_mask()
	assert_gt(g_tw.text_rects().size(), 0, "the window's words fade the dump (B1c-b word mask)")
	var mat := g_tw.material as ShaderMaterial
	assert_gt(int(mat.get_shader_parameter(&"hex_text_count")), 0, "the rects reach the shader")
	assert_eq(tw.get_theme_stylebox(&"panel").get(&"bg_color").a, 0.0, "the window box has no fill: the glass is it")


## Art director B5 fix 1: the body of every migrated terminal is the navy glass whatever its accent; the accent is on
## the edge, title and keyline only. Nothing of the owner's own box (a fill, an edge-glow shadow) shows through.
func _assert_navy_body(owner: Control, accent: Color, what: String) -> void:
	var g := _glass_of(owner)
	assert_not_null(g, "%s: the kit glass" % what)
	if g == null:
		return
	var m := g.material as ShaderMaterial
	assert_eq(m.get_shader_parameter(&"glass_top"), PaletteSkins.chrome(Palette.CRT_GLASS_TOP), "%s: navy glass top" % what)
	assert_eq(m.get_shader_parameter(&"glass_bottom"), PaletteSkins.chrome(Palette.CRT_GLASS_BOTTOM), "%s: navy glass foot" % what)
	assert_eq(Color(m.get_shader_parameter(&"accent")), PaletteSkins.chrome(accent), "%s: the accent is the edge's" % what)
	for sb_name in [&"panel", &"normal"]:
		if not owner.has_theme_stylebox(sb_name):
			continue
		var sb := owner.get_theme_stylebox(sb_name)
		if sb is StyleBoxFlat:
			var f := sb as StyleBoxFlat
			assert_eq(f.bg_color.a, 0.0, "%s: its own box has no fill over the glass" % what)
			assert_true(f.shadow_size == 0 or f.shadow_color.a == 0.0, "%s: no edge-glow shadow washing through the clear box" % what)
	for c in owner.get_children(true):
		if c is ColorRect and (c as CanvasItem).show_behind_parent:
			assert_eq((c as ColorRect).color.a, 0.0, "%s: no fill rect over the glass" % what)


func test_every_migrated_terminal_body_is_navy_glass_for_every_accent() -> void:
	var host: Control = add_child_autofree(Control.new())
	host.size = Vector2(1280, 720)
	for accent in [Palette.NET_CYAN, Palette.CELL_ACID, Palette.HARM, Palette.CELL_PINK, Palette.NEON_VIOLET, Palette.CORP_SOLACE]:
		var tw := TerminalWindow.new("REPORT", accent)
		host.add_child(tw)
		await _frames(1)
		_assert_navy_body(tw, accent, "TerminalWindow %s" % accent)
	var bar := HudBar.new()
	var dlg := ConfirmDialog.new("Quit?", "QUIT", "CANCEL", "QUIT", "Saved.", true, "", "keep going [B]")
	var note := TerminalNote.new("TUTORIAL")
	var zine := ZinePanel.new("OPTIONS", 0.0, true)
	for c: Control in [bar, dlg, note, zine]:
		host.add_child(c)
	await _frames(2)
	_assert_navy_body(bar, Palette.NET_CYAN, "HudBar")
	_assert_navy_body(dlg.panel, (dlg.panel as HudDialogPanel).edge_color(), "HudDialogPanel (destructive)")
	_assert_navy_body(note, Palette.NET_CYAN, "TerminalNote")
	_assert_navy_body(zine, Palette.NET_CYAN, "ZinePanel terminal")
	# The netrun / HQ panel hosts and logs: their theme boxes lie clear over the glass.
	var themed: Control = Control.new()
	themed.theme = UiTheme.build()
	host.add_child(themed)
	for v in [[UiTheme.CRT_GLASS_PANEL, "PanelContainer"], [UiTheme.CRT_LOG_TEXT, "RichTextLabel"]]:
		var c: Control = PanelContainer.new() if v[1] == "PanelContainer" else RichTextLabel.new()
		c.theme_type_variation = v[0]
		themed.add_child(c)
		CrtTerminalPanel.behind(c)
		await _frames(1)
		_assert_navy_body(c, Palette.NET_CYAN, String(v[0]))

# --- Follow-up 3: words over the world carry an ink keyline ------------------------------------

func test_the_title_foot_line_and_pad_prompts_carry_the_ink_keyline() -> void:
	assert_gte(float(Chrome.keyline_size()) * 0.5 * Chrome.BOARD_H / Chrome.LAYOUT_H, Chrome.KEYLINE_1080, ">= 3 px at 1080p")
	var t: Control = add_child_autofree(load("res://scenes/menu/title_scene.tscn").instantiate())
	await _frames(2)
	var build := t.find_child("Build", true, false) as Label
	assert_eq(build.get_theme_constant(&"outline_size"), Chrome.keyline_size(), "the foot line's keyline")
	assert_eq(build.get_theme_color(&"font_outline_color"), Chrome.KEYLINE_INK)
	for v in t.find_children("Verb", "Label", true, false):
		assert_eq((v as Label).get_theme_constant(&"outline_size"), Chrome.keyline_size(), "the pad prompt '%s'" % (v as Label).text)
	assert_true(t.ticker.visible, "ON AIR on the title's main page (D20)")
	t.show_slots()
	await _frames(2)
	assert_false(t.ticker.visible, "D20: no ON AIR on a sub-page")
	assert_true(t.sub_foot.visible, "its foot line and pad prompts instead")
	var line := t.sub_foot.find_child("FootLine", true, false) as Label
	assert_eq(line.get_theme_constant(&"outline_size"), Chrome.keyline_size())


# --- Slots (D21, D24, designer ruling 2) --------------------------------------------------------

func test_a_slot_folder_is_the_cells_own_file_lying_tilted_on_the_glass() -> void:
	var c := CaseFileCard.new("2", {"corporation": "solace", "heat": 58, "ice": 1, "runs": 9, "saved_at": 1.7e9}, [], true)
	var h: Control = add_child_autofree(Control.new())
	h.add_child(c)
	await _frames(3)
	assert_eq(c.tab_clip.text, tr("SLOT %s // CELL-%02d") % ["2", 2], "the Cell's terminal tab clip")
	assert_true(c.stamp.baked(), "the Cell's red hex-and-fist stamp, the concept's own image")
	assert_eq(c.stamp.word, "ACTIVE")
	assert_between(absf(c.tilt), PaperLie.TILT_MIN_DEG, PaperLie.TILT_MAX_DEG, "D24: a seeded 1-2 degree tilt")
	assert_eq(c.tilt, PaperLie.tilt_deg(CaseFileCard.TILT_SEED + 2), "seeded (the same every time)")
	assert_almost_eq(c.folder.rotation_degrees, c.tilt, 0.001)
	c.load_button.grab_focus()
	await _frames(1)
	assert_almost_eq(c.folder.rotation_degrees, 0.0, 0.001, "the focused slot lies straight")
	assert_eq((c.load_button as VerbSticker).fill, VerbSticker.Fill.PINK)
	assert_true((c.load_button as VerbSticker).sweep_primary, "the newest LOAD carries the page's sweep")
	assert_eq((c.delete_button as VerbSticker).fill, VerbSticker.Fill.WHITE, "DELETE: the neutral white vinyl")
	assert_not_null(c.cant_undo, "with its CAN'T UNDO in pencil")
	assert_eq((c.find_child("CorpName", true, false) as Label).get_theme_font(&"font"), Palette.mono(), "printed in the Cell's mono")


func test_the_pad_x_deletes_the_focused_slot_and_it_asks_first() -> void:
	RunManager.save_slot = "1"
	RunManager.new_campaign(3)
	RunManager.autosave()
	var t: Control = add_child_autofree(load("res://scenes/menu/title_scene.tscn").instantiate())
	await _frames(2)
	t.show_slots()
	await _frames(4)
	var card := t._panel.find_child("Slot1", true, false) as CaseFileCard
	card.load_button.grab_focus()
	await _frames(1)
	var x := InputEventJoypadButton.new()
	x.button_index = JOY_BUTTON_X
	x.pressed = true
	t._unhandled_input(x)
	await _frames(2)
	assert_true(t._confirm is AbandonDialog, "X asks first (the abandon dialog)")
	RunManager.delete_slot("1")


func test_paper_lies_with_a_clip_a_tilt_and_a_soft_shadow() -> void:
	for seed in [1, 7, 42, 2100]:
		var a := absf(PaperLie.tilt_deg(seed))
		assert_between(a, PaperLie.TILT_MIN_DEG, PaperLie.TILT_MAX_DEG, "seed %d" % seed)
		assert_eq(PaperLie.tilt_deg(seed), PaperLie.tilt_deg(seed), "seeded")
	assert_almost_eq(PaperLie.shadow_px(1080.0), 6.0, 0.001, "a 6 px contact shadow at 1080p")
	var p := CorpPaperPanel.new()
	add_child_autofree(p)
	assert_true(p.clip, "D24: the work order / dossier wears the concepts' paper clip")
	assert_not_null(PaperLie.CLIP, "the clip is the concept kit's own (tools/art/export_paper_clip.py)")
	var sheet := PaperSheet.new()
	add_child_autofree(sheet)
	assert_true(sheet.clip, "the dossier's sheets too")


# --- New campaign (review section f) -------------------------------------------------------------

func test_the_new_campaign_tiles_mark_the_choice_with_an_edge_and_corps_on_holo_chips() -> void:
	var p := PlanningPicker.new([{"name": "SOLACE", "corp": &"solace"}, {"name": "MERIDIAN", "corp": &"meridian"}] as Array[Dictionary], 0, Vector2(150, 60))
	var h: Control = add_child_autofree(Control.new())
	h.size = Vector2(800, 200)
	h.add_child(p)
	p.size = Vector2(800, 120)
	await _frames(3)
	assert_false(p.fill_selected, "selected = the cyan edge and its SELECTED tab, never a solid fill")
	var chips := p.find_children("HoloChip*", "DecryptedHoloPanel", true, false)
	assert_eq(chips.size(), 2, "each corporation's crest on a small holo chip")
	var chip := chips[0] as DecryptedHoloPanel
	assert_false(chip.seal, "no seal on a chip")
	assert_false(chip.stamp_slot.visible, "no stamp on a chip")
	assert_false(chip.scrim, "no screen scrim")


# --- Codex (D11 / Q13) ---------------------------------------------------------------------------

func test_the_codex_corporations_open_an_intercepted_holo_card_never_paper() -> void:
	var entries := Codex.entries(RunManager.lookup())
	var book: CodexBook = add_child_autofree(CodexBook.new(entries, 0.0, 1200.0))
	await _frames(2)
	assert_true(book.frame is CrtWindow, "terminal glass")
	book.show_section(CodexBook.CORP_SECTION)
	await _frames(2)
	assert_not_null(book.holo_card, "the picked corporation's holo card")
	assert_true(book.holo_card.holo is DecryptedHoloPanel, "the kit's decrypted holo")
	# Art director B5 fix 5: the DECRYPTED stamp stands in the header's corner, clear of the header's words.
	await _frames(2)
	var card := book.holo_card
	var stamp_r := Rect2(card.global_position + card.holo.stamp_slot.position, card.holo.stamp_slot.size)
	var header := card.find_child("Header", true, false) as Control
	assert_lt(stamp_r.position.y - card.global_position.y, DecryptedHoloPanel.STAMP_SLOT.y, "in the card's top corner (seen at 720 without scrolling)")
	assert_false(stamp_r.intersects(header.get_global_rect()), "never over the header's words")
	var first: StringName = book.holo_card.corporation
	book.page.grab_focus()
	var down := InputEventAction.new()
	down.action = &"ui_down"
	down.pressed = true
	book._on_page_input(down)
	await _frames(1)
	assert_eq(book.selected_corp, 1, "down picks the next corporation")
	if book.holo_card != null:
		assert_ne(book.holo_card.corporation, first, "its card shows")
	for row in book.columns.find_children("Tile", "", true, false):
		assert_true((row as Control).has_meta(&"tile_edge"), "every entry's glyph sits in its tile")


# --- Stats (review section c) ---------------------------------------------------------------------

func test_run_history_rows_are_terminal_log_lines_with_stickers_only_for_completed_and_flatlined() -> void:
	var outcomes := {"completed": true, "died": true, "aborted": false, "none": false}
	for o in outcomes:
		var row: RunLogRow = add_child_autofree(RunLogRow.of_run({"corporation": "solace", "tier": 1, "site": "t1", "outcome": o, "cycles": 3, "banked": 1}, "Solace", 0))
		assert_eq(row.sticker != null, outcomes[o], "%s: a sticker only for COMPLETED / FLATLINED" % o)
		assert_eq(row.theme_type_variation, &"MenuItem", "a terminal row (caret and brackets on focus)")
	var died: RunLogRow = add_child_autofree(RunLogRow.of_run({"corporation": "solace", "outcome": "died"}, "Solace", 1))
	assert_eq(died.sticker.shown_text(), tr("FLATLINED"))
	assert_eq(died.sticker.fill, VerbSticker.Fill.RED)


# --- Loadout (review section c: liner sheet, the D4 wheel) -----------------------------------------

func test_the_deck_sits_on_the_liner_and_the_spinner_tab_is_the_d4_wheel() -> void:
	RunManager.new_campaign(2)
	var op: OperativeState = RunManager.campaign.living_operatives()[0]
	var view := LoadoutView.new(op, RunManager.lookup())
	add_child_autofree(view)
	await _frames(3)
	var deck := view._view as DeckView
	assert_not_null(deck.liner, "the deck's stickers on the white liner")
	assert_eq(deck.liner.slots_host.get_child_count(), op.deck.size(), "a kiss-cut slot under each sticker")
	view.show_spinner()
	await _frames(3)
	var sp := view._view as SpinnerView
	assert_not_null(sp.d4, "the combat's own D4 wheel")
	assert_true(sp.d4 is WheelView)
	var r := sp.d4.wheel_rect().size.x * 0.5 - 22.0  # WheelView.wheel_rect: the disc's radius + 22 px
	assert_between(r * 1.5, 180.0, 260.0, "at combat size (about r = 220 at 1080p)")
	assert_eq(sp.d4.combatant.wheel.slot_slice_ids, op.slot_slice_ids, "the operative's own slices")
	assert_eq(sp.find_child("SliceRows", true, false).get_child_count(), op.slot_slice_ids.size(), "a glyph row per slice")
	RunManager.reset()


# --- Campaign end (Q8) ------------------------------------------------------------------------------

func test_the_end_shot_hands_back_the_network_points_headless() -> void:
	var got := []
	var shot := EndShot.new(func() -> Array: return [{"at": Vector2(10, 20), "home": true}], func() -> bool: return true)
	shot.taken.connect(func(img: Image, pts: Array) -> void: got.append([img, pts]))
	add_child_autofree(shot)
	await _frames(3)
	assert_eq(got.size(), 1, "one shot")
	assert_null(got[0][0], "headless: no frame to read")
	assert_eq((got[0][1] as Array).size(), 1, "the network's points")
