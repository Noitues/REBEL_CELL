class_name NetrunShaderKit
extends RefCounted
## NA-22: builds and drives the netrun city shaders (`city_building` section / occlusion / look blend, `city_fog`,
## `beam_shaft`, `wet_street`, `streak_lane`) from `CityShaderConfigData` and `NetrunArtConfigData`. View glue only:
## it builds materials, meshes and nodes and sets uniforms; no game state. Uniform names and sources are listed in
## `docs/handoff/plan2/drafts/NA22_SHADER_PARAMS.md`.

const FOG := preload("res://shaders/city/city_fog.gdshader")
const BEAM := preload("res://shaders/city/beam_shaft.gdshader")
const WET := preload("res://shaders/city/wet_street.gdshader")
const STREAK := preload("res://shaders/city/streak_lane.gdshader")
const SKY := preload("res://shaders/city/city_sky.gdshader")
const BEAM_SEGMENTS := 48
const BEAM_RINGS := 24


static func _cfg() -> CityShaderConfigData:
	return CityShaderConfigData.shipped()


static func _v2(a: Array) -> Vector2:
	return Vector2(float(a[0]), float(a[1]))


static func _v3(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))


## NA-25b r5: the dissolve's stagger and a glyph cell's life (city_building.gdshader: `tc = (open - h * 0.6) / 0.4`).
const BIT_STAGGER := 0.6
const BIT_LIFE := 0.4


## The share of a wall's bit cells that show a glyph at room-open share `open` (the cells' hashes spread evenly over 0..1): a cell shows
## its glyph from `h * BIT_STAGGER` for BIT_LIFE of the open share, then is cut. The glyphs keep their size, so the count is what thins out.
static func bit_glyph_share(open: float) -> float:
	if open <= 0.0 or open >= BIT_STAGGER + BIT_LIFE:
		return 0.0
	return clampf(open / BIT_STAGGER, 0.0, 1.0) - clampf((open - BIT_LIFE) / BIT_STAGGER, 0.0, 1.0)


## The clock for `mats` (materials on the netrun shaders): `anim_t` seconds (the 4.0 s loop) and, under reduce effects, the
## `frozen_t` value they stop at (the plate's recorded `anim_t`; `NAN` = the config `reduce.anim_t_default`).
static func set_clock(mats: Array, anim_t: float, frozen_t: float = NAN) -> void:
	var f: float = float(_cfg().reduce["anim_t_default"]) if is_nan(frozen_t) else frozen_t
	for m: Variant in mats:
		var sm := m as ShaderMaterial
		if sm == null:
			continue
		sm.set_shader_parameter(&"anim_t", anim_t)
		sm.set_shader_parameter(&"anim_t_frozen", f)


## Sets the netrun look on a `city_building` material: `look_blend`, the poche / edge colours (the `section` block of
## `NetrunArtConfigData`), the edge band and boost, the plinth, the corridor pad and the ghost opacity ceiling.
static func setup_building(m: ShaderMaterial, look_blend: float = 0.0) -> void:
	var b: Dictionary = _cfg().building
	var sec: Dictionary = NetrunArtConfigData.shipped().section
	m.set_shader_parameter(&"look_blend", look_blend)
	m.set_shader_parameter(&"poche", _v3(sec["poche"]))
	m.set_shader_parameter(&"edge_col", _v3(sec["edge_col"]))
	m.set_shader_parameter(&"edge_gain", float(NetrunArtConfigData.shipped().occlusion["edge"]))
	m.set_shader_parameter(&"edge_band", float(b["edge_band_bu"]))
	m.set_shader_parameter(&"edge_boost", float(b["edge_alpha_boost"]))
	m.set_shader_parameter(&"ghost_dim", float(b["window_dim"]))
	m.set_shader_parameter(&"sec_pad", float(b["corridor_pad"]))
	m.set_shader_parameter(&"sec_side", float(b["side_test"]))
	m.set_shader_parameter(&"plinth_on", _v2(b["plinth_on"]))
	m.set_shader_parameter(&"plinth_off", float(b["plinth_off_bu"]))
	m.set_shader_parameter(&"plinth_albedo", float(b["plinth_albedo"]))
	m.set_shader_parameter(&"plinth_blue", float(b["plinth_blue"]))
	for k: String in ["facade_albedo", "facade_light", "win_share", "win_floor", "win_pow", "win_emit", "trim_emit", "haze_k", "haze_h",
			"haze_hi", "wash_gain", "edge_share", "edge_emit", "edge_bu"]:
		m.set_shader_parameter(StringName(k), float(b[k]))
	m.set_shader_parameter(&"edge_blend", _v2(b["edge_blend"]))
	m.set_shader_parameter(&"wash_floors", _v2(b["wash_floors"]))
	m.set_shader_parameter(&"wash_a", _v3(b["wash_a"]))
	m.set_shader_parameter(&"wash_b", _v3(b["wash_b"]))
	m.set_shader_parameter(&"edge_a", _v3(b["edge_a"]))
	m.set_shader_parameter(&"edge_b", _v3(b["edge_b"]))
	m.set_shader_parameter(&"haze_col", _v3(b["haze_col"]))
	var wet: Dictionary = _cfg().wet
	m.set_shader_parameter(&"wet_noise_scale", float(wet["noise_scale"]))
	m.set_shader_parameter(&"wet_rough_noise", _v2(wet["rough_noise"]))
	m.set_shader_parameter(&"wet_rough", _v2(wet["rough_wet"]))
	m.set_shader_parameter(&"wet_spec", float(wet["specular"]))
	# AAA-2 PBR (MATERIAL_SPEC 4): concrete (rough, metal, spec), the glass panes, the light gains.
	var pbr: Dictionary = _cfg().aaa["pbr"]
	var cc: Dictionary = pbr["concrete"]
	var gl: Dictionary = pbr["glass"]
	m.set_shader_parameter(&"pbr_concrete", Vector3(float(cc["rough"]), float(cc["metal"]), float(cc["spec"])))
	m.set_shader_parameter(&"pbr_glass", Vector3(float(gl["rough"]), float(gl["metal"]), float(gl["spec"])))
	m.set_shader_parameter(&"glass_col", _v3(gl["col"]))
	m.set_shader_parameter(&"glass_tone", _v2(gl["tone"]))
	var fam := PackedVector3Array()
	for c: Array in cc["families"]:
		fam.append(_v3(c))
	m.set_shader_parameter(&"concrete_fam", fam)
	m.set_shader_parameter(&"pbr_diffuse_k", float(pbr["diffuse_k"]))
	m.set_shader_parameter(&"pbr_spec_k", float(pbr["spec_k"]))


## Switches the street section on: corridor beside the plan segment `a` -> `c` (plan x, y), camera-side normal `nrm`, local
## ground height `ground_z`, cut height `z_cut` above it (`NetrunSection.zcut`).
static func set_section(m: ShaderMaterial, a: Vector2, c: Vector2, nrm: Vector2, ground_z: float, z_cut: float) -> void:
	m.set_shader_parameter(&"sec_on", true)
	m.set_shader_parameter(&"sec_a", a)
	m.set_shader_parameter(&"sec_c", c)
	m.set_shader_parameter(&"sec_nrm", nrm)
	m.set_shader_parameter(&"sec_ground", ground_z)
	m.set_shader_parameter(&"z_cut", z_cut)


## Switches the street section off (the page as before).
static func clear_section(m: ShaderMaterial) -> void:
	m.set_shader_parameter(&"sec_on", false)
	m.set_shader_parameter(&"z_cut", float(NetrunArtConfigData.shipped().section["no_cut"]))


## A `wet_street` material carrying the uniforms of the ground material `ground` (the toon ramp, the lane flag) and the wet
## numbers of the config. Same parameters, so it can stand in for the ground shader at any `look_blend`.
static func wet_street_from(ground: ShaderMaterial) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = WET
	for u: Dictionary in ground.shader.get_shader_uniform_list():
		var n: StringName = u["name"]
		var v: Variant = ground.get_shader_parameter(n)
		if v != null:
			m.set_shader_parameter(n, v)
	setup_wet(m)
	return m


## The wet numbers of the config on a `wet_street` material.
static func setup_wet(m: ShaderMaterial) -> void:
	var w: Dictionary = _cfg().wet
	m.set_shader_parameter(&"noise_scale", float(w["noise_scale"]))
	m.set_shader_parameter(&"noise_octaves", int(w["noise_octaves"]))
	m.set_shader_parameter(&"rough_noise", _v2(w["rough_noise"]))
	m.set_shader_parameter(&"rough_wet", _v2(w["rough_wet"]))
	m.set_shader_parameter(&"wet_specular", float(w["specular"]))
	m.set_shader_parameter(&"albedo_mul", float(w["albedo_mul"]))


## The speed quantized so the lane length is a whole number of loops: `L = k * speed * T`, `k = max(1, round(L / (speed T)))`
## (DERIVE_V2_REVIEW AD item 14). Returns `{speed, k}`.
static func quantize_speed(lane_len: float, speed: float, loop_s: float) -> Dictionary:
	var k: int = maxi(1, roundi(lane_len / maxf(speed * loop_s, 0.0001)))
	return {"speed": lane_len / (float(k) * loop_s), "k": k}


## The N x 1 float texture of a lane's streaks (`[{u0, len, gap, bright}]` as in dress `streak_lanes[].streaks`), at most
## `streak.max_streaks` of them: texel (u0, len, bright, 0).
static func streak_texture(streaks: Array) -> ImageTexture:
	var n: int = clampi(streaks.size(), 1, int(_cfg().streak["max_streaks"]))
	var img := Image.create(n, 1, false, Image.FORMAT_RGBAF)
	for i in mini(streaks.size(), n):
		var s: Dictionary = streaks[i]
		img.set_pixel(i, 0, Color(float(s["u0"]), float(s["len"]), float(s["bright"]), 0.0))
	return ImageTexture.create_from_image(img)


## A `streak_lane` material for the dress lane `lane` (`a`, `b` plan xy, `speed`, `streaks[]`), colour `col`. The lane
## length is |b - a|; the speed is quantized to the loop (`quantize_speed`); direction +1 runs a -> b, -1 runs b -> a.
static func streak_material(lane: Dictionary, col: Color, dir: float = 1.0) -> ShaderMaterial:
	var s: Dictionary = _cfg().streak
	var a: Vector2 = Vector2(float(lane["a"][0]), float(lane["a"][1]))
	var c: Vector2 = Vector2(float(lane["b"][0]), float(lane["b"][1]))
	var length: float = a.distance_to(c)
	var q: Dictionary = quantize_speed(length, float(lane["speed"]), float(s["loop_s"]))
	var m := ShaderMaterial.new()
	m.shader = STREAK
	m.set_shader_parameter(&"streaks", streak_texture(lane["streaks"]))
	m.set_shader_parameter(&"streak_count", mini((lane["streaks"] as Array).size(), int(s["max_streaks"])))
	m.set_shader_parameter(&"lane_len", length)
	m.set_shader_parameter(&"speed", float(q["speed"]))
	m.set_shader_parameter(&"dir", dir)
	m.set_shader_parameter(&"loop_s", float(s["loop_s"]))
	m.set_shader_parameter(&"lane_col", Vector3(col.r, col.g, col.b))
	m.set_shader_parameter(&"emit", float(s["emit"]))
	m.set_shader_parameter(&"bright_floor", float(s["floor"]))
	m.set_shader_parameter(&"bright_pow", float(s["power"]))
	return m


## The strip mesh of a lane of length `length` BU and half width `half_w`: UV.x = BU along, UV.y = -1 .. 1 across.
static func streak_mesh(length: float, half_w: float) -> ArrayMesh:
	var arr: Array = []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = PackedVector3Array([Vector3(0, 0, -half_w), Vector3(length, 0, -half_w), Vector3(length, 0, half_w), Vector3(0, 0, half_w)])
	arr[Mesh.ARRAY_TEX_UV] = PackedVector2Array([Vector2(0, -1), Vector2(length, -1), Vector2(length, 1), Vector2(0, 1)])
	arr[Mesh.ARRAY_NORMAL] = PackedVector3Array([Vector3.UP, Vector3.UP, Vector3.UP, Vector3.UP])
	arr[Mesh.ARRAY_INDEX] = PackedInt32Array([0, 1, 2, 0, 2, 3])
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	return mesh


## A `MeshInstance3D` for the dress lane `lane` (plan `a`, `b`, `z` height): the strip placed along the lane. Direction
## +1 runs a -> b.
static func streak_node(lane: Dictionary, col: Color, dir: float = 1.0) -> MeshInstance3D:
	var s: Dictionary = _cfg().streak
	var a: Vector2 = Vector2(float(lane["a"][0]), float(lane["a"][1]))
	var c: Vector2 = Vector2(float(lane["b"][0]), float(lane["b"][1]))
	var length: float = a.distance_to(c)
	var mi := MeshInstance3D.new()
	mi.mesh = streak_mesh(length, float(s["width"]))
	mi.material_override = streak_material(lane, col, dir)
	var d: Vector2 = (c - a).normalized()
	var x_axis := Vector3(d.x, 0.0, -d.y)
	var basis := Basis(x_axis, Vector3.UP, x_axis.cross(Vector3.UP)).orthonormalized()
	mi.transform = Transform3D(basis, Vector3(a.x, float(lane["z"]), -a.y))
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mi


## The open unit tube the `beam_shaft` shader sizes (vertex x, z on the unit circle, UV.y = 0 .. 1 along), `extent` BU for
## the culling box.
static func beam_mesh(extent: float) -> ArrayMesh:
	var verts := PackedVector3Array()
	var uvs := PackedVector2Array()
	var norms := PackedVector3Array()
	var idx := PackedInt32Array()
	for r in BEAM_RINGS + 1:
		var t: float = float(r) / float(BEAM_RINGS)
		for s in BEAM_SEGMENTS + 1:
			var ang: float = TAU * float(s) / float(BEAM_SEGMENTS)
			verts.append(Vector3(cos(ang), t, sin(ang)))
			uvs.append(Vector2(float(s) / float(BEAM_SEGMENTS), t))
			norms.append(Vector3(cos(ang), 0.0, sin(ang)))
	var row: int = BEAM_SEGMENTS + 1
	for r in BEAM_RINGS:
		for s in BEAM_SEGMENTS:
			var i0: int = r * row + s
			idx.append_array(PackedInt32Array([i0, i0 + 1, i0 + row, i0 + 1, i0 + row + 1, i0 + row]))
	var arr: Array = []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = verts
	arr[Mesh.ARRAY_TEX_UV] = uvs
	arr[Mesh.ARRAY_NORMAL] = norms
	arr[Mesh.ARRAY_INDEX] = idx
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	mesh.custom_aabb = AABB(Vector3(-extent, -extent, -extent), Vector3(extent, extent, extent) * 2.0)
	return mesh


## A `beam_shaft` material for a dress beam (`lean` [x, y] degrees, `sweep_deg`, `phase`) of colour `col`, `front_h` the
## frontage roof height (BU) the shaft length scales with (`beam.length_front` x it).
static func beam_material(beam: Dictionary, col: Color, front_h: float) -> ShaderMaterial:
	var b: Dictionary = _cfg().beam
	var length: float = float(b["length_front"]) * front_h
	var m := ShaderMaterial.new()
	m.shader = BEAM
	m.set_shader_parameter(&"beam_col", Vector3(col.r, col.g, col.b))
	m.set_shader_parameter(&"beam_len", length)
	m.set_shader_parameter(&"start_radius", float(b["start_radius"]))
	m.set_shader_parameter(&"end_radius", length * tan(deg_to_rad(float(b["half_deg"]))))
	var lean: Array = beam["lean"] if beam.has("lean") else beam["lean_deg"]
	m.set_shader_parameter(&"lean_deg", Vector2(float(lean[0]), float(lean[1])))
	m.set_shader_parameter(&"sweep_deg", float(beam.get("sweep_deg", 0.0)))
	m.set_shader_parameter(&"phase", float(beam.get("phase", 0.0)))
	m.set_shader_parameter(&"loop_s", float(b["period_s"]))
	m.set_shader_parameter(&"pitch_share", float(b["pitch_share"]))
	m.set_shader_parameter(&"core_sigma", float(b["core_sigma"]))
	m.set_shader_parameter(&"core_w", float(b["core_w"]))
	m.set_shader_parameter(&"skirt_sigma", float(b["skirt_sigma"]))
	m.set_shader_parameter(&"skirt_w", float(b["skirt_w"]))
	m.set_shader_parameter(&"efold", float(b["efold"]))
	m.set_shader_parameter(&"fade", float(b["fade"]))
	m.set_shader_parameter(&"fade_from", float(b["fade_from"]))
	m.set_shader_parameter(&"fade_in", float(b["fade_in"]))
	m.set_shader_parameter(&"noise_scale", float(b["noise_scale"]))
	m.set_shader_parameter(&"noise_range", Vector2(float(b["noise_lo"]), float(b["noise_hi"])))
	m.set_shader_parameter(&"hot", float(b["hot"]))
	m.set_shader_parameter(&"emit", float(b["emit"]))
	return m


## A `MeshInstance3D` for the dress beam `beam` (`pos` plan xyz): the shaft at its roof position, plan -> world axes.
static func beam_node(beam: Dictionary, col: Color, front_h: float) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var length: float = float(_cfg().beam["length_front"]) * front_h
	mi.mesh = beam_mesh(length * 1.5)
	mi.material_override = beam_material(beam, col, front_h)
	var p: Array = beam["pos"]
	mi.position = Vector3(float(p[0]), float(p[2]), -float(p[1]))
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mi


## The `city_fog` material from the config. `h_front` BU = the median frontage roof across the street; `band` = the LOD
## weights of the `fog_octaves` band (x banks, y wisps, z clumps).
static func fog_material(h_front: float = -1.0, octave_w: Vector3 = Vector3.ONE) -> ShaderMaterial:
	var f: Dictionary = _cfg().fog
	var h: float = float(f["h_front"]) if h_front <= 0.0 else h_front
	var m := ShaderMaterial.new()
	m.shader = FOG
	m.set_shader_parameter(&"peak", float(f["peak"]))
	m.set_shader_parameter(&"h_front", h)
	m.set_shader_parameter(&"h_sky", h * float(f["h_sky_k"]))
	for k: String in ["strata_k", "warp_k", "tilt", "wisp_at", "wisp_half", "wisp_k", "gb_top", "ground_bank", "mid_bank", "haze",
			"haze_efold", "underlight_k", "ground_glow", "mid_glow", "emit_gain", "back_haze", "back_h_k"]:
		m.set_shader_parameter(StringName(k), float(f[k]))
	for k: String in ["bank_freq", "wisp_freq", "clump_freq", "scatter", "wind", "tint_a", "tint_b", "tint_c"]:
		m.set_shader_parameter(StringName(k), _v3(f[k]))
	for k: String in ["bank_mix", "remap_oct", "remap_clump", "front", "gb_off", "mid_range", "mid_remap"]:
		m.set_shader_parameter(StringName(k), _v2(f[k]))
	m.set_shader_parameter(&"floor_range", _v2(f["floor"]))
	m.set_shader_parameter(&"back_depth", _v2(f["back_depth"]))
	m.set_shader_parameter(&"octave_w", octave_w)
	return m


## The LOD weights of the `fog_octaves` band at the zoom detail `zoom_detail` (0 .. 1): the higher octaves come in over the
## band `lod.bands.fog_octaves` (PIPELINE_SPEC 5.2), smoothstep.
static func octave_weights(zoom_detail: float) -> Vector3:
	var band: Array = NetrunArtConfigData.shipped().lod["bands"]["fog_octaves"]
	var w: float = smoothstep(float(band[0]), float(band[1]), zoom_detail)
	return Vector3(1.0, w, w)


## A `FogVolume` (box) carrying `fog_material`, centred on `centre` (world), box size from the config.
static func fog_volume(centre: Vector3, h_front: float = -1.0) -> FogVolume:
	var f: Dictionary = _cfg().fog
	var fv := FogVolume.new()
	fv.shape = RenderingServer.FOG_VOLUME_SHAPE_BOX
	fv.size = _v3(f["box"]) * Vector3(2.0, 1.0, 2.0)
	fv.position = centre + Vector3(0.0, fv.size.y * 0.5, 0.0)
	fv.material = fog_material(h_front)
	return fv


## The Environment tonemap exposure at `look_blend`: 1 at 0 (the page as before), `look.exposure` at 1 (the value-band solve).
static func exposure_at(look_blend: float) -> float:
	return lerpf(1.0, float(_cfg().look["exposure"]), clampf(look_blend, 0.0, 1.0))


## The night sky at `look_blend`: `base` is the mainline background colour. Above 0 the Environment shows the `city_sky` sky
## (near-black zenith, warm city-glow band at the horizon) mixed from `base`; at 0 it is the flat background colour as before.
## The sky only fills the background (ambient and reflections stay disabled).
static func apply_sky(env: Environment, look_blend: float, base: Color) -> void:
	var lb: float = clampf(look_blend, 0.0, 1.0)
	if lb <= 0.0:
		env.background_mode = Environment.BG_COLOR
		env.background_color = base
		return
	var s: Dictionary = _cfg().sky
	var mat: ShaderMaterial = null
	if env.sky != null:
		mat = env.sky.sky_material as ShaderMaterial
	if mat == null:
		mat = ShaderMaterial.new()
		mat.shader = SKY
		var sky := Sky.new()
		sky.sky_material = mat
		sky.radiance_size = Sky.RADIANCE_SIZE_32
		sky.process_mode = Sky.PROCESS_MODE_QUALITY
		env.sky = sky
	mat.set_shader_parameter(&"base", Vector3(base.r, base.g, base.b))
	mat.set_shader_parameter(&"top", _v3(s["top"]))
	mat.set_shader_parameter(&"horizon", _v3(s["horizon"]))
	mat.set_shader_parameter(&"ground", _v3(s["ground"]))
	mat.set_shader_parameter(&"glow_k", float(s["glow_k"]))
	mat.set_shader_parameter(&"look_blend", lb)
	env.background_mode = Environment.BG_SKY


## Darkens the landmark toon materials `mats` (the `landmark_mats` of CityView3D: key -> {name -> ShaderMaterial}) toward the
## lights-out facade at `look_blend`: the ramp and the self-lit share (`lit_emission`) scale by `building.landmark_dim` at 1.
## The mainline values are kept in the material's meta, so 0 restores the page as before and a re-call is idempotent.
static func dim_landmarks(mats: Dictionary, look_blend: float) -> void:
	var k: float = lerpf(1.0, float(_cfg().building["landmark_dim"]), clampf(look_blend, 0.0, 1.0))
	for group: Variant in mats.values():
		if not group is Dictionary:
			continue
		for m: Variant in (group as Dictionary).values():
			var sm := m as ShaderMaterial
			if sm == null or sm.shader == null:
				continue
			if sm.shader.resource_path.ends_with("landmark_beam.gdshader"):
				# The mainline light cone (a flat tan shape over the sky in the canyon frame) fades out as the netrun beam shafts
				# take over: `building.beam_fade` = [look_blend where it starts to fade, look_blend where it is gone].
				if not sm.has_meta(&"nr_base_alpha"):
					var a: Variant = sm.get_shader_parameter(&"beam_alpha")
					if a == null:
						continue
					sm.set_meta(&"nr_base_alpha", a)
				var bf: Array = _cfg().building["beam_fade"]
				var keep: float = 1.0 - smoothstep(float(bf[0]), float(bf[1]), clampf(look_blend, 0.0, 1.0))
				sm.set_shader_parameter(&"beam_alpha", float(sm.get_meta(&"nr_base_alpha")) * keep)
				continue
			if not sm.shader.resource_path.ends_with("landmark_toon.gdshader"):
				continue
			var b: Dictionary = _cfg().building
			var fl: Vector2 = _v2(b["wash_floors"]) * float(b["wash_floor_bu"])
			sm.set_shader_parameter(&"wash_k", clampf(look_blend, 0.0, 1.0))
			sm.set_shader_parameter(&"wash_col", _v3(b["wash_a"]).lerp(_v3(b["wash_b"]), 0.5))
			sm.set_shader_parameter(&"wash_gain", float(b["landmark_wash_gain"]))
			sm.set_shader_parameter(&"wash_h", fl)
			if not sm.has_meta(&"nr_base"):
				sm.set_meta(&"nr_base", {"ramp_shadow": sm.get_shader_parameter(&"ramp_shadow"), "ramp_mid": sm.get_shader_parameter(&"ramp_mid"),
					"ramp_lit": sm.get_shader_parameter(&"ramp_lit"), "lit_emission": sm.get_shader_parameter(&"lit_emission")})
			var base: Dictionary = sm.get_meta(&"nr_base")
			for n: StringName in [&"ramp_shadow", &"ramp_mid", &"ramp_lit"]:
				if base[n] != null:
					sm.set_shader_parameter(n, base[n] * k)
			if base[&"lit_emission"] != null:
				sm.set_shader_parameter(&"lit_emission", float(base[&"lit_emission"]) * k)


## Volumetric fog settings on `env` (the scene's Environment): enabled, zero global density (the FogVolume carries it), the
## scatter albedo and anisotropy, length and the temporal reprojection.
static func configure_environment(env: Environment) -> void:
	var f: Dictionary = _cfg().fog
	var sc: Vector3 = _v3(f["scatter"])
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.0
	env.volumetric_fog_albedo = Color(sc.x, sc.y, sc.z)
	env.volumetric_fog_anisotropy = float(f["anisotropy"])
	env.volumetric_fog_length = float(f["length"])
	# AAA-2: the fog is a real volume to the far skyline (the froxels past `length` repeat the last slice, which turned every far
	# building to fog at the plate's density): finer froxels, the length follows the camera (`fog_length_for`).
	env.volumetric_fog_detail_spread = float(f["detail_spread"])
	var fx: Array = f["froxel"]
	RenderingServer.environment_set_volumetric_fog_volume_size(int(fx[0]), int(fx[1]))
	env.volumetric_fog_temporal_reprojection_enabled = false


## The volumetric fog length (BU) for a camera `dist` BU from its target: the target plus `fog.length` beyond it.
static func fog_length_for(dist: float) -> float:
	return minf(dist + float(_cfg().fog["length"]), float(_cfg().fog["length_max"]))
