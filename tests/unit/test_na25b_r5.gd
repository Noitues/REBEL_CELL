extends GutTest
## NA-25b r5 (art-pass A-037): the CRT hold's glass is the class field's hue at 0.8x its value, the SAVED stamp waits out the jack
## transition, and the dissolve's 0 / 1 glyphs thin out (fewer) as the share falls instead of shrinking.

const SHADER_PATH := "res://shaders/city/city_building.gdshader"


func test_the_hold_glass_is_the_field_hue_at_a_share_of_its_value() -> void:
	for accent: Color in [Palette.NET_CYAN, Palette.CELL_PINK, Palette.CELL_ACID]:
		var f := JackHubField.field_color(accent)
		var g := JackWheel.glass_color(accent)
		assert_almost_eq(g.v, f.v * JackWheel.HOLD_GLASS_VALUE, 0.01, "0.8x the field's value")
		assert_almost_eq(g.s, f.s, 0.01, "the field's saturation")
		if f.s > 0.05:
			assert_almost_eq(g.h, f.h, 0.01, "the field's hue")


func test_the_saved_stamp_is_held_through_the_transition_and_shows_after() -> void:
	Fx.saved_label.modulate.a = 0.0
	Fx.hold_saved(true)
	Fx.show_saved()
	await wait_process_frames(3)
	assert_false(Fx.saved_showing(), "no stamp over the transition")
	assert_true(Fx.saved_queued, "the save waits")
	var shown := Fx.saved_shown
	Fx.hold_saved(false)
	await wait_process_frames(3)
	assert_eq(Fx.saved_shown, shown + 1, "the stamp is put up once the hub has burnt open")
	assert_false(Fx.saved_queued)
	Fx.hold_saved(true)
	Fx.show_saved()
	Fx.hold_saved(false)
	Fx.hold_saved(true)  # a transition begins in the frame the stamp was about to appear
	await wait_process_frames(3)
	assert_false(Fx.saved_showing(), "a stamp that was about to appear waits")
	assert_true(Fx.saved_queued)
	Fx.hold_saved(false)
	await wait_process_frames(3)
	assert_false(Fx.saved_queued)


func test_a_release_with_no_save_shows_nothing() -> void:
	Fx.saved_label.modulate.a = 0.0
	Fx.hold_saved(true)
	Fx.hold_saved(false)
	await wait_process_frames(3)
	assert_false(Fx.saved_showing())


func test_the_glyph_count_thins_out_as_the_share_falls() -> void:
	var prev := -1.0
	for i in range(0, 61):
		var s := NetrunShaderKit.bit_glyph_share(float(i) / 100.0)
		assert_gte(s, prev - 0.0001, "monotonic in the share up to the stagger (%d)" % i)
		prev = s
	assert_lt(NetrunShaderKit.bit_glyph_share(0.30), NetrunShaderKit.bit_glyph_share(0.55), "fewer glyphs at 0.30 than at 0.55")
	assert_gt(NetrunShaderKit.bit_glyph_share(0.30), 0.0)
	assert_eq(NetrunShaderKit.bit_glyph_share(0.0), 0.0)
	assert_eq(NetrunShaderKit.bit_glyph_share(1.0), 0.0, "open: no bits left")


func test_the_shader_draws_fixed_size_glyphs_on_the_netrun_clock() -> void:
	var code := FileAccess.get_file_as_string(SHADER_PATH)
	assert_true(code.contains("bit_glyph("), "the 0 / 1 are drawn as glyphs")
	assert_true(code.contains("bit_px"), "the glyph height is set in screen px")
	assert_false(code.contains("(1.0 - 0.8 * tc)"), "the glyph no longer shrinks with its life")
	assert_true(code.contains("h * 0.6) / 0.4"), "the stagger / life the kit mirrors (BIT_STAGGER, BIT_LIFE)")
	assert_true(code.contains("nr_clock(anim_t, anim_t_frozen)"))
