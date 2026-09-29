extends GutTest
## Art pass W2 (ART_BIBLE §6, §6.4-§6.8, §7.4, §12): the component kit. Every component
## has the six states; disabled labels keep 4.5:1; the focus brackets draw outside and never
## change a minimum size; the focus scale never reflows; the one toast keeps off bottom
## controls; stamps hold for their reading time; every pad glyph set has every button;
## pad wording never says click or drag; the redrawn status icons exist.

const SCREEN := Rect2(0, 0, 1280, 720)


func before_each() -> void:
	Settings.set_text_scale(1.0)
	Settings.set_pad_active(false)
	Motion.force_live = false


func after_each() -> void:
	Settings.set_text_scale(1.0)
	Settings.set_pad_active(false)
	Motion.force_live = false


func _holder() -> Control:
	var h: Control = add_child_autofree(Control.new())
	h.size = SCREEN.size
	UiTheme.apply(h)
	return h


## Every kit component, fresh.
func _components() -> Array[Control]:
	var tiles: Array[Dictionary] = [{"name": "Solace", "meta": "T1", "icon": StatIcon.HOME},
		{"name": "Meridian", "meta": "T2", "icon": StatIcon.SHOP, "locked": true, "unlock": "Win a campaign"}]
	var out: Array[Control] = [ZineToggle.new("Subtitles", true), ZineSlider.new(0.8, 2.0, 0.1, 1.6), Stepper.new(0, 5, 1, 2),
		TilePicker.new(tiles), ZineStamp.new("JACK IN"), StickerButton.new("RESPIN")]
	return out


# --- §6 the six states -------------------------------------------------------------------------

func test_every_component_exposes_all_six_states() -> void:
	var h := _holder()
	assert_eq(KitState.ALL, [KitState.IDLE, KitState.HOVER, KitState.FOCUS, KitState.PRESSED, KitState.DISABLED, KitState.REFUSED])
	for c in _components():
		h.add_child(c)
		assert_true(c.has_method(&"state"), "%s reports its state" % c.get_class())
		assert_eq(c.call(&"state"), KitState.IDLE, "%s idles" % c.get_script().get_global_name())
		for st in KitState.ALL:
			KitState.force(c, st)
			assert_eq(c.call(&"state"), st, "%s shows %s" % [c.get_script().get_global_name(), st])
		KitState.clear_force(c)


func test_live_states_follow_the_control() -> void:
	var h := _holder()
	var t := ZineToggle.new("Subtitles")
	h.add_child(t)
	t.disabled = true
	assert_eq(t.state(), KitState.DISABLED)
	t.refuse()
	assert_eq(t.state(), KitState.REFUSED, "a refusal shows over disabled")
	var s := Stepper.new(0, 2, 1, 2)
	h.add_child(s)
	watch_signals(s)
	s.nudge(1)
	assert_signal_emitted(s, "refused", "a step past the end is refused")
	assert_eq(s.state(), KitState.REFUSED)
	assert_eq(s.value, 2.0)
	s.nudge(-1)
	assert_eq(s.value, 1.0)
	s.grab_focus()
	await wait_frames(1)
	KitState.clear_force(s)
	s.remove_meta(KitState.META_REFUSED)
	assert_eq(s.state(), KitState.FOCUS)


func test_every_button_variant_has_every_state_box() -> void:
	var th := UiTheme.build(1.0)
	for kind in [&"Button"] + UiTheme.BUTTON_VARIANTS:
		for key in [&"normal", &"hover", &"pressed", &"disabled", &"focus"]:
			assert_true(th.has_stylebox(key, kind), "%s has %s" % [kind, key])
		assert_true(th.get_stylebox(&"focus", kind) is StyleBoxBrackets, "%s focus is the brackets" % kind)
		assert_true(th.get_stylebox(&"disabled", kind) is StyleBoxLocked, "%s disabled has the lock" % kind)
	assert_eq(th.get_type_variation_base(UiTheme.PRIMARY), &"Button", "HotButton is the Primary")
	assert_eq((th.get_stylebox(&"normal", UiTheme.PRIMARY) as StyleBoxFlat).bg_color, Palette.CELL_PINK)
	assert_eq((th.get_stylebox(&"normal", UiTheme.DANGER) as StyleBoxFlat).border_color, Palette.HARM)
	assert_eq(th.get_color(&"font_color", UiTheme.SECONDARY), Palette.TEXT_HI)


func test_hover_lifts_2_and_pressed_drops_1_without_resizing() -> void:
	var th := UiTheme.build(1.0)
	for kind in [&"Button", UiTheme.PRIMARY, UiTheme.DANGER]:
		var n := th.get_stylebox(&"normal", kind) as StyleBoxFlat
		var hv := th.get_stylebox(&"hover", kind) as StyleBoxFlat
		var pr := th.get_stylebox(&"pressed", kind) as StyleBoxFlat
		assert_eq(hv.expand_margin_top - n.expand_margin_top, float(UiTheme.HOVER_LIFT), "%s hover lifts" % kind)
		assert_eq(pr.expand_margin_bottom - n.expand_margin_bottom, float(UiTheme.PRESS_DROP), "%s pressed drops" % kind)
		assert_eq(hv.get_minimum_size(), n.get_minimum_size(), "%s hover keeps the size" % kind)
		assert_eq(pr.get_minimum_size(), n.get_minimum_size(), "%s pressed keeps the size" % kind)
		assert_gt(hv.shadow_size, n.shadow_size, "hover glows more")
		assert_lt(pr.shadow_size, n.shadow_size, "pressed glows less")


func test_a_standalone_button_is_its_label_plus_32() -> void:
	var th := UiTheme.build(1.0)
	for kind in [UiTheme.PRIMARY, UiTheme.SECONDARY, UiTheme.DANGER]:
		var n := th.get_stylebox(&"normal", kind)
		assert_eq(n.get_margin(SIDE_LEFT) + n.get_margin(SIDE_RIGHT), 32.0, "%s: label + 32 px" % kind)


func test_menu_item_uses_a_type_step() -> void:
	for s in [1.0, 1.6, 2.0]:
		assert_eq(UiTheme.build(s).get_font_size(&"font_size", &"MenuItem"), UiTheme.font_px_at(UiTheme.BODY, s))


# --- §3.7 disabled contrast ----------------------------------------------------------------------

func test_disabled_labels_keep_4_5_to_1() -> void:
	var th := UiTheme.build(1.0)
	for kind in [&"Button"] + UiTheme.BUTTON_VARIANTS + [&"MenuItem"]:
		var label := th.get_color(&"font_disabled_color", kind)
		var bg := Palette.over(Palette.NIGHT_SKY, (th.get_stylebox(&"disabled", kind) as StyleBoxLocked).fill)
		assert_gte(Palette.contrast(label, bg), 4.5, "%s disabled label on its box" % kind)
		assert_ne(label, Color(Palette.CELL_PINK, 0.5), "never a faded active colour")
	assert_gte(Palette.contrast(KitState.label_color(KitState.DISABLED), Palette.over(Palette.NIGHT_SKY, Palette.TERMINAL_BG)), 4.5)
	assert_gte(Palette.contrast(Palette.DISABLED, Palette.over(Palette.NIGHT_SKY, Palette.TERMINAL_BG)), 3.0, "the outline reads at 3:1")


# --- §6 focus: brackets and the 1.03 scale -------------------------------------------------------

func test_focus_brackets_draw_outside_and_never_change_min_size() -> void:
	var h := _holder()
	var b := Button.new()
	b.text = "CONTINUE"
	h.add_child(b)
	await wait_frames(1)
	var before := b.get_combined_minimum_size()
	var sb := b.get_theme_stylebox(&"focus") as StyleBoxBrackets
	assert_not_null(sb, "the theme's focus is the brackets")
	assert_eq(sb.get_minimum_size(), Vector2.ZERO, "adds nothing to the size")
	b.grab_focus()
	await wait_frames(1)
	assert_eq(b.get_combined_minimum_size(), before, "focus never changes the min size")
	var r := Rect2(Vector2.ZERO, Vector2(120, 40))
	var arms := StyleBoxBrackets.arm_rects(r.grow(StyleBoxBrackets.OFFSET))
	assert_eq(arms.size(), 8, "four corners, two arms each")
	for a in arms:
		assert_false(r.grow(-0.01).intersects(a), "every arm sits outside the control")
		assert_true(minf(a.size.x, a.size.y) == StyleBoxBrackets.THICKNESS, "2 px thick")
	assert_eq(sb._get_draw_rect(r), r.grow(StyleBoxBrackets.OFFSET + StyleBoxBrackets.THICKNESS + StyleBoxBrackets.KEYLINE))


func test_focus_scale_is_1_03_about_the_centre_and_never_reflows() -> void:
	Motion.force_live = true
	Settings.set_reduce_effects(true)  # the end state at once
	Settings.set_pad_active(true)  # the scale is for pad focus (TV distance)
	var h := _holder()
	var box := VBoxContainer.new()
	h.add_child(box)
	var a := Button.new()
	a.text = "ONE"
	var b := Button.new()
	b.text = "TWO"
	box.add_child(a)
	box.add_child(b)
	await wait_frames(2)
	var rect_b := b.get_rect()
	var size_a := a.size
	a.grab_focus()
	await wait_frames(1)
	assert_almost_eq(a.scale.x, Motion.amplitude(UiFocus.SCALE_MOTION), 0.001, "1.03 on focus")
	assert_almost_eq(Motion.amplitude(UiFocus.SCALE_MOTION), 1.03, 0.0001)
	assert_eq(Motion.entry(UiFocus.SCALE_MOTION).tier, UiMotionEntryData.Tier.T1_FEEDBACK, "a T1 motion")
	assert_eq(a.size, size_a, "the size never changes")
	assert_eq(a.pivot_offset, a.size * 0.5, "about its centre")
	assert_eq(b.get_rect(), rect_b, "its neighbour never moves")
	box.queue_sort()
	await wait_frames(1)
	assert_almost_eq(a.scale.x, 1.03, 0.001, "kept through a container sort")
	b.grab_focus()
	await wait_frames(1)
	assert_almost_eq(a.scale.x, 1.0, 0.001, "back to rest when focus leaves")
	assert_almost_eq(b.scale.x, 1.03, 0.001)
	Settings.set_reduce_effects(false)


func test_cards_and_tilted_controls_keep_their_own_focus_look() -> void:
	var c := Button.new()
	c.set_meta(UiFocus.META_NO_SCALE, true)
	assert_false(UiFocus.scales_on_focus(c))
	var t := Button.new()
	t.rotation = 0.1
	assert_false(UiFocus.scales_on_focus(t))
	assert_true(UiFocus.scales_on_focus(Button.new()))
	assert_false(UiFocus.scales_on_focus(Label.new()))
	for n in [c, t]:
		n.free()


# --- §6.7 the one toast ---------------------------------------------------------------------------

func test_the_toast_never_overlaps_a_bottom_button() -> void:
	var host := SCREEN
	var sz := Vector2(420, 48)
	var bottom := Rect2(540, 640, 200, 44)
	var at := Toast.spot(host, sz, Rect2(), [bottom])
	assert_false(Rect2(at, sz).intersects(bottom), "keeps off the bottom-centre button")
	assert_true(host.encloses(Rect2(at, sz)), "inside the screen")
	# A full bottom row of buttons and a prompt bar: it climbs above them.
	var row: Array[Rect2] = [Rect2(24, 600, 1232, 44), Rect2(300, 670, 680, 30)]
	at = Toast.spot(host, sz, Rect2(), row)
	for r in row:
		assert_false(Rect2(at, sz).intersects(r), "clear of %s" % r)
	# Beside an anchor, never on it.
	var anchor := Rect2(600, 300, 120, 40)
	at = Toast.spot(host, sz, anchor, [])
	assert_false(Rect2(at, sz).intersects(anchor), "never covers what it refers to")
	assert_lt(Rect2(at, sz).get_center().distance_to(anchor.get_center()), 120.0, "near it")


func test_one_toast_style_for_every_caller() -> void:
	var h := _holder()
	var note := ToastNote.show_on(h, "Saved.", false)
	assert_true(note is Toast, "ToastNote renders through the one sticky")
	assert_false(note.refusal, "news: the info glyph")
	var style := note.get_theme_stylebox(&"panel") as StyleBoxFlat
	assert_eq(style.bg_color, Palette.NOTE_YELLOW, "a NOTE_YELLOW sticky")
	assert_eq(note.label.get_theme_font_size(&"font_size"), UiTheme.font_px(UiTheme.LABEL), "words in the label step")
	assert_eq(note.mouse_filter, Control.MOUSE_FILTER_IGNORE)
	assert_eq(note.focus_mode, Control.FOCUS_NONE)
	var refusal := Toast.pop_on(h, "Not enough RAM", true)
	assert_true(refusal.refusal, "a refusal: the no-entry glyph")
	assert_eq(h.get_children().filter(func(c: Node) -> bool: return c is Toast and not c.is_queued_for_deletion()).size(), 1, "one per screen")
	var combat := Toast.new()
	h.add_child(combat)
	combat.show_text("Nope", Vector2(640, 600), 300.0)
	assert_eq((combat.get_theme_stylebox(&"panel") as StyleBoxFlat).bg_color, Palette.NOTE_YELLOW, "combat's own toast is the same sticky")
	# Contrast: INK on the sticky.
	assert_gte(Palette.contrast(Palette.INK, Palette.NOTE_YELLOW), 4.5)


func test_toast_timings_follow_the_bible() -> void:
	assert_almost_eq(Motion.entry(Toast.IN_MOTION).duration, 0.18, 0.0001)
	assert_almost_eq(Motion.entry(Toast.HOLD_MOTION).duration, 2.5, 0.0001)
	assert_almost_eq(Motion.entry(Toast.OUT_MOTION).duration, 0.2, 0.0001)
	assert_almost_eq(Toast.hold_seconds("Saved."), 2.5, 0.0001, "a short toast holds 2.5 s")
	var long := "x".repeat(60)
	assert_almost_eq(Toast.hold_seconds(long), ZineStamp.hold_seconds(long), 0.0001, "long words hold to the reading rule")


# --- §6.8 tooltips ----------------------------------------------------------------------------------

func test_tooltips_fold_to_26_to_36_columns_and_long_text_uses_the_body_face() -> void:
	assert_eq(UiTip.COLUMNS, 36)
	assert_eq(UiTip.MIN_COLUMNS, 26)
	var text := "A long description of what this Daemon does when it triggers on the wheel and what it costs to run it."
	for line in UiTip.fold(text).split("\n"):
		assert_lte(line.length(), UiTip.COLUMNS)
	var short := UiTip.make("Heat rises when you are seen.", "Heat")
	var body := short.get_child(1) as Label
	assert_eq(body.theme_type_variation, &"TooltipLabel", "3 lines or fewer: mono")
	var long_tip := UiTip.make(text + " " + text)
	var long_body := long_tip.get_child(0) as Label
	assert_eq(long_body.theme_type_variation, UiTheme.BODY_TEXT, "over 3 lines: the body face")
	for n in [short, long_tip]:
		n.free()


func test_a_tooltip_never_repeats_its_title() -> void:
	var tip := UiTip.make("Daemon Twin Pointer\nYour wheel is also read at the bottom.", "Twin Pointer")
	var texts: Array[String] = []
	for c in tip.get_children():
		texts.append((c as Label).text)
	assert_eq(texts[0], "TWIN POINTER")
	assert_false(texts[1].contains("Daemon Twin Pointer"), "the title is said once")
	tip.free()


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


# --- §6.6 stamps and banners -------------------------------------------------------------------------

func test_stamp_hold_follows_the_reading_rule() -> void:
	for text in ["REPELLED", "CLEAN EXIT", "NO DAMAGE"]:
		assert_gte(ZineStamp.hold_seconds(text), 0.6 + 0.05 * text.length() - 0.0001, "%s is held long enough" % text)
	var e := Motion.entry(ZineStamp.HOLD_MOTION)
	assert_almost_eq(e.duration, 0.6, 0.0001)
	assert_almost_eq(e.amplitude, 0.05, 0.0001)


func test_a_stamp_says_three_words_at_most() -> void:
	assert_false(ZineStamp.warn_if_wordy("CLEAN EXIT"))
	assert_true(ZineStamp.warn_if_wordy("THIS IS FAR TOO LONG"), "a debug warning past 3 words")
	assert_eq(ZineStamp.word_count("NO DAMAGE"), 2)


func test_one_banner_per_region_the_rest_queue() -> void:
	var h := _holder()
	var q := BannerQueue.of(h, &"hub")
	assert_eq(BannerQueue.of(h, &"hub"), q, "one queue per region")
	assert_ne(BannerQueue.of(h, &"map"), q)
	var a := ZineStamp.new("PHASE")
	var b := ZineStamp.new("NO DAMAGE")
	h.add_child(a)
	h.add_child(b)
	q.push(a)
	q.push(b)
	assert_eq(q.current(), a, "the first shows")
	assert_true(a.visible)
	assert_false(b.visible, "the second waits")
	assert_eq(q.pending(), 1)
	q.finish_current()
	await BoundedWait.until(get_tree(), func() -> bool: return q.current() == b, BoundedWait.motion_limit([BannerQueue.GAP_MOTION]))
	assert_eq(q.current(), b, "then the next")
	assert_true(b.visible)


func test_a_zine_stamp_word_never_falls_under_caption() -> void:
	var h := _holder()
	var s := ZineStamp.new("CATASTROPHIC")
	h.add_child(s)
	await wait_frames(1)
	assert_gte(s.word_px(50.0), UiTheme.font_px(UiTheme.CAPTION))


# --- §12 pad glyphs ------------------------------------------------------------------------------------

func test_every_pad_glyph_set_has_every_button() -> void:
	assert_eq(PadGlyph.SETS, [PadGlyph.SET_XBOX, PadGlyph.SET_PLAYSTATION, PadGlyph.SET_SWITCH, PadGlyph.SET_DECK])
	for s in PadGlyph.SETS:
		for b in PadGlyph.BUTTONS:
			assert_true(PadGlyph.has_glyph(s, b), "%s has button %d" % [s, b])
			assert_ne(PadGlyph.name_of(b, s), "")
		assert_ne(PadGlyph.name_of(PadGlyph.MENU, s).to_lower(), "[view]")
	assert_eq(PadGlyph.name_of(PadGlyph.FACE_SOUTH, PadGlyph.SET_SWITCH), "B", "Switch: B at the bottom")
	assert_eq(PadGlyph.name_of(PadGlyph.FACE_EAST, PadGlyph.SET_SWITCH), "A")
	assert_eq(PadGlyph.name_of(PadGlyph.FACE_SOUTH, PadGlyph.SET_PLAYSTATION), "Cross")


func test_pad_glyphs_draw_every_button_in_every_set() -> void:
	var h := _holder()
	for s in PadGlyph.SETS:
		for b in PadGlyph.BUTTONS:
			var g := PadGlyph.new(b, s)
			h.add_child(g)
			assert_gt(g.get_combined_minimum_size().y, 0.0)
	await wait_frames(1)  # every _draw runs without an error
	assert_true(true)


func test_auto_glyph_set_detects_the_pad() -> void:
	assert_eq(PadGlyph.detect_set("Xbox Series Controller"), PadGlyph.SET_XBOX)
	assert_eq(PadGlyph.detect_set("PS5 Controller"), PadGlyph.SET_PLAYSTATION)
	assert_eq(PadGlyph.detect_set("DualShock 4"), PadGlyph.SET_PLAYSTATION)
	assert_eq(PadGlyph.detect_set("Nintendo Switch Pro Controller"), PadGlyph.SET_SWITCH)
	assert_eq(PadGlyph.detect_set("Steam Deck"), PadGlyph.SET_DECK)
	assert_eq(PadGlyph.detect_set(""), PadGlyph.SET_XBOX, "no pad: Godot's own layout")
	assert_true(PadGlyph.SETS.has(PadGlyph.current_set()))


func test_prompts_are_glyph_and_word_never_bracketed_letters() -> void:
	var h := _holder()
	var row := PadPrompts.new()
	h.add_child(row)
	Settings.set_pad_active(true)
	row.set_prompts([[&"ui_accept", "Buy"], [&"ui_cancel", "Leave"], [&"open_settings", "Settings"]])
	assert_true(row.visible)
	assert_eq(row.glyphs().size(), 3, "a drawn glyph per prompt")
	assert_eq(row.glyphs()[0].button, PadGlyph.FACE_SOUTH)
	for pair in row.get_children():
		for c in pair.get_children():
			if c is Label:
				assert_false((c as Label).text.contains("["), "no letters in brackets")
				assert_false((c as Label).text in ["Menu", "View", "A", "B"], "the button is the glyph, not a word")
	assert_eq(row.texts()[0], "A  Buy")


# --- §7.4 icons ----------------------------------------------------------------------------------

func test_the_status_glyphs_are_stat_icons() -> void:
	for st in [RC.Status.CORRUPTED, RC.Status.OVERCLOCKED, RC.Status.ENCRYPTED, RC.Status.PARASITE]:
		var k := StatIcon.for_status(st)
		assert_ne(k, &"", "status %d has an icon" % st)
		assert_true(StatIcon.ALL.has(k))
	for k in StatIcon.KIT_KINDS:
		assert_true(StatIcon.ALL.has(k), "%s is a StatIcon" % k)
	assert_almost_eq(StatIcon.stroke_for(StatIcon.GRID_PX * 0.5), StatIcon.STROKE_PX, 0.1, "2 px stroke on the 24 px grid")


func test_status_icons_draw_filled_and_open() -> void:
	var h := _holder()
	var d := _Drawer.new()
	h.add_child(d)
	await wait_frames(1)
	assert_true(d.drew, "every status and kit icon draws, filled and open")


class _Drawer extends Control:
	var drew := false

	func _draw() -> void:
		for k in StatIcon.STATUS_KINDS.values() + StatIcon.KIT_KINDS:
			StatIcon.draw(self, Vector2(20, 20), 12.0, k, Palette.TEXT_HI, false)
			StatIcon.draw(self, Vector2(50, 20), 12.0, k, Palette.TEXT_HI, true)
		drew = true


# --- the SAVED stamp -------------------------------------------------------------------------------

func test_saved_is_a_type_step_with_4_5_to_1() -> void:
	Fx.place_saved(SCREEN)
	assert_eq(Fx.saved_label.get_theme_font_size(&"font_size"), UiTheme.font_px(UiTheme.LABEL), "a type step")
	var paper := Fx.saved_label.get_theme_stylebox(&"normal") as StyleBoxFlat
	assert_not_null(paper, "lettered on paper")
	assert_gte(Palette.contrast(Fx.saved_label.get_theme_color(&"font_color"), paper.bg_color), 4.5)


# --- inputs ----------------------------------------------------------------------------------------

func test_inputs_emit_expose_value_and_take_focus() -> void:
	var h := _holder()
	var t := ZineToggle.new("Subtitles")
	var sl := ZineSlider.new(0.8, 2.0, 0.1, 1.0)
	sl.format = func(v: float) -> String: return "%.1f×" % v
	var st := Stepper.new(0, 5, 1, 2)
	var tiles: Array[Dictionary] = [{"name": "A"}, {"name": "B", "locked": true, "unlock": "Win once"}, {"name": "C"}]
	var tp := TilePicker.new(tiles)
	var cf := CodeField.new("ABCD-1234", true)
	for c in [t, sl, st, tp, cf]:
		h.add_child(c)
	for c in [t, sl, st, tp]:
		assert_ne((c as Control).focus_mode, Control.FOCUS_NONE, "%s is focusable" % c)
	watch_signals(t)
	t.button_pressed = true
	assert_signal_emitted(t, "value_changed")
	assert_true(t.value)
	sl.value = 1.6
	assert_eq(sl.readout(), "1.6×", "the slider reads its value")
	watch_signals(tp)
	tp.choose(1)
	assert_signal_emitted(tp, "refused", "a locked tile is refused")
	assert_eq(tp.selected(), 0)
	tp.choose(2)
	assert_signal_emitted(tp, "tile_chosen")
	assert_eq(tp.value, 2.0)
	assert_eq(cf.value, "ABCD-1234")
	assert_false(cf.field.editable, "a code to copy, not to type")


func test_toggles_line_up_16_px_right_of_the_longest_label() -> void:
	var h := _holder()
	var a := ZineToggle.new("Subtitles")
	var b := ZineToggle.new("Reduce effects")
	h.add_child(a)
	h.add_child(b)
	ZineToggle.align_group([a, b])
	a.size = a.get_combined_minimum_size()
	b.size = b.get_combined_minimum_size()
	assert_eq(a.pill_rect().position.x, b.pill_rect().position.x, "the switches line up")
	assert_almost_eq(a.pill_rect().position.x, b.own_label_width() + UiTheme.SP_M, 0.01, "16 px right of the longest label")


func test_the_tile_picker_moves_its_cursor_with_the_keys() -> void:
	var h := _holder()
	var tiles: Array[Dictionary] = [{"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}]
	var tp := TilePicker.new(tiles, 2)
	h.add_child(tp)
	tp.grab_focus()
	var right := InputEventAction.new()
	right.action = &"ui_right"
	right.pressed = true
	tp._gui_input(right)
	assert_eq(tp.cursor, 1)
	var down := InputEventAction.new()
	down.action = &"ui_down"
	down.pressed = true
	tp._gui_input(down)
	assert_eq(tp.cursor, 3, "down a row")
	tp._gui_input(right)
	assert_eq(tp.cursor, 3, "the edge lets focus move on")


func test_refusal_mark_flashes_on_native_buttons() -> void:
	var h := _holder()
	var b := Button.new()
	b.text = "BUY"
	h.add_child(b)
	var m := RefusalMark.flash(b)
	assert_eq(RefusalMark.of(b), m)
	assert_eq(KitState.of(m), KitState.REFUSED)
	assert_eq(m.mouse_filter, Control.MOUSE_FILTER_IGNORE)
