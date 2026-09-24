extends GutTest
## Title screen, save slots, pause menu, confirm dialogs and the tutorial overlay
## (gap analysis 2.5). Scene switching is off so nothing replaces the test runner.

const TITLE := "res://scenes/menu/title_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const COMBAT := "res://scenes/combat/combat_scene.tscn"

var _saved_settings: Dictionary


func before_each() -> void:
	AudioDirector.muted = true
	_saved_settings = Settings.to_dict()
	RunManager.scene_switching_enabled = false
	for slot in ["gut_a", "gut_b"]:
		RunManager.delete_slot(slot)
	RunManager.save_slot = "gut_test"
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	AudioDirector.muted = false
	for slot in ["gut_a", "gut_b"]:
		RunManager.delete_slot(slot)
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true
	RunManager.pending_tutorial = false
	Settings.from_dict(_saved_settings)
	Settings.save_settings()


func test_title_shows_main_menu_slots_codex_stats_and_options() -> void:
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	assert_eq(title.panel_name, "main")
	title.show_slots()
	assert_eq(title.panel_name, "slots")
	title.show_codex()
	assert_eq(title.panel_name, "codex")
	title.show_stats()
	assert_eq(title.panel_name, "stats")
	title.show_options()
	assert_eq(title.panel_name, "options")
	title.show_main()
	title.confirm_quit()
	assert_true(title.confirm_visible(), "quit asks first")
	title._confirm.no_button.pressed.emit()
	await get_tree().process_frame
	assert_false(title.confirm_visible())


func test_save_slots_are_independent_listed_and_deletable() -> void:
	RunManager.save_slot = "gut_a"
	RunManager.new_campaign(4)
	RunManager.campaign.heat = 33
	RunManager.autosave()
	RunManager.save_slot = "gut_b"
	RunManager.new_campaign(5, &"solace", 2)
	RunManager.autosave()
	var slots := SaveService.list_campaign_slots()
	assert_true(slots.has("gut_a") and slots.has("gut_b"))
	var a := RunManager.slot_summary("gut_a")
	assert_eq(int(a["heat"]), 33)
	assert_eq(a["state"], "active")
	assert_eq(int(RunManager.slot_summary("gut_b")["ice"]), 2)
	assert_eq(RunManager.slot_summary("gut_nothing"), {})
	assert_eq(RunManager.latest_slot(), "gut_b", "saved last")
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	title.load_slot("gut_a")
	assert_eq(RunManager.save_slot, "gut_a")
	assert_eq(RunManager.campaign.heat, 33)
	title.confirm_delete("gut_a")
	assert_true(title.confirm_visible())
	title._confirm.yes_button.pressed.emit()
	assert_false(SaveService.list_campaign_slots().has("gut_a"))
	assert_null(RunManager.campaign, "the loaded slot was deleted")
	title.new_in_slot("gut_a")
	assert_eq(RunManager.save_slot, "gut_a")


func test_pause_menu_opens_from_hq_with_options_and_codex() -> void:
	var hq: Control = add_child_autofree(load(HQ).instantiate())
	hq.new_campaign(2)
	hq.open_settings()
	assert_not_null(hq._settings_panel)
	assert_true(hq._settings_panel is PauseMenu)
	var menu: PauseMenu = hq._settings_panel
	menu.show_options()
	assert_not_null(menu.settings_panel)
	menu.show_codex()
	assert_null(menu.settings_panel, "options closed when the codex opens")
	assert_not_null(menu.codex_note)
	assert_true(menu.codex_note.label.get_parsed_text().contains("Lexicon"))
	watch_signals(menu)
	menu.resumed.emit()
	assert_null(hq._settings_panel, "resumed closes the menu")
	hq.open_settings()
	hq._settings_panel.quit_to_title.emit()
	assert_null(hq._settings_panel)


func test_tutorial_overlay_advances_on_events_and_skip_marks_it_done() -> void:
	Settings.set_tutorial_done(false)
	RunManager.pending_tutorial = true
	var scene: Control = add_child_autofree(load(COMBAT).instantiate())
	assert_not_null(scene.tutorial, "pending tutorial starts it")
	assert_false(RunManager.pending_tutorial)
	var t: TutorialOverlay = scene.tutorial
	assert_eq(t.current_title(), "THE WHEEL")
	t.advance()
	assert_eq(t.current_title(), "PRECISION")
	scene.nudge(1)
	assert_eq(t.current_title(), "RESISTANCE", "a nudge advances the precision step")
	t.advance()
	assert_eq(t.current_title(), "CARDS & PREVIEW")
	scene.play_card(0)
	assert_eq(t.current_title(), "REWIND")
	scene.rewind()
	assert_eq(t.current_title(), "SEND IT", "a rewind advances")
	scene.end_turn()
	assert_eq(t.current_title(), "HEAT & BANKING")
	t.skip()
	await get_tree().process_frame
	assert_true(Settings.tutorial_done)
	assert_null(scene.tutorial)
