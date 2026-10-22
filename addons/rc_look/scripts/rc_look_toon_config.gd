class_name RcLookToonConfig
extends Resource
## LOOK-TOOLBOX module 4: the toon presets (addons/rc_look/config/look_toon.tres). No quality rule (bands are static).

## Preset name -> RcLookToonPreset.
@export var presets: Dictionary = {}


## Problems with the config (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for n in RcLookToon.REQUIRED:
		if not presets.has(n):
			errs.append("missing preset %s" % n)
	for n: StringName in presets:
		if not presets[n] is RcLookToonPreset:
			errs.append("%s is not an RcLookToonPreset" % n)
			continue
		for e in (presets[n] as RcLookToonPreset).validate():
			errs.append("%s: %s" % [n, e])
	return errs
