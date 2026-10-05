extends GutTest
## Static visual lint (ART-0 D, ported from art-pass W10; ART_BIBLE v1 §4.3 rule 1, §13, §14):
## literal colours and literal font sizes in `scripts/ui/**` may only go down. The baseline
## holds main's violations on 2026-10-05 (205 lines in 41 files); ART-1…ART-12 drive it to 0. Counts per file and rule are compared with the
## committed baseline `tools/visual_qa/lint_baseline.json`; a new file starts at 0. File
## reads only (no scene is instanced). Lower the baseline after a migration with
## `python tools/visual_qa/update_lint_baseline.py`: ART-0 audit D1, a count that went
## down without the baseline following fails too, so the baseline never keeps slack that
## would let literals come back silently.

const Lint := preload("res://tools/visual_qa/visual_lint_static.gd")


func test_no_file_gains_literal_colours_or_font_sizes() -> void:
	var findings := Lint.scan_all()
	var base := Lint.load_baseline()
	assert_false(base.is_empty(), "%s exists and lists files" % Lint.BASELINE)
	var cmp := Lint.compare(findings, base)
	assert_eq((cmp["up"] as Array).size(), 0, "literal colours / font sizes went up:\n%s" % "\n".join(cmp["up"]))


func test_the_baseline_has_no_slack() -> void:
	# ART-0 audit D1: the baseline equals today's counts. A count that went down must be
	# lowered in the same commit, or the freed slack would hide a literal coming back.
	var cmp := Lint.compare(Lint.scan_all(), Lint.load_baseline())
	assert_eq((cmp["down"] as Array).size(), 0,
		"the lint went down; lower the baseline (python tools/visual_qa/update_lint_baseline.py):\n%s" % "\n".join(cmp["down"]))


func test_named_colour_constants_are_palette_tokens() -> void:
	# ART-0 audit C1 / D2: high contrast's background is a Palette token, and the views'
	# plain whites and clears read the Palette tokens (the lint counts Color.WHITE and the like).
	assert_eq(HighContrast.BG, Palette.HC_BG, "high contrast's background is Palette.HC_BG")
	assert_eq(Palette.HC_BG, Color(0, 0, 0, 1), "#000 (ART_BIBLE §12)")
	assert_eq(Palette.NO_TINT, Color(1, 1, 1, 1))
	assert_eq(Palette.CLEAR.a, 0.0)
	var named := RegEx.create_from_string("\\bColor\\.[A-Z][A-Z0-9_]*\\b")
	for p in Lint.ui_files():
		if Lint.COLOR_EXEMPT.has(p):
			continue
		var lines := FileAccess.get_file_as_string(p).split("\n")
		for i in lines.size():
			var code := Lint.strip_comment(lines[i])
			assert_null(named.search(code), "%s:%d uses a named Color constant: %s" % [p, i + 1, code.strip_edges()])


func test_baseline_names_only_existing_files_and_known_rules() -> void:
	var files := Lint.ui_files()
	var base := Lint.load_baseline()
	for p in base:
		assert_true(files.has(p), "baseline file %s exists (remove it from the baseline)" % p)
		for r in base[p]:
			assert_true(Lint.RULES.has(r), "baseline rule %s of %s is known" % [r, p])


func test_colour_rule_counts_literals_and_skips_tokens_and_comments() -> void:
	var text := "\n".join([
		"var a := Color(1, 0, 0)",
		"var b := Color(\"#ff0000\")",
		"var c := Color8(255, 0, 0)",
		"var d := Color.html(\"#fff\")",
		"var e := Color.hex(0xff0000ff)",
		"var f := Color(Palette.INK, 0.5)",
		"var g := Palette.INK  # Color(1, 1, 1) in a comment",
		"var h := Color(-0.5, 0, 0)",
		"var i := Color.WHITE",
		"\tdraw_rect(r, Color.TRANSPARENT)",
		"const J := Color.BLACK.lerp(Palette.INK, 0.5)",
		"var k := Palette.NO_TINT",
	])
	var got: Dictionary = Lint.scan_text("res://scripts/ui/x.gd", text)
	assert_eq(got["color"], [1, 2, 3, 4, 5, 8, 9, 10, 11], "named constants (Color.WHITE…) count too (ART-0 audit D2)")
	var pal: Dictionary = Lint.scan_text("res://scripts/ui/kit/palette.gd", text)
	assert_eq(pal["color"], [], "palette.gd defines the tokens")


func test_font_rules_count_literal_sizes_only() -> void:
	var text := "\n".join([
		"\tlabel.add_theme_font_size_override(\"font_size\", 22)",
		"\tlabel.add_theme_font_size_override(\"font_size\", UiTheme.size(22))",
		"const HUB_FONT_SIZE := 10",
		"const HUB_MIN_FONT_SIZE: int = 8",
		"const BIG_FONT := 30",
		"const BANNER_FONT_FLOOR := 8",
		"\tfont_size = 14",
		"\tfont_size = UiTheme.BASE_SIZE",
		"\tdraw_string(font, Vector2.ZERO, \"x\", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Palette.INK)",
		"\tdraw_string(font, Vector2.ZERO, \"x\", HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.INK)",
		"\tfont.draw_string(ci, Vector2.ZERO, \"x\", HORIZONTAL_ALIGNMENT_LEFT, -1, 11)",
		"\t_c.draw_string(f, Vector2(1,",
		"\t\t2), \"x\", HORIZONTAL_ALIGNMENT_LEFT, -1, 9, Palette.INK)",
		"\tdraw_multiline_string(font, p, t, HORIZONTAL_ALIGNMENT_LEFT, w, fs)",
	])
	var got: Dictionary = Lint.scan_text("res://scripts/ui/x.gd", text)
	assert_eq(got["font_override"], [1])
	assert_eq(got["font_const"], [3, 4, 6], "FONT constants under the 12 px caption floor")
	assert_eq(got["font_size_assign"], [7])
	assert_eq(got["draw_size"], [9, 11, 12])


func test_compare_flags_a_rise_names_lines_and_starts_new_files_at_zero() -> void:
	var findings := {
		"res://scripts/ui/a.gd": {"color": [3, 9], "font_override": [], "draw_size": [], "font_const": [], "font_size_assign": []},
		"res://scripts/ui/new.gd": {"color": [], "font_override": [4], "draw_size": [], "font_const": [], "font_size_assign": []},
	}
	var base := {"res://scripts/ui/a.gd": {"color": 1}, "res://scripts/ui/b.gd": {"draw_size": 2}}
	var cmp := Lint.compare(findings, base)
	assert_eq((cmp["up"] as Array).size(), 2)
	assert_string_contains(cmp["up"][0], "a.gd [color] 2 > baseline 1, lines [3, 9]")
	assert_string_contains(cmp["up"][1], "new.gd [font_override] 1 > baseline 0")
	assert_eq((cmp["down"] as Array).size(), 1, "b.gd went down")
