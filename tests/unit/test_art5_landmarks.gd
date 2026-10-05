extends GutTest
## ART-5 5b: the five landmarks import and load headless (bible 4.4): every corporation's landmark folder passes
## the validator hook, every glTF scene loads and instantiates with only landmark material roles, the animated ones
## carry their loop, Orbital its two silo states, REBEL_CELL its fist and reveal meshes and its crest mask texture,
## and LandmarkMaterials puts a shader material on every surface. No view uses them yet (5a places them).

const ROOT := "res://assets/city/landmarks"
const LOOK_PATH := "res://assets/city/landmarks/landmark_look.tres"


func _corps() -> Array[StringName]:
	var out: Array[StringName] = []
	for id in ContentRegistry.all_ids():
		if ContentRegistry.get_content(id) is CorporationData:
			out.append(id)
	out.sort()
	return out


func _manifest(cid: StringName) -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string("%s/%s/manifest.json" % [ROOT, cid]))


func _meshes(n: Node) -> Array[MeshInstance3D]:
	var out: Array[MeshInstance3D] = []
	for c in n.find_children("*", "MeshInstance3D", true, false):
		out.append(c as MeshInstance3D)
	return out


func test_every_corporation_has_a_valid_landmark_folder() -> void:
	var corps := _corps()
	assert_eq(corps.size(), 5, "five corporations")
	assert_eq(LandmarkAssetChecks.errors(corps), PackedStringArray())


func test_every_landmark_scene_loads_with_landmark_roles_only() -> void:
	for cid in _corps():
		for e: Dictionary in _manifest(cid)["landmarks"]:
			if not String(e["file"]).ends_with(".glb"):
				continue
			var ps: PackedScene = load("%s/%s/%s" % [ROOT, cid, e["file"]])
			assert_not_null(ps, "%s loads" % e["file"])
			if ps == null:
				continue
			var n := ps.instantiate()
			var meshes := _meshes(n)
			assert_gt(meshes.size(), 0, "%s has meshes" % e["file"])
			for mi in meshes:
				for s in mi.mesh.get_surface_count():
					var mat := mi.mesh.surface_get_material(s)
					var nm := mat.resource_name if mat != null else ""
					assert_ne(LandmarkMaterials.role_of(nm), -2, "%s %s: role %s" % [e["file"], mi.name, nm])
			n.free()


func test_animated_landmarks_carry_their_loop() -> void:
	for cid in _corps():
		for e: Dictionary in _manifest(cid)["landmarks"]:
			if e.get("animation") == null:
				continue
			var n: Node = (load("%s/%s/%s" % [ROOT, cid, e["file"]]) as PackedScene).instantiate()
			var players := n.find_children("*", "AnimationPlayer", true, false)
			assert_eq(players.size(), 1, "%s has an AnimationPlayer" % e["file"])
			if players.size() == 1:
				var ap := players[0] as AnimationPlayer
				var an := String(e["animation"]["name"])
				assert_true(ap.has_animation(an), "%s has '%s'" % [e["file"], an])
				if ap.has_animation(an):
					assert_almost_eq(ap.get_animation(an).length, float(e["animation"]["loop_seconds"]), 0.02)
			n.free()


func test_orbital_has_both_silo_states_and_rebel_cell_its_reveal_meshes() -> void:
	var orb: Node = (load("%s/orbital/orbital_hq.glb" % ROOT) as PackedScene).instantiate()
	assert_eq(orb.find_children("*state_closed", "", true, false).size(), 1, "closed silo")
	assert_eq(orb.find_children("*state_open", "", true, false).size(), 1, "open silo")
	orb.free()
	var rc: Node = (load("%s/rebel_cell/rebel_cell_district.glb" % ROOT) as PackedScene).instantiate()
	for part in ["win_fist_home", "win_fist_dispatch", "win_ring", "win_lines", "lines"]:
		assert_eq(rc.find_children("*__" + part, "MeshInstance3D", true, false).size(), 1, part)
	rc.free()


func test_the_crest_mask_imports_with_its_manifest_size_and_draws_the_fist() -> void:
	var entry: Dictionary = {}
	for e: Dictionary in _manifest(&"rebel_cell")["landmarks"]:
		if e.get("kind", "") == "mask":
			entry = e
	assert_false(entry.is_empty(), "the crest mask is in the manifest")
	var tex: Texture2D = load("%s/rebel_cell/%s" % [ROOT, entry["file"]])
	assert_not_null(tex)
	assert_eq(tex.get_width(), int(entry["mask"]["width_px"]))
	assert_eq(tex.get_height(), int(entry["mask"]["height_px"]))
	var img := tex.get_image()
	var fist := 0
	var line := 0
	for y in range(0, img.get_height(), 2):
		for x in range(0, img.get_width(), 2):
			var r := roundi(img.get_pixel(x, y).r * 255.0)
			if r == 255:
				fist += 1
			elif r == 128:
				line += 1
	assert_gt(fist, 0, "fist texels")
	assert_gt(line, 0, "detail-line texels")


func test_landmark_materials_cover_every_surface() -> void:
	var look: LandmarkLook = load(LOOK_PATH)
	assert_not_null(look)
	var n: Node = (load("%s/halcyon/halcyon_hq.glb" % ROOT) as PackedScene).instantiate()
	var mats := LandmarkMaterials.apply(n, look, &"halcyon", false)
	assert_true(mats.has("lm_beam"), "the searchlight cone")
	for mi in _meshes(n):
		for s in mi.mesh.get_surface_count():
			assert_true(mi.get_surface_override_material(s) is ShaderMaterial, "%s surface %d" % [mi.name, s])
	n.free()
	var rc: Node = (load("%s/rebel_cell/rebel_cell_district.glb" % ROOT) as PackedScene).instantiate()
	var rm := LandmarkMaterials.apply(rc, look, &"rebel_cell", false)
	LandmarkMaterials.set_reveal(rm, 0.25)
	assert_almost_eq(float((rm["lm_win_ring"] as ShaderMaterial).get_shader_parameter("reveal_q")), 0.25, 0.0001)
	LandmarkMaterials.show_dispatch(rc, true)
	assert_false((rc.find_children("*__win_fist_home", "MeshInstance3D", true, false)[0] as Node3D).visible)
	assert_true((rc.find_children("*__win_fist_dispatch", "MeshInstance3D", true, false)[0] as Node3D).visible)
	rc.free()
