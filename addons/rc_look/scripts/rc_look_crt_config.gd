class_name RcLookCrtConfig
extends Resource
## LOOK-TOOLBOX module 14: the CRT presets and the reduce-effects convention (addons/rc_look/config/look_crt.tres).

## Preset name -> RcLookCrtPreset.
@export var presets: Dictionary = {}
## What reduce effects does to a preset (RcLookCrt.Reduce) until the designer rules: static scanlines stay (what the
## shaders do through rc_live and what ART_BIBLE §5.4 says).
@export var reduce: int = 0


## Problems with the config (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for n in RcLookCrt.REQUIRED:
		if not presets.has(n):
			errs.append("missing preset %s" % n)
	for n: StringName in presets:
		if not presets[n] is RcLookCrtPreset:
			errs.append("%s is not an RcLookCrtPreset" % n)
			continue
		for e in (presets[n] as RcLookCrtPreset).validate():
			errs.append("%s: %s" % [n, e])
	if reduce < 0 or reduce >= RcLookCrt.Reduce.size():
		errs.append("reduce must name a RcLookCrt.Reduce (%s)" % reduce)
	return errs
