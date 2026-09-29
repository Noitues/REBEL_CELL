extends GutTest
## Art pass W9 (ART_BIBLE §12, §5.4, §10): the accessibility and presentation settings.
## Defaults; old settings files load unchanged; text scale reaches 2.0 (Q5); colour-blind
## correction layer per mode and none when off; high contrast reaches 7:1; reduce motion
## helpers; resolve speed scales (instant = 0); pad glyph detection; the Steam Deck
## first-run default through an injected device probe; the Options rows.

var _saved: Dictionary


func before_each() -> void:
	_saved = Settings.to_dict()


func after_each() -> void:
	Settings.from_dict(_saved)
	Settings.save_settings()
	Settings.changed.emit()


func _fresh() -> Node:
	return autofree(load("res://scripts/autoload/settings.gd").new())


# --- Defaults and old files ------------------------------------------------------------

func test_new_settings_have_their_defaults() -> void:
	var s := _fresh()
	assert_eq(s.colorblind_mode, &"off")
	assert_false(s.high_contrast)
	assert_false(s.reduce_motion)
	assert_eq(s.resolve_speed, &"x1")
	assert_eq(s.pad_glyph_set, &"auto")
	assert_eq(s.text_scale, 1.0)


func test_an_old_settings_file_without_the_new_keys_loads_unchanged() -> void:
	# A settings.json as the build before W9 wrote it (every key it had, none of W9's).
	var old := {"reduce_effects": true, "flash_limiter": false, "text_scale": 1.4, "subtitles": false,
		"subtitle_typing": true, "master_volume": 0.5, "music_volume": 0.3, "sfx_volume": 0.7, "language": "en",
		"window_mode": 0, "resolution": [1600, 900], "vsync": false, "show_fps": true, "map_legend": false,
		"system_log": true, "keybinds": {"nudge_left": KEY_A}, "tutorial_done": true, "assist_mode": true}
	var s := _fresh()
	s.from_dict(JSON.parse_string(JSON.stringify(old)))
	assert_true(s.reduce_effects)
	assert_false(s.flash_limiter)
	assert_almost_eq(s.text_scale, 1.4, 0.0001)
	assert_eq(s.resolution, Vector2i(1600, 900))
	assert_eq(int(s.keybinds["nudge_left"]), KEY_A)
	assert_true(s.assist_mode)
	assert_eq(s.colorblind_mode, &"off", "new keys take their defaults")
	assert_false(s.high_contrast)
	assert_false(s.reduce_motion)
	assert_eq(s.resolve_speed, &"x1")
	assert_eq(s.pad_glyph_set, &"auto")
	# Everything the old file had is written back the same way (additive format).
	var d: Dictionary = s.to_dict()
	for k in old:
		assert_true(d.has(k), "old key %s still saved" % k)


func test_new_settings_round_trip_and_reject_unknown_values() -> void:
	var s := _fresh()
	s.from_dict({"colorblind_mode": "tritan", "high_contrast": true, "reduce_motion": true,
		"resolve_speed": "instant", "pad_glyph_set": "switch"})
	var back := _fresh()
	back.from_dict(JSON.parse_string(JSON.stringify(s.to_dict())))
	assert_eq(back.colorblind_mode, &"tritan")
	assert_true(back.high_contrast)
	assert_true(back.reduce_motion)
	assert_eq(back.resolve_speed, &"instant")
	assert_eq(back.pad_glyph_set, &"switch")
	back.from_dict({"colorblind_mode": "sepia", "resolve_speed": "x9", "pad_glyph_set": "atari"})
	assert_eq(back.colorblind_mode, &"off", "unknown values fall back to the default")
	assert_eq(back.resolve_speed, &"x1")
	assert_eq(back.pad_glyph_set, &"auto")


# --- 1. Text scale 2.0 ------------------------------------------------------------------

func test_text_scale_reaches_two_and_clamps_there() -> void:
	assert_eq(Settings.TEXT_SCALE_MAX, 2.0, "Q5: the ceiling is 2.0")
	Settings.set_text_scale(2.0)
	assert_eq(Settings.text_scale, 2.0)
	Settings.set_text_scale(2.7)
	assert_eq(Settings.text_scale, 2.0, "clamped at 2.0")
	var s := _fresh()
	s.from_dict({"text_scale": 5.0})
	assert_eq(s.text_scale, 2.0, "a file past the range loads at 2.0")
	s.from_dict({"text_scale": 1.6})
	assert_almost_eq(s.text_scale, 1.6, 0.0001, "the old ceiling loads unchanged")


# --- 2. Colour-blind correction ---------------------------------------------------------

func test_each_colorblind_mode_adds_the_layer_and_off_removes_it() -> void:
	Settings.set_colorblind_mode(&"off")
	assert_null(ColorblindFilter.layer, "off: no layer")
	assert_eq(ColorblindFilter.get_child_count(), 0, "off: nothing in the tree, no cost")
	for mode in [&"deutan", &"protan", &"tritan"]:
		Settings.set_colorblind_mode(mode)
		var layer: ColorblindLayer = ColorblindFilter.layer
		assert_not_null(layer, "%s adds the layer" % mode)
		assert_true(layer.is_inside_tree())
		assert_eq(layer.layer, ColorblindLayer.LAYER)
		assert_eq(layer.shader_mode(), ColorblindLayer.MODES[mode], "%s drives the shader" % mode)
		assert_eq(ColorblindFilter.active_mode(), mode)
		assert_eq(ColorblindFilter.get_child_count(), 1, "one layer, reused")
	Settings.set_colorblind_mode(&"off")
	assert_null(ColorblindFilter.layer)
	assert_eq(ColorblindFilter.get_child_count(), 0, "off frees the layer")
	assert_eq(ColorblindFilter.active_mode(), &"off")


func test_correction_layer_sits_above_the_game_and_below_the_review_filter() -> void:
	assert_gt(ColorblindLayer.LAYER, Fx.layer, "over Fx (and every game layer)")
	assert_lt(ColorblindLayer.LAYER, 128, "under the W10 simulation filter (layer 128)")
	var layer: ColorblindLayer = autofree(ColorblindLayer.new(&"protan"))
	assert_eq(layer.rect.mouse_filter, Control.MOUSE_FILTER_IGNORE, "never takes a click")
	assert_true(ColorblindLayer.SHADER.code.contains("hint_screen_texture"))
	assert_true(ColorblindLayer.SHADER.code.contains("rc_common.gdshaderinc"), "W6 shader conventions")


func _separation(a: Color, b: Color, mode: StringName) -> float:
	var sa := ColorblindLayer.simulate(a, mode)
	var sb := ColorblindLayer.simulate(b, mode)
	return Vector3(sa.r - sb.r, sa.g - sb.g, sa.b - sb.b).length()


func test_the_correction_separates_hues_the_deficiency_merges() -> void:
	# Red/green pairs for deutan and protan (Solace green vs harm red, gain vs harm), a
	# blue/green pair for tritan: after the correction, the simulated viewer sees them
	# further apart than before.
	var pairs := {&"deutan": [Palette.CORP_SOLACE, Palette.HARM], &"protan": [Palette.GAIN, Palette.HARM],
		&"tritan": [Palette.NET_CYAN, Palette.GAIN]}
	for mode in pairs:
		var a: Color = pairs[mode][0]
		var b: Color = pairs[mode][1]
		var before := _separation(a, b, mode)
		var after := _separation(ColorblindLayer.correct(a, mode), ColorblindLayer.correct(b, mode), mode)
		assert_gt(after, before, "%s: %.3f -> %.3f" % [mode, before, after])
	assert_eq(ColorblindLayer.correct(Palette.HARM, &"off"), Palette.HARM, "off passes colours through")
	var grey := Color(0.5, 0.5, 0.5)
	var g := ColorblindLayer.correct(grey, &"deutan")
	assert_almost_eq(g.r, grey.r, 0.02, "neutral greys stay (almost) put")
	assert_almost_eq(g.g, grey.g, 0.02)


# --- 3. High contrast -------------------------------------------------------------------

func test_high_contrast_theme_reaches_seven_to_one() -> void:
	var t := UiTheme.build(1.0)
	HighContrast.apply(t)
	# Labels on the theme's panels.
	for panel in [&"TerminalPanel", &"GlassPanel"]:
		var sb := t.get_stylebox(&"panel", panel) as StyleBoxFlat
		assert_eq(sb.bg_color.a, 1.0, "%s is opaque" % panel)
		assert_eq(sb.shadow_size, 0, "%s has no soft halo" % panel)
		for label in [&"Label", &"HeaderLabel", &"BodyText"]:
			var c := t.get_color(&"font_color", label)
			assert_gte(Palette.contrast(c, sb.bg_color), HighContrast.HC_MIN_CONTRAST, "%s on %s" % [label, panel])
	assert_gte(Palette.contrast(t.get_color(&"default_color", &"RichTextLabel"), HighContrast.BG), HighContrast.HC_MIN_CONTRAST)
	# Buttons: each state's font colour on that state's own box.
	var states := {&"normal": &"font_color", &"hover": &"font_hover_color", &"pressed": &"font_pressed_color",
		&"focus": &"font_focus_color", &"disabled": &"font_disabled_color"}
	for kind in [&"Button", &"OptionButton", &"HotButton", &"NoteButton", &"MenuItem"]:
		for state in states:
			if not t.has_color(states[state], kind):
				continue
			var fc := t.get_color(states[state], kind)
			var bg := HighContrast.BG
			if state != &"focus" and t.has_stylebox(state, kind):
				var box := t.get_stylebox(state, kind) as StyleBoxFlat
				if box != null and box.draw_center and box.bg_color.a > 0.0:
					bg = box.bg_color
					assert_eq(bg.a, 1.0, "%s %s is opaque" % [kind, state])
			assert_gte(Palette.contrast(fc, bg), HighContrast.HC_MIN_CONTRAST, "%s %s text" % [kind, state])


func test_high_contrast_gives_buttons_and_focus_a_solid_thick_edge() -> void:
	var t := UiTheme.build(1.0)
	HighContrast.apply(t)
	for kind in [&"Button", &"HotButton"]:
		var n := t.get_stylebox(&"normal", kind) as StyleBoxFlat
		assert_gte(n.border_width_left, HighContrast.HC_BUTTON_BORDER, "%s edge" % kind)
		assert_eq(n.border_color.a, 1.0, "%s edge is solid" % kind)
	# W2: focus is drawn as FOCUS corner brackets (StyleBoxBrackets), thickened here.
	var f := t.get_stylebox(&"focus", &"Button") as StyleBoxBrackets
	assert_not_null(f, "focus is the bracket box")
	assert_eq(f.thickness, float(HighContrast.HC_FOCUS_BORDER))
	assert_eq(f.color, Palette.FOCUS)
	var grab := t.get_stylebox(&"grabber", &"VScrollBar") as StyleBoxFlat
	assert_eq(grab.bg_color.a, 1.0, "a scroll grabber stays visible (its fill made opaque)")
	assert_ne(grab.bg_color, HighContrast.BG)


func test_the_setting_rebuilds_the_theme_through_settings_changed() -> void:
	var root: Control = add_child_autofree(Control.new())
	UiTheme.apply(root)
	Settings.set_high_contrast(false)
	var off := root.theme.get_stylebox(&"panel", &"GlassPanel") as StyleBoxFlat
	assert_lt(off.bg_color.a, 1.0, "normal glass is translucent")
	Settings.set_high_contrast(true)
	var on := root.theme.get_stylebox(&"panel", &"GlassPanel") as StyleBoxFlat
	assert_eq(on.bg_color, HighContrast.BG, "high contrast: opaque #000")
	assert_eq(root.theme.get_color(&"font_color", &"Label"), Palette.TEXT_HI)
	Settings.set_high_contrast(false)
	assert_lt((root.theme.get_stylebox(&"panel", &"GlassPanel") as StyleBoxFlat).bg_color.a, 1.0, "and back")


# --- 4. Reduce motion -------------------------------------------------------------------

func test_reduce_motion_helpers() -> void:
	Settings.set_reduce_motion(false)
	Settings.set_reduce_effects(false)
	assert_true(Motion.camera_moves_allowed())
	assert_true(Motion.parallax_allowed())
	assert_eq(Motion.page_transition_style(), Motion.PAGE_SLIDE)
	Settings.set_reduce_motion(true)
	assert_false(Motion.camera_moves_allowed())
	assert_false(Motion.parallax_allowed())
	assert_eq(Motion.page_transition_style(), Motion.PAGE_FADE, "cross-fades only")
	assert_false(Settings.reduce_effects, "reduce motion leaves reduce effects alone")
	assert_true(Fx.effects_enabled(), "effects still play")
	Settings.set_reduce_motion(false)
	Settings.set_reduce_effects(true)
	assert_true(Motion.camera_moves_allowed(), "reduce effects keeps its own meaning")
	assert_eq(Motion.page_transition_style(), Motion.PAGE_SLIDE)
	Settings.set_reduce_effects(false)


# --- 5. Resolve speed -------------------------------------------------------------------

func test_resolve_speed_scales_and_instant_is_zero() -> void:
	Settings.set_resolve_speed(&"x1")
	assert_eq(Motion.resolve_time_scale(), 1.0)
	assert_false(Motion.resolve_instant())
	Settings.set_resolve_speed(&"x2")
	assert_eq(Motion.resolve_time_scale(), 0.5)
	Settings.set_resolve_speed(&"instant")
	assert_eq(Motion.resolve_time_scale(), 0.0)
	assert_true(Motion.resolve_instant(), "instant: the end state at once")
	Settings.set_resolve_speed(&"warp")
	assert_eq(Settings.resolve_speed, &"instant", "an unknown speed is ignored")
	Settings.set_resolve_speed(&"x1")


func test_fast_forward_is_an_input_action_with_a_key_and_a_pad_binding() -> void:
	assert_true(InputMap.has_action(Motion.FAST_FORWARD_ACTION))
	var key := false
	var pad := false
	for ev in InputMap.action_get_events(Motion.FAST_FORWARD_ACTION):
		key = key or ev is InputEventKey
		pad = pad or ev is InputEventJoypadButton or ev is InputEventJoypadMotion
	assert_true(key, "a default key")
	assert_true(pad, "a default pad binding")
	assert_true(Settings.REBINDABLE.has(Motion.FAST_FORWARD_ACTION), "rebindable like the other combat keys")
	var k := Settings.key_for(Motion.FAST_FORWARD_ACTION)
	for other in Settings.REBINDABLE:
		if other != Motion.FAST_FORWARD_ACTION:
			assert_ne(Settings.key_for(other), k, "no key clash with %s" % other)
	assert_false(Motion.fast_forward_held(), "not held with no input")
	Input.action_press(Motion.FAST_FORWARD_ACTION)
	assert_true(Motion.fast_forward_held())
	Settings.set_resolve_speed(&"x1")
	assert_eq(Motion.resolve_time_scale_now(), Motion.FAST_FORWARD_TIME_SCALE, "held: faster")
	Input.action_release(Motion.FAST_FORWARD_ACTION)
	assert_false(Motion.fast_forward_held())
	assert_eq(Motion.resolve_time_scale_now(), 1.0)


# --- 6. Pad glyph set -------------------------------------------------------------------

func test_glyph_set_detection_from_joy_names() -> void:
	var cases := {
		"Xbox Series Controller": &"xbox", "XInput Gamepad (GLFW)": &"xbox", "Xbox 360 Controller": &"xbox",
		"PS5 Controller": &"playstation", "DualSense Wireless Controller": &"playstation",
		"Sony DualShock 4": &"playstation", "PS4 Controller": &"playstation", "PlayStation 3 Controller": &"playstation",
		"Nintendo Switch Pro Controller": &"switch", "Joy-Con (L/R)": &"switch", "Switch Pro Controller": &"switch",
		"Steam Deck": &"deck", "Steam Deck Controller": &"deck",
		"Generic USB Gamepads": &"xbox", "Logitech F310": &"xbox", "": &"xbox",
	}
	for joy in cases:
		assert_eq(Settings.glyph_set_for_joy_name(joy), cases[joy], "'%s'" % joy)


func test_effective_glyph_set_follows_the_setting_or_the_pad() -> void:
	for set_name in [&"xbox", &"playstation", &"switch", &"deck"]:
		Settings.set_pad_glyph_set(set_name)
		assert_eq(Settings.effective_glyph_set(), set_name, "a fixed set wins")
	Settings.set_pad_glyph_set(&"auto")
	assert_eq(Settings.effective_glyph_set(), Settings.glyph_set_for_joy_name(Settings.active_joy_name()), "auto detects")
	Settings.set_pad_glyph_set(&"sega")
	assert_eq(Settings.pad_glyph_set, &"auto", "an unknown set is ignored")


# --- 7. Steam Deck default --------------------------------------------------------------

func _probe(feature: bool = false, env: String = "", os_name: String = "Windows", screen: Vector2i = Vector2i(1920, 1080), joys: PackedStringArray = PackedStringArray()) -> Dictionary:
	return {"feature": feature, "env": env, "os": os_name, "screen": screen, "joy_names": joys}


func test_steam_deck_detection_from_an_injected_probe() -> void:
	assert_true(Settings.is_steam_deck_from(_probe(true)), "the steamdeck feature tag")
	assert_true(Settings.is_steam_deck_from(_probe(false, "1")), "SteamDeck=1")
	assert_false(Settings.is_steam_deck_from(_probe(false, "0")))
	assert_true(Settings.is_steam_deck_from(_probe(false, "", "Linux", Vector2i(1280, 800), PackedStringArray(["Steam Deck"]))), "1280x800 Linux with a Deck pad")
	assert_false(Settings.is_steam_deck_from(_probe(false, "", "Linux", Vector2i(1280, 800), PackedStringArray(["Xbox Series Controller"]))), "a 1280x800 laptop is not a Deck")
	assert_false(Settings.is_steam_deck_from(_probe(false, "", "Windows", Vector2i(1280, 800), PackedStringArray(["Steam Deck"]))))
	assert_false(Settings.is_steam_deck_from(_probe()))


func test_first_run_on_a_steam_deck_defaults_text_scale_to_1_2() -> void:
	var deck := _fresh()
	deck.apply_first_run_defaults(_probe(true))
	assert_eq(deck.text_scale, Settings.TEXT_SCALE_STEAM_DECK)
	assert_eq(Settings.TEXT_SCALE_STEAM_DECK, 1.2, "§5.4")
	var pc := _fresh()
	pc.apply_first_run_defaults(_probe())
	assert_eq(pc.text_scale, 1.0, "elsewhere the default stays 1.0")
	# Only a first run: a Deck with a settings file keeps the player's own scale.
	var dir := "user://w9_deck_%d" % OS.get_process_id()
	DirAccess.make_dir_recursive_absolute(dir)
	var with_file := _fresh()
	with_file.path = dir + "/settings.json"
	with_file.text_scale = 0.9
	with_file.save_settings()
	var again := _fresh()
	again.path = with_file.path
	again.device_probe_override = _probe(true)
	again.load_settings()
	assert_almost_eq(again.text_scale, 0.9, 0.0001, "the saved scale wins")
	var first := _fresh()
	first.path = dir + "/missing.json"
	first.device_probe_override = _probe(true)
	first.load_settings()
	assert_eq(first.text_scale, Settings.TEXT_SCALE_STEAM_DECK, "no file on a Deck: 1.2")
	DirAccess.remove_absolute(with_file.path)
	DirAccess.remove_absolute(dir)


# --- 8. Options rows --------------------------------------------------------------------

func test_options_rows_drive_the_new_settings() -> void:
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	panel.show_section("Accessibility")
	for w in [panel.colorblind_option, panel.high_contrast_check, panel.reduce_motion_check, panel.resolve_speed_option]:
		assert_true(w.is_inside_tree(), "%s is in Accessibility" % w.name)
		assert_ne(w.focus_mode, Control.FOCUS_NONE, "%s is pad-reachable" % w.name)
	panel.high_contrast_check.button_pressed = true
	assert_true(Settings.high_contrast)
	panel.high_contrast_check.button_pressed = false
	panel.reduce_motion_check.button_pressed = true
	assert_true(Settings.reduce_motion)
	panel.reduce_motion_check.button_pressed = false
	panel.colorblind_option.select(Settings.COLORBLIND_MODES.find(&"protan"))
	panel.colorblind_option.item_selected.emit(Settings.COLORBLIND_MODES.find(&"protan"))
	assert_eq(Settings.colorblind_mode, &"protan")
	panel.colorblind_option.item_selected.emit(0)
	assert_eq(Settings.colorblind_mode, &"off")
	panel.resolve_speed_option.item_selected.emit(Settings.RESOLVE_SPEEDS.find(&"instant"))
	assert_eq(Settings.resolve_speed, &"instant")
	assert_eq(panel.scale_slider.max_value, 2.0, "the slider reaches 2.0")
	panel.show_section("Controls")
	assert_true(panel.glyph_option.is_inside_tree(), "pad glyphs sit with the controls")
	panel.glyph_option.item_selected.emit(Settings.PAD_GLYPH_SETS.find(&"playstation"))
	assert_eq(Settings.pad_glyph_set, &"playstation")


func test_new_option_words_have_string_keys_and_no_mouse_wording() -> void:
	var csv := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for word in SettingsPanel.W9_WORDS:
		assert_true(csv.contains(word), "strings.csv has '%s'" % word)
		var lower := String(word).to_lower()
		for mouse_word in ["click", "drag", "mouse"]:
			assert_false(lower.contains(mouse_word), "'%s' has no mouse wording" % word)
