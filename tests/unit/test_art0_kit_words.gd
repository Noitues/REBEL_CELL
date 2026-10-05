extends GutTest
## ART-0 F (Salvage S5; ported from art-pass W2 bb4f2e2, W9F c77b99f / 9ad2133, WF fc477fc /
## b9af7e3; ART_BIBLE v1 §4.3, §5.3, §6.8, §12 kept by v2 §5.6): the kit's words and paper on
## main. A pad player never reads "click" or "drag" (UiTip.for_input, the pad variants, the
## FocusTip safety net); no label breaks a word (UiWrap.whole_words, no WORD_SMART left);
## FitScroll and ScrollHint survive pre-layout frames; the paper pieces keep their stock in
## high contrast with INK words and edges (PaperInk). M13's look tests are dropped (DECISIONS
## "Art direction — ART-0 kit behaviour (salvage S5, area F)").

const SCREEN := Rect2(0, 0, 1280, 720)
const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SLOT := "gut_art0_kit_words"
const LONG_TEXT := "A long wrapped paragraph that has no width yet, so for one frame it measures one word per line and thousands of pixels tall before the layout gives it room."

var _saved: Dictionary


func before_each() -> void:
	_saved = Settings.snapshot()
	Settings.set_text_scale(1.0)
	Settings.set_pad_active(false)
	Settings.high_contrast = false


func after_each() -> void:
	Motion.force_live = false
	Settings.restore(_saved)


func _frames(n: int = 1) -> void:
	for i in n:
		await get_tree().process_frame


func _holder() -> Control:
	var h: Control = add_child_autofree(Control.new())
	h.size = SCREEN.size
	UiTheme.apply(h)
	return h


func _files(dir: String) -> PackedStringArray:
	var out := PackedStringArray()
	var d := DirAccess.open(dir)
	if d == null:
		return out
	for f in d.get_files():
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for sub in d.get_directories():
		out.append_array(_files(dir.path_join(sub)))
	return out


func _all(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_all(c))
	return out


# --- §6.8 / §12 input-aware words ------------------------------------------------------------------

func test_pad_players_never_read_click_or_drag() -> void:
	Settings.set_pad_active(false)
	assert_eq(UiTip.for_input("Click to buy", "Press A to buy"), "Click to buy")
	Settings.set_pad_active(true)
	assert_eq(UiTip.for_input("Click to buy", "Press A to buy"), "Press A to buy")
	for pair in [["Click to buy", "Click to buy"], ["Drag a card", "Drag a card onto a wheel"], ["x", "Right-click to inspect"],
			["x", "DRAG IT"], ["x", "clicking and dragging"]]:
		var out := UiTip.for_input(pair[0], pair[1])
		assert_false(UiTip.has_mouse_words(out), "pad wording: '%s'" % out)
		for w in ["click", "drag"]:
			assert_false(out.to_lower().contains(w), "'%s' has no %s" % [out, w])
	assert_eq(UiTip.pad_safe("Drag it, then click."), "Move it, then press.", "the first letter's case kept")


## Game-code lines that say a mouse word in a player-facing string must pick the device's words:
## UiTip.for_input, a pad branch on the same statement, or a mouse-only table that for_input reads.
func test_mouse_words_in_player_strings_go_through_for_input() -> void:
	var mouse := RegEx.create_from_string("(?i)\\b(click|clicks|clicked|clicking|right-click|right click|left click|drag|drags|dragged|dragging|hover|hovering)\\b")
	var literal := RegEx.create_from_string("\"([^\"\\\\]|\\\\.)*\"")
	var allowed_tables := ["DRAG_TIPS := {", "DRAG_TIPS_MORE := {"]
	for p in _files("res://scripts"):
		if p.ends_with("ui_tip.gd") or p.ends_with("/settings.gd") or p.ends_with("audio_director.gd") or p.ends_with("ui_motion_data.gd"):
			continue
		var lines := FileAccess.get_file_as_string(p).split("\n")
		var in_table := false
		for i in lines.size():
			var line := lines[i]
			var code := line.split("#")[0] if not line.contains("\"") else line
			if line.strip_edges().begins_with("#"):
				continue
			for t in allowed_tables:
				if line.contains(t):
					in_table = true
			if in_table and line.contains("}"):
				in_table = false
				continue
			if in_table:
				continue
			for m in literal.search_all(code):
				var s := m.get_string()
				if not mouse.search(s):
					continue
				if code.contains("print(") or code.contains("play_sfx") or code.contains("stylebox") or code.contains("&\"hover\"") or s == "\"hover\"":
					continue
				var context := "\n".join(lines.slice(maxi(0, i - 2), i + 2))
				var ok := context.contains("for_input(") or context.contains("if pad") or context.contains("pad_active")
				assert_true(ok, "%s:%d: %s is mouse wording with no pad variant" % [p, i + 1, s.left(60)])


func test_every_drag_tip_has_a_pad_line_without_mouse_words() -> void:
	var scene: Script = load("res://scripts/ui/netrun_scene.gd")
	var consts := scene.get_script_constant_map()
	var pad: Dictionary = consts["DRAG_TIPS_PAD"]
	for table in ["DRAG_TIPS", "DRAG_TIPS_MORE"]:
		for kind in (consts[table] as Dictionary):
			assert_true(pad.has(kind), "%s has a pad line" % kind)
			assert_false(UiTip.has_mouse_words(String(pad.get(kind, ""))), "%s's pad line has no mouse words" % kind)


func test_focus_tip_never_shows_mouse_words_to_a_pad() -> void:
	Settings.set_pad_active(true)
	var b: Button = add_child_autofree(Button.new())
	b.text = "x"
	b.tooltip_text = "Drag it onto a slot, or click it."
	FocusTip.attach(b)
	await _frames(1)
	b.grab_focus()
	await _frames(2)
	var tip := FocusTip.tip_of(b)
	assert_not_null(tip, "the focus tip shows")
	if tip != null:
		assert_false(UiTip.has_mouse_words(tip.text), "pad words: '%s'" % tip.text)


## With a pad in use, no words shown or tipped on a page say "click", "drag" or "hover".
func _assert_pad_words(root: Node, where: String) -> void:
	for n in _all(root):
		if not (n is Control) or not (n as Control).is_visible_in_tree():
			continue
		var c := n as Control
		var words := String(c.get(&"text")) if (c is Label or c is Button) else ""
		for w in [words, c.tooltip_text]:
			if w == "":
				continue
			assert_false(UiTip.has_mouse_words(w), "%s: '%s' (%s) says a mouse word to a pad player" % [where, w.left(60), c.name])


func test_pad_pages_speak_pad_and_show_glyph_prompts() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	Settings.set_pad_active(true)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	await _frames(4)
	hq.new_campaign(1)
	await _frames(4)
	_assert_pad_words(hq, "hq")
	assert_true(hq.pad_prompts.visible and not hq.pad_prompts.glyphs().is_empty(), "hq: prompt bar with glyphs")
	hq.show_grid()
	await _frames(4)
	_assert_pad_words(hq, "grid")
	hq.queue_free()
	await _frames(2)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.start_run(1)
	await _frames(4)
	_assert_pad_words(scene, "route")
	assert_true(scene.pad_prompts.visible and not scene.pad_prompts.glyphs().is_empty(), "route: prompt bar")
	var s := RunManager.netrun
	s.run.cycles = 120
	s._open_shop()
	scene._show_current()
	await _frames(4)
	_assert_pad_words(scene, "mainframe")
	scene.open_remove()
	await _frames(3)
	var deck := scene.get_node("DeckView") as DeckView
	assert_true(PageTransition.modal_open(scene), "the deck viewer is a modal")
	_assert_pad_words(deck, "deck viewer")
	deck.close()
	await _frames(2)
	Dialogue.clear()
	Dialogue.dock_default()
	AudioDirector.muted = false
	get_tree().paused = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


# --- §4.3 rule 3: no mid-word breaks --------------------------------------------------------------

func test_no_mid_word_wrap_mode_left_in_game_code() -> void:
	for p in _files("res://scripts"):
		var src := FileAccess.get_file_as_string(p)
		assert_false(src.contains("AUTOWRAP_WORD_SMART"), "%s: WORD_SMART breaks a word that doesn't fit mid-word" % p)
		assert_false(src.contains("AUTOWRAP_ARBITRARY"), "%s: ARBITRARY breaks anywhere" % p)


func test_whole_words_keeps_a_label_as_wide_as_its_longest_word() -> void:
	var box: VBoxContainer = add_child_autofree(VBoxContainer.new())
	box.size = Vector2(40, 200)
	var l := Label.new()
	l.text = "a BREAKER b"
	UiWrap.whole_words(l)
	box.add_child(l)
	await _frames(3)
	assert_eq(l.autowrap_mode, TextServer.AUTOWRAP_WORD, "whole words")
	var need := UiWrap.longest_word_px("BREAKER", l.get_theme_font(&"font"), l.get_theme_font_size(&"font_size"))
	assert_true(l.custom_minimum_size.x >= need - 0.5, "never narrower than BREAKER (%.0f < %.0f)" % [l.custom_minimum_size.x, need])
	# A width the view sets later is kept when wider.
	l.custom_minimum_size.x = 300.0
	l.add_theme_font_size_override(&"font_size", 20)
	await _frames(3)
	assert_eq(l.custom_minimum_size.x, 300.0, "the view's own width stays")


func test_crew_card_class_tag_never_breaks_mid_word_at_the_ceiling() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var box: HBoxContainer = add_child_autofree(HBoxContainer.new())
	var card := CrewCard.new("BREAKER 1", "Breaker", 0, 50, 50, "", 0.0)
	box.add_child(card)
	await _frames(4)
	var tag: Label = null
	for l in card.find_children("*", "Label", true, false):
		if (l as Label).text.contains("BREAKER") and (l as Label).text.contains("//"):
			tag = l as Label
	assert_not_null(tag, "the class tags")
	if tag != null:
		assert_eq(tag.autowrap_mode, TextServer.AUTOWRAP_WORD)
		assert_true(tag.size.x + 0.5 >= UiWrap.longest_word_px("BREAKER", tag.get_theme_font(&"font"), tag.get_theme_font_size(&"font_size")), "BREAKER fits whole")


# --- §5.3 FitScroll / ScrollHint pre-layout frames ----------------------------------------------

## A wrapped label at width 0 inside a FitScroll (one word per line, thousands of px tall for
## a frame) never crashes or errors, and the view settles to the laid-out content.
func test_fit_scroll_survives_a_zero_width_wrapped_label() -> void:
	var h := _holder()
	var box := VBoxContainer.new()
	for i in 12:
		var l := Label.new()
		l.autowrap_mode = TextServer.AUTOWRAP_WORD
		l.text = LONG_TEXT
		box.add_child(l)
	var fit := FitScroll.new(box, 400.0)
	var panel := PanelContainer.new()
	panel.add_child(fit)
	h.add_child(panel)
	await _frames(3)
	assert_true(fit.scroll.custom_minimum_size.y <= FitScroll.MAX_VIEW_PX + 0.5, "the view never takes a degenerate height")
	panel.size = Vector2(600, 500)
	panel.position = Vector2.ZERO
	await _frames(6)
	assert_true(fit.scroll.custom_minimum_size.y <= 400.0 + 0.5, "the view keeps to its cap")
	assert_true(fit.overflowing(), "the laid-out text still overflows the cap")
	assert_true(fit.hint.room.custom_minimum_size.y < 200.0, "the hint's room stays tag-sized")
	# A rebuild at width 0 again (a page rebuilt before layout): still no runaway.
	for c in box.get_children():
		(c as Label).text = LONG_TEXT + " " + LONG_TEXT
	fit.max_height = 0.0
	await _frames(4)
	assert_true(fit.scroll.custom_minimum_size.y <= FitScroll.MAX_VIEW_PX + 0.5, "uncapped, the view is still bounded")


## A FitScroll in a centring container never gets a width from its parent: its wrapped text
## measures ~31000 px for as long as that lasts. Uncapped, the view waits the measure out and
## never passes MAX_VIEW_PX.
func test_an_uncapped_fit_scroll_never_takes_a_pre_layout_height() -> void:
	var h := _holder()
	var cc := CenterContainer.new()
	cc.size = SCREEN.size
	h.add_child(cc)
	var box := VBoxContainer.new()
	for i in 12:
		var l := Label.new()
		l.autowrap_mode = TextServer.AUTOWRAP_WORD
		l.text = LONG_TEXT
		box.add_child(l)
	var fit := FitScroll.new(box, 0.0)
	var panel := PanelContainer.new()
	panel.add_child(fit)
	cc.add_child(panel)
	var tallest := 0.0
	for f in FitScroll.DEGENERATE_FRAMES + 3:
		await _frames(1)
		tallest = maxf(tallest, panel.size.y)
		assert_true(fit.degenerate(fit.content_height()), "the content still measures pre-layout")
	assert_true(tallest <= FitScroll.MAX_VIEW_PX + 64.0, "the panel never takes the pre-layout height (%s)" % tallest)
	assert_true(fit.hint.room.custom_minimum_size.y < 100.0, "the hint's room stays tag-sized")
	# Given a width, the real height comes through.
	for c in box.get_children():
		(c as Label).custom_minimum_size.x = 300
	await _frames(3)
	assert_false(fit.degenerate(fit.content_height()))
	assert_almost_eq(fit.scroll.custom_minimum_size.y, ceilf(fit.content_height()), 1.0, "the view is the laid-out content")


func test_scroll_hint_says_nothing_about_a_degenerate_view() -> void:
	var h := _holder()
	var box := VBoxContainer.new()
	h.add_child(box)
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(200, 200)
	box.add_child(scroll)
	var list := VBoxContainer.new()
	for i in 40:
		var l := Label.new()
		l.text = "row %d" % i
		list.add_child(l)
	scroll.add_child(list)
	var hint := ScrollHint.new(scroll)
	box.add_child(hint)
	await _frames(3)
	assert_false(hint.degenerate_view(), "a laid-out view")
	assert_true(hint.visible, "more below")
	scroll.custom_minimum_size.y = ScrollHint.DEGENERATE_PX * Settings.text_scale + 100.0
	await _frames(2)
	assert_true(hint.degenerate_view(), "a pre-layout height")
	hint.refresh()
	assert_false(hint.visible, "says nothing about what is below")


# --- §3.3 / §12 paper inks and high contrast on paper -------------------------------------------

func test_paper_inks_meet_4_5_to_1_on_every_paper_stock() -> void:
	for ink in [Palette.HARM_INK, Palette.GAIN_INK]:
		for stock in Palette.PAPER_STOCKS:
			assert_gte(Palette.contrast(ink, stock), 4.5, "%s on %s" % [ink.to_html(false), stock.to_html(false)])
	assert_lt(Palette.contrast(Palette.HARM, Palette.PAPER), 4.5)
	assert_lt(Palette.contrast(Palette.GAIN, Palette.PAPER), 4.5)
	assert_ne(Palette.HARM_INK, Palette.GAIN_INK)


func _paper_pieces() -> Dictionary:
	var h := _holder()
	var photo := Polaroid.new("RANK 3", "[BREAKER PORTRAIT]")
	photo.size = Vector2(110, 134)
	h.add_child(photo)
	var toast := Toast.new()
	h.add_child(toast)
	toast.show_note("Respin landed on BLOCK.", Vector2(400, 400))
	var card := CrewCard.new("ACE", "Breaker", 1, 30, 50, "Stationed nowhere.", 0.0)
	h.add_child(card)
	return {"photo": photo, "toast": toast, "card": card}


func test_paper_pieces_in_high_contrast_keep_their_paper_with_ink_words_and_edges() -> void:
	Settings.high_contrast = true
	var p := _paper_pieces()
	await _frames(2)
	# ART-2 2D: the toast is a terminal strip now (§4.13): bright words on dark glass, its edge opaque.
	var toast: Toast = p["toast"]
	assert_gte(Palette.contrast(toast.label.get_theme_color(&"font_color"), Color(HudSkin.TERMINAL_BG, 1.0)), PaperInk.MIN_CONTRAST, "the toast's words")
	assert_eq(toast.edge_color().a, 1.0, "the toast's edge is opaque")
	assert_gte(toast.edge_width(), PaperInk.EDGE_PX, "and %s px" % PaperInk.EDGE_PX)
	assert_gte(Palette.contrast((p["photo"] as Polaroid).caption_ink(), Palette.PAPER), PaperInk.MIN_CONTRAST, "the caption")
	var card: CrewCard = p["card"]
	for l in card.find_children("*", "Label", true, false):
		var col := (l as Label).get_theme_color(&"font_color")
		assert_gte(Palette.contrast(col, Palette.NOTE_PAPER), PaperInk.MIN_CONTRAST, "dossier '%s' at 7:1" % (l as Label).text)
	for key in ["photo", "card"]:
		var piece: Object = p[key]
		var ec: Color = piece.call(&"edge_color")
		assert_eq(ec, Palette.INK, "%s edge is opaque INK" % key)
		assert_gte(float(piece.call(&"edge_width")), PaperInk.EDGE_PX, "%s edge is %s px" % [key, PaperInk.EDGE_PX])
	assert_eq(PaperInk.opaque(Palette.NOTE_TAPE).a, 1.0, "tape is opaque")
	Settings.high_contrast = false


func test_out_of_high_contrast_the_paper_pieces_look_as_before() -> void:
	var p := _paper_pieces()
	await _frames(1)
	assert_eq((p["photo"] as Polaroid).edge_color(), Color(Palette.INK, Polaroid.EDGE_ALPHA), "the Polaroid's soft edge")
	assert_eq((p["card"] as CrewCard).edge_color(), Color(Palette.INK, CrewCard.EDGE_ALPHA), "the dossier's soft edge")
	assert_eq((p["toast"] as Toast).edge_width(), Toast.EDGE_PX, "the toast's own edge")
	for key in ["photo", "card"]:
		assert_almost_eq(float((p[key] as Object).call(&"edge_width")), 1.0, 0.01)
	assert_eq(PaperInk.text(Palette.HARM_INK), Palette.HARM_INK)
	assert_eq(PaperInk.opaque(Palette.NOTE_TAPE), Palette.NOTE_TAPE)
