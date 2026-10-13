extends GutTest
## M14 12Q-WORDS (DECISIONS "M14 12Q-WORDS"; QA matrix audit docs/handoff/m14_12q/qa_matrix_audit.md):
## L40 the fight's subtitle box pages by its room (the outcome's line whole at 1.0 / 1.6 / 2.0);
## L41 the campaign end's DISPATCH band holds two lines; L48 VOICE ONLY // NO FEED stands whole in
## its feed; L54 the route key wraps instead of being scaled down; L59 a terminal window's glass
## covers the whole window (its header inset from the edge) and its title follows the text size;
## L61 OURS NOW stands clear of the subtitle box; L65 the lint leads: paper / manila soft ink at
## 4.5:1, SAVED, CONNECTING and the fight banner on the type scale, the address never under the floor.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const COMBAT := preload("res://scripts/ui/combat_scene.gd")
const NETRUN_SCRIPT := preload("res://scripts/ui/netrun_scene.gd")
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
## The won fight's operative line (the audit's "Perfect. Tell the board the …").
const VICTORY_LINE := "Perfect. Tell the board the invoice is in the mail."

var _scale: float = 1.0
var _reduce: bool = false
## The last netrun's holder (freed after each scale).
var _holder: Control = null


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_m14_12q_words"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
		Fx.apply_settings()
	Dialogue.clear()
	Dialogue.dock_default()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


## A netrun on its route at text size `scale`.
func _netrun(scale: float) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	_holder = holder
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames()
	return scene


## A won fight, its outcome landed (the review pack's combat_victory).
func _won_fight(scale: float) -> Control:
	var scene := await _netrun(scale)
	scene.enter_node(RunManager.netrun.available_nodes()[0])
	await _frames(5)
	var combat: Control = scene.combat_scene
	assert_not_null(combat, "x%.1f: a fight" % scale)
	scene._demo_combat_end("win")
	for i in 300:
		await get_tree().process_frame
		if not is_instance_valid(combat) or combat.engine.state().outcome != CombatState.Outcome.NONE:
			break
	await _frames(2)
	combat.skip_motion()
	await _frames(5)
	return combat


## The WCAG relative luminance (sRGB channels linearised).
static func _lum(c: Color) -> float:
	var l := c.srgb_to_linear()
	return 0.2126 * l.r + 0.7152 * l.g + 0.0722 * l.b


static func _wcag(a: Color, b: Color) -> float:
	var la := _lum(a)
	var lb := _lum(b)
	return (maxf(la, lb) + 0.05) / (minf(la, lb) + 0.05)


static func _on_steps(px: int, scale: float) -> bool:
	for st in UiTheme.STEPS:
		if UiTheme.font_px_at(st, scale) == px:
			return true
	return false


# --- L40 / L61: the fight's subtitle box and OURS NOW -------------------------------------------

func test_the_fight_box_pages_by_its_room_and_ours_now_stands_clear_of_it() -> void:
	for scale in TestScope.scales([1.0, 1.6]):
		var combat := await _won_fight(scale)
		var dock: Rect2 = combat._subtitle_dock
		assert_true(dock.has_area(), "x%.1f: the box's rect is kept" % scale)
		assert_eq(Dialogue.dock_lines, maxi(COMBAT.SUBTITLE_LINES, Dialogue.page_lines_in(dock)), "x%.1f: pages hold the box's room" % scale)
		assert_gte(Dialogue.dock_lines, COMBAT.SUBTITLE_LINES, "x%.1f: never fewer lines than before" % scale)
		# The won fight's operative line, in this box: one page, whole, and inside the box.
		Dialogue.clear()
		Dialogue.say(RC.Voice.STREET_MERC, VICTORY_LINE, 0.0, &"", true, "", &"breaker")
		Dialogue.finish_typing()
		await _frames(2)
		var shown := Dialogue.text_label.get_parsed_text()
		assert_false(shown.ends_with(Dialogue.CONTINUED_MARK), "x%.1f: the line is not cut to a next page: '%s'" % [scale, shown])
		assert_eq(Dialogue.current_text(), VICTORY_LINE, "x%.1f: the whole line on one page" % scale)
		assert_lte(Dialogue._page_height(VICTORY_LINE), Dialogue._dock_text_room() + 0.5, "x%.1f: the page fits the box" % scale)
		# OURS NOW (the won backdrop's pencil) is clear of the box.
		var ours: GreasePencilWord = combat.arena_backdrop.ours_now()
		if ours.visible:
			assert_false(ours.global_rect().intersects(dock), "x%.1f: OURS NOW clear of the subtitle box: %s vs %s" % [scale, ours.global_rect(), dock])
		_holder.queue_free()
		await _frames(3)


func test_page_lines_in_counts_the_lines_under_the_name_row() -> void:
	for scale in TestScope.scales(SCALES):
		Settings.set_text_scale(scale)
		var h := (COMBAT.SUBTITLE_CHROME_PX + COMBAT.SUBTITLE_LINES * COMBAT.SUBTITLE_LINE_PX) * scale
		var n := Dialogue.page_lines_in(Rect2(0, 0, 300, h))
		var line := UiTheme.line_px(Palette.mono(), roundi(Dialogue.TEXT_FONT_SIZE * scale))
		assert_gte(n, COMBAT.SUBTITLE_LINES, "x%.1f: at least the box's nominal lines" % scale)
		assert_lte(n * line, h - Dialogue.BAR_PADDING, "x%.1f: the lines fit the box under its padding" % scale)
	assert_eq(Dialogue.page_lines_in(Rect2(0, 0, 300, 4)), 1, "at least one line")


# --- L41: the campaign end's DISPATCH band -------------------------------------------------------

func test_the_campaign_end_gives_dispatch_a_two_line_band() -> void:
	for outcome in [CampaignState.Outcome.WON, CampaignState.Outcome.LOST]:
		for scale in TestScope.scales(SCALES):
			Settings.set_text_scale(scale)
			RunManager.new_campaign(1)
			var hq: Control = load(HQ).instantiate()
			add_child_autofree(hq)
			hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			await _frames(2)
			assert_eq(hq.subtitle_strip.lines, 1, "x%.1f: one line on the HQ" % scale)
			DemoSetup.end_campaign(RunManager.campaign, outcome)
			hq.show_end()
			Dialogue.finish_typing()
			await _frames(4)
			var tag := "%s x%.1f" % ["won" if outcome == CampaignState.Outcome.WON else "lost", scale]
			assert_eq(hq.subtitle_strip.lines, hq.END_SUBTITLE_LINES, "%s: the verdict's band holds two lines" % tag)
			assert_true(Dialogue.is_showing(), "%s: DISPATCH says the verdict" % tag)
			var shown := Dialogue.text_label.get_parsed_text()
			assert_false(shown.ends_with(Dialogue.CONTINUED_MARK), "%s: the verdict whole, not cut to a next page: '%s'" % [tag, shown])
			hq.show_hq()
			await _frames(2)
			assert_eq(hq.subtitle_strip.lines, 1, "%s: back to one line off the end pages" % tag)
			hq.queue_free()
			Dialogue.clear()
			RunManager.reset()
			await _frames(2)


# --- L48: VOICE ONLY // NO FEED --------------------------------------------------------------------

func test_voice_only_words_stand_whole_inside_the_feed() -> void:
	for scale in TestScope.scales(SCALES):
		var os := minf(scale, ShopItem.OBJECT_MAX_SCALE)
		var box: Vector2 = NETRUN_SCRIPT.EVENT_CAM * os
		if scale >= NETRUN_SCRIPT.EVENT_FEED_BELOW:
			box = Vector2(NETRUN_SCRIPT.EVENT_CAM_STRIP_W, NETRUN_SCRIPT.EVENT_CAM_STRIP_H) * minf(scale, NETRUN_SCRIPT.EVENT_CAM_STRIP_GROW)
		var font := Palette.mono()
		var fs := roundi(CamFeed.CAPTION_PX * os)
		var inner := Rect2(Vector2.ZERO, box).grow(-CamFeed.FRAME * 2.0)
		var lines := CamFeed.voice_lines(tr("VOICE ONLY // NO FEED"), font, fs, inner.size.x)
		assert_eq(" ".join(lines), tr("VOICE ONLY // NO FEED"), "x%.1f: every word, in order" % scale)
		if lines.size() == 2:
			assert_eq(lines[0], "VOICE ONLY //", "x%.1f: broken at the separator" % scale)
		for l in lines:
			assert_lte(font.get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, inner.size.x, "x%.1f: '%s' inside the frame" % [scale, l])
		assert_lte(UiTheme.line_px(font, fs) * lines.size() + CamFeed.VOICE_PAD, inner.size.y, "x%.1f: the lines inside the frame's height" % scale)
		assert_gte(fs, CamFeed.CAPTION_PX, "x%.1f: never smaller than at 1.0" % scale)
	assert_eq(CamFeed.voice_lines("VOICE ONLY // NO FEED", Palette.mono(), 13, 1000.0).size(), 1, "one line when it fits")


# --- L54: the route key wraps, never scaled ------------------------------------------------------

func test_the_route_key_follows_the_text_size_and_wraps_instead_of_scaling() -> void:
	for scale in TestScope.scales(SCALES):
		var scene := await _netrun(scale)
		await _frames(4)
		var legend: RouteLegend = scene.route_legend
		assert_eq(legend.scale, Vector2.ONE, "x%.1f: never scaled down" % scale)
		assert_true(legend.strip is HFlowContainer, "x%.1f: a flow (it wraps)" % scale)
		var row := legend.get_parent() as Control
		assert_lte(legend.size.x, row.size.x + 0.5, "x%.1f: within its row" % scale)
		assert_true(SCREEN.grow(1.0).encloses(legend.get_global_rect()), "x%.1f: on screen: %s" % [scale, legend.get_global_rect()])
		for l in legend.find_children("*", "Label", true, false):
			if (l as Label).text != "":
				assert_eq((l as Label).get_theme_font_size(&"font_size"), roundi(RouteLegend.FONT * scale), "x%.1f: '%s' at the text size" % [scale, (l as Label).text])
		assert_gte(row.custom_minimum_size.y, legend.size.y - 0.5, "x%.1f: the row holds every line of the key" % scale)
		_holder.queue_free()
		await _frames(2)


func test_a_narrow_route_key_wraps_to_more_rows() -> void:
	if TestScope.deferred():
		pending(TestScope.REASON)
		return
	Settings.set_text_scale(2.0)
	var legend: RouteLegend = add_child_autofree(RouteLegend.new(RouteLegend.ORDER))
	await _frames()
	var one := legend.one_row_width()
	legend.size = Vector2(one, 0.0)
	await _frames(2)
	var tall_one := legend.get_combined_minimum_size().y
	legend.size = Vector2(one * 0.55, 0.0)
	await _frames(3)
	assert_gt(legend.get_combined_minimum_size().y, tall_one + 1.0, "half the room: more rows")
	assert_eq(legend.scale, Vector2.ONE)


# --- L59: a terminal window's glass and header ----------------------------------------------------

func test_a_terminal_windows_glass_covers_it_and_its_title_follows_the_text_size() -> void:
	for scale in TestScope.scales(SCALES):
		Settings.set_text_scale(scale)
		var w: TerminalWindow = add_child_autofree(TerminalWindow.new("RAID // COLLECTIONS: FIRST NOTICE", Palette.CORP_SOLACE))
		w.body.add_child(Label.new())
		w.size = Vector2(520, 0)
		await _frames(2)
		var glass := w.backing()
		assert_not_null(glass, "x%.1f: the kit glass" % scale)
		assert_eq(glass.get_rect(), Rect2(Vector2.ZERO, w.size), "x%.1f: over the whole window" % scale)
		var head := w.find_child("TerminalTitle", true, false) as Label
		var sb := w.get_theme_stylebox("panel")
		var inset := head.get_global_rect().position.x - glass.get_global_rect().position.x
		assert_gte(inset, sb.get_margin(SIDE_LEFT) - 0.5, "x%.1f: the header inset from the glass's edge (%.1f px)" % [scale, inset])
		assert_eq(head.get_theme_font_size(&"font_size"), UiTheme.font_px(TerminalWindow.TITLE_STEP), "x%.1f: the title at the text size" % scale)
		assert_true(_on_steps(head.get_theme_font_size(&"font_size"), scale), "x%.1f: on the type scale" % scale)
		assert_lte(w.size.x, 520.0 + 0.5, "x%.1f: a long title wraps, the window keeps its width" % scale)
		w.free()


# --- L65: the lint leads ---------------------------------------------------------------------------

func test_paper_and_manila_soft_ink_read_at_four_and_a_half_to_one() -> void:
	for stock in [Palette.PAPER, Palette.PAPER_ALT]:
		assert_gte(_wcag(Palette.PAPER_INK_SOFT, stock), 4.5, "soft ink on %s" % stock.to_html(false))
	# The case file's manila (END_MANILA, and the darker grain the lint measured, #DBC08A).
	for manila in [Palette.END_MANILA, Color("#DBC08A")]:
		assert_gte(_wcag(Palette.MANILA_FIELD_INK, manila), 4.5, "field ink on %s" % manila.to_html(false))
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/raid_paper.gd")
	assert_false(src.contains("Palette.INK.lerp(Palette.PAPER, 0.42)"), "the sub line uses the token")
	assert_false(src.contains("Palette.INK.lerp(Palette.PAPER, 0.5)"), "the footer uses the token")


func test_saved_connecting_and_the_fight_banner_are_on_the_type_scale() -> void:
	for scale in TestScope.scales(SCALES):
		Settings.set_text_scale(scale)
		assert_true(_on_steps(UiTheme.font_px(Fx.SAVED_FONT), scale), "x%.1f: SAVED" % scale)
		assert_true(_on_steps(UiTheme.font_px(Fx.CONNECT_FONT), scale), "x%.1f: CONNECTING" % scale)
		assert_gte(UiTheme.font_px(Fx.SAVED_FONT), 20, "x%.1f: SAVED never smaller than before" % scale)
		var title: int = COMBAT.banner_title_px()
		assert_true(_on_steps(title, scale), "x%.1f: the banner title (%d px) on the type scale" % [scale, title])
		assert_lte(title, COMBAT.BANNER_TITLE_MAX_PX, "x%.1f: never past its cap" % scale)
		assert_gte(title, 20, "x%.1f: never smaller than at 1.0 before" % scale)
		for step in COMBAT.ADDRESS_STEPS:
			assert_gte(UiTheme.font_px(step), roundi(UiTheme.CAPTION * scale), "x%.1f: the address never under the floor" % scale)


func test_the_fight_address_keeps_the_outcome_word_and_the_floor() -> void:
	for scale in TestScope.scales([1.6, 2.0]):
		var combat := await _won_fight(scale)
		var address := combat._address as Label
		var fs := address.get_theme_font_size(&"font_size")
		assert_gte(fs, roundi(UiTheme.CAPTION * scale), "x%.1f: the address at or over the floor (%d px)" % [scale, fs])
		assert_true(_on_steps(fs, scale), "x%.1f: on the type scale" % scale)
		assert_string_contains(address.text, combat._status.text, "x%.1f: the outcome's word stays" % scale)
		_holder.queue_free()
		await _frames(3)
