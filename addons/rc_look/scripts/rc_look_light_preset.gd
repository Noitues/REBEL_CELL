class_name RcLookLightPreset
extends Resource
## LOOK-TOOLBOX module 6: one light's falloff and gain (RcLookLight, rc_light.gdshaderinc). Read only.

enum Kind { EXP, POW }

## EXP: exp(-(d / reach)^shape), unbounded (glows, halos). POW: (1 - d / reach)^shape, zero at reach (pools, spill).
@export var kind: Kind = Kind.EXP
## Distance at which EXP falls to 1/e or POW reaches 0. The shipped presets are unit (1.0): a caller passes the
## distance over its emitter's size (px for UI, BU for the city), so one preset reads the same at any scale.
@export var reach: float = 1.0
## EXP's exponent k or POW's power p.
@export var shape: float = 2.0
## Linear-light intensity at the source.
@export var gain: float = 1.0


## Problems with the numbers (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if reach <= 0.0:
		errs.append("reach must be > 0 (%s)" % reach)
	if shape <= 0.0:
		errs.append("shape must be > 0 (%s)" % shape)
	if gain < 0.0:
		errs.append("gain must be >= 0 (%s)" % gain)
	return errs
