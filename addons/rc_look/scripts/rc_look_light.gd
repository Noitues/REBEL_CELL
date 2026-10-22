class_name RcLookLight
extends RefCounted
## LOOK-TOOLBOX module 6: light, spill, glow, bloom. The shader side is rc_light.gdshaderinc (falloffs, linear light
## add, bright pass) and rc_bloom.gdshader (the 2D screen bloom); this is their exact GDScript mirror plus the preset
## lookup and the material fillers. Pure: no Node, no Settings.

const BLOOM_SHADER := "res://addons/rc_look/shaders/rc_bloom.gdshader"
## Quality module id in look_quality.tres.
const QUALITY_MODULE := &"light"

static var _cfg: RcLookLightConfig


## The shipped config, loaded once.
static func default_config() -> RcLookLightConfig:
	if _cfg == null:
		_cfg = load(RcLookLightConfig.DEFAULT_PATH) as RcLookLightConfig
	return _cfg


## A shipped preset by name (null when unknown).
static func preset(name: StringName) -> RcLookLightPreset:
	return default_config().presets.get(name) as RcLookLightPreset


## exp(-(d / reach)^k), as rcl_fall_exp.
static func fall_exp(d: float, reach: float, k: float) -> float:
	return exp(-pow(maxf(d, 0.0) / maxf(reach, 1e-5), k))


## (1 - d / reach)^p clamped, as rcl_fall_pow.
static func fall_pow(d: float, reach: float, p: float) -> float:
	return pow(clampf(1.0 - maxf(d, 0.0) / maxf(reach, 1e-5), 0.0, 1.0), p)


## A preset's linear-light intensity at distance `d` (its falloff times its gain).
static func at(p: RcLookLightPreset, d: float) -> float:
	var f := fall_exp(d, p.reach, p.shape) if p.kind == RcLookLightPreset.Kind.EXP else fall_pow(d, p.reach, p.shape)
	return f * p.gain


## Light `light_lin` (linear) added to sRGB `base` in linear light under the soft ceiling, as rcl_light_add.
static func light_add(base: Color, light_lin: Color) -> Color:
	var b := base.srgb_to_linear()
	var o := Color(_ceil(b.r, light_lin.r), _ceil(b.g, light_lin.g), _ceil(b.b, light_lin.b)).linear_to_srgb()
	return Color(o.r, o.g, o.b, base.a)


static func _ceil(b: float, l: float) -> float:
	var c := minf(b, 1.0)
	var room := maxf(1.0 - c, 1e-5)
	return maxf(1.0 - room * exp(-maxf(l, 0.0) / room), c)


## The soft-knee bright pass on a linear colour, as rcl_bright (`key` 0: brightest channel, 1: chroma).
static func bright(lin: Color, threshold: float, knee: float, key: int = 0) -> Color:
	var hi := maxf(lin.r, maxf(lin.g, lin.b))
	var l := hi if key == 0 else hi - minf(lin.r, minf(lin.g, lin.b))
	var k := maxf(knee, 1e-5)
	var soft := clampf(l - threshold + k, 0.0, 2.0 * k)
	soft = soft * soft / (4.0 * k)
	var w := maxf(soft, l - threshold) / maxf(l, 1e-5)
	return Color(lin.r * w, lin.g * w, lin.b * w, lin.a)


## A ShaderMaterial for the 2D bloom pass, filled for quality state `state` (null: the top tier, no flags).
static func bloom_material(state: RcLookQualityState = null) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(BLOOM_SHADER) as Shader
	apply_bloom(m, state)
	return m


## Fills a bloom material from the config and the quality rules ("light.bloom" strength).
static func apply_bloom(mat: ShaderMaterial, state: RcLookQualityState = null) -> void:
	var c := default_config()
	var q := RcLookQuality.of(QUALITY_MODULE, state if state != null else RcLookQualityState.make(RcLookQualityConfig.TIER_COUNT - 1))
	mat.set_shader_parameter(&"strength", float(q.get("bloom", 1.0)))
	mat.set_shader_parameter(&"threshold", c.bloom_threshold)
	mat.set_shader_parameter(&"knee", c.bloom_knee)
	mat.set_shader_parameter(&"key", c.bloom_key)
	mat.set_shader_parameter(&"lods", c.bloom_lods)
	mat.set_shader_parameter(&"weights", c.bloom_weights)
