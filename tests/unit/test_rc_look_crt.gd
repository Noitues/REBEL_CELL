extends GutTest
## LOOK-TOOLBOX module 14 (fast tier): the CRT / terminal glass. The shipped config validates; the GDScript mirror is the
## formulas of the shaders it replaces; the presets hold the numbers those shaders and their callers hard-code today
## (the terminal preset keeps CrtTerminalPanel's pinned SCAN_PX / SCAN_STRENGTH / HEX_ALPHA); the include carries the
## existing forms verbatim; reduce effects resolves by the three conventions (flicker and roll stop in all of them).

const INC := "res://addons/rc_look/shaders/rc_crt.gdshaderinc"
const EPS := 1e-6


func test_shipped_config_validates() -> void:
	assert_eq(RcLookCrt.default_config().validate(), PackedStringArray())
	for n in RcLookCrt.REQUIRED:
		assert_not_null(RcLookCrt.preset(n), "preset %s" % n)


func test_a_bad_preset_and_config_are_reported() -> void:
	var p := RcLookCrtPreset.new()
	p.scan_px = 0.0
	p.flicker = 2.0
	p.roll_width = 0.0
	assert_eq(p.validate().size(), 3, str(p.validate()))
	var cfg := RcLookCrtConfig.new()
	cfg.presets = {&"terminal": RcLookCrtPreset.new()}
	cfg.reduce = 9
	assert_eq(cfg.validate().size(), RcLookCrt.REQUIRED.size(), str(cfg.validate()))


func test_scan_is_the_step_form() -> void:
	# crt_terminal.gdshader: step(0.5, fract((p.y - panel.y) / scan_px - 0.08)); FRAGCOORD form: step(0.5, fract(y / 3.0))
	for y: float in [0.0, 0.5, 1.5, 2.5, 3.5, 17.5, 100.5]:
		assert_eq(RcLookCrt.scan(y, 3.0, 0.08), (1.0 if fposmod(y / 3.0 - 0.08, 1.0) >= 0.5 else 0.0), "terminal y %s" % y)
		assert_eq(RcLookCrt.scan(y, 3.0, 0.0), (1.0 if fposmod(y / 3.0, 1.0) >= 0.5 else 0.0), "fragcoord y %s" % y)
	# 3 px: pixel centres 0.5 and 1.5 fall on the bright half, 2.5 on the dark with phase 0 (a centre never sits on an edge)
	assert_eq(RcLookCrt.scan(0.5, 3.0, 0.0), 0.0)
	assert_eq(RcLookCrt.scan(2.5, 3.0, 0.0), 1.0)
	# the phase keeps pixel centres off the 0.5 edge: the phased form never lands exactly on it at a half-pixel centre
	for k in 40:
		var v := (float(k) + 0.5) / 3.0 - 0.08
		assert_gt(absf(fposmod(v, 1.0) - 0.5), 0.01, "centre %s clear of the edge" % k)


func test_sine_scan_is_scanlines_gdshader() -> void:
	for y: float in [0.0, 0.1, 0.37, 0.9]:
		assert_almost_eq(RcLookCrt.scan_sine(y, 360.0), 0.5 + 0.5 * sin(y * 360.0 * 3.14159), EPS)


func test_flicker_roll_vignette_glow_are_the_formulas() -> void:
	for t: float in [0.0, 0.37, 2.5]:
		for rate: float in [41.0, 43.0, 47.0]:
			assert_almost_eq(RcLookCrt.flicker(t, rate, 0.04), 1.0 - 0.04 * (0.5 + 0.5 * sin(t * rate)), EPS)
	assert_eq(RcLookCrt.flicker(1.234, 43.0, 0.0), 1.0, "no amount, no flicker")
	assert_almost_eq(RcLookCrt.roll(0.5, 0.5, 0.08), 1.0, EPS, "peak at the band")
	assert_almost_eq(RcLookCrt.roll(0.6, 0.5, 0.08), exp(-pow((0.6 - 0.5) / 0.08, 2.0)), EPS)
	assert_almost_eq(RcLookCrt.vignette_sd(0.0, 28.0, 0.78), 0.78, EPS, "edge keeps the floor")
	assert_almost_eq(RcLookCrt.vignette_sd(-28.0, 28.0, 0.78), 1.0, EPS, "whole from the reach in")
	assert_almost_eq(RcLookCrt.vignette_sd(-14.0, 28.0, 0.78), lerpf(0.78, 1.0, smoothstep(0.0, 28.0, 14.0)), EPS)
	assert_almost_eq(RcLookCrt.vignette_uv(Vector2(0.5, 0.5), 0.25, 0.45, 0.85), 1.0, EPS, "centre untouched")
	assert_almost_eq(RcLookCrt.vignette_uv(Vector2(-0.5, 0.5), 0.18, 0.45, 0.85), 1.0 - 0.18, EPS, "past the outer end it takes all")
	assert_almost_eq(RcLookCrt.glow(0.0, 10.0, 0.45), 0.45, EPS)
	assert_almost_eq(RcLookCrt.glow(4.2, 10.0, 0.45), 0.45 * exp(-1.0), EPS, "one falloff length is glow_px x 0.42")
	assert_almost_eq(RcLookCrt.glow(1.0, 0.1, 1.0), exp(-1.0 / 0.5), EPS, "the 0.5 px floor")
	assert_eq(RcLookCrt.band_at(7.0, 7.0), 0.0)
	assert_almost_eq(RcLookCrt.band_at(3.5, 7.0), 0.5, EPS)


func test_terminal_preset_keeps_the_pinned_values() -> void:
	var p := RcLookCrt.preset(&"terminal")
	assert_eq(p.scan_px, CrtTerminalPanel.SCAN_PX)
	assert_eq(p.scan_strength, CrtTerminalPanel.SCAN_STRENGTH)
	assert_eq(p.hex_alpha, CrtTerminalPanel.HEX_ALPHA)
	assert_eq(p.glow_px, CrtTerminalPanel.GLOW_PX)
	assert_eq(p.edge_px, CrtTerminalPanel.EDGE_PX)
	assert_eq(p.scan_px, 3.0)
	assert_eq(p.scan_strength, 0.10)
	assert_eq(p.hex_alpha, 0.06)
	assert_true(p.accent.is_equal_approx(Palette.NET_CYAN))
	assert_true(p.glass_top.is_equal_approx(Palette.CRT_GLASS_TOP))
	assert_true(p.glass_bottom.is_equal_approx(Palette.CRT_GLASS_BOTTOM))


func test_accent_presets_are_the_panels_accents() -> void:
	assert_true(RcLookCrt.preset(&"firmware").accent.is_equal_approx(Palette.CELL_ACID))
	assert_true(RcLookCrt.preset(&"schematics").accent.is_equal_approx(Palette.RESIST_GOLD))
	assert_true(RcLookCrt.preset(&"dispatch").accent.is_equal_approx(Palette.HARM))
	assert_true(RcLookCrt.preset(&"corp").accent.is_equal_approx(Palette.CORP_SOLACE), "CrtTerminalPanel's default corp colour")
	var t := RcLookCrt.preset(&"terminal")
	for n: StringName in [&"firmware", &"schematics", &"dispatch", &"corp"]:
		var p := RcLookCrt.preset(n)
		assert_eq([p.scan_px, p.scan_phase, p.scan_strength, p.roll_strength, p.glow_px], [t.scan_px, t.scan_phase,
				t.scan_strength, t.roll_strength, t.glow_px], "%s differs from the terminal only by its accent" % n)


func test_terminal_numbers_are_crt_terminals_defaults() -> void:
	var code := (load("res://shaders/kit/crt_terminal.gdshader") as Shader).code
	var p := RcLookCrt.preset(&"terminal")
	for line: String in ["uniform float inner_glow : hint_range(0.0, 1.0) = %.2f;" % p.inner_glow,
			"uniform float glow_strength : hint_range(0.0, 1.0) = %.2f;" % p.glow_strength,
			"uniform float roll_strength : hint_range(0.0, 0.2) = %.2f;" % p.roll_strength,
			"uniform float roll_seconds = %.1f;" % p.roll_seconds,
			"uniform float notch_px = %.1f;" % p.notch_px, "uniform float corner_px = %.1f;" % p.corner_px,
			"/ 0.08, 2.0)", "fract((p.y - panel.y) / scan_px - %.2f)" % p.scan_phase,
			"mix(0.78, 1.0, vig)", "smoothstep(0.0, 28.0, -sd)", "glow_px * 0.42"]:
		assert_string_contains(code, line)
	assert_eq(p.vignette_floor, 0.78)
	assert_eq(p.vignette_px, 28.0)
	assert_eq(p.roll_width, 0.08)


func test_other_screens_numbers_are_the_games() -> void:
	var ui := RcLookCrt.preset(&"ui_panel")
	var ui_theme := FileAccess.get_file_as_string("res://scripts/ui/kit/ui_theme.gd")
	assert_string_contains(ui_theme, "0.0 if Settings.reduce_effects else %s)" % "0.12")
	assert_string_contains(ui_theme, "\"flicker\", 0.0 if Settings.reduce_effects else 0.01)")
	assert_eq([ui.scan_strength, ui.flicker, ui.flicker_rate, ui.scan_phase], [0.12, 0.01, 43.0, 0.0])
	assert_string_contains((load("res://shaders/crt_panel.gdshader") as Shader).code, "sin(rc_time(TIME) * 43.0)")
	var sk := RcLookCrt.preset(&"neon_sketch")
	var nc := FileAccess.get_file_as_string("res://scripts/ui/kit/neon_city.gd")
	assert_string_contains(nc, "\"scan_strength\", 0.07 if live else 0.0")
	assert_string_contains(nc, "\"flicker\", 0.012 if live else 0.0")
	assert_eq([sk.scan_strength, sk.flicker, sk.flicker_rate, sk.scan_phase], [0.07, 0.012, 41.0, 0.0])
	for s: String in ["res://shaders/city_sketch.gdshader", "res://shaders/city_live.gdshader"]:
		var c := (load(s) as Shader).code
		assert_string_contains(c, "step(0.5, fract(FRAGCOORD.y / 3.0))", s)
		assert_string_contains(c, "sin(rc_time(TIME) * 41.0)", s)
	var fx := RcLookCrt.preset(&"fx_overlay")
	var fx_code := FileAccess.get_file_as_string("res://scripts/autoload/fx.gd")
	assert_string_contains(fx_code, "\"flicker_strength\", 0.01)")
	assert_string_contains(fx_code, "\"vignette\", 0.18)")
	assert_string_contains(fx_code, "\"scanline_strength\", 0.0)")
	var scan := (load("res://shaders/scanline.gdshader") as Shader).code
	assert_string_contains(scan, "uniform float scanline_density = %.1f;" % fx.scan_sine_density)
	assert_string_contains(scan, "sin(rc_time(TIME) * 47.0)")
	assert_eq([fx.scan_strength, fx.flicker, fx.flicker_rate, fx.screen_vignette, fx.screen_vignette_inner,
			fx.screen_vignette_outer], [0.0, 0.01, 47.0, 0.18, 0.45, 0.85])
	assert_string_contains(scan, "smoothstep(0.45, 0.85, d)")


func test_the_include_holds_the_existing_forms() -> void:
	var inc := FileAccess.get_file_as_string(INC)
	for f: String in ["step(0.5, fract(y_px / period_px - phase))", "1.0 - amount * (0.5 + 0.5 * sin(t * rate_rad_s))",
			"exp(-pow((y01 - band) / width, 2.0))", "mix(floor_gain, 1.0, smoothstep(0.0, reach_px, -sd))",
			"1.0 - amount * smoothstep(inner, outer, distance(uv, vec2(0.5)))", "RCL_CRT_GLOW_REACH = %s" % "0.42",
			"RCL_CRT_SINE_PI = 3.14159", "#ifndef RC_CRT_INCLUDED"]:
		assert_string_contains(inc, f)
	assert_eq(RcLookCrt.GLOW_REACH, 0.42)
	assert_eq(RcLookCrt.SINE_PI, 3.14159)
	assert_false(inc.contains("#include"), "standalone: fog-safe, no rc_look")


func test_reduce_effects_conventions() -> void:
	var t := RcLookCrt.preset(&"terminal")
	var fx := RcLookCrt.preset(&"fx_overlay")
	var off := RcLookCrt.resolve(t, false)
	assert_eq([off[&"scan_strength"], off[&"roll_strength"], off[&"visible"]], [0.10, 0.03, true])
	var keep := RcLookCrt.resolve(t, true, RcLookCrt.Reduce.KEEP_STATIC)
	assert_eq(keep[&"scan_strength"], 0.10, "static scanlines stay")
	assert_eq([keep[&"flicker"], keep[&"roll_strength"], keep[&"visible"]], [0.0, 0.0, true])
	assert_eq(RcLookCrt.resolve(RcLookCrt.preset(&"ui_panel"), true, RcLookCrt.Reduce.KEEP_STATIC)[&"flicker"], 0.0)
	var zero := RcLookCrt.resolve(t, true, RcLookCrt.Reduce.ZERO_SCAN)
	assert_eq([zero[&"scan_strength"], zero[&"flicker"], zero[&"roll_strength"], zero[&"visible"]], [0.0, 0.0, 0.0, true])
	assert_eq(RcLookCrt.resolve(fx, true, RcLookCrt.Reduce.ZERO_SCAN)[&"screen_vignette"], 0.18, "the vignette stays")
	var hide := RcLookCrt.resolve(fx, true, RcLookCrt.Reduce.HIDE)
	assert_eq([hide[&"visible"], hide[&"screen_vignette"], hide[&"scan_strength"]], [false, 0.0, 0.0])
	assert_eq(RcLookCrt.resolve(t, true), keep, "the config default is KEEP_STATIC")


func test_wrapper_defaults_are_what_the_game_sets() -> void:
	# designer 2026-10-22 (art-pass): a shader's default is what its caller sets, so no pixel changes and no default lies
	var t := RcLookCrt.preset(&"terminal")
	var ct := (load("res://shaders/kit/crt_terminal.gdshader") as Shader).code
	for line: String in ["uniform vec4 glass_top : source_color = vec4(%.6f, %.6f, %.6f, 1.0);" % [t.glass_top.r, t.glass_top.g, t.glass_top.b],
			"uniform vec4 glass_bottom : source_color = vec4(%.6f, %.6f, %.6f, 1.0);" % [t.glass_bottom.r, t.glass_bottom.g, t.glass_bottom.b],
			"uniform vec4 accent : source_color = vec4(%.6f, %.6f, 1.0, 1.0);" % [t.accent.r, t.accent.g]]:
		assert_string_contains(ct, line)
	var fx := RcLookCrt.preset(&"fx_overlay")
	var sc := (load("res://shaders/scanline.gdshader") as Shader).code
	for line: String in ["uniform float scanline_strength : hint_range(0.0, 1.0) = %s;" % _g(fx.scan_strength),
			"uniform float flicker_strength : hint_range(0.0, 1.0) = %s;" % _g(fx.flicker),
			"uniform float aberration : hint_range(0.0, 0.02) = 0.0;", "uniform float vignette : hint_range(0.0, 1.0) = %s;" % _g(fx.screen_vignette)]:
		assert_string_contains(sc, line)


func test_reduce_default_is_keep_static_for_good() -> void:
	assert_eq(RcLookCrt.default_config().reduce, RcLookCrt.Reduce.KEEP_STATIC, "designer ruling 82c92714")


## A float the way the shader text writes it (0.0, 0.01, 0.18).
func _g(v: float) -> String:
	var s := "%s" % snappedf(v, 0.0001)
	return s if s.contains(".") else s + ".0"
