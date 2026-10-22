extends GutTest
## LOOK-TOOLBOX module 9 (fast tier): the shared grade. The shipped presets validate; cel is the identity; the shoulder
## lands white on 1 and never reorders tones; the 3D city preset keeps the combat backdrop's numbers; the combat
## backdrop grades through rc_look (its shader includes rc_grade and keeps no copy of the curve).

const STEPS := 16


func test_shipped_config_validates_and_has_the_required_presets() -> void:
	assert_eq(RcLookGrade.default_config().validate(), PackedStringArray())
	for n in RcLookGradeConfig.REQUIRED:
		assert_not_null(RcLookGrade.preset(n), "preset %s" % n)


func test_a_bad_preset_is_reported() -> void:
	var cfg := RcLookGradeConfig.new()
	var p := RcLookGradePreset.new()
	p.exposure = 0.0
	p.white = -1.0
	cfg.presets = {&"cel": p, &"x": "nope"}
	var errs := cfg.validate()
	assert_eq(errs.size(), 4, "missing aaa2, not a preset, exposure, white: %s" % [errs])


func test_cel_is_the_identity() -> void:
	var cel := RcLookGrade.preset(&"cel")
	for i in STEPS + 1:
		var v := float(i) / STEPS
		var c := Color(v, 1.0 - v, v * 0.5, 0.7)
		assert_true(RcLookGrade.grade_preset(c, cel).is_equal_approx(c), "cel keeps %s" % c)


func test_the_shoulder_lands_white_on_one_and_keeps_order() -> void:
	for w: float in [1.5, 3.0, 8.0]:
		assert_almost_eq(RcLookGrade.shoulder(w, w), 1.0, 1e-6, "W %.1f lands on 1" % w)
		var last := -1.0
		for i in STEPS + 1:
			var l := w * float(i) / STEPS
			var s := RcLookGrade.shoulder(l, w)
			assert_gt(s, last, "monotone at %.2f" % l)
			assert_true(s <= l + 1e-6, "never brighter than the input at %.2f" % l)
			last = s
	assert_eq(RcLookGrade.shoulder(5.0, 0.0), 5.0, "white 0: no shoulder")


func test_saturation_and_tint_act_in_display_values() -> void:
	var c := Color(0.8, 0.2, 0.4)
	var g := RcLookGrade.grade(c, 1.0, 0.0, Color(1, 1, 1), 0.0)
	assert_almost_eq(g.r, g.g, 1e-6, "saturation 0 is grey")
	assert_almost_eq(g.r, Vector3(c.r, c.g, c.b).dot(RcLookGrade.LUMA), 1e-6, "around the display luma")
	var t := RcLookGrade.grade(Color(0.9, 0.9, 0.9), 1.0, 0.0, Color(2, 0.5, 1), 1.0)
	assert_eq(t.r, 1.0, "the tint clamps")
	assert_almost_eq(t.g, 0.45, 1e-6)


func test_the_city_preset_is_the_combat_backdrops_curve() -> void:
	var cfg := CityView3D.CONFIG
	var p := RcLookGrade.preset(&"aaa2")
	assert_eq(p.exposure, cfg.backdrop_exposure, "aaa2 exposure = CityConfig backdrop_exposure")
	assert_eq(p.white, cfg.backdrop_white, "aaa2 white = CityConfig backdrop_white")


func test_the_combat_backdrop_grades_through_rc_look() -> void:
	var cfg := CityView3D.CONFIG
	for corp: StringName in [&"", &"halcyon", &"orbital"]:
		for i in STEPS + 1:
			var v := float(i) / STEPS
			var c := Color(v, v * 0.6, 1.0 - v)
			var t: Color = cfg.backdrop_tint_by_corp.get(corp, cfg.backdrop_tint)
			assert_true(CombatBackdrop.graded(cfg, c, corp).is_equal_approx(
					RcLookGrade.grade(c, cfg.backdrop_exposure, cfg.backdrop_white, t, cfg.backdrop_saturation)))
	var code := (load("res://shaders/arena/combat_backdrop.gdshader") as Shader).code
	assert_true(code.contains("rc_grade.gdshaderinc"), "the shader includes the shared grade")
	assert_true(code.contains("rcl_grade("), "and calls it")
	assert_false(code.contains("1.0 / 2.4"), "no copy of the sRGB transfer left in it")
