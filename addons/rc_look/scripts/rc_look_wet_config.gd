class_name RcLookWetConfig
extends Resource
## LOOK-TOOLBOX module 8: the wet presets (addons/rc_look/config/look_wet.tres).

## Preset name -> RcLookWetPreset.
@export var presets: Dictionary = {}


## Problems with the config (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for n in RcLookWet.REQUIRED:
		if not presets.has(n):
			errs.append("missing preset %s" % n)
	for n: StringName in presets:
		if not presets[n] is RcLookWetPreset:
			errs.append("%s is not an RcLookWetPreset" % n)
			continue
		for e in (presets[n] as RcLookWetPreset).validate():
			errs.append("%s: %s" % [n, e])
	return errs
