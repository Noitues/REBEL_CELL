extends GutTest
## NA-23: the street netrun view's rules (key map, view states, Esc / Z, node and link states, the hovered branch, the TARGET arrow
## switch), the seven room silhouettes and the refusal of an unknown kind, the packed `route` bit, and the config. Pure: no scene.

var _rg: Dictionary = {}


func before_all() -> void:
	var w := NaFixture.load_inputs("101")
	_rg = w["run_graph"]


func test_config_validates() -> void:
	assert_eq(StreetRouteConfigData.shipped().validate(), PackedStringArray(), "no missing key or bad range")
	var bad := StreetRouteConfigData.new()
	assert_gt(bad.validate().size(), 0, "an empty config reports its missing keys")


# --- Keys, states, Esc / Z ----------------------------------------------------------------------

func test_number_keys_pick_the_nth_option() -> void:
	var opts := ["L2N0", "L2N1", "L2N2"]
	assert_eq(StreetRouteRules.option_for_key(KEY_1, opts), "L2N0")
	assert_eq(StreetRouteRules.option_for_key(KEY_3, opts), "L2N2")
	assert_eq(StreetRouteRules.option_for_key(KEY_KP_2, opts), "L2N1", "the keypad too")
	assert_eq(StreetRouteRules.option_for_key(KEY_4, opts), "", "a number past the options picks nothing")
	assert_eq(StreetRouteRules.option_for_key(KEY_0, opts), "")
	assert_eq(StreetRouteRules.option_for_key(KEY_A, opts), "", "a letter is not an option")
	assert_eq(StreetRouteRules.option_for_key(KEY_9, ["a", "b", "c", "d", "e", "f", "g", "h", "i"]), "i", "keys 1-9")


func test_z_toggles_overview_and_hover_returns_to_overview() -> void:
	assert_eq(StreetRouteRules.toggled(StreetRouteRules.View.DECISION), StreetRouteRules.View.OVERVIEW)
	assert_eq(StreetRouteRules.toggled(StreetRouteRules.View.OVERVIEW), StreetRouteRules.View.DECISION)
	assert_eq(StreetRouteRules.toggled(StreetRouteRules.View.HOVER), StreetRouteRules.View.OVERVIEW)


func test_esc_lets_go_then_leaves_overview_then_pauses() -> void:
	var V := StreetRouteRules.View
	assert_eq(StreetRouteRules.esc_action(V.DECISION, true), StreetRouteRules.Esc.CLEAR_FOCUS)
	assert_eq(StreetRouteRules.esc_action(V.OVERVIEW, true), StreetRouteRules.Esc.CLEAR_FOCUS, "a hover goes first")
	assert_eq(StreetRouteRules.esc_action(V.OVERVIEW, false), StreetRouteRules.Esc.BACK_TO_DECISION)
	assert_eq(StreetRouteRules.esc_action(V.DECISION, false), StreetRouteRules.Esc.PAUSE)


func test_hover_state_only_in_decision_on_an_option() -> void:
	var V := StreetRouteRules.View
	assert_eq(StreetRouteRules.view_for(V.DECISION, true), V.HOVER)
	assert_eq(StreetRouteRules.view_for(V.DECISION, false), V.DECISION)
	assert_eq(StreetRouteRules.view_for(V.OVERVIEW, true), V.OVERVIEW)


func test_node_and_link_states_follow_the_run() -> void:
	var first := NetrunPoseBuilder.successors(_rg, "")
	var cur := String(first[0])
	var opts := NetrunPoseBuilder.successors(_rg, cur)
	var visited: Array = []
	assert_eq(StreetRouteRules.node_state(_rg, cur, cur, visited, opts), StreetRouteRules.STATE_WALKED, "where the run stands is walked")
	assert_eq(StreetRouteRules.node_state(_rg, String(opts[0]), cur, visited, opts), StreetRouteRules.STATE_NEXT)
	if first.size() > 1:
		assert_eq(StreetRouteRules.node_state(_rg, String(first[1]), cur, visited, opts), StreetRouteRules.STATE_CUT, "a sibling the run passed is cut")
	var far := String(_rg["nodes"][-1]["id"])
	assert_eq(StreetRouteRules.node_state(_rg, far, cur, visited, opts), StreetRouteRules.STATE_LATER)
	assert_eq(StreetRouteRules.link_state(_rg, cur, String(opts[0]), cur, visited, opts), StreetRouteRules.LINK_OPTION)
	var e: Dictionary = (_rg["edges"] as Array)[0]
	assert_eq(StreetRouteRules.link_state(_rg, String(e["a"]), String(e["b"]), "", [], first), StreetRouteRules.LINK_AHEAD)
	assert_eq(StreetRouteRules.link_state(_rg, String(e["a"]), String(e["b"]), String(e["b"]), [String(e["a"])], []), StreetRouteRules.LINK_WALKED)


func test_the_hovered_branch_is_the_node_and_everything_ahead_to_the_target() -> void:
	var first := NetrunPoseBuilder.successors(_rg, "")
	var branch := StreetRouteRules.branch_of(_rg, String(first[0]))
	assert_true(branch.has(String(first[0])))
	assert_true(branch.has(StreetRouteRules.target_of(_rg)), "the whole branch to the TARGET lights")
	var sorted := branch.duplicate()
	IdSort.sort_ids(sorted)
	assert_eq(branch, sorted, "ids sorted, never in dictionary order")
	var last := StreetRouteRules.target_of(_rg)
	assert_eq(StreetRouteRules.branch_of(_rg, last), [last], "the TARGET has nothing beyond it")


func test_the_target_is_on_the_last_layer() -> void:
	var t := StreetRouteRules.target_of(_rg)
	assert_eq(StreetRouteRules.layer_of(_rg, t), int(_rg["layers"]))


# --- TARGET edge arrow (9.5b) -----------------------------------------------------------------

func test_visible_share_of_a_box_in_the_usable_area() -> void:
	var area := Rect2(0, 0, 100, 100)
	assert_almost_eq(StreetRouteRules.visible_share(Rect2(10, 10, 20, 20), area), 1.0, 0.0001)
	assert_almost_eq(StreetRouteRules.visible_share(Rect2(90, 0, 20, 10), area), 0.5, 0.0001)
	assert_eq(StreetRouteRules.visible_share(Rect2(200, 0, 20, 10), area), 0.0, "off screen: nothing visible")
	assert_eq(StreetRouteRules.visible_share(Rect2(), area), 0.0)


func test_arrow_shows_at_or_below_half_visible_and_never_flickers() -> void:
	var c := StreetRouteConfigData.shipped().target
	var sw := float(c["switch_share"])
	var hy := float(c["hysteresis"])
	assert_true(StreetRouteRules.arrow_on(0.0, false, sw, hy), "off screen: the arrow")
	assert_false(StreetRouteRules.arrow_on(1.0, false, sw, hy), "all visible: no arrow")
	assert_true(StreetRouteRules.arrow_on(sw - hy - 0.01, false, sw, hy), "below the band it turns on")
	assert_false(StreetRouteRules.arrow_on(sw, false, sw, hy), "inside the band an off arrow stays off")
	assert_true(StreetRouteRules.arrow_on(sw, true, sw, hy), "inside the band an on arrow stays on")
	assert_false(StreetRouteRules.arrow_on(sw + hy + 0.01, true, sw, hy), "above the band it turns off")
	# A share that wobbles inside the band never flips the arrow.
	var on := true
	var flips := 0
	for share in [0.48, 0.52, 0.49, 0.54, 0.5, 0.53]:
		var now := StreetRouteRules.arrow_on(share, on, sw, hy)
		if now != on:
			flips += 1
		on = now
	assert_eq(flips, 0, "no flicker while the camera moves")


# --- Room silhouettes ---------------------------------------------------------------------------

func test_seven_kinds_have_distinct_silhouettes() -> void:
	assert_eq(StreetRoomKit.KINDS.size(), 7, "the four run-graph types and rest, workshop, cache")
	for i in StreetRoomKit.KINDS.size():
		var a := StreetRoomKit.silhouette(StreetRoomKit.KINDS[i])
		var filled := 0
		for v in a:
			filled += v
		assert_gt(filled, 6, "%s draws props" % StreetRoomKit.KINDS[i])
		for j in range(i + 1, StreetRoomKit.KINDS.size()):
			var b := StreetRoomKit.silhouette(StreetRoomKit.KINDS[j])
			var diff := 0
			for k in a.size():
				if a[k] != b[k]:
					diff += 1
			assert_gt(diff, 12, "%s and %s read differently by shape" % [StreetRoomKit.KINDS[i], StreetRoomKit.KINDS[j]])


func test_an_elite_router_wears_a_crown() -> void:
	var plain := StreetRoomKit.silhouette("router", false)
	var elite := StreetRoomKit.silhouette("router", true)
	assert_ne(plain, elite)


func test_unknown_kinds_are_refused() -> void:
	assert_false(StreetRoomKit.is_kind("boss"))
	assert_false(StreetRoomKit.is_kind(""))
	assert_eq(StreetRoomKit.props("boss"), [])
	var w := NaFixture.load_inputs("101")
	var d := NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"], w["partial_street"])
	var room: Dictionary = (d["rooms"] as Dictionary).values()[0]
	var cfg := StreetRouteConfigData.shipped().rooms
	assert_null(StreetRoomKit.build_mesh(room, "boss", false, Color.WHITE, cfg), "no mesh for an unknown kind")
	assert_true(DressReader.is_room_kind("rest") and DressReader.is_room_kind("workshop") and DressReader.is_room_kind("cache"))
	for k in StreetRoomKit.KINDS:
		assert_true(DressReader.is_room_kind(k), "%s is a kind the data contract knows" % k)


func test_every_kind_builds_a_mesh_on_a_real_room() -> void:
	var w := NaFixture.load_inputs("101")
	var d := NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"], w["partial_street"])
	var room: Dictionary = (d["rooms"] as Dictionary).values()[0]
	var cfg := StreetRouteConfigData.shipped().rooms
	for k in StreetRoomKit.KINDS:
		var rgb: Array = cfg["colors"][k]
		var m := StreetRoomKit.build_mesh(room, k, false, Color(rgb[0], rgb[1], rgb[2]), cfg)
		assert_not_null(m, "%s builds" % k)
		assert_gt(m.get_aabb().size.x, 1.0, "%s has a room's width" % k)
	var vol := StreetRoomKit.volume(room, 0.02)
	assert_false(vol.is_empty())
	var box: Vector4 = vol["box"]
	assert_gt(box.z - box.x, 1.0)
	assert_gt(box.w - box.y, 1.0)


# --- Packed route bit ---------------------------------------------------------------------------

func test_the_route_bit_round_trips_and_is_not_an_occlusion() -> void:
	var w := NetrunInstancePack.pack(20.0, 20.0, 1.0, 0.0, 0.0, false, true)
	assert_true(bool(NetrunInstancePack.unpack(w)["route"]))
	assert_false(NetrunInstancePack.is_occluded(w), "a route building is not drawn as a cut / ghosted one")
	assert_eq(w, float(int(w)), "exact in a float32")
	assert_lt(w, 16777216.0, "below 2^24")
	var cut := NetrunInstancePack.pack(20.0, 4.0, 0.18, 0.6, 0.0, false, true)
	var u := NetrunInstancePack.unpack(cut)
	assert_true(bool(u["route"]))
	assert_true(NetrunInstancePack.is_occluded(cut))
	assert_false(bool(NetrunInstancePack.unpack(NetrunInstancePack.pack(20.0, 4.0, 0.18, 0.6, 0.0))["route"]), "off by default")
