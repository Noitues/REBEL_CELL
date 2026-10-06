extends GutTest
## M14 parity PAUSE-01..03 (designer 2026-10-05): the pause menu blurs and darkens the page
## behind it (GlassScrim) over the HQ, the route and a fight; no PAUSED sticker; `Resume [Esc]`
## is the first row, the one pink sticker, and takes focus; the other rows carry icons; the
## campaign code sits in a field whose copy button copies it; it all fits at every text scale.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _text_scale_before: float = 1.0
var _copied: Array[String] = []


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	RunManager.save_slot = "gut_test_parity_pause"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	_copied.clear()
	CodeField.clipboard_writer = func(t: String) -> void: _copied.append(t)  # headless has no clipboard


func after_each() -> void:
	CodeField.clipboard_writer = Callable()
	Settings.set_text_scale(_text_scale_before)
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _assert_scrim(menu: PauseMenu, where: String) -> void:
	var back := menu.get_node("Backdrop") as GlassScrim
	assert_not_null(back, "%s: the backdrop is a GlassScrim" % where)
	if back == null:
		return
	assert_false(back.opaque(), "%s: blurred, not opaque" % where)
	assert_eq(back.mouse_filter, Control.MOUSE_FILTER_STOP, "%s: it eats the clicks meant for the page" % where)
	assert_eq(back.get_index(), 0, "%s: drawn behind the menu" % where)
	assert_true(back.get_global_rect().encloses(get_viewport().get_visible_rect()), "%s: over the whole page" % where)
	assert_eq(back.material, GlassScrim.shared_material(), "%s: the shared blur and dim" % where)
	assert_null(menu.find_child("TitleSticker", true, false), "%s: no PAUSED sticker" % where)


func test_the_pause_menu_has_a_scrim_over_the_hq() -> void:
	var hq: Control = add_child_autofree(load(HQ).instantiate())
	await _frames()
	hq.open_settings()
	await _frames()
	_assert_scrim(hq._settings_panel, "HQ")
	hq.open_settings()


func test_the_pause_menu_has_a_scrim_over_the_route_and_a_fight() -> void:
	var scene: Control = add_child_autofree(load(NETRUN).instantiate())
	scene.start_run(1)
	await _frames()
	scene.open_settings()
	await _frames()
	_assert_scrim(scene._settings_panel, "route")
	scene.open_settings()
	scene.enter_node(RunManager.netrun.available_nodes()[0])
	await _frames()
	var combat: Control = scene.combat_scene
	combat.open_settings()
	await _frames()
	_assert_scrim(combat._settings_panel, "fight")
	combat.open_settings()


func test_a_fight_alone_pauses_over_a_scrim() -> void:
	var scene: Control = add_child_autofree(load(COMBAT).instantiate())
	scene.start_fight(&"triage_unit", 7)
	scene.open_settings()
	await _frames()
	_assert_scrim(scene._settings_panel, "fight")
	scene.open_settings()


func test_resume_is_first_pink_and_focused_and_the_rows_have_icons() -> void:
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames()
	var resume := menu.resume_button as VerbSticker
	assert_not_null(resume, "Resume is a verb sticker")
	assert_eq(resume.fill, VerbSticker.Fill.PINK, "the one pink primary")
	assert_eq(resume.name, "Resume")
	assert_string_starts_with(resume.text, "Resume")
	assert_string_contains(resume.text, Settings.hint(&"open_settings"), "its key shows")
	assert_eq(UiFocus.first_focusable(menu._menu), resume, "first in the menu")
	assert_eq(get_viewport().gui_get_focus_owner(), resume, "focused on open")
	var kinds: Array[StringName] = []
	for b in menu._rows.get_children():
		kinds.append(StringName(b.get_meta(&"icon_kind", &"")))
	assert_eq(kinds, [StatIcon.SETTINGS, StatIcon.CODEX, StatIcon.SAVE, StatIcon.QUIT], "an icon on every other row")
	var resumed := []
	menu.resumed.connect(func() -> void: resumed.append(true))
	resume.pressed.emit()
	assert_eq(resumed.size(), 1)


func test_the_campaign_code_has_a_field_and_a_copy_button() -> void:
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames()
	assert_not_null(menu.code_field, "the code field")
	var code := PauseMenu.share_code()
	assert_ne(code, "")
	assert_eq(menu.code_field.value, code)
	assert_true(menu.code_field.read_only)
	assert_eq(menu.code_field.copy_button.get_meta(&"icon_kind"), StatIcon.COPY, "the copy icon")
	menu.code_field.copy_button.pressed.emit()
	assert_eq(_copied, [code], "the button copied the code to the clipboard")


func test_the_pause_menu_fits_at_every_text_scale() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var hq: Control = load(HQ).instantiate()
		add_child(hq)
		await _frames()
		hq.open_settings()
		await _frames(4)
		var menu: PauseMenu = hq._settings_panel
		var view := get_viewport().get_visible_rect()
		assert_true(view.encloses(menu.get_global_rect()), "x%s: the menu %s is on the %s screen" % [scale, menu.get_global_rect(), view])
		var body := menu._host.get_combined_minimum_size()
		assert_lte(body.x, menu.size.x, "x%s: nothing wider than the menu" % scale)
		var code_right := menu.code_field.get_global_rect().end.x
		assert_lte(code_right, menu.get_global_rect().end.x, "x%s: the code field and its copy button fit" % scale)
		assert_true(menu.code_field.copy_button.get_global_rect().size.x > 0.0)
		hq.open_settings()
		hq.queue_free()
		await _frames()
