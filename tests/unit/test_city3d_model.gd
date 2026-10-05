extends GutTest
## ART-5 5a (bible §4.1, §6.1): the production city model and its seams, headless. The
## whole-city config, a chunked model of the game's own layout (deterministic, every
## building in its chunk, picking through the chunks equal to testing every prism), the
## building LOD and view bands by ortho with hysteresis, the continuous log-linear zoom and
## pan, the network decal's buffers, and CityView3D's scene-layer and picking API.

const CONFIG := preload("res://content/config/city_config.tres")
## A part of the city round the Halcyon / REBEL_CELL border (chunks of the real layout).
const PART := Rect2i(20, -4, 40, 40)

var cfg: CityConfig = CONFIG
var model: CityModel


func before_all() -> void:
	model = CityModel.build(cfg, 7, PART)


func test_the_whole_city_config() -> void:
	assert_eq(cfg.resource_path, "res://content/config/city_config.tres")
	for corp: StringName in [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]:
		var hq := Rect2i(Vector2i(NeonCity.hq_of(corp)), Vector2i(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS))
		assert_true(cfg.city_rect.encloses(hq.grow(20)), "%s's district is inside the city" % corp)
	var covered := 0
	for key in CityModel.chunk_keys(cfg, cfg.city_rect):
		var r := CityModel.chunk_rect(cfg, key)
		covered += r.size.x * r.size.y
	assert_eq(covered, cfg.city_rect.size.x * cfg.city_rect.size.y, "the chunks tile the city exactly")


func test_the_model_is_the_games_layout_chunked_and_deterministic() -> void:
	assert_gt(model.prisms.size(), 1000, "real buildings")
	assert_gt(model.streets.size(), 300, "and street lots")
	assert_true(model.hqs.has(&"halcyon"), "the Halcyon HQ lot")
	var again := CityModel.build(cfg, 7, PART)
	assert_eq(again.prisms.size(), model.prisms.size())
	for n in [0, model.prisms.size() / 3, model.prisms.size() - 1]:
		assert_eq(again.prisms[n]["poly"], model.prisms[n]["poly"], "same seed, same footprint %d" % n)
		assert_eq(again.prisms[n]["chunk"], model.prisms[n]["chunk"])
	for key in model.keys():
		var ch: Dictionary = model.chunks[key]
		var box := model.chunk_aabb(key)
		for n: int in ch["prisms"]:
			var pr := model.prisms[n]
			assert_eq(pr["chunk"], key)
			for q: Vector2 in pr["poly"]:
				assert_true(box.has_point(Vector3(q.x, 0.5, q.y)), "prism %d inside its chunk's box" % n)


func test_the_fist_roads_are_not_laid_out() -> void:
	# Round 34 lock (bible §4.4): the Cell's district keeps the normal street grid.
	var cell := CityModel.build(cfg, 7, Rect2i(30, 32, 10, 10))
	assert_gt(cell.prisms.size(), 20, "the Cell's district is built up")


func test_picking_through_chunks_equals_testing_every_prism() -> void:
	var c := Vector2(PART.get_center())
	var cam := CityIsoCamera.make(cfg, CityIsoCamera.lot_to_world(cfg, c), 300.0, Vector2(1920, 1080))
	var hits := 0
	for k in 24:
		var p := Vector2(80 + (k % 6) * 330, 100 + (k / 6) * 260)
		var brute := -1
		var best := INF
		var o := cam.ray_origin(p)
		for n in model.prisms.size():
			var t := CityDistrict.ray_prism(o, cam.forward(), model.prisms[n])
			if t < best:
				best = t
				brute = n
		assert_eq(model.pick(cam, p), brute, "pixel %s" % p)
		if brute >= 0:
			hits += 1
			var info := model.pick_info(cam, p)
			assert_eq(info["building"], model.prisms[brute]["building"])
			assert_true((info["cell"] as Rect2i).has_point(info["lot"]), "the picked lot is the building's")
	assert_gt(hits, 6, "most pixels hit a building")


func test_every_prism_of_a_chunk_lands_in_one_family_buffer() -> void:
	var inks := CityMeshKit.ink_palette(model.prisms)
	assert_lte(inks.size(), 16)
	for key in model.keys():
		var idx: PackedInt32Array = model.chunks[key]["prisms"]
		var fams := CityMeshKit.families_of(cfg, model.prisms, idx)
		var total := 0
		for fk: int in fams:
			var ids: PackedInt32Array = fams[fk]
			total += ids.size()
			var buf := CityMeshKit.instance_buffer(cfg, model.prisms, ids, inks)
			assert_eq(buf.size(), ids.size() * CityMeshKit.INSTANCE_FLOATS)
			var t := CityMeshKit.instance_transform(model.prisms[ids[0]]["poly"], model.prisms[ids[0]]["y0"], model.prisms[ids[0]]["h"])
			assert_almost_eq(Vector3(buf[3], buf[7], buf[11]), t.origin, Vector3.ONE * 0.0001, "row-major transform, origin last")
			assert_almost_eq(buf[1], t.basis.y.x, 0.0001)
		assert_eq(total, idx.size(), "chunk %s: every prism in a family" % key)


func test_top_at_is_the_tallest_roof_on_the_lot() -> void:
	var pr := model.prisms[model.prisms.size() / 2]
	var cell: Rect2i = pr["cell"]
	assert_gte(model.top_at(cell.position), float(pr["y0"]) + float(pr["h"]) - 0.001)


func test_building_lod_by_ortho_with_hysteresis() -> void:
	assert_eq(CityLod.building_lod(cfg, 300.0), 0, "raid frustum: LOD0")
	assert_eq(CityLod.building_lod(cfg, cfg.grid_ortho), 1, "the City Grid: LOD1")
	assert_eq(CityLod.building_lod(cfg, 1200.0), 2, "the whole city: LOD2")
	var edge := cfg.lod0_below
	assert_eq(CityLod.building_lod(cfg, edge * 1.02, 0), 0, "holds LOD0 inside the band")
	assert_eq(CityLod.building_lod(cfg, edge * 1.2, 0), 1, "swaps past it")
	assert_eq(CityLod.building_lod(cfg, edge * 0.98, 1), 1, "holds LOD1 inside the band")
	assert_eq(CityLod.building_lod(cfg, cfg.lod2_above * 0.98, 2), 2)
	assert_eq(_rows(0), cfg.height_class_rows[2], "LOD0 keeps every facet row")
	assert_eq(_rows(2), 1, "LOD2 is a plain extrusion")


func _rows(lod: int) -> int:
	return CityMeshKit.lod_rows(cfg, 2, lod)


func test_view_bands_host_the_views_by_zoom() -> void:
	assert_eq(CityLod.band(cfg, cfg.grid_ortho), CityLod.Band.GRID, "the Grid at ortho 440 is solid")
	assert_almost_eq(CityLod.opacity(cfg, CityIsoCamera.lod_of(cfg, cfg.grid_ortho)), 1.0, 0.001)
	assert_eq(CityLod.band(cfg, 380.0), CityLod.Band.RAID, "the raid fit")
	assert_eq(CityLod.band(cfg, 160.0), CityLod.Band.NETRUN, "the netrun transit")
	assert_eq(CityLod.band(cfg, 430.0, CityLod.Band.GRID), CityLod.Band.GRID, "hysteresis keeps the Grid")
	assert_almost_eq(CityLod.ortho_of_lod(cfg, CityIsoCamera.lod_of(cfg, 300.0)), 300.0, 0.01)
	assert_almost_eq(CityLod.ortho_of_lod(cfg, CityIsoCamera.lod_of(cfg, 120.0)), 120.0, 0.01)


func test_zoom_is_log_linear_about_the_cursor_and_pan_slides() -> void:
	var cam := CityIsoCamera.make(cfg, Vector3(10, 0, -20), cfg.grid_ortho, Vector2(1920, 1080))
	var p := Vector2(1400, 300)
	var g := cam.unproject(p)
	cam.zoom_about(p, 1.0 / cfg.zoom_step, cfg.zoom_ortho_min, cfg.zoom_ortho_max)
	assert_almost_eq(cam.ortho, cfg.grid_ortho / cfg.zoom_step, 0.001, "one notch is one factor")
	assert_almost_eq(cam.project(g), p, Vector2(0.01, 0.01), "the point under the cursor stays put")
	for k in 60:
		cam.zoom_about(p, cfg.zoom_step, cfg.zoom_ortho_min, cfg.zoom_ortho_max)
	assert_almost_eq(cam.ortho, cfg.zoom_ortho_max, 0.001, "clamped")
	var before := cam.project(Vector3.ZERO)
	cam.pan_px(Vector2(100, -40))
	assert_almost_eq(cam.project(Vector3.ZERO), before - Vector2(100, -40), Vector2(0.01, 0.01), "the city slides")


func test_network_decal_buffers_from_a_graph() -> void:
	var nodes: Array[Dictionary] = [
		{"id": &"a", "color": Palette.CORP_HALCYON, "kind": CityMapOverlay.KIND_TIER, "tier": 2},
		{"id": &"b", "color": Palette.CELL_TURF, "mark": CityMapOverlay.MARK_SPRAY, "tier": 1},
		{"id": &"home", "color": Palette.CELL_TURF, "kind": CityMapOverlay.KIND_HOME, "big": true}]
	var edges: Array[Dictionary] = [{"a": &"a", "b": &"b", "color": Palette.NET_CYAN, "width": 2.0},
		{"a": &"b", "b": &"home", "color": Palette.CELL_TURF, "width": 3.5, "flow": true},
		{"a": &"a", "b": &"home", "color": Palette.CORP_HALCYON, "dashed": true, "arrows": true, "flow": true}]
	var lots := {&"a": Vector2i(30, 10), &"b": Vector2i(34, 10), &"home": Vector2i(34, 16)}
	var routes := [PackedVector2Array([Vector2(30.5, 10.5), Vector2(34.5, 10.5)]),
		PackedVector2Array([Vector2(34.5, 10.5), Vector2(34.5, 16.5)]),
		PackedVector2Array([Vector2(30.5, 10.5), Vector2(30.5, 16.5), Vector2(34.5, 16.5)])]
	var d := CityNetworkData.from_graph(cfg, nodes, edges, func(id: StringName) -> Vector2i: return lots[id],
		func(k: int) -> PackedVector2Array: return routes[k])
	assert_eq(d.nodes.size(), 3)
	assert_eq(d.nodes[0]["state"], CityNetworkData.NodeState.CORPORATE)
	assert_eq(d.nodes[1]["state"], CityNetworkData.NodeState.CLAIMED)
	assert_eq(d.nodes[2]["state"], CityNetworkData.NodeState.HOME)
	assert_eq(d.segments.size(), 4, "one segment per street run")
	var last: Dictionary = d.segments[3]
	assert_eq(int(last["flags"]), CityNetworkData.FLAG_DASHED | CityNetworkData.FLAG_FLOW | CityNetworkData.FLAG_THREAT)
	assert_almost_eq(float(last["u0"]), 6.0 * cfg.lot_bu, 0.001, "length along the link before the bend")
	var img := d.segment_image(cfg.net_points_max)
	assert_eq(img.get_width(), cfg.net_points_max)
	var px := img.get_pixel(0, 0)
	var a := CityIsoCamera.lot_to_world(cfg, Vector2(30.5, 10.5))
	assert_almost_eq(Vector2(px.r, px.g), Vector2(a.x, a.z), Vector2(0.001, 0.001), "the buffer holds world points")
	var ni := d.node_image(cfg.net_nodes_max)
	assert_almost_eq(ni.get_pixel(2, 0).b, 1.4, 0.001, "big nodes")
	assert_almost_eq(ni.get_pixel(0, 1).a, 2.0, 0.001, "tier")


func test_city_view_layers_and_picking_api() -> void:
	var view := CityView3D.new()
	view.size = Vector2i(1280, 720)
	view.use_model(model)
	add_child_autofree(view)
	for n in CityView3D.LAYERS:
		assert_not_null(view.layer(n), "layer %s" % n)
	var probe := MeshInstance3D.new()
	view.add_to_layer(&"traffic", probe, true)
	assert_eq(probe.get_parent(), view.layer(&"traffic"))
	assert_true(probe.get_layer_mask_value(CityView3D.GROUND_LAYER), "drawn in the ground pass")
	var seen: Array = []
	view.camera_changed.connect(func(c: CityIsoCamera) -> void: seen.append(c.ortho))
	var target := view.lot_world(Vector2(PART.get_center()) + Vector2(0.5, 0.5))
	view.set_iso(CityIsoCamera.make(cfg, target, 300.0, Vector2(1280, 720)))
	assert_eq(seen, [300.0], "layers hear the camera")
	assert_eq(view.band, CityLod.Band.RAID)
	assert_eq(view.building_lod, 0)
	assert_almost_eq(view.project(target), Vector2(640, 360), Vector2(0.01, 0.01))
	var hit := view.pick(Vector2(640, 360))
	assert_eq(hit["prism"], model.pick(view.iso, Vector2(640, 360)), "pick() is the model's")
	assert_eq(view.lot_at(Vector2(640, 360)), PART.get_center(), "the ground lot under the centre")
	assert_ne(view.landmark_slot(&"halcyon"), Transform3D(), "Halcyon's landmark slot")
	var r: Rect2i = model.hqs[&"halcyon"]
	assert_almost_eq(view.landmark_slot(&"halcyon").origin, view.lot_world(Vector2(r.get_center())), Vector3.ONE * 0.001)


func test_ambient_pauses_under_reduce_motion_and_when_covered() -> void:
	var view := CityView3D.new()
	view.use_model(model)
	add_child_autofree(view)
	assert_eq(view.ambient_scale, 1.0)
	view.covered = true
	assert_eq(view.ambient_scale, 0.0, "a covered map pauses its ambient layers")
	view.covered = false
	var was := Settings.reduce_motion
	Settings.reduce_motion = true
	Settings.changed.emit()
	assert_eq(view.ambient_scale, 0.0, "reduce motion stills them")
	Settings.reduce_motion = was
	Settings.changed.emit()
	assert_eq(view.ambient_scale, 1.0)
