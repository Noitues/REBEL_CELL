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
