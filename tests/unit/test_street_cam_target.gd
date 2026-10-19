extends GutTest
## STREET-CAM (art-pass A-025): the red TARGET pencil word and its circle stay inside the safe frame (the usable area), never cut
## by it. For campaign seeds 1..20 on the street netrun's OVERVIEW pose at 1080p, the TARGET word's padded box (the rule
## `StreetRouteRules.target_word_place`, the one the overlay lays with) lies inside the usable frame whenever the circle is drawn.

const SEEDS := 20
const CORPS: Array[StringName] = [&"halcyon", &"meridian", &"orbital", &"rebel_cell", &"solace"]


func after_each() -> void:
	RunManager.reset()


func test_the_word_flips_to_the_circles_inside_at_the_right_edge() -> void:
	var frame := Rect2(0, 0, 1000, 600)
	var size := Vector2(80, 24)
	var a := StreetRouteRules.target_word_place(Vector2(400, 300), 45.0, size, 8.0, frame)
	assert_false(a["flipped"], "room on the right: the word sits right of the circle")
	var b := StreetRouteRules.target_word_place(Vector2(960, 300), 45.0, size, 8.0, frame)
	assert_true(b["flipped"], "at the right edge the word flips to the circle's left")
	assert_true(frame.encloses(b["rect"]))
	var c := StreetRouteRules.target_word_place(Vector2(40, 20), 45.0, size, 8.0, frame)
	assert_true(frame.encloses(c["rect"]), "the last clamp keeps it in the frame")


func test_the_target_word_is_inside_the_safe_frame_for_seeds_1_to_20() -> void:
	RunManager.save_slot = "gut_street_cam"
	RunManager.scene_switching_enabled = false
	var cfg := CityView3D.CONFIG
	var rc := StreetRouteConfigData.shipped()
	var fr: Dictionary = rc.frame
	var usable := Rect2(Vector2(float(fr["left_px"]), float(fr["top_px"])),
		Vector2(1920.0 - float(fr["left_px"]) - float(fr["right_px"]), 1080.0 - float(fr["top_px"]) - float(fr["bottom_px"])))
	var local := Rect2(Vector2.ZERO, usable.size)
	var rr := float(rc.stickers["radius_px"]) * StreetRouteOverlay.TARGET_SHARE
	var wsz := PencilSet.word_size(StreetRouteOverlay.WORD_TARGET, StreetRouteOverlay.TARGET_FONT)
	var pad := wsz.x * StreetRouteOverlay.TARGET_WORD_PAD
	var checked := 0
	var flipped: Array[int] = []
	var bad: Array[String] = []
	for s in range(1, SEEDS + 1):
		RunManager.reset()
		RunManager.new_campaign(s, CORPS[s % CORPS.size()])
		var sites := RunManager.launchable_sites()
		if sites.is_empty():
			continue
		RunManager.netrun = null
		var session := RunManager.start_run(&"", sites[0].id)
		if session == null:
			continue
		var d := StreetRouteData.build(session, CityModel.shared(cfg, CityPlan.current_seed()), cfg, CityLayout.site_points(RunManager.corporation))
		if d.error != "":
			continue
		var pose: NetrunPose = d.overview_state()["pose"]
		var tid := StreetRouteRules.target_of(d.run_graph)
		var room: Dictionary = d.rooms()[tid]
		var pts: Array = []
		for q: Array in room["front"]:
			var p: Array = pose.proj([q[0], q[1], float(q[2]) + float(room.get("ground_z", 0.0))])
			if p.is_empty():
				pts = []
				break
			pts.append(Vector2(p[0], p[1]))
		if pts.size() < 4:
			continue
		var idx := [0, 1, 2, 3]
		idx.sort_custom(func(a: int, b: int) -> bool: return pts[a].x < pts[b].x)
		var left := [pts[idx[0]], pts[idx[1]]]
		left.sort_custom(func(a: Vector2, b: Vector2) -> bool: return a.y < b.y)
		var c: Vector2 = (left[0] as Vector2).lerp(left[1], float((rc.stickers["anchor"] as Array)[1])) - usable.position
		if not local.has_point(c):
			continue       # the circle is not drawn (the edge arrow shows instead)
		checked += 1
		var place := StreetRouteRules.target_word_place(c, rr, wsz, pad, local)
		if place["flipped"]:
			flipped.append(s)
		if not local.encloses(place["rect"]):
			bad.append("seed %d %s in %s" % [s, str(place["rect"]), str(local)])
	assert_gt(checked, 0)
	gut.p("TARGET word: %d seeds checked, flipped at %s" % [checked, str(flipped)])
	assert_eq(bad, [], "TARGET word outside the safe frame: %s" % str(bad))
