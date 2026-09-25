extends GutTest
## Horizontal pass 4 fixes (GAP_ANALYSIS H4): focus survives card plays, Tab stays Cycle
## target, modals take and give back focus, the start panel is pad-reachable, and a built
## REBEL_CELL's elite pool holds on resume and special runs.

var _cfg: CampaignConfigData


func before_all() -> void:
	_cfg = CombatFixture.config()


func _frames(n: int = 2) -> void:
	for i in n:
		await get_tree().process_frame


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


func test_focus_survives_a_card_play() -> void:
	_begin("gut_test_focus_play")
	RunManager.new_campaign(1)
	var scene: Control = add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())
	scene.start_fight(&"triage_unit", 7)
	await _frames()
	scene.play_card(0)
	await _frames(3)
	var owner := get_viewport().gui_get_focus_owner()
	assert_not_null(owner, "something still has focus after the hand rebuilt")
	assert_false(owner.is_queued_for_deletion())
	_end()


func test_tab_cycles_targets_not_focus() -> void:
	var tab_on_cycle := false
	for ev in InputMap.action_get_events(&"cycle_target"):
		tab_on_cycle = tab_on_cycle or (ev is InputEventKey and ((ev as InputEventKey).physical_keycode == KEY_TAB or (ev as InputEventKey).keycode == KEY_TAB))
	assert_true(tab_on_cycle, "Tab is Cycle target")
	for ev in InputMap.action_get_events(&"ui_focus_next"):
		if ev is InputEventKey and not (ev as InputEventKey).shift_pressed:
			assert_ne((ev as InputEventKey).keycode, KEY_TAB)
			assert_ne((ev as InputEventKey).physical_keycode, KEY_TAB)


func test_the_pause_menu_takes_and_returns_focus() -> void:
	var holder := Button.new()
	holder.text = "hand"
	add_child_autofree(holder)
	holder.grab_focus()
	var menu := PauseMenu.new()
	add_child_autofree(menu)
	await _frames()
	var owner := get_viewport().gui_get_focus_owner()
	assert_true(owner != null and menu.is_ancestor_of(owner), "the menu focuses its own button")
	menu.visible = false
	await _frames()
	assert_eq(get_viewport().gui_get_focus_owner(), holder, "focus goes back to where it was")


func test_confirm_dialogs_focus_no() -> void:
	var d := ConfirmDialog.new("Really?")
	add_child_autofree(d)
	await _frames()
	assert_eq(get_viewport().gui_get_focus_owner(), d.no_button)


func test_the_start_panel_ice_and_seed_are_pad_reachable() -> void:
	_begin("gut_test_ice_pad")
	var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
	hq.show_start()
	await _frames()
	var spin := hq.find_child("IceSpin", true, false) as SpinBox
	var up := hq.find_child("IceUp", true, false) as Button
	var seed := hq.find_child("SeedSpin", true, false) as SpinBox
	var next := hq.find_child("SeedNext", true, false) as Button
	assert_true(up != null and next != null)
	up.pressed.emit()
	assert_eq(int(spin.value), 1)
	next.pressed.emit()
	assert_eq(int(seed.value), 2)
	_end()


func test_a_built_rebel_cell_pool_holds_on_resume_and_special_runs() -> void:
	var template := ContentRegistry.get_content(&"rebel_cell") as CorporationData
	var lookup := GridFixture.lookup()
	var stale := RebelCellBuilder.build(template, {"classes": ["breaker"], "daemons": [], "nodes": ["relay"], "assets": ["turret"]}, lookup)
	lookup.add(stale)
	var corp := RebelCellBuilder.build(template, {"classes": ["rigger"], "daemons": [], "nodes": ["relay"], "assets": ["turret"]}, lookup)
	lookup.add(corp)
	var resolver := CombatResolver.new(_cfg, lookup)
	var c := CampaignRules.new_campaign(corp, _cfg, lookup, 3, ContentRegistry.get_content(&"rigger") as ClassData, GridFixture.home_node())
	var s := NetrunSession.start(resolver, c, c.roster[0].id, 1, &"r1_a", 5, corp)
	var back := NetrunSession.from_dict(resolver, c, s.to_dict(), corp)
	assert_eq(back.pools()["elites"], [&"rc_mirror_rigger"], "resume")
	var special := NetrunSession.start_special(resolver, c, c.roster[0].id, "reclaim", &"r1_a", 1, 5, &"echo_process", {}, corp)
	assert_eq(special.pools()["elites"], [&"rc_mirror_rigger"], "special run")
