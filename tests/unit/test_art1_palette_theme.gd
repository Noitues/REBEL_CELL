extends GutTest
## ART-1 1A: palette v2 (ART_BIBLE v2 §2.1-2.8, §2.10), the faces (§2.9) and the v2 theme
## type variations (§6.4). The token table below is the bible's tables, row by row.


## Every §2 row with a value: Palette constant name -> the bible's hex (alpha where given).
const TOKEN_TABLE := {
	# §2.1 brand and neutral
	&"CELL_PINK": "#FF3DA8", &"CELL_ACID": "#D4FF00", &"FOCUS": "#D4FF00", &"CELL_TURF": "#D4FF00",
	&"NET_CYAN": "#5CE1FF", &"PROTECT": "#5CE1FF", &"TERMINAL_TEXT": "#CFF6FF", &"INK": "#111111",
	&"GLYPH_OUTLINE": "#0C0A16", &"PAPER": "#F2EEE4", &"PAPER_ALT": "#E9E4D6", &"CRT_AMBER": "#FFB000",
	&"WARN": "#FFB000", &"RESIST_GOLD": "#FFD24D", &"NEON_VIOLET": "#B04DFF",
	# §2.2 semantic and new
	&"HARM": "#FF4433", &"GAIN": "#7BE07B", &"HARM_INK": "#AB2E22", &"GAIN_INK": "#396739",
	&"DISABLED": "#6A7080", &"TEXT_HI": "#F2F6FF", &"TEXT_MID": "#AFC0D6", &"TEXT_LO": "#7A889C",
	&"PENCIL_PLAN": "#FFE200", &"PENCIL_THREAT": "#FF1C2C", &"HEAT_B": "#CE5412",
	&"RING_AVAILABLE": "#FF8C1A", &"RING_UNAVAILABLE": "#F2F6FF",
	# §2.3 slices
	&"SLICE_HOTFIX": "#7BE07B", &"SLICE_INFECT": "#C85AFF", &"SLICE_TROJAN": "#B08CFF", &"SLICE_NULL": "#6A6A6A",
	# §2.4 corp kits (round 18)
	&"CORP_MERIDIAN": "#FF8C1A", &"CORP_SOLACE": "#96FF46", &"CORP_HALCYON": "#B06EFF",
	&"CORP_ORBITAL": "#CDF0FF", &"CORP_REBEL_CELL": "#E8141E", &"CORP_MERIDIAN_2": "#FF2E28",
	&"CORP_SOLACE_2": "#FF4696", &"CORP_HALCYON_2": "#FFAA28", &"CORP_ORBITAL_2": "#FFFFFF",
	&"CORP_REBEL_CELL_2": "#FFAAAC",
	# §2.6 Daemon families (round 34) and §2.7 rarity
	&"DAEMON_NULL": "#EC303A", &"DAEMON_ACTION": "#BA92FF", &"DAEMON_PERFECT": "#FFD640",
	&"DAEMON_TURN": "#5CE1FF", &"DAEMON_RUN": "#96FF6E", &"DAEMON_HEAT": "#FF8C3C",
	&"RARITY_COMMON": "#D6DEEC", &"RARITY_UNCOMMON": "#5CE1FF", &"RARITY_RARE": "#FFD640",
	# §2.8 Heat (five bands: PURGE keeps HUNTED's look)
	&"HEAT_COOL": "#AFC0D6", &"HEAT_NOTICED": "#FFB000", &"HEAT_FLAGGED": "#FF7A1A",
	&"HEAT_HUNTED": "#FF4433", &"HEAT_PURGE": "#FF4433",
	# §2.10 state chrome
	&"SELECTED": "#5CE1FF", &"STICKER_SAFE": "#FFEE60", &"STICKER_SAFE_LOW": "#FFB60E",
	&"STICKER_COMMIT": "#FF3DA8", &"LIVE_NUMBER_RIM": "#06060A",
}

## §2.5 class accents (round 22 `class_colours_v2`).
const CLASS_TABLE := {
	&"breaker": "#FF3DA8", &"wrecker": "#FF6E32", &"ghost": "#5BE0FF", &"phantom": "#DBC1FF",
	&"rigger": "#7AE07A", &"overclocker": "#FFB040", &"botnet": "#6072FF", &"hivemind": "#C659FF",
}


func _token(name: StringName) -> Color:
	var consts := (Palette as Script).get_script_constant_map()
	assert_true(consts.has(name), "Palette has %s" % name)
	return consts.get(name, Color.TRANSPARENT)


func test_every_bible_row_has_a_token_with_its_value() -> void:
	for name: StringName in TOKEN_TABLE:
		var c := _token(name)
		assert_eq(c.to_html(false).to_upper(), String(TOKEN_TABLE[name]).trim_prefix("#"), "%s is the bible's %s" % [name, TOKEN_TABLE[name]])
	for id: StringName in CLASS_TABLE:
		assert_eq(Palette.class_accent(id).to_html(false).to_upper(), String(CLASS_TABLE[id]).trim_prefix("#"), "%s accent" % id)
	# Alpha rows: terminal glass rgba(5,13,28,.92-.95), edge #5CE1FF @ 75-80 %, scrim, pencil shadow.
	assert_eq(Palette.TERMINAL_BG.to_html(false).to_upper(), "050D1C", "terminal glass rgb(5,13,28)")
	assert_between(Palette.TERMINAL_BG.a, 0.92, 0.95, "terminal glass alpha")
	assert_eq(Palette.TERMINAL_EDGE.to_html(false).to_upper(), "5CE1FF")
	assert_between(Palette.TERMINAL_EDGE.a, 0.75, 0.80, "terminal edge alpha")
	assert_eq(Palette.PENCIL_SHADOW.to_html(false).to_upper(), "060308")
	assert_almost_eq(Palette.PENCIL_SHADOW.a, 0.85, 0.005)
	assert_eq(Palette.RARITY_PIPS, [1, 2, 3] as Array[int], "rarity pips")
	assert_eq(Palette.RARITY_COLORS.size(), Palette.RARITY_PIPS.size())


func test_corp_secondaries_and_lookups() -> void:
	for corp: StringName in [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]:
		assert_ne(Palette.corp_secondary(corp), Palette.corp_color(corp), "%s has a second hue" % corp)
	assert_eq(Palette.corp_secondary(&"nobody"), Palette.TEXT_HI)
	assert_ne(Palette.CORP_SOLACE, Palette.CELL_TURF, "Solace leaf green is not the Cell's lime")
	assert_ne(Palette.CORP_ORBITAL, Palette.TEXT_HI, "Orbital ice is not text white")
	for fam: StringName in Palette.DAEMON_FAMILY_COLORS:
		assert_true([&"perfect", &"null", &"turn", &"action", &"run", &"heat"].has(fam), "family %s" % fam)
	assert_eq(Palette.DAEMON_FAMILY_COLORS.size(), 6, "six trigger families")


func test_five_heat_bands_have_their_tokens_and_purge_its_own() -> void:
	assert_eq(Palette.HEAT_BAND_COLORS, [Palette.HEAT_COOL, Palette.HEAT_NOTICED, Palette.HEAT_FLAGGED,
		Palette.HEAT_HUNTED, Palette.HEAT_PURGE] as Array[Color])
	assert_true((Palette as Script).get_script_constant_map().has(&"HEAT_PURGE"), "PURGE has a token of its own")
	var levels: Array[int] = [25, 50, 75, 100]
	assert_eq(Palette.heat_color(100, levels), Palette.HEAT_PURGE)


func test_meaningful_colours_note_their_greyscale_pair() -> void:
	# §5.1: every token that carries meaning names its non-colour cue.
	for name: StringName in [&"HARM", &"GAIN", &"HARM_INK", &"GAIN_INK", &"PROTECT", &"WARN", &"FOCUS",
			&"DISABLED", &"SELECTED", &"PENCIL_PLAN", &"PENCIL_THREAT", &"RING_AVAILABLE", &"RING_UNAVAILABLE",
			&"RING_CUT", &"HEAT_COOL", &"HEAT_NOTICED", &"HEAT_FLAGGED", &"HEAT_HUNTED", &"HEAT_PURGE",
			&"HEAT_B", &"CORP_*", &"CLASS_ACCENTS", &"SLICE_*", &"DAEMON_*", &"RARITY_*", &"STICKER_SAFE",
			&"STICKER_COMMIT"]:
		assert_true(Palette.PAIRED_WITH.has(name), "%s notes its pair" % name)
		assert_gt(String(Palette.PAIRED_WITH.get(name, "")).length(), 4, "%s: the pair is named" % name)


func test_text_tokens_read_on_their_panels() -> void:
	var glass := Palette.over(Palette.NIGHT_SKY, Palette.TERMINAL_BG)
	var hot := Palette.over(Palette.NIGHT_SKY, Palette.TERMINAL_BG_HOT)
	# typography.jpg: white or cyan on navy glass >= 9:1.
	assert_gt(Palette.contrast(Palette.TEXT_HI, glass), 9.0, "TEXT_HI on glass")
	assert_gt(Palette.contrast(Palette.TERMINAL_TEXT, glass), 9.0, "TERMINAL_TEXT on glass")
	assert_gt(Palette.contrast(Palette.NET_CYAN, glass), 9.0, "cyan on glass")
	assert_gt(Palette.contrast(Palette.TEXT_MID, glass), 4.5, "TEXT_MID on glass")
	assert_gt(Palette.contrast(Palette.TEXT_LO, glass), 4.5, "TEXT_LO (disabled words) on glass")
	assert_gt(Palette.contrast(Palette.TEXT_HI, hot), 7.0, "TEXT_HI on hover glass")
	assert_gt(Palette.contrast(Palette.FOCUS, glass), 7.0, "focus lime on glass")
	assert_gt(Palette.contrast(Palette.ON_SELECTED, Palette.SELECTED), 7.0, "navy on the selected cyan fill")
	assert_gt(Palette.contrast(Palette.INK, Palette.STICKER_COMMIT), 4.5, "ink on the pink verb sticker")
	assert_gt(Palette.contrast(Palette.INK, Palette.STICKER_SAFE), 4.5, "ink on the yellow sticker")
	assert_gt(Palette.contrast(Palette.INK, Palette.DISABLED), 3.0, "ink on grey vinyl (large text)")
	assert_gt(Palette.contrast(Palette.INK, Palette.PAPER), 13.0, "ink on corp paper (13:1)")
	for c: Color in [Palette.HEAT_COOL, Palette.HEAT_NOTICED, Palette.HEAT_FLAGGED, Palette.HEAT_HUNTED]:
		assert_gt(Palette.contrast(c, glass), 4.5, "Heat %s on glass" % c.to_html(false))
	var holo := Palette.over(Palette.NIGHT_SKY, UiTheme.holo_box(Palette.CORP_HALCYON).bg_color)
	assert_gt(Palette.contrast(Palette.TEXT_HI, holo), 7.0, "TEXT_HI on a holo plate")


func test_theme_text_reads_on_its_own_boxes() -> void:
	var t := UiTheme.build(1.0)
	var night := Palette.NIGHT_SKY
	for pair in [[&"Button", &"normal", &"font_color", 7.0], [&"Button", &"hover", &"font_hover_color", 7.0],
			[&"Button", &"pressed", &"font_pressed_color", 7.0], [&"Button", &"disabled", &"font_disabled_color", 4.5],
			[UiTheme.TERMINAL_BUTTON, &"pressed", &"font_pressed_color", 7.0], [&"HotButton", &"normal", &"font_color", 4.5],
			[&"MenuItem", &"pressed", &"font_pressed_color", 7.0]]:
		var sb := t.get_stylebox(pair[1], pair[0]) as StyleBoxFlat
		var bg := Palette.over(night, sb.bg_color)
		var fg := t.get_color(pair[2], pair[0])
		assert_gt(Palette.contrast(fg, bg), float(pair[3]), "%s %s words on their box" % [pair[0], pair[1]])
	var tab := t.get_stylebox(&"tab_selected", &"TabBar") as StyleBoxFlat
	assert_gt(Palette.contrast(t.get_color(&"font_selected_color", &"TabBar"), tab.bg_color), 7.0, "the selected tab")


func test_theme_has_the_v2_type_variations() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		var t := UiTheme.build(scale)
		for v: StringName in [&"TerminalPanel", UiTheme.TERMINAL_BUTTON, UiTheme.HOLO_PANEL, UiTheme.PAPER_PANEL]:
			assert_true(t.get_type_variation_base(v) != &"", "%s exists at %.1f" % [v, scale])
		var panel := t.get_stylebox(&"panel", &"TerminalPanel") as StyleBoxFlat
		assert_eq(panel.bg_color, Palette.TERMINAL_BG, "navy glass")
		assert_eq(panel.border_color, Palette.TERMINAL_EDGE, "cyan edge")
		assert_eq(panel.corner_radius_top_right, UiTheme.TERMINAL_CHAMFER_PX, "the cut corner")
		assert_eq(panel.corner_detail, 1, "a straight cut (a chamfer, not a round)")
		assert_true(t.get_stylebox(&"focus", UiTheme.TERMINAL_BUTTON) is StyleBoxBrackets, "TerminalButton focus = F's brackets")
		assert_false(t.get_stylebox(&"focus", &"HotButton") is StyleBoxBrackets, "a sticker gets its halo, no brackets")
		assert_eq((t.get_stylebox(&"focus", &"HotButton") as StyleBoxFlat).border_color, Palette.FOCUS, "the lime halo")
		var hot := t.get_stylebox(&"hover", &"Button") as StyleBoxFlat
		assert_eq(hot.border_color, Palette.NET_CYAN, "hover lights the cyan edge (no pink)")
		assert_eq((t.get_stylebox(&"pressed", &"Button") as StyleBoxFlat).bg_color, Palette.SELECTED, "pressed fills cyan")
		var paper := t.get_stylebox(&"panel", UiTheme.PAPER_PANEL) as StyleBoxFlat
		assert_eq(paper.bg_color, Palette.PAPER, "paper stock")
		assert_eq(t.get_font(&"font", &"TooltipLabel"), Palette.body(), "tooltips in Plex (§2.9)")
		assert_eq(t.get_font_size(&"font_size", &"HotButton"), UiTheme.font_px_at(UiTheme.TITLE, scale), "the verb scales with the text")


func test_live_numbers_are_bare_anton_with_a_dark_rim_and_own_glow() -> void:
	var ls := UiTheme.live_number(UiTheme.HEADING, Palette.GAIN, 1.0)
	assert_eq((ls.font as FontVariation).base_font, Palette.display(), "Anton")
	assert_eq(ls.font_size, UiTheme.font_px_at(UiTheme.HEADING, 1.0))
	assert_eq(ls.outline_color, Palette.LIVE_NUMBER_RIM, "#06060A rim")
	assert_eq(ls.outline_size, UiTheme.LIVE_RIM_PX * 2, "2 px each side")
	assert_eq(ls.shadow_color, Color(Palette.GAIN, 0.5), "glow in its own colour at 50 %")
	assert_eq(ls.shadow_size, UiTheme.LIVE_GLOW_PX)
	assert_eq(UiTheme.live_number(UiTheme.HEADING, Palette.GAIN, 1.0), ls, "cached")
	assert_eq(UiTheme.live_number(UiTheme.HEADING, Palette.GAIN, 2.0).font_size, UiTheme.font_px_at(UiTheme.HEADING, 2.0), "scales")


func test_high_contrast_is_still_applied_last() -> void:
	var saved := Settings.high_contrast
	Settings.high_contrast = true
	var t := UiTheme.build(1.0)
	Settings.high_contrast = saved
	var panel := t.get_stylebox(&"panel", &"TerminalPanel") as StyleBoxFlat
	assert_eq(panel.bg_color, HighContrast.BG, "opaque black terminal under high contrast")
	assert_eq(panel.shadow_size, 0, "no glow")
	assert_eq((t.get_stylebox(&"panel", UiTheme.HOLO_PANEL) as StyleBoxFlat).bg_color, HighContrast.BG, "the holo becomes an opaque terminal")
	assert_eq(t.get_color(&"font_color", &"Button"), HighContrast.TEXT)


func test_faces_courier_prime_ships_with_its_licence_and_marker_is_pencil_only() -> void:
	for path in [Palette.FONT_PAPER, Palette.FONT_PAPER_BOLD]:
		var f := load(path) as FontFile
		assert_not_null(f, path)
		assert_string_contains(f.get_font_name(), "Courier Prime", path)
		assert_true(f.multichannel_signed_distance_field, "%s imports as MSDF" % path)
	assert_true(FileAccess.file_exists("res://assets/fonts/OFL_CourierPrime.txt"), "OFL shipped with Courier Prime")
	assert_true(Palette.FONTS_MSDF, "MSDF on (§2.9)")
	assert_ne(Palette.paper_bold(), Palette.paper())
	assert_eq(Palette.marker(), Palette.display(), "the Cell's lettering is the sticker face, Anton")
	assert_string_contains((Palette.pencil() as FontFile).get_font_name(), "Permanent Marker", "pencil only")
	var readme := FileAccess.get_file_as_string("res://assets/fonts/README.md")
	for word in ["Anton", "Share Tech Mono", "IBM Plex Sans Condensed", "Courier Prime", "Permanent Marker"]:
		assert_string_contains(readme, word, "README row for %s" % word)


func test_line_px_is_the_rich_text_line_height() -> void:
	# A RichTextLabel lays each line at the ascent and descent rounded up (the radio note and
	# the subtitle pages size and page by it); MSDF heights are fractional.
	var rtl: RichTextLabel = add_child_autofree(RichTextLabel.new())
	rtl.fit_content = true
	rtl.size = Vector2(400, 10)
	rtl.add_theme_font_override(&"normal_font", Palette.mono())
	rtl.add_theme_constant_override(&"line_separation", 0)
	for px in [15, 30]:
		rtl.add_theme_font_size_override(&"normal_font_size", px)
		rtl.text = "A\nB\nC\nD"
		await get_tree().process_frame
		assert_almost_eq(float(rtl.get_content_height()), UiTheme.line_px(Palette.mono(), px) * 4.0, 1.0, "four lines at %d px" % px)
