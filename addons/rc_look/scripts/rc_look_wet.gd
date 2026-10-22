class_name RcLookWet
extends RefCounted
## LOOK-TOOLBOX module 8: wet and water. The shader side is rc_wet.gdshaderinc; this is its exact GDScript mirror (all
## but the noise) plus the presets (config/look_wet.tres: "street" the wet street, "plinth" the wet plinth top,
## "water" the water plane). Pure: no Node, no Settings.

const DEFAULT_PATH := "res://addons/rc_look/config/look_wet.tres"
const REQUIRED: Array[StringName] = [&"street", &"plinth", &"water"]

static var _cfg: RcLookWetConfig


## The shipped presets, loaded once.
static func default_config() -> RcLookWetConfig:
	if _cfg == null:
		_cfg = load(DEFAULT_PATH) as RcLookWetConfig
	return _cfg


## A shipped preset by name (null when unknown).
static func preset(name: StringName) -> RcLookWetPreset:
	return default_config().presets.get(name) as RcLookWetPreset


## Roughness over the puddle noise, as rcl_puddle_rough.
static func puddle_rough(n: float, rough_noise: Vector2, rough_wet: Vector2) -> float:
	return lerpf(rough_wet.x, rough_wet.y, smoothstep(rough_noise.x, rough_noise.y, n))


## Schlick Fresnel, power 5, as rcl_fresnel.
static func fresnel(cos_t: float, f0: float) -> float:
	return f0 + (1.0 - f0) * pow(1.0 - cos_t, 5.0)


## The dielectric F0 of an index of refraction, as rcl_f0_ior.
static func f0_ior(ior: float) -> float:
	return pow((ior - 1.0) / (ior + 1.0), 2.0)


## The isotropic GGX distribution (a = roughness^2), as rcl_ggx_d.
static func ggx_d(nh: float, a: float) -> float:
	return a * a / (PI * pow(nh * nh * (a * a - 1.0) + 1.0, 2.0))


## 1 on the noise's mid line fading over `width`, as rcl_ridge.
static func ridge(n: float, width: float) -> float:
	return 1.0 - smoothstep(0.0, width, absf(2.0 * n - 1.0))


## exp(-d / len), as rcl_shore.
static func shore(d: float, length: float) -> float:
	return exp(-d / maxf(length, 0.001))
