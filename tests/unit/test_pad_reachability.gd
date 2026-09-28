extends GutTest
## Horizontal pass 6 (GAP_ANALYSIS H6): from the control a panel focuses, every usable
## control must be reachable with the D-pad (walking focus neighbours the way Godot does:
## Control.find_valid_focus_neighbor on the four sides). Covers the HQ start panel, the
## Grid list, netrun rewards, the Modem and combat.

var _pad_before: bool = false


func before_each() -> void:
	_pad_before = Settings.pad_active


## A pushed pad button switches the device to the pad: put it back (Test suite
## optimization: a later script in the same process read pad hints where it expected keys).
func after_each() -> void:
	if Settings.pad_active != _pad_before:
		Settings.set_pad_active(_pad_before)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


## Every usable control under `root` that the D-pad can reach from the current focus.
func _reachable(root: Node) -> Array:
	var start := get_viewport().gui_get_focus_owner()
	assert_not_null(start, "a control has focus")
	if start == null:
		return []
	var seen := {start: true}
	var queue: Array = [start]
	while not queue.is_empty():
		var c: Control = queue.pop_front()
		for side in [SIDE_LEFT, SIDE_RIGHT, SIDE_TOP, SIDE_BOTTOM]:
			var n := c.find_valid_focus_neighbor(side)
			if n != null and not seen.has(n):
				seen[n] = true
				queue.append(n)
	var out := []
	for k in seen:
		if root.is_ancestor_of(k):
			out.append(k)
	return out


func _usable(root: Node, out: Array) -> void:
	for child in root.get_children():
		if child is SpinBox or not (child is Control) or not (child as Control).is_visible_in_tree():
			continue
		if child is BaseButton and not (child as BaseButton).disabled and (child as Control).focus_mode != Control.FOCUS_NONE:
			out.append(child)
		_usable(child, out)


func _assert_all_reachable(panel: Node, label: String) -> void:
	var reach := _reachable(panel)
	var want := []
	_usable(panel, want)
	for c in want:
		assert_true(reach.has(c), "%s: %s '%s' is reachable by pad" % [label, c.get_class(), c.get("text")])


func _begin(slot: String) -> void:
	RunManager.save_slot = slot
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func _end() -> void:
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_hq_start_panel_and_grid_are_pad_reachable() -> void:
	_begin("gut_test_pad_hq")
	var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
	hq.show_start()
	await _frames()
	_assert_all_reachable(hq._panel, "start")
	RunManager.new_campaign(1)
	hq.show_grid()
	await _frames()
	_assert_all_reachable(hq._panel, "grid")
	_end()


func test_rewards_and_modem_are_pad_reachable() -> void:
	_begin("gut_test_pad_netrun")
	RunManager.new_campaign(1)
	var scene: Control = add_child_autofree(load("res://scenes/netrun_map/netrun_scene.tscn").instantiate())
	scene.start_run(1)
	var s := RunManager.netrun
	s.run.pending_rewards.append({"kind": "card", "options": ["whirl", "firewall", "bulwark"]})
	s.run.phase = RunState.Phase.REWARD
	scene._show_current()
	await _frames()
	_assert_all_reachable(scene._panel, "rewards")
	s.run.pending_rewards.clear()
	s.run.cycles = 400
	s._open_shop()
	scene._show_current()
	await _frames()
	_assert_all_reachable(scene._panel, "modem")
	_end()


func test_combat_is_pad_reachable() -> void:
	_begin("gut_test_pad_combat")
	RunManager.new_campaign(1)
	var scene: Control = add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())
	scene.start_fight(&"triage_unit", 7)
	await _frames()
	var reach := _reachable(scene)
	for c in scene._hand_box.get_children():
		if not (c as BaseButton).disabled:
			assert_true(reach.has(c), "card %s reachable" % c.get("card_title"))
	assert_true(reach.has(scene._end_turn_button), "SEND IT reachable")
	# H20: RESPIN and UNDO stand between the hand and SEND IT.
	for key in scene._stickers:
		assert_true(reach.has(scene._stickers[key]), "%s sticker reachable" % key)
	assert_eq(scene._end_turn_button.find_valid_focus_neighbor(SIDE_LEFT), scene._stickers["respin"], "Left from SEND IT reaches the stickers")
	assert_eq(scene._stickers["respin"].find_valid_focus_neighbor(SIDE_LEFT), scene._hand_box.get_child(scene._hand_box.get_child_count() - 1), "and left again returns to the hand")
	_end()


func test_title_options_every_section_is_pad_reachable() -> void:
	var title: Control = add_child_autofree(load("res://scenes/menu/title_scene.tscn").instantiate())
	title.show_options()
	await _frames()
	var settings: SettingsPanel = null
	for n in title.find_children("*", "SettingsPanel", true, false):
		settings = n
	assert_not_null(settings)
	for section in ["Accessibility", "Display", "Audio", "Controls", "Language"]:
		settings.show_section(section)
		await _frames()
		var reach := _reachable(settings)
		var want := []
		_usable(settings, want)
		for c in want:
			assert_true(reach.has(c), "%s: '%s' reachable" % [section, c.get("text")])
		for n in settings.find_children("*", "HSlider", true, false):
			if (n as Control).is_visible_in_tree():
				assert_true(reach.has(n), "%s: slider reachable" % section)


func test_combat_inside_a_netrun_is_pad_reachable() -> void:
	_begin("gut_test_pad_netrun_combat")
	RunManager.new_campaign(1)
	var scene: Control = add_child_autofree(load("res://scenes/netrun_map/netrun_scene.tscn").instantiate())
	scene.start_run(1)
	scene.enter_node(RunManager.netrun.available_nodes()[0])
	await _frames()
	var combat: Control = scene.combat_scene
	assert_not_null(combat)
	assert_true(get_viewport().gui_get_focus_owner() is ZineCard, "entering a fight focuses the hand, not Settings")
	var reach := _reachable(combat)
	for c in combat._hand_box.get_children():
		if not (c as BaseButton).disabled:
			assert_true(reach.has(c))
	assert_true(reach.has(combat._end_turn_button))
	_end()


func test_reference_notes_start_at_the_top_and_take_focus() -> void:
	var note := ZineNote.new("CODEX").make_reference()
	assert_false(note.label.scroll_following)
	assert_eq(note.label.focus_mode, Control.FOCUS_ALL)



func _pad(button: JoyButton) -> void:
	var down := InputEventJoypadButton.new()
	down.button_index = button
	down.pressed = true
	get_viewport().push_input(down)
	var up := down.duplicate() as InputEventJoypadButton
	up.pressed = false
	get_viewport().push_input(up)


func test_a_pad_scrolls_a_long_note_and_leaves_it_at_the_edge() -> void:
	var box := VBoxContainer.new()
	add_child_autofree(box)
	var note := ZineNote.new("CODEX", Vector2(400, 120)).make_reference()
	box.add_child(note)
	for i in 80:
		note.append("line %d of a long codex" % i)
	var after := Button.new()
	after.text = "Back"
	box.add_child(after)
	UiFocus.link_layout(box)
	await _frames()
	note.label.grab_focus()
	await _frames()
	var bar := note.label.get_v_scroll_bar()
	assert_eq(bar.value, 0.0, "starts at the top")
	_pad(JOY_BUTTON_DPAD_DOWN)
	await _frames()
	assert_true(bar.value > 0.0, "D-pad down scrolls the note")
	assert_eq(get_viewport().gui_get_focus_owner(), note.label, "and keeps focus while there is more to read")
	for i in 200:
		_pad(JOY_BUTTON_DPAD_DOWN)
		if get_viewport().gui_get_focus_owner() != note.label:
			break
	await _frames()
	assert_eq(get_viewport().gui_get_focus_owner(), after, "at the bottom, down moves on")


## ANIM-R4 H1: the HQ menu is a column: from the first focus the D-pad reaches every item
## (City Grid, RAID PENDING, Scrub Heat, Codex, Settings, Save) when no operative is alive
## (no crew orders to walk through) and with a raid pending, at every text size.
func test_hq_menu_is_pad_reachable_with_no_crew_and_a_raid_pending() -> void:
	var scale_before := Settings.text_scale
	for raid in [false, true]:
		for scale in [1.0, 1.3, 1.6]:
			_begin("gut_test_pad_hq_menu")
			Settings.set_text_scale(scale)
			RunManager.new_campaign(1)
			var c := RunManager.campaign
			for op in c.roster:
				op.alive = false
			if raid:
				CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")
			var holder: Control = add_child_autofree(Control.new())
			holder.size = Vector2(1280, 720)
			var hq: Control = load("res://scenes/hq/hq_scene.tscn").instantiate()
			holder.add_child(hq)
			hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			hq.show_hq()
			await _frames()
			var label := "hq %s raid=%s" % [scale, raid]
			_assert_all_reachable(hq._panel, label)
			var names := ["CityGrid", "ScrubHeat", "SettingsButton", "SaveButton"]
			if raid:
				names.append("RaidPending")
			var reach := _reachable(hq._panel)
			for n in names:
				var b: Node = hq._panel.find_child(n, true, false)
				assert_not_null(b, "%s: %s shown" % [label, n])
				assert_true(reach.has(b), "%s: %s reachable by pad" % [label, n])
			# The menu walks down item by item.
			var grid: Control = hq._panel.find_child("CityGrid", true, false)
			var below := grid.find_valid_focus_neighbor(SIDE_BOTTOM)
			assert_true(below != null and below.get_parent() == grid.get_parent(), "%s: down from City Grid is the next menu item (%s)" % [label, below.name if below != null else "none"])
			holder.queue_free()
			await _frames(1)
			_end()
	Settings.set_text_scale(scale_before)
