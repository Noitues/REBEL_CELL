extends GutTest
## Options beyond accessibility (gap analysis 2.5): display, audio, key rebinding,
## language and the tutorial flag persist; rebinding drives the InputMap; the fps
## counter follows its setting; achievements and profile stats round-trip.

var _saved: Dictionary


func before_each() -> void:
	_saved = Settings.to_dict()


func after_each() -> void:
	Settings.from_dict(_saved)
	Settings.apply_keybinds()
	Settings.reset_keybinds()
	Settings.save_settings()
	Fx.apply_settings()


func test_display_audio_language_and_tutorial_settings_round_trip() -> void:
	Settings.set_window_mode(Settings.WindowMode.FULLSCREEN)
	Settings.set_resolution(Vector2i(1920, 1080))
	Settings.set_vsync(false)
	Settings.set_master_volume(0.5)
	Settings.set_tutorial_done(true)
	var d := Settings.to_dict()
	assert_eq(int(d["window_mode"]), Settings.WindowMode.FULLSCREEN)
	assert_eq(d["resolution"], [1920, 1080])
	assert_false(bool(d["vsync"]))
	assert_almost_eq(float(d["master_volume"]), 0.5, 0.001)
	assert_true(bool(d["tutorial_done"]))
	var fresh := Settings.to_dict()
	Settings.from_dict({})
	assert_eq(Settings.window_mode, Settings.WindowMode.WINDOWED, "defaults")
	assert_eq(Settings.resolution, Vector2i(1280, 720))
	Settings.from_dict(fresh)
	assert_eq(Settings.resolution, Vector2i(1920, 1080))
	assert_eq(Settings.language, "en")
	assert_true(Settings.available_languages().has("en"))


func test_rebinding_changes_the_input_map_and_persists() -> void:
	assert_eq(Settings.key_for(&"nudge_left"), KEY_Q)
	Settings.rebind(&"nudge_left", KEY_A)
	assert_eq(Settings.key_for(&"nudge_left"), KEY_A)
	assert_eq(int(Settings.to_dict()["keybinds"]["nudge_left"]), KEY_A)
	var ev := InputEventKey.new()
	ev.physical_keycode = KEY_A
	ev.pressed = true
	assert_true(InputMap.event_is_action(ev, &"nudge_left"))
	Settings.rebind(&"card_1", KEY_B)
	assert_false(Settings.to_dict()["keybinds"].has("card_1"), "card keys are not rebindable")
	Settings.reset_keybinds()
	assert_eq(Settings.key_for(&"nudge_left"), KEY_Q, "defaults restored")
	assert_eq(Settings.to_dict()["keybinds"].size(), 0)
	# Rewind keeps its Ctrl+Z variant is not required, but the plain key is rebound.
	Settings.rebind(&"rewind", KEY_U)
	assert_eq(Settings.key_for(&"rewind"), KEY_U)


func test_fps_counter_follows_the_setting() -> void:
	Settings.set_show_fps(true)
	assert_true(Fx.fps_label.visible)
	Fx._process(0.016)
	assert_true(Fx.fps_label.text.ends_with("fps"))
	Settings.set_show_fps(false)
	assert_false(Fx.fps_label.visible)
	Fx.show_saved()
	assert_almost_eq(Fx.saved_label.modulate.a, 1.0, 0.001, "autosave indicator lit")


func test_settings_panel_sections_and_rebind_capture() -> void:
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	for section in SettingsPanel.SECTIONS:
		panel.show_section(section)
		assert_eq(panel.section, section)
	panel.show_section("Controls")
	panel.begin_rebind(&"end_turn")
	assert_eq(panel.rebinding, &"end_turn")
	var ev := InputEventKey.new()
	ev.physical_keycode = KEY_ENTER
	ev.pressed = true
	assert_true(panel.handle_key(ev))
	assert_eq(Settings.key_for(&"end_turn"), KEY_ENTER)
	assert_eq(panel.rebinding, &"")
	panel.begin_rebind(&"end_turn")
	var esc := InputEventKey.new()
	esc.physical_keycode = KEY_ESCAPE
	esc.pressed = true
	assert_true(panel.handle_key(esc))
	assert_eq(Settings.key_for(&"end_turn"), KEY_ENTER, "Escape cancels without rebinding")


func test_achievements_are_earned_once_and_profile_extras_round_trip() -> void:
	var p := ProfileState.new()
	assert_eq(Achievements.check(p).size(), 0)
	p.runs_completed = 1
	assert_eq(Achievements.check(p), [&"first_blood"])
	p.add_achievement(&"first_blood")
	assert_eq(Achievements.check(p).size(), 0, "not earned twice")
	var c := CampaignState.new()
	c.outcome = CampaignState.Outcome.WON
	c.ice_level = 5
	c.deaths = 0
	c.thresholds_fired = [100]
	p.campaigns_won = 1
	var earned := Achievements.check(p, c)
	for id in [&"breach", &"clean_hands", &"ice_5", &"purge_survivor"]:
		assert_true(earned.has(id), String(id))
	assert_false(earned.has(&"ice_10"))
	assert_false(earned.has(&"final_final"), "REBEL_CELL is not built yet")
	p.add_stat("perfects", 500)
	p.add_stat("racks", 10)
	p.record_run({"corporation": "solace", "tier": 1, "site": "t1_a", "outcome": "completed", "cycles": 40, "banked": 10})
	var again := ProfileState.from_dict(p.to_dict())
	assert_eq(again.achievements, [&"first_blood"])
	assert_eq(int(again.stats["perfects"]), 500)
	assert_eq(again.run_history.size(), 1)
	assert_eq(int(again.run_history[0]["cycles"]), 40)
	assert_true(Achievements.check(again).has(&"perfectionist"))
	assert_true(Achievements.check(again).has(&"banked"))
	assert_eq(Achievements.definition(&"breach")["title"], "Breach")
	for i in 25:
		p.record_run({"cycles": i})
	assert_eq(p.run_history.size(), ProfileState.RUN_HISTORY_CAP)
