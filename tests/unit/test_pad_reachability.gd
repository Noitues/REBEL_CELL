extends GutTest
## Horizontal pass 6 (GAP_ANALYSIS H6): from the control a panel focuses, every usable
## control must be reachable with the D-pad (walking focus neighbours the way Godot does:
## Control.find_valid_focus_neighbor on the four sides). Covers the HQ start panel, the
## Grid list, netrun rewards, the Modem and combat.


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
	assert_eq(scene._end_turn_button.find_valid_focus_neighbor(SIDE_LEFT), scene._hand_box.get_child(scene._hand_box.get_child_count() - 1), "Left from SEND IT returns to the hand")
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
