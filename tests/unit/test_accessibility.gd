extends GutTest
## Accessibility (M4 acceptance): the reduce-effects toggle disables scanlines, flicker
## and chromatic effects everywhere; every slice type and status is distinguishable
## without colour; settings persist; the theme scales text.

var _saved: Dictionary


func before_each() -> void:
	_saved = Settings.to_dict()


func after_each() -> void:
	Settings.from_dict(_saved)
	Settings.save_settings()
	Fx.apply_settings()


func test_reduce_effects_disables_scanlines_and_distortion_everywhere() -> void:
	Settings.set_reduce_effects(false)
	assert_true(Fx.scanlines.visible, "scanline/flicker/chromatic overlay on by default")
	assert_true(Fx.effects_enabled())
	Settings.set_reduce_effects(true)
	assert_false(Fx.scanlines.visible, "overlay off: no scanlines, flicker or chromatic aberration")
	assert_false(Fx.distortion.visible)
	assert_eq(Fx.distortion.material.get_shader_parameter("intensity"), 0.0)
	assert_false(Fx.effects_enabled())
	Fx.heat_pulse()
	assert_false(Fx.distortion.visible, "heat pulse ignored under reduce-effects")
	var bg: WireframeBackground = autofree(WireframeBackground.new())
	var before: float = bg.floor_offset
	bg._process(0.5)
	assert_eq(bg.floor_offset, before, "background animation frozen under reduce-effects")
	Settings.set_reduce_effects(false)
	assert_true(Fx.scanlines.visible, "back on")
	bg._process(0.5)
	assert_ne(bg.floor_offset, before, "animation resumes")


func test_scanline_shader_exposes_every_effect_as_a_uniform() -> void:
	var code: String = Fx.SCANLINE_SHADER.code
	for u in ["scanline_strength", "flicker_strength", "aberration"]:
		assert_true(code.contains("uniform float " + u), "%s is a uniform" % u)


func test_flash_limiter_setting_drives_the_fx_limiter() -> void:
	Settings.set_flash_limiter(true)
	assert_true(Fx.limiter.enabled)
	Settings.set_flash_limiter(false)
	assert_false(Fx.limiter.enabled)


func test_every_slice_type_and_status_has_a_distinct_glyph() -> void:
	var glyphs := {}
	for type in RC.SliceType.values():
		assert_true(Palette.SLICE_GLYPHS.has(type), "glyph for %s" % RC.SliceType.keys()[type])
		var g: String = Palette.SLICE_GLYPHS[type]
		assert_ne(g, "", "non-empty glyph for %s" % RC.SliceType.keys()[type])
		assert_false(glyphs.has(g), "glyph %s is unique" % g)
		glyphs[g] = true
		assert_true(Palette.SLICE_NAMES.has(type), "text tag for %s" % RC.SliceType.keys()[type])
	var status_glyphs := {}
	for status in RC.Status.values():
		if status == RC.Status.NONE:
			continue
		var g: String = Palette.STATUS_GLYPHS[status]
		assert_ne(g, "")
		assert_false(status_glyphs.has(g), "status glyph %s is unique" % g)
		status_glyphs[g] = true
		assert_ne(Palette.STATUS_TAGS[status], "")


func test_settings_round_trip_and_clamp() -> void:
	Settings.set_text_scale(9.0)
	assert_eq(Settings.text_scale, Settings.TEXT_SCALE_MAX, "clamped")
	Settings.set_subtitles(false)
	var d := Settings.to_dict()
	var fresh: Node = load("res://scripts/autoload/settings.gd").new()
	fresh.from_dict(JSON.parse_string(JSON.stringify(d)))
	assert_eq(fresh.text_scale, Settings.TEXT_SCALE_MAX)
	assert_false(fresh.subtitles)
	fresh.free()


func test_theme_uses_style_guide_fonts_and_scales_text() -> void:
	assert_true(ResourceLoader.exists(Palette.FONT_MARKER), "Permanent Marker present")
	assert_true(ResourceLoader.exists(Palette.FONT_DISPLAY), "Anton present")
	assert_true(ResourceLoader.exists(Palette.FONT_MONO), "Share Tech Mono present")
	var t1 := UiTheme.build(1.0)
	var t2 := UiTheme.build(1.5)
	assert_eq(t1.default_font_size, UiTheme.BASE_SIZE)
	assert_eq(t2.default_font_size, roundi(UiTheme.BASE_SIZE * 1.5))
	assert_same(t1.default_font, Palette.mono())


func test_settings_panel_toggles_write_to_settings() -> void:
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	panel.reduce_check.button_pressed = true
	assert_true(Settings.reduce_effects, "check button drives the setting")
	panel.reduce_check.button_pressed = false
	assert_false(Settings.reduce_effects)
	panel.scale_slider.value = 1.2
	assert_almost_eq(Settings.text_scale, 1.2, 0.001)
