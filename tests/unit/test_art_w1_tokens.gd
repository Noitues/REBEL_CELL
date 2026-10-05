extends GutTest
## ART-0 E (S3), ported from art-pass W1 (and WF items 6 and 9): the design-token mechanism.
## Semantic, corp, slice and class colour tokens and their lookups; the HP and Heat scales;
## the WCAG contrast helper; the type scale, its text-scale arithmetic and tracking per
## step; spacing tokens; the body face and the one MSDF switch. Values are main's where
## main had one (ART-1 sets the v2 palette); the corp pattern painters are not ported
## (ART_BIBLE v2 §2.4 gives each corp a material and crest instead).


# --- Semantic tokens -----------------------------------------------------------------------

func test_semantic_tokens_have_their_values() -> void:
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
	assert_eq(Palette.AUTO.a, 0.0, "AUTO is never drawn")


func test_harm_is_never_the_cell_pink() -> void:
	assert_ne(Palette.HARM, Palette.CELL_PINK, "pink is the brand, never damage")


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


# --- Corporations, slices, class accents ---------------------------------------------------

func test_corp_colours_are_named_constants_with_mains_values() -> void:
	assert_eq(Palette.corp_color(&"solace"), Palette.CORP_SOLACE)
	assert_eq(Palette.corp_color(&"meridian"), Palette.CORP_MERIDIAN)
	assert_eq(Palette.corp_color(&"halcyon"), Palette.CORP_HALCYON)
	assert_eq(Palette.corp_color(&"orbital"), Palette.CORP_ORBITAL)
	assert_eq(Palette.corp_color(&"rebel_cell"), Palette.CORP_REBEL_CELL)
	# main's values until ART-1 moves them to the v2 kits (ART_BIBLE v2 §2.4 palette debt).
	assert_eq(Palette.CORP_SOLACE, Color("#3DFF8B"))
	assert_eq(Palette.CORP_MERIDIAN, Color("#FF8C1A"))
	assert_eq(Palette.CORP_HALCYON, Color("#8C7BFF"))
	assert_eq(Palette.CORP_ORBITAL, Color("#DDE3FF"))
	assert_eq(Palette.CORP_REBEL_CELL, Color("#E8141E"))
	assert_eq(Palette.corp_color(&"nobody"), Palette.NET_CYAN, "unknown corp falls back to the net cyan")


func test_every_corporation_in_content_has_its_own_hue() -> void:
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
		assert_false(roles.has(Palette.corp_color(corp)), "%s is not a UI role hue" % corp)


func test_slice_colours_keep_their_values_through_named_constants() -> void:
	assert_eq(Palette.slice_color(RC.SliceType.SHIM), Palette.CELL_PINK)
	assert_eq(Palette.slice_color(RC.SliceType.OVERFLOW), Palette.CELL_PINK)
	assert_eq(Palette.slice_color(RC.SliceType.DEFRAG), Palette.NET_CYAN)
	assert_eq(Palette.slice_color(RC.SliceType.SANDBOX), Palette.NET_CYAN)
	assert_eq(Palette.slice_color(RC.SliceType.DETOUR), Color("#7BE07B"))
	assert_eq(Palette.slice_color(RC.SliceType.HOTFIX), Palette.SLICE_HOTFIX)
	assert_eq(Palette.slice_color(RC.SliceType.INFECT), Color("#C85AFF"))
	assert_eq(Palette.slice_color(RC.SliceType.TROJAN), Color("#B08CFF"))
	assert_eq(Palette.slice_color(RC.SliceType.NULL), Color("#6A6A6A"))


func test_every_class_in_content_has_its_accent() -> void:
	var dir := DirAccess.open("res://content/classes")
	var n := 0
	for f in dir.get_files():
		if not f.ends_with(".tres"):
			continue
		var cls := load("res://content/classes/" + f) as ClassData
		assert_true(Palette.CLASS_ACCENTS.has(cls.id), "%s has an accent" % cls.id)
		assert_eq(Palette.class_accent(cls.id), Palette.CLASS_ACCENTS[cls.id], "%s accent by lookup" % cls.id)
		n += 1
	assert_eq(n, Palette.CLASS_ACCENTS.size(), "one accent per class, no strays")
	assert_eq(Palette.class_accent(&"breaker"), Palette.CELL_PINK, "the Breaker wears the Cell's pink")
	assert_eq(Palette.class_accent(&"no_such_class"), Palette.CLASS_ACCENT_FALLBACK, "safe fallback")


# --- HP and Heat scales, contrast -------------------------------------------------------------

func test_hp_color_bands() -> void:
	assert_eq(Palette.hp_color(1.0), Palette.GAIN)
	assert_eq(Palette.hp_color(0.5), Palette.GAIN, "50% is still GAIN")
	assert_eq(Palette.hp_color(0.49), Palette.WARN)
	assert_eq(Palette.hp_color(0.25), Palette.WARN, "25% is WARN")
	assert_eq(Palette.hp_color(0.24), Palette.HARM)
	assert_eq(Palette.hp_color(1.0 / 60.0), Palette.HARM, "1/60 is never green")
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
	assert_eq(Palette.heat_color(majors[2] - 1), Palette.HEAT_FLAGGED, "FLAGGED up to the last major")
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


# --- Type scale and tracking -------------------------------------------------------------------

func test_type_steps_have_their_sizes_and_line_heights() -> void:
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
	assert_almost_eq(UiTheme.line_height(13), 1.0, 0.001, "off the scale: 1.0")
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


func test_step_of_finds_the_step_a_size_belongs_to() -> void:
	assert_eq(UiTheme.step_of(15, 1.0), UiTheme.BODY)
	assert_eq(UiTheme.step_of(17, 1.0), UiTheme.BODY, "between steps: the lower one")
	assert_eq(UiTheme.step_of(8, 1.0), UiTheme.CAPTION, "under the floor: caption")
	assert_eq(UiTheme.step_of(UiTheme.font_px_at(UiTheme.HEADING, 1.6), 1.6), UiTheme.HEADING, "at the text scale")


func test_header_label_scales_with_the_text_as_before() -> void:
	# The header kept main's size (22 x the scale); it now reads it from the TITLE step.
	for scale in [0.8, 1.0, 1.6, 2.0]:
		var t := UiTheme.build(scale)
		assert_eq(t.get_font_size(&"font_size", &"HeaderLabel"), roundi(22 * scale), "HeaderLabel at %.1f" % scale)
		assert_eq(t.get_font_size(&"font_size", &"HeaderLabel"), UiTheme.font_px_at(UiTheme.TITLE, scale))


func test_tracking_is_px_per_type_step_and_never_rounds_away() -> void:
	for face in [UiTheme.TRACK_DISPLAY, UiTheme.TRACK_MONO_CAPS]:
		for step in UiTheme.STEPS:
			assert_true((UiTheme.TRACKING_PX[face] as Dictionary).has(step), "%s has a value at %d" % [face, step])
			assert_gte(UiTheme.tracking_step_px(face, step, 1.0), 1, "%s at %d px tracks at least 1 px" % [face, step])
			var prev := 0
			for scale: float in [1.0, 1.6, 2.0]:
				var px := UiTheme.tracking_step_px(face, step, scale)
				assert_gte(px, prev, "grows with the text scale")
				prev = px
	assert_eq(UiTheme.tracking_step_px(UiTheme.TRACK_DISPLAY, UiTheme.LABEL, 1.0), 1, "Anton +1 at label")
	assert_eq(UiTheme.tracking_step_px(UiTheme.TRACK_DISPLAY, UiTheme.TITLE, 1.0), 1, "Anton +1 at title")
	assert_eq(UiTheme.tracking_step_px(UiTheme.TRACK_DISPLAY, UiTheme.HEADING, 1.0), 2, "Anton +2 at heading")
	assert_eq(UiTheme.tracking_step_px(UiTheme.TRACK_MONO_CAPS, UiTheme.CAPTION, 1.0), 1, "mono caps +1 at caption")
	assert_eq(UiTheme.tracking_step_px(UiTheme.TRACK_MONO_CAPS, UiTheme.BODY, 1.0), 1, "mono caps +1 at body")
	assert_eq(UiTheme.tracking_step_px(UiTheme.TRACK_DISPLAY, UiTheme.HEADING, 2.0), 4, "x the text scale")
	assert_eq(UiTheme.tracking_step_px(&"body_plex", UiTheme.BODY, 1.0), 0, "everything else: default")
	# The old fraction rounded to 0 below heading (why the table exists).
	assert_eq(UiTheme.tracking_px(UiTheme.TRACKING_DISPLAY, UiTheme.TITLE), 0)


func test_a_tracked_font_carries_the_step_spacing() -> void:
	var f := UiTheme.tracked(Palette.display(), UiTheme.TRACK_DISPLAY, UiTheme.HEADING, 1.6)
	assert_true(f is FontVariation, "a FontVariation")
	assert_eq((f as FontVariation).spacing_glyph, UiTheme.tracking_step_px(UiTheme.TRACK_DISPLAY, UiTheme.HEADING, 1.6))
	assert_eq(UiTheme.tracked(Palette.display(), UiTheme.TRACK_DISPLAY, UiTheme.HEADING, 1.6), f, "cached")
	assert_eq(UiTheme.tracked(Palette.mono(), &"none", UiTheme.BODY), Palette.mono(), "no tracking: the font itself")
	assert_ne(Palette.display(), f, "the loaded font itself is never changed")


func test_track_label_tracks_anton_and_mono_caps_only() -> void:
	var anton: Label = add_child_autofree(Label.new())
	anton.text = "SEND IT"
	anton.add_theme_font_override(&"font", Palette.display())
	anton.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.HEADING))
	UiTheme.track_label(anton)
	var af := anton.get_theme_font(&"font")
	assert_true(af is FontVariation and (af as FontVariation).base_font == Palette.display(), "Anton is tracked")
	var caps: Label = add_child_autofree(Label.new())
	caps.text = "RAM 6/12"
	caps.add_theme_font_override(&"font", Palette.mono())
	UiTheme.track_label(caps)
	assert_true(caps.get_theme_font(&"font") is FontVariation, "mono in CAPS is tracked")
	caps.text = "Mixed case words"
	UiTheme.track_label(caps)
	assert_eq(caps.get_theme_font(&"font"), Palette.mono(), "mixed-case mono: the tracking comes off")
	var marker: Label = add_child_autofree(Label.new())
	marker.text = "TAG"
	marker.add_theme_font_override(&"font", Palette.marker())
	UiTheme.track_label(marker)
	assert_eq(marker.get_theme_font(&"font"), Palette.marker(), "other faces are left alone")
	UiTheme.track_label(null)


# --- Spacing --------------------------------------------------------------------------------------

func test_spacing_tokens_sit_on_the_4px_grid() -> void:
	assert_eq(UiTheme.SPACING, [4, 8, 16, 24, 32, 48] as Array[int])
	assert_eq([UiTheme.SP_XS, UiTheme.SP_S, UiTheme.SP_M, UiTheme.SP_L, UiTheme.SP_XL, UiTheme.SP_XXL], [4, 8, 16, 24, 32, 48])
	assert_eq(UiTheme.SAFE_MARGIN, 24)
	assert_eq(UiTheme.PANEL_PAD_H, 16)
	assert_eq(UiTheme.PANEL_PAD_V, 12)
	assert_eq(UiTheme.GUTTER, 16)
	for v in UiTheme.SPACING + [UiTheme.SAFE_MARGIN, UiTheme.PANEL_PAD_H, UiTheme.PANEL_PAD_V, UiTheme.GUTTER]:
		assert_eq(v % 4, 0, "%d is a multiple of 4" % v)


# --- MSDF and the body face ----------------------------------------------------------------------

func test_every_face_follows_the_one_msdf_switch() -> void:
	# The switch lives in each face's tracked .import file (a fresh checkout keeps it) and
	# agrees with Palette.FONTS_MSDF (off until ART-1 moves the layouts MSDF changes).
	for path in Palette.FONT_FACES:
		var f := load(path) as FontFile
		assert_not_null(f, path)
		assert_eq(f.multichannel_signed_distance_field, Palette.FONTS_MSDF, "%s follows the MSDF switch" % path)
		assert_eq(f.msdf_pixel_range, Palette.FONTS_MSDF_RANGE, "%s field range covers 6-8 px outlines" % path)
		var imp := FileAccess.get_file_as_string(path + ".import")
		assert_string_contains(imp, "multichannel_signed_distance_field=%s" % str(Palette.FONTS_MSDF).to_lower(), "%s.import carries the switch" % path)
		assert_string_contains(imp, "msdf_pixel_range=%d" % Palette.FONTS_MSDF_RANGE)


func test_body_face_is_plex_with_its_licence() -> void:
	for path in [Palette.FONT_BODY, Palette.FONT_BODY_MEDIUM]:
		var f := load(path) as FontFile
		assert_not_null(f, path)
		assert_string_contains(f.get_font_name(), "Plex", path)
	assert_true(FileAccess.file_exists("res://assets/fonts/OFL_IBMPlexSansCondensed.txt"), "OFL shipped with the face")
	assert_ne(Palette.body(), ThemeDB.fallback_font, "the body face loads")
	assert_ne(Palette.body_medium(), Palette.body(), "two weights")


func test_body_text_variation_serves_label_and_rich_text() -> void:
	for scale in [1.0, 1.6, 2.0]:
		var t := UiTheme.build(scale)
		var px := UiTheme.font_px_at(UiTheme.BODY, scale)
		var v := UiTheme.BODY_TEXT
		assert_eq(t.get_type_variation_base(v), &"Label")
		assert_eq(t.get_font(&"font", v), Palette.body())
		assert_eq(t.get_font(&"normal_font", v), Palette.body())
		assert_eq(t.get_font(&"bold_font", v), Palette.body_medium())
		assert_eq(t.get_font_size(&"font_size", v), px, "Label size at %.1f" % scale)
		assert_eq(t.get_font_size(&"normal_font_size", v), px, "RichTextLabel size at %.1f" % scale)
		# Line height 1.4: the face's own height plus the spacing.
		var line := Palette.body().get_height(px) + t.get_constant(&"line_spacing", v)
		assert_almost_eq(float(line), px * 1.4, 1.0, "body line height at %.1f" % scale)
		assert_eq(t.get_constant(&"line_separation", v), t.get_constant(&"line_spacing", v))
		assert_eq(t.get_color(&"font_color", v), Palette.TEXT_HI)
	var lbl: Label = add_child_autofree(Label.new())
	lbl.theme = UiTheme.build(1.0)
	lbl.theme_type_variation = UiTheme.BODY_TEXT
	assert_eq(lbl.get_theme_font(&"font"), Palette.body(), "a Label picks the variation up")
	var rtl: RichTextLabel = add_child_autofree(RichTextLabel.new())
	rtl.theme = UiTheme.build(1.0)
	rtl.theme_type_variation = UiTheme.BODY_TEXT
	assert_eq(rtl.get_theme_font(&"normal_font"), Palette.body(), "a RichTextLabel picks the variation up")
	assert_eq(rtl.get_theme_font_size(&"normal_font_size"), UiTheme.BODY)


func test_the_shared_theme_is_unchanged_for_mains_screens() -> void:
	# ART-0 E ports the mechanism only: the variations main's screens use keep their look.
	var t := UiTheme.build(1.0)
	assert_eq(t.default_font, Palette.mono(), "system text stays Share Tech Mono")
	assert_eq(t.get_font_size(&"font_size", &"HotButton"), 22, "the Primary keeps its size")
	assert_eq(t.get_font(&"font", &"HeaderLabel"), Palette.mono(), "the header is not tracked yet")
	assert_eq(t.get_color(&"font_color", &"Label"), Palette.TERMINAL_TEXT)
