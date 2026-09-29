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
	await get_tree().create_timer(PageTransition.MODAL_BUDGET + 0.1).timeout
	assert_true(done[0], "then it is gone and the caller goes on")
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
