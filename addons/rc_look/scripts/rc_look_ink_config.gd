class_name RcLookInkConfig
extends Resource
## LOOK-TOOLBOX module 5: the ink presets (addons/rc_look/config/look_ink.tres).

## Preset name -> RcLookInkPreset.
@export var presets: Dictionary = {}
## The ortho size the post presets' depth_edge is tuned at (city_post: dthr = depth_edge * ortho / ortho_ref).
@export var ortho_ref: float = 300.0


## Problems with the config (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if ortho_ref <= 0.0:
		errs.append("ortho_ref must be above 0 (%s)" % ortho_ref)
	for n in RcLookInk.REQUIRED:
		if not presets.has(n):
			errs.append("missing preset %s" % n)
	for n: StringName in presets:
		if not presets[n] is RcLookInkPreset:
			errs.append("%s is not an RcLookInkPreset" % n)
			continue
		for e in (presets[n] as RcLookInkPreset).validate():
			errs.append("%s: %s" % [n, e])
	return errs
