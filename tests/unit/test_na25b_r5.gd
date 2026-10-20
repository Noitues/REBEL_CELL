extends GutTest
## NA-25b r5 / r6 (art-pass A-037, A-046): the SAVED stamp waits out the jack
## transition, and the dissolve's 0 / 1 glyphs thin out (fewer) as the share falls instead of shrinking.

const SHADER_PATH := "res://shaders/city/city_building.gdshader"


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


func test_the_hold_hex_is_the_rim_hue_with_an_age_fade() -> void:
	var rim := PaletteSkins.chrome(Palette.NET_CYAN)
	var c := JackSequence.hex_color(rim)
	assert_almost_eq(c.h, rim.h, 0.01, "the rim's hue")
	assert_almost_eq(c.v, rim.v * 0.75, 0.01, "0.75 of the rim's value")
	assert_almost_eq(JackSequence.HOLD_HEX_ALPHA, 0.65, 0.001, "newest rows")
	assert_almost_eq(JackSequence.HOLD_HEX_OLDEST_ALPHA, 0.35, 0.001, "oldest rows")
	assert_gt(JackSequence.HOLD_HEX_ALPHA, JackSequence.HOLD_HEX_OLDEST_ALPHA)
	var seq := JackSequence.new()
	add_child_autofree(seq)
	seq._begin({"street": true, "from": "A", "to": "B"})
	var ov := seq.hold.shader_overrides
	assert_eq(ov[&"hex_tint"], JackSequence.hex_color(seq.hold.accent()))
	assert_almost_eq(float(ov[&"hex_age_oldest"]) * JackSequence.HOLD_HEX_ALPHA, JackSequence.HOLD_HEX_OLDEST_ALPHA, 0.001)
	assert_false(ov.has(&"glass_top") or ov.has(&"glass_bottom"), "the glass is the terminal panel's own, not a field colour")


func test_saved_waits_for_the_end_of_the_street_entry_and_the_jack_out_releases_it() -> void:
	# A-054: the jack-in's sequence ends at the dot, but SAVED stays held through the dive until the scene releases it (the zoom has settled).
	Fx.saved_label.modulate.a = 0.0
	var seq := JackSequence.new()
	add_child_autofree(seq)
	seq._begin({"street": true, "from": "A", "to": "B"})
	seq._reverse = false
	Fx.hold_saved(true)
	seq._end()
	Fx.show_saved()
	await wait_process_frames(3)
	assert_true(Fx.saved_held, "still held after the sequence ends: the dive is playing")
	assert_false(Fx.saved_showing(), "no SAVED before the settle")
	Fx.hold_saved(false)  # the street scene's release after the entry's zoom settled
	await wait_process_frames(3)
	assert_true(Fx.saved_showing(), "shown once the entry has settled")
	assert_true(Fx.saved_label.get_theme_stylebox(&"normal") is StyleBoxFlat, "a CRT glass toast, not a bare word")
	Fx.saved_label.modulate.a = 0.0
	seq._begin({"street": true, "from": "A", "to": "B"})
	seq._reverse = true
	Fx.hold_saved(true)
	seq._fx = Fx
	seq._end()
	assert_false(Fx.saved_held, "the jack-out's own end releases it")
