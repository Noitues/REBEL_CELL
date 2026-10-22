extends GutTest
## PB-SOL-1 B-07 / C-10: stationing works from the raid setup. Two playtesters never found where
## a crew member is stationed (it was only on the HQ page, by a drag or the node card's button).
## The raid setup now has its own STATION button for the runner on the target node; it is the same
## rule call as the HQ button (`CampaignRules.station`) and the setup's crew line and warning follow.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_raid_station"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _scene() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


## A campaign with a claimed safehouse (a station slot) and a raid pending.
func _campaign(hq: Control) -> StringName:
	hq.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var grid_data := corp.city_grid
	var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
	CampaignRules.on_run_completed(c, corp, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	for sd in grid_data.sites:
		if sd == null or sd.id == first or sd.id == grid_data.home_site_id or not sd.claimable:
			continue
		CampaignRules.on_run_completed(c, corp, RunManager.config(), hq._demo_run(sd.id))
		if CampaignRules.claim_error(c, corp, RunManager.config(), RunManager.lookup(), sd.id, &"safehouse", RunManager.profile) == "":
			CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), sd.id, &"safehouse", RunManager.profile)
			return sd.id
	return &""


func test_the_raid_setup_stations_the_runner_on_the_target_and_recalls_them() -> void:
	var hq := _scene()
	var safe := _campaign(hq)
	assert_ne(safe, &"", "a safehouse is claimed")
	hq.show_raid()
	await _frames(4)
	var c := RunManager.campaign
	assert_eq(CampaignRules.stationed_count(c), 0, "nobody stationed at first")
	assert_not_null(hq._panel.find_child("NoCrewWarning", true, false), "the setup warns")
	hq.select_target(safe)
	await _frames(3)
	var op: OperativeState = hq.selected_op()
	var btn := hq._panel.find_child("StationCrew", true, false) as Button
	assert_not_null(btn, "STATION is on the raid setup")
	var expect := c.duplicate_state()
	CampaignRules.station(expect, RunManager.lookup(), op.id, safe)
	btn.pressed.emit()
	await _frames(4)
	assert_eq(hq.panel_name, "raid", "stationing keeps the player on the raid setup")
	assert_eq(c.state_hash(), expect.state_hash(), "the same change as the HQ station rule")
	assert_eq(CampaignRules.stationed_site(c, op.id), safe)
	assert_null(hq._panel.find_child("NoCrewWarning", true, false), "the warning is gone")
	assert_string_contains((hq._panel.find_child("CrewCount", true, false) as Label).text, "Stationed: 1")
	var recall_btn := hq._panel.find_child("RecallCrew", true, false) as Button
	assert_not_null(recall_btn, "RECALL replaces STATION on the same node")
	recall_btn.pressed.emit()
	await _frames(4)
	assert_eq(CampaignRules.stationed_count(c), 0, "recalled")
	assert_eq(hq.panel_name, "raid")


func test_the_no_crew_dialog_says_where_to_station() -> void:
	var hq := _scene()
	assert_false(hq.NO_CREW_BODY.contains("at HQ first"), "the dialog no longer sends the player to another page")
	assert_string_contains(hq.NO_CREW_BODY, "STATION")
