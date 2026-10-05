extends GutTest
## ART-0 C (Salvage S1; ported from art-pass eaa7a2c, M13 W9 / W9s / W9F, ART_BIBLE §12,
## §5.4, §10): the accessibility and presentation settings on main. Defaults equal main's
## behaviour; old settings files load unchanged; every setting round-trips through
## settings.json; text scale reaches 2.0 (Q5); colour-blind correction layer per mode and
## none when off; high contrast reaches 7:1; reduce motion (separate from reduce effects)
## and its consumers; resolve speed scales (instant = 0) and fast-forward is never a skip;
## pad glyph detection; the Steam Deck first-run default through an injected device probe;
## the Options rows.

var _saved: Dictionary
var _force_live: bool


func before_each() -> void:
	_saved = Settings.snapshot()
	_force_live = Motion.force_live


func after_each() -> void:
	Motion.force_live = _force_live
	if Input.is_action_pressed(Motion.FAST_FORWARD_ACTION):
		Input.action_release(Motion.FAST_FORWARD_ACTION)
	Settings.restore(_saved)


func _fresh() -> Node:
	return autofree(load("res://scripts/autoload/settings.gd").new())


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


# --- Defaults and old files ------------------------------------------------------------

func test_new_settings_have_their_defaults() -> void:
	var s := _fresh()
	assert_eq(s.colorblind_mode, &"off")
	assert_false(s.high_contrast)
	assert_false(s.reduce_motion)
	assert_eq(s.resolve_speed, &"x1")
	assert_eq(s.pad_glyph_set, &"auto")
	assert_eq(s.city_quality, -1, "the renderer's own default")
	assert_eq(s.text_scale, 1.0)


func test_defaults_keep_mains_behaviour() -> void:
	Settings.from_dict({})
	assert_true(Motion.camera_moves_allowed(), "cameras move as before")
	assert_true(Motion.parallax_allowed())
	assert_eq(Motion.page_transition_style(), Motion.PAGE_SLIDE, "pages slide as before")
	assert_eq(Motion.resolve_time_scale(), 1.0, "the replay at its own speed")
	var plain := UiTheme.build(1.0)
	var glass := plain.get_stylebox(&"panel", &"GlassPanel") as StyleBoxFlat
	assert_lt(glass.bg_color.a, 1.0, "glass stays glass (no high contrast)")
	Settings.sync_colorblind_layer()
	assert_null(Settings.colorblind_layer, "no correction layer")


func test_an_old_settings_file_without_the_new_keys_loads_unchanged() -> void:
	# A settings.json as main wrote it before ART-0 C (every key it had, none of W9's).
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
	assert_eq(s.city_quality, -1)
	var d: Dictionary = s.to_dict()
	for k in old:
		assert_true(d.has(k), "old key %s still saved" % k)


func test_every_new_setting_round_trips_through_settings_json() -> void:
	var dir := "user://gut_w9_roundtrip_%d" % OS.get_process_id()
	DirAccess.make_dir_recursive_absolute(dir)
	var s := _fresh()
	s.path = dir + "/settings.json"
	s.from_dict({"colorblind_mode": "tritan", "high_contrast": true, "reduce_motion": true,
		"resolve_speed": "instant", "pad_glyph_set": "switch", "city_quality": 1, "text_scale": 2.0})
	assert_eq(s.save_settings(), OK)
	var back := _fresh()
	back.path = s.path
	back.load_settings()
	assert_eq(back.colorblind_mode, &"tritan")
	assert_true(back.high_contrast)
	assert_true(back.reduce_motion)
	assert_eq(back.resolve_speed, &"instant")
	assert_eq(back.pad_glyph_set, &"switch")
	assert_eq(back.city_quality, 1)
	assert_eq(back.text_scale, 2.0, "2.0 survives the file")
	back.from_dict({"colorblind_mode": "sepia", "resolve_speed": "x9", "pad_glyph_set": "atari", "city_quality": 7})
	assert_eq(back.colorblind_mode, &"off", "unknown values fall back to the default")
	assert_eq(back.resolve_speed, &"x1")
	assert_eq(back.pad_glyph_set, &"auto")
	assert_eq(back.city_quality, Settings.CITY_QUALITY_MAX, "a tier past the range clamps")
	DirAccess.remove_absolute(s.path)
	DirAccess.remove_absolute(dir)


func test_the_suite_snapshot_covers_the_new_settings() -> void:
	var snap := Settings.snapshot()
	for k in ["colorblind_mode", "high_contrast", "reduce_motion", "resolve_speed", "pad_glyph_set", "city_quality"]:
		assert_true(snap.has(k), "%s is restored after tests (suite guard)" % k)
	Settings.set_high_contrast(true)
	Settings.set_colorblind_mode(&"protan")
	Settings.restore(snap)
	assert_false(Settings.high_contrast)
	assert_eq(Settings.colorblind_mode, &"off")
	assert_null(Settings.colorblind_layer, "restore takes the layer away too")


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

func _layers() -> int:
	var n := 0
	for c in Settings.get_children():
		if c is ColorblindLayer and not c.is_queued_for_deletion():
			n += 1
	return n


func test_each_colorblind_mode_adds_the_layer_and_off_removes_it() -> void:
	Settings.set_colorblind_mode(&"off")
	assert_null(Settings.colorblind_layer, "off: no layer")
	assert_eq(_layers(), 0, "off: nothing in the tree, no cost")
	for mode in [&"deutan", &"protan", &"tritan"]:
		Settings.set_colorblind_mode(mode)
		var layer: ColorblindLayer = Settings.colorblind_layer
		assert_not_null(layer, "%s adds the layer" % mode)
		assert_true(layer.is_inside_tree())
		assert_eq(layer.layer, ColorblindLayer.LAYER)
		assert_eq(layer.shader_mode(), ColorblindLayer.MODES[mode], "%s drives the shader" % mode)
		assert_eq(Settings.active_colorblind_mode(), mode)
		assert_eq(_layers(), 1, "one layer, reused")
	Settings.set_colorblind_mode(&"off")
	assert_null(Settings.colorblind_layer)
	assert_eq(_layers(), 0, "off frees the layer")
	assert_eq(Settings.active_colorblind_mode(), &"off")


func test_correction_layer_sits_above_the_game_and_below_the_review_filter() -> void:
	assert_gt(ColorblindLayer.LAYER, Fx.layer, "over Fx (and every game layer)")
	assert_lt(ColorblindLayer.LAYER, 128, "under the visual QA simulation filter (layer 128)")
	var layer: ColorblindLayer = autofree(ColorblindLayer.new(&"protan"))
	assert_eq(layer.rect.mouse_filter, Control.MOUSE_FILTER_IGNORE, "never takes a click")
	assert_true(ColorblindLayer.SHADER.code.contains("hint_screen_texture"))


func _separation(a: Color, b: Color, mode: StringName) -> float:
	var sa := ColorblindLayer.simulate(a, mode)
	var sb := ColorblindLayer.simulate(b, mode)
	return Vector3(sa.r - sb.r, sa.g - sb.g, sa.b - sb.b).length()


func test_the_correction_separates_hues_the_deficiency_merges() -> void:
	# Red / green pairs for deutan and protan (Solace green vs a harm red, a gain green vs
	# the harm red: M13's HARM #FF4433 and GAIN #7BE07B, which area E's tokens bring to main),
	# a blue / green pair for tritan: after the correction, the simulated viewer sees them
	# further apart than before.
	var harm := Color("#FF4433")
	var gain := Color("#7BE07B")
	var pairs := {&"deutan": [Palette.CORP_SOLACE, harm], &"protan": [gain, harm], &"tritan": [Palette.NET_CYAN, gain]}
	for mode in pairs:
		var a: Color = pairs[mode][0]
		var b: Color = pairs[mode][1]
		var before := _separation(a, b, mode)
		var after := _separation(ColorblindLayer.correct(a, mode), ColorblindLayer.correct(b, mode), mode)
		assert_gt(after, before, "%s: %.3f -> %.3f" % [mode, before, after])
	assert_eq(ColorblindLayer.correct(Palette.CORP_REBEL_CELL, &"off"), Palette.CORP_REBEL_CELL, "off passes colours through")
	var grey := Color(0.5, 0.5, 0.5)
	var g := ColorblindLayer.correct(grey, &"deutan")
	assert_almost_eq(g.r, grey.r, 0.02, "neutral greys stay (almost) put")
	assert_almost_eq(g.g, grey.g, 0.02)


# --- 3. High contrast -------------------------------------------------------------------

func test_high_contrast_theme_reaches_seven_to_one() -> void:
	var t := UiTheme.build(1.0)
	HighContrast.apply(t)
	for panel in [&"TerminalPanel", &"GlassPanel"]:
		var sb := t.get_stylebox(&"panel", panel) as StyleBoxFlat
		assert_eq(sb.bg_color.a, 1.0, "%s is opaque" % panel)
		assert_eq(sb.shadow_size, 0, "%s has no soft halo" % panel)
		for label in [&"Label", &"HeaderLabel", &"HudLabel"]:
			var c := t.get_color(&"font_color", label)
			assert_gte(HighContrast.contrast(c, sb.bg_color), HighContrast.HC_MIN_CONTRAST, "%s on %s" % [label, panel])
	assert_gte(HighContrast.contrast(t.get_color(&"default_color", &"RichTextLabel"), HighContrast.BG), HighContrast.HC_MIN_CONTRAST)
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
			var floor_ratio := HighContrast.HC_MIN_DISABLED_CONTRAST if state == &"disabled" else HighContrast.HC_MIN_CONTRAST
			assert_gte(HighContrast.contrast(fc, bg), floor_ratio, "%s %s text" % [kind, state])


func test_high_contrast_gives_buttons_and_focus_a_solid_thick_edge() -> void:
	var t := UiTheme.build(1.0)
	HighContrast.apply(t)
	for kind in [&"Button", &"HotButton"]:
		var n := t.get_stylebox(&"normal", kind) as StyleBoxFlat
		assert_gte(n.border_width_left, HighContrast.HC_BUTTON_BORDER, "%s edge" % kind)
		assert_eq(n.border_color.a, 1.0, "%s edge is solid" % kind)
	var f := t.get_stylebox(&"focus", &"Button") as StyleBoxFlat
	assert_eq(f.border_width_left, HighContrast.HC_FOCUS_BORDER, "a 4 px focus edge")
	assert_eq(f.border_color, HighContrast.FOCUS)
	assert_eq(f.shadow_size, 0, "no soft glow")
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
	assert_eq(root.theme.get_color(&"font_color", &"Label"), HighContrast.TEXT)
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


func test_reduce_motion_pages_cross_fade_in_place() -> void:
	Motion.force_live = true
	for reduce in [false, true]:
		Settings.set_reduce_motion(reduce)
		var holder: Control = add_child_autofree(Control.new())
		holder.size = Vector2(400, 300)
		var page: Control = Control.new()
		page.size = Vector2(200, 100)
		holder.add_child(page)
		var helper := PageTransition.enter(page, PageTransition.Look.GLASS)
		assert_not_null(helper, "the entrance plays (forced live)")
		assert_eq(helper.fade_only, reduce, "fade only under reduce motion (%s)" % reduce)
		await _frames(2)
		if reduce:
			assert_eq(page.position, Vector2.ZERO, "no slide: the page fades where it rests")
			assert_null(page.get_node_or_null(^"PageTransition/CrtRoll"), "no CRT roll jump")
		helper.finish()


func test_reduce_motion_shakes_nothing_and_holds_no_camera() -> void:
	Motion.force_live = true
	Settings.set_reduce_motion(true)
	var n: Control = add_child_autofree(Control.new())
	n.position = Vector2(10, 20)
	assert_null(Motion.shake(n, &"hit_shake"), "no shake under reduce motion")
	assert_eq(n.position, Vector2(10, 20))
	Settings.set_reduce_motion(false)
	var tw := Motion.shake(n, &"hit_shake")
	if Motion.live(&"hit_shake"):
		assert_not_null(tw, "the shake plays without it")
	Motion.stop(n)


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
	Settings.reset_keybinds()
	assert_eq(Settings.key_for(Motion.FAST_FORWARD_ACTION), KEY_SHIFT, "reset keeps the default key")
	assert_false(Motion.fast_forward_held(), "not held with no input")
	Input.action_press(Motion.FAST_FORWARD_ACTION)
	assert_true(Motion.fast_forward_held())
	Settings.set_resolve_speed(&"x1")
	assert_eq(Motion.resolve_time_scale_now(), Motion.FAST_FORWARD_TIME_SCALE, "held: faster")
	Input.action_release(Motion.FAST_FORWARD_ACTION)
	assert_false(Motion.fast_forward_held())
	assert_eq(Motion.resolve_time_scale_now(), 1.0)


func test_a_fast_forward_press_never_completes_a_motion() -> void:
	var shift := InputEventKey.new()
	shift.physical_keycode = KEY_SHIFT
	shift.pressed = true
	assert_false(MotionSkip.is_press(shift), "holding fast-forward speeds the replay; it is no skip")
	var other := InputEventKey.new()
	other.physical_keycode = KEY_K
	other.pressed = true
	assert_true(MotionSkip.is_press(other), "any other key still skips")


func test_the_combat_replay_runs_on_the_resolve_clock_and_gives_it_back() -> void:
	var before := Engine.time_scale
	RunManager.save_slot = "gut_w9_clock"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var combat: Control = add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())
	combat.start_fight(&"triage_unit", 7)
	await _frames()
	Settings.set_resolve_speed(&"x2")
	combat._apply_resolve_speed()
	assert_almost_eq(Engine.time_scale, before * 2.0, 0.001, "2x: the clock runs twice as fast")
	Input.action_press(Motion.FAST_FORWARD_ACTION)
	combat._apply_resolve_speed()
	assert_almost_eq(Engine.time_scale, before * Motion.SPEED_MAX, 0.001, "held: 4x")
	Input.action_release(Motion.FAST_FORWARD_ACTION)
	combat.skip_motion()
	assert_eq(Engine.time_scale, before, "a skip gives the clock back")
	Settings.set_resolve_speed(&"x1")
	combat._apply_resolve_speed()
	assert_eq(Engine.time_scale, before, "1x never touches the clock")
	combat.queue_free()
	await _frames()
	assert_eq(Engine.time_scale, before)
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


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


func test_first_run_on_a_steam_deck_defaults_text_scale_and_city_quality() -> void:
	var deck := _fresh()
	deck.apply_first_run_defaults(_probe(true))
	assert_eq(deck.text_scale, Settings.TEXT_SCALE_STEAM_DECK)
	assert_eq(Settings.TEXT_SCALE_STEAM_DECK, 1.2, "§5.4")
	assert_eq(deck.city_quality, Settings.CITY_QUALITY_STEAM_DECK, "§13: medium city on a Deck")
	var pc := _fresh()
	pc.apply_first_run_defaults(_probe())
	assert_eq(pc.text_scale, 1.0, "elsewhere the default stays 1.0")
	assert_eq(pc.city_quality, -1)
	# Only a first run: a Deck with a settings file keeps the player's own scale.
	var dir := "user://gut_w9_deck_%d" % OS.get_process_id()
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
	var plain := _fresh()
	plain.path = dir + "/missing.json"
	plain.load_settings()
	assert_eq(plain.text_scale, 1.0, "a test run never probes the real machine")
	DirAccess.remove_absolute(with_file.path)
	DirAccess.remove_absolute(dir)


# --- 8. Options rows --------------------------------------------------------------------

func _choose(o: OptionButton, i: int) -> void:
	o.select(i)
	o.item_selected.emit(i)


func test_options_rows_drive_the_new_settings() -> void:
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	panel.show_section("Accessibility")
	for w in [panel.colorblind_option, panel.high_contrast_check, panel.reduce_motion_check, panel.resolve_speed_option]:
		assert_true(w.is_inside_tree(), "%s is in Accessibility" % w.name)
		assert_ne(w.focus_mode, Control.FOCUS_NONE, "%s is pad-reachable" % w.name)
	panel.high_contrast_check.button_pressed = true
	assert_true(Settings.high_contrast)
	panel.high_contrast_check.button_pressed = false
	assert_false(Settings.high_contrast)
	panel.reduce_motion_check.button_pressed = true
	assert_true(Settings.reduce_motion)
	panel.reduce_motion_check.button_pressed = false
	_choose(panel.colorblind_option, Settings.COLORBLIND_MODES.find(&"protan"))
	assert_eq(Settings.colorblind_mode, &"protan")
	_choose(panel.colorblind_option, 0)
	assert_eq(Settings.colorblind_mode, &"off")
	_choose(panel.resolve_speed_option, Settings.RESOLVE_SPEEDS.find(&"instant"))
	assert_eq(Settings.resolve_speed, &"instant")
	assert_eq(panel.scale_slider.max_value, 2.0, "the slider reaches 2.0")
	panel.show_section("Controls")
	assert_true(panel.glyph_option.is_inside_tree(), "pad glyphs sit with the controls")
	_choose(panel.glyph_option, Settings.PAD_GLYPH_SETS.find(&"playstation"))
	assert_eq(Settings.pad_glyph_set, &"playstation")
	assert_eq(panel.colorblind_option.item_count, Settings.COLORBLIND_MODES.size(), "one word per mode")
	assert_eq(panel.resolve_speed_option.item_count, Settings.RESOLVE_SPEEDS.size())
	assert_eq(panel.glyph_option.item_count, Settings.PAD_GLYPH_SETS.size())


func test_options_panel_fits_the_screen_at_text_scale_two() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	for section in SettingsPanel.SECTIONS:
		panel.show_section(section)
		await _frames(2)
		assert_lte(panel.get_combined_minimum_size().x, 1280.0, "%s fits the width at 2.0" % section)


func test_new_option_words_have_string_keys_and_no_mouse_wording() -> void:
	var csv := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for word in SettingsPanel.W9_WORDS:
		assert_true(csv.contains(word), "strings.csv has '%s'" % word)
		var lower := String(word).to_lower()
		for mouse_word in ["click", "drag", "mouse"]:
			assert_false(lower.contains(mouse_word), "'%s' has no mouse wording" % word)
