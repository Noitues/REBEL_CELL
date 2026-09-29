extends GutTest
## Art pass WF (kit follow-ups): FitScroll / ScrollHint survive degenerate frames; TilePicker
## wraps long names at word boundaries; StickerButton caps its growth; the Polaroid caption
## always fits; CombatFxLayer.stamp takes an icon; paper-ink HARM/GAIN meet 4.5:1 on paper;
## high contrast on the custom-drawn paper pieces; the Deck's city quality default; tracking
## in px per type step.

const SCREEN := Rect2(0, 0, 1280, 720)
const LONG_TEXT := "A long wrapped paragraph that has no width yet, so for one frame it measures one word per line and thousands of pixels tall before the layout gives it room."


func before_each() -> void:
	Settings.set_text_scale(1.0)
	Settings.high_contrast = false


func after_each() -> void:
	Settings.set_text_scale(1.0)
	Settings.high_contrast = false
	Motion.force_live = false


func _holder() -> Control:
	var h: Control = add_child_autofree(Control.new())
	h.size = SCREEN.size
	UiTheme.apply(h)
	return h


# --- 1. FitScroll / ScrollHint degenerate frames ------------------------------------------

## A wrapped label at width 0 inside a FitScroll (one word per line, thousands of px tall for
## a frame) never crashes or errors, and the view settles to the laid-out content.
func test_fit_scroll_survives_a_zero_width_wrapped_label() -> void:
	var h := _holder()
	var box := VBoxContainer.new()
	for i in 12:
		var l := Label.new()
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.text = LONG_TEXT
		box.add_child(l)
	var fit := FitScroll.new(box, 400.0)
	var panel := PanelContainer.new()
	panel.add_child(fit)
	h.add_child(panel)
	await wait_frames(3)
	assert_true(fit.scroll.custom_minimum_size.y <= FitScroll.MAX_VIEW_PX + 0.5, "the view never takes a degenerate height")
	panel.size = Vector2(600, 500)
	panel.position = Vector2.ZERO
	await wait_frames(6)
	assert_true(fit.scroll.custom_minimum_size.y <= 400.0 + 0.5, "the view keeps to its cap")
	assert_true(fit.overflowing(), "the laid-out text still overflows the cap")
	assert_true(fit.hint.room.custom_minimum_size.y < 200.0, "the hint's room stays tag-sized")
	# A rebuild at width 0 again (a page rebuilt before layout): still no runaway.
	for c in box.get_children():
		(c as Label).text = LONG_TEXT + " " + LONG_TEXT
	fit.max_height = 0.0
	await wait_frames(4)
	assert_true(fit.scroll.custom_minimum_size.y <= FitScroll.MAX_VIEW_PX + 0.5, "uncapped, the view is still bounded")


## A FitScroll in a centring container never gets a width from its parent: its wrapped text
## measures ~31000 px for as long as that lasts. Uncapped, the view (and the panel round it)
## used to take all of it; now it waits the measure out and never passes MAX_VIEW_PX.
func test_an_uncapped_fit_scroll_never_takes_a_pre_layout_height() -> void:
	var h := _holder()
	var cc := CenterContainer.new()
	cc.size = SCREEN.size
	h.add_child(cc)
	var box := VBoxContainer.new()
	for i in 12:
		var l := Label.new()
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.text = LONG_TEXT
		box.add_child(l)
	var fit := FitScroll.new(box, 0.0)
	var panel := PanelContainer.new()
	panel.add_child(fit)
	cc.add_child(panel)
	var tallest := 0.0
	for f in FitScroll.DEGENERATE_FRAMES + 3:
		await wait_frames(1)
		tallest = maxf(tallest, panel.size.y)
		assert_true(fit.degenerate(fit.content_height()), "the content still measures pre-layout")
	assert_true(tallest <= FitScroll.MAX_VIEW_PX + 64.0, "the panel never takes the pre-layout height (%s)" % tallest)
	assert_true(fit.hint.room.custom_minimum_size.y < 100.0, "the hint's room stays tag-sized")
	# Given a width, the real height comes through.
	for c in box.get_children():
		(c as Label).custom_minimum_size.x = 300
	await wait_frames(3)
	assert_false(fit.degenerate(fit.content_height()))
	assert_almost_eq(fit.scroll.custom_minimum_size.y, ceilf(fit.content_height()), 1.0, "the view is the laid-out content")


# --- 2. TilePicker long names (§4.3 rule 3) ------------------------------------------------

## Every corporation, class and home-server name in the content (display names).
func _content_names() -> Array[String]:
	var out: Array[String] = []
	for dir in ["res://content/corporations", "res://content/classes", "res://content/nodes"]:
		for file in DirAccess.get_files_at(dir):
			if not file.ends_with(".tres") or (dir.ends_with("nodes") and not file.begins_with("home_")):
				continue
			var res := load(dir + "/" + file)
			if res is CorporationData or res is ClassData or res is HomeServerVariantData:
				out.append(String(res.get(&"display_name")))
	return out


func test_tile_names_wrap_at_words_and_fit_at_every_scale() -> void:
	var names := _content_names()
	assert_gt(names.size(), 15, "corporations, classes and home servers")
	var longest := ""
	for n in names:
		if n.length() > longest.length():
			longest = n
	var f := Palette.mono()
	for scale: float in [1.0, 1.6, 2.0]:
		Settings.set_text_scale(scale)
		var h := _holder()
		var tiles: Array[Dictionary] = []
		for i in names.size():
			tiles.append({"name": names[i], "meta": "T%d" % (i % 3), "icon": StatIcon.HOME, "locked": i % 4 == 3, "unlock": "Win a campaign"})
		var tp := TilePicker.new(tiles, 3)
		h.add_child(tp)
		for i in tiles.size():
			var nl := tp.name_layout(i)
			var lines: PackedStringArray = nl["lines"]
			var words := " ".join(names[i].split(" ", false))
			assert_eq(" ".join(lines), words, "%s at %s: whole words only, none dropped" % [names[i], scale])
			assert_true(int(nl["px"]) >= UiTheme.font_px(UiTheme.CAPTION), "%s never under caption" % names[i])
			var r := tp.tile_rect(i)
			var w: float = tp.name_width(r.size.x) - (TilePicker.ICON_R * scale * TilePicker.LOCK_SHARE * 2.0 if tp.is_locked(i) else 0.0)
			assert_true(TilePicker.widest(lines, f, int(nl["px"])) <= w + 0.5, "%s at %s: every line inside the tile" % [names[i], scale])
			var ml := tp.meta_layout(i)
			var name_h := lines.size() * float(nl["line_h"])
			var meta_h := (ml["lines"] as PackedStringArray).size() * float(ml["line_h"])
			assert_true(TilePicker.PAD * 2.0 + name_h + meta_h <= r.size.y + 0.5, "%s at %s: name and meta stacked inside the tile" % [names[i], scale])
		var ll := tp.name_layout(names.find(longest))
		assert_true((ll["lines"] as PackedStringArray).size() >= 2, "the longest name (%s) wraps rather than cuts" % longest)
		h.free()
	Settings.set_text_scale(1.0)


func test_wrap_words_never_breaks_a_word() -> void:
	var f := Palette.mono()
	var lines := TilePicker.wrap_words("Solace Root Certificate Store", f, 18, 10.0)
	assert_eq(lines, PackedStringArray(["Solace", "Root", "Certificate", "Store"]), "a word too wide sits alone, whole")


# --- 3. StickerButton growth cap -------------------------------------------------------------

func _sticker(h: Control, words: String, icon: String) -> StickerButton:
	var b := StickerButton.new(words, Palette.STICKER_PINK, 3.0)
	b.pre_translated = true
	b.drawn_icon = icon
	b.container_width = SCREEN.size.x
	b.max_share = StickerButton.MAX_SHARE
	h.add_child(b)
	b.refit()
	return b


func test_a_sticker_yields_its_type_step_before_passing_its_share() -> void:
	for scale: float in [1.0, 1.6, 2.0]:
		Settings.set_text_scale(scale)
		var h := _holder()
		for words in ["RESPIN 2 RAM R", "RESPIN 2 RAM RS", "UNDO Z", "RESPIN"]:
			var b := _sticker(h, words, "respin")
			var cap := SCREEN.size.x * StickerButton.MAX_SHARE
			assert_true(b.size.x <= cap + 0.5 or b.lettering_px() == UiTheme.font_px_at(UiTheme.CAPTION, 1.0),
				"%s at %s: %s px wide, within %s of the page" % [words, scale, b.size.x, StickerButton.MAX_SHARE])
			assert_true(b.lettering_px() >= UiTheme.CAPTION, "%s at %s: never under caption" % [words, scale])
			if b.width_at(StickerButton.font_px(), scale) <= cap:
				assert_eq(b.lettering_px(), StickerButton.font_px(), "%s at %s: grows with the text while it fits" % [words, scale])
			# The words sit on the paper, clear of the icon (they never overrun).
			var lr := b.lettering_rect()
			assert_true(lr.position.x >= StickerButton.ICON_ROOM * b.sticker_scale() - 0.5, "%s at %s: clear of the icon" % [words, scale])
			assert_true(lr.end.x <= b.size.x + 0.5 and lr.position.y >= -0.5 and lr.end.y <= b.size.y + 0.5, "%s at %s: the words on the paper" % [words, scale])
		h.free()
	Settings.set_text_scale(1.0)


func test_without_a_cap_a_sticker_grows_as_before() -> void:
	Settings.set_text_scale(2.0)
	var h := _holder()
	var b := StickerButton.new("RESPIN 2 RAM R")
	b.drawn_icon = "respin"
	h.add_child(b)
	b.refit()
	assert_eq(b.lettering_px(), StickerButton.font_px(), "opt-in: no max_share, full growth")
	Settings.set_text_scale(1.0)


func test_respin_at_2_is_capped_and_1_0_is_unchanged() -> void:
	var h := _holder()
	var b := _sticker(h, "RESPIN 2 RAM R", "respin")
	assert_eq(b.lettering_px(), StickerButton.FONT_SIZE, "1.0 draws as before")
	assert_almost_eq(b.size.y, StickerButton.HEIGHT, 0.01)
	h.free()
	Settings.set_text_scale(2.0)
	h = _holder()
	b = _sticker(h, "RESPIN 2 RAM R", "respin")
	var grown := b.width_at(StickerButton.font_px(), 2.0)
	assert_lt(b.size.x, grown, "at 2.0 it no longer grows to %s px" % grown)
	assert_lt(b.lettering_px(), StickerButton.font_px(), "the lettering yielded")
	Settings.set_text_scale(1.0)


# --- 4. Polaroid caption fits at every scale ------------------------------------------------

func test_the_polaroid_caption_always_fits_whole() -> void:
	var captions: Array[String] = ["RANK 3", "RANK 12", "Mara Voss-Okonkwo", "Jin"]
	for c in DirAccess.get_files_at("res://content/classes"):
		if c.ends_with(".tres"):
			var cls := load("res://content/classes/" + c) as ClassData
			captions.append(String(cls.display_name))
			captions.append(String(cls.display_name).to_upper())
	# Combat's Polaroid, the crew card's (full and compact) and the case file's mini one.
	var frames: Array[Vector2] = [Vector2(110, 134), CrewCard.POLAROID_SIZE, CrewCard.POLAROID_SIZE * CrewCard.COMPACT_POLAROID]
	for scale: float in [1.0, 1.6, 2.0]:
		Settings.set_text_scale(scale)
		var sizes := frames.duplicate()
		sizes.append(CaseFileCard.POLAROID * scale)
		for sz: Vector2 in sizes:
			for cap in captions:
				var p := Polaroid.new(cap)
				p.size = sz
				var cl := p.caption_layout()
				var room := p.caption_room()
				var drawn: Vector2 = cl["size"]
				var k: Vector2 = cl["scale"]
				var what := "'%s' in %s at %s" % [cap, sz, scale]
				assert_true(drawn.x <= room.x + 0.5, "%s: the whole caption across (%s of %s)" % [what, drawn.x, room.x])
				assert_true(drawn.y <= room.y + 0.5, "%s: the whole caption in the band (%s of %s)" % [what, drawn.y, room.y])
				assert_true(int(cl["px"]) * k.y >= UiTheme.CAPTION - 0.01, "%s: never under caption at 1.0" % what)
				assert_true(k.x >= k.y * Polaroid.CONDENSE_MIN - 0.001, "%s: condensed no further than %s" % [what, Polaroid.CONDENSE_MIN])
				var words := String(cl["text"])
				assert_true(words.length() >= 1, "%s: never empty" % what)
				p.free()
	Settings.set_text_scale(1.0)


func test_a_polaroid_caption_abbreviates_by_w5s_rule() -> void:
	assert_eq(Polaroid.short_caption("RANK 12"), tr("R%d") % 12, "the rank as W5's compact R n")
	assert_eq(Polaroid.short_caption("Mara Voss-Okonkwo"), "Mara V.")
	assert_eq(Polaroid.short_caption("BREAKER"), "BREAKER", "one word stays whole (condensed, never clipped)")
	Settings.set_text_scale(2.0)
	var p := Polaroid.new("BREAKER")
	p.size = Vector2(110, 134)
	var cl := p.caption_layout()
	assert_eq(String(cl["text"]), "BREAKER", "combat's 2.0 caption keeps every letter (was BREAKE)")
	p.free()
	p = Polaroid.new("RANK 12")
	p.size = CrewCard.POLAROID_SIZE * CrewCard.COMPACT_POLAROID
	assert_eq(String(p.caption_layout()["text"]), tr("R%d") % 12)
	p.free()
	Settings.set_text_scale(1.0)


# --- 5. CombatFxLayer.stamp with an icon ------------------------------------------------------

func _fx_layer() -> CombatFxLayer:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var layer := CombatFxLayer.new()
	holder.add_child(layer)
	return layer


func test_a_status_stamp_carries_its_stat_icon() -> void:
	Motion.force_live = true
	var layer := _fx_layer()
	layer.stamp(Vector2(200, 200), "", Palette.HARM, 0.5, 0.0, StatIcon.for_status(RC.Status.CORRUPTED))
	var s: Array = layer.sprites.filter(func(x: Dictionary) -> bool: return String(x["kind"]) == "stamp")
	assert_eq(s.size(), 1, "one stamp")
	assert_eq(s[0]["icon"], StatIcon.CORRUPTED, "the status's StatIcon rides the stamp")
	# The old five-argument call still works (no icon: the bare disc or a glyph).
	layer.stamp(Vector2(300, 200), "", Palette.GAIN, 0.5, 0.1)
	s = layer.sprites.filter(func(x: Dictionary) -> bool: return String(x["kind"]) == "stamp")
	assert_eq(s.size(), 2)
	assert_eq(s[1]["icon"], &"", "no icon by default")
	# Both draw (a frame past their delay) without an error.
	await wait_frames(3)
	layer.queue_redraw()
	await wait_frames(1)
	assert_true(StatIcon.ALL.has(StatIcon.for_status(RC.Status.CORRUPTED)), "a drawn kit icon")
	Motion.force_live = false


# --- 6. Paper-ink semantic tokens (§3.3, §3.7) ----------------------------------------------

func test_paper_inks_meet_4_5_to_1_on_every_paper_stock() -> void:
	for ink in [Palette.HARM_INK, Palette.GAIN_INK]:
		for stock in Palette.PAPER_STOCKS:
			assert_gte(Palette.contrast(ink, stock), 4.5, "%s on %s" % [ink.to_html(false), stock.to_html(false)])
	# The screen hues don't (that is why the inks exist), and the inks keep their hue.
	assert_lt(Palette.contrast(Palette.HARM, Palette.PAPER), 4.5)
	assert_lt(Palette.contrast(Palette.GAIN, Palette.PAPER), 4.5)
	assert_almost_eq(Palette.HARM_INK.h, Palette.HARM.h, 0.02, "HARM_INK is HARM's hue")
	assert_almost_eq(Palette.GAIN_INK.h, Palette.GAIN.h, 0.02, "GAIN_INK is GAIN's hue")
	assert_ne(Palette.HARM_INK, Palette.GAIN_INK)


func test_paper_pieces_use_the_paper_inks() -> void:
	var lost := CaseFileCard.new("2", {"corporation": "solace", "heat": 80, "runs": 3, "ice": 2, "saved_at": 0.0, "state": "lost"})
	add_child_autofree(lost)
	var st := lost.find_child("State", true, false) as Label
	assert_eq(st.get_theme_color(&"font_color"), Palette.HARM_INK, "LOST on the folder is HARM ink")
	assert_gte(Palette.contrast(st.get_theme_color(&"font_color"), Palette.PAPER), 4.5)


# --- 7. High contrast on the custom-drawn paper pieces (§12) -----------------------------------

func _paper_pieces() -> Dictionary:
	var h := _holder()
	var folder := CaseFileCard.new("1", {"corporation": "solace", "heat": 62, "runs": 4, "ice": 3, "saved_at": 0.0, "state": "lost"})
	h.add_child(folder)
	var slip := RunReceipt.of_run({"tier": 2, "site": "Patient Records Vault", "outcome": "cleared", "cycles": 34, "banked": 12}, "Solace Biosystems", 0)
	h.add_child(slip)
	var photo := Polaroid.new("RANK 3", "[PHANTOM PORTRAIT]")
	photo.size = Vector2(110, 134)
	h.add_child(photo)
	var toast := Toast.new()
	h.add_child(toast)
	toast.show_note("Respin landed on BLOCK.", Vector2(400, 400))
	var earned := AchievementBadge.new(&"first_blood", "First Blood", "Finish a run.", true)
	var locked := AchievementBadge.new(&"wall", "The Wall", "Hold a raid.", false)
	h.add_child(earned)
	h.add_child(locked)
	return {"folder": folder, "slip": slip, "photo": photo, "toast": toast, "earned": earned, "locked": locked}


func _labels_under(n: Node) -> Array[Label]:
	var out: Array[Label] = []
	for c in n.find_children("*", "Label", true, false):
		out.append(c as Label)
	return out


func test_paper_pieces_in_high_contrast_keep_their_paper_with_ink_words_and_edges() -> void:
	Settings.high_contrast = true
	var p := _paper_pieces()
	await wait_frames(2)
	# Words on paper: INK, 7:1 on every stock.
	for key in ["folder", "slip"]:
		for l in _labels_under(p[key]):
			if l.get_parent() is StatField:
				continue
			var col := l.get_theme_color(&"font_color")
			assert_gte(Palette.contrast(col, Palette.PAPER), PaperInk.MIN_CONTRAST, "%s '%s' at 7:1" % [key, l.text])
	var toast: Toast = p["toast"]
	assert_gte(Palette.contrast(toast.label.get_theme_color(&"font_color"), Palette.NOTE_YELLOW), PaperInk.MIN_CONTRAST, "the toast's words")
	assert_gte(Palette.contrast((p["photo"] as Polaroid).caption_ink(), Palette.PAPER), PaperInk.MIN_CONTRAST, "the caption")
	# Edges: opaque INK, 2 px.
	for key in ["folder", "slip", "photo", "toast"]:
		var piece: Object = p[key]
		var ec: Color = piece.call(&"edge_color")
		assert_eq(ec, Palette.INK, "%s edge is opaque INK" % key)
		assert_gte(float(piece.call(&"edge_width")), PaperInk.EDGE_PX, "%s edge is %s px" % [key, PaperInk.EDGE_PX])
	# Nothing translucent on the paper.
	assert_eq(PaperInk.opaque(Palette.NOTE_TAPE).a, 1.0, "tape is opaque")
	# Badges sit on the glass: their name and unearned outline at 7:1 on high contrast's black.
	var locked: AchievementBadge = p["locked"]
	assert_gte(Palette.contrast(AchievementBadge.outline_color(), HighContrast.BG), PaperInk.MIN_CONTRAST, "the unearned outline")
	for l in _labels_under(locked):
		assert_gte(Palette.contrast(l.get_theme_color(&"font_color"), HighContrast.BG), PaperInk.MIN_CONTRAST, "badge name")
	Settings.high_contrast = false


func test_out_of_high_contrast_the_paper_pieces_look_as_before() -> void:
	var p := _paper_pieces()
	await wait_frames(1)
	for key in ["folder", "slip", "photo", "toast"]:
		var piece: Object = p[key]
		var ec: Color = piece.call(&"edge_color")
		assert_lt(ec.a, 1.0, "%s keeps its soft ink edge" % key)
		assert_almost_eq(float(piece.call(&"edge_width")), 1.0, 0.01)
	assert_eq(AchievementBadge.outline_color(), Palette.DISABLED)
	assert_eq(PaperInk.text(Palette.HARM_INK), Palette.HARM_INK)
