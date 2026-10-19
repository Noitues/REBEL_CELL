extends GutTest
## NA-22 (fast tier): the netrun city shaders' contracts that need no GPU. The INSTANCE_CUSTOM packing (pack / unpack
## round trip, 0 = nothing happens, float-exact), the Bayer coverage of the ghost, the streak speed quantization, the
## config (shipped values validate), the uniform contract (every parameter the kit sets exists on its shader; the new
## uniforms of `city_building` default to the old page), reduce effects (no shader reads TIME; the clock is `nr_clock`),
## and `CityView3D.set_look_blend` (0 is the old ground shader itself). The pixel checks (parity at look_blend 0, four
## instances, Bayer 50 %, streak loop, emission linearity) are in `test_city_shaders_render.gd` (windowed).

const BUILDING := "res://shaders/city/city_building.gdshader"
const NEW_SHADERS: Array[String] = ["res://shaders/city/city_fog.gdshader", "res://shaders/city/beam_shaft.gdshader",
	"res://shaders/city/wet_street.gdshader", "res://shaders/city/streak_lane.gdshader"]
const CFG := preload("res://content/config/city_config.tres")


func _uniforms(path: String) -> Dictionary:
	var out: Dictionary = {}
	for u: Dictionary in (load(path) as Shader).get_shader_uniform_list():
		out[StringName(u["name"])] = u
	return out


func _material_params_exist(m: ShaderMaterial, label: String) -> void:
	var names: Dictionary = {}
	for u: Dictionary in m.shader.get_shader_uniform_list():
		names[StringName(u["name"])] = true
	for p: Dictionary in m.get_property_list():
		var pn: String = p["name"]
		if pn.begins_with("shader_parameter/"):
			assert_true(names.has(StringName(pn.trim_prefix("shader_parameter/"))), "%s: the shader has %s" % [label, pn])


# --- Config -----------------------------------------------------------------------------------

func test_the_shipped_config_validates() -> void:
	assert_not_null(CityShaderConfigData.shipped())
	assert_eq(CityShaderConfigData.shipped().validate(), PackedStringArray(), "no missing key or bad range")


func test_an_empty_config_reports_its_gaps_and_bad_ranges_are_named() -> void:
	assert_gt(CityShaderConfigData.new().validate().size(), 20, "every key is required")
	var c: CityShaderConfigData = CityShaderConfigData.shipped().duplicate(true)
	c.streak["loop_s"] = 0.0
	c.look["ink_fade"] = 1.5
	var msg: String = ",".join(c.validate())
	assert_true(msg.contains("streak.loop_s") and msg.contains("look.ink_fade"), msg)


func test_the_beam_and_streak_loops_are_the_netrun_loop() -> void:
	var c: CityShaderConfigData = CityShaderConfigData.shipped()
	assert_eq(float(c.streak["loop_s"]), 4.0, "streak lanes loop on T = 4 s (3.6 rule 4)")
	assert_eq(float(c.beam["period_s"]), 4.0, "the beam sweep period is the same loop")
	assert_eq(float(NetrunArtConfigData.shipped().occlusion["ease_s"]), 0.35, "the ghost / cut ease is 0.35 s")


# --- INSTANCE_CUSTOM packing ----------------------------------------------------------------------

func test_an_untouched_building_packs_to_the_old_w() -> void:
	assert_eq(NetrunInstancePack.pack(20.0, 1000.0, 1.0, 0.0, 0.0), 0.0, "no cut, opaque, no dissolve = 0")
	assert_eq(NetrunInstancePack.pack(20.0, 1000.0, 1.0, 0.0, 0.0, true), 1.0, "only the crest flag = 1, as before")
	assert_false(NetrunInstancePack.is_occluded(0.0))
	assert_false(NetrunInstancePack.is_occluded(1.0))


func test_pack_round_trips_every_field_within_its_quantum() -> void:
	for crest in [false, true]:
		for opacity in [1.0, 0.5, 0.18, 0.0625, 0.0]:
			for dissolve in [0.0, 0.25, 1.0]:
				var top := 57.0
				var cut := 3.8
				var w: float = NetrunInstancePack.pack(top, cut, opacity, 0.6, dissolve, crest)
				var u: Dictionary = NetrunInstancePack.unpack(w)
				assert_eq(u["crest"], crest)
				assert_almost_eq(top * (1.0 - float(u["cut_frac"])), cut, top / float(NetrunInstancePack.CUT_MAX), "cut height")
				assert_almost_eq(float(u["opacity"]), opacity, 0.5 / float(NetrunInstancePack.GHOST_LEVELS) + 0.0001, "opacity")
				assert_almost_eq(float(u["edge"]), 0.6, 0.5 / float(NetrunInstancePack.EDGE_MAX) + 0.0001, "edge")
				assert_almost_eq(float(u["dissolve"]), dissolve, 0.5 / float(NetrunInstancePack.DISSOLVE_LEVELS) + 0.0001, "dissolve")


func test_the_packed_value_is_exact_in_float32_and_every_state_marks_occluded() -> void:
	var w: float = NetrunInstancePack.pack(100.0, 0.0, 0.0, 1.0, 1.0, true)
	assert_lt(w, 16777216.0, "below 2^24: an integer, exact as float32")
	assert_eq(float(roundi(w)), w)
	assert_true(NetrunInstancePack.is_occluded(NetrunInstancePack.pack(10.0, 3.8, 1.0, 0.0, 0.0)), "a cut")
	assert_true(NetrunInstancePack.is_occluded(NetrunInstancePack.pack(10.0, 99.0, 0.18, 0.0, 0.0)), "a ghost")
	assert_true(NetrunInstancePack.is_occluded(NetrunInstancePack.pack(10.0, 99.0, 1.0, 0.0, 0.5)), "a dissolve")
	assert_false(NetrunInstancePack.is_occluded(NetrunInstancePack.pack(10.0, 99.0, 1.0, 1.0, 0.0)), "edge lines alone do not occlude")


func test_a_stub_is_never_below_zero_and_the_cut_is_the_height_share() -> void:
	var w: float = NetrunInstancePack.pack(40.0, 4.0, 1.0, 0.0, 0.0)
	assert_almost_eq(float(NetrunInstancePack.unpack(w)["cut_frac"]), 0.9, 0.003)
	var all_gone: float = NetrunInstancePack.pack(40.0, -5.0, 1.0, 0.0, 0.0)
	assert_eq(float(NetrunInstancePack.unpack(all_gone)["cut_frac"]), 1.0, "a negative cut clamps (the caller keeps the stub)")


# --- Bayer ghost -------------------------------------------------------------------------------------

func test_the_bayer_ghost_covers_its_opacity_of_pixels_in_every_4x4_block() -> void:
	for level in range(0, NetrunInstancePack.GHOST_LEVELS + 1):
		var opacity: float = float(level) / float(NetrunInstancePack.GHOST_LEVELS)
		var drawn := 0
		for y in 4:
			for x in 4:
				if NetrunInstancePack.bayer4(x, y) < opacity:
					drawn += 1
		assert_eq(drawn, level, "opacity %f draws %d of 16 pixels" % [opacity, level])
	assert_eq(NetrunInstancePack.coverage(0.5), 0.5)
	assert_almost_eq(NetrunInstancePack.coverage(0.18), 3.0 / 16.0, 0.0001, "the default ghost 0.18 quantizes to 3/16")


func test_the_bayer_matrix_is_the_same_on_every_call() -> void:
	var a: Array[float] = []
	var b: Array[float] = []
	for i in 64:
		a.append(NetrunInstancePack.bayer4(i, i * 3))
	for i in 64:
		b.append(NetrunInstancePack.bayer4(i, i * 3))
	assert_eq(a, b, "no randomness: pixel position only")


# --- Streak lanes ------------------------------------------------------------------------------------

func test_the_streak_speed_is_quantized_to_a_whole_number_of_loops() -> void:
	for length in [80.0, 143.0, 31.4]:
		for speed in [20.0, 17.3, 55.0, 3.0]:
			var q: Dictionary = NetrunShaderKit.quantize_speed(length, speed, 4.0)
			assert_almost_eq(float(q["k"]) * float(q["speed"]) * 4.0, length, 0.0001, "L = k speed T")
			assert_gte(int(q["k"]), 1)
	assert_almost_eq(float(NetrunShaderKit.quantize_speed(80.0, 20.0, 4.0)["speed"]), 20.0, 0.0001, "the concept's 80 BU per 4 s keeps 20 BU/s")


func test_the_streak_texture_holds_the_derive_streaks_up_to_the_cap() -> void:
	var streaks: Array = []
	for i in 40:
		streaks.append({"u0": float(i), "len": 5.0, "gap": 3.0, "bright": 0.5 + float(i) * 0.01})
	var tex: ImageTexture = NetrunShaderKit.streak_texture(streaks)
	assert_eq(tex.get_width(), int(CityShaderConfigData.shipped().streak["max_streaks"]), "capped")
	var px: Color = tex.get_image().get_pixel(3, 0)
	assert_almost_eq(px.r, 3.0, 0.0001)
	assert_almost_eq(px.g, 5.0, 0.0001)
	assert_almost_eq(px.b, 0.53, 0.0001)


# --- Uniform contract --------------------------------------------------------------------------------

func test_the_new_building_uniforms_default_to_the_old_page() -> void:
	var u: Dictionary = _uniforms(BUILDING)
	var src := FileAccess.get_file_as_string(BUILDING)
	var defaults := {"look_blend": "float look_blend = 0.0;", "emission_multiplier": "float emission_multiplier = 1.0;",
		"sec_on": "bool sec_on = false;", "z_cut": "float z_cut = 10000.0;", "id_mode": "bool id_mode = false;"}
	for k: String in defaults:
		assert_true(u.has(StringName(k)), "city_building has %s" % k)
		assert_true(src.contains("uniform " + String(defaults[k])), "%s defaults to the old page" % k)


func test_every_netrun_shader_loads_and_declares_its_documented_uniforms() -> void:
	var wanted := {
		"res://shaders/city/streak_lane.gdshader": ["streaks", "streak_count", "lane_len", "speed", "dir", "loop_s", "anim_t", "anim_t_frozen", "emission_multiplier"],
		"res://shaders/city/beam_shaft.gdshader": ["beam_col", "beam_len", "lean_deg", "sweep_deg", "phase", "anim_t", "anim_t_frozen", "core_sigma", "skirt_sigma", "efold", "hot", "emit", "emission_multiplier"],
		"res://shaders/city/wet_street.gdshader": ["look_blend", "emission_multiplier", "noise_scale", "rough_noise", "rough_wet", "wet_specular", "albedo_mul", "puddles_sharp"],
		"res://shaders/city/city_fog.gdshader": ["look_blend", "peak", "h_front", "h_sky", "octave_w", "wind", "anim_t", "anim_t_frozen", "emit_gain"],
		BUILDING: ["look_blend", "emission_multiplier", "sec_on", "sec_a", "sec_c", "sec_nrm", "sec_pad", "sec_ground", "z_cut", "plinth_on", "plinth_off", "poche", "edge_col", "id_mode", "id_class"],
	}
	for path: String in wanted:
		assert_not_null(load(path) as Shader, "%s loads" % path)
		var u: Dictionary = _uniforms(path)
		for n: String in wanted[path]:
			assert_true(u.has(StringName(n)), "%s declares %s" % [path.get_file(), n])


func test_what_the_kit_sets_exists_on_the_shaders() -> void:
	var b := CityMaterials.building(CFG, [])
	NetrunShaderKit.setup_building(b, 0.5)
	NetrunShaderKit.set_section(b, Vector2(0, 0), Vector2(0, 50), Vector2(1, 0), 0.0, 12.0)
	NetrunShaderKit.set_clock([b], 1.0)
	_material_params_exist(b, "building")
	var lane := {"a": [0.0, 0.0], "b": [80.0, 0.0], "z": 0.5, "speed": 20.0, "streaks": [{"u0": 0.0, "len": 10.0, "gap": 5.0, "bright": 1.0}]}
	var s := NetrunShaderKit.streak_material(lane, Color.WHITE)
	_material_params_exist(s, "streak")
	assert_eq(s.get_shader_parameter(&"lane_len"), 80.0)
	var beam := {"pos": [0.0, 0.0, 30.0], "lean": [5.0, 8.0], "sweep_deg": 5.0, "phase": 0.3}
	var bm := NetrunShaderKit.beam_material(beam, Color.MAGENTA, 14.0)
	_material_params_exist(bm, "beam")
	assert_almost_eq(float(bm.get_shader_parameter(&"beam_len")), 49.0, 0.001, "3.5 x H_FRONT")
	_material_params_exist(NetrunShaderKit.fog_material(), "fog")
	_material_params_exist(NetrunShaderKit.wet_street_from(CityMaterials.ground(CFG, false)), "wet")
	for m: ShaderMaterial in [b, s, bm]:
		NetrunShaderKit.set_clock([m], 2.5, 1.25)
		assert_eq(m.get_shader_parameter(&"anim_t"), 2.5)
		assert_eq(m.get_shader_parameter(&"anim_t_frozen"), 1.25, "the plate's recorded anim_t")


func test_the_fog_octave_weights_follow_the_lod_band() -> void:
	var band: Array = NetrunArtConfigData.shipped().lod["bands"]["fog_octaves"]
	assert_eq(NetrunShaderKit.octave_weights(float(band[0]) - 0.1), Vector3(1.0, 0.0, 0.0), "the higher octaves are out below the band")
	assert_eq(NetrunShaderKit.octave_weights(float(band[1]) + 0.1), Vector3.ONE, "all in above it")


# --- Reduce effects -------------------------------------------------------------------------------------

func test_the_netrun_shaders_have_no_clock_but_the_one_that_freezes() -> void:
	for path in NEW_SHADERS + [BUILDING]:
		var src := FileAccess.get_file_as_string(path)
		for line in src.split("\n"):
			var code := line.split("//")[0]
			assert_false(code.contains("TIME"), "%s reads no TIME (the clock is nr_clock: anim_t, frozen under reduce effects): %s" % [path.get_file(), line.strip_edges()])
	for path in ["res://shaders/city/streak_lane.gdshader", "res://shaders/city/beam_shaft.gdshader", "res://shaders/city/city_fog.gdshader"]:
		assert_true(FileAccess.get_file_as_string(path).contains("nr_clock(anim_t, anim_t_frozen)"), "%s uses the frozen clock" % path.get_file())
	var inc := FileAccess.get_file_as_string("res://shaders/lib/netrun_clock.gdshaderinc")
	assert_true(inc.contains("mix(live_t, frozen_t, clamp(reduce_effects, 0.0, 1.0))"), "reduce effects = the plate's anim_t")


func test_reduce_effects_ease_is_zero_so_the_end_state_is_immediate() -> void:
	assert_eq(float(CityShaderConfigData.shipped().reduce["ease_s"]), 0.0)


# --- CityView3D ------------------------------------------------------------------------------------------

func test_look_blend_zero_is_the_old_ground_shader_itself() -> void:
	var model := CityModel.build(CFG, 7, Rect2i(20, -4, 6, 6))
	var view := CityView3D.new()
	view.size = Vector2i(160, 90)
	view.use_model(model)
	add_child_autofree(view)
	var bm: ShaderMaterial = view.building_material()
	assert_not_null(bm)
	assert_eq(view.look_blend, 0.0)
	view.set_look_blend(0.0)
	assert_eq(bm.get_shader_parameter(&"look_blend"), 0.0)
	assert_eq(view._ground_mat.shader, CityMaterials.GROUND, "look_blend 0: the old ground shader")
	view.set_look_blend(0.5)
	assert_eq(bm.get_shader_parameter(&"look_blend"), 0.5)
	assert_eq(view._ground_mat.shader, CityMaterials.WET_STREET, "above 0: the wet street")
	assert_eq(view._lane_mat.shader, CityMaterials.WET_STREET)
	assert_gt(float(view._post.get_shader_parameter(&"ink_fade")), 0.0, "the ink fades")
	assert_lt(float(view._post.get_shader_parameter(&"fog_amount")), CFG.fog_amount, "the mainline fog patches fade")
	view.set_look_blend(0.0)
	assert_eq(view._ground_mat.shader, CityMaterials.GROUND, "back to the old shader")
	assert_eq(float(view._post.get_shader_parameter(&"ink_fade")), 0.0)
	assert_eq(float(view._post.get_shader_parameter(&"fog_amount")), CFG.fog_amount)
