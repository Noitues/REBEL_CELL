extends GutTest
## LOOK-TOOLBOX module 13 (fast tier): the vinyl sticker look. look_vinyl.tres validates and its numbers equal the
## `const RCV_*` of rc_vinyl.gdshaderinc; the presets equal the stock and verb colours the game's palette holds today;
## the GDScript mirrors equal the shader formulas (fold, gloss, band, flap back, dissolve, grey, shadow, markers,
## glitch, holo, card); reduce effects leaves the end state (no white sweep, no card gloss, no holo drift).

const INCLUDE := "res://addons/rc_look/shaders/rc_vinyl.gdshaderinc"
const WRAPPERS := ["rc_vinyl_kit", "rc_vinyl_chrome", "rc_vinyl_fill", "rc_vinyl_card"]
const EPS := 1e-5
const BODY := Rect2(0.0, 0.0, 100.0, 100.0)


func _near(a: float, b: float, msg: String = "", eps: float = EPS) -> void:
	assert_almost_eq(a, b, eps, msg)


func _c3(c: Color) -> Vector3:
	return Vector3(c.r, c.g, c.b)


func _consts() -> Dictionary:
	var out := {}
	var rx := RegEx.create_from_string("(?m)^const (float|vec2|vec3) RCV_(\\w+) = (.*);$")
	for m in rx.search_all(FileAccess.get_file_as_string(INCLUDE)):
		var t := m.get_string(1)
		var v := m.get_string(3)
		var val: Variant
		if t == "float":
			val = float(v)
		else:
			var parts := v.substr(v.find("(") + 1, v.rfind(")") - v.find("(") - 1).split(",")
			val = Vector2(float(parts[0]), float(parts[1])) if t == "vec2" else Vector3(float(parts[0]), float(parts[1]), float(parts[2]))
		out[m.get_string(2).to_lower()] = val
	return out


# ---- config -------------------------------------------------------------------------------------------------------

func test_shipped_config_loads_and_validates() -> void:
	assert_not_null(RcLookVinyl.config(), "look_vinyl.tres loads")
	assert_eq(RcLookVinyl.config().validate(), PackedStringArray())
	for id in RcLookVinyl.REQUIRED:
		assert_not_null(RcLookVinyl.preset(id), "preset %s" % id)


func test_validate_reports_bad_numbers() -> void:
	var c := RcLookVinyl.config().duplicate() as RcLookVinylConfig
	c.band_width = 0.0
	c.peel_max_share = 1.0
	c.presets = {}
	var errs := c.validate()
	assert_gt(errs.size(), RcLookVinyl.REQUIRED.size(), "missing presets and bad numbers are all reported")
	var p := RcLookVinylPreset.new()
	p.glossy = 2.0
	assert_gt(p.validate().size(), 0, "a preset out of range")


func test_every_shader_constant_is_in_the_config_with_the_same_value() -> void:
	var consts := _consts()
	assert_gt(consts.size(), 80, "the include's constants were found")
	var c := RcLookVinyl.config()
	for n: String in consts:
		var v: Variant = c.get(n)
		assert_not_null(v, "config has a field %s" % n)
		if v == null:
			continue
		if v is float:
			_near(float(v), float(consts[n]), n, 1e-9)
		else:
			assert_eq(v, consts[n], n)


func test_wrappers_include_the_shared_forms_and_keep_no_inline_look_numbers() -> void:
	for w in WRAPPERS:
		var code := FileAccess.get_file_as_string("res://addons/rc_look/shaders/%s.gdshader" % w)
		assert_true(code.contains("rc_vinyl.gdshaderinc"), "%s includes the module" % w)
		assert_not_null(load("res://addons/rc_look/shaders/%s.gdshader" % w), "%s loads" % w)
	var kit := FileAccess.get_file_as_string("res://addons/rc_look/shaders/rc_vinyl_kit.gdshader")
	assert_false(kit.contains("0.157"), "the rim colour lives in the include only")


# ---- presets equal today's stocks and verb colours ----------------------------------------------------------------

func test_kit_stock_fills_equal_the_palette() -> void:
	var cases := {
		&"kit_pink": Palette.STICKER_FILL_PINK, &"kit_red": Palette.STICKER_FILL_RED,
		&"kit_yellow": Palette.STICKER_FILL_YELLOW, &"kit_white": [Palette.STICKER_DIE_CUT, Palette.VINYL_WHITE_LO],
		&"kit_ink": [Palette.VINYL_INK, Palette.VINYL_EXTRUDE], &"kit_kraft": Palette.STICKER_FILL_PINK,
	}
	for id: StringName in cases:
		var p := RcLookVinyl.preset(id)
		assert_true(p.fill_top.is_equal_approx(cases[id][0]), "%s top" % id)
		assert_true(p.fill_bottom.is_equal_approx(cases[id][1]), "%s bottom" % id)
		assert_eq(p.family, RcLookVinylPreset.Family.KIT)
		assert_true(p.shadow_color.is_equal_approx(Palette.VINYL_EXTRUDE), "%s shadow is VINYL_EXTRUDE" % id)


func test_kit_backing_kraft_and_holo() -> void:
	assert_true(RcLookVinyl.preset(&"kit_pink").backing_color().is_equal_approx(Palette.VINYL_BACKING))
	assert_true(RcLookVinyl.preset(&"kit_kraft").backing_color().is_equal_approx(Palette.KRAFT.lightened(0.2)), "kraft: KRAFT lightened 0.2")
	assert_eq(RcLookVinyl.preset(&"kit_kraft").glossy, 0.0, "kraft is not glossy")
	assert_true(RcLookVinyl.preset(&"kit_holo").holo_face)
	assert_false(RcLookVinyl.preset(&"kit_pink").holo_face)


func test_chrome_verbs_equal_the_verb_sticker_colours() -> void:
	var cases := {
		&"chrome_pink": Palette.STICKER_FILL_PINK, &"chrome_yellow": Palette.STICKER_FILL_YELLOW,
		&"chrome_blue": [Palette.STICKER_BLUE, Palette.STICKER_BLUE_LOW], &"chrome_grey": [Palette.TEXT_MID, Palette.DISABLED],
	}
	for id: StringName in cases:
		var p := RcLookVinyl.preset(id)
		assert_true(p.fill_top.is_equal_approx(cases[id][0]), "%s top" % id)
		assert_true(p.fill_bottom.is_equal_approx(cases[id][1]), "%s bottom" % id)
		assert_eq(p.family, RcLookVinylPreset.Family.CHROME)
		assert_true(p.shadow_color.is_equal_approx(Palette.VINYL_EXTRUDE), "%s: extrude and shadow are VINYL_EXTRUDE on both families (ruling 4)" % id)
	assert_eq(RcLookVinyl.preset(&"chrome_glitch").marker, RcLookVinylPreset.Marker.GREEN)
	assert_eq(RcLookVinyl.marker_color(&"chrome_glitch"), Palette.STICKER_GLITCH_MARKER)
	assert_eq(RcLookVinyl.marker_color(&"chrome_pink"), Palette.STICKER_FILL_MARKER)


func test_tokens_and_rest_numbers_equal_the_builders() -> void:
	var c := RcLookVinyl.config()
	assert_true(c.die_cut.is_equal_approx(Palette.STICKER_DIE_CUT))
	assert_true(c.vinyl_ink.is_equal_approx(Palette.VINYL_INK))
	assert_true(c.vinyl_extrude.is_equal_approx(Palette.VINYL_EXTRUDE))
	assert_true(c.glitch_a.is_equal_approx(Palette.CELL_PINK), "glitch_a = CELL_PINK")
	assert_true(c.glitch_b.is_equal_approx(Palette.CORP_SOLACE), "glitch_b = CORP_SOLACE")
	assert_eq(c.disabled_grey, Palette.STICKER_DISABLED_GREY, "disabled: 80 % grey on both families (ruling 3)")
	assert_eq(c.disabled_alpha, VinylSticker.DISABLED_ALPHA, "and alpha 0.8")
	assert_eq(c.legacy_kit_disabled_grey, 1.0, "the old kit drew full grey")
	assert_eq(c.gloss_rest, VinylSticker.GLOSS_REST)
	assert_eq(c.gloss_pos_rest, VinylSticker.GLOSS_POS_REST)
	assert_eq(c.rim_rest, VinylSticker.RIM)
	assert_eq(c.band_deg, VinylSticker.SWEEP_BAND_DEG)
	assert_eq(c.holo_drift, VinylSticker.HOLO_DRIFT)
	assert_eq(c.edge_share, VinylSticker.EDGE_SHARE)
	assert_eq(c.edge_max_px, float(VinylSticker.EDGE_MAX_PX))
	assert_eq(c.keyline_px, float(VinylSticker.KEYLINE_PX))
	assert_eq(c.extrude_px, float(VinylSticker.EXTRUDE_PX))
	assert_eq(c.peel_max_share, VinylSticker.PEEL_MAX_SHARE)
	assert_eq(c.peel_board_h, float(VinylSticker.PEEL_BACK_BOARD_H))
	assert_eq(c.verb_die_cut, VerbSticker.DIE_CUT)
	assert_eq(c.verb_keyline, VerbSticker.KEYLINE)
	assert_eq(c.verb_extrude, VerbSticker.EXTRUDE)
	assert_eq(c.verb_shadow_alpha, VerbSticker.SHADOW_ALPHA)


func test_kit_uniforms_carry_the_preset() -> void:
	var u := RcLookVinyl.kit_uniforms(&"kit_kraft", BODY)
	assert_eq(u[&"glossy"], 0.0)
	assert_eq(u[&"body_rect"], Vector4(0, 0, 100, 100))
	assert_true((u[&"backing_color"] as Color).is_equal_approx(Palette.KRAFT.lightened(0.2)))
	var ch := RcLookVinyl.chrome_uniforms(&"chrome_pink", 60.0, 10.0, 50.0, 100.0)
	assert_almost_eq(float(ch[&"sweep_width"]), 11.0, 1e-4, "one source (run_sweep): band_width of the word's width, halved (ruling 6)")
	assert_almost_eq(float(ch[&"scan_period"]), 7.2, 1e-4, "12 % of the font size")
	assert_eq(float(RcLookVinyl.chrome_uniforms(&"chrome_pink", 10.0, 0.0, 10.0, 100.0)[&"scan_period"]), 3.0, "the scan period floor")
	var d := RcLookVinyl.kit_pose(&"disabled")
	assert_eq(d[&"grey"], 0.8)
	assert_eq(d[&"opacity"], 0.8)
	assert_eq(RcLookVinyl.kit_pose(&"disabled_legacy")[&"grey"], 1.0, "the old kit look stays available for the old | new rows")


# ---- mirror == formulas -------------------------------------------------------------------------------------------

func test_fold_frame_and_folded_alpha() -> void:
	var fr := RcLookVinyl.fold_frame(BODY, RcLookVinyl.CORNER_TOP_RIGHT, 0.0, 1.0, 34.0)
	var d := 0.70710678
	assert_true(fr["on"])
	_near((fr["u"] as Vector2).x, -d)
	_near((fr["u"] as Vector2).y, d)
	_near(float(fr["depth"]), 34.0 * d)
	_near((fr["P"] as Vector2).x, 100.0 - 17.0, "the legs are peel_px long", 1e-4)
	_near((fr["P"] as Vector2).y, 17.0, "", 1e-4)
	var free := RcLookVinyl.fold_frame(BODY, RcLookVinyl.CORNER_TOP_LEFT, 0.5, 0.0, 34.0)
	_near(float(free["depth"]), 0.5 * Vector2(50, 50).length(), "fold * distance corner to centre", 1e-4)
	assert_false(RcLookVinyl.fold_frame(BODY, 1, 0.0, 0.0, 34.0)["on"])
	var solid := func(p: Vector2) -> float: return 1.0 if BODY.has_point(p) else 0.0
	assert_eq(RcLookVinyl.folded_alpha(solid, Vector2(99, 1), fr), 0.0, "the folded-away corner is gone")
	assert_eq(RcLookVinyl.folded_alpha(solid, Vector2(50, 50), fr), 1.0, "the rest stays")
	assert_eq(RcLookVinyl.folded_alpha(solid, Vector2(120, 120), RcLookVinyl.fold_frame(BODY, 1, 0.0, 0.0, 34.0)), 0.0, "unfolded: plain alpha")


func test_gloss_coordinate_and_spec() -> void:
	var c := RcLookVinyl.config()
	_near(RcLookVinyl.gloss_t(BODY.position, BODY, 28.0), 0.0, "the first corner")
	_near(RcLookVinyl.gloss_t(BODY.end, BODY, 28.0), 1.0, "the last corner")
	_near(RcLookVinyl.spec(0.32, 0.22, 0.32, 1.0), c.soft_k_glossy * 0.22, "at the soft peak (glossy)")
	_near(RcLookVinyl.spec(0.32 + c.sharp_off, 1.0, 0.32, 1.0), maxf(c.sharp_k, exp(-pow(c.sharp_off / c.soft_w_glossy, 2.0)) * c.soft_k_glossy), "the sharp line")
	_near(RcLookVinyl.spec(0.32 + c.sharp_off, 1.0, 0.32, 0.0), exp(-pow(c.sharp_off / c.soft_w_kraft, 2.0)) * c.soft_k_kraft, "kraft has only the broad sheen")
	_near(RcLookVinyl.spec(0.9, 0.0, 0.32, 1.0), 0.0, "no gloss strength, no gloss")
	var lit := RcLookVinyl.kit_gloss(Vector3.ZERO, Vector2(50, 50), BODY, 1.0, RcLookVinyl.gloss_t(Vector2(50, 50), BODY, 28.0), 28.0, 1.0)
	assert_gt(lit.x, 0.2, "gloss lightens the vinyl at its peak")
	assert_eq(RcLookVinyl.kit_gloss(Vector3(0.3, 0.3, 0.3), Vector2(50, 50), BODY, 0.0, 0.5, 28.0, 1.0), Vector3(0.3, 0.3, 0.3))


func test_rim_lights_the_top_left_edge_and_shades_the_bottom_right() -> void:
	var box := func(p: Vector2) -> float: return 1.0 if Rect2(10, 10, 80, 80).has_point(p) else 0.0
	var top_left := RcLookVinyl.kit_rim(Vector3(0.5, 0.5, 0.5), 1.0, box, Vector2(11, 11), 0.8, 1.0)
	var bottom_right := RcLookVinyl.kit_rim(Vector3(0.5, 0.5, 0.5), 1.0, box, Vector2(89, 89), 0.8, 1.0)
	var inside := RcLookVinyl.kit_rim(Vector3(0.5, 0.5, 0.5), 1.0, box, Vector2(50, 50), 0.8, 1.0)
	assert_gt(top_left.x, 0.5, "rim light")
	assert_lt(bottom_right.x, 0.5, "rim shade")
	assert_eq(inside, Vector3(0.5, 0.5, 0.5), "the middle is untouched")


func test_band_forms_kit_and_chrome() -> void:
	var foil0 := RcLookVinyl.foil(0.0)
	var c := RcLookVinyl.config()
	_near(foil0.x, clampf(pow(0.5 + 0.5 * cos(c.foil_tau * c.foil_phase.x), c.foil_pow) * c.foil_gain, 0.0, 1.0))
	assert_eq(RcLookVinyl.band_w(0.0), 1.0)
	assert_eq(RcLookVinyl.band_w(1.5), 0.0)
	# the kit band at 45 deg crosses the body: centre at band_t 0.5 passes through the body centre
	_near(RcLookVinyl.kit_band_dd(Vector2(50, 50), BODY, 0.5, 0.22, 45.0), 0.0, "band_t 0.5 centres on the body", 1e-4)
	assert_lt(RcLookVinyl.kit_band_dd(Vector2(0, 100), BODY, 0.5, 0.22, 45.0) * RcLookVinyl.kit_band_dd(Vector2(100, 0), BODY, 0.5, 0.22, 45.0), 0.0, "the kit band runs along (1, 1): corners (0,100) and (100,0) sit on opposite sides")
	assert_gt(RcLookVinyl.chrome_band_dd(Vector2(60, 40), 80.0, 10.0), -1e-9, "x + y = 100 is past sweep 80")
	_near(RcLookVinyl.chrome_band_dd(Vector2(60, 40), 100.0, 10.0), 0.0, "the chrome band runs along x + y = sweep")
	_near(RcLookVinyl.chrome_band_dd(Vector2(100, 0), 100.0, 10.0), 0.0, "(100, 0) and (0, 100) are on the same chrome band line")
	var base := Vector3(0.4, 0.4, 0.4)
	assert_eq(RcLookVinyl.band_mix(base, foil0, 0.0, 0.55, 1.0), base, "outside the band nothing changes")
	assert_eq(RcLookVinyl.band_mix(base, foil0, 1.0, 0.55, 0.0), base, "no coverage (chrome glyph alpha 0), nothing changes")
	var lit := RcLookVinyl.band_mix(base, foil0, 1.0, 0.55, 1.0)
	assert_ne(lit, base)
	assert_true(lit.x <= 1.0)


func test_flap_back_and_flap() -> void:
	var c := RcLookVinyl.config()
	var backing := Vector3(0.8, 0.8, 0.8)
	var crease := RcLookVinyl.flap_back(0.0, backing, 0.0)
	_near(crease.x, lerpf(0.8, 1.0, c.crease_k), "a bright crease at the fold line")
	var far := RcLookVinyl.flap_back(1.0, backing, 0.0)
	_near(far.x, 0.8 * (1.0 - c.back_shade), "darker toward the flap's tip", 1e-6)
	assert_gt(RcLookVinyl.flap_back(1.0, backing, 1.0).x, far.x, "peel_back lightens the back")
	var solid := func(p: Vector2) -> float: return 1.0 if BODY.has_point(p) else 0.0
	var fr := RcLookVinyl.fold_frame(BODY, 1, 0.0, 1.0, 34.0)
	var folded := RcLookVinyl.kit_flap(solid, Vector2(80, 14), fr, backing, 1.0, Vector3(0.1, 0.1, 0.1), 1.0)
	assert_ne(folded["rgb"], Vector3(0.1, 0.1, 0.1), "the flap shows the adhesive back")
	assert_eq(RcLookVinyl.kit_flap(solid, Vector2(50, 90), fr, backing, 1.0, Vector3(0.1, 0.1, 0.1), 1.0)["rgb"], Vector3(0.1, 0.1, 0.1), "far from the fold nothing changes")


func test_dissolve_grey_and_shadow() -> void:
	var c := RcLookVinyl.config()
	assert_eq(RcLookVinyl.dissolve_verdict(0.1, 0.0), RcLookVinyl.Dissolve.KEEP, "dissolve 0 cuts nothing")
	assert_eq(RcLookVinyl.dissolve_verdict(0.1, 1.0), RcLookVinyl.Dissolve.CUT)
	assert_eq(RcLookVinyl.dissolve_verdict(c.dissolve_over - 0.04, 1.0), RcLookVinyl.Dissolve.WHITE, "a white-hot rim just behind the front")
	var o1 := RcLookVinyl.dissolve_order(Vector2(10, 50), BODY, 4.0)
	var o2 := RcLookVinyl.dissolve_order(Vector2(90, 50), BODY, 4.0)
	assert_gt(o2, o1 - c.dissolve_h, "the order grows with x (the hash adds at most its share)")
	assert_eq(RcLookVinyl.dissolve_order(Vector2(10, 50), BODY, 4.0), o1, "deterministic")
	assert_eq(RcLookVinyl.grey(Vector3(1, 0, 0), 0.0), Vector3(1, 0, 0))
	var g := RcLookVinyl.grey(Vector3(1, 0, 0), 1.0)
	_near(g.x, 0.299)
	_near(g.y, 0.299)
	assert_eq(RcLookVinyl.shadow_offset(0.0), c.shadow_off)
	assert_eq(RcLookVinyl.shadow_offset(1.0), c.shadow_off + c.shadow_off_lift)
	_near(RcLookVinyl.shadow_radius(0.5), c.shadow_r + c.shadow_r_lift * 0.5)
	assert_eq(RcLookVinyl.shadow_alpha(1.0, 1.0, 0.0, 0.0, 0.0), 0.0, "shadow_k 0: no shadow")
	_near(RcLookVinyl.shadow_alpha(1.0, 1.0, 0.0, 1.0, 0.0), c.contact_k, "at rest the contact shadow wins")
	_near(RcLookVinyl.shadow_alpha(1.0, 1.0, 1.0, 1.0, 0.0), c.shadow_k * (1.0 - c.shadow_k_lift), "lifted: only the soft shadow (no contact)")
	assert_eq(RcLookVinyl.shadow_alpha(1.0, 1.0, 0.0, 1.0, 1.0), 0.0, "a dissolved sticker casts nothing")


func test_chrome_markers_fills_and_glitch() -> void:
	var m := RcLookVinyl.chrome_marker(Color(1, 0, 1))
	assert_eq(m["kind"], RcLookVinyl.KIND_MAGENTA)
	assert_eq(m["bright"], 1.0)
	var dim := RcLookVinyl.chrome_marker(Color(0.5, 0, 0.5))
	assert_eq(dim["bright"], 0.5, "the marker brightness carries a modulate dim")
	var gr := RcLookVinyl.chrome_marker(Color(0, 1, 3.0 / 8.0))
	assert_eq(gr["kind"], RcLookVinyl.KIND_GREEN)
	assert_eq(gr["band"], 3.0, "b / g * 8 is the band")
	assert_eq(RcLookVinyl.chrome_marker(Color(0, 1, 0))["band"], 0.0)
	assert_eq(RcLookVinyl.chrome_marker(Color(0.3, 0.6, 0.9))["kind"], RcLookVinyl.KIND_NONE, "an ordinary colour is not a marker")
	assert_eq(RcLookVinyl.chrome_marker(Color(0.01, 0.01, 0.01))["kind"], RcLookVinyl.KIND_NONE, "too dark to be a marker")
	var top := Vector3(1, 0, 0)
	var bot := Vector3(0, 0, 1)
	var wk := RcLookVinyl.config().sweep_white_k
	var f0 := RcLookVinyl.chrome_marker_fill(Vector2(0, 50), 0.0, 100.0, top, bot, 0.0, RcLookVinyl.SWEEP_OFF, 14.0, 1.0, wk)
	_near(f0.x, 0.5, "the gradient's middle")
	var glossed := RcLookVinyl.chrome_marker_fill(Vector2(0, 0), 0.0, 100.0, top, bot, 0.22, RcLookVinyl.SWEEP_OFF, 14.0, 1.0, wk)
	_near(glossed.y, 0.22, "the rest gloss lightens the top of the fill")
	var swept := RcLookVinyl.chrome_marker_fill(Vector2(0, 50), 0.0, 100.0, top, bot, 0.0, 22.5, 14.0, 1.0, wk)
	var still := RcLookVinyl.chrome_marker_fill(Vector2(0, 50), 0.0, 100.0, top, bot, 0.0, 22.5, 14.0, 0.0, wk)
	var dropped := RcLookVinyl.chrome_marker_fill(Vector2(0, 50), 0.0, 100.0, top, bot, 0.0, 22.5, 14.0, 1.0, 0.0)
	assert_gt(swept.y, f0.y, "the white sweep lightens the fill")
	assert_eq(still, f0, "reduce effects (live 0): the white sweep never shows")
	assert_eq(dropped, f0, "white_k 0: the second white sweep is gone (ruling 2)")
	assert_true(RcLookVinyl.glitch_keep(Vector2(0, 5), 0.0, 0.0, 10.0), "band 0 keeps the whole word")
	assert_true(RcLookVinyl.glitch_keep(Vector2(0, 25), 0.0, 3.0, 10.0), "band 3 spans y 20..30")
	assert_false(RcLookVinyl.glitch_keep(Vector2(0, 31), 0.0, 3.0, 10.0))
	var w := Vector3(1, 1, 1)
	var a := Vector3(1, 0, 0)
	var b := Vector3(0, 1, 0)
	assert_eq(RcLookVinyl.glitch_color(Vector2(0, 0.5), 0.0, 5.0, w, a, b), a, "row 0 scan line: glitch_a")
	assert_eq(RcLookVinyl.glitch_color(Vector2(0, 5.5), 0.0, 5.0, w, a, b), b, "row 1 scan line: glitch_b")
	assert_eq(RcLookVinyl.glitch_color(Vector2(0, 2.5), 0.0, 5.0, w, a, b), w, "between lines: white")


func test_holo_hsv_and_card() -> void:
	var red := RcLookVinyl.hsv2rgb(0.0, 1.0, 1.0)
	_near(red.x, 1.0)
	_near(red.y, 0.0)
	_near(red.z, 0.0)
	var grey_v := RcLookVinyl.hsv2rgb(0.3, 0.0, 0.6)
	_near(grey_v.x, 0.6)
	_near(grey_v.z, 0.6)
	var h1 := RcLookVinyl.holo_fill(Vector2(40, 30), Vector2(260, 96), 11.0, 0.0, 0.55)
	assert_eq(RcLookVinyl.holo_fill(Vector2(40, 30), Vector2(260, 96), 11.0, 0.0, 0.55), h1, "deterministic")
	for v in [h1.x, h1.y, h1.z]:
		assert_true(v >= 0.0 and v <= 1.0, "clamped")
	var drifted := RcLookVinyl.holo_fill(Vector2(40, 30), Vector2(260, 96), 11.0, 0.25, 0.55)
	assert_ne(drifted, h1, "the hue drifts with the phase (the shader passes rc_time(TIME) * holo_drift: 0 under reduce effects)")
	_near(RcLookVinyl.card_front(0.0, 0.1), -0.1)
	_near(RcLookVinyl.card_front(1.0, 0.1), 1.1)
	_near(RcLookVinyl.card_gloss_share(Vector2(0.5, 0.5), 0.5, 0.18, 0.55, 1.0), 0.55, "the gloss peak is its alpha")
	assert_eq(RcLookVinyl.card_gloss_share(Vector2(0.5, 0.5), 0.5, 0.18, 0.55, 0.0), 0.0, "reduce effects: no card gloss")
	assert_eq(RcLookVinyl.card_gloss_share(Vector2(0.0, 0.0), 0.9, 0.18, 0.55, 1.0), 0.0, "far from the band")


func test_peel_leg_and_edge() -> void:
	var c := RcLookVinyl.config()
	# 1080 board, text scale 1: a long body gets the long leg, a short one the short leg
	_near(RcLookVinyl.peel_leg(600.0, 1080.0, 1.0, 240.0, 24.0, 34.0), minf(34.0, maxf(34.0, 600.0 * c.peel_max_share)))
	_near(RcLookVinyl.peel_leg(100.0, 1080.0, 1.0, 240.0, 24.0, 34.0), minf(24.0, maxf(24.0, 100.0 * c.peel_max_share)))
	assert_lt(RcLookVinyl.peel_leg(100.0, 540.0, 1.0, 240.0, 24.0, 34.0), 24.0, "scales with the screen height")
	_near(RcLookVinyl.edge_for(30.0, 1.0), minf(30.0 * c.edge_share, c.edge_max_px))
	_near(RcLookVinyl.edge_for(200.0, 1.0), c.edge_max_px, "the cap")
	_near(RcLookVinyl.edge_for(200.0, 2.0), c.edge_max_px * 2.0, "the cap grows with the text scale")


func test_lab_art_is_a_sticker() -> void:
	var art := RcLookVinyl.lab_art(&"kit_pink")
	var img: Image = art["image"]
	var body: Rect2 = art["body"]
	assert_eq(img.get_pixelv(Vector2i(0, 0)).a, 0.0, "the padding is clear")
	assert_gt(img.get_pixelv(Vector2i(body.get_center())).a, 0.99, "the body is solid")
	var holo := RcLookVinyl.lab_art(&"kit_holo")["image"] as Image
	assert_ne(holo.get_pixelv(Vector2i(body.get_center())), img.get_pixelv(Vector2i(body.get_center())), "the holo stock has its own face")


func test_chrome_band_takes_the_kit_geometry_parallel_to_the_peel() -> void:
	var half_w := 11.0
	var t := 0.37
	var kit_centre := RcLookVinyl.band_centre(BODY, t, half_w, 45.0)
	for px in [Vector2(10, 20), Vector2(80, 33), Vector2(50, 50)]:
		_near(RcLookVinyl.band_dd_at(px, kit_centre, half_w, 45.0), RcLookVinyl.kit_band_dd(px, BODY, t, half_w * 2.0 / BODY.size.x, 45.0), "one geometry for both families (ruling 1)", 1e-4)
	# the band's axis n is the peel's fold direction u from the top-right corner, so its lines are parallel to the fold line
	var fr := RcLookVinyl.fold_frame(BODY, RcLookVinyl.CORNER_TOP_RIGHT, 0.0, 1.0, 34.0)
	var n := Vector2(-sin(deg_to_rad(45.0)), cos(deg_to_rad(45.0)))
	_near(n.dot(fr["u"]), 1.0, "the band is parallel to the peel", 1e-5)
	# a "\\" shape: two points along (1, 1) share a band coordinate
	_near(RcLookVinyl.band_dd_at(Vector2(20, 20), kit_centre, half_w, 45.0), RcLookVinyl.band_dd_at(Vector2(70, 70), kit_centre, half_w, 45.0), "", 1e-4)
	assert_lt(RcLookVinyl.band_centre(BODY, 0.0, half_w, 45.0), RcLookVinyl.band_centre(BODY, 1.0, half_w, 45.0))
