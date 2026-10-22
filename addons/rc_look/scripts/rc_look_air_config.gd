class_name RcLookAirConfig
extends Resource
## LOOK-TOOLBOX module 7: the air presets (addons/rc_look/config/look_air.tres), one per time of day. The air has no
## quality or accessibility rule (static; reduce effects keeps it).

const DEFAULT_PATH := "res://addons/rc_look/config/look_air.tres"
## "solace_night": the Solace HQ page (designer DIRECTION_REVIEW 0f336345, 82c92714): the night air from 150 BU in a dark violet
## that pulls the far city down toward the plate (hq_solace_overview) instead of greying it; only its air (start, density, height,
## high, horizon = the air colour) reaches the page, through the 3D air pass.
const REQUIRED: Array[StringName] = [&"day", &"night", &"solace_night"]

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
