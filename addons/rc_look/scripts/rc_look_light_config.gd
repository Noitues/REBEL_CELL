class_name RcLookLightConfig
extends Resource
## LOOK-TOOLBOX module 6: the light presets and the bloom pass (addons/rc_look/config/look_light.tres). Bloom strength
## by quality tier is in look_quality.tres (module "light"); reduce effects keeps bloom (it is static).

const DEFAULT_PATH := "res://addons/rc_look/config/look_light.tres"
## Presets every view may ask for by name.
const REQUIRED: Array[StringName] = [&"glow", &"halo", &"pool", &"spill", &"spill_ui"]

## Preset name -> RcLookLightPreset.
@export var presets: Dictionary = {}
## Bloom: bright-pass threshold and knee (linear light), screen mip levels and their weights.
@export var bloom_threshold: float = 0.8
@export var bloom_knee: float = 0.4
## The 2D bloom's key: 0 brightest channel, 1 chroma (2D layers: paper never blooms, neon does).
@export_range(0, 1) var bloom_key: int = 1
@export var bloom_lods: Vector3 = Vector3(2.0, 4.0, 6.0)
@export var bloom_weights: Vector3 = Vector3(0.5, 0.35, 0.25)


## Problems with the config (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for n in REQUIRED:
		if not presets.has(n):
			errs.append("missing preset %s" % n)
	for n: StringName in presets:
		if not presets[n] is RcLookLightPreset:
			errs.append("%s is not an RcLookLightPreset" % n)
			continue
		for e in (presets[n] as RcLookLightPreset).validate():
			errs.append("%s: %s" % [n, e])
	if bloom_knee <= 0.0:
		errs.append("bloom_knee must be > 0")
	return errs
