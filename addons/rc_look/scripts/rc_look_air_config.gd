class_name RcLookAirConfig
extends Resource
## LOOK-TOOLBOX module 7: the air presets (addons/rc_look/config/look_air.tres), one per time of day. The air has no
## quality or accessibility rule (static; reduce effects keeps it).

const DEFAULT_PATH := "res://addons/rc_look/config/look_air.tres"
const REQUIRED: Array[StringName] = [&"day", &"night"]

## Preset name -> RcLookAirPreset.
@export var presets: Dictionary = {}


## Problems with the config (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for n in REQUIRED:
		if not presets.has(n):
			errs.append("missing preset %s" % n)
	for n: StringName in presets:
		if not presets[n] is RcLookAirPreset:
			errs.append("%s is not an RcLookAirPreset" % n)
			continue
		for e in (presets[n] as RcLookAirPreset).validate():
			errs.append("%s: %s" % [n, e])
	return errs
