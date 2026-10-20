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
	assert_gt(rows.size(), 0, "the decision cone occludes at least one building")
	v.set_base_view(StreetRouteRules.View.OVERVIEW)
	var ov: Array = (v.data.overview_state()["rec"]["occlusion"] as Dictionary)["buildings"]
	var in_ov := {}
	for r: Dictionary in ov:
		in_ov[String(r["bid"])] = true
	for r: Dictionary in rows:
		var bid := String(r["bid"])
		if not in_ov.has(bid):
			assert_almost_eq(float(v.rig.occlusion_of(bid)[1]), 1.0, 0.001, "a building out of the new cone is whole again")


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


# --- NA-25b: the facade dissolve ------------------------------------------------------------------------------

func test_a_room_dissolves_open_by_a_share_and_lands_on_the_same_end_state() -> void:
	var v := _view()
	var id: String = v.rig.room_ids()[0]
	var bm := v.rig.view.building_material()
	v.rig.set_room_dissolve(id, 0.0)
	assert_false(v.rig.room_is_open(id), "0: the closed facade, the room hidden")
	assert_almost_eq(v.rig.room_dissolve_of(id), 0.0, 0.0001)
	v.rig.set_room_dissolve(id, 0.4)
	assert_true(v.rig.room_is_open(id), "between: the room shows through the dissolving wall")
	assert_almost_eq(v.rig.room_dissolve_of(id), 0.4, 0.0001)
	var opens: PackedFloat32Array = bm.get_shader_parameter(&"room_open")
	var slots := 0
	for k in opens:
		if k > 0.39 and k < 0.41:
			slots += 1
	assert_eq(slots, 1, "the shader reads the share for that one room's slot")
	v.rig.set_room_dissolve(id, 1.0)
	var open_state := [v.rig.room_is_open(id), v.rig.room_dissolve_of(id), _open_window_count(v)]
	v.rig.set_room_dissolve(id, 0.0)
	v.rig.set_room_open(id, true)
	assert_eq([v.rig.room_is_open(id), v.rig.room_dissolve_of(id), _open_window_count(v)], open_state, "set_room_open(true) is dissolve 1: one end state")
	v.rig.set_room_dissolve(id, 7.0)
	assert_almost_eq(v.rig.room_dissolve_of(id), 1.0, 0.0001, "the share is clamped")


func test_the_reveal_dissolves_each_layer_by_its_timeline_share() -> void:
	var live_before := Motion.force_live
	Motion.force_live = true  # headless takes every beat as 0 s; the share needs the beat's real length
	var v := _view()
	var layers := int(v.data.run_graph["layers"])
	var total := Motion.seconds(&"entry_reveal")
	var s := EntryBeats.layer_times(1, layers, total)
	v.entry_begin()
	var first: String = ""
	for id: String in v.rig.room_ids():
		if StreetRouteRules.layer_of(v.data.run_graph, id) == 1:
			first = id
			break
	assert_ne(first, "")
	v.entry_reveal(float(s["up_start"]) + (float(s["up_end"]) - float(s["up_start"])) * 0.5, total)
	var half := v.rig.room_dissolve_of(first)
	assert_gt(half, 0.0, "mid-rise the facade is partly dissolved")
	assert_lt(half, 1.0)
	v.entry_reveal(total, total)
	assert_almost_eq(v.rig.room_dissolve_of(first), 1.0, 0.0001, "the end of the beat has it whole")
	v.entry_end()
	assert_almost_eq(v.rig.room_dissolve_of(first), 1.0, 0.0001, "and the entry's end state keeps it")
	Motion.force_live = live_before


# --- NA-25b: the jack-out from an end-of-run page, the zoom reusing the dive -------------------------------------

func test_an_end_page_rebuilds_the_street_to_play_the_dive_backwards() -> void:
	# Headless nothing animates, so the page never starts the reverse itself; the rebuild must still work on a run with no options.
	assert_false(_scene._street_reverse_possible(), "headless: no dive to play")
	var s := RunManager.netrun
	var old: StreetRouteView = _scene.street_view
	old.queue_free()
	_scene.street_view = null
	await get_tree().process_frame
	await _scene._street_reverse_from_page()
	var v: StreetRouteView = _scene.street_view
	assert_not_null(v, "the street is rebuilt behind the page")
	assert_eq((v.run_state()["options"] as Array).size(), 0, "an end page has no options")
	assert_eq(v.run_state()["current"], String(s.run.current_node_id))
	assert_true(v.visible)
	assert_null(_scene.entry_cover, "the reverse ended: no cover is left playing")
	_scene._set_entry_ui(0.0)
	assert_false(_scene.scrim.visible, "no page scrim is left over the dive back")
	_scene._set_entry_ui(1.0)
	assert_true(_scene.scrim.visible, "and it is back with the page")


func test_the_grid_zoom_out_and_in_runs_the_dive_hooks_and_changes_no_state() -> void:
	var s := RunManager.netrun
	var before := s.state_hash()
	await _scene._zoom_out_to_grid()
	assert_true(_scene._grid_zoomed, "the zoom out ends on the Grid page")
	var back := _scene._panel.find_child("GridZoom", true, false) as Button
	back.pressed.emit()
	assert_false(_scene._grid_zoomed)
	await get_tree().process_frame
	await get_tree().process_frame
	assert_false(_scene._zoom_in_wanted, "the request is spent")
	assert_not_null(_scene.street_view, "the way back down is the street page again")
	assert_false(_scene.street_view.entry_active, "the dive ended on the DECISION state")
	assert_eq(_scene.street_view.current_view(), StreetRouteRules.View.DECISION)
	assert_eq(s.state_hash(), before, "a zoom is a view")


func test_a_street_jack_out_ends_on_the_hq_through_the_street_link() -> void:
	# Headless Fx.jack_out_link falls back to the plain jack-out: the switch runs once, at once.
	var hit := [0]
	await Fx.jack_out_link(func() -> void: hit[0] += 1, {"street": true, "from": "A", "to": "B"}, "HQ")
	assert_eq(hit[0], 1, "the switch ran")
	RunManager.street_link = {"street": true}
	RunManager.reset()
	assert_true(RunManager.street_link.is_empty(), "a new campaign forgets the last jack's link")


func test_the_operative_token_has_a_loaded_texture_and_sits_on_the_current_room() -> void:
	var v := _view()
	var o := v.overlay
	assert_false(is_finite(o.token_center().x), "no current room, no token")
	var opts: Array = v.run_state()["options"]
	assert_gt(opts.size(), 0, "the street offers rooms")
	v.set_run_state(String(opts[0]), [], [], false)
	await get_tree().process_frame
	await get_tree().process_frame
	var tex := o.token_texture()
	assert_not_null(tex, "the token texture loads")
	assert_gt(tex.get_width(), 0, "the token texture has pixels")
	assert_same(tex, o.token_texture(), "the token holds one cached texture (a fresh load() per draw drew white)")
	var want := o.sticker_pos(String(opts[0])) + StreetRouteOverlay.TOKEN_OFFSET_R * o.sticker_radius()
	assert_lt(o.token_center().distance_to(want), 3.0, "the token stands at the current room's marker, by its pin offset")
