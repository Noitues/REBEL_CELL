extends GutTest
## M14 parity PAUSE-01..03 (designer 2026-10-05): the pause menu blurs and darkens the page
## behind it (GlassScrim) over the HQ, the route and a fight; no PAUSED sticker; `Resume [Esc]`
## is the top left sticker, the one pink one, and takes focus; two columns of stickers in their colours; the
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


func _sticker_in(cell: Node) -> HoloSticker:
	return cell.find_children("*", "HoloSticker", true, false)[0] as HoloSticker


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


func test_two_columns_of_stickers_each_in_its_role_colour() -> void:
	RunManager.new_campaign(1)
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames()
	var resume := menu.resume_button
	assert_eq(resume.sticker.fill, VinylSticker.Fill.PINK, "Resume is the one pink verb")
	assert_eq(resume.name, "Resume")
	assert_eq(UiFocus.first_focusable(menu._menu), resume, "first in the menu (top left)")
	assert_eq(get_viewport().gui_get_focus_owner(), resume, "focused on open")
	assert_eq(menu.resume_hint.text, Settings.hint(&"open_settings"), "its key hint sits with it")
	var left: Array[String] = []
	for c in menu._left.get_children():
		left.append(String(_sticker_in(c).name))
	var right: Array[String] = []
	for c in menu._right.get_children():
		right.append(String(_sticker_in(c).name))
	assert_eq(left, ["Resume", "Options", "Codex"] as Array[String], "left column, top down")
	assert_eq(right, ["AbandonCampaign", "QuitMain", "Quit"] as Array[String], "right column, top down (at HQ)")
	var pinks := 0
	for b in menu._stickers:
		assert_true(b is HoloSticker, "%s is a vinyl sticker" % b.name)
		pinks += 1 if b.sticker.fill == VinylSticker.Fill.PINK else 0
		assert_eq(b.sticker.state, VinylSticker.State.HOVER if b.has_focus() else VinylSticker.State.REST, "%s: coloured, only the focused one lifts" % b.name)
		assert_false(b.sticker.grey > 0.0, "%s is never greyed" % b.name)
	assert_eq(pinks, 1, "one primary")
	assert_eq(menu.abandon_campaign_button.sticker.fill, VinylSticker.Fill.RED, "abandon is harm")
	assert_ne((menu.find_child("Quit", true, false) as HoloSticker).sticker.fill, VinylSticker.Fill.RED, "quit is not destructive")
	var resumed := []
	menu.resumed.connect(func() -> void: resumed.append(true))
	resume.pressed.emit()
	assert_eq(resumed.size(), 1)


func test_a_run_reads_abandon_run_in_the_same_slot() -> void:
	RunManager.new_campaign(1)
	RunManager.start_run()
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames()
	assert_eq(_sticker_in(menu._right.get_child(0)), menu.abandon_run_button, "the top right slot")
	assert_null(menu.abandon_campaign_button)
	assert_eq(menu.abandon_run_button.sticker.fill, VinylSticker.Fill.RED)


func test_focus_order_and_left_right_across_the_columns() -> void:
	RunManager.new_campaign(1)
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames()
	var order: Array[String] = []
	for b in menu._stickers:
		order.append(String(b.name))
	assert_eq(order, ["Resume", "Options", "Codex", "AbandonCampaign", "QuitMain", "Quit"] as Array[String], "left column, right column")
	var resume := menu.resume_button
	assert_eq(resume.get_node(resume.focus_neighbor_right), menu.abandon_campaign_button, "Right crosses to the same row")
	assert_eq(menu.abandon_campaign_button.get_node(menu.abandon_campaign_button.focus_neighbor_left), resume, "and Left comes back")
	var codex := menu.find_child("Codex", true, false) as Control
	assert_eq(codex.get_node(codex.focus_neighbor_right), menu.find_child("Quit", true, false), "row 3 crosses to row 3")


func test_the_grease_pencil_notes_and_their_ink() -> void:
	RunManager.new_campaign(1)
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames(3)
	var notes := {}
	for n in menu._notes:
		notes[n.name] = n
	assert_eq(notes.size(), 4, "Resume's (beside, and the below one held back), abandon's and quit's")
	assert_eq((notes["ResumeNote"] as PencilWords).words, "Down with the Oligarchy!")
	assert_eq((notes["ResumeNoteBelow"] as PencilWords).words, "Down with the Oligarchy!")
	assert_eq((notes["AbandonCampaignNote"] as PencilWords).words, "No Going Back")
	assert_eq((notes["AbandonCampaignNote"] as PencilWords).color, Palette.PENCIL_THREAT, "red grease ink on the harm sticker")
	assert_eq((notes["QuitNote"] as PencilWords).words, "Come Back Soon")
	assert_eq(menu.note_mode, PauseMenu.NoteMode.BESIDE, "at 1.0 Resume's note stands beside its sticker")
	var resume := menu.resume_button
	var beside := notes["ResumeNote"] as PencilWords
	assert_true(beside.visible and not (notes["ResumeNoteBelow"] as PencilWords).visible)
	assert_gte(beside.get_global_rect().position.x, resume.get_global_rect().end.x - 1.0, "to the right of the sticker, never over its word")
	assert_lte(beside.get_global_rect().end.x, menu._right.get_global_rect().position.x + 1.0, "in the gap: clear of the right column")
	assert_gte(menu.resume_hint.get_global_rect().position.y, resume.get_global_rect().end.y - 1.0, "the key hint stays below Resume")
	for n: PencilWords in menu._notes:
		if n == beside or not n.visible:
			continue
		var sticker := _sticker_in(n.get_parent())
		assert_gte(n.get_global_rect().position.y, sticker.get_global_rect().end.y - 1.0, "%s sits under its sticker, never over its word" % n.name)


func test_the_note_wraps_below_then_drops_as_the_text_grows() -> void:
	RunManager.new_campaign(1)
	var modes := {}
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var menu: PauseMenu = add_child_autofree(PauseMenu.new())
		await _frames(3)
		modes[scale] = menu.note_mode
		assert_true(menu.get_global_rect().encloses(menu._columns.get_global_rect()), "x%s: the columns are inside the menu" % scale)
		for n: PencilWords in menu._notes:
			if n.visible:
				for b in menu._stickers:
					assert_false(n.get_global_rect().intersects(b.get_global_rect().grow(-4.0)), "x%s: %s never covers a sticker" % [scale, n.name])
	assert_eq(modes[1.0], PauseMenu.NoteMode.BESIDE)
	assert_eq(modes[2.0], PauseMenu.NoteMode.NONE, "at 2.0 the notes drop")
	assert_ne(modes[1.6], PauseMenu.NoteMode.BESIDE, "at 1.6 the beside note no longer fits: below, or dropped")


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
		assert_lte(body.x, menu.size.x, "x%s: nothing wider than the menu (%s)" % [scale, body])
		for b in menu._stickers:
			assert_true(menu.get_global_rect().encloses(b.get_global_rect()), "x%s: %s is inside the menu" % [scale, b.name])
		if menu.note_mode == PauseMenu.NoteMode.NONE:
			for n in menu._notes:
				assert_false(n.visible, "x%s: dropped notes are all hidden" % scale)
		var code_right := menu.code_field.get_global_rect().end.x
		assert_lte(code_right, menu.get_global_rect().end.x, "x%s: the code field and its copy button fit" % scale)
		assert_true(menu.code_field.copy_button.get_global_rect().size.x > 0.0)
		hq.open_settings()
		hq.queue_free()
		await _frames()
