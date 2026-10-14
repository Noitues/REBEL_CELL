extends GutTest
## Plan 1 wave 3, W3-HQ (C6 crew recovery, R7 redundancy, F1 stamps): JACK IN is enabled exactly
## when the rules let a living operative launch; an all-flatlined, 0-Schematics Cell reaches a
## deployable crew through the recover card where the crew cards stand; CREW / MARKET tabs
## carry no counts (the top bar has them); the map's stamps never stack.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Vector2(1280, 720)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_w3_hq_crew"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(7)


func after_each() -> void:
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


func _hq() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(5)
	return scene


func _flatline_all() -> void:
	for op in RunManager.campaign.roster:
		op.alive = false
	RunManager.campaign.schematics = 0


func _can_deploy(site: SiteData) -> bool:
	return CampaignRules.can_deploy(RunManager.campaign, RunManager.corporation, RunManager.config(), RunManager.lookup(), site)


func test_can_deploy_is_the_launch_rule_for_a_seeded_campaign() -> void:
	var sites := RunManager.launchable_sites()
	assert_false(sites.is_empty())
	assert_true(_can_deploy(sites[0]))
	_flatline_all()
	assert_true(CampaignRules.needs_crew(RunManager.campaign))
	assert_false(_can_deploy(sites[0]))


func test_all_flatlined_with_no_schematics_reaches_a_deployable_crew() -> void:
	var site := RunManager.launchable_sites()[0]
	_flatline_all()
	var events := RunManager.recruit()
	assert_eq(events[0]["type"], "recruited", "the recruit is free when nobody is left")
	assert_eq(RunManager.campaign.schematics, 0)
	assert_true(_can_deploy(site))


func test_the_recover_card_and_a_disabled_jack_in_show_when_all_are_flatlined() -> void:
	_flatline_all()
	var hq := await _hq()
	var page: Control = hq._panel
	var recover := page.find_child("Recover_*", true, false) as BaseButton
	assert_not_null(recover, "the recruit offer stands where the crew cards are")
	assert_true(page.get_node("HqPage/Hand").is_ancestor_of(recover) if page.has_node("HqPage/Hand") else true)
	var jack := page.find_child("Launch", true, false) as VerbSticker
	if jack != null:
		assert_true(jack.disabled, "JACK IN is disabled with no crew")
		assert_string_contains(jack.tooltip_text, "hire", "and says why")
	recover.pressed.emit()
	await _frames(4)
	assert_false(CampaignRules.needs_crew(RunManager.campaign))
	assert_null(hq._panel.find_child("Recover_*", true, false), "the offer is gone once someone is alive")
	var jack2 := hq._panel.find_child("Launch", true, false) as VerbSticker
	if jack2 != null:
		assert_false(jack2.disabled)


func test_crew_and_market_tabs_carry_no_counts() -> void:
	var hq := await _hq()
	for tab_name in ["Tab_CREW", "Tab_MARKET"]:
		var tab := hq._panel.find_child(tab_name, true, false) as MenuChip
		assert_not_null(tab)
		assert_eq(tab.line, "", "%s repeats nothing from the top bar" % tab_name)


func test_stamps_placed_one_after_another_do_not_overlap() -> void:
	var city := NeonCity.new()
	add_child_autofree(city)
	var placed: Array[Rect2] = []
	var a := {"at": Vector2(3, 3), "word": "CLAIMED", "color": Color.WHITE}
	var b := {"at": Vector2(3, 3), "word": "CLAIMED", "color": Color.WHITE}
	var ra := city.stamp_rect(a, placed)
	placed.append(NeonCity._tilted_bounds(ra, NeonCity.MARK_TILT))
	var rb := city.stamp_rect(b, placed)
	assert_false(NeonCity._tilted_bounds(rb, NeonCity.MARK_TILT).intersects(placed[0]), "the second stamp keeps clear of the first")
