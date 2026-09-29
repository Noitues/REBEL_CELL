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
