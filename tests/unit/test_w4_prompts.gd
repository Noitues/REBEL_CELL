extends GutTest
## W4-PROMPTS (D-UX2 / D-UX3 / D-UX4): one prompt look read from InputMap, the Menu button on the top bar, an
## outside click closes a menu and nothing else.

const COVERED := [
	"res://scripts/ui/kit/pause_menu.gd", "res://scripts/ui/kit/settings_panel.gd",
	"res://scripts/ui/kit/deck_view.gd", "res://scripts/ui/kit/combat_legend.gd", "res://scripts/ui/kit/hud_bar.gd",
]


func after_each() -> void:
	Settings.set_pad_active(false)


func test_covered_screens_draw_prompts_only_through_the_helper() -> void:
	for path in COVERED:
		var src := FileAccess.get_file_as_string(path)
		assert_false(src.contains("Settings.hint("), "%s builds no prompt text of its own" % path)


func test_chip_glyph_is_the_input_map_binding() -> void:
	for action in [&"ui_cancel", &"open_settings", &"end_turn", &"nudge_left"]:
		var chip := InputPrompt.make_chip(action)
		add_child_autofree(chip)
		assert_eq(InputPrompt.chip_label(chip).text, Settings.hint(action).to_upper(), "%s" % action)
		assert_eq(chip.get_meta(InputPrompt.META_ACTION), action)
	var pair := InputPrompt.make_pair(&"ui_cancel", "Back")
	add_child_autofree(pair)
	assert_not_null(pair.find_child(InputPrompt.CHIP_NAME, true, false), "a pair carries the same chip")


func test_chip_follows_the_device() -> void:
	var chip := InputPrompt.make_chip(&"open_settings")
	add_child_autofree(chip)
	var keys := InputPrompt.chip_label(chip).text
	Settings.set_pad_active(true)
	assert_eq(InputPrompt.chip_label(chip).text, InputPrompt.chip_text(&"open_settings"))
	assert_ne(InputPrompt.chip_label(chip).text, keys, "the pad's button replaces the key")


func test_hud_bar_has_the_menu_button_left_of_the_heat_gauge() -> void:
	var bar := HudBar.new()
	add_child_autofree(bar)
	var row := bar.heat_gauge.get_parent()
	assert_lt(bar.menu_button.get_index(), bar.heat_gauge.get_index(), "Menu sits before the Heat gauge")
	assert_eq(bar.menu_button.get_parent(), row)
	var seen: Array[bool] = [false]
	bar.menu_pressed.connect(func() -> void: seen[0] = true)
	bar.menu_button.pressed.emit()
	assert_true(seen[0], "pressing Menu asks the screen for the pause menu")


func test_outside_click_closes_a_menu_but_not_a_dialog_or_page() -> void:
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	assert_true(PauseMenu.outside_click_closes(click, false, false))
	assert_false(PauseMenu.outside_click_closes(click, true, false), "an open confirm keeps the menu")
	assert_false(PauseMenu.outside_click_closes(click, false, true), "an open page keeps the menu")
	click.button_index = MOUSE_BUTTON_RIGHT
	assert_false(PauseMenu.outside_click_closes(click, false, false), "only the left button")
	var release := InputEventMouseButton.new()
	release.button_index = MOUSE_BUTTON_LEFT
	assert_false(PauseMenu.outside_click_closes(release, false, false), "a release is not a click")


func test_backdrop_click_resumes_the_real_menu() -> void:
	var menu := PauseMenu.new()
	add_child_autofree(menu)
	await get_tree().process_frame
	var got: Array[bool] = [false]
	menu.resumed.connect(func() -> void: got[0] = true)
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	menu._backdrop.gui_input.emit(click)
	assert_true(got[0], "the backdrop closes the menu")
