extends GutTest
## NA-23: the street route page on the real netrun scene (headless: the view keeps its projection, occlusion and input; nothing
## renders). Keys select, Z flips OVERVIEW, Enter confirms, Esc backs out; the selection is a node of the run's graph; the 7.1
## occlusion written on the city equals the helper's block and never touches a route building; the hover power cut lights the
## branch; the TARGET arrow follows the visible-share rule; the wax stays clear of stickers and UI; layout holds at 1280 x 720.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCRIPT := preload("res://scripts/ui/netrun_scene.gd")

var _scene: Control = null


func before_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_na23_flow"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()
	SCRIPT.street_route = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	_scene = load(NETRUN).instantiate()
	holder.add_child(_scene)
	_scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	# NA-12: the street netrun still builds on the fixed city (StreetRouteView.build_data reads cfg.city_seed; NA-25b owns the
	# switch to CityPlan.current_seed()), so this flow pins the fixed city (city_seed 0) its 1080p room floors were measured on.
	RunManager.campaign.city_seed = 0
	_scene.start_run(1)
	await get_tree().process_frame
	await get_tree().process_frame


func after_each() -> void:
	SCRIPT.street_route = true
	CityBakeCache.shutdown()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _key(code: int) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = code
	e.pressed = true
	return e


func _view() -> StreetRouteView:
	return _scene.street_view


func test_the_street_page_mounts_with_the_runs_options() -> void:
	var v := _view()
	assert_not_null(v, "the street view is the route page")
	assert_eq(v.current_view(), StreetRouteRules.View.DECISION, "the page opens on the DECISION")
	var opts: Array = v.run_state()["options"]
	var avail: Array[StringName] = RunManager.netrun.available_nodes()
	assert_eq(opts.size(), avail.size())
	for i in opts.size():
		assert_eq(opts[i], String(avail[i]), "the options are the session's choices in order")
		assert_true(v.rig.room_mesh(opts[i]) != null, "every option has a drawn room")


func test_keys_select_z_flips_enter_confirms() -> void:
	var v := _view()
	var opts: Array = v.run_state()["options"]
	var seen: Array = []
	v.node_selected.connect(func(id: String) -> void: seen.append(id))
	v._unhandled_key_input(_key(KEY_1))
	assert_eq(v.selected_id, opts[0], "key 1 selects the first option")
	assert_eq(seen, [opts[0]])
	assert_eq(v.current_view(), StreetRouteRules.View.HOVER, "a selected option shows in HOVER")
	assert_true(RunManager.netrun.available_nodes().has(StringName(v.selected_id)), "the selection is a node of the graph the session offers")
	assert_eq(_scene.route_selected(), StringName(opts[0]), "the ROUTE window confirm names it")
	v._unhandled_key_input(_key(KEY_Z))
	assert_eq(v.base_view, StreetRouteRules.View.OVERVIEW)
	assert_ne(v.current_view(), StreetRouteRules.View.HOVER, "OVERVIEW has no hover camera")
	v._unhandled_key_input(_key(KEY_Z))
	assert_eq(v.base_view, StreetRouteRules.View.DECISION)


func test_esc_backs_out_before_pausing() -> void:
	var v := _view()
	var paused: Array = [0]
	v.pause_requested.connect(func() -> void: paused[0] += 1)
	v._unhandled_key_input(_key(KEY_1))
	v.set_base_view(StreetRouteRules.View.OVERVIEW)
	assert_eq(v.press_escape(), StreetRouteRules.Esc.CLEAR_FOCUS)
	assert_eq(v.selected_id, "")
	assert_eq(v.press_escape(), StreetRouteRules.Esc.BACK_TO_DECISION)
	assert_eq(v.base_view, StreetRouteRules.View.DECISION)
	assert_eq(paused[0], 0)
	assert_eq(v.press_escape(), StreetRouteRules.Esc.PAUSE)
	assert_eq(paused[0], 1, "only then the pause menu")


func test_enter_confirms_the_selection_and_enters_the_node() -> void:
	var v := _view()
	var opts: Array = v.run_state()["options"]
	var got: Array = []
	v.node_confirmed.connect(func(id: String) -> void: got.append(id))
	v._unhandled_key_input(_key(KEY_ENTER))
	assert_eq(got, [], "nothing selected: Enter confirms nothing")
	v._unhandled_key_input(_key(KEY_2 if opts.size() > 1 else KEY_1))
	var want: String = opts[1 if opts.size() > 1 else 0]
	v._unhandled_key_input(_key(KEY_ENTER))
	assert_eq(got, [want])
	assert_ne(RunManager.netrun.run.current_node_id, &"", "the run entered the node")
	assert_eq(String(RunManager.netrun.run.current_node_id), want)


func test_the_occlusion_on_the_city_equals_the_helper_and_spares_the_route() -> void:
	var v := _view()
	var st := v.data.decision_state("", v.run_state()["options"])
	var rows: Array = (st["rec"]["occlusion"] as Dictionary)["buildings"]
	assert_gt(rows.size(), 0, "the DECISION cuts or ghosts something in front of the rooms")
	var oc := NetrunArtConfigData.shipped().occlusion
	var route := v.data.route_bids()
	for r: Dictionary in rows:
		var bid := String(r["bid"])
		assert_false(route.has(bid), "%s: a route building is never an occluder" % bid)
		var now := v.rig.occlusion_of(bid)
		assert_almost_eq(float(now[0]), float(r["cut_height"]), 0.02, "%s cut height eased to the helper's" % bid)
		assert_almost_eq(float(now[1]), float(r["opacity"]), 0.001)
		assert_gte(float(now[1]), float(oc["ghost"]) - 0.001, "never fully hidden: opacity stays at the ghost level or above")
	for bid: String in route:
		for g: Array in v.rig._prism_geom[bid]:
			var w := v.rig.view.prism_w(int(g[0]))
			assert_true(bool(NetrunInstancePack.unpack(w)["route"]), "%s carries the route bit" % bid)
			assert_false(NetrunInstancePack.is_occluded(w), "%s is neither cut nor ghosted" % bid)


func test_occlusion_restores_when_the_cone_moves_away() -> void:
	var v := _view()
	var rows: Array = (v.data.decision_state("", v.run_state()["options"])["rec"]["occlusion"] as Dictionary)["buildings"]
	var bid := String(rows[0]["bid"])
	v.set_base_view(StreetRouteRules.View.OVERVIEW)
	var ov: Array = (v.data.overview_state()["rec"]["occlusion"] as Dictionary)["buildings"]
	var still := false
	for r: Dictionary in ov:
		if String(r["bid"]) == bid:
			still = true
	if not still:
		var now := v.rig.occlusion_of(bid)
		assert_almost_eq(float(now[1]), 1.0, 0.001, "a building out of the new cone is whole again")


func test_hover_cuts_power_to_the_rest_and_leaving_restores() -> void:
	var v := _view()
	var opts: Array = v.run_state()["options"]
	var g := v.rig.grade()
	assert_eq(float(g.get_shader_parameter(&"k")), 0.0, "idle: no grade")
	v._set_hover(String(opts[0]))
	assert_eq(v.current_view(), StreetRouteRules.View.HOVER)
	assert_eq(float(g.get_shader_parameter(&"k")), 1.0, "the cut is on")
	assert_true(v._branch.has(String(opts[0])))
	assert_true(v._branch.has(StreetRouteRules.target_of(v.data.run_graph)), "the whole branch to the TARGET lights")
	var cfg := StreetRouteConfigData.shipped().hover
	assert_eq(float(g.get_shader_parameter(&"cut_level")), float(cfg["cut_level"]))
	assert_eq(float(g.get_shader_parameter(&"branch_boost")), float(cfg["branch_boost"]))
	if opts.size() > 1:
		var other := String(opts[1])
		assert_false(v._branch.has(other), "a sibling option is outside the branch")
		var lit := v.rig.room_box_px(String(opts[0])).get_center() * float(cfg["mask_scale"])
		var dark := v.rig.room_box_px(other).get_center() * float(cfg["mask_scale"])
		assert_gt(v._mask_img.get_pixelv(Vector2i(lit)).r, 0.9, "the hovered room is on the mask")
		assert_lt(v._mask_img.get_pixelv(Vector2i(dark)).r, 0.1, "the other option is not")
	v._set_hover("")
	assert_eq(float(g.get_shader_parameter(&"k")), 0.0, "leaving restores the picture")
	assert_eq(v.overlay.modulate, Color.WHITE, "the overlay (the TARGET arrow) is never dimmed")
	assert_lt(v.rig.get_index(), v.overlay.get_index(), "the grade is under the overlay")


func test_target_arrow_follows_the_visible_share_rule() -> void:
	var v := _view()
	await get_tree().process_frame
	var o := v.overlay
	var cfgt := StreetRouteConfigData.shipped().target
	var share := o.target_share()
	assert_eq(o.arrow_showing(), StreetRouteRules.arrow_on(share, false, float(cfgt["switch_share"]), float(cfgt["hysteresis"])) or o.arrow_showing())
	v.set_base_view(StreetRouteRules.View.OVERVIEW)
	await get_tree().process_frame
	await get_tree().process_frame
	assert_gt(o.target_share(), 0.5, "the whole route is in the OVERVIEW frame")
	assert_false(o.arrow_showing(), "TARGET on screen: no arrow, the red circle only")
	v.set_base_view(StreetRouteRules.View.DECISION)
	await get_tree().process_frame
	await get_tree().process_frame
	var off := o.target_share() <= float(cfgt["switch_share"])
	assert_eq(o.arrow_showing(), off, "the DECISION frame has the TARGET off screen (or past half): the arrow shows exactly then")


func test_wax_stays_clear_of_stickers_chips_and_ui() -> void:
	var v := _view()
	await get_tree().process_frame
	var o := v.overlay
	var ui := Rect2(0, 0, 1280, 60)
	o.avoid = [ui]
	var runs := o.link_runs()
	assert_gt(runs.size(), 0, "links are drawn")
	var pad := float(StreetRouteConfigData.shipped().links["clear_pad_px"]) * o.k()
	var r := o.sticker_radius()
	var stickers := o.sticker_rects()
	for run: PackedVector2Array in runs:
		for p in run:
			assert_false(ui.has_point(p), "no pencil inside a UI rect")
			for sr in stickers:
				var c := sr.get_center()
				# a sticker ring is 2r wide; a number chip (chip_px 26 vs radius_px 26) is half of that: the old `<=` test took
				# chips for rings, which only failed once NA-11 moved a pencil past a chip
				if absf(sr.size.x - r * 2.0) < 0.1 and absf(sr.size.x - sr.size.y) < 0.1:
					assert_gte(c.distance_to(p), r + pad - 0.5, "no pencil inside a sticker ring + pad")
				else:
					assert_false(sr.grow(pad - 0.5).has_point(p), "no pencil under a number chip")
	for rc in o.arrow_rects():
		assert_true(o.usable.grow(2.0).encloses(rc) or rc.size == Vector2.ZERO, "the arrow stands inside the usable area, clear of the UI")


func test_layout_at_1280_by_720() -> void:
	var v := _view()
	var o := v.overlay
	assert_gte(o.sticker_radius() * 2.0, 24.0, "every sticker is at least 24 px")
	var opts: Array = v.run_state()["options"]
	var chip := float(StreetRouteConfigData.shipped().stickers["chip_px"]) * o.k()
	assert_gte(chip, 16.0, "the option number chips are legible (16 px or more)")
	# Rooms at OVERVIEW 1080p: the twin's reference frame.
	var ov := v.data.overview_state()["pose"] as NetrunPose
	for id: String in v.data.rooms():
		var c: PackedVector2Array = []
		for q: Array in v.data.rooms()[id]["front"]:
			c.append(Vector2(ov.proj([q[0], q[1], float(q[2]) + float(v.data.rooms()[id].get("ground_z", 0.0))])[0], ov.proj([q[0], q[1], float(q[2]) + float(v.data.rooms()[id].get("ground_z", 0.0))])[1]))
		var h := 0.0
		for p in c:
			for p2 in c:
				h = maxf(h, absf(p.y - p2.y))
		# The derive's span rule (NA-21) sizes the rooms from the first layer: 46 px there; a farther column is smaller by perspective
		# (43 px measured on seed 1, reported in the NA-23 hand-back).
		var floor_px := 46.0 if int(v.data.rooms()[id]["layer"]) == 1 else 40.0
		assert_gte(h, floor_px, "%s is tall enough at OVERVIEW, 1080p" % id)
	assert_gt(opts.size(), 0)


func _open_window_count(v: StreetRouteView) -> int:
	var boxes: PackedVector4Array = v.rig.view.building_material().get_shader_parameter(&"room_box")
	var n := 0
	for b in boxes:
		if b != Vector4():
			n += 1
	return n


func test_an_unrevealed_room_keeps_the_closed_facade() -> void:
	var v := _view()
	var ids: Array = v.rig.room_ids()
	assert_gt(ids.size(), 0)
	for id: String in ids:
		assert_true(v.rig.room_is_open(id), "at rest every room is open: %s" % id)
	assert_eq(_open_window_count(v), ids.size(), "each open room has its window cut in the wall")
	v.entry_begin()
	for id: String in ids:
		assert_false(v.rig.room_is_open(id), "the dive starts on closed rooms: %s" % id)
	assert_eq(_open_window_count(v), 0, "no wall is cut: the building keeps its windows and wash, never a black box")
	v.entry_end()
	assert_eq(_open_window_count(v), ids.size(), "the end state of the entry opens every room again")


func test_the_street_look_is_set_on_the_route_street_only() -> void:
	var v := _view()
	var look: Dictionary = StreetRouteConfigData.shipped().look
	var bm := v.rig.view.building_material()
	assert_almost_eq(float(bm.get_shader_parameter(&"look_blend")), 1.0, 0.0001, "the street runs the netrun look in full")
	for k: String in look["building"]:
		assert_almost_eq(float(bm.get_shader_parameter(StringName(k))), float(look["building"][k]), 0.0001, "building.%s" % k)
	var lane := v.rig.view.lane_material()
	assert_true(lane.shader.resource_path.ends_with("route_lane.gdshader"), "the lane lines are the quiet route lane")
	assert_almost_eq(float(lane.get_shader_parameter(&"lane_sat")), float(look["lane"]["sat"]), 0.0001, "desaturated lane lines")
