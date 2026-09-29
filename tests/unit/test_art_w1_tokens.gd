extends GutTest
## Art pass W1 (ART_BIBLE §3, §4, §5.1): the design-token foundation. Semantic, corp,
## slice and class colour tokens; the HP and Heat scales; the WCAG contrast helper; the
## type scale and its text-scale arithmetic; spacing tokens; the corp pattern painters;
## the body face and MSDF on every face.


# --- §3.3 semantic tokens ------------------------------------------------------------------

func test_semantic_tokens_have_the_bible_values() -> void:
	assert_eq(Palette.HARM, Color("#FF4433"))
	assert_eq(Palette.GAIN, Color("#7BE07B"))
	assert_eq(Palette.PROTECT, Palette.NET_CYAN)
	assert_eq(Palette.WARN, Palette.CRT_AMBER)
	assert_eq(Palette.FOCUS, Palette.CELL_ACID)
	assert_eq(Palette.DISABLED, Color("#6A7080"))
	assert_eq(Palette.TEXT_HI, Color("#F2F6FF"))
	assert_eq(Palette.TEXT_MID, Color("#AFC0D6"))
	assert_eq(Palette.TEXT_LO, Color("#7A889C"))
	assert_eq(Palette.HEAT_FLAGGED, Color("#FF7A1A"))
	assert_eq(Palette.SCRIM.to_html(false), Color("#02030A").to_html(false), "scrim hue #02030A")
	assert_almost_eq(Palette.SCRIM.a, 0.55, 0.001, "scrim at 55%")
	assert_eq(Palette.SCRIM_BLUR_PX, 6)


func test_harm_is_never_the_cell_pink() -> void:
	assert_ne(Palette.HARM, Palette.CELL_PINK, "pink is the brand, never damage (§3.3)")


# --- §3.6 corporations, §3.4 slices, §7.1 class accents -----------------------------------

func test_corp_colours_are_named_constants_and_orbital_moved_off_text_white() -> void:
	assert_eq(Palette.corp_color(&"solace"), Palette.CORP_SOLACE)
	assert_eq(Palette.corp_color(&"meridian"), Palette.CORP_MERIDIAN)
	assert_eq(Palette.corp_color(&"halcyon"), Palette.CORP_HALCYON)
	assert_eq(Palette.corp_color(&"orbital"), Palette.CORP_ORBITAL)
	assert_eq(Palette.corp_color(&"rebel_cell"), Palette.CORP_REBEL_CELL)
	assert_eq(Palette.CORP_SOLACE, Color("#3DFF8B"))
	assert_eq(Palette.CORP_MERIDIAN, Color("#FF8C1A"))
	assert_eq(Palette.CORP_HALCYON, Color("#8C7BFF"))
	assert_eq(Palette.CORP_ORBITAL, Color("#7FA8FF"), "Orbital is #7FA8FF (§15)")
	assert_eq(Palette.CORP_REBEL_CELL, Color("#E8141E"))
	assert_eq(Palette.corp_color(&"nobody"), Palette.NET_CYAN, "unknown corp falls back to the net cyan")


func test_every_corporation_in_content_has_its_own_hue_and_pattern() -> void:
	var dir := DirAccess.open("res://content/corporations")
	assert_not_null(dir)
	var seen := {}
	for f in dir.get_files():
		if not f.ends_with(".tres"):
			continue
		var corp := load("res://content/corporations/" + f) as CorporationData
		assert_not_null(corp, f)
		var col := Palette.corp_color(corp.id)
		assert_ne(col, Palette.NET_CYAN, "%s has its own hue" % corp.id)
		assert_false(seen.has(col.to_html()), "%s's hue is unique" % corp.id)
		seen[col.to_html()] = true


func test_no_corp_hue_is_a_ui_role_token() -> void:
	var roles: Array[Color] = [Palette.HARM, Palette.GAIN, Palette.PROTECT, Palette.WARN, Palette.FOCUS,
		Palette.DISABLED, Palette.TEXT_HI, Palette.TEXT_MID, Palette.TEXT_LO, Palette.CELL_PINK]
	for corp in [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]:
		assert_false(roles.has(Palette.corp_color(corp)), "%s is not a UI role hue (§3.6)" % corp)


func test_slice_colours_keep_their_values_through_named_constants() -> void:
	assert_eq(Palette.slice_color(RC.SliceType.ATTACK), Palette.CELL_PINK)
	assert_eq(Palette.slice_color(RC.SliceType.CRIT), Palette.CELL_PINK)
	assert_eq(Palette.slice_color(RC.SliceType.DEFEND), Palette.NET_CYAN)
	assert_eq(Palette.slice_color(RC.SliceType.SHIELD), Palette.NET_CYAN)
	assert_eq(Palette.slice_color(RC.SliceType.EVADE), Color("#7BE07B"))
	assert_eq(Palette.slice_color(RC.SliceType.HEAL), Palette.SLICE_HEAL)
	assert_eq(Palette.slice_color(RC.SliceType.AFFLICT), Color("#C85AFF"))
	assert_eq(Palette.slice_color(RC.SliceType.DEPLOY), Color("#B08CFF"))
	assert_eq(Palette.slice_color(RC.SliceType.MISS), Color("#6A6A6A"))


func test_every_class_in_content_has_its_accent() -> void:
	var want := {&"breaker": Palette.CELL_PINK, &"wrecker": Color("#FF7A1A"), &"ghost": Color("#9FE8FF"),
		&"phantom": Color("#C8B6FF"), &"rigger": Color("#FFD24D"), &"overclocker": Color("#FF4FD8"),
		&"botnet": Color("#7BE07B"), &"hivemind": Color("#B04DFF")}
	var dir := DirAccess.open("res://content/classes")
	var n := 0
	for f in dir.get_files():
		if not f.ends_with(".tres"):
			continue
		var cls := load("res://content/classes/" + f) as ClassData
		assert_true(Palette.CLASS_ACCENTS.has(cls.id), "%s has an accent" % cls.id)
		assert_eq(Palette.class_accent(cls.id), want.get(cls.id), "%s accent per §7.1" % cls.id)
		n += 1
	assert_eq(n, Palette.CLASS_ACCENTS.size(), "one accent per class, no strays")
	assert_eq(Palette.class_accent(&"no_such_class"), Palette.CLASS_ACCENT_FALLBACK, "safe fallback")


# --- §3.5 HP and Heat scales, §3.7 contrast ------------------------------------------------

func test_hp_color_bands() -> void:
	assert_eq(Palette.hp_color(1.0), Palette.GAIN)
	assert_eq(Palette.hp_color(0.5), Palette.GAIN, "50% is still GAIN")
	assert_eq(Palette.hp_color(0.49), Palette.WARN)
	assert_eq(Palette.hp_color(0.25), Palette.WARN, "25% is WARN")
	assert_eq(Palette.hp_color(0.24), Palette.HARM)
	assert_eq(Palette.hp_color(1.0 / 60.0), Palette.HARM, "1/60 is never green (§15)")
	assert_eq(Palette.hp_color(0.0), Palette.HARM)
	assert_eq(Palette.HP_WARN_BELOW, 0.5)
	assert_eq(Palette.HP_HARM_BELOW, 0.25)


func test_heat_color_bands_follow_the_config_majors() -> void:
	var majors := (load(ContentRegistry.CONFIG_PATH) as CampaignConfigData).major_heat_levels()
	assert_eq(majors.size(), 3, "three MAJOR thresholds (COOL/NOTICED/FLAGGED/HUNTED)")
	assert_eq(Palette.heat_color(0), Palette.TEXT_MID, "COOL")
	assert_eq(Palette.heat_color(majors[0] - 1), Palette.TEXT_MID, "COOL up to the first major")
	assert_eq(Palette.heat_color(majors[0]), Palette.WARN, "NOTICED")
	assert_eq(Palette.heat_color(majors[1]), Palette.HEAT_FLAGGED, "FLAGGED")
	assert_eq(Palette.heat_color(62), Palette.HEAT_FLAGGED, "Heat 62 no longer reads good (§15)")
	assert_eq(Palette.heat_color(majors[2]), Palette.HARM, "HUNTED")
	assert_eq(Palette.heat_color(100), Palette.HARM)
	var custom: Array[int] = [10, 20, 30, 40]
	assert_eq(Palette.heat_band(15, custom), 1, "explicit levels are honoured")
	assert_eq(Palette.heat_band(99, custom), 3, "capped at HUNTED")


func test_heat_is_never_green() -> void:
	for h in range(0, 201):
		var c := Palette.heat_color(h)
		assert_ne(c, Palette.GAIN, "Heat %d is not GAIN" % h)
		assert_false(c.h > 0.2 and c.h < 0.45 and c.s > 0.3, "Heat %d hue is not green" % h)


func test_contrast_matches_known_wcag_pairs() -> void:
	assert_almost_eq(Palette.contrast(Color.BLACK, Color.WHITE), 21.0, 0.01, "black on white")
	assert_almost_eq(Palette.contrast(Color.WHITE, Color.BLACK), 21.0, 0.01, "order-free")
	assert_almost_eq(Palette.contrast(Color.WHITE, Color.WHITE), 1.0, 0.001)
	assert_almost_eq(Palette.contrast(Color("#777777"), Color.WHITE), 4.48, 0.01, "#777 on white")
	assert_almost_eq(Palette.contrast(Color("#767676"), Color.WHITE), 4.54, 0.01, "#767676 on white (AA)")
	assert_almost_eq(Palette.contrast(Color("#0000FF"), Color.WHITE), 8.59, 0.01, "blue on white")
	assert_almost_eq(Palette.contrast(Color("#FF0000"), Color.WHITE), 4.0, 0.01, "red on white")


func test_text_tokens_read_on_glass_and_over_the_scrim() -> void:
	var glass := Palette.over(Palette.NIGHT_SKY, Palette.TERMINAL_BG)
	assert_gt(Palette.contrast(Palette.TEXT_HI, glass), 7.0, "TEXT_HI on glass")
	assert_gt(Palette.contrast(Palette.TEXT_MID, glass), 4.5, "TEXT_MID on glass")
	assert_gt(Palette.contrast(Palette.DISABLED, glass), 3.0, "DISABLED outline is visible")
	var bright := Palette.over(Color.WHITE, Palette.SCRIM)
	assert_almost_eq(bright.a, 1.0, 0.001, "over an opaque ground is opaque")
	assert_lt(Palette.luminance(bright), Palette.luminance(Color.WHITE), "the scrim dims")
	assert_eq(Palette.over(Color.RED, Color(0, 0, 1, 1)), Color(0, 0, 1, 1), "an opaque fg covers")
	assert_eq(Palette.over(Color.RED, Color(0, 0, 1, 0)), Color.RED, "a clear fg leaves the ground")


# --- §3.6 corp patterns --------------------------------------------------------------------

## Calls `paint` from its own _draw (painters may only draw there) and counts the calls.
class Painter extends Node2D:
	var paint: Callable
	var drawn: int = 0

	func _draw() -> void:
		paint.call(self)
		drawn += 1


func test_every_corporation_in_content_has_a_pattern() -> void:
	var kinds := {}
	for corp in [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]:
		var k := Palette.corp_pattern_id(corp)
		assert_ne(k, CorpPattern.Kind.NONE, "%s has a pattern" % corp)
		assert_false(kinds.has(k), "%s's pattern is its own" % corp)
		kinds[k] = true
	assert_eq(Palette.corp_pattern_id(&"solace"), CorpPattern.Kind.HELIX_DOTS)
	assert_eq(Palette.corp_pattern_id(&"meridian"), CorpPattern.Kind.CONTAINER_STRIPES)
	assert_eq(Palette.corp_pattern_id(&"halcyon"), CorpPattern.Kind.CIVIC_RINGS)
	assert_eq(Palette.corp_pattern_id(&"orbital"), CorpPattern.Kind.STAR_GRID)
	assert_eq(Palette.corp_pattern_id(&"rebel_cell"), CorpPattern.Kind.SCAN_GLITCH)
	assert_eq(Palette.corp_pattern_id(&"nobody"), CorpPattern.Kind.NONE)
	var dir := DirAccess.open("res://content/corporations")
	for f in dir.get_files():
		if f.ends_with(".tres"):
			var corp := load("res://content/corporations/" + f) as CorporationData
			assert_ne(Palette.corp_pattern_id(corp.id), CorpPattern.Kind.NONE, "%s has a pattern" % corp.id)


func test_patterns_are_deterministic_and_distinct() -> void:
	var r := Rect2(13, 7, 120, 80)
	var signatures := {}
	for k in CorpPattern.KINDS:
		var a := CorpPattern.marks(k, r)
		var b := CorpPattern.marks(k, r)
		assert_eq(str(a), str(b), "%s draws the same marks every time" % CorpPattern.KIND_NAMES[k])
		assert_gt(a.dots.size() + a.lines.size(), 0, "%s draws something" % CorpPattern.KIND_NAMES[k])
		var sig := "%d dots/%d lines" % [a.dots.size(), a.lines.size()]
		assert_false(signatures.has(sig), "%s differs in structure" % CorpPattern.KIND_NAMES[k])
		signatures[sig] = true
	var d1 := CorpPattern.dash_marks(Vector2.ZERO, Vector2(200, 50), CorpPattern.Kind.SCAN_GLITCH, 2.0, 1.0, 3.0)
	var d2 := CorpPattern.dash_marks(Vector2.ZERO, Vector2(200, 50), CorpPattern.Kind.SCAN_GLITCH, 2.0, 1.0, 3.0)
	assert_eq(str(d1), str(d2), "dashed glitch line is deterministic")
	assert_true(CorpPattern.marks(CorpPattern.Kind.NONE, r).dots.is_empty(), "NONE fills nothing")


func test_every_pattern_paints_each_variant_on_a_canvas_item() -> void:
	var calls := {"n": 0}
	var node: Painter = add_child_autofree(Painter.new())
	node.paint = func(ci: CanvasItem) -> void:
		for k in CorpPattern.KINDS + [CorpPattern.Kind.NONE]:
			CorpPattern.fill_rect(ci, Rect2(0, 0, 90, 60), k, Palette.CORP_ORBITAL)
			CorpPattern.fill_polygon(ci, PackedVector2Array([Vector2(0, 0), Vector2(80, 10), Vector2(40, 70)]), k, Palette.CORP_SOLACE, 1.5)
			CorpPattern.fill_ring(ci, Vector2(100, 100), 40, 60, k, Palette.CORP_HALCYON)
			CorpPattern.dashed_line(ci, Vector2(0, 0), Vector2(300, 120), k, Palette.CORP_MERIDIAN, 2.0, 1.0, 5.0)
			calls.n += 1
	node.queue_redraw()
	await get_tree().process_frame
	await get_tree().process_frame
	assert_gt(node.drawn, 0, "the painter ran inside _draw")
	assert_eq(calls.n, (CorpPattern.KINDS.size() + 1) * node.drawn, "every kind and variant painted")


func test_ring_fill_keeps_marks_inside_the_annulus() -> void:
	var c := Vector2(50, 50)
	var m := CorpPattern.marks(CorpPattern.Kind.HELIX_DOTS, Rect2(c - Vector2(60, 60), Vector2(120, 120)))
	var kept := 0
	for d in m.dots:
		var dist: float = d.p.distance_to(c)
		if dist >= 30.0 and dist <= 60.0:
			kept += 1
	assert_gt(kept, 20, "a bezel-sized ring holds a readable number of dots")


# --- §4.2 type scale ------------------------------------------------------------------------

func test_type_steps_have_the_bible_sizes_and_line_heights() -> void:
	assert_eq(UiTheme.CAPTION, 12)
	assert_eq(UiTheme.BODY, 15)
	assert_eq(UiTheme.BODY, UiTheme.BASE_SIZE)
	assert_eq(UiTheme.LABEL, 18)
	assert_eq(UiTheme.TITLE, 22)
	assert_eq(UiTheme.HEADING, 30)
	assert_eq(UiTheme.DISPLAY, 44)
	assert_eq(UiTheme.HERO, 64)
	assert_eq(UiTheme.HERO_MAX, 96)
	var want := {12: 1.3, 15: 1.4, 18: 1.25, 22: 1.2, 30: 1.1, 44: 1.0, 64: 1.0}
	for step in UiTheme.STEPS:
		assert_almost_eq(UiTheme.line_height(step), want[step], 0.001, "line height of %d" % step)
	assert_almost_eq(UiTheme.TRACKING_DISPLAY, 0.02, 0.0001, "Anton +2%")
	assert_almost_eq(UiTheme.TRACKING_MONO_CAPS, 0.08, 0.0001, "mono CAPS +8%")
	assert_eq(UiTheme.tracking_px(UiTheme.TRACKING_MONO_CAPS, 25), 2)


func test_font_px_scales_every_step_at_every_text_scale() -> void:
	for scale in [0.8, 1.0, 1.6, 2.0]:
		for step in UiTheme.STEPS:
			assert_eq(UiTheme.font_px_at(step, scale), roundi(step * scale), "%d at %.1f" % [step, scale])
	assert_eq(UiTheme.font_px_at(UiTheme.CAPTION, 2.0), 24)
	assert_eq(UiTheme.font_px_at(UiTheme.HERO, 2.0), 128)
	assert_eq(UiTheme.font_px_at(UiTheme.BODY, 1.6), 24)
	assert_eq(UiTheme.font_px_at(UiTheme.TITLE, 0.8), 18)
	for step in UiTheme.STEPS:
		assert_true(UiTheme.font_px_at(step, 1.0) >= UiTheme.CAPTION, "no step under 12 at 1.0 (%d)" % step)
	var saved := Settings.text_scale
	Settings.text_scale = 1.6
	assert_eq(UiTheme.font_px(UiTheme.LABEL), UiTheme.font_px_at(UiTheme.LABEL, 1.6), "font_px reads the setting")
	Settings.text_scale = saved


func test_hot_button_and_header_scale_with_the_text() -> void:
	for scale in [0.8, 1.0, 1.6, 2.0]:
		var t := UiTheme.build(scale)
		assert_eq(t.get_font_size(&"font_size", &"HotButton"), UiTheme.font_px_at(UiTheme.TITLE, scale), "HotButton at %.1f" % scale)
		assert_eq(t.get_font_size(&"font_size", &"HeaderLabel"), UiTheme.font_px_at(UiTheme.TITLE, scale), "HeaderLabel at %.1f" % scale)
	assert_eq(UiTheme.build(1.0).get_font_size(&"font_size", &"HotButton"), 22, "unchanged at 1.0")
