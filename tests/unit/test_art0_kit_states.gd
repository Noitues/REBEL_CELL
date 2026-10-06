extends GutTest
## ART-0 F (Salvage S5; ported from art-pass W2 59b064e / 77c96df / ccf30fc, W8a a155849 /
## d91a26f; ART_BIBLE v1 §6, §10, §12 kept by v2, v2 §2.10): the kit's behaviour on main.
## Every kit component has the six states; the focus brackets are 3 px at 7 px outside the
## control (round 31, v2 Appendix C #15) and never change a minimum size; the pad focus scale
## never reflows; PadGlyph draws every button of every glyph set, from area C's stored set;
## the prompt bar is glyph + verb; modals open and close in their budget, sit on a GlassScrim
## and a page never changes under one. M13's look tests are dropped (DECISIONS "Art
## direction — ART-0 kit behaviour (salvage S5, area F)").

const SCREEN := Rect2(0, 0, 1280, 720)
const TITLE := "res://scenes/menu/title_scene.tscn"
const SLOT := "gut_art0_kit_states"

var _saved: Dictionary
var _force_live: bool


func before_each() -> void:
	_saved = Settings.snapshot()
	_force_live = Motion.force_live
	Settings.set_text_scale(1.0)
	Settings.set_pad_active(false)
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = _force_live
	Settings.restore(_saved)


func _frames(n: int = 1) -> void:
	for i in n:
		await get_tree().process_frame


func _holder() -> Control:
	var h: Control = add_child_autofree(Control.new())
	h.size = SCREEN.size
	UiTheme.apply(h)
	return h


## Every kit component on main that draws its own states, fresh.
func _components() -> Array[Control]:
	var out: Array[Control] = [ZineStamp.new("JACK IN"), StickerButton.new("RESPIN"), DripButton.new("SEND IT")]
	return out


# --- §6 the six states -------------------------------------------------------------------------

func test_every_component_exposes_all_six_states() -> void:
	var h := _holder()
	assert_eq(KitState.ALL, [KitState.IDLE, KitState.HOVER, KitState.FOCUS, KitState.PRESSED, KitState.DISABLED, KitState.REFUSED])
	for c in _components():
		h.add_child(c)
		assert_true(c.has_method(&"state"), "%s reports its state" % c.get_script().get_global_name())
		assert_true(c.has_method(&"refuse"), "%s can be refused" % c.get_script().get_global_name())
		assert_eq(c.call(&"state"), KitState.IDLE, "%s idles" % c.get_script().get_global_name())
		for st in KitState.ALL:
			KitState.force(c, st)
			assert_eq(c.call(&"state"), st, "%s shows %s" % [c.get_script().get_global_name(), st])
		KitState.clear_force(c)
	await _frames(1)  # every state draws without an error


func test_live_states_follow_the_control() -> void:
	var h := _holder()
	var s := StickerButton.new("UNDO")
	h.add_child(s)
	s.disabled = true
	assert_eq(s.state(), KitState.DISABLED)
	s.refuse()
	assert_eq(s.state(), KitState.REFUSED, "a refusal shows over disabled")
	s.remove_meta(KitState.META_REFUSED)
	s.disabled = false
	assert_eq(s.state(), KitState.IDLE)
	s.grab_focus()
	await _frames(1)
	assert_eq(s.state(), KitState.FOCUS)
	KitState.set_pressed(s, true)
	assert_eq(s.state(), KitState.PRESSED, "a press held shows over focus")
	KitState.set_pressed(s, false)
	assert_eq(KitState.lift(KitState.HOVER), -float(UiTheme.HOVER_LIFT), "hover lifts")
	assert_eq(KitState.lift(KitState.PRESSED), float(UiTheme.PRESS_DROP), "pressed drops")
	assert_gt(KitState.glow(KitState.HOVER), KitState.glow(KitState.IDLE))
	assert_lt(KitState.glow(KitState.PRESSED), KitState.glow(KitState.IDLE))


func test_the_refused_state_lasts_its_entry_and_is_a_t2_motion() -> void:
	var e := Motion.entry(KitState.REFUSED_MOTION)
	assert_not_null(e, "button_refused is in the table")
	assert_eq(e.tier, UiMotionEntryData.Tier.T2_OUTCOME, "a T2 motion")
	assert_true(UiMotionData.REQUIRED_IDS.has(KitState.REFUSED_MOTION))
	var h := _holder()
	var s := StickerButton.new("RESPIN")
	h.add_child(s)
	s.refuse()
	assert_true(KitState.refused(s))
	assert_almost_eq(KitState.refused_progress(s), 0.0, 0.25, "it has just started (its length is the entry's seconds)")
	assert_eq(KitState.refused_progress(autofree(StickerButton.new("X"))), 1.0, "never refused: over")


func test_hover_lifts_2_and_pressed_drops_1_without_resizing() -> void:
	var th := UiTheme.build(1.0)
	for kind in [&"Button", &"HotButton", &"NoteButton", &"MenuItem"]:
		var n := th.get_stylebox(&"normal", kind) as StyleBoxFlat
		var hv := th.get_stylebox(&"hover", kind) as StyleBoxFlat
		var pr := th.get_stylebox(&"pressed", kind) as StyleBoxFlat
		assert_eq(hv.expand_margin_top - n.expand_margin_top, float(UiTheme.HOVER_LIFT), "%s hover lifts" % kind)
		assert_eq(pr.expand_margin_bottom - n.expand_margin_bottom, float(UiTheme.PRESS_DROP), "%s pressed drops" % kind)
		assert_eq(hv.get_minimum_size(), n.get_minimum_size(), "%s hover keeps the size" % kind)
		assert_eq(pr.get_minimum_size(), n.get_minimum_size(), "%s pressed keeps the size" % kind)


func test_refusal_mark_flashes_on_native_buttons() -> void:
	var h := _holder()
	var b := Button.new()
	b.text = "BUY"
	h.add_child(b)
	var before := b.get_combined_minimum_size()
	var m := RefusalMark.flash(b)
	assert_eq(RefusalMark.of(b), m)
	assert_eq(RefusalMark.flash(b), m, "a second refusal restarts the one there")
	assert_eq(KitState.of(m), KitState.REFUSED)
	assert_eq(m.mouse_filter, Control.MOUSE_FILTER_IGNORE)
	assert_eq(m.focus_mode, Control.FOCUS_NONE)
	assert_eq(b.get_combined_minimum_size(), before, "never resizes its control")
	await _frames(1)


func test_force_native_shows_each_state_on_a_theme_button() -> void:
	var h := _holder()
	var b := Button.new()
	b.text = "CONTINUE"
	h.add_child(b)
	for st in KitState.ALL:
		KitState.force_native(b, st)
		assert_eq(KitState.of(b), st if st != KitState.IDLE else KitState.IDLE, "native %s" % st)
	KitState.force_native(b, KitState.IDLE)
	assert_false(b.disabled)
	assert_null(b.get_node_or_null(KitState.FORCED_NODE))
	await _frames(1)


# --- v2 §2.10 focus: brackets and the 1.03 scale ---------------------------------------------

func test_focus_brackets_are_3_px_at_7_px_on_every_focus_type() -> void:
	assert_eq(StyleBoxBrackets.THICKNESS, 3.0, "round 31: 3 px thick")
	assert_eq(StyleBoxBrackets.OFFSET, 7.0, "round 31: 7 px outside")
	assert_eq(StyleBoxBrackets.new().color, Palette.FOCUS, "lime FOCUS")
	var th := UiTheme.build(1.0)
	for kind in UiTheme.BRACKET_FOCUS_TYPES:
		assert_true(th.get_stylebox(&"focus", kind) is StyleBoxBrackets, "%s focus is the brackets" % kind)
	# A sticker (HotButton) gets its lime die-cut halo, never brackets (v2 §2.10; ART-1 1A).
	var h := _holder()
	var hot := Button.new()
	hot.theme_type_variation = &"HotButton"
	h.add_child(hot)
	assert_false(hot.get_theme_stylebox(&"focus") is StyleBoxBrackets, "HotButton focus is the sticker halo")
	assert_eq((hot.get_theme_stylebox(&"focus") as StyleBoxFlat).border_color, Palette.FOCUS, "a lime halo")


func test_focus_brackets_draw_outside_and_never_change_min_size() -> void:
	var h := _holder()
	var b := Button.new()
	b.text = "CONTINUE"
	h.add_child(b)
	await _frames(1)
	var before := b.get_combined_minimum_size()
	var sb := b.get_theme_stylebox(&"focus") as StyleBoxBrackets
	assert_not_null(sb, "the theme's focus is the brackets")
	assert_eq(sb.get_minimum_size(), Vector2.ZERO, "adds nothing to the size")
	b.grab_focus()
	await _frames(1)
	assert_eq(b.get_combined_minimum_size(), before, "focus never changes the min size")
	var r := Rect2(Vector2.ZERO, Vector2(120, 40))
	var arms := StyleBoxBrackets.arm_rects(r.grow(StyleBoxBrackets.OFFSET))
	assert_eq(arms.size(), 8, "four corners, two arms each")
	var bound := arms[0]
	for a in arms:
		assert_false(r.grow(-0.01).intersects(a), "every arm sits outside the control")
		assert_eq(minf(a.size.x, a.size.y), StyleBoxBrackets.THICKNESS, "3 px thick")
		bound = bound.merge(a)
	assert_eq(bound, r.grow(StyleBoxBrackets.OFFSET), "the brackets' outer edge is 7 px out")
	assert_eq(sb._get_draw_rect(r), r.grow(StyleBoxBrackets.OFFSET + StyleBoxBrackets.THICKNESS + StyleBoxBrackets.KEYLINE))


func test_high_contrast_thickens_the_brackets() -> void:
	var th := UiTheme.build(1.0)
	HighContrast.apply(th)
	for kind in UiTheme.BRACKET_FOCUS_TYPES:
		var sb := th.get_stylebox(&"focus", kind) as StyleBoxBrackets
		assert_eq(sb.thickness, float(HighContrast.HC_FOCUS_BORDER), "%s: thicker for 3 m" % kind)
		assert_eq(sb.color, HighContrast.FOCUS)
	Settings.set_high_contrast(true)
	assert_eq(StyleBoxBrackets.current_thickness(), float(HighContrast.HC_FOCUS_BORDER), "drawn brackets too")
	Settings.set_high_contrast(false)
	assert_eq(StyleBoxBrackets.current_thickness(), StyleBoxBrackets.THICKNESS)


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
	await _frames(2)
	var rect_b := b.get_rect()
	var size_a := a.size
	a.grab_focus()
	await _frames(1)  # fixed-wait-ok: reduce effects is on, so the scale is its end state at once
	assert_almost_eq(a.scale.x, Motion.amplitude(UiFocus.SCALE_MOTION), 0.001, "1.03 on focus")
	assert_almost_eq(Motion.amplitude(UiFocus.SCALE_MOTION), 1.03, 0.0001)
	assert_eq(Motion.entry(UiFocus.SCALE_MOTION).tier, UiMotionEntryData.Tier.T1_FEEDBACK, "a T1 motion")
	assert_eq(a.size, size_a, "the size never changes")
	assert_eq(a.pivot_offset, a.size * 0.5, "about its centre")
	assert_eq(b.get_rect(), rect_b, "its neighbour never moves")
	box.queue_sort()
	await _frames(1)  # fixed-wait-ok: the sort, not a motion (reduce effects: end state at once)
	assert_almost_eq(a.scale.x, 1.03, 0.001, "kept through a container sort")
	b.grab_focus()
	await _frames(1)  # fixed-wait-ok: reduce effects is on, so the scale is its end state at once
	assert_almost_eq(a.scale.x, 1.0, 0.001, "back to rest when focus leaves")
	assert_almost_eq(b.scale.x, 1.03, 0.001)
	b.release_focus()
	await _frames(1)


func test_mouse_and_headless_focus_never_scale() -> void:
	assert_eq(UiFocus.focus_scale(), 1.0, "headless keeps every rect exact")
	Motion.force_live = true
	Settings.set_pad_active(false)
	assert_eq(UiFocus.focus_scale(), 1.0, "a mouse or keyboard player sees the brackets alone")


func test_cards_and_tilted_controls_keep_their_own_focus_look() -> void:
	var c := Button.new()
	c.set_meta(UiFocus.META_NO_SCALE, true)
	assert_false(UiFocus.scales_on_focus(c))
	var t := Button.new()
	t.rotation = 0.1
	assert_false(UiFocus.scales_on_focus(t))
	assert_true(UiFocus.scales_on_focus(autofree(Button.new())))
	assert_false(UiFocus.scales_on_focus(autofree(Label.new())))
	var card: ZineCard = add_child_autofree(ZineCard.new("JAM", 1, "Deal 8.", 0))  # in the tree: its parts free with it
	assert_false(UiFocus.scales_on_focus(card), "a card lifts itself")
	for n in [c, t]:
		n.free()


# --- §12 pad glyphs ------------------------------------------------------------------------------

func test_every_pad_glyph_set_has_every_button() -> void:
	assert_eq(PadGlyph.SETS, [PadGlyph.SET_XBOX, PadGlyph.SET_PLAYSTATION, PadGlyph.SET_SWITCH, PadGlyph.SET_DECK])
	for s in PadGlyph.SETS:
		assert_true(Settings.PAD_GLYPH_SETS.has(s), "%s is a set Settings stores" % s)
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
			assert_eq(g.glyph_name(), PadGlyph.name_of(b, s))
	await _frames(1)  # every _draw runs without an error
	assert_true(true)


func test_the_glyph_set_is_the_one_settings_stores_or_detects() -> void:
	assert_eq(PadGlyph.detect_set("Xbox Series Controller"), PadGlyph.SET_XBOX)
	assert_eq(PadGlyph.detect_set("PS5 Controller"), PadGlyph.SET_PLAYSTATION)
	assert_eq(PadGlyph.detect_set("DualShock 4"), PadGlyph.SET_PLAYSTATION)
	assert_eq(PadGlyph.detect_set("Nintendo Switch Pro Controller"), PadGlyph.SET_SWITCH)
	assert_eq(PadGlyph.detect_set("Steam Deck"), PadGlyph.SET_DECK)
	assert_eq(PadGlyph.detect_set(""), PadGlyph.SET_XBOX, "no pad: Godot's own layout")
	assert_true(PadGlyph.SETS.has(PadGlyph.current_set()))
	for s in PadGlyph.SETS:
		Settings.set_pad_glyph_set(s)
		assert_eq(PadGlyph.current_set(), s, "the stored set is drawn (%s)" % s)
	Settings.set_pad_glyph_set(&"auto")
	assert_eq(PadGlyph.current_set(), Settings.effective_glyph_set(), "auto: the detected set")


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
	Settings.set_pad_glyph_set(&"playstation")
	row.set_prompts(row.prompts)
	assert_eq(row.texts()[0], "Cross  Buy", "the glyphs follow the stored set")


# --- §10 modals and the SCRIM --------------------------------------------------------------------

func test_modals_open_and_close_within_budget_never_a_cut() -> void:
	for id in [&"modal_in", &"modal_out"]:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(Motion.seconds(id) > 0.0 and Motion.seconds(id) <= PageTransition.MODAL_BUDGET, "%s in budget" % id)
	Motion.force_live = true
	var m := Control.new()
	add_child(m)
	PageTransition.open_modal(m)
	assert_true(PageTransition.modal_open(self))
	assert_true(m.is_in_group(PageTransition.MODAL_GROUP))
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


func test_headless_modals_open_and_close_at_once() -> void:
	var m: Control = Control.new()
	add_child(m)
	PageTransition.open_modal(m)
	assert_eq(m.modulate.a, 1.0, "no motion headless: open at once")
	var seen := []
	PageTransition.after_modals(self, func() -> void: seen.append(PageTransition.modal_open(self)))
	assert_eq(seen, [false], "the action runs once every modal has closed")
	await _frames(1)
	assert_false(is_instance_valid(m))


func test_no_page_change_under_an_open_modal() -> void:
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	await _frames(3)
	title.confirm_quit()
	assert_true(title.confirm_visible())
	assert_true(PageTransition.modal_open(title), "the confirm is a modal")
	var seen: Array = []
	PageTransition.after_modals(title, func() -> void: seen.append(PageTransition.modal_open(title)))
	await _frames(3)
	assert_eq(seen, [false], "the page change runs once, with no modal open")
	title.confirm_quit()
	title.show_codex()
	await _frames(3)
	assert_false(title.confirm_visible(), "a page change closes the confirm first")
	assert_eq(title.panel_name, "codex")
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func test_a_confirm_sits_on_a_scrim_that_takes_the_page_clicks_and_traps_the_pad() -> void:
	var h := _holder()
	var page := Button.new()
	page.text = "BEHIND"
	h.add_child(page)
	var d := ConfirmDialog.new("Quit?")
	h.add_child(d)
	await _frames(2)
	var scrim := d.get_node_or_null("ModalScrim") as GlassScrim
	assert_not_null(scrim, "a GlassScrim behind the confirm")
	assert_eq(scrim.mouse_filter, Control.MOUSE_FILTER_STOP, "it takes the clicks meant for the page")
	# ART-10 4C: a plain child behind the dialog (top-level, it drew over the dialog's words),
	# still over the whole screen.
	assert_true(scrim.show_behind_parent)
	assert_eq(scrim.size, d.get_viewport_rect().size, "over the whole screen")
	assert_eq(scrim.get_global_rect().position, Vector2.ZERO, "from the screen's corner")
	assert_true(d.is_in_group(PageTransition.MODAL_GROUP))
	# Pad reachability inside the modal: Yes and No, and never out to the page behind.
	var start := get_viewport().gui_get_focus_owner()
	assert_eq(start, d.no_button, "the safe answer takes focus")
	var seen := {start: true}
	var queue: Array = [start]
	while not queue.is_empty():
		var c: Control = queue.pop_front()
		for side in [SIDE_LEFT, SIDE_RIGHT, SIDE_TOP, SIDE_BOTTOM]:
			var n := c.find_valid_focus_neighbor(side)
			if n != null and not seen.has(n):
				seen[n] = true
				queue.append(n)
	assert_true(seen.has(d.yes_button), "Yes is pad reachable")
	assert_false(seen.has(page), "the page behind is not")
	d.no_button.pressed.emit()
	await _frames(1)
	assert_false(is_instance_valid(d) and d.is_inside_tree(), "No closes it")


func test_high_contrast_makes_the_scrim_opaque() -> void:
	Settings.set_high_contrast(true)
	var s := GlassScrim.new()
	add_child_autofree(s)
	assert_true(s.opaque(), "opaque under high contrast")
	assert_eq(s.color, HighContrast.BG)
	Settings.set_high_contrast(false)
	s.sync()
	assert_false(s.opaque(), "a blur otherwise")
	assert_eq((s.material as ShaderMaterial).shader, GlassScrim.SHADER)
	assert_eq(s.mouse_filter, Control.MOUSE_FILTER_IGNORE, "a plain scrim eats no clicks")
	assert_eq(s.focus_mode, Control.FOCUS_NONE)


func test_the_scrim_shader_reads_the_reduce_effects_global() -> void:
	var src := FileAccess.get_file_as_string("res://shaders/glass_blur.gdshader")
	assert_string_contains(src, "rc_common.gdshaderinc", "the shared include (VfxTier rule)")
	assert_false(src.contains("uniform float reduce_effects"), "no per-material copy")
