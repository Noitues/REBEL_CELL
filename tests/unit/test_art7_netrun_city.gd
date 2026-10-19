extends GutTest
## ART-7 7w (ART_BIBLE v2 §4.1, §4.6; round 38 transit v3, round 40 cars_lod): the netrun route
## on the unified 3D city: the route page on the 3D city at the NETRUN band (GRID VIEW at the Grid's, other pages
## on the 2D city), the see-through look the band holds, the Grid view's camera (a view: no game state changes).
## NA-26: the cable router and the 2D route page's cables retired with the old page (see NA26_PORT_MAP.md).
## Headless (the 3D city keeps its projection and placement; nothing renders).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const CFG := preload("res://content/config/city_config.tres")


func before_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art7_netrun_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _netrun() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	scene.start_run(1)
	return scene


func test_the_route_page_is_the_3d_city_at_the_netrun_band() -> void:
	var scene := _netrun()
	await _frames()
	var bg: WireframeBackground = scene.background
	assert_true(bg.city3d, "the route page is on the unified 3D city")
	assert_true(bg.city.city3d)
	assert_eq(bg.city.band_lock, CityLod.Band.NETRUN, "it holds the NETRUN band")
	assert_not_null(scene.street_view, "the street view is the route page")
	# GRID VIEW: the whole Grid, at the Grid's band.
	scene._grid_zoomed = true
	scene._show_map()
	await _frames()
	assert_eq(bg.city.band_lock, CityLod.Band.GRID, "GRID VIEW holds the Grid's band")
	scene._grid_zoomed = false
	scene._show_map()
	await _frames()
	# Another page (an event) keeps the 2D city.
	DemoSetup.open_event(RunManager.netrun, &"ev_leash_on_the_floor")
	scene._show_current()
	await _frames()
	assert_false(bg.city3d, "pages that have not moved keep the 2D city")
	assert_eq(bg.city.band_lock, -1)


## The 2D bake's stand-in silhouette (flat roof slabs) never draws over the 3D city: the route
## page turns the 3D city on after the page's first 2D frames.
func test_the_bake_silhouette_goes_when_the_3d_city_comes_on() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	holder.add_child(city)
	await _frames()
	var sil := city.get_node(^"CityView/CitySilhouette") as Control
	sil.visible = true  # what a 2D frame with no bake yet leaves
	city.city3d = true
	assert_false(sil.visible, "no 2D silhouette over the 3D city")


func test_the_netrun_band_is_see_through_at_any_zoom() -> void:
	for ortho in [60.0, 160.0, 440.0, 900.0]:
		assert_lte(CityLod.opacity(CFG, CityView3D.view_lod(CFG, ortho, CityLod.Band.NETRUN)), CFG.see_through_opacity + 0.0001,
			"NETRUN at ortho %d: see-through" % ortho)
		assert_almost_eq(CityLod.opacity(CFG, CityView3D.view_lod(CFG, ortho, CityLod.Band.GRID)), 1.0, 0.0001,
			"GRID at ortho %d: solid" % ortho)


func test_the_grid_views_camera_is_a_view() -> void:
	var scene := _netrun()
	await _frames()
	scene._grid_zoomed = true
	scene._show_map()
	await _frames()
	assert_not_null(scene.route_controls, "the player's camera is on the Grid view")
	var s := RunManager.netrun
	var before := [s.run.current_node_id, s.run.visited.duplicate(), s.run.phase]
	var z0: float = scene.background.city.scale.x
	scene.route_controls.zoom_at(SCREEN.size * 0.5, -2.0)
	await _frames(1)
	assert_gt(scene.background.city.scale.x, z0, "the wheel zooms in")
	scene.route_controls.pan_by(Vector2(40, 0))
	await _frames(1)
	assert_eq([s.run.current_node_id, s.run.visited, s.run.phase], before, "the camera changes no game state")
