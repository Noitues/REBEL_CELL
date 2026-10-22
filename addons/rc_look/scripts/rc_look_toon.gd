class_name RcLookToon
extends RefCounted
## LOOK-TOOLBOX module 4: toon (cel) bands. The shader side is rc_toon.gdshaderinc; this is its exact GDScript mirror
## plus the presets (config/look_toon.tres: "props" for the kit's props / busts / aircraft, "city" for buildings,
## landmarks and compounds). Pure: no Node, no Settings.

const DEFAULT_PATH := "res://addons/rc_look/config/look_toon.tres"
const REQUIRED: Array[StringName] = [&"props", &"city"]

static var _cfg: RcLookToonConfig


## The shipped presets, loaded once.
static func default_config() -> RcLookToonConfig:
	if _cfg == null:
		_cfg = load(DEFAULT_PATH) as RcLookToonConfig
	return _cfg


## A shipped preset by name (null when unknown).
static func preset(name: StringName) -> RcLookToonPreset:
	return default_config().presets.get(name) as RcLookToonPreset


## 0 shadow, 1 mid, 2 lit, as rcl_band.
static func band(x: float, lo: float, hi: float) -> int:
	return 2 if x > hi else (1 if x > lo else 0)


## The band's share of full light, as rcl_band_shade.
static func band_shade(x: float, lo: float, hi: float, mid: float, low: float) -> float:
	return 1.0 if x > hi else (mid if x > lo else low)


## The band's tint (shadow_tint in the shadow band to white when lit), as rcl_band_tint.
static func band_tint(shade: float, low: float, shadow_tint: Color) -> Color:
	var t := (shade - low) / maxf(1.0 - low, 0.001)
	return Color(lerpf(shadow_tint.r, 1.0, t), lerpf(shadow_tint.g, 1.0, t), lerpf(shadow_tint.b, 1.0, t))


## (1 - n . v)^p, as rcl_rim.
static func rim(n: Vector3, v: Vector3, p: float) -> float:
	return pow(1.0 - clampf(n.dot(v), 0.0, 1.0), p)
