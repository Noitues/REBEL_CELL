class_name RcLookGradeConfig
extends Resource
## LOOK-TOOLBOX module 9: the named grade presets (addons/rc_look/config/look_grade.tres). `cel` is the identity (the
## cel views are authored in display values); `aaa2` keeps exposure 1 with the highlight shoulder, so lit neon rolls
## off instead of clipping. A view with its own tuning (the combat backdrop: CityConfig backdrop_*) passes its numbers
## to RcLookGrade.grade and still shares the curve. The grade has no quality or accessibility rule.

const DEFAULT_PATH := "res://addons/rc_look/config/look_grade.tres"
## The presets every view may ask for by name.
const REQUIRED: Array[StringName] = [&"cel", &"aaa2"]

## Preset name -> RcLookGradePreset.
@export var presets: Dictionary = {}


## Problems with the config (empty when good): a required preset missing, a value that is not a preset, bad numbers.
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for n in REQUIRED:
		if not presets.has(n):
			errs.append("missing preset %s" % n)
	for n: StringName in presets:
		if not presets[n] is RcLookGradePreset:
			errs.append("%s is not an RcLookGradePreset" % n)
			continue
		for e in (presets[n] as RcLookGradePreset).validate():
			errs.append("%s: %s" % [n, e])
	return errs
