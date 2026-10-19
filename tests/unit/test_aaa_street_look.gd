extends GutTest
## A-022 street look parity (P1 + P5): the MATERIAL_SPEC "Realistic night" numbers are in the config and reach the materials, the
## emissive hierarchy is on the dressing, the facet grit is deterministic geometry, the street's real lights obey their budget and
## their fog energy, the moon and the flat world are applied, and look_blend 0 (the mainline city) is untouched.

const CFG := preload("res://content/config/city_config.tres")
var _cache: Dictionary = {}


func after_all() -> void:
	for k: String in _cache:
		((_cache[k] as Dictionary)["dressing"] as StreetDressing).root.free()
	_cache.clear()


func _street(seed_name: String) -> Dictionary:
	if not _cache.has(seed_name):
		var w: Dictionary = NaFixture.load_inputs(seed_name)
		var d: Dictionary = NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"], w["partial_street"])
		_cache[seed_name] = {"derive": d, "city": w["city"], "dressing": StreetDressing.build(d, w["city"])}
	return _cache[seed_name]


func _aaa() -> Dictionary:
	return CityShaderConfigData.shipped().aaa


# --- The numbers of the spec ----------------------------------------------------------------------

func test_the_config_holds_the_material_spec_numbers() -> void:
	assert_eq(CityShaderConfigData.shipped().validate().size(), 0, str(CityShaderConfigData.shipped().validate()))
	var a := _aaa()
	var e: Dictionary = a["emit"]
	for k: String in ["hero", "secondary", "shop", "backdrop", "mega", "window", "trim", "panel", "lamp_head"]:
		assert_true(e.has(k), "emit.%s" % k)
	assert_eq([e["hero"], e["secondary"], e["shop"], e["backdrop"], e["mega"], e["window"], e["trim"], e["panel"], e["lamp_head"]],
		[4.0, 2.6, 1.5, 2.4, 3.0, 0.9, 1.0, 4.0, 8.0], "the emissive hierarchy (MATERIAL_SPEC 8, 4)")
	var p: Dictionary = a["pbr"]
	assert_eq([p["concrete"]["rough"], p["concrete"]["spec"], p["concrete"]["albedo"]], [0.55, 0.5, 0.85], "concrete")
	assert_eq([p["glass"]["rough"], p["glass"]["metal"], p["glass"]["spec"]], [0.12, 0.2, 1.0], "glass")
	assert_eq([p["panel"]["rough"], p["panel"]["metal"]], [0.45, 0.3], "panel")
	assert_eq(a["world"]["color"], [0.006, 0.006, 0.014], "the flat world colour")
	assert_eq(a["world"]["moon"]["energy"], 0.05, "the moon")
	var po: Dictionary = a["post"]
	assert_eq(po["bloom_sigma_px"], [4.5, 18.0, 101.25], "bloom radii")
	assert_eq(po["bloom_w"], [0.12, 0.1, 0.08])
	assert_eq([po["vignette"], po["contrast"], po["ca_px"], po["grain"]], [0.38, 1.12, 2.4, 0.03])
	assert_eq([a["grit"]["cell"], a["grit"]["jitter"], a["grit"]["normal"]], [1.7, 0.28, 0.12], "fgrid")
	assert_eq(a["exposure_solve"]["median"], 0.14, "the exposure solve target")
	var f: Dictionary = CityShaderConfigData.shipped().fog
	assert_almost_eq(float(f["peak"]), 0.1521, 0.0001, "fog cores 0.152 per BU")
	assert_eq(f["anisotropy"], 0.45)
	assert_almost_eq(float(f["h_front"]) * 0.5, 7.7, 0.0001, "the fog falls off above 7.7 BU")
	assert_almost_eq(float(f["h_front"]) * float(f["h_sky_k"]), 28.6, 0.01, "with an e-fold of 28.6 BU")
	assert_eq([f["ground_bank"], f["gb_top"], f["mid_bank"]], [0.12, 2.2, 0.105], "the ground band and the mid banks")
	var w: Dictionary = CityShaderConfigData.shipped().wet
	assert_eq([w["rough_wet"], w["specular"]], [[0.3, 0.03], 0.7], "wet street roughness 0.03 .. 0.30, spec 0.7")


func test_the_post_chain_numbers_reach_the_post_material_at_look_blend_1_and_the_mainline_post_is_untouched_at_0() -> void:
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/city/city_post.gdshader")
	NetrunShaderKitAaa.setup_post(m, false, 0.6)
	assert_false(bool(m.get_shader_parameter(&"aaa_on")), "look_blend 0: the mainline post")
	assert_eq(m.get_shader_parameter(&"aaa_bloom_sigma"), null, "no chain uniform written while off")
	NetrunShaderKitAaa.setup_post(m, true, 0.7)
	assert_true(bool(m.get_shader_parameter(&"aaa_on")))
	assert_eq(m.get_shader_parameter(&"aaa_bloom_sigma"), Vector3(4.5, 18.0, 101.25))
	assert_eq(m.get_shader_parameter(&"aaa_bloom_w"), Vector3(0.12, 0.1, 0.08))
	assert_eq(m.get_shader_parameter(&"aaa_exposure"), 0.7)
	assert_eq(m.get_shader_parameter(&"aaa_shadow_tint"), Vector3(0.25, 0.45, 0.6))
	assert_eq(m.get_shader_parameter(&"aaa_vig"), Vector3(0.38, 0.35, 1.6))
	assert_eq(m.get_shader_parameter(&"aaa_rain2b"), Vector3(0.25, 3.0, 1.6), "the third rain layer")


# --- The moon and the flat world --------------------------------------------------------------------

func test_the_moon_shines_along_the_blender_sun_direction_and_the_world_is_flat() -> void:
	var b := NetrunShaderKitAaa.moon_basis(_aaa()["world"]["moon"]["rot"])
	var d := -b.z
	# Blender rot (40, 0, 30): travel (-0.3214, 0.5567, -0.7660) in plan axes = (x, z, -y) in the world.
	assert_almost_eq(d.x, -0.3214, 0.001)
	assert_almost_eq(d.y, -0.7660, 0.001)
	assert_almost_eq(d.z, -0.5567, 0.001)
	var env := Environment.new()
	var sun := DirectionalLight3D.new()
	sun.light_energy = 1.0
	sun.light_color = Color(1, 0.9, 0.8)
	NetrunShaderKitAaa.apply_world(env, sun, 1.0, Color(0.1, 0.0, 0.0))
	assert_eq(env.background_mode, Environment.BG_COLOR, "no sky gradient")
	assert_almost_eq(env.background_color.r, 0.006, 0.0001)
	assert_almost_eq(env.background_color.b, 0.014, 0.0001)
	assert_almost_eq(sun.light_energy, 0.05, 0.0001, "the moon 0.05")
	assert_almost_eq(sun.light_color.b, 1.0, 0.0001)
	assert_false(sun.shadow_enabled)
	NetrunShaderKitAaa.apply_world(env, sun, 0.0, Color(0.1, 0.0, 0.0))
	assert_eq(sun.light_energy, 1.0, "look_blend 0 gives the mainline key light back")
	assert_eq(sun.light_color, Color(1, 0.9, 0.8))
	assert_eq(env.background_color, Color(0.1, 0.0, 0.0))
	assert_false(env.ssr_enabled)
	sun.free()


# --- The emissive hierarchy on the dressing -----------------------------------------------------------

func test_the_emissive_hierarchy_is_on_the_dressing_materials() -> void:
	var sd: StreetDressing = _street("101")["dressing"]
	var emit: Dictionary = _aaa()["emit"]
	var hero_full: ShaderMaterial = (sd.nodes["hero_full"][0] as MultiMeshInstance3D).material_override as ShaderMaterial
	assert_eq(float(hero_full.get_shader_parameter(&"tier_emit")), float(emit["hero"]), "hero signs 4.0")
	for g: String in ["sign_full", "sign_neon"]:
		if sd.nodes.has(g) and not (sd.nodes[g] as Array).is_empty():
			var m: ShaderMaterial = ((sd.nodes[g] as Array)[0] as MultiMeshInstance3D).material_override as ShaderMaterial
			assert_eq(float(m.get_shader_parameter(&"tier_emit")), float(emit["secondary"]), "%s: secondary signs 2.6" % g)
	var expect := {"shop_strip": "shop", "billboard_panel": "backdrop", "lamp_dot": "lamp_head"}
	for g: String in expect:
		if not sd.nodes.has(g) or (sd.nodes[g] as Array).is_empty():
			continue
		var m: ShaderMaterial = ((sd.nodes[g] as Array)[0] as MultiMeshInstance3D).material_override as ShaderMaterial
		assert_eq(float(m.get_shader_parameter(&"emit")), float(emit[expect[g]]), "%s: %s" % [g, expect[g]])
		assert_eq(m.shader, DressKit.SOLID, "%s is opaque so the post chain blooms it" % g)


# --- Facet grit as geometry ------------------------------------------------------------------------------

func _poly(w: float, d: float) -> PackedVector2Array:
	return PackedVector2Array([Vector2(0, 0), Vector2(w, 0), Vector2(w, d), Vector2(0, d)])


func test_fgrid_cells_follow_the_wall_size_and_the_triangle_count_is_the_formula() -> void:
	var g: Dictionary = _aaa()["grit"]
	var poly := _poly(17.0, 8.5)
	var h := 30.0
	var mesh := NetrunFgrid.mesh_of(poly, 0.0, h, 1234)
	var verts: PackedVector3Array = mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	assert_eq(verts.size() / 3, NetrunFgrid.triangle_count(poly, 0.0, h), "mesh == formula")
	# Walls 17 and 8.5 BU: nu = round(17 / 1.7) = 10 and round(8.5 / 1.7) = 5; nv = round(30 / 1.7) = 18; 4 roof triangles.
	var want := 2 * (10 * 18) * 2 + 2 * (5 * 18) * 2 + 4
	assert_eq(NetrunFgrid.triangle_count(poly, 0.0, h), want, "nu, nv from the cell %.1f" % float(g["cell"]))
	assert_eq(NetrunFgrid.triangle_count(_poly(40.0, 40.0), 0.0, 90.0), 4 * (12 * 30 * 2) + 4, "nu <= 12, nv <= 30")
	assert_eq(NetrunFgrid.triangle_count(_poly(1.5, 1.5), 0.0, 20.0), 4 * 2 + 4, "a short wall is two triangles")
	assert_eq(NetrunFgrid.triangle_count(_poly(10.0, 10.0), 0.0, 2.5), 4 * 2 + 4, "a low wall is two triangles")


func test_fgrid_is_a_pure_function_of_the_building_seed_and_stays_inside_its_jitter() -> void:
	var g: Dictionary = _aaa()["grit"]
	var poly := _poly(17.0, 8.5)
	var a := NetrunFgrid.mesh_of(poly, 0.0, 30.0, 77)
	var b := NetrunFgrid.mesh_of(poly, 0.0, 30.0, 77)
	var c := NetrunFgrid.mesh_of(poly, 0.0, 30.0, 78)
	var va: PackedVector3Array = a.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	assert_eq(va, b.surface_get_arrays(0)[Mesh.ARRAY_VERTEX], "the same seed, the same mesh")
	assert_ne(va, c.surface_get_arrays(0)[Mesh.ARRAY_VERTEX], "another seed, another grit")
	# Wall 0 is the first 2 * 10 * 18 triangles: the 17 BU side at unit z = -0.5. Its interior vertices move along the wall by at most
	# 0.28 of a cell and off its plane by at most 0.12 BU (unit space: / the 8.5 BU depth), the border stays on the wall.
	var tol_n: float = float(g["normal"]) / 8.5 + 0.0001
	var cell_u: float = float(g["cell"]) / 17.0
	var step_u := 1.0 / 10.0
	var off_plane := 0
	for t in 2 * 10 * 18 * 3:
		var v: Vector3 = va[t]
		assert_lte(absf(v.z + 0.5), tol_n, "normal jitter within 0.12 BU")
		if absf(v.z + 0.5) > 0.0001:
			off_plane += 1
		var k: float = (v.x + 0.5) / step_u
		assert_lte(absf(k - roundf(k)) * step_u, float(g["jitter"]) / 10.0 * 1.01 + 0.0001, "along-wall jitter within 0.28 of a cell")
	assert_gt(off_plane, 0, "interior vertices are lifted off the plane")
	assert_gt(cell_u, 0.0)


# --- The street's real lights ----------------------------------------------------------------------------------

func test_the_light_rig_obeys_its_caps_its_fog_only_mask_and_the_watt_to_energy_factors() -> void:
	var st := _street("101")
	var sd: StreetDressing = st["dressing"]
	var lc: Dictionary = _aaa()["lights"]
	var src := sd.light_sources(st["derive"])
	var again := sd.light_sources(st["derive"])
	assert_eq(src["lamps"].size(), again["lamps"].size())
	assert_eq(src["lamps"][0]["pos"], again["lamps"][0]["pos"], "placement is deterministic")
	var rig := StreetLightRig.build(src)
	var total := 0
	for k: String in rig.counts:
		total += int(rig.counts[k])
	assert_lte(int(rig.counts.get("lamp", 0)), int(lc["lamp"]["cap"]), "lamps within their cap")
	assert_lte(int(rig.counts.get("glow", 0)), int(lc["glow"]["cap"]))
	assert_lte(int(rig.counts.get("facade", 0)), int(lc["wash"]["cap"]))
	assert_eq(int(rig.counts.get("fog", 0)), int(lc["city_glow"]["count"]), "18 city-glow lights")
	assert_lte(int(rig.counts.get("beam", 0)), int(lc["beam"]["cap"]))
	assert_lte(total, 160, "the whole rig is within the light budget: %d" % total)
	var lamps := 0
	for n: Node in rig.root.get_children():
		var l := n as Light3D
		if n.name.begins_with("fog_") or n.name.begins_with("beam_"):
			assert_eq(l.light_volumetric_fog_energy, StreetLightRig.FOG_ENERGY_CAP, "%s: fog energy at the cap" % n.name)
			var want: float = float(lc["city_glow" if n.name.begins_with("fog_") else "beam"]["energy"])
			assert_almost_eq(l.light_energy * l.light_volumetric_fog_energy, want, 0.0001, "%s: the fog gets the configured energy, surfaces 1/16 of it" % n.name)
			assert_false(l.shadow_enabled)
		else:
			assert_ne(l.light_cull_mask & 1, 0, "%s lights the surfaces" % n.name)
		if n.name.begins_with("lamp_"):
			lamps += 1
			assert_almost_eq(l.light_energy, float(lc["lamp"]["watts"]) * float(lc["omni_k"]), 0.0001, "60 W -> energy")
			assert_eq(l.omni_attenuation, 2.0, "inverse square")
	assert_eq(lamps, int(rig.counts.get("lamp", 0)))
	rig.root.free()


# --- The page is untouched at look_blend 0 -------------------------------------------------------------------------

func test_look_blend_0_leaves_the_mainline_key_light_environment_and_post_as_they_were() -> void:
	var model := CityModel.build(CFG, 7, Rect2i(20, -4, 6, 6))
	var view := CityView3D.new()
	view.size = Vector2i(160, 90)
	view.use_model(model)
	add_child_autofree(view)
	var env := view.environment()
	var e0 := env.tonemap_exposure
	var bg0 := env.background_color
	var sun_e0 := view._sun.light_energy
	view.set_look_blend(1.0)
	assert_almost_eq(view._sun.light_energy, 0.05, 0.0001, "the moon at 1")
	assert_true(bool(view._post.get_shader_parameter(&"aaa_on")))
	view.set_look_blend(0.0)
	assert_eq(env.tonemap_exposure, e0)
	assert_eq(env.background_color, bg0)
	assert_eq(view._sun.light_energy, sun_e0, "the mainline key light is back")
	assert_false(bool(view._post.get_shader_parameter(&"aaa_on")))
	assert_eq(view._building_mat.get_shader_parameter(&"look_blend"), 0.0)
