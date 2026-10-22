extends GutTest
## LOOK-TOOLBOX module 17 (fast tier): the glTF material-slot map. It equals the runtime tables it stands for
## (LandmarkMaterials, HqCompoundMaterials, StreetR2Materials.for_slot by behaviour), every surface of every Blender export
## under assets/ is listed (no slot reaches a renderer's silent fallback), and the post-import pilots (uplink pads, roof
## props, the folders of post_import_dirs: the rc_look editor plugin) carry their stamp.

const PILOTS: Array[String] = ["res://assets/raid/uplink/uplink_pads.glb", "res://assets/city/roof_props/roof_props.glb"]


func test_the_map_is_valid_and_equals_the_landmark_tables() -> void:
	var c := RcLookSlots.config()
	assert_eq(c.validate().size(), 0, str(c.validate()))
	assert_eq(c.landmark_roles, LandmarkMaterials.ROLES, "lm_* roles = LandmarkMaterials.ROLES")
	assert_eq(c.landmark_beam, LandmarkMaterials.BEAM)
	assert_eq(c.hq_alias, HqCompoundMaterials.LANDMARK_NAME, "hq_* = HqCompoundMaterials.LANDMARK_NAME")
	for nm: String in c.landmark_roles:
		assert_eq(RcLookSlots.of(nm)["role"], LandmarkMaterials.role_of(nm), nm)
	for nm: String in c.hq_alias:
		assert_eq(RcLookSlots.of(nm)["role"], HqCompoundMaterials.role_of(nm), nm)
	assert_eq(RcLookSlots.of("hq_sx_glass")["family"], RcLookSlots.SOLACE, "the Solace slots are their own family")


## Same role -> the same StreetR2Materials material, other roles -> another one (for_slot's prefix and fallback included).
func test_the_street_slots_equal_for_slot() -> void:
	var c := RcLookSlots.config()
	var mats := StreetR2Materials.new()
	var names: Array = c.street_exact.keys()
	for p: String in c.street_prefix:
		names.append(p)
		names.append(p + "_2")
	names.append("never_exported")
	var by_role := {}
	for nm: String in names:
		var role := String(RcLookSlots.of(nm)["role"])
		var m := mats.for_slot(nm)
		if by_role.has(role):
			assert_eq(m, by_role[role], "%s: the %s material" % [nm, role])
		else:
			for other: String in by_role:
				assert_ne(m, by_role[other], "%s (%s) is not the %s material" % [nm, role, other])
			by_role[role] = m
	assert_false(RcLookSlots.of("never_exported")["listed"], "an unknown name is reported")
	assert_eq(RcLookSlots.of("never_exported")["role"], c.street_fallback, "and names the fallback it would get")


func test_every_export_lists_every_slot() -> void:
	var files: Array[String] = []
	_glbs("res://assets", files)
	assert_gt(files.size(), 40, "the exports were found")
	for f: String in files:
		var root := (load(f) as PackedScene).instantiate()
		assert_eq(RcLookSlots.unlisted(root).size(), 0, "%s: unlisted slots %s" % [f, RcLookSlots.unlisted(root)])
		root.free()


func test_the_pilots_carry_the_post_import_stamp() -> void:
	for f: String in PILOTS:
		assert_true(RcLookSlots.wants(f), "%s is under a post-import folder" % f)
	assert_false(RcLookSlots.wants("res://assets/street_kit/lamp_post.glb"), "other folders are not stamped yet")
	for f: String in PILOTS:
		var root := (load(f) as PackedScene).instantiate()
		var n := 0
		for e: Dictionary in RcLookSlots.surfaces(root):
			var mi := root.get_node(NodePath(String(e["node"]))) if String(e["node"]) != "." else root
			assert_true(mi.has_meta(RcLookSlots.META), "%s %s stamped" % [f, e["node"]])
			assert_eq(String((mi.get_meta(RcLookSlots.META) as PackedStringArray)[int(e["surface"])]), "%s:%s" % [e["family"], e["role"]])
			n += 1
		assert_gt(n, 0, f)
		root.free()


func _glbs(dir: String, out: Array[String]) -> void:
	for d: String in DirAccess.get_directories_at(dir):
		_glbs(dir.path_join(d), out)
	for f: String in DirAccess.get_files_at(dir):
		if f.ends_with(".glb"):
			out.append(dir.path_join(f))
	out.sort()
