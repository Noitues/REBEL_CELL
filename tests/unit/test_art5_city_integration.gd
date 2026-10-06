extends GutTest
## ART-5 5e (bible 4.1, 4.3, 4.4, 4.5, 5.4; round 39 city_grid; round 40 unified40): the city
## integration, headless. Reduce motion is not a host pause (street traffic keeps 40 %); the
## day-look call; the Cell's blackout reveal (end state when it does not play, a tween when it
## does, MotionSkip settles it); the x2 Site spread aimed into each corporation's own
## territory; the Grid's city life from the campaign (Heat band, hardened Sites, DISPATCH,
## the Site landmark) and the roof lift on the landmark's lots; the off-screen TARGET's edge
## clamp; the roof props (the concept's models placed by its rules); the Grid's markers (the
## overlay snaps to the nearest building; GridMarkerProjection keeps the layout's lot).

const CITY_CONFIG := preload("res://content/config/city_config.tres")
## A part of the city for the view tests (lots): Halcyon's border.
const PART := Rect2i(10, 0, 30, 30)
const CORPS: Array[StringName] = [&"halcyon", &"meridian", &"orbital", &"rebel_cell", &"solace"]
## The overlay snaps a Site to the nearest building within this many lots (CityMapOverlay).
const SNAP_LOTS := 4

var cfg: CityConfig = CITY_CONFIG
var model: CityModel
var _reduce_motion: bool
var _reduce_effects: bool


func before_all() -> void:
	model = CityModel.build(cfg, 7, PART)
	_reduce_motion = Settings.reduce_motion
	_reduce_effects = Settings.reduce_effects


func after_each() -> void:
	Settings.reduce_motion = _reduce_motion
	Settings.reduce_effects = _reduce_effects
	Settings.changed.emit()
	Motion.force_live = false


func _view() -> CityView3D:
	var view := CityView3D.new()
	view.size = Vector2i(640, 360)
	view.use_model(model)
	add_child_autofree(view)
	return view


func _corp(id: StringName) -> CorporationData:
	return load("res://content/corporations/%s.tres" % id) as CorporationData


func _campaign(corp: CorporationData) -> CampaignState:
	var home := RunManager.lookup().get_content(RunManager.DEFAULT_HOME) as HomeServerVariantData
	return CampaignRules.new_campaign(corp, RunManager.config(), RunManager.lookup(), 1,
		RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData, home.core, 0, home)


func test_reduce_motion_is_not_a_host_pause() -> void:
	var view := _view()
	var motion := CityViewMotion.make(view)
	view.add_child(motion)
	await get_tree().process_frame
	assert_not_null(motion.layers, "the motion layers are on the view")
	Settings.reduce_motion = true
	Settings.changed.emit()
	assert_eq(view.ambient_scale, 0.0, "the view's own rain and fog still")
	assert_false(view.host_paused(), "reduce motion is not a pause")
	assert_eq(motion.layers.host_ambient, 1.0, "the layers keep running: street traffic at 40 % (bible 5.4)")
	assert_false(motion.layers.paused())
	view.covered = true
	assert_eq(motion.layers.host_ambient, 0.0, "a covered map pauses them")
	assert_true(motion.layers.paused())
	view.covered = false
	assert_eq(motion.layers.host_ambient, 1.0, "uncovered: live again")


func test_the_day_look_call_restyles_the_city() -> void:
	var view := _view()
	var mcfg := CityMotionConfigData.shipped()
	var day := CityViewMotion.day_look(mcfg)
	for k in ["ramp", "sky", "window_gain", "neon_gain", "haze", "grade"]:
		assert_true(day.has(k), "the day look carries %s" % k)
	view.set_night_share(0.0, day)
	assert_eq(view.night_share, 0.0)
	assert_true(view._env.background_color.is_equal_approx(mcfg.day_sky), "the day sky")
	assert_almost_eq(float(view._building_mat.get_shader_parameter(&"window_gain")), mcfg.day_window_gain, 0.0001)
	assert_false(bool(view._post.get_shader_parameter(&"rain_on")), "no rain by day")
	view.set_night_share(1.0, day)
	assert_true(view._env.background_color.is_equal_approx(cfg.sky), "the night sky again")
	assert_almost_eq(float(view._building_mat.get_shader_parameter(&"window_gain")), cfg.window_gain, 0.0001)


func test_the_cell_reveal_is_a_t0_motion_with_its_end_state() -> void:
	assert_true(Motion.has(CityView3D.CELL_REVEAL_MOTION), "cell_fist_reveal is in ui_motion.tres")
	assert_true(UiMotionData.REQUIRED_IDS.has(CityView3D.CELL_REVEAL_MOTION), "and a required id")
	var e := Motion.entry(CityView3D.CELL_REVEAL_MOTION)
	assert_eq(int(e.tier), VfxTier.T0)
	assert_true(VfxTier.fits(e))
	var view := _view()
	view.cell_reveal = 0.2
	assert_null(view.play_cell_reveal(), "headless: nothing plays")
	assert_eq(view.cell_reveal, 1.0, "the fist at once")
	Motion.force_live = true
	Settings.reduce_motion = true
	view.cell_reveal = 0.2
	assert_null(view.play_cell_reveal(), "reduce motion: the end state")
	assert_eq(view.cell_reveal, 1.0)
	Settings.reduce_motion = false
	var tw := view.play_cell_reveal()
	assert_not_null(tw, "live: the reveal plays")
	assert_eq(view.cell_reveal, 0.0, "from the sector fully lit")
	assert_true(Motion.held(view, ^"cell_reveal"), "MotionSkip sees it running")
	Motion.settle(view, ^"cell_reveal")
	assert_eq(view.cell_reveal, 1.0, "a skip ends on the fist")


func test_the_spread_layout_stays_in_each_territory() -> void:
	var city := NeonCity.new()
	for id in CORPS:
		var corp := _corp(id)
		var pts := CityLayout.site_points(corp)
		var r := CityLayout.spread_report(city, corp, pts)
		assert_eq(int(r["in"]), int(r["sites"]), "%s: every Site in its own territory (off: %s)" % [id, r["off"]])
		assert_eq(int(r["hq"]), 0, "%s: no Site on an HQ plaza" % id)
		assert_eq(int(r["out"]), 0, "%s: none off the city" % id)
		assert_eq(int(r["dup"]), 0, "%s: one Site a lot" % id)
		# x2: the layout spans twice the 5a layout, the boss end kept by the HQ.
		var one := CityLayout.site_points_aimed(corp, float(cfg.site_aim_deg.get(id, 0.0)), bool(cfg.site_mirror.get(id, false)), 1.0)
		assert_almost_eq(_span(pts) / _span(one), cfg.site_spread, 0.01, "%s: spread x%.1f" % [id, cfg.site_spread])
	city.free()


func _span(pts: Dictionary) -> float:
	var lo := Vector2(INF, INF)
	var hi := -lo
	for id in pts:
		lo = lo.min(pts[id])
		hi = hi.max(pts[id])
	return (hi - lo).length()


func test_the_grid_city_life_reads_the_campaign() -> void:
	var cc := RunManager.config()
	var solace := _corp(&"solace")
	var c := _campaign(solace)
	var life := GridCityLife.of(c, solace, cc)
	assert_eq(int(life["heat_band"]), Palette.heat_band(c.heat, HeatRules.band_levels(c, cc)))
	assert_false(bool(life["dispatch"]), "DISPATCH's fist only in the REBEL_CELL campaign")
	assert_eq(life["site_corp"], &"solace", "Solace has a Site landmark")
	var pts := CityLayout.site_points(solace)
	assert_eq(life["site_lot"], (pts[cfg.site_landmarks[&"solace"]] as Vector2).floor() + Vector2(0.5, 0.5), "on its Site's lot")
	assert_eq(life["home_lot"], pts[c.grid.home_site_id], "the Cell's home lot")
	assert_eq((life["hardened"] as Array).size(), 0, "no ENEMY_RESISTANCE at the start: nothing hardened")
	c.heat = cc.heat_max
	assert_gt(c.rule_modifier(cc, RC.RuleModifierType.ENEMY_RESISTANCE), 0.0, "high Heat hardens the fights")
	life = GridCityLife.of(c, solace, cc)
	var want: Array[StringName] = []
	for s in CampaignRules.launchable_sites(c, solace, cc):
		want.append(s.id)
	want.sort()
	assert_eq(life["hardened"], want, "the launchable Sites are hardened")
	assert_eq(life, GridCityLife.of(c, solace, cc), "same campaign, same life")
	var cell := _corp(&"rebel_cell")
	var lc := GridCityLife.of(_campaign(cell), cell, cc)
	assert_true(bool(lc["dispatch"]), "the REBEL_CELL campaign shows DISPATCH's fist")
	assert_eq(lc["site_corp"], &"", "the Cell has no Site landmark")


func test_the_site_landmark_lifts_the_roofs_under_it() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var city := NeonCity.new()
	city.city3d = true
	holder.add_child(city)
	city.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT)
	city.size = holder.size
	var solace := _corp(&"solace")
	var life := GridCityLife.of(_campaign(solace), solace, RunManager.config())
	var lot: Vector2 = life["site_lot"]
	city.focus_grid = lot
	city.update_camera()
	var l := Vector2i(lot.floor())
	assert_eq(city.lift_at(l), 0.0, "no lift before the city life")
	var before := city.roof_of(l.x, l.y)
	var stamp := city.frame_stamp()
	city.set_city_life(life)
	var path := CityLandmarks.site_path(&"solace")
	assert_almost_eq(city.lift_at(l), CityLandmarks.top_of(path), 0.001, "the landmark's top over its lot")
	assert_ne(city.frame_stamp(), stamp, "overlays re-place their markers")
	if not before.is_empty():
		var after := city.roof_of(l.x, l.y)
		assert_lt(_mid(after["roof"]).y, _mid(before["roof"]).y, "the marker's roof rises to the landmark")
	assert_eq(city.lift_at(l + Vector2i(40, 40)), 0.0, "other lots keep their roofs")


func _mid(pts: PackedVector2Array) -> Vector2:
	var c := Vector2.ZERO
	for p in pts:
		c += p
	return c / maxf(1.0, pts.size())


func test_the_offscreen_target_clamps_to_the_edge() -> void:
	var r := Rect2(0, 0, 800, 600)
	var inside := TargetEdgeMarker.edge_point(r, Vector2(400, 300), 40.0)
	assert_true(bool(inside["inside"]), "on screen: no arrow")
	var right := TargetEdgeMarker.edge_point(r, Vector2(2000, 300), 40.0)
	assert_false(bool(right["inside"]))
	assert_almost_eq(right["at"], Vector2(760, 300), Vector2(0.01, 0.01), "on the right edge, inside the margin")
	assert_almost_eq(right["dir"], Vector2.RIGHT, Vector2(0.001, 0.001), "pointing at it")
	var corner := TargetEdgeMarker.edge_point(r, Vector2(-1000, -1000), 40.0)
	var at: Vector2 = corner["at"]
	assert_true(r.grow(-40.0).grow(0.01).has_point(at), "clamped into the area")
	assert_true(is_equal_approx(at.x, 40.0) or is_equal_approx(at.y, 40.0), "on the shrunk rect's edge")
	var just := TargetEdgeMarker.edge_point(r, Vector2(780, 300), 40.0)
	assert_true(bool(just["inside"]), "on screen, if near the edge: no arrow (the target shows)")


func test_roof_props_are_the_concepts_placed_by_its_rules() -> void:
	var names: Array[String] = []
	for nm in CityRoofProps.names():
		names.append(String(nm))
		assert_not_null(CityRoofProps.mesh_of(nm), "%s is exported" % nm)
	assert_eq(names, RoofPropAssetChecks.PROPS, "the validator checks the props the city places")
	assert_eq(RoofPropAssetChecks.errors().size(), 0, "the export is in place: %s" % [RoofPropAssetChecks.errors()])
	var idx := PackedInt32Array()
	for n in model.prisms.size():
		idx.append(n)
	var placed := CityRoofProps.place(cfg, model.prisms, idx)
	assert_eq(placed, CityRoofProps.place(cfg, model.prisms, idx), "deterministic")
	var total := 0
	for nm in CityRoofProps.names():
		total += (placed[nm] as Array).size()
	assert_gt(total, 0, "props stand on the city's roofs")
	assert_gt((placed[CityRoofProps.AC] as Array).size(), 0, "AC units")
	# Every prop stands on a flat roof that is big enough, at its top; antennas on tall ones.
	for nm in CityRoofProps.names():
		for xf: Transform3D in placed[nm]:
			var pr := _prism_under(Vector2(xf.origin.x, xf.origin.z), xf.origin.y)
			assert_false(pr.is_empty(), "%s stands on a roof" % nm)
			if pr.is_empty():
				continue
			assert_gte(float(pr["taper"]), cfg.roof_prop_min_top_scale, "a flat roof")
			if nm == CityRoofProps.ANTENNA:
				assert_gt(float(pr["h"]), cfg.roof_antenna_above, "antennas on tall roofs")
			elif String(nm).begins_with("billboard"):
				assert_gt(float(pr["h"]), cfg.roof_billboard_above, "billboards over 14 BU")


func _prism_under(p: Vector2, top: float) -> Dictionary:
	for pr in model.prisms:
		if absf(float(pr["y0"]) + float(pr["h"]) - top) > 0.001:
			continue
		var poly: PackedVector2Array = pr["poly"]
		if Geometry2D.is_point_in_polygon(p, poly):
			return pr
	return {}


func test_the_grid_markers_are_the_overlays_on_the_layouts_lots() -> void:
	# ART-5 5e call (b): the Grid overlay keeps drawing 5d's markers. Its anchors snap each
	# Site to the nearest building of its layout point (a Site is a building); the
	# projection (raid / netrun views without a NeonCity) keeps the layout's own lot.
	RunManager.save_slot = "gut_art5_city_integration"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var hq: Control = load("res://scenes/hq/hq_scene.tscn").instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hq.new_campaign(1)
	hq.show_grid()
	var ov: CityMapOverlay = hq.city_overlay
	await BoundedWait.until(get_tree(), func() -> bool: return not ov.nodes.is_empty() and ov.city.camera_settled(), 5.0)
	var proj := GridMarkerProjection.from_camera(cfg, RunManager.corporation, Vector2(1280, 720))
	assert_not_null(hq.grid_target, "the Grid has its off-screen TARGET")
	assert_false(hq.wireframe.city.city_life.is_empty(), "the Grid's city shows the campaign")
	var checked := 0
	for n in ov.nodes:
		var id: StringName = n["id"]
		if not proj.lots.has(id):
			continue
		var want := Vector2i((proj.lots[id] as Vector2).round())
		var got := ov.lot_of(id)
		assert_lte(maxi(absi(got.x - want.x), absi(got.y - want.y)), SNAP_LOTS, "%s: the overlay's building is next to its layout lot" % id)
		checked += 1
	assert_gt(checked, 0)
	hq.get_parent().queue_free()
	await get_tree().process_frame
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
	AudioDirector.muted = false


func test_a_rebuilt_map_keeps_the_newer_maps_decal() -> void:
	# ART-5 5e (found in the Heat-band review): the Grid rebuilds its map on every Site
	# selection; the old map leaves the tree after the new one fed the decal, and must not
	# clear it.
	var city: NeonCity = autofree(NeonCity.new())
	var view := _view()
	city.view3d = view
	var holder: Control = add_child_autofree(Control.new())
	var old_map := CityMapOverlay.new(city)
	holder.add_child(old_map)
	old_map._feed_decal()
	var new_map := CityMapOverlay.new(city)
	holder.add_child(new_map)
	new_map._feed_decal()
	var fed := view.network
	assert_not_null(fed, "the new map fed the decal")
	holder.remove_child(old_map)
	old_map.free()
	assert_eq(view.network, fed, "the old map leaving keeps the new map's decal")
	holder.remove_child(new_map)
	new_map.free()
	assert_null(view.network, "the last map leaving clears it")
