extends GutTest
## ART-5 5a (bible §4.1, §6.1): the City Grid on the unified 3D city, headless. The 2D map
## layer and the 3D camera agree (a lot's map point is the 3D camera's projection of it; a
## roof sits at its 3D height); the layout drops the fist roads; the player camera (log-
## linear zoom about the cursor, clamped; pan kept in the city; the minimap's iso); the Grid
## page runs in city-3D mode, its map feeds the network decal, and leaving it leaves 3D.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SETTLE := 12
const CONFIG := preload("res://content/config/city_config.tres")

var cfg: CityConfig = CONFIG


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_city3d_grid"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _city(focus: Vector2, zoom: float) -> NeonCity:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var c := NeonCity.new()
	c.city3d = true
	holder.add_child(c)
	c.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT)
	c.scale = Vector2(zoom, zoom)
	c.size = SCREEN.size / zoom
	c.focus_grid = focus
	c.focus_anchor = Vector2(0.4, 0.6)
	c.update_camera()
	return c


func test_the_map_layer_projects_like_the_3d_camera() -> void:
	var c := _city(Vector2(36, 8), 0.4)
	var cam := c.iso_camera()
	for g in [Vector2(36, 8), Vector2(20, 30), Vector2(50.5, -3.25)]:
		var w := CityIsoCamera.lot_to_world(cfg, g)
		assert_almost_eq(c.grid_to_local(g.x, g.y), cam.project(w), Vector2(0.01, 0.01), "lot %s" % g)
	assert_almost_eq(cam.ortho, c.size.x / NeonCity.px_per_bu(), 0.001, "the frame's width in BU")
	assert_almost_eq(c.tile_b(), NeonCity.TILE_A * sin(deg_to_rad(cfg.pitch_deg)), 0.0001, "pitch 40, not 2:1")


func test_roofs_sit_at_their_3d_height() -> void:
	var c := _city(Vector2(30, 10), 0.5)
	var cam := c.iso_camera()
	var model := CityModel.build(cfg, c.city_seed, Rect2i(24, 4, 16, 16))
	var checked := 0
	for n in model.prisms.size():
		var pr := model.prisms[n]
		var cell: Rect2i = pr["cell"]
		if pr["hq"] or float(pr["taper"]) < 0.99 or float(pr["y0"]) > 0.0 or (pr["poly"] as PackedVector2Array).size() != 4:
			continue
		var lot := cell.end - Vector2i.ONE
		var rec := c.roof_of(lot.x, lot.y)
		if rec.is_empty():
			continue
		var top := model.top_at(lot)
		if not is_equal_approx(top, float(pr["h"])):
			continue  # stacked or clutter on top: the roof is another extrusion's
		var pc: Vector2 = pr["centre"]
		var want := cam.project(Vector3(pc.x, top, pc.y))
		var roof: PackedVector2Array = rec["roof"]
		var got := Vector2.ZERO
		for q in roof:
			got += q
		got /= roof.size()
		assert_almost_eq(got, want, Vector2(4.0, 4.0), "the roof of lot %s over its 3D top" % lot)
		checked += 1
		if checked >= 12:
			break
	assert_gt(checked, 4, "plain box buildings checked")


func test_the_3d_layout_keeps_the_cells_street_grid() -> void:
	var c := _city(Vector2(35, 37), 0.5)
	var flat := NeonCity.new()
	add_child_autofree(flat)
	var model := CityModel.build(cfg, c.city_seed, Rect2i(26, 28, 18, 18))
	var streets := {}
	for s in model.streets:
		streets[s["lot"]] = true
	var differ := 0
	var p2 := flat._placement()
	for i in range(26, 44):
		for j in range(28, 46):
			assert_eq(c.is_street(i, j), streets.has(Vector2i(i, j)), "lot %d,%d: the map's streets are the model's" % [i, j])
			if c.is_street(i, j) != p2._is_street_lot(i, j) or c._placement()._has_building(Vector2i(i, j)) != p2._has_building(Vector2i(i, j)):
				differ += 1
	assert_eq(c.fist_roads, false)
	assert_gt(differ, 0, "the 2D fist roads are gone from the 3D layout")
	assert_true(flat.fist_roads, "the 2D city keeps its fist")


func test_zoom_is_log_linear_about_the_cursor_and_clamped() -> void:
	var screen := Vector2(1280, 720)
	var tb := NeonCity.TILE_A * sin(deg_to_rad(cfg.pitch_deg))
	var s0 := CityMapCamera.scale_for_ortho(screen.x, cfg.grid_ortho)
	assert_almost_eq(CityMapCamera.ortho_of(screen.x, s0), cfg.grid_ortho, 0.001)
	var p := Vector2(900, 200)
	var g := CityMapCamera.grid_at(p, screen, Vector2(30, 10), Vector2(0.4, 0.6), s0, tb)
	var f := CityMapCamera.zoom_about(cfg, p, 1.0 / cfg.zoom_step, screen, Vector2(30, 10), Vector2(0.4, 0.6), s0, tb)
	assert_almost_eq(CityMapCamera.ortho_of(screen.x, f["scale"]), cfg.grid_ortho / cfg.zoom_step, 0.01, "one notch in")
	assert_almost_eq(CityMapCamera.screen_of(g, screen, f["focus"], f["anchor"], f["scale"], tb), p, Vector2(0.01, 0.01),
		"the ground under the cursor stays")
	var far := CityMapCamera.zoom_about(cfg, p, 1000.0, screen, f["focus"], f["anchor"], f["scale"], tb)
	assert_almost_eq(CityMapCamera.ortho_of(screen.x, far["scale"]), cfg.zoom_ortho_max, 0.01, "clamped out")
	var near := CityMapCamera.zoom_about(cfg, p, 0.0001, screen, f["focus"], f["anchor"], f["scale"], tb)
	assert_almost_eq(CityMapCamera.ortho_of(screen.x, near["scale"]), cfg.zoom_ortho_min, 0.01, "clamped in")


func test_pan_follows_the_drag_and_stays_in_the_city() -> void:
	var screen := Vector2(1280, 720)
	var tb := NeonCity.TILE_A * sin(deg_to_rad(cfg.pitch_deg))
	var s0 := CityMapCamera.scale_for_ortho(screen.x, cfg.grid_ortho)
	var g := Vector2(12, 14)
	var at := CityMapCamera.screen_of(g, screen, Vector2(10, 10), Vector2(0.5, 0.5), s0, tb)
	var f := CityMapCamera.pan(cfg, Vector2(60, -25), screen, Vector2(10, 10), Vector2(0.5, 0.5), s0, tb)
	assert_almost_eq(CityMapCamera.screen_of(g, screen, f["focus"], f["anchor"], s0, tb), at + Vector2(60, -25), Vector2(0.01, 0.01),
		"the city follows the drag")
	var out := CityMapCamera.pan(cfg, Vector2(1e6, 1e6), screen, Vector2(10, 10), Vector2(0.5, 0.5), s0, tb)
	assert_true(Rect2(cfg.city_rect).grow(0.01).has_point(out["focus"]), "the frame's centre stays in the city")
	var quad := CityMapCamera.view_quad(screen, f["focus"], f["anchor"], s0, tb)
	assert_eq(quad.size(), 4)
	assert_almost_eq(CityMapCamera.screen_of(quad[2], screen, f["focus"], f["anchor"], s0, tb), screen, Vector2(0.01, 0.01))


func test_the_minimap_iso_round_trips() -> void:
	var m: CityMinimap = add_child_autofree(CityMinimap.new())
	m.size = cfg.minimap_size
	await _frames(1)
	for g in [Vector2(0, 0), Vector2(36, 2), Vector2(-60, 70)]:
		assert_almost_eq(m.from_map(m.to_map(g)), g, Vector2(0.001, 0.001), "grid %s" % g)
	var r := Rect2(cfg.city_rect)
	for corner in [r.position, r.end]:
		var p := m.to_map(corner)
		assert_true(Rect2(Vector2.ZERO, m._map.size).grow(0.5).has_point(p), "the whole city fits the minimap")


func _hq_grid() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hq.new_campaign(1)
	hq.show_grid()
	await _frames(SETTLE)
	return hq


func test_the_grid_page_is_the_3d_city_and_feeds_the_decal() -> void:
	var hq := await _hq_grid()
	var wire: WireframeBackground = hq.wireframe
	assert_true(wire.city.city3d, "the Grid draws the unified city")
	assert_true(wire.city3d)
	var ov: CityMapOverlay = hq.city_overlay
	assert_true(ov.on_ground_decal(), "its links are the ground decal")
	var d := ov.network_data()
	assert_eq(d.nodes.size(), ov.nodes.size(), "every Site is a decal node")
	assert_gt(d.segments.size(), 0, "links along the streets")
	for n in d.nodes:
		var lot := CityIsoCamera.world_to_lot(cfg, n["world"])
		assert_eq(Vector2i(lot.floor()), ov.lot_of(n["id"]), "a decal node sits on its Site's building lot")
	var ortho := CityMapCamera.ortho_of(hq.size.x, wire.city.scale.x)
	assert_between(ortho, cfg.zoom_ortho_min, cfg.zoom_ortho_max, "the fitted frame is inside the zoom range")
	hq.show_hq()
	await _frames(2)
	assert_false(wire.city.city3d, "other pages keep the 2D city until they move")
	hq.get_parent().queue_free()
	await _frames(1)


func test_the_grid_camera_zooms_and_pans_on_request() -> void:
	var hq := await _hq_grid()
	var ctl: CityGridControls = hq.grid_controls
	assert_not_null(ctl, "the Grid has its camera controls")
	var city: NeonCity = hq.wireframe.city
	var o0 := CityMapCamera.ortho_of(hq.size.x, city.scale.x)
	ctl.zoom_at(hq.size * 0.5, 1.0)
	assert_almost_eq(CityMapCamera.ortho_of(hq.size.x, city.scale.x), clampf(o0 * cfg.zoom_step, cfg.zoom_ortho_min, cfg.zoom_ortho_max), 0.01,
		"a wheel notch out")
	var g := Vector2(40, 5)
	var at := city.get_global_transform() * city.grid_to_local(g.x, g.y)
	ctl.pan_by(Vector2(30, 12))
	city.update_camera()
	var now := city.get_global_transform() * city.grid_to_local(g.x, g.y)
	assert_almost_eq(now, at + Vector2(30, 12), Vector2(0.5, 0.5), "the city follows the pan")
	assert_not_null(hq.grid_minimap, "the minimap terminal")
	assert_eq(hq.grid_minimap.view_quad.size(), 4, "it shows the view box")
	hq.get_parent().queue_free()
	await _frames(1)
