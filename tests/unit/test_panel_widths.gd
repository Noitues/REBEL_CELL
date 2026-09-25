extends GutTest
## Horizontal pass 9 (GAP_ANALYSIS H9): with everything unlocked and a full roster, no HQ
## panel is wider than the 1280-wide screen (rows wrap instead of running off screen).

const SCREEN_WIDTH := 1280.0


var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


## A failed width test must not leave the player's text scale changed.
func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)

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



func test_the_mid_run_raid_screen_fits_the_screen() -> void:
	RunManager.save_slot = "gut_test_widths_raid"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var grid_data := RunManager.corporation.city_grid
	var claimed := 0
	for sd in grid_data.sites:
		if sd.tier == 1 and sd.id != grid_data.home_site_id and sd.objective == RC.SiteObjective.NONE and claimed < 6:
			var s := c.grid.site(sd.id)
			s["status"] = GridState.SiteStatus.CLAIMED
			s["node_type"] = "firewall_relay"
			s["integrity"] = 30
			s["max_integrity"] = 30
			s["assets"] = ["turret"]
			claimed += 1
	c.armory = [&"turret", &"ice_lock", &"decoy", &"railgun", &"sentry", &"tar_pit"]
	var scene: Control = add_child_autofree(load("res://scenes/netrun_map/netrun_scene.tscn").instantiate())
	scene.start_run(1)
	HeatRules.add_heat(c, 26, RunManager.config(), "test")
	RunManager.netrun._maybe_raid_interlude()
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.RAID, "the raid interlude is open")
	scene._show_current()
	await _frames()
	var w: float = scene._panel.get_combined_minimum_size().x
	assert_true(w <= SCREEN_WIDTH, "raid interlude panel is %d px wide" % w)
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)  # H13: and at the largest text scale
	scene._show_current()
	await _frames()
	w = scene._panel.get_combined_minimum_size().x
	assert_true(w <= SCREEN_WIDTH, "raid interlude panel is %d px wide at text scale %.1f" % [w, Settings.text_scale])
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


## Horizontal pass 11: the widest text scale (GDD 9.6) still fits the combat controls and
## the Grid list.
func test_the_largest_text_scale_still_fits() -> void:
	var before := Settings.text_scale
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	RunManager.save_slot = "gut_test_widths_scale"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var combat: Control = add_child_autofree(load("res://scenes/combat/combat_scene.tscn").instantiate())
	combat.start_fight(&"triage_unit", 7)
	await _frames()
	var w: float = combat.controls_row.get_combined_minimum_size().x
	assert_true(w <= SCREEN_WIDTH, "combat controls %d px at text scale %.1f" % [w, Settings.text_scale])
	combat.queue_free()
	var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
	hq.show_grid()
	await _frames()
	_check(hq, "grid at max text scale")
	hq.show_hq()
	await _frames()
	_check(hq, "HQ at max text scale")
	Settings.set_text_scale(before)
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
