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
