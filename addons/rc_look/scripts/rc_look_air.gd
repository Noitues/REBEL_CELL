class_name RcLookAir
extends RefCounted
## LOOK-TOOLBOX module 7: atmosphere. The shader side is rc_air.gdshaderinc (rcl_air, rcl_air_mix, rcl_sky); this is
## its exact GDScript mirror plus the preset lookup and a material filler; `pass_node` builds the 3D air pass
## (rc_air_pass.gdshader) a view adds under its camera. No Settings.

const PASS_SHADER := "res://addons/rc_look/shaders/rc_air_pass.gdshader"
## The pass quad's cull margin: it covers the whole screen from any camera, so it is never culled.
const PASS_CULL_MARGIN := 16384.0

static var _cfg: RcLookAirConfig


## The shipped config, loaded once.
static func default_config() -> RcLookAirConfig:
	if _cfg == null:
		_cfg = load(RcLookAirConfig.DEFAULT_PATH) as RcLookAirConfig
	return _cfg


## A shipped preset by name (`day`, `night`; null when unknown).
static func preset(name: StringName) -> RcLookAirPreset:
	return default_config().presets.get(name) as RcLookAirPreset


## The air between the eye and a point `d` away at height `y`, 0..1, as rcl_air.
static func amount(p: RcLookAirPreset, d: float, y: float) -> float:
	var depth := 1.0 - exp(-maxf(d - p.start, 0.0) * p.density)
	var thin := lerpf(1.0, p.high, 1.0 - exp(-maxf(y, 0.0) / maxf(p.height, 1e-5)))
	return clampf(depth * thin, 0.0, 1.0)


## sRGB `c` seen through `t` of air `air` (linear-light mix), as rcl_air_mix. Alpha kept.
static func mix(c: Color, air: Color, t: float) -> Color:
	var o := c.srgb_to_linear().lerp(air.srgb_to_linear(), clampf(t, 0.0, 1.0)).linear_to_srgb()
	return Color(o.r, o.g, o.b, c.a)


## The sky at elevation `e` (sin of the view angle), as rcl_sky.
static func sky(p: RcLookAirPreset, e: float) -> Color:
	var t := p.sky_top.srgb_to_linear()
	var h := p.sky_horizon.srgb_to_linear()
	var o: Color
	if e >= 0.0:
		o = t + (h - t) * exp(-p.glow_k * e)
	else:
		o = h.lerp(p.sky_ground.srgb_to_linear(), clampf(-e * p.ground_k, 0.0, 1.0))
	o = o.linear_to_srgb()
	return Color(o.r, o.g, o.b, 1.0)


## Writes a preset into a material's `<prefix>air` (vec3, the horizon colour), `<prefix>air_a` (vec4), `<prefix>sky_top / sky_horizon /
## sky_ground` (vec3) and `<prefix>glow_k / ground_k`.
static func apply(mat: ShaderMaterial, p: RcLookAirPreset, prefix: String = "") -> void:
	var a := p.air_color()
	mat.set_shader_parameter(prefix + "air", Vector3(a.r, a.g, a.b))
	mat.set_shader_parameter(prefix + "air_a", p.air_vec())
	mat.set_shader_parameter(prefix + "sky_top", Vector3(p.sky_top.r, p.sky_top.g, p.sky_top.b))
	mat.set_shader_parameter(prefix + "sky_horizon", Vector3(p.sky_horizon.r, p.sky_horizon.g, p.sky_horizon.b))
	mat.set_shader_parameter(prefix + "sky_ground", Vector3(p.sky_ground.r, p.sky_ground.g, p.sky_ground.b))
	mat.set_shader_parameter(prefix + "glow_k", p.glow_k)
	mat.set_shader_parameter(prefix + "ground_k", p.ground_k)


## The 3D air pass for preset `p`: a full-screen quad (add it anywhere in the view's 3D scene) that lays the air over
## every pixel by its depth and height above `ground_y`. `overrides` may replace "start", "density", "height", "high".
static func pass_node(p: RcLookAirPreset, ground_y: float = 0.0, overrides: Dictionary = {}) -> MeshInstance3D:
	var q := QuadMesh.new()
	q.size = Vector2(2.0, 2.0)
	var m := ShaderMaterial.new()
	m.shader = load(PASS_SHADER) as Shader
	var a := p.air_color()
	m.set_shader_parameter(&"air", Vector3(a.r, a.g, a.b))
	var v := p.air_vec()
	m.set_shader_parameter(&"air_a", Vector4(float(overrides.get("start", v.x)), float(overrides.get("density", v.y)),
			float(overrides.get("height", v.z)), float(overrides.get("high", v.w))))
	m.set_shader_parameter(&"ground_y", ground_y)
	var n := MeshInstance3D.new()
	n.name = "RcLookAirPass"
	n.mesh = q
	n.material_override = m
	n.extra_cull_margin = PASS_CULL_MARGIN
	n.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return n
