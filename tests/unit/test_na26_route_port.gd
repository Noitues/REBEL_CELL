extends GutTest
## NA-26: the street route is the netrun's route page; the City Grid view stays as the zoom-out (designer D6): street -> GRID VIEW
## -> the whole Grid -> ROUTE VIEW -> the street, with no game state changed; a run whose street cannot be derived falls back to the
## transit list page. Headless.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCRIPT := preload("res://scripts/ui/netrun_scene.gd")

var _scene: Control = null


func before_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_na26_port"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	_scene = load(NETRUN).instantiate()
	holder.add_child(_scene)
	_scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)


func after_each() -> void:
	SCRIPT.street_route = true
	CityBakeCache.shutdown()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_the_street_route_is_on_by_default() -> void:
	assert_true(SCRIPT.street_route, "NA-26: the street netrun is the default route page")


func test_zoom_out_to_the_grid_and_back_changes_no_state() -> void:
	_scene.start_run(1)
	await get_tree().process_frame
	assert_not_null(_scene.street_view, "the street page")
	var s := RunManager.netrun
	var before := s.state_hash()
	var campaign_before := RunManager.campaign.state_hash()
	var zoom := _scene._panel.find_child("GridZoom", true, false) as Button
	assert_not_null(zoom, "GRID VIEW is on the street page")
	zoom.pressed.emit()
	await get_tree().process_frame
	await get_tree().process_frame
	assert_null(_scene.street_view, "the street is left")
	assert_true(_scene.city_overlay is CityMapOverlay, "the City Grid view shows the run's path")
	var back := _scene._panel.find_child("GridZoom", true, false) as Button
	assert_eq(back.text, tr("ROUTE VIEW"), "the same button zooms back")
	back.pressed.emit()
	await get_tree().process_frame
	await get_tree().process_frame
	assert_not_null(_scene.street_view, "back on the street")
	assert_eq(s.state_hash(), before, "the zoom is a view: the run is unchanged")
	assert_eq(RunManager.campaign.state_hash(), campaign_before)
	assert_eq(_scene.street_view.run_state()["options"].size(), s.available_nodes().size(), "the same choices")


func test_without_a_street_the_transit_page_lists_the_choices_and_zooms_too() -> void:
	SCRIPT.street_route = false
	_scene.start_run(1)
	await get_tree().process_frame
	assert_null(_scene.street_view)
	assert_null(_scene.city_overlay, "no 2D route map on the fallback page")
	var buttons: Array = _scene._route_buttons
	assert_eq(buttons.size(), RunManager.netrun.available_nodes().size(), "one list row per choice")
	var zoom := _scene._panel.find_child("GridZoom", true, false) as Button
	zoom.pressed.emit()
	await get_tree().process_frame
	assert_true(_scene.city_overlay is CityMapOverlay, "GRID VIEW works from the fallback too")
