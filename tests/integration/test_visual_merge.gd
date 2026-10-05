extends GutTest
## Merge of the visual/UI pass into main (DECISIONS "Merge: visual pass + H17-H19"): the
## sticker controls and SEND IT carry the bound keys and follow a rebind; stickers and
## intent tags never lie on a wheel at text scale 1.0 or 1.6; the docked combat subtitle
## pages long lines so it never reaches a wheel; the pause menu keeps its click-eating
## backdrop on the terminal panel; the new Options switches persist.

var _text_scale_before: float = 1.0
var _legend_before: bool = true
var _log_before: bool = false
var _pad_before: bool = false

const LONG_LINE := "Runner, the compliance office has flagged your cell for audit. Keep the needle off the NULL slice, bank the Rack before the auditors land, and do not let the Heat climb past the next threshold or the whole district locks down for a week."


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_legend_before = Settings.map_legend
	_log_before = Settings.system_log


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_visual_merge"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	# The key hints are keyboard hints (a pad left active by an earlier script shows R3).
	_pad_before = Settings.pad_active
	Settings.set_pad_active(false)


func after_each() -> void:
	Settings.set_pad_active(_pad_before)
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	if Settings.map_legend != _legend_before:
		Settings.set_map_legend(_legend_before)
	if Settings.system_log != _log_before:
		Settings.set_system_log(_log_before)
	Settings.reset_keybinds()
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


func _combat(scale: float) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load("res://scenes/combat/combat_scene.tscn").instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"compliance_officer", 5)
	await _frames()
	return scene


func test_stickers_and_send_it_show_the_bound_keys() -> void:
	var scene := await _combat(1.0)
	for key in scene.STICKER_ACTIONS:
		var action: StringName = scene.STICKER_ACTIONS[key]
		assert_string_contains(scene._stickers[key].text, "[%s]" % Settings.key_text(action), "%s sticker names its key" % key)
	assert_eq(scene._end_turn_button.key_hint, "[%s]" % Settings.key_text(&"end_turn"))
	Settings.rebind(&"respin", KEY_G)
	Settings.rebind(&"end_turn", KEY_B)
	await _frames()
	assert_string_contains(scene._stickers["respin"].text, "[%s]" % OS.get_keycode_string(KEY_G), "a rebind shows on the sticker at once")
	assert_eq(scene._end_turn_button.key_hint, "[%s]" % OS.get_keycode_string(KEY_B), "and under SEND IT")


func test_stickers_and_intent_tags_stay_off_the_wheels_at_every_text_scale() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(scale)
		assert_eq(scene.layout_violations(), [], "text scale %.1f" % scale)
		# ART-2 2D (D15): the forecast is the result chips beside the HP, not a tag.
		assert_true(scene._player_view.hud_results and not scene._player_view.intent_rect().has_area(), "the player's forecast is its chips")
		assert_not_null(scene.chip_row(&"player"), "the player spinner has its result chips")
		for key in scene._stickers:
			assert_true(scene._stickers[key].get_global_rect().position.y >= scene._hand_box.get_global_rect().position.y, "H20: the %s sticker sits by SEND IT, under the arena" % key)


func test_the_combat_subtitle_pages_and_never_reaches_a_wheel() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(scale)
		Dialogue.say(RC.Voice.DISPATCH, LONG_LINE)
		await _frames()
		# H20: the dock is the right column's free area; layout_violations checks the bar
		# against every wheel's drawing and every tag while it shows.
		assert_true(Dialogue.bar.visible)
		assert_eq(scene.layout_violations(), [], "subtitles clear of the wheels and tags at %.1f" % scale)
		assert_true(Dialogue.pages_of(LONG_LINE).size() >= 2, "a long line is paged")
		assert_true(LONG_LINE.begins_with(Dialogue.current_text().strip_edges()), "the first page shows first")
		assert_eq(Dialogue.history[-1]["text"], LONG_LINE, "the history keeps the whole line")
		Dialogue.clear()


## H20: the default dock (the old bottom bar moved to the top band) pages long lines to
## the lines that fit, so it never grows over a control.
func test_the_default_dock_pages_to_the_lines_that_fit() -> void:
	Dialogue.dock_bottom()
	assert_true(Dialogue.dock_lines >= 1, "paged")
	assert_true(Dialogue.pages_of(LONG_LINE).size() >= 2, "a long line is shown in pages")


func test_the_pause_menu_keeps_its_backdrop_on_the_terminal_panel() -> void:
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames(2)
	var backdrop := menu.get_node("Backdrop") as ColorRect
	assert_not_null(backdrop, "H17 backdrop")
	assert_eq(backdrop.mouse_filter, Control.MOUSE_FILTER_STOP)
	var terminal := false
	for c in menu.get_children():
		terminal = terminal or c is CrtWindow  # ART-10 4C: the v2 terminal (1B's glass)
	assert_true(terminal, "the menu is terminal glass (visual pass)")


func test_map_legend_and_system_log_round_trip() -> void:
	Settings.set_map_legend(not _legend_before)
	Settings.set_system_log(not _log_before)
	var d := Settings.to_dict()
	assert_eq(d["map_legend"], not _legend_before)
	assert_eq(d["system_log"], not _log_before)
	Settings.from_dict({})
	assert_true(Settings.map_legend, "default on")
	assert_false(Settings.system_log, "default off")
	Settings.from_dict(d)
	assert_eq(Settings.map_legend, not _legend_before)
	assert_eq(Settings.system_log, not _log_before)
