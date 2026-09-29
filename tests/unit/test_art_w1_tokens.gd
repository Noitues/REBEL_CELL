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
