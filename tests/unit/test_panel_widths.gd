extends GutTest
## Horizontal pass 9 (GAP_ANALYSIS H9): with everything unlocked and a full roster, no HQ
## panel is wider than the 1280-wide screen (rows wrap instead of running off screen).

const SCREEN_WIDTH := 1280.0


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _check(hq: Control, label: String) -> void:
	var w: float = hq._panel.get_combined_minimum_size().x
	assert_true(w <= SCREEN_WIDTH, "%s panel is %d px wide (max %d)" % [label, w, SCREEN_WIDTH])


func test_hq_panels_fit_the_screen_with_everything_unlocked() -> void:
	RunManager.save_slot = "gut_test_widths"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	var p := RunManager.profile
	for id in RunManager.lookup().ids_of_class(&"ProfileUnlockData"):
		p.add_unlock(id)
	for id in ["solace", "meridian", "halcyon", "orbital", "rebel_cell"]:
		p.best_ice_by_corp[id] = 10
	p.best_ice = 10
	var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
	hq.show_start()
	await _frames()
	_check(hq, "start")
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	for id in RunManager.lookup().ids_of_class(&"ClassData"):
		c.recruit(RunManager.lookup().get_content(id) as ClassData)
	c.schematics = 999
	hq.show_hq()
	await _frames()
	_check(hq, "HQ")
	hq.show_codex()
	await _frames()
	_check(hq, "codex")
	hq.show_grid()
	await _frames()
	_check(hq, "grid")
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
