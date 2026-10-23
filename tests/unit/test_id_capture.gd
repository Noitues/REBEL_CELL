extends GutTest
## NA-ID: the id capture (IdCapture, IdCaptureClasses, id_flat.gdshader). Headless: the class table, the byte rules, the canonical
## capture.json, the class assignment of a view's meshes and that begin / end leave the view as it was (state hash). The pixels
## (class set, byte-identity of two runs) need a renderer: tools/netrun_art/id_capture_lab.tscn through tools/run_windowed.py.


func _view() -> CityView3D:
	var v := CityView3D.new()
	v.size = Vector2i(160, 90)
	v.use_model(CityModel.build(CityView3D.CONFIG, 7, Rect2i(20, -4, 6, 6)))
	add_child_autofree(v)
	return v


func _mesh(parent: Node) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	m.mesh = BoxMesh.new()
	parent.add_child(m)
	return m


## A hash of what the id pass may touch: every geometry instance's override / visibility, the environment, the camera.
func _state(v: CityView3D) -> int:
	var parts: Array = []
	for g in v.find_children("*", "GeometryInstance3D", true, false):
		var gi := g as GeometryInstance3D
		parts.append([String(v.get_path_to(gi)), gi.visible, gi.material_override.get_instance_id() if gi.material_override != null else 0])
	var env := v.environment()
	for p in CityView3D.ID_ENV_PROPS:
		parts.append([String(p), str(env.get(p))])
	parts.append(v.camera.global_transform)
	return hash(parts)


func test_the_class_table_is_the_adopted_one() -> void:
	assert_eq(IdCaptureClasses.CLASSES, [0, 1, 2, 3, 4, 5, 6, 7] as Array[int])
	assert_true(IdCaptureClasses.is_written(IdCaptureClasses.OUTER), "class 7 (the land past the city) is written")
	assert_true(IdCaptureClasses.is_written(IdCaptureClasses.GROUND), "class 4 (the ground) is written")
	assert_eq(IdCaptureClasses.room_bytes(3, 2), Vector3i(5, 3, 2), "class 5: G the place in the run graph, B the layer")
	assert_eq(IdCaptureClasses.bytes(2, IdCaptureClasses.STUB_G, 0), Vector3i(2, 255, 0), "a stub is class 2, G 255, B 0")
	assert_eq(IdCaptureClasses.bytes(9, 999, -4), Vector3i(9, 255, 0), "bytes clamp")


func test_class_counts_and_the_written_set() -> void:
	var img := Image.create(4, 2, false, Image.FORMAT_RGB8)
	img.fill(Color8(2, 0, 0))
	img.set_pixel(0, 0, Color8(0, 0, 0))
	img.set_pixel(1, 0, Color8(5, 3, 2))
	img.set_pixel(2, 0, Color8(6, 0, 0))
	assert_eq(IdCaptureClasses.count_classes(img), {2: 5, 0: 1, 5: 1, 6: 1})
	assert_true(IdCaptureClasses.only_written_classes(img))
	img.set_pixel(3, 1, Color8(4, 0, 0))
	assert_true(IdCaptureClasses.only_written_classes(img), "a class 4 pixel is allowed")
	img.set_pixel(3, 1, Color8(7, 0, 0))
	assert_true(IdCaptureClasses.only_written_classes(img), "a class 7 pixel (the land past the city) is allowed")
	img.set_pixel(3, 1, Color8(8, 0, 0))
	assert_false(IdCaptureClasses.only_written_classes(img), "a class 8 pixel is not")


func test_capture_json_is_canonical() -> void:
	var cap := {"version": 1, "run": "r", "layout_seed": "18446744073709551615", "anim_t": 1.234567, "look_blend": 0.5,
		"camera": {"position": Vector3(1.00004, 2.0, 3.99996), "size": 107.73744}, "resolution": [1920, 1080]}
	var a := IdCaptureClasses.capture_json(cap)
	var b := IdCaptureClasses.capture_json(cap.duplicate(true))
	assert_eq(a, b, "same input, same bytes")
	var parsed: Dictionary = JSON.parse_string(a)
	assert_eq(parsed["layout_seed"], "18446744073709551615", "the seed stays a decimal string")
	assert_eq(parsed["anim_t"], 1.2346, "floats round to 1e-4")
	assert_eq(parsed["camera"]["position"], [1.0, 2.0, 4.0])
	assert_true(a.contains("
 \"anim_t\""), "one-space indent")
	assert_false(a.contains("	") or a.contains(""), "no tabs, LF only")
	var keys := a.find("\"anim_t\"") < a.find("\"camera\"") and a.find("\"camera\"") < a.find("\"layout_seed\"") and a.find("\"layout_seed\"") < a.find("\"version\"")
	assert_true(keys, "keys are sorted")


func test_capture_dict_carries_the_optional_scope_keys_only_when_given() -> void:
	var v := _view()
	var bare := IdCapture.capture_dict(v, 640, 360, {"run": "x"}, 0.0)
	for k: String in ["kind", "view", "look", "look_blend", "corp", "exempt"]:
		assert_false(bare.has(k), k)
	assert_eq(bare["layout_seed"], str(CityView3D.CONFIG.city_seed))
	var full := IdCapture.capture_dict(v, 640, 360, {"kind": "hq", "view": "overview", "look": "mainline", "corp": "solace", "exempt": {"flash": false}}, 2.0)
	assert_eq(full["kind"], "hq")
	assert_eq(full["anim_t"], 2.0)
	assert_true(full["camera"].has("position"))
	assert_eq(bare["time"], "night" if v.night_share >= 0.5 else "day", "time follows the view's night share")
	assert_eq(IdCapture.capture_dict(v, 640, 360, {"time": "day"}, 0.0)["time"], "day", "meta time wins")


func test_landmarks_movers_and_links_get_their_classes_and_everything_is_restored() -> void:
	var v := _view()
	var lm := Node3D.new()
	v.layer(&"landmarks").add_child(lm)
	var tower := _mesh(lm)
	var crane := _mesh(lm)
	crane.add_to_group(IdCaptureClasses.GROUP_MOVER)
	var link := _mesh(v.layer(&"props"))
	link.add_to_group(IdCaptureClasses.GROUP_LINK)
	var prop := _mesh(v.layer(&"props"))
	var floor_part := _mesh(lm)
	floor_part.add_to_group(IdCaptureClasses.GROUP_GROUND)
	var gnode := Node3D.new()
	gnode.name = IdCaptureClasses.GROUND_NODE_NAME
	lm.add_child(gnode)
	var node_part := _mesh(gnode)
	var before := _state(v)
	var cap := IdCapture.new(get_tree(), v)
	cap.begin_id()
	var cls := cap.classify()
	assert_eq(cls[tower], IdCaptureClasses.LANDMARK)
	assert_eq(cls[crane], IdCaptureClasses.MOVER, "a mover under a landmark stays 6")
	assert_eq(cls[link], IdCaptureClasses.LINK)
	assert_eq(cls[prop], IdCaptureClasses.CITY, "a loose mesh is city")
	assert_eq(cls[floor_part], IdCaptureClasses.GROUND, "an id_ground part of a compound is class 4, not 1")
	var ground_meshes := 0
	for gm in cls:
		if cls[gm] == IdCaptureClasses.GROUND:
			ground_meshes += 1
	assert_gt(ground_meshes, 1, "the ground itself is drawn as class 4")
	var outer := v.layer(&"ground").get_node_or_null(^"OuterGround") as GeometryInstance3D
	assert_not_null(outer, "the view has its outer plane")
	assert_eq(cls[outer], IdCaptureClasses.OUTER, "the outer plane past the city is class 7, not floor")
	assert_eq(cls[node_part], IdCaptureClasses.GROUND, "a mesh under a node named id_ground (the glb's ground node) is class 4")
	assert_eq(cls[tower], IdCaptureClasses.LANDMARK, "a vertical body beside it stays class 1")
	var mat := tower.material_override as ShaderMaterial
	assert_not_null(mat, "the override is in place during the pass")
	assert_eq((mat.get_shader_parameter(&"id_rgb") as Vector3).x, 1.0)
	assert_eq(((crane.material_override as ShaderMaterial).get_shader_parameter(&"id_rgb") as Vector3).x, 6.0)
	cap.end_id()
	assert_null(tower.material_override)
	assert_eq(_state(v), before, "begin / end leave the view as it was")


func test_a_hidden_mesh_stays_hidden_and_a_beam_never_carries_a_class() -> void:
	var v := _view()
	var lm := Node3D.new()
	v.layer(&"landmarks").add_child(lm)
	var hidden := _mesh(lm)
	hidden.visible = false
	var beam := _mesh(lm)
	var bm := StandardMaterial3D.new()
	bm.resource_name = LandmarkMaterials.BEAM
	beam.material_override = bm
	var cap := IdCapture.new(get_tree(), v)
	cap.begin_id()
	assert_false(beam.visible, "a light cone is hidden in the id frame")
	cap.end_id()
	assert_true(beam.visible)
	assert_false(hidden.visible)
	assert_eq(beam.material_override, bm, "the original override comes back")
