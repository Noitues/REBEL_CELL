extends GutTest
## Art pass W8d (ART_BIBLE §11 Campaign end (WON / LOST), §8 T4, §6.4, §12, critique 62/63):
## WON and LOST are distinct templates (different art, stamp words and grade); the WON wall
## has one Polaroid per operative (the dead flatlined); LOST greys the city; the story is
## Plex on paper at ≤ 70 characters a line; the page fits at every text scale; the T4 is
## skippable and shows its end at once under reduce effects; the actions are Primary and
## Secondary; the pad gets its prompt bar; the corps read in greyscale by pattern and shape.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SLOT := "gut_art_w8d"
const CANVAS := Vector2(1280, 720)

var _text_scale_before: float = 1.0
var _pad_before: bool = false
var _hc_before: bool = false


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_pad_before = Settings.pad_active
	_hc_before = Settings.high_contrast


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Motion.force_live = false
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(_pad_before)
	if Settings.high_contrast != _hc_before:
		Settings.set_high_contrast(_hc_before)
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


## An HQ on the campaign's end page: `won` or lost, with `dead` operatives flatlined.
func _end(won: bool, dead: int = 0, seed: int = 7) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = CANVAS
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	await _frames(2)
	hq.new_campaign(seed)
	var c := RunManager.campaign
	c.story_beats_revealed = 99
	for i in mini(dead, c.roster.size()):
		c.roster[i].alive = false
	c.outcome = CampaignState.Outcome.WON if won else CampaignState.Outcome.LOST
	hq.show_end()
	await _frames(4)
	return hq


func _stage(hq: Control) -> CampaignEndStage:
	return hq._panel as CampaignEndStage


func _close(hq: Control) -> void:
	hq.get_parent().queue_free()
	await _frames(2)


func _all(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_all(c))
	return out


func _texts(root: Node) -> Array[Control]:
	var out: Array[Control] = []
	for n in _all(root):
		if (n is Label or n is Button) and (n as Control).is_visible_in_tree():
			out.append(n as Control)
	return out


## The part of `c` that shows: its rect clipped by every clipping ancestor below the stage
## (the story's scroll view hides the lines scrolled out of it).
func _shown(c: Control) -> Rect2:
	var r := c.get_global_rect()
	var n := c.get_parent()
	while n != null and not (n is CampaignEndStage):
		if n is Control and ((n as Control).clip_contents or n is ScrollContainer):
			r = r.intersection((n as Control).get_global_rect())
		n = n.get_parent()
	return r


# --- 1. Distinct templates ------------------------------------------------------------------------

func test_won_and_lost_build_different_templates() -> void:
	var hq := await _end(true)
	var won := _stage(hq)
	assert_not_null(won, "the campaign's end is staged")
	assert_eq(hq.panel_name, "end")
	won.finish_now()
	assert_true(won.art is CorpFallArt, "WON: the corp's billboard")
	var bill := won.art as CorpFallArt
	assert_eq(bill.corp_id, RunManager.campaign.corporation_id)
	assert_not_null(bill.landmark(), "the corp's landmark silhouette is baked art")
	assert_eq(bill.fall, 1.0, "the landmark has fallen")
	assert_true(bill.crossed_out(), "the hue and pattern are crossed out in spray")
	assert_eq(bill.strokes[0].material.get_shader_parameter(&"ink"), Palette.CELL_PINK, "CELL_PINK spray")
	assert_eq(won.stamp.shown_word(), tr("CORP DOWN"))
	assert_eq(won.stamp.font_px, VerdictStamp.hero_px(), "the stamp at hero size")
	await _close(hq)
	hq = await _end(false)
	var lost := _stage(hq)
	lost.finish_now()
	assert_true(lost.art is CellCrackArt, "LOST: the Cell's hexagon")
	assert_true((lost.art as CellCrackArt).broken(), "cracked and split")
	assert_eq(lost.stamp.shown_word(), tr("CELL BURNED"))
	assert_ne(won.stamp.shown_word() if is_instance_valid(won) else tr("CORP DOWN"), lost.stamp.shown_word())
	assert_ne(CampaignEndStage.color_of(true), CampaignEndStage.color_of(false), "different stamp inks")
	for w in [CampaignEndStage.verdict_of(true), CampaignEndStage.verdict_of(false)]:
		assert_true(ZineStamp.word_count(w) <= ZineStamp.MAX_WORDS, "a stamp says one thing (§6.6)")
	await _close(hq)


func test_won_leans_the_city_to_the_corp_and_lost_greys_it() -> void:
	var hq := await _end(true)
	var won := _stage(hq)
	won.finish_now()
	assert_eq(won.grade_amount(), 0.0, "a win keeps the city's colour")
	var atmo: CityAtmosphere = hq.background.city.atmosphere()
	assert_almost_eq(atmo.state.progress, 1.0, 0.001, "full campaign progress (§9.3)")
	assert_eq(atmo.state.corp_id, RunManager.campaign.corporation_id, "toward the target corp")
	assert_true(hq.background.visible, "the city shows behind the end: never a black void")
	assert_eq(hq._panel_host.theme_type_variation, &"", "no glass box over the stage")
	await _close(hq)
	hq = await _end(false)
	var lost := _stage(hq)
	lost.finish_now()
	assert_almost_eq(lost.grade_amount(), RunEndStage.GREY_AMOUNT, 0.01, "a loss greys the city")
	# Art pass W9F: the grey is the city's own flatline context (whole screen, behind the
	# subtitle band and the prompt strip too); the stage's own grade is only the fallback.
	assert_almost_eq(hq.background.city.atmosphere().blend_amount(), RunEndStage.GREY_AMOUNT, 0.01, "the city itself greys")
	assert_eq(hq.background.city.atmosphere().state.context, &"flatline")
	assert_false(lost.grade.visible, "no second grade over the page")
	await _close(hq)


func test_the_wall_has_one_polaroid_per_operative() -> void:
	var hq := await _end(true, 1)
	var stage := _stage(hq)
	var roster := RunManager.campaign.roster
	assert_true(roster.size() >= 2, "a crew to show")
	assert_eq(stage.wall.polaroids.size(), roster.size(), "one Polaroid per operative")
	for i in roster.size():
		var want := PortraitArt.Expr.TRIUMPHANT if roster[i].alive else PortraitArt.Expr.FLATLINED
		assert_eq(stage.wall.polaroids[i].expression, want, "%s: %s" % [roster[i].name, "triumphant" if roster[i].alive else "flatlined"])
		assert_eq(stage.wall.polaroids[i].caption, roster[i].name)
		assert_true(absf(stage.wall.polaroids[i].tilt) <= 4.0, "a slight tilt (§2 PAPER)")
		assert_not_null(stage.wall.cells[i].get_node_or_null(^"Tape"), "taped")
	await _close(hq)
	hq = await _end(false, 1)
	stage = _stage(hq)
	assert_eq(stage.wall.polaroids.size(), roster.size())
	assert_eq(stage.wall.polaroids[0].expression, PortraitArt.Expr.FLATLINED, "the lost operative flatlined")
	assert_eq(stage.wall.polaroids[1].expression, PortraitArt.Expr.HURT, "the living hurt")
	await _close(hq)


# --- 2. Story and stats ---------------------------------------------------------------------------

func test_story_is_plex_on_paper_at_most_seventy_characters_a_line() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var hq := await _end(true)
		var stage := _stage(hq)
		stage.finish_now()
		await _frames(2)
		assert_true(stage.story is ZinePanel and not stage.story.terminal, "the story on PAPER")
		var texts := 0
		for l in stage.story_labels:
			if l.name != &"BeatText":
				continue
			texts += 1
			assert_eq(l.theme_type_variation, UiTheme.BODY_TEXT, "Plex body")
			assert_false(l.text.contains("["), "no [x] text")
			var para := TextParagraph.new()
			para.add_string(l.text, l.get_theme_font(&"font"), l.get_theme_font_size(&"font_size"))
			para.width = l.size.x
			para.break_flags = TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
			for i in para.get_line_count():
				var r := para.get_line_range(i)
				assert_true(l.text.substr(r.x, r.y - r.x).strip_edges().length() <= CampaignEndStage.STORY_COLUMNS,
					"≤ 70 characters a line at %.1f: '%s'" % [scale, l.text.substr(r.x, r.y - r.x)])
		assert_true(texts > 0, "the beats are shown")
		if scale == 1.0:
			assert_true(not stage.foot_row.vertical and not stage.hero_row.vertical, "side by side at 1.0 (%s, %s)" % [stage.size, stage.get_combined_minimum_size()])
			assert_true(stage.story.fit != null and stage.story.fit.overflowing(), "a long story scrolls inside its paper at 1.0")
		await _close(hq)


func test_records_are_a_receipt_of_icon_and_number_fields() -> void:
	var hq := await _end(true)
	var stage := _stage(hq)
	assert_true(stage.receipt is RunReceipt, "a taped receipt")
	var kinds: Array[StringName] = []
	var corps := 0
	for n in _all(stage.receipt):
		if n is StatField:
			kinds.append((n as StatField).kind)
		if n is CorpGlyphField:
			corps += 1
			assert_true((n as CorpGlyphField).has_glyph(), "%s: its landmark glyph" % n.name)
	assert_true(kinds.has(StatIcon.WON) and kinds.has(StatIcon.CLOSE) and kinds.has(StatIcon.ICE), "won, lost and best ICE by their icons")
	assert_true(corps >= 4, "each corporation's ICE by its glyph")
	assert_string_contains(stage.receipt.tooltip_text, "Best ICE", "the records in words on hover")
	for c in _texts(stage):
		assert_false((c as Control).get("text").contains("[") , "no [x] text: %s" % (c as Control).get("text"))
		if c is Button:
			continue
		assert_true(c.size.x < CANVAS.x * 0.9, "no full-width bars: '%s'" % (c as Label).text.left(20))
	await _close(hq)


func test_actions_are_primary_and_secondary_and_the_pad_gets_a_prompt_bar() -> void:
	Settings.set_pad_active(true)
	var hq := await _end(true)
	var stage := _stage(hq)
	stage.finish_now()
	assert_eq(stage.new_button.theme_type_variation, UiTheme.PRIMARY, "New campaign is Primary (§6.4)")
	assert_eq(stage.title_button.theme_type_variation, UiTheme.SECONDARY, "Back to title is Secondary")
	assert_eq(stage.new_button.text, tr("New campaign"))
	assert_eq(stage.title_button.text, tr("Back to title"))
	var primaries := 0
	for n in _all(stage):
		if n is Button and (n as Button).theme_type_variation == UiTheme.PRIMARY:
			primaries += 1
	assert_eq(primaries, 1, "one primary")
	await _frames(3)
	assert_true(stage.new_button.size.x < CANVAS.x * 0.5, "sized to its label, not a full-width bar")
	assert_true(hq.pad_prompts.visible, "the prompt bar shows with a pad")
	assert_true(hq.pad_prompts.texts().size() > 0)
	assert_eq(get_viewport().gui_get_focus_owner(), stage.new_button, "focus starts on the primary")
	await _close(hq)


# --- 3. Scale and access --------------------------------------------------------------------------

func test_it_fits_at_every_text_scale() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		for won in [true, false]:
			var hq := await _end(won, 1)
			var stage := _stage(hq)
			stage.finish_now()
			await _frames(3)
			var tag := "%s at %.1f" % ["WON" if won else "LOST", scale]
			assert_true(stage.get_combined_minimum_size().x <= CANVAS.x + 0.5, "%s: fits the width (%.0f)" % [tag, stage.get_combined_minimum_size().x])
			for piece in [stage.art, stage.stamp, stage.wall, stage.story, stage.receipt, stage.actions]:
				var r := (piece as Control).get_global_rect()
				assert_true(r.position.x >= -0.5 and r.end.x <= CANVAS.x + 0.5, "%s: %s within the width %s" % [tag, (piece as Control).name, r])
			var texts := _texts(stage)
			for c in texts:
				var r := c.get_global_rect()
				assert_true(r.position.x >= -0.5 and r.end.x <= CANVAS.x + 0.5, "%s: '%s' within the width" % [tag, String(c.get("text")).left(24)])
				var fs := c.get_theme_font_size(&"font_size")
				assert_true(fs >= UiTheme.font_px(UiTheme.CAPTION), "%s: '%s' at %d px >= caption" % [tag, String(c.get("text")).left(24), fs])
				if c is Label and (c as Label).autowrap_mode != TextServer.AUTOWRAP_OFF:
					var l := c as Label
					assert_true(l.get_line_count() <= maxi(1, l.get_visible_line_count()), "%s: '%s' shows every line" % [tag, l.text.left(24)])
			for i in texts.size():
				for j in range(i + 1, texts.size()):
					var a := texts[i]
					var b := texts[j]
					if a.is_ancestor_of(b) or b.is_ancestor_of(a):
						continue
					if not (a.is_visible_in_tree() and b.is_visible_in_tree()):
						continue
					var ov := _shown(a).intersection(_shown(b))
					assert_false(ov.size.x > 3.0 and ov.size.y > 3.0, "%s: '%s' overlaps '%s' (%s / %s)" % [tag, String(a.get("text")).left(20), String(b.get("text")).left(20), _shown(a), _shown(b)])
			# The polaroids never overlap one another, nor the stamp.
			var photos: Array[Rect2] = []
			for p in stage.wall.polaroids:
				photos.append(p.get_global_rect())
			for i in photos.size():
				for j in range(i + 1, photos.size()):
					assert_false(photos[i].intersects(photos[j]), "%s: photos %d and %d overlap" % [tag, i, j])
				assert_false(photos[i].intersects(stage.stamp.get_global_rect()), "%s: photo %d under the stamp" % [tag, i])
			assert_true(stage.art.get_global_rect().size.y >= stage.art.custom_minimum_size.y - 0.5, "%s: the art at its size" % tag)
			await _close(hq)


func test_at_one_the_page_fits_the_screen_without_a_page_scroll() -> void:
	Settings.set_text_scale(1.0)
	for pad in [false, true]:
		Settings.set_pad_active(pad)
		var hq := await _end(true)
		var stage := _stage(hq)
		stage.finish_now()
		await _frames(6)
		var page := (hq._panel_host.get_parent() as ScrollContainer).get_global_rect()
		if hq.pad_prompts.is_visible_in_tree():
			page.size.y = minf(page.size.y, hq.pad_prompts.get_global_rect().position.y - page.position.y)
		var need := stage.get_combined_minimum_size().y
		assert_true(need <= page.size.y + 0.5, "pad %s: the page needs %.0f px of %.0f (story view %.0f)" % [pad, need, page.size.y, stage.story.fit.scroll.size.y if stage.story.fit != null else -1.0])
		assert_true(stage.story.get_global_rect().end.y <= page.end.y + 0.5, "pad %s: the story's paper ends on the page (%s / %s)" % [pad, stage.story.get_global_rect(), page])
		await _close(hq)


func test_high_contrast_paper_is_ink_at_seven_to_one() -> void:
	Settings.set_high_contrast(true)
	var hq := await _end(true)
	var stage := _stage(hq)
	for l in stage.story_labels:
		var col := l.get_theme_color(&"font_color")
		assert_eq(col, Palette.INK, "story words INK in high contrast")
		assert_true(Palette.contrast(col, Palette.PAPER) >= PaperInk.MIN_CONTRAST)
	for n in _all(stage.receipt):
		if n is Label:
			assert_eq((n as Label).get_theme_color(&"font_color"), Palette.INK)
	await _close(hq)


func test_a_skippable_t4_that_ends_at_once_under_reduce_effects() -> void:
	for id in [CampaignEndStage.MOTION_WON, CampaignEndStage.MOTION_LOST]:
		var e := Motion.entry(id)
		assert_not_null(e, "%s is in ui_motion.tres" % id)
		assert_eq(e.tier, 4, "a T4 moment")
		assert_lte(e.duration, 2.5, "within T4's 2.5 s")
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "required")
	for won in [true, false]:
		var hq := await _end(won)
		var stage := _stage(hq)
		Motion.force_live = true
		stage.play()
		assert_true(stage.running(), "the sequence plays")
		assert_eq(stage.stamp.modulate.a, 0.0, "the stamp comes later")
		var ev := InputEventKey.new()
		ev.keycode = KEY_SPACE
		ev.pressed = true
		stage._input(ev)
		assert_false(stage.running(), "a press skips it")
		assert_eq(stage.progress(), 1.0, "to its end state")
		assert_eq(stage.stamp.modulate.a, 1.0)
		stage.play()
		PageTransition.settle(stage)
		await _frames(2)
		assert_false(stage.running(), "a page settle ends it too")
		assert_eq(stage.stamp.scale, Vector2.ONE, "at its end state")
		assert_eq(stage.receipt.modulate.a, 1.0)
		Motion.force_live = false
		Settings.set_reduce_effects(true)
		stage.play()
		assert_false(stage.running(), "reduce effects: the end state at once (the page cross-fades in)")
		assert_eq(stage.progress(), 1.0)
		assert_eq(stage.wall.cells[0].modulate.a, 1.0)
		if won:
			assert_true((stage.art as CorpFallArt).crossed_out())
		else:
			assert_almost_eq(stage.grade_amount(), RunEndStage.GREY_AMOUNT, 0.01)
		Settings.set_reduce_effects(false)
		await _close(hq)


func test_the_corps_read_in_greyscale_by_pattern_and_landmark() -> void:
	var patterns := {}
	var files := {}
	for id in [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]:
		var path := CorpFallArt.landmark_path(id)
		assert_ne(path, "", "%s has a landmark silhouette" % id)
		var svg := FileAccess.get_file_as_string(path)
		assert_true(svg != "" and not svg.contains("<text"), "%s: baked shapes, no text" % id)
		files[svg.md5_text()] = id
		var kind := Palette.corp_pattern_id(id)
		assert_ne(kind, CorpPattern.Kind.NONE, "%s has a pattern" % id)
		patterns[kind] = id
		var img := Image.new()
		assert_eq(img.load_svg_from_string(svg, 1.0), OK, "%s rasterises" % id)
	assert_eq(patterns.size(), 5, "five different patterns")
	assert_eq(files.size(), 5, "five different landmarks")
	for f in [CellCrackArt.LEFT, CellCrackArt.RIGHT, CellCrackArt.CRACK, CorpFallArt.SPRAY]:
		var img := Image.new()
		assert_eq(img.load_svg_from_string(FileAccess.get_file_as_string(f), 1.0), OK, "%s rasterises" % f)


func test_new_campaign_leaves_the_end_for_the_start_page() -> void:
	var hq := await _end(true)
	var stage := _stage(hq)
	stage.finish_now()
	stage.new_button.pressed.emit()
	await _frames(2)
	assert_eq(hq.panel_name, "start", "New campaign opens the start page")
	assert_null(RunManager.campaign)
	assert_almost_eq(hq.background.city.atmosphere().state.progress, 0.0, 0.001, "the city's lean is reset")
	await _close(hq)
