extends GutTest
## LOOK Solace THE BLOOM A "Necrosis" (fast tier): the look mapper `BloomLook`. It is pure and deterministic: the same state and layout give
## the same look dictionary (the preview is the result), strength 0 / a disabled Bloom is off, the keep-outs come from the layout, the front
## moves with the layers and the band picks the concept's per-state tune, the HQ front rides the route nodes and the decision lifts it, the
## ribbons are deterministic and keep out of the boxes, and the shaders that carry the skin gate it on `bl_strength`.

const SKIN_SHADERS: Array[String] = ["res://shaders/city/city_building.gdshader", "res://shaders/city/wet_street.gdshader",
	"res://shaders/city/dress_sign.gdshader", "res://shaders/city/dress_solid.gdshader", "res://shaders/street_r2/street_r2_surface.gdshader",
	"res://shaders/street_r2/street_r2_sign.gdshader", "res://shaders/city/hq_solace_pbr.gdshader", "res://shaders/city/hq_solace_window.gdshader"]


## A small street derive: the street runs from (100, 0) to (0, 0) (along -x), the rooms stand on the +y side, three layers 12 BU apart.
func _derive() -> Dictionary:
	var rooms := {}
	var cols: Array = []
	for l in [1, 2, 3]:
		var x1 := 100.0 - 12.0 * float(l)
		var x0 := x1 - 6.0
		rooms["L%dN0" % l] = {"layer": l, "kind": "router",
			"front": [[x0, 3.0, 0.12], [x1, 3.0, 0.12], [x1, 3.0, 3.68], [x0, 3.0, 3.68]],
			"back": [[x0, 5.6, 0.12], [x1, 5.6, 0.12], [x1, 5.6, 3.68], [x0, 5.6, 3.68]]}
		cols.append({"layer": l, "u0": 100.0 - x1, "u1": 100.0 - x0})
	var edges: Array = [{"a": "L1N0", "b": "L2N0", "type": "facade", "path": [[78.0, 2.4, 1.9], [72.0, 2.4, 1.9], [72.0, 2.4, 1.9], [66.0, 2.4, 1.9]]}]
	return {"street": {"a": [100.0, 0.0], "c": [0.0, 0.0]}, "nrm": [0.0, 1.0], "rooms": rooms, "col_info": cols, "edges": edges}


func _state(front_milli: int, layer_milli: int, enabled: bool = true) -> BloomState:
	var b := BloomState.new()
	b.enabled = enabled
	b.front_milli = front_milli
	b.layer_milli = layer_milli
	return b


func _cfg() -> CampaignConfigData:
	return load("res://content/config/campaign_config.tres") as CampaignConfigData


func test_shipped_config_validates() -> void:
	assert_eq(BloomLook.config().validate(), PackedStringArray())


func test_a_bad_config_is_reported() -> void:
	var c := RcLookBloomConfig.new()
	assert_gt(c.validate().size(), 5, "an empty config misses every block: %s" % str(c.validate().size()))


func test_a_disabled_bloom_is_off() -> void:
	var lay := BloomLook.street_layout(_derive())
	var look := BloomLook.from_state(_state(0, 2000, false), lay, _cfg())
	assert_eq(float(look["strength"]), 0.0)
	assert_eq(float((look["uniforms"] as Dictionary)[&"bl_strength"]), 0.0)
	assert_false(look.has("ribbons"), "an off look draws no ribbons")
	assert_eq(BloomLook.from_state(null, lay, _cfg())["strength"], 0.0)
	assert_eq(BloomLook.at_front(0.5, 2, lay, &"", 0.0)["strength"], 0.0, "strength 0 is off whatever the front")


func test_same_state_same_look() -> void:
	var lay := BloomLook.street_layout(_derive())
	var a := BloomLook.from_state(_state(500, 2000), lay, _cfg())
	var b := BloomLook.from_state(_state(500, 2000), lay, _cfg())
	assert_eq(a, b, "the street look is a function of the state and the layout")
	assert_eq(BloomLook.street_layout(_derive()), lay, "the layout too")


func test_preview_equals_result() -> void:
	# The preview of a node (BloomRules.gap_after_entry / NetrunSession.bloom_preview) and the result of entering it give the same front: the
	# same front figures in give the same uniforms out, whichever way the state got there.
	var lay := BloomLook.street_layout(_derive())
	var cc := _cfg()
	var b := _state(-1500, 1000)
	var look_a := BloomLook.from_state(b, lay, cc)
	b.front_milli += 700
	b.layer_milli = 2000
	var look_b := BloomLook.from_state(b, lay, cc)
	var direct := BloomLook.at_front(-0.8, int(BloomRules.band_for_gap(2800, cc)), lay)
	assert_ne(look_a["front"], look_b["front"], "entering moves the front")
	assert_eq(look_b, BloomLook.at_front(-0.8, int(BloomRules.band_for_gap(2800, cc)), lay), "same front in, same look out")
	assert_eq(float(direct["front"]), float(look_b["front"]))


func test_the_front_moves_with_the_layers() -> void:
	var lay := BloomLook.street_layout(_derive())
	# x = frame x0 - along; the first layer's column centre is at u = 12 + 3 and each layer is 12 BU on
	var x1 := BloomLook.layer_x_at(lay, 1.0)
	var x2 := BloomLook.layer_x_at(lay, 2.0)
	var x3 := BloomLook.layer_x_at(lay, 3.0)
	assert_almost_eq(x1 - x2, 12.0, 1e-3)
	assert_almost_eq(x2 - x3, 12.0, 1e-3)
	assert_almost_eq(BloomLook.layer_x_at(lay, 1.5), (x1 + x2) * 0.5, 1e-3)
	assert_almost_eq(BloomLook.layer_x_at(lay, 0.0), x1 + 12.0, 1e-3, "behind the first layer: the end slope goes on")
	assert_almost_eq(BloomLook.layer_x_at(lay, 4.0), x3 - 12.0, 1e-3, "past the last layer too")


func test_the_band_picks_the_state_tune() -> void:
	var lay := BloomLook.street_layout(_derive())
	var cc := _cfg()
	var creeping := BloomLook.from_state(_state(-500, 2000), lay, cc)   # gap 2.5
	var close := BloomLook.from_state(_state(750, 2000), lay, cc)       # gap 1.25
	var catching := BloomLook.from_state(_state(1400, 2000), lay, cc)   # gap 0.6
	assert_eq(int(creeping["band"]), int(BloomRules.Band.CREEPING))
	assert_eq(int(close["band"]), int(BloomRules.Band.CLOSE))
	assert_eq(int(catching["band"]), int(BloomRules.Band.CATCHING))
	assert_lt(float(creeping["ribbons"]["strength"]), float(close["ribbons"]["strength"]), "creeping: the ribbons are fainter")
	var cu: Dictionary = catching["uniforms"]
	var ku: Dictionary = close["uniforms"]
	assert_gt(float(cu[&"bl_veins"]), float(ku[&"bl_veins"]), "catching: more veins")
	assert_gt(float(cu[&"bl_hatch_k"]), float(ku[&"bl_hatch_k"]), "catching: more hatch")


func test_keep_outs_come_from_the_layout() -> void:
	var lay := BloomLook.street_layout(_derive())
	var boxes: Array = lay["boxes"]
	# 3 rooms + the link's distinct boxes (the path repeats one point: two segments and the point's own box)
	assert_eq(boxes.size(), 6)
	var look := BloomLook.at_front(0.0, 2, lay)
	var u: Dictionary = look["uniforms"]
	assert_gt(int(u[&"bl_box_n"]), 0)
	assert_eq((u[&"bl_box_lo"] as PackedVector3Array).size(), BloomLook.SHADER_BOXES, "the shader's array is always full size")
	# a room's centre is inside its own keep-out box (in the street frame), every room has one
	var x0 := float(lay["x0"])
	var y0 := float(lay["y0"])
	for l in [1, 2, 3]:
		var cx := x0 - (12.0 * float(l) + 3.0)
		var c := Vector3(cx, y0 + 4.3, 1.9)
		var hit := false
		for bx: Array in boxes:
			if c.x > (bx[0] as Vector3).x and c.x < (bx[1] as Vector3).x and c.y > (bx[0] as Vector3).y and c.y < (bx[1] as Vector3).y and c.z > (bx[0] as Vector3).z and c.z < (bx[1] as Vector3).z:
				hit = true
		assert_true(hit, "room of layer %d is kept out" % l)
	# the room boxes carry the margins (+10 % of the size, the jamb in y, the frame ring in z)
	var any_room: Array = boxes[0]
	assert_gt(((any_room[1] as Vector3) - (any_room[0] as Vector3)).x, 6.0, "wider than the room itself")


func test_a_street_in_any_direction_gets_the_same_frame() -> void:
	# a street rotated about the world gives the same layer columns and boxes in the street frame
	var d := _derive()
	var lay0 := BloomLook.street_layout(d)
	var rot := Transform2D(deg_to_rad(37.0), Vector2(5.0, -9.0))
	var st: Dictionary = d["street"]
	st["a"] = _p2(rot * Vector2(100.0, 0.0))
	st["c"] = _p2(rot * Vector2(0.0, 0.0))
	var nr := (rot.basis_xform(Vector2(0.0, 1.0)))
	d["nrm"] = _p2(nr)
	for id: String in d["rooms"]:
		for key: String in ["front", "back"]:
			for p: Array in d["rooms"][id][key]:
				var q := rot * Vector2(float(p[0]), float(p[1]))
				p[0] = q.x
				p[1] = q.y
	for e: Dictionary in d["edges"]:
		for p: Array in e["path"]:
			var q := rot * Vector2(float(p[0]), float(p[1]))
			p[0] = q.x
			p[1] = q.y
	var lay1 := BloomLook.street_layout(d)
	for l in [1, 2, 3]:
		assert_almost_eq(BloomLook.layer_x_at(lay1, float(l)), BloomLook.layer_x_at(lay0, float(l)), 1e-3, "layer %d" % l)
	assert_eq(lay1["boxes"].size(), lay0["boxes"].size())
	for i in lay0["boxes"].size():
		assert_true(((lay1["boxes"][i][0] as Vector3) - (lay0["boxes"][i][0] as Vector3)).length() < 1e-2, "box %d lo" % i)
		assert_true(((lay1["boxes"][i][1] as Vector3) - (lay0["boxes"][i][1] as Vector3)).length() < 1e-2, "box %d hi" % i)


func _p2(v: Vector2) -> Array:
	return [v.x, v.y]


func test_ribbons_are_deterministic_and_keep_out() -> void:
	var lay := BloomLook.street_layout(_derive())
	var look := BloomLook.at_front(1.0, 2, lay)
	var rb: Dictionary = look["ribbons"]
	var m1 := BloomRibbons.build(rb)
	var m2 := BloomRibbons.build(rb)
	assert_not_null(m1)
	var v1: PackedVector3Array = m1.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	var v2: PackedVector3Array = m2.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	assert_eq(v1, v2, "the same look draws the same ribbons")
	assert_gt(BloomRibbons.count(rb), 10, "ribbons are made")
	# the ribbons crawl AHEAD of the front (smaller x) and stay in the ground band / the lowest facade metres
	var zmax := 0.0
	for v in v1:
		zmax = maxf(zmax, v.z)
	assert_lte(zmax, float(rb["facade_h"]) + 0.5, "no ribbon climbs past the facade band")
	var off := BloomLook.at_front(1.0, 2, lay, &"", 0.0)
	assert_null(BloomRibbons.build(off.get("ribbons", {})), "strength 0 draws none")


func test_ribbon_vertices_stay_out_of_the_keep_out_boxes() -> void:
	var lay := BloomLook.street_layout(_derive())
	var rb: Dictionary = BloomLook.at_front(0.0, 2, lay)["ribbons"]
	var m := BloomRibbons.build(rb)
	var verts: PackedVector3Array = m.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	var inside := 0
	# a quad's corners sit up to half a ribbon width off its centre line, so shrink each box by that for the check
	var w := float(rb["width"])
	for v in verts:
		for bx: Array in rb["boxes"]:
			var lo := (bx[0] as Vector3) + Vector3.ONE * w
			var hi := (bx[1] as Vector3) - Vector3.ONE * w
			if v.x > lo.x and v.x < hi.x and v.y > lo.y and v.y < hi.y and v.z > lo.z and v.z < hi.z:
				inside += 1
	assert_eq(inside, 0, "no ribbon enters a route room or a link")


func _hq_layout() -> Dictionary:
	var m := HqCompoundStage.manifest(&"solace")
	var at := Transform3D(Basis(), Vector3(100.0, 0.0, -40.0))
	return BloomLook.hq_layout(m, HqCompoundStage.layout(&"solace"), at)


func test_hq_layout_maps_the_compound_to_plate_units() -> void:
	var lay := _hq_layout()
	var k := float(lay["unit_k"])
	assert_gt(k, 0.0)
	var w2p: Transform3D = lay["w2p"]
	var at: Transform3D = lay["at"]
	assert_true((w2p * at.origin).length() < 1e-4, "the compound's origin is the plate's origin")
	# a point 1 right, 2 up and 3 toward the viewer of the compound (Godot +z) is plate (1, -3, 2) / k
	var p := w2p * (at * Vector3(1.0, 2.0, 3.0))
	assert_true((p - Vector3(1.0, -3.0, 2.0) / k).length() < 1e-3)
	var lz: Dictionary = lay["layer_z"]
	assert_eq(lz.size(), 6, "the six node rows")
	for l in range(2, 7):
		assert_gt(float(lz[l]), float(lz[l - 1]), "the rows climb")
	assert_eq((lay["rooms"] as Array).size(), 13, "the route windows of six floors on both strands and the core are the keep-outs")


func test_hq_front_rides_the_route_nodes_and_the_decision_lifts_it() -> void:
	var lay := _hq_layout()
	var h: Dictionary = BloomLook.config().hq
	var ov := BloomLook.at_front(3.0, 3, lay)
	assert_almost_eq(float(ov["front"]), BloomLook.hq_layer_z(lay, 3.0) + float(h["front_over_node"]), 1e-4)
	assert_gt(BloomLook.hq_layer_z(lay, 4.0), BloomLook.hq_layer_z(lay, 3.0))
	assert_lt(BloomLook.hq_layer_z(lay, 0.0), BloomLook.hq_layer_z(lay, 1.0), "below the first row: the slope goes on")
	var dec := BloomLook.at_front(3.0, 3, lay, BloomLook.VIEW_DECISION)
	assert_almost_eq(float(dec["front"]) - float(ov["front"]), float(h["decision_lift"]), 1e-4, "the decision lifts the front")
	assert_eq(BloomLook.at_front(3.0, 3, lay), ov, "deterministic")
	assert_eq(int(ov["uniforms"][&"bl_room_n"]), (lay["rooms"] as Array).size())
	var hv := BloomLook.haze_volume(ov)
	assert_not_null(hv, "the HQ front carries the spore haze")
	if hv != null:
		hv.free()
	assert_null(BloomLook.haze_volume(BloomLook.at_front(3.0, 3, lay, &"", 0.0)), "none at strength 0")


func test_the_shaders_gate_the_skin_on_the_strength() -> void:
	var inc := FileAccess.get_file_as_string("res://shaders/city/bloom_necrosis.gdshaderinc")
	assert_string_contains(inc, "uniform float bl_strength = 0.0;", "off by default")
	for fn in ["bl_apply_street", "bl_unlit_street", "bl_apply_tube", "bl_dim_tube"]:
		var i := inc.find("%s(" % fn)
		assert_gt(i, 0, fn)
		assert_gt(inc.find("if (bl_strength <= 0.0)", i), i, "%s returns at strength 0" % fn)
	for path in SKIN_SHADERS:
		var code := FileAccess.get_file_as_string(path)
		assert_string_contains(code, "bloom_necrosis.gdshaderinc", path)
		assert_true(code.contains("bl_strength > 0.0") or code.contains("bl_mode") or code.contains("bl_unlit_street"), "%s gates on the Bloom" % path)


func test_every_skin_shader_declares_the_bloom() -> void:
	for path in SKIN_SHADERS:
		var sh := load(path) as Shader
		assert_not_null(sh, path)
		var names := {}
		for d: Dictionary in sh.get_shader_uniform_list():
			names[d["name"]] = true
		assert_true(names.has("bl_strength"), "%s carries bl_strength" % path)
