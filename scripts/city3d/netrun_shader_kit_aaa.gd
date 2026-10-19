class_name NetrunShaderKitAaa
extends RefCounted
## The AAA-2 "Realistic night" half of the netrun look (A-022 / MATERIAL_SPEC): the post chain uniforms, the flat world colour, the
## moon and ambient, SSR. View glue only; every number comes from `CityShaderConfigData.aaa`. Used by `CityView3D.set_look_blend`
## (look_blend above 0 only: the mainline city keeps the cel look).


## The `aaa` block of the shader config.
static func cfg() -> Dictionary:
	return CityShaderConfigData.shipped().aaa


static func _v3(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))


static func _v4(a: Array) -> Vector4:
	return Vector4(float(a[0]), float(a[1]), float(a[2]), float(a[3]))


## The post exposure at `look_blend` (1 at 0: the page as before; `aaa.post.exposure` at 1).
static func exposure_at(look_blend: float) -> float:
	return lerpf(1.0, float(cfg()["post"]["exposure"]), clampf(look_blend, 0.0, 1.0))


## The post chain numbers (`aaa.post`) on the `city_post` material `m` and the switch `on`. The post draws first as in the mainline;
## the screen copy it reads is taken before the transparent pass, so the emissive dressing that must bloom is opaque (`dress_solid`,
## `dress_sign`) and the few transparent additive pieces (beams, streaks, plumes, flickers) are scaled by the exposure themselves.
static func setup_post(m: ShaderMaterial, on: bool, exposure: float) -> void:
	m.set_shader_parameter(&"aaa_on", on)
	if not on:
		return
	var p: Dictionary = cfg()["post"]
	m.set_shader_parameter(&"aaa_exposure", exposure)
	m.set_shader_parameter(&"aaa_ref_w", float(p["ref_w"]))
	m.set_shader_parameter(&"aaa_bloom_thr", float(p["bloom_thr"]))
	m.set_shader_parameter(&"aaa_bloom_sigma", _v3(p["bloom_sigma_px"]))
	m.set_shader_parameter(&"aaa_bloom_w", _v3(p["bloom_w"]))
	m.set_shader_parameter(&"aaa_bloom_lod_k", float(p["bloom_lod_k"]))
	var a: Array = p["aces"]
	m.set_shader_parameter(&"aaa_aces_abc", Vector3(float(a[0]), float(a[1]), float(a[2])))
	m.set_shader_parameter(&"aaa_aces_de", Vector2(float(a[3]), float(a[4])))
	m.set_shader_parameter(&"aaa_aces_blend", _v3(p["aces_blend"]))
	m.set_shader_parameter(&"aaa_shadow_tint", _v3(p["shadow_tint"]))
	m.set_shader_parameter(&"aaa_shadow", Vector2(float(p["shadow_k"]), float(p["shadow_slope"])))
	m.set_shader_parameter(&"aaa_hi_tint", _v3(p["hi_tint"]))
	m.set_shader_parameter(&"aaa_hi", Vector3(float(p["hi_k"]), float(p["hi_from"]), float(p["hi_slope"])))
	m.set_shader_parameter(&"aaa_lift", _v3(p["lift"]))
	m.set_shader_parameter(&"aaa_vig", Vector3(float(p["vignette"]), float(p["vig_r0"]), float(p["vig_pow"])))
	m.set_shader_parameter(&"aaa_contrast", Vector2(float(p["contrast"]), float(p["contrast_pivot"])))
	m.set_shader_parameter(&"aaa_knee", _v3(p["knee"]))
	m.set_shader_parameter(&"aaa_ca", Vector3(float(p["ca_px"]), float(p["ca_r0"]), float(p["ca_pow"])))
	m.set_shader_parameter(&"aaa_grain", Vector2(float(p["grain"]), float(p["grain_lum"])))
	var r: Array = p["rain"]
	for i in 3:
		var l: Array = r[i]
		m.set_shader_parameter(StringName("aaa_rain%d" % i), Vector3(float(l[0]), float(l[1]), float(l[2])))
		m.set_shader_parameter(StringName("aaa_rain%db" % i), Vector3(float(l[3]), float(l[4]), float(l[5])))
	var wr: Dictionary = cfg()["wet_refl"]
	m.set_shader_parameter(&"aaa_wr_on", on and bool(wr["enabled"]))
	m.set_shader_parameter(&"aaa_wr_steps", int(wr["steps"]))
	m.set_shader_parameter(&"aaa_wr_march", _v4(wr["march"]))
	m.set_shader_parameter(&"aaa_wr_shape", _v4(wr["shape"]))
	m.set_shader_parameter(&"aaa_wr_rough", _v4(wr["rough"]))
	m.set_shader_parameter(&"aaa_wr_bokeh", _v4(wr["bokeh"]))
	m.set_shader_parameter(&"aaa_wr_sky", float(wr["sky"]))
	m.set_shader_parameter(&"aaa_rain_fall", Vector2(float(p["rain_fall_px"]), float(p["rain_slant"])))


## The flat world (A-022: no sky gradient), its weak ambient, SSR and the moon. `lb` 0 puts back the mainline's `base` background,
## no ambient, no SSR; `sun` is the view's key light: above 0 it is the moon (energy `aaa.world.moon.energy`, no shadow map), at 0 the
## saved mainline values come back.
static func apply_world(env: Environment, sun: DirectionalLight3D, lb: float, base: Color) -> void:
	lb = clampf(lb, 0.0, 1.0)
	var w: Dictionary = cfg()["world"]
	var wc := _v3(w["color"])
	if sun != null and not sun.has_meta(&"nr_sun"):
		sun.set_meta(&"nr_sun", {"energy": sun.light_energy, "color": sun.light_color, "basis": sun.transform.basis,
			"shadow": sun.shadow_enabled})
	if lb <= 0.0:
		env.background_mode = Environment.BG_COLOR
		env.background_color = base
		env.ambient_light_source = Environment.AMBIENT_SOURCE_DISABLED
		env.ssr_enabled = false
		if sun != null:
			var s0: Dictionary = sun.get_meta(&"nr_sun")
			sun.light_energy = float(s0["energy"])
			sun.light_color = s0["color"]
			sun.transform = Transform3D(s0["basis"], sun.transform.origin)
			sun.shadow_enabled = bool(s0["shadow"])
		return
	env.background_mode = Environment.BG_COLOR
	env.background_color = base.lerp(Color(wc.x, wc.y, wc.z), lb)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(wc.x, wc.y, wc.z)
	env.ambient_light_energy = float(w["ambient_energy"]) * lb
	var ss: Dictionary = cfg()["ssr"]
	env.ssr_enabled = bool(ss["enabled"])
	env.ssr_max_steps = int(ss["max_steps"])
	env.ssr_fade_in = float(ss["fade_in"])
	env.ssr_fade_out = float(ss["fade_out"])
	env.ssr_depth_tolerance = float(ss["depth_tolerance"])
	if sun != null:
		var s: Dictionary = sun.get_meta(&"nr_sun")
		var mo: Dictionary = w["moon"]
		sun.light_energy = lerpf(float(s["energy"]), float(mo["energy"]), lb)
		var mc: Array = mo["color"]
		sun.light_color = (s["color"] as Color).lerp(Color(float(mc[0]), float(mc[1]), float(mc[2])), lb)
		sun.shadow_enabled = false if lb >= 1.0 else bool(s["shadow"])
		if lb >= 1.0:
			sun.transform = Transform3D(moon_basis(mo["rot"]), sun.transform.origin)


## The moon's light basis: a Blender sun with Euler XYZ `rot` degrees (plan x, y, z up) shines along its local -Z; the world is
## (x, height, -y). The Godot light shines along its -Z too.
static func moon_basis(rot: Array) -> Basis:
	var rx := Basis(Vector3.RIGHT, deg_to_rad(float(rot[0])))
	var ry := Basis(Vector3.UP, deg_to_rad(float(rot[1])))
	var rz := Basis(Vector3.BACK, deg_to_rad(float(rot[2])))
	var d_plan := (rz * ry * rx) * Vector3(0.0, 0.0, -1.0)
	var d := Vector3(d_plan.x, d_plan.z, -d_plan.y).normalized()
	var up := Vector3.UP if absf(d.y) < 0.99 else Vector3.RIGHT
	return Basis.looking_at(d, up)
